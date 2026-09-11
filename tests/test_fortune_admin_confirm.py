"""T0b 骨架，M1 用例随 T202/T204 扩充。

验收基线（SPEC docs/plans/开工门槛-管理台重构_v0.2.md §D1）：本文件在
2026-09-11 基线时不存在，由 T0b 建立。当前只放 1 个 smoke 用例
（既有读端点 GET /api/ontology 断言 200）；confirm 写端点（含 R8
decision/escalate）与试算端点的用例随 T202/T204 扩充。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.fortune_admin.main import app

    with TestClient(app) as c:
        yield c


def test_ontology_endpoint_smoke(client: TestClient):
    """smoke：既有读端点 GET /api/ontology 返回 200 且含 rules 结构。"""
    res = client.get("/api/ontology")
    assert res.status_code == 200, res.text
    body = res.json()
    assert isinstance(body["rules"], list)
