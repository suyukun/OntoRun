"""LLM/Agent 接入层（波 3 AI 角色，技术方案 §5）。

- provider.py：LLM provider 热插拔（DeepSeek / Mock，工厂 + 环境变量切换，A1）；
- tools_generator.py：本体 schema → OpenAI function-calling tools（A2）；
- agent.py：意图→动作→回填→回复编排 + 高风险双签 + guard（A3）。
"""

from src.agent.agent import Agent, AgentTurn, ToolResult, build_system_prompt
from src.agent.provider import (
    ChatMessage,
    ChatResponse,
    DeepSeekProvider,
    MockProvider,
    ToolCall,
    get_provider,
)
from src.agent.tools_generator import READ_TOOL_NAME, build_tool_map, build_tools

__all__ = [
    "READ_TOOL_NAME",
    "Agent",
    "AgentTurn",
    "ChatMessage",
    "ChatResponse",
    "DeepSeekProvider",
    "MockProvider",
    "ToolCall",
    "ToolResult",
    "build_system_prompt",
    "build_tool_map",
    "build_tools",
    "get_provider",
]
