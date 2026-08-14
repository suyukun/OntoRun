"""链接类型定义 —— 8 条双向链接（技术方案 §2.3）。

双向命名约定：inverse_name = "<target_api_name>.<source_api_name>"（如
order.customer 的反向 = customer.orders）。外键位置由基数决定：
N:1 → 外键在 source（多对一，多的那侧持 FK）；1:N → 外键在 target。
"""

from typing import Literal

from pydantic import BaseModel


class LinkTypeDef(BaseModel):
    """链接类型注册定义。"""

    name: str  # 正向 API 名（从 source 出发遍历）
    source_type: str
    target_type: str
    cardinality: Literal["N:1", "1:N"]
    fk_field: str  # 外键字段（所在侧由 cardinality 决定）
    inverse_name: str  # 反向 API 名
    description: str


LINK_TYPES: list[LinkTypeDef] = [
    LinkTypeDef(
        name="order.customer",
        source_type="Order",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_id",
        inverse_name="customer.orders",
        description="下单：一个订单属于一个客户",
    ),
    LinkTypeDef(
        name="order.items",
        source_type="Order",
        target_type="OrderItem",
        cardinality="1:N",
        fk_field="order_id",
        inverse_name="order_item.order",
        description="包含：一个订单含多行",
    ),
    LinkTypeDef(
        name="order_item.product",
        source_type="OrderItem",
        target_type="Product",
        cardinality="N:1",
        fk_field="product_id",
        inverse_name="product.order_items",
        description="订购：订单行对应一个商品",
    ),
    LinkTypeDef(
        name="product.inventory_records",
        source_type="Product",
        target_type="Inventory",
        cardinality="1:N",
        fk_field="product_id",
        inverse_name="inventory.product",
        description="库存：一个商品有多个仓库存记录",
    ),
    LinkTypeDef(
        name="inventory.warehouse",
        source_type="Inventory",
        target_type="Warehouse",
        cardinality="N:1",
        fk_field="warehouse_id",
        inverse_name="warehouse.inventory_records",
        description="归属：库存记录属于一个仓库",
    ),
    LinkTypeDef(
        name="shipment.order",
        source_type="Shipment",
        target_type="Order",
        cardinality="N:1",
        fk_field="order_id",
        inverse_name="order.shipments",
        description="履约：发货单对应一个订单",
    ),
    LinkTypeDef(
        name="shipment.warehouse",
        source_type="Shipment",
        target_type="Warehouse",
        cardinality="N:1",
        fk_field="warehouse_id",
        inverse_name="warehouse.shipments",
        description="发货仓：从哪个仓库发出",
    ),
    LinkTypeDef(
        name="refund.order",
        source_type="Refund",
        target_type="Order",
        cardinality="N:1",
        fk_field="order_id",
        inverse_name="order.refunds",
        description="退款：退款申请对应一个订单",
    ),
]
