"""B1 验收测试：对象索引 / 对象查询 / 详情 / 链接遍历（技术方案 §3.1 index+query、§3.2）。

- index：启动从源库全量加载（§7.4 取舍），PK→对象（含 derived 计算态），链接正/反向索引；
- query：list_objects（等值过滤/分页）、get_detail（属性+链接计数）、get_links（双向遍历）；
- §2.7 derived 字段（available_qty / line_total_cents）计算态永不写。
"""

import shutil
import sqlite3

import pytest

from data import seed_retail_source as seed
from src.ontology import build_registry
from src.runtime.index import ObjectIndex
from src.runtime.query import (
    InvalidDirection,
    LinkNotFound,
    ObjectNotFound,
    ObjectQuery,
    UnknownFilterField,
    UnknownObjectType,
)

ORD_1001 = "ORD-1001"  # confirmed：SKU-003×3 + SKU-004×2（seed 预置，可取消演示）


@pytest.fixture(scope="module")
def seed_db_path(tmp_path_factory):
    """临时源系统库（不写正式种子库，防并行竞态；参考 test_b2 的 tmp 正例）。"""
    return seed.build_database(tmp_path_factory.mktemp("b1") / "source.db")


@pytest.fixture(scope="module")
def index(seed_db_path) -> ObjectIndex:
    reg = build_registry()
    idx = ObjectIndex(reg)
    conn = sqlite3.connect(seed_db_path)
    conn.row_factory = sqlite3.Row
    idx.load_all(conn)
    conn.close()
    return idx


@pytest.fixture(scope="module")
def query(index: ObjectIndex) -> ObjectQuery:
    return ObjectQuery(index, build_registry())


