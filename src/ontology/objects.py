"""对象类型定义 —— 零售供应链 8 个对象（技术方案 §2.2）。

字段用 own(ownership, description) 标注状态归属三分类：
- source-backed：源系统权威，动作写回（写回目标明确，防平行数据库幻觉，§2.7）；
- ontology-owned：本体自有状态（源系统无此列，如 Order.cancel_reason）；
- derived：计算态，永不写（available_qty / line_total_cents）。
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OWN_SOURCE = "source-backed"
OWN_ONTOLOGY = "ontology-owned"
OWN_DERIVED = "derived"
_OWNERSHIPS = (OWN_SOURCE, OWN_ONTOLOGY, OWN_DERIVED)

OrderStatus = Literal[
    "pending", "confirmed", "shipped", "delivered", "cancelled", "refunded"
]


def own(ownership: str, description: str, **kwargs) -> Field:
    """带状态归属标注的 Pydantic Field（json_schema_extra 供 self_check 与 schema 导出消费）。"""
    if ownership not in _OWNERSHIPS:
        raise ValueError(f"非法状态归属: {ownership}")
    return Field(
        description=description, json_schema_extra={"ownership": ownership}, **kwargs
    )


def field_ownership(model: type[BaseModel], field_name: str) -> str | None:
    """读取字段的状态归属标注；未标注返回 None。"""
    extra = model.model_fields[field_name].json_schema_extra
    return extra.get("ownership") if isinstance(extra, dict) else None


class Customer(BaseModel):
    """客户。PK/Title = customer_id。"""

    customer_id: str = own(OWN_SOURCE, "全局唯一客户号（PK/Title）")
    name: str = own(OWN_SOURCE, "客户名称")
    segment: Literal["retail", "sme", "corporate"] = own(OWN_SOURCE, "客户分层")
    region: str = own(OWN_SOURCE, "所在城市")
    credit_level: Literal["A", "B", "C"] = own(OWN_SOURCE, "信用等级（风控预留）")
    created_at: datetime = own(OWN_SOURCE, "建档时间")


class Product(BaseModel):
    """商品（SKU）。PK/Title = product_id。archived 商品不可下单。"""

    product_id: str = own(OWN_SOURCE, "SKU（PK/Title）")
    name: str = own(OWN_SOURCE, "商品名")
    category: str = own(OWN_SOURCE, "品类")
    price_cents: int = own(OWN_SOURCE, "单价（分）")
    status: Literal["active", "archived"] = own(OWN_SOURCE, "在售状态")
    description: str = own(
        OWN_SOURCE, "商品描述（自由文本，prompt-injection 演示靶场字段）"
    )


class Warehouse(BaseModel):
    """仓库。PK/Title = warehouse_id。"""

    warehouse_id: str = own(OWN_SOURCE, "仓库号（PK/Title）")
    name: str = own(OWN_SOURCE, "仓库名")
    city: str = own(OWN_SOURCE, "所在城市")
    capacity_cubic_m: int = own(OWN_SOURCE, "库容（预留，MVP 不校验）")


class Inventory(BaseModel):
    """库存（每仓每商品一条）。PK = inventory_id（"WH|SKU" 组合）。"""

    inventory_id: str = own(
        OWN_SOURCE, "库存记录号（PK，派生自 warehouse_id+product_id）"
    )
    warehouse_id: str = own(OWN_SOURCE, "所属仓库（FK->Warehouse）")
    product_id: str = own(OWN_SOURCE, "商品（FK->Product）")
    on_hand_qty: int = own(OWN_SOURCE, "在库数量")
    reserved_qty: int = own(OWN_SOURCE, "已锁定数量（下单锁定、发货扣减）")
    available_qty: int = own(
        OWN_DERIVED, "可用数量 = on_hand - reserved（计算态，永不写）"
    )
    updated_at: datetime = own(OWN_SOURCE, "更新时间")


class Order(BaseModel):
    """订单。PK/Title = order_id。状态机见 §2.5。"""

    order_id: str = own(OWN_SOURCE, "订单号（PK/Title）")
    customer_id: str = own(OWN_SOURCE, "下单客户（FK->Customer）")
    status: OrderStatus = own(OWN_SOURCE, "订单状态（状态机 §2.5）")
    total_cents: int = own(OWN_SOURCE, "下单时金额快照")
    paid_cents: int = own(OWN_SOURCE, "实付金额（≤ total）")
    payment_status: Literal["unpaid", "paid"] = own(OWN_SOURCE, "支付状态（MVP 简化）")
    note: str = own(OWN_SOURCE, "订单备注（自由文本，prompt-injection 演示靶场字段）")
    created_at: datetime = own(OWN_SOURCE, "下单时间")
    updated_at: datetime = own(OWN_SOURCE, "更新时间")
    cancel_reason: str | None = own(
        OWN_ONTOLOGY, "取消原因（本体自有状态，源系统无此列）", default=None
    )


class OrderItem(BaseModel):
    """订单行。PK = order_item_id。"""

    order_item_id: str = own(OWN_SOURCE, "订单行号（PK）")
    order_id: str = own(OWN_SOURCE, "所属订单（FK->Order）")
    product_id: str = own(OWN_SOURCE, "商品（FK->Product）")
    qty: int = own(OWN_SOURCE, "数量")
    unit_price_cents: int = own(OWN_SOURCE, "下单时单价快照")
    line_total_cents: int = own(
        OWN_DERIVED, "行金额 = qty × unit_price（计算态，永不写）"
    )


class Shipment(BaseModel):
    """发货单。PK/Title = shipment_id。MVP 一单一运（1:1）。"""

    shipment_id: str = own(OWN_SOURCE, "发货单号（PK/Title）")
    order_id: str = own(OWN_SOURCE, "履约订单（FK->Order）")
    warehouse_id: str = own(OWN_SOURCE, "发货仓（FK->Warehouse）")
    status: Literal["shipped", "delivered"] = own(
        OWN_SOURCE, "发货状态（create_shipment 即置 shipped）"
    )
    tracking_no: str = own(OWN_SOURCE, "运单号（自动生成）")
    shipped_at: datetime = own(OWN_SOURCE, "出库时间")


class Refund(BaseModel):
    """退款申请。PK/Title = refund_id。MVP 整单退款为主。"""

    refund_id: str = own(OWN_SOURCE, "退款单号（PK/Title）")
    order_id: str = own(OWN_SOURCE, "退款订单（FK->Order）")
    amount_cents: int = own(OWN_SOURCE, "退款金额（分）")
    status: Literal["pending", "approved", "rejected"] = own(OWN_SOURCE, "退款状态")
    reason: str = own(OWN_SOURCE, "客户申请原因")
    review_note: str | None = own(
        OWN_ONTOLOGY, "审核备注（本体自有状态，源系统无此列）", default=None
    )
    created_at: datetime = own(OWN_SOURCE, "申请时间")
    reviewed_at: datetime | None = own(OWN_SOURCE, "审核时间", default=None)


class ObjectTypeDef(BaseModel):
    """对象类型注册定义（§3.2）：模型 + 主键 + API 命名 + 源系统承载表。"""

    name: str
    api_name: str
    description: str
    model: type[BaseModel]
    pk_field: str
    title_field: str | None = None
    source_table: str


def _obj(
    name: str,
    api_name: str,
    description: str,
    model: type[BaseModel],
    pk_field: str,
    source_table: str,
) -> ObjectTypeDef:
    return ObjectTypeDef(
        name=name,
        api_name=api_name,
        description=description,
        model=model,
        pk_field=pk_field,
        title_field=pk_field,
        source_table=source_table,
    )


OBJECT_TYPES: list[ObjectTypeDef] = [
    _obj("Customer", "customer", "客户", Customer, "customer_id", "customers"),
    _obj("Product", "product", "商品", Product, "product_id", "products"),
    _obj("Warehouse", "warehouse", "仓库", Warehouse, "warehouse_id", "warehouses"),
    _obj("Inventory", "inventory", "库存", Inventory, "inventory_id", "inventory"),
    _obj("Order", "order", "订单", Order, "order_id", "orders"),
    _obj(
        "OrderItem", "order_item", "订单行", OrderItem, "order_item_id", "order_items"
    ),
    _obj("Shipment", "shipment", "发货", Shipment, "shipment_id", "shipments"),
    _obj("Refund", "refund", "退款", Refund, "refund_id", "refunds"),
]
