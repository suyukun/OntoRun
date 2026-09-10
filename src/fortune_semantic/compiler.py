"""确定性编译器：结构化请求 -> DuckDB SQL -> 执行 -> {sql, rows}。

规则：
- JOIN 维表取维表列（快照取 max(ds)），禁止明细自带渠道名分组；
- SQL 里禁止出现业务字面量（表名/列名/过滤/粒度格式全部从注册表绑定生成，
  时间边界走绑定参数）；
- 未注册原语/非法粒度一律结构化报错，禁止静默。
"""

import datetime as dt
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import duckdb
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from src.fortune_semantic.registry import (
    SNAPSHOT_LATEST,
    JoinSpec,
    Measure,
    SemanticError,
    SemanticRegistry,
)

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "fortune_mirror.duckdb"


class QueryRequest(BaseModel):
    """结构化查询请求（无 LLM）：dimensions 条目为 "维度" 或 "维度=参数"。"""

    model_config = ConfigDict(frozen=True)

    measure: str
    dimensions: tuple[str, ...] = ()
    time_from: str
    time_to: str

    @field_validator("time_from", "time_to")
    @classmethod
    def _iso_date(cls, value: str) -> str:
        try:
            dt.date.fromisoformat(value)
        except ValueError as exc:
            raise SemanticError(
                "INVALID_REQUEST", f"日期非法: {value!r}（需 YYYY-MM-DD）", field=value
            ) from exc
        return value


class CompiledQuery(BaseModel):
    """编译产物：SQL + 绑定参数 + 输出列名。"""

    model_config = ConfigDict(frozen=True)

    sql: str
    params: tuple[str, ...]
    columns: tuple[str, ...]


def parse_request(data: Mapping[str, Any]) -> QueryRequest:
    """dict -> QueryRequest；pydantic 校验失败转结构化错误。"""
    try:
        return QueryRequest.model_validate(dict(data))
    except ValidationError as exc:
        raise SemanticError(
            "INVALID_REQUEST",
            f"请求结构非法: {exc.error_count()} 处",
            errors=exc.errors(include_url=False),
        ) from exc


def _split_dimension_entry(entry: str) -> tuple[str, str | None]:
    if "=" in entry:
        dim_id, arg = entry.split("=", 1)
        return dim_id.strip(), arg.strip() or None
    return entry.strip(), None


def _resolve_dimensions(
    request: QueryRequest, registry: SemanticRegistry
) -> list[tuple[str, str]]:
    """解析维度条目 -> [(输出列别名, SQL 表达式)]，并做参数/重复校验。"""
    measure = registry.get_measure(request.measure)
    resolved: list[tuple[str, str]] = []
    seen: set[str] = set()
    for entry in request.dimensions:
        dim_id, arg = _split_dimension_entry(entry)
        if dim_id in seen:
            raise SemanticError(
                "DUPLICATE_DIMENSION", f"维度重复: {dim_id}", dimension=dim_id
            )
        seen.add(dim_id)
        dim = registry.get_dimension(dim_id)
        if dim.grains is not None:
            if arg is None:
                raise SemanticError(
                    "INVALID_TIME_GRAIN",
                    f"维度 {dim_id} 需要粒度参数（{entry!r}）",
                    dimension=dim_id,
                    available=sorted(dim.grains),
                )
            if arg not in dim.grains:
                raise SemanticError(
                    "INVALID_TIME_GRAIN",
                    f"时间粒度未注册: {arg}",
                    dimension=dim_id,
                    grain=arg,
                    available=sorted(dim.grains),
                )
            template = dim.grains[arg]
            expr = template.format(t=f"{measure.source_alias}.{measure.time_field}")
            resolved.append((f"{dim_id}_{arg}", expr))
        else:
            if arg is not None:
                raise SemanticError(
                    "UNEXPECTED_DIMENSION_ARGUMENT",
                    f"维度 {dim_id} 不接受参数: {arg!r}",
                    dimension=dim_id,
                    argument=arg,
                )
            if dim.join is None:
                raise SemanticError(
                    "INVALID_REGISTRY_ENTRY",
                    f"维度 {dim_id} 缺少 join 绑定",
                    dimension=dim_id,
                )
            resolved.append((dim.id, dim.expression.format(j=dim.join.alias)))
    return resolved


