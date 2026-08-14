"""A1 验收测试：LLM provider 热插拔（技术方案 §5.1）。

验收点：
- MockProvider 对话单测绿（不烧 token）：脚本化响应 / tool_calls 模拟 / 耗尽回退；
- DeepSeekProvider：key 只从环境变量读取（绝不打印/提交），缺失 key 快速失败；
- 工厂注册表 get_provider + LLM_PROVIDER 环境变量切换生效（deepseek|mock）；
- Agent 层值对象（ChatMessage/ToolCall/ChatResponse）与 SDK 解耦。
"""

import pytest

from src.agent.provider import (
    ChatMessage,
    ChatResponse,
    DeepSeekProvider,
    MockProvider,
    ToolCall,
    get_provider,
)

# ======================================================================
# MockProvider：无网可跑、不烧 token
# ======================================================================


def test_mock_returns_scripted_content():
    p = MockProvider(responses=[ChatResponse(content="好的，已处理")])
    resp = p.chat([ChatMessage(role="user", content="你好")])
    assert resp.content == "好的，已处理"
    assert resp.tool_calls == []


def test_mock_returns_default_when_exhausted():
    p = MockProvider(
        responses=[ChatResponse(content="第一条")], default_content="兜底回复"
    )
    assert p.chat([]).content == "第一条"
    assert p.chat([]).content == "兜底回复"
    assert p.chat([]).content == "兜底回复"


def test_mock_tool_calls_roundtrip():
    p = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="cancel_order",
                        arguments={"order_id": "ORD-1001"},
                    )
                ]
            )
        ]
    )
    resp = p.chat([ChatMessage(role="user", content="取消 ORD-1001")])
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "cancel_order"
    assert resp.tool_calls[0].arguments == {"order_id": "ORD-1001"}


def test_mock_records_messages_and_tools():
    seen = {}

    def on_chat(messages, tools):
        seen["messages"] = messages
        seen["tools"] = tools

    p = MockProvider(on_chat=on_chat)
    p.chat([ChatMessage(role="user", content="hi")], tools=[{"type": "function"}])
    assert seen["messages"][0].content == "hi"
    assert seen["tools"] == [{"type": "function"}]


# ======================================================================
# 工厂注册表 + 环境变量切换（验收：切换生效）
# ======================================================================


def test_get_provider_mock_by_name():
    assert isinstance(get_provider("mock"), MockProvider)


def test_get_provider_env_switch_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    assert isinstance(get_provider(), MockProvider)


def test_get_provider_env_switch_deepseek(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")
    assert isinstance(get_provider(), DeepSeekProvider)


def test_get_provider_unknown_raises():
    with pytest.raises(ValueError):
        get_provider("gpt-unknown")


def test_get_provider_missing_key_raises(monkeypatch):
    """DeepSeek 缺 key 必须快速失败（key 只放环境变量，绝不进代码）。"""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_provider("deepseek")


# ======================================================================
# DeepSeekProvider：环境变量读取（不烧 token，不联网）
# ======================================================================


def test_deepseek_reads_env_defaults(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")
    p = DeepSeekProvider()
    assert p.model == "deepseek-chat"  # DEEPSEEK_MODEL 未设置时默认
    assert p.base_url == "https://api.deepseek.com"  # DEEPSEEK_BASE_URL 未设置时默认


def test_deepseek_reads_env_overrides(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://gateway.example.com/v1")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    p = DeepSeekProvider()
    assert p.model == "deepseek-reasoner"
    assert p.base_url == "https://gateway.example.com/v1"


def test_deepseek_missing_key_raises(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ValueError):
        DeepSeekProvider()


def test_deepseek_never_exposes_key_in_attributes(monkeypatch):
    """防回归：provider 对象上不保留明文 key 属性（打印/序列化不泄密）。"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret-abc")
    p = DeepSeekProvider()
    attrs = {k: v for k, v in vars(p).items()}
    assert not any("sk-test-secret" in str(v) for v in attrs.values())
    assert "api_key" not in attrs and "key" not in attrs


# ======================================================================
# Agent 层值对象（与 SDK 解耦）
# ======================================================================


def test_chat_message_tool_message_shape():
    m = ChatMessage(role="tool", content='{"outcome":"applied"}', tool_call_id="call_1")
    dumped = m.model_dump(exclude_none=True)
    assert dumped["role"] == "tool" and dumped["tool_call_id"] == "call_1"


def test_tool_call_arguments_must_be_dict():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ToolCall(id="c1", name="x", arguments="not-a-dict")
