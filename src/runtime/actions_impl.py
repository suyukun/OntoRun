"""6 个业务动作的实现（B2，技术方案 §2.4）。

每个动作 = 快照读取（事务内重读）+ 前置规则（按声明顺序）+ 效果计算（纯函数）。
- 前置规则必须按声明顺序执行（引擎按 registry 声明顺序逐条调用 check）；
- 写回只针对 source-backed（§2.7 三分类）；ontology-owned 由引擎统一落本体库；
- 目标仓 = seed 主仓 WH-1（§2.4 单仓简化，多仓分配发布期待定）。
"""

from __future__ import annotations

from typing import Any

from data.seed_retail_source import MAIN_WAREHOUSE_ID
from src.runtime.action_engine import (
    ActionHandler,
    Effect,
    Snapshot,
    Violation,
    Writeback,
    _now,
)

SEQUENCE = {
    "orders": ("order_id", "ORD-"),
    "shipments": ("shipment_id", "SHP-"),
}


# ======================================================================
# A1 create_order 下单
# ======================================================================


class CreateOrderHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "customer": snapshot.get("Customer", params.customer_id),
            "items": [
                {
                    "input": item,
                    "product": snapshot.get("Product", item.product_id),
                    "inventory": snapshot.one(
                        "SELECT * FROM inventory WHERE warehouse_id=? AND product_id=?",
                        (MAIN_WAREHOUSE_ID, item.product_id),
                    ),
                }
                for item in params.items
            ],
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "CUSTOMER_NOT_FOUND":
            return snapshot["customer"] is not None, None
        if code == "PRODUCT_NOT_FOUND":
            missing = [
                i["input"].product_id for i in snapshot["items"] if i["product"] is None
            ]
            return not missing, {"missing_product_ids": missing} if missing else None
        if code == "PRODUCT_INACTIVE":
            inactive = [
                i["input"].product_id
                for i in snapshot["items"]
                if i["product"] and i["product"]["status"] != "active"
            ]
            return not inactive, {
                "inactive_product_ids": inactive
            } if inactive else None
        if code == "OUT_OF_STOCK":
            for item in snapshot["items"]:
                inv = item["inventory"]
                available = (inv["on_hand_qty"] - inv["reserved_qty"]) if inv else 0
                if available < item["input"].qty:
                    return False, {
                        "product_id": item["input"].product_id,
                        "available_qty": available,
                        "requested_qty": item["input"].qty,
                    }
            return True, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        seq = self.engine.next_seq(conn, "orders", "order_id", "ORD-")
        order_id = f"ORD-{seq:04d}"
        now = _now()
        total = sum(
            i["input"].qty * i["product"]["price_cents"] for i in snapshot["items"]
        )
        effects: list[Effect] = [
            Effect(
                object_type="Order",
                pk=order_id,
                prop="status",
                old=None,
                new="pending",
                note="创建订单",
            )
        ]
        writebacks: list[Writeback] = [
            Writeback(
                sql="INSERT INTO orders (order_id, customer_id, status, total_cents, paid_cents, "
                "payment_status, note, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                params=[
                    order_id,
                    params.customer_id,
                    "pending",
                    total,
                    0,
                    "unpaid",
                    "",
                    now,
                    now,
                ],
                table="orders",
            )
        ]
        for j, item in enumerate(snapshot["items"]):
            oi_id = f"OI-{seq:04d}-{j + 1}"
            inv = item["inventory"]
            # 新订单行必须入索引：引擎按 effects 覆盖对象刷新（§3.3 ⑦ refresh_many），
            # 缺 OrderItem effect 会导致建单后 order.items 链接/详情计数为 0（索引一致性）。
            effects.append(
                Effect(
                    object_type="OrderItem",
                    pk=oi_id,
                    prop="qty",
                    old=None,
                    new=item["input"].qty,
                    note="新增订单行",
                )
            )
            writebacks.append(
                Writeback(
                    sql="INSERT INTO order_items (order_item_id, order_id, product_id, qty, "
                    "unit_price_cents) VALUES (?,?,?,?,?)",
                    params=[
                        oi_id,
                        order_id,
                        item["input"].product_id,
                        item["input"].qty,
                        item["product"]["price_cents"],
                    ],
                    table="order_items",
                )
            )
            inv_id = f"{MAIN_WAREHOUSE_ID}|{item['input'].product_id}"
            effects.append(
                Effect(
                    object_type="Inventory",
                    pk=inv_id,
                    prop="reserved_qty",
                    old=inv["reserved_qty"],
                    new=inv["reserved_qty"] + item["input"].qty,
                    note=f"锁库 {item['input'].qty} 件",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE inventory SET reserved_qty = reserved_qty + ?, updated_at = ? "
                    "WHERE inventory_id = ?",
                    params=[item["input"].qty, now, inv_id],
                    table="inventory",
                )
            )
        return effects, writebacks


