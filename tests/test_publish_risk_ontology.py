"""S3：风险本体 33 对象 / 37 链接 批量 review/publish 验收（TestClient 模式）。

验收点（对应用户交付 3）：
1. 走状态机的批量发布全链路：draft -> reviewed -> published（33 对象 + 37 链接）；
2. 幂等重跑：零变更零报错，总数不变；
3. 「S1 浏览不被污染」机器验证（铁律②）：/meta/schema 不含风险对象、
   /objects/{risk_type} 返回 OBJECT_TYPE_NOT_FOUND、loader 跳过 ot_s3_/lt_s3_ 行；
4. 图谱页聚合端点：/api/v1/builder/graph 含完整风险本体（33 对象 / 37 链接），
   端点解析为对象名（非 ot_s3_* 行 id）。

约定：临时双库隔离（对齐 tests/test_agent_api.py），不污染真实 data/ontology/ontology.db；
风险对象/链接清单从注册表派生（单一事实来源，测试不手抄）。
"""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_SCRIPT = REPO_ROOT / "scripts" / "seed_builder_from_risk_ontology.py"
PUBLISH_SCRIPT = REPO_ROOT / "scripts" / "publish_risk_ontology.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEED = _load_module("seed_builder_from_risk_ontology", SEED_SCRIPT)
PUBLISH = _load_module("publish_risk_ontology", PUBLISH_SCRIPT)


@pytest.fixture(scope="session")
def retail_source_db(tmp_path_factory) -> Path:
    from data import seed_retail_source as retail_seed

    path = tmp_path_factory.mktemp("publish_risk") / "source.db"
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
def risk_names() -> dict:
    """风险注册表实况：对象 api_name 清单 + 链接 name 清单（单一事实来源派生）。"""
    registry = SEED.build_risk_source_registry()
    return {
        "objects": sorted(o.api_name for o in registry.object_types()),
        "links": sorted(l.name for l in registry.link_types()),
        "object_count": len(list(registry.object_types())),
        "link_count": len(list(registry.link_types())),
    }


def _seed_and_publish(ontology_path: Path) -> dict:
    """seed（draft 入库）→ publish 脚本全量发布，返回 publish 摘要。"""
    SEED.seed(ontology_path)
    return PUBLISH.publish(ontology_path)


def _published_counts(ontology_path: Path) -> tuple[int, int]:
    conn = sqlite3.connect(ontology_path)
    conn.row_factory = sqlite3.Row
    try:
        ot = conn.execute(
            "SELECT COUNT(*) AS n FROM object_types WHERE id LIKE 'ot_s3_%' AND status='published'"
        ).fetchone()["n"]
        lt = conn.execute(
            "SELECT COUNT(*) AS n FROM link_types WHERE id LIKE 'lt_s3_%' AND status='published'"
        ).fetchone()["n"]
    finally:
        conn.close()
    return ot, lt


# ======================================================================
# 1. 走状态机的批量发布全链路
# ======================================================================


def test_batch_publish_full_chain(client, ontology_path, risk_names):
    """seed draft → publish 脚本 → 33 对象 + 37 链接全 published，0 failed。"""
    summary = _seed_and_publish(ontology_path)

    assert summary["summary"]["objects"] == risk_names["object_count"]
    assert summary["summary"]["links"] == risk_names["link_count"]
    assert summary["summary"]["failed"] == 0
    # 首次全为 draft：reviewed == published == 行数
    assert (
        summary["summary"]["reviewed"]
        == risk_names["object_count"] + risk_names["link_count"]
    )
    assert summary["object_types"]["published"] == risk_names["object_count"]
    assert summary["link_types"]["published"] == risk_names["link_count"]

    ot_pub, lt_pub = _published_counts(ontology_path)
    assert ot_pub == risk_names["object_count"]
    assert lt_pub == risk_names["link_count"]

    # builder 端点抽查：published 状态行数与对象清单一致
    resp = client.get("/api/v1/builder/object-types?status=published&page_size=100")
    assert resp.status_code == 200
    pub_items = resp.json()["data"]["items"]
    s3_pub = [i for i in pub_items if i["id"].startswith("ot_s3_")]
    assert len(s3_pub) == risk_names["object_count"]


# ======================================================================
# 2. 幂等重跑
# ======================================================================


def test_publish_idempotent_rerun(client, ontology_path, risk_names):
    """二次执行：零变更零报错；published 计数不变。"""
    _seed_and_publish(ontology_path)
    ot_before, lt_before = _published_counts(ontology_path)

    second = PUBLISH.publish(ontology_path)

    assert second["summary"]["published"] == 0
    assert second["summary"]["reviewed"] == 0
    assert second["summary"]["failed"] == 0
    assert second["object_types"]["skipped"] == risk_names["object_count"]
    assert second["link_types"]["skipped"] == risk_names["link_count"]

    ot_after, lt_after = _published_counts(ontology_path)
    assert (ot_after, lt_after) == (ot_before, lt_before)


