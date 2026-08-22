"""DES → 本体物化器（设计 §1.4/§1.5）：DuckDB sqlite_scan 跨 3 源系统库打通竖井 →
组装 200 Material + 830 Code 实体，物化到可查询存储（DuckDB 内存 + SQLite 物化库）。

- 竖井打通发生在语义层而非数据层：三库之间无外键，join 由本体映射 + DuckDB 完成（设计 §1.5）；
- Material 以 ERP.MARA 为主承载（200 行驱动），MES.MPLA join 补 mes_code，WMS.WMMD join 校验 base_unit；
- Code 830 行 = plm/erp/wms 各 200（value=matnr）+ mes 200（value='MP-'+matnr）+ legacy 30（value=BISMT）；
- 物化可机验锚点：Material 数 = MARA 行数 = 200；Code 行数 = 830（设计 §1.4/§1.5）。
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import duckdb

from src.des.config import DEFAULT_ENTERPRISES_DIR, load_config
from src.ontology.des_objects import (
    Code,
    ErpCustomer,
    FinanceEntry,
    InventoryLocation,
    Material,
    Vendor,
)
from src.ontology.registry import Issue, Registry

MATERIAL_TABLE = "material"  # 物化表名（与 Material.source_table 对齐）
CODE_TABLE = "codes"  # 物化表名（与 Code.source_table 对齐）
MATERIALIZED_DB = "materialized.db"

# 跨 3 库 join 物化 SQL：表/字段名全部为常量（非用户输入，无注入面），库路径参数化绑定
_MATERIAL_SQL = """
SELECT
  m.MATNR AS matnr,
  m.MAKTX AS name,
  m.MTART AS material_type,
  m.MATNR AS plm_code,
  p.MPLA_ID AS mes_code,
  m.BISMT AS old_code,
  m.MEINS AS base_unit,
  m.MATKL AS material_group,
  m.ERDAT AS created_date
FROM sqlite_scan(?, 'MARA') AS m
LEFT JOIN sqlite_scan(?, 'MPLA') AS p ON p.MATNR = m.MATNR
LEFT JOIN sqlite_scan(?, 'WMMD') AS w ON w.MATNR = m.MATNR
ORDER BY m.MATNR
"""

# Code 对象确定性物化：主码族 3 码空间 + MES 派生码 + 旧码族（设计 §1.4 表）
_CODES_SQL = """
WITH materials AS (SELECT matnr, mes_code, old_code FROM material)
SELECT 'erp' || ':' || matnr AS code_id, 'erp' AS code_space, matnr AS value, matnr AS material_matnr FROM materials
UNION ALL SELECT 'plm' || ':' || matnr, 'plm', matnr, matnr FROM materials
UNION ALL SELECT 'wms' || ':' || matnr, 'wms', matnr, matnr FROM materials
UNION ALL SELECT 'mes' || ':' || mes_code, 'mes', mes_code, matnr FROM materials
UNION ALL SELECT 'legacy' || ':' || old_code, 'legacy', old_code, matnr FROM materials WHERE old_code IS NOT NULL
ORDER BY code_id
"""

# P2 主体对象接线（报告 §5 缺口修复：注册对象 ≠ 可查询对象，源表按对象模型字段映射物化）：
# ErpCustomer（erp.KNA1）/ Vendor（scm.LFA1）/ InventoryLocation（erp.MARD 地点粒度）/
# FinanceEntry（fin.ACDOCA）——物化成与对象 schema 同构的表
# （erp_customer/vendor/inventory_location/finance_entry），供 v0.1 对象路径查询。
ERP_CUSTOMER_TABLE = "erp_customer"  # 物化表名（与 ErpCustomer.source_table 对齐）
VENDOR_TABLE = "vendor"  # 物化表名（与 Vendor.source_table 对齐）
INV_LOC_TABLE = "inventory_location"  # 物化表名（与 InventoryLocation.source_table 对齐）
FINANCE_TABLE = "finance_entry"  # 物化表名（与 FinanceEntry.source_table 对齐）

# ERP 客户主数据物化：ERP.KNA1 → ErpCustomer 模型字段（PK = KUNNR，设计 §1.5 表；
# 2026-08-22 独立对象注册，解决 Customer 同名冲突）
_ERP_CUSTOMER_SQL = """
SELECT KUNNR AS erp_customer_id, NAME1 AS name, KTOKD AS customer_group, ORT01 AS city
FROM sqlite_scan(?, 'KNA1') ORDER BY KUNNR
"""

# 供应商物化：SCM.LFA1 → Vendor 模型字段（PK = LIFNR，设计 §1.5 表）
_VENDOR_SQL = """
SELECT LIFNR AS vendor_id, NAME1 AS name, ORT01 AS city, LAND1 AS country
FROM sqlite_scan(?, 'LFA1') ORDER BY LIFNR
"""

# 库存地点物化：ERP.MARD 地点粒度（WERKS+LGORT 去重，PK = '{WERKS}|{LGORT}'，设计 §1.5 表）
_INV_LOC_SQL = """
SELECT WERKS || '|' || LGORT AS location_id, WERKS AS factory, LGORT AS location
FROM (SELECT DISTINCT WERKS, LGORT FROM sqlite_scan(?, 'MARD')) AS d ORDER BY 1
"""

# 财务凭证行物化：FIN.ACDOCA → FinanceEntry 模型字段（PK = '{BELNR}|{POSNR}'，设计 §1.5 表）
_FIN_SQL = """
SELECT BELNR || '|' || POSNR AS entry_id, BELNR AS belnr, POSNR AS posnr,
       RACCT AS account, KOSTL AS cost_center, WSL AS amount, BUDAT AS post_date,
       REF_TYPE AS ref_type, REF_DOC AS ref_doc
