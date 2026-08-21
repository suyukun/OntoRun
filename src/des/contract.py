"""结构化查询契约 v0.1/v0.2 校验 + 执行器（设计 §3）。

v0.1（对象路径，行为不变）：V1-V5 校验 fail-closed（设计 §3.3）——字段白名单查 Registry / 类型约束 /
≤1 跳 / 防注入参数化 / 结果护栏；过滤 + 聚合 + group_by + link_traversal（≤1 跳）参数化执行，契约值永不拼 SQL（V4）；
DQ-01「哪些物料一物多码？」：执行器对 old_code 非空结果集强制再过一物多码全谓词（§2.2），口径单点化；
reconcile_dq01：本体查询结果 vs 数据侧注入集 + manifest.multi_code_count 三方对账（§2.3）。

v0.2 扩展（设计 §3.1/§3.2，老 v0.1 契约原样可执行）：
- metric 键 → 指标物化路径：metric_id ∈ 指标注册表（M 系列）、dimension_filters 键 ∈ 维度白名单、
  time_range 绑定日期维度，查询命中 metrics.db 物化表（预聚合，不现场算），读前过 T3 版本守卫；
  ContractExecutor.execute 开头按 has_metric 分派：metric → _execute_metric（物化路径），
  否则走 v0.1 对象路径（行为完全不变）；
- count_distinct 聚合函数（v0.1 普通聚合同样支持）；
- time_range（{from, to} ISO 日期）——metric 块内绑定日期维度；非 metric 契约绑定对象唯一 date 字段。
- 读侧权限（P1.5 decide(read) 接线，设计 §3.3）：permission_ctx 非 None 时查询前
decide(subject, object_type, 'read')，属性级 visible_attributes 过滤返回列，
契约显式请求的字段触及不可见列 fail-closed 拒答（不静默裁剪，防推断泄漏）。
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin

import duckdb

from src.des.config import DEFAULT_ENTERPRISES_DIR
from src.des.materialize import DesMaterialization, materialize_des, rows_as_dicts
from src.des.metrics import (
    METRIC_META_TABLE,
    METRICS_DB,
    SOURCE_COLUMNS,
    DimensionField,
    MetricDef,
    MetricRegistry,
    date_dimension_grain,
    is_date_dimension,
    metric_table_name,
)
from src.ontology import build_registry
from src.ontology.registry import Registry
from src.runtime.permissions import PermissionRegistry, PermissionSubject

# ---------------------------------------------------------------------------
# 常量（契约 schema 白名单 / 护栏上限，设计 §3.1/§3.3）
# ---------------------------------------------------------------------------
CONTRACT_KEYS = {
    "contract_version", "object_type", "filters", "aggregations",
    "group_by", "link_traversal", "metric", "time_range",
}
FILTER_EXPR_KEYS = {"op", "value"}
METRIC_KEYS = {"metric_id", "dimension_filters", "time_range", "group_by"}
TIME_RANGE_KEYS = {"from", "to"}
OPS = ("eq", "ne", "is_null", "is_not_null", "in")
AGG_FUNCS = ("count", "sum", "avg", "min", "max", "count_distinct")  # v0.2 追加 count_distinct
RESULT_LIMIT_FLOOR = 1000  # V5 结果护栏下限（实际上限从配置派生 = max(下限, 2×round(N×rate))，禁硬编码）
MAX_AGGREGATIONS = 5  # V5
MAX_GROUP_BY = 4  # V5
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # time_range ISO 日期（V2）
# 物化表子集重聚合（group_by）仅可加聚合合法：sum/count 加法、min/max 幂等；avg/count_distinct 非可加拒答
_METRIC_REAGG_SQL = {"sum": "SUM", "count": "SUM", "min": "MIN", "max": "MAX"}
_SQL_FRAGMENT_MARKERS = ("'", '"', ";", "--", "/*", "*/")
_SQL_KEYWORDS = re.compile(r"\b(select|union|insert|delete|update|drop|alter)\b", re.IGNORECASE)
PERMISSION_DENIED = "PERMISSION_DENIED"  # 读侧权限拒绝错误码（设计 §3.3，fail-closed 拒答）

# DQ-01「哪些物料一物多码？」契约实例（设计 §3.2）
DQ01_CONTRACT = {
    "contract_version": "0.1",
    "object_type": "Material",
    "filters": {"old_code": {"op": "is_not_null"}},
    "aggregations": [],
    "group_by": [],
    "link_traversal": {"link": "material.codes", "hops": 1},
}


class ContractError(Exception):
    """契约校验/执行失败（fail-closed 拒答，不降级为裸执行）。"""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        # 未显式传 code 时回落到子类类属性（PermissionDeniedError.code=PERMISSION_DENIED）
        self.code = code if code is not None else getattr(type(self), "code", None)


class PermissionDeniedError(ContractError):
    """读侧权限拒绝（设计 §3.3：fail-closed 拒答，不静默裁剪防推断泄漏）。

    与 ContractError 同族（既有 pytest.raises(ContractError) 兼容不破坏）；
    附加 code=PERMISSION_DENIED 供上层映射错误码/拒答语义。
    """

    code = PERMISSION_DENIED


@dataclass(frozen=True)
class PermissionContext:
    """读侧权限上下文（设计 §3.3）：主体 + 权限注册表。

    传给 ContractExecutor 即启用读侧权限：查询前 decide(subject, object_type, "read")，
    属性级 visible_attributes 过滤返回列；契约显式请求的字段触及不可见列 fail-closed 拒答
    （不静默裁剪，防推断泄漏）。缺省 None = 无权限校验（保持既有调用兼容）。
    """

    subject: PermissionSubject
    permission_registry: PermissionRegistry


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
        if fname not in dims:
            v.append(f"dimension_filters 字段不在 {mid} 维度白名单: {fname!r}")
            continue
        v.extend(_validate_filter_expr(fname, expr, _dimension_value_check(fname, md, fname)))

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


# ---------------------------------------------------------------------------
# 执行器
# ---------------------------------------------------------------------------
def _expr_op(expr: Any) -> str:
    """取过滤表达式的操作符（标量简写 = 等值）。"""
    return expr.get("op") if isinstance(expr, dict) else "eq"


def _build_where(filters: dict) -> tuple[str, list[Any]]:
    """把白名单校验过的 filters 转成参数化 WHERE（字段名 = 白名单标识符，值一律 ? 绑定）。"""
    clauses: list[str] = []
    params: list[Any] = []
    for field, expr in sorted(filters.items()):
        op, value = _expr_op(expr), (expr.get("value") if isinstance(expr, dict) else expr)
        if op == "eq":
            clauses.append(f"{field} = ?")
            params.append(value)
        elif op == "ne":
            clauses.append(f"{field} != ?")
            params.append(value)
        elif op == "is_null":
            clauses.append(f"{field} IS NULL")
        elif op == "is_not_null":
            clauses.append(f"{field} IS NOT NULL")
        elif op == "in":
            clauses.append(f"{field} IN ({','.join('?' for _ in value)})")
            params.extend(value)
    return (" AND ".join(clauses) if clauses else "1=1"), params


def _compute_agg(rows: list[dict[str, Any]], agg: dict) -> dict[str, Any]:
    """单聚合计算（对已谓词过滤的行；count=行数/非空数，sum/avg/min/max 数值）。"""
    fn, fld = agg["function"], agg["field"]
    if fld == "*":
        return {"function": fn, "field": fld, "value": len(rows)}
    vals = [r[fld] for r in rows if r[fld] is not None]
    if fn == "count":
        return {"function": fn, "field": fld, "value": len(vals)}
    if fn in ("sum", "avg", "min", "max") and not vals:
        return {"function": fn, "field": fld, "value": None}
    if fn == "sum":
        return {"function": fn, "field": fld, "value": sum(vals)}
    if fn == "min":
        return {"function": fn, "field": fld, "value": min(vals)}
    if fn == "max":
        return {"function": fn, "field": fld, "value": max(vals)}
    if fn == "count_distinct":  # v0.2 扩展：COUNT(DISTINCT 字段) 去重计数
        return {"function": fn, "field": fld, "value": len(set(vals))}
    return {"function": fn, "field": fld, "value": sum(vals) / len(vals)}


class ContractExecutor:
    """契约 v0.1/v0.2 执行器：校验 → 参数化查询 → 多码谓词强制 → 结果护栏。

    v0.1 对象路径（默认）：DuckDB 动态派生（过滤/聚合/≤1 跳 link_traversal）；
    v0.2 指标路径（contract 含 metric）：命中 metrics.db 预聚合表（不现场算，设计 §3.2）。
    """

    def __init__(
        self,
        materialization: DesMaterialization,
        registry: Registry,
        metrics: MetricRegistry | None = None,
        metrics_db: Path | None = None,
        permission_ctx: PermissionContext | None = None,
    ) -> None:
        """metrics：指标注册表（v0.2 metric 路径必需；未注入时含 metric 契约 fail-closed 拒答）。

        metrics_db：metrics.db 路径（默认 = 企业目录 / metrics.db，与 manifest.json 同目录，
        供 T3 版本守卫比对）。
        permission_ctx：读侧权限上下文（设计 §3.3，P1.5 接线）；缺省 None = 无权限校验，
        保持既有调用兼容。非 None 时 execute/_execute_metric 前置 decide(read) 并做可见列过滤。
        """
        self._mz = materialization
        self._registry = registry
        self._metrics = metrics
        self._conn = materialization.duckdb
        self._legacy_re = materialization.legacy_re
        self._metrics_db = metrics_db or (
            DEFAULT_ENTERPRISES_DIR / materialization.enterprise_code / METRICS_DB
        )
        self._permission_ctx = permission_ctx

    def execute(self, contract: dict) -> dict:
        """校验并执行契约；任一校验失败抛 ContractError（fail-closed 拒答）。

        contract 含 metric → v0.2 指标物化路径（_execute_metric）；
        否则走 v0.1 对象路径（行为完全不变）。
        """
        if isinstance(contract, dict) and contract.get("metric") is not None:
            return self._execute_metric(contract)
        violations = validate_contract(contract, self._registry, self._metrics)
        if violations:
            raise ContractError("契约校验失败（fail-closed 拒答）: " + "; ".join(violations))
        obj = _resolve_type(self._registry, contract["object_type"])
        # 读侧权限（设计 §3.3：validate 后、execute 前）：decide(read) + 显式请求列可见性 fail-closed
        visible = self._permission_visible(obj.name)
        requested = [obj.pk_field] + list((contract.get("filters") or {}).keys())
        requested += [
            a.get("field") for a in (contract.get("aggregations") or []) if a.get("field") != "*"
        ]
        requested += contract.get("group_by") or []
        self._assert_fields_visible(visible, requested, obj.name)
        where, params = _build_where(contract.get("filters") or {})
        sql = f"SELECT * FROM {obj.source_table} WHERE {where} ORDER BY {obj.pk_field}"
        try:
            rows = rows_as_dicts(self._conn, sql, params)
        except Exception as exc:  # 表不存在/类型错误即 fail-closed
            raise ContractError(f"契约执行失败（fail-closed 拒答）: {exc}") from exc
        limit = self._result_limit()
        if len(rows) > limit:
            raise ContractError(f"结果行数 {len(rows)} 超过护栏上限 {limit}（V5，请加过滤）")

        # 多码谓词强制（设计 §3.2：对 old_code 非空结果集再过 §2.2 全谓词，口径单点化）
        excluded = 0
        if self._needs_multi_code_predicate(contract):
            kept = [r for r in rows if self._is_multi_code(r)]
            excluded = len(rows) - len(kept)
            rows = kept

        if contract.get("aggregations"):
            return self._run_aggregation(contract, obj, rows, excluded)
        items = self._build_items(obj, rows, contract.get("link_traversal"), visible)
        result = {"object_type": obj.name, "count": len(items), "items": items}
        if excluded:
            result["_diagnostics"] = {"predicate_excluded": excluded}
        return result

    def _result_limit(self) -> int:
        """V5 结果护栏上限：从生效配置派生（禁硬编码 1000）——max(下限, 2×round(N×rate))。

        保证 DQ-01 全量结果（round(N×rate) 条）可放行，同时按量级封顶大结果集（如未过滤的全表）；
        N = MARA 行数、rate = multi_code 注入率，均取自定义配置（单一事实来源）。
        """
        config = self._mz.config
        mara = config["enterprise"]["systems"]["erp"]["tables"]["MARA"]["row_count"]
        rate = config["injection"]["multi_code"]["rate"]
        return max(RESULT_LIMIT_FLOOR, 2 * round(mara * rate))

    # ------------------------------------------------------------------
    # 读侧权限（设计 §3.3：P1.5 decide(read) 接线；fail-closed 不静默裁剪）
    # ------------------------------------------------------------------
    def _permission_visible(self, object_type: str) -> list[str] | None:
        """前置 decide(subject, object_type, 'read')：allowed=False → fail-closed 拒答。

        返回 visible_attributes（读侧可见属性列表，属性级 deny 已剔除）；无权限上下文 → None
        （不校验，兼容既有调用）。allowed 但可见集缺失（decide 异常态）保守视为全字段可见。
        """
        ctx = self._permission_ctx
        if ctx is None:
            return None
        decision = ctx.permission_registry.decide(ctx.subject, object_type, "read")
        if not decision.allowed:
            raise PermissionDeniedError(
                f"读侧权限拒绝: 主体 {ctx.subject.kind}:{ctx.subject.id} 无 {object_type} 的 "
                "read 权限（fail-closed）"
            )
        if decision.visible_attributes is not None:
            return decision.visible_attributes
        if self._registry.has_object_type(object_type):  # 异常态兜底：全字段可见
            return list(self._registry.object_type(object_type).model.model_fields)
        return None

    def _object_fields(self, object_type: str, names: list[str]) -> list[str]:
        """把请求列裁剪到对象字段（指标派生列/度量列非对象字段，不受属性级 deny 约束）。"""
        if not self._registry.has_object_type(object_type):
            return []
        fields = self._registry.object_type(object_type).model.model_fields
        return [n for n in names if n in fields]

    def _assert_fields_visible(
        self, visible: list[str] | None, fields: list[str], what: str
    ) -> None:
        """契约显式请求的字段触及不可见列 → fail-closed 拒答（不静默裁剪，防推断泄漏）。

        visible=None（无权限上下文）或请求为空时不触发；重复字段去重后判定。
        """
        if visible is None:
            return
        invisible = sorted(f for f in set(fields) if f is not None and f not in visible)
        if invisible:
            raise PermissionDeniedError(
                f"读侧权限拒绝（{what}）: 请求字段不可见 {invisible}（属性级 deny，fail-closed）"
            )

    def _filter_metric_rows(
        self, rows: list[dict[str, Any]], visible: list[str] | None, md: MetricDef
    ) -> list[dict[str, Any]]:
        """返回行按可见列过滤（设计 §3.3）：对象字段列仅保留可见者；度量/派生列（非对象字段）为指标答案保留。

        visible=None（无权限上下文）或 rows 为空 → 原样返回。
        """
        if visible is None or not rows:
            return rows
        obj_fields: set[str] = set()
        if self._registry.has_object_type(md.object_type):
            obj_fields = set(self._registry.object_type(md.object_type).model.model_fields)
        keep = [c for c in rows[0] if c not in obj_fields or c in visible]
        return [{k: v for k, v in r.items() if k in keep} for r in rows]

    def _needs_multi_code_predicate(self, contract: dict) -> bool:
        """契约是否以 old_code is_not_null 选中一物多码结果集（触发全谓词强制）。"""
        filters = contract.get("filters") or {}
        return "old_code" in filters and _expr_op(filters["old_code"]) == "is_not_null"

    def _is_multi_code(self, row: dict[str, Any]) -> bool:
        """一物多码判定谓词（设计 §2.2）：BISMT 非空 ∧ ≠matnr ∧ 匹配旧码正则。"""
        old = row.get("old_code")
        return (
            old is not None
            and str(old) != str(row.get("matnr"))
            and bool(self._legacy_re.match(str(old)))
        )

    def _run_aggregation(
        self, contract: dict, obj: Any, rows: list[dict[str, Any]], excluded: int
    ) -> dict:
        """聚合执行：无 group_by → 标量；有 group_by → 分组（设计 §3.1）。"""
        gb = contract.get("group_by") or []
        result: dict[str, Any] = {"object_type": obj.name, "row_count": len(rows)}
        if not gb:
            result["aggregations"] = [_compute_agg(rows, a) for a in contract["aggregations"]]
        else:
            groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
            for r in rows:
                groups[tuple(str(r[g]) for g in gb)].append(r)
            result["groups"] = [
                {
                    "group": dict(zip(gb, key)),
                    "aggregations": [_compute_agg(grp, a) for a in contract["aggregations"]],
                }
                for key, grp in sorted(groups.items())
            ]
        if excluded:
            result["_diagnostics"] = {"predicate_excluded": excluded}
        return result

    def _build_items(
        self,
        obj: Any,
        rows: list[dict[str, Any]],
        link_traversal: dict | None,
        visible: list[str] | None = None,
    ) -> list[dict]:
        """组装 items：properties 为可见列（permission_ctx 下 = visible_attributes，属性级 deny 剔除）；
        link_traversal（material.codes, hops=1）带回 codes 数组。"""
        fields = list(visible) if visible is not None else list(obj.model.model_fields)
        by_pk: dict[str, list[dict]] = defaultdict(list)
        if link_traversal:
            link = _find_link(self._registry, obj, link_traversal["link"])
            target = self._registry.object_type(link.target_type)
            for c in rows_as_dicts(self._conn, f"SELECT * FROM {target.source_table}", []):
                by_pk[c[link.fk_field]].append({"code_space": c["code_space"], "value": c["value"]})
            for codes in by_pk.values():
                codes.sort(key=lambda c: c["code_space"])
        items = []
        for r in rows:
            pk = str(r[obj.pk_field])
            item: dict[str, Any] = {"pk": pk, "properties": {k: r[k] for k in fields}}
            if link_traversal:
                item["codes"] = by_pk.get(pk, [])
            items.append(item)
        return items

    # ------------------------------------------------------------------
    # v0.2 指标物化路径（设计 §3.2：命中 metrics.db 预聚合表，不现场算）
    # ------------------------------------------------------------------
    def _execute_metric(self, contract: dict) -> dict:
        """执行 v0.2 指标契约：M 系列校验 → T3 版本守卫 → 查 metrics.db 物化表。

        返回 {object_type, metric_id, count, rows}；结果护栏与 v0.1 一致（V5）。
        """
        if self._metrics is None:
            raise ContractError("契约含 metric 但执行器未注入指标注册表（M 系列 fail-closed）")
        violations = validate_contract(contract, self._registry, self._metrics)
        if violations:
            raise ContractError("契约校验失败（fail-closed 拒答）: " + "; ".join(violations))
        if not self._metrics_db.is_file():
            raise ContractError(f"metrics.db 缺失: {self._metrics_db}（先运行 materialize_metrics）")
        md = self._metrics.by_id()[contract["metric"]["metric_id"]]
        # 读侧权限（设计 §3.3）：资源 = 指标主体对象；维度/度量列过滤（对象字段受属性级约束）
        visible = self._permission_visible(md.object_type)
        requested = list((contract["metric"].get("dimension_filters") or {}).keys())
        tr = contract["metric"].get("time_range") if contract["metric"].get("time_range") is not None else contract.get("time_range")
        if tr is not None:
            requested.append(self._date_dimension(md).name)
        requested += contract["metric"].get("group_by") or []
        requested = self._object_fields(md.object_type, requested)  # 指标派生列（非对象字段）不受属性级约束
        self._assert_fields_visible(visible, requested, md.object_type)
        conn = duckdb.connect(str(self._metrics_db), read_only=True)
        try:
            self._guard_version(conn)  # T3 版本守卫（漂移 fail-fast）
            where, params = self._metric_where(contract, md)
            gb = contract["metric"].get("group_by") or []
            rows = self._query_metric(conn, md, gb, where, params)
        finally:
            conn.close()
        limit = self._result_limit()
        if len(rows) > limit:
            raise ContractError(f"结果行数 {len(rows)} 超过护栏上限 {limit}（V5，请加过滤）")
        rows = self._filter_metric_rows(rows, visible, md)
        return {
            "object_type": md.object_type,
            "metric_id": md.metric_id,
            "count": len(rows),
            "rows": rows,
        }

    def _guard_version(self, conn: Any) -> None:
        """T3 查询侧版本守卫（设计 §2.2(3)）：metric_meta.data_version/config_sha256 vs manifest。

        与 metrics_materialize.check_metrics_version 同源口径（单一事实来源 = manifest.json）；
        漂移（源数据变更后未刷新）即抛 ContractError（fail-closed：拒答并提示刷新）。
        """
        man_path = self._metrics_db.parent / "manifest.json"
        if not man_path.is_file():
            raise ContractError(f"manifest 缺失: {man_path}（先运行 python -m src.des --enterprise <code>）")
        man = json.loads(man_path.read_text(encoding="utf-8"))
        rows = conn.execute(
            f"SELECT metric_id, data_version, config_sha256 FROM {METRIC_META_TABLE} ORDER BY metric_id"
        ).fetchall()
        if not rows:
            raise ContractError(f"{METRIC_META_TABLE} 为空（尚未物化）: {self._metrics_db}")
        drifted = [
            f"{mid}: 物化 {dv}/{sha} ≠ manifest {man['data_version']}/{man['config_sha256']}"
            for mid, dv, sha in rows
            if dv != man["data_version"] or sha != man["config_sha256"]
        ]
        if drifted:
            raise ContractError("数据版本漂移，请刷新（T3 fail-closed）: " + "; ".join(drifted))

    def _metric_where(self, contract: dict, md: MetricDef) -> tuple[str, list[Any]]:
        """指标 WHERE：dimension_filters 参数化（V4）+ time_range 绑定日期维度。

        物化表列名 = 维度语义名（metric_table_name 约定）；time_range 值按日期维度粒度
        截断（substr(1,7) → 前 7 位 YYYY-MM）后比较；块内 time_range 优先于顶层。
        """
        metric = contract["metric"]
        where, params = _build_where(metric.get("dimension_filters") or {})
        tr = metric.get("time_range") if metric.get("time_range") is not None else contract.get("time_range")
        if tr is not None:
            dim = self._date_dimension(md)
            grain = date_dimension_grain(dim)
            frm = tr["from"][:grain] if grain else tr["from"]
            to = tr["to"][:grain] if grain else tr["to"]
            where = f"{where} AND {dim.name} >= ? AND {dim.name} <= ?"
            params += [frm, to]
        return where, params

    def _date_dimension(self, md: MetricDef) -> DimensionField:
        """指标时间维度（time_range 绑定点）：带 substr 派生的日期维度（校验已保证存在）。"""
        for d in md.dimension_fields:
            if is_date_dimension(d):
                return d
        raise ContractError(f"指标 {md.metric_id} 无日期维度，time_range 无法绑定（校验应已拦截）")

    def _query_metric(
        self, conn: Any, md: MetricDef, gb: list[str], where: str, params: list[Any]
    ) -> list[dict[str, Any]]:
        """查 metric_<id> 物化表（参数化，V4）：无 group_by → 维度全列 + 度量列；
        有 group_by → 物化表子集重聚合（仅可加聚合 sum/count/min/max，校验已挡 avg/count_distinct）。

        表名/列名全为注册表派生常量（无用户输入，无注入面），值一律 ? 绑定。
        """
        table = metric_table_name(md.metric_id)
        measure_col = md.measure.name
        if gb:
            select = ", ".join(
                gb + [f"{_METRIC_REAGG_SQL[md.agg_function]}({measure_col}) AS {measure_col}"]
            )
            order = ", ".join(gb)
            sql = f"SELECT {select} FROM {table} WHERE {where} GROUP BY {order} ORDER BY {order}"
        else:
            cols = ", ".join([d.name for d in md.dimension_fields] + [measure_col])
            order = ", ".join(d.name for d in md.dimension_fields)
            sql = f"SELECT {cols} FROM {table} WHERE {where} ORDER BY {order}"
        try:
            return rows_as_dicts(conn, sql, params)
        except Exception as exc:  # 表缺失/类型错误即 fail-closed
            raise ContractError(f"指标执行失败（fail-closed 拒答）: {exc}") from exc


# ---------------------------------------------------------------------------
# DQ-01 跑通 + 对账（设计 §2.3/§3.2/§4.3）
# ---------------------------------------------------------------------------
@dataclass
class ReconcileResult:
    """DQ-01 三方对账结果：本体查询 vs 数据侧注入集 vs manifest。"""

    ok: bool
    expected_count: int
    actual_count: int
    ratio: float
    differences: list[str]


def reconcile_dq01(
    result: dict,
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    manifest: dict | None = None,
) -> ReconcileResult:
    """本体查询结果 vs 数据侧注入集 + manifest.multi_code_count 三方对账（设计 §2.3）。"""
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    conn = sqlite3.connect(str(out / "erp.db"))
    try:
        data_side = [r[0] for r in conn.execute("SELECT MATNR FROM MARA WHERE BISMT IS NOT NULL ORDER BY MATNR")]
    finally:
        conn.close()
    if manifest is None:
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    erp_entry = manifest["tables"]["erp.MARA"]
    onto_side = [item["pk"] for item in result.get("items", [])]
    n = int(erp_entry["rows"])
    expected = int(erp_entry["multi_code_count"])
    differences = sorted(set(onto_side) ^ set(data_side))
    if len(onto_side) != len(data_side):
        differences.append(f"条数不一致: 本体 {len(onto_side)} ≠ 数据侧 {len(data_side)}")
    ok = not differences and len(onto_side) == expected
    return ReconcileResult(
        ok=ok,
        expected_count=expected,
        actual_count=len(onto_side),
        ratio=len(onto_side) / n if n else 0.0,
        differences=differences,
    )


def run_dq01(
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    registry: Registry | None = None,
) -> tuple[dict, DesMaterialization]:
    """物化 + 执行 DQ-01，返回 (查询结果, 物化对象)。调用方负责 mz.duckdb.close()。"""
    reg = registry or build_registry()
    mz = materialize_des(enterprise_code, out_dir=out_dir, registry=reg)
    return ContractExecutor(mz, reg).execute(DQ01_CONTRACT), mz
