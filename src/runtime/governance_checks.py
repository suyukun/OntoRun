"""GovernanceValidator 自检（P1.5 治理骨架，设计 §4.4 / §1.4）。

对 ontology.db 治理段数据做「引用一致性 + 枚举合法性」机验，经 Registry.add_self_check
挂载（des_self_checks 先例，registry 保持通用）：

- 权限策略（permission_policies）：引用的对象/属性必须在注册表存在（V1/V2）、
  operation/effect/subject_kind/scope 枚举合法（V3/V4/V5）、approve 仅 human（V9）；
- 映射候选（mapping_candidates）：target 必须在注册表存在（C4，link 不入此校验——
  P3 入注册表时校验）、score∈[0,1]、confidence_level 与 classify(score) 自洽（档位漂移警告）。

调用形态（对齐 des_self_checks 的 self_check(instance_data=...) 签名）：
- 有 instance_data 时用行数据校验（{permission_policies: [...], permission_roles: [...],
  mapping_candidates: [...]}，行 = 治理段表行 dict）；
- 无 instance_data 时从 store 全量扫描治理段表做一致性校验（store 为 None 则跳过，不误报）。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from src.builder.mapping.annotate import classify
from src.ontology.registry import Issue, Registry
from src.runtime.store import (
    PERMISSION_EFFECTS,
    PERMISSION_OPERATIONS,
    POLICY_SCOPES,
    SUBJECT_KINDS,
    Store,
)

# instance_data 数据键（治理段行数据）
KEY_POLICIES = "permission_policies"
KEY_ROLES = "permission_roles"
KEY_CANDIDATES = "mapping_candidates"

# 权限策略一致性（error）
GOV_POLICY_UNKNOWN_OBJECT = "GOV_POLICY_UNKNOWN_OBJECT"
GOV_POLICY_UNKNOWN_ATTRIBUTE = "GOV_POLICY_UNKNOWN_ATTRIBUTE"
GOV_POLICY_BAD_OPERATION = "GOV_POLICY_BAD_OPERATION"
GOV_POLICY_BAD_EFFECT = "GOV_POLICY_BAD_EFFECT"
GOV_POLICY_BAD_SUBJECT_KIND = "GOV_POLICY_BAD_SUBJECT_KIND"
GOV_POLICY_BAD_SCOPE = "GOV_POLICY_BAD_SCOPE"
GOV_POLICY_APPROVE_NOT_HUMAN = "GOV_POLICY_APPROVE_NOT_HUMAN"
# 映射候选一致性
GOV_CAND_UNKNOWN_TARGET = "GOV_CAND_UNKNOWN_TARGET"
GOV_CAND_SCORE_OUT_OF_RANGE = "GOV_CAND_SCORE_OUT_OF_RANGE"
GOV_CAND_LEVEL_INCONSISTENT = "GOV_CAND_LEVEL_INCONSISTENT"

_OP_SET = frozenset(PERMISSION_OPERATIONS)
_EFFECT_SET = frozenset(PERMISSION_EFFECTS)
_KIND_SET = frozenset(SUBJECT_KINDS)
_SCOPE_SET = frozenset(POLICY_SCOPES)

# 挂载函数签名（与 des_self_checks 一致）
GovernanceCheckFn = Callable[
    ["Registry", dict[str, list[dict[str, Any]]] | None], list[Issue]
]


def _parse_list(value: Any) -> list:
    """attributes_json / members_json 可能是 JSON 字符串或已解析列表（兼容两种行形态）。"""
    if isinstance(value, str):
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (ValueError, TypeError):
            return []
    return list(value or [])


def _attributes_of(row: dict) -> list:
    """策略行的属性列表（attributes 或 attributes_json）。"""
    return _parse_list(row.get("attributes") or row.get("attributes_json"))


def _role_members(role: dict) -> list:
    """角色行的成员列表（members 或 members_json）。"""
    return _parse_list(role.get("members") or role.get("members_json"))


# ----------------------------------------------------------------------
# 权限策略（V1/V2 引用一致 + V3/V4/V5 枚举合法 + V9 approve 仅 human）
# ----------------------------------------------------------------------
def check_permission_policies(
    registry: Registry,
    policies: list[dict],
    roles: dict[str, dict] | None = None,
) -> list[Issue]:
    """校验全部策略：对象/属性存在、操作/效果/主体/粒度枚举合法、approve 仅 human。"""
    roles = roles or {}
    issues: list[Issue] = []
    for row in policies:
        issues.extend(_check_policy_target(registry, row))
        issues.extend(_check_policy_enums(row))
        issues.extend(_check_policy_approve_human(row, roles))
    return issues


def _check_policy_target(registry: Registry, row: dict) -> list[Issue]:
    """V1/V2：策略引用的对象类型 + 属性必须存在。"""
    obj = row.get("object_type") or ""
    pid = row.get("policy_id") or "?"
    if not registry.has_object_type(obj):
        return [
            Issue(
                severity="error",
                code=GOV_POLICY_UNKNOWN_OBJECT,
                message=f"策略 {pid}: 对象 {obj} 未注册",
            )
        ]
    fields = registry.object_type(obj).model.model_fields
    bad = [a for a in _attributes_of(row) if a not in fields]
    if bad:
        return [
            Issue(
                severity="error",
                code=GOV_POLICY_UNKNOWN_ATTRIBUTE,
                message=f"策略 {pid}: 属性 {bad} 不在对象 {obj} 字段",
            )
        ]
    return []


def _check_policy_enums(row: dict) -> list[Issue]:
    """V3/V4/V5 + scope 粒度枚举合法。"""
    issues: list[Issue] = []
    pid = row.get("policy_id") or "?"
    if row.get("operation") not in _OP_SET:
        issues.append(
            Issue(
                severity="error",
                code=GOV_POLICY_BAD_OPERATION,
                message=f"策略 {pid}: operation={row.get('operation')} 非法",
            )
        )
    if row.get("effect") not in _EFFECT_SET:
        issues.append(
            Issue(
                severity="error",
                code=GOV_POLICY_BAD_EFFECT,
                message=f"策略 {pid}: effect={row.get('effect')} 非法",
            )
        )
    sk = row.get("subject_kind") or ""
    if sk and sk not in _KIND_SET:
        issues.append(
            Issue(
                severity="error",
                code=GOV_POLICY_BAD_SUBJECT_KIND,
                message=f"策略 {pid}: subject_kind={sk} 非法",
            )
        )
    scope = row.get("scope") or "object"
    if scope not in _SCOPE_SET:
        issues.append(
            Issue(
                severity="error",
                code=GOV_POLICY_BAD_SCOPE,
                message=f"策略 {pid}: scope={scope} 非法",
            )
        )
    return issues


def _check_policy_approve_human(row: dict, roles: dict[str, dict]) -> list[Issue]:
    """V9：operation=approve ⇒ subject 为 human（直接主体或角色成员全 human）。"""
    if row.get("operation") != "approve":
        return []
    pid = row.get("policy_id") or "?"
    sk = row.get("subject_kind") or ""
    if sk:
        if sk != "human":
            return [
                Issue(
                    severity="error",
                    code=GOV_POLICY_APPROVE_NOT_HUMAN,
                    message=f"策略 {pid}: approve 但 subject.kind={sk} 非 human",
                )
            ]
        return []
    role_id = row.get("role_id") or ""
    if role_id:
        role = roles.get(role_id)
        if role is not None and any(
            (m.get("kind") or "") != "human" for m in _role_members(role)
        ):
            return [
                Issue(
                    severity="error",
                    code=GOV_POLICY_APPROVE_NOT_HUMAN,
                    message=f"策略 {pid}: 角色 {role_id} 含非 human 成员",
                )
            ]
        return []  # 角色数据缺失时跳过（V7 写时范畴，此处不误报）
    return [
        Issue(
            severity="error",
            code=GOV_POLICY_APPROVE_NOT_HUMAN,
            message=f"策略 {pid}: approve 缺少 human 主体",
        )
    ]


# ----------------------------------------------------------------------
# 映射候选（C4 target 存在 + score∈[0,1] + 档位与分数自洽）
# ----------------------------------------------------------------------
def check_mapping_candidates(registry: Registry, candidates: list[dict]) -> list[Issue]:
    """校验全部候选：target 存在（C4）、score∈[0,1]、level 与 classify(score) 自洽。"""
    issues: list[Issue] = []
    for row in candidates:
        issues.extend(_check_candidate_target(registry, row))
        issues.extend(_check_candidate_score(row))
    return issues


def _check_candidate_target(registry: Registry, row: dict) -> list[Issue]:
    """C4：object → 已注册对象类型；attribute → 某已注册对象的字段；link → 不入校验。"""
    kind = row.get("kind") or ""
    target = row.get("target") or ""
    cid = row.get("candidate_id") or "?"
    if kind == "object" and not registry.has_object_type(target):
        return [
            Issue(
                severity="error",
                code=GOV_CAND_UNKNOWN_TARGET,
                message=f"候选 {cid}: 对象 target {target} 未注册",
            )
        ]
    if kind == "attribute" and not any(
        target in o.model.model_fields for o in registry.object_types()
    ):
        return [
            Issue(
                severity="error",
                code=GOV_CAND_UNKNOWN_TARGET,
                message=f"候选 {cid}: 属性 target {target} 未注册",
            )
        ]
    return []


def _check_candidate_score(row: dict) -> list[Issue]:
    """score∈[0,1]（error）；level 与 classify(score) 自洽（warning——阈值可校准，C2）。"""
    cid = row.get("candidate_id") or "?"
    score = row.get("confidence_score")
    level = row.get("confidence_level")
    if score is None:
        return []
    try:
        score_val = float(score)
    except (TypeError, ValueError):
        return [
            Issue(
                severity="error",
                code=GOV_CAND_SCORE_OUT_OF_RANGE,
                message=f"候选 {cid}: score={score} 非数值",
            )
        ]
    if not 0.0 <= score_val <= 1.0:
        return [
            Issue(
                severity="error",
                code=GOV_CAND_SCORE_OUT_OF_RANGE,
                message=f"候选 {cid}: score={score} 超出 [0,1]",
            )
        ]
    if level and classify(score_val) != level:
        return [
            Issue(
                severity="warning",
                code=GOV_CAND_LEVEL_INCONSISTENT,
                message=f"候选 {cid}: level={level} ≠ classify({score_val})",
            )
        ]
    return []


# ----------------------------------------------------------------------
# store 全量扫描 + 挂载（des_self_checks 先例）
# ----------------------------------------------------------------------
def _load_from_store(store: Store) -> dict:
    """从治理段表全量扫描行（表不存在则跳过，防未 migrate 库误报）。"""
    conn = store.ontology_conn()
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        out: dict[str, list[dict]] = {"policies": [], "roles": [], "candidates": []}
        if "permission_policies" in tables:
            out["policies"] = [
                dict(r) for r in conn.execute("SELECT * FROM permission_policies").fetchall()
            ]
        if "permission_roles" in tables:
            out["roles"] = [
                dict(r) for r in conn.execute("SELECT * FROM permission_roles").fetchall()
            ]
        if "mapping_candidates" in tables:
            out["candidates"] = [
                dict(r) for r in conn.execute("SELECT * FROM mapping_candidates").fetchall()
            ]
        return out
    finally:
        conn.close()


def governance_self_checks(store: Store | None = None) -> GovernanceCheckFn:
    """返回挂载函数 fn(registry, instance_data=None) -> list[Issue]（des_self_checks 签名）。

    - instance_data 提供治理段行数据时用行数据校验（KEY_POLICIES/KEY_ROLES/KEY_CANDIDATES）；
    - 无 instance_data 时从 store 全量扫描治理段表（store 为 None 则返回空，不误报）。
    """

    def check(
        registry: Registry,
        instance_data: dict[str, list[dict[str, Any]]] | None = None,
    ) -> list[Issue]:
        if instance_data is not None:
            roles = {r.get("role_id", ""): r for r in instance_data.get(KEY_ROLES, [])}
            policies = instance_data.get(KEY_POLICIES, [])
            candidates = instance_data.get(KEY_CANDIDATES, [])
        elif store is not None:
            rows = _load_from_store(store)
            roles = {r.get("role_id", ""): r for r in rows["roles"]}
            policies = rows["policies"]
            candidates = rows["candidates"]
        else:
            return []
        issues = check_permission_policies(registry, policies, roles)
        issues.extend(check_mapping_candidates(registry, candidates))
        return issues

    return check


def mount_governance_checks(registry: Registry, store: Store | None = None) -> None:
    """把 GovernanceValidator 挂到 registry.self_check 扩展点（des_self_checks 先例）。"""
    registry.add_self_check(governance_self_checks(store))


__all__ = [
    "GOV_CAND_LEVEL_INCONSISTENT",
    "GOV_CAND_SCORE_OUT_OF_RANGE",
    "GOV_CAND_UNKNOWN_TARGET",
    "GOV_POLICY_APPROVE_NOT_HUMAN",
    "GOV_POLICY_BAD_EFFECT",
    "GOV_POLICY_BAD_OPERATION",
    "GOV_POLICY_BAD_SCOPE",
    "GOV_POLICY_BAD_SUBJECT_KIND",
    "GOV_POLICY_UNKNOWN_ATTRIBUTE",
    "GOV_POLICY_UNKNOWN_OBJECT",
    "KEY_CANDIDATES",
    "KEY_POLICIES",
    "KEY_ROLES",
    "check_mapping_candidates",
    "check_permission_policies",
    "governance_self_checks",
    "mount_governance_checks",
]
