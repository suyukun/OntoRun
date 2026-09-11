"""T201 增量测试：R8 双口径对照装配进 GET /api/ontology 的 rules。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §A2-US2 / §B3 / §C1-T201：
- [US2] WHEN 打开 R8 THEN SHALL 呈现双口径对照而非二值按钮（数据侧：
  divergence 含 account/user 两口径，value_evidence 带 595/552/55 数字证据）；
- 非 R8 规则 divergence 为 None；decision 默认 None（随 T202 裁决写入）；
- import 冒烟：ontology_payload() 不炸，rules 计数与 live registry 一致。
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.fortune_admin.main import app

    with TestClient(app) as c:
        yield c


def _ontology(client: TestClient) -> dict:
    res = client.get("/api/ontology")
    assert res.status_code == 200, res.text
    return res.json()


def test_r8_divergence_dual_options_with_numeric_evidence(client: TestClient):
    """[US2] R8 项 divergence 含账户/用户两口径且证据带数字（r8_divergence_card 数据侧）。"""
    rule = next(r for r in _ontology(client)["rules"] if r["id"] == "R8")
    divergence = rule["divergence"]
    assert isinstance(divergence, list) and len(divergence) == 2
    assert {opt["key"] for opt in divergence} == {"account", "user"}
    for opt in divergence:
        assert opt["label"], opt["key"]
        assert opt["applies_to"], opt["key"]
        assert any(ch.isdigit() for ch in opt["value_evidence"]), opt["key"]
    evidence = " ".join(opt["value_evidence"] for opt in divergence)
    # 595 账户 / 552 去重用户 / 55 名被内联注册表丢弃（"55 名"避免被 "552" 子串误中）
    for num in ("595", "552", "55 名"):
        assert num in evidence, num


def test_r8_decision_defaults_none(client: TestClient):
    """decision 默认 None，随 T202 裁决写入。"""
    rule = next(r for r in _ontology(client)["rules"] if r["id"] == "R8")
    assert rule["decision"] is None


def test_non_r8_rules_divergence_is_none(client: TestClient):
    """无分歧规则 divergence/decision 为 None（缺省语义）。"""
    others = [r for r in _ontology(client)["rules"] if r["id"] != "R8"]
    assert others, "registry 应存在 R8 以外的口径规则"
    for r in others:
        assert r.get("divergence") is None, r["id"]
        assert r.get("decision") is None, r["id"]


def test_ontology_payload_smoke_rules_count_stable():
    """import 冒烟：ontology_payload() 不炸，rules 计数与 live registry 一致（装配不增删规则）。"""
    from src.fortune_admin.ontology import load_registry, ontology_payload

    payload = ontology_payload()
    registry = load_registry()
    assert payload["summary"]["rules"] == len(payload["rules"]) == len(registry.rules)
    assert {r["id"] for r in payload["rules"]} == set(registry.rules.keys())
