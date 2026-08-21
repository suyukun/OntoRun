"""S2 P1b DES 横向铺开 —— 数据侧门禁（行数口径 / 全外键无孤儿 / 对账自洽 / 确定性 SHA256）可机验断言。

对照 docs/P1b-DES-横向铺开设计_v0.1.md（§3.1 分表行数 / §4.2 跨系统无孤儿口径 / §5.1 SHA256 泛化 / §5.2 生成拓扑）：
- 行数口径：18 表各表行数 == 配置 row_count（§3.1），Σ == total_target（1,000,000）；
- B2：MARA.BISMT 非空 == round(row_count × rate)（8,000 × 15% = 精确 1,200，配置驱动）；
- D1-D8：全外键 LEFT JOIN 空侧孤儿 = 0（§4.2；D7 可空字段非空时成立，D8 按 REF_TYPE 多态引用）；
- D9：WMMD.MEINS = MARA.MEINS（计量单位一致，P1a D3 保留）；
- D10：对账自洽 —— Σ MSEG.MENGE（按 MATNR+LGORT）= MARD.LABST，diff = 0（§4.2/§6 Q5）；
- 确定性：同 seed 两次生成 → 18 表 table_sha256 逐一相同（§5.1 约定 1-5）。
量级门禁（§6 五查询 P95 + 内存）由 test_des_p1b_scale.py 承接，本文件不做。
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.des.config import config_sha256, load_config
from src.des.generate import build_enterprise
from src.des.manifest import read_table_rows, table_sha256

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_DIR = ROOT / "data" / "des" / "enterprises" / "hc_precision"
ENTERPRISE_CODE = "hc_precision"
EXPECTED_SEED = 20260821
# 生效配置（模板层 + 企业覆盖层合并后，模块级缓存）：行数/注入期望全部从配置读取，不硬编码。
_CONFIG = load_config(ENTERPRISE_CODE)
TABLE_IDS = sorted(
    f"{code}.{name}"
    for code, sys_cfg in _CONFIG["enterprise"]["systems"].items()
    for name in sys_cfg["tables"]
)


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


def _db_path(gen_dir: Path, config: dict, sys_name: str) -> Path:
    """系统 → SQLite 库文件路径（配置单一事实来源）。"""
    return gen_dir / config["enterprise"]["systems"][sys_name]["db"]


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _escaped(path: Path) -> str:
    """SQL 字面量转义（ATTACH/路径串用）。"""
    return str(path).replace("'", "''")


def _orphan_count(
    child_db: Path,
    child_table: str,
    child_col: str,
    parent_db: Path | None,
    parent_table: str,
    parent_col: str,
    child_where: str | None = None,
) -> int:
    """LEFT JOIN 空侧孤儿计数（§4.2 口径）：父表为空的行数；跨库 ATTACH，同库直接引用。

    child_where：对子表行的附加过滤（如 D7 可空 FK 仅非空行、D8 按 REF_TYPE），
    引用子表列时用别名 c。
    """
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
    config: dict,
    gate: str,
    checks: list[tuple[str, str, str, str, str, str, str | None]],
) -> None:
    """gate 内逐条 FK 断言 LEFT JOIN 空侧孤儿 = 0，失败时带子检查上下文。

    checks 元素：(child_sys, child_table, child_col, parent_sys, parent_table, parent_col, child_where)。
    """
    for child_sys, child_tbl, child_col, parent_sys, parent_tbl, parent_col, child_where in checks:
        child_db = _db_path(gen_dir, config, child_sys)
        parent_db = _db_path(gen_dir, config, parent_sys)
        n = _orphan_count(child_db, child_tbl, child_col, parent_db, parent_tbl, parent_col, child_where)
        assert n == 0, (
            f"{gate} {child_sys}.{child_tbl}.{child_col} → {parent_sys}.{parent_tbl}.{parent_col} "
            f"孤儿 {n}（应 0）"
        )


def _all_table_shas(db_dir: Path, config: dict) -> dict[str, str]:
    """{18 表 table_id: table_sha256}（按各表主键排序的 canonical dump，§5.1）。"""
    return {
        f"{code}.{name}": table_sha256(
            read_table_rows(db_dir / sys_cfg["db"], name, sys_cfg["tables"][name]["pk"])
        )
        for code, sys_cfg in config["enterprise"]["systems"].items()
        for name in sys_cfg["tables"]
    }


# ===========================================================================
# 行数口径（§3.1）：各表 == 配置 row_count，Σ == total_target
# ===========================================================================
@pytest.mark.parametrize("table_id", TABLE_IDS)
def test_row_count_matches_config(gen_dir: Path, config: dict, table_id: str) -> None:
    """18 表各表行数 == 配置 row_count（§3.1 分表行数，配置驱动）。"""
    code, name = table_id.split(".", 1)
    sys_cfg = config["enterprise"]["systems"][code]
    spec = sys_cfg["tables"][name]
    rows = read_table_rows(_db_path(gen_dir, config, code), name, spec["pk"])
    assert len(rows) == spec["row_count"], f"{table_id} 行数 {len(rows)} != 配置 {spec['row_count']}"


def test_total_rows_equals_target(gen_dir: Path, config: dict) -> None:
    """Σ 18 表行数 == total_target（1,000,000，§1.2 量级口径）。"""
    total = sum(
        len(read_table_rows(_db_path(gen_dir, config, code), name, sys_cfg["tables"][name]["pk"]))
        for code, sys_cfg in config["enterprise"]["systems"].items()
        for name in sys_cfg["tables"]
    )
    assert total == config["total_target"], f"Σ行数 {total} != total_target {config['total_target']}"


# ===========================================================================
# B2：注入精确命中（§7.1 兼容红线）
# ===========================================================================
def test_b2_exact_injected_count(gen_dir: Path, config: dict) -> None:
    """B2：（更紧）count(MARA.BISMT NOT NULL) == round(row_count × rate) == 1,200。"""
    mara = config["enterprise"]["systems"]["erp"]["tables"]["MARA"]
    rows = read_table_rows(_db_path(gen_dir, config, "erp"), "MARA", mara["pk"])
    injected = sum(1 for r in rows if r.get("BISMT") is not None)
    rate = config["injection"]["multi_code"]["rate"]
    expected = round(mara["row_count"] * rate)
    assert injected == expected, f"BISMT 非空行数 {injected} != round({mara['row_count']}×{rate}) {expected}"


# ===========================================================================
# D 门禁：全外键无孤儿（§4.2）
# ===========================================================================
def test_d1_mpla_wmmd_no_orphan_vs_mara(gen_dir: Path, config: dict) -> None:
    """D1：MPLA/WMMD.MATNR → MARA.MATNR 孤儿 = 0（P1a 保留）。"""
    _assert_no_orphans(gen_dir, config, "D1", [
        ("mes", "MPLA", "MATNR", "erp", "MARA", "MATNR", None),
        ("wms", "WMMD", "MATNR", "erp", "MARA", "MATNR", None),
    ])


def test_d2_marc_mard_mast_no_orphan_vs_mara(gen_dir: Path, config: dict) -> None:
    """D2：MARC/MARD/MAST.MATNR → MARA.MATNR 孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D2", [
        ("erp", "MARC", "MATNR", "erp", "MARA", "MATNR", None),
        ("erp", "MARD", "MATNR", "erp", "MARA", "MATNR", None),
        ("erp", "MAST", "MATNR", "erp", "MARA", "MATNR", None),
    ])


