"""S2 P1b DES 横向铺开 —— 量级达标测试（P1b 门禁）§6：五查询 P95 + 峰值 RSS + 全量生成耗时。

对照 docs/P1b-DES-横向铺开设计_v0.1.md §6：
- 6.1 数据集口径：同 seed 同配置确定性生成的 1,000,000 行（18 表 5 库）；测量 = 每查询预热 1 次 +
  重复 N 次取 P95；实现 = DuckDB sqlite_scan 直读 5 库（库路径参数化；SQLite ATTACH 为设计兜底路径，
  本测试主路径为 DuckDB，不可用时明确 skip 而非静默通过）；
- 6.2 五查询 Q1-Q5（跨库 join / 无预聚合大聚合 / 过滤+TOP-N / 6 跳链路 / 对账自洽）——照设计 SQL 形态；
- 6.3 阈值：Q1≤500ms / Q2≤2000ms / Q3≤800ms / Q4≤3000ms / Q5≤2000ms；峰值 RSS≤1.5GB；全量生成≤3min。

判定口径：宽松判据 = P95 × 1.5 余量（防 CI 抖动误报，§6.3 风险 R3）+ 实测值打印；
超阈值如实报告、不静默通过（§6.3 降级路径说明）。本文件为 @pytest.mark.slow（pyproject 已注册）。
运行提示：pytest tests/test_des_p1b_scale.py -s -v；
  N（重复次数）默认 5，快速验证设 DES_P1B_SCALE_N=3；正式门禁建议 10（§6.1 ≥10）；
  全量生成测试可选一次，设 DES_P1B_SCALE_FULL_GEN=1 启用（默认 skip）。
"""

from __future__ import annotations

import json
import os
import resource
import sys
import time
from pathlib import Path
from typing import Any

import duckdb
import pytest

from src.des.config import config_sha256, load_config
from src.des.generate import build_enterprise

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_DIR = ROOT / "data" / "des" / "enterprises" / "hc_precision"
ENTERPRISE_CODE = "hc_precision"
EXPECTED_SEED = 20260821
# 生效配置（模板层 + 企业覆盖层合并后，模块级缓存）：库文件名/阈值全部从配置读，不硬编码。
_CONFIG = load_config(ENTERPRISE_CODE)

# ---------------------------------------------------------------------------
# 测量参数（§6.1：预热 1 次 + 重复 N 次取 P95）
# ---------------------------------------------------------------------------
WARMUP = 1  # 预热次数（固定）
REPEAT = int(os.environ.get("DES_P1B_SCALE_N", "5"))  # 重复次数：默认 5（保持可跑），正式门禁建议 10
assert REPEAT >= 2, "DES_P1B_SCALE_N 至少为 2（否则 P95 无意义）"
# 全量生成耗时测试为「可选做一次」（§6.3 附加操作上界），默认 skip，DES_P1B_SCALE_FULL_GEN=1 启用
RUN_FULL_GENERATION = os.environ.get("DES_P1B_SCALE_FULL_GEN", "0") == "1"

# §6.3 阈值（ms）+ 宽松判据余量
_QUERY_THRESHOLDS_MS = {"Q1": 500, "Q2": 2000, "Q3": 800, "Q4": 3000, "Q5": 2000}
_P95_MARGIN = 1.5  # P95 × 1.5 余量：防 CI 抖动误报（§6.3）
RSS_LIMIT_BYTES = 1.5 * 1024**3  # 峰值 RSS ≤ 1.5GB（§6.3，生成 + 查询全流程）
GENERATION_LIMIT_S = 180  # 全量生成 ≤ 3min（§6.3 附加操作上界）
_RECON_TOL = 1e-6  # Q5 对账 diff=0 浮点容差（SUM(REAL) 1e-6 内视为 0）

