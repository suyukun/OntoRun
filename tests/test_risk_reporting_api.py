"""S4 M3a 增量测试：监管报送初稿 + 全局督办看板（真实再生库断言，禁 mock）。

断言回链 docs/v0.4-核心链口径包-v0.3.md：
- §七 第 6 幕：看板含天晟 10.8%（归集 86.4 亿 / 集团并表资本 800 亿）、瑞华 9.4%；
- §七 第 5 幕：报送初稿含 12.8% 红色案例（天晟归集 102.4 亿 = 86.4 自身 + 恒昌 16 隐性关联），
  依据条款 2018 办法第三十七/三十四条文案。
数据全部从 ap_anping 六库实算（读侧），与 scripts/verify_demo_numbers.py 同一数据源。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# 口径包§一 期望值（与 risk_script_props.CAPITAL_PARAMS / verify_demo_numbers.py 同源）
GROUP_CAPITAL_YI = 800.0


@pytest.fixture(scope="module")
def client():
    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        yield c


def _r1a_level(ratio: float) -> str:
    """与看板同源的 R1a 定级（读 base.ap_sys_param 阈值，禁硬编码）。"""
    from src.runtime.risk_rules import R1aConfig, level_for_ratio, open_rules_conn

    conn = open_rules_conn()
    try:
        return level_for_ratio(ratio, R1aConfig.load(conn))
    finally:
        conn.close()


def _ts_ranking_entry(data: dict) -> dict:
    """从看板集中度排名中取出天晟集团有限公司条目。"""
    ranking = data["group_concentration_ranking"]
    for g in ranking:
        if g["group_customer_name"] == "天晟集团有限公司":
            return g
    raise AssertionError(f"看板集中度排名未含天晟集团有限公司（实得: {ranking}）")


# ---------------------------------------------------------------------------
# 第 6 幕：全局督办看板
# ---------------------------------------------------------------------------


def test_dashboard_contains_tiansheng_128(client: TestClient):
    """看板前十大集团集中度排名含天晟 R2 纳入后口径 12.8%（P0-3：分子含隐性关联方恒昌）。"""
    res = client.get("/risk/dashboard")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    data = body["data"]
    ts = _ts_ranking_entry(data)
    # R2 纳入后口径：自身 86.4 + 恒昌 16 = 102.4 亿 → 12.8% 红（P0-3 修复，不再 10.8% 红矛盾）
    assert ts["consolidated_balance_yi"] == pytest.approx(102.4, abs=1e-3)
    assert ts["own_balance_yi"] == pytest.approx(86.4, abs=1e-3)
    assert ts["hidden_related_balance_yi"] == pytest.approx(16.0, abs=1e-3)
    assert ts["concentration_ratio"] == pytest.approx(102.4 / GROUP_CAPITAL_YI, abs=1e-3)
    assert ts["concentration_ratio"] == pytest.approx(0.128, abs=1e-3)
    assert ts["concentration_level"] == "红"  # 与 12.8% 实算一致
    assert ts["warning_dimension"] == "concentration"
    # 排名按集中度降序
    ratios = [g["concentration_ratio"] for g in data["group_concentration_ranking"]]
    assert ratios == sorted(ratios, reverse=True)


def test_dashboard_level_consistent_with_ratio(client: TestClient):
    """P0-3 级别展示与比例校验一致：<9% 不得标红/橙，非集中度类预警分列维度。"""
    data = client.get("/risk/dashboard").json()["data"]
    for g in data["group_concentration_ranking"]:
        ratio = g["concentration_ratio"]
        level = g["concentration_level"]
        if ratio < 0.09:
            assert level in ("无", "黄"), f"{g['group_customer_name']} {ratio} 不应标红/橙（实得 {level}）"
            assert level != "红" and level != "橙"
        # 集中度维度行：级别必须与 ratio 的 R1a 实算一致
        assert g["concentration_level"] == _r1a_level(ratio)
    # 非集中度类预警分列维度存在（背景集团行为/合规红警不混进集中度排名级别）
    assert "non_concentration_warnings" in data
    for w in data["non_concentration_warnings"]:
        assert w["warn_level"] in ("红", "橙")
        assert w["concentration_ratio"] < 0.09


def test_dashboard_ruihua_094(client: TestClient):
    """看板含瑞华 9.4%（口径包§七 瑞华黄档案例）。"""
    data = client.get("/risk/dashboard").json()["data"]
    ranking = data["group_concentration_ranking"]
    ruihua = next(
        (g for g in ranking if g["group_customer_name"] == "瑞华能源集团有限公司"), None
    )
    assert ruihua is not None
    assert ruihua["concentration_ratio"] == pytest.approx(0.094, abs=1e-3)


def test_dashboard_capital_block(client: TestClient):
    """资本常量（口径包§一）：集团并表 800 / 银行 600/480/60 / R1a 三线 9/10/12。"""
    cap = client.get("/risk/dashboard").json()["data"]["capital"]
    assert cap["group_consolidated_capital_yi"] == GROUP_CAPITAL_YI
    assert cap["bank_net_capital_yi"] == 600.0
    assert cap["bank_tier1_capital_yi"] == 480.0
    assert cap["bank_internal_limit_yi"] == 60.0
    assert (cap["concern_line"], cap["warn_line"], cap["internal_limit_ratio"]) == (
        0.09,
        0.10,
        0.12,
    )


def test_dashboard_signal_status_distribution_seven_states(client: TestClient):
    """预警状态分布为七态（口径包§四 生命周期状态全集）。"""
    dist = client.get("/risk/dashboard").json()["data"]["signal_status_distribution"]
    assert set(dist.keys()) == {
        "待确认",
        "确认中",
        "已确认",
        "处置中",
        "已关闭",
        "已撤销",
        "已排除",
    }
    assert sum(dist.values()) > 19000  # 信号总量 ~2 万（口径包§五，不展示总量）
    for n in dist.values():
        assert n > 0


def test_dashboard_overdue_default_and_configurable(client: TestClient):
    """超期阈值可配：默认 30 天，overdue_days 参数可调（口径包§七 第 6 幕）。"""
    default = client.get("/risk/dashboard").json()["data"]["overdue"]
    assert default["pending_confirm_overdue"] >= 0
    assert default["in_disposal_overdue"] >= 0
    # 更宽松阈值（365 天）应产生更少的超期数（截止日更近）
    loose = client.get(
        "/risk/dashboard", params={"overdue_days": 365}
    ).json()["data"]["overdue"]
    assert loose["pending_confirm_overdue"] <= default["pending_confirm_overdue"]
    assert loose["in_disposal_overdue"] <= default["in_disposal_overdue"]
    # 非法阈值拒绝
    bad = client.get("/risk/dashboard", params={"overdue_days": "abc"})
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "INVALID_PARAM"


def test_dashboard_subsidiary_response(client: TestClient):
    """各附属机构响应时效：含机构名与处置平均时长字段。"""
    resp = client.get("/risk/dashboard").json()["data"]["subsidiary_response"]
    assert len(resp) >= 5
    orgs = {r["org_name"] for r in resp}
    assert "安平银行" in orgs and "安平证券" in orgs
    for r in resp:
        assert "avg_disposal_days" in r
        assert "completed_disposal_count" in r
        assert r["completed_disposal_count"] > 0


# ---------------------------------------------------------------------------
# 第 5 幕：监管报送初稿（大额风险暴露口径）
# ---------------------------------------------------------------------------

RED_WARNING_ID = "WS-2026-90000002"  # 天晟红色预警（口径包§七 第 2/5 幕）


def test_reporting_draft_red_contains_128(client: TestClient):
    """红色预警报送初稿含 12.8%（口径包§七 第 5 幕：102.4/800）。"""
    res = client.get("/risk/reporting/draft", params={"warning_id": RED_WARNING_ID})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    data = body["data"]
    assert data["report_title"] == "大额风险暴露口径监管报送初稿"
    assert data["group_customer"]["group_customer_name"] == "天晟集团有限公司"
    exp = data["consolidated_exposure"]
    assert exp["own_balance_yi"] == pytest.approx(86.4, abs=1e-3)
    assert exp["hidden_related_party_balance_yi"] == pytest.approx(16.0, abs=1e-3)
    assert exp["total_balance_yi"] == pytest.approx(102.4, abs=1e-3)
    assert exp["concentration_ratio"] == pytest.approx(0.128, abs=1e-3)
    assert exp["ratio_display"] == "12.8%"


def test_reporting_draft_breakdown_single_safe(client: TestClient):
    """报送初稿逐家明细「单看都安全」：银行 48/600=8%、证券 22/400=5.5%、资管 16.4/200=8.2%。"""
    breakdown = client.get(
        "/risk/reporting/draft", params={"warning_id": RED_WARNING_ID}
    ).json()["data"]["breakdown"]
    by_org = {b["org_name"]: b for b in breakdown}
    assert by_org["安平银行"]["balance_yi"] == pytest.approx(48.0, abs=1e-3)
    assert by_org["安平银行"]["org_reference_ratio"] == pytest.approx(0.08, abs=1e-3)
    assert by_org["安平证券"]["org_reference_ratio"] == pytest.approx(0.055, abs=1e-3)
    assert by_org["安平资产管理"]["org_reference_ratio"] == pytest.approx(0.082, abs=1e-3)


def test_reporting_draft_hidden_related_and_rules(client: TestClient):
    """隐性关联方（恒昌三线索）+ 触发规则引用 + 依据条款文案（R1a+R2，2018 办法 37/34）。"""
    data = client.get(
        "/risk/reporting/draft", params={"warning_id": RED_WARNING_ID}
    ).json()["data"]
    hidden = data["hidden_related_parties"]
    assert len(hidden) == 1
    assert hidden[0]["customer_name"] == "恒昌贸易有限公司"
    assert hidden[0]["balance_yi"] == pytest.approx(16.0, abs=1e-3)
    assert len(hidden[0]["relation_clues"]) >= 3  # 股权代持/交叉担保/资金往来
    rules = {r["rule"]: r for r in data["trigger_rules"]}
    assert "R1a" in rules and "R2" in rules
    arts = {b["article"]: b["text"] for b in data["regulatory_basis"]}
    assert "2018 办法第三十七条" in arts and "2018 办法第三十四条" in arts
    assert "立即报告银行业监督管理机构" in arts["2018 办法第三十七条"]


def test_reporting_draft_post_body(client: TestClient):
    """POST /risk/reporting/draft（JSON body）与 GET 同口径。"""
    res = client.post("/risk/reporting/draft", json={"warning_id": RED_WARNING_ID})
    assert res.status_code == 200, res.text
    exp = res.json()["data"]["consolidated_exposure"]
    assert exp["total_balance_yi"] == pytest.approx(102.4, abs=1e-3)
    assert exp["ratio_display"] == "12.8%"


def test_reporting_draft_by_group_customer_no(client: TestClient):
    """按集团客户编号生成报送初稿：自动取该集团红色预警。"""
    res = client.get(
        "/risk/reporting/draft", params={"group_customer_no": "GRP-2026-900001"}
    )
    assert res.status_code == 200, res.text
    exp = res.json()["data"]["consolidated_exposure"]
    assert exp["total_balance_yi"] == pytest.approx(102.4, abs=1e-3)


def test_reporting_draft_rejects_non_red(client: TestClient):
    """仅红色预警可生成报送初稿（橙色预警 → 400 NOT_RED_WARNING）。"""
    res = client.get("/risk/reporting/draft", params={"warning_id": "WS-2026-90000001"})
    assert res.status_code == 400
    body = res.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "NOT_RED_WARNING"


def test_reporting_draft_missing_identifier(client: TestClient):
    """未提供预警标识 → 400。"""
    res = client.get("/risk/reporting/draft")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "MISSING_IDENTIFIER"
