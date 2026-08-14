"""动作类型定义 —— 6 个业务动作（技术方案 §2.4）与错误码全集（§4.3）。

每个动作 = 参数模型（Pydantic，导出 JSON Schema 供前端表单/LLM 工具生成）
          + 前置规则（submission criteria，声明式错误码）
          + 状态归属效果（source-backed / ontology-owned / derived 标注，§2.7）
执行管道本身由 runtime/action_engine（B2）实现；本模块是声明与注册。
"""

from typing import Literal

from pydantic import BaseModel, Field

# §4.3 错误码全集（MVP）——新增错误码必须先修技术方案
CANONICAL_ERROR_CODES: tuple[str, ...] = (
    "INVALID_PARAMS",
    "UNKNOWN_ACTION",
    "ORDER_NOT_FOUND",
    "INVENTORY_NOT_FOUND",
    "CUSTOMER_NOT_FOUND",
    "PRODUCT_NOT_FOUND",
    "PRODUCT_INACTIVE",
    "OUT_OF_STOCK",
    "ORDER_NOT_CONFIRMABLE",
    "ORDER_NOT_CANCELLABLE",
    "SHIPPED_ORDER_CANNOT_BE_CANCELLED",
    "ORDER_NOT_SHIPPABLE",
    "INSUFFICIENT_INVENTORY",
    "INSUFFICIENT_RESERVED",
    "REFUND_NOT_PENDING",
    "AMOUNT_EXCEEDS_PAID",
    "REFUND_NOT_ALLOWED",
)


class Precondition(BaseModel):
    """前置规则（submission criteria）：错误码 + 规则摘要。"""

    error_code: str
    summary: str


class StateEffects(BaseModel):
    """动作的状态归属效果标注（§2.7）：<Type>.<field> 引用对象字段。"""

    source_backed: list[str] = Field(
        default_factory=list, description="写回源系统的字段"
    )
    ontology_owned: list[str] = Field(
        default_factory=list, description="本体自有状态字段"
    )
    derived: list[str] = Field(
        default_factory=list, description="计算态（动作不写，仅标注）"
    )


class ActionDef(BaseModel):
    """动作类型注册定义。"""

    name: str
    description: str  # LLM 面向描述（含前置规则摘要，§5.2）
    params_model: type[BaseModel]
    preconditions: list[Precondition]
    state_effects: StateEffects
    error_codes: list[str]
    high_risk: bool = False  # 高风险动作需人机双签（§5.4）


# ---- 参数模型（LLM 输出视为不可信输入：类型/枚举/边界/长度上限经 Pydantic 校验，§5.4） ----
# 长度上限：ID 类 64（seed 主键格式上限宽松），自由文本 500（reason/review_note 等）
_STR_MAX = 64
_TEXT_MAX = 500


class OrderItemInput(BaseModel):
    product_id: str = Field(max_length=_STR_MAX)
    qty: int = Field(ge=1)


class CreateOrderParams(BaseModel):
    customer_id: str = Field(max_length=_STR_MAX)
    items: list[OrderItemInput] = Field(min_length=1)


class ConfirmOrderParams(BaseModel):
    order_id: str = Field(max_length=_STR_MAX)


class CancelOrderParams(BaseModel):
    order_id: str = Field(max_length=_STR_MAX)
    reason: str | None = Field(default=None, max_length=_TEXT_MAX)


class CreateShipmentParams(BaseModel):
    order_id: str = Field(max_length=_STR_MAX)
    warehouse_id: str = Field(max_length=_STR_MAX)


class AdjustInventoryParams(BaseModel):
    warehouse_id: str = Field(max_length=_STR_MAX)
    product_id: str = Field(max_length=_STR_MAX)
    new_on_hand_qty: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=_TEXT_MAX)


class ApproveRefundParams(BaseModel):
    refund_id: str = Field(max_length=_STR_MAX)
    decision: Literal["approved", "rejected"]
    review_note: str = Field(max_length=_TEXT_MAX)


