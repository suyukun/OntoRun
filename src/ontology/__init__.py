"""本体 schema 定义与注册（D2，技术方案 §2.2/§2.3/§2.4 + §3.2）。

build_registry() 为统一入口：8 对象 / 8 链接 / 6 动作注册后返回 Registry，
供 runtime（B1/B2）、API（B3）、Agent 工具生成（A2）消费。
"""

from src.ontology.actions import (
    ACTIONS,
    CANONICAL_ERROR_CODES,
    ActionDef,
    Precondition,
    StateEffects,
)
from src.ontology.links import LINK_TYPES, LinkTypeDef
from src.ontology.objects import OBJECT_TYPES, ObjectTypeDef, field_ownership
from src.ontology.registry import Issue, Registry


def build_registry() -> Registry:
    """注册全部对象/链接/动作，返回 Registry（self_check 由调用方执行）。"""
    reg = Registry()
    for obj in OBJECT_TYPES:
        reg.register_object_type(obj)
    for link in LINK_TYPES:
        reg.register_link_type(link)
    for action in ACTIONS:
        reg.register_action_type(action)
    return reg


__all__ = [
    "ACTIONS",
    "CANONICAL_ERROR_CODES",
    "LINK_TYPES",
    "OBJECT_TYPES",
    "ActionDef",
    "Issue",
    "LinkTypeDef",
    "ObjectTypeDef",
    "Precondition",
    "Registry",
    "StateEffects",
    "build_registry",
    "field_ownership",
]
