"""P4 动作权限门接线：演示策略种子（幂等）+ create_app 装配。

- seed_demo_permission_policies：为 ALLOWED_ACTORS × ACTION_PERMISSION_MAP 幂等插入 allow 策略，
  使演示/既有测试在 fail-closed 权限门下保持可用（显式、可见的演示放行，非默认放行）；
- build_permission_enforcer：加载/创建 PermissionRegistry 并返回 DefaultPermissionEnforcer。
"""

from __future__ import annotations

from src.runtime.action_engine import ALLOWED_ACTORS  # 同源（store.py）
from src.runtime.permission_enforcer import ACTION_PERMISSION_MAP
from src.runtime.permissions import (
    PermissionPolicy,
    PermissionService,
    PermissionSubject,
)


def seed_demo_permission_policies(
    service: PermissionService, allowed_actors: tuple[str, ...] = ALLOWED_ACTORS
) -> int:
    """幂等种子：ALLOWED_ACTORS × 6 动作 → allow 策略（演示/既有测试可用性）。

    已存在的 policy_id 跳过（幂等）；返回本次新增条数。
    """
    created = 0
    for action, (object_type, operation) in ACTION_PERMISSION_MAP.items():
        for actor in allowed_actors:
            # V9：approve 审=人专属，agent（llm/api）不可审批——approve 只给 human 种子
            if operation == "approve" and actor != "human":
                continue
            policy_id = f"demo_{action}_{actor}"
            if service.get(policy_id) is not None:
                continue
            service.create(
                PermissionPolicy(
                    policy_id=policy_id,
                    object_type=object_type,
                    operation=operation,
                    effect="allow",
                    subject=PermissionSubject(
                        kind="human" if actor != "llm" else "agent", id=actor
                    ),
                )
            )
            created += 1
    return created


def build_permission_enforcer(store, registry):
    """装配 P4 动作权限门：PermissionRegistry（从表加载）+ 演示种子 + enforcer。

    供 create_app 在 ActionEngine 构造前调用。
    """
    from src.runtime.permissions import PermissionRegistry

    perm_registry = PermissionRegistry(store, registry)
    perm_registry.load()
    service = PermissionService(store, registry, perm_registry=perm_registry)
    seed_demo_permission_policies(service)
    from src.runtime.permission_enforcer import DefaultPermissionEnforcer

    return DefaultPermissionEnforcer(perm_registry)
