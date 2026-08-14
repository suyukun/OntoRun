"""D2 验收测试：本体 schema 定义与注册。

技术方案依据：§2.2 对象清单（8）、§2.3 链接（8，双向命名）、§2.4 动作（6）、
§3.2 registry 自检（主键唯一 / 链接双向命名一致 / 动作参数完整 / 状态归属标注）、§4.3 错误码全集。
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

EXPECTED_OBJECTS = {"Customer", "Product", "Warehouse", "Inventory",
                    "Order", "OrderItem", "Shipment", "Refund"}
EXPECTED_ACTIONS = {"create_order", "confirm_order", "cancel_order",
                    "create_shipment", "adjust_inventory", "approve_refund"}


@pytest.fixture(scope="module")
def registry() -> Registry:
    return build_registry()


# ---------- 加载与数量 ----------

def test_registry_loads(registry):
    assert len(registry.object_types()) == 8
    assert {t.name for t in registry.object_types()} == EXPECTED_OBJECTS


def test_link_count_and_names(registry):
    assert len(registry.link_types()) == 8
    names = [l.name for l in registry.link_types()]
    assert "order.customer" in names and "order.items" in names and "refund.order" in names


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
            assert own in (OWN_SOURCE, OWN_ONTOLOGY, OWN_DERIVED), \
                f"{obj.name}.{fname} 缺少状态归属标注"


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
        assert link.inverse_name.startswith(prefix), \
            f"{link.name} 的 inverse_name={link.inverse_name} 应以 {prefix} 开头"
        assert link.name not in seen and link.inverse_name not in seen, "链接命名重复"
        seen.add(link.name)
        seen.add(link.inverse_name)


def test_link_fk_field_exists(registry):
    """外键字段必须存在于正确一侧的对象模型上（N:1 在 source，1:N 在 target）。"""
    for link in registry.link_types():
        model = registry.object_type(link.source_type).model if link.cardinality == "N:1" \
            else registry.object_type(link.target_type).model
        assert link.fk_field in model.model_fields, f"{link.name} 的 fk 字段 {link.fk_field} 不存在"


# ---------- 动作：参数 / 前置规则 / 错误码 / 状态归属 ----------

def test_action_params_complete(registry):
    """每个动作的参数模型可导出 JSON Schema（类型/必填完整），且必填字段非空。"""
    for action in registry.actions():
        schema = action.params_model.model_json_schema()
        assert schema.get("properties"), f"{action.name} 参数 schema 为空"
        assert action.params_model.model_fields, f"{action.name} 无参数"
        assert schema.get("required"), f"{action.name} 应有必填参数"


def test_action_error_codes_within_canonical(registry):
    """动作声明的错误码 ⊆ §4.3 全集；每条前置规则引用的错误码 ⊆ 动作声明集。"""
    for action in registry.actions():
        assert set(action.error_codes) <= set(CANONICAL_ERROR_CODES), \
            f"{action.name} 含全集外错误码"
        for pc in action.preconditions:
            assert pc.error_code in CANONICAL_ERROR_CODES
            assert pc.error_code in action.error_codes, \
                f"{action.name} 前置规则引用 {pc.error_code} 未声明"


def test_actions_have_state_effects(registry):
    """每个动作都标注状态归属效果；approve_refund 标记为高风险（双签）。"""
    for action in registry.actions():
        eff = action.state_effects
        assert eff.source_backed or eff.ontology_owned, f"{action.name} 无任何状态效果"
        for field in eff.source_backed + eff.ontology_owned + eff.derived:
            assert isinstance(field, str) and field, f"{action.name} 效果字段非法: {field}"
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
            assert field in fields_by_ownership[OWN_SOURCE], f"{action.name} 效果 {field} 非 source-backed"
        for field in action.state_effects.ontology_owned:
            assert field in fields_by_ownership[OWN_ONTOLOGY], f"{action.name} 效果 {field} 非 ontology-owned"


def test_cancel_order_preconditions_order(registry):
    """cancel_order 的三条前置规则按序声明（三问测试 3 的机制依据）。"""
    cancel = registry.action("cancel_order")
    codes = [pc.error_code for pc in cancel.preconditions]
    assert codes == ["ORDER_NOT_FOUND", "ORDER_NOT_CANCELLABLE", "SHIPPED_ORDER_CANNOT_BE_CANCELLED"]


# ---------- registry 负向路径（self_check 能发现问题 / 重复注册被拒） ----------

def test_duplicate_object_registration_rejected():
    reg = Registry()
    obj = ObjectTypeDef(name="Customer", api_name="customer", description="d",
                        model=BaseModel, pk_field="customer_id", source_table="customers")
    reg.register_object_type(obj)
    with pytest.raises(ValueError):
        reg.register_object_type(obj)


def test_self_check_flags_unknown_link_source():
    reg = Registry()
    reg.register_object_type(ObjectTypeDef(name="Customer", api_name="customer", description="d",
                                           model=BaseModel, pk_field="customer_id", source_table="customers"))
    reg.register_link_type(LinkTypeDef(
        name="order.customer", source_type="Ghost", target_type="Customer",
        cardinality="N:1", fk_field="customer_id", inverse_name="customer.ghost",
        description="坏链接"))
    codes = {i.code for i in reg.self_check()}
    assert "LINK_UNKNOWN_SOURCE" in codes


def test_self_check_flags_bad_inverse_name():
    reg = Registry()
    reg.register_object_type(ObjectTypeDef(name="Order", api_name="order", description="d",
                                           model=BaseModel, pk_field="order_id", source_table="orders"))
    reg.register_object_type(ObjectTypeDef(name="Customer", api_name="customer", description="d",
                                           model=BaseModel, pk_field="customer_id", source_table="customers"))
    reg.register_link_type(LinkTypeDef(
        name="order.customer", source_type="Order", target_type="Customer",
        cardinality="N:1", fk_field="customer_id", inverse_name="wrong.naming",
        description="命名错误"))
    codes = {i.code for i in reg.self_check()}
    assert "LINK_INVERSE_MISMATCH" in codes


def test_self_check_flags_unknown_action_error_code():
    reg = Registry()

    class FakeParams(BaseModel):
        customer_id: str

    reg.register_action_type(ActionDef(
        name="fake_action", description="d", params_model=FakeParams,
        preconditions=[Precondition(error_code="NOT_A_REAL_CODE", summary="x")],
        state_effects=StateEffects(source_backed=["Customer.name"]),
        error_codes=["NOT_A_REAL_CODE"]))
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_ERROR_CODE_UNKNOWN" in codes


def test_self_check_flags_missing_ownership():
    reg = Registry()

    class NoOwnership(BaseModel):
        x: str

    reg.register_object_type(ObjectTypeDef(name="Broken", api_name="broken", description="d",
                                           model=NoOwnership, pk_field="x", source_table="broken"))
    codes = {i.code for i in reg.self_check()}
    assert "FIELD_MISSING_OWNERSHIP" in codes


def test_self_check_flags_unknown_target_and_fk():
    reg = Registry()
    reg.register_object_type(ObjectTypeDef(name="Order", api_name="order", description="d",
                                           model=BaseModel, pk_field="order_id", source_table="orders"))
    reg.register_link_type(LinkTypeDef(
        name="order.ghost", source_type="Order", target_type="Ghost",
        cardinality="1:N", fk_field="ghost_id", inverse_name="ghost.orders",
        description="坏目标"))
    codes = {i.code for i in reg.self_check()}
    assert "LINK_UNKNOWN_TARGET" in codes
    # FK 检查对未注册类型跳过（continue），另行验证
    reg2 = Registry()
    reg2.register_object_type(ObjectTypeDef(name="Order", api_name="order", description="d",
                                            model=BaseModel, pk_field="order_id", source_table="orders"))
    reg2.register_object_type(ObjectTypeDef(name="OrderItem", api_name="order_item", description="d",
                                            model=BaseModel, pk_field="order_item_id", source_table="order_items"))
    reg2.register_link_type(LinkTypeDef(
        name="order.items", source_type="Order", target_type="OrderItem",
        cardinality="1:N", fk_field="order_id", inverse_name="order_item.orders",
        description="缺 FK"))
    codes2 = {i.code for i in reg2.self_check()}
    assert "LINK_FK_MISSING" in codes2


def test_self_check_flags_action_no_params():
    reg = Registry()

    class EmptyParams(BaseModel):
        pass

    reg.register_action_type(ActionDef(
        name="no_params", description="d", params_model=EmptyParams,
        preconditions=[], state_effects=StateEffects(source_backed=["Customer.name"]),
        error_codes=[]))
    codes = {i.code for i in reg.self_check()}
    assert "ACTION_NO_PARAMS" in codes


def test_self_check_flags_effect_unknown_field():
    reg = Registry()
    from src.ontology.objects import Customer
    reg.register_object_type(ObjectTypeDef(name="Customer", api_name="customer", description="d",
                                           model=Customer, pk_field="customer_id", source_table="customers"))

    class P(BaseModel):
        x: str

    reg.register_action_type(ActionDef(
        name="touches_ghost", description="d", params_model=P,
        preconditions=[], state_effects=StateEffects(source_backed=["Order.status"]),
        error_codes=[]))
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
