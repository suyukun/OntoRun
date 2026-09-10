"""确定性编译器：结构化请求 -> DuckDB SQL -> 执行 -> {sql, rows}。

规则：
- JOIN 维表取维表列（快照取 max(ds)），禁止明细自带渠道名分组；
- SQL 里禁止出现业务字面量（表名/列名/过滤/粒度格式全部从注册表绑定生成，
  时间边界走绑定参数）；
- 未注册原语/非法粒度一律结构化报错，禁止静默；
- 复合度量（RatioMeasure）：分子/分母按各自度量绑定分别聚合成子查询，
  维度键 IS NOT DISTINCT FROM 全外对齐后外层相除，分母 0/缺失输出 NULL（R10）。
"""

import datetime as dt
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import duckdb
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.fortune_semantic.registry import (
    SNAPSHOT_LATEST,
    JoinSpec,
    Measure,
    RatioMeasure,
    SemanticError,
    SemanticRegistry,
)

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "fortune_mirror.duckdb"


class DimensionFilter(BaseModel):
    """维度值过滤（Gap A 演示版）：值走绑定参数，永不拼 SQL（防注入）。"""

    model_config = ConfigDict(frozen=True)

    dimension: str
    value: str


class QueryRequest(BaseModel):
    """结构化查询请求（无 LLM）：dimensions 条目为 "维度" 或 "维度=参数"。"""

    model_config = ConfigDict(frozen=True)

    measure: str
    dimensions: tuple[str, ...] = ()
    time_from: str
    time_to: str
    filters: tuple[DimensionFilter, ...] = Field(
        default=(),
        description="维度值过滤：编译为 维表列=?（绑定参数）；不参与分组",
    )

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
    request: QueryRequest,
    registry: SemanticRegistry,
    measure: Measure,
) -> list[tuple[str, str]]:
    """解析维度条目 -> [(输出列别名, SQL 表达式)]，并做参数/重复校验。

    度量级 dimension_overrides 优先：同一维度 id 在特定度量下
    改用覆写绑定（如授权度量经用户维取注册渠道名，R9）。
    """
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
        override = measure.dimension_overrides.get(dim_id)
        if dim.grains is not None:
            if override is not None:
                raise SemanticError(
                    "INVALID_REGISTRY_ENTRY",
                    f"维度 {dim_id} 为时间粒度维度，不支持度量级覆写",
                    dimension=dim_id,
                    measure=measure.id,
                )
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
            if override is not None:
                resolved.append(
                    (dim.id, override.expression.format(j=override.join.alias))
                )
                continue
            if dim.join is None:
                raise SemanticError(
                    "INVALID_REGISTRY_ENTRY",
                    f"维度 {dim_id} 缺少 join 绑定",
                    dimension=dim_id,
                )
            resolved.append((dim.id, dim.expression.format(j=dim.join.alias)))
    return resolved


def _collect_joins(
    request: QueryRequest, registry: SemanticRegistry, measure: Measure
) -> list[JoinSpec]:
    """收集维度所需 JOIN；同 (table, alias) 冲突时合并 select_columns。

    度量级覆写优先于维度默认绑定（R9：授权度量的渠道维度改走用户维）。
    合并保证 gender(usr_sex) 与覆写渠道列共用同一用户维 JOIN 不丢列。
    """
    joins: list[JoinSpec] = []
    index: dict[tuple[str, str], int] = {}
    dim_ids = [_split_dimension_entry(entry)[0] for entry in request.dimensions]
    dim_ids += [item.dimension for item in request.filters]
    for dim_id in dim_ids:
        dim = registry.get_dimension(dim_id)
        override = measure.dimension_overrides.get(dim_id)
        join = override.join if override is not None else dim.join
        if join is None:
            continue
        key = (join.table, join.alias)
        if key not in index:
            index[key] = len(joins)
            joins.append(join)
            continue
        existing = joins[index[key]]
        if existing is join:
            continue
        merged = tuple(dict.fromkeys(existing.select_columns + join.select_columns))
        if merged != existing.select_columns:
            joins[index[key]] = existing.model_copy(update={"select_columns": merged})
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
        f"{join.snapshot_column} = (SELECT max({join.snapshot_column})"
        f" FROM {join.table})"
    )
    subquery = (
        f"(SELECT {', '.join(join.select_columns)} FROM {join.table} WHERE {snapshot})"
    )
    on_clause = join.on.format(src=measure.source_alias, j=join.alias)
    return f"LEFT JOIN {subquery} AS {join.alias}\n  ON {on_clause}"


