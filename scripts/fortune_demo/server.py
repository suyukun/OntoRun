#!/usr/bin/env python3
"""财富广场注册域演示·服务层。数据浏览 + 规则表 + 决策链 API（未来证据链的雏形：每次查询发 request_id + 全步 trace）。"""
import sqlite3, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.responses import FileResponse
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

@app.post("/api/ask")
def ask(body: Ask):
    return sl.run_query(body.question)
