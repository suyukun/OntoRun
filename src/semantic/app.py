"""FastAPI service for the fortune-registration profile (T1).

Endpoints: GET /api/insights · GET /api/profile · POST /api/chat (SSE) · GET /api/history ·
GET /api/trace/{rid} · DELETE /api/history/{rid} (hide) · /api/sessions CRUD.
SSE frames: step / token / final (+ terminal error frame), heartbeat comment
frames while a blocking engine step runs (product doc appendix A).
"""

import asyncio
import json
from contextlib import asynccontextmanager, suppress

import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from . import config, engine, insights, storage
from .rules import build_profile


@asynccontextmanager
async def lifespan(_app: FastAPI):
    storage.migrate()
    yield


app = FastAPI(title="OntoRun Semantic Service · fortune-registration", lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    client_request_id: str | None = None
    # 引擎改动单 v0.2 B3（可选字段，缺省 = 行为与现状完全一致）：
    clarify_context: dict | None = None       # 对上轮澄清卡的结构化应答声明
    conversation_context: dict | None = None  # 历史对话数据（数据非指令，≤3 轮）


class SessionCreate(BaseModel):
    title: str | None = None


class SessionPatch(BaseModel):
    title: str | None = None
    pinned: bool | None = None
    starred: bool | None = None
    archived: bool | None = None


# ------------------------------------------------------------------ chat (SSE)

def _persist_messages(conversation_id: str | None, question: str, final: dict) -> str:
    """Snapshot the turn into the session store (user + assistant message)."""
    if conversation_id is None:
        conversation_id = storage.create_conversation(question[:20])["id"]
    storage.append_message(conversation_id, "user", question=question)
    storage.append_message(
        conversation_id, "assistant", question=question,
        request_id=final["request_id"], state=final.get("state"),
        answer=final.get("answer"), result=final,
    )
    return conversation_id


def chat_events(question: str, conversation_id: str | None, client_request_id: str | None,
                clarify_context: dict | None = None,
                conversation_context: dict | None = None):
    """Writer-side generator shared by the SSE endpoint and tests.
    Idempotency: a repeated client_request_id replays the stored snapshot and
    never produces a second trace."""
    if client_request_id:
        prev_rid = storage.find_request_id(client_request_id)
        if prev_rid:
            snapshot = storage.load_trace(prev_rid)
            if snapshot:
                for step in snapshot.get("steps", []):
                    yield {"kind": "step", "step": step}
                yield {"kind": "final", "result": snapshot}
                return

    conv_id = conversation_id
    if conv_id is not None and storage.get_conversation(conv_id) is None:
        conv_id = None  # unknown or hidden session → fall back to auto-create

    for event in engine.iter_query(question, clarify_context=clarify_context,
                                    conversation_context=conversation_context):
        if event["kind"] == "final":
            final = event["result"]
            conv_id = _persist_messages(conv_id, question, final)
            final["conversation_id"] = conv_id
            if client_request_id:
                storage.record_idempotency(client_request_id, final["request_id"])
        yield event


async def _sse_stream(gen):
    """Drive the sync engine generator off the event loop; heartbeat comment
    frames whenever a single blocking step exceeds HEARTBEAT_S."""
    loop = asyncio.get_running_loop()
    sentinel = object()

    def next_frame():
        return next(gen_iter, sentinel)

    gen_iter = iter(gen)
    try:
        while True:
            try:
                event = await asyncio.wait_for(
                    loop.run_in_executor(None, next_frame), timeout=config.HEARTBEAT_S
                )
            except asyncio.TimeoutError:
                yield ": ping\n\n"
                continue
            if event is sentinel:
                break
            yield "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
    finally:
        with suppress(Exception):  # engine records a canceled trace on client disconnect
            gen_iter.close()


@app.post("/api/chat")
async def chat(body: ChatRequest):
    return StreamingResponse(
        _sse_stream(chat_events(
            body.question, body.conversation_id, body.client_request_id,
            clarify_context=body.clarify_context,
            conversation_context=body.conversation_context)),
        media_type="text/event-stream",
    )


# ------------------------------------------------------------------- profile

@app.get("/api/profile")
def profile():
    return build_profile()


# ---------------------------------------------------- proactive insights (T-U2)

@app.get("/api/insights")
def list_insights():
    """主动洞察（B3 契约冻结）：命中 → insights；无命中/镜像不可读 → 常用查询兜底。

    只读、零请求参数（无用户输入进查询，阈值来自 insights 模块数值常量）；
    响应为纯事实字段：零 SQL、零表结构、零归因。
    """
    try:
        found = insights.detect_insights()
    except (duckdb.Error, OSError):
        found = []  # 镜像不可读 → 诚实降级兜底态，不 500、不编造
    if found:
        return {"insights": found}
    return {"insights": [], "fallback": "common_queries"}


# ------------------------------------------------------- history & trace audit

@app.get("/api/history")
def history(limit: int = config.HISTORY_DEFAULT_LIMIT):
    out = []
    for trace in storage.load_traces():
        if storage.is_hidden_history(trace.get("request_id", "")):
            continue
        out.append({
            "request_id": trace.get("request_id"),
            "started_at": trace.get("started_at", ""),
            "question": trace.get("question", ""),
            "path": trace.get("path"),
            "state": trace.get("state"),
            "answer": (trace.get("answer") or "")[:80],
        })
    return list(reversed(out))[: max(1, limit)]  # newest N, newest first


@app.get("/api/trace/{request_id}")
def trace(request_id: str):
    if storage.is_hidden_history(request_id):
        raise HTTPException(status_code=404, detail="trace not found")
    found = storage.load_trace(request_id)
    if found is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return found


@app.delete("/api/history/{request_id}")
def hide_history(request_id: str):
    """History delete = hidden marker; the trace JSONL stays append-only."""
    return {"hidden": 1 if storage.hide_history(request_id) else 0, "request_id": request_id}


# ------------------------------------------------------------------ sessions

@app.post("/api/sessions")
def create_session(body: SessionCreate):
    return storage.create_conversation(body.title or "新对话")


@app.get("/api/sessions")
def list_sessions(archived: bool = False):
    """?archived=true 返回归档区（主列表默认排除归档会话）。"""
    return storage.list_conversations(archived=archived)


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    conversation = storage.get_conversation(session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="session not found")
    return {"conversation": conversation, "messages": storage.list_messages(session_id)}


@app.patch("/api/sessions/{session_id}")
def patch_session(session_id: str, body: SessionPatch):
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=422, detail="no fields to update")
    conversation = storage.update_conversation(session_id, fields)
    if conversation is None:
        raise HTTPException(status_code=404, detail="session not found")
    return conversation


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """Session delete = hidden flag + hide linked history entries (acceptance #7:
    gone from both the session list and history replay); physical rows and the
    append-only trace JSONL stay preserved for audit (appendix D)."""
    if storage.get_conversation(session_id) is None:
        raise HTTPException(status_code=404, detail="session not found")
    storage.hide_conversation(session_id)
    for msg in storage.list_messages(session_id):
        if msg.get("request_id"):
            storage.hide_history(msg["request_id"])
    return {"hidden": 1, "id": session_id}
