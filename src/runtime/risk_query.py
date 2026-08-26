"""S3 M3b 风险读引擎 —— 受限结构化查询执行器（RiskQuery）。

自然语言经 LLM 映射为**受限契约**（{object_type, filters, group_by, aggregations}）
→ 结构校验（fail-closed）→ 参数化 SQL 执行 ap_anping 六库 → 结构化结果供 LLM
生成自然语言答案。LLM 输出视为不可信输入：不直接执行 LLM 生成的 SQL，只允许经
src.runtime.risk_query_spec（可表达集单一真相）白名单的 对象/字段/操作符/聚合 组合。

fail-closed 语义（域外拒答，Agent 层映射为 DECLINE + 可查项引导）：
- object_type 不在可查询集（或属无源表对象）→ 拒答；
- filter/group_by/aggregation/order_by 字段不在该对象可查询字段表 → 拒答；
- 操作符/聚合函数不在白名单 → 拒答；隐式结果超护栏 → 拒答（提示加过滤/显式 limit）。

数据源：RiskStore（risk.db 主库 + 5 库 ATTACH，跨库查询同连接）。执行层只读。
"""

from __future__ import annotations

import sqlite3
from typing import Any

from pydantic import ValidationError

from src.ontology.registry import Registry
from src.runtime.risk_db import RiskStore, build_risk_source_registry
from src.runtime.risk_query_spec import (
    AGG_FUNCTIONS,
    ANALYTIC_PARAMS,
    ANALYTIC_SQL,
    FILTER_OPS,
    MAX_ANALYTIC_ROWS,
    MAX_FILTERS,
    MAX_LIMIT,
    NOT_QUERYABLE_OBJECTS,
    RISK_QUERY_DERIVED,
    RISK_QUERY_FIELDS,
    adapt_status,
)


class RiskQueryError(Exception):
    """读引擎错误基类（fail-closed 拒答；Agent 层映射为 DECLINE）。"""

    code = "RISK_QUERY_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.code = code or self.__class__.code
        super().__init__(message)


class UnknownObjectType(RiskQueryError):
    code = "UNKNOWN_OBJECT_TYPE"


class ObjectNotQueryable(RiskQueryError):
    code = "OBJECT_NOT_QUERYABLE"


class UnknownFilterField(RiskQueryError):
    code = "UNKNOWN_FILTER_FIELD"


class InvalidFilterOperator(RiskQueryError):
    code = "INVALID_FILTER_OPERATOR"


class InvalidAggregation(RiskQueryError):
    code = "INVALID_AGGREGATION"


class InvalidOrderBy(RiskQueryError):
    code = "INVALID_ORDER_BY"


class InvalidContract(RiskQueryError):
    code = "INVALID_CONTRACT"


class ResultTooLarge(RiskQueryError):
    code = "RESULT_TOO_LARGE"


class InvalidAnalytic(RiskQueryError):
    code = "INVALID_ANALYTIC"


class UnknownAnalytic(RiskQueryError):
    code = "UNKNOWN_ANALYTIC"


def _resolve_object(registry: Registry, api_name: str) -> Any:
    for obj in registry.object_types():
        if obj.api_name == api_name:
            return obj
    raise UnknownObjectType(f"未知对象类型: {api_name}")


def _sql_op(op: str) -> str:
    return {
        "eq": "=",
        "ne": "!=",
        "gt": ">",
        "ge": ">=",
        "lt": "<",
        "le": "<=",
        "contains": "LIKE",
        "is_null": "IS NULL",
        "is_not_null": "IS NOT NULL",
    }[op]


def _agg_expr(fn: str, column: str) -> str:
    if fn == "count" and column == "*":
        return "COUNT(*)"
    if fn == "count":
        return f"COUNT({column})"
    if fn == "count_distinct":
        return f"COUNT(DISTINCT {column})"
    return f"{fn.upper()}({column})"