def _validate_range(request: QueryRequest) -> None:
    if request.time_from > request.time_to:
        raise SemanticError(
            "INVALID_TIME_RANGE",
            f"time_from {request.time_from} 晚于 time_to {request.time_to}",
            time_from=request.time_from,
            time_to=request.time_to,
        )


def _measure_where(
    measure: Measure, time_from: str, time_to: str
) -> tuple[list[str], tuple[str, ...]]:
    """度量 WHERE 条件：registry 过滤模板（{src}/{tbl}）+ 显式时间边界。"""
    src = measure.source_alias
    where_parts = [f.format(src=src, tbl=measure.source_table) for f in measure.filters]
    time_col = f"{src}.{measure.time_field}"
    where_parts.append(f"CAST({time_col} AS DATE) >= ?")
    where_parts.append(f"CAST({time_col} AS DATE) <= ?")
    return where_parts, (time_from, time_to)


def _filter_clauses(
    request: QueryRequest,
    registry: SemanticRegistry,
    measure: Measure,
) -> tuple[list[str], list[str]]:
    """filters → WHERE 谓词（维表列 = ?）与绑定值（值永不拼 SQL，防注入）。

    维度解析与 _resolve_dimensions 同源（度量级覆写优先）：过滤列所在
    join/别名与该维度参与分组/收集 JOIN 时完全一致。未注册维度结构化报错。
    """
    parts: list[str] = []
    values: list[str] = []
    for item in request.filters:
        dim = registry.get_dimension(item.dimension)
        override = measure.dimension_overrides.get(item.dimension)
        join = override.join if override is not None else dim.join
        if dim.grains is not None:
            raise SemanticError(
                "INVALID_TIME_GRAIN",
                f"维度 {item.dimension} 为时间粒度维度，不支持值过滤",
                dimension=item.dimension,
            )
        if join is None:
            raise SemanticError(
                "INVALID_REGISTRY_ENTRY",
                f"维度 {item.dimension} 缺少 join 绑定，无法按值过滤",
                dimension=item.dimension,
            )
        parts.append(f"{dim.expression.format(j=join.alias)} = ?")
        values.append(item.value)
    return parts, values


