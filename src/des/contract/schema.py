"""契约 schema 常量 + 类型/注解解析辅助 + 校验函数（设计 §3.1/§3.3，fail-closed）。

v0.1 对象路径：V1-V5 校验（字段白名单查 Registry / 类型约束 / ≤1 跳 / 防注入参数化 / 结果护栏）；
v0.2 指标路径：metric 块校验（metric_id ∈ 指标注册表、dimension_filters 键 ∈ 维度白名单、
time_range 绑定日期维度、group_by 取物化表维度子集且仅可加聚合、topN 上限）。
与 v0.1 单文件实现行为一致。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, Literal, Union, get_args, get_origin

from src.des.metrics import (
    SOURCE_COLUMNS,
    MetricDef,
    MetricRegistry,
    is_date_dimension,
)
from src.ontology.registry import Registry

# ---------------------------------------------------------------------------
# 常量（契约 schema 白名单 / 护栏上限，设计 §3.1/§3.3）
# ---------------------------------------------------------------------------
CONTRACT_KEYS = {
    "contract_version", "object_type", "filters", "aggregations",
    "group_by", "link_traversal", "metric", "time_range",
}
FILTER_EXPR_KEYS = {"op", "value"}
METRIC_KEYS = {"metric_id", "dimension_filters", "time_range", "group_by", "topN"}
TIME_RANGE_KEYS = {"from", "to"}
# v0.2 表达力扩展（报告 v0.2 建议③）：比较操作符 gt/ge/lt/le（阈值过滤 F2/F4，含度量列过滤）
OPS = ("eq", "ne", "gt", "ge", "lt", "le", "is_null", "is_not_null", "in")
AGG_FUNCS = ("count", "sum", "avg", "min", "max", "count_distinct")  # v0.2 追加 count_distinct
MAX_TOP_N = 1000  # metric.topN 上限（Top-N 契约表达力，J4 取前 5 等，防意外大返回）
RESULT_LIMIT_FLOOR = 1000  # V5 结果护栏下限（实际上限 = max(下限, 规模系数×查询规模)，禁硬编码）
RESULT_LIMIT_SCALE_FACTOR = 1  # V5 护栏规模系数（red-team P3-9：按查询对象/指标 row_count 派生，改 analytics 口径）
MAX_AGGREGATIONS = 5  # V5
MAX_GROUP_BY = 4  # V5
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # time_range ISO 日期（V2）
# 物化表子集重聚合（group_by）仅可加聚合合法：sum/count 加法、min/max 幂等；avg/count_distinct 非可加拒答
_METRIC_REAGG_SQL = {"sum": "SUM", "count": "SUM", "min": "MIN", "max": "MAX"}
_SQL_FRAGMENT_MARKERS = ("'", '"', ";", "--", "/*", "*/")
_SQL_KEYWORDS = re.compile(r"\b(select|union|insert|delete|update|drop|alter)\b", re.IGNORECASE)

# DQ-01「哪些物料一物多码？」契约实例（设计 §3.2）
DQ01_CONTRACT = {
    "contract_version": "0.1",
    "object_type": "Material",
    "filters": {"old_code": {"op": "is_not_null"}},
    "aggregations": [],
    "group_by": [],
    "link_traversal": {"link": "material.codes", "hops": 1},
}


# ---------------------------------------------------------------------------
# 校验 V1-V5（设计 §3.3，fail-closed）
# ---------------------------------------------------------------------------
def _resolve_type(registry: Registry, type_name: Any) -> Any:
    """按类型名（Material）或 api_name（material）解析对象类型；未注册返回 None。"""
    if not isinstance(type_name, str):
        return None
    for obj in registry.object_types():
        if obj.name == type_name or obj.api_name == type_name:
            return obj
    return None


def _unwrap_optional(annotation: Any) -> Any:
    """剥掉 Optional[...] 包装，返回实际类型注解。"""
    if get_origin(annotation) is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        return args[0] if len(args) == 1 else annotation
    return annotation


def _is_literal(annotation: Any) -> bool:
    return get_origin(annotation) is Literal


def _is_numeric(annotation: Any) -> bool:
    return annotation in (int, float)


def _is_date(annotation: Any) -> bool:
    return getattr(annotation, "__name__", "") == "date"


def _find_link(registry: Registry, obj: Any, link_name: str) -> Any:
    """定位从 obj 出发的已注册正向链接（v0.1 仅支持 source_type==obj 的 forward）。"""
    for link in registry.link_types():
        if link.name == link_name and link.source_type == obj.name:
            return link
    return None


def _check_sql_fragment(v: list[str], fname: str, value: Any) -> None:
    """V4 值内容防注入：禁 SQL 注释/引号逃逸/危险关键字（参数化为主，此为纵深防御）。"""
    if not isinstance(value, str):
        return
    if any(m in value for m in _SQL_FRAGMENT_MARKERS) or _SQL_KEYWORDS.search(value):
        v.append(f"过滤值含疑似 SQL 片段（V4 防注入拒答）: {fname}")


def _check_value_type(v: list[str], fname: str, value: Any, field_info: Any) -> None:
    """V2 类型约束：过滤值类型匹配字段 schema（字符串/数值/枚举/日期）。"""
    ann = _unwrap_optional(field_info.annotation)
    if _is_literal(ann):
        if value not in get_args(ann):
            v.append(f"过滤值非枚举值: {fname}={value!r}（应为 {sorted(get_args(ann))}）")
    elif _is_numeric(ann):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            v.append(f"过滤值类型应为数值: {fname}={value!r}")
    elif _is_date(ann):
        if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            v.append(f"过滤值类型应为日期 YYYY-MM-DD: {fname}={value!r}")
    elif not isinstance(value, str):
        v.append(f"过滤值类型应为字符串: {fname}={value!r}")


def _validate_filter_expr(
    fname: str, expr: Any, value_check: Callable[[list[str], Any], None]
) -> list[str]:
    """校验单个过滤表达式（标量简写 = 等值；对象含 op/value，V2/V4）。

    value_check(v, value) 做值级检查（类型 V2 + 防注入 V4）——对象路径与指标维度路径各自注入。
    """
    v: list[str] = []
    if isinstance(expr, (str, int, float, bool)):
        value_check(v, expr)
        return v
    if not isinstance(expr, dict):
        return [f"过滤表达式必须为对象或标量: {fname}"]
    unknown = set(expr) - FILTER_EXPR_KEYS
    if unknown:
        v.append(f"过滤表达式未知键: {fname} {sorted(unknown)}")
    op = expr.get("op")
    if op not in OPS:
        v.append(f"过滤操作符非法: {fname}.op={op!r}（应为 {list(OPS)}）")
        return v
    if op in ("is_null", "is_not_null"):
        if "value" in expr:
            v.append(f"{op} 不得携带 value: {fname}")
        return v
    if "value" not in expr:
        v.append(f"op={op} 缺少 value: {fname}")
        return v
    value = expr["value"]
    if op == "in":
        if not isinstance(value, list) or not value:
            v.append(f"op=in 的 value 必须为非空数组: {fname}")
            return v
        for item in value:
            value_check(v, item)
        return v
    value_check(v, value)
    return v


def _object_value_check(fname: str, field_info: Any) -> Callable[[list[str], Any], None]:
    """对象字段过滤值检查：类型（V2）+ 防注入（V4）。"""

    def check(v: list[str], value: Any) -> None:
        _check_value_type(v, fname, value, field_info)
        _check_sql_fragment(v, fname, value)

    return check


def _dimension_value_check(
    fname: str, md: MetricDef, dim_name: str
) -> Callable[[list[str], Any], None]:
    """指标维度过滤值检查：维度列类型（来源列契约派生）+ 防注入（V4）。"""

    def check(v: list[str], value: Any) -> None:
        _check_dimension_value_type(v, fname, value, md, dim_name)
        _check_sql_fragment(v, fname, value)

    return check


def _dimension_value_type(md: MetricDef, dim_name: str) -> type:
    """物化维度列期望类型（从注册表 source 列契约派生：REAL→float，其余→str；未知保守 str）。

    维度过滤值类型须与物化列类型一致（V2 对齐指标维度白名单）。
    """
    for dim in md.dimension_fields:
        if dim.name != dim_name:
            continue
        table, _, column = dim.source.partition(".")
        for tid, cols in SOURCE_COLUMNS.items():
            if tid.rsplit(".", 1)[-1] == table and column in cols:
                return float if cols[column] == "REAL" else str
        return str  # 来源列契约缺失时保守按字符串（当前 15 指标维度全为 TEXT）
    return str


def _check_dimension_value_type(
    v: list[str], fname: str, value: Any, md: MetricDef, dim_name: str
) -> None:
    """V2 维度过滤值类型约束：匹配物化维度列类型（REAL→数值，TEXT→字符串）。"""
    t = _dimension_value_type(md, dim_name)
    if t is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            v.append(f"维度过滤值类型应为数值: {fname}={value!r}")
    elif not isinstance(value, str):
        v.append(f"维度过滤值类型应为字符串: {fname}={value!r}")


def _measure_value_check(md: MetricDef) -> Callable[[list[str], Any], None]:
    """度量列过滤值检查（报告 v0.2 建议③ 按度量过滤）：度量列物化为 REAL → 数值；防注入（V4）。"""

    def check(v: list[str], value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            v.append(f"度量过滤值类型应为数值: {md.measure.name}={value!r}")
        _check_sql_fragment(v, md.measure.name, value)

    return check


def _validate_time_range(v: list[str], tr: Any) -> None:
    """V2 time_range 校验：{from, to} ISO 日期字符串且 from ≤ to（设计 §3.1）。"""
    if not isinstance(tr, dict):
        v.append("time_range 必须为对象 {from, to}")
        return
    unknown = set(tr) - TIME_RANGE_KEYS
    if unknown:
        v.append(f"time_range 未知键: {sorted(unknown)}")
    frm, to = tr.get("from"), tr.get("to")
    for name, val in (("from", frm), ("to", to)):
        if not isinstance(val, str) or not _ISO_DATE_RE.match(val):
            v.append(f"time_range.{name} 必须为 ISO 日期 YYYY-MM-DD: {val!r}")
    if isinstance(frm, str) and isinstance(to, str) and frm > to:
        v.append(f"time_range.from 必须 ≤ to: {frm!r} > {to!r}")


def _date_fields(obj: Any) -> list[str]:
    """对象 schema 中类型为 date 的字段（非 metric 路径 time_range 的绑定点）。"""
    return [
        name
        for name, f in obj.model.model_fields.items()
        if _is_date(_unwrap_optional(f.annotation))
    ]


def _validate_metric_block(
    v: list[str],
    metric: Any,
    metrics: MetricRegistry,
    top_time_range: Any = None,
) -> None:
    """M 系列指标校验（设计 §3.1/§3.2）：metric_id ∈ 注册表 / dimension_filters 键 ∈ 维度白名单 /
    值类型 / time_range 合法且指标须有日期维度 / group_by 取物化表维度子集且仅可加聚合。

    top_time_range：顶层 time_range（未放 metric 块内时与块内等价，执行取块内优先）。
    """
    if not isinstance(metric, dict):
        v.append("metric 必须为对象")
        return
    unknown = set(metric) - METRIC_KEYS
    if unknown:
        v.append(f"metric 未知键: {sorted(unknown)}")
    mid = metric.get("metric_id")
    if not isinstance(mid, str) or mid not in metrics.by_id():
        v.append(f"metric_id 不在指标注册表（M 系列）: {mid!r}")
        return  # 后续校验依赖 metric 定义
    md = metrics.by_id()[mid]
    dims = {d.name for d in md.dimension_fields}

    dim_filters = metric.get("dimension_filters") or {}
    if not isinstance(dim_filters, dict):
        v.append("metric.dimension_filters 必须为对象")
        dim_filters = {}
    for fname, expr in dim_filters.items():
        if fname not in dims and fname != md.measure.name:
            v.append(f"dimension_filters 字段不在 {mid} 维度白名单/度量列: {fname!r}")
            continue
        # 度量列过滤（报告 v0.2 建议③）：值须数值（物化列 REAL）；维度列走维度类型检查
        value_check = _measure_value_check(md) if fname == md.measure.name else _dimension_value_check(fname, md, fname)
        v.extend(_validate_filter_expr(fname, expr, value_check))

    tr = metric.get("time_range") if metric.get("time_range") is not None else top_time_range
    if tr is not None:
        _validate_time_range(v, tr)
        if not any(is_date_dimension(d) for d in md.dimension_fields):
            v.append(f"指标 {mid} 无日期维度（substr 派生），time_range 无法绑定")

    gb = metric.get("group_by")
    if gb is not None:
        if not isinstance(gb, list):
            v.append("metric.group_by 必须为数组")
        elif len(gb) > MAX_GROUP_BY:
            v.append(f"metric.group_by 超过上限 {MAX_GROUP_BY}（V5）")
        elif gb:
            for g in gb:
                if not isinstance(g, str) or g not in dims:
                    v.append(f"metric.group_by 不在 {mid} 维度白名单: {g!r}")
            if md.agg_function in ("avg", "count_distinct"):
                v.append(f"聚合 {md.agg_function} 非可加，禁物化表子集重聚合 group_by: {mid}")

    top_n = metric.get("topN")
    if top_n is not None and (isinstance(top_n, bool) or not isinstance(top_n, int) or top_n < 1 or top_n > MAX_TOP_N):
        v.append(f"metric.topN 必须为正整数（≤{MAX_TOP_N}）: {top_n!r}")


def _validate_aggregation(agg: Any, fields: dict, obj_name: str) -> list[str]:
    """V2 聚合约束：函数合法、字段白名单、'*' 仅 count、sum/avg/min/max 仅数值字段。"""
    v: list[str] = []
    if not isinstance(agg, dict):
        return ["聚合项必须为对象"]
    unknown = set(agg) - {"function", "field"}
    if unknown:
        v.append(f"聚合项未知键: {sorted(unknown)}")
    fn, fld = agg.get("function"), agg.get("field")
    if fn not in AGG_FUNCS:
        v.append(f"聚合函数非法: {fn!r}（应为 {list(AGG_FUNCS)}）")
    if fld == "*" and fn != "count":
        v.append("field='*' 仅 count 允许")  # 设计 §3.1：field='*' 仅 count 允许
    elif fld != "*" and (not isinstance(fld, str) or fld not in fields):
        v.append(f"聚合字段不在 {obj_name} 白名单: {fld!r}")
    if (
        fld != "*"
        and fld in fields
        and fn in ("sum", "avg", "min", "max")
        and not _is_numeric(_unwrap_optional(fields[fld].annotation))
    ):
        v.append(f"{fn} 要求数值字段: {fld}")
    return v


def validate_contract(
    contract: Any, registry: Registry, metrics: MetricRegistry | None = None
) -> list[str]:
    """契约 v0.1/v0.2 校验（V1-V5 + M 系列）。返回违规列表；空列表 = 通过（fail-closed：非空即拒答）。

    contract 含 metric → v0.2 指标物化路径校验（M 系列，口径由指标注册表单点定义，不要求 object_type）；
    无 metric → v0.1 对象路径（老契约行为完全不变；count_distinct / time_range 为 v0.1 扩展）。
    metrics 未注入且契约含 metric → 拒答（M 系列 fail-closed）。
    """
    v: list[str] = []
    if not isinstance(contract, dict):
        return ["契约必须为 JSON 对象"]
    unknown = set(contract) - CONTRACT_KEYS
    if unknown:
        v.append(f"未知顶层键（additionalProperties:false）: {sorted(unknown)}")

    if contract.get("metric") is not None:
        if metrics is None:
            v.append("contract 含 metric 但未提供指标注册表（M 系列拒答，fail-closed）")
        else:
            _validate_metric_block(v, contract["metric"], metrics, contract.get("time_range"))
        return v  # v0.2 物化路径：语义由指标注册表单点定义（§3.1 R3）

    if contract.get("time_range") is not None:
        # red-team P2-2：v0.1 非 metric 对象路径不支持 time_range，校验期 fail-closed 拒答
        # （杜绝静默忽略——否则查询返回全周期数据却让用户以为已过滤）。
        v.append("非 metric 契约不支持 time_range（v0.1 对象路径 fail-closed 拒答）")

    obj = _resolve_type(registry, contract.get("object_type"))
    if obj is None:
        v.append(f"object_type 未注册或非法（V1 白名单）: {contract.get('object_type')!r}")
        return v  # 后续校验依赖 object_type
    fields = obj.model.model_fields

    filters = contract.get("filters") or {}
    if not isinstance(filters, dict):
        v.append("filters 必须为对象")
        filters = {}
    for fname, expr in filters.items():
        if fname not in fields:
            v.append(f"过滤字段不在 {obj.name} 白名单: {fname}")
            continue
        v.extend(_validate_filter_expr(fname, expr, _object_value_check(fname, fields[fname])))

    aggs = contract.get("aggregations") or []
    if not isinstance(aggs, list):
        v.append("aggregations 必须为数组")
    elif len(aggs) > MAX_AGGREGATIONS:
        v.append(f"aggregations 超过上限 {MAX_AGGREGATIONS}（V5）")
    else:
        for agg in aggs:
            v.extend(_validate_aggregation(agg, fields, obj.name))

    gb = contract.get("group_by") or []
    if not isinstance(gb, list):
        v.append("group_by 必须为数组")
    elif len(gb) > MAX_GROUP_BY:
        v.append(f"group_by 超过上限 {MAX_GROUP_BY}（V5）")
    else:
        for g in gb:
            if not isinstance(g, str) or g not in fields:
                v.append(f"group_by 字段不在 {obj.name} 白名单: {g!r}")

    lt = contract.get("link_traversal")
    if lt is not None:
        if not isinstance(lt, dict):
            v.append("link_traversal 必须为对象或 null")
        else:
            unknown_lt = set(lt) - {"link", "hops"}
            if unknown_lt:
                v.append(f"link_traversal 未知键: {sorted(unknown_lt)}")
            link_name = lt.get("link")
            if not isinstance(link_name, str) or _find_link(registry, obj, link_name) is None:
                v.append(f"链接未注册或不可从 {obj.name} 遍历: {link_name!r}")
            if lt.get("hops") != 1:
                v.append(f"link_traversal.hops 必须为 1（v0.1 单跳封顶）: {lt.get('hops')!r}")
    return v
