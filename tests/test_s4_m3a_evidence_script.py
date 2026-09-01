"""S4 M3a 增量测试：证据链载荷结构 + 第 1/2/4 幕端到端（真实库断言 10.8%/12.8%）。

只跑本文件（增量，禁全量 pytest）：
    /opt/anaconda3/bin/python3 -m pytest tests/test_s4_m3a_evidence_script.py -q

覆盖（口径包 v0.3 §六/§七）：
- 证据链载荷统一结构 {结论/依据表名/命中规则+条款/分母说明/明细行引用}（禁 mock）；
- 第 1 幕：天晟逐家 8.0%/5.5%/8.2% 单看都安全 → 归集 86.4/800 = 10.8% 橙（M2 引擎实算，非查表回显）；
- 第 2 幕：恒昌三线索（股权代持/交叉担保/资金往来）+ R2 重算 102.4/800 = 12.8% 红；
- 第 4 幕：approve_disposal REJECTED（2023 关联交易办法第二十三条）→ 处置退回重新起草（未处置）；
- 对话证据链：/agent/risk/chat 答案携带 evidence（剧本工具 / risk_query 内嵌）。

数据源 = ap_anping 真实库（只读）；第 4 幕写路径在 ap_anping 副本上执行（不污染演示数据）。
"""

from __future__ import annotations

import re
import shutil

import pytest
from fastapi.testclient import TestClient

from src.runtime.risk_db import AP_ANPING_DIR, RiskStore

TIANSHENG = "天晟集团有限公司"
GROUP_CAPITAL_YI = 800.0

# 证据链载荷统一键（口径包§六：结论/依据表名/命中规则+条款/分母说明/明细行引用）
EVIDENCE_KEYS = (
    "intent",
    "conclusion",
    "basis_tables",
    "rules_hits",
    "denominator",
    "detail_rows",
)


# ---------------------------------------------------------------------------
# 共享只读端点（真实 ap_anping，禁 mock）
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        yield c


def _reveal(client: TestClient) -> dict:
    res = client.get(
        "/risk/evidence/group-reveal", params={"group_customer_name": TIANSHENG}
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    return body["data"]


def _upgrade(client: TestClient) -> dict:
    res = client.get(
        "/risk/evidence/related-upgrade", params={"group_customer_name": TIANSHENG}
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]


# ---------------------------------------------------------------------------
# 证据链载荷结构（统一五要素）
# ---------------------------------------------------------------------------


def test_evidence_payload_structure(client: TestClient) -> None:
    """三个剧本查询的证据链载荷均为统一五要素结构（口径包§六，禁 mock）。"""
    for payload in (_reveal(client), _upgrade(client)):
        for key in EVIDENCE_KEYS:
            assert key in payload, f"证据链载荷缺 {key}: {payload.get('intent')}"
        assert isinstance(payload["basis_tables"], list) and payload["basis_tables"]
        assert isinstance(payload["rules_hits"], list)
        assert isinstance(payload["detail_rows"], list)
    # 第 4 幕审批链同样五要素（denominator 为 None，分母不适用）
    ac = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-00010309"}
    ).json()["data"]
    for key in EVIDENCE_KEYS:
        assert key in ac, f"审批链证据载荷缺 {key}"


def test_evidence_denominator_has_source(client: TestClient) -> None:
    """分母说明带真实来源（base.ap_sys_param，非硬编码）。"""
    denom = _reveal(client)["denominator"]
    assert denom["value_yi"] == GROUP_CAPITAL_YI
    assert denom["source"] == "base.ap_sys_param.CAP_GROUP_CONSOLIDATED"


# ---------------------------------------------------------------------------
# 第 1 幕：揭示（逐家单看都安全 → 归集 10.8% 橙）
# ---------------------------------------------------------------------------


def test_act1_per_institution_safe(client: TestClient) -> None:
    """逐家附属机构单看都安全（口径包§七 第 1 幕：48/8.0%、22/5.5%、16.4/8.2%）。"""
    detail = {d["org_name"]: d for d in _reveal(client)["detail_rows"]}
    assert detail["安平银行"]["balance_yi"] == pytest.approx(48.0, abs=1e-3)
    assert detail["安平银行"]["ratio_display"] == "8.0%"
    assert detail["安平银行"]["reference_denom_yi"] == 600.0
    assert detail["安平证券"]["ratio_display"] == "5.5%"
    assert detail["安平证券"]["reference_denom_yi"] == 400.0
    assert detail["安平资产管理"]["ratio_display"] == "8.2%"
    assert detail["安平资产管理"]["reference_denom_yi"] == 200.0


