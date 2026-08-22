"""结构化查询契约 v0.1/v0.2 校验 + 执行器（设计 §3）。

v0.1（对象路径，行为不变）：V1-V5 校验 fail-closed（设计 §3.3）——字段白名单查 Registry / 类型约束 /
≤1 跳 / 防注入参数化 / 结果护栏；过滤 + 聚合 + group_by + link_traversal（≤1 跳）参数化执行，契约值永不拼 SQL（V4）；
DQ-01「哪些物料一物多码？」：执行器对 old_code 非空结果集强制再过一物多码全谓词（§2.2），口径单点化；
reconcile_dq01：本体查询结果 vs 数据侧注入集 + manifest.multi_code_count 三方对账（§2.3）。

v0.2 扩展（设计 §3.1/§3.2，老 v0.1 契约原样可执行）：
- metric 键 → 指标物化路径：metric_id ∈ 指标注册表（M 系列）、dimension_filters 键 ∈ 维度白名单、
  time_range 绑定日期维度，查询命中 metrics.db 物化表（预聚合，不现场算），读前过 T3 版本守卫；
  ContractExecutor.execute 开头按 has_metric 分派：metric → _execute_metric（物化路径），
  否则走 v0.1 对象路径（行为完全不变）；
- count_distinct 聚合函数（v0.1 普通聚合同样支持）；
- time_range（{from, to} ISO 日期）——metric 块内绑定日期维度；非 metric 契约校验期
  fail-closed 拒答「不支持 time_range」（red-team P2-2：杜绝静默忽略）。
- 读侧权限（P1.5 decide(read) 接线，设计 §3.3）：permission_ctx 缺省 = 默认 deny
  （fail-closed，red-team P1-1：无 ctx ≠ 无校验），查询前 decide(subject, object_type, 'read')，
  属性级 visible_attributes 过滤返回列；契约显式请求的字段触及不可见列 fail-closed 拒答
  （不静默裁剪，防推断泄漏）；link_traversal 目标对象同样 decide(read)（red-team P1-2）。

模块划分（纯重构拆分，行为不变）：errors.py（错误类型）/ permissions.py（读侧权限上下文）/
schema.py（常量 + 类型解析辅助 + 校验函数）/ executor.py（执行辅助 + ContractExecutor）/
reconcile.py（ReconcileResult + DQ-01 对账/跑通）。
"""

from src.des.contract.errors import (
    PERMISSION_DENIED,
    ContractError,
    PermissionDeniedError,
)
from src.des.contract.executor import ContractExecutor
from src.des.contract.permissions import (
    SYSTEM_SUBJECT,
    PermissionContext,
    PermissionDecider,
)
from src.des.contract.reconcile import ReconcileResult, reconcile_dq01, run_dq01
from src.des.contract.schema import (
    AGG_FUNCS,
    CONTRACT_KEYS,
    DQ01_CONTRACT,
    FILTER_EXPR_KEYS,
    MAX_AGGREGATIONS,
    MAX_GROUP_BY,
    MAX_TOP_N,
    METRIC_KEYS,
    OPS,
    RESULT_LIMIT_FLOOR,
    RESULT_LIMIT_SCALE_FACTOR,
    TIME_RANGE_KEYS,
    validate_contract,
)

__all__ = [
    "AGG_FUNCS",
    "CONTRACT_KEYS",
    "DQ01_CONTRACT",
    "FILTER_EXPR_KEYS",
    "MAX_AGGREGATIONS",
    "MAX_GROUP_BY",
    "MAX_TOP_N",
    "METRIC_KEYS",
    "OPS",
    "PERMISSION_DENIED",
    "RESULT_LIMIT_FLOOR",
    "RESULT_LIMIT_SCALE_FACTOR",
    "SYSTEM_SUBJECT",
    "TIME_RANGE_KEYS",
    "ContractError",
    "ContractExecutor",
    "PermissionContext",
    "PermissionDecider",
    "PermissionDeniedError",
    "ReconcileResult",
    "reconcile_dq01",
    "run_dq01",
    "validate_contract",
]