FROM sqlite_scan(?, 'ACDOCA') ORDER BY 1
"""


class MaterializeError(Exception):
    """物化失败（数据与本体契约不一致即 fail-fast，不静默）。"""


@dataclass
class DesMaterialization:
    """DES 物化结果：可查询的 Material/Code 实体 + 物化元信息。

    duckdb：跨 3 库物化出的内存 DuckDB（material/codes 两表，可查询，语义层物化）；
    material_db_path：持久化 SQLite 物化库（机器可验产物，*.db 不入 git）。
    """

    enterprise_code: str
    config: dict[str, Any]
    duckdb: Any
    material_db_path: Path
    material_count: int
    code_count: int
    legacy_re: re.Pattern[str]
    erp_customer_count: int = 0  # P2 接线：ERP.KNA1 行数（2026-08-22 ErpCustomer 独立注册）
    vendor_count: int = 0  # P2 接线：SCM.LFA1 行数
    inventory_location_count: int = 0  # P2 接线：MARD 地点粒度（WERKS+LGORT 去重）
    finance_entry_count: int = 0  # P2 接线：FIN.ACDOCA 行数
    validation: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def rows_as_dicts(conn: Any, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    """执行参数化 SQL 并返回行 dict 列表（DuckDB 与 sqlite3 cursor 共用，均暴露 description）。"""
    cur = conn.execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def derive_legacy_regex(config: dict[str, Any]) -> re.Pattern[str]:
    """由配置派生旧码正则（设计 §2.2 禁硬编码：{prefix}-{year}{seq:05d} → ^HC-\\d{9}$）。"""
    multi = config["injection"]["multi_code"]
    pattern = multi["legacy_pattern"]
    match = re.search(r"\{seq:0(\d+)d\}", pattern)
    if not match:
        raise ValueError(f"legacy_pattern 缺少 {{seq:0Nd}} 位宽占位: {pattern!r}")
    seq_digits = int(match.group(1))
    year_digits = len(str(config["coding"]["year"]))
    return re.compile(rf"^{re.escape(multi['legacy_prefix'])}-\d{{{year_digits + seq_digits}}}$")


def _db_paths(out_dir: Path) -> dict[str, Path]:
    """企业目录下 5 个源系统库路径（设计 §5 布局；P2 接线补 scm/fin）。"""
    return {
        "erp": out_dir / "erp.db",
        "mes": out_dir / "mes.db",
        "wms": out_dir / "wms.db",
        "scm": out_dir / "scm.db",
        "fin": out_dir / "fin.db",
    }


def _write_materialized_db(
    path: Path,
    material_rows: list[dict[str, Any]],
    code_rows: list[dict[str, Any]],
    erp_customer_rows: list[dict[str, Any]] | None = None,
    vendor_rows: list[dict[str, Any]] | None = None,
    inv_loc_rows: list[dict[str, Any]] | None = None,
    finance_rows: list[dict[str, Any]] | None = None,
) -> None:
    """把物化结果落盘为 SQLite 物化库（持久化可机验产物，幂等重建）。

    P2 接线：erp_customer/vendor/inventory_location/finance_entry 四表（对象 schema 同构）
    随 material/codes 一并落盘；不传时（仅 Material/Code 场景）保持旧 schema 行为。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(
            f"""
            CREATE TABLE {MATERIAL_TABLE} (
              matnr TEXT PRIMARY KEY, name TEXT NOT NULL, material_type TEXT NOT NULL,
              plm_code TEXT NOT NULL, mes_code TEXT NOT NULL, old_code TEXT,
              base_unit TEXT NOT NULL, material_group TEXT NOT NULL, created_date TEXT NOT NULL
            );
            CREATE TABLE {CODE_TABLE} (
              code_id TEXT PRIMARY KEY, code_space TEXT NOT NULL, value TEXT NOT NULL,
              material_matnr TEXT NOT NULL
            );
            """
        )
        if erp_customer_rows is not None:
            conn.execute(
                f"CREATE TABLE {ERP_CUSTOMER_TABLE} ("
                "erp_customer_id TEXT PRIMARY KEY, name TEXT NOT NULL, "
                "customer_group TEXT NOT NULL, city TEXT NOT NULL)"
            )
        if vendor_rows is not None:
            conn.execute(
                f"CREATE TABLE {VENDOR_TABLE} ("
                "vendor_id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL, "
                "country TEXT NOT NULL)"
            )
        if inv_loc_rows is not None:
            conn.execute(
                f"CREATE TABLE {INV_LOC_TABLE} ("
                "location_id TEXT PRIMARY KEY, factory TEXT NOT NULL, location TEXT NOT NULL)"
            )
        if finance_rows is not None:
            conn.execute(
                f"CREATE TABLE {FINANCE_TABLE} ("
                "entry_id TEXT PRIMARY KEY, belnr TEXT NOT NULL, posnr TEXT NOT NULL, "
                "account TEXT NOT NULL, cost_center TEXT NOT NULL, amount REAL NOT NULL, "
                "post_date TEXT NOT NULL, ref_type TEXT NOT NULL, ref_doc TEXT)"
            )
        conn.executemany(
            f"INSERT INTO {MATERIAL_TABLE} VALUES (?,?,?,?,?,?,?,?,?)",
            [tuple(r[c] for c in ("matnr", "name", "material_type", "plm_code", "mes_code",
                                  "old_code", "base_unit", "material_group", "created_date"))
             for r in material_rows],
        )
        conn.executemany(
            f"INSERT INTO {CODE_TABLE} VALUES (?,?,?,?)",
            [tuple(r[c] for c in ("code_id", "code_space", "value", "material_matnr"))
             for r in code_rows],
        )
        if erp_customer_rows is not None:
            conn.executemany(
                f"INSERT INTO {ERP_CUSTOMER_TABLE} VALUES (?,?,?,?)",
                [tuple(r[c] for c in ("erp_customer_id", "name", "customer_group", "city"))
                 for r in erp_customer_rows],
            )
        if vendor_rows is not None:
            conn.executemany(
                f"INSERT INTO {VENDOR_TABLE} VALUES (?,?,?,?)",
                [tuple(r[c] for c in ("vendor_id", "name", "city", "country"))
                 for r in vendor_rows],
            )
        if inv_loc_rows is not None:
            conn.executemany(
                f"INSERT INTO {INV_LOC_TABLE} VALUES (?,?,?)",
                [tuple(r[c] for c in ("location_id", "factory", "location"))
                 for r in inv_loc_rows],
            )
        if finance_rows is not None:
            conn.executemany(
                f"INSERT INTO {FINANCE_TABLE} VALUES (?,?,?,?,?,?,?,?,?)",
                [tuple(r[c] for c in ("entry_id", "belnr", "posnr", "account",
                                      "cost_center", "amount", "post_date", "ref_type", "ref_doc"))
                 for r in finance_rows],
            )
        conn.commit()
    finally:
        conn.close()