def test_act1_aggregation_108_orange(client: TestClient) -> None:
    """归集实算 86.4/800 = 10.8% 橙（M2 引擎 risk_rules 实算，口径包§七 第 1 幕）。"""
    data = _reveal(client)
    comp = data["rules_hits"][0]["computed"]
    assert data["rules_hits"][0]["rule"] == "R1a"
    assert comp["numerator_yi"] == pytest.approx(86.4, abs=1e-3)
    assert comp["denominator_yi"] == GROUP_CAPITAL_YI
    assert comp["ratio"] == pytest.approx(0.108, abs=1e-3)
    assert comp["ratio_display"] == "10.8%"
    assert comp["level"] == "橙"
    # R1a 条款引用（金控办法第三十二/三十三条）+ 橙色预警信号已生成
    assert "第三十二/三十三条" in data["rules_hits"][0]["clause"]
    assert any(s["warn_level"] == "橙" for s in data["signals"])


def test_act1_not_table_echo_computed(client: TestClient) -> None:
    """数据经 M2 引擎实算（红队玩具分水岭）：结论含「归集实算」，且与库内信号原因可互证。"""
    data = _reveal(client)
    assert "实算" in data["conclusion"]
    assert data["conclusion"].startswith(TIANSHENG)


# ---------------------------------------------------------------------------
# 第 2 幕：升级识别（恒昌三线索 + R2 纳入重算 12.8% 红）
# ---------------------------------------------------------------------------


def test_act2_hengchang_three_clues(client: TestClient) -> None:
    """恒昌贸易三线索可回溯（股权代持/交叉担保/资金往来，customer_relation_tree 明细行）。"""
    data = _upgrade(client)
    party = next(d for d in data["detail_rows"] if "恒昌" in d["customer_name"])
    assert party["balance_yi"] == pytest.approx(16.0, abs=1e-3)
    assert set(party["clue_names"]) == {"股权代持", "交叉担保", "资金往来"}
    clue_names = {c["clue"] for c in party["relation_clues"]}
    assert clue_names == {"股权代持", "交叉担保", "资金往来"}
    # 每条线索带真实明细行引用（关系树 PK）
    assert all(
        c["row_ref"].startswith("customer.ap_customer_relation_tree#")
        for c in party["relation_clues"]
    )


def test_act2_r2_recompute_128_red(client: TestClient) -> None:
    """R2 纳入归集重算 102.4/800 = 12.8% 红（口径包§七 第 2 幕）。"""
    data = _upgrade(client)
    rules = {h["rule"]: h for h in data["rules_hits"]}
    assert "R2" in rules and "R1a" in rules
    comp = rules["R1a"]["computed"]
    assert comp["numerator_yi"] == pytest.approx(102.4, abs=1e-3)
    assert comp["ratio"] == pytest.approx(0.128, abs=1e-3)
    assert comp["ratio_display"] == "12.8%"
    assert comp["level"] == "红"
    assert rules["R2"]["computed"]["related_balance_yi"] == pytest.approx(
        16.0, abs=1e-3
    )
    assert "2018" in rules["R2"]["clause"]
    assert any(s["warn_level"] == "红" for s in data["signals"])


# ---------------------------------------------------------------------------
# 第 4 幕：双签驳回（2023 办法第二十三条 → 处置退回重新起草）
# ---------------------------------------------------------------------------


def test_act4_approval_chain_article23(client: TestClient) -> None:
    """审批链证据含 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）。"""
    data = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-00010309"}
    ).json()["data"]
    hit = data["rules_hits"][0]
    assert hit["rule"] == "2023 关联交易办法第二十三条"
    assert "拆分交易" in hit["text"]
    # 明细行：信号 + 处置 + 审批单/任务
    row = data["detail_rows"][0]
    assert row["signal"]["signal_id"] == "SGN-2026-00010309"
    assert row["approve_orders"], "应解析出审批单"
    assert row["approve_orders"][0]["order"]["approve_order_status"] == "PROCESS"


def _pick_process_order(store: RiskStore) -> dict:
    """从 ap_anping（或其副本）挑一个与处置关联的 PROCESS 审批单。"""
    conn = store.source_conn()
    try:
        for o in conn.execute(
            "SELECT approve_order_id, remark FROM approval.ap_approve_order "
            "WHERE approve_order_status='PROCESS' LIMIT 300"
        ):
            m = re.search(r"SGN-\d{4}-\d{8}", o["remark"] or "")
            if not m:
                continue
            w = conn.execute(
                "SELECT warning_id FROM ap_warning_signal WHERE signal_id=?",
                (m.group(0),),
            ).fetchone()
            if not w:
                continue
            d = conn.execute(
                "SELECT disposal_id FROM ap_warning_disposal WHERE warning_id=?",
                (w["warning_id"],),
            ).fetchone()
            if d:
                return {
                    "order": o["approve_order_id"],
                    "signal": m.group(0),
                    "warning": w["warning_id"],
                    "disposal": d["disposal_id"],
                }
    finally:
        conn.close()
    raise AssertionError("ap_anping 未找到与处置关联的 PROCESS 审批单")