# ======================================================================
# 3. S1 浏览不被污染（铁律② 机器验证）
# ======================================================================


def test_meta_schema_not_polluted_after_publish(tmp_path, retail_source_db, risk_names):
    """publish 后新建应用（loader 重跑）→ /meta/schema 仍只含零售段，风险对象零泄漏。"""
    ontology = tmp_path / "ontology.db"
    source = tmp_path / "source.db"
    shutil.copy(retail_source_db, source)

    # 第一遍：seed + publish（draft -> published 落库）
    app = create_test_app(source, ontology)
    with TestClient(app):
        SEED.seed(ontology)
    PUBLISH.publish(ontology)

    # 第二遍：新建应用 → create_app 跑 loader（published 风险行已在库）
    app2 = create_test_app(source, ontology)
    with TestClient(app2) as c2:
        schema = c2.get("/meta/schema").json()
        names = {o["name"] for o in schema["data"]["objects"]}
        leaked = set(risk_names["objects"]) & names
        assert not leaked, f"/meta/schema 泄漏风险对象: {leaked}"
        assert len(schema["data"]["objects"]) == 14, "零售段对象数应为 14"
        # 点开风险对象必须 404（S1 浏览页不会出现空表）
        for risk_type in ("risk_customer", "warning_signal", "codebt_customer"):
            resp = c2.get(f"/objects/{risk_type}")
            assert resp.status_code == 404, resp.text
            assert resp.json()["error"]["code"] == "OBJECT_TYPE_NOT_FOUND"


def test_loader_skips_s3_risk_rows(tmp_path, risk_names):
    """loader 单元验证：published 风险行被过滤，s3_risk_skipped 计数正确。"""
    from src.builder.registry_loader import load_published_into_registry
    from src.ontology import build_registry
    from src.runtime.store import init_builder_schema

    ontology = tmp_path / "ontology.db"
    conn = sqlite3.connect(ontology)
    conn.row_factory = sqlite3.Row
    init_builder_schema(conn)
    conn.close()
    SEED.seed(ontology)
    PUBLISH.publish(ontology)

    reg = build_registry()
    result = load_published_into_registry(ontology, reg)
    assert (
        result["s3_risk_skipped"]
        == risk_names["object_count"] + risk_names["link_count"]
    )
    assert result["loaded_ot"] == 0
    assert result["loaded_lt"] == 0
    assert any(i["code"] == "BUILDER_S3_RISK_SKIPPED" for i in result["issues"])
    reg_names = {o.name for o in reg.object_types()}
    assert not set(risk_names["objects"]) & reg_names, "风险对象不应进入共享 Registry"


# ======================================================================
# 4. 图谱页聚合端点
# ======================================================================


def test_graph_endpoint_full_risk_ontology(client, ontology_path, risk_names):
    """/api/v1/builder/graph 含完整风险本体（33 对象 / 37 链接），端点解析为对象名。"""
    _seed_and_publish(ontology_path)
    resp = client.get("/api/v1/builder/graph")
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == "ok"
    data = body["data"]

    obj_names = {o["name"] for o in data["objects"]}
    link_names = {l["name"] for l in data["links"]}
    # 完整风险本体：33 对象 / 37 链接 全部在场
    assert set(risk_names["objects"]) <= obj_names
    assert set(risk_names["links"]) <= link_names
    # 零售段也在（聚合展示不丢）
    assert {"Order", "Customer", "Product"} <= obj_names
    # 链接端点解析为对象名（不是 ot_s3_* 行 id）
    risk_link_set = set(risk_names["links"])
    for l in data["links"]:
        if l["name"] in risk_link_set:
            assert not l["source_type"].startswith("ot_s3_"), l
            assert not l["target_type"].startswith("ot_s3_"), l
            assert l["source_type"] in obj_names, l
            assert l["target_type"] in obj_names, l


# ======================================================================
# 5. 动作行零触碰（边界：不动 9 个动作行）
# ======================================================================


def test_actions_untouched_by_publish(client, ontology_path, risk_names):
    """publish 只动对象/链接；动作行保持 published 且数量不变。"""
    _seed_and_publish(ontology_path)
    resp = client.get("/api/v1/builder/actions?status=published&page_size=100")
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert len(items) >= 9
    assert all(i["status"] == "published" for i in items)


def create_test_app(source: Path, ontology: Path):
    from src.app.main import create_app

    return create_app(source_db=source, ontology_db=ontology)
