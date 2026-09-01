"""S3 回归：/risk-objects/{type} 名称归一化与 404（2026-08-27 修 api_name KeyError→500）。

背景：注册表键为驼峰名（RiskCustomer），前端/快照/文档统一用 api_name
（snake_case，risk_customer）。原实现直取 registry.object_type() 对缺失键抛
KeyError → 全局 handler 转 500 INTERNAL_ERROR。修复后两种名字都可查，
未知类型返回 404 OBJECT_TYPE_NOT_FOUND。数据走真实 ap_anping 库。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        yield c


def _risk_api_names() -> list[str]:
    from src.runtime.risk_db import build_risk_source_registry

    return [o.api_name for o in build_risk_source_registry().object_types()]


def test_list_by_camel_name(client: TestClient):
    """注册名（CamelCase）可查：RiskCustomer 返回真实行。"""
    res = client.get("/risk-objects/RiskCustomer", params={"page_size": 3})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    data = body["data"]
    assert data["type"] == "RiskCustomer"
    assert data["total"] > 0
    assert len(data["items"]) >= 1


def test_list_by_api_name(client: TestClient):
    """api_name（snake_case，演示体系对外统一风格）可查，且与注册名同一数据源。"""
    by_api = client.get("/risk-objects/risk_customer", params={"page_size": 3})
    by_camel = client.get("/risk-objects/RiskCustomer", params={"page_size": 3})
    assert by_api.status_code == 200, by_api.text
    assert by_camel.status_code == 200
    a = by_api.json()["data"]
    b = by_camel.json()["data"]
    assert a["total"] == b["total"]
    assert [i.get("customer_no") for i in a["items"]] == [
        i.get("customer_no") for i in b["items"]
    ]


def test_unknown_type_returns_404(client: TestClient):
    """不存在的类型返回结构化 404（不抛 500）。"""
    res = client.get("/risk-objects/no_such_object")
    assert res.status_code == 404
    body = res.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "OBJECT_TYPE_NOT_FOUND"


def test_all_34_objects_queryable_by_api_name(client: TestClient):
    """铁律②机器验证：「全部 34 对象可查」的承诺按 api_name 风格成立。

    （S4 彩排修复 P0-1：sys_param 注册为可查询对象，33 → 34。）"""
    names = _risk_api_names()
    assert len(names) == 34
    for name in names:
        res = client.get(f"/risk-objects/{name}", params={"page_size": 1})
        assert res.status_code == 200, f"{name} -> {res.status_code} {res.text[:120]}"