# ======================================================================
# A2 confirm_order 履约确认
# ======================================================================


class ConfirmOrderHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {"order": snapshot.get("Order", params.order_id)}

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "ORDER_NOT_FOUND":
            return snapshot["order"] is not None, None
        if code == "ORDER_NOT_CONFIRMABLE":
            order = snapshot["order"]
            return order is not None and order["status"] == "pending", {
                "order_status": order["status"]
            } if order else None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        order = snapshot["order"]
        effects = [
            Effect(
                object_type="Order",
                pk=order["order_id"],
                prop="status",
                old=order["status"],
                new="confirmed",
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE orders SET status='confirmed', updated_at=? WHERE order_id=?",
                params=[_now(), order["order_id"]],
                table="orders",
            )
        ]
        return effects, writebacks


# ======================================================================
# A3 cancel_order 取消订单（★三问测试对象）
# ======================================================================


class CancelOrderHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        order = snapshot.get("Order", params.order_id)
        items = (
            snapshot.list_where("OrderItem", "order_id", params.order_id)
            if order
            else []
        )
        shipments = (
            snapshot.list_where("Shipment", "order_id", params.order_id)
            if order
            else []
        )
        return {
            "order": order,
            "items": items,
            "shipments": shipments,
            "inventory": [
                snapshot.one(
                    "SELECT * FROM inventory WHERE warehouse_id=? AND product_id=?",
                    (MAIN_WAREHOUSE_ID, it["product_id"]),
                )
                for it in items
            ],
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        order = snapshot["order"]
        if code == "ORDER_NOT_FOUND":
            return order is not None, None
        if code == "ORDER_NOT_CANCELLABLE":
            # 终态（cancelled/refunded）不可取消；shipped/delivered 下放到
            # SHIPPED_ORDER_CANNOT_BE_CANCELLED（§4.2 示例与 corner ② 语义，三问测试 3）
            if order is None:
                return True, {"skipped": "订单不存在（由 ORDER_NOT_FOUND 拒绝）"}
            ok = order["status"] not in ("cancelled", "refunded")
            return ok, {"order_status": order["status"]}
        if code == "SHIPPED_ORDER_CANNOT_BE_CANCELLED":
            if order is None:
                return True, {"skipped": "订单不存在"}
            shipped = [
                s["shipment_id"]
                for s in snapshot["shipments"]
                if s["status"] in ("shipped", "delivered")
            ]
            return not shipped, {"shipment_ids": shipped} if shipped else None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        order = snapshot["order"]
        now = _now()
        effects: list[Effect] = [
            Effect(
                object_type="Order",
                pk=order["order_id"],
                prop="status",
                old=order["status"],
                new="cancelled",
            )
        ]
        if params.reason:
            effects.append(
                Effect(
                    object_type="Order",
                    pk=order["order_id"],
                    prop="cancel_reason",
                    old=None,
                    new=params.reason,
                    note="本体自有状态",
                )
            )
        writebacks: list[Writeback] = [
            Writeback(
                sql="UPDATE orders SET status='cancelled', updated_at=? WHERE order_id=?",
                params=[now, order["order_id"]],
                table="orders",
            )
        ]
        for item, inv in zip(snapshot["items"], snapshot["inventory"]):
            inv_id = f"{MAIN_WAREHOUSE_ID}|{item['product_id']}"
            effects.append(
                Effect(
                    object_type="Inventory",
                    pk=inv_id,
                    prop="reserved_qty",
                    old=inv["reserved_qty"],
                    new=inv["reserved_qty"] - item["qty"],
                    note=f"释放 {item['qty']} 件",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE inventory SET reserved_qty = reserved_qty - ?, updated_at = ? "
                    "WHERE inventory_id = ?",
                    params=[item["qty"], now, inv_id],
                    table="inventory",
                )
            )
        return effects, writebacks


# ======================================================================
# A4 create_shipment 发货
# ======================================================================


class CreateShipmentHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        order = snapshot.get("Order", params.order_id)
        items = (
            snapshot.list_where("OrderItem", "order_id", params.order_id)
            if order
            else []
        )
        return {
            "order": order,
            "warehouse": snapshot.get("Warehouse", params.warehouse_id),
            "items": items,
            "inventory": [
                snapshot.one(
                    "SELECT * FROM inventory WHERE warehouse_id=? AND product_id=?",
                    (params.warehouse_id, it["product_id"]),
                )
                for it in items
            ],
        }

    def validate_semantics(self, snapshot: dict, params: Any) -> Violation | None:
        if snapshot["warehouse"] is None:
            return Violation(
                error_code="INVALID_PARAMS",
                message="发货仓不存在",
                detail={"warehouse_id": params.warehouse_id},
            )
        return None

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        order = snapshot["order"]
        if code == "ORDER_NOT_FOUND":
            return order is not None, None
        if code == "ORDER_NOT_SHIPPABLE":
            ok = order is not None and order["status"] == "confirmed"
            return ok, {"order_status": order["status"]} if order else None
        if code == "INSUFFICIENT_INVENTORY":
            for item, inv in zip(snapshot["items"], snapshot["inventory"]):
                on_hand = inv["on_hand_qty"] if inv else 0
                if on_hand < item["qty"]:
                    return False, {
                        "product_id": item["product_id"],
                        "on_hand_qty": on_hand,
                        "requested_qty": item["qty"],
                    }
            return True, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        order = snapshot["order"]
        seq = self.engine.next_seq(conn, "shipments", "shipment_id", "SHP-")
        shipment_id = f"SHP-{seq:04d}"
        now = _now()
        effects: list[Effect] = [
            Effect(
                object_type="Shipment",
                pk=shipment_id,
                prop="status",
                old=None,
                new="shipped",
                note="创建发货单",
            ),
            Effect(
                object_type="Order",
                pk=order["order_id"],
                prop="status",
                old=order["status"],
                new="shipped",
            ),
        ]
        writebacks: list[Writeback] = [
            Writeback(
                sql="INSERT INTO shipments (shipment_id, order_id, warehouse_id, status, "
                "tracking_no, shipped_at) VALUES (?,?,?,?,?,?)",
                params=[
                    shipment_id,
                    order["order_id"],
                    params.warehouse_id,
                    "shipped",
                    f"SF{seq:08d}",
                    now,
                ],
                table="shipments",
            ),
            Writeback(
                sql="UPDATE orders SET status='shipped', updated_at=? WHERE order_id=?",
                params=[now, order["order_id"]],
                table="orders",
            ),
        ]
        for item, inv in zip(snapshot["items"], snapshot["inventory"]):
            inv_id = f"{params.warehouse_id}|{item['product_id']}"
            effects.append(
                Effect(
                    object_type="Inventory",
                    pk=inv_id,
                    prop="on_hand_qty",
                    old=inv["on_hand_qty"],
                    new=inv["on_hand_qty"] - item["qty"],
                    note=f"出库 {item['qty']} 件",
                )
            )
            effects.append(
                Effect(
                    object_type="Inventory",
                    pk=inv_id,
                    prop="reserved_qty",
                    old=inv["reserved_qty"],
                    new=inv["reserved_qty"] - item["qty"],
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE inventory SET on_hand_qty = on_hand_qty - ?, "
                    "reserved_qty = reserved_qty - ?, updated_at = ? WHERE inventory_id = ?",
                    params=[item["qty"], item["qty"], now, inv_id],
                    table="inventory",
                )
            )
        return effects, writebacks


# ======================================================================
# A5 adjust_inventory 调整库存
# ======================================================================


class AdjustInventoryHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "inventory": snapshot.one(
                "SELECT * FROM inventory WHERE warehouse_id=? AND product_id=?",
                (params.warehouse_id, params.product_id),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        inv = snapshot["inventory"]
        if code == "INVENTORY_NOT_FOUND":
            return inv is not None, None
        if code == "INSUFFICIENT_RESERVED":
            ok = inv is not None and params.new_on_hand_qty >= inv["reserved_qty"]
            return ok, {"reserved_qty": inv["reserved_qty"]} if inv else None
        if code == "INVALID_PARAMS":
            return bool(params.reason), None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        inv = snapshot["inventory"]
        effects = [
            Effect(
                object_type="Inventory",
                pk=inv["inventory_id"],
                prop="on_hand_qty",
                old=inv["on_hand_qty"],
                new=params.new_on_hand_qty,
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE inventory SET on_hand_qty = ?, updated_at = ? WHERE inventory_id = ?",
                params=[params.new_on_hand_qty, _now(), inv["inventory_id"]],
                table="inventory",
            )
        ]
        return effects, writebacks


# ======================================================================
# A6 approve_refund 审核退款（高风险，双签）
# ======================================================================


class ApproveRefundHandler(ActionHandler):
    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        refund = snapshot.get("Refund", params.refund_id)
        order = snapshot.get("Order", refund["order_id"]) if refund else None
        approved_sum = 0
        if order:
            approved = snapshot.list_where("Refund", "order_id", refund["order_id"])
            approved_sum = sum(
                r["amount_cents"]
                for r in approved
                if r["status"] == "approved" and r["refund_id"] != refund["refund_id"]
            )
        return {"refund": refund, "order": order, "approved_sum": approved_sum}

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        refund, order = snapshot["refund"], snapshot["order"]
        if code == "REFUND_NOT_PENDING":
            ok = refund is not None and refund["status"] == "pending"
            return ok, {"refund_status": refund["status"]} if refund else None
        # 以下两条仅 approved 时执行（decision=rejected 直接跳过）
        if params.decision != "approved":
            return True, {"skipped": "decision=rejected"}
        if code == "AMOUNT_EXCEEDS_PAID":
            limit = order["paid_cents"] - snapshot["approved_sum"] if order else 0
            ok = refund is not None and refund["amount_cents"] <= limit
            return ok, {
                "amount_cents": refund["amount_cents"],
                "paid_cents": order["paid_cents"],
                "approved_sum": snapshot["approved_sum"],
                "limit": limit,
            } if refund and order else None
        if code == "REFUND_NOT_ALLOWED":
            ok = order is not None and (
                order["status"] in ("shipped", "delivered")
                or (order["status"] == "cancelled" and snapshot["approved_sum"] == 0)
            )
            return ok, {"order_status": order["status"]} if order else None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        refund, order = snapshot["refund"], snapshot["order"]
        now = _now()
        effects: list[Effect] = [
            Effect(
                object_type="Refund",
                pk=refund["refund_id"],
                prop="status",
                old=refund["status"],
                new=params.decision,
            ),
            Effect(
                object_type="Refund",
                pk=refund["refund_id"],
                prop="reviewed_at",
                old=refund.get("reviewed_at"),
                new=now,
            ),
            Effect(
                object_type="Refund",
                pk=refund["refund_id"],
                prop="review_note",
                old=refund.get("review_note"),
                new=params.review_note,
                note="本体自有状态",
            ),
        ]
        writebacks: list[Writeback] = [
            Writeback(
                sql="UPDATE refunds SET status=?, reviewed_at=? WHERE refund_id=?",
                params=[params.decision, now, refund["refund_id"]],
                table="refunds",
            )
        ]
        full_refund = (
            params.decision == "approved"
            and refund["amount_cents"] == order["paid_cents"]
        )
        if full_refund:
            effects.append(
                Effect(
                    object_type="Order",
                    pk=order["order_id"],
                    prop="status",
                    old=order["status"],
                    new="refunded",
                    note="整单退款",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE orders SET status='refunded', updated_at=? WHERE order_id=?",
                    params=[now, order["order_id"]],
                    table="orders",
                )
            )
        return effects, writebacks


HANDLERS: dict[str, type[ActionHandler]] = {
    "create_order": CreateOrderHandler,
    "confirm_order": ConfirmOrderHandler,
    "cancel_order": CancelOrderHandler,
    "create_shipment": CreateShipmentHandler,
    "adjust_inventory": AdjustInventoryHandler,
    "approve_refund": ApproveRefundHandler,
}
