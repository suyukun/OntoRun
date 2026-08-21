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
from src.ontology.des_objects import Code, Material
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
    """企业目录下 3 个源系统库路径（设计 §5 布局）。"""
    return {
        "erp": out_dir / "erp.db",
        "mes": out_dir / "mes.db",
        "wms": out_dir / "wms.db",
    }


def _write_materialized_db(
    path: Path, material_rows: list[dict[str, Any]], code_rows: list[dict[str, Any]]
) -> None:
    """把物化结果落盘为 SQLite 物化库（持久化可机验产物，幂等重建）。"""
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

    material_rows = rows_as_dicts(con, f"SELECT * FROM {MATERIAL_TABLE} ORDER BY matnr")
    code_rows = rows_as_dicts(con, f"SELECT * FROM {CODE_TABLE} ORDER BY code_id")

    # 1) Pydantic 模型校验（schema 一致性，fail-fast）
    for row in material_rows:
        Material.model_validate(row)
    for row in code_rows:
        Code.model_validate(row)

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
    _write_materialized_db(material_db_path, material_rows, code_rows)

    validation = {
        "material_count": len(material_rows),
        "code_count": len(code_rows),
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
        legacy_re=derive_legacy_regex(config),
        validation=validation,
    )
