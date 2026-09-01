"""波 4a 任务 1：/agent 会话端点接线。

在现有 api/main.py 的 create_app 基础上新增 agent 会话端点：
- POST /agent/chat  → 用户消息 → LLM 编排 → 回复（可能含 need_confirm）
- POST /agent/confirm → 双签确认/拒绝 → 执行/取消 → 回复

与现有 API 路由共存：同一 FastAPI 实例挂载 /meta /objects /actions /audit + /agent。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
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
    """POST /agent/chat 响应体。

    S4 M3a：evidence 为证据链载荷列表（口径包§六「每个答案统一附证据链」）——
    剧本工具（risk_group_reveal / risk_related_reveal / risk_approval_chain）与
    risk_query 的结果内嵌 {结论, 依据表名, 命中规则+条款, 分母说明, 明细行引用}，
    路由层聚合后随答案返回（S1 /agent 不产生 evidence，保持 None 向后兼容）。
    """

    session_id: str
    reply: str
    need_confirm: dict | None = None
    outcome: str | None = None
    evidence: list[dict] | None = None


class ConfirmRequest(BaseModel):
    """POST /agent/confirm 请求体。"""

    session_id: str = Field(..., min_length=1)
    call_id: str = Field(..., min_length=1)
    confirmed: bool


class ConfirmResponse(BaseModel):
    """POST /agent/confirm 响应体。"""

    reply: str
    outcome: str
    evidence: list[dict] | None = None


def _extract_evidence(turn: Any) -> list[dict] | None:
    """从一轮编排的工具结果聚合证据链载荷（工具内容 JSON 的 evidence 键）。

    剧本工具与 risk_query 的结果信封内嵌 evidence（见 src/agent/risk_agent.py），
    此处把每轮命中的证据链载荷汇总附到答案上（口径包§六「每个答案统一附证据链载荷」）。
    """
    out: list[dict] = []
    for r in turn.tool_results:
        try:
            payload = json.loads(r.content)
        except (TypeError, ValueError):
            continue
        ev = payload.get("evidence")
        if isinstance(ev, dict):
            out.append(ev)
    return out or None


# P1-1 追问信号：来源/真伪/分母/依据等，直接回证据链载荷明细，不反问主体
_FOLLOWUP_KEYWORDS: tuple[str, ...] = (
    "哪来",
    "来源",
    "真吗",
    "真假",
    "属实",
    "可信",
    "分母",
    "怎么算",
    "怎么得",
    "依据",
    "凭什么",
    "明细",
    "展开",
    "详细讲讲",
    "为什么",
)


def _is_followup_question(message: str) -> bool:
    """判定是否为对上一轮答案的来源/真伪/分母追问（P1-1）。"""
    return any(k in message for k in _FOLLOWUP_KEYWORDS)


def _with_evidence_context(message: str, evidence: dict) -> str:
    """把会话最近一次证据链载荷注入追问，LLM 直接引用明细作答（不反问主体）。"""
    return (
        "[会话最近一次证据链载荷（用户追问来源/真伪/分母时直接引用，勿反问是哪个主体）]\n"
        + json.dumps(evidence, ensure_ascii=False)
        + f"\n\n用户追问：{message}"
    )


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
    from src.app.des_overview import register_des_routes

    app = create_api_app(
        source_db=source_db,
        ontology_db=ontology_db,
        rebuild_seed=rebuild_seed,
    )

    # 注册 agent 端点（P4：会话持久化，SessionManager 在路由内构造并注入 store + agent 工厂）
    _register_agent_routes(app, app.state.runtime.store)

    # 注册风险 Agent 端点（S3 M3b：独立风险运行时而建，不触碰 S1 /agent）
    register_risk_agent_routes(app)

    # 注册读侧端点（S4 M3a：全局督办看板 + 监管报送初稿，独立模块）
    from src.api.risk_reporting import register_risk_reporting_routes

    register_risk_reporting_routes(app)

    # 注册证据链端点（S4 M3a：七幕剧本查询的证据链载荷，独立模块）
    from src.api.risk_evidence_api import register_risk_evidence_routes

    register_risk_evidence_routes(app)

    # 注册 DES 企业模拟概览端点（S3 M4：让 DES 升级可见的界面入口）
    register_des_routes(app)

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
        actor = request.headers.get(
            "X-Actor", "human"
        )  # demo 单用户控制台：缺省=人类操作者
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


# ======================================================================
# S3 M3b 风险 Agent 会话端点（独立于 S1 /agent，数据源 ap_anping）
# ----------------------------------------------------------------------
# 挂载 /agent/risk/chat + /agent/risk/confirm：用户消息 → RiskAgent（LLM tool
# calling）→ （读）risk_query 受限查询精准问答 / （写）风险动作提议 → need_confirm
# 双签 → 确认后走 build_risk_engine 真实写回 + 审计。
# 风险运行时（RiskStore + build_risk_source_registry + build_risk_engine + RiskQuery）
# 与 S1 零售运行时完全独立，不触碰 S1 共享注册表与既有 /agent。
# ======================================================================


def register_risk_agent_routes(app: FastAPI) -> None:
    """挂载 /agent/risk/chat 与 /agent/risk/confirm（可在任意 FastAPI 实例上复用）。

    构建生产风险运行时（RiskStore + build_risk_engine + RiskQuery），独立于 S1。
    """
    import json as _json

    from src.agent.provider import get_provider
    from src.agent.risk_agent import RiskActionExecutor, RiskAgent
    from src.runtime.risk_actions_impl import build_risk_engine
    from src.runtime.risk_db import RiskStore, build_risk_source_registry
    from src.runtime.risk_query import RiskQuery

    # ---- 风险运行时（独立于 S1） ----
    risk_store = RiskStore()
    risk_store.migrate()
    risk_registry = build_risk_source_registry()
    risk_engine = build_risk_engine(store=risk_store, registry=risk_registry)
    risk_query = RiskQuery(risk_registry, store=risk_store)
    risk_executor = RiskActionExecutor(risk_engine, risk_query)

    def _get_agent(provider_name: str | None = None) -> RiskAgent:
        provider = get_provider(provider_name)
        return RiskAgent(
            registry=risk_registry,
            provider=provider,
            executor=risk_executor,
            query=risk_query,
        )

    # 风险会话独立持久化（同 Store 的 sessions/messages 表）
    risk_sessions = SessionManager(risk_store, agent_factory=_get_agent)

    @app.get("/risk-objects/{type}")
    def risk_object_list(
        type: str, request: Request, page: int = 1, page_size: int = 20
    ):
        """风险对象列表（实时查 ap_anping 真实数据，供风险演示数据浏览页）。

        风险对象在独立注册表（build_risk_source_registry），与 S1 共享注册表分离；
        非 page/page_size 的 query 参数视为等值过滤。
        """
        # 名称归一化：同时接受注册名（CamelCase，如 RiskCustomer）与 api_name
        # （snake_case，如 risk_customer；前端/快照/文档统一用此风格）。
        if risk_registry.has_object_type(type):
            obj = risk_registry.object_type(type)
        else:
            obj = next(
                (o for o in risk_registry.object_types() if o.api_name == type),
                None,
            )
        if obj is None:
            return JSONResponse(
                status_code=404,
                content={
                    "request_id": "",
                    "outcome": "error",
                    "error": {
                        "code": "OBJECT_TYPE_NOT_FOUND",
                        "message": f"风险对象类型不存在: {type}",
                        "detail": None,
                    },
                },
            )
        table = obj.source_table
        conn = risk_store.source_conn()
        try:
            filters = {
                k: v
                for k, v in request.query_params.items()
                if k not in ("page", "page_size")
            }
            where = ""
            args: list = []
            if filters:
                conds = []
                for k, v in filters.items():
                    conds.append(f"{k} = ?")
                    args.append(v)
                where = " WHERE " + " AND ".join(conds)
            total = conn.execute(
                f"SELECT COUNT(*) FROM {table}{where}", args
            ).fetchone()[0]
            limit = max(1, min(page_size, 100))
            offset = max(0, (page - 1) * limit)
            rows = conn.execute(
                f"SELECT * FROM {table}{where} ORDER BY {obj.pk_field} LIMIT ? OFFSET ?",
                args + [limit, offset],
            ).fetchall()
            items = [dict(rr) for rr in rows]
        finally:
            conn.close()
        return JSONResponse(
            content={
                "request_id": "",
                "outcome": "ok",
                "data": {
                    "type": type,
                    "page": page,
                    "page_size": limit,
                    "total": total,
                    "items": items,
                },
            },
        )

    @app.post("/agent/risk/chat")
    async def risk_agent_chat(body: ChatRequest, request: Request):
        """风险场景对话：用户消息 → RiskAgent 编排 → 回复（读精准问答 / 写双签提议）。"""
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
        state = risk_sessions.get(session_id, owner=actor) if session_id else None
        if state is None:
            agent = _get_agent()
            session_id = risk_sessions.create(agent, owner=actor)
            state = risk_sessions.get(session_id, owner=actor)
        else:
            agent = state.agent

        # P1-1 会话上下文：追问来源/真伪/分母时，注入最近一次证据链载荷（不反问主体）
        message = body.message
        if _is_followup_question(message) and state.last_evidence:
            message = _with_evidence_context(message, state.last_evidence)

        turn = await asyncio.to_thread(agent.run_turn, message)
        if turn.need_confirm:
            risk_sessions.set_pending(session_id, turn.need_confirm)
        else:
            risk_sessions.set_pending(session_id, None)
        # P1-1：缓存最近一次证据链载荷（供下一轮追问直接引用）
        # 附带 P2（M4 第三轮终审）：两连问第二轮若未命中工具（evidence=null），
        # 用会话最近一次载荷补位，保证「每个答案统一附证据链」不因轮次空窗断链。
        ev = _extract_evidence(turn)
        if ev:
            state.last_evidence = ev[-1]
            response_evidence: list | None = ev
        elif state.last_evidence:
            response_evidence = [state.last_evidence]
        else:
            response_evidence = None
        risk_sessions.persist(session_id, agent)

        need_confirm_dict = None
        if turn.need_confirm:
            tc = turn.need_confirm
            need_confirm_dict = {
                "id": tc.id,
                "name": tc.name,
                "arguments": tc.arguments,
            }

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
            evidence=response_evidence,
        )

    @app.post("/agent/risk/confirm")
    async def risk_agent_confirm(body: ConfirmRequest, request: Request):
        """风险双签确认/驳回：仅 human 可确认（防伪造双签），确认后走风险引擎执行 + 审计。"""
        actor = request.headers.get("X-Actor", "human")
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
        state = risk_sessions.get(body.session_id, owner=actor)
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
        try:
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
        risk_sessions.set_pending(body.session_id, None)
        risk_sessions.persist(body.session_id, state.agent)

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
            evidence=_extract_evidence(turn),
        )

    @app.get("/risk/audit")
    def risk_audit(
        request: Request,
        action: str | None = None,
        outcome: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """风险审计聚合（F11）：/audit 一键调档改指风险审计库 s3_risk_ontology.db。

        检查组「一键调档」落点：聚合风险动作全程审计（approve_disposal / confirm_warning /
        adjust_warning_level / submit_disposal …，WORM 哈希链全绿），与 approval-chain 的
        audit_trail 同库同源；不再读 S1 零售审计库（total=0 空账）。
        """
        from src.runtime.audit import AuditLog
        from src.runtime.risk_db import RiskStore
        from src.runtime.risk_evidence import audit_display_item

        audit = AuditLog(RiskStore())
        items, total = audit.query(
            action=action, outcome=outcome, page=page, page_size=page_size
        )
        # F15：审计展示 in-universe——actor/actor_detail 开发期机码（llm:DeepSeekProvider、
        # confirmed_call:call_00_…）→ 业务文案；WORM 原行不改，仅展示层映射。
        display = [audit_display_item(dict(it)) for it in items]
        return JSONResponse(
            content={
                "request_id": "",
                "outcome": "ok",
                "data": {"items": display, "total": total},
                "error": None,
            }
        )

    @app.post("/risk/demo/reset-approval")
    def risk_demo_reset_approval():
        """演示重置（F10）：天晟审批单回 PROCESS（节点 2 回 PENDING），供现场第 4 幕 live 驳回。

        把预置 REJECTED 驳回态重置回待审：节点 1 保持已审、节点 2 回 PENDING，审批人可现场
        按 2023 关联交易办法第二十三条驳回；审计 WORM 不清（历史驳回审计行仍可回放），
        live 驳回将追加新审计行。幂等：可重复执行（每次重置回 PENDING）。
        """
        from scripts.patch_risk_live_data import patch_approval_reset_to_pending

        conn = risk_store.source_conn()
        try:
            patch_approval_reset_to_pending(conn)
            conn.commit()
        finally:
            conn.close()
        return JSONResponse(
            content={
                "request_id": "",
                "outcome": "ok",
                "data": {"reset": True, "approve_order_status": "PROCESS"},
                "error": None,
            }
        )


def create_risk_agent_app() -> FastAPI:
    """最小风险 Agent 应用（仅 /agent/risk/* + /des/*，供冒烟/独立部署，不经 S1 API 层）。"""
    from src.app.des_overview import register_des_routes

    app = FastAPI(title="OntoRun 风险 Agent 对话", version="0.1.0")
    register_risk_agent_routes(app)
    from src.api.risk_reporting import register_risk_reporting_routes

    register_risk_reporting_routes(app)
    from src.api.risk_evidence_api import register_risk_evidence_routes

    register_risk_evidence_routes(app)
    register_des_routes(app)
    _register_error_handlers(app)
    return app


app = create_app()
