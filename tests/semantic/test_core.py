"""T1 core invariants (exploration stage: only these, no full-suite runs).

Env overrides happen BEFORE importing src.semantic so the package pins the
isolated tmp stores; SEMANTIC_DISABLE_LLM=1 forces keyword routing (deterministic,
no network) — which also exercises the degraded-success mapping (§4.2 #2b).
Queries run against the L2 mirror via fortune_semantic.compiler.
"""

import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="semantic-test-"))
os.environ["SEMANTIC_APP_DB"] = str(_TMP / "app.db")
os.environ["SEMANTIC_TRACE_LOG"] = str(_TMP / "trace.jsonl")
os.environ["SEMANTIC_DISABLE_LLM"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from src.semantic import engine, sanitize, storage  # noqa: E402
from src.semantic.app import app  # noqa: E402
from src.semantic.rules import SENSITIVE_FIELDS  # noqa: E402

storage.migrate()
client = TestClient(app)

QUESTIONS = {
    "kpi": "2026年8月注册用户数是多少？",
    "channel": "2026年8月分渠道注册用户数",
    "gender": "2026年8月注册用户男女比例",
    "rejected": "抽奖活动效果怎么样？",
    "blocked_param": "注册用户数是多少？",
    "out_of_range": "2026年10月注册用户数是多少？",
}
EXPECTED = {  # question -> (path, state, block_reason)
    "kpi": ("semantic_pushdown", "success_warning", None),  # degraded: LLM disabled -> keyword route
    "channel": ("semantic_pushdown", "success_warning", None),
    "gender": ("semantic_pushdown", "success_warning", None),  # + honest unfilled-dimension degradation
    "rejected": ("rejected", "reject_scope", None),
    "blocked_param": ("blocked_param", "ask_param", "missing_param"),
    "out_of_range": ("blocked_param", "reject_range", "out_of_range"),
}
NUM_RE = re.compile(r"(?<![A-Za-z0-9])(\d[\d,]*\.?\d*)")


def _final(frames):
    finals = [f for f in frames if f["kind"] == "final"]
    assert len(finals) == 1
    return finals[0]["result"]


def _trace_count() -> int:
    return len(storage.load_traces())


def test_six_paths_each_produce_final_with_structured_state():
    """Six paths all persist + one final frame; path/state/block_reason mapping (§4.2)."""
    before = _trace_count()
    for key, question in QUESTIONS.items():
        frames = list(engine.iter_query(question))
        result = _final(frames)
        expected_path, expected_state, expected_block = EXPECTED[key]
        assert result["path"] == expected_path, (key, result["path"])
        assert result["state"] == expected_state, (key, result["state"])
        assert result.get("block_reason") == expected_block, (key, result.get("block_reason"))
        assert result["request_id"], key
        assert result["data_profile"] == "mock", key  # every result carries the mock badge
        # steps numbered 1..N continuously (§7 #3)
        nums = [s["n"] for s in result["steps"]]
        assert nums == list(range(1, len(nums) + 1)), (key, nums)
    assert _trace_count() == before + len(QUESTIONS)  # every path persisted


def test_answer_numbers_traceable_to_rows():
    """D6 invariant: every number in the answer derives from rows/params, no hallucination."""
    for key in ("kpi", "channel", "gender"):
        result = _final(list(engine.iter_query(QUESTIONS[key])))
        assert result["rows"], key
        allowed = engine.traceable_numbers(
            result["measure"], result.get("dimensions") or (), result["rows"], result.get("params"))
        answer_nums = {t.replace(",", "") for t in NUM_RE.findall(result["answer"])}
        assert answer_nums <= allowed, (key, answer_nums - allowed)


def test_client_request_id_idempotent_single_trace():
    """Same client_request_id twice -> exactly one new trace, identical snapshot."""
    before = _trace_count()
    request_ids = []
    for _ in range(2):
        with client.stream(
            "POST", "/api/chat",
            json={"question": QUESTIONS["kpi"], "client_request_id": "CRID-TEST-1"},
        ) as resp:
            assert resp.status_code == 200
            frames = [
                json.loads(line[len("data: "):])
                for line in resp.iter_lines()
                if line.startswith("data: ")
            ]
        finals = [f for f in frames if f["kind"] == "final"]
        assert len(finals) == 1
        request_ids.append(finals[0]["result"]["request_id"])
    assert request_ids[0] == request_ids[1]
    assert _trace_count() == before + 1  # replay produced no second trace


def test_session_delete_is_hidden_not_physical():
    """Delete = hidden flag: API-invisible everywhere, rows physically retained."""
    session_id = client.post("/api/sessions", json={"title": "T1测试会话"}).json()["id"]
    with client.stream(
        "POST", "/api/chat",
        json={"question": QUESTIONS["kpi"], "conversation_id": session_id,
              "client_request_id": "CRID-SESS-1"},
    ) as resp:
        assert resp.status_code == 200
        list(resp.iter_lines())

    detail = client.get("/api/sessions/" + session_id)
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert messages[1]["result"]["rows"]  # snapshot replay source present
    assert any(s["id"] == session_id for s in client.get("/api/sessions").json())

    assert client.delete("/api/sessions/" + session_id).status_code == 200
    assert not any(s["id"] == session_id for s in client.get("/api/sessions").json())
    assert client.get("/api/sessions/" + session_id).status_code == 404

    conn = sqlite3.connect(os.environ["SEMANTIC_APP_DB"])
    try:
        hidden, msg_count = conn.execute(
            "SELECT c.hidden, (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) "
            "FROM conversations c WHERE c.id = ?",
            (session_id,),
        ).fetchone()
    finally:
        conn.close()
    assert hidden == 1 and msg_count == 2  # physically retained


def test_pii_guard_passes_encrypted_masks_plaintext():
    """PII hook: encrypted state passes through; plaintext-looking values masked."""
    rows = sanitize.apply_pii_policy(
        [{"usr_phone_erpt": "enc(aes)::phone:ab12", "usr_idcardno_erpt": "13800000000",
          "total": 5}],
        SENSITIVE_FIELDS,
    )
    assert rows[0]["usr_phone_erpt"] == "enc(aes)::phone:ab12"
    assert rows[0]["usr_idcardno_erpt"] == "***MASKED***"
    assert rows[0]["total"] == 5


def test_viz_contract_propagated():
    """D7: shape-derived viz must propagate to final.result.viz (None → table fallback)."""
    from semantic.engine import iter_query
    for q, expected in [("8月按渠道的注册用户数？", "bar"), ("8月注册用户数是多少？", "kpi")]:
        final = None
        for ev in iter_query(q, request_id="VIZ-CONTRACT"):
            if ev["kind"] == "final":
                final = ev["result"]
        assert final is not None
        assert final.get("viz") == expected, f"{q}: viz={final.get('viz')}, expected {expected}"