def _validate_cross_db(duckdb_conn: Any, db_paths: dict[str, Path]) -> dict[str, Any]:
    """跨系统一致性复核（设计 §1.5/门禁 D1-D3）：无孤儿、计量单位一致。"""
    orphan_mpla = rows_as_dicts(
        duckdb_conn,
        "SELECT COUNT(*) AS n FROM sqlite_scan(?, 'MPLA') p "
        "LEFT JOIN material m ON p.MATNR = m.matnr WHERE m.matnr IS NULL",
        [str(db_paths["mes"])],
    )[0]["n"]
    orphan_wmmd = rows_as_dicts(
        duckdb_conn,
        "SELECT COUNT(*) AS n FROM sqlite_scan(?, 'WMMD') w "
        "LEFT JOIN material m ON w.MATNR = m.matnr WHERE m.matnr IS NULL",
        [str(db_paths["wms"])],
    )[0]["n"]
    d3_mismatch = rows_as_dicts(
        duckdb_conn,
        "SELECT COUNT(*) AS n FROM sqlite_scan(?, 'WMMD') w "
        "JOIN material m ON w.MATNR = m.matnr WHERE w.MEINS <> m.base_unit",
        [str(db_paths["wms"])],
    )[0]["n"]
    return {"orphan_mpla": orphan_mpla, "orphan_wmmd": orphan_wmmd, "d3_mismatch": d3_mismatch}


