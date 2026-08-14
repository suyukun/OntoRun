"""本体注册表（§3.2）——对象/链接/动作注册 + 启动自检。

对标 Palantir OMS / Ontology Manager（palantir §1.3 / §3.1，见附录 A）。
self_check 覆盖：主键唯一性、链接双向命名一致、动作参数完整、状态归属标注。
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel

from src.ontology.actions import CANONICAL_ERROR_CODES, ActionDef
from src.ontology.links import LinkTypeDef
from src.ontology.objects import (
    OWN_DERIVED,
    OWN_ONTOLOGY,
    OWN_SOURCE,
    ObjectTypeDef,
    field_ownership,
)

_API_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class Issue(BaseModel):
    """self_check 输出的问题条目。severity=error 视为不通过。"""

    severity: Literal["error", "warning"]
    code: str
    message: str


class Registry:
    """对象 / 链接 / 动作的统一注册表（schema 元数据单一来源，四处消费：运行时索引、
    API /meta/schema、前端动态 UI、Agent 工具生成——§3.2）。"""

    def __init__(self) -> None:
        self._objects: dict[str, ObjectTypeDef] = {}
        self._links: list[LinkTypeDef] = []
        self._actions: dict[str, ActionDef] = {}

    # ---- 注册（重复注册直接报错，防静默覆盖） ----
    def register_object_type(self, defn: ObjectTypeDef) -> None:
        if defn.name in self._objects:
            raise ValueError(f"对象类型重复注册: {defn.name}")
        self._objects[defn.name] = defn

    def register_link_type(self, defn: LinkTypeDef) -> None:
        self._links.append(defn)

    def register_action_type(self, defn: ActionDef) -> None:
        if defn.name in self._actions:
            raise ValueError(f"动作重复注册: {defn.name}")
        self._actions[defn.name] = defn

    # ---- 查询 ----
    def object_types(self) -> list[ObjectTypeDef]:
        return list(self._objects.values())

    def object_type(self, name: str) -> ObjectTypeDef:
        return self._objects[name]

    def link_types(self) -> list[LinkTypeDef]:
        return list(self._links)

    def actions(self) -> list[ActionDef]:
        return list(self._actions.values())

    def action(self, name: str) -> ActionDef:
        return self._actions[name]

    # ---- 启动自检（§3.2：主键唯一 / 链接双向命名 / 动作参数完整 / 状态归属标注） ----
    def self_check(self) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_objects())
        issues.extend(self._check_links())
        issues.extend(self._check_actions())
        return issues

    def _check_objects(self) -> list[Issue]:
        issues: list[Issue] = []
        for obj in self._objects.values():
            fields = obj.model.model_fields
            if obj.pk_field not in fields:
                issues.append(
                    Issue(
                        severity="error",
                        code="OBJECT_PK_MISSING",
                        message=f"{obj.name}: 主键字段 {obj.pk_field} 不存在",
                    )
                )
            title = obj.title_field or obj.pk_field
            if title not in fields:
                issues.append(
                    Issue(
                        severity="error",
                        code="OBJECT_TITLE_MISSING",
                        message=f"{obj.name}: Title 字段 {title} 不存在",
                    )
                )
            if not _API_NAME_RE.match(obj.api_name):
                issues.append(
                    Issue(
                        severity="error",
                        code="OBJECT_API_NAME_INVALID",
                        message=f"{obj.name}: api_name={obj.api_name} 非法",
                    )
                )
            if not obj.source_table:
                issues.append(
                    Issue(
                        severity="error",
                        code="OBJECT_NO_SOURCE_TABLE",
                        message=f"{obj.name}: 缺少源系统承载表",
                    )
                )
            for fname in fields:
                if field_ownership(obj.model, fname) not in (
                    OWN_SOURCE,
                    OWN_ONTOLOGY,
                    OWN_DERIVED,
                ):
                    issues.append(
                        Issue(
                            severity="error",
                            code="FIELD_MISSING_OWNERSHIP",
                            message=f"{obj.name}.{fname}: 缺少状态归属标注",
                        )
                    )
        return issues

    def _check_links(self) -> list[Issue]:
        issues: list[Issue] = []
        seen_names: set[str] = set()
        seen_inverse: set[str] = set()
        for link in self._links:
            if link.name in seen_names:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_NAME_DUPLICATE",
                        message=f"链接名重复: {link.name}",
                    )
                )
            seen_names.add(link.name)
            if link.inverse_name in seen_inverse:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_INVERSE_DUPLICATE",
                        message=f"反向名重复: {link.inverse_name}",
                    )
                )
            seen_inverse.add(link.inverse_name)
            if link.source_type not in self._objects:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_UNKNOWN_SOURCE",
                        message=f"{link.name}: 源类型 {link.source_type} 未注册",
                    )
                )
                continue
            if link.target_type not in self._objects:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_UNKNOWN_TARGET",
                        message=f"{link.name}: 目标类型 {link.target_type} 未注册",
                    )
                )
                continue
            if link.source_type == link.target_type:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_SELF_LOOP",
                        message=f"{link.name}: 不允许自环链接",
                    )
                )
            # 外键所在侧：N:1 → source；1:N → target
            fk_model = (
                self._objects[link.source_type].model
                if link.cardinality == "N:1"
                else self._objects[link.target_type].model
            )
            if link.fk_field not in fk_model.model_fields:
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_FK_MISSING",
                        message=f"{link.name}: 外键 {link.fk_field} 不在 "
                        f"{'source' if link.cardinality == 'N:1' else 'target'} 侧模型",
                    )
                )
            # 双向命名约定：反向名必须以目标类型 api_name 开头（如 order.customer ↔
            # customer.orders，§2.3 的复数/惯用名词由定义者掌握），且全局唯一
            prefix = f"{self._objects[link.target_type].api_name}."
            if not link.inverse_name.startswith(prefix):
                issues.append(
                    Issue(
                        severity="error",
                        code="LINK_INVERSE_MISMATCH",
                        message=f"{link.name}: inverse_name={link.inverse_name} "
                        f"必须以 {prefix} 开头（双向命名约定）",
                    )
                )
        return issues

    def _check_actions(self) -> list[Issue]:
        issues: list[Issue] = []
        # 对象字段归属索引：<Type>.<field> -> ownership（供效果引用校验）
        field_own: dict[str, str] = {}
        for obj in self._objects.values():
            for fname in obj.model.model_fields:
                own = field_ownership(obj.model, fname)
                if own in (OWN_SOURCE, OWN_ONTOLOGY, OWN_DERIVED):
                    field_own[f"{obj.name}.{fname}"] = own
        for action in self._actions.values():
            if not action.params_model.model_fields:
                issues.append(
                    Issue(
                        severity="error",
                        code="ACTION_NO_PARAMS",
                        message=f"{action.name}: 参数模型为空",
                    )
                )
            try:
                action.params_model.model_json_schema()
            except Exception as exc:  # noqa: BLE001 —— schema 导出失败即参数不完整
                issues.append(
                    Issue(
                        severity="error",
                        code="ACTION_PARAMS_SCHEMA_FAIL",
                        message=f"{action.name}: 参数 JSON Schema 导出失败: {exc}",
                    )
                )
            for code in action.error_codes:
                if code not in CANONICAL_ERROR_CODES:
                    issues.append(
                        Issue(
                            severity="error",
                            code="ACTION_ERROR_CODE_UNKNOWN",
                            message=f"{action.name}: 错误码 {code} 不在 §4.3 全集",
                        )
                    )
            for pc in action.preconditions:
                if pc.error_code not in CANONICAL_ERROR_CODES:
                    issues.append(
                        Issue(
                            severity="error",
                            code="ACTION_PRECONDITION_UNKNOWN",
                            message=f"{action.name}: 前置规则错误码 {pc.error_code} 不在全集",
                        )
                    )
                if pc.error_code not in action.error_codes:
                    issues.append(
                        Issue(
                            severity="error",
                            code="ACTION_PRECONDITION_UNDECLARED",
                            message=f"{action.name}: 前置规则 {pc.error_code} 未在 error_codes 声明",
                        )
                    )
            eff = action.state_effects
            if not (eff.source_backed or eff.ontology_owned):
                issues.append(
                    Issue(
                        severity="error",
                        code="ACTION_NO_EFFECTS",
                        message=f"{action.name}: 无任何状态效果",
                    )
                )
            for field, expected_own in ((f, OWN_SOURCE) for f in eff.source_backed):
                self._check_effect_field(issues, action, field, expected_own, field_own)
            for field in eff.ontology_owned:
                self._check_effect_field(issues, action, field, OWN_ONTOLOGY, field_own)
            for field in eff.derived:
                self._check_effect_field(issues, action, field, OWN_DERIVED, field_own)
        return issues

    @staticmethod
    def _check_effect_field(
        issues: list[Issue],
        action: ActionDef,
        field: str,
        expected_own: str,
        field_own: dict[str, str],
    ) -> None:
        if field not in field_own:
            issues.append(
                Issue(
                    severity="error",
                    code="ACTION_EFFECT_UNKNOWN_FIELD",
                    message=f"{action.name}: 效果字段 {field} 不存在于任何对象",
                )
            )
        elif field_own[field] != expected_own:
            issues.append(
                Issue(
                    severity="error",
                    code="ACTION_EFFECT_OWNERSHIP_MISMATCH",
                    message=f"{action.name}: 效果字段 {field} 归属为 "
                    f"{field_own[field]}，标注为 {expected_own}",
                )
            )
