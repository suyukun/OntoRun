"""DeepSeekProvider 序列化/映射单测（stub client，不联网不烧 token）。"""

from types import SimpleNamespace

from src.agent.provider import (
    ChatMessage,
    DeepSeekProvider,
    ToolCall,
    _to_openai_message,
)


def _stub_client(payloads: list[dict]) -> SimpleNamespace:
    """极简 OpenAI 兼容 stub：chat.completions.create 返回脚本化 choice。"""

    class Completions:
        def __init__(self):
            self._i = 0

        def create(self, **kwargs):
            p = payloads[self._i % len(payloads)]
            self._i += 1
            tc = [
                SimpleNamespace(
                    id=t["id"],
                    function=SimpleNamespace(name=t["name"], arguments=t["arguments"]),
                )
                for t in p.get("tool_calls", [])
            ]
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=p["content"], tool_calls=tc or None
                        )
                    )
                ]
            )

    class Chat:
        completions = Completions()

    return SimpleNamespace(chat=Chat())


def _provider(monkeypatch, payloads) -> DeepSeekProvider:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")
    p = DeepSeekProvider()
    p._client = _stub_client(payloads)  # 替换真实 client，绝不联网
    return p


def test_to_openai_message_assistant_tool_calls():
    m = ChatMessage(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(id="c1", name="cancel_order", arguments={"order_id": "ORD-1001"})
        ],
    )
    d = _to_openai_message(m)
    assert d["role"] == "assistant" and "content" not in d
    assert d["tool_calls"][0]["function"]["arguments"] == '{"order_id": "ORD-1001"}'


def test_to_openai_message_tool_role():
    d = _to_openai_message(
        ChatMessage(role="tool", content='{"outcome":"applied"}', tool_call_id="c1")
    )
    assert d == {
        "role": "tool",
        "content": '{"outcome":"applied"}',
        "tool_call_id": "c1",
    }


def test_to_openai_message_system_and_user():
    assert _to_openai_message(ChatMessage(role="system", content="规则")) == {
        "role": "system",
        "content": "规则",
    }
    assert _to_openai_message(ChatMessage(role="user", content="hi")) == {
        "role": "user",
        "content": "hi",
    }


def test_deepseek_chat_maps_content_and_tool_calls(monkeypatch):
    p = _provider(
        monkeypatch,
        [
            {
                "content": "我来看一下",
                "tool_calls": [
                    {
                        "id": "c1",
                        "name": "cancel_order",
                        "arguments": '{"order_id":"ORD-1001"}',
                    }
                ],
            }
        ],
    )
    resp = p.chat([ChatMessage(role="user", content="取消 ORD-1001")], tools=[])
    assert resp.content == "我来看一下"
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "cancel_order"
    assert resp.tool_calls[0].arguments == {"order_id": "ORD-1001"}


def test_deepseek_chat_no_tool_calls(monkeypatch):
    p = _provider(monkeypatch, [{"content": "明白", "tool_calls": []}])
    resp = p.chat([ChatMessage(role="user", content="hi")])
    assert resp.content == "明白" and resp.tool_calls == []


def test_deepseek_chat_bad_arguments_json_falls_back_empty(monkeypatch):
    """LLM 返回非法 JSON 参数（不可信输入）：回退空 dict，不崩。"""
    p = _provider(
        monkeypatch,
        [
            {
                "content": None,
                "tool_calls": [
                    {"id": "c1", "name": "cancel_order", "arguments": "not-json"}
                ],
            }
        ],
    )
    resp = p.chat([ChatMessage(role="user", content="x")])
    assert resp.tool_calls[0].arguments == {}


def test_deepseek_chat_non_dict_arguments_falls_back_empty(monkeypatch):
    p = _provider(
        monkeypatch,
        [
            {
                "content": None,
                "tool_calls": [{"id": "c1", "name": "x", "arguments": '["a"]'}],
            }
        ],
    )
    resp = p.chat([ChatMessage(role="user", content="x")])
    assert resp.tool_calls[0].arguments == {}


def test_deepseek_chat_passes_tools_to_sdk(monkeypatch):
    captured = {}

    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="ok", tool_calls=None)
                    )
                ]
            )

    class Chat:
        completions = Completions()

    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")
    p = DeepSeekProvider()
    p._client = SimpleNamespace(chat=Chat())
    p.chat([ChatMessage(role="user", content="hi")], tools=[{"type": "function"}])
    assert captured["tools"] == [{"type": "function"}]
    assert captured["model"] == "deepseek-chat"
