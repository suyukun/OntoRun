"""P3 映射管道编排（设计 §1.1）：单表一个批次跑通 -> PipelineReport。

run_mapping_pipeline(source, *, store, registry, thresholds) -> PipelineReport：
- 阶段 1：四适配器产出候选（复用 annotate._adapt_all）；
- 阶段 2：classify 分级 + routing 路由（阈值可配，缺省 0.9/0.6；P1.5 纯函数）；
- 落 mapping_candidates 表 + C4 未注册 target 显式计数（red-team P2-4：不再静默丢弃）；
- PipelineReport = {source_table, total_candidates, auto_approved, in_queue,
  by_level: {high/medium/low: n}, skipped_c4: [target,...]}。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.builder.mapping.annotate import (
    DRAFT,
    MappingCandidateService,
    _adapt_all,
    _persist_candidates,
)
from src.runtime.store import Store

if TYPE_CHECKING:
    from src.ontology.registry import Registry


def run_mapping_pipeline(
    source: dict,
    *,
    store: Store,
    registry: Registry,
    thresholds: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """单表映射管道编排（设计 §1.1）：适配 → 分级/路由落表 → PipelineReport。

    source = SourceDescriptor（source_table + columns/detected_links/alias_result/des_mappings）；
    thresholds = (high, medium) 校准阈值；None 用缺省 0.9/0.6（P1.5 默认）。
    """
    service = MappingCandidateService(store, registry)
    persisted, skipped_c4 = _persist_candidates(
        service, _adapt_all(source), thresholds=thresholds
    )
    by_level = {"high": 0, "medium": 0, "low": 0}
    for c in persisted:
        by_level[c.confidence_level] += 1
    return {
        "source_table": source["source_table"],
        "total_candidates": len(persisted),
        "auto_approved": sum(1 for c in persisted if c.auto_approved),
        "in_queue": sum(1 for c in persisted if c.review_status == DRAFT),
        "by_level": by_level,
        "skipped_c4": sorted(set(skipped_c4)),
    }


__all__ = [
    "run_mapping_pipeline",
]