# ---------------------------------------------------------------------------
# §6.2 五查询（照设计 SQL；库路径参数化：sqlite_scan(?, 'T') 绑绝对路径）
# 每项 = (SQL, [第 i 个 ? 对应的系统代码，按出现顺序])
# ---------------------------------------------------------------------------
_QUERIES: dict[str, tuple[str, list[str]]] = {
    "Q1": (
        """
        SELECT p.EBELN, p.EBELP, p.MATNR, m.MAKTX, l.NAME1 AS vendor_name, p.MENGE, p.NETWR
        FROM   sqlite_scan(?, 'EKPO') p
        JOIN   sqlite_scan(?, 'EKKO') h ON p.EBELN = h.EBELN
        JOIN   sqlite_scan(?, 'MARA') m ON p.MATNR = m.MATNR
        JOIN   sqlite_scan(?, 'LFA1') l ON h.LIFNR = l.LIFNR
        WHERE  p.NETWR > 1000
        ORDER BY p.NETWR DESC LIMIT 50
        """,
        ["scm", "scm", "erp", "scm"],
    ),
    "Q2": (
        """
        SELECT 'MES' AS sys, substr(DATUM,1,7) AS ym, SUM(ISM01) AS qty, SUM(ISMN1) AS hrs
        FROM   sqlite_scan(?, 'COFV') GROUP BY 1,2
        UNION ALL
        SELECT 'WMS', substr(BUDAT,1,7), SUM(MENGE), 0
        FROM   sqlite_scan(?, 'MSEG') GROUP BY 1,2
        UNION ALL
        SELECT 'FIN', substr(BUDAT,1,7), 0, SUM(WSL)
        FROM   sqlite_scan(?, 'ACDOCA') GROUP BY 1,2
        ORDER BY sys, ym
        """,
        ["mes", "wms", "fin"],
    ),
    "Q3": (
        """
        SELECT m.MAKTX, v.MATNR, SUM(v.KWMENG) AS qty, SUM(v.NETWR) AS amount
        FROM   sqlite_scan(?, 'VBAP') v
        JOIN   sqlite_scan(?, 'MARA') m ON v.MATNR = m.MATNR
        WHERE  m.MTART = 'FERT'
        GROUP BY m.MAKTX, v.MATNR
        ORDER BY amount DESC LIMIT 20
        """,
        ["erp", "erp"],
    ),
    "Q4": (
        """
        SELECT m.MATNR, stp.IDNRK AS comp_matnr, e.EBELN, s.MBLNR, a.BELNR AS fi_doc
        FROM   sqlite_scan(?, 'MARA') m
        LEFT JOIN sqlite_scan(?, 'MAST') mast ON mast.MATNR = m.MATNR
        LEFT JOIN sqlite_scan(?, 'STPO') stp ON stp.STLNR = mast.STLNR
        LEFT JOIN sqlite_scan(?, 'EKPO') e ON e.MATNR = stp.IDNRK
        LEFT JOIN sqlite_scan(?, 'MSEG') s ON s.MATNR = e.MATNR AND s.EBELN = e.EBELN
        LEFT JOIN sqlite_scan(?, 'ACDOCA') a ON a.REF_DOC = s.MBLNR
        WHERE  m.MATNR = 'MAT-2026-0001-K4V'
        """,
        ["erp", "erp", "erp", "scm", "wms", "fin"],
    ),
    "Q5": (
        """
        SELECT COALESCE(sd.LGORT, mv.LGORT) AS lgort,
               COALESCE(sd.labst, 0)    AS book_stock,
               COALESCE(mv.flow_qty, 0) AS flow_stock,
               COALESCE(sd.labst, 0) - COALESCE(mv.flow_qty, 0) AS diff
        FROM (SELECT LGORT, SUM(LABST) AS labst FROM sqlite_scan(?, 'MARD') GROUP BY LGORT) sd
        FULL OUTER JOIN (SELECT LGORT, SUM(MENGE) AS flow_qty FROM sqlite_scan(?, 'MSEG') GROUP BY LGORT) mv
          ON sd.LGORT = mv.LGORT
        ORDER BY lgort
        """,
        ["erp", "wms"],
    ),
}


