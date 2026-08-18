"""P1 建模验收测试（蓝图 v0.3 §9-P1 / 补丁 A1/E4 + 蓝图 §5 API）。

覆盖：
1. object_types / link_types CRUD（GET 列表含 category 筛选 / POST / GET 单个 / PUT / DELETE 仅 draft）；
2. E4 状态机：draft -> reviewed -> published；非法流转 4xx；
3. publish 校验：property_schema 必须是合法 JSON Schema（含 name/PK 字段）；
4. A1 单向流入 Registry：published 行 -> create_model 动态注册进内存 Registry；
5. 冲突检测：builder 名与内置 OBJECT_TYPES 同名 -> 报 error 级 issue + 不入 Registry；
6. 启动聚合：动态类型出现在 /meta/schema；现有 8 内置行为零变化。

约定：临时库隔离，不污染 data/ontology/ontology.db。
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ----------------------------------------------------------------------
# 公共 fixture：seed 源库 + builder 表已建
# ----------------------------------------------------------------------


@pytest.fixture(scope="session")
def seed_db_path_p1(tmp_path_factory):
    """session 范围建一次源库（避免每个测试都重 seed 慢）。"""
    from data import seed_retail_source as seed

    path = tmp_path_factory.mktemp("seed_p1") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def builder_client(tmp_path: Path, seed_db_path_p1: Path):
    """复用现有 create_app 模式 + 临时本体库。"""
    from src.api.main import create_app

    source = tmp_path / "source.db"
    shutil.copy(seed_db_path_p1, source)
    app = create_app(source_db=source, ontology_db=tmp_path / "ontology.db")
    with TestClient(app) as c:
        yield c


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _sample_property_schema(pk: str = "id") -> dict:
    """合法的 property_schema：name (PK) + 一些示例字段。"""
    return {
        "type": "object",
        "properties": {
            pk: {"type": "string", "description": "主键"},
            "label": {"type": "string", "description": "标题"},
            "status": {"type": "string", "enum": ["active", "archived"]},
        },
        "required": [pk, "label"],
    }


def _create_object_type_payload(**overrides) -> dict:
    payload = {
        "ontology_id": "default",
        "name": _new_id("Ot"),
        "name_cn": "测试对象",
        "description": "P1 测试对象类型",
        "category": "domain",
        "property_schema": _sample_property_schema(),
    }
    payload.update(overrides)
    return payload


# ======================================================================
# 1. object_types CRUD
# ======================================================================


def test_create_object_type_returns_201_and_persists(builder_client):
    body = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    assert body["outcome"] == "ok"
    ot = body["data"]
    assert ot["status"] == "draft"
    assert ot["id"]
    # 持久化（GET 详情可拿回）
    got = builder_client.get(f"/api/v1/builder/object-types/{ot['id']}").json()
    assert got["outcome"] == "ok"
    assert got["data"]["name"] == ot["name"]


def test_list_object_types_filter_by_category(builder_client):
    p1 = _create_object_type_payload(category="domain")
    p2 = _create_object_type_payload(category="artifact", name=_new_id("Artifact"))
    builder_client.post("/api/v1/builder/object-types", json=p1)
    builder_client.post("/api/v1/builder/object-types", json=p2)
    resp = builder_client.get("/api/v1/builder/object-types?category=domain").json()
    cats = {o["category"] for o in resp["data"]["items"]}
    assert cats == {"domain"}


def test_get_object_type_not_found(builder_client):
    resp = builder_client.get("/api/v1/builder/object-types/nope")
    assert resp.status_code == 404
    body = resp.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "BUILDER_OBJECT_TYPE_NOT_FOUND"


def test_update_object_type_draft_only(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types",
        json=_create_object_type_payload(name_cn="初稿"),
    ).json()
    ot_id = create["data"]["id"]
    upd = builder_client.put(
        f"/api/v1/builder/object-types/{ot_id}",
        json={"name_cn": "改名了"},
    ).json()
    assert upd["outcome"] == "ok"
    assert upd["data"]["name_cn"] == "改名了"


def test_delete_object_type_draft_works(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    resp = builder_client.delete(f"/api/v1/builder/object-types/{ot_id}")
    assert resp.status_code == 200
    # 二次 GET 应 404
    again = builder_client.get(f"/api/v1/builder/object-types/{ot_id}")
    assert again.status_code == 404


def test_create_object_type_rejects_bad_category(builder_client):
    resp = builder_client.post(
        "/api/v1/builder/object-types",
        json=_create_object_type_payload(category="unknown_kind"),
    )
    # 业务级 4xx（BUILDER_INVALID_REQUEST 400）；不走 FastAPI 默认 422
    # 因为 API 层在 endpoint 内显式 try/except ValidationError 映射到 envelope
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_INVALID_REQUEST"


def test_create_object_type_rejects_bad_json_schema(builder_client):
    payload = _create_object_type_payload(
        property_schema={"type": "not-a-schema"}
    )
    resp = builder_client.post("/api/v1/builder/object-types", json=payload)
    # property_schema 缺 type=object（API 层 _coerce_json 通过后端 validator 拦）
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_INVALID_PROPERTY_SCHEMA"


# ======================================================================
# 2. E4 状态机
# ======================================================================


def _publish_object_type(client, **overrides) -> dict:
    """建 + review + publish 一条龙，返回最终 published 行。"""
    payload = _create_object_type_payload(**overrides)
    create = client.post("/api/v1/builder/object-types", json=payload).json()
    ot_id = create["data"]["id"]
    r1 = client.post(f"/api/v1/builder/object-types/{ot_id}/review").json()
    assert r1["outcome"] == "ok", r1
    r2 = client.post(f"/api/v1/builder/object-types/{ot_id}/publish").json()
    assert r2["outcome"] == "ok", r2
    return r2["data"]


def test_review_draft_to_reviewed(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    body = builder_client.post(
        f"/api/v1/builder/object-types/{ot_id}/review"
    ).json()
    assert body["outcome"] == "ok"
    assert body["data"]["status"] == "reviewed"


def test_publish_reviewed_to_published(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    builder_client.post(f"/api/v1/builder/object-types/{ot_id}/review")
    body = builder_client.post(
        f"/api/v1/builder/object-types/{ot_id}/publish"
    ).json()
    assert body["outcome"] == "ok"
    assert body["data"]["status"] == "published"


def test_publish_from_draft_rejected(builder_client):
    """draft 不能直接 published，必须先 reviewed。"""
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    resp = builder_client.post(
        f"/api/v1/builder/object-types/{ot_id}/publish"
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_INVALID_STATUS_TRANSITION"


def test_review_twice_rejected(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    builder_client.post(f"/api/v1/builder/object-types/{ot_id}/review")
    resp = builder_client.post(
        f"/api/v1/builder/object-types/{ot_id}/review"
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_INVALID_STATUS_TRANSITION"


def test_published_cannot_delete(builder_client):
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    builder_client.post(f"/api/v1/builder/object-types/{ot_id}/review")
    builder_client.post(f"/api/v1/builder/object-types/{ot_id}/publish")
    resp = builder_client.delete(f"/api/v1/builder/object-types/{ot_id}")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_DELETE_NOT_ALLOWED"


def test_publish_validates_property_schema(builder_client):
    """publish 时再校验一次 property_schema（POST 时只粗校验）。"""
    # 先建一个合法 draft，但随后手动改 DB 让 property_schema 不合法
    create = builder_client.post(
        "/api/v1/builder/object-types", json=_create_object_type_payload()
    ).json()
    ot_id = create["data"]["id"]
    # 直接改库塞非法 schema
    rt = builder_client.app.state.runtime
    with rt.store.ontology_conn() as conn:
        conn.execute(
            "UPDATE object_types SET property_schema=? WHERE id=?",
            ("{\"type\": \"garbage\"}", ot_id),
        )
        conn.commit()
    builder_client.post(f"/api/v1/builder/object-types/{ot_id}/review")
    resp = builder_client.post(
        f"/api/v1/builder/object-types/{ot_id}/publish"
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_INVALID_PROPERTY_SCHEMA"


# ======================================================================
# 3. link_types CRUD + publish 校验
# ======================================================================


def _create_object_type(client, **overrides) -> dict:
    payload = _create_object_type_payload(**overrides)
    return client.post("/api/v1/builder/object-types", json=payload).json()["data"]


def _publish_object(client, **overrides) -> dict:
    return _publish_object_type(client, **overrides)


def _create_link_payload(source_name: str, target_name: str, **overrides) -> dict:
    payload = {
        "ontology_id": "default",
        "name": f"{source_name}.test_{_new_id('lt').lower()}",
        "semantic_name": "测试链接",
        "category": "semantic",
        "source_type_id": source_name,
        "target_type_id": target_name,
        "cardinality": "1:N",
    }
    payload.update(overrides)
    return payload


def test_link_type_create_requires_existing_source_and_target(builder_client):
    src = _publish_object(builder_client, name=_new_id("Src"))
    tgt = _publish_object(builder_client, name=_new_id("Tgt"))
    payload = _create_link_payload(src["id"], tgt["id"])
    body = builder_client.post("/api/v1/builder/link-types", json=payload).json()
    assert body["outcome"] == "ok", body
    assert body["data"]["status"] == "draft"


def test_link_type_create_rejects_unknown_source(builder_client):
    tgt = _publish_object(builder_client, name=_new_id("Tgt"))
    payload = _create_link_payload("ot_nope_does_not_exist", tgt["id"])
    resp = builder_client.post("/api/v1/builder/link-types", json=payload)
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body["error"]["code"] == "BUILDER_UNKNOWN_SOURCE_TYPE"


def test_link_type_publish_state_machine(builder_client):
    src = _publish_object(builder_client, name=_new_id("Src"))
    tgt = _publish_object(builder_client, name=_new_id("Tgt"))
    payload = _create_link_payload(src["id"], tgt["id"])
    lt_id = builder_client.post(
        "/api/v1/builder/link-types", json=payload
    ).json()["data"]["id"]
    # draft -> reviewed -> published
    builder_client.post(f"/api/v1/builder/link-types/{lt_id}/review")
    body = builder_client.post(
        f"/api/v1/builder/link-types/{lt_id}/publish"
    ).json()
    assert body["outcome"] == "ok", body
    assert body["data"]["status"] == "published"


# ======================================================================
# 4. A1 启动合并 + 冲突检测
# ======================================================================


def test_dynamic_type_appears_in_meta_schema(builder_client):
    """published 行 -> 动态注册进内存 Registry -> 出现在 /meta/schema。"""
    pub = _publish_object_type(builder_client)
    body = builder_client.get("/meta/schema").json()
    names = {o["name"] for o in body["data"]["objects"]}
    assert pub["name"] in names, f"动态类型 {pub['name']} 应出现在 /meta/schema"
    # 内置 8 个类型不丢
    assert {"Customer", "Product", "Order"}.issubset(names)


def test_draft_type_not_in_registry(builder_client):
    """draft 行不进入内存 Registry。"""
    create = builder_client.post(
        "/api/v1/builder/object-types",
        json=_create_object_type_payload(name=_new_id("Draft")),
    ).json()
    name = create["data"]["name"]
    body = builder_client.get("/meta/schema").json()
    names = {o["name"] for o in body["data"]["objects"]}
    assert name not in names


def test_builder_name_conflict_with_builtin_logs_issue(builder_client, tmp_path):
    """builder 类型与内置同名 -> POST 即拒 + publish 也会拒（双保险）。"""
    # POST 阶段就被冲突检测拦下
    create_resp = builder_client.post(
        "/api/v1/builder/object-types",
        json=_create_object_type_payload(name="Customer"),
    )
    assert create_resp.status_code == 400, create_resp.text
    create = create_resp.json()
    assert create["error"]["code"] == "BUILDER_NAME_CONFLICT"
    # 内存 Registry 中没有第二个 Customer
    body_schema = builder_client.get("/meta/schema").json()
    customers = [o for o in body_schema["data"]["objects"] if o["name"] == "Customer"]
    assert len(customers) == 1, "内置 Customer 应仍是唯一"


def test_builtin_types_unchanged_after_loader(builder_client):
    """loader 不破坏现有 8 内置类型（零回归铁律）。"""
    body = builder_client.get("/meta/schema").json()
    objs = {o["name"] for o in body["data"]["objects"]}
    assert {
        "Customer",
        "Product",
        "Warehouse",
        "Inventory",
        "Order",
        "OrderItem",
        "Shipment",
        "Refund",
    }.issubset(objs)


def test_loader_uses_create_model_for_property_schema(tmp_path):
    """动态类型生成的 Pydantic model 应能实例化（不是 stub）。"""
    import tempfile

    from data import seed_retail_source as seed

    with tempfile.TemporaryDirectory() as td:
        src_db = Path(td) / "src.db"
        seed.build_database(src_db)
        from src.api.main import create_app

        app = create_app(
            source_db=src_db,
            ontology_db=Path(td) / "ont.db",
        )
        client = TestClient(app)
        pub = _publish_object_type(client)
        # 拉一次详情，看 model 字段（property_schema 真的实例化）
        got = client.get("/meta/schema").json()
        for o in got["data"]["objects"]:
            if o["name"] == pub["name"]:
                props = o["properties"]
                assert "id" in props, "动态类型应含 PK 字段 id"
                assert "label" in props, "动态类型应含 label 字段"
                return
        pytest.fail(f"动态类型 {pub['name']} 不在 /meta/schema 中")


# ======================================================================
# 5. 错误码 + 信封一致性
# ======================================================================


def test_object_type_not_found_uses_envelope(builder_client):
    resp = builder_client.get("/api/v1/builder/object-types/nope")
    assert resp.status_code == 404
    body = resp.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"]
    assert body["request_id"]


def test_builder_error_codes_use_builder_prefix(builder_client):
    """所有 BUILDER_* 错误码在 schemas.ERROR_MESSAGES 中应有中文消息。"""
    from src.api.schemas import ERROR_MESSAGES

    expected = {
        "BUILDER_OBJECT_TYPE_NOT_FOUND",
        "BUILDER_INVALID_PROPERTY_SCHEMA",
        "BUILDER_INVALID_STATUS_TRANSITION",
        "BUILDER_DELETE_NOT_ALLOWED",
        "BUILDER_NAME_CONFLICT",
        "BUILDER_UNKNOWN_SOURCE_TYPE",
        "BUILDER_UNKNOWN_TARGET_TYPE",
        "BUILDER_INVALID_REQUEST",
        "BUILDER_LINK_TYPE_NOT_FOUND",
    }
    missing = expected - set(ERROR_MESSAGES)
    assert not missing, f"错误码未在 ERROR_MESSAGES 注册：{missing}"


# ======================================================================
# 6. 单元测试（避免 fixture 启动整个 app，聚焦模块逻辑）
# ======================================================================


def test_publish_validator_requires_pk_in_property_schema(tmp_path):
    """纯单元：property_schema 缺 required 字段应失败。"""
    from src.builder.publish_validator import validate_object_type

    class _Row:
        name = "X"
        # 有 properties 但无 required → 必失败（缺 PK）
        property_schema = json.dumps(
            {"type": "object", "properties": {"foo": {"type": "string"}}}
        )
        pk_field = "id"
        category = "domain"

    err = validate_object_type(_Row())
    assert err is not None
    # 错误消息中文含"主键"，英文 lower 后含 pk
    assert "主键" in err or "pk" in err.lower()


def test_status_machine_blocks_illegal_transitions():
    from src.builder.status_machine import (
        IllegalTransitionError,
        assert_transition,
    )

    # 合法
    assert_transition("draft", "reviewed")
    assert_transition("reviewed", "published")
    # 非法
    with pytest.raises(IllegalTransitionError):
        assert_transition("draft", "published")
    with pytest.raises(IllegalTransitionError):
        assert_transition("published", "draft")
    with pytest.raises(IllegalTransitionError):
        assert_transition("published", "reviewed")


def test_registry_loader_skips_conflicting_name(tmp_path):
    """纯单元：loader 跳过与 builtin 同名行。"""
    from src.builder.registry_loader import load_published_into_registry

    # 准备本体库 + 一行 published name="Customer"
    db = tmp_path / "ont.db"
    from src.runtime.store import init_builder_schema

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    init_builder_schema(conn)
    conn.execute(
        "INSERT INTO object_types (id, ontology_id, name, name_cn, description, "
        "category, property_schema, status, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            "ot_conflict",
            "default",
            "Customer",
            "冲突",
            "与内置冲突",
            "domain",
            json.dumps(_sample_property_schema()),
            "published",
            "2026-01-01 00:00:00",
            "2026-01-01 00:00:00",
        ),
    )
    conn.commit()
    conn.close()
    # 用真 registry
    from src.ontology import build_registry

    base = build_registry()
    result = load_published_into_registry(db, base)
    # 冲突检测：issues 至少 1 条 error
    assert any(i["code"] == "BUILDER_NAME_CONFLICT" for i in result["issues"])
    # Customer 在 Registry 中只有 1 个
    customers = [o for o in base.object_types() if o.name == "Customer"]
    assert len(customers) == 1


def test_registry_loader_registers_unique_published(tmp_path):
    from src.builder.registry_loader import load_published_into_registry
    from src.ontology import build_registry
    from src.runtime.store import init_builder_schema

    db = tmp_path / "ont.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    init_builder_schema(conn)
    new_name = _new_id("Dyn")
    conn.execute(
        "INSERT INTO object_types (id, ontology_id, name, name_cn, description, "
        "category, property_schema, status, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            "ot_ok",
            "default",
            new_name,
            "动态类型",
            "loader 单测",
            "domain",
            json.dumps(_sample_property_schema()),
            "published",
            "2026-01-01 00:00:00",
            "2026-01-01 00:00:00",
        ),
    )
    conn.commit()
    conn.close()
    base = build_registry()
    result = load_published_into_registry(db, base)
    assert any(i["code"] == "BUILDER_LOADED" for i in result["issues"])
    loaded = [o for o in base.object_types() if o.name == new_name]
    assert len(loaded) == 1
    # 动态类真能实例化（不是 stub）
    model_cls = loaded[0].model
    inst = model_cls(**{loaded[0].pk_field: "x1", "label": "测试"})
    assert inst.model_dump()[loaded[0].pk_field] == "x1"

# ======================================================================
# 7. 覆盖率补测：仓储负向路径 + conflict + publish_validator
# ======================================================================


def _fresh_ont_conn(tmp_path):
    conn = sqlite3.connect(tmp_path / "ont.db")
    conn.row_factory = sqlite3.Row
    from src.runtime.store import init_builder_schema
    init_builder_schema(conn)
    return conn


def test_object_type_repo_rejects_bad_category(tmp_path):
    from src.builder.object_types import create as ot_create
    conn = _fresh_ont_conn(tmp_path)
    with pytest.raises(ValueError, match="category"):
        ot_create(
            conn,
            ontology_id="default",
            name="X",
            name_cn="",
            description="",
            category="bogus",
            property_schema={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]},
        )


def test_object_type_repo_update_only_draft(tmp_path):
    from src.builder.object_types import create as ot_create
    from src.builder.object_types import transition_status, update
    conn = _fresh_ont_conn(tmp_path)
    row = ot_create(
        conn,
        ontology_id="default",
        name="X",
        name_cn="",
        description="",
        category="domain",
        property_schema={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]},
    )
    transition_status(conn, row.id, "reviewed")
    with pytest.raises(PermissionError, match="draft"):
        update(conn, row.id, {"name_cn": "改不动"})


def test_object_type_repo_delete_published_rejected(tmp_path):
    from src.builder.object_types import create as ot_create
    from src.builder.object_types import delete, transition_status
    conn = _fresh_ont_conn(tmp_path)
    row = ot_create(
        conn,
        ontology_id="default",
        name="X",
        name_cn="",
        description="",
        category="domain",
        property_schema={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]},
    )
    transition_status(conn, row.id, "reviewed")
    transition_status(conn, row.id, "published")
    with pytest.raises(PermissionError, match="published"):
        delete(conn, row.id)


def test_object_type_repo_illegal_transition(tmp_path):
    from src.builder.object_types import create as ot_create
    from src.builder.object_types import transition_status
    from src.builder.status_machine import IllegalTransitionError
    conn = _fresh_ont_conn(tmp_path)
    row = ot_create(
        conn,
        ontology_id="default",
        name="X",
        name_cn="",
        description="",
        category="domain",
        property_schema={"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]},
    )
    with pytest.raises(IllegalTransitionError):
        transition_status(conn, row.id, "published")


def test_link_type_repo_rejects_bad_enums(tmp_path):
    from src.builder.link_types import create as lt_create
    conn = _fresh_ont_conn(tmp_path)
    with pytest.raises(ValueError, match="link category"):
        lt_create(
            conn,
            ontology_id="default",
            name="x.y",
            semantic_name="",
            category="bogus",
            source_type_id="a",
            target_type_id="b",
            cardinality="1:N",
        )
    with pytest.raises(ValueError, match="cardinality"):
        lt_create(
            conn,
            ontology_id="default",
            name="x.y",
            semantic_name="",
            category="semantic",
            source_type_id="a",
            target_type_id="b",
            cardinality="bogus",
        )


def test_link_type_repo_full_lifecycle(tmp_path):
    from src.builder.link_types import (
        create as lt_create,
    )
    from src.builder.link_types import (
        delete,
        get,
        list_all,
        transition_status,
        update,
    )
    conn = _fresh_ont_conn(tmp_path)
    row = lt_create(
        conn,
        ontology_id="default",
        name="a.b",
        semantic_name="测试",
        category="semantic",
        source_type_id="a",
        target_type_id="b",
        cardinality="1:N",
    )
    assert get(conn, row.id) is not None
    listed, total = list_all(conn)
    assert total == 1
    assert isinstance(listed, list)
    transition_status(conn, row.id, "reviewed")
    with pytest.raises(PermissionError):
        update(conn, row.id, {"name": "new"})
    transition_status(conn, row.id, "published")
    with pytest.raises(PermissionError, match="published"):
        delete(conn, row.id)


def test_conflict_scan_returns_nothing_for_clean_db(tmp_path):
    from src.builder.conflict import scan_all_published
    db = tmp_path / "clean.db"
    conn = sqlite3.connect(db)
    from src.runtime.store import init_builder_schema
    init_builder_schema(conn)
    conn.close()
    issues = scan_all_published(db)
    assert issues == []


def test_publish_validator_link_self_loop_rejected():
    from src.builder.publish_validator import validate_link_type
    class _Row:
        name = "x.y"
        source_type_id = "A"
        target_type_id = "A"
        cardinality = "1:N"
        fk_field = ""
    err = validate_link_type(_Row(), {"A", "B"})
    assert err is not None
    assert "自环" in err


def test_publish_validator_link_bad_cardinality():
    from src.builder.publish_validator import validate_link_type
    class _Row:
        name = "x.y"
        source_type_id = "A"
        target_type_id = "B"
        cardinality = "WRONG"
        fk_field = ""
    err = validate_link_type(_Row(), {"A", "B"})
    assert err is not None
    assert "cardinality" in err.lower()


def test_publish_validator_object_type_bad_json_string():
    from src.builder.publish_validator import validate_object_type
    class _Row:
        name = "X"
        property_schema = "{not valid json"
        pk_field = "id"
        category = "domain"
    err = validate_object_type(_Row())
    assert err is not None
    assert "JSON" in err or "json" in err.lower()


def test_publish_validator_object_type_pk_wrong_type():
    from src.builder.publish_validator import validate_object_type
    class _Row:
        name = "X"
        property_schema = '{"type": "object", "properties": {"id": {"type": "weird"}}, "required": ["id"]}'
        pk_field = "id"
        category = "domain"
    err = validate_object_type(_Row())
    assert err is not None
    assert "type" in err.lower() or "主键" in err


def test_status_machine_allowed_next_and_is_terminal():
    from src.builder.status_machine import (
        DRAFT,
        PUBLISHED,
        REVIEWED,
        allowed_next,
        is_terminal,
    )
    assert allowed_next(DRAFT) == {"reviewed"}
    assert allowed_next(REVIEWED) == {"published"}
    assert allowed_next(PUBLISHED) == frozenset()
    assert is_terminal(PUBLISHED) is True
    assert is_terminal(DRAFT) is False
    assert allowed_next("unknown") == frozenset()


def test_registry_loader_handles_enum_property():
    from src.builder.registry_loader import _build_dynamic_model
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "color": {"type": "string", "enum": ["red", "green", "blue"]},
        },
        "required": ["id"],
    }
    m = _build_dynamic_model(schema, "EnumTest")
    inst = m(id="1", color="red")
    assert inst.color == "red"
    inst2 = m(id="2")
    assert inst2.color is None


def test_load_issue_dataclass_frozen():
    import dataclasses

    from src.builder.registry_loader import LoadIssue
    i = LoadIssue(code="X", severity="info", message="m")
    with pytest.raises((AttributeError, dataclasses.FrozenInstanceError)):
        i.code = "Y"  # frozen


def test_conflict_check_object_type_name_builtin_match():
    from src.builder.conflict import check_object_type_name_conflict
    conn = sqlite3.connect(":memory:")
    issue = check_object_type_name_conflict(conn, "Customer")
    assert issue is not None
    assert issue["code"] == "BUILDER_NAME_CONFLICT"
    assert check_object_type_name_conflict(conn, "BrandNew") is None
    conn.close()


def test_conflict_check_link_type_name_builtin_match():
    from src.builder.conflict import check_link_type_name_conflict
    conn = sqlite3.connect(":memory:")
    issue = check_link_type_name_conflict(conn, "order.customer")
    assert issue is not None
    assert check_link_type_name_conflict(conn, "weird.link") is None
    conn.close()

