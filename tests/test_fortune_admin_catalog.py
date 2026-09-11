"""T501 增量测试：数字目录装配（GET /api/ontology 的 measures 增量字段）。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §A2-US4 / §C1-T501：
- [US4] catalog_plain_names 数据侧前置：measures[].domain 反查 TABLE_DOMAINS，
  与域登记一致（无登记表 -> None，不猜、禁表名前缀兜底）；domain_name = DOMAINS 人话名；
- 版本行摘要 measures[].caliber 与 confirmations.json 一致（不造数据：
  取不到的字段如实 None）；空确认记录 -> 待确认态（全 None + 待锚规则状态）。

跑法（禁跑全量）：
    pytest tests/test_fortune_admin_catalog.py -q
"""

from __future__ import annotations

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


def _expected_caliber(measure_id: str) -> dict | None:
    """独立复算期望值（不走 ontology._measure_caliber，防同源自证）：
    trial._RULE_MEASURES 反查关联规则 -> 有确认记录取最新一条（按时间），
    否则登记顺序第一条；状态取 registry 现值，确认明细取该规则最新记录。"""
    from src.fortune_admin.trial import _RULE_MEASURES

    registry = ontology.load_registry()
    rule_ids = [rid for rid, mid in _RULE_MEASURES.items() if mid == measure_id]
    if not rule_ids:
        return None
    records = {}
    for rec in ontology.load_confirmations():
        records[rec["rule_id"]] = rec  # 追加式，后者覆盖 = 最新一次
    candidates = [
        (rid, records[rid]) for rid in rule_ids if rid in registry.rules and rid in records
    ]
    if candidates:
        anchor_id, rec = max(candidates, key=lambda kv: kv[1]["time"])
    else:
        anchor_id, rec = rule_ids[0], None
    commit = None
    if rec is not None:
        commit = rec.get("commit") or (
            ontology._commit_for_code(rec["code"]) if rec.get("code") else None
        )
    return {
        "rule_id": anchor_id,
        "status": registry.rules[anchor_id].status,
        "code": rec.get("code") if rec else None,
        "confirmer": rec.get("confirmer") if rec else None,
        "time": rec.get("time") if rec else None,
        "commit": commit,
        "verdict": rec.get("verdict") if rec else None,
    }


def test_measure_domain_matches_table_domains(client: TestClient):
    """measures[].domain 与 TABLE_DOMAINS 登记全等（含未登记表 -> None）；人话名同源 DOMAINS。"""
    module = ontology.load_registry_module()
    payload = _ontology(client)
    registry = ontology.load_registry()
    assert {m["id"] for m in payload["measures"]} == set(registry.measures)
    for m in payload["measures"]:
        source_table = registry.measures[m["id"]].source_table
        expected_key = module.TABLE_DOMAINS.get(source_table)
        assert m["domain"] == expected_key, m["id"]
        if expected_key is None:
            assert m["domain_name"] is None, m["id"]
        else:
            expected_name = next(
                d.name for d in module.DOMAINS if d.key == expected_key
            )
            assert m["domain_name"] == expected_name, m["id"]


def test_measure_domain_anchor_real_registry():
    """现值锚：注册用户数所用表 cdm.dwd_cu_rgst_fin_di 已登记 -> 用户域 cu（§9 终态）。"""
    payload = ontology.ontology_payload()
    reg = next(m for m in payload["measures"] if m["id"] == "reg_user_cnt")
    assert reg["source_table"] == "cdm.dwd_cu_rgst_fin_di"
    assert reg["domain"] == "cu"
    assert reg["domain_name"] == "用户域"


def test_measure_caliber_matches_confirmations(client: TestClient):
    """版本行摘要与真实确认记录一致（数据态感知，同 T-FIX1 风格：不钉死具体值）。"""
    for m in _ontology(client)["measures"]:
        assert m["caliber"] == _expected_caliber(m["id"]), m["id"]


def test_measure_caliber_empty_confirmations_pending(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    """空确认记录（受控）：caliber = 登记顺序第一条关联规则 + registry 状态 + 明细全 None（待确认态）。"""
    controlled = tmp_path / "confirmations.json"
    controlled.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(ontology, "CONFIRMATIONS_PATH", controlled)

    payload = ontology.ontology_payload()
    from src.fortune_admin.trial import _RULE_MEASURES

    for m in payload["measures"]:
        caliber = m["caliber"]
        rule_ids = [rid for rid, mid in _RULE_MEASURES.items() if mid == m["id"]]
        assert caliber is not None, m["id"]  # 现值三个度量均有关联规则
        assert caliber["rule_id"] == rule_ids[0], m["id"]
        assert caliber["status"] == ontology.load_registry().rules[rule_ids[0]].status
        assert caliber["code"] is None and caliber["confirmer"] is None, m["id"]
        assert caliber["time"] is None and caliber["commit"] is None, m["id"]


def test_measure_without_related_rules_caliber_none():
    """无关联规则 -> caliber None（不造待确认假锚，不造数据）。"""
    assert ontology._measure_caliber([], {}, {}) is None
