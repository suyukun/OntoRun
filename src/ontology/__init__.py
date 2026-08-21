"""本体 schema 定义与注册（D2，技术方案 §2.2/§2.3/§2.4 + §3.2）。

build_registry() 为统一入口：8 对象 / 8 链接 / 6 动作 + DES 5 对象（Material/Code +
P2 ChatBI 主体对象 Vendor/InventoryLocation/FinanceEntry，2026-08-21 Jack 拍板；Customer
主体对象复用 S1 零售 Customer，同一注册表）/ 1 链接（hasCode）注册后返回 Registry，供
runtime（B1/B2）、API（B3）、Agent 工具生成（A2）消费。
DES 对象与 S1 8 对象同一注册表（设计 §1.4：/meta/schema 与本体驱动 UI 自动暴露新对象）。
"""

from src.ontology.actions import (
    ACTIONS,
    CANONICAL_ERROR_CODES,
    ActionDef,
    Precondition,
    StateEffects,
)
from src.ontology.des_objects import (
    CODE_SPACES,
    DES_LINK_TYPES,
    DES_OBJECT_TYPES,
    HAS_CODE_LINK,
    FinanceEntry,
    InventoryLocation,
    Material,
    MaterialType,
    Vendor,
    des_self_checks,
)
from src.ontology.links import LINK_TYPES, LinkTypeDef
from src.ontology.objects import OBJECT_TYPES, ObjectTypeDef, field_ownership
from src.ontology.registry import Issue, Registry


def build_registry() -> Registry:
    """注册全部对象/链接/动作（S1 8 + DES 5）与 DES self_check 钩子，返回 Registry。

    self_check 由调用方执行；instance_data（{类型名: [行 dict]}）可传物化数据做实例级校验。
    """
    reg = Registry()
    for obj in OBJECT_TYPES:
        reg.register_object_type(obj)
    for link in LINK_TYPES:
        reg.register_link_type(link)
    for action in ACTIONS:
        reg.register_action_type(action)
    for obj in DES_OBJECT_TYPES:
        reg.register_object_type(obj)
    for link in DES_LINK_TYPES:
        reg.register_link_type(link)
    reg.add_self_check(des_self_checks)
    return reg


__all__ = [
    "ACTIONS",
    "CANONICAL_ERROR_CODES",
    "CODE_SPACES",
    "DES_LINK_TYPES",
    "DES_OBJECT_TYPES",
    "HAS_CODE_LINK",
    "LINK_TYPES",
    "OBJECT_TYPES",
    "ActionDef",
    "FinanceEntry",
    "InventoryLocation",
    "Issue",
    "LinkTypeDef",
    "Material",
    "MaterialType",
    "ObjectTypeDef",
    "Precondition",
    "Registry",
    "StateEffects",
    "Vendor",
    "build_registry",
    "des_self_checks",
    "field_ownership",
]
