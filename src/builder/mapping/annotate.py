"""映射置信度打标骨架（P1.5 治理骨架 ③，设计 §3）。

对 builder 映射输出自动打标：score → 置信度档位（classify）→ 初始状态（routing：
高置信度自动过 / 中低进审核队列）；审核状态机 + 审核痕迹（append-only）。
适配器把 fk_detection / alias_matcher / naming / DES 语义输出适配为 MappingCandidate
（score 公式见设计 3.5），打标入口 annotate_mapping_candidates()（classify → routing → 落表）。

approved 候选如何写入 mappings/注册表 = P3 接线点（设计 3.5 注），P1.5 只落标注状态。
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from src.builder.mapping.alias_matcher import AliasMatchResult
from src.builder.mapping.fk_detection import DetectedLink
from src.builder.mapping.naming import to_pascal_case
from src.builder.status_machine import IllegalTransitionError
from src.ontology.registry import Registry
from src.runtime.store import (
    CONFIDENCE_LEVELS,
    MAPPING_KINDS,
    REVIEW_STATUSES,
    Store,
)

ConfidenceLevel = Literal["high", "medium", "low"]
ReviewStatus = Literal["draft", "reviewing", "approved", "rejected"]
MappingKind = Literal["object", "attribute", "link"]

# 枚举集合（单一来源 = store 顶部常量，与 mapping_candidates 表 CHECK 同源）
_CONFIDENCE_SET = frozenset(CONFIDENCE_LEVELS)
_STATUS_SET = frozenset(REVIEW_STATUSES)
_KIND_SET = frozenset(MAPPING_KINDS)

# 状态常量
DRAFT = "draft"
REVIEWING = "reviewing"
APPROVED = "approved"
REJECTED = "rejected"

# 阈值常量（设计 3.2，C2：临时默认，P3 用 ground truth 校准，不把阈值写死为神圣数字）
HIGH_THRESHOLD = 0.9
MEDIUM_THRESHOLD = 0.6
# 适配器固定分数（设计 3.5）
NAMING_SCORE = 0.9
DES_SCORE = 1.0
AUTO_REVIEWER = "auto"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ----------------------------------------------------------------------
# 候选模型（设计 3.1）
# ----------------------------------------------------------------------
class MappingCandidate(BaseModel):
    """一条「源表字段 → 本体目标」的映射建议，携带置信度与审核状态。"""

    candidate_id: str
    kind: MappingKind
    source_table: str
    source_field: str | None = None  # object 级候选可为空
    target: str  # 目标对象类型名 / 属性名 / 链接名（注册表校验 C4）
    confidence_score: float = Field(ge=0, le=1)  # 0-1，来自适配器
    confidence_level: ConfidenceLevel  # classify(score) 派生（纯函数）
    review_status: ReviewStatus = "draft"
    auto_approved: bool = False
    evidence_json: dict = Field(default_factory=dict)  # 证据：method + 原始分量
    created_at: str = ""
    updated_at: str = ""


# ----------------------------------------------------------------------
# classify / routing（设计 3.2，纯函数）
# ----------------------------------------------------------------------
def classify(
    score: float, high: float = HIGH_THRESHOLD, medium: float = MEDIUM_THRESHOLD
) -> ConfidenceLevel:
    """纯函数：score ≥ high → high；≥ medium → medium；否则 low。"""
    if score >= high:
        return "high"
    if score >= medium:
        return "medium"
    return "low"


def routing(candidate: MappingCandidate) -> MappingCandidate:
    """routing：high → auto_approved + approved（历史由服务层写 reviewer='auto'）；中/低 → draft 进审核队列。"""
    if candidate.confidence_level == "high":
        return candidate.model_copy(
            update={"auto_approved": True, "review_status": APPROVED}
        )
    return candidate.model_copy(update={"review_status": DRAFT})


# ----------------------------------------------------------------------
# 审核状态机（设计 3.3，复用 status_machine 的 assert_transition 模式）
# ----------------------------------------------------------------------
# 合法流转表：draft→reviewing/approved；reviewing→approved/rejected；rejected→draft；approved 终态
_REVIEW_TRANSITIONS: dict[str, frozenset[str]] = {
    DRAFT: frozenset({REVIEWING, APPROVED}),
    REVIEWING: frozenset({APPROVED, REJECTED}),
    REJECTED: frozenset({DRAFT}),
    APPROVED: frozenset(),  # 终态：不可回退不可改，入注册表的依据
}


def allowed_next(status: str) -> frozenset[str]:
    """查询 status 的合法下一态集合（公开给审核工作台）。"""
    return _REVIEW_TRANSITIONS.get(status, frozenset())


def is_terminal(status: str) -> bool:
    """是否终态（approved：不可流转）。"""
    return status == APPROVED


def assert_review_transition(current: str, target: str) -> None:
    """断言从 current 流转到 target 合法；非法抛 IllegalTransitionError（复用现有异常语义）。"""
    allowed = _REVIEW_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise IllegalTransitionError(current, target)


class TargetNotRegisteredError(ValueError):
    """C4：候选 target 未在注册表（对象/属性）；link 不入此校验（P3 入注册表时校验）。"""


# ----------------------------------------------------------------------
# 行 <-> 模型转换（mapping_candidates / mapping_review_history 表）
# ----------------------------------------------------------------------
_CAND_COLUMNS = (
    "candidate_id, kind, source_table, source_field, target, confidence_score, "
    "confidence_level, review_status, auto_approved, evidence_json, created_at, updated_at"
)


def _candidate_to_row(c: MappingCandidate) -> tuple:
    return (
        c.candidate_id,
        c.kind,
        c.source_table,
        c.source_field,
        c.target,
        c.confidence_score,
        c.confidence_level,
        c.review_status,
        1 if c.auto_approved else 0,
        json.dumps(c.evidence_json, ensure_ascii=False),
        c.created_at,
        c.updated_at,
    )


def _row_to_candidate(row) -> MappingCandidate:
    return MappingCandidate(
        candidate_id=row["candidate_id"],
        kind=row["kind"],
        source_table=row["source_table"],
        source_field=row["source_field"],
        target=row["target"],
        confidence_score=row["confidence_score"],
        confidence_level=row["confidence_level"],
        review_status=row["review_status"],
        auto_approved=bool(row["auto_approved"]),
        evidence_json=json.loads(row["evidence_json"] or "{}"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ----------------------------------------------------------------------
# MappingCandidateService（create/classify/routing/transition/落表 + history append-only）
# ----------------------------------------------------------------------
class MappingCandidateService:
    """映射候选服务：create（classify→routing→落表 + auto 历史）/ transition（状态机 + 历史）/ get/list。"""

    def __init__(self, store: Store, registry: Registry) -> None:
        self._store = store
        self._registry = registry

    # ---- C4 目标注册表校验（机验 ⑤） ----
    def check_c4(self, kind: str, target: str) -> list[str]:
        """C4 校验（公开，P1-3 ③ review 的 corrected_target 复用同一实现）：
        object → 已注册对象类型；attribute → 某已注册对象的字段；link → 不校验。"""
        if kind == "object":
            if not self._registry.has_object_type(target):
                return [f"C4 未知对象 target: {target}"]
        elif kind == "attribute" and not any(
            target in o.model.model_fields for o in self._registry.object_types()
        ):
            return [f"C4 未知属性 target: {target}"]
        return []

    def _validate_target(self, candidate: MappingCandidate) -> list[str]:
        return self.check_c4(candidate.kind, candidate.target)

    def create(
        self, candidate: MappingCandidate, *, thresholds: tuple[float, float] | None = None
    ) -> MappingCandidate:
        """落表：派生档位（自洽）→ C4 校验 → routing → 落 mapping_candidates + auto 历史。

        thresholds=(high, medium)：P3 校准阈值覆盖（§1.3 阈值读取顺序，缺省 None 用默认）。
        """
        if candidate.kind not in _KIND_SET:
            raise ValueError(f"非法映射类型: {candidate.kind}")
        now = _now()
        # 档位与分数自洽：一律由 classify(score) 派生，防 caller 传入不一致档位
        high, medium = thresholds if thresholds else (HIGH_THRESHOLD, MEDIUM_THRESHOLD)
        candidate = candidate.model_copy(
            update={"confidence_level": classify(candidate.confidence_score, high, medium)}
        )
        errors = self._validate_target(candidate)
        if errors:
            raise TargetNotRegisteredError("；".join(errors))
        routed = routing(candidate).model_copy(
            update={"created_at": now, "updated_at": now}
        )
        conn = self._store.ontology_conn()
        try:
            conn.execute(
                f"INSERT INTO mapping_candidates ({_CAND_COLUMNS}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                _candidate_to_row(routed),
            )
            if routed.auto_approved:
                # 高置信度自动过：写 reviewer='auto' 的审核历史（机验：auto_approved ⟺ 历史含 auto）
                self._insert_history(
                    conn, routed.candidate_id, DRAFT, APPROVED, AUTO_REVIEWER, now,
                    note="高置信度自动通过",
                )
            conn.commit()
        finally:
            conn.close()
        return routed

    def create_pending_registration(
        self,
        candidate: MappingCandidate,
        *,
        thresholds: tuple[float, float] | None = None,
    ) -> MappingCandidate:
        """C4 待补录：未注册 object 候选落 draft 待补录队列（red-team P2-4）。

        与 create 的关系：create 对 C4 失败 fail-fast 抛 TargetNotRegisteredError；本方法是
        治理策略——annotate/pipeline 对「object 目标未注册」不静默丢弃，落 draft 队列
        （evidence 标 c4=pending_registration），等对象经 P1a 注册后人工审核/自动过。
        attribute 目标未注册仍走 create 的抛错（跳过 + skipped_c4 计数，不进队）。
        """
        if candidate.kind != "object":
            raise ValueError(f"待补录仅适用于 object 候选: kind={candidate.kind!r}")
        high, medium = thresholds if thresholds else (HIGH_THRESHOLD, MEDIUM_THRESHOLD)
        now = _now()
        draft = candidate.model_copy(
            update={
                "confidence_level": classify(candidate.confidence_score, high, medium),
                "review_status": DRAFT,
                "auto_approved": False,
                "evidence_json": {
                    **candidate.evidence_json,
                    "c4": "pending_registration",
                    "c4_reason": f"目标对象未注册（待补录）: {candidate.target}",
                },
                "created_at": now,
                "updated_at": now,
            }
        )
        conn = self._store.ontology_conn()
        try:
            conn.execute(
                f"INSERT INTO mapping_candidates ({_CAND_COLUMNS}) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                _candidate_to_row(draft),
            )
            conn.commit()
        finally:
            conn.close()
        return draft

    def transition(
        self, candidate_id: str, target: str, reviewer: str, note: str = ""
    ) -> MappingCandidate:
        """人工审核流转：状态机断言 + 更新状态 + 落 history（每次流转必有一条，append-only）。"""
        current = self.get(candidate_id)
        if current is None:
            raise KeyError(f"候选不存在: {candidate_id}")
        conn = self._store.ontology_conn()
        try:
            self.transition_on(
                conn, candidate_id, target, reviewer, note, from_status=current.review_status
            )
            conn.commit()
        finally:
            conn.close()
        updated = self.get(candidate_id)
        assert updated is not None
        return updated

    def transition_on(
        self,
        conn,
        candidate_id: str,
        target: str,
        reviewer: str,
        note: str = "",
        *,
        from_status: str | None = None,
    ) -> None:
        """流转核心（接受外部连接，P2-6 单连接单事务复用；commit 由调用方负责）。

        from_status：显式传值则跳过重读——事务内上一跳未提交时，重读新连接看不到
        中间态（如 reject 的 draft→reviewing→rejected 两跳），会误判非法流转。
        """
        if from_status is None:
            current = self.get(candidate_id)
            if current is None:
                raise KeyError(f"候选不存在: {candidate_id}")
            from_status = current.review_status
        assert_review_transition(from_status, target)
        now = _now()
        conn.execute(
            "UPDATE mapping_candidates SET review_status=?, updated_at=? WHERE candidate_id=?",
            (target, now, candidate_id),
        )
        self._insert_history(
            conn, candidate_id, from_status, target, reviewer, now, note
        )

    def update_target(self, candidate_id: str, target: str) -> None:
        """改 target（服务层方法，供 review 的 corrected_target 原子复用）。"""
        conn = self._store.ontology_conn()
        try:
            self.update_target_on(conn, candidate_id, target)
            conn.commit()
        finally:
            conn.close()

    def update_target_on(self, conn, candidate_id: str, target: str) -> None:
        """改 target 核心（接受外部连接，P2-6 单连接单事务复用；commit 由调用方负责）。"""
        conn.execute(
            "UPDATE mapping_candidates SET target=?, updated_at=? WHERE candidate_id=?",
            (target, _now(), candidate_id),
        )

    def _insert_history(
        self,
        conn,
        candidate_id: str,
        from_status: str,
        to_status: str,
        reviewer: str,
        reviewed_at: str,
        note: str,
    ) -> None:
        conn.execute(
            "INSERT INTO mapping_review_history (history_id, candidate_id, from_status, "
            "to_status, reviewer, reviewed_at, note) VALUES (?,?,?,?,?,?,?)",
            (
                _new_id("hist"),
                candidate_id,
                from_status,
                to_status,
                reviewer,
                reviewed_at,
                note,
            ),
        )

    # ---- 查询 ----
    def get(self, candidate_id: str) -> MappingCandidate | None:
        conn = self._store.ontology_conn()
        try:
            row = conn.execute(
                "SELECT * FROM mapping_candidates WHERE candidate_id=?",
                (candidate_id,),
            ).fetchone()
            return _row_to_candidate(row) if row else None
        finally:
            conn.close()

    def list(
        self,
        *,
        status: str | None = None,
        level: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MappingCandidate], int]:
        """候选列表：按 review_status / confidence_level 过滤 + 分页，队列按 score 降序。"""
        where: list[str] = []
        params: list = []
        if status:
            where.append("review_status=?")
            params.append(status)
        if level:
            where.append("confidence_level=?")
            params.append(level)
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        conn = self._store.ontology_conn()
        try:
            total = conn.execute(
                f"SELECT COUNT(*) AS c FROM mapping_candidates {where_sql}", params
            ).fetchone()["c"]
            rows = conn.execute(
                f"SELECT * FROM mapping_candidates {where_sql} "
                "ORDER BY confidence_score DESC LIMIT ? OFFSET ?",
                params + [page_size, max(0, (page - 1) * page_size)],
            ).fetchall()
            return [_row_to_candidate(r) for r in rows], total
        finally:
            conn.close()

    def list_history(self, candidate_id: str) -> list[dict]:
        """某候选的审核痕迹（append-only 表，只读查询；机验：流转必有一条历史）。"""
        conn = self._store.ontology_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM mapping_review_history WHERE candidate_id=? "
                "ORDER BY reviewed_at ASC",
                (candidate_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


# ----------------------------------------------------------------------
# 适配器（设计 3.5：接 S1 builder 映射输出，score 公式精确到分量）
# ----------------------------------------------------------------------
def _fk_score(summary: dict) -> float:
    """fk_detection link 候选 score = (direct + format_normalized) / total（total=0 → 0.0）。"""
    total = summary.get("total_rows", 0)
    if not total:
        return 0.0
    return (
        summary.get("direct_match_rows", 0) + summary.get("format_normalized_match_rows", 0)
    ) / total


def adapt_fk_links(
    detected_links: list[DetectedLink], source_table: str
) -> list[MappingCandidate]:
    """fk_detection.detect_links → link 候选（每 DetectedLink 一条）。"""
    out: list[MappingCandidate] = []
    for link in detected_links:
        summary = dict(link.match_summary or {})
        score = _fk_score(summary)
        out.append(
            MappingCandidate(
                candidate_id=_new_id("cand"),
                kind="link",
                source_table=source_table,
                source_field=link.source_field,
                target=link.link_id,
                confidence_score=score,
                confidence_level=classify(score),
                evidence_json={
                    "method": "fk_detection.detect_links",
                    "detection_method": link.detection_method,
                    "direct": summary.get("direct_match_rows", 0),
                    "format_normalized": summary.get("format_normalized_match_rows", 0),
                    "unmatched": summary.get("unmatched_rows", 0),
                    "total": summary.get("total_rows", 0),
                },
            )
        )
    return out


def adapt_naming_attributes(
    columns: list[dict], source_table: str
) -> list[MappingCandidate]:
    """naming.derive_property_schema → attribute 候选（每非 is_technical 列一条，score 0.9）。"""
    out: list[MappingCandidate] = []
    for c in columns:
        col = c.get("column", "")
        if not col or c.get("is_technical"):
            continue
        out.append(
            MappingCandidate(
                candidate_id=_new_id("cand"),
                kind="attribute",
                source_table=source_table,
                source_field=col,
                target=to_pascal_case(col),
                confidence_score=NAMING_SCORE,
                confidence_level=classify(NAMING_SCORE),
                evidence_json={
                    "method": "naming.derive_property_schema",
                    "inferred_type": c.get("inferred_type", "string"),
                },
            )
        )
    return out


def adapt_alias_matches(
    alias_result: AliasMatchResult | None, source_table: str
) -> list[MappingCandidate]:
    """alias_matcher.match_aliases → link 候选（仅 matches；no_match 不进候选池——S1 已归待补录）。"""
    if alias_result is None:
        return []
    out: list[MappingCandidate] = []
    for m in alias_result.matches:
        evidence: dict = {
            "method": "alias_matcher.match_aliases",
            "match_type": m.match_type,
        }
        if m.disambiguation_note:
            evidence["disambiguation_note"] = m.disambiguation_note
        out.append(
            MappingCandidate(
                candidate_id=_new_id("cand"),
                kind="link",
                source_table=source_table,
                source_field=m.alias,
                target=m.matched_supplier_id or m.alias,
                confidence_score=m.confidence,
                confidence_level=classify(m.confidence),
                evidence_json=evidence,
            )
        )
    return out


def adapt_des_semantics(
    des_mappings: list[dict], source_table: str
) -> list[MappingCandidate]:
    """DES 语义（设计 3.5：DES 自带对象语义）→ object/attribute 候选，score 1.0（高置信度自动过）。

    des_mappings 形如 [{"kind": "object", "target": "Material"},
                       {"kind": "attribute", "target": "matnr", "source_field": "material_number"}, ...]，
    由 DES 管道声明已知语义映射。
    """
    out: list[MappingCandidate] = []
    for dm in des_mappings:
        out.append(
            MappingCandidate(
                candidate_id=_new_id("cand"),
                kind=dm["kind"],
                source_table=source_table,
                source_field=dm.get("source_field"),
                target=dm["target"],
                confidence_score=DES_SCORE,
                confidence_level=classify(DES_SCORE),
                evidence_json={"method": "DES_semantic"},
            )
        )
    return out


def _adapt_all(source: dict) -> list[MappingCandidate]:
    """四适配器产出候选（design §1.1 阶段 1 的候选来源，pipeline 与 annotate 共用）。"""
    source_table = source["source_table"]
    adapted: list[MappingCandidate] = []
    adapted.extend(adapt_naming_attributes(source.get("columns") or [], source_table))
    adapted.extend(adapt_fk_links(source.get("detected_links") or [], source_table))
    adapted.extend(adapt_alias_matches(source.get("alias_result"), source_table))
    adapted.extend(adapt_des_semantics(source.get("des_mappings") or [], source_table))
    return adapted


def _persist_candidates(
    service: MappingCandidateService,
    adapted: list[MappingCandidate],
    *,
    thresholds: tuple[float, float] | None = None,
) -> tuple[list[MappingCandidate], list[str]]:
    """落表 + C4 未注册 target 显式处理（red-team P2-4：不再静默丢弃）：
    - object 目标未注册 → 进待补录队列（draft，evidence 标 c4=pending_registration）
      + skipped_c4 计数——等对象 P1a 注册后人工审核（Jack 拍板「注册后新对象可入」）；
    - attribute 目标未注册 → 跳过（不进队）+ skipped_c4 计数；
    - link 不入 C4 校验（create 正常落表）。
    thresholds 透传 create / create_pending_registration（校准阈值覆盖，缺省 None 用默认）。
    """
    persisted: list[MappingCandidate] = []
    skipped_c4: list[str] = []
    for cand in adapted:
        try:
            persisted.append(service.create(cand, thresholds=thresholds))
        except TargetNotRegisteredError:
            if cand.kind == "object":
                persisted.append(
                    service.create_pending_registration(cand, thresholds=thresholds)
                )
            skipped_c4.append(cand.target)
    return persisted, skipped_c4


def annotate_mapping_candidates(
    source: dict,
    registry: Registry,
    *,
    store: Store | None = None,
) -> list[MappingCandidate]:
    """打标入口（设计 3.5）：适配器产出候选 → classify → routing → 落表。

    source 字段：
      source_table（必填）——本源表名；
      columns（naming 输入：[{column, inferred_type, is_technical, ...}]）；
      detected_links（fk_detection.detect_links 输出）；
      alias_result（alias_matcher.match_aliases 输出，可 None）；
      des_mappings（DES 语义已知映射：[{kind, target, source_field?}]）。
    返回成功落表的候选：已注册 target 正常过（高置信自动过）；object target 未注册
    进待补录队列（draft，不静默丢弃）；attribute target 未注册跳过。skipped_c4 明细由
    run_mapping_pipeline（PipelineReport.skipped_c4）显式收集。
    """
    service = MappingCandidateService(store or Store(), registry)
    persisted, _skipped = _persist_candidates(service, _adapt_all(source))
    return persisted


__all__ = [
    "APPROVED",
    "AUTO_REVIEWER",
    "DES_SCORE",
    "DRAFT",
    "HIGH_THRESHOLD",
    "MEDIUM_THRESHOLD",
    "NAMING_SCORE",
    "REJECTED",
    "REVIEWING",
    "ConfidenceLevel",
    "MappingCandidate",
    "MappingCandidateService",
    "MappingKind",
    "ReviewStatus",
    "TargetNotRegisteredError",
    "_adapt_all",
    "_persist_candidates",
    "adapt_alias_matches",
    "adapt_des_semantics",
    "adapt_fk_links",
    "adapt_naming_attributes",
    "allowed_next",
    "annotate_mapping_candidates",
    "assert_review_transition",
    "classify",
    "is_terminal",
    "routing",
]
