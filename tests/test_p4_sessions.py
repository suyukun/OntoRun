"""P4 会话持久化测试（会话重启不丢）：SessionManager SQLite 写-through + 恢复。

覆盖（设计 §3）：创建/持久化/重建恢复（历史 + 待确认）、TTL 清理、get_or_create 兼容。
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.agent.agent import Agent
from src.agent.provider import ChatResponse, MockProvider
from src.app.session import SessionManager
from src.ontology import build_registry
from src.runtime.store import Store


class _FakeExecutor:
    """测试用 executor（不走 REST）。"""

    def execute(self, action_name, params, **kw):
        return {"outcome": "applied", "data": {}}

    def search(self, object_type, **kw):
        return {"items": []}


def _make_agent() -> Agent:
    provider = MockProvider(responses=[ChatResponse(content="你好，我是测试助手。")])
    return Agent(
        registry=build_registry(),
        provider=provider,
        executor=_FakeExecutor(),
    )


def _make_manager(store: Store) -> SessionManager:
    return SessionManager(store, agent_factory=_make_agent)


def test_create_persist_restore_history() -> None:
    """创建会话 + 消息 → 新 SessionManager（新缓存）→ 恢复：历史完整。"""
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()

    sm1 = _make_manager(store)
    agent = _make_agent()
    sid = sm1.create(agent)
    # 模拟一轮对话（MockProvider 回复文本，历史含 user+assistant）
    turn = agent.run_turn("查一下库存")
    assert turn.reply is not None
    sm1.persist(sid, agent)

    # 重启：新 SessionManager（空缓存）
    sm2 = _make_manager(store)
    state = sm2.get(sid)
    assert state is not None, "重启后会话应可恢复"
    restored = state.agent
    assert [m.role for m in restored.history] == ["user", "assistant"]
    assert restored.history[0].content == "查一下库存"


def test_pending_confirm_restored() -> None:
    """待确认提议持久化：重启后 pending_confirm 恢复。"""
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()

    from src.agent.provider import ToolCall

    sm1 = _make_manager(store)
    agent = _make_agent()
    sid = sm1.create(agent)
    sm1.persist(sid, agent)
    call = ToolCall(id="tc1", name="cancel_order", arguments={"order_id": "ORD-1001"})
    sm1.set_pending(sid, call)

    sm2 = _make_manager(store)
    state = sm2.get(sid)
    assert state is not None and state.pending_confirm is not None
    assert state.pending_confirm.name == "cancel_order"
    assert sm2.clear_pending(sid).name == "cancel_order"


def test_cleanup_expired_ttl() -> None:
    """TTL 清理：超期会话被删（sessions+messages），未超期保留。"""
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()

    sm = _make_manager(store)
    sid = sm.create(_make_agent())
    sm.persist(sid, sm.get(sid).agent)
    # 直接改 updated_at 到 31 天前（模拟超期）
    with store.ontology_conn() as conn:
        conn.execute("UPDATE sessions SET updated_at='2020-01-01 00:00:00' WHERE session_id=?", (sid,))
    removed = sm.cleanup_expired(ttl_days=30)
    assert removed == 1
    assert sm.get(sid) is None  # 恢复路径也不应找到（行已删）


def test_get_or_create_compat() -> None:
    """get_or_create 兼容：无 session_id → 新建；有 → 复用。"""
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()

    sm = _make_manager(store)
    state1 = sm.get_or_create(None, _make_agent())
    assert state1.agent is not None
    sid = next(iter(sm._cache))
    state2 = sm.get_or_create(sid, _make_agent())
    assert state2 is state1
