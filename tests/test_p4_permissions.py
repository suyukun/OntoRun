"""P4 操作权限门测试（越权 0）：DefaultPermissionEnforcer + 种子策略。

覆盖（设计 §1 + red-team P1-1/P2-1 修复）：
- 写动作 fail-closed（未种子 actor 拒绝）、种子 actor 放行；
- approve_refund 入权限门 → (Refund, 'approve')：human 放行，agent（llm/api）拒绝（R4 兜底）；
- 未映射动作（动态新动作）→ 显式 deny（缺省 deny + 显式 allowlist，P2-1）；
- resolve_actor 双主体解析。
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.ontology import build_registry
from src.runtime.action_engine import ALLOWED_ACTORS
from src.runtime.permission_enforcer import (
    ACTION_PERMISSION_MAP,
    DefaultPermissionEnforcer,
    resolve_actor,
)
from src.runtime.permission_setup import build_permission_enforcer
from src.runtime.store import Store

# 注册表 6 动作 = 映射表 6 动作（P1-1：approve_refund 必须入权限门）
ALL_ACTIONS = {
    "create_order",
    "confirm_order",
    "cancel_order",
    "create_shipment",
    "adjust_inventory",
    "approve_refund",
}


def _setup() -> tuple[Store, DefaultPermissionEnforcer]:
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()
    registry = build_registry()
    enforcer = build_permission_enforcer(store, registry)
    return store, enforcer


def test_map_covers_all_registered_actions() -> None:
    """映射表覆盖全部 6 个动作；approve_refund → (Refund, 'approve')。"""
    assert set(ACTION_PERMISSION_MAP) == ALL_ACTIONS
    assert ACTION_PERMISSION_MAP["approve_refund"] == ("Refund", "approve")
    for action, (obj, op) in ACTION_PERMISSION_MAP.items():
        if action == "approve_refund":
            assert op == "approve", f"{action} 应为 approve 操作"
        else:
            assert op == "write", f"{action} 应为 write 操作"


def test_seeded_actor_allowed() -> None:
    """种子 actor（human/llm/api）执行写动作 → allow。"""
    _, enforcer = _setup()
    for actor in ALLOWED_ACTORS:
        dec = enforcer.decide("cancel_order", {}, actor)
        assert dec is not None and dec.allowed, f"{actor} cancel_order 应 allow"


def test_unseeded_actor_denied() -> None:
    """未种子 actor（越权）执行写动作 → deny（fail-closed，越权 0）。"""
    _, enforcer = _setup()
    for actor in ("attacker", "suspicious"):
        dec = enforcer.decide("cancel_order", {}, actor)
        assert dec is not None and not dec.allowed, f"{actor} 应 deny（越权 0）"


def test_approve_human_allowed() -> None:
    """P1-1：approve 审=人专属——human 主体 approve_refund → allow（种子策略）。"""
    _, enforcer = _setup()
    dec = enforcer.decide("approve_refund", {}, "human")
    assert dec is not None and dec.allowed, "human approve_refund 应 allow"


def test_approve_agent_denied() -> None:
    """P1-1：approve 审=人专属——agent（llm）→ R4 兜底 deny；api（无种子）→ deny。"""
    _, enforcer = _setup()
    for actor in ("llm", "api"):
        dec = enforcer.decide("approve_refund", {}, actor)
        assert dec is not None and not dec.allowed, f"{actor} approve_refund 应 deny"


def test_unmapped_action_denied() -> None:
    """P2-1：未列入映射表的动作 → 显式 deny（缺省 deny + 显式 allowlist）。"""
    _, enforcer = _setup()
    for actor in ("human", "llm", "api"):
        dec = enforcer.decide("some_dynamic_new_action", {}, actor)
        assert dec is not None, "未映射动作不得返回 None（=默认放行）"
        assert not dec.allowed, f"{actor} 动态新动作应 deny（fail-closed）"


def test_resolve_actor_dual_subject() -> None:
    """双主体解析：llm → agent；human/api → human。"""
    assert resolve_actor("llm", is_llm=True).kind == "agent"
    assert resolve_actor("human", is_llm=False).kind == "human"
    assert resolve_actor("api", is_llm=False).kind == "human"
