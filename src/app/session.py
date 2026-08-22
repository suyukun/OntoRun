"""会话管理器（P4 持久化版：SQLite 写-through + 重启恢复，议题 4 形态）。

- sessions/messages 表（store.py SESSIONS_SCHEMA）：会话元数据 + 消息历史 + 待确认提议；
- 恢复语义：get(session_id, owner) 缓存未命中 → 从表加载 → agent_factory() 重建 Agent →
  回放历史（restore_history）+ 回填待确认提议（set_pending，P1-3：Agent._pending 也恢复，
  否则重启后 confirm_pending 必败）+ 恢复 pending_json；
- 写-through：persist(agent) 在每轮后落历史与 pending（会话重启不丢）；会话行已被 TTL
  清理时跳过写历史（P2-4 防孤儿 messages）；
- owner 绑定（P2-2）：create 记录创建者身份，get 校验 owner 匹配——非 owner 调用方
  无法恢复/接管他人会话（返回 None，不泄漏存在性）；
- TTL：30 天分级清理（标准档 30 天，可配），SessionManager 构造时惰性清理一次（P2-4）。
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from src.agent.provider import ChatMessage, ToolCall

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.agent.agent import Agent
    from src.runtime.store import Store

SESSION_TTL_DAYS = 30  # 标准档 TTL（议题 4：30 天清理）
_MESSAGES = ("user", "assistant", "tool")


@dataclass
class SessionState:
    """单个会话的状态：Agent 实例 + 待确认的高风险提议 + owner。"""

    agent: Any
    pending_confirm: ToolCall | None = None
    owner: str = ""
    created_at: str = field(default_factory=lambda: str(uuid.uuid4().node))


class SessionManager:
    """SQLite 持久化会话管理器（缓存 + 写-through + 重启恢复）。

    P2-2 owner 语义：owner 为会话创建者身份（应用层 X-Actor）；
    owner 空串 = 未绑定（存量库迁移兼容，单用户 demo 下视为可访问——
    会话不隔离为已知限制，见 docs/S2-P4-完成记录.md）。
    """

    def __init__(self, store: Store, agent_factory: Callable[[], Agent]) -> None:
        self._store = store
        self._factory = agent_factory
        self._cache: dict[str, SessionState] = {}
        # P2-4：启动时惰性清理一次（TTL 过期会话；表不存在/空库时零开销）
        try:
            self.cleanup_expired()
        except Exception:  # 清理失败不阻断启动，仅告警
            logger.warning("启动清理过期会话失败（不阻断）", exc_info=True)

    # ---- 创建 / 获取 / 恢复 ----
    def create(self, agent: Agent, owner: str = "") -> str:
        """创建新会话，落 sessions 行，返回 session_id。owner = 创建者身份（P2-2）。"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = _now()
        with self._store.ontology_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, owner, created_at, updated_at) "
                "VALUES (?,?,?,?)",
                (session_id, owner, now, now),
            )
        self._cache[session_id] = SessionState(agent=agent, owner=owner, created_at=now)
        return session_id

    def get(self, session_id: str, owner: str | None = None) -> SessionState | None:
        """获取会话状态：缓存未命中 → 从表恢复；owner 提供时校验匹配（P2-2）。

        - owner 不匹配 → 返回 None（不泄漏会话存在性）；
        - owner=None（内部调用/兼容接口）→ 不校验。
        """
        state = self._cache.get(session_id)
        if state is None:
            return self._restore(session_id, owner=owner)
        if not self._owner_matches(state.owner, owner):
            return None
        return state

    def get_or_create(
        self, session_id: str | None, agent: Agent, owner: str = ""
    ) -> SessionState:
        """获取已有会话或创建新会话（兼容旧接口）。"""
        if session_id and self.get(session_id, owner=owner) is not None:
            return self._cache[session_id]
        sid = self.create(agent, owner=owner)
        return self._cache[sid]

    def _restore(self, session_id: str, owner: str | None = None) -> SessionState | None:
        """从 sessions/messages 表恢复会话（会话重启不丢）。"""
        with self._store.ontology_conn() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            if row is None:
                return None
            if not self._owner_matches(row["owner"], owner):
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
        # P1-3：待确认提议必须回填 Agent._pending（否则 confirm_pending 必败）
        agent.set_pending(pending_call)
        state = SessionState(
            agent=agent,
            pending_confirm=pending_call,
            owner=row["owner"],
            created_at=row["created_at"],
        )
        self._cache[session_id] = state
        return state

    @staticmethod
    def _owner_matches(stored_owner: str, caller_owner: str | None) -> bool:
        """owner 校验：调用方未提供（owner=None）→ 放行（内部/兼容）；
        存量行 owner 空串（未绑定，单用户 demo 迁移）→ 放行；否则必须精确匹配。"""
        if caller_owner is None:
            return True
        if stored_owner == "":
            return True  # legacy 未绑定会话：单用户 demo 迁移兼容（已知限制）
        return stored_owner == caller_owner

    # ---- 写-through（每轮后落盘，会话重启不丢）----
    def persist(self, session_id: str, agent: Agent) -> None:
        """落会话历史 + 待确认（写-through；历史 = agent.history，不含 system）。

        P2-4 防孤儿：会话行已被 TTL 清理（或不存在）时跳过写历史——
        清理后迟到的 persist 不再产生孤儿 messages。
        """
        now = _now()
        with self._store.ontology_conn() as conn:
            cur = conn.execute(
                "UPDATE sessions SET updated_at=? WHERE session_id=?", (now, session_id)
            )
            if cur.rowcount == 0:
                return  # 会话已被清理/不存在：不写孤儿消息
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
        """删除超 TTL 会话（sessions + messages 级联），返回删除数。

        P2-4：缓存剔除与 DB 删除同一事务（with 块提交），配合 persist 的
        行存在性守卫（rowcount==0 跳过），保证清理后不产生孤儿 messages。
        """
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
