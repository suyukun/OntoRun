"""逻辑规则真实推导（蓝图 v0.3 §1.1-E4 弃疗项 3 / §10 决策 1.1.3 / P4-T1）。

核心承诺：**禁模板化**——规则内容必须来自真实 schema 数据；不同 schema
推导出不同规则；无约束 schema 不产规则。不硬塞固定条数。

推导来源 = 已发布 object_types 行的 property_schema（JSON Schema 子集）：
- required 字段            -> precondition 规则（kind=required）
- enum 字段                -> invariant 取值域规则（kind=enum_domain）
- 数值边界 minimum/maximum  -> threshold 范围规则（kind=range）
- status 类 enum 字段       -> state_machine 合法流转规则（kind=state_transitions），
  流转仅从字段/对象描述中的箭头链（A->B / A/B->C）解析，且两端必须都在
  enum 值域内（不凭空造）；解析不出流转链则不产 state_machine 规则。

expression 是结构化、可机器执行的 JSON（非自然语言文本）：
  {"kind": ..., "object_type": ..., "field": ..., ...kind 专属字段}
evaluate_expression / evaluate_transition 提供机器执行（submission_criteria
引用与 dry_run 证据计算共用）。
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Any

from src.builder.logic import rules_repo
from src.builder.object_types import ObjectTypeRow, list_published

# status 语义字段名（含常见变体；不含凭空扩展）
_STATUS_FIELD_NAMES = frozenset({"status", "state"})
_STATUS_FIELD_SUFFIXES = ("_status", "_state")

# 箭头链分隔符（中英文箭头；"/" 表示多源态）
_ARROW_SPLIT_RE = re.compile(r"(?:->|→|➜)")
# 提取形如 "pending->confirmed->shipped" 或 "pending/confirmed -> cancelled" 的片段
_SEGMENT_RE = re.compile(
    r"[\w]+(?:\s*/\s*[\w]+)*(?:\s*(?:->|→|➜)\s*[\w]+(?:\s*/\s*[\w]+)*)+"
)

KIND_REQUIRED = "required"
KIND_ENUM_DOMAIN = "enum_domain"
KIND_RANGE = "range"
KIND_STATE_TRANSITIONS = "state_transitions"
KNOWN_KINDS = frozenset(
    {KIND_REQUIRED, KIND_ENUM_DOMAIN, KIND_RANGE, KIND_STATE_TRANSITIONS}
)

_NUMERIC_BOUND_KEYS = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum")


@dataclass(frozen=True)
class DerivedRule:
    """一条推导产物（落库前的纯数据形态）。"""

    name: str
    logic_type: str
    expression: dict
    severity: str


# ----------------------------------------------------------------------
# 解析工具
# ----------------------------------------------------------------------


def is_status_like(field_name: str) -> bool:
    """字段名是否具有状态语义（status/state/x_status/x_state）。"""
    if field_name in _STATUS_FIELD_NAMES:
        return True
    return field_name.endswith(_STATUS_FIELD_SUFFIXES)


def parse_transition_chain(text: str, states: list) -> list[tuple[str, str]]:
    """从描述文本解析合法流转对；仅保留两端都在 states 内的（不凭空造）。

    支持形态："A->B->C"（链式，取相邻对）、"A/B->C"（多源态）。
    """
    state_set = {str(s) for s in states}
    transitions: list[tuple[str, str]] = []
    for seg in _SEGMENT_RE.finditer(text or ""):
        parts = [
            [a.strip() for a in p.split("/") if a.strip()]
            for p in _ARROW_SPLIT_RE.split(seg.group(0))
        ]
        for i in range(len(parts) - 1):
            for src in parts[i]:
                for dst in parts[i + 1]:
                    if src in state_set and dst in state_set and src != dst:
                        pair = (src, dst)
                        if pair not in transitions:
                            transitions.append(pair)
    return transitions


def _field_enum(prop: dict) -> list | None:
    values = prop.get("enum")
    if isinstance(values, list) and values:
        return values
    return None


def _numeric_bounds(prop: dict) -> dict:
    bounds = {k: prop[k] for k in _NUMERIC_BOUND_KEYS if k in prop}
    return bounds if bounds else {}


def _derive_state_machine(
    object_type: str, field: str, prop: dict, schema: dict, row_desc: str
) -> DerivedRule | None:
    """状态机规则：enum 值域 + 描述中的流转链；链解析不出 -> None（不凭空造）。"""
    states = _field_enum(prop)
    if states is None or not is_status_like(field):
        return None
    candidates = [
        prop.get("description") or "",
        schema.get("description") or "",
        row_desc or "",
    ]
    transitions: list[tuple[str, str]] = []
    for text in candidates:
        transitions = parse_transition_chain(text, states)
        if transitions:
            break
    if not transitions:
        return None
    return DerivedRule(
        name=f"{object_type}.{field}_state_machine",
        logic_type="state_machine",
        expression={
            "kind": KIND_STATE_TRANSITIONS,
            "object_type": object_type,
            "field": field,
            "states": [str(s) for s in states],
            "transitions": [list(t) for t in transitions],
            "source": "property_description",
        },
        severity="error",
    )


def derive_rules_from_schema(row: ObjectTypeRow) -> list[DerivedRule]:
    """从单个 object_type 行的 property_schema 推导规则（纯函数，不落库）。

    规则条数完全由 schema 约束决定（反模板化）：无约束 -> 空列表。
    """
    schema = row.property_schema or {}
    properties = schema.get("properties") or {}
    if not isinstance(properties, dict):
        return []
    required = schema.get("required") or []
    if not isinstance(required, list):
        required = []
    rules: list[DerivedRule] = []

    for field in required:
        if str(field) not in properties:
            continue
        rules.append(
            DerivedRule(
                name=f"{row.name}.{field}_required",
                logic_type="precondition",
                expression={
                    "kind": KIND_REQUIRED,
                    "object_type": row.name,
                    "field": str(field),
                },
                severity="error",
            )
        )

    for field, prop in properties.items():
        prop = prop if isinstance(prop, dict) else {}
        enum_values = _field_enum(prop)
        if enum_values is not None:
            rules.append(
                DerivedRule(
                    name=f"{row.name}.{field}_enum_domain",
                    logic_type="invariant",
                    expression={
                        "kind": KIND_ENUM_DOMAIN,
                        "object_type": row.name,
                        "field": str(field),
                        "values": enum_values,
                    },
                    severity="error",
                )
            )
        bounds = _numeric_bounds(prop)
        if bounds:
            rules.append(
                DerivedRule(
                    name=f"{row.name}.{field}_range",
                    logic_type="threshold",
                    expression={
                        "kind": KIND_RANGE,
                        "object_type": row.name,
                        "field": str(field),
                        **bounds,
                    },
                    severity="warning",
                )
            )
        state_rule = _derive_state_machine(
            row.name, str(field), prop, schema, row.description
        )
        if state_rule is not None:
            rules.append(state_rule)
    return rules


# ----------------------------------------------------------------------
# 落库编排（幂等：同名同 expression 跳过）
# ----------------------------------------------------------------------


def discover_rules(
    conn: sqlite3.Connection,
    *,
    object_type_ref: str | None = None,
    ontology_id: str = "default",
) -> dict:
    """对指定（或全部）已发布 object_types 推导并落库 draft 规则。

    返回 {"discovered", "created", "skipped_existing", "object_types_scanned",
    "rules"}；同名同 expression 已存在（任意状态）则跳过（幂等）。
    """
    published = list_published(conn)
    if object_type_ref is not None:
        rows = [
            r for r in published if r.id == object_type_ref or r.name == object_type_ref
        ]
        if not rows:
            return {"error": "not_found_or_not_published"}
    else:
        rows = published

    created: list[dict] = []
    skipped = 0
    discovered = 0
    for row in rows:
        for derived in derive_rules_from_schema(row):
            discovered += 1
            existing = rules_repo.find_same_expression(
                conn, derived.name, derived.expression
            )
            if existing is not None:
                skipped += 1
                continue
            saved = rules_repo.create(
                conn,
                ontology_id=ontology_id,
                name=derived.name,
                logic_type=derived.logic_type,
                expression=derived.expression,
                severity=derived.severity,
            )
            created.append(rules_repo.row_to_dict(saved))
    return {
        "discovered": discovered,
        "created": len(created),
        "skipped_existing": skipped,
        "object_types_scanned": [r.name for r in rows],
        "rules": created,
    }


# ----------------------------------------------------------------------
# 表达式校验与机器执行
# ----------------------------------------------------------------------


def validate_expression(expression: Any) -> str | None:
    """结构校验（publish 前置）；合法返回 None，否则返回错误信息。"""
    if not isinstance(expression, dict):
        return "expression 必须为 JSON object"
    kind = expression.get("kind")
    if kind not in KNOWN_KINDS:
        return f"expression.kind 非法: {kind}（可选 {sorted(KNOWN_KINDS)}）"
    if not isinstance(expression.get("object_type"), str) or not expression.get(
        "object_type"
    ):
        return "expression.object_type 必须为非空字符串"
    if not isinstance(expression.get("field"), str) or not expression.get("field"):
        return "expression.field 必须为非空字符串"
    if kind == KIND_ENUM_DOMAIN:
        values = expression.get("values")
        if not isinstance(values, list) or not values:
            return "enum_domain.values 必须为非空列表"
    if kind == KIND_RANGE:
        bounds = {k: expression.get(k) for k in _NUMERIC_BOUND_KEYS}
        if not any(v is not None for v in bounds.values()):
            return (
                "range 至少需要 minimum/maximum/exclusiveMinimum/exclusiveMaximum 之一"
            )
    if kind == KIND_STATE_TRANSITIONS:
        states = expression.get("states")
        if not isinstance(states, list) or not states:
            return "state_transitions.states 必须为非空列表"
        transitions = expression.get("transitions")
        if not isinstance(transitions, list) or not transitions:
            return "state_transitions.transitions 必须为非空列表"
        state_set = {str(s) for s in states}
        for t in transitions:
            if not (isinstance(t, (list, tuple)) and len(t) == 2):
                return f"transition 必须为 [from, to]: {t}"
            if str(t[0]) not in state_set or str(t[1]) not in state_set:
                return f"transition 端点不在 states 内: {t}"
    return None


def evaluate_expression(expression: dict, record: dict) -> tuple[bool, dict | None]:
    """机器执行：对一条记录求值表达式（record = 对象字段 dict）。

    返回 (passed, violation)；state_transitions 对 record 求值 =
    当前值在 states 值域内（流转合法性用 evaluate_transition）。
    """
    kind = expression.get("kind")
    field = expression.get("field")
    value = record.get(field)
    if kind == KIND_REQUIRED:
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, {"field": field, "reason": "missing"}
        return True, None
    if kind == KIND_ENUM_DOMAIN:
        if value not in (expression.get("values") or []):
            return False, {"field": field, "value": value, "reason": "not_in_domain"}
        return True, None
    if kind == KIND_RANGE:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, {"field": field, "value": value, "reason": "not_numeric"}
        minimum = expression.get("minimum")
        maximum = expression.get("maximum")
        if minimum is not None and value < minimum:
            return False, {"field": field, "value": value, "reason": "below_minimum"}
        if maximum is not None and value > maximum:
            return False, {"field": field, "value": value, "reason": "above_maximum"}
        return True, None
    if kind == KIND_STATE_TRANSITIONS:
        if value not in (expression.get("states") or []):
            return False, {"field": field, "value": value, "reason": "unknown_state"}
        return True, None
    return False, {"reason": f"unknown kind: {kind}"}


def evaluate_transition(expression: dict, from_state: str, to_state: str) -> bool:
    """状态机流转合法性：from->to 是否在合法流转表内。"""
    transitions = {
        (str(t[0]), str(t[1]))
        for t in (expression.get("transitions") or [])
        if isinstance(t, (list, tuple)) and len(t) == 2
    }
    return (str(from_state), str(to_state)) in transitions


__all__ = [
    "KNOWN_KINDS",
    "DerivedRule",
    "derive_rules_from_schema",
    "discover_rules",
    "evaluate_expression",
    "evaluate_transition",
    "is_status_like",
    "parse_transition_chain",
    "validate_expression",
]