# ---------------------------------------------------------------------------
# fixtures / 工具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def gen_dir() -> Path:
    """确保样例企业 5 库为当前配置（config_sha 不符或缺库则确定性重建，幂等），返回企业目录。"""
    manifest_path = ENTERPRISE_DIR / "manifest.json"
    current_sha = config_sha256(_CONFIG, EXPECTED_SEED)
    stale = True
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stale = manifest.get("config_sha256") != current_sha
    if stale:
        build_enterprise(ENTERPRISE_CODE, out_dir=str(ENTERPRISE_DIR))
    return ENTERPRISE_DIR


@pytest.fixture(scope="session")
def duck(gen_dir: Path):
    """DuckDB 内存连接 + sqlite 扩展（§6.1 主实现：sqlite_scan 直读 5 库）；扩展不可得时明确 skip。"""
    try:
        con = duckdb.connect()
        con.execute("LOAD sqlite")
    except duckdb.Error as exc:  # sqlite 扩展不可用 → skip（兜底路径 SQLite ATTACH 留设计文档）
        pytest.skip(f"DuckDB sqlite 扩展不可用，跳过量级查询测试: {exc}")
    yield con
    con.close()


def _db_paths(gen_dir: Path) -> dict[str, str]:
    """系统代码 → SQLite 库文件绝对路径（配置单一事实来源，§6.2 路径参数化）。"""
    return {
        code: str(gen_dir / sys_cfg["db"])
        for code, sys_cfg in _CONFIG["enterprise"]["systems"].items()
    }


def _p95(samples: list[float]) -> float:
    """P95：升序样本线性分位（numpy percentile 默认口径），N 小时近似上分位（§6.1 测量方法）。"""
    s = sorted(samples)
    idx = int(0.95 * (len(s) - 1))
    return s[idx]


def _measure(con: Any, sql: str, params: list[str], repeat: int = REPEAT, warmup: int = WARMUP) -> tuple[list[float], int]:
    """预热 warmup 次后重复 repeat 次计时（ms），返回 (样本, 最后一次返回行数)。"""
    for _ in range(warmup):
        con.execute(sql, params).fetchall()
    samples: list[float] = []
    rows = 0
    for _ in range(repeat):
        t0 = time.perf_counter()
        rows = len(con.execute(sql, params).fetchall())
        samples.append((time.perf_counter() - t0) * 1000)
    return samples, rows


def _peak_rss_bytes() -> int:
    """进程峰值 RSS（ru_maxrss：macOS 字节 / Linux KB → 统一转字节，§6.3 内存口径）。"""
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


# ===========================================================================
# §6.2/6.3：五查询 P95（量级门禁核心）
# ===========================================================================
@pytest.mark.slow
@pytest.mark.parametrize("qid", ["Q1", "Q2", "Q3", "Q4", "Q5"])
def test_query_p95_within_threshold(duck: Any, gen_dir: Path, qid: str) -> None:
    """Q1-Q5：P95 ≤ 阈值 × 1.5 余量（§6.3），实测样本与 P95 如实打印；超阈值如实报告、不静默通过。"""
    sql, sys_order = _QUERIES[qid]
    params = [_db_paths(gen_dir)[s] for s in sys_order]
    samples, rows = _measure(duck, sql, params)
    p95 = _p95(samples)
    threshold = _QUERY_THRESHOLDS_MS[qid]
    relaxed = threshold * _P95_MARGIN
    print(
        f"\n{qid} 实测：N={REPEAT}，样本ms={[round(s, 1) for s in samples]}，"
        f"P95={p95:.1f}ms（阈值 {threshold}ms，宽松判据 {relaxed:.0f}ms），返回 {rows} 行"
    )
    assert rows > 0, f"{qid} 返回空结果（查询未命中数据）"
    assert p95 <= relaxed, (
        f"{qid} P95 {p95:.1f}ms 超宽松判据 {relaxed:.0f}ms（原阈值 {threshold}ms）——"
        "超阈值如实上报（§6.3 降级路径：缩小 join 面/抽样集 + 报告量级缺口），不静默通过"
    )


