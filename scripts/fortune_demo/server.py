#!/usr/bin/env python3
"""财富广场注册域演示·服务层。数据浏览 + 规则表 + 决策链 API（未来证据链的雏形：每次查询发 request_id + 全步 trace）。"""
import sqlite3, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
import json as _json
from pydantic import BaseModel
import semantic_layer as sl

DB = sl.DB
app = FastAPI(title="Fortune Plaza Registration Demo")

class Ask(BaseModel):
    question: str

@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))

@app.get("/api/tables")
def tables():
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    out = []
    for t in names:
        cols = [{"name": c[1], "type": c[2]} for c in conn.execute(f"PRAGMA table_info({t})")]
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        sample = [dict(r) for r in conn.execute(f"SELECT * FROM {t} LIMIT 20")]
        out.append({"name": t, "rows": n, "columns": cols, "sample": sample})
    conn.close()
    return out

@app.get("/api/rules")
def rules():
    return [{"id": k, **{kk: vv for kk, vv in v.items() if kk in ("desc", "caliber", "path", "sql", "notice")}} for k, v in sl.RULES.items()]

@app.get("/chat")
def chat_page():
    return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat.html"))

@app.get("/api/profile")
def profile():
    # 业务档案：壳按此装配。未来风控接入 = 增加一份 profile（如 jinrong-risk），壳零改动。
    # 金控示例（结构预留）：{"name":"jinrong-risk","endpoint":"/agent/risk/chat/stream","panels":["conclusion_basis","need_confirm"]}
    return {
        "name": "fortune-registration",
        "display": "财富广场 · 注册域",
        "endpoint": "/api/chat",
        "panels": ["decision_pipeline", "path_badge", "conclusion_basis", "history"],
    }

@app.post("/api/chat")
def chat(body: Ask):
    """SSE：决策步骤逐帧直播 → 回答逐字流式 → final（完整 trace）。"""
    def gen():
        for ev in sl.iter_query(body.question):
            yield f"data: {_json.dumps(ev, ensure_ascii=False)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/api/history")
def history():
    import json as _json
    out = []
    try:
        for line in open(sl.TRACE_LOG, encoding="utf-8"):
            d = _json.loads(line)
            out.append({"request_id": d["request_id"], "started_at": d.get("started_at", ""),
                        "question": d["question"], "path": d["path"], "answer": (d.get("answer") or "")[:80]})
    except FileNotFoundError:
        pass
    return list(reversed(out))[-50:]

@app.get("/api/trace/{request_id}")
def trace(request_id: str):
    import json as _json
    try:
        for line in open(sl.TRACE_LOG, encoding="utf-8"):
            d = _json.loads(line)
            if d["request_id"] == request_id:
                return d
    except FileNotFoundError:
        pass
    return {"error": "not found"}

@app.post("/api/ask")
def ask(body: Ask):
    return sl.run_query(body.question)
