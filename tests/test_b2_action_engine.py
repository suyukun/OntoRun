"""B2 验收测试：动作执行引擎 + 冲突消解 + 审计 + 双库存储（技术方案 §3.3/§3.4/§3.5）。

验收点：
- 6 个动作（create_order/confirm_order/cancel_order/create_shipment/
  adjust_inventory/approve_refund）正反路径；
- 拒绝路径零写库断言（源库快照前后一致）；
- 审计落库断言（writeback_json 含写回 SQL 与影响行数——"源记录真变"自证）；
- 前置规则按声明顺序执行（audit.preconditions_json 顺序）。
"""

import json
import shutil
import sqlite3
from datetime import datetime, timezone

import pytest

from data import seed_retail_source as seed
from src.ontology import build_registry
from src.runtime.action_engine import ActionEngine
from src.runtime.audit import AuditLog
from src.runtime.conflict import (
    STRATEGY_TIMESTAMP_WINS,
    STRATEGY_USER_EDIT_WINS,
    resolve,
)
from src.runtime.index import ObjectIndex
from src.runtime.permissions import PermissionDecision
from src.runtime.store import Store

TABLES = [
    "customers",
    "products",
    "warehouses",
    "inventory",
    "orders",
    "order_items",
    "shipments",
    "refunds",
]

NOW = datetime.now(timezone.utc)


class Runtime:
    def __init__(self, store, index, audit, engine):
        self.store = store
        self.index = index
        self.audit = audit
        self.engine = engine

    def source(self) -> sqlite3.Connection:
        return self.store.source_conn()

    def ontology(self) -> sqlite3.Connection:
        return self.store.ontology_conn()


@pytest.fixture(scope="session")
def seed_db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def runtime(tmp_path, seed_db_path) -> Runtime:
    """每个测试独立双库：源库由 seed 重建后拷贝（保证写回测试基于重建库）。"""
    source = tmp_path / "source.db"
    shutil.copy(seed_db_path, source)
    store = Store(source, tmp_path / "ontology.db")
    store.migrate()
    registry = build_registry()
    index = ObjectIndex(registry)
    with store.source_conn() as conn:
        index.load_all(conn)
    with store.ontology_conn() as conn:
        index.load_ontology_state(conn)
    audit = AuditLog(store)
    engine = ActionEngine(registry, store, index, audit)
    return Runtime(store, index, audit, engine)


def table_snapshot(conn: sqlite3.Connection) -> dict:
    """源库全表快照（按 rowid 稳定排序），用于零写库断言。"""
    return {
        t: conn.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall() for t in TABLES
    }


# P4 权限门测试替身（PermissionEnforcer 协议实现：deny/allow/skip 三态）
class _DenyEnforcer:
    """一律拒绝：返回 deny 决策 + 命中策略 id（供审计 detail_json 断言）。"""

    def decide(self, action_name, params, actor):
        return PermissionDecision(allowed=False, matched_policy_ids=["deny-1", "deny-2"])


class _AllowEnforcer:
    """一律放行。"""

    def decide(self, action_name, params, actor):
        return PermissionDecision(allowed=True, matched_policy_ids=["allow-1"])


class _SkipEnforcer:
    """返回 None：该动作不纳入权限门（跳过权限裁决）。"""

    def decide(self, action_name, params, actor):
        return None


def runtime_with_enforcer(runtime: Runtime, enforcer) -> Runtime:
    """基于既有双库再造一台带权限门的引擎（复用同一 store/index/audit）。"""
    engine = ActionEngine(
        runtime.engine.registry, runtime.store, runtime.index, runtime.audit, enforcer=enforcer
    )
    return Runtime(runtime.store, runtime.index, runtime.audit, engine)


def row(runtime: Runtime, sql: str, params=()) -> sqlite3.Row | None:
    c = runtime.source()
    try:
        c.row_factory = sqlite3.Row
        return c.execute(sql, params).fetchone()
    finally:
        c.close()


def exec_action(
    runtime: Runtime, action: str, params: dict, request_id: str = "req-test"
):
    return runtime.engine.execute(
        action, params, actor="api", actor_detail="pytest", request_id=request_id
    )


