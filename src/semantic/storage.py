"""Persistence: SQLite app store (conversations/messages/idempotency/history_hidden)
+ trace JSONL. Delete = hidden flag; physical rows preserved (appendix D)."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from . import config

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.APP_DB)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def migrate() -> None:
    """Apply packaged migrations (idempotent, sorted by filename)."""
    config.APP_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    try:
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            conn.executescript(sql_file.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------- conversations

def create_conversation(title: str) -> dict:
    cid = uuid.uuid4().hex
    now = _now()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (cid, title, now, now),
        )
        conn.commit()
    finally:
        conn.close()
    return {"id": cid, "title": title, "pinned": 0, "starred": 0, "hidden": 0,
            "created_at": now, "updated_at": now}


def list_conversations() -> list:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, title, pinned, starred, created_at, updated_at "
            "FROM conversations WHERE hidden = 0 ORDER BY pinned DESC, updated_at DESC"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def get_conversation(cid: str) -> dict | None:
    """Hidden conversations read as absent (API-invisible, physically retained)."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id, title, pinned, starred, created_at, updated_at "
            "FROM conversations WHERE id = ? AND hidden = 0", (cid,)
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def update_conversation(cid: str, fields: dict) -> dict | None:
    sets, vals = ["updated_at = ?"], [_now()]
    for col in ("title", "pinned", "starred"):
        if fields.get(col) is not None:
            val = fields[col]
            vals.insert(len(vals) - 1, int(val) if col != "title" else val)
            sets.insert(len(sets) - 1, col + " = ?")
    conn = _connect()
    try:
        cur = conn.execute(
            "UPDATE conversations SET " + ", ".join(sets) + " WHERE id = ? AND hidden = 0",
            (*vals, cid),
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
    finally:
        conn.close()
    return get_conversation(cid)


def hide_conversation(cid: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute(
            "UPDATE conversations SET hidden = 1, updated_at = ? WHERE id = ?", (_now(), cid)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# -------------------------------------------------------------------- messages

def append_message(cid: str, role: str, *, question: str | None = None,
                   request_id: str | None = None, state: str | None = None,
                   answer: str | None = None, result: dict | None = None) -> str:
    mid = uuid.uuid4().hex
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO messages (id, conversation_id, role, question, request_id, state, "
            "answer, result_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (mid, cid, role, question, request_id, state, answer,
             json.dumps(result, ensure_ascii=False) if result is not None else None, _now()),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (_now(), cid))
        conn.commit()
    finally:
        conn.close()
    return mid


def list_messages(cid: str) -> list:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, conversation_id, role, question, request_id, state, answer, "
            "result_json, created_at FROM messages WHERE conversation_id = ? ORDER BY rowid",
            (cid,),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        item = dict(r)
        item["result"] = json.loads(item.pop("result_json")) if item["result_json"] else None
        out.append(item)
    return out


# ----------------------------------------------------------------- idempotency

def find_request_id(client_request_id: str) -> str | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT request_id FROM idempotency WHERE client_request_id = ?", (client_request_id,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def record_idempotency(client_request_id: str, request_id: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO idempotency (client_request_id, request_id, created_at) "
            "VALUES (?, ?, ?)", (client_request_id, request_id, _now()),
        )
        conn.commit()
    finally:
        conn.close()


# -------------------------------------------------------------- history hidden

def hide_history(request_id: str) -> bool:
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO history_hidden (request_id, hidden_at) VALUES (?, ?)",
            (request_id, _now()),
        )
        conn.commit()
        row = conn.execute(
            "SELECT 1 FROM history_hidden WHERE request_id = ?", (request_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def is_hidden_history(request_id: str) -> bool:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM history_hidden WHERE request_id = ?", (request_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


# ---------------------------------------------------------------- trace JSONL

def persist_trace(result: dict) -> None:
    """Append one full result snapshot (replay = snapshot, never re-executed)."""
    config.TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(config.TRACE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def load_traces() -> list:
    if not config.TRACE_LOG.exists():
        return []
    out = []
    for line in config.TRACE_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # torn tail line: skip, never crash the API
    return out


def load_trace(request_id: str) -> dict | None:
    for trace in load_traces():
        if trace.get("request_id") == request_id:
            return trace
    return None
