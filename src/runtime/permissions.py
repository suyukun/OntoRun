"""权限元数据（P1.5 治理骨架 ①，设计 §1）。

权限 = 语义层「操作级门禁 + 属性级读标注」（D5/D6：数据权限下沉 P4，此处只标注不强制）。
- 双主体（agent/human）读·写·审三分治（D1/D2/D3）；
- 对象级 + 属性级（属性级只读，D4）；
- 策略元数据落 permission_roles / permission_policies 表；内存注册表供 O(1) decide()；
- 写时（create/update）与批量校验共用 validate_policy 单一实现（V1–V9，设计 1.4）。

P1.5 不接线动作/查询执行（接线 = P4/P2，接入点见设计 1.6/4.4）。
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from src.ontology.registry import Registry
from src.runtime.store import (
    PERMISSION_EFFECTS,
    PERMISSION_OPERATIONS,
    POLICY_SCOPES,
    SUBJECT_KINDS,
    Store,
)

PermissionOperation = Literal["read", "write", "approve"]  # D2 三分治
PermissionEffect = Literal["allow", "deny"]
SubjectKind = Literal["agent", "human"]  # D1 双主体
PolicyScope = Literal["object", "attribute"]  # D4 粒度

# 枚举集合（单一来源 = store 顶部常量，防运行时校验与 DB CHECK 双轨漂移）
_OP_SET = frozenset(PERMISSION_OPERATIONS)
_EFFECT_SET = frozenset(PERMISSION_EFFECTS)
_KIND_SET = frozenset(SUBJECT_KINDS)
_SCOPE_SET = frozenset(POLICY_SCOPES)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------------
# 模型（设计 1.2）
# ----------------------------------------------------------------------
class PermissionSubject(BaseModel):
    """双主体：agent（LLM/Agent 操作）或 human（人/工作台）。"""

    kind: SubjectKind
    id: str  # agent:"procurement_agent" / human:"jack"


class PermissionPolicy(BaseModel):
    """一条权限策略：谁（subject/role）对哪个对象/属性做什么操作、allow 还是 deny。"""

    policy_id: str
    object_type: str  # 必须已注册对象（V1）
    operation: PermissionOperation
    effect: PermissionEffect = "allow"
    subject: PermissionSubject | None = None  # 直接主体；与 role_id 二选一（V7）
    role_id: str | None = None  # 便捷分组引用
    scope: PolicyScope = "object"
    attributes: list[str] = Field(default_factory=list)  # 仅 operation=read 允许非空（V6）
    version: int = 1
    created_at: str = ""
    updated_at: str = ""


class PermissionRole(BaseModel):
    """角色便捷分组：role = 一组 subject；策略可引用 role_id 代替逐主体列举（D7）。"""

    role_id: str
    name: str
    members: list[PermissionSubject] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


# ----------------------------------------------------------------------
# V1–V9 写时机验单一实现（设计 1.4：写时与批量校验共用，防双轨漂移）
# ----------------------------------------------------------------------
def validate_policy(
    policy: PermissionPolicy,
    *,
    registry: Registry,
    roles: dict[str, PermissionRole],
    existing_policy_ids: set[str],
) -> list[str]:
    """校验一条策略（V1–V9），返回违规消息列表；空列表 = 通过。

    - registry：本体注册表（V1 未知对象 / V2 未知属性）；
    - roles：当前已知角色（{role_id: role}，V7 角色存在 / V9 角色成员全 human）；
    - existing_policy_ids：已占用 policy_id（V8 唯一，create 传全量，update 传排除自身）。
    """
    errors: list[str] = []
    # V1 未知对象
    if not registry.has_object_type(policy.object_type):
        errors.append(f"V1 未知对象: {policy.object_type}")
    else:
        # V2 属性级策略的每个 attribute 必须是该对象 model 字段
        fields = registry.object_type(policy.object_type).model.model_fields
        for attr in policy.attributes:
            if attr not in fields:
                errors.append(f"V2 未知属性: {policy.object_type}.{attr}")
    # V3 非法操作
    if policy.operation not in _OP_SET:
        errors.append(f"V3 非法操作: {policy.operation}")
    # V4 非法效果
    if policy.effect not in _EFFECT_SET:
        errors.append(f"V4 非法效果: {policy.effect}")
    # V5 非法主体类型
    if policy.subject is not None and policy.subject.kind not in _KIND_SET:
        errors.append(f"V5 非法主体类型: {policy.subject.kind}")
    # V6 属性级仅读（attributes 非空 ⇒ operation == "read"）
    if policy.attributes and policy.operation != "read":
        errors.append(f"V6 属性级仅读: attributes 非空但 operation={policy.operation}")
    # V7 角色存在 / subject 与 role_id 二选一
    if policy.role_id is not None and policy.role_id:
        if policy.role_id not in roles:
            errors.append(f"V7 未知角色: {policy.role_id}")
        if policy.subject is not None:
            errors.append("V7 主体与角色二选一: subject 与 role_id 不能同时填写")
    elif policy.subject is None:
        errors.append("V7 主体与角色二选一: subject 与 role_id 必须填写其一")
    # V8 policy_id 唯一（防静默覆盖，对齐 Registry 先例）
    if policy.policy_id in existing_policy_ids:
        errors.append(f"V8 重复策略: {policy.policy_id}")
    # V9 审=人专属（operation=approve ⇒ subject 为 human / 角色成员全 human）
    if policy.operation == "approve":
        if policy.subject is not None:
            if policy.subject.kind != "human":
                errors.append(f"V9 审=人专属: operation=approve 但 subject.kind={policy.subject.kind}")
        elif policy.role_id is not None:
            role = roles.get(policy.role_id)
            if role is not None and any(m.kind != "human" for m in role.members):
                errors.append(f"V9 审=人专属: 角色 {policy.role_id} 含非 human 成员")
        else:
            errors.append("V9 审=人专属: operation=approve 缺少 subject/role")
    return errors


# ----------------------------------------------------------------------
# decide() 纯函数（设计 1.3）
# ----------------------------------------------------------------------
class PermissionDecision(BaseModel):
    """权限判定结果：allowed + 属性级可见集（读）+ 命中的策略 id（审计溯源）。"""

    allowed: bool
    visible_attributes: list[str] | None = None
    matched_policy_ids: list[str] = Field(default_factory=list)


def _subject_matches(
    policy: PermissionPolicy,
    subject: PermissionSubject,
    roles: dict[str, PermissionRole],
) -> bool:
    """策略主体匹配：直接 subject 精确匹配，或 role 展开后包含该 subject。"""
    if policy.subject is not None:
        return policy.subject.kind == subject.kind and policy.subject.id == subject.id
    if policy.role_id:
        role = roles.get(policy.role_id)
        return role is not None and any(
            m.kind == subject.kind and m.id == subject.id for m in role.members
        )
    return False


def decide(
    subject: PermissionSubject,
    object_type: str,
    operation: PermissionOperation,
    attribute: str | None = None,
    *,
    registry: Registry,
    policies: Iterable[PermissionPolicy],
    roles: dict[str, PermissionRole] | None = None,
) -> PermissionDecision:
    """权限判定（纯函数，无副作用，P4/P2 接线时直接复用）。

    规则：
    R1  fail-closed：无匹配策略 → denied；
    R2  deny-wins：同 (object_type, operation, subject) 上显式 deny 覆盖 allow；
    R3  属性级读可见集：对象级 read allow 给出可读属性全集（对象全部字段），
        再按属性级 deny 剔除；对象级 deny 全局优先（属性级 allow 无法翻案）；
    R4  operation=approve 仅 human（V9 写时机验 + 此处兜底）。
    """
    roles = roles or {}
    matched = [
        p
        for p in policies
        if p.object_type == object_type
        and p.operation == operation
        and _subject_matches(p, subject, roles)
    ]
    matched_ids = [p.policy_id for p in matched]
    # R4 approve-human 兜底（防绕过写时机验的直达调用）
    if operation == "approve" and subject.kind != "human":
        return PermissionDecision(
            allowed=False, visible_attributes=None, matched_policy_ids=matched_ids
        )
    object_denied = any(p.scope == "object" and p.effect == "deny" for p in matched)
    if operation == "read":
        object_allowed = any(
            p.scope == "object" and p.effect == "allow" for p in matched
        )
        if object_denied or not object_allowed:  # R1 + R2
            return PermissionDecision(
                allowed=False, visible_attributes=None, matched_policy_ids=matched_ids
            )
        # R3 属性级读可见集：全字段 - 属性级 deny 剔除
        model = registry.object_type(object_type).model
        denied_attrs: set[str] = set()
        for p in matched:
            if p.scope == "attribute" and p.effect == "deny":
                denied_attrs.update(p.attributes)
        visible = [f for f in model.model_fields if f not in denied_attrs]
        allowed = attribute is None or attribute in visible
        return PermissionDecision(
            allowed=allowed,
            visible_attributes=visible,
            matched_policy_ids=matched_ids,
        )
    # write / approve：对象级 deny 优先（R2），否则对象级 allow
    object_allowed = any(
        p.scope == "object" and p.effect == "allow" for p in matched
    )
    return PermissionDecision(
        allowed=not object_denied and object_allowed,
        visible_attributes=None,
        matched_policy_ids=matched_ids,
    )


# ----------------------------------------------------------------------
# 行 <-> 模型转换（permission_policies / permission_roles 表）
# ----------------------------------------------------------------------
def _policy_to_row(policy: PermissionPolicy) -> tuple:
    subject = policy.subject
    return (
        policy.policy_id,
        policy.object_type,
        policy.operation,
        policy.effect,
        subject.kind if subject else "",
        subject.id if subject else "",
        policy.role_id or "",
        policy.scope,
        json.dumps(policy.attributes, ensure_ascii=False),
        policy.version,
        policy.created_at,
        policy.updated_at,
    )


def _row_to_policy(row) -> PermissionPolicy:
    subject = (
        PermissionSubject(kind=row["subject_kind"], id=row["subject_id"])
        if row["subject_kind"]
        else None
    )
    return PermissionPolicy(
        policy_id=row["policy_id"],
        object_type=row["object_type"],
        operation=row["operation"],
        effect=row["effect"],
        subject=subject,
        role_id=row["role_id"] or None,
        scope=row["scope"],
        attributes=json.loads(row["attributes_json"] or "[]"),
        version=row["version"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _role_to_row(role: PermissionRole) -> tuple:
    return (
        role.role_id,
        role.name,
        json.dumps([m.model_dump() for m in role.members], ensure_ascii=False),
        role.created_at,
        role.updated_at,
    )


def _row_to_role(row) -> PermissionRole:
    members = [
        PermissionSubject(**m) for m in json.loads(row["members_json"] or "[]")
    ]
    return PermissionRole(
        role_id=row["role_id"],
        name=row["name"],
        members=members,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ----------------------------------------------------------------------
# PermissionRegistry：内存镜像 + 持久化（设计 1.5）
# ----------------------------------------------------------------------
class PermissionRegistry:
    """权限元数据内存镜像 + 落表 CRUD（启动 load() 从表加载，供 O(1) decide()）。"""

    def __init__(self, store: Store, registry: Registry) -> None:
        self._store = store
        self._registry = registry
        self._policies: dict[str, PermissionPolicy] = {}
        self._roles: dict[str, PermissionRole] = {}
        self.load()

    @property
    def registry(self) -> Registry:
        """本体注册表（V1/V2 与 decide 的属性集来源）。"""
        return self._registry

    # ---- 加载 / 刷新 ----
    def load(self) -> None:
        """从表全量加载进内存镜像（幂等，可重复调用刷新）。"""
        conn = self._store.ontology_conn()
        try:
            # sqlite3.Row 只支持键访问（row["x"]），不支持属性访问（row.x）
            roles = {
                r["role_id"]: _row_to_role(r)
                for r in conn.execute("SELECT * FROM permission_roles").fetchall()
            }
            policies = {
                p["policy_id"]: _row_to_policy(p)
                for p in conn.execute("SELECT * FROM permission_policies").fetchall()
            }
            self._roles = roles
            self._policies = policies
        finally:
            conn.close()

    # ---- 策略持久化（落表 + 更新内存） ----
    def save_policy(self, policy: PermissionPolicy) -> PermissionPolicy:
        conn = self._store.ontology_conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO permission_policies (policy_id, object_type, "
                "operation, effect, subject_kind, subject_id, role_id, scope, "
                "attributes_json, version, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                _policy_to_row(policy),
            )
            conn.commit()
        finally:
            conn.close()
        self._policies[policy.policy_id] = policy
        return policy

    def delete_policy(self, policy_id: str) -> bool:
        conn = self._store.ontology_conn()
        try:
            cur = conn.execute(
                "DELETE FROM permission_policies WHERE policy_id=?", (policy_id,)
            )
            conn.commit()
            removed = cur.rowcount > 0
        finally:
            conn.close()
        self._policies.pop(policy_id, None)
        return removed

    # ---- 角色持久化 ----
    def save_role(self, role: PermissionRole) -> PermissionRole:
        conn = self._store.ontology_conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO permission_roles (role_id, name, members_json, "
                "created_at, updated_at) VALUES (?,?,?,?,?)",
                _role_to_row(role),
            )
            conn.commit()
        finally:
            conn.close()
        self._roles[role.role_id] = role
        return role

    def delete_role(self, role_id: str) -> bool:
        conn = self._store.ontology_conn()
        try:
            cur = conn.execute(
                "DELETE FROM permission_roles WHERE role_id=?", (role_id,)
            )
            conn.commit()
            removed = cur.rowcount > 0
        finally:
            conn.close()
        self._roles.pop(role_id, None)
        return removed

    # ---- 查询 ----
    def get_policy(self, policy_id: str) -> PermissionPolicy | None:
        return self._policies.get(policy_id)

    def list_policies(self) -> list[PermissionPolicy]:
        return sorted(self._policies.values(), key=lambda p: p.policy_id)

    def policy_ids(self) -> set[str]:
        return set(self._policies)

    def get_role(self, role_id: str) -> PermissionRole | None:
        return self._roles.get(role_id)

    def list_roles(self) -> list[PermissionRole]:
        return sorted(self._roles.values(), key=lambda r: r.role_id)

    def roles_dict(self) -> dict[str, PermissionRole]:
        return dict(self._roles)

    # ---- 判定入口（内存镜像） ----
    def decide(
        self,
        subject: PermissionSubject,
        object_type: str,
        operation: PermissionOperation,
        attribute: str | None = None,
    ) -> PermissionDecision:
        return decide(
            subject,
            object_type,
            operation,
            attribute,
            registry=self._registry,
            policies=self._policies.values(),
            roles=self._roles,
        )


# ----------------------------------------------------------------------
# PermissionService：CRUD + V1–V9 校验（设计 1.5，P1.5「可写」以服务层为准）
# ----------------------------------------------------------------------
class PermissionService:
    """权限服务层：create/update/delete/get/list（策略 + 角色），V1–V9 校验后落表并同步镜像。"""

    def __init__(
        self,
        store: Store,
        registry: Registry,
        perm_registry: PermissionRegistry | None = None,
    ) -> None:
        self._store = store
        self._registry = registry
        self._perm = perm_registry or PermissionRegistry(store, registry)

    @property
    def perm_registry(self) -> PermissionRegistry:
        return self._perm

    # ---- 策略 CRUD ----
    def _validate(
        self, policy: PermissionPolicy, *, exclude_self: bool = False
    ) -> list[str]:
        existing = self._perm.policy_ids()
        if exclude_self:
            existing = {i for i in existing if i != policy.policy_id}
        return validate_policy(
            policy,
            registry=self._registry,
            roles=self._perm.roles_dict(),
            existing_policy_ids=existing,
        )

    def create(self, policy: PermissionPolicy) -> PermissionPolicy:
        errors = self._validate(policy)
        if errors:
            raise ValueError("；".join(errors))
        now = _now()
        policy = policy.model_copy(update={"created_at": now, "updated_at": now})
        return self._perm.save_policy(policy)

    def update(self, policy_id: str, changes: dict) -> PermissionPolicy:
        """更新策略：replace 语义 + version+1（设计任务口径），V1–V9 复验。"""
        current = self._perm.get_policy(policy_id)
        if current is None:
            raise KeyError(f"策略不存在: {policy_id}")
        updated = current.model_copy(
            update={**changes, "version": current.version + 1, "updated_at": _now()}
        )
        errors = self._validate(updated, exclude_self=True)
        if errors:
            raise ValueError("；".join(errors))
        return self._perm.save_policy(updated)

    def delete(self, policy_id: str) -> bool:
        if not self._perm.delete_policy(policy_id):
            raise KeyError(f"策略不存在: {policy_id}")
        return True

    def get(self, policy_id: str) -> PermissionPolicy | None:
        return self._perm.get_policy(policy_id)

    def list(self) -> list[PermissionPolicy]:
        return self._perm.list_policies()

    # ---- 角色 CRUD（D7 便捷分组） ----
    def create_role(self, role: PermissionRole) -> PermissionRole:
        if self._perm.get_role(role.role_id) is not None:
            raise ValueError(f"V8 重复角色: {role.role_id}")
        for member in role.members:
            if member.kind not in _KIND_SET:
                raise ValueError(f"V5 非法主体类型: {member.kind}")
        now = _now()
        role = role.model_copy(update={"created_at": now, "updated_at": now})
        return self._perm.save_role(role)

    def get_role(self, role_id: str) -> PermissionRole | None:
        return self._perm.get_role(role_id)

    def list_roles(self) -> list[PermissionRole]:
        return self._perm.list_roles()

    def delete_role(self, role_id: str) -> bool:
        if not self._perm.delete_role(role_id):
            raise KeyError(f"角色不存在: {role_id}")
        return True


__all__ = [
    "PermissionDecision",
    "PermissionEffect",
    "PermissionOperation",
    "PermissionPolicy",
    "PermissionRegistry",
    "PermissionRole",
    "PermissionService",
    "PermissionSubject",
    "PolicyScope",
    "SubjectKind",
    "decide",
    "validate_policy",
]
