"""LLM Provider 热插拔（A1，技术方案 §5.1）。

- LLMProvider：协议（chat 接口，SDK 无关）——上层 agent 只依赖此协议；
- ChatMessage / ToolCall / ChatResponse：Agent 层值对象（与具体 SDK 解耦，
  换 provider 不动业务代码）；
- DeepSeekProvider：OpenAI 兼容 SDK（openai>=1.0，可直连 api.deepseek.com）；
  key/base_url/model 只从环境变量读取（DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL /
  DEEPSEEK_MODEL），绝不打印/提交/存对象属性（防泄密回归测试锚点）；
- MockProvider：无网可跑测试（不烧 token）——脚本化响应按序弹出、支持
  tool_calls 模拟、可挂 on_chat 回调供 guard 测试断言；
- 工厂注册表 PROVIDERS + get_provider()：.env LLM_PROVIDER=deepseek|mock 切换，
  切换只改环境变量不动业务代码（AGENTS.md 决策 4）。
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_PROVIDER = "deepseek"


class ToolCall(BaseModel):
    """LLM 提议的一次工具调用（name + 已解析的 JSON 参数）。"""

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """Agent 层消息（与 SDK 消息格式解耦，序列化由 provider 负责）。

    content 可为 None：assistant 携带 tool_calls 提议时无正文（OpenAI 兼容约束）。
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_call_id: str | None = None  # role=tool 时关联的调用
    tool_calls: list[ToolCall] | None = None  # role=assistant 时携带提议


class ChatResponse(BaseModel):
    """LLM 一次回复：自然语言内容和/或工具调用提议。"""

    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(Protocol):
    """Provider 协议（§5.1）：chat 一次完整对话往返。"""

    def chat(
        self, messages: list[ChatMessage], tools: list[dict] | None = None
    ) -> ChatResponse: ...


class DeepSeekProvider:
    """DeepSeek（OpenAI 兼容）provider：openai SDK 直连 api.deepseek.com。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "未设置 DEEPSEEK_API_KEY（key 只放环境变量，绝不进代码/提交）"
            )
        self.base_url = base_url or os.environ.get(
            "DEEPSEEK_BASE_URL", DEFAULT_BASE_URL
        )
        self.model = model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
        from openai import OpenAI  # 延迟导入：仅 DeepSeek 路径需要该依赖

        # key 只进 SDK client，不存为 provider 自身属性（防打印/序列化泄密）
        self._client = OpenAI(api_key=api_key, base_url=self.base_url)

    @property
    def api_key(self) -> str | None:
        """只读访问器（key 仅在 SDK client 内部，不落 provider 属性）。"""
        return getattr(self._client, "api_key", None)

    def chat(
        self, messages: list[ChatMessage], tools: list[dict] | None = None
    ) -> ChatResponse:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[_to_openai_message(m) for m in messages],
            tools=tools,
        )
        choice = resp.choices[0].message
        tool_calls: list[ToolCall] = []
        for tc in choice.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
        return ChatResponse(content=choice.content, tool_calls=tool_calls)


def _to_openai_message(m: ChatMessage) -> dict:
    """Agent 层消息 → OpenAI SDK 消息（assistant tool_calls / tool 关联转换）。"""
    d: dict[str, Any] = {"role": m.role}
    if m.content is not None:
        d["content"] = m.content
    if m.tool_call_id:
        d["tool_call_id"] = m.tool_call_id
    if m.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
            }
            for tc in m.tool_calls
        ]
    return d


class MockProvider:
    """脚本化 provider（不烧 token）：响应按序弹出，耗尽后返回 default_content。

    - 单测/A3 E2E：responses=[ChatResponse(tool_calls=[...]), ChatResponse(content=...)]
      模拟"提议工具调用 → 执行 → 回填 → 生成自然语言回复"两轮往返；
    - on_chat 回调：记录每次收到的 messages/tools（guard 测试断言系统提示词
      不拼用户自由文本、工具白名单等）。
    """

    def __init__(
        self,
        responses: list[ChatResponse] | None = None,
        default_content: str = "（MockProvider 兜底回复）",
        on_chat: Callable[[list[ChatMessage], list[dict] | None], None] | None = None,
    ) -> None:
        self._responses = list(responses or [])
        self._default = ChatResponse(content=default_content)
        self._on_chat = on_chat
        self.calls: list[tuple[list[ChatMessage], list[dict] | None]] = []

    def chat(
        self, messages: list[ChatMessage], tools: list[dict] | None = None
    ) -> ChatResponse:
        self.calls.append((messages, tools))
        if self._on_chat:
            self._on_chat(messages, tools)
        if self._responses:
            return self._responses.pop(0)
        return self._default


# 工厂注册表：名称 -> 零参工厂（新 provider 在此登记，切换只改环境变量）
PROVIDERS: dict[str, Callable[[], LLMProvider]] = {
    "deepseek": DeepSeekProvider,
    "mock": MockProvider,
}


def get_provider(name: str | None = None) -> LLMProvider:
    """按名称构造 provider；name 缺省读 LLM_PROVIDER 环境变量（deepseek|mock）。"""
    resolved = (
        (name or os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER)).strip().lower()
    )
    factory = PROVIDERS.get(resolved)
    if factory is None:
        raise ValueError(
            f"未知 LLM provider: {resolved}（可选: {', '.join(sorted(PROVIDERS))}）"
        )
    return factory()


__all__ = [
    "DEFAULT_PROVIDER",
    "PROVIDERS",
    "ChatMessage",
    "ChatResponse",
    "DeepSeekProvider",
    "LLMProvider",
    "MockProvider",
    "ToolCall",
    "get_provider",
]
