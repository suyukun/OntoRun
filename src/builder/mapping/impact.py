"""P3 映射变更影响分析（设计 §4.3，C2「必有映射变更影响分析」）。

analyze_change(candidate) -> MappingChangeReport：对一次 approved 映射变更（新增/修正
target），反向扫描受影响面：
- objects/links：Registry 现注册集中是否存在同名/同端点（新增 vs 覆盖，覆盖被拒只能新增）；
- metrics：metrics 注册表（src/des/metrics.py）中 object_type 引用该对象、或 dimension/
  measure 的 source 引用该候选源表列 → 物化 SQL 受影响（需 P2 refresh 管道重物化）；
- contracts：受影响契约形态（v0.1 object / v0.2 metric）；
- audit_chain_ok：审计哈希链 verify_integrity 全绿（变更前可追溯）。

变更流程纪律（设计 §4.3）：approved 终态不可改 → 变更 = 新建候选重新走完整管道，
旧映射不删除；本报告在变更前生成并归档（写入变更审计 detail_json）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.runtime.audit import AuditLog
from src.runtime.store import Store

if TYPE_CHECKING:  # 仅类型提示（避免 ontology/des 强耦合）
    from src.ontology.registry import Registry

RISK_HIGH = "high"
RISK_MEDIUM = "medium"
RISK_LOW = "low"


def _risk_level(affected: dict) -> str:
    """风险分级：读侧指标受影响 → high（需重物化）；对象/链接受影响 → medium；否则 low。"""
    if affected["metrics"]:
        return RISK_HIGH
    if affected["objects"] or affected["links"]:
        return RISK_MEDIUM
    return RISK_LOW


def _affected_metrics(metrics, candidate) -> list[str]:
    """受影响 metric_id：object_type 引用该目标对象，或维度/度量 source 引用候选源表列。

    metric 的 source 形如 'VBAP.MATNR'（表名省略系统前缀，设计 §1.2），与候选
    source_table 'erp.VBAP' 比较时取末段表名对齐。
    """
    src_table_short = candidate.source_table.rsplit(".", 1)[-1] if candidate.source_table else ""
    out: list[str] = []
    for m in metrics.metrics:
        refs_source = (
            any((d.source or "").split(".", 1)[0] == src_table_short for d in m.dimension_fields)
            or (m.measure.source or "").split(".", 1)[0] == src_table_short
        )
        if m.object_type == candidate.target or (src_table_short and refs_source):
            out.append(m.metric_id)
    return out


def _affected_contracts(affected: dict) -> list[str]:
    """受影响契约形态（v0.1 object 扩展 / v0.2 metric，按受影响面派生，禁枚举具体契约文档）。"""
    forms: list[str] = []
    if affected["metrics"]:
        forms.append("v0.2 metric")
    if affected["objects"]:
        forms.append("v0.1 object")
    return forms


def analyze_change(
    candidate,
    *,
    store: Store,
    registry: Registry,
    metrics,
) -> dict[str, Any]:
    """变更影响分析：反向扫描受影响对象/链接/指标/契约 + 审计链自洽（设计 §4.3）。

    返回 MappingChangeReport：
      {change, affected: {objects, links, metrics, contracts, audit_chain_ok}, risk}
    """
    change = {
        "candidate_id": candidate.candidate_id,
        "kind": candidate.kind,
        "source_table": candidate.source_table,
        "source_field": candidate.source_field,
        "target_from": None,  # approved 终态不可改：变更 = 新增候选，无旧 target
        "target_to": candidate.target,
    }
    objects: list[str] = []
    links: list[str] = []
    if registry.has_object_type(candidate.target):
        objects.append(candidate.target)
    for l in registry.link_types():
        if (
            l.name == candidate.target
            or l.source_type == candidate.target
            or l.target_type == candidate.target
        ):
            links.append(l.name)
    metric_ids = _affected_metrics(metrics, candidate)
    affected = {
        "objects": sorted(set(objects)),
        "links": sorted(set(links)),
        "metrics": sorted(set(metric_ids)),
        "contracts": _affected_contracts(
            {"objects": objects, "metrics": metric_ids}
        ),
        "audit_chain_ok": AuditLog(store).verify_integrity()["ok"],
    }
    return {
        "change": change,
        "affected": affected,
        "risk": _risk_level(affected),
    }


__all__ = [
    "RISK_HIGH",
    "RISK_LOW",
    "RISK_MEDIUM",
    "analyze_change",
]
