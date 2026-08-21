"""P4 操作权限门测试（越权 0）：DefaultPermissionEnforcer + 种子策略。

覆盖（设计 §1）：写动作 fail-closed（未种子 actor 拒绝）、种子 actor 放行、
approve 不入权限门（双签人机层）、resolve_actor 双主体解析。
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


def _setup() -> tuple[Store, DefaultPermissionEnforcer]:
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()
    registry = build_registry()
    enforcer = build_permission_enforcer(store, registry)
    return store, enforcer


def test_map_covers_write_actions() -> None:
    """映射表覆盖 5 个写动作，approve 不入权限门（双签人机层）。"""
    assert set(ACTION_PERMISSION_MAP) == {
        "create_order", "confirm_order", "cancel_order",
        "create_shipment", "adjust_inventory",
    }
    for action, (obj, op) in ACTION_PERMISSION_MAP.items():
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


def test_approve_not_gated() -> None:
    """approve_refund 不入权限门（双签人机层把关），enforcer 返回 None。"""
    _, enforcer = _setup()
    assert enforcer.decide("approve_refund", {}, "llm") is None


def test_resolve_actor_dual_subject() -> None:
    """双主体解析：llm → agent；human/api → human。"""
    assert resolve_actor("llm", is_llm=True).kind == "agent"
    assert resolve_actor("human", is_llm=False).kind == "human"
    assert resolve_actor("api", is_llm=False).kind == "human"
