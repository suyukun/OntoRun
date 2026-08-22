"""契约执行器（设计 §3.2）：执行辅助 + ContractExecutor。

_execr_op/_build_where（参数化 WHERE，V4）/ _compute_agg（单聚合计算）；ContractExecutor：
v0.1 对象路径（DuckDB 动态派生：过滤/聚合/≤1 跳 link_traversal + 多码谓词强制 + V5 结果护栏）
与 v0.2 指标路径（命中 metrics.db 预聚合表，T3 版本守卫，Top-N）。与 v0.1 单文件实现行为一致。
v0.2 指标路径叠加 P4 数据权限下沉（设计 §2）：真实策略 permission_ctx 下查询强制走
metrics.db 对象级权限视图 perm_<object_type>（deny 对象无视图 → fail-closed 拒答），
allow-all 上下文（内部工具/对账）保持直查物化表（行为不变）。
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import duckdb

from src.des.config import DEFAULT_ENTERPRISES_DIR
from src.des.contract.errors import ContractError, PermissionDeniedError
from src.des.contract.permissions import PermissionContext
from src.des.contract.schema import (
    _METRIC_REAGG_SQL,
    RESULT_LIMIT_FLOOR,
    RESULT_LIMIT_SCALE_FACTOR,
    _find_link,
    _resolve_type,
    validate_contract,
)
from src.des.materialize import DesMaterialization, rows_as_dicts
from src.des.metrics import (
    METRIC_META_TABLE,
    METRICS_DB,
    DimensionField,
    MetricDef,
    MetricRegistry,
    date_dimension_grain,
    is_date_dimension,
    metric_table_name,
)
from src.des.permission_views import permission_view_name
from src.ontology.registry import Registry


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
        elif op == "gt":
            clauses.append(f"{field} > ?")
            params.append(value)
        elif op == "ge":
            clauses.append(f"{field} >= ?")
            params.append(value)
        elif op == "lt":
            clauses.append(f"{field} < ?")
            params.append(value)
        elif op == "le":
            clauses.append(f"{field} <= ?")
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
        permission_ctx：读侧权限上下文（设计 §3.3，P1.5 接线）；缺省 None = 默认 deny
        （fail-closed，red-team P1-1：无 ctx ≠ 无校验，读操作直接拒答）。内部工具需显式
        PermissionContext.allow_all() 才放行；execute/_execute_metric 前置 decide(read) 并做可见列过滤。
        """
        self._mz = materialization
        self._registry = registry
        self._metrics = metrics
        self._conn = materialization.duckdb
        self._legacy_re = materialization.legacy_re
        self._metrics_db = metrics_db or (
            DEFAULT_ENTERPRISES_DIR / materialization.enterprise_code / METRICS_DB
        )
        # red-team P1-1：缺省默认 deny（而非跳过校验）——读侧权限唯一入口 fail-closed
        self._permission_ctx = (
            permission_ctx if permission_ctx is not None else PermissionContext.deny_all()
        )

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
        # red-team P1-2：link_traversal 目标对象读权限 fail-closed（目标 decide(read) + 返回列可见集）
        lt = contract.get("link_traversal")
        if lt is not None:
            self._check_link_target_permission(_find_link(self._registry, obj, lt["link"]))
        where, params = _build_where(contract.get("filters") or {})
        sql = f"SELECT * FROM {obj.source_table} WHERE {where} ORDER BY {obj.pk_field}"
        try:
            rows = rows_as_dicts(self._conn, sql, params)
        except Exception as exc:  # 表不存在/类型错误即 fail-closed
            raise ContractError(f"契约执行失败（fail-closed 拒答）: {exc}") from exc
        scale = self._object_scale(obj)
        limit = self._result_limit(scale)
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
        items = self._build_items(obj, rows, lt, visible)
        result = {"object_type": obj.name, "count": len(items), "items": items}
        if excluded:
            result["_diagnostics"] = {"predicate_excluded": excluded}
        return result

    def _object_scale(self, obj: Any) -> int:
        """对象路径查询规模 = 源表行数（V5 按规模派生，red-team P3-9；表名为注册表常量，无注入面）。"""
        n = self._conn.execute(f"SELECT COUNT(*) FROM {obj.source_table}").fetchone()[0]
        return int(n)

    def _result_limit(self, scale_row_count: int) -> int:
        """V5 结果护栏上限：按查询规模派生（red-team P3-9，不再锚定 MARA 一刀切 2400）。

        limit = max(下限, 规模系数 × 查询目标 row_count)。规模 = 查询目标数据集的自然行数
        （对象路径 = 源表 COUNT(*)，指标路径 = 物化表 row_count）：合法全表分析（A1 77,936 /
        L4 24,000 / F5 16,000）按规模放行，系数=1 时护栏退化为「不超源数据集规模的天然封顶」。
        上限始终从注册表/配置派生，禁硬编码 2400。
        """
        return max(RESULT_LIMIT_FLOOR, RESULT_LIMIT_SCALE_FACTOR * scale_row_count)

    # ------------------------------------------------------------------
    # 读侧权限（设计 §3.3：P1.5 decide(read) 接线；fail-closed 不静默裁剪）
    # ------------------------------------------------------------------
    def _permission_visible(self, object_type: str) -> list[str] | None:
        """前置 decide(subject, object_type, 'read')：allowed=False → fail-closed 拒答。

        返回 visible_attributes（读侧可见属性列表，属性级 deny 已剔除）；ctx 缺省 = 默认 deny
        （red-team P1-1：无 ctx 不豁免校验）。allowed 但可见集缺失（decide 异常态）保守全字段可见。
        """
        ctx = self._permission_ctx
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

    def _check_link_target_permission(self, link: Any) -> None:
        """link_traversal 目标对象读权限（red-team P1-2）：目标 decide(read) fail-closed。

        链接返回列（fk_field/code_space/value）必须落在目标可见集内；任一不可见即拒答
        （不静默裁剪，防 link_traversal 系统性旁路被 deny 的敏感对象）。
        """
        target = self._registry.object_type(link.target_type)
        visible = self._permission_visible(target.name)
        need = [link.fk_field, "code_space", "value"]
        invisible = sorted(c for c in set(need) if c not in visible)
        if invisible:
            raise PermissionDeniedError(
                f"读侧权限拒绝（link 目标 {target.name}）: 返回列不可见 {invisible}"
                "（属性级 deny，fail-closed）"
            )

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
            # red-team P1-2：link 返回列显式白名单（已过目标可见集校验，禁 SELECT * 直读）
            cols = f"{link.fk_field}, code_space, value"
            for c in rows_as_dicts(self._conn, f"SELECT {cols} FROM {target.source_table}", []):
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
        """执行 v0.2 指标契约：M 系列校验 → T3 版本守卫 → 查 metrics.db 物化表（权限视图）。

        返回 {object_type, metric_id, count, rows}；结果护栏按指标物化表规模派生（V5，P3-9）。
        P4 数据权限下沉（设计 §2）：真实策略 ctx 下 _query_metric 强制走权限视图
        perm_<object_type>（视图缺失/为空 = 对象级 deny，PermissionDeniedError fail-closed）；
        allow-all ctx（内部工具/对账）直查物化表（行为不变）。
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
            top_n = contract["metric"].get("topN")  # Top-N 执行（v0.2，已校验 ≤1000）
            rows = self._query_metric(conn, md, gb, where, params, top_n)
            scale = self._metric_scale(conn, md)  # V5 规模派生（conn 关闭前取 meta.row_count）
        finally:
            conn.close()
        limit = self._result_limit(scale)
        if len(rows) > limit:
            raise ContractError(f"结果行数 {len(rows)} 超过护栏上限 {limit}（V5，请加过滤）")
        rows = self._filter_metric_rows(rows, visible, md)
        return {
            "object_type": md.object_type,
            "metric_id": md.metric_id,
            "count": len(rows),
            "rows": rows,
        }

    def _metric_scale(self, conn: Any, md: MetricDef) -> int:
        """指标查询规模 = 物化表行数（metric_meta.row_count，V5 按规模派生，red-team P3-9）。

        meta 缺该指标行时保守回落下限（fail-closed 语义：不因元数据缺失而放大护栏）。
        """
        row = conn.execute(
            f"SELECT row_count FROM {METRIC_META_TABLE} WHERE metric_id=?", (md.metric_id,)
        ).fetchone()
        if row is None or row[0] is None:
            return RESULT_LIMIT_FLOOR
        return int(row[0])

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

    def _permission_is_allow_all(self) -> bool:
        """是否为 allow-all 直查上下文（内部工具/对账）：静态 allow_all 判定（read 全属性可见）。

        判别语义：真实策略注册表对 read 的判定 allowed 时 visible_attributes 恒为列表
        （R3 属性集裁剪结果）；visible_attributes=None 仅静态 allow_all 产生 → 判为
        无属性级约束 → 直查物化表（视图路径仅真实策略 ctx 启用，不施加内部工具）。
        """
        decision = self._permission_ctx.permission_registry.decide(
            self._permission_ctx.subject, "__probe__", "read"
        )
        return decision.allowed and decision.visible_attributes is None

    def _metric_source(self, conn: Any, md: MetricDef) -> tuple[str, bool]:
        """指标查询数据源：(名称, 是否权限视图)。

        allow-all 上下文 → 直查物化表（行为不变）；真实策略上下文 → 强制走权限视图，
        视图缺失/为空 = 对象级 deny 语义（PermissionDeniedError fail-closed，绝不回落
        直查物化表，防视图旁路）。
        """
        if self._permission_is_allow_all():
            return metric_table_name(md.metric_id), False
        view = permission_view_name(md.object_type)
        exists = conn.execute(
            "SELECT 1 FROM information_schema.views "
            "WHERE table_schema='main' AND table_name=?",
            (view,),
        ).fetchone()
        if exists is None:
            raise PermissionDeniedError(
                f"读侧权限拒绝（视图缺失，fail-closed）: {view}"
                "（对象级 deny 或未重建，防视图旁路直查）"
            )
        if conn.execute(f"SELECT 1 FROM {view} LIMIT 1").fetchone() is None:
            raise PermissionDeniedError(
                f"读侧权限拒绝（视图为空，fail-closed）: {view}"
                "（对象级 deny 或未物化，防视图旁路直查）"
            )
        return view, True

    def _query_metric(
        self,
        conn: Any,
        md: MetricDef,
        gb: list[str],
        where: str,
        params: list[Any],
        top_n: int | None = None,
    ) -> list[dict[str, Any]]:
        """查指标数据（参数化，V4）：无 group_by → 维度全列 + 度量列；有 group_by → 子集重聚合
        （仅可加聚合 sum/count/min/max，校验已挡 avg/count_distinct）。

        数据源 = 权限视图（真实策略 ctx，P4 设计 §2，行按 metric_id 判别列过滤防串表）
        或物化表 metric_<id>（allow-all 直查）。top_n（v0.2 表达力 Top-N，报告 §6 J4）：
        按度量值降序截断前 N 行（参数化 LIMIT，N 已校验 ≤1000），有/无 group_by 均生效；
        缺省 None = 不截断。表名/视图名/列名全为注册表派生常量（无用户输入，无注入面），
        值一律 ? 绑定。
        """
        source, is_view = self._metric_source(conn, md)
        if is_view:
            # 视图行含 metric_id 判别列（同对象多指标 UNION ALL，防列名碰撞串表）；
            # metric_id 为注册表 M7 常量（snake_case，无注入面），返回列显式选择不含它
            where = f"{where} AND metric_id = '{md.metric_id}'"
        measure_col = md.measure.name
        if gb:
            select = ", ".join(
                gb + [f"{_METRIC_REAGG_SQL[md.agg_function]}({measure_col}) AS {measure_col}"]
            )
            order = ", ".join(gb)
            sql = f"SELECT {select} FROM {source} WHERE {where} GROUP BY {order}"
        else:
            cols = ", ".join([d.name for d in md.dimension_fields] + [measure_col])
            order = ", ".join(d.name for d in md.dimension_fields)
            sql = f"SELECT {cols} FROM {source} WHERE {where}"
        if top_n is not None:
            # Top-N：按度量值降序取前 N（J4 退款 Top5 等）；LIMIT 参数化（V4），N 已校验 ≤1000
            sql += f" ORDER BY {measure_col} DESC, {order} LIMIT ?"
            params = [*params, top_n]
        else:
            sql += f" ORDER BY {order}"
        try:
            return rows_as_dicts(conn, sql, params)
        except Exception as exc:  # 表缺失/类型错误即 fail-closed
            raise ContractError(f"指标执行失败（fail-closed 拒答）: {exc}") from exc