@pytest.fixture()
def act4_env(tmp_path_factory):
    """在 ap_anping 副本上建写引擎（第 4 幕写路径不污染演示数据）。"""
    dst = tmp_path_factory.mktemp("s4m3a_act4")
    for f in AP_ANPING_DIR.glob("*.db"):
        shutil.copy2(f, dst / f.name)
    store = RiskStore(ap_dir=dst, ontology_path=dst / "ontology.db")
    from src.runtime.risk_actions_impl import build_risk_engine

    engine = build_risk_engine(store=store)
    return store, engine


def test_act4_reject_returns_to_redraft(act4_env) -> None:
    """审批人依 2023 办法第二十三条驳回 → 处置退回重新起草（未处置），全程留痕。

    （口径包§七 第 4 幕：approve_disposal decision=REJECTED → 处置退回重新起草；
    驳回依据文案 = 第二十三条「禁止隐匿关联关系拆分交易」。）
    """
    store, engine = act4_env
    target = _pick_process_order(store)

    from src.runtime.risk_evidence import ARTICLE_2023_23

    opinion = (
        "驳回：AI 提议将天晟部分授信拆分至非关联第三方通道主体降低名义归集集中度，"
        "违反 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）。"
        + ARTICLE_2023_23
    )
    res = engine.execute(
        "approve_disposal",
        {
            "approve_order_id": target["order"],
            "decision": "REJECTED",
            "opinion": opinion,
        },
        actor="human",
        actor_detail="human:风控审批人; confirmed_call:s4m3a",
        request_id="s4m3a-reject-test",
    )
    assert res.outcome == "applied", f"驳回应生效: {res.error_code} {res.message}"

    conn = store.source_conn()
    try:
        order = conn.execute(
            "SELECT approve_order_status, opinion_description "
            "FROM approval.ap_approve_order WHERE approve_order_id=?",
            (target["order"],),
        ).fetchone()
        disposal = conn.execute(
            "SELECT disposal_status FROM ap_warning_disposal WHERE disposal_id=?",
            (target["disposal"],),
        ).fetchone()
        signal = conn.execute(
            "SELECT disposal_status FROM ap_warning_signal WHERE warning_id=?",
            (target["warning"],),
        ).fetchone()
        tasks = conn.execute(
            "SELECT approve_task_status, approve_result FROM approval.ap_approve_task "
            "WHERE approve_order_id=?",
            (target["order"],),
        ).fetchall()
    finally:
        conn.close()
    assert order["approve_order_status"] == "REJECTED"
    assert "第二十三条" in (order["opinion_description"] or "")
    # 状态退回重新起草：处置回到 DRAFT（未处置），信号处置状态=暂缓处置
    assert disposal["disposal_status"] == "未处置", (
        f"处置应退回未处置重新起草（实得 {disposal['disposal_status']}）"
    )
    assert signal["disposal_status"] == "暂缓处置"
    assert tasks and all(t["approve_task_status"] == "COMPLETED" for t in tasks)
    assert all(t["approve_result"] == "REJECTED" for t in tasks)
    # 审计留痕
    n = engine.audit.query(action="approve_disposal", outcome="applied")[1]
    assert n >= 1


# ---------------------------------------------------------------------------
# 对话证据链：/agent/risk/chat 答案携带 evidence（剧本工具）
# ---------------------------------------------------------------------------


def test_agent_chat_evidence_attached(tmp_path, monkeypatch) -> None:
    """「天晟集团风险有多大」→ 答案携带第 1 幕证据链载荷（对话为演示一级入口）。"""
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t1",
                        name="risk_group_reveal",
                        arguments={"group_customer_name": TIANSHENG},
                    )
                ]
            ),
            ChatResponse(
                content="天晟集团归集 86.4 亿元 ÷ 800 亿元 = 10.8%，触发橙色预警。"
            ),
        ]
    )
    # 路由内 from src.agent.provider import get_provider 在 app 创建时绑定 → 先打补丁再建 app
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "天晟集团风险有多大？"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["evidence"], "每个答案统一附证据链载荷"
        ev = body["evidence"][0]
        assert ev["intent"] == "act1_group_reveal"
        assert ev["rules_hits"][0]["rule"] == "R1a"
        assert ev["rules_hits"][0]["computed"]["ratio_display"] == "10.8%"
        assert ev["denominator"]["value_yi"] == GROUP_CAPITAL_YI


def test_agent_chat_risk_query_evidence(tmp_path, monkeypatch) -> None:
    """普通 risk_query 答案也带最小证据链载荷（依据表名/明细行引用）。"""
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t2",
                        name="risk_query",
                        arguments={
                            "object_type": "warning_signal",
                            "filters": [
                                {"field": "warn_level", "op": "eq", "value": "红"}
                            ],
                            "aggregations": [{"function": "count", "field": "*"}],
                        },
                    )
                ]
            ),
            ChatResponse(content="红色预警若干条。"),
        ]
    )
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "红色预警几条？"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["evidence"]
        ev = body["evidence"][0]
        assert ev["intent"] == "risk_query:warning_signal"
        assert "ap_warning_signal" in ev["basis_tables"]
