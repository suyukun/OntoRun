"""T204 增量测试：试算只读端点三态 + 404/422 + 当日缓存。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §B2-4 / §B3 / §C1-T204 / §A4-4：
- 成功态：走查询链路真实取数（source=semantic_query，month/unit/value 正确）；
- 缓存态：同 rule_id+month 当日二调 source=cache 且值一致，查询只执行一次；
- 失败态：查询链路异常 -> 503 {"detail": "trial_unavailable"}，绝不 500 裸栈；
- rule_id 不存在 -> 404；month 格式非法 -> 422；跨天缓存失效。

打桩说明（如实）：端点行为是测试对象，不是 DuckDB 查询本身——三态用例
monkeypatch trial.run_query（trial._query_value 调用的查询链路唯一入口）注入
确定值/异常，隔离镜像库依赖；另设真实链路冒烟用例（不打桩，镜像库缺失时
skip）证明端点与 compiler.run_query 端到端同源。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.fortune_admin import trial
from src.fortune_admin.ontology import TrialResult
from src.fortune_semantic.compiler import DEFAULT_DB_PATH


@pytest.fixture(scope="module")
def client():
    from src.fortune_admin.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def fake_query(monkeypatch: pytest.MonkeyPatch):
    """打桩 trial.run_query：记录请求参数，行数据/异常可按用例注入。"""
    calls: list[dict] = []
    state = {"rows": [(552,)], "error": None}

    def fake(request):
        calls.append(
            {
                "measure": request.measure,
                "time_from": request.time_from,
                "time_to": request.time_to,
            }
        )
        if state["error"] is not None:
            raise state["error"]
        return {"columns": [request.measure], "rows": state["rows"]}

    monkeypatch.setattr(trial, "run_query", fake)
    monkeypatch.setattr(trial, "_trial_cache", {})  # 用例间缓存隔离
    return state, calls


def _stale_entry(rule_id: str, month: str) -> tuple[date, TrialResult]:
    return (
        date.today() - timedelta(days=1),
        TrialResult(
            rule_id=rule_id,
            month=month,
            value=999.0,
            unit="户",
            generated_at=datetime.now(),
            source="semantic_query",
        ),
    )


def test_trial_success_real_query_chain(client: TestClient, fake_query):
    """① 成功态：查询链路真实返回数字，value/unit/month 正确，source=semantic_query。"""
    _, calls = fake_query
    res = client.get("/api/trial/R8", params={"month": "2026-08"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["rule_id"] == "R8"
    assert data["month"] == "2026-08"
    assert data["value"] == 552.0
    assert data["unit"] == "户"
    assert data["source"] == "semantic_query"
    assert data["generated_at"]

    # 端点真实构造了查询：度量口径锚正确 + month 换算为整月时间窗
    assert calls == [
        {
            "measure": "auth_user_cnt",
            "time_from": "2026-08-01",
            "time_to": "2026-08-31",
        }
    ]


def test_trial_second_same_day_call_served_from_cache(client: TestClient, fake_query):
    """② 缓存态：同参二调 source=cache 且值一致，查询链路只真实执行一次。"""
    _, calls = fake_query
    first = client.get("/api/trial/R8", params={"month": "2026-08"})
    second = client.get("/api/trial/R8", params={"month": "2026-08"})
    assert first.status_code == second.status_code == 200
    assert first.json()["value"] == second.json()["value"] == 552.0
    assert first.json()["source"] == "semantic_query"
    assert second.json()["source"] == "cache"
    assert len(calls) == 1


def test_trial_cache_expires_next_day(client: TestClient, fake_query):
    """跨天失效：昨日缓存不再命中，重新走查询链路。"""
    _, calls = fake_query
    trial._trial_cache[("R8", "2026-08")] = _stale_entry("R8", "2026-08")
    res = client.get("/api/trial/R8", params={"month": "2026-08"})
    assert res.status_code == 200
    assert res.json()["source"] == "semantic_query"
    assert res.json()["value"] == 552.0  # 昨日脏值 999 未透出
    assert len(calls) == 1


def test_trial_query_failure_returns_503_trial_unavailable(
    client: TestClient, fake_query
):
    """③ 失败态：查询链路异常 -> 503 detail=trial_unavailable，细节不外泄。"""
    state, _calls = fake_query
    state["error"] = RuntimeError("duckdb internal boom (should not leak)")
    res = client.get("/api/trial/R8", params={"month": "2026-08"})
    assert res.status_code == 503
    assert res.json() == {"detail": "trial_unavailable"}


def test_trial_null_ratio_returns_503(client: TestClient, fake_query):
    """比率分母 0/缺失（R10 NULL 行）同样落 503，不透出 None。"""
    state, _ = fake_query
    state["rows"] = [(None,)]
    res = client.get("/api/trial/R10", params={"month": "2026-08"})
    assert res.status_code == 503
    assert res.json() == {"detail": "trial_unavailable"}


def test_trial_unknown_rule_returns_404(client: TestClient, fake_query):
    _, calls = fake_query
    res = client.get("/api/trial/NOPE", params={"month": "2026-08"})
    assert res.status_code == 404
    assert calls == []  # 未触查询链路


@pytest.mark.parametrize("bad", ["2026-13", "2026-8", "abc", "2026/08", "08-2026"])
def test_trial_invalid_month_returns_422(client: TestClient, fake_query, bad):
    _, calls = fake_query
    res = client.get("/api/trial/R8", params={"month": bad})
    assert res.status_code == 422
    assert calls == []  # 格式校验先于查询


def test_trial_month_defaults_to_current_month(client: TestClient, fake_query):
    _, calls = fake_query
    res = client.get("/api/trial/R8")
    assert res.status_code == 200
    expected = date.today().strftime("%Y-%m")
    assert res.json()["month"] == expected
    assert calls[0]["time_from"].startswith(expected)


def test_trial_ratio_rule_unit_percent(client: TestClient, fake_query):
    state, _ = fake_query
    state["rows"] = [(0.92,)]
    res = client.get("/api/trial/R10", params={"month": "2026-08"})
    assert res.status_code == 200
    assert res.json()["unit"] == "%"
    assert res.json()["value"] == 0.92


def test_trial_real_semantic_chain_smoke(client: TestClient):
    """真实链路冒烟（不打桩）：端点与 compiler.run_query 端到端同源。"""
    if not DEFAULT_DB_PATH.exists():
        pytest.skip("data/fortune_mirror.duckdb 不存在，跳过真实链路冒烟")
    res = client.get("/api/trial/R5", params={"month": "2026-08"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["source"] == "semantic_query"
    assert data["unit"] == "户"
    assert data["month"] == "2026-08"
    assert data["value"] > 0  # 2026-08 镜像库有实名数据（非 0 真实执行）
    again = client.get("/api/trial/R5", params={"month": "2026-08"})
    assert again.json()["source"] == "cache"
    assert again.json()["value"] == data["value"]