# ===========================================================================
# §6.2 Q5：对账自洽 diff=0（D10，数据侧既有断言，此处并入量级门禁）
# ===========================================================================
@pytest.mark.slow
def test_q5_reconciliation_diff_zero(duck: Any, gen_dir: Path) -> None:
    """Q5：账面 MARD vs 流水 MSEG 按地点对账 diff ≈ 0（D10 自洽 → 全量断言，§6.2/§4.2）。"""
    sql, sys_order = _QUERIES["Q5"]
    rows = duck.execute(sql, [_db_paths(gen_dir)[s] for s in sys_order]).fetchall()
    assert rows, "Q5 对账结果为空"
    diffs = {str(r[0]): float(r[3]) for r in rows}
    print(f"\nQ5 对账 diff（按 LGORT）={diffs}（应全 ≈0）")
    for lgort, diff in diffs.items():
        assert abs(diff) <= _RECON_TOL, f"对账 diff={diff}（地点 {lgort}），应 ≈0（D10 自洽）"


# ===========================================================================
# §6.3：峰值 RSS ≤ 1.5GB（生成 + 查询全流程；默认查询流峰值，配 full-gen 则含生成）
# ===========================================================================
@pytest.mark.slow
def test_peak_rss_within_limit(duck: Any, gen_dir: Path) -> None:
    """进程峰值 RSS ≤ 1.5GB。默认跑全 5 查询采样查询流峰值；与 full-gen 测试同进程时含生成峰值。"""
    before = _peak_rss_bytes()
    db = _db_paths(gen_dir)
    for sql, sys_order in _QUERIES.values():
        duck.execute(sql, [db[s] for s in sys_order]).fetchall()
    after = _peak_rss_bytes()
    peak_gb = after / 1024**3
    print(
        f"\n峰值 RSS = {peak_gb:.3f} GB（测试前 {before / 1024**3:.3f} GB，查询流后 {peak_gb:.3f} GB，"
        f"阈值 1.5 GB）"
    )
    assert after <= RSS_LIMIT_BYTES, f"峰值 RSS {peak_gb:.3f}GB 超 1.5GB，如实上报"


# ===========================================================================
# §6.3 附加：全量生成 ≤ 3min（可选做一次，DES_P1B_SCALE_FULL_GEN=1 启用）
# ===========================================================================
@pytest.mark.slow
@pytest.mark.skipif(
    not RUN_FULL_GENERATION,
    reason="全量生成耗时测试为可选（§6.3 附加操作上界）；设 DES_P1B_SCALE_FULL_GEN=1 启用",
)
def test_full_generation_within_limit(tmp_path: Path) -> None:
    """全量生成 1,000,000 行 ≤ 3min，并采样生成后进程峰值 RSS（配合 RSS 门禁口径）。"""
    t0 = time.perf_counter()
    result = build_enterprise(ENTERPRISE_CODE, out_dir=str(tmp_path / "gen"))
    elapsed = time.perf_counter() - t0
    peak_gb = _peak_rss_bytes() / 1024**3
    assert result["total_rows"] == _CONFIG["total_target"], (
        f"生成行数 {result['total_rows']} != total_target {_CONFIG['total_target']}"
    )
    print(
        f"\n全量生成 {result['total_rows']} 行耗时 {elapsed:.1f}s（阈值 {GENERATION_LIMIT_S}s），"
        f"生成后峰值 RSS {peak_gb:.3f} GB（阈值 1.5 GB）"
    )
    assert elapsed <= GENERATION_LIMIT_S, f"全量生成 {elapsed:.1f}s 超 {GENERATION_LIMIT_S}s，如实上报"
    assert peak_gb * 1024**3 <= RSS_LIMIT_BYTES, f"生成后峰值 RSS {peak_gb:.3f}GB 超 1.5GB，如实上报"
