"""B3 验收测试：FastAPI 语义接口（技术方案 §4）。

验收点：
- 全端点（meta/objects/actions/audit）+ 统一响应信封（§4.1）；
- 一切写操作只能经 POST /actions/{name}（无泛化 update，D-T3，§1.1/§5.2）；
- §4.3 错误码全集 17 码在 API 层有映射（错误码全集单测）；
- OpenAPI 自动生成（/openapi.json）。
"""
import json
import shutil

import pytest
from fastapi.testclient import TestClient

from data import seed_retail_source as seed
from src.api.main import create_app
from src.ontology.actions import CANONICAL_ERROR_CODES
from src.api.schemas import ERROR_CODE_HTTP_STATUS, ERROR_MESSAGES


@pytest.fixture(scope="session")
def seed_db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def client(tmp_path, seed_db_path):
    source = tmp_path / "source.db"
    shutil.copy(seed_db_path, source)
    app = create_app(source_db=source, ontology_db=tmp_path / "ontology.db")
    with TestClient(app) as c:
        yield c


def envelope(resp) -> dict:
    return resp.json()


def assert_ok(resp):
    body = envelope(resp)
    assert body["outcome"] == "ok", body
    return body


# ---------- /meta ----------

def test_meta_schema_counts(client):
    body = assert_ok(client.get("/meta/schema"))
    assert len(body["data"]["objects"]) == 8
    assert len(body["data"]["links"]) == 8
    assert len(body["data"]["actions"]) == 6


def test_meta_objects(client):
    body = assert_ok(client.get("/meta/objects"))
    names = {o["name"] for o in body["data"]}
    assert "Order" in names and "Inventory" in names
    order = next(o for o in body["data"] if o["name"] == "Order")
    assert order["pk_field"] == "order_id"
    assert "properties" in order and "status" in order["properties"]


def test_meta_actions_include_params_schema(client):
    body = assert_ok(client.get("/meta/actions"))
    names = {a["name"] for a in body["data"]}
    assert names == {"create_order", "confirm_order", "cancel_order",
                     "create_shipment", "adjust_inventory", "approve_refund"}
    cancel = next(a for a in body["data"] if a["name"] == "cancel_order")
    assert "order_id" in cancel["params_schema"]["properties"]
    assert cancel["params_schema"]["required"] == ["order_id"]
    refund = next(a for a in body["data"] if a["name"] == "approve_refund")
    assert refund["high_risk"] is True


# ---------- /objects ----------

def test_object_list_filter_pagination(client):
    body = assert_ok(client.get("/objects/Order", params={"status": "confirmed", "page": 1, "page_size": 5}))
    data = body["data"]
    assert data["total"] >= 100
    assert len(data["items"]) == 5
    assert all(i["properties"]["status"] == "confirmed" for i in data["items"])
    assert [i["pk"] for i in data["items"]] == sorted(i["pk"] for i in data["items"])


def test_object_list_accepts_api_name(client):
    body = assert_ok(client.get("/objects/order", params={"page_size": 3}))
    assert len(body["data"]["items"]) == 3


def test_object_list_unknown_type(client):
    resp = client.get("/objects/Ghost")
    assert resp.status_code == 404
    assert envelope(resp)["outcome"] == "error"
    assert envelope(resp)["error"]["code"] == "OBJECT_TYPE_NOT_FOUND"


def test_object_list_unknown_filter_field(client):
    resp = client.get("/objects/Order", params={"no_such_field": "x"})
    assert resp.status_code == 400
    assert envelope(resp)["error"]["code"] == "UNKNOWN_FILTER_FIELD"


def test_object_detail_with_link_counts(client):
    body = assert_ok(client.get("/objects/Order/ORD-1001"))
    data = body["data"]
    assert data["object_type"] == "Order" and data["pk"] == "ORD-1001"
    assert data["properties"]["status"] == "confirmed"
    assert data["links"]["out"]["order.customer"] == 1
    assert data["links"]["out"]["order.items"] == 2


def test_object_detail_not_found(client):
    resp = client.get("/objects/Order/ORD-NOPE")
    assert resp.status_code == 404
    assert envelope(resp)["error"]["code"] == "OBJECT_NOT_FOUND"


# ---------- 链接遍历 ----------

def test_link_traversal_out(client):
    body = assert_ok(client.get("/objects/Order/ORD-1001/links/order.items"))
    data = body["data"]
    assert data["link_name"] == "order.items" and data["direction"] == "out"
    assert len(data["objects"]) == 2


def test_link_traversal_in(client):
    cus = client.get("/objects/Order/ORD-1001").json()["data"]["properties"]["customer_id"]
    body = assert_ok(client.get(f"/objects/Customer/{cus}/links/order.customer",
                                params={"direction": "in"}))
    assert body["data"]["direction"] == "in"
    assert body["data"]["objects"]


def test_link_traversal_bad_direction(client):
    resp = client.get("/objects/Order/ORD-1001/links/order.items", params={"direction": "up"})
    assert resp.status_code == 400
    assert envelope(resp)["error"]["code"] == "INVALID_DIRECTION"


def test_link_traversal_unknown_link(client):
    resp = client.get("/objects/Order/ORD-1001/links/order.ghost")
    assert resp.status_code == 404
    assert envelope(resp)["error"]["code"] == "LINK_NOT_FOUND"


# ---------- /actions（唯一写入口） ----------

