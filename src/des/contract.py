"""结构化查询契约 v0.1 校验 + 执行器（设计 §3）。

- V1-V5 校验 fail-closed（设计 §3.3）：字段白名单查 Registry / 类型约束 / ≤1 跳 / 防注入参数化 / 结果护栏；
- 执行：过滤 + 聚合 + group_by + link_traversal（≤1 跳）参数化执行，契约值永不拼 SQL（V4）；
- DQ-01「哪些物料一物多码？」：执行器对 old_code 非空结果集强制再过一物多码全谓词（§2.2），口径单点化；
- reconcile_dq01：本体查询结果 vs 数据侧注入集 + manifest.multi_code_count 三方对账（§2.3）。
"""

from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin

from src.des.config import DEFAULT_ENTERPRISES_DIR
from src.des.materialize import DesMaterialization, materialize_des, rows_as_dicts
from src.ontology import build_registry
from src.ontology.registry import Registry

# ---------------------------------------------------------------------------
# 常量（契约 schema 白名单 / 护栏上限，设计 §3.1/§3.3）
# ---------------------------------------------------------------------------
CONTRACT_KEYS = {"contract_version", "object_type", "filters", "aggregations", "group_by", "link_traversal"}
FILTER_EXPR_KEYS = {"op", "value"}
OPS = ("eq", "ne", "is_null", "is_not_null", "in")
AGG_FUNCS = ("count", "sum", "avg", "min", "max")
RESULT_LIMIT = 1000  # V5 结果行数上限
MAX_AGGREGATIONS = 5  # V5
MAX_GROUP_BY = 4  # V5
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


class ContractError(Exception):
    """契约校验/执行失败（fail-closed 拒答，不降级为裸执行）。"""


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


def _validate_filter_expr(fname: str, expr: Any, field_info: Any) -> list[str]:
    """校验单个过滤表达式（标量简写 = 等值；对象含 op/value，V2/V4）。"""
    v: list[str] = []
    if isinstance(expr, (str, int, float, bool)):
        _check_value_type(v, fname, expr, field_info)
        _check_sql_fragment(v, fname, expr)
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
            _check_value_type(v, fname, item, field_info)
            _check_sql_fragment(v, fname, item)
        return v
    _check_value_type(v, fname, value, field_info)
    _check_sql_fragment(v, fname, value)
    return v


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


def validate_contract(contract: Any, registry: Registry) -> list[str]:
    """契约 v0.1 校验（V1-V5）。返回违规列表；空列表 = 通过（fail-closed：非空即拒答）。"""
    v: list[str] = []
    if not isinstance(contract, dict):
        return ["契约必须为 JSON 对象"]
    unknown = set(contract) - CONTRACT_KEYS
    if unknown:
        v.append(f"未知顶层键（additionalProperties:false）: {sorted(unknown)}")

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
        v.extend(_validate_filter_expr(fname, expr, fields[fname]))

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
    return {"function": fn, "field": fld, "value": sum(vals) / len(vals)}


class ContractExecutor:
    """契约 v0.1 执行器：校验 → 参数化查询 → 多码谓词强制 → 结果护栏。"""

    def __init__(self, materialization: DesMaterialization, registry: Registry) -> None:
        self._mz = materialization
        self._registry = registry
        self._conn = materialization.duckdb
        self._legacy_re = materialization.legacy_re

    def execute(self, contract: dict) -> dict:
        """校验并执行契约；任一校验失败抛 ContractError（fail-closed 拒答）。"""
        violations = validate_contract(contract, self._registry)
        if violations:
            raise ContractError("契约校验失败（fail-closed 拒答）: " + "; ".join(violations))
        obj = _resolve_type(self._registry, contract["object_type"])
        where, params = _build_where(contract.get("filters") or {})
        sql = f"SELECT * FROM {obj.source_table} WHERE {where} ORDER BY {obj.pk_field}"
        try:
            rows = rows_as_dicts(self._conn, sql, params)
        except Exception as exc:  # 表不存在/类型错误即 fail-closed
            raise ContractError(f"契约执行失败（fail-closed 拒答）: {exc}") from exc
        if len(rows) > RESULT_LIMIT:
            raise ContractError(f"结果行数 {len(rows)} 超过护栏上限 {RESULT_LIMIT}（V5，请加过滤）")

        # 多码谓词强制（设计 §3.2：对 old_code 非空结果集再过 §2.2 全谓词，口径单点化）
        excluded = 0
        if self._needs_multi_code_predicate(contract):
            kept = [r for r in rows if self._is_multi_code(r)]
            excluded = len(rows) - len(kept)
            rows = kept

        if contract.get("aggregations"):
            return self._run_aggregation(contract, obj, rows, excluded)
        items = self._build_items(obj, rows, contract.get("link_traversal"))
        result = {"object_type": obj.name, "count": len(items), "items": items}
        if excluded:
            result["_diagnostics"] = {"predicate_excluded": excluded}
        return result

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
        self, obj: Any, rows: list[dict[str, Any]], link_traversal: dict | None
    ) -> list[dict]:
        """组装 items：properties 全字段；link_traversal（material.codes, hops=1）带回 codes 数组。"""
        fields = list(obj.model.model_fields)
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
