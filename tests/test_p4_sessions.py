"""P4 会话持久化测试（会话重启不丢）：SessionManager SQLite 写-through + 恢复。

覆盖（设计 §3 + red-team 修复）：
- 创建/持久化/重建恢复（历史 + 待确认）；
- P1-3：重启后待确认提议实际可执行（confirm_pending 不再 ValueError）；
- P2-2：会话 owner 绑定与校验（非 owner 无法恢复）；
- P2-4：TTL 清理 + 清理后迟到 persist 不产生孤儿 messages；
- get_or_create 兼容。
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.agent.agent import Agent
from src.agent.provider import ChatResponse, MockProvider, ToolCall
from src.app.session import SessionManager
from src.ontology import build_registry
from src.runtime.store import Store


class _FakeExecutor:
    """测试用 executor（不走 REST）。"""

    def execute(self, action_name, params, **kw):
        return {"outcome": "applied", "data": {}}

    def search(self, object_type, **kw):
        return {"items": []}


class _RecordingExecutor(_FakeExecutor):
    """记录执行调用（双签确认断言用）。"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def execute(self, action_name, params, **kw):
        self.calls.append((action_name, params))
        return {"outcome": "applied", "data": {}}


def _make_agent() -> Agent:
    provider = MockProvider(responses=[ChatResponse(content="你好，我是测试助手。")])
    return Agent(
        registry=build_registry(),
        provider=provider,
        executor=_FakeExecutor(),
    )


def _make_manager(store: Store) -> SessionManager:
    return SessionManager(store, agent_factory=_make_agent)


def _tmp_store() -> tuple[Store, Path]:
    d = Path(tempfile.mkdtemp())
    store = Store(str(d / "src.db"), str(d / "ont.db"))
    store.migrate()
    return store, d


def test_create_persist_restore_history() -> None:
    """创建会话 + 消息 → 新 SessionManager（新缓存）→ 恢复：历史完整。"""
    store, _ = _tmp_store()

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
    """待确认提议持久化：重启后 pending_confirm 恢复（含 agent._pending 回填）。"""
    store, _ = _tmp_store()

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
    # P1-3：Agent 内部待确认区也必须回填（否则 confirm_pending 必败）
    assert state.agent._pending is not None, "重启后 Agent._pending 必须回填"
    assert sm2.clear_pending(sid).name == "cancel_order"


def test_restart_confirm_executes() -> None:
    """P1-3：重启后待确认提议实际执行成功（confirm_pending 不再 ValueError）。"""
    store, _ = _tmp_store()

    def _propose_agent() -> Agent:
        provider = MockProvider(
            responses=[
                ChatResponse(
                    tool_calls=[
                        ToolCall(
                            id="tc_restart",
                            name="approve_refund",
                            arguments={
                                "refund_id": "REF-0106",
                                "decision": "approved",
                                "review_note": "x",
                            },
                        )
                    ]
                ),
                ChatResponse(content="已确认：退款审核通过。"),
            ]
        )
        return Agent(registry=build_registry(), provider=provider, executor=_RecordingExecutor())

    def _restart_agent() -> Agent:
        # 重启后 agent 只剩一次 provider 调用：确认后的自然语言回复
        provider = MockProvider(responses=[ChatResponse(content="已确认：退款审核通过。")])
        return Agent(registry=build_registry(), provider=provider, executor=_RecordingExecutor())

    sm1 = SessionManager(store, agent_factory=_restart_agent)
    agent = _propose_agent()
    sid = sm1.create(agent)
    turn = agent.run_turn("审核退款 REF-0106，批准")
    assert turn.need_confirm is not None
    sm1.set_pending(sid, turn.need_confirm)
    sm1.persist(sid, agent)

    # 重启：新 SessionManager（空缓存）
    sm2 = SessionManager(store, agent_factory=_restart_agent)
    state = sm2.get(sid)
    assert state is not None and state.pending_confirm is not None

    turn2 = state.agent.confirm_pending(True)  # 修复前：ValueError
    assert turn2.reply == "已确认：退款审核通过。"


def test_owner_binding() -> None:
    """P2-2：会话 owner 绑定与校验——非 owner 调用方无法恢复会话。"""
    store, _ = _tmp_store()
    sm = _make_manager(store)
    sid = sm.create(_make_agent(), owner="human")

    assert sm.get(sid, owner="human") is not None
    # 缓存未命中 + 缓存命中两条路径都校验 owner
    assert sm.get(sid, owner="attacker") is None, "非 owner 不得恢复会话"
    assert sm.get(sid, owner="attacker") is None
    assert sm.get(sid) is not None  # 内部调用（owner=None）不校验，兼容既有接口


def test_cleanup_expired_ttl() -> None:
    """TTL 清理：超期会话被删（sessions+messages），未超期保留。"""
    store, _ = _tmp_store()

    sm = _make_manager(store)
    sid = sm.create(_make_agent())
    sm.persist(sid, sm.get(sid).agent)
    # 直接改 updated_at 到 31 天前（模拟超期）
    with store.ontology_conn() as conn:
        conn.execute("UPDATE sessions SET updated_at='2020-01-01 00:00:00' WHERE session_id=?", (sid,))
    removed = sm.cleanup_expired(ttl_days=30)
    assert removed == 1
    assert sm.get(sid) is None  # 恢复路径也不应找到（行已删）


def test_cleanup_then_persist_no_orphan() -> None:
    """P2-4：TTL 清理后，迟到的 persist 不产生孤儿 messages（防孤儿）。"""
    store, _ = _tmp_store()

    sm = _make_manager(store)
    sid = sm.create(_make_agent())
    sm.persist(sid, sm.get(sid).agent)
    with store.ontology_conn() as conn:
        conn.execute("UPDATE sessions SET updated_at='2020-01-01 00:00:00' WHERE session_id=?", (sid,))
    assert sm.cleanup_expired(ttl_days=30) == 1

    # 迟到的 persist（会话已被清理）不得写孤儿 messages
    sm.persist(sid, _make_agent())
    with store.ontology_conn() as conn:
        n_msgs = conn.execute(
            "SELECT COUNT(*) AS n FROM messages WHERE session_id=?", (sid,)
        ).fetchone()["n"]
        n_sess = conn.execute(
            "SELECT COUNT(*) AS n FROM sessions WHERE session_id=?", (sid,)
        ).fetchone()["n"]
    assert n_sess == 0 and n_msgs == 0, "清理后 persist 不得产生孤儿消息/会话"


def test_startup_cleanup_runs() -> None:
    """P2-4：SessionManager 启动时惰性清理一次（过期会话被清）。"""
    store, _ = _tmp_store()
    sm = _make_manager(store)
    sid = sm.create(_make_agent())
    sm.persist(sid, sm.get(sid).agent)
    with store.ontology_conn() as conn:
        conn.execute("UPDATE sessions SET updated_at='2020-01-01 00:00:00' WHERE session_id=?", (sid,))
    # 新 manager 构造即触发一次清理
    sm2 = _make_manager(store)
    assert sm2.get(sid) is None, "启动清理应删除过期会话"


def test_get_or_create_compat() -> None:
    """get_or_create 兼容：无 session_id → 新建；有 → 复用。"""
    store, _ = _tmp_store()

    sm = _make_manager(store)
    state1 = sm.get_or_create(None, _make_agent())
    assert state1.agent is not None
    sid = next(iter(sm._cache))
    state2 = sm.get_or_create(sid, _make_agent())
    assert state2 is state1