class RiskQuery:
    """风险读引擎：受限契约 → 参数化 SQL 执行 ap_anping 六库（只读，fail-closed）。"""

    def __init__(
        self, registry: Registry | None = None, store: RiskStore | None = None
    ) -> None:
        self._registry = registry or build_risk_source_registry()
        self._store = store or RiskStore()
        self._as_of: str | None = None

    # ---- 对外入口 ----

    def as_of_date(self) -> str:
        """数据截至日期（演示口径单一来源：源数据 MAX(signal_generate_date)）。"""
        if self._as_of is None:
            with self._source() as conn:
                row = conn.execute(
                    "SELECT MAX(signal_generate_date) FROM ap_warning_signal"
                ).fetchone()
            self._as_of = row[0] if row and row[0] else "2026-12-31"
        return self._as_of

    def queryable_objects(self) -> list[str]:
        return sorted(RISK_QUERY_FIELDS.keys())

    def execute(self, contract: dict) -> dict:
        """执行受限契约；任一校验失败抛 RiskQueryError（fail-closed 拒答）。"""
        if not isinstance(contract, dict):
            raise InvalidContract("契约必须是 JSON 对象")
        if contract.get("analytic"):
            return self._execute_analytic(contract)
        return self._execute_object_query(contract)

    # ---- 基本对象查询（object_type + filters + group_by + aggregations） ----

    def _execute_object_query(self, contract: dict) -> dict:
        api_name = contract.get("object_type")
        if not isinstance(api_name, str) or not api_name:
            raise InvalidContract("缺少 object_type（或提供 analytic 名称）")
        if api_name in NOT_QUERYABLE_OBJECTS:
            raise ObjectNotQueryable(
                f"对象 {api_name} 暂不可查（{NOT_QUERYABLE_OBJECTS[api_name]}）"
            )
        fields = RISK_QUERY_FIELDS.get(api_name)
        if fields is None:
            if any(o.api_name == api_name for o in self._registry.object_types()):
                raise ObjectNotQueryable(
                    f"对象 {api_name} 已注册但无源表映射，暂不可查"
                )
            raise UnknownObjectType(f"未知对象类型: {api_name}")
        obj = _resolve_object(self._registry, api_name)
        derived = RISK_QUERY_DERIVED.get(api_name, {})
        all_fields = {**fields, **derived}

        filters = self._validate_filters(contract, api_name, fields)
        group_by = self._validate_group_by(contract, api_name, fields)
        aggregations = self._validate_aggregations(contract, api_name, fields)
        order_by = self._validate_order_by(
            contract, api_name, all_fields, aggregations, group_by
        )
        limit, explicit = self._validate_limit(contract)

        where, params = self._build_where(filters, fields)
        table = obj.source_table
        if aggregations:
            return self._run_aggregate(
                api_name,
                table,
                where,
                params,
                group_by,
                aggregations,
                order_by,
                limit,
                explicit,
            )
        return self._run_rows(
            api_name, table, where, params, order_by, limit, explicit, fields, derived
        )

    def _validate_filters(
        self, contract: dict, api_name: str, fields: dict
    ) -> list[dict]:
        raw = contract.get("filters") or []
        if not isinstance(raw, list):
            raise InvalidContract("filters 必须是数组")
        if len(raw) > MAX_FILTERS:
            raise InvalidContract(f"过滤条件超过上限 {MAX_FILTERS}")
        out: list[dict] = []
        for f in raw:
            if not isinstance(f, dict):
                raise InvalidContract("过滤项必须是对象 {field, op, value}")
            field = f.get("field")
            if field not in fields:
                raise UnknownFilterField(
                    f"{api_name}.{field} 不在可查询字段（可查: {', '.join(sorted(fields))}）"
                )
            op = f.get("op") or "eq"
            if op not in FILTER_OPS:
                raise InvalidFilterOperator(
                    f"操作符 {op} 不在白名单（{', '.join(FILTER_OPS)}）"
                )
            value = f.get("value")
            if op in ("is_null", "is_not_null"):
                value = None
            elif op == "contains":
                if not isinstance(value, str):
                    raise InvalidContract("contains 值必须是字符串")
                value = f"%{value}%"
            elif op == "in":
                if not isinstance(value, list) or not value:
                    raise InvalidContract("in 值必须是非空数组")
                value = [adapt_status(field, v) for v in value]
            else:
                value = adapt_status(field, value)
            out.append({"field": field, "op": op, "value": value})
        return out

    def _validate_group_by(
        self, contract: dict, api_name: str, fields: dict
    ) -> list[tuple[str, str]]:
        raw = contract.get("group_by") or []
        if not isinstance(raw, list):
            raise InvalidContract("group_by 必须是数组")
        out: list[tuple[str, str]] = []
        for g in raw:
            granularity: str | None = None
            if isinstance(g, dict):
                g_field, granularity = g.get("field"), g.get("granularity")
            else:
                g_field = g
            if g_field not in fields:
                raise UnknownFilterField(
                    f"{api_name}.{g_field} 不在可查询字段（不可按此分组）"
                )
            col = fields[g_field]
            if granularity:
                if granularity not in ("month", "day"):
                    raise InvalidContract(
                        f"group_by 粒度仅支持 month/day（{granularity}）"
                    )
                expr = f"substr({col},1,{7 if granularity == 'month' else 10})"
                out.append((g_field, expr))
            else:
                out.append((g_field, col))
        return out

    def _validate_aggregations(
        self, contract: dict, api_name: str, fields: dict
    ) -> list[dict]:
        raw = contract.get("aggregations") or []
        if not isinstance(raw, list):
            raise InvalidContract("aggregations 必须是数组")
        if len(raw) > 5:
            raise InvalidContract("聚合项超过上限 5")
        out: list[dict] = []
        for a in raw:
            if not isinstance(a, dict):
                raise InvalidContract("聚合项必须是对象 {function, field}")
            fn, field = a.get("function"), a.get("field")
            if fn not in AGG_FUNCTIONS:
                raise InvalidAggregation(
                    f"聚合函数 {fn} 不在白名单（{', '.join(AGG_FUNCTIONS)}）"
                )
            if field != "*" and field not in fields:
                raise InvalidAggregation(
                    f"{api_name}.{field} 不可聚合（可聚合: * 或 {', '.join(sorted(fields))}）"
                )
            out.append({"function": fn, "field": field})
        return out

    def _validate_order_by(
        self,
        contract: dict,
        api_name: str,
        all_fields: dict,
        aggregations: list,
        group_by: list,
    ) -> list[dict]:
        raw = contract.get("order_by") or []
        if not isinstance(raw, list):
            raise InvalidContract("order_by 必须是数组")
        out: list[dict] = []
        for o in raw:
            if not isinstance(o, dict):
                raise InvalidContract("order_by 项必须是对象 {field, direction}")
            field, direction = o.get("field"), (o.get("direction") or "asc")
            if direction not in ("asc", "desc"):
                raise InvalidOrderBy(f"排序方向仅支持 asc/desc（{direction}）")
            if (
                aggregations
                and field in all_fields
                and field not in {g[0] for g in group_by}
            ):
                # 聚合查询按聚合字段值排序（top-N 敞口等，R04）
                out.append({"field": field, "direction": direction, "aggregate": True})
                continue
            if field not in all_fields:
                raise InvalidOrderBy(
                    f"{api_name}.{field} 不可排序（不在可查询/分组字段）"
                )
            out.append({"field": field, "direction": direction, "aggregate": False})
        return out

    @staticmethod
    def _validate_limit(contract: dict) -> tuple[int, bool]:
        """返回 (limit, 是否显式指定)。显式 limit 由调用方截断；缺省用护栏上限。"""
        raw = contract.get("limit")
        if raw is None:
            return MAX_LIMIT, False
        if (
            not isinstance(raw, int)
            or isinstance(raw, bool)
            or raw < 1
            or raw > MAX_LIMIT
        ):
            raise InvalidContract(f"limit 必须是 1..{MAX_LIMIT} 的整数")
        return raw, True

    def _build_where(self, filters: list[dict], fields: dict) -> tuple[str, list]:
        clauses: list[str] = []
        params: list[Any] = []
        for f in filters:
            col = fields[f["field"]]
            if f["op"] == "in":
                placeholders = ",".join("?" for _ in f["value"])
                clauses.append(f"{col} IN ({placeholders})")
                params.extend(f["value"])
            elif f["op"] == "is_null":
                clauses.append(f"{col} IS NULL")
            elif f["op"] == "is_not_null":
                clauses.append(f"{col} IS NOT NULL")
            else:
                clauses.append(f"{col} {_sql_op(f['op'])} ?")
                params.append(f["value"])
        return (" AND ".join(clauses) if clauses else "1=1"), params

    def _run_rows(
        self,
        api_name: str,
        table: str,
        where: str,
        params: list,
        order_by: list,
        limit: int,
        explicit: bool,
        fields: dict,
        derived: dict,
    ) -> dict:
        select_cols = [f"{c} AS {name}" for name, c in fields.items()]
        for name, expr in derived.items():
            select_cols.append(f"{expr.format(t='t')} AS {name}")
        order_sql = self._order_sql(order_by, fields, derived, aggregate=False)
        sql = (
            f"SELECT {', '.join(select_cols)} FROM {table} t WHERE {where}"
            f"{order_sql} LIMIT {limit + 1}"
        )
        with self._source() as conn:
            rows = self._query(conn, sql, params)
        truncated = len(rows) > limit
        if truncated and not explicit:
            raise ResultTooLarge(
                f"结果行数超过护栏上限 {limit}，请加过滤或显式指定 limit（当前命中 {len(rows)} 行）"
            )
        rows = rows[:limit]
        pk_field = self._pk_field(api_name)
        items = [{"pk": str(r.get(pk_field, "")), "properties": r} for r in rows]
        return {
            "object_type": api_name,
            "count": len(items),
            "items": items,
            "truncated": truncated,
        }

    @staticmethod
    def _pk_field(api_name: str) -> str:
        return {
            "risk_customer": "customer_id",
            "group_customer": "group_customer_no",
            "warning_signal": "warning_id",
            "metric": "dim_metric_id",
            "disposal": "disposal_id",
            "approve_order": "approve_order_id",
            "approve_task": "approve_task_id",
            "concentration_limit": "concentration_limit_id",
            "risk_project": "risk_project_id",
        }.get(api_name, "warning_id")

    def _run_aggregate(
        self,
        api_name: str,
        table: str,
        where: str,
        params: list,
        group_by: list,
        aggregations: list,
        order_by: list,
        limit: int,
        explicit: bool = False,
    ) -> dict:
        """聚合执行：显式列别名（group_i / agg_i）→ 字典取值（无聚合值时返回 None）。"""
        gb_exprs = [expr for _, expr in group_by]
        select_parts = [*[f"{e} AS group_{i}" for i, (_, e) in enumerate(group_by)]]
        select_parts += [
            f"{_agg_expr(a['function'], a['field'])} AS agg_{i}"
            for i, a in enumerate(aggregations)
        ]
        sql = f"SELECT {', '.join(select_parts)} FROM {table} t WHERE {where}"
        if gb_exprs:
            sql += " GROUP BY " + ", ".join(gb_exprs)
        sql += self._order_sql(
            order_by, dict(group_by), {}, aggregate=True, aggregations=aggregations
        )
        sql += f" LIMIT {limit + 1}"
        with self._source() as conn:
            rows = self._query(conn, sql, params)
        truncated = len(rows) > limit
        if truncated and not explicit:
            raise ResultTooLarge(
                f"分组结果超过护栏上限 {limit}，请加过滤或显式指定 limit"
            )
        rows = rows[:limit]
        if not group_by:
            return {
                "object_type": api_name,
                "row_count": len(rows),
                "truncated": truncated,
                "aggregations": [
                    {
                        "function": a["function"],
                        "field": a["field"],
                        "value": (rows[0][f"agg_{i}"] if rows else None),
                    }
                    for i, a in enumerate(aggregations)
                ],
            }
        groups = []
        for r in rows:
            group = {name: r[f"group_{i}"] for i, (name, _) in enumerate(group_by)}
            groups.append(
                {
                    "group": group,
                    "aggregations": [
                        {
                            "function": a["function"],
                            "field": a["field"],
                            "value": r[f"agg_{i}"],
                        }
                        for i, a in enumerate(aggregations)
                    ],
                }
            )
        return {
            "object_type": api_name,
            "group_by": [g for g, _ in group_by],
            "row_count": len(groups),
            "groups": groups,
            "truncated": truncated,
        }

    def _order_sql(
        self,
        order_by: list,
        fields: dict,
        derived: dict,
        *,
        aggregate: bool,
        aggregations: list | None = None,
    ) -> str:
        if not order_by:
            return ""
        parts: list[str] = []
        for o in order_by:
            dir_sql = o["direction"]
            if aggregate and o.get("aggregate"):
                parts.append(f"{_agg_expr('sum', o['field'])} {dir_sql}")
            else:
                col = fields.get(o["field"])
                if col is None and o["field"] in derived:
                    parts.append(f"{derived[o['field']].format(t='t')} {dir_sql}")
                elif col is not None:
                    parts.append(f"{col} {dir_sql}")
        return (" ORDER BY " + ", ".join(parts)) if parts else ""

    # ---- Analytics（受限多跳白名单） ----

    def _execute_analytic(self, contract: dict) -> dict:
        name = contract.get("analytic")
        params_model = ANALYTIC_PARAMS.get(name)
        if params_model is None:
            raise UnknownAnalytic(
                f"未知 analytic: {name}（可选: {', '.join(sorted(ANALYTIC_PARAMS))}）"
            )
        raw_params = contract.get("params") or {}
        try:
            p = params_model.model_validate(raw_params)
        except ValidationError as exc:
            raise InvalidAnalytic(f"analytic 参数校验失败: {exc.errors()}") from exc
        sql, param_names = ANALYTIC_SQL[name]
        values: list[Any] = [
            getattr(p, f) for f in param_names if f not in ("limit", "signal_id")
        ]
        if "signal_id" in param_names and p.signal_id:
            sql = sql.replace("{signal_clause}", "AND w.signal_id = ?")
            values.append(p.signal_id)
        else:
            sql = sql.replace("{signal_clause}", "")
        values.append(MAX_ANALYTIC_ROWS)
        with self._source() as conn:
            rows = self._query(conn, sql, values)
        note = (
            "approve_node_name = 当前审批岗位，approve_node_seq = 节点序号（1 首审）"
            if name == "warning_approval_step"
            else "concentration_limit=集中度限额，warning_value=预警阈值，current_status=RED_ALERT/NORMAL"
        )
        return {"analytic": name, "rows": rows, "note": note}

    # ---- 基础设施 ----

    def _source(self) -> sqlite3.Connection:
        return self._store.source_conn()

    @staticmethod
    def _query(conn: sqlite3.Connection, sql: str, params: list) -> list[dict]:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


__all__ = [
    "InvalidAggregation",
    "InvalidAnalytic",
    "InvalidContract",
    "InvalidFilterOperator",
    "InvalidOrderBy",
    "ObjectNotQueryable",
    "ResultTooLarge",
    "RiskQuery",
    "RiskQueryError",
    "UnknownAnalytic",
    "UnknownFilterField",
    "UnknownObjectType",
]