def test_post_action_applied_and_audit_replay(client):
    resp = client.post("/actions/cancel_order", json={"order_id": "ORD-1001", "reason": "改主意"})
    body = envelope(resp)
    assert resp.status_code == 200
    assert body["outcome"] == "applied"
    assert body["data"]["audit_id"]
    effects = body["data"]["effects"]
    assert any(e["object_type"] == "Order" and e["new"] == "cancelled" for e in effects)
    # 幂等重放：GET /actions/{audit_id} 回查
    replay = assert_ok(client.get(f"/actions/{body['data']['audit_id']}"))
    assert replay["data"]["outcome"] == "applied"
    assert replay["data"]["action_name"] == "cancel_order"


def test_post_action_rejected_business_200(client):
    """业务拒绝 = 200 + outcome=rejected（§4.2：非 4xx）。"""
    resp = client.post("/actions/cancel_order", json={"order_id": "ORD-2007"})
    assert resp.status_code == 200
    body = envelope(resp)
    assert body["outcome"] == "rejected"
    assert body["error"]["code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
    assert body["error"]["detail"]["shipment_ids"] == ["SHP-88"]


def test_post_action_unknown(client):
    resp = client.post("/actions/no_such", json={})
    body = envelope(resp)
    assert resp.status_code == 200 and body["outcome"] == "rejected"
    assert body["error"]["code"] == "UNKNOWN_ACTION"


def test_post_action_invalid_params(client):
    resp = client.post("/actions/create_order",
                       json={"customer_id": "CUS-0001", "items": [{"product_id": "SKU-003", "qty": 0}]})
    body = envelope(resp)
    assert body["outcome"] == "rejected" and body["error"]["code"] == "INVALID_PARAMS"


def test_post_action_malformed_json(client):
    resp = client.post("/actions/confirm_order", content="{not json", headers={"Content-Type": "application/json"})
    assert resp.status_code == 400
    assert envelope(resp)["error"]["code"] == "INVALID_REQUEST"


def test_post_action_echo_request_id(client):
    resp = client.post("/actions/confirm_order", json={"order_id": "ORD-0001"},
                       headers={"X-Request-ID": "req_abc123"})
    assert envelope(resp)["request_id"] == "req_abc123"


def test_action_create_order_end_to_end(client):
    """create_order → confirm_order → create_shipment 全链路（唯一写入口）。"""
    r1 = client.post("/actions/create_order",
                     json={"customer_id": "CUS-0001", "items": [{"product_id": "SKU-003", "qty": 2}]})
    assert envelope(r1)["outcome"] == "applied"
    order_id = envelope(r1)["data"]["effects"][0]["pk"]
    assert client.post("/actions/confirm_order", json={"order_id": order_id}).json()["outcome"] == "applied"
    r3 = client.post("/actions/create_shipment",
                     json={"order_id": order_id, "warehouse_id": seed.MAIN_WAREHOUSE_ID})
    assert envelope(r3)["outcome"] == "applied"
    detail = assert_ok(client.get(f"/objects/Order/{order_id}"))
    assert detail["data"]["properties"]["status"] == "shipped"


# ---------- /audit ----------

def test_audit_query_and_get(client):
    client.post("/actions/cancel_order", json={"order_id": "ORD-1001"})
    body = assert_ok(client.get("/audit", params={"action": "cancel_order"}))
    assert body["data"]["total"] == 1
    audit_id = body["data"]["items"][0]["audit_id"]
    single = assert_ok(client.get(f"/audit/{audit_id}"))
    assert single["data"]["outcome"] == "applied"
    assert json.loads(single["data"]["writeback_json"])


# ---------- 错误码全集映射（§4.3） ----------

def test_error_code_full_set_mapped():
    """17 个规范错误码全部有 API 层消息与 HTTP 状态映射。"""
    missing_msg = [c for c in CANONICAL_ERROR_CODES if not ERROR_MESSAGES.get(c)]
    missing_status = [c for c in CANONICAL_ERROR_CODES if c not in ERROR_CODE_HTTP_STATUS]
    assert missing_msg == [], f"缺消息: {missing_msg}"
    assert missing_status == [], f"缺状态映射: {missing_status}"
    # 业务码（§4.3 全集）在信封内以 200 返回，不产生 4xx 语义
    assert all(ERROR_CODE_HTTP_STATUS[c] == 200 for c in CANONICAL_ERROR_CODES)


# ---------- 无泛化写路径（D-T3，§1.1/§5.2） ----------

def test_no_generic_write_paths():
    """OpenAPI 中不存在对对象/字段的泛化写端点（无 PUT/PATCH/DELETE /objects）。"""
    openapi = TestClient(create_app()).get("/openapi.json").json()
    for path, methods in openapi["paths"].items():
        if path.startswith("/objects"):
            assert not ({"put", "patch", "delete", "post"} & set(methods)), f"泛化写路径: {path} {methods}"
    assert "/actions/{action_name}" in openapi["paths"]
    assert "post" in openapi["paths"]["/actions/{action_name}"]


# ---------- OpenAPI ----------

def test_openapi_generated(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.json()
    assert spec["info"]["title"] == "OntoRun 语义接口"
    paths = spec["paths"]
    for p in ["/meta/schema", "/meta/objects", "/meta/actions",
              "/objects/{type}", "/objects/{type}/{pk}",
              "/objects/{type}/{pk}/links/{link_name}",
              "/actions/{action_name}", "/audit", "/audit/{audit_id}"]:
        assert p in paths, f"OpenAPI 缺端点 {p}"
    # 动作参数 schema 进入 OpenAPI components
    assert "CreateOrderParams" in spec["components"]["schemas"]
