"""冲突消解策略（B2，技术方案 §3.4）。

- 策略 1 用户编辑优先（默认）：动作写回永远覆盖源系统当前值 —— MVP 实现；
- 策略 2 时间戳优先：编辑时间新于源系统 updated_at 才生效 —— 预留接口（发布期待定）；
- 读-改-写竞态：MVP 用 SQLite 单写连接 + 事务内重读根除（机制从简，不引分布式锁）。

接线说明：策略 1 的语义由 action_engine 各 handler 的"无条件写回"隐式执行——
compute_effects 计算新值 → writeback 覆盖源库当前值，即 user_edit_wins；
引擎不再显式调用 resolve()（原 conflict_strategy 参数已删，dead code），
本模块保留为策略 2（时间戳优先）等扩展点的声明与测试锚点。
"""

from __future__ import annotations

from typing import Any, Protocol

STRATEGY_USER_EDIT_WINS = "user_edit_wins"
STRATEGY_TIMESTAMP_WINS = "timestamp_wins"
DEFAULT_STRATEGY = STRATEGY_USER_EDIT_WINS


class ConflictResolver(Protocol):
    """冲突消解策略协议（策略 2 等扩展点）。"""

    def resolve(self, current: Any, incoming: Any) -> Any: ...


def resolve(strategy: str, current: Any, incoming: Any) -> Any:
    """按策略消解冲突并返回值。策略 1 恒取 incoming（动作写回覆盖当前值）。"""
    if strategy == STRATEGY_USER_EDIT_WINS:
        return incoming
    if strategy == STRATEGY_TIMESTAMP_WINS:
        raise NotImplementedError(
            "策略 2（时间戳优先）为预留接口，MVP 未实现（技术方案 §3.4 待定）"
        )
    raise ValueError(f"未知冲突消解策略: {strategy}")
