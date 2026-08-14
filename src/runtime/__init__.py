"""本体运行时（B1/B2，技术方案 §3）——自研核心：索引/查询/动作执行/审计/冲突/双库。

模块：index（对象索引）/ query（对象查询）/ action_engine（动作管道）/ audit（审计）/
conflict（冲突消解）/ store（双库连接与 schema 管理）。
"""
from src.runtime.action_engine import ActionEngine, ActionResult, Effect, Writeback
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.conflict import DEFAULT_STRATEGY, STRATEGY_USER_EDIT_WINS, resolve
from src.runtime.index import ObjectIndex
from src.runtime.query import ObjectQuery
from src.runtime.store import Store

__all__ = [
    "ActionEngine", "ActionResult", "Effect", "Writeback",
    "AuditLog", "AuditRecord",
    "DEFAULT_STRATEGY", "STRATEGY_USER_EDIT_WINS", "resolve",
    "ObjectIndex", "ObjectQuery", "Store",
]
