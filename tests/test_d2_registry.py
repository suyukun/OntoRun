"""D2 验收测试：本体 schema 定义与注册。

技术方案依据：§2.2 对象清单（8）、§2.3 链接（8，双向命名）、§2.4 动作（6）、
§3.2 registry 自检（主键唯一 / 链接双向命名一致 / 动作参数完整 / 状态归属标注）、§4.3 错误码全集。
S2 P1a/P2：DES 对象（Material/Code + P2 主体对象 Vendor/InventoryLocation/FinanceEntry）同注册表。
"""

import pytest
from pydantic import BaseModel

from src.ontology import build_registry
from src.ontology.actions import (
    CANONICAL_ERROR_CODES,
    ActionDef,
    Precondition,
    StateEffects,
)
from src.ontology.links import LinkTypeDef
from src.ontology.objects import (
    OWN_DERIVED,
    OWN_ONTOLOGY,
    OWN_SOURCE,
    ObjectTypeDef,
    field_ownership,
)
from src.ontology.registry import Registry

EXPECTED_OBJECTS = {
    "Customer",
    "Product",
    "Warehouse",
    "Inventory",
    "Order",
    "OrderItem",
    "Shipment",
    "Refund",
}
# P2 ChatBI 主体对象（2026-08-21 Jack 拍板；Customer 复用 S1 零售对象，其余 3 个新注册）
P2_SUBJECT_OBJECTS = {"Customer", "Vendor", "InventoryLocation", "FinanceEntry"}
EXPECTED_ACTIONS = {
    "create_order",
    "confirm_order",
    "cancel_order",
    "create_shipment",
    "adjust_inventory",
    "approve_refund",
}


@pytest.fixture(scope="module")
def registry() -> Registry:
    return build_registry()


# ---------- 加载与数量 ----------


def test_registry_loads(registry):
    # S2 P1a/P2：DES 对象（Material/Code + P2 主体对象 Vendor/InventoryLocation/FinanceEntry）
    # 与 S1 8 对象同一注册表（设计 §1.4/§1.5），共 13 个
    assert len(registry.object_types()) == 13
    assert EXPECTED_OBJECTS <= {t.name for t in registry.object_types()}
    assert {"Material", "Code"} <= {t.name for t in registry.object_types()}
    # P2 4 个指标主体对象全部已注册（解除 planned，M1 前置）
    assert P2_SUBJECT_OBJECTS <= {t.name for t in registry.object_types()}


def test_link_count_and_names(registry):
    # S2 P1a：hasCode（material.codes）追加注册，共 9 条链接（设计 §1.4）
    assert len(registry.link_types()) == 9
    names = [l.name for l in registry.link_types()]
    assert (
        "order.customer" in names and "order.items" in names and "refund.order" in names
    )
    assert "material.codes" in names


def test_action_count(registry):
    assert len(registry.actions()) == 6
    assert {a.name for a in registry.actions()} == EXPECTED_ACTIONS


# ---------- self_check ----------


def test_self_check_zero_issues(registry):
    issues = registry.self_check()
    assert issues == [], f"self_check 发现问题: {[i.message for i in issues]}"


# ---------- 状态归属标注 ----------


def test_all_object_fields_have_ownership(registry):
    for obj in registry.object_types():
        for fname in obj.model.model_fields:
            own = field_ownership(obj.model, fname)
            assert own in (OWN_SOURCE, OWN_ONTOLOGY, OWN_DERIVED), (
                f"{obj.name}.{fname} 缺少状态归属标注"
            )


def test_three_ownership_categories_present(registry):
    """三分类都要真实出现：derived（available_qty/line_total）与 ontology-owned（cancel_reason/review_note）。"""
    inv = registry.object_type("Inventory")
    assert field_ownership(inv.model, "available_qty") == OWN_DERIVED
    oi = registry.object_type("OrderItem")
    assert field_ownership(oi.model, "line_total_cents") == OWN_DERIVED
    order = registry.object_type("Order")
    assert field_ownership(order.model, "cancel_reason") == OWN_ONTOLOGY
    refund = registry.object_type("Refund")
    assert field_ownership(refund.model, "review_note") == OWN_ONTOLOGY


# ---------- 链接双向命名 ----------


