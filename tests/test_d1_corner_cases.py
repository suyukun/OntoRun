"""D1 验收测试：源系统库生成 + 4 类 corner case 样本断言 + 数据一致性不变量。

技术方案依据：§2.6 corner case 设计、§7.1 表结构、§7.2 seed 设计。
"""
import sqlite3

import pytest

from data import seed_retail_source as seed

# 4 类 corner case 的期望样本（与 data/seed_retail_source.py 中常量对应）
SHORTAGE_SKU_ID = "SKU-001"      # available = 30（缺货演示：要 100 件被拦）
ZERO_STOCK_SKU_ID = "SKU-002"    # on_hand = 0（零库存演示）
INTERCEPT_ORDER_ID = "ORD-2007"  # 已发货订单（拦截取消演示，对齐 §4.2 示例）
INTERCEPT_SHIPMENT_ID = "SHP-88"


@pytest.fixture(scope="module")
def conn() -> sqlite3.Connection:
    """在规范路径生成源系统库（确定性、幂等），并返回只读连接。"""
    db_path = seed.build_database()
    assert db_path.exists(), f"源系统库未生成: {db_path}"
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


# ---------- 4 类 corner case ----------

def test_corner_1_shortage_sku_exists(conn):
    """corner ①缺货：存在 available_qty == 30 的 active 商品（on_hand - reserved = 30）。"""
    row = conn.execute(
        "SELECT i.*, p.status FROM inventory i JOIN products p ON p.product_id = i.product_id "
        "WHERE i.product_id = ? AND i.warehouse_id = ?",
        (SHORTAGE_SKU_ID, seed.MAIN_WAREHOUSE_ID),
    ).fetchone()
    assert row is not None, "缺货样本 SKU-001 不存在"
    assert row["status"] == "active"
    assert row["on_hand_qty"] - row["reserved_qty"] == 30


def test_corner_2_shipped_order_exists(conn):
    """corner ②已发货：存在 status=shipped 的订单且有关联 shipment(status=shipped)。

    对齐技术方案 §4.2 示例：ORD-2007 / SHP-88 / 2026-08-12 出库，用于拦截取消演示。
    """
    row = conn.execute(
        "SELECT o.order_id, s.shipment_id, s.status AS ship_status "
        "FROM orders o JOIN shipments s ON s.order_id = o.order_id "
        "WHERE o.order_id = ?", (INTERCEPT_ORDER_ID,),
    ).fetchone()
    assert row is not None, "已发货拦截样本 ORD-2007 不存在"
    assert row["shipment_id"] == INTERCEPT_SHIPMENT_ID
    assert row["ship_status"] == "shipped"


def test_corner_3_pending_refund_exists(conn):
    """corner ③退款：pending 退款存在（双签演示），且含 1 笔超实付、1 笔已 approved（冲突演示）。"""
    pending = conn.execute("SELECT COUNT(*) AS n FROM refunds WHERE status='pending'").fetchone()["n"]
    assert pending >= 2, f"pending 退款应 ≥2 笔，实际 {pending}"
    # 超实付样本：amount > 对应订单 paid_cents
    over = conn.execute(
        "SELECT r.refund_id FROM refunds r JOIN orders o ON o.order_id = r.order_id "
        "WHERE r.status='pending' AND r.amount_cents > o.paid_cents LIMIT 1"
    ).fetchone()
    assert over is not None, "缺少超实付 pending 退款样本（AMOUNT_EXCEEDS_PAID 演示）"
    approved = conn.execute("SELECT COUNT(*) AS n FROM refunds WHERE status='approved'").fetchone()["n"]
    assert approved >= 1, "缺少已 approved 退款样本（REFUND_NOT_PENDING 冲突演示）"


def test_corner_4_zero_inventory_exists(conn):
    """corner ④零库存：存在 on_hand_qty == 0 的库存记录（active 商品）。"""
    row = conn.execute(
        "SELECT i.inventory_id FROM inventory i JOIN products p ON p.product_id = i.product_id "
        "WHERE i.on_hand_qty = 0 AND p.status = 'active' AND i.warehouse_id = ? LIMIT 1",
        (seed.MAIN_WAREHOUSE_ID,),
    ).fetchone()
    assert row is not None, "零库存样本不存在"


# ---------- 规模与一致性不变量 ----------

