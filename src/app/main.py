"""波 4a 任务 1：/agent 会话端点接线。

在现有 api/main.py 的 create_app 基础上新增 agent 会话端点：
- POST /agent/chat  → 用户消息 → LLM 编排 → 回复（可能含 need_confirm）
- POST /agent/confirm → 双签确认/拒绝 → 执行/取消 → 回复

与现有 API 路由共存：同一 FastAPI 实例挂载 /meta /objects /actions /audit + /agent。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent.agent import ActionExecutor, Agent
from src.agent.provider import get_provider
from src.app.session import SessionManager
from src.runtime.action_engine import ALLOWED_ACTORS

# ======================================================================
# 请求/响应模型（与前端共享契约）
# ======================================================================


class ChatRequest(BaseModel):
    """POST /agent/chat 请求体。"""

    message: str = Field(..., min_length=1, description="用户消息")
    session_id: str | None = Field(
        None, description="会话 ID（可选，不传则创建新会话）"
    )


class ChatResponse(BaseModel):
    """POST /agent/chat 响应体。"""

    session_id: str
    reply: str
    need_confirm: dict | None = None
    outcome: str | None = None


class ConfirmRequest(BaseModel):
    """POST /agent/confirm 请求体。"""

    session_id: str = Field(..., min_length=1)
    call_id: str = Field(..., min_length=1)
    confirmed: bool


class ConfirmResponse(BaseModel):
    """POST /agent/confirm 响应体。"""

    reply: str
    outcome: str


# ======================================================================
# ActionExecutor 实现（走 REST 端点，与 UI 同一写入口 §5.5）
# ======================================================================


class RestActionExecutor(ActionExecutor):
    """通过 HTTP 调用同一 FastAPI 实例的动作端点（统一写入口）。

    不走 TestClient 内部调用，而是直接调用 runtime engine，
    避免循环依赖（agent 端点需要 executor，但 executor 不能
    再走 HTTP 回环）。

    实际实现：直接调 runtime engine（与 API routes 共享同一 engine 实例）。
    """

    def __init__(self, engine: Any, query: Any) -> None:
        self._engine = engine
        self._query = query

    def execute(
        self,
        action_name: str,
        params: dict,
        *,
        actor: str = "llm",
        actor_detail: str = "",
        request_id: str = "",
    ) -> dict:
        """走与 API routes 相同的 engine.execute() 管道。"""
        from src.api.schemas import Envelope, ErrorInfo

        result = self._engine.execute(
            action_name=action_name,
            params=params,
            actor=actor,
            actor_detail=actor_detail,
            request_id=request_id,
        )
        # 构建与 API routes 一致的 data 结构
        data = {
            "effects": [e.model_dump() for e in result.effects],
            "audit_id": result.audit_id,
        }
        return Envelope(
            request_id=result.request_id,
            outcome=result.outcome,
            data=data,
            error=(
                ErrorInfo(
                    code=result.error_code,
                    message=result.message or "",
                    detail=result.detail,
                )
                if result.error_code
                else None
            ),
        ).model_dump()

    def search(
        self,
        object_type: str,
        filter: dict | None = None,
        page_size: int = 10,
    ) -> dict:
        """走与 API routes 相同的 query.list_objects() 管道。"""
        from src.api.schemas import Envelope

        try:
            items, total = self._query.list_objects(
                object_type, filters=filter or {}, page=1, page_size=page_size
            )
            return Envelope(
                request_id="",
                outcome="ok",
                data={
                    "type": object_type,
                    "page": 1,
                    "page_size": page_size,
                    "total": total,
                    "items": items,
                },
            ).model_dump()
        except (ValueError, LookupError, RuntimeError) as exc:
            return Envelope(
                request_id="",
                outcome="error",
                error={
                    "code": "QUERY_ERROR",
                    "message": str(exc),
                },
            ).model_dump()


# ======================================================================
# 应用工厂
# ======================================================================


def create_app(
    source_db: str | Path | None = None,
    ontology_db: str | Path | None = None,
    rebuild_seed: bool = False,
) -> FastAPI:
    """创建完整的 OntoRun 应用（API 路由 + Agent 会话端点）。

    复用 src.api.main.create_app 初始化 runtime 服务，
    在此基础上挂载 /agent 端点。
    """
    from src.api.main import create_app as create_api_app

    app = create_api_app(
        source_db=source_db,
        ontology_db=ontology_db,
        rebuild_seed=rebuild_seed,
    )

    # 注册 agent 端点（P4：会话持久化，SessionManager 在路由内构造并注入 store + agent 工厂）
    _register_agent_routes(app, app.state.runtime.store)

    # 注册错误处理
    _register_error_handlers(app)

    return app


def _register_agent_routes(app: FastAPI, store) -> None:
    """挂载 /agent/chat 和 /agent/confirm 端点。"""
    import json as _json

    from src.agent.agent import Agent
    from src.ontology import build_registry

    # 预设 registry（与 api 层共享同一实例）
    registry = build_registry()

    def _get_agent(provider_name: str | None = None) -> Agent:
        """构造 Agent 实例（共享 app.state.runtime 的 engine/query）。"""
        rt = app.state.runtime
        executor = RestActionExecutor(engine=rt.engine, query=rt.query)
        provider = get_provider(provider_name)
        return Agent(registry=registry, provider=provider, executor=executor)

    # P4：会话持久化（SQLite 写-through + 重启恢复）
    sessions = SessionManager(store, agent_factory=_get_agent)

    @app.post("/agent/chat")
    async def agent_chat(body: ChatRequest, request: Request):
        """用户消息 → LLM 编排 → 回复。

        流程：
        1. 身份解析（X-Actor，缺省 human——demo 单用户控制台）并做 owner 绑定（P2-2）
        2. 获取或创建会话（session_id 可选；owner 不匹配的既有会话视为不存在）
        3. 调用 Agent.run_turn() 编排 LLM 往返
        4. 如有高风险提议（need_confirm），记录到会话待确认区
        5. 返回 reply + 可选 need_confirm
        """
        actor = request.headers.get("X-Actor", "human")
        if actor not in ALLOWED_ACTORS:
            return JSONResponse(
                status_code=400,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "INVALID_ACTOR",
                        "message": f"非法操作者（X-Actor 仅允许 {ALLOWED_ACTORS}）",
                        "detail": {"actor": actor},
                    },
                },
            )
        session_id = body.session_id
        state = sessions.get(session_id, owner=actor) if session_id else None

        if state is None:
            agent = _get_agent()
            session_id = sessions.create(agent, owner=actor)
            state = sessions.get(session_id, owner=actor)
        else:
            agent = state.agent

        # TD-6：Agent 编排环是同步（内部多次 provider.chat）；整体扔线程池，
        # 真 DeepSeek 路径不阻塞事件循环（MockProvider 路径开销可忽略）。
        turn = await asyncio.to_thread(agent.run_turn, body.message)

        # 记录待确认提议
        if turn.need_confirm:
            sessions.set_pending(session_id, turn.need_confirm)
        else:
            # 新一轮消息到来：作废旧提议
            sessions.set_pending(session_id, None)

        # P4：每轮写-through 落会话历史（会话重启不丢）
        sessions.persist(session_id, agent)

        need_confirm_dict = None
        if turn.need_confirm:
            tc = turn.need_confirm
            need_confirm_dict = {
                "id": tc.id,
                "name": tc.name,
                "arguments": tc.arguments,
            }

        # 从 tool_results 推断 outcome
        outcome = None
        if turn.tool_results:
            last = turn.tool_results[-1]
            try:
                payload = _json.loads(last.content)
                outcome = payload.get("outcome")
            except (_json.JSONDecodeError, KeyError):
                pass

        return ChatResponse(
            session_id=session_id,
            reply=turn.reply or "",
            need_confirm=need_confirm_dict,
            outcome=outcome,
        )

    @app.post("/agent/confirm")
    async def agent_confirm(body: ConfirmRequest, request: Request):
        """双签确认/拒绝（P1-2：确认者必须为 human，审计记录确认者身份）。

        流程：
        1. 身份校验：X-Actor 必须为 human（agent/api 直调 → 403，防伪造双签）
        2. 从会话待确认区取出提议（owner 绑定校验，P2-2）
        3. 校验 call_id 匹配（确认必须绑定发起提议的会话）
        4. 调用 Agent.confirm_pending() 执行/取消（确认者身份入审计 actor_detail）
        5. 确认成功后才清 pending + 落历史（P1-3：失败不丢 pending）
        6. 返回回复 + outcome
        """
        actor = request.headers.get("X-Actor", "human")  # demo 单用户控制台：缺省=人类操作者
        if actor != "human":
            return JSONResponse(
                status_code=403,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "HUMAN_CONFIRM_REQUIRED",
                        "message": "双签确认必须由人类发起（X-Actor: human）",
                        "detail": {"actor": actor},
                    },
                },
            )
        actor_detail = request.headers.get("X-Actor-Detail", "")

        state = sessions.get(body.session_id, owner=actor)
        if state is None:
            return JSONResponse(
                status_code=404,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "会话不存在或已过期",
                    },
                },
            )

        pending = state.pending_confirm
        if pending is None:
            return JSONResponse(
                status_code=400,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "NO_PENDING_CONFIRM",
                        "message": "当前没有待确认的高风险动作提议",
                    },
                },
            )

        if pending.id != body.call_id:
            return JSONResponse(
                status_code=400,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "CALL_ID_MISMATCH",
                        "message": f"call_id 不匹配（期望 {pending.id}，收到 {body.call_id}）",
                    },
                },
            )

        # P1-3：不在确认前清 pending——失败时提议保留（可重试），成功后才清
        try:
            # TD-6：与 /agent/chat 同理，同步编排环扔线程池（真 LLM 不阻塞事件循环）
            turn = await asyncio.to_thread(
                state.agent.confirm_pending,
                body.confirmed,
                confirmant=actor,
                confirmant_detail=actor_detail,
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=400,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "NO_PENDING_CONFIRM",
                        "message": str(exc),
                    },
                },
            )

        # 确认成功：清 pending + 落历史（工具结果/回复入库，重启不丢）
        sessions.set_pending(body.session_id, None)
        sessions.persist(body.session_id, state.agent)

        # 推断 outcome
        outcome = body.confirmed and "applied" or "cancelled_by_user"
        if turn.tool_results:
            last = turn.tool_results[-1]
            try:
                payload = _json.loads(last.content)
                outcome = payload.get("outcome", outcome)
            except (_json.JSONDecodeError, KeyError):
                pass

        return ConfirmResponse(
            reply=turn.reply or "",
            outcome=outcome,
        )


def _register_error_handlers(app: FastAPI) -> None:
    """注册全局异常处理器（P2-3：固定安全文案 + 完整异常进日志，不回显内部细节）。"""
    import logging

    from fastapi.responses import JSONResponse

    logger = logging.getLogger(__name__)

    @app.exception_handler(Exception)
    async def global_exception_handler(_request: Any, exc: Exception):
        # 原始异常只进日志（含 traceback）；对外 message 固定文案，
        # 与 action_engine 失败路径口径一致（错误信息不泄漏敏感数据）
        logger.exception("未捕获异常（对外只返回固定文案）: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "request_id": "",
                "outcome": "error",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                },
            },
        )


app = create_app()
