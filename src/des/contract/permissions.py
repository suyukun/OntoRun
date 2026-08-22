"""读侧权限上下文（设计 §3.3）：PermissionDecider 协议 + 静态注册表 + PermissionContext。

ContractExecutor 传入 permission_ctx 即启用读侧权限：查询前 decide(subject, object_type,
"read")，属性级 visible_attributes 过滤返回列；缺省 None = 默认 deny（fail-closed）。
与 v0.1 单文件实现行为一致。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.runtime.permissions import (
    PermissionDecision,
    PermissionSubject,
)


class PermissionDecider(Protocol):
    """权限判定协议：PermissionRegistry 与静态工厂（deny_all/allow_all）共用 decide()。"""

    def decide(
        self,
        subject: PermissionSubject,
        object_type: str,
        operation: str,
        attribute: str | None = None,
    ) -> PermissionDecision: ...


class _StaticPermissionRegistry:
    """固定判定注册表（PermissionContext.deny_all/allow_all 内部用）。

    deny=True → 一切操作判定 denied（fail-closed 默认）；deny=False → read 全属性可见
    （visible_attributes=None 语义 = 全字段可见，见 _permission_visible 兜底）。
    """

    def __init__(self, *, deny: bool) -> None:
        self._deny = deny

    def decide(
        self,
        subject: PermissionSubject,
        object_type: str,
        operation: str,
        attribute: str | None = None,
    ) -> PermissionDecision:
        if self._deny:
            return PermissionDecision(allowed=False, visible_attributes=None)
        return PermissionDecision(allowed=True, visible_attributes=None)


# deny_all/allow_all 静态上下文的系统主体（内部工具/默认 deny 标识，非真实用户）
SYSTEM_SUBJECT = PermissionSubject(kind="agent", id="system")


@dataclass(frozen=True)
class PermissionContext:
    """读侧权限上下文（设计 §3.3）：主体 + 权限判定器。

    传给 ContractExecutor 即启用读侧权限：查询前 decide(subject, object_type, "read")，
    属性级 visible_attributes 过滤返回列；契约显式请求的字段触及不可见列 fail-closed 拒答
    （不静默裁剪，防推断泄漏）。缺省 None = 默认 deny（red-team P1-1：无 ctx ≠ 无校验，
    fail-closed）——内部工具需显式 PermissionContext.allow_all() 才放行。
    """

    subject: PermissionSubject
    permission_registry: PermissionDecider

    @classmethod
    def deny_all(cls, subject: PermissionSubject | None = None) -> PermissionContext:
        """默认 deny 上下文（fail-closed）：一切操作判定 denied（read 直接拒答）。

        ContractExecutor 未显式传 ctx 时的缺省——无 ctx ≠ 无权限校验。
        """
        return cls(
            subject=subject or SYSTEM_SUBJECT,
            permission_registry=_StaticPermissionRegistry(deny=True),
        )

    @classmethod
    def allow_all(cls, subject: PermissionSubject | None = None) -> PermissionContext:
        """显式 allow-all 上下文（内部工具/测试口径）：read 全属性可见。

        仅一次性脚本/内部对账工具显式选择；生产查询不得使用（权限开关必须显式可见）。
        """
        return cls(
            subject=subject or SYSTEM_SUBJECT,
            permission_registry=_StaticPermissionRegistry(deny=False),
        )
