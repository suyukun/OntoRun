"""波 4a 任务 2：/agent 端点 E2E 三问测试（mock LLM 全量）。

验收点：
- POST /agent/chat：cancel_order 全链路（源库真变更+库存释放+审计 actor=llm+错误回填）
- 已发货拦截（SHIPPED_ORDER_CANNOT_BE_CANCELLED 源库零变更）
- 双签确认/拒绝路径（POST /agent/confirm）
- search_objects 上下文查询可用
- 审计断言：audit_log 有记录、writeback_json 自证
"""

import json
import shutil
import sqlite3

import pytest
from fastapi.testclient import TestClient

from data import seed_retail_source as seed
from src.agent.provider import ChatResponse, MockProvider, ToolCall
from src.ontology import build_registry

REG = build_registry()


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture(scope="session")
def seed_db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("agent_api") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def agent_client(tmp_path, seed_db_path, monkeypatch):
    """创建带 agent 端点的 TestClient（每次测试独立双库）。

    默认 LLM_PROVIDER=mock，各测试可通过 monkeypatch.setattr
    覆盖 get_provider 来定制 MockProvider 响应。
    """
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    source = tmp_path / "source.db"
    shutil.copy(seed_db_path, source)
    ontology = tmp_path / "ontology.db"

    from src.app.main import create_app as create_agent_app

    app = create_agent_app(source_db=source, ontology_db=ontology)
    with TestClient(app) as c:
        yield c


def source_db(agent_client, tmp_path) -> sqlite3.Connection:
    """获取源库连接（用 tmp_path 推断路径）。"""
    # 从 app.state 获取路径
    app = agent_client.app
    source_path = app.state.runtime.store.source_path
    conn = sqlite3.connect(source_path)
    conn.row_factory = sqlite3.Row
    return conn


def ontology_db(agent_client) -> sqlite3.Connection:
    app = agent_client.app
    ontology_path = app.state.runtime.store.ontology_path
    conn = sqlite3.connect(ontology_path)
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================================
# Helpers
# ======================================================================


def pick_pending_refund(agent_client) -> dict:
    """挑 1 笔可走 approved 的 pending 退款。"""
    conn = source_db(agent_client, None)
    try:
        row = conn.execute(
            "SELECT r.refund_id, r.amount_cents, o.paid_cents, o.order_id, o.status "
            "FROM refunds r JOIN orders o ON o.order_id = r.order_id "
            "WHERE r.status='pending' AND o.status IN ('shipped','delivered') "
            "AND r.amount_cents < o.paid_cents ORDER BY r.refund_id LIMIT 1"
        ).fetchone()
        assert row is not None, "seed 缺少可走 approved 的 pending 退款样本"
        return dict(row)
    finally:
        conn.close()


# ======================================================================
# 会话管理基础
# ======================================================================


def test_agent_chat_returns_session_id(agent_client):
    """POST /agent/chat 返回 session_id。"""
    resp = agent_client.post("/agent/chat", json={"message": "你好"})
    assert resp.status_code == 200
    body = resp.json()
    assert "session_id" in body
    assert "reply" in body


def test_agent_chat_reuses_session(agent_client):
    """同一 session_id 跨轮累积历史。"""
    resp1 = agent_client.post("/agent/chat", json={"message": "第一轮"})
    sid = resp1.json()["session_id"]

    resp2 = agent_client.post(
        "/agent/chat", json={"message": "第二轮", "session_id": sid}
    )
    assert resp2.status_code == 200
    assert resp2.json()["session_id"] == sid


# ======================================================================
# 三问测试 1：cancel_order 全链路（mock LLM）
# ======================================================================