def test_links_bidirectional_naming(registry):
    """inverse_name 必须以目标类型 api_name 开头（如 order.customer ↔ customer.orders），且全局唯一。"""
    api = {t.name: t.api_name for t in registry.object_types()}
    seen = set()
    for link in registry.link_types():
        prefix = f"{api[link.target_type]}."
        assert link.inverse_name.startswith(prefix), (
            f"{link.name} 的 inverse_name={link.inverse_name} 应以 {prefix} 开头"
        )
        assert link.name not in seen and link.inverse_name not in seen, "链接命名重复"
        seen.add(link.name)
        seen.add(link.inverse_name)


def test_link_fk_field_exists(registry):
    """外键字段必须存在于正确一侧的对象模型上（N:1 在 source，1:N 在 target）。"""
    for link in registry.link_types():
        model = (
            registry.object_type(link.source_type).model
            if link.cardinality == "N:1"
            else registry.object_type(link.target_type).model
        )
        assert link.fk_field in model.model_fields, (
            f"{link.name} 的 fk 字段 {link.fk_field} 不存在"
        )


# ---------- 动作：参数 / 前置规则 / 错误码 / 状态归属 ----------


def test_action_params_complete(registry):
    """每个动作的参数模型可导出 JSON Schema（类型/必填完整），且必填字段非空。"""
    for action in registry.actions():
        schema = action.params_model.model_json_schema()
        assert schema.get("properties"), f"{action.name} 参数 schema 为空"
        assert action.params_model.model_fields, f"{action.name} 无参数"
        assert schema.get("required"), f"{action.name} 应有必填参数"


def test_canonical_error_codes_include_a1_codes():
    """§4.3：create_order 的客户/商品不存在·下架三码必须在内（LLM 反馈粒度）。"""
    for code in ("CUSTOMER_NOT_FOUND", "PRODUCT_NOT_FOUND", "PRODUCT_INACTIVE"):
        assert code in CANONICAL_ERROR_CODES, f"{code} 不在错误码全集"


def test_create_order_has_dedicated_error_codes(registry):
    """create_order 前置规则用独立三码，而非笼统归入 INVALID_PARAMS。"""
    create = registry.action("create_order")
    codes = [pc.error_code for pc in create.preconditions]
    assert "CUSTOMER_NOT_FOUND" in codes
    assert "PRODUCT_NOT_FOUND" in codes
    assert "PRODUCT_INACTIVE" in codes
    assert "OUT_OF_STOCK" in codes
    assert "INVALID_PARAMS" not in codes


def test_action_error_codes_within_canonical(registry):
    """动作声明的错误码 ⊆ §4.3 全集；每条前置规则引用的错误码 ⊆ 动作声明集。"""
    for action in registry.actions():
        assert set(action.error_codes) <= set(CANONICAL_ERROR_CODES), (
            f"{action.name} 含全集外错误码"
        )
        for pc in action.preconditions:
            assert pc.error_code in CANONICAL_ERROR_CODES
            assert pc.error_code in action.error_codes, (
                f"{action.name} 前置规则引用 {pc.error_code} 未声明"
            )


def test_actions_have_state_effects(registry):
    """每个动作都标注状态归属效果；approve_refund 标记为高风险（双签）。"""
    for action in registry.actions():
        eff = action.state_effects
        assert eff.source_backed or eff.ontology_owned, f"{action.name} 无任何状态效果"
        for field in eff.source_backed + eff.ontology_owned + eff.derived:
            assert isinstance(field, str) and field, (
                f"{action.name} 效果字段非法: {field}"
            )
    refund = registry.action("approve_refund")
    assert refund.high_risk is True
    cancel = registry.action("cancel_order")
    assert "Order.status" in cancel.state_effects.source_backed
    assert "Inventory.reserved_qty" in cancel.state_effects.source_backed
    assert "Order.cancel_reason" in cancel.state_effects.ontology_owned


def test_state_effects_reference_real_fields(registry):
    """动作效果里引用的 '<Type>.<field>' 必须真实存在于对象定义且归属一致。"""
    fields_by_ownership = {OWN_SOURCE: set(), OWN_ONTOLOGY: set(), OWN_DERIVED: set()}
    for obj in registry.object_types():
        for fname in obj.model.model_fields:
            own = field_ownership(obj.model, fname)
            fields_by_ownership[own].add(f"{obj.name}.{fname}")
    for action in registry.actions():
        for field in action.state_effects.source_backed:
            assert field in fields_by_ownership[OWN_SOURCE], (
                f"{action.name} 效果 {field} 非 source-backed"
            )
        for field in action.state_effects.ontology_owned:
            assert field in fields_by_ownership[OWN_ONTOLOGY], (
                f"{action.name} 效果 {field} 非 ontology-owned"
            )


