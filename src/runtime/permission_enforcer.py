"""动作执行侧权限门实现（P4，设计 §1）：DefaultPermissionEnforcer + 动作→(对象,操作) 映射。

- ACTION_PERMISSION_MAP：6 动作 → (object_type, operation)（design §1.1）；
- resolve_actor：actor 字符串 → PermissionSubject（human/agent，approve 强制 human R4）；
- DefaultPermissionEnforcer：实现 PermissionEnforcer Protocol（action_engine），
  委托 src.runtime.permissions.decide 纯函数，fail-closed：
  * 映射表内动作：无匹配策略/显式 deny → denied（越权 0）；
  * 未映射动作：显式 deny（P2-1 缺省 deny + 显式 allowlist，与设计文档
    「任何无显式 allow 策略的动作执行 → denied」一致，杜绝默认放行）。
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
    # P1-1（red-team）：approve_refund 入权限门 → (Refund, 'approve')。
    # 审=人专属（R4）：agent（llm）主体直调 → deny；种子策略仅给 human；
    # LLM 路径只能走 /agent 双签（LLM 提议 → human 确认 → 以 human 身份提交）。
    "approve_refund": ("Refund", "approve"),
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

    映射表内动作：无匹配策略/显式 deny → denied（越权 0，fail-closed）；
    未映射动作：显式 deny（P2-1，缺省 deny + 显式 allowlist）——绝不返回
    None 放行：任何无显式 allow 策略的动作执行 → denied（设计文档口径）。
    """

    def __init__(self, permission_registry: PermissionRegistry) -> None:
        self._registry = permission_registry

    def decide(
        self, action_name: str, params: dict[str, Any], actor: str
    ) -> PermissionDecision:
        mapping = ACTION_PERMISSION_MAP.get(action_name)
        if mapping is None:
            # P2-1：未映射动作（动态新动作等）→ 显式 deny（缺省 deny + 显式 allowlist）。
            # 命中策略为空（matched_policy_ids=[]），引擎 detail 记 action_name/actor 溯源。
            return PermissionDecision(
                allowed=False, visible_attributes=None, matched_policy_ids=[]
            )
        object_type, operation = mapping
        subject = resolve_actor(actor, is_llm=(actor == "llm"))
        return self._registry.decide(subject, object_type, operation)
