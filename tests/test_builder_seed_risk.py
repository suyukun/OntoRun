"""S3：风险本体 seed builder 存储层 —— smoke（Jack 验收口径）。

验收点：
- seed 后 GET /api/v1/builder/object-types total >= 33 且含 codebt_customer；
- GET /api/v1/builder/link-types total >= 37；
- GET /api/v1/builder/actions total >= 9（该端点存在；risk 动作名全覆盖）
- 幂等重跑不重复、总数不变；
- 同名冲突（模拟 S1/S2 或人工行）跳过不覆盖。

测试用 tmp 双库（fixture 模式对齐 tests/test_agent_api.py），不污染真实
data/ontology/ontology.db；阈值数字即任务清单值，风险动作名从注册表现取
（单一事实来源，不在测试里手抄清单）。
"""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "seed_builder_from_risk_ontology.py"


def _load_seed_module():
    spec = importlib.util.spec_from_file_location(
        "seed_builder_from_risk_ontology", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEED = _load_seed_module()


@pytest.fixture(scope="session")
def retail_source_db(tmp_path_factory) -> Path:
    from data import seed_retail_source as retail_seed

    path = tmp_path_factory.mktemp("builder_seed") / "source.db"
    retail_seed.build_database(path)
    return path


@pytest.fixture
def client(tmp_path, retail_source_db):
    from src.app.main import create_app

    app = create_app(source_db=retail_source_db, ontology_db=tmp_path / "ontology.db")
    with TestClient(app) as c:
        yield c


@pytest.fixture
def ontology_path(client, tmp_path) -> Path:
    return Path(client.app.state.runtime.store.ontology_path)


@pytest.fixture
def risk_counts() -> dict:
    """注册表实况计数与动作名（单一事实来源派生，测试不硬抄清单）。"""
    registry = SEED.build_risk_source_registry()
    return {
        "objects": len(registry.object_types()),
        "links": len(registry.link_types()),
        "actions": len(registry.actions()),
        "action_names": {a.name for a in registry.actions()},
    }


def _list_page(
    client: TestClient, url: str, *, page_size: int = 100
) -> tuple[int, list]:
    resp = client.get(url, params={"page_size": page_size})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["outcome"] == "ok"
    assert body["data"]["total"] == len(body["data"]["items"]), (
        f"{url}: total 与分页 items 数不一致（page_size 过小？）"
    )
    return body["data"]["total"], body["data"]["items"]


def test_seed_populates_all_three_builder_endpoints(client, ontology_path, risk_counts):
    """核心验收：seed 后三个 builder 列表端点非空且计数达标。"""
    summary = SEED.seed(ontology_path)
    assert summary["source"]["objects"] == risk_counts["objects"]
    assert summary["object_types"]["inserted"] == risk_counts["objects"]
    assert summary["link_types"]["inserted"] == risk_counts["links"]
    assert summary["action_types"]["created"] == risk_counts["actions"]

    ot_total, ot_items = _list_page(client, "/api/v1/builder/object-types")
    assert ot_total >= 33, f"object-types 总数不足 33: {ot_total}"
    api_names = [i["api_name"] for i in ot_items]
    assert "codebt_customer" in api_names, "缺 codebt_customer 行"
    # 行结构合法：status/category/property_schema 可被后续 publish 链路消费
    seeded_ot = [i for i in ot_items if i["id"].startswith("ot_s3_")]
    assert all(i["status"] == "draft" for i in seeded_ot)
    assert all(i["category"] in ("domain", "artifact", "conceptual") for i in seeded_ot)
    for i in seeded_ot:
        schema = i["property_schema"]
        assert schema["type"] == "object"
        assert i["pk_field"] in schema["properties"]
        assert i["pk_field"] == schema["required"][0]

    lt_total, lt_items = _list_page(client, "/api/v1/builder/link-types")
    assert lt_total >= 37, f"link-types 总数不足 37: {lt_total}"
    # seed 行用确定性 id 前缀识别（与源注册表计数精确对账）
    seeded_lt = [i for i in lt_items if i["id"].startswith("lt_s3_")]
    assert len(seeded_lt) == risk_counts["links"]
    assert all(i["cardinality"] in ("1:1", "1:N", "N:1", "N:M") for i in lt_items)
    assert all(i["fk_field"] for i in seeded_lt)

    at_total, at_items = _list_page(client, "/api/v1/builder/actions")
    assert at_total >= 9, f"actions 总数不足 9: {at_total}"
    got_action_names = {i["name"] for i in at_items}
    missing = risk_counts["action_names"] - got_action_names
    assert not missing, f"动作缺失: {missing}"


def test_seed_is_idempotent_on_rerun(client, ontology_path, risk_counts):
    """幂等：二次执行零新增，端点总数不变。"""
    SEED.seed(ontology_path)
    ot_first, _ = _list_page(client, "/api/v1/builder/object-types")
    lt_first, _ = _list_page(client, "/api/v1/builder/link-types")
    at_first, _ = _list_page(client, "/api/v1/builder/actions")

    second = SEED.seed(ontology_path)
    assert second["object_types"]["inserted"] == 0
    assert second["object_types"]["skipped"] == risk_counts["objects"]
    assert second["link_types"]["inserted"] == 0
    assert second["action_types"]["created"] == 0

    ot_second, _ = _list_page(client, "/api/v1/builder/object-types")
    lt_second, _ = _list_page(client, "/api/v1/builder/link-types")
    at_second, _ = _list_page(client, "/api/v1/builder/actions")
    assert (ot_second, lt_second, at_second) == (ot_first, lt_first, at_first)
    assert ot_first == risk_counts["objects"]  # tmp 库无其他干扰行


def test_seed_skips_same_name_conflict_rows(client, ontology_path):
    """冲突策略：同名异 id 的既有行跳过不覆盖；链接端点解析到旧行 id。"""
    conn = sqlite3.connect(ontology_path)
    conn.execute(
        "INSERT INTO object_types (id, ontology_id, name, name_cn, description, "
        "category, property_schema, status, created_at, updated_at) "
        "VALUES ('ot_manual_riskcustomer', 'default', 'risk_customer', '旧手工行', "
        "'x', 'domain', '{\"type\":\"object\"}', 'published', '2026-01-01', '2026-01-01')"
    )
    conn.commit()
    conn.close()

    summary = SEED.seed(ontology_path)

    # 34 - 1 冲突 = 33 条新增（S4 彩排修复 P0-1：sys_param 注册为可查询对象）；
    # risk_customer（RiskCustomer）保留人工行
    assert summary["object_types"]["inserted"] == 33
    conn = sqlite3.connect(ontology_path)
    kept = conn.execute(
        "SELECT id, status FROM object_types WHERE name = 'risk_customer'"
    ).fetchall()
    conn.close()
    assert [(r[0], r[1]) for r in kept] == [("ot_manual_riskcustomer", "published")]

    # 引用 RiskCustomer 端点的链接解析到既有行 id（详情端点按行 id 查）
    resp = client.get(
        f"/api/v1/builder/link-types/{SEED._lt_row_id('risk_customer.belongs_to_group')}"
    )
    assert resp.status_code == 200, resp.text
    row = resp.json()["data"]
    assert row["source_type_id"] == "ot_manual_riskcustomer"