def test_cancel_order_preconditions_order(registry):
    """cancel_order 的三条前置规则按序声明（三问测试 3 的机制依据）。"""
    cancel = registry.action("cancel_order")
    codes = [pc.error_code for pc in cancel.preconditions]
    assert codes == [
        "ORDER_NOT_FOUND",
        "ORDER_NOT_CANCELLABLE",
        "SHIPPED_ORDER_CANNOT_BE_CANCELLED",
    ]


# ---------- registry 负向路径（self_check 能发现问题 / 重复注册被拒） ----------


def test_duplicate_object_registration_rejected():
    reg = Registry()
    obj = ObjectTypeDef(
        name="Customer",
        api_name="customer",
        description="d",
        model=BaseModel,
        pk_field="customer_id",
        source_table="customers",
    )
    reg.register_object_type(obj)
    with pytest.raises(ValueError):
        reg.register_object_type(obj)


def test_self_check_flags_unknown_link_source():
    reg = Registry()
    reg.register_object_type(
        ObjectTypeDef(
            name="Customer",
            api_name="customer",
            description="d",
            model=BaseModel,
            pk_field="customer_id",
            source_table="customers",
        )
    )
    reg.register_link_type(
        LinkTypeDef(
            name="order.customer",
            source_type="Ghost",
            target_type="Customer",
            cardinality="N:1",
            fk_field="customer_id",
            inverse_name="customer.ghost",
            description="坏链接",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_UNKNOWN_SOURCE" in codes


def test_self_check_flags_bad_inverse_name():
    reg = Registry()
    reg.register_object_type(
        ObjectTypeDef(
            name="Order",
            api_name="order",
            description="d",
            model=BaseModel,
            pk_field="order_id",
            source_table="orders",
        )
    )
    reg.register_object_type(
        ObjectTypeDef(
            name="Customer",
            api_name="customer",
            description="d",
            model=BaseModel,
            pk_field="customer_id",
            source_table="customers",
        )
    )
    reg.register_link_type(
        LinkTypeDef(
            name="order.customer",
            source_type="Order",
            target_type="Customer",
            cardinality="N:1",
            fk_field="customer_id",
            inverse_name="wrong.naming",
            description="命名错误",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_INVERSE_MISMATCH" in codes


def test_self_check_flags_inverse_duplicate():
    """反向名前缀正确但重复（两个链接共用同一 inverse_name）必须被 self_check 检出。"""
    reg = Registry()
    for name in ("Order", "Customer", "Shipment"):
        reg.register_object_type(
            ObjectTypeDef(
                name=name,
                api_name=name.lower(),
                description="d",
                model=BaseModel,
                pk_field=f"{name.lower()}_id",
                source_table=name.lower(),
            )
        )
    reg.register_link_type(
        LinkTypeDef(
            name="order.customer",
            source_type="Order",
            target_type="Customer",
            cardinality="N:1",
            fk_field="customer_id",
            inverse_name="customer.orders",
            description="链接 A",
        )
    )
    reg.register_link_type(
        LinkTypeDef(
            name="shipment.order",
            source_type="Shipment",
            target_type="Order",
            cardinality="N:1",
            fk_field="order_id",
            inverse_name="customer.orders",
            description="链接 B（反向名与 A 重复）",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_INVERSE_DUPLICATE" in codes


def test_self_check_flags_unknown_action_error_code():
    reg = Registry()

    class FakeParams(BaseModel):
        customer_id: str

    reg.register_action_type(
        ActionDef(
            name="fake_action",
            description="d",
            params_model=FakeParams,
            preconditions=[Precondition(error_code="NOT_A_REAL_CODE", summary="x")],
            state_effects=StateEffects(source_backed=["Customer.name"]),
            error_codes=["NOT_A_REAL_CODE"],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_ERROR_CODE_UNKNOWN" in codes


def test_self_check_flags_missing_ownership():
    reg = Registry()

    class NoOwnership(BaseModel):
        x: str

    reg.register_object_type(
        ObjectTypeDef(
            name="Broken",
            api_name="broken",
            description="d",
            model=NoOwnership,
            pk_field="x",
            source_table="broken",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "FIELD_MISSING_OWNERSHIP" in codes


def test_self_check_flags_unknown_target_and_fk():
    reg = Registry()
    reg.register_object_type(
        ObjectTypeDef(
            name="Order",
            api_name="order",
            description="d",
            model=BaseModel,
            pk_field="order_id",
            source_table="orders",
        )
    )
    reg.register_link_type(
        LinkTypeDef(
            name="order.ghost",
            source_type="Order",
            target_type="Ghost",
            cardinality="1:N",
            fk_field="ghost_id",
            inverse_name="ghost.orders",
            description="坏目标",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_UNKNOWN_TARGET" in codes
    # FK 检查对未注册类型跳过（continue），另行验证
    reg2 = Registry()
    reg2.register_object_type(
        ObjectTypeDef(
            name="Order",
            api_name="order",
            description="d",
            model=BaseModel,
            pk_field="order_id",
            source_table="orders",
        )
    )
    reg2.register_object_type(
        ObjectTypeDef(
            name="OrderItem",
            api_name="order_item",
            description="d",
            model=BaseModel,
            pk_field="order_item_id",
            source_table="order_items",
        )
    )
    reg2.register_link_type(
        LinkTypeDef(
            name="order.items",
            source_type="Order",
            target_type="OrderItem",
            cardinality="1:N",
            fk_field="order_id",
            inverse_name="order_item.orders",
            description="缺 FK",
        )
    )
    codes2 = {i.code for i in reg2.self_check()}
    assert "LINK_FK_MISSING" in codes2


def test_self_check_flags_action_no_params():
    reg = Registry()

    class EmptyParams(BaseModel):
        pass

    reg.register_action_type(
        ActionDef(
            name="no_params",
            description="d",
            params_model=EmptyParams,
            preconditions=[],
            state_effects=StateEffects(source_backed=["Customer.name"]),
            error_codes=[],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_NO_PARAMS" in codes


def test_self_check_flags_effect_unknown_field():
    reg = Registry()
    from src.ontology.objects import Customer

    reg.register_object_type(
        ObjectTypeDef(
            name="Customer",
            api_name="customer",
            description="d",
            model=Customer,
            pk_field="customer_id",
            source_table="customers",
        )
    )

    class P(BaseModel):
        x: str

    reg.register_action_type(
        ActionDef(
            name="touches_ghost",
            description="d",
            params_model=P,
            preconditions=[],
            state_effects=StateEffects(source_backed=["Order.status"]),
            error_codes=[],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_EFFECT_UNKNOWN_FIELD" in codes


def test_duplicate_action_registration_rejected():
    reg = Registry()
    from src.ontology.actions import ACTIONS

    reg.register_action_type(ACTIONS[0])
    with pytest.raises(ValueError):
        reg.register_action_type(ACTIONS[0])


def test_own_rejects_illegal_ownership():
    from src.ontology.objects import own

    with pytest.raises(ValueError):
        own("bogus", "非法归属")


# ---------- self_check 负路径补测（red-team 第 7 项：registry 覆盖率红线 80%+） ----------


def _obj(name, api_name, model, pk_field, source_table) -> ObjectTypeDef:
    return ObjectTypeDef(
        name=name,
        api_name=api_name,
        description="d",
        model=model,
        pk_field=pk_field,
        source_table=source_table,
    )


def test_self_check_flags_object_api_name_invalid():
    """对象 api_name 不符合 ^[a-z][a-z0-9_]*$（含大写）→ OBJECT_API_NAME_INVALID。"""
    reg = Registry()
    reg.register_object_type(_obj("Order", "BadName", BaseModel, "order_id", "orders"))
    codes = {i.code for i in reg.self_check()}
    assert "OBJECT_API_NAME_INVALID" in codes


def test_self_check_flags_object_no_source_table():
    """对象缺少源系统承载表 → OBJECT_NO_SOURCE_TABLE。"""
    reg = Registry()
    reg.register_object_type(_obj("Order", "order", BaseModel, "order_id", ""))
    codes = {i.code for i in reg.self_check()}
    assert "OBJECT_NO_SOURCE_TABLE" in codes


def test_self_check_flags_link_name_duplicate():
    """两个链接共用同一正向名 → LINK_NAME_DUPLICATE（反向名不重复）。"""
    from src.ontology.objects import Customer, Order

    reg = Registry()
    reg.register_object_type(_obj("Order", "order", Order, "order_id", "orders"))
    reg.register_object_type(
        _obj("Customer", "customer", Customer, "customer_id", "customers")
    )
    for i in range(2):
        reg.register_link_type(
            LinkTypeDef(
                name="order.customer",
                source_type="Order",
                target_type="Customer",
                cardinality="N:1",
                fk_field="customer_id",
                inverse_name=f"customer.orders{i}",
                description=f"链接 {i}",
            )
        )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_NAME_DUPLICATE" in codes


def test_self_check_flags_self_loop_link():
    """自环链接（source_type == target_type）→ LINK_SELF_LOOP。"""
    from src.ontology.objects import Order

    reg = Registry()
    reg.register_object_type(_obj("Order", "order", Order, "order_id", "orders"))
    reg.register_link_type(
        LinkTypeDef(
            name="order.parent",
            source_type="Order",
            target_type="Order",
            cardinality="N:1",
            fk_field="customer_id",
            inverse_name="order.children",
            description="自环链接",
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "LINK_SELF_LOOP" in codes


def test_self_check_flags_params_schema_fail():
    """参数模型 JSON Schema 导出失败 → ACTION_PARAMS_SCHEMA_FAIL。"""
    reg = Registry()

    class BrokenParams(BaseModel):
        x: str

        @classmethod
        def model_json_schema(cls, *args, **kwargs):
            raise RuntimeError("schema 导出失败")

    reg.register_action_type(
        ActionDef(
            name="broken_schema",
            description="d",
            params_model=BrokenParams,
            preconditions=[],
            state_effects=StateEffects(source_backed=["Customer.name"]),
            error_codes=[],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_PARAMS_SCHEMA_FAIL" in codes


def test_self_check_flags_precondition_undeclared():
    """前置规则错误码合法（§4.3 全集内）但未在 action.error_codes 声明 → UNDECLARED。"""
    reg = Registry()

    class P(BaseModel):
        x: str

    reg.register_action_type(
        ActionDef(
            name="undeclared_pc",
            description="d",
            params_model=P,
            preconditions=[Precondition(error_code="ORDER_NOT_FOUND", summary="x")],
            state_effects=StateEffects(source_backed=["Customer.name"]),
            error_codes=["INVALID_PARAMS"],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_PRECONDITION_UNDECLARED" in codes
    assert "ACTION_PRECONDITION_UNKNOWN" not in codes  # 错误码本身在全集内


def test_self_check_flags_no_effects():
    """动作无任何状态效果（source_backed/ontology_owned 均空）→ ACTION_NO_EFFECTS。"""
    reg = Registry()

    class P(BaseModel):
        x: str

    reg.register_action_type(
        ActionDef(
            name="no_effects",
            description="d",
            params_model=P,
            preconditions=[],
            state_effects=StateEffects(),
            error_codes=[],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_NO_EFFECTS" in codes


def test_self_check_accepts_derived_effects():
    """derived 效果标注引用真实 derived 字段 → self_check 零问题（覆盖 derived 校验循环）。"""
    from src.ontology.objects import Customer, Inventory

    reg = Registry()
    reg.register_object_type(
        _obj("Customer", "customer", Customer, "customer_id", "customers")
    )
    reg.register_object_type(
        _obj("Inventory", "inventory", Inventory, "inventory_id", "inventory")
    )

    class P(BaseModel):
        x: str

    reg.register_action_type(
        ActionDef(
            name="derived_effect",
            description="d",
            params_model=P,
            preconditions=[],
            state_effects=StateEffects(
                source_backed=["Customer.name"], derived=["Inventory.available_qty"]
            ),
            error_codes=[],
        )
    )
    issues = reg.self_check()
    assert issues == [], (
        f"含 derived 效果的动作应自检通过: {[i.message for i in issues]}"
    )


def test_self_check_flags_effect_ownership_mismatch():
    """效果字段存在但归属标注与定义不符（ontology-owned 标成 source-backed）→ MISMATCH。"""
    from src.ontology.objects import Order

    reg = Registry()
    reg.register_object_type(_obj("Order", "order", Order, "order_id", "orders"))

    class P(BaseModel):
        x: str

    reg.register_action_type(
        ActionDef(
            name="mismatch_effect",
            description="d",
            params_model=P,
            preconditions=[],
            state_effects=StateEffects(source_backed=["Order.cancel_reason"]),
            error_codes=[],
        )
    )
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_EFFECT_OWNERSHIP_MISMATCH" in codes
