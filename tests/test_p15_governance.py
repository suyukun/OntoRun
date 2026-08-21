"""P1.5 治理骨架门禁测试（docs/P1.5-治理骨架设计_v0.1.md §0.5/§1.3/§2.5/§3.6）。

覆盖三条门禁（机验口径）：
- ① 权限元数据可写：PermissionService CRUD + V1-V9 写时拒绝 + decide 语义
  （fail-closed / deny-wins / 属性级剔除 / approve 仅 human 兜底）；
- ② 审计骨架可查：哈希链（record_hash 按规格重算一致 + prev_hash 衔接 + genesis=""）、
  verify_integrity 全绿/旁路篡改检出、WORM 触发器禁改删、字段镜像一一对应、
  retention_class/source 枚举合法、审计独立于会话；
- ③ 映射打标可跑：classify 阈值边界、高置信度自动过、中低进队列、审核状态机合法/非法、
  target 未注册拒绝、审核痕迹 append-only、score∈[0,1]；
- GovernanceValidator：引用不存在对象的策略 / target 未注册的候选 → self_check error 级 Issue。

约束：全部使用 tmp_path 临时双库（source + ontology），不触碰真实 data/ontology/ontology.db。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from src.builder.mapping.annotate import (
    APPROVED,
    AUTO_REVIEWER,
    DRAFT,
    HIGH_THRESHOLD,
    MEDIUM_THRESHOLD,
    REJECTED,
    REVIEWING,
    MappingCandidate,
    MappingCandidateService,
    TargetNotRegisteredError,
    annotate_mapping_candidates,
    classify,
)
from src.builder.status_machine import IllegalTransitionError
from src.ontology import build_registry
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.governance_checks import (
    GOV_CAND_UNKNOWN_TARGET,
    GOV_POLICY_UNKNOWN_ATTRIBUTE,
    GOV_POLICY_UNKNOWN_OBJECT,
    governance_self_checks,
    mount_governance_checks,
)
from src.runtime.permissions import (
    PermissionPolicy,
    PermissionRole,
    PermissionService,
    PermissionSubject,
    decide,
)
from src.runtime.store import Store


# ----------------------------------------------------------------------
# 工具 / fixtures
# ----------------------------------------------------------------------
def _agent() -> PermissionSubject:
    return PermissionSubject(kind="agent", id="procurement_agent")


def _human() -> PermissionSubject:
    return PermissionSubject(kind="human", id="jack")


def _policy(**kw) -> PermissionPolicy:
    defaults = {
        "policy_id": "p1",
        "object_type": "Order",
        "operation": "read",
        "effect": "allow",
        "subject": _agent(),
    }
    return PermissionPolicy(**{**defaults, **kw})


def _audit_record(**kw) -> AuditRecord:
    defaults = {"action_name": "test_action", "outcome": "applied", "actor": "api"}
    return AuditRecord(**{**defaults, **kw})


def _candidate(candidate_id: str = "c1", target: str = "Order", score: float = 0.7, **kw) -> MappingCandidate:
    defaults = {
        "candidate_id": candidate_id,
        "kind": "object",
        "source_table": "retail_orders",
        "source_field": None,
        "target": target,
        "confidence_score": score,
        "confidence_level": classify(score),
    }
    return MappingCandidate(**{**defaults, **kw})


@dataclass
class _FieldEffect:
    """字段级镜像输入（与 FieldEffect 协议兼容：object_type/pk/prop/old/new）。"""

    object_type: str
    pk: str
    prop: str
    old: object
    new: object


@pytest.fixture
def store(tmp_path) -> Store:
    """每个测试独立临时双库（source + ontology），绝不碰真实 data/。"""
    s = Store(tmp_path / "source.db", tmp_path / "ontology.db")
    s.migrate()
    return s


@pytest.fixture
def registry() -> Registry:
    return build_registry()


@pytest.fixture
def perm(store, registry) -> PermissionService:
    return PermissionService(store, registry)


@pytest.fixture
def audit(store) -> AuditLog:
    return AuditLog(store)


@pytest.fixture
def mapping(store, registry) -> MappingCandidateService:
    return MappingCandidateService(store, registry)


# ======================================================================
# ① 权限元数据可写（门禁 1）
# ======================================================================
def test_policy_crud(perm) -> None:
    """策略 create/get/list/update/delete 全链路，update 为 replace 语义 + version 递增。"""
    created = perm.create(_policy())
    assert created.policy_id == "p1" and created.version == 1
    assert created.created_at and created.updated_at
    got = perm.get("p1")
    assert got is not None and got.object_type == "Order" and got.operation == "read"
    assert [p.policy_id for p in perm.list()] == ["p1"]
    updated = perm.update("p1", {"effect": "deny"})
    assert updated.effect == "deny" and updated.version == 2
    assert perm.delete("p1") is True
    assert perm.get("p1") is None and perm.list() == []


def test_policy_missing_ops(perm) -> None:
    """对不存在的策略 update/delete → KeyError，get → None。"""
    assert perm.get("nope") is None
    with pytest.raises(KeyError):
        perm.update("nope", {"effect": "deny"})
    with pytest.raises(KeyError):
        perm.delete("nope")


def test_policy_update_revalidates(perm) -> None:
    """update 变更再次走 V1-V9 复验，失败不落库。"""
    perm.create(_policy())
    with pytest.raises(ValueError) as exc:
        perm.update("p1", {"object_type": "GhostObj"})
    assert "V1" in str(exc.value)
    assert perm.get("p1").object_type == "Order"  # 复验失败，内存/表均未变


def test_v1_unknown_object(perm) -> None:
    with pytest.raises(ValueError) as exc:
        perm.create(_policy(policy_id="p-v1", object_type="NoSuchObject"))
    assert "V1" in str(exc.value) and "NoSuchObject" in str(exc.value)


def test_v2_unknown_attribute(perm) -> None:
    """属性级策略的 attribute 必须是该对象 model 字段。"""
    with pytest.raises(ValueError) as exc:
        perm.create(
            _policy(policy_id="p-v2", operation="read", scope="attribute", attributes=["bogus_col"])
        )
    assert "V2" in str(exc.value)


def test_v3_illegal_operation(perm) -> None:
    """operation 非 read/write/approve → 拒绝（Literal 无法直接构造，走 model_construct 直抵校验）。"""
    bad = PermissionPolicy.model_construct(
        policy_id="p-v3", object_type="Order", operation="execute", effect="allow",
        subject=_agent(), scope="object", attributes=[],
    )
    with pytest.raises(ValueError) as exc:
        perm.create(bad)
    assert "V3" in str(exc.value)


def test_v4_illegal_effect(perm) -> None:
    bad = PermissionPolicy.model_construct(
        policy_id="p-v4", object_type="Order", operation="read", effect="maybe",
        subject=_agent(), scope="object", attributes=[],
    )
    with pytest.raises(ValueError) as exc:
        perm.create(bad)
    assert "V4" in str(exc.value)


def test_v5_illegal_subject_kind(perm) -> None:
    bad_subject = PermissionSubject.model_construct(kind="robot", id="x")
    bad = PermissionPolicy.model_construct(
        policy_id="p-v5", object_type="Order", operation="read", effect="allow",
        subject=bad_subject, scope="object", attributes=[],
    )
    with pytest.raises(ValueError) as exc:
        perm.create(bad)
    assert "V5" in str(exc.value)


def test_v6_attribute_scope_read_only(perm) -> None:
    """attributes 非空 ⇒ operation 必须为 read（属性级只读，D4）。"""
    with pytest.raises(ValueError) as exc:
        perm.create(_policy(policy_id="p-v6", operation="write", attributes=["status"]))
    assert "V6" in str(exc.value)


def test_v7_unknown_role(perm) -> None:
    with pytest.raises(ValueError) as exc:
        perm.create(_policy(policy_id="p-v7", role_id="ghost_role", subject=None))
    assert "V7" in str(exc.value)


def test_v7_subject_and_role_mutually_exclusive(perm) -> None:
    """subject 与 role_id 二选一：双填拒绝。"""
    perm.create_role(PermissionRole(role_id="procurement", name="采购", members=[_agent()]))
    with pytest.raises(ValueError) as exc:
        perm.create(_policy(policy_id="p-v7b", role_id="procurement", subject=_agent()))
    assert "二选一" in str(exc.value)


def test_v8_duplicate_policy_id(perm) -> None:
    """policy_id 重复注册拒绝（防静默覆盖）。"""
    perm.create(_policy())
    with pytest.raises(ValueError) as exc:
        perm.create(_policy())
    assert "V8" in str(exc.value)


def test_v9_approve_human_only(perm) -> None:
    """审=人专属：operation=approve 的 subject.kind 强制 human。"""
    with pytest.raises(ValueError) as exc:
        perm.create(_policy(policy_id="p-v9", operation="approve", subject=_agent()))
    assert "V9" in str(exc.value)


def test_v9_approve_role_all_human(perm) -> None:
    """approve 引用的角色必须全 human 成员；全 human 角色可通过。"""
    perm.create_role(
        PermissionRole(role_id="reviewers", name="审核", members=[_agent(), _human()])
    )
    with pytest.raises(ValueError) as exc:
        perm.create(
            _policy(policy_id="p-v9r", operation="approve", role_id="reviewers", subject=None)
        )
    assert "V9" in str(exc.value)
    perm.create_role(PermissionRole(role_id="humans", name="人", members=[_human()]))
    ok = perm.create(
        _policy(policy_id="p-v9ok", operation="approve", role_id="humans", subject=None)
    )
    assert ok.operation == "approve"


def test_role_crud(perm) -> None:
    """角色（D7 便捷分组）CRUD + 重复/非法成员拒绝。"""
    r = perm.create_role(PermissionRole(role_id="procurement", name="采购", members=[_agent()]))
    assert r.role_id == "procurement"
    assert perm.get_role("procurement") is not None
    assert [x.role_id for x in perm.list_roles()] == ["procurement"]
    assert perm.delete_role("procurement") is True
    assert perm.get_role("procurement") is None
    perm.create_role(PermissionRole(role_id="r2", name="x"))
    with pytest.raises(ValueError):
        perm.create_role(PermissionRole(role_id="r2", name="x"))
    with pytest.raises(ValueError):
        perm.create_role(
            PermissionRole(
                role_id="r3", name="x",
                members=[PermissionSubject.model_construct(kind="robot", id="z")],
            )
        )


def test_decide_fail_closed(perm) -> None:
    """R1 fail-closed：无匹配策略 → denied，可见集为空。"""
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is False
    assert decision.visible_attributes is None
    assert decision.matched_policy_ids == []


def test_decide_allow(perm, registry) -> None:
    """对象级 read allow → allowed，可见属性 = 对象全字段。"""
    perm.create(_policy())
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is True
    assert decision.visible_attributes == list(registry.object_type("Order").model.model_fields)
    assert decision.matched_policy_ids == ["p1"]


def test_decide_deny_wins_read(perm) -> None:
    """R2 deny-wins：同 (对象, 操作, 主体) 上 deny 覆盖 allow。"""
    perm.create(_policy())
    perm.create(_policy(policy_id="p-deny", effect="deny"))
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is False
    assert "p-deny" in decision.matched_policy_ids


def test_decide_write_deny_wins(perm) -> None:
    perm.create(_policy(policy_id="p-w-allow", operation="write"))
    perm.create(_policy(policy_id="p-w-deny", operation="write", effect="deny"))
    decision = perm.perm_registry.decide(_agent(), "Order", "write")
    assert decision.allowed is False
    assert {"p-w-allow", "p-w-deny"} <= set(decision.matched_policy_ids)


def test_decide_object_deny_beats_attribute_allow(perm) -> None:
    """R3 对象级 deny 全局优先：属性级 allow 无法翻案。"""
    perm.create(_policy(policy_id="p-obj-deny", effect="deny"))  # 对象级 deny read
    perm.create(
        _policy(policy_id="p-attr-allow", scope="attribute", attributes=["total_cents"])
    )
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is False and decision.visible_attributes is None


def test_decide_attribute_pruning(perm) -> None:
    """R3 属性级剔除：可见集 = 全字段 - 属性级 deny；属性级读判定按可见集。"""
    perm.create(_policy())  # 对象级 read allow
    perm.create(
        _policy(policy_id="p-attr-deny", operation="read", effect="deny",
                scope="attribute", attributes=["status"])
    )
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is True
    assert "status" not in decision.visible_attributes
    assert "total_cents" in decision.visible_attributes
    # 属性级读判定
    assert perm.perm_registry.decide(_agent(), "Order", "read", attribute="status").allowed is False
    assert perm.perm_registry.decide(_agent(), "Order", "read", attribute="total_cents").allowed is True


def test_decide_role_expansion(perm) -> None:
    """D7 角色便捷分组：策略引用 role_id，decide 展开成员判定。"""
    perm.create_role(PermissionRole(role_id="procurement", name="采购", members=[_agent()]))
    perm.create(_policy(policy_id="p-role", role_id="procurement", subject=None))
    decision = perm.perm_registry.decide(_agent(), "Order", "read")
    assert decision.allowed is True and decision.matched_policy_ids == ["p-role"]


def test_decide_approve_human_only_fallback(perm, registry) -> None:
    """R4 approve 仅 human：正常路径 human 可审；绕过写时机验的 agent 直调仍被兜底拒绝。"""
    perm.create(_policy(policy_id="p-app-h", operation="approve", subject=_human()))
    assert perm.perm_registry.decide(_human(), "Order", "approve").allowed is True
    # 兜底：即使策略主体匹配 agent（模拟绕过 V9 的直达调用），approve 对 agent 也拒绝
    bypass = PermissionPolicy.model_construct(
        policy_id="p-app-agent", object_type="Order", operation="approve", effect="allow",
        subject=_agent(), scope="object", attributes=[],
    )
    decision = decide(_agent(), "Order", "approve", registry=registry, policies=[bypass], roles={})
    assert decision.allowed is False


# ======================================================================
# ② 审计骨架可查（门禁 2）
# ======================================================================
def _recompute_hash(prev_hash: str, row: dict) -> str:
    """按设计 2.3 规格独立重算 record_hash（不调用实现，防测试与实现同错）。"""
    content = {k: v for k, v in row.items() if k not in ("prev_hash", "record_hash")}
    payload = (
        (prev_hash or "")
        + "|"
        + json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_audit_hash_chain_correct(audit, store) -> None:
    """哈希链：genesis prev=""、record_hash 与按规格重算一致、prev_hash 逐条衔接。"""
    for _ in range(3):
        audit.append(_audit_record())
    conn = store.ontology_conn()
    try:
        rows = [
            dict(r)
            for r in conn.execute("SELECT * FROM audit_log ORDER BY audit_id ASC").fetchall()
        ]
    finally:
        conn.close()
    assert len(rows) == 3
    assert rows[0]["prev_hash"] == ""  # genesis
    assert rows[0]["record_hash"] == _recompute_hash("", rows[0])
    assert rows[1]["prev_hash"] == rows[0]["record_hash"]
    assert rows[1]["record_hash"] == _recompute_hash(rows[0]["record_hash"], rows[1])
    assert rows[2]["prev_hash"] == rows[1]["record_hash"]
    assert rows[2]["record_hash"] == _recompute_hash(rows[1]["record_hash"], rows[2])


def test_verify_integrity_ok(audit) -> None:
    """正常链 verify_integrity 全绿。"""
    for _ in range(3):
        audit.append(_audit_record())
    report = audit.verify_integrity()
    assert report["ok"] is True
    assert report["checked"] == 3
    assert report["broken"] == []
    assert report["first_broken_index"] is None


def test_verify_integrity_detects_bypass_tamper(tmp_path, store, audit) -> None:
    """L3 旁路篡改：拷库 + 删触发器 + 改数据 → verify_integrity 检出 broken。"""
    first_id = audit.append(_audit_record(action_name="first"))
    audit.append(_audit_record(action_name="second"))
    copy_path = tmp_path / "ontology_tampered.db"
    shutil.copy(store.ontology_path, copy_path)
    conn = sqlite3.connect(copy_path)
    try:
        conn.execute("DROP TRIGGER IF EXISTS trg_audit_log_wo_upd")
        # 篡改无 CHECK 约束的 action_name（避开 actor 白名单 CHECK，确保是触发器被删才放行）
        conn.execute("UPDATE audit_log SET action_name='tampered' WHERE audit_id=?", (first_id,))
        conn.commit()
    finally:
        conn.close()
    tampered_store = Store(tmp_path / "s.db", copy_path)
    report = AuditLog(tampered_store).verify_integrity()
    assert report["ok"] is False
    assert first_id in report["broken"]
    assert report["first_broken_index"] == 0


def test_audit_log_worm_update_delete(audit, store) -> None:
    """L2 WORM：绕过 API 直连库 UPDATE/DELETE audit_log → IntegrityError。"""
    audit.append(_audit_record())
    conn = store.ontology_conn()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_log SET actor='hack'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_log")
    finally:
        conn.close()


def test_field_mirror_consistency(audit, store) -> None:
    """字段级镜像：effects 行数 = 镜像行数，且一一对应（audit_id/对象/主键/属性/新旧值）。"""
    effects = [
        _FieldEffect("Order", "ORD-1", "status", "pending", "confirmed"),
        _FieldEffect("Order", "ORD-1", "total_cents", 100, 200),
        _FieldEffect("Order", "ORD-2", "note", None, "hello"),
    ]
    audit_id = audit.append(_audit_record(action_name="update_order"), effects=effects)
    conn = store.ontology_conn()
    try:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM audit_field_mirror WHERE audit_id=?", (audit_id,)
            ).fetchall()
        ]
    finally:
        conn.close()
    assert len(rows) == len(effects)

    def _sv(v: object) -> str | None:
        """镜像值形态：None 原样，其余转 str（与 append 落库口径一致）。"""
        return None if v is None else str(v)

    actual = {
        (r["object_type"], r["pk"], r["prop"], r["old_value"], r["new_value"]) for r in rows
    }
    expected = {(e.object_type, e.pk, e.prop, _sv(e.old), _sv(e.new)) for e in effects}
    assert actual == expected


def test_field_mirror_worm(audit, store) -> None:
    """字段级镜像表同样受 WORM 触发器保护。"""
    audit.append(
        _audit_record(action_name="update_order"),
        effects=[_FieldEffect("Order", "ORD-1", "status", "a", "b")],
    )
    conn = store.ontology_conn()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_field_mirror SET new_value='x'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_field_mirror")
    finally:
        conn.close()


def test_retention_class_source_enum(audit) -> None:
    """机验 ⑤：retention_class/source 枚举合法（单一来源 = store 常量）。"""
    with pytest.raises(ValueError):
        audit.append(_audit_record(retention_class="bogus"))
    with pytest.raises(ValueError):
        audit.append(_audit_record(source="bogus"))
    audit_id = audit.append(_audit_record(retention_class="standard", source="review"))
    got = audit.get(audit_id)
    assert got is not None
    assert got["retention_class"] == "standard" and got["source"] == "review"


def test_audit_independent_of_session(store) -> None:
    """机验 ⑥：AuditLog 初始化仅依赖 Store，不依赖任何会话状态。"""
    audit = AuditLog(store)  # 无需任何 session/上下文
    audit_id = audit.append(_audit_record())
    assert audit.get(audit_id)["audit_id"] == audit_id
    # L1 接口面：只追加，无 update/delete 公开方法
    assert not hasattr(AuditLog, "update")
    assert not hasattr(AuditLog, "delete")


# ======================================================================
# ③ 映射打标可跑（门禁 3）
# ======================================================================
def test_classify_threshold_boundaries() -> None:
    """classify：阈值边界（>=high → high；>=medium → medium；否则 low）。"""
    assert classify(HIGH_THRESHOLD) == "high"
    assert classify(MEDIUM_THRESHOLD) == "medium"
    assert classify(HIGH_THRESHOLD - 0.001) == "medium"
    assert classify(MEDIUM_THRESHOLD - 0.001) == "low"


def test_classify_buckets() -> None:
    """classify：0.95→high / 0.7→medium / 0.3→low（任务点名样例）。"""
    assert classify(0.95) == "high"
    assert classify(0.7) == "medium"
    assert classify(0.3) == "low"
    assert classify(0.0) == "low"


def test_high_confidence_auto_approved(mapping) -> None:
    """高置信度自动过：auto_approved=True + status=approved + 历史含 reviewer=auto 记录。"""
    cand = mapping.create(_candidate(candidate_id="c-auto", score=0.95))
    assert cand.confidence_level == "high"
    assert cand.review_status == APPROVED
    assert cand.auto_approved is True
    history = mapping.list_history("c-auto")
    assert len(history) == 1
    assert history[0]["reviewer"] == AUTO_REVIEWER
    assert history[0]["from_status"] == DRAFT and history[0]["to_status"] == APPROVED


def test_medium_low_enter_draft_queue(mapping) -> None:
    """中/低置信度进审核队列：初始 draft、auto_approved=False、无 auto 历史。"""
    medium = mapping.create(_candidate(candidate_id="c-m", score=0.7))
    low = mapping.create(_candidate(candidate_id="c-l", score=0.3))
    assert medium.review_status == DRAFT and medium.auto_approved is False
    assert low.review_status == DRAFT and low.auto_approved is False
    assert mapping.list_history("c-m") == []
    items, total = mapping.list(level="low")
    assert total == 1 and items[0].candidate_id == "c-l"
    # 队列按 score 降序：0.7 在 0.3 之前
    queued, _ = mapping.list(status=DRAFT)
    assert [c.candidate_id for c in queued] == ["c-m", "c-l"]


def test_review_state_machine_full_path(mapping) -> None:
    """合法流转：draft→reviewing→approved。"""
    mapping.create(_candidate(candidate_id="c-sm", score=0.7))  # draft
    cand = mapping.transition("c-sm", REVIEWING, reviewer="jack", note="人工接手")
    assert cand.review_status == REVIEWING
    cand = mapping.transition("c-sm", APPROVED, reviewer="jack", note="人工裁决")
    assert cand.review_status == APPROVED


def test_review_state_machine_reject_loop(mapping) -> None:
    """合法流转：draft→reviewing→rejected→draft（允许回环）。"""
    mapping.create(_candidate(candidate_id="c-rj", score=0.5))
    mapping.transition("c-rj", REVIEWING, reviewer="jack")
    cand = mapping.transition("c-rj", REJECTED, reviewer="jack", note="证据不足")
    assert cand.review_status == REJECTED
    cand = mapping.transition("c-rj", DRAFT, reviewer="jack", note="重新打标")
    assert cand.review_status == DRAFT


def test_draft_to_approved_direct_accept(mapping) -> None:
    """合法流转：draft→approved（工作台一键接受）。"""
    mapping.create(_candidate(candidate_id="c-ac", score=0.7))
    cand = mapping.transition("c-ac", APPROVED, reviewer="jack", note="一键接受")
    assert cand.review_status == APPROVED


def test_review_illegal_transition_raises(mapping) -> None:
    """非法流转抛 IllegalTransitionError：draft→rejected、reviewing→draft。"""
    mapping.create(_candidate(candidate_id="c-il", score=0.7))  # draft
    with pytest.raises(IllegalTransitionError):
        mapping.transition("c-il", REJECTED, reviewer="jack")
    mapping.transition("c-il", REVIEWING, reviewer="jack")
    with pytest.raises(IllegalTransitionError):
        mapping.transition("c-il", DRAFT, reviewer="jack")


def test_approved_terminal_state(mapping) -> None:
    """approved 为终态：不可回退不可改。"""
    mapping.create(_candidate(candidate_id="c-term", score=0.7))
    mapping.transition("c-term", APPROVED, reviewer="jack")
    with pytest.raises(IllegalTransitionError):
        mapping.transition("c-term", REJECTED, reviewer="jack")
    with pytest.raises(IllegalTransitionError):
        mapping.transition("c-term", DRAFT, reviewer="jack")
    # 已批准候选（高置信度自动过）同样终态锁定
    mapping.create(_candidate(candidate_id="c-auto2", score=0.95))
    with pytest.raises(IllegalTransitionError):
        mapping.transition("c-auto2", REJECTED, reviewer="jack")


def test_target_not_registered_rejected(mapping) -> None:
    """C4：target 未注册（对象/属性）→ TargetNotRegisteredError；link 不入此校验。"""
    with pytest.raises(TargetNotRegisteredError):
        mapping.create(_candidate(candidate_id="c-bad", target="GhostObject", score=0.95))
    with pytest.raises(TargetNotRegisteredError):
        mapping.create(
            _candidate(candidate_id="c-bad2", kind="attribute", target="ghost_field", score=0.9)
        )
    link = mapping.create(
        _candidate(candidate_id="c-link", kind="link", target="any_link", score=0.8)
    )
    assert link.kind == "link"


def test_review_history_append_only(mapping, store) -> None:
    """审核痕迹：每次流转必有一条 history、与终态一致、append-only（触发器禁改删）。"""
    mapping.create(_candidate(candidate_id="c-h", score=0.7))
    mapping.transition("c-h", REVIEWING, reviewer="jack", note="接单")
    mapping.transition("c-h", APPROVED, reviewer="jack", note="通过")
    history = mapping.list_history("c-h")
    assert len(history) == 2
    assert [h["to_status"] for h in history] == [REVIEWING, APPROVED]
    assert mapping.get("c-h").review_status == APPROVED
    conn = store.ontology_conn()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE mapping_review_history SET reviewer='x'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM mapping_review_history")
    finally:
        conn.close()


def test_score_out_of_range_rejected() -> None:
    """score∈[0,1]：越界构造直接 ValidationError（模型 Field(ge=0, le=1)）。"""
    with pytest.raises(ValidationError):
        _candidate(score=1.5)
    with pytest.raises(ValidationError):
        _candidate(score=-0.1)


def test_confidence_level_derived_from_score(mapping) -> None:
    """档位与分数自洽：create 一律由 classify(score) 派生，覆盖 caller 传入的不一致档位。"""
    cand = mapping.create(
        _candidate(candidate_id="c-consist", score=0.95, confidence_level="low")
    )
    assert cand.confidence_level == "high"


def test_annotate_mapping_candidates_entry(mapping, store, registry) -> None:
    """打标入口：适配器输出 → classify → routing → 落表；未注册 target 跳过。"""
    source = {
        "source_table": "retail_orders",
        "des_mappings": [
            {"kind": "object", "target": "Order"},
            {"kind": "attribute", "target": "order_id", "source_field": "order_no"},
            {"kind": "object", "target": "GhostObject"},  # 未注册 → 跳过
        ],
    }
    persisted = annotate_mapping_candidates(source, registry, store=store)
    assert len(persisted) == 2
    assert sorted(c.target for c in persisted) == ["Order", "order_id"]
    assert all(c.auto_approved and c.review_status == APPROVED for c in persisted)


# ======================================================================
# GovernanceValidator（self_check 一致性机验）
# ======================================================================
def _policy_row(**kw) -> dict:
    defaults = {
        "policy_id": "p", "object_type": "Order", "operation": "read", "effect": "allow",
        "subject_kind": "agent", "subject_id": "a", "role_id": "", "scope": "object",
        "attributes_json": "[]",
    }
    return {**defaults, **kw}


def _candidate_row(**kw) -> dict:
    defaults = {
        "candidate_id": "c", "kind": "object", "source_table": "t", "source_field": None,
        "target": "Order", "confidence_score": 0.7, "confidence_level": "medium",
        "review_status": "draft", "auto_approved": 0, "evidence_json": "{}",
    }
    return {**defaults, **kw}


def test_gov_policy_unknown_object(registry) -> None:
    """instance_data 路径：策略引用不存在对象 → error 级 GOV_POLICY_UNKNOWN_OBJECT。"""
    check = governance_self_checks()
    issues = check(
        registry,
        {"permission_policies": [_policy_row(object_type="GhostObj")],
         "permission_roles": [], "mapping_candidates": []},
    )
    assert any(i.severity == "error" and i.code == GOV_POLICY_UNKNOWN_OBJECT for i in issues)


def test_gov_policy_unknown_attribute(registry) -> None:
    check = governance_self_checks()
    issues = check(
        registry,
        {"permission_policies": [_policy_row(attributes_json='["bogus_col"]')],
         "permission_roles": [], "mapping_candidates": []},
    )
    assert any(i.severity == "error" and i.code == GOV_POLICY_UNKNOWN_ATTRIBUTE for i in issues)


def test_gov_candidate_unknown_target(registry) -> None:
    check = governance_self_checks()
    issues = check(
        registry,
        {"permission_policies": [], "permission_roles": [],
         "mapping_candidates": [_candidate_row(target="GhostObj")]},
    )
    assert any(i.severity == "error" and i.code == GOV_CAND_UNKNOWN_TARGET for i in issues)


def test_gov_mount_store_scan_detects_bad_rows(store, registry) -> None:
    """store 扫描路径：mount 后 self_check 全量扫出库内脏数据（绕过服务层的旁路写入）。"""
    conn = store.ontology_conn()
    try:
        conn.execute(
            "INSERT INTO permission_policies (policy_id, object_type, operation, effect, "
            "subject_kind, subject_id, role_id, scope, attributes_json, version, created_at, "
            "updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("bad-policy", "GhostObj", "read", "allow", "agent", "a", "", "object", "[]",
             1, "t", "t"),
        )
        conn.execute(
            "INSERT INTO mapping_candidates (candidate_id, kind, source_table, source_field, "
            "target, confidence_score, confidence_level, review_status, auto_approved, "
            "evidence_json, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("bad-cand", "object", "t", None, "GhostObj", 0.7, "medium", "draft", 0, "{}",
             "t", "t"),
        )
        conn.commit()
    finally:
        conn.close()
    mount_governance_checks(registry, store)
    issues = registry.self_check()
    codes = [i.code for i in issues]
    assert GOV_POLICY_UNKNOWN_OBJECT in codes
    assert GOV_CAND_UNKNOWN_TARGET in codes
    bad = [i for i in issues if i.code == GOV_POLICY_UNKNOWN_OBJECT]
    assert all(i.severity == "error" for i in bad)
