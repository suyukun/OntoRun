"""T4 session-persistence & history integration invariants (exploration stage).

Locks the minimal app.py patches T4 relies on:
- /api/history returns the NEWEST `limit` traces, newest first;
- session delete cascades to hiding its traces from history & trace replay
  (product doc acceptance #7) while rows stay physically retained (appendix D);
- client_request_id replay appends no duplicate messages (snapshot restore
  stays 1:1 with what the user saw);
- direct history delete makes trace replay 404.

Env note: config reads SEMANTIC_* at import time; whichever tests/semantic
module imports first pins the tmp store. Every test here counts deltas
relative to pre-state, so sharing the store with test_core is safe.
"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="semantic-t4-"))
os.environ.setdefault("SEMANTIC_APP_DB", str(_TMP / "app.db"))
os.environ.setdefault("SEMANTIC_TRACE_LOG", str(_TMP / "trace.jsonl"))
os.environ.setdefault("SEMANTIC_DISABLE_LLM", "1")

from fastapi.testclient import TestClient  # noqa: E402

from src.semantic import storage  # noqa: E402
from src.semantic.app import app  # noqa: E402

storage.migrate()
client = TestClient(app)

QUESTION = "2026年8月注册用户数是多少？"


def _chat(question: str, **payload) -> str:
    """One streamed chat turn; returns the final frame's request_id."""
    request_id = None
    with client.stream("POST", "/api/chat", json={"question": question, **payload}) as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines():
            if line.startswith("data: ") and '"final"' in line:
                request_id = json.loads(line[len("data: "):])["result"]["request_id"]
    assert request_id
    return request_id


def _message_count(cid: str) -> int:
    return len(client.get("/api/sessions/" + cid).json()["messages"])


def test_history_returns_newest_limit_newest_first():
    """Newest-first slice (was [-limit:] -> oldest slice once traces exceed limit)."""
    rids = [_chat(QUESTION) for _ in range(3)]
    rows = client.get("/api/history", params={"limit": 2}).json()
    assert [r["request_id"] for r in rows] == rids[-2:][::-1]


def test_delete_session_hides_linked_history_and_trace():
    """Delete session -> gone from list, history, and replay; rows physically kept."""
    sid = client.post("/api/sessions", json={"title": "T4级联删除"}).json()["id"]
    rid = _chat(QUESTION, conversation_id=sid, client_request_id="CRID-T4-CASCADE")
    assert any(r["request_id"] == rid for r in client.get("/api/history").json())
    assert client.get("/api/trace/" + rid).status_code == 200

    assert client.delete("/api/sessions/" + sid).status_code == 200
    assert not any(s["id"] == sid for s in client.get("/api/sessions").json())
    assert not any(r["request_id"] == rid for r in client.get("/api/history").json())
    assert client.get("/api/trace/" + rid).status_code == 404  # replay source hidden

    conn = sqlite3.connect(os.environ["SEMANTIC_APP_DB"])
    try:
        hidden, msg_count = conn.execute(
            "SELECT c.hidden, (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) "
            "FROM conversations c WHERE c.id = ?",
            (sid,),
        ).fetchone()
    finally:
        conn.close()
    assert hidden == 1 and msg_count == 2  # appendix D: physical retention


def test_client_request_id_replay_appends_no_duplicate_messages():
    """Idempotent retry: same crid -> same trace, message pair not duplicated."""
    sid = client.post("/api/sessions", json={"title": "T4幂等"}).json()["id"]
    r1 = _chat(QUESTION, conversation_id=sid, client_request_id="CRID-T4-REPLAY")
    count = _message_count(sid)
    r2 = _chat(QUESTION, conversation_id=sid, client_request_id="CRID-T4-REPLAY")
    assert r1 == r2
    assert _message_count(sid) == count


def test_history_delete_makes_trace_replay_404():
    """History entry deleted -> replay endpoint answers 404 (friendly-notice source)."""
    rid = _chat(QUESTION)
    assert client.delete("/api/history/" + rid).json()["hidden"] == 1
    assert client.get("/api/trace/" + rid).status_code == 404
