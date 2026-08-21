"""P2 指标物化管道（DuckDB）：SQLite 5 源库 → 预聚合指标表 → metrics.db。

依据 docs/P2-ChatBI闭环设计_v0.1.md §2（DuckDB 物化设计）：
- §2.1：每指标 1 张物化表 metric_<id>（dimension_fields 全列 + measure 1 列，粒度组合=主键），
  落企业目录 metrics.db（DuckDB 持久化文件，与 5 源 SQLite 库 + materialized.db 并列）；
- §2.2 C4 流转契约：全量重建（CREATE OR REPLACE 幂等）；metric_meta 记录每指标
  data_version/config_sha256（与 DES manifest 同源，T3 版本守卫漂移即 fail-fast）；
- §2.3 reconcile：物化表 vs 源库直算（同 definition 同 SQL）按维度键逐行 diff=0，
  ReconcileResult 对齐 contract.py reconcile_dq01 形态（R1 门禁）；
- R3 口径单点：物化 SQL 与 reconcile SQL 均由指标注册表派生（derive_metric_sql 单点生成），禁双处手写。

复用什么：materialize.py 的 DuckDB sqlite_scan 跨库直读 + 库路径参数化模式、config.py 表注册表
（systems[].tables[].fk 派生 join 键 + db 路径）、metrics.py 的 MetricDef/load_metrics（M1-M7）、
contract.py 的 ReconcileResult。不引新依赖（DuckDB 既有）。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from src.des.config import DEFAULT_ENTERPRISES_DIR, load_config
from src.des.contract import ReconcileResult
from src.des.metrics import (
    METRIC_META_TABLE,
    METRICS_DB,
    MetricDef,
    MetricRegistry,
    load_metrics,
    metric_table_name,
)

# ---------------------------------------------------------------------------
# 常量（物化存储/命名/元表，§2.1/§2.2；物化表名由注册表派生，禁硬编码）
# ---------------------------------------------------------------------------
REFRESH_MODE_FULL = "full"  # S2 固定全量重建（C4 契约 §2.2，增量留 S3）

# metric_meta 表结构（§2.1：metric_id/data_version/config_sha256/refresh_mode/refresh_ts/row_count/source_total_rows）
META_SCHEMA = """(
  metric_id TEXT PRIMARY KEY,
  data_version TEXT,
  config_sha256 TEXT,
  refresh_mode TEXT,
  refresh_ts TEXT,
  row_count BIGINT,
  source_total_rows BIGINT
)"""

_MAX_DIFFS = 20  # reconcile 差异报告截断条数（防超大列表）

# 聚合函数 → SQL 模板（M4 白名单；count_distinct 单独处理）
_AGG_TEMPLATES = {"sum": "SUM({c})", "count": "COUNT({c})", "avg": "AVG({c})", "min": "MIN({c})", "max": "MAX({c})"}


class MetricMaterializeError(Exception):
    """指标物化失败（fail-fast，不静默；任一步骤失败即抛，不提交版本戳）。"""


@dataclass
class MetricsMaterializationResult:
    """一次全量物化的结果：逐指标表行数 + 逐指标 reconcile 报告 + 版本戳信息。

    tables 与 reconciles 均按指标注册表顺序排列（一一对应）。
    """

    enterprise_code: str
    metrics_db_path: Path
    data_version: str
    config_sha256: str
    refresh_mode: str
    tables: dict[str, int]  # metric_id -> 物化表行数
    reconciles: tuple[ReconcileResult, ...]  # 逐指标 diff=0 报告（对齐 contract.py）


# ---------------------------------------------------------------------------
# 同源 SQL 派生（物化与 reconcile 共用，R3 口径单点；表/字段/join 键全为常量，无注入面）
# ---------------------------------------------------------------------------

def _table_alias(table_id: str) -> str:
    """'erp.VBAP' → 'VBAP'（sqlite_scan 别名 = 表名末段，延续 materialize.py）。"""
    return table_id.rsplit(".", 1)[-1]


def _db_path_for(out_dir: Path, config: dict, table_id: str) -> Path:
    """由配置表注册表解析表所在源库路径：out_dir / systems[code].db（§2.6 复用 config.py）。"""
    code = table_id.split(".", 1)[0]
    return out_dir / config["enterprise"]["systems"][code]["db"]


def _split_transform(transform: str) -> tuple[str, str]:
    """'substr(1,7)' → ('substr', '1,7')（函数名 + 参数串，源列作首参；字符串切分，无正则转义面）。"""
    open_idx = transform.find("(")
    if open_idx <= 0 or not transform.endswith(")"):
        raise MetricMaterializeError(f"transform 格式非法（应为 func(args)）: {transform!r}")
    return transform[:open_idx], transform[open_idx + 1 : -1]


def _transform_expr(column: str, transform: str | None) -> str:
    """transform 'substr(1,7)' → 'substr(<col>,1,7)'（源列作函数首参，口径单点 §2.3）。"""
    if not transform:
        return column
    func, args = _split_transform(transform)
    return f"{func}({column}{',' + args if args else ''})"


def _measure_expr(metric: MetricDef) -> str:
    """度量聚合表达式：SUM(列)/COUNT(*)/COUNT(DISTINCT 列)…（M4/M5，§1.3）。"""
    source = metric.measure.source
    if source == "*":
        if metric.agg_function == "count":
            return "COUNT(*)"
        raise MetricMaterializeError(
            f"measure.source='*' 仅支持 count（M5）: {metric.metric_id!r} agg={metric.agg_function!r}"
        )
    if metric.agg_function == "count_distinct":
        return f"COUNT(DISTINCT {source})"
    template = _AGG_TEMPLATES.get(metric.agg_function)
    if template is None:
        raise MetricMaterializeError(f"agg_function 非法（M4）: {metric.agg_function!r}")
    return template.format(c=source)


def _table_source(out_dir: Path, config: dict, table_id: str) -> str:
    """sqlite_scan('<db>','<TABLE>') AS <TABLE>（延续 materialize.py 跨库直读模式）。"""
    alias = _table_alias(table_id)
    return f"sqlite_scan('{_db_path_for(out_dir, config, table_id)}','{alias}') AS {alias}"


def _join_on(table_id: str, config: dict, joined: set[str]) -> str | None:
    """返回 table_id 与已入链表表的 join 条件（如 'MARC.MATNR = MARA.MATNR'）或 None。

    join 键从配置表注册表 fk 派生（§2.6）：优先子表 fk 指向已入链表父表；
    否则反向（父表 fk 指向本表）。父侧取父表主键首列（fk 字段名 = 父主键列的约定见模板配置）。
    """
    code, name = table_id.split(".", 1)
    spec = config["enterprise"]["systems"][code]["tables"][name]
    for field, parent in (spec.get("fk") or {}).items():
        if parent in joined:
            pcode, pname = parent.split(".", 1)
            parent_pk = config["enterprise"]["systems"][pcode]["tables"][pname]["pk"][0]
            return f"{name}.{field} = {pname}.{parent_pk}"
    for prev in joined:
        pcode, pname = prev.split(".", 1)
        for field, child in (config["enterprise"]["systems"][pcode]["tables"][pname].get("fk") or {}).items():
            if child == table_id:
                return f"{name}.{spec['pk'][0]} = {pname}.{field}"
    return None


def derive_metric_sql(metric: MetricDef, config: dict, out_dir: Path) -> str:
    """由指标注册表派生物化/reconcile 同源 SQL（§2.3 R3 口径单点，禁双处手写）。

    表/字段/join 键全部来自注册表 + 配置表注册表常量（无用户输入，无注入面）；
    库路径源自配置（非用户值）。形如：
      SELECT MARA.MTART AS material_type, MARC.WERKS AS factory, COUNT(*) AS material_count
      FROM sqlite_scan('<erp.db>','MARA') AS MARA
      JOIN sqlite_scan('<erp.db>','MARC') AS MARC ON MARC.MATNR = MARA.MATNR
      GROUP BY 1,2
    本函数不输出 ORDER BY；物化（CTAS）与 reconcile 两侧由调用方统一追加
    ORDER BY <维度键>（§2.3 按维度键排序逐行比对，见 _ordered_rows）。
    """
    selects = [f"{_transform_expr(d.source, d.transform)} AS {d.name}" for d in metric.dimension_fields]
    selects.append(f"{_measure_expr(metric)} AS {metric.measure.name}")
    froms = [_table_source(out_dir, config, metric.source_tables[0])]
    joined = {metric.source_tables[0]}
    for table_id in metric.source_tables[1:]:
        on = _join_on(table_id, config, joined)
        if on is None:
            raise MetricMaterializeError(
                f"指标 {metric.metric_id}: 无法从配置 fk 派生 {table_id} 的 join 键"
            )
        froms.append(f"JOIN {_table_source(out_dir, config, table_id)} ON {on}")
        joined.add(table_id)
    group = ", ".join(str(i) for i in range(1, len(metric.dimension_fields) + 1))
    return "SELECT " + ", ".join(selects) + "\n FROM " + " ".join(froms) + f"\n GROUP BY {group}"


# ---------------------------------------------------------------------------
# 物化元信息（manifest 同源，§2.2(4)）
# ---------------------------------------------------------------------------
def _load_manifest(out_dir: Path) -> dict:
    """读企业目录 manifest.json（版本戳单一事实来源，§2.2(4)；缺失即 fail-fast）。"""
    path = out_dir / "manifest.json"
    if not path.is_file():
        raise MetricMaterializeError(f"manifest 缺失: {path}（先运行 python -m src.des --enterprise <code>）")
    return json.loads(path.read_text(encoding="utf-8"))


def _source_total_rows(metric: MetricDef, manifest: dict) -> int:
    """指标源表行数合计（manifest.tables[].rows，物化上界量级锚 §2.2）。"""
    return sum(int(manifest["tables"][t]["rows"]) for t in metric.source_tables)


# ---------------------------------------------------------------------------
# metrics.db 连接与 reconcile 单指标
# ---------------------------------------------------------------------------
def _open_metrics_db(path: Path, read_only: bool = False) -> Any:
    """打开持久化 metrics.db（DuckDB 文件）；建目录 + 建 metric_meta（读模式跳过）。"""
    if not read_only:
        path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path), read_only=read_only)
    con.execute("LOAD sqlite")
    if not read_only:
        con.execute(f"CREATE TABLE IF NOT EXISTS {METRIC_META_TABLE} {META_SCHEMA}")
    return con


def _ordered_rows(conn: Any, sql: str, order_by: str) -> list[tuple[Any, ...]]:
    """执行 SQL 并按维度键排序取行（物化侧/源库侧共用，保证两侧列序一致）。"""
    cur = conn.execute(f"{sql} ORDER BY {order_by}")
    return [tuple(row) for row in cur.fetchall()]


def _reconcile_one(conn: Any, metric: MetricDef, sql: str) -> ReconcileResult:
    """单指标 reconcile：物化表 vs 源库直算（同 SQL）按维度键逐行 diff=0（§2.3 R1）。"""
    dims = ", ".join(d.name for d in metric.dimension_fields)
    materialized = _ordered_rows(conn, f"SELECT * FROM {metric_table_name(metric.metric_id)}", dims)
    source = _ordered_rows(conn, sql, dims)
    diffs: list[str] = []
    if len(materialized) != len(source):
        diffs.append(f"行数不一致: 物化 {len(materialized)} ≠ 源库直算 {len(source)}")
    for index, (m_row, s_row) in enumerate(zip(materialized, source)):
        if m_row != s_row:
            diffs.append(f"第 {index} 行不一致: 物化 {m_row!r} ≠ 源库 {s_row!r}")
        if len(diffs) >= _MAX_DIFFS:
            break
    expected = len(source)
    return ReconcileResult(
        ok=not diffs,
        expected_count=expected,
        actual_count=len(materialized),
        ratio=len(materialized) / expected if expected else 1.0,
        differences=diffs,
    )


# ---------------------------------------------------------------------------
# 公开入口：reconcile / 物化 / 版本守卫
# ---------------------------------------------------------------------------
def reconcile_metrics(
    enterprise_code: str = "hc_precision",
    metrics_path: str | Path | None = None,
    out_dir: str | Path | None = None,
    config: dict | None = None,
    metrics: MetricRegistry | None = None,
) -> tuple[ReconcileResult, ...]:
    """reconcile 全检：每指标物化表 vs 源库直算（同 SQL）逐行 diff=0（§2.3 R1）。

    返回逐指标 ReconcileResult（ok/expected_count/actual_count/differences）。
    纯校验口径，不落库、不写版本戳。metrics.db 缺失即 fail-fast。
    """
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    cfg = config or load_config(enterprise_code)
    reg = metrics or load_metrics(metrics_path, config=cfg)
    db_path = out / METRICS_DB
    if not db_path.is_file():
        raise MetricMaterializeError(f"metrics.db 缺失: {db_path}（先运行 materialize_metrics）")
    con = _open_metrics_db(db_path, read_only=True)
    try:
        return tuple(
            _reconcile_one(con, metric, derive_metric_sql(metric, cfg, out))
            for metric in reg.metrics
        )
    finally:
        con.close()


def materialize_metrics(
    enterprise_code: str = "hc_precision",
    metrics_path: str | Path | None = None,
    out_dir: str | Path | None = None,
    config: dict | None = None,
    manifest: dict | None = None,
) -> MetricsMaterializationResult:
    """P2 指标物化管道（§2.2 C4 流转契约：全量重建 + reconcile 全检 + 版本戳提交）。

    流程：① 加载+校验指标注册表（M1-M7，复用 metrics.py）→ ② 逐指标
    CREATE OR REPLACE TABLE metric_<id> AS <derive_metric_sql>（sqlite_scan 跨库直读源库）
    → ③ reconcile 全检（§2.3 R1）→ ④ 全绿才提交 metric_meta 版本戳；任一失败抛异常，
    整批不提交新版本戳（fail-closed，查询侧仍读旧物化，§2.2(1)）。
    幂等：CREATE OR REPLACE 天然幂等，同源同配置重跑产出逐位相同（§2.3 R4）。
    刷新触发 = 显式调用（构建管道/CLI，T1/T2）；T3 查询侧版本守卫见 check_metrics_version。
    """
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    cfg = config or load_config(enterprise_code)
    reg = load_metrics(metrics_path, config=cfg)
    man = manifest or _load_manifest(out)
    # 源库存在性门禁（fail-fast，延续 materialize.py）
    for table_id in {t for m in reg.metrics for t in m.source_tables}:
        db = _db_path_for(out, cfg, table_id)
        if not db.is_file():
            raise MetricMaterializeError(
                f"源系统库缺失: {db}（先运行 python -m src.des --enterprise {enterprise_code}）"
            )

    db_path = out / METRICS_DB
    con = _open_metrics_db(db_path)
    try:
        tables: dict[str, int] = {}
        reconciles: list[ReconcileResult] = []
        for metric in reg.metrics:
            table_name = metric_table_name(metric.metric_id)
            dims = ", ".join(d.name for d in metric.dimension_fields)
            sql = derive_metric_sql(metric, cfg, out)
            con.execute(f"CREATE OR REPLACE TABLE {table_name} AS {sql} ORDER BY {dims}")
            tables[metric.metric_id] = int(
                con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            )
            reconciles.append(_reconcile_one(con, metric, sql))
        bad = [
            f"{m.metric_id}: {r.differences}"
            for m, r in zip(reg.metrics, reconciles)
            if not r.ok
        ]
        if bad:
            raise MetricMaterializeError(
                "reconcile 未全绿（R1），整批不提交版本戳（fail-closed）: " + "; ".join(bad)
            )
        # 全绿才提交版本戳（§2.2(1) ⑤）
        data_version = man["data_version"]
        config_sha = man["config_sha256"]
        refresh_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        con.executemany(
            f"INSERT OR REPLACE INTO {METRIC_META_TABLE} VALUES (?,?,?,?,?,?,?)",
            [
                (
                    m.metric_id,
                    data_version,
                    config_sha,
                    REFRESH_MODE_FULL,
                    refresh_ts,
                    tables[m.metric_id],
                    _source_total_rows(m, man),
                )
                for m in reg.metrics
            ],
        )
        return MetricsMaterializationResult(
            enterprise_code=enterprise_code,
            metrics_db_path=db_path,
            data_version=data_version,
            config_sha256=config_sha,
            refresh_mode=REFRESH_MODE_FULL,
            tables=tables,
            reconciles=tuple(reconciles),
        )
    finally:
        con.close()


def check_metrics_version(
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    manifest: dict | None = None,
) -> dict[str, Any]:
    """T3 查询侧版本守卫：metric_meta.data_version/config_sha256 vs DES manifest（§2.2(3)）。

    漂移（源数据变更后未刷新）即抛 MetricMaterializeError（fail-closed：拒答并提示刷新）。
    全绿返回 metric_meta 摘要（每指标 row_count/source_total_rows，供查询侧路由与量级锚）。
    """
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    db_path = out / METRICS_DB
    if not db_path.is_file():
        raise MetricMaterializeError(f"metrics.db 缺失: {db_path}（先运行 materialize_metrics）")
    man = manifest or _load_manifest(out)
    con = _open_metrics_db(db_path, read_only=True)
    try:
        rows = con.execute(
            f"SELECT metric_id, data_version, config_sha256, row_count, source_total_rows "
            f"FROM {METRIC_META_TABLE} ORDER BY metric_id"
        ).fetchall()
    finally:
        con.close()
    if not rows:
        raise MetricMaterializeError(f"{METRIC_META_TABLE} 为空（尚未物化）: {db_path}")
    drifted = [
        f"{mid}: 物化 {dv}/{sha} ≠ manifest {man['data_version']}/{man['config_sha256']}"
        for mid, dv, sha, _rc, _sr in rows
        if dv != man["data_version"] or sha != man["config_sha256"]
    ]
    if drifted:
        raise MetricMaterializeError("数据版本漂移，请刷新（T3 fail-closed）: " + "; ".join(drifted))
    return {
        "enterprise_code": enterprise_code,
        "data_version": man["data_version"],
        "config_sha256": man["config_sha256"],
        "metrics": [
            {"metric_id": mid, "row_count": int(rc), "source_total_rows": int(sr)}
            for mid, _dv, _sha, rc, sr in rows
        ],
    }
