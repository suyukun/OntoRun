"""T201 增量测试：R8 双口径对照装配进 GET /api/ontology 的 rules。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §A2-US2 / §B3 / §C1-T201：
- [US2] WHEN 打开 R8 THEN SHALL 呈现双口径对照而非二值按钮（数据侧：
  divergence 含 account/user 两口径，value_evidence 带 595/607/55 数字证据
  且两口径均注明数据日期：user 607=试算端点实跑、account/55=2026-08 历史实证）；
- 非 R8 规则 divergence 为 None；decision 默认 None（随 T202 裁决写入）；
- import 冒烟：ontology_payload() 不炸，rules 计数与 live registry 一致。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.fortune_admin import ontology


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
    # user 口径 607=2026-09-11 试算端点实跑真值（与 /api/trial/R8 同源）；
    # account 595 / 55 名被内联注册表丢弃=2026-08 镜像历史实证（"55 名"
    # 避免被 "595"/"607" 子串误中）
    for num in ("595", "607", "55 名"):
        assert num in evidence, num
    # 来源日期透明（证据刷新原则）：两口径证据文本均注明数据日期
    for opt in divergence:
        assert re.search(r"\d{4}-\d{2}(-\d{2})?", opt["value_evidence"]), opt["key"]


@pytest.fixture()
def empty_confirmations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """确认记录隔离到空的受控文件：默认态断言不依赖真实 confirmations.json。"""
    controlled = tmp_path / "confirmations.json"
    controlled.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(ontology, "CONFIRMATIONS_PATH", controlled)
    return controlled


def _expected_r8_decision() -> dict | None:
    """按 payload 契约从真实确认记录推导 R8 decision（§A2-US2：最新记录回流，
    commit 缺失按短码反查补全）——断言"与实际数据态一致"而非钉死具体值。"""
    r8_records = [r for r in ontology.load_confirmations() if r["rule_id"] == "R8"]
    if not r8_records:
        return None
    rec = dict(r8_records[-1])
    if rec.get("commit") is None and rec.get("code"):
        rec["commit"] = ontology._commit_for_code(rec["code"])
    return ontology._decision_from_record(rec)


def test_r8_decision_defaults_none(client: TestClient, empty_confirmations: Path):
    """decision 默认 None，随 T202 裁决写入（受控空确认记录，数据态无关）。"""
    rule = next(r for r in _ontology(client)["rules"] if r["id"] == "R8")
    assert rule["decision"] is None


def test_r8_decision_matches_real_confirmation_records(client: TestClient):
    """数据态感知：payload decision 与真实确认记录回流一致（T-FIX1）。

    真实 confirmations.json 随演示/验收追加（如 D3 已真实裁决 R8），
    断言与最新记录推导值相等（无记录/普通确认 → None），不钉死 None。
    """
    rule = next(r for r in _ontology(client)["rules"] if r["id"] == "R8")
    assert rule["decision"] == _expected_r8_decision()


def test_non_r8_rules_divergence_is_none(client: TestClient, empty_confirmations: Path):
    """无分歧规则 divergence 为 None；decision 默认 None（受控空确认记录）。"""
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
