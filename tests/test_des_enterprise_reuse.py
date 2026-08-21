"""S2 P1b DES 第二企业模板复用（R7）——「同模板不同企业」复用性可机验断言（scale=0.025，~25,000 行）。

对照 docs/P1b-DES-横向铺开设计_v0.1.md（§7.2 扩展点 / §8 R7 第二企业样例）：
- 模板复用：nh_heavy 生效配置 = 加载器 deep_merge(行业模板默认, 企业覆盖层)；模板默认
  （rate=0.15 / coding.master_pattern / 18 表注册表行数/pk/depends_on/fk）原样继承，企业覆盖
  （code_prefix=NH / seed=20260915 / legacy_prefix=NH）生效 —— 企业层只声明差异，复用成立；
- 小规模生成确定性：build_enterprise(nh_heavy, scale=0.025) 两次 → config_sha256 / 18 表
  table_sha256 逐一相同；改 seed → 全变（§5.1 约定 1-5；确定性属性与规模无关，两档测试制度 §7）；
- D 门禁（小规模全量）：D1-D8 全外键 LEFT JOIN 空侧孤儿 = 0、D9 单位一致、D10 对账 diff=0（§4.2）；
- B2：MARA.BISMT 注入精确 round(N×rate)（200 × 15% = 精确 30，配置驱动）；
- 编码：MAT-2026-NNNN-CCC 全匹配（A1）、YYYY = 配置年（A3）、NNNN 物料宇宙唯一、
  BISMT 旧码全为 NH- 前缀且无 HC 残留（第二企业专属：旧码前缀随企业切换，无首企业残留）。
量级门禁（§6 五查询 P95 / 1M 全量）不参与（R7：不参与 1M 门禁，避免稀释量级）；本文件全部在
临时目录小规模生成，不写 data/（生成器确定性，结果与提交样本同配置同 seed 逐位一致）。
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.des.config import config_sha256, load_config
from src.des.generate import build_enterprise
from src.des.manifest import read_table_rows, table_sha256

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "nh_heavy"
EXPECTED_SEED = 20260915
# R7 第二企业样例规模：1,000,000 × 0.025 = 25,000 行（提交样本同口径；量级门禁不参与）
SCALE = 0.025
# 生效配置（模板层 + 企业覆盖层合并）：全量（复用断言）与小规模（生成/D 门禁）各缓存一份
_CONFIG = load_config(ENTERPRISE_CODE)
_CONFIG_SMALL = load_config(ENTERPRISE_CODE, scale=SCALE)
_TEMPLATE = yaml.safe_load(
    (ROOT / "data" / "des" / "des_industry_template.yaml").read_text(encoding="utf-8")
)
TABLE_IDS = sorted(
    f"{code}.{name}"
    for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items()
    for name in sys_cfg["tables"]
)
# 期望值从配置读取（单一事实来源 = 配置，§7.3）：MARA 200 × 0.15 → 精确 30
_MARA_SMALL = _CONFIG_SMALL["enterprise"]["systems"]["erp"]["tables"]["MARA"]
EXPECTED_INJECTED = round(
    _MARA_SMALL["row_count"] * _CONFIG_SMALL["injection"]["multi_code"]["rate"]
)
MASTER_RE = re.compile(r"^MAT-\d{4}-\d{4}-[A-Z0-9]{3}$")
# 旧码格式 = 模板 legacy_pattern "{prefix}-{year}{seq:05d}" 代入 prefix=NH、year=2026 → NH-2026XXXXX
# （NH- + {year:04d}{seq:05d} = NH- + 9 位数字）
NH_LEGACY_RE = re.compile(r"^NH-\d{9}$")

# D 门禁 D1-D8 全外键检查清单（§4.2，口径与 test_des_p1b_data.py 完全一致）：
# (子系统, 子表, 子列, 父系统, 父表, 父列, 子行过滤 child_where)
D_CHECKS: dict[str, list[tuple[str, str, str, str, str, str, str | None]]] = {
    "D1": [
        ("mes", "MPLA", "MATNR", "erp", "MARA", "MATNR", None),
        ("wms", "WMMD", "MATNR", "erp", "MARA", "MATNR", None),
    ],
    "D2": [
        ("erp", "MARC", "MATNR", "erp", "MARA", "MATNR", None),
        ("erp", "MARD", "MATNR", "erp", "MARA", "MATNR", None),
        ("erp", "MAST", "MATNR", "erp", "MARA", "MATNR", None),
    ],
    "D3": [
        ("erp", "STPO", "IDNRK", "erp", "MARA", "MATNR", None),
        ("erp", "STPO", "STLNR", "erp", "MAST", "STLNR", None),
    ],
    "D4": [
        ("scm", "EKKO", "LIFNR", "scm", "LFA1", "LIFNR", None),
        ("scm", "EKPO", "EBELN", "scm", "EKKO", "EBELN", None),
        ("scm", "EKPO", "MATNR", "erp", "MARA", "MATNR", None),
    ],
    "D5": [
        ("erp", "VBAK", "KUNNR", "erp", "KNA1", "KUNNR", None),
        ("erp", "VBAP", "VBELN", "erp", "VBAK", "VBELN", None),
        ("erp", "VBAP", "MATNR", "erp", "MARA", "MATNR", None),
    ],
    "D6": [
        ("mes", "AUFK", "MATNR", "erp", "MARA", "MATNR", None),
        ("mes", "AFPO", "AUFNR", "mes", "AUFK", "AUFNR", None),
        ("mes", "AFPO", "MATNR", "erp", "MARA", "MATNR", None),
        ("mes", "COFV", "AUFNR", "mes", "AUFK", "AUFNR", None),
    ],
    "D7": [
        ("wms", "MSEG", "MATNR", "erp", "MARA", "MATNR", None),
        ("wms", "MSEG", "EBELN", "scm", "EKKO", "EBELN", "c.EBELN IS NOT NULL"),
        ("wms", "MSEG", "AUFNR", "mes", "AUFK", "AUFNR", "c.AUFNR IS NOT NULL"),
    ],
    "D8": [
        ("fin", "ACDOCA", "REF_DOC", "erp", "VBAK", "VBELN", "c.REF_TYPE = 'SO'"),
        ("fin", "ACDOCA", "REF_DOC", "scm", "EKKO", "EBELN", "c.REF_TYPE = 'PO'"),
        ("fin", "ACDOCA", "REF_DOC", "wms", "MSEG", "MBLNR", "c.REF_TYPE = 'MV'"),
    ],
}


# ---------------------------------------------------------------------------
# fixtures / 工具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def nh_dir(tmp_path_factory) -> Path:
    """小规模（scale=0.025，~25,000 行）确定性生成 nh_heavy 到临时目录（不写 data/）。"""
    out = tmp_path_factory.mktemp("nh_reuse")
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out), scale=SCALE)
    return out


def _db_path(gen_dir: Path, sys_name: str) -> Path:
    """系统 → SQLite 库文件路径（配置单一事实来源）。"""
    return gen_dir / _CONFIG_SMALL["enterprise"]["systems"][sys_name]["db"]


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _escaped(path: Path) -> str:
    """SQL 字面量转义（ATTACH/路径串用）。"""
    return str(path).replace("'", "''")


def _read(gen_dir: Path, sys_name: str, table: str) -> list[dict]:
    """按主键升序读取表全行（dict 列表，read_table_rows 封装）。"""
    spec = _CONFIG_SMALL["enterprise"]["systems"][sys_name]["tables"][table]
    return read_table_rows(_db_path(gen_dir, sys_name), table, spec["pk"])


def _orphan_count(
    child_db: Path,
    child_table: str,
    child_col: str,
    parent_db: Path | None,
    parent_table: str,
    parent_col: str,
    child_where: str | None = None,
) -> int:
    """LEFT JOIN 空侧孤儿计数（§4.2 口径）：父表为空的行数；跨库 ATTACH，同库直接引用。"""
    conn = _connect(child_db)
    try:
        parent_ref = parent_table
        if parent_db is not None and parent_db.resolve() != child_db.resolve():
            conn.execute(f"ATTACH DATABASE '{_escaped(parent_db)}' AS par")
            parent_ref = f"par.{parent_table}"
        sql = (
            f"SELECT COUNT(*) FROM {child_table} c "
            f"LEFT JOIN {parent_ref} p ON c.{child_col} = p.{parent_col} "
            f"WHERE p.{parent_col} IS NULL"
        )
        if child_where:
            sql += f" AND ({child_where})"
        return int(conn.execute(sql).fetchone()[0])
    finally:
        conn.close()


def _assert_no_orphans(
    gen_dir: Path,
    gate: str,
    checks: list[tuple[str, str, str, str, str, str, str | None]],
) -> None:
    """gate 内逐条 FK 断言 LEFT JOIN 空侧孤儿 = 0，失败时带子检查上下文。"""
    for (
        child_sys,
        child_tbl,
        child_col,
        parent_sys,
        parent_tbl,
        parent_col,
        child_where,
    ) in checks:
        n = _orphan_count(
            _db_path(gen_dir, child_sys),
            child_tbl,
            child_col,
            _db_path(gen_dir, parent_sys),
            parent_tbl,
            parent_col,
            child_where,
        )
        assert n == 0, (
            f"{gate} {child_sys}.{child_tbl}.{child_col} → {parent_sys}.{parent_tbl}.{parent_col} "
            f"孤儿 {n}（应 0）"
        )


def _all_table_shas(db_dir: Path) -> dict[str, str]:
    """{18 表 table_id: table_sha256}（按各表主键排序的 canonical dump，§5.1）。"""
    return {
        f"{code}.{name}": table_sha256(_read(db_dir, code, name))
        for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items()
        for name in sys_cfg["tables"]
    }


# ===========================================================================
# 模板复用（R7）：模板默认原样继承 + 企业覆盖生效 + 企业层只声明差异
# ===========================================================================
def test_config_inherits_template_defaults() -> None:
    """模板默认原样继承：rate=0.15 / coding.master_pattern / 18 表注册表（行数/pk/depends_on/fk）。"""
    tpl_multi = _TEMPLATE["injection"]["multi_code"]
    assert _CONFIG["injection"]["multi_code"]["rate"] == tpl_multi["rate"] == 0.15
    assert _CONFIG["injection"]["multi_code"]["field"] == tpl_multi["field"] == "BISMT"
    assert (
        _CONFIG["injection"]["multi_code"]["legacy_pattern"]
        == tpl_multi["legacy_pattern"]
    )
    assert _CONFIG["coding"]["master_pattern"] == _TEMPLATE["coding"]["master_pattern"]
    assert _CONFIG["coding"]["year"] == _TEMPLATE["coding"]["year"] == 2026
    # 18 表注册表：模板表集合与生效配置完全一致（企业层未增删、未改行数/主键/依赖/FK）
    tpl_tables = {
        f"{code}.{name}": spec
        for code, sys_cfg in _TEMPLATE["enterprise"]["systems"].items()
        for name, spec in sys_cfg["tables"].items()
    }
    assert len(TABLE_IDS) == 18
    assert set(TABLE_IDS) == set(tpl_tables)
    for tid in TABLE_IDS:
        code, name = tid.split(".", 1)
        eff = _CONFIG["enterprise"]["systems"][code]["tables"][name]
        tpl = tpl_tables[tid]
        assert eff["row_count"] == tpl["row_count"], f"{tid} 行数未继承模板"
        assert eff["pk"] == list(tpl["pk"]), f"{tid} pk 未继承模板"
        assert eff["depends_on"] == list(tpl["depends_on"]), (
            f"{tid} depends_on 未继承模板"
        )
        assert eff["fk"] == dict(tpl.get("fk") or {}), f"{tid} fk 未继承模板"


def test_enterprise_overrides_apply() -> None:
    """企业覆盖生效：code_prefix=NH / seed=20260915 / legacy_prefix=NH / 企业名。"""
    ent = _CONFIG["enterprise"]
    assert ent["code"] == ENTERPRISE_CODE
    assert ent["code_prefix"] == "NH"
    assert ent["seed"] == EXPECTED_SEED
    assert _CONFIG["injection"]["multi_code"]["legacy_prefix"] == "NH"
    assert ent["name"] == "宁海重工（Ninghai Heavy Industry）"


def test_enterprise_declares_only_differences() -> None:
    """纯配置复用：nh_heavy 企业层只声明差异（未重写模板的表注册表/注入率/主码格式）。"""
    ent_yaml = yaml.safe_load(
        (
            ROOT
            / "data"
            / "des"
            / "enterprises"
            / ENTERPRISE_CODE
            / "des_enterprise.yaml"
        ).read_text(encoding="utf-8")
    )["enterprise"]
    assert "systems" not in ent_yaml, "企业层不应重写 18 表注册表（应继承模板）"
    assert "coding" not in ent_yaml, "企业层不应重写主码格式（应继承模板）"
    multi = ent_yaml["injection"]["multi_code"]
    assert "rate" not in multi, "企业层不应重写注入率（应继承模板 0.15）"
    assert "legacy_pattern" not in multi, "企业层不应重写旧码格式（应继承模板）"


# ===========================================================================
# 小规模生成确定性（§5.1 约定 1-5）：同 seed 两次生成 sha 相同；改 seed → 全变
# ===========================================================================
def test_determinism_same_seed_all_18_tables(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """同 seed 同配置（scale=0.025）两次生成 → config_sha256 / 18 表 table_sha256 逐一相同。"""
    out1, out2 = tmp_path_factory.mktemp("nh_g1"), tmp_path_factory.mktemp("nh_g2")
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out1), scale=SCALE)
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out2), scale=SCALE)
    m1 = json.loads((out1 / "manifest.json").read_text(encoding="utf-8"))
    m2 = json.loads((out2 / "manifest.json").read_text(encoding="utf-8"))
    assert m1["config_sha256"] == m2["config_sha256"]
    assert m1["total_rows"] == _CONFIG_SMALL["total_target"] == 25_000, (
        "小规模行数 ≠ 配置 total_target"
    )
    assert _all_table_shas(out1) == _all_table_shas(out2)


def test_determinism_changed_seed_all_shas_change(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """改 seed → config_sha256 变，且 18 表 table_sha256 全变（每表独立 RNG 流，约定 1）。"""
    assert config_sha256(_CONFIG_SMALL, EXPECTED_SEED) != config_sha256(
        _CONFIG_SMALL, EXPECTED_SEED + 1
    )
    base = tmp_path_factory.mktemp("nh_base")
    alt = tmp_path_factory.mktemp("nh_alt")
    build_enterprise(ENTERPRISE_CODE, out_dir=str(base), scale=SCALE)
    build_enterprise(
        ENTERPRISE_CODE, out_dir=str(alt), scale=SCALE, seed=EXPECTED_SEED + 1
    )
    base_shas, alt_shas = _all_table_shas(base), _all_table_shas(alt)
    for tid in TABLE_IDS:
        assert alt_shas[tid] != base_shas[tid], f"改 seed 后 {tid} sha 未变"


# ===========================================================================
# 编码（第二企业专属）：MAT-2026-NNNN-CCC 全匹配 + BISMT 旧码全 NH- 无 HC 残留
# ===========================================================================
def test_a1_matnr_pattern_year_and_unique(nh_dir: Path) -> None:
    """编码 A1+A3：全部 MATNR 匹配 MAT-YYYY-NNNN-CCC，YYYY = 配置年 2026，NNNN 物料宇宙唯一。"""
    rows = _read(nh_dir, "erp", "MARA")
    year = _CONFIG_SMALL["coding"]["year"]
    assert year == 2026
    seqs: list[int] = []
    for r in rows:
        assert MASTER_RE.match(r["MATNR"]), f"MATNR 非法: {r['MATNR']}"
        assert int(r["MATNR"][4:8]) == year, f"YYYY ≠ coding.year: {r['MATNR']}"
        seqs.append(int(r["MATNR"][9:13]))
    assert len(seqs) == len(set(seqs)), "NNNN 在企业物料宇宙内重复（应唯一）"


def test_a4_bismt_all_nh_prefix_no_hc_residue(nh_dir: Path) -> None:
    """编码 A4（第二企业）：BISMT 非空行全为 NH- 前缀旧码（格式 NH-{year}{seq:05d}）、互异、无 HC 残留。"""
    rows = _read(nh_dir, "erp", "MARA")
    injected = [r["BISMT"] for r in rows if r["BISMT"] is not None]
    assert len(injected) == EXPECTED_INJECTED, f"BISMT 非空行数应为 {EXPECTED_INJECTED}"
    assert len(set(injected)) == len(injected), "旧码存在重复（应互异）"
    for code in injected:
        assert code.startswith("NH-"), f"旧码前缀非 NH: {code}"
        assert NH_LEGACY_RE.match(code), f"旧码格式不符 NH-{'{year}{seq:05d}'}: {code}"
        assert not code.startswith("HC-"), f"残留首企业 HC 前缀旧码: {code}"
        assert not MASTER_RE.match(code), f"旧码不应匹配主码格式（格式互斥）: {code}"


# ===========================================================================
# B2：注入精确命中（§7.1 兼容红线，round(N×rate)）
# ===========================================================================
def test_b2_exact_injected_count(nh_dir: Path) -> None:
    """B2：count(MARA.BISMT NOT NULL) == round(N × rate)（200 × 0.15 = 精确 30）。"""
    rows = _read(nh_dir, "erp", "MARA")
    injected = sum(1 for r in rows if r.get("BISMT") is not None)
    rate = _CONFIG_SMALL["injection"]["multi_code"]["rate"]
    assert injected == round(len(rows) * rate)
    assert injected == EXPECTED_INJECTED


# ===========================================================================
# D 门禁（小规模全量，§4.2）：D1-D8 全外键无孤儿 / D9 单位一致 / D10 对账 diff=0
# ===========================================================================
@pytest.mark.parametrize("gate_id", sorted(D_CHECKS))
def test_d_gates_no_orphans(nh_dir: Path, gate_id: str) -> None:
    """D1-D8：逐门禁断言全外键 LEFT JOIN 空侧孤儿 = 0（口径与 test_des_p1b_data.py 一致）。"""
    _assert_no_orphans(nh_dir, gate_id, D_CHECKS[gate_id])


def test_d9_wmmd_meins_equals_mara(nh_dir: Path) -> None:
    """D9：同物料 WMMD.MEINS = MARA.MEINS（计量单位一致，差异 = 0）。"""
    conn = _connect(_db_path(nh_dir, "wms"))
    try:
        conn.execute(f"ATTACH DATABASE '{_escaped(_db_path(nh_dir, 'erp'))}' AS erp")
        n = conn.execute(
            "SELECT COUNT(*) FROM WMMD w JOIN erp.MARA m ON w.MATNR = m.MATNR "
            "WHERE w.MEINS <> m.MEINS"
        ).fetchone()[0]
        assert int(n) == 0
    finally:
        conn.close()


def test_d10_inventory_reconciliation(nh_dir: Path) -> None:
    """D10：对账自洽 —— Σ MSEG.MENGE（按 MATNR+LGORT）= MARD.LABST，diff = 0（§4.2 Q5 口径）。"""
    conn = _connect(_db_path(nh_dir, "erp"))
    try:
        conn.execute(f"ATTACH DATABASE '{_escaped(_db_path(nh_dir, 'wms'))}' AS wms")
        # (a) 账面侧：每组 (MATNR,LGORT) 账面 LABST 与流水净变差额 > 1e-6 的行数 = 0
        diff_rows = conn.execute(
            "SELECT COUNT(*) FROM ("
            "  SELECT d.MATNR, d.LGORT, d.LABST, COALESCE(mv.flow, 0) AS flow"
            "  FROM MARD d"
            "  LEFT JOIN (SELECT MATNR, LGORT, SUM(MENGE) AS flow"
            "             FROM wms.MSEG GROUP BY MATNR, LGORT) mv"
            "    ON mv.MATNR = d.MATNR AND mv.LGORT = d.LGORT"
            ") WHERE ABS(LABST - flow) > 1e-6"
        ).fetchone()[0]
        assert int(diff_rows) == 0, (
            f"D10 账面≠流水 的 (MATNR,LGORT) 组 {int(diff_rows)} 个（应 0）"
        )
        # (b) 流水侧：流水存在但账面缺失的 (MATNR,LGORT) 组 = 0（反向无孤儿）
        missing = conn.execute(
            "SELECT COUNT(*) FROM ("
            "  SELECT MATNR, LGORT FROM wms.MSEG GROUP BY MATNR, LGORT"
            ") mv LEFT JOIN MARD d ON d.MATNR = mv.MATNR AND d.LGORT = mv.LGORT"
            " WHERE d.MATNR IS NULL"
        ).fetchone()[0]
        assert int(missing) == 0, (
            f"D10 流水无账面 的 (MATNR,LGORT) 组 {int(missing)} 个（应 0）"
        )
    finally:
        conn.close()
