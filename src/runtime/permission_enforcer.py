"""动作执行侧权限门实现（P4，设计 §1）：DefaultPermissionEnforcer + 动作→(对象,操作) 映射。

- ACTION_PERMISSION_MAP：6 动作 → (object_type, operation)（design §1.1）；
- resolve_actor：actor 字符串 → PermissionSubject（human/agent，approve 强制 human V9）；
- DefaultPermissionEnforcer：实现 PermissionEnforcer Protocol（action_engine），
  委托 src.runtime.permissions.decide 纯函数，fail-closed（无匹配策略 → denied）。
"""

from __future__ import annotations

from typing import Any

from src.runtime.permissions import (
    PermissionDecision,
    PermissionRegistry,
    PermissionSubject,
)

# ---------------------------------------------------------------------------
# 动作 → (对象, 操作) 映射（设计 §1.1，单一来源常量）
# ---------------------------------------------------------------------------
ACTION_PERMISSION_MAP: dict[str, tuple[str, str]] = {
    "create_order": ("Order", "write"),
    "confirm_order": ("Order", "write"),
    "cancel_order": ("Order", "write"),
    "create_shipment": ("Shipment", "write"),
    "adjust_inventory": ("Inventory", "write"),
    # approve_refund 不入权限门（demo 口径）：S1 §5.4 双签人机层把关
    # （LLM 提议 → human 确认才执行，执行器 actor=llm 但已被人类授权）；
    # 策略级 approve 门（subject=human）留 P4 收尾/发布期在 confirm 路径接 human 后纳入。
}


def resolve_actor(actor: str, *, is_llm: bool) -> PermissionSubject:
    """actor 字符串 → PermissionSubject（设计 §1.2）。

    - is_llm=True（Agent/LLM 执行）→ agent 主体；
    - 否则 → human 主体（API X-Actor，S1 白名单已在路由层校验）。
    """
    kind = "agent" if is_llm else "human"
    return PermissionSubject(kind=kind, id=actor)


class DefaultPermissionEnforcer:
    """动作权限门：映射表取 (对象, 操作) → 解析 subject → decide（fail-closed）。

    未在映射表中的动作返回 None（不纳入权限门，保持调用方语义）；
    映射表中动作：无匹配策略/显式 deny → denied（越权 0，fail-closed）。
    """

    def __init__(self, permission_registry: PermissionRegistry) -> None:
        self._registry = permission_registry

    def decide(
        self, action_name: str, params: dict[str, Any], actor: str
    ) -> PermissionDecision | None:
        mapping = ACTION_PERMISSION_MAP.get(action_name)
        if mapping is None:
            return None  # 未纳入权限门（协议语义）
        object_type, operation = mapping
        subject = resolve_actor(actor, is_llm=(actor == "llm"))
        return self._registry.decide(subject, object_type, operation)