def test_d3_stpo_no_orphan_vs_mara_mast(gen_dir: Path, config: dict) -> None:
    """D3：STPO.IDNRK → MARA.MATNR；STPO.STLNR → MAST.STLNR 孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D3", [
        ("erp", "STPO", "IDNRK", "erp", "MARA", "MATNR", None),
        ("erp", "STPO", "STLNR", "erp", "MAST", "STLNR", None),
    ])


def test_d4_scm_purchase_no_orphan(gen_dir: Path, config: dict) -> None:
    """D4：EKKO.LIFNR → LFA1.LIFNR；EKPO.EBELN → EKKO.EBELN；EKPO.MATNR → MARA.MATNR 孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D4", [
        ("scm", "EKKO", "LIFNR", "scm", "LFA1", "LIFNR", None),
        ("scm", "EKPO", "EBELN", "scm", "EKKO", "EBELN", None),
        ("scm", "EKPO", "MATNR", "erp", "MARA", "MATNR", None),
    ])


def test_d5_erp_sales_no_orphan(gen_dir: Path, config: dict) -> None:
    """D5：VBAK.KUNNR → KNA1.KUNNR；VBAP.VBELN → VBAK.VBELN；VBAP.MATNR → MARA.MATNR 孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D5", [
        ("erp", "VBAK", "KUNNR", "erp", "KNA1", "KUNNR", None),
        ("erp", "VBAP", "VBELN", "erp", "VBAK", "VBELN", None),
        ("erp", "VBAP", "MATNR", "erp", "MARA", "MATNR", None),
    ])


def test_d6_mes_production_no_orphan(gen_dir: Path, config: dict) -> None:
    """D6：AUFK.MATNR → MARA.MATNR；AFPO.AUFNR → AUFK.AUFNR；AFPO.MATNR → MARA.MATNR；COFV.AUFNR → AUFK.AUFNR。"""
    _assert_no_orphans(gen_dir, config, "D6", [
        ("mes", "AUFK", "MATNR", "erp", "MARA", "MATNR", None),
        ("mes", "AFPO", "AUFNR", "mes", "AUFK", "AUFNR", None),
        ("mes", "AFPO", "MATNR", "erp", "MARA", "MATNR", None),
        ("mes", "COFV", "AUFNR", "mes", "AUFK", "AUFNR", None),
    ])


def test_d7_mseg_no_orphan(gen_dir: Path, config: dict) -> None:
    """D7：MSEG.MATNR → MARA.MATNR；MSEG.EBELN 非空 → EKKO.EBELN；MSEG.AUFNR 非空 → AUFK.AUFNR 孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D7", [
        ("wms", "MSEG", "MATNR", "erp", "MARA", "MATNR", None),
        ("wms", "MSEG", "EBELN", "scm", "EKKO", "EBELN", "c.EBELN IS NOT NULL"),
        ("wms", "MSEG", "AUFNR", "mes", "AUFK", "AUFNR", "c.AUFNR IS NOT NULL"),
    ])


