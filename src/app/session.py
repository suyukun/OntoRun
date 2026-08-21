"""会话管理器（P4 持久化版：SQLite 写-through + 重启恢复，议题 4 形态）。

- sessions/messages 表（store.py SESSIONS_SCHEMA）：会话元数据 + 消息历史 + 待确认提议；
- 恢复语义：get(session_id) 缓存未命中 → 从表加载 → agent_factory() 重建 Agent →
  回放历史（restore_history）+ 恢复待确认提议（pending_json）；
- 写-through：persist(agent) 在每轮后落历史与 pending（会话重启不丢）；
- TTL：30 天分级清理（标准档 30 天，可配）。
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from src.agent.provider import ChatMessage, ToolCall

if TYPE_CHECKING:
    from src.agent.agent import Agent
    from src.runtime.store import Store

SESSION_TTL_DAYS = 30  # 标准档 TTL（议题 4：30 天清理）
_MESSAGES = ("user", "assistant", "tool")


@dataclass
class SessionState:
    """单个会话的状态：Agent 实例 + 待确认的高风险提议。"""

    agent: Any
    pending_confirm: ToolCall | None = None
    created_at: str = field(default_factory=lambda: str(uuid.uuid4().node))


class SessionManager:
    """SQLite 持久化会话管理器（缓存 + 写-through + 重启恢复）。"""

    def __init__(self, store: Store, agent_factory: Callable[[], Agent]) -> None:
        self._store = store
        self._factory = agent_factory
        self._cache: dict[str, SessionState] = {}

    # ---- 创建 / 获取 / 恢复 ----
    def create(self, agent: Agent) -> str:
        """创建新会话，落 sessions 行，返回 session_id。"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = _now()
        with self._store.ontology_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, created_at, updated_at) VALUES (?,?,?)",
                (session_id, now, now),
            )
        self._cache[session_id] = SessionState(agent=agent, created_at=now)
        return session_id

    def get(self, session_id: str) -> SessionState | None:
        """获取会话状态：缓存未命中 → 从表恢复（重建 Agent + 回放历史）。"""
        if session_id in self._cache:
            return self._cache[session_id]
        return self._restore(session_id)

    def get_or_create(self, session_id: str | None, agent: Agent) -> SessionState:
        """获取已有会话或创建新会话（兼容旧接口）。"""
        if session_id and self.get(session_id) is not None:
            return self._cache[session_id]
        sid = self.create(agent)
        return self._cache[sid]

    def _restore(self, session_id: str) -> SessionState | None:
        """从 sessions/messages 表恢复会话（会话重启不丢）。"""
        with self._store.ontology_conn() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            if row is None:
                return None
            msgs = conn.execute(
                "SELECT role, content, tool_call_id, tool_calls_json FROM messages "
                "WHERE session_id=? ORDER BY created_at, message_id",
                (session_id,),
            ).fetchall()
        agent = self._factory()
        history: list[ChatMessage] = []
        for m in msgs:
            tcs = json.loads(m["tool_calls_json"] or "[]")
            history.append(
                ChatMessage(
                    role=m["role"],
                    content=m["content"],
                    tool_call_id=m["tool_call_id"],
                    tool_calls=[ToolCall(**tc) for tc in tcs] if tcs else None,
                )
            )
        agent.restore_history(history)
        pending = json.loads(row["pending_json"] or "{}")
        pending_call = ToolCall(**pending) if pending else None
        state = SessionState(
            agent=agent, pending_confirm=pending_call, created_at=row["created_at"]
        )
        self._cache[session_id] = state
        return state

    # ---- 写-through（每轮后落盘，会话重启不丢）----
    def persist(self, session_id: str, agent: Agent) -> None:
        """落会话历史 + 待确认（写-through；历史 = agent.history，不含 system）。"""
        now = _now()
        with self._store.ontology_conn() as conn:
            conn.execute(
                "UPDATE sessions SET updated_at=? WHERE session_id=?", (now, session_id)
            )
            conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
            for i, m in enumerate(agent.history):
                tcs = (
                    [tc.model_dump() for tc in m.tool_calls] if m.tool_calls else []
                )
                conn.execute(
                    "INSERT INTO messages (message_id, session_id, role, content, "
                    "tool_call_id, tool_calls_json, created_at) VALUES (?,?,?,?,?,?,?)",
                    (
                        f"{session_id}:{i}",
                        session_id,
                        m.role,
                        m.content,
                        m.tool_call_id,
                        json.dumps(tcs, ensure_ascii=False),
                        now,
                    ),
                )

    def set_pending(self, session_id: str, call: ToolCall | None) -> None:
        """设置/清除待确认提议（落 sessions.pending_json）。"""
        state = self._cache.get(session_id) or self._restore(session_id)
        if state is None:
            return
        state.pending_confirm = call
        payload = call.model_dump() if call else {}
        with self._store.ontology_conn() as conn:
            conn.execute(
                "UPDATE sessions SET pending_json=?, updated_at=? WHERE session_id=?",
                (json.dumps(payload, ensure_ascii=False), _now(), session_id),
            )

    def clear_pending(self, session_id: str) -> ToolCall | None:
        """取出并清除待确认提议。"""
        state = self._cache.get(session_id) or self._restore(session_id)
        if state is None:
            return None
        call = state.pending_confirm
        self.set_pending(session_id, None)
        return call

    # ---- TTL 清理（30 天，标准档）----
    def cleanup_expired(self, ttl_days: int = SESSION_TTL_DAYS) -> int:
        """删除超 TTL 会话（sessions + messages 级联），返回删除数。"""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=ttl_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        with self._store.ontology_conn() as conn:
            expired = [
                r[0]
                for r in conn.execute(
                    "SELECT session_id FROM sessions WHERE updated_at < ?", (cutoff,)
                )
            ]
            for sid in expired:
                conn.execute("DELETE FROM messages WHERE session_id=?", (sid,))
                conn.execute("DELETE FROM sessions WHERE session_id=?", (sid,))
                self._cache.pop(sid, None)
        return len(expired)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


__all__ = ["SessionManager", "SessionState"]