def _compile_ratio(
    request: QueryRequest, registry: SemanticRegistry, ratio: RatioMeasure
) -> CompiledQuery:
    """复合度量：分子/分母子查询分别聚合 + 外层相除（R10）。

    两侧维度键可能不全（各自源表在该维度上的组不同），用
    IS NOT DISTINCT FROM 全外对齐（NULL 组也参与配对）；分母为 0
    或对侧缺失时 NULLIF 产出 NULL，不报错。
    """
    numerator = registry.get_measure(ratio.numerator)
    denominator = registry.get_measure(ratio.denominator)
    ctes: list[str] = []
    params: list[str] = []
    dim_aliases: tuple[str, ...] | None = None
    for tag, side in (("num", numerator), ("den", denominator)):
        dim_cols = _resolve_dimensions(request, registry, side)
        aliases = tuple(alias for alias, _ in dim_cols)
        if dim_aliases is None:
            dim_aliases = aliases
        elif aliases != dim_aliases:
            raise SemanticError(
                "INVALID_REGISTRY_ENTRY",
                f"复合度量 {ratio.id} 分子分母维度别名不一致",
                ratio=ratio.id,
                numerator=ratio.numerator,
                denominator=ratio.denominator,
            )
        src = side.source_alias
        select_parts = [f"{expr} AS {alias}" for alias, expr in dim_cols]
        select_parts.append(f"{side.expression.format(src=src)} AS {side.id}")
        lines = [f"SELECT\n  {',\n  '.join(select_parts)}"]
        lines.append(f"FROM {side.source_table} AS {src}")
        for join in _collect_joins(request, registry, side):
            lines.append(_join_sql(side, join))
        where_parts, side_params = _measure_where(
            side, request.time_from, request.time_to
        )
        filter_parts, filter_values = _filter_clauses(request, registry, side)
        where_parts.extend(filter_parts)
        side_params = (*side_params, *filter_values)
        params.extend(side_params)
        lines.append("WHERE\n  " + "\n  AND ".join(where_parts))
        if dim_cols:
            ordinals = ", ".join(str(i) for i in range(1, len(dim_cols) + 1))
            lines.append(f"GROUP BY {ordinals}")
        ctes.append(f"{tag} AS (\n" + "\n".join(lines) + "\n)")

    assert dim_aliases is not None  # 循环至少执行一次
    num_id, den_id = numerator.id, denominator.id
    # 对侧缺失的组按 0 计（COUNT 空集语义）；分母 0 -> NULLIF -> NULL 不报错
    select_parts = [
        f"COALESCE(num.{num_id}, 0) AS {num_id}",
        f"COALESCE(den.{den_id}, 0) AS {den_id}",
    ]
    select_parts.append(
        f"COALESCE(num.{num_id}, 0) / NULLIF(COALESCE(den.{den_id}, 0), 0)"
        f" AS {ratio.id}"
    )
    if dim_aliases:
        coalesced = [
            f"COALESCE(num.{alias}, den.{alias}) AS {alias}" for alias in dim_aliases
        ]
        on_clause = "\n  AND ".join(
            f"num.{alias} IS NOT DISTINCT FROM den.{alias}" for alias in dim_aliases
        )
        ordinals = ", ".join(str(i) for i in range(1, len(dim_aliases) + 1))
        lines = [
            "WITH " + ",\n".join(ctes),
            f"SELECT\n  {',\n  '.join(coalesced + select_parts)}",
            "FROM num",
            "FULL OUTER JOIN den",
            f"  ON {on_clause}",
            f"ORDER BY {ordinals}",
        ]
        columns = dim_aliases + (num_id, den_id, ratio.id)
    else:
        lines = [
            "WITH " + ",\n".join(ctes),
            f"SELECT\n  {',\n  '.join(select_parts)}",
            "FROM num\nCROSS JOIN den",
        ]
        columns = (num_id, den_id, ratio.id)
    return CompiledQuery(
        sql="\n".join(lines),
        params=tuple(params),
        columns=columns,
    )


def compile_query(
    request: QueryRequest, registry: SemanticRegistry | None = None
) -> CompiledQuery:
    """结构化请求 -> 确定性 SQL（全部原语从注册表绑定，无业务字面量）。"""
    if registry is None:
        from src.fortune_semantic.registry import REGISTRY

        registry = REGISTRY
    _validate_range(request)
    ratio = registry.ratios.get(request.measure)
    if ratio is not None:
        return _compile_ratio(request, registry, ratio)
    measure = registry.get_measure(request.measure)
    dim_cols = _resolve_dimensions(request, registry, measure)
    src = measure.source_alias

    select_parts = [f"{expr} AS {alias}" for alias, expr in dim_cols]
    select_parts.append(f"{measure.expression.format(src=src)} AS {measure.id}")
    lines = [f"SELECT\n  {',\n  '.join(select_parts)}"]
    lines.append(f"FROM {measure.source_table} AS {src}")
    for join in _collect_joins(request, registry, measure):
        lines.append(_join_sql(measure, join))

    where_parts, _ = _measure_where(measure, request.time_from, request.time_to)
    filter_parts, filter_values = _filter_clauses(request, registry, measure)
    where_parts.extend(filter_parts)
    lines.append("WHERE\n  " + "\n  AND ".join(where_parts))

    if dim_cols:
        ordinals = ", ".join(str(i) for i in range(1, len(dim_cols) + 1))
        lines.append(f"GROUP BY {ordinals}\nORDER BY {ordinals}")

    return CompiledQuery(
        sql="\n".join(lines),
        params=(request.time_from, request.time_to, *filter_values),
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
