"""S4 M2 风险动作的 R1a/R2 规则校验挂接 —— confirm/adjust/submit 与 R1a 状态一致。

规则引擎在 src.runtime.risk_rules（纯函数 + 阈值落 base.ap_sys_param）；本模块把引擎
结果转换为 action_engine.Violation，供 risk_actions_impl 的 handler.validate_semantics
调用（校验发生在动作事务内、前置状态规则之前；规则违反 → rejected + 规则依据，源库零变更）。

作用域：仅 warn_reason 引用「R1a」的信号受约束（口径包 M2 注册范围=只注册剧本命中的
R1a/R2）；RNG 信号无引用 → 一律放行，既有行为不变。
"""

from __future__ import annotations

from typing import Any

from src.runtime.action_engine import Violation
from src.runtime.risk_rules import (
    RuleViolation,
    check_adjust_level,
    check_level_consistency,
    evaluate_warning,
    governing_level,
    is_r1a_governed,
)


def _to_violation(v: RuleViolation) -> Violation:
    return Violation(error_code=v.error_code, message=v.message, detail=v.detail)


def _evaluate(engine: Any, warning: dict[str, Any]):
    """信号所属集团的 R1a-only / R1a+R2 两口径结果（只读新连接，随用随关）。"""
    conn = engine.store.source_conn()
    try:
        return evaluate_warning(conn, warning)
    finally:
        conn.close()


def validate_confirm_level(
    engine: Any, warning: dict[str, Any] | None
) -> Violation | None:
    """confirm_warning：信号等级须与 R1a 管辖级别一致（reason 引用 R2 → R1a+R2，否则 R1a）。"""
    if warning is None or not is_r1a_governed(warning):
        return None
    r1a, r1a_r2 = _evaluate(engine, warning)
    if r1a is None:
        return None
    governing = governing_level(warning, r1a.level, r1a_r2.level)
    v = check_level_consistency(governing, warning["warn_level"], r1a, r1a_r2)
    return _to_violation(v) if v else None


def validate_adjust_level(
    engine: Any, warning: dict[str, Any] | None, new_level: str
) -> Violation | None:
    """adjust_warning_level：目标等级不得高于 R1a+R2 定级（升级红须 >12% 命中，否则拒绝）。"""
    if warning is None or not is_r1a_governed(warning):
        return None
    _r1a, r1a_r2 = _evaluate(engine, warning)
    if r1a_r2 is None:
        return None
    v = check_adjust_level(r1a_r2, new_level)
    return _to_violation(v) if v else None


def validate_disposal_level(
    engine: Any, warning: dict[str, Any] | None
) -> Violation | None:
    """submit_disposal：关联信号等级须与 R1a 管辖级别一致（与 confirm 同口径）。"""
    if warning is None or not is_r1a_governed(warning):
        return None
    r1a, r1a_r2 = _evaluate(engine, warning)
    if r1a is None:
        return None
    governing = governing_level(warning, r1a.level, r1a_r2.level)
    v = check_level_consistency(governing, warning["warn_level"], r1a, r1a_r2)
    return _to_violation(v) if v else None


__all__ = [
    "validate_adjust_level",
    "validate_confirm_level",
    "validate_disposal_level",
]
