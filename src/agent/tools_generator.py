"""工具生成器（A2，技术方案 §5.2）——本体 schema → OpenAI function-calling tools。

核心机制：每个动作 → 一个 function 工具；工具参数 = 动作参数的 JSON Schema
（由 Pydantic 模型自动导出）；外加 1 个只读查询工具（search_objects，供 LLM
获取上下文）。"一处定义，四处消费"（§3.2）：运行时索引 / API /meta/schema /
前端动态 UI / Agent 工具生成，全部来自同一 registry。

关键设计约束（结构性防注入 / 防 Action Sprawl，§5.2）：
1. 不给泛化 update/任意字段工具——LLM 只能通过 6 个业务动作改数据（D-T3）；
2. 只读工具只给 1 个（控制 tool 数量与 token 消耗）；
3. 动作描述含前置规则摘要（description 来自 ActionDef，让 LLM 一次说对）。
"""

from __future__ import annotations

from typing import Any

from src.ontology.registry import Registry

READ_TOOL_NAME = "search_objects"


def build_tools(registry: Registry) -> list[dict]:
    """由 registry 自动生成完整 tools 列表：6 动作工具 + 1 只读工具。"""
    tools: list[dict[str, Any]] = [_action_tool(a) for a in registry.actions()]
    tools.append(_read_tool(registry))
    return tools


def _action_tool(action: Any) -> dict:
    """动作 → function tool（参数 schema 直接映射动作 params_schema）。"""
    return {
        "type": "function",
        "function": {
            "name": action.name,
            "description": action.description,
            "parameters": action.params_model.model_json_schema(),
        },
    }


def _read_tool(registry: Registry) -> dict:
    """只读查询工具：按对象类型 + 可选等值过滤检索（LLM 上下文获取，不能改数据）。"""
    object_types = sorted(o.api_name for o in registry.object_types())
    return {
        "type": "function",
        "function": {
            "name": READ_TOOL_NAME,
            "description": (
                "只读查询：按对象类型与可选等值过滤检索对象（供 LLM 获取上下文，"
                "不修改任何数据）。对象类型见 object_type 枚举。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "object_type": {
                        "type": "string",
                        "enum": object_types,
                        "description": "对象类型 API 名",
                    },
                    "filter": {
                        "type": "object",
                        "description": "等值/枚举过滤（键=属性名，值=期望值；可省略）",
                    },
                    "page_size": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                        "description": "每页条数",
                    },
                },
                "required": ["object_type"],
            },
        },
    }


def build_tool_map(registry: Registry) -> dict[str, dict]:
    """name → 工具 dict（agent 白名单校验用）。"""
    return {t["function"]["name"]: t for t in build_tools(registry)}


__all__ = ["READ_TOOL_NAME", "build_tool_map", "build_tools"]
