"""E3 七道校验器（蓝图 v0.3 §8 / 补丁 v0.3.1）。

四级严重度：fatal / error / warning / info。
P3 输出为 ValidationReport dataclass（汇总 + 列表 + 期望摘要），落到
extraction_tasks.validation_report_json。

V1 结构（fatal）：LLM 输出必须是合法 JSON 对象，含 entities / relations /
    logic_rules / actions 数组（可空）；其他顶层 key 视为 warning。
V2 必填（fatal）：实体 {name, type}；关系 {source, target, type}；动作 {name}。
V3 引用完整性（fatal）：关系两端必须指向存在的实体名；动作的 linked_logic /
    linked_entities 必须指向真实项。
V4 去重（error）：实体按 (name, type) 去重，重复 error；关系按
    (source, type, target) 去重，重复 warning。
V5 类型白名单（warning）：实体 type 不在预设域集合 -> warning；同时统计
    自定义率，超过 50% 视为 warning。
V6 语法（fatal）：动作 function_code 字段用 ast.parse 校验。
V7 语义引用（error）：linked_entities / linked_logic 指向真实存在的项；
    V3 已捕 fatal 重复 entity 情况；V7 处理 logic rule 引用 entities。
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

SEVERITY_ORDER = ("info", "warning", "error", "fatal")


@dataclass(frozen=True)
class Issue:
    validator: str
    severity: str  # info / warning / error / fatal
    message: str
    target: str = ""  # 关联实体/关系/动作名


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[Issue, ...] = field(default_factory=tuple)
    counts_by_severity: dict[str, int] = field(default_factory=dict)
    summary: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "issues": [
                {
                    "validator": i.validator,
                    "severity": i.severity,
                    "message": i.message,
                    **({"target": i.target} if i.target else {}),
                }
                for i in self.issues
            ],
            "counts_by_severity": self.counts_by_severity,
            "summary": self.summary,
        }

    @property
    def has_fatal(self) -> bool:
        return self.counts_by_severity.get("fatal", 0) > 0

    @property
    def has_error(self) -> bool:
        return self.counts_by_severity.get("error", 0) > 0


def _index_by(items: Iterable[dict], key: str) -> dict[Any, list[dict]]:
    out: dict[Any, list[dict]] = {}
    for it in items:
        out.setdefault(it.get(key), []).append(it)
    return out


def _count(issues: Iterable[Issue]) -> dict[str, int]:
    out: dict[str, int] = {s: 0 for s in SEVERITY_ORDER}
    for i in issues:
        out[i.severity] = out.get(i.severity, 0) + 1
    return out


# ----- V1 结构 -----


def v1_structure(payload: Any) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(payload, dict):
        issues.append(
            Issue("V1_structure", "fatal", "LLM 输出顶层必须为 JSON object")
        )
        return issues
    if "entities" not in payload:
        issues.append(
            Issue("V1_structure", "fatal", "LLM 输出缺 entities 数组（顶层 key）")
        )
    elif not isinstance(payload["entities"], list):
        issues.append(
            Issue("V1_structure", "fatal", "LLM 输出 entities 字段必须为 array")
        )
    for opt in ("relations", "logic_rules", "actions"):
        if opt in payload and not isinstance(payload[opt], list):
            issues.append(
                Issue("V1_structure", "fatal", f"{opt} 字段必须为 array")
            )
    return issues


# ----- V2 必填 -----


def v2_required_fields(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    for e in payload.get("entities") or []:
        if not isinstance(e, dict):
            issues.append(
                Issue("V2_required_fields", "fatal", "entity 不是 dict")
            )
            continue
        if not e.get("name") or not e.get("type"):
            issues.append(
                Issue(
                    "V2_required_fields",
                    "fatal",
                    f"实体缺 name 或 type: {e}",
                    target=str(e.get("name") or "?"),
                )
            )
    for r in payload.get("relations") or []:
        if not isinstance(r, dict):
            issues.append(
                Issue("V2_required_fields", "fatal", "relation 不是 dict")
            )
            continue
        if not (r.get("source") and r.get("target") and r.get("type")):
            issues.append(
                Issue(
                    "V2_required_fields",
                    "fatal",
                    f"关系缺 source/target/type: {r}",
                    target=str(r.get("source")) + "->" + str(r.get("target")),
                )
            )
    for a in payload.get("actions") or []:
        if not isinstance(a, dict):
            issues.append(
                Issue("V2_required_fields", "fatal", "action 不是 dict")
            )
            continue
        if not a.get("name"):
            issues.append(
                Issue(
                    "V2_required_fields",
                    "fatal",
                    f"动作缺 name: {a}",
                )
            )
    for lr in payload.get("logic_rules") or []:
        if not isinstance(lr, dict):
            issues.append(
                Issue("V2_required_fields", "fatal", "logic_rule 不是 dict")
            )
            continue
        if not lr.get("rule_id") or not lr.get("logic_type"):
            issues.append(
                Issue(
                    "V2_required_fields",
                    "fatal",
                    f"logic_rule 缺 rule_id 或 logic_type: {lr}",
                    target=str(lr.get("rule_id") or "?"),
                )
            )
    return issues


# ----- V3 引用完整性 -----


def v3_referential_integrity(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    entities = payload.get("entities") or []
    entity_names: set[str] = {
        e.get("name") for e in entities if isinstance(e, dict) and e.get("name")
    }
    logic_rule_ids: set[str] = {
        lr.get("rule_id")
        for lr in (payload.get("logic_rules") or [])
        if isinstance(lr, dict) and lr.get("rule_id")
    }
    for r in payload.get("relations") or []:
        if not isinstance(r, dict):
            continue
        if r.get("source") not in entity_names:
            issues.append(
                Issue(
                    "V3_referential_integrity",
                    "fatal",
                    f"关系 source={r.get('source')!r} 不在 entities 中",
                    target=str(r.get("source")) + "->" + str(r.get("target")),
                )
            )
        if r.get("target") not in entity_names:
            issues.append(
                Issue(
                    "V3_referential_integrity",
                    "fatal",
                    f"关系 target={r.get('target')!r} 不在 entities 中",
                    target=str(r.get("source")) + "->" + str(r.get("target")),
                )
            )
    for a in payload.get("actions") or []:
        if not isinstance(a, dict):
            continue
        for lr_ref in a.get("linked_logic") or []:
            if lr_ref not in logic_rule_ids:
                issues.append(
                    Issue(
                        "V3_referential_integrity",
                        "fatal",
                        f"linked_logic 引用了不存在的 {lr_ref!r}；本数据集 LR 集合为 {sorted(logic_rule_ids)}",
                        target=str(a.get("name")),
                    )
                )
        for e_ref in a.get("linked_entities") or []:
            if e_ref not in entity_names:
                issues.append(
                    Issue(
                        "V3_referential_integrity",
                        "fatal",
                        f"linked_entities 引用了不存在的 {e_ref!r}",
                        target=str(a.get("name")),
                    )
                )
    return issues


# ----- V4 去重 -----


def v4_dedup(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    e_seen: dict[tuple[str, str], int] = {}
    for e in payload.get("entities") or []:
        if not isinstance(e, dict) or not e.get("name") or not e.get("type"):
            continue
        k = (e["name"], e["type"])
        e_seen[k] = e_seen.get(k, 0) + 1
    for (name, t), n in e_seen.items():
        if n > 1:
            issues.append(
                Issue(
                    "V4_dedup",
                    "error",
                    f"实体 ({name}, {t}) 出现 {n} 次，必须按 (name,type) 去重保留首条",
                    target=name,
                )
            )
    r_seen: dict[tuple, int] = {}
    for r in payload.get("relations") or []:
        if not isinstance(r, dict) or not (r.get("source") and r.get("type") and r.get("target")):
            continue
        k = (r["source"], r["type"], r["target"])
        r_seen[k] = r_seen.get(k, 0) + 1
    for (s, t, tgt), n in r_seen.items():
        if n > 1:
            issues.append(
                Issue(
                    "V4_dedup",
                    "warning",
                    f"关系 ({s} -{t}-> {tgt}) 出现 {n} 次，按 (source,type,target) 去重",
                    target=s + "->" + tgt,
                )
            )
    return issues


# ----- V5 类型白名单 -----


def v5_type_whitelist(
    payload: dict, *, entity_types_whitelist: list[str]
) -> list[Issue]:
    issues: list[Issue] = []
    entities = payload.get("entities") or []
    if not entities:
        return issues
    whitelist = set(entity_types_whitelist or [])
    total = 0
    custom = 0
    for e in entities:
        if not isinstance(e, dict) or not e.get("type"):
            continue
        total += 1
        t = e["type"]
        if t not in whitelist:
            custom += 1
            issues.append(
                Issue(
                    "V5_type_whitelist",
                    "warning",
                    f"实体类型 {t!r} 不在预设白名单中；属自定义类型",
                    target=str(e.get("name") or "?"),
                )
            )
    if total > 0 and custom / total >= 0.5:
        issues.append(
            Issue(
                "V5_type_whitelist",
                "warning",
                f"自定义类型比例 {custom}/{total} >= 50%，建议重审 entity_types_whitelist",
            )
        )
    return issues


# ----- V6 语法 -----


def v6_syntax(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    for a in payload.get("actions") or []:
        if not isinstance(a, dict):
            continue
        code = a.get("function_code")
        if not code:
            # 无 function_code -> 跳过（MVP 不要求）
            continue
        if not isinstance(code, str):
            issues.append(
                Issue(
                    "V6_syntax",
                    "fatal",
                    f"action {a.get('name')!r} function_code 必须为字符串",
                    target=str(a.get("name")),
                )
            )
            continue
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                Issue(
                    "V6_syntax",
                    "fatal",
                    f"action {a.get('name')!r} function_code 语法错误: {e}",
                    target=str(a.get("name")),
                )
            )
    return issues


# ----- V7 语义引用 -----


def v7_semantic_reference(payload: dict) -> list[Issue]:
    issues: list[Issue] = []
    entities = payload.get("entities") or []
    entity_names: set[str] = {
        e.get("name") for e in entities if isinstance(e, dict) and e.get("name")
    }
    logic_rule_ids: set[str] = {
        lr.get("rule_id")
        for lr in (payload.get("logic_rules") or [])
        if isinstance(lr, dict) and lr.get("rule_id")
    }
    # 动作的 linked_logic / linked_entities 已在 V3 检查；V7 重点：logic_rule 引用
    # entities（如 mention_entities / scope 字段）。
    for lr in payload.get("logic_rules") or []:
        if not isinstance(lr, dict):
            continue
        for e_ref in lr.get("mention_entities") or []:
            if e_ref not in entity_names:
                issues.append(
                    Issue(
                        "V7_semantic_reference",
                        "error",
                        f"logic_rule {lr.get('rule_id')!r} mention_entities 引用了不存在的 {e_ref!r}",
                        target=str(lr.get("rule_id")),
                    )
                )
        for lr_ref in lr.get("linked_logic") or []:
            if lr_ref not in logic_rule_ids:
                issues.append(
                    Issue(
                        "V7_semantic_reference",
                        "error",
                        f"logic_rule {lr.get('rule_id')!r} linked_logic 引用了不存在的 {lr_ref!r}",
                        target=str(lr.get("rule_id")),
                    )
                )
    return issues


# ----------------------------------------------------------------------
# 汇总入口
# ----------------------------------------------------------------------


def run_all(
    payload: Any,
    *,
    entity_types_whitelist: list[str] | None = None,
) -> ValidationReport:
    """跑 V1-V7 全部校验器，汇总返回 ValidationReport。"""
    if not isinstance(payload, dict):
        # V1 fatal：尝试给出"无 entities"问题
        only_issue = Issue("V1_structure", "fatal", "LLM 输出顶层不是 JSON object")
        return ValidationReport(
            issues=(only_issue,),
            counts_by_severity={"fatal": 1, "error": 0, "warning": 0, "info": 0},
            summary={
                "V1_structure": "fail",
                "V2_required_fields": "pass",
                "V3_referential_integrity": "pass",
                "V4_dedup": "pass",
                "V5_type_whitelist": "pass",
                "V6_syntax": "pass",
                "V7_semantic_reference": "pass",
            },
        )
    issues: list[Issue] = []
    issues.extend(v1_structure(payload))
    issues.extend(v2_required_fields(payload))
    # 若 V1/V2 已 fatal，后续校验可能误报；V3/V4/V5 仍跑（让 review 看全量），
    # 严重度 fatal 在 counts 中已能区分
    issues.extend(v3_referential_integrity(payload))
    issues.extend(v4_dedup(payload))
    issues.extend(
        v5_type_whitelist(payload, entity_types_whitelist=entity_types_whitelist or [])
    )
    issues.extend(v6_syntax(payload))
    issues.extend(v7_semantic_reference(payload))
    counts = _count(issues)
    # summary：每道 pass/fail
    summary: dict[str, str] = {}
    for v in ("V1_structure", "V2_required_fields", "V3_referential_integrity",
              "V4_dedup", "V5_type_whitelist", "V6_syntax", "V7_semantic_reference"):
        v_issues = [i for i in issues if i.validator == v]
        if not v_issues:
            summary[v] = "pass"
        elif any(i.severity == "fatal" for i in v_issues):
            summary[v] = "fail (fatal)"
        elif any(i.severity == "error" for i in v_issues):
            summary[v] = "fail (error)"
        else:
            summary[v] = "warning"
    return ValidationReport(
        issues=tuple(issues),
        counts_by_severity=counts,
        summary=summary,
    )


__all__ = [
    "SEVERITY_ORDER",
    "Issue",
    "ValidationReport",
    "run_all",
    "v1_structure",
    "v2_required_fields",
    "v3_referential_integrity",
    "v4_dedup",
    "v5_type_whitelist",
    "v6_syntax",
    "v7_semantic_reference",
]