def test_agent_chat_cancel_order_full_chain(agent_client, monkeypatch):
    """三问测试 1：POST /agent/chat → LLM 提议 cancel_order → 源库真变更 + 库存释放 + 审计。"""
    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_c1",
                        name="cancel_order",
                        arguments={"order_id": "ORD-1001", "reason": "客户改主意"},
                    )
                ]
            ),
            ChatResponse(content="好的，订单 ORD-1001 已取消。"),
        ]
    )
    monkeypatch.setattr(
        "src.app.main.get_provider", lambda name=None: mock
    )

    # 记录库存快照
    conn = source_db(agent_client, None)
    before_reserved = {
        r["product_id"]: r["reserved_qty"]
        for r in conn.execute(
            "SELECT product_id, reserved_qty FROM inventory WHERE warehouse_id=?",
            (seed.MAIN_WAREHOUSE_ID,),
        )
    }
    conn.close()

    resp = agent_client.post(
        "/agent/chat", json={"message": "把 ORD-1001 取消，理由：客户改主意"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "好的，订单 ORD-1001 已取消。"
    assert body.get("need_confirm") is None

    # 源记录真变
    conn = source_db(agent_client, None)
    order = conn.execute(
        "SELECT status FROM orders WHERE order_id='ORD-1001'"
    ).fetchone()
    assert order["status"] == "cancelled"

    # 库存释放
    for pid, qty in (("SKU-003", 3), ("SKU-004", 2)):
        r = conn.execute(
            "SELECT reserved_qty FROM inventory WHERE product_id=? AND warehouse_id=?",
            (pid, seed.MAIN_WAREHOUSE_ID),
        ).fetchone()
        assert r["reserved_qty"] == before_reserved[pid] - qty, f"{pid} 未释放"
    conn.close()

    # 审计留痕（actor=llm）
    oconn = ontology_db(agent_client)
    audit = oconn.execute(
        "SELECT * FROM audit_log WHERE action_name='cancel_order' ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    assert audit is not None
    assert audit["outcome"] == "applied"
    assert audit["actor"] == "llm"
    assert "llm:" in audit["actor_detail"]
    wb = json.loads(audit["writeback_json"])
    assert any("UPDATE orders" in w["sql"] for w in wb)
    assert all(w["rows"] >= 1 for w in wb)
    oconn.close()


# ======================================================================
# 三问测试 3：已发货拦截（源库零变更）
# ======================================================================


def test_agent_chat_cancel_rejected_shipped_order(agent_client, monkeypatch):
    """三问测试 3：已发货订单被拦 → 错误码回填 → LLM 学习规则。"""
    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_c2",
                        name="cancel_order",
                        arguments={"order_id": "ORD-2007"},
                    )
                ]
            ),
            ChatResponse(content="ORD-2007 已发货，不能取消，建议走退款流程。"),
        ]
    )
    monkeypatch.setattr("src.app.main.get_provider", lambda name=None: mock)

    resp = agent_client.post("/agent/chat", json={"message": "把 ORD-2007 取消"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "ORD-2007 已发货，不能取消，建议走退款流程。"

    # 源库零变更
    conn = source_db(agent_client, None)
    assert (
        conn.execute(
            "SELECT status FROM orders WHERE order_id='ORD-2007'"
        ).fetchone()["status"]
        == "shipped"
    )
    conn.close()

    # 审计有 rejected 记录
    oconn = ontology_db(agent_client)
    audit = oconn.execute(
        "SELECT * FROM audit_log WHERE action_name='cancel_order' ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    assert audit is not None
    assert audit["outcome"] == "rejected"
    assert audit["error_code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
    oconn.close()


# ======================================================================
# 双签：确认路径
# ======================================================================


def test_agent_confirm_approve_refund(agent_client, monkeypatch):
    """双签确认：/agent/chat 返回 need_confirm → /agent/confirm 确认 → 源库真变 + 审计。"""
    refund = pick_pending_refund(agent_client)

    mock = MockProvider(
        responses=[
            # 第一轮：LLM 提议 approve_refund（高风险）
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_refund_1",
                        name="approve_refund",
                        arguments={
                            "refund_id": refund["refund_id"],
                            "decision": "approved",
                            "review_note": "审核通过，同意退款",
                        },
                    )
                ]
            ),
            # 第二轮：确认后 LLM 生成回复
            ChatResponse(
                content=f"已确认：退款 {refund['refund_id']} 审核通过。"
            ),
        ]
    )
    monkeypatch.setattr("src.app.main.get_provider", lambda name=None: mock)

    # Step 1: /agent/chat → 返回 need_confirm
    resp1 = agent_client.post(
        "/agent/chat", json={"message": f"审核退款 {refund['refund_id']}，批准"}
    )
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert body1.get("need_confirm") is not None
    assert body1["need_confirm"]["name"] == "approve_refund"
    call_id = body1["need_confirm"]["id"]
    session_id = body1["session_id"]

    # 提议阶段：源库未变
    conn = source_db(agent_client, None)
    assert (
        conn.execute(
            "SELECT status FROM refunds WHERE refund_id=?",
            (refund["refund_id"],),
        ).fetchone()["status"]
        == "pending"
    )
    conn.close()

    # 提议阶段：无审计
    oconn = ontology_db(agent_client)
    n = oconn.execute(
        "SELECT COUNT(*) AS n FROM audit_log WHERE action_name='approve_refund'"
    ).fetchone()["n"]
    assert n == 0, "提议未确认前不得留审计"
    oconn.close()

    # Step 2: /agent/confirm → 确认执行
    resp2 = agent_client.post(
        "/agent/confirm",
        json={"session_id": session_id, "call_id": call_id, "confirmed": True},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert "审核通过" in body2["reply"]
    assert body2.get("outcome") == "applied"

    # 源库真变更
    conn = source_db(agent_client, None)
    row = conn.execute(
        "SELECT r.status FROM refunds r WHERE r.refund_id=?",
        (refund["refund_id"],),
    ).fetchone()
    assert row["status"] == "approved"
    conn.close()

    # 审计留痕（P1-2：确认后以 human 身份执行，记录确认者身份——可追溯「谁确认了什么」）
    oconn = ontology_db(agent_client)
    audit = oconn.execute(
        "SELECT * FROM audit_log WHERE action_name='approve_refund' ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    assert audit is not None
    assert audit["outcome"] == "applied"
    assert audit["actor"] == "human"
    assert "human:" in audit["actor_detail"]
    assert json.loads(audit["writeback_json"])  # writeback 自证
    oconn.close()


# ======================================================================
# 双签：拒绝路径
# ======================================================================


def test_agent_confirm_reject_refund(agent_client, monkeypatch):
    """双签拒绝：/agent/confirm confirmed=false → 不执行、不审计。"""
    refund = pick_pending_refund(agent_client)

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_refund_2",
                        name="approve_refund",
                        arguments={
                            "refund_id": refund["refund_id"],
                            "decision": "approved",
                            "review_note": "审核通过",
                        },
                    )
                ]
            ),
            ChatResponse(content="好的，已取消这笔退款审核。"),
        ]
    )
    monkeypatch.setattr("src.app.main.get_provider", lambda name=None: mock)

    resp1 = agent_client.post(
        "/agent/chat", json={"message": f"审核退款 {refund['refund_id']}"}
    )
    body1 = resp1.json()
    assert body1.get("need_confirm") is not None
    call_id = body1["need_confirm"]["id"]
    session_id = body1["session_id"]

    resp2 = agent_client.post(
        "/agent/confirm",
        json={"session_id": session_id, "call_id": call_id, "confirmed": False},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert "取消" in body2["reply"]

    # 源库未变
    conn = source_db(agent_client, None)
    assert (
        conn.execute(
            "SELECT status FROM refunds WHERE refund_id=?",
            (refund["refund_id"],),
        ).fetchone()["status"]
        == "pending"
    )
    conn.close()

    # 无审计
    oconn = ontology_db(agent_client)
    assert (
        oconn.execute(
            "SELECT COUNT(*) AS n FROM audit_log WHERE action_name='approve_refund'"
        ).fetchone()["n"]
        == 0
    )
    oconn.close()


# ======================================================================
# search_objects 上下文查询
# ======================================================================


def test_agent_chat_search_objects_then_act(agent_client, monkeypatch):
    """LLM 先 search_objects 查上下文 → 回填对象数据 → 再决策执行动作。"""
    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_s1",
                        name="search_objects",
                        arguments={
                            "object_type": "order",
                            "filter": {"order_id": "ORD-1001"},
                        },
                    )
                ]
            ),
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="call_c3",
                        name="cancel_order",
                        arguments={"order_id": "ORD-1001", "reason": "查证后取消"},
                    )
                ]
            ),
            ChatResponse(content="已查证并取消 ORD-1001。"),
        ]
    )
    monkeypatch.setattr("src.app.main.get_provider", lambda name=None: mock)

    resp = agent_client.post(
        "/agent/chat", json={"message": "先查 ORD-1001 状态，再决定是否取消"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "已查证并取消 ORD-1001。"

    # 源库真变更
    conn = source_db(agent_client, None)
    assert (
        conn.execute(
            "SELECT status FROM orders WHERE order_id='ORD-1001'"
        ).fetchone()["status"]
        == "cancelled"
    )
    conn.close()

    # 审计有两条记录：cancel_order applied
    oconn = ontology_db(agent_client)
    audit = oconn.execute(
        "SELECT * FROM audit_log WHERE action_name='cancel_order' ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    assert audit is not None and audit["outcome"] == "applied"
    oconn.close()


# ======================================================================
# 边界：无待确认时 confirm
# ======================================================================


def test_agent_confirm_without_pending_returns_error(agent_client):
    """无待确认提议时 /agent/confirm 返回错误。"""
    resp = agent_client.post(
        "/agent/chat", json={"message": "你好"}
    )
    session_id = resp.json()["session_id"]

    resp2 = agent_client.post(
        "/agent/confirm",
        json={"session_id": session_id, "call_id": "fake_call", "confirmed": True},
    )
    assert resp2.status_code == 400
    body = resp2.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "NO_PENDING_CONFIRM"


# ======================================================================
# 边界：会话不存在
# ======================================================================


def test_agent_confirm_unknown_session(agent_client):
    """不存在的 session_id 返回错误。"""
    resp = agent_client.post(
        "/agent/confirm",
        json={"session_id": "nonexistent", "call_id": "x", "confirmed": True},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "SESSION_NOT_FOUND"


# ======================================================================
# red-team P1-1 / P1-2 / P2-2：双签身份认证 + owner 绑定 + approve 直调拒绝
# ======================================================================


def test_agent_confirm_requires_human_actor(agent_client):
    """P1-2：非 human 主体（X-Actor: llm/api）调 /agent/confirm → 明确错误（403）。"""
    resp = agent_client.post("/agent/chat", json={"message": "你好"})
    session_id = resp.json()["session_id"]
    for bad_actor in ("llm", "api"):
        resp2 = agent_client.post(
            "/agent/confirm",
            headers={"X-Actor": bad_actor},
            json={"session_id": session_id, "call_id": "x", "confirmed": True},
        )
        assert resp2.status_code == 403
        assert resp2.json()["error"]["code"] == "HUMAN_CONFIRM_REQUIRED"


def test_agent_confirm_owner_mismatch(agent_client):
    """P2-2：会话 owner 校验——非 owner 调用方无法确认他人会话（404，不泄漏存在性）。"""
    # 会话由 X-Actor: api 创建（owner=api）
    resp = agent_client.post(
        "/agent/chat", headers={"X-Actor": "api"}, json={"message": "你好"}
    )
    session_id = resp.json()["session_id"]
    # human 尝试确认（owner 不匹配）→ 404 SESSION_NOT_FOUND
    resp2 = agent_client.post(
        "/agent/confirm",
        headers={"X-Actor": "human"},
        json={"session_id": session_id, "call_id": "x", "confirmed": True},
    )
    assert resp2.status_code == 404
    assert resp2.json()["error"]["code"] == "SESSION_NOT_FOUND"


def test_actions_approve_rejects_agent_direct_call(agent_client):
    """P1-1：API 层拒绝 agent 主体直调 approve 动作（指引走 /agent 双签流）。"""
    resp = agent_client.post(
        "/actions/approve_refund",
        headers={"X-Actor": "llm"},
        json={"refund_id": "REF-0001", "decision": "approved", "review_note": "x"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "APPROVE_REQUIRES_HUMAN"


def test_actions_approve_human_direct_allowed_with_audit(agent_client):
    """P1-1：human 主体直调 approve_refund → 引擎放行（审计 actor=human 可追溯）。"""
    resp = agent_client.post(
        "/actions/approve_refund",
        headers={"X-Actor": "human"},
        json={"refund_id": "REF-0001", "decision": "approved", "review_note": "x"},
    )
    # REF-0001 已 approved（seed），此处只需断言走权限门而非被 403 拦
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] in ("applied", "rejected")
    if body["outcome"] == "rejected":
        # 若业务拒绝，也必须是业务错误码（不是权限拒绝）——权限门已放行 human
        assert body["error"]["code"] != "PERMISSION_DENIED"


def test_global_exception_handler_hides_internal_detail(tmp_path, seed_db_path, monkeypatch):
    """P2-3：全局异常处理器——未捕获异常对外只回显固定文案，内部细节不泄漏。

    模拟 LLM 编排层意外崩溃（run_turn 抛 RuntimeError），断言：
    - 响应 500 + INTERNAL_ERROR + 固定 message（不含异常原文）；
    - 完整异常只进日志（logger.exception），响应体不包含内部细节。
    """
    from src.agent.agent import Agent as AgentCls

    monkeypatch.setenv("LLM_PROVIDER", "mock")
    source = tmp_path / "source.db"
    shutil.copy(seed_db_path, source)
    ontology = tmp_path / "ontology.db"

    from src.app.main import create_app as create_agent_app

    app = create_agent_app(source_db=source, ontology_db=ontology)

    def _boom(self, user_message):
        raise RuntimeError("内部机密: refund-amount-42")

    monkeypatch.setattr(AgentCls, "run_turn", _boom)
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.post("/agent/chat", json={"message": "你好"})
    assert resp.status_code == 500
    body = resp.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["message"] == "服务器内部错误"
    # 固定安全文案：内部细节（异常消息原文）不得出现在响应中
    assert "refund-amount-42" not in resp.text