def test_scale_targets(conn):
    """§7.2 规模：几百客户 / 上千订单 / 几十商品 / 多仓库 / 有发货与退款。"""
    counts = {
        "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
        "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        "warehouses": conn.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "order_items": conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0],
        "shipments": conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0],
        "refunds": conn.execute("SELECT COUNT(*) FROM refunds").fetchone()[0],
    }
    assert counts["customers"] >= 200, counts
    assert counts["products"] >= 30, counts
    assert counts["warehouses"] >= 3, counts
    assert counts["orders"] >= 1000, counts
    assert counts["order_items"] >= 2000, counts
    assert counts["shipments"] >= 50, counts
    assert counts["refunds"] >= 20, counts


def test_inventory_never_negative(conn):
    """available_qty = on_hand - reserved 恒 ≥ 0（库存三态一致性底线）。"""
    bad = conn.execute(
        "SELECT COUNT(*) AS n FROM inventory WHERE on_hand_qty < 0 OR reserved_qty < 0 "
        "OR on_hand_qty - reserved_qty < 0"
    ).fetchone()["n"]
    assert bad == 0, f"存在非法库存 {bad} 行"


def test_order_total_matches_line_items(conn):
    """订单金额 = 行金额之和；实付 ≤ 总额；行价 = 商品快照价。"""
    bad = conn.execute(
        "SELECT o.order_id FROM orders o "
        "WHERE o.total_cents != (SELECT COALESCE(SUM(qty * unit_price_cents), 0) "
        "                         FROM order_items WHERE order_id = o.order_id) "
        "OR o.paid_cents > o.total_cents"
    ).fetchone()
    assert bad is None, f"金额不一致订单: {bad['order_id'] if bad else bad}"


def test_shipment_status_consistent_with_order(conn):
    """shipped/delivered/refunded 订单恰有 1 个 shipment；pending/confirmed/cancelled 为 0 个。"""
    with_ship = conn.execute(
        "SELECT o.order_id FROM orders o WHERE o.status IN ('shipped','delivered','refunded') "
        "AND (SELECT COUNT(*) FROM shipments s WHERE s.order_id = o.order_id) != 1 LIMIT 1"
    ).fetchone()
    assert with_ship is None, f"应有恰 1 个 shipment 的订单: {with_ship}"
    no_ship = conn.execute(
        "SELECT o.order_id FROM orders o WHERE o.status IN ('pending','confirmed','cancelled') "
        "AND (SELECT COUNT(*) FROM shipments s WHERE s.order_id = o.order_id) != 0 LIMIT 1"
    ).fetchone()
    assert no_ship is None, f"不应有 shipment 的订单: {no_ship}"


def test_refunded_orders_have_full_approved_refund(conn):
    """refunded 订单 = 已发货 + 恰 1 笔 approved 且金额等于实付（整单退款）。"""
    bad = conn.execute(
        "SELECT o.order_id FROM orders o WHERE o.status = 'refunded' AND NOT EXISTS ("
        "  SELECT 1 FROM refunds r WHERE r.order_id = o.order_id "
        "  AND r.status = 'approved' AND r.amount_cents = o.paid_cents"
        ") LIMIT 1"
    ).fetchone()
    assert bad is None, f"refunded 订单缺少整单 approved 退款: {bad}"


def test_all_order_statuses_present(conn):
    """§7.2：pending/confirmed/shipped/delivered/cancelled/refunded 各状态都要有。"""
    rows = conn.execute("SELECT status, COUNT(*) AS n FROM orders GROUP BY status").fetchall()
    present = {r["status"] for r in rows if r["n"] > 0}
    assert present == {"pending", "confirmed", "shipped", "delivered", "cancelled", "refunded"}, present


TABLE_PKS = {
    "customers": "customer_id", "products": "product_id", "warehouses": "warehouse_id",
    "inventory": "inventory_id", "orders": "order_id", "order_items": "order_item_id",
    "shipments": "shipment_id", "refunds": "refund_id",
}


def test_seed_is_deterministic(tmp_path):
    """同一 seed 两次生成，各表逐行内容一致（按主键排序全行比对，非仅行数）。"""
    db1 = seed.build_database(tmp_path / "a.db")
    db2 = seed.build_database(tmp_path / "b.db")
    for table, pk in TABLE_PKS.items():
        with sqlite3.connect(db1) as c1, sqlite3.connect(db2) as c2:
            rows1 = c1.execute(f"SELECT * FROM {table} ORDER BY {pk}").fetchall()
            rows2 = c2.execute(f"SELECT * FROM {table} ORDER BY {pk}").fetchall()
            assert rows1 == rows2, f"{table} 逐行不一致（{len(rows1)} vs {len(rows2)} 行）"
