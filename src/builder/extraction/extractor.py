"""E3 LLM 提取器（蓝图 v0.3 §8 / 补丁 v0.3.1）。

输入：MD/PDF/DOCX 文本（经 md_to_struct 产出）+ provider（src.agent.provider）。
输出：entities / relations / logic_rules / actions JSON 数组 + 七道校验报告。

设计：
  - 真实 prompt 构造（system 固定 + user 拼文本 + 严格 JSON 模式提示）。
  - provider 优先用 MockProvider（不烧 token），DeepSeek 走 DEEPSEEK_API_KEY 真调用。
  - 期望 schema（entity_types_whitelist / relation_types_whitelist 等）作为
    provider 的 tool description 一并下发。
  - 解析：从 ChatResponse.content 抽 JSON；解析失败 -> V1 fatal。
  - 输出：归一（lower type / strip type 空白）+ DTO dataclass。

P3 简化：fallback 行为（Mock 未挂响应 + content 不是 JSON）= 把 content
原样塞到 entities 数组外层 kind=raw_text 标记，由校验器判 V1 fatal。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from src.agent.provider import ChatMessage, MockProvider
from src.builder.extraction.validators import ValidationReport, run_all

EXTRACTION_SYSTEM_PROMPT = """你是 OntoRun 业务本体构建子系统的 LLM 提取器。
任务：从输入的零售供应链业务文档（中文/英文混合）中抽取本体元素，输出
严格 JSON（不带代码围栏；不含其它文字）。

输出顶层字段：
  entities: 实体列表
  relations: 关系列表
  logic_rules: 业务逻辑规则列表
  actions: 动作类型列表

每条 entity 必含 name + type；type 取自 entity_types_whitelist。
relation 必含 source + type + target；type 取自 relation_types_whitelist。
logic_rule 必含 rule_id + name + logic_type + expression + severity。
action 必含 name + action_type + parameters（list）+ linked_logic（list）。

严禁：编造 rule_id；关系两端必须指向已抽取实体；动作 linked_logic 必须
指向已抽取的 logic rule。"""

EXTRACTION_USER_TEMPLATE = """文档来源：{source_path}
字符数：{char_count}（含中文 {zh_count}）

【实体类型白名单 entity_types_whitelist】
{entity_types_whitelist}

【关系类型白名单 relation_types_whitelist】
{relation_types_whitelist}

【逻辑规则类型 logic_rule_patterns】
{logic_rule_patterns}

【动作类型白名单 action_types】
{action_types}

【文档正文（已 md_to_struct 结构化）】
{body}

请只输出 JSON，遵循上述 schema。"""


@dataclass(frozen=True)
class ExtractionPayload:
    entities: list = field(default_factory=list)
    relations: list = field(default_factory=list)
    logic_rules: list = field(default_factory=list)
    actions: list = field(default_factory=list)

    def as_dict(self):
        return {
            "entities": self.entities,
            "relations": self.relations,
            "logic_rules": self.logic_rules,
            "actions": self.actions,
        }

    @classmethod
    def from_raw(cls, raw):
        if isinstance(raw, cls):
            return raw
        if not isinstance(raw, dict):
            return cls()
        return cls(
            entities=[e for e in (raw.get("entities") or []) if isinstance(e, dict)],
            relations=[r for r in (raw.get("relations") or []) if isinstance(r, dict)],
            logic_rules=[lr for lr in (raw.get("logic_rules") or []) if isinstance(lr, dict)],
            actions=[a for a in (raw.get("actions") or []) if isinstance(a, dict)],
        )


@dataclass(frozen=True)
class ExtractionResult:
    payload: ExtractionPayload
    validation_report: ValidationReport
    provider: str
    source_path: str
    raw_response: str = ""

    def as_dict(self):
        return {
            "payload": self.payload.as_dict(),
            "validation_report": self.validation_report.as_dict(),
            "provider": self.provider,
            "source_path": self.source_path,
            "raw_response": self.raw_response,
        }


# ----------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------

_FENCED_RE = re.compile(r"^\s*`{3}(?:json)?\s*|`{3}\s*$", re.MULTILINE)


def _extract_json(text):
    if not text:
        return ""
    t = text.strip()
    t = _FENCED_RE.sub("", t).strip()
    if t.startswith("{") and t.endswith("}"):
        return t
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return t[start: end + 1]


def _safe_json_loads(text):
    try:
        obj = json.loads(text)
    except (TypeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _provider_name(provider):
    if isinstance(provider, MockProvider):
        return "mock"
    return type(provider).__name__.lower()


def _char_counts(text):
    return len(text), sum(1 for c in text if "\u4e00" <= c <= "\u9fff")


# ----------------------------------------------------------------------
# 主入口
# ----------------------------------------------------------------------


def extract_from_text(
    text,
    *,
    provider,
    source_path="",
    schema=None,
):
    schema = schema or {}
    entity_types_whitelist = schema.get("entity_types_whitelist", [])
    relation_types_whitelist = schema.get("relation_types_whitelist", [])
    logic_rule_patterns = schema.get("logic_rule_patterns", [])
    action_types = schema.get("action_types", [])
    char_count, zh_count = _char_counts(text)
    user_text = EXTRACTION_USER_TEMPLATE.format(
        source_path=source_path or "(inline)",
        char_count=char_count,
        zh_count=zh_count,
        entity_types_whitelist=", ".join(entity_types_whitelist) or "(无)",
        relation_types_whitelist=", ".join(relation_types_whitelist) or "(无)",
        logic_rule_patterns=", ".join(logic_rule_patterns) or "(无)",
        action_types=", ".join(action_types) or "(无)",
        body=text[:8000],
    )
    messages = [
        ChatMessage(role="system", content=EXTRACTION_SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_text),
    ]
    response = provider.chat(messages)
    raw_text = response.content or ""
    json_text = _extract_json(raw_text)
    payload_obj = _safe_json_loads(json_text) if json_text else None
    if payload_obj is None:
        # 解析失败：直接调 validators 报 V1 fatal（不要构造空 dict 走通）
        report = run_all(None, entity_types_whitelist=entity_types_whitelist)
        return ExtractionResult(
            payload=ExtractionPayload(),
            validation_report=report,
            provider=_provider_name(provider),
            source_path=source_path or "(inline)",
            raw_response=raw_text,
        )
    payload = ExtractionPayload.from_raw(payload_obj)
    report = run_all(
        payload.as_dict(),
        entity_types_whitelist=entity_types_whitelist,
    )
    return ExtractionResult(
        payload=payload,
        validation_report=report,
        provider=_provider_name(provider),
        source_path=source_path or "(inline)",
        raw_response=raw_text,
    )


__all__ = [
    "EXTRACTION_SYSTEM_PROMPT",
    "EXTRACTION_USER_TEMPLATE",
    "ExtractionPayload",
    "ExtractionResult",
    "extract_from_text",
]
