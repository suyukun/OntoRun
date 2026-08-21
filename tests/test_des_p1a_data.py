"""S2 P1a DES 垂直切片 —— 数据侧门禁 A/B/C/D 可机验断言（设计文档 §6）。

对照 docs/P1a-DES-配置与表结构设计_v0.1.md §6（门禁 → 检查项 → 断言）：
- 门禁 A（编码 100% 合规）：A1-A4；
- 门禁 B（注入率 ±2%）：B1-B4；
- 门禁 C（确定性 SHA256）：C1-C4；
- 门禁 D（跨系统一致性）：D1-D4。
确定性可复跑：B3/C1/C2/C3 使用临时目录小规模（scale=SMALL_SCALE，~3000 行，生成 <1s）独立生成
对比（确定性属性与规模无关，测试分层 §7 两档测试制度）；其余读样例企业产物（缺则确定性重建）。
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path

import pytest
import yaml

from src.des.config import config_sha256, load_config
from src.des.generate import build_enterprise, check_code
from src.des.manifest import read_table_rows, table_sha256

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_DIR = ROOT / "data" / "des" / "enterprises" / "hc_precision"
ENTERPRISE_CODE = "hc_precision"
EXPECTED_SEED = 20260821
# 行数/注入期望值从配置读取（单一事实来源 = 配置，设计 §7.3）：
# expected = 配置 row_count（erp.MARA = 8,000）；expected_injected = round(row_count × rate)（15% → 1,200）。
_CONFIG = load_config(ENTERPRISE_CODE)
EXPECTED_COUNT = _CONFIG["enterprise"]["systems"]["erp"]["tables"]["MARA"]["row_count"]
EXPECTED_RATE = _CONFIG["injection"]["multi_code"]["rate"]
EXPECTED_INJECTED = round(EXPECTED_COUNT * EXPECTED_RATE)
# 小规模确定性测试（测试分层，§7 两档测试制度）：确定性属性与规模无关，B3/C1/C2/C3 用
# scale=SMALL_SCALE（~3000 行，生成 <1s）独立生成对比；其余测试读样例 1M 库保留全量验证。
SMALL_SCALE = 0.003
_CONFIG_SMALL = load_config(ENTERPRISE_CODE, scale=SMALL_SCALE)
EXPECTED_INJECTED_SMALL = round(
    _CONFIG_SMALL["enterprise"]["systems"]["erp"]["tables"]["MARA"]["row_count"]
    * _CONFIG_SMALL["injection"]["multi_code"]["rate"]
)
MASTER_RE = re.compile(r"^MAT-\d{4}-\d{4}-[A-Z0-9]{3}$")

# 系统代码 -> (库文件名, 表名)（设计 §1.3/§5）
SYSTEMS = {
    "erp": ("erp.db", "MARA"),
    "mes": ("mes.db", "MPLA"),
    "wms": ("wms.db", "WMMD"),
}


# ---------------------------------------------------------------------------
# fixtures / 工具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def gen_dir() -> Path:
    """确保样例企业库为当前配置（config_sha 不符或缺库则确定性重建，幂等），返回企业目录。"""
    manifest_path = ENTERPRISE_DIR / "manifest.json"
    current_sha = config_sha256(_CONFIG, EXPECTED_SEED)
    stale = True
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stale = manifest.get("config_sha256") != current_sha
    if stale:
        build_enterprise(ENTERPRISE_CODE, out_dir=str(ENTERPRISE_DIR))
    return ENTERPRISE_DIR


@pytest.fixture()
def config() -> dict:
    """hc_precision 生效配置（模板层 + 企业覆盖层合并后，模块级缓存）。"""
    return _CONFIG


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _rows(db_path: Path, table: str, order_by: str = "MATNR") -> list[sqlite3.Row]:
    """读取表全行（按 MATNR 升序），自动关闭连接。"""
    conn = _connect(db_path)
    try:
        return conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    finally:
        conn.close()


def _table_pk(config: dict, sys_name: str) -> list[str]:
    """某系统表的配置主键列（read_table_rows/manifest 泛化排序键，设计 §5.1）。"""
    _, tbl = SYSTEMS[sys_name]
    return config["enterprise"]["systems"][sys_name]["tables"][tbl]["pk"]


def _table_shas(db_dir: Path, config: dict) -> dict[str, str]:
    """{系统名: 该表 table_sha256}，用于 C 门禁对比。"""
    return {
        name: table_sha256(read_table_rows(db_dir / db, tbl, _table_pk(config, name)))
        for name, (db, tbl) in SYSTEMS.items()
    }


# ===========================================================================
# 门禁 A：编码 100% 合规
# ===========================================================================
def test_a1_all_matnr_match_pattern(gen_dir: Path) -> None:
    r"""A1：全部 MATNR（三表）匹配 ^MAT-\d{4}-\d{4}-[A-Z0-9]{3}$。"""
    for db_name, table in SYSTEMS.values():
        for row in _rows(gen_dir / db_name, table):
            assert MASTER_RE.match(row["MATNR"]), f"{table}.MATNR 非法: {row['MATNR']}"


def test_a2_ccc_recompute_equals_stored(gen_dir: Path) -> None:
    """A2：逐行重算 CCC 与存储值相等（100%）。"""
    for row in _rows(gen_dir / "erp.db", "MARA"):
        year = int(row["MATNR"][4:8])
        seq = int(row["MATNR"][9:13])
        assert check_code(year, seq) == row["MATNR"][14:17], f"CCC 不匹配: {row['MATNR']}"


def test_a3_nnnn_unique_and_year_matches_config(gen_dir: Path, config: dict) -> None:
    """A3：NNNN 在企业物料宇宙内无重复；YYYY = 配置 coding.year。"""
    rows = _rows(gen_dir / "erp.db", "MARA")
    seqs = [int(r["MATNR"][9:13]) for r in rows]
    assert len(seqs) == len(set(seqs)), "NNNN 存在重复（物料宇宙内不唯一）"
    expected_year = config["coding"]["year"]
    assert all(int(r["MATNR"][4:8]) == expected_year for r in rows), "存在 YYYY ≠ coding.year 的主码"


def test_a4_bismt_mutually_exclusive_distinct_count(gen_dir: Path) -> None:
    """A4：BISMT 非空行 —— 不匹配主码正则（新旧码格式互斥）、互异、非空行数 = 30。"""
    non_null = [r["BISMT"] for r in _rows(gen_dir / "erp.db", "MARA") if r["BISMT"] is not None]
    assert len(non_null) == EXPECTED_INJECTED, f"BISMT 非空行数应为 {EXPECTED_INJECTED}"
    assert len(set(non_null)) == len(non_null), "BISMT 旧码存在重复（应互异）"
    for code in non_null:
        assert not MASTER_RE.match(code), f"旧码不应匹配主码正则（格式互斥）: {code}"


# ===========================================================================
# 门禁 B：注入率 ±2%
# ===========================================================================
def test_b1_injection_rate_within_tolerance(gen_dir: Path, config: dict) -> None:
    """B1：|注入率 − 配置率| ≤ tolerance（0.02）。"""
    rows = _rows(gen_dir / "erp.db", "MARA")
    count = sum(1 for r in rows if r["BISMT"] is not None)
    multi = config["injection"]["multi_code"]
    assert abs(count / len(rows) - multi["rate"]) <= multi["tolerance"]


def test_b2_exact_round_count(gen_dir: Path, config: dict) -> None:
    """B2：（更紧）count(BISMT NOT NULL) == round(N × rate) == 30。"""
    rows = _rows(gen_dir / "erp.db", "MARA")
    count = sum(1 for r in rows if r["BISMT"] is not None)
    rate = config["injection"]["multi_code"]["rate"]
    assert count == round(len(rows) * rate)
    assert count == EXPECTED_INJECTED


def test_b3_same_seed_same_injected_set(tmp_path: Path) -> None:
    """B3：同 seed 两次生成，BISMT 非空行集（按 MATNR 排序）逐一相等。"""
    out1, out2 = tmp_path / "g1", tmp_path / "g2"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out1), scale=SMALL_SCALE)
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out2), scale=SMALL_SCALE)
    set1 = [(r["MATNR"], r["BISMT"]) for r in _rows(out1 / "erp.db", "MARA") if r["BISMT"] is not None]
    set2 = [(r["MATNR"], r["BISMT"]) for r in _rows(out2 / "erp.db", "MARA") if r["BISMT"] is not None]
    assert set1 == set2
    assert len(set1) == EXPECTED_INJECTED_SMALL


def test_b4_no_malformed_rows(gen_dir: Path) -> None:
    """B4：注入行每行至多一个旧码；无同时缺 MATNR 或缺 BISMT 的畸形行。"""
    rows = _rows(gen_dir / "erp.db", "MARA")
    for r in rows:
        assert r["MATNR"], "存在缺 MATNR 的行"
        if r["BISMT"] is not None:
            assert r["BISMT"] != r["MATNR"], f"旧码与主码不应相同（多码冲突点）: {r['MATNR']}"
        else:
            assert r["BISMT"] is None, "非注入行 BISMT 应为 NULL"
    injected = [r for r in rows if r["BISMT"] is not None]
    assert len(injected) == EXPECTED_INJECTED
    assert len(rows) - len(injected) == EXPECTED_COUNT - EXPECTED_INJECTED


# ===========================================================================
# 门禁 C：确定性 SHA256
# ===========================================================================
def test_c1_same_seed_same_config_hashes_equal(tmp_path: Path) -> None:
    """C1：同 seed 同配置两次生成，三表 table_sha256 逐一相同。"""
    out1, out2 = tmp_path / "g1", tmp_path / "g2"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out1), scale=SMALL_SCALE)
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out2), scale=SMALL_SCALE)
    assert _table_shas(out1, _CONFIG) == _table_shas(out2, _CONFIG)


def test_c2_seed_and_config_change_hashes(tmp_path: Path, config: dict) -> None:
    """C2：改 seed → 三表 sha 全变；改配置（rate）→ config_sha256 变、MARA sha 变（配置参与 hash）。"""
    base = tmp_path / "base"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(base), seed=EXPECTED_SEED, scale=SMALL_SCALE)
    base_shas = _table_shas(base, config)

    # (a) 改 seed → 三表 sha 全变
    alt = tmp_path / "alt_seed"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(alt), seed=EXPECTED_SEED + 1, scale=SMALL_SCALE)
    alt_shas = _table_shas(alt, config)
    for name in SYSTEMS:
        assert alt_shas[name] != base_shas[name], f"改 seed 后 {name} sha 未变"

    # (b) 改配置（rate 0.15 → 0.20）→ config_sha256 变、生成结果 erp.MARA sha 变
    data = yaml.safe_load((ENTERPRISE_DIR / "des_enterprise.yaml").read_text(encoding="utf-8"))
    data["enterprise"]["injection"]["multi_code"]["rate"] = 0.20
    mod_path = tmp_path / "des_enterprise_rate020.yaml"
    mod_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    mod_cfg = load_config(ENTERPRISE_CODE, config_file=str(mod_path), scale=SMALL_SCALE)
    assert mod_cfg["injection"]["multi_code"]["rate"] == 0.20
    assert config_sha256(mod_cfg, EXPECTED_SEED) != config_sha256(_CONFIG_SMALL, EXPECTED_SEED)
    alt_cfg = tmp_path / "alt_cfg"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(alt_cfg), seed=EXPECTED_SEED, config_file=str(mod_path), scale=SMALL_SCALE)
    assert _table_shas(alt_cfg, config)["erp"] != base_shas["erp"], "改配置后 erp.MARA sha 未变"


def test_c3_no_wall_clock_dependence(tmp_path: Path) -> None:
    """C3：两次运行墙钟不同，sha 仍相同（生成不依赖系统时间）。"""
    out1, out2 = tmp_path / "g1", tmp_path / "g2"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out1), scale=SMALL_SCALE)
    time.sleep(1.1)  # 拉大两次运行的墙钟间隔
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out2), scale=SMALL_SCALE)
    assert _table_shas(out1, _CONFIG) == _table_shas(out2, _CONFIG)


def test_c4_manifest_matches_recomputed(gen_dir: Path, config: dict) -> None:
    """C4：manifest.json 记录值与实测重算一致（config_sha/table_sha/行数/注入计数）。"""
    manifest = json.loads((gen_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["enterprise"] == ENTERPRISE_CODE
    assert manifest["seed"] == EXPECTED_SEED
    assert manifest["config_sha256"] == config_sha256(config, EXPECTED_SEED)
    for name, (db, tbl) in SYSTEMS.items():
        rows = read_table_rows(gen_dir / db, tbl, _table_pk(config, name))
        entry = manifest["tables"][f"{name}.{tbl}"]
        assert entry["rows"] == len(rows)
        assert entry["sha256"] == table_sha256(rows)
        if name == "erp":
            assert entry["multi_code_count"] == sum(1 for r in rows if r.get("BISMT"))


# ===========================================================================
# 门禁 D：跨系统一致性（关联口径）
# ===========================================================================
def _orphan_count(attach_db: Path, main_db: Path, left_table: str, right_table: str) -> int:
    """跨库 LEFT JOIN：右表 MATNR 为 NULL 的孤儿数（用 ATTACH 模拟设计 §6-D 的 SQL 口径）。"""
    conn = _connect(main_db)
    try:
        attached = str(attach_db).replace("'", "''")
        conn.execute(f"ATTACH DATABASE '{attached}' AS erp")
        row = conn.execute(
            f"SELECT COUNT(*) AS n FROM {left_table} l "
            f"LEFT JOIN erp.{right_table} r ON l.MATNR = r.MATNR WHERE r.MATNR IS NULL"
        ).fetchone()
        return int(row["n"])
    finally:
        conn.close()


def test_d1_wmmd_no_orphan_vs_mara(gen_dir: Path) -> None:
    """D1：WMMD.MATNR 相对 MARA.MATNR 孤儿 = 0。"""
    assert _orphan_count(gen_dir / "erp.db", gen_dir / "wms.db", "WMMD", "MARA") == 0


def test_d2_mpla_no_orphan_vs_mara(gen_dir: Path) -> None:
    """D2：MPLA.MATNR 相对 MARA.MATNR 孤儿 = 0。"""
    assert _orphan_count(gen_dir / "erp.db", gen_dir / "mes.db", "MPLA", "MARA") == 0


def test_d3_wmmd_meins_equals_mara(gen_dir: Path) -> None:
    """D3：同物料 WMMD.MEINS = MARA.MEINS（计量单位一致）。"""
    conn = _connect(gen_dir / "wms.db")
    try:
        attached = str(gen_dir / "erp.db").replace("'", "''")
        conn.execute(f"ATTACH DATABASE '{attached}' AS erp")
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM WMMD w JOIN erp.MARA m ON w.MATNR = m.MATNR "
            "WHERE w.MEINS <> m.MEINS"
        ).fetchone()
        assert int(row["n"]) == 0
    finally:
        conn.close()


def test_d4_row_counts_111(gen_dir: Path) -> None:
    """D4：MPLA / WMMD 行数 = MARA 行数 = 200（1:1:1 宇宙对齐）。"""
    counts = {name: len(_rows(gen_dir / db, tbl)) for name, (db, tbl) in SYSTEMS.items()}
    assert counts["erp"] == counts["mes"] == counts["wms"] == EXPECTED_COUNT