# ======================================================================
# A1 create_order
# ======================================================================


def test_create_order_applied(runtime):
    price = row(runtime, "SELECT price_cents FROM products WHERE product_id='SKU-003'")[
        "price_cents"
    ]
    before_reserved = row(
        runtime,
        "SELECT reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )["reserved_qty"]
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": "SKU-003", "qty": 5}]},
    )
    assert res.outcome == "applied", res.message
    # 源库：新订单 pending + 库存锁库
    order = row(runtime, "SELECT * FROM orders WHERE order_id='ORD-2201'")
    assert order is not None and order["status"] == "pending"
    assert order["total_cents"] == price * 5 and order["paid_cents"] == 0
    assert order["payment_status"] == "unpaid"
    item = row(runtime, "SELECT * FROM order_items WHERE order_id='ORD-2201'")
    assert item is not None and item["qty"] == 5 and item["unit_price_cents"] == price
    inv = row(
        runtime,
        "SELECT reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )
    assert inv["reserved_qty"] == before_reserved + 5
    # 审计：applied + writeback_json 自证（INSERT orders / UPDATE inventory）
    audit = runtime.audit.get(res.audit_id)
    assert audit["outcome"] == "applied"
    wb = json.loads(audit["writeback_json"])
    sqls = [w["sql"] for w in wb]
    assert any("INSERT INTO orders" in s for s in sqls)
    assert any("UPDATE inventory" in s for s in sqls)
    assert all(w["rows"] >= 1 for w in wb)
    assert res.request_id == "req-test"


def test_create_order_out_of_stock_rejected_with_available(runtime):
    """corner ①：SKU-001 available=30，要 100 件被拦，返回当前可用量，源库零变更。"""
    conn = runtime.source()
    before = table_snapshot(conn)
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": "SKU-001", "qty": 100}]},
    )
    assert res.outcome == "rejected"
    assert res.error_code == "OUT_OF_STOCK"
    assert res.detail["available_qty"] == 30
    assert table_snapshot(conn) == before, "拒绝路径源库必须零变更"
    audit = runtime.audit.get(res.audit_id)
    assert audit["outcome"] == "rejected" and audit["error_code"] == "OUT_OF_STOCK"


def test_create_order_customer_not_found(runtime):
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-9999", "items": [{"product_id": "SKU-003", "qty": 1}]},
    )
    assert res.outcome == "rejected" and res.error_code == "CUSTOMER_NOT_FOUND"


def test_create_order_product_not_found(runtime):
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": "SKU-999", "qty": 1}]},
    )
    assert res.outcome == "rejected" and res.error_code == "PRODUCT_NOT_FOUND"


def test_create_order_product_inactive(runtime):
    """archived 商品（SKU-056..060）拒绝下单。"""
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": "SKU-060", "qty": 1}]},
    )
    assert res.outcome == "rejected" and res.error_code == "PRODUCT_INACTIVE"


def test_create_order_invalid_params(runtime):
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": "SKU-003", "qty": 0}]},
    )
    assert res.outcome == "rejected" and res.error_code == "INVALID_PARAMS"


# ======================================================================
# A2 confirm_order
# ======================================================================


def test_confirm_order_applied(runtime):
    res = exec_action(runtime, "confirm_order", {"order_id": "ORD-0001"})
    assert res.outcome == "applied"
    assert (
        row(runtime, "SELECT status FROM orders WHERE order_id='ORD-0001'")["status"]
        == "confirmed"
    )
    audit = runtime.audit.get(res.audit_id)
    wb = json.loads(audit["writeback_json"])
    assert any("UPDATE orders" in w["sql"] and w["rows"] == 1 for w in wb)


def test_confirm_order_not_confirmable(runtime):
    res = exec_action(
        runtime, "confirm_order", {"order_id": "ORD-1001"}
    )  # 已 confirmed
    assert res.outcome == "rejected" and res.error_code == "ORDER_NOT_CONFIRMABLE"


# ======================================================================
# A3 cancel_order（三问测试对象）
# ======================================================================


