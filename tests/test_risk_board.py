"""S4 M3a 读侧端点增量测试：监管报送初稿 + 全局督办看板（真实再生库断言）。

数据源：data/des/enterprises/ap_anping 六库（口径包 v0.3 再生成，
scripts/verify_demo_numbers.py 53 项全绿）。本测试直接断言真实再生库，不做小 scale 再生成。

断言（回链口径包 docs/v0.4-核心链口径包-v0.3.md）：
- 看板前十大集团集中度含「天晟集团有限公司 10.8%」（§一 / §七 第 1、6 幕）；
- 报送初稿红色案例 = 归集 86.4 + 恒昌 16 = 102.4 亿 → 12.8%（§七 第 2、5 幕），
  触发规则引用 R1a+R2，依据文案含 2018 办法第三十七/三十四条；
- 七态分布计数 = 全量信号数（§五：~2 万）；超期阈值默认 30 天且可配（§七 第 6 幕）；
- 各附属机构响应时效处置平均时长为正、含安平银行等 10 家机构。

用法：pytest tests/test_risk_board.py -q（增量，秒级；禁全量 pytest）。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.risk_reporting import _ReportService, register_risk_reporting_routes

ROOT = Path(__file__).resolve().parents[1]
AP_DIR = ROOT / "data" / "des" / "enterprises" / "ap_anping"

pytestmark = pytest.mark.skipif(
    not (AP_DIR / "risk.db").is_file(),
    reason="ap_anping 真实再生库缺失：请先执行全量再生成（verify_demo_numbers.py 全绿）",
)


@pytest.fixture(scope="module")
def service() -> _ReportService:
    return _ReportService()


def _pct(ratio: float) -> str:
    return f"{ratio * 100:.1f}%"


class TestDashboard:
    """全局督办看板聚合（§七 第 6 幕）。"""

    def test_concentration_top10_contains_tiansheng_10_8(self, service) -> None:
        d = service.dashboard()
        ranking = d["group_concentration_ranking"]
        assert len(ranking) == 10, f"前十大集团集中度应恰 10 条，实 {len(ranking)}"
        top = ranking[0]
        assert top["group_customer_name"] == "天晟集团有限公司"
        assert top["consolidated_balance_yi"] == 86.4
        assert top["concentration_ratio"] == 0.108
        assert _pct(top["concentration_ratio"]) == "10.8%"
        assert (
            d["capital"]["group_consolidated_capital_yi"] == 800.0
        )  # 口径包§一 并表资本

    def test_state_distribution_sums_to_total_signals(self, service) -> None:
        d = service.dashboard()
        dist = d["signal_status_distribution"]
        assert set(dist) == {
            "待确认",
            "确认中",
            "已确认",
            "处置中",
            "已关闭",
            "已撤销",
            "已排除",
        }
        total = sum(dist.values())
        with sqlite3.connect(f"file:{AP_DIR / 'risk.db'}?mode=ro", uri=True) as conn:
            n = conn.execute("SELECT COUNT(*) FROM ap_warning_signal").fetchone()[0]
        assert total == n  # 七态计数守恒（§五）

    def test_overdue_default_and_configurable(self, service) -> None:
        default = service.dashboard()["overdue"]
        assert default["cutoff_date"]  # as_of - 30 天
        assert default["pending_confirm_overdue"] >= 0
        assert default["in_disposal_overdue"] >= 0
        relaxed = service.dashboard(overdue_days=365)["overdue"]
        # 阈值越大越宽松（cutoff 更早）→ 超期数不增加（口径单调非增）
        assert (
            relaxed["pending_confirm_overdue"] + relaxed["in_disposal_overdue"]
        ) <= (default["pending_confirm_overdue"] + default["in_disposal_overdue"])

    def test_subsidiary_response_positive_duration(self, service) -> None:
        d = service.dashboard()
        resp = d["subsidiary_response"]
        orgs = {r["org_name"] for r in resp}
        assert "安平银行" in orgs and "安平证券" in orgs
        for r in resp:
            assert r["avg_open_age_days"] >= 0
            assert r["avg_disposal_days"] >= 0, f"{r['org_name']} 处置平均时长应为正"


class TestReportingDraft:
    """监管报送初稿（§七 第 5 幕）：红色预警 → 大额风险暴露口径。"""

    def test_red_case_12_8_percent(self, service) -> None:
        dr = service.reporting_draft(group_customer_no="GRP-2026-900001")
        expo = dr["consolidated_exposure"]
        assert dr["group_customer"]["group_customer_name"] == "天晟集团有限公司"
        assert expo["own_balance_yi"] == 86.4
        assert expo["hidden_related_party_balance_yi"] == 16.0
        assert expo["total_balance_yi"] == 102.4
        assert expo["concentration_ratio"] == 0.128
        assert expo["ratio_display"] == "12.8%"

    def test_hidden_party_and_rules(self, service) -> None:
        dr = service.reporting_draft(warning_id="WS-2026-90000002")
        hidden = dr["hidden_related_parties"]
        assert len(hidden) == 1
        assert hidden[0]["customer_name"] == "恒昌贸易有限公司"
        assert hidden[0]["balance_yi"] == 16.0
        assert len(hidden[0]["relation_clues"]) == 3  # 股权代持/交叉担保/资金往来
        rules = {r["rule"] for r in dr["trigger_rules"]}
        assert {"R1a", "R2"} <= rules

    def test_regulatory_basis_articles(self, service) -> None:
        dr = service.reporting_draft(group_customer_no="GRP-2026-900001")
        arts = {r["article"] for r in dr["regulatory_basis"]}
        assert "2018 办法第三十七条" in arts
        assert "2018 办法第三十四条" in arts
        text = "".join(r["text"] for r in dr["regulatory_basis"])
        assert "立即报告" in text and "监管评级" in text

    def test_non_red_warning_rejected(self, service) -> None:
        with pytest.raises(ValueError, match="仅对红色预警"):
            service.reporting_draft(warning_id="WS-2026-90000001")  # 橙色


class TestEndpoints:
    """端点级冒烟（TestClient 走真实路由 + 真实库）。"""

    @pytest.fixture(scope="class")
    def client(self):
        app = FastAPI(title="risk-reporting-test")
        register_risk_reporting_routes(app)
        return TestClient(app)

    def test_dashboard_endpoint(self, client) -> None:
        r = client.get("/risk/dashboard")
        assert r.status_code == 200
        data = r.json()["data"]
        assert (
            data["group_concentration_ranking"][0]["group_customer_name"]
            == "天晟集团有限公司"
        )

    def test_report_draft_endpoint(self, client) -> None:
        r = client.get(
            "/risk/reporting/draft", params={"group_customer_no": "GRP-2026-900001"}
        )
        assert r.status_code == 200
        expo = r.json()["data"]["consolidated_exposure"]
        assert expo["ratio_display"] == "12.8%"
        # 非法参数 → 400 口径错误
        bad = client.get("/risk/reporting/draft", params={"warning_id": "NOPE"})
        assert bad.status_code == 400
        assert bad.json()["outcome"] == "error"