def _collect_joins(request: QueryRequest, registry: SemanticRegistry) -> list[JoinSpec]:
    joins: list[JoinSpec] = []
    seen: set[tuple[str, str]] = set()
    for entry in request.dimensions:
        dim_id, _ = _split_dimension_entry(entry)
        dim = registry.get_dimension(dim_id)
        if dim.join is None:
            continue
        key = (dim.join.table, dim.join.alias)
        if key not in seen:
            seen.add(key)
            joins.append(dim.join)
    return joins


def _join_sql(measure: Measure, join: JoinSpec) -> str:
    if join.snapshot_policy != SNAPSHOT_LATEST:
        raise SemanticError(
            "UNSUPPORTED_SNAPSHOT_POLICY",
            f"快照策略未支持: {join.snapshot_policy}",
            table=join.table,
            snapshot_policy=join.snapshot_policy,
        )
    # 谓词在子查询内部：引用裸列名（外层别名在此不可见）
    snapshot = (
        f"{join.snapshot_column} = (SELECT max({join.snapshot_column}) FROM {join.table})"
    )
    subquery = (
        f"(SELECT {', '.join(join.select_columns)} FROM {join.table} WHERE {snapshot})"
    )
    on_clause = join.on.format(src=measure.source_alias, j=join.alias)
    return f"LEFT JOIN {subquery} AS {join.alias}\n  ON {on_clause}"


def compile_query(
    request: QueryRequest, registry: SemanticRegistry | None = None
) -> CompiledQuery:
    """结构化请求 -> 确定性 SQL（全部原语从注册表绑定，无业务字面量）。"""
    if registry is None:
        from src.fortune_semantic.registry import REGISTRY

        registry = REGISTRY
    if request.time_from > request.time_to:
        raise SemanticError(
            "INVALID_TIME_RANGE",
            f"time_from {request.time_from} 晚于 time_to {request.time_to}",
            time_from=request.time_from,
            time_to=request.time_to,
        )
    measure = registry.get_measure(request.measure)
    dim_cols = _resolve_dimensions(request, registry)
    src = measure.source_alias

    select_parts = [f"{expr} AS {alias}" for alias, expr in dim_cols]
    select_parts.append(f"{measure.expression.format(src=src)} AS {measure.id}")
    lines = [f"SELECT\n  {',\n  '.join(select_parts)}"]
    lines.append(f"FROM {measure.source_table} AS {src}")
    for join in _collect_joins(request, registry):
        lines.append(_join_sql(measure, join))

    where_parts = [f.format(src=src) for f in measure.filters]
    time_col = f"{src}.{measure.time_field}"
    where_parts.append(f"CAST({time_col} AS DATE) >= ?")
    where_parts.append(f"CAST({time_col} AS DATE) <= ?")
    lines.append("WHERE\n  " + "\n  AND ".join(where_parts))

    if dim_cols:
        ordinals = ", ".join(str(i) for i in range(1, len(dim_cols) + 1))
        lines.append(f"GROUP BY {ordinals}\nORDER BY {ordinals}")

    return CompiledQuery(
        sql="\n".join(lines),
        params=(request.time_from, request.time_to),
        columns=tuple(alias for alias, _ in dim_cols) + (measure.id,),
    )


def run_query(
    request: QueryRequest,
    conn: duckdb.DuckDBPyConnection | None = None,
    db_path: Path | None = None,
    registry: SemanticRegistry | None = None,
) -> dict:
    """编译 + 执行，返回 {sql, params, columns, rows}。conn 为空时自开只读连接。"""
    compiled = compile_query(request, registry)
    own_conn = conn is None
    if own_conn:
        path = db_path or DEFAULT_DB_PATH
        conn = duckdb.connect(str(path), read_only=True)
    try:
        cursor = conn.execute(compiled.sql, list(compiled.params))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    finally:
        if own_conn:
            conn.close()
    return {
        "sql": compiled.sql,
        "params": list(compiled.params),
        "columns": columns,
        "rows": rows,
    }