def test_cancel_order_applied_releases_reserved(runtime):
    """ORD-1001（confirmed，SKU-003×3+SKU-004×2）取消：状态变更 + 释放锁库 + 审计自证。"""
    before_r = row(
        runtime,
        "SELECT reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )["reserved_qty"]
    res = exec_action(
        runtime, "cancel_order", {"order_id": "ORD-1001", "reason": "客户改主意"}
    )
    assert res.outcome == "applied"
    order = row(runtime, "SELECT * FROM orders WHERE order_id='ORD-1001'")
    assert order["status"] == "cancelled"
    after_r = row(
        runtime,
        "SELECT reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )["reserved_qty"]
    assert after_r == before_r - 3, "取消应释放 3 件 SKU-003 锁库"
    # 审计：writeback_json 含 UPDATE orders 与 UPDATE inventory，rows=1
    audit = runtime.audit.get(res.audit_id)
    assert audit["outcome"] == "applied"
    wb = json.loads(audit["writeback_json"])
    assert any("UPDATE orders" in w["sql"] and w["rows"] == 1 for w in wb)
    assert any("UPDATE inventory" in w["sql"] and w["rows"] == 1 for w in wb)
    effects = json.loads(audit["effects_json"])
    assert any(
        e["object_type"] == "Order"
        and e["prop"] == "status"
        and e["old"] == "confirmed"
        and e["new"] == "cancelled"
        for e in effects
    )
    # 本体自有状态：cancel_reason 落 ontology_state，索引 get 合并可见
    os_row = (
        runtime.ontology()
        .execute(
            "SELECT value FROM ontology_state WHERE object_type='Order' AND pk='ORD-1001' "
            "AND prop='cancel_reason'"
        )
        .fetchone()
    )
    assert os_row is not None and os_row[0] == "客户改主意"
    assert runtime.index.get("Order", "ORD-1001")["cancel_reason"] == "客户改主意"


def test_cancel_order_shipped_intercepted(runtime):
    """corner ②（三问测试 3）：ORD-2007 已发货 → 拒绝取消，源库零变更。"""
    conn = runtime.source()
    before = table_snapshot(conn)
    res = exec_action(runtime, "cancel_order", {"order_id": "ORD-2007"})
    assert res.outcome == "rejected"
    assert res.error_code == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
    assert res.detail["shipment_ids"] == ["SHP-88"]
    assert table_snapshot(conn) == before, "已发货订单取消被拦，源库零变更"
    audit = runtime.audit.get(res.audit_id)
    assert audit["error_code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"


def test_cancel_order_not_cancellable(runtime):
    """refunded 状态订单不可取消 → ORDER_NOT_CANCELLABLE（第二条前置）。"""
    oid = row(runtime, "SELECT order_id FROM orders WHERE status='refunded' LIMIT 1")[
        "order_id"
    ]
    res = exec_action(runtime, "cancel_order", {"order_id": oid})
    assert res.outcome == "rejected" and res.error_code == "ORDER_NOT_CANCELLABLE"


def test_cancel_order_not_found(runtime):
    """第一条前置 ORDER_NOT_FOUND 先于状态检查触发。"""
    res = exec_action(runtime, "cancel_order", {"order_id": "ORD-9999"})
    assert res.outcome == "rejected" and res.error_code == "ORDER_NOT_FOUND"


def test_preconditions_executed_in_declared_order(runtime):
    """audit.preconditions_json 记录每条前置规则的检查顺序与结果。"""
    res = exec_action(runtime, "cancel_order", {"order_id": "ORD-9999"})
    audit = runtime.audit.get(res.audit_id)
    checks = json.loads(audit["preconditions_json"])
    codes = [c["code"] for c in checks]
    assert codes[:3] == [
        "ORDER_NOT_FOUND",
        "ORDER_NOT_CANCELLABLE",
        "SHIPPED_ORDER_CANNOT_BE_CANCELLED",
    ]
    assert checks[0]["passed"] is False and checks[1]["passed"] is True


# ======================================================================
# A4 create_shipment
# ======================================================================


def _create_and_confirm(runtime, product_id="SKU-003", qty=5) -> str:
    res = exec_action(
        runtime,
        "create_order",
        {"customer_id": "CUS-0001", "items": [{"product_id": product_id, "qty": qty}]},
    )
    assert res.outcome == "applied"
    order_id = res.effects[0].pk
    res = exec_action(runtime, "confirm_order", {"order_id": order_id})
    assert res.outcome == "applied"
    return order_id


def test_create_shipment_applied(runtime):
    order_id = _create_and_confirm(runtime)
    before = row(
        runtime,
        "SELECT on_hand_qty, reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )
    res = exec_action(
        runtime,
        "create_shipment",
        {"order_id": order_id, "warehouse_id": seed.MAIN_WAREHOUSE_ID},
    )
    assert res.outcome == "applied", res.message
    assert (
        row(runtime, "SELECT status FROM orders WHERE order_id=?", (order_id,))[
            "status"
        ]
        == "shipped"
    )
    ship = row(runtime, "SELECT * FROM shipments WHERE order_id=?", (order_id,))
    assert ship is not None and ship["status"] == "shipped" and ship["tracking_no"]
    after = row(
        runtime,
        "SELECT on_hand_qty, reserved_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )
    assert after["on_hand_qty"] == before["on_hand_qty"] - 5
    assert after["reserved_qty"] == before["reserved_qty"] - 5
    # 索引同步（§3.3 ⑦）
    assert runtime.index.get("Order", order_id)["status"] == "shipped"


def test_create_shipment_not_shippable(runtime):
    res = exec_action(
        runtime,
        "create_shipment",
        {"order_id": "ORD-0001", "warehouse_id": seed.MAIN_WAREHOUSE_ID},
    )  # pending
    assert res.outcome == "rejected" and res.error_code == "ORDER_NOT_SHIPPABLE"


def test_create_shipment_unknown_warehouse(runtime):
    """warehouse 不存在 → INVALID_PARAMS（§2.4 A4：存在性归入参数校验）。"""
    order_id = _create_and_confirm(runtime)
    res = exec_action(
        runtime, "create_shipment", {"order_id": order_id, "warehouse_id": "WH-99"}
    )
    assert res.outcome == "rejected" and res.error_code == "INVALID_PARAMS"


def test_create_shipment_insufficient_inventory(runtime):
    """corner ④：发货仓物理在库不足 → INSUFFICIENT_INVENTORY。"""
    order_id = _create_and_confirm(runtime, product_id="SKU-029", qty=5)
    # 把 WH-2（SKU-029 第二仓行）on_hand 调到 2（reserved=0，允许）
    res = exec_action(
        runtime,
        "adjust_inventory",
        {
            "warehouse_id": "WH-2",
            "product_id": "SKU-029",
            "new_on_hand_qty": 2,
            "reason": "测试调低",
        },
    )
    assert res.outcome == "applied"
    res = exec_action(
        runtime, "create_shipment", {"order_id": order_id, "warehouse_id": "WH-2"}
    )
    assert res.outcome == "rejected" and res.error_code == "INSUFFICIENT_INVENTORY"
    assert res.detail["on_hand_qty"] == 2


# ======================================================================
# A5 adjust_inventory
# ======================================================================


def test_adjust_inventory_applied(runtime):
    res = exec_action(
        runtime,
        "adjust_inventory",
        {
            "warehouse_id": seed.MAIN_WAREHOUSE_ID,
            "product_id": "SKU-003",
            "new_on_hand_qty": 1234,
            "reason": "盘点纠正",
        },
    )
    assert res.outcome == "applied"
    inv = row(
        runtime,
        "SELECT on_hand_qty FROM inventory WHERE product_id='SKU-003' "
        "AND warehouse_id=?",
        (seed.MAIN_WAREHOUSE_ID,),
    )
    assert inv["on_hand_qty"] == 1234


def test_adjust_inventory_insufficient_reserved(runtime):
    """corner ④另一形态：新值低于已锁库存 → INSUFFICIENT_RESERVED。"""
    res = exec_action(
        runtime,
        "adjust_inventory",
        {
            "warehouse_id": seed.MAIN_WAREHOUSE_ID,
            "product_id": "SKU-001",
            "new_on_hand_qty": 5,
            "reason": "误操作",
        },
    )  # SKU-001 reserved=10
    assert res.outcome == "rejected" and res.error_code == "INSUFFICIENT_RESERVED"
    assert res.detail["reserved_qty"] == 10


def test_adjust_inventory_not_found(runtime):
    res = exec_action(
        runtime,
        "adjust_inventory",
        {
            "warehouse_id": "WH-2",
            "product_id": "SKU-001",
            "new_on_hand_qty": 100,
            "reason": "x",
        },
    )  # SKU-001 只在 WH-1
    assert res.outcome == "rejected" and res.error_code == "INVENTORY_NOT_FOUND"


# ======================================================================
# A6 approve_refund（高风险，双签）
# ======================================================================


def _pending_refund(runtime):
    return row(
        runtime,
        "SELECT r.refund_id, r.amount_cents, r.order_id FROM refunds r "
        "WHERE r.status='pending' AND r.amount_cents <= (SELECT o.paid_cents FROM orders o "
        "WHERE o.order_id=r.order_id) LIMIT 1",
    )


def test_approve_refund_applied_partial(runtime):
    """部分退款（< 实付）：refund → approved，订单保持 shipped，review_note 落本体自有状态。"""
    refund = _pending_refund(runtime)
    res = exec_action(
        runtime,
        "approve_refund",
        {
            "refund_id": refund["refund_id"],
            "decision": "approved",
            "review_note": "符合退货政策",
        },
    )
    assert res.outcome == "applied", res.message
    r = row(runtime, "SELECT * FROM refunds WHERE refund_id=?", (refund["refund_id"],))
    assert r["status"] == "approved" and r["reviewed_at"] is not None
    order = row(
        runtime, "SELECT status FROM orders WHERE order_id=?", (refund["order_id"],)
    )
    assert order["status"] in ("shipped", "delivered")  # 部分退款不触发 refunded
    os_row = (
        runtime.ontology()
        .execute(
            "SELECT value FROM ontology_state WHERE object_type='Refund' AND pk=? AND prop='review_note'",
            (refund["refund_id"],),
        )
        .fetchone()
    )
    assert os_row is not None and os_row[0] == "符合退货政策"


def test_approve_refund_full_refunded_order(runtime):
    """整单退款（金额=实付）：订单 → refunded（A6 效果）。"""
    order_id = _create_and_confirm(runtime)
    res = exec_action(
        runtime,
        "create_shipment",
        {"order_id": order_id, "warehouse_id": seed.MAIN_WAREHOUSE_ID},
    )
    assert res.outcome == "applied"
    # 模拟支付：实付=总额（create_order 默认 unpaid，全额退款要求 order.paid_cents == amount）
    conn = runtime.source()
    conn.execute(
        "UPDATE orders SET paid_cents=total_cents, payment_status='paid' WHERE order_id=?",
        (order_id,),
    )
    conn.commit()
    conn.close()
    total = row(
        runtime, "SELECT total_cents FROM orders WHERE order_id=?", (order_id,)
    )["total_cents"]
    refund_id = f"REF-{order_id[4:]}"
    conn = runtime.source()
    conn.execute(
        "INSERT INTO refunds (refund_id, order_id, amount_cents, status, reason, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (
            refund_id,
            order_id,
            total,
            "pending",
            "整单退款",
            NOW.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
    res = exec_action(
        runtime,
        "approve_refund",
        {"refund_id": refund_id, "decision": "approved", "review_note": "整单退"},
    )
    assert res.outcome == "applied"
    assert (
        row(runtime, "SELECT status FROM orders WHERE order_id=?", (order_id,))[
            "status"
        ]
        == "refunded"
    )


def test_approve_refund_rejected_decision(runtime):
    """decision=rejected：refund → rejected，订单不变。"""
    refund = _pending_refund(runtime)
    res = exec_action(
        runtime,
        "approve_refund",
        {
            "refund_id": refund["refund_id"],
            "decision": "rejected",
            "review_note": "无质量问题",
        },
    )
    assert res.outcome == "applied"
    r = row(
        runtime, "SELECT status FROM refunds WHERE refund_id=?", (refund["refund_id"],)
    )
    assert r["status"] == "rejected"
    order = row(
        runtime, "SELECT status FROM orders WHERE order_id=?", (refund["order_id"],)
    )
    assert order["status"] in ("shipped", "delivered")  # 拒绝退款不改变订单


def test_approve_refund_not_pending(runtime):
    """corner ③：已 approved 退款再审 → REFUND_NOT_PENDING。"""
    approved = row(
        runtime, "SELECT refund_id FROM refunds WHERE status='approved' LIMIT 1"
    )
    res = exec_action(
        runtime,
        "approve_refund",
        {
            "refund_id": approved["refund_id"],
            "decision": "approved",
            "review_note": "重复审核",
        },
    )
    assert res.outcome == "rejected" and res.error_code == "REFUND_NOT_PENDING"


def test_approve_refund_amount_exceeds_paid(runtime):
    """corner ③：退款金额超实付 → AMOUNT_EXCEEDS_PAID。"""
    over = row(
        runtime,
        "SELECT refund_id FROM refunds WHERE status='pending' "
        "AND amount_cents > (SELECT paid_cents FROM orders o WHERE o.order_id=refunds.order_id) LIMIT 1",
    )
    res = exec_action(
        runtime,
        "approve_refund",
        {
            "refund_id": over["refund_id"],
            "decision": "approved",
            "review_note": "超付测试",
        },
    )
    assert res.outcome == "rejected" and res.error_code == "AMOUNT_EXCEEDS_PAID"


def test_approve_refund_not_allowed_order_status(runtime):
    """未履约订单（confirmed）不可批准退款 → REFUND_NOT_ALLOWED。"""
    order_id = _create_and_confirm(runtime)
    conn = runtime.source()
    # 模拟支付：未履约订单即便已支付也不可退款（REFUND_NOT_ALLOWED 在金额检查之后）
    conn.execute(
        "UPDATE orders SET paid_cents=total_cents, payment_status='paid' WHERE order_id=?",
        (order_id,),
    )
    conn.execute(
        "INSERT INTO refunds (refund_id, order_id, amount_cents, status, reason, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (
            f"REF-{order_id[4:]}",
            order_id,
            100,
            "pending",
            "未发货退款",
            NOW.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
    res = exec_action(
        runtime,
        "approve_refund",
        {
            "refund_id": f"REF-{order_id[4:]}",
            "decision": "approved",
            "review_note": "不应批准",
        },
    )
    assert res.outcome == "rejected" and res.error_code == "REFUND_NOT_ALLOWED"


# ======================================================================
# 引擎级行为：UNKNOWN_ACTION / 拒绝零写库 / 索引同步 / 冲突 / 审计查询
# ======================================================================


def test_unknown_action(runtime):
    res = exec_action(runtime, "no_such_action", {})
    assert res.outcome == "rejected" and res.error_code == "UNKNOWN_ACTION"


# ======================================================================
# P4 权限门（PermissionEnforcer：① 参数校验后、④ 前置规则前）
# ======================================================================


def test_execute_without_enforcer_s1_compat(runtime):
    """P4 兼容：缺省不传 enforcer → 权限门不启用，动作执行与 S1 完全一致。"""
    res = exec_action(runtime, "confirm_order", {"order_id": "ORD-0001"})
    assert res.outcome == "applied" and res.error_code is None
    assert runtime.engine._enforcer is None  # 缺省关闭，不改变既有行为


def test_permission_gate_deny_rejected_with_audit(runtime):
    """P4 权限门：enforcer deny → rejected + PERMISSION_DENIED + 审计落 rejected（含 matched_policy_ids），源库零变更。"""
    rt = runtime_with_enforcer(runtime, _DenyEnforcer())
    conn = rt.source()
    before = table_snapshot(conn)
    res = exec_action(rt, "cancel_order", {"order_id": "ORD-1001", "reason": "越权尝试"})
    assert res.outcome == "rejected"
    assert res.error_code == "PERMISSION_DENIED"
    assert res.detail["matched_policy_ids"] == ["deny-1", "deny-2"]
    assert table_snapshot(conn) == before, "权限拒绝路径源库必须零变更"
    audit = rt.audit.get(res.audit_id)
    assert audit["outcome"] == "rejected"
    assert audit["error_code"] == "PERMISSION_DENIED"
    detail = json.loads(audit["detail_json"])
    assert detail["matched_policy_ids"] == ["deny-1", "deny-2"]
    assert detail["action_name"] == "cancel_order" and detail["actor"] == "api"
    conn.close()


def test_permission_gate_allow_proceeds(runtime):
    """P4 权限门：enforcer allow → 继续执行（applied），不改变既有管道。"""
    rt = runtime_with_enforcer(runtime, _AllowEnforcer())
    res = exec_action(rt, "confirm_order", {"order_id": "ORD-0001"})
    assert res.outcome == "applied"
    assert (
        row(rt, "SELECT status FROM orders WHERE order_id='ORD-0001'")["status"]
        == "confirmed"
    )


def test_permission_gate_enforcer_skip_none(runtime):
    """P4 权限门：enforcer 返回 None（该动作不纳入权限门）→ 跳过权限裁决，正常执行。"""
    rt = runtime_with_enforcer(runtime, _SkipEnforcer())
    res = exec_action(rt, "confirm_order", {"order_id": "ORD-0001"})
    assert res.outcome == "applied"
    assert res.error_code is None


def test_rejected_paths_zero_write_assertion(runtime):
    """多路径拒绝后源库全表零变更（拒绝路径零写库验收的集中断言）。"""
    conn = runtime.source()
    before = table_snapshot(conn)
    cases = [
        (
            "create_order",
            {
                "customer_id": "CUS-0001",
                "items": [{"product_id": "SKU-001", "qty": 100}],
            },
        ),
        ("cancel_order", {"order_id": "ORD-2007"}),
        ("confirm_order", {"order_id": "ORD-1001"}),
        (
            "adjust_inventory",
            {
                "warehouse_id": seed.MAIN_WAREHOUSE_ID,
                "product_id": "SKU-001",
                "new_on_hand_qty": 1,
                "reason": "x",
            },
        ),
        (
            "create_shipment",
            {"order_id": "ORD-0001", "warehouse_id": seed.MAIN_WAREHOUSE_ID},
        ),
        ("cancel_order", {"order_id": "ORD-9999"}),
        (
            "approve_refund",
            {"refund_id": "REF-0001", "decision": "approved", "review_note": "x"},
        ),
    ]
    for action, params in cases:
        res = exec_action(runtime, action, params)
        assert res.outcome == "rejected", f"{action} 应被拒绝: {res.error_code}"
    assert table_snapshot(conn) == before, "全部拒绝路径源库必须零变更"


def test_index_synced_after_action(runtime):
    """动作后索引同步（§3.3 ⑦）：取消后索引 get 直接可见新状态。"""
    exec_action(runtime, "cancel_order", {"order_id": "ORD-1001"})
    assert runtime.index.get("Order", "ORD-1001")["status"] == "cancelled"
    assert (
        runtime.index.get("Order", "ORD-1001")["cancel_reason"] is None
    )  # 未传 reason


def test_audit_query_filters_and_pagination(runtime):
    exec_action(runtime, "cancel_order", {"order_id": "ORD-1001"})
    exec_action(runtime, "confirm_order", {"order_id": "ORD-0001"})
    items, total = runtime.audit.query(outcome="applied", page=1, page_size=10)
    assert total >= 2 and len(items) == 2
    items2, total2 = runtime.audit.query(action="cancel_order", page=1, page_size=10)
    assert total2 == 1 and items2[0]["action_name"] == "cancel_order"
    audit = runtime.audit.get(items[0]["audit_id"])
    assert audit is not None and audit["audit_id"] == items[0]["audit_id"]


def test_audit_get_missing(runtime):
    assert runtime.audit.get("aud_does_not_exist") is None


def test_store_migrate_schema_version(runtime):
    assert runtime.store.get_schema_version() == 1
    tables = {
        r[0]
        for r in runtime.ontology()
        .execute("SELECT name FROM sqlite_master WHERE type='table'")
        .fetchall()
    }
    assert {"audit_log", "ontology_state", "schema_version"} <= tables


def test_conflict_resolve_strategies():
    """策略 1 用户编辑优先：动作写回覆盖源系统当前值；策略 2 时间戳优先为预留接口。"""
    assert resolve(STRATEGY_USER_EDIT_WINS, "current", "incoming") == "incoming"
    assert resolve(STRATEGY_USER_EDIT_WINS, 10, 20) == 20
    with pytest.raises(NotImplementedError):
        resolve(STRATEGY_TIMESTAMP_WINS, "current", "incoming")
    with pytest.raises(ValueError):
        resolve("bogus", "current", "incoming")


def test_audit_record_full_schema(runtime):
    """§3.5 全字段：params/preconditions/effects/writeback/duration 等。"""
    res = exec_action(
        runtime, "cancel_order", {"order_id": "ORD-1001", "reason": "审计完整性"}
    )
    audit = runtime.audit.get(res.audit_id)
    assert audit["action_name"] == "cancel_order"
    assert audit["actor"] == "api" and audit["request_id"] == "req-test"
    assert json.loads(audit["params_json"]) == {
        "order_id": "ORD-1001",
        "reason": "审计完整性",
    }
    assert json.loads(audit["effects_json"])
    assert json.loads(audit["writeback_json"])
    assert isinstance(audit["duration_ms"], int) and audit["duration_ms"] >= 0
    assert len(audit["audit_id"]) == 26  # ULID


# ======================================================================
# red-team 修复回归：actor 白名单（写必有痕） / 建单索引一致性 / 参数长度上限
# ======================================================================


def test_engine_rejects_invalid_actor_no_write(runtime):
    """【重要1 兜底】非法 actor 直调引擎 → failed，源库零变更、零审计（写必有痕的防缺口）。"""
    conn = runtime.source()
    before = table_snapshot(conn)
    res = runtime.engine.execute(
        "confirm_order",
        {"order_id": "ORD-0001"},
        actor="evil_hacker",
        request_id="req-bad-actor",
    )
    assert res.outcome == "failed"
    assert res.message and "evil_hacker" in res.message
    assert table_snapshot(conn) == before, "非法 actor 拒绝路径源库必须零变更"
    items, _ = runtime.audit.query(action="confirm_order")
    assert items == [], "非法 actor 不应产生审计记录（无法落库即不应写源库）"
    conn.close()


def test_create_order_index_links_order_items(runtime):
    """【重要2】建单后新 OrderItem 必须入索引：order.items 链接数 = 下单件数。"""
    res = exec_action(
        runtime,
        "create_order",
        {
            "customer_id": "CUS-0001",
            "items": [
                {"product_id": "SKU-003", "qty": 2},
                {"product_id": "SKU-004", "qty": 3},
            ],
        },
    )
    assert res.outcome == "applied", res.message
    order_id = res.effects[0].pk
    # 详情链接计数：order.items = 2（索引一致性，red-team 实测曾为 0）
    counts = runtime.index.get_link_counts("Order", order_id)
    assert counts["out"]["order.items"] == 2, counts
    # 链接遍历可取到订单项，且 derived line_total 计算正确
    items = runtime.index.get_links("Order", order_id, "order.items", "out")
    assert len(items) == 2
    qty_by_product = {it["product_id"]: it["qty"] for it in items}
    assert qty_by_product == {"SKU-003": 2, "SKU-004": 3}
    for it in items:
        assert it["line_total_cents"] == it["qty"] * it["unit_price_cents"]


def test_string_param_length_limits(runtime):
    """【建议5】§5.4 长度上限：reason/review_note 超 500 字符 → INVALID_PARAMS。"""
    long = "x" * 501
    res = exec_action(runtime, "cancel_order", {"order_id": "ORD-1001", "reason": long})
    assert res.outcome == "rejected" and res.error_code == "INVALID_PARAMS"
    res = exec_action(
        runtime,
        "adjust_inventory",
        {
            "warehouse_id": seed.MAIN_WAREHOUSE_ID,
            "product_id": "SKU-003",
            "new_on_hand_qty": 100,
            "reason": long,
        },
    )
    assert res.outcome == "rejected" and res.error_code == "INVALID_PARAMS"
    refund = _pending_refund(runtime)
    res = exec_action(
        runtime,
        "approve_refund",
        {"refund_id": refund["refund_id"], "decision": "approved", "review_note": long},
    )
    assert res.outcome == "rejected" and res.error_code == "INVALID_PARAMS"