def materialize_des(
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    registry: Registry | None = None,
) -> DesMaterialization:
    """DuckDB 跨 3 库物化 Material/Code，落盘 SQLite 物化库，返回可查询物化结果。

    物化后校验：
    1) Pydantic 模型校验（Material/Code schema 一致性，V2 同类类型约束）；
    2) 跨系统一致性复核（无孤儿 / 计量单位一致，设计 §1.5）；
    3) registry.self_check(instance_data=...) 跑 CODE_SPACE_ENUM_VALID / MULTI_CODE_FIELD_CONSISTENT，
       发现 error 级问题即 MaterializeError（fail-fast）。
    """
    config = load_config(enterprise_code)
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    db_paths = _db_paths(out)
    for path in db_paths.values():
        if not path.is_file():
            raise MaterializeError(f"源系统库缺失: {path}（先运行 python -m src.des --enterprise {enterprise_code}）")

    con = duckdb.connect()
    con.execute("LOAD sqlite")
    con.execute("CREATE TABLE material AS " + _MATERIAL_SQL, [str(db_paths["erp"]), str(db_paths["mes"]), str(db_paths["wms"])])
    con.execute("CREATE TABLE codes AS " + _CODES_SQL)
    # P2 主体对象接线（报告 §5 缺口修复）：对象 schema 同构物化表，v0.1 对象路径可查询
    con.execute("CREATE TABLE erp_customer AS " + _ERP_CUSTOMER_SQL, [str(db_paths["erp"])])
    con.execute("CREATE TABLE vendor AS " + _VENDOR_SQL, [str(db_paths["scm"])])
    con.execute("CREATE TABLE inventory_location AS " + _INV_LOC_SQL, [str(db_paths["erp"])])
    con.execute("CREATE TABLE finance_entry AS " + _FIN_SQL, [str(db_paths["fin"])])

    material_rows = rows_as_dicts(con, f"SELECT * FROM {MATERIAL_TABLE} ORDER BY matnr")
    code_rows = rows_as_dicts(con, f"SELECT * FROM {CODE_TABLE} ORDER BY code_id")
    erp_customer_rows = rows_as_dicts(con, f"SELECT * FROM {ERP_CUSTOMER_TABLE} ORDER BY erp_customer_id")
    vendor_rows = rows_as_dicts(con, f"SELECT * FROM {VENDOR_TABLE} ORDER BY vendor_id")
    inv_loc_rows = rows_as_dicts(con, f"SELECT * FROM {INV_LOC_TABLE} ORDER BY location_id")
    finance_rows = rows_as_dicts(con, f"SELECT * FROM {FINANCE_TABLE} ORDER BY entry_id")

    # 1) Pydantic 模型校验（schema 一致性，fail-fast）
    for row in material_rows:
        Material.model_validate(row)
    for row in code_rows:
        Code.model_validate(row)
    for row in erp_customer_rows:
        ErpCustomer.model_validate(row)
    for row in vendor_rows:
        Vendor.model_validate(row)
    for row in inv_loc_rows:
        InventoryLocation.model_validate(row)
    for row in finance_rows:
        FinanceEntry.model_validate(row)

    # 2) 跨系统一致性复核
    cross = _validate_cross_db(con, db_paths)

    # 3) self_check 实例级检查（CODE_SPACE_ENUM_VALID / MULTI_CODE_FIELD_CONSISTENT）
    instance_data = {"Material": material_rows, "Code": code_rows}
    checks: list[Issue] = []
    if registry is not None:
        checks = registry.self_check(instance_data=instance_data)
        errors = [i.message for i in checks if i.severity == "error"]
        if errors:
            con.close()
            raise MaterializeError("物化数据未通过 self_check: " + "; ".join(errors))

    material_db_path = out / MATERIALIZED_DB
    _write_materialized_db(
        material_db_path, material_rows, code_rows, erp_customer_rows, vendor_rows, inv_loc_rows, finance_rows
    )

    validation = {
        "material_count": len(material_rows),
        "code_count": len(code_rows),
        "erp_customer_count": len(erp_customer_rows),
        "vendor_count": len(vendor_rows),
        "inventory_location_count": len(inv_loc_rows),
        "finance_entry_count": len(finance_rows),
        "cross_db": cross,
        "self_check_issues": [i.model_dump() for i in checks],
    }
    return DesMaterialization(
        enterprise_code=enterprise_code,
        config=config,
        duckdb=con,
        material_db_path=material_db_path,
        material_count=len(material_rows),
        code_count=len(code_rows),
        erp_customer_count=len(erp_customer_rows),
        vendor_count=len(vendor_rows),
        inventory_location_count=len(inv_loc_rows),
        finance_entry_count=len(finance_rows),
        legacy_re=derive_legacy_regex(config),
        validation=validation,
    )
