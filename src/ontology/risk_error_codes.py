"""S3 金控风控场景错误码全集（与 S1 §4.3 CANONICAL_ERROR_CODES 并列）。

单一来源：本元组由 src/ontology/actions.py 在模块加载时并入 CANONICAL_ERROR_CODES
（仅追加、不改动既有码），使 Registry.self_check 的动作错误码门禁（ACTION_ERROR_CODE_UNKNOWN
/ ACTION_PRECONDITION_UNKNOWN）对 S3 风险动作同样生效。命名对齐 S1：<领域>_<条件> 全大写。
"""

RISK_ERROR_CODES: tuple[str, ...] = (
    # 预警信号
    "WARNING_NOT_FOUND",  # 预警信号不存在
    "WARNING_NOT_CONFIRMABLE",  # 信号状态非 GENERATED，不可确认
    "WARNING_NOT_ADJUSTABLE",  # 信号状态非 CONFIRMED，不可调整等级
    "WARNING_LEVEL_INVALID",  # 预警等级非法，或升级至更高等级需审批
    # 处置
    "DISPOSAL_NOT_FOUND",  # 处置记录不存在
    "DISPOSAL_NOT_SUBMITTABLE",  # 处置状态非 DRAFT，不可提交
    # 审批
    "APPROVE_ORDER_NOT_FOUND",  # 审批单不存在
    # 集中度限额
    "CONCENTRATION_LIMIT_NOT_FOUND",  # 集中度限额不存在
    # 风险项目
    "RISK_PROJECT_NOT_FOUND",  # 风险项目不存在
    "RISK_PROJECT_ALREADY_EXISTS",  # 风险项目重复登记
)