def test_d8_acdoca_ref_no_orphan(gen_dir: Path, config: dict) -> None:
    """D8：ACDOCA.REF_DOC 按 REF_TYPE（SO/PO/MV）join 回 VBAK/EKKO/MSEG 主键，孤儿 = 0。"""
    _assert_no_orphans(gen_dir, config, "D8", [
        ("fin", "ACDOCA", "REF_DOC", "erp", "VBAK", "VBELN", "c.REF_TYPE = 'SO'"),
        ("fin", "ACDOCA", "REF_DOC", "scm", "EKKO", "EBELN", "c.REF_TYPE = 'PO'"),
        ("fin", "ACDOCA", "REF_DOC", "wms", "MSEG", "MBLNR", "c.REF_TYPE = 'MV'"),
    ])


def test_d9_wmmd_meins_equals_mara(gen_dir: Path, config: dict) -> None:
    """D9：同物料 WMMD.MEINS = MARA.MEINS（计量单位一致，P1a D3 保留），差异 = 0。"""
    conn = _connect(_db_path(gen_dir, config, "wms"))
    try:
        conn.execute(f"ATTACH DATABASE '{_escaped(_db_path(gen_dir, config, 'erp'))}' AS erp")
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM WMMD w JOIN erp.MARA m ON w.MATNR = m.MATNR "
            "WHERE w.MEINS <> m.MEINS"
        ).fetchone()
        assert int(row["n"]) == 0
    finally:
        conn.close()


def test_d10_inventory_reconciliation(gen_dir: Path, config: dict) -> None:
    """D10：对账自洽 —— Σ MSEG.MENGE（按 MATNR+LGORT）= MARD.LABST，diff = 0（§4.2/§6 Q5）。"""
    conn = _connect(_db_path(gen_dir, config, "erp"))
    try:
        conn.execute(f"ATTACH DATABASE '{_escaped(_db_path(gen_dir, config, 'wms'))}' AS wms")
        # (a) 账面侧：每组 (MATNR,LGORT) 账面 LABST 与流水净变差额 > 1e-6 的行数 = 0
        diff_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM ("
            "  SELECT d.MATNR, d.LGORT, d.LABST, COALESCE(mv.flow, 0) AS flow"
            "  FROM MARD d"
            "  LEFT JOIN (SELECT MATNR, LGORT, SUM(MENGE) AS flow"
            "             FROM wms.MSEG GROUP BY MATNR, LGORT) mv"
            "    ON mv.MATNR = d.MATNR AND mv.LGORT = d.LGORT"
            ") WHERE ABS(LABST - flow) > 1e-6"
        ).fetchone()
        assert int(diff_rows["n"]) == 0, f"D10 账面≠流水 的 (MATNR,LGORT) 组 {int(diff_rows['n'])} 个（应 0）"
        # (b) 流水侧：流水存在但账面缺失的 (MATNR,LGORT) 组 = 0（反向无孤儿）
        missing = conn.execute(
            "SELECT COUNT(*) AS n FROM ("
            "  SELECT MATNR, LGORT FROM wms.MSEG GROUP BY MATNR, LGORT"
            ") mv LEFT JOIN MARD d ON d.MATNR = mv.MATNR AND d.LGORT = mv.LGORT"
            " WHERE d.MATNR IS NULL"
        ).fetchone()
        assert int(missing["n"]) == 0, f"D10 流水无账面 的 (MATNR,LGORT) 组 {int(missing['n'])} 个（应 0）"
    finally:
        conn.close()


# ===========================================================================
# 确定性（§5.1 约定 1-5）：同 seed 两次生成 → 18 表 sha256 相同
# ===========================================================================
def test_determinism_same_seed_all_18_tables(tmp_path: Path) -> None:
    """同 seed 同配置两次生成，18 表 table_sha256 逐一相同（约定 1-5）。"""
    out1, out2 = tmp_path / "g1", tmp_path / "g2"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out1))
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out2))
    assert _all_table_shas(out1, _CONFIG) == _all_table_shas(out2, _CONFIG)
