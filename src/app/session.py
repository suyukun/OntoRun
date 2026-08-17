"""会话管理器（MVP 简化：内存映射）。

- session_id → Agent 实例 + 待确认提议
- 支持跨轮对话历史累积
- 线程安全：单写连接 = 天然串行（FastAPI 事件循环），无需锁
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.agent.provider import ToolCall

if TYPE_CHECKING:
    from src.agent.agent import Agent


@dataclass
class SessionState:
    """单个会话的状态：Agent 实例 + 待确认的高风险提议。"""

    agent: Agent
    pending_confirm: ToolCall | None = None
    created_at: str = field(default_factory=lambda: str(uuid.uuid4().node))


class SessionManager:
    """内存 session 映射（MVP 简化）。

    生产环境应迁移到 Redis/DB 以支持多进程部署。
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create(self, agent: Agent) -> str:
        """创建新会话，返回 session_id。"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        self._sessions[session_id] = SessionState(agent=agent)
        return session_id

    def get(self, session_id: str) -> SessionState | None:
        """获取会话状态，不存在返回 None。"""
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None, agent: Agent) -> SessionState:
        """获取已有会话或创建新会话。"""
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        return SessionState(agent=agent)

    def set_pending(self, session_id: str, call: ToolCall | None) -> None:
        """设置/清除待确认提议。"""
        state = self._sessions.get(session_id)
        if state:
            state.pending_confirm = call

    def clear_pending(self, session_id: str) -> ToolCall | None:
        """取出并清除待确认提议。"""
        state = self._sessions.get(session_id)
        if state is None:
            return None
        call = state.pending_confirm
        state.pending_confirm = None
        return call


__all__ = ["SessionManager", "SessionState"]