@pytest.fixture(scope="module")
def source_conn(seed_db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(seed_db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ---------- 加载与对象读取 ----------


def test_index_load_counts_match_source(index, source_conn):
    """索引行数 = 源库各表行数（8 对象全量加载）。"""
    tables = [
        "customers",
        "products",
        "warehouses",
        "inventory",
        "orders",
        "order_items",
        "shipments",
        "refunds",
    ]
    for table in tables:
        obj_type = {
            "customers": "Customer",
            "products": "Product",
            "warehouses": "Warehouse",
            "inventory": "Inventory",
            "orders": "Order",
            "order_items": "OrderItem",
            "shipments": "Shipment",
            "refunds": "Refund",
        }[table]
        n_source = source_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert len(index.list_all(obj_type)) == n_source, f"{obj_type} 行数不一致"


def test_get_inventory_derived_available_qty(index):
    """Inventory.available_qty = on_hand - reserved（derived 计算态，corner ①=30）。"""
    inv = index.get("Inventory", f"{seed.MAIN_WAREHOUSE_ID}|{seed.SHORTAGE_SKU_ID}")
    assert inv is not None
    assert inv["available_qty"] == 30


def test_get_order_item_derived_line_total(index):
    """OrderItem.line_total_cents = qty × unit_price（derived）。"""
    items = index.get_links("Order", ORD_1001, "order.items", "out")
    assert len(items) == 2
    for it in items:
        assert it["line_total_cents"] == it["qty"] * it["unit_price_cents"]


def test_get_missing_returns_none(index):
    assert index.get("Order", "ORD-NOPE") is None


def test_get_unknown_type_returns_none(index):
    """索引层对未知类型返回 None；类型合法性由 query 层 resolve_type 保证。"""
    assert index.get("Ghost", "x") is None


def test_ontology_state_merge(index):
    """ontology-owned 状态（cancel_reason）由 set_ontology_state 写入、get 合并（§2.7）。"""
    index.set_ontology_state("Order", ORD_1001, "cancel_reason", "客户改主意")
    order = index.get("Order", ORD_1001)
    assert order["cancel_reason"] == "客户改主意"
    # 清理，避免影响其他测试
    index.set_ontology_state("Order", ORD_1001, "cancel_reason", None)


# ---------- 对象查询（list/filter/分页） ----------


def test_list_objects_filter_and_pagination(query, source_conn):
    """等值过滤 + 分页 + total（MVP 过滤：等值与枚举，§3.2）。"""
    n_confirmed = source_conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status='confirmed'"
    ).fetchone()[0]
    page1, total = query.list_objects(
        "Order", filters={"status": "confirmed"}, page=1, page_size=10
    )
    assert total == n_confirmed
    assert len(page1) == 10
    pks1 = [it["pk"] for it in page1]
    assert pks1 == sorted(pks1), "分页结果应按主键升序（确定性）"
    page2, _ = query.list_objects(
        "Order", filters={"status": "confirmed"}, page=2, page_size=10
    )
    assert [it["pk"] for it in page2] != pks1


def test_list_objects_filter_on_derived(query):
    """derived 字段可过滤：available_qty == 30（缺货样本）。"""
    items, total = query.list_objects("Inventory", filters={"available_qty": 30})
    assert total >= 1
    assert all(it["properties"]["available_qty"] == 30 for it in items)


def test_list_objects_unknown_type_raises(query):
    with pytest.raises(UnknownObjectType):
        query.list_objects("Ghost")


def test_list_objects_unknown_filter_field_raises(query):
    with pytest.raises(UnknownFilterField):
        query.list_objects("Order", filters={"no_such_field": 1})


# ---------- 详情与链接计数 ----------


def test_get_detail_shape_and_link_counts(query, source_conn):
    """Order 详情：全属性 + out（order.customer/order.items）+ in（order.shipments 等）。"""
    detail = query.get_detail("Order", ORD_1001)
    assert detail["object_type"] == "Order"
    assert detail["pk"] == ORD_1001
    props = detail["properties"]
    assert props["status"] == "confirmed"
    links = detail["links"]
    # out：本对象出发（order.customer / order.items）
    assert links["out"]["order.customer"] == 1
    assert links["out"]["order.items"] == 2
    # out 也含 target 侧反向名（order.shipments / order.refunds）
    assert links["out"]["order.shipments"] == 0
    assert links["out"]["order.refunds"] == 0
    # in：指向本对象（items 经 order_item.order；shipments/refunds 经 L.name）
    assert links["in"]["order_item.order"] == 2
    assert links["in"]["shipment.order"] == 0
    assert links["in"]["refund.order"] == 0
    # 源库一致：该订单行数
    n_items = source_conn.execute(
        "SELECT COUNT(*) FROM order_items WHERE order_id=?", (ORD_1001,)
    ).fetchone()[0]
    assert n_items == 2


def test_get_detail_customer_incoming_orders(query, source_conn):
    """Customer 详情：out 为空、in 含 customer.orders（订单数 = 源库该客户订单数）。"""
    cus = source_conn.execute(
        "SELECT customer_id FROM orders WHERE order_id=?", (ORD_1001,)
    ).fetchone()["customer_id"]
    detail = query.get_detail("Customer", cus)
    # out：从 Customer 出发经反向名 customer.orders；in：order.customer 指向它
    n_orders = source_conn.execute(
        "SELECT COUNT(*) FROM orders WHERE customer_id=?", (cus,)
    ).fetchone()[0]
    assert detail["links"]["out"]["customer.orders"] == n_orders
    assert detail["links"]["in"]["order.customer"] == n_orders


def test_get_detail_unknown_pk_raises(query):
    with pytest.raises(ObjectNotFound):
        query.get_detail("Order", "ORD-NOPE")


# ---------- 链接遍历（双向） ----------


def test_traverse_out_order_items(query):
    objs = query.get_links("Order", ORD_1001, "order.items", "out")
    assert len(objs) == 2
    assert {o["object_type"] for o in objs} == {"OrderItem"}
    qty_by_product = {
        o["properties"]["product_id"]: o["properties"]["qty"] for o in objs
    }
    assert qty_by_product == {"SKU-003": 3, "SKU-004": 2}


def test_traverse_out_order_customer(query):
    objs = query.get_links("Order", ORD_1001, "order.customer", "out")
    assert len(objs) == 1
    assert objs[0]["object_type"] == "Customer"
    assert objs[0]["properties"]["customer_id"] == objs[0]["pk"]


def test_traverse_in_customer_orders(query, source_conn):
    """Customer → order.customer（in 方向：指向该客户的订单）。"""
    cus = source_conn.execute(
        "SELECT customer_id FROM orders WHERE order_id=?", (ORD_1001,)
    ).fetchone()["customer_id"]
    objs = query.get_links("Customer", cus, "order.customer", "in")
    assert objs, "客户应有订单"
    assert all(o["object_type"] == "Order" for o in objs)
    n = source_conn.execute(
        "SELECT COUNT(*) FROM orders WHERE customer_id=?", (cus,)
    ).fetchone()[0]
    assert len(objs) == n


def test_traverse_in_order_customer(query, source_conn):
    """TD-14 修复：Order 的入向链接（customer.orders）应返回其客户（此前为空）。"""
    cus = source_conn.execute(
        "SELECT customer_id FROM orders WHERE order_id=?", (ORD_1001,)
    ).fetchone()["customer_id"]
    objs = query.get_links("Order", ORD_1001, "customer.orders", "in")
    assert len(objs) == 1
    assert objs[0]["object_type"] == "Customer"
    assert objs[0]["pk"] == cus


def test_traverse_out_unknown_link_raises(query):
    with pytest.raises(LinkNotFound):
        query.get_links("Order", ORD_1001, "order.ghost", "out")


def test_traverse_bad_direction_raises(query):
    with pytest.raises(InvalidDirection):
        query.get_links("Order", ORD_1001, "order.items", "sideways")


def test_traverse_wrong_endpoint_raises(query):
    """从错误端点遍历（Order 不是 order.customer 的目标侧）应报 LinkNotFound。"""
    with pytest.raises(LinkNotFound):
        query.get_links("Order", ORD_1001, "customer.orders", "out")


# ---------- 增量更新（动作后同步，§3.3 ⑦） ----------


def test_refresh_updates_row_and_links(index, seed_db_path, tmp_path):
    """refresh：源库行变更后增量更新对象与链接（不重建全索引）。

    在 tmp 拷贝上改行（不碰模块级 index 与种子库，防污染后续测试）。
    """
    db_path = tmp_path / "refresh.db"
    shutil.copy(seed_db_path, db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # 用一个新索引避免污染 module 级 index
    idx = ObjectIndex(build_registry())
    idx.load_all(conn)
    assert idx.get("Order", ORD_1001)["status"] == "confirmed"
    conn.execute(
        "UPDATE orders SET status='cancelled', updated_at='2026-08-14 12:00:00' WHERE order_id=?",
        (ORD_1001,),
    )
    conn.commit()
    idx.refresh("Order", ORD_1001, conn)
    assert idx.get("Order", ORD_1001)["status"] == "cancelled"
    # 链接不受影响（FK 未变：客户/行数仍一致）
    assert len(idx.get_links("Order", ORD_1001, "order.items", "out")) == 2
    conn.close()
