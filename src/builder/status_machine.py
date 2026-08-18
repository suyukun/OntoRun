"""E4 状态机（蓝图 v0.3 §4 / 补丁 v0.3.1 B4）。

P1 范围：object_types / link_types 的 draft -> reviewed -> published 三态。
- draft: 新建/编辑中；
- reviewed: 已审核，等待发布；
- published: 已发布到运行时 Registry（不可回退不可删）。

非法流转通过 IllegalTransitionError 抛出，由 API 层映射为 BUILDER_INVALID_STATUS_TRANSITION。
P4 阶段逻辑规则 / 动作类型可能也复用此状态机；当前模块先支撑 object_types / link_types。
"""

from __future__ import annotations

from typing import Final

DRAFT: Final = "draft"
REVIEWED: Final = "reviewed"
PUBLISHED: Final = "published"

# 合法状态集（与 BUILDER_SCHEMA CHECK 约束一致，补丁 A3）
ALL_STATUSES: Final = (DRAFT, REVIEWED, PUBLISHED)

# 合法流转图：当前状态 -> 允许的下一态集合
_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    DRAFT: frozenset({REVIEWED}),
    REVIEWED: frozenset({PUBLISHED}),
    PUBLISHED: frozenset(),  # 终态
}


class IllegalTransitionError(ValueError):
    """非法状态流转；API 层映射为 BUILDER_INVALID_STATUS_TRANSITION（4xx）。"""

    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(f"非法状态流转: {current} -> {target}")


def assert_transition(current: str, target: str) -> None:
    """断言从 current 流转到 target 合法；非法时抛 IllegalTransitionError。"""
    if current not in _TRANSITIONS:
        raise IllegalTransitionError(current, target)
    if target not in _TRANSITIONS[current]:
        raise IllegalTransitionError(current, target)


def allowed_next(current: str) -> frozenset[str]:
    """查询 current 状态的合法下一态集合（公开给 API 详情页等）。"""
    return _TRANSITIONS.get(current, frozenset())


def is_terminal(status: str) -> bool:
    """是否终态（不可流转、不可删）。"""
    return status == PUBLISHED