ACTIONS: list[ActionDef] = [
    ActionDef(
        name="create_order",
        description=(
            "下单：按客户与商品行创建订单（pending）并锁定库存 reserved+=qty；"
            "目标仓可用量不足时拒绝（返回当前可用量）。"
        ),
        params_model=CreateOrderParams,
        preconditions=[
            Precondition(error_code="CUSTOMER_NOT_FOUND", summary="customer 存在"),
            Precondition(error_code="PRODUCT_NOT_FOUND", summary="product 存在"),
            Precondition(
                error_code="PRODUCT_INACTIVE",
                summary="product status=active（已下架拒绝下单）",
            ),
            Precondition(
                error_code="OUT_OF_STOCK",
                summary="每个订单行：目标仓 available_qty ≥ qty，否则返回当前可用量",
            ),
        ],
        state_effects=StateEffects(
            source_backed=["Order.status", "OrderItem.qty", "Inventory.reserved_qty"]
        ),
        error_codes=[
            "INVALID_PARAMS",
            "CUSTOMER_NOT_FOUND",
            "PRODUCT_NOT_FOUND",
            "PRODUCT_INACTIVE",
            "OUT_OF_STOCK",
        ],
    ),
    ActionDef(
        name="confirm_order",
        description="履约确认：仅 pending 订单可确认，状态 → confirmed。",
        params_model=ConfirmOrderParams,
        preconditions=[
            Precondition(error_code="ORDER_NOT_FOUND", summary="订单存在"),
            Precondition(
                error_code="ORDER_NOT_CONFIRMABLE", summary="status 必须为 pending"
            ),
        ],
        state_effects=StateEffects(source_backed=["Order.status"]),
        error_codes=["INVALID_PARAMS", "ORDER_NOT_FOUND", "ORDER_NOT_CONFIRMABLE"],
    ),
    ActionDef(
        name="cancel_order",
        description=(
            "取消订单（三问测试对象）：仅 pending/confirmed 且无 shipped/delivered "
            "shipment 的订单可取消；取消后释放未发货行库存 reserved-=qty，"
            "cancel_reason 落本体自有状态。已发货订单请走退款流程。"
        ),
        params_model=CancelOrderParams,
        preconditions=[
            Precondition(error_code="ORDER_NOT_FOUND", summary="订单存在"),
            Precondition(
                error_code="ORDER_NOT_CANCELLABLE",
                summary="status ∈ {pending, confirmed}（shipped/delivered/cancelled/refunded 拒绝）",
            ),
            Precondition(
                error_code="SHIPPED_ORDER_CANNOT_BE_CANCELLED",
                summary="无任何关联 shipment 处于 shipped/delivered（已发货拦截，三问 3）",
            ),
        ],
        state_effects=StateEffects(
            source_backed=["Order.status", "Inventory.reserved_qty"],
            ontology_owned=["Order.cancel_reason"],
        ),
        error_codes=[
            "INVALID_PARAMS",
            "ORDER_NOT_FOUND",
            "ORDER_NOT_CANCELLABLE",
            "SHIPPED_ORDER_CANNOT_BE_CANCELLED",
        ],
    ),
    ActionDef(
        name="create_shipment",
        description=(
            "发货：仅 confirmed 订单可发货；校验该仓物理在库 on_hand ≥ 订单行总量；"
            "成功后建 Shipment(shipped)、订单 → shipped、on_hand-=qty、reserved-=qty。"
        ),
        params_model=CreateShipmentParams,
        preconditions=[
            Precondition(error_code="ORDER_NOT_FOUND", summary="订单存在"),
            Precondition(
                error_code="ORDER_NOT_SHIPPABLE",
                summary="order status=confirmed 且 warehouse 存在（后者归入参数校验）",
            ),
            Precondition(
                error_code="INSUFFICIENT_INVENTORY",
                summary="发货仓该品 on_hand_qty ≥ 订单行总量（物理在库校验，corner ④）",
            ),
        ],
        state_effects=StateEffects(
            source_backed=[
                "Shipment.status",
                "Order.status",
                "Inventory.on_hand_qty",
                "Inventory.reserved_qty",
            ]
        ),
        error_codes=[
            "INVALID_PARAMS",
            "ORDER_NOT_FOUND",
            "ORDER_NOT_SHIPPABLE",
            "INSUFFICIENT_INVENTORY",
        ],
    ),
    ActionDef(
        name="adjust_inventory",
        description=(
            "人工盘点/纠错：设置 on_hand_qty = new_on_hand_qty；不能把已锁库存调没"
            "（new_on_hand ≥ reserved），reason 必填。"
        ),
        params_model=AdjustInventoryParams,
        preconditions=[
            Precondition(error_code="INVENTORY_NOT_FOUND", summary="库存记录存在"),
            Precondition(
                error_code="INSUFFICIENT_RESERVED",
                summary="new_on_hand_qty ≥ reserved_qty（不能低于已锁库存，corner ④ 另一形态）",
            ),
            Precondition(error_code="INVALID_PARAMS", summary="reason 非空"),
        ],
        state_effects=StateEffects(source_backed=["Inventory.on_hand_qty"]),
        error_codes=["INVALID_PARAMS", "INVENTORY_NOT_FOUND", "INSUFFICIENT_RESERVED"],
    ),
    ActionDef(
        name="approve_refund",
        description=(
            "审核退款（高风险，LLM 提议 + 用户确认双签）：仅 pending 可审；"
            "approved 时金额 ≤ 实付-已批退款，且订单须已履约（shipped/delivered）或 "
            "已取消未退款；整单退款后订单 → refunded；review_note 落本体自有状态。"
        ),
        params_model=ApproveRefundParams,
        preconditions=[
            Precondition(
                error_code="REFUND_NOT_PENDING",
                summary="refund 存在且 status=pending（已审核再审 → 冲突，corner ③）",
            ),
            Precondition(
                error_code="AMOUNT_EXCEEDS_PAID",
                summary="amount_cents ≤ order.paid_cents − Σ(该单已批准退款)，否则超付（corner ③）",
            ),
            Precondition(
                error_code="REFUND_NOT_ALLOWED",
                summary="order 状态须为 shipped/delivered（已履约才可退），或 cancelled 且未退款",
            ),
        ],
        state_effects=StateEffects(
            source_backed=["Refund.status", "Order.status"],
            ontology_owned=["Refund.review_note"],
        ),
        error_codes=[
            "INVALID_PARAMS",
            "REFUND_NOT_PENDING",
            "AMOUNT_EXCEEDS_PAID",
            "REFUND_NOT_ALLOWED",
        ],
        high_risk=True,
    ),
]
