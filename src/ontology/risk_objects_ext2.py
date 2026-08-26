"""S3 金控风控场景本体 —— 全量补全对象（M1b 全量 42 表 → M2 本体扩展）。

对象/字段来源：docs/S3-M1a-字段脱敏映射-全量42表.json（字段名 = renamed 新英文名，
description = field_comments 中文注释；value_desensitize 命中的字段在注释标注「（脱敏）」）。
PK/Title 遵循 M1a「<类型>_id = 主键ID」模式；SubsidiaryCreditDetail 例外：源表
o_a_erms_credit_detail_1 无独立主键列，业务主键即 project_id（全链路以 proj_id 引用）。
枚举字段用 Literal（值取自字典项 P0xx 注释；未枚举完整值集的字段保持 str）。
状态归属：全量补全对象均 source-backed（源系统权威，供动作写回/语义接口只读查询）。
链接关系见 risk_links.py 的 RISK_LINK_TYPES 扩展；本模块经 risk_objects.py 的
RISK_OBJECT_TYPES 统一注册（register_risk_objects 一并安装）。

对象命名与脊柱一致（RiskCustomer 前缀风格，新增对象直接语义名，如 CustomerRelation）。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from src.ontology.objects import (
    OWN_SOURCE,
    ObjectTypeDef,
    own,
)


class ConcentrationWarnAdj(BaseModel):
    """集中度预警调整表。PK/Title = concentration_warn_adj_id（源 o_a_erms_larg_cust_warn_adj）。"""

    concentration_warn_adj_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    concentration_limit_id: str = own(OWN_SOURCE, "集中度限额编号（FK→ConcentrationLimit.concentration_limit_id）")
    customer_no: str = own(OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    concentration_warn_line: str = own(OWN_SOURCE, "风险预警线（脱敏）")
    concentration_warn_line_old: str = own(OWN_SOURCE, "风险预警线-更新前的值（脱敏）")
    current_status: str = own(OWN_SOURCE, "集团预警维护-状态")
    approve_status: str = own(OWN_SOURCE, "审批状态")
    approve_comment: str = own(OWN_SOURCE, "审批意见（脱敏）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")

class WarningConcentration(BaseModel):
    """客户集中度预警信号表。PK/Title = concentration_signal_id（源 p_erms_cust_warn_sgn_concentration）。"""

    concentration_signal_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    top500_customer_id: str = own(OWN_SOURCE, "前500大客户风险结果表ID（FK→Top500CustomerRisk.top500_customer_id）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    org_id: str = own(OWN_SOURCE, "机构编码")
    customer_no: str = own(OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    group_customer_no: str = own(OWN_SOURCE, "集团客户编号（FK→GroupCustomer.group_customer_no）（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    group_member_count: int = own(OWN_SOURCE, "集团成员数")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    concentration_degree: float = own(OWN_SOURCE, "集中度监测（脱敏）")
    signal_name: str = own(OWN_SOURCE, "集中度预警信号名称")
    warn_reason: str = own(OWN_SOURCE, "预警事由（脱敏）")
    concentration_limit: float = own(OWN_SOURCE, "集中度限额（脱敏）")
    risk_warning_threshold: float = own(OWN_SOURCE, "风险预警线（脱敏）")
    warn_rule: str = own(OWN_SOURCE, "集中度风险预警等级 字典项P082 红色预警B1和B2、黄色预警A1和A2")
    signal_establish_date: date = own(OWN_SOURCE, "预警建立日期")
    signal_status: str = own(OWN_SOURCE, "信号数据状态 字典项P055")
    comp_lead_push_status: str = own(OWN_SOURCE, "金控领导预警推送状态 字典项P057")
    sub_company_push_status: str = own(OWN_SOURCE, "子公司推送状态 字典项P059")
    sub_company_push_time: datetime = own(OWN_SOURCE, "子公司推送时间")
    warn_level: Literal["RED", "YELLOW"] = own(OWN_SOURCE, "集中度预警等级 字典项P081 红色预警RED、黄色预警YELLOW")
    is_deleted: int = own(OWN_SOURCE, "0:未删除,1:删除")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_user: str = own(OWN_SOURCE, "更新人")

class WarningDerive(BaseModel):
    """客户衍生预警信号表。PK/Title = derive_warning_id（源 p_erms_cust_warn_sgn_derive）。"""

    derive_warning_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    customer_id: str = own(OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_id）（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    belong_group: str = own(OWN_SOURCE, "所属集团（脱敏）")
    warn_level: Literal["RED", "YELLOW", "BLUE"] = own(OWN_SOURCE, "预警等级")
    event_type: str = own(OWN_SOURCE, "信号类型")
    warn_source: str = own(OWN_SOURCE, "预警信息来源")
    warn_reason: str = own(OWN_SOURCE, "预警事由（脱敏）")
    signal_way: str = own(OWN_SOURCE, "信号产生方式")
    sys_proposal_signal_grade: str = own(OWN_SOURCE, "系统建议信号等级")
    signal_id: str = own(OWN_SOURCE, "信号编号")
    signal_name: str = own(OWN_SOURCE, "信号名称")
    signal_status: Literal["GENERATED", "CONFIRMED", "GRADED", "IN_DISPOSAL", "CLOSED"] = own(OWN_SOURCE, "信号状态")
    signal_level1_topic: str = own(OWN_SOURCE, "信号一级主题")
    signal_level2_topic: str = own(OWN_SOURCE, "信号二级主题")
    signal_description: str = own(OWN_SOURCE, "信号描述（脱敏）")
    signal_generate_date: date = own(OWN_SOURCE, "信号生成日期")
    signal_establish_date: date = own(OWN_SOURCE, "信号建立日期")
    signal_establish_operator: str = own(OWN_SOURCE, "信号建立人（脱敏）")
    signal_update_date: date = own(OWN_SOURCE, "信号更新日期")
    data_source: str = own(OWN_SOURCE, "数据来源")
    derive_signal_level1_topic: str = own(OWN_SOURCE, "衍生信号一级主题 字典项P052")
    derive_signal_level2_topic: str = own(OWN_SOURCE, "衍生信号二级主题 字典项P051")
    derive_warn_level: str = own(OWN_SOURCE, "衍生预警等级 字典项P054")
    derive_establish_date: date = own(OWN_SOURCE, "衍生预警信号建立日期")
    warn_model: str = own(OWN_SOURCE, "预警模型（脱敏）")
    ai_data: str = own(OWN_SOURCE, "AI智能体数据（脱敏）")
    derive_risk_type_determine: str = own(OWN_SOURCE, "风险类型判定 字典项P044")
    assess_extent_impact: str = own(OWN_SOURCE, "影响程度评估")
    deal_suggestion: str = own(OWN_SOURCE, "处置建议（脱敏）")
    derive_signal_status: str = own(OWN_SOURCE, "信号数据状态 字典项P055")
    comp_lead_push_status: str = own(OWN_SOURCE, "金控领导预警推送状态 字典项P057")
    warn_reason_update_status: str = own(OWN_SOURCE, "预警事由修改状态 字典项P058")
    warn_reason_updated: str = own(OWN_SOURCE, "修改后的预警事由（脱敏）")
    sub_company_push_status: str = own(OWN_SOURCE, "子公司推送状态 字典项P059")
    sub_company_push_time: datetime = own(OWN_SOURCE, "子公司推送时间")
    is_deleted: int = own(OWN_SOURCE, "0:未删除,1:删除")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    opinion_description: str = own(OWN_SOURCE, "审批意见（脱敏）")
    approve_order_status: Literal["PROCESS", "APPROVED", "REJECTED"] = own(OWN_SOURCE, "字典项P061 PROCESS-审批中 APPROVED-已通过 REJECTED-已驳回")
    approve_order_id: str = own(OWN_SOURCE, "审批单ID（FK→ApproveOrder.approve_order_id）")
    is_holding_add: int = own(OWN_SOURCE, "是否金控新增 0-否、1-是")

class WarningDeviation(BaseModel):
    """客户背离预警信号表。PK/Title = deviation_signal_id（源 p_erms_cust_warn_sgn_deviation）。"""

    deviation_signal_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    customer_no: str = own(OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    group_customer_no: str = own(OWN_SOURCE, "集团客户编号（FK→GroupCustomer.group_customer_no）（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    group_member_count: int = own(OWN_SOURCE, "集团成员数")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    signal_name: str = own(OWN_SOURCE, "背离预警信号名称")
    warn_reason: str = own(OWN_SOURCE, "预警事由（脱敏）")
    signal_establish_date: date = own(OWN_SOURCE, "预警信号建立日期")
    mom: float = own(OWN_SOURCE, "环比 Month-on-Month")
    mgr: float = own(OWN_SOURCE, "单月增幅 Monthly Growth Rate")
    ytd: float = own(OWN_SOURCE, "较年初 Growth Since the Beginning of the Year")
    warn_rule: str = own(OWN_SOURCE, "背离预警触发规则标识 字典项P080 环比A、单月增幅阈值B、较年初C")
    deviation_signal_status: str = own(OWN_SOURCE, "信号数据状态 字典项P055")
    comp_lead_push_status: str = own(OWN_SOURCE, "金控领导预警推送状态 字典项P057")
    sub_company_push_status: str = own(OWN_SOURCE, "子公司推送状态 字典项P059")
    sub_company_push_time: datetime = own(OWN_SOURCE, "子公司推送时间")
    is_deleted: int = own(OWN_SOURCE, "0:未删除,1:删除")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    opinion_description: str = own(OWN_SOURCE, "审批意见（脱敏）")
    approve_order_status: Literal["PROCESS", "APPROVED", "REJECTED"] = own(OWN_SOURCE, "字典项P061 PROCESS-审批中 APPROVED-已通过 REJECTED-已驳回")
    approve_order_id: str = own(OWN_SOURCE, "申请单ID（FK→ApproveOrder.approve_order_id）")

class DeviationScore(BaseModel):
    """趋势背离预警评分模型结果表。PK/Title = deviation_warn_score_id（源 p_erms_deviation_cust_warn_score）。"""

    deviation_warn_score_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型 01 单一客户，02集团客户")
    signal_name: str = own(OWN_SOURCE, "背离预警信号名称")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露额(亿元)（脱敏）")
    invest_balance: float = own(OWN_SOURCE, "投融资余额(亿元)（脱敏）")
    mom: float = own(OWN_SOURCE, "环比 Month-on-Month")
    ytd: float = own(OWN_SOURCE, "较年初 Growth Since the Beginning of the Year")
    mgr: float = own(OWN_SOURCE, "单月增幅 Monthly Growth Rate")
    warn_reason: str = own(OWN_SOURCE, "预警事由（脱敏）")
    customer_level: str = own(OWN_SOURCE, "客户等级")
    score: float = own(OWN_SOURCE, "风险评分")
    warn_level_code: str = own(OWN_SOURCE, "预警等级代码")
    warn_level: str = own(OWN_SOURCE, "预警等级")
    exposure_change: float = own(OWN_SOURCE, "敞口变化")
    signal_strength: float = own(OWN_SOURCE, "信号强度")
    disposal_priority: str = own(OWN_SOURCE, "处置优先级")
    involved_amount_level: str = own(OWN_SOURCE, "涉及金额等级")
    is_disposal_needed: int = own(OWN_SOURCE, "是否需处置")
    suggest_actions: str = own(OWN_SOURCE, "建议动作（脱敏）")
    variation: float = own(OWN_SOURCE, "金额×变化率")
    calc_detail: str = own(OWN_SOURCE, "计算过程（脱敏）")
    create_time: datetime = own(OWN_SOURCE, "创建时间")

class ApproveTodo(BaseModel):
    """用户待办任务表。PK/Title = approve_todo_id（源 p_erms_approve_todo）。"""

    approve_todo_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    approve_task_id: str = own(OWN_SOURCE, "关联审批任务ID（岗位级，FK→ApproveTask.approve_task_id）")
    user_id: str = own(OWN_SOURCE, "待办用户ID")
    approve_todo_status: Literal["UNHANDLED", "HANDLED", "INVALID"] = own(OWN_SOURCE, "待办状态 字典项P065：UNHANDLED-未处理 HANDLED-已处理 INVALID-已失效")
    is_deleted: int = own(OWN_SOURCE, "是否删除 0-未删 1-已删")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_time: datetime = own(OWN_SOURCE, "更新时间")

class ApproveOperLog(BaseModel):
    """审批操作日志表。PK/Title = approve_log_id（源 p_erms_approve_oper_log）。"""

    approve_log_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    approve_order_id: str = own(OWN_SOURCE, "审批单ID（FK→ApproveOrder.approve_order_id）")
    approve_task_id: str = own(OWN_SOURCE, "审批任务ID（FK→ApproveTask.approve_task_id）")
    operator_user_id: str = own(OWN_SOURCE, "操作人ID（脱敏）")
    operate_type: Literal["SUBMIT", "APPROVE", "REJECT"] = own(OWN_SOURCE, "操作类型：SUBMIT-提交 APPROVE-审批通过 REJECT-审批驳回")
    operate_remark: str = own(OWN_SOURCE, "操作备注（脱敏）")
    operate_time: datetime = own(OWN_SOURCE, "操作时间")
    ext: str = own(OWN_SOURCE, "扩展字段")


RISK_OBJECT_TYPES_EXT_2: list[ObjectTypeDef] = [
    ObjectTypeDef(
        name="ConcentrationWarnAdj",
        api_name="concentration_warn_adj",
        description="ConcentrationWarnAdj（集中度预警调整表，源 o_a_erms_larg_cust_warn_adj）",
        model=ConcentrationWarnAdj,
        pk_field="concentration_warn_adj_id",
        title_field="concentration_warn_adj_id",
        source_table="o_a_erms_larg_cust_warn_adj",
    ),
    ObjectTypeDef(
        name="WarningConcentration",
        api_name="warning_concentration",
        description="WarningConcentration（客户集中度预警信号表，源 p_erms_cust_warn_sgn_concentration）",
        model=WarningConcentration,
        pk_field="concentration_signal_id",
        title_field="concentration_signal_id",
        source_table="p_erms_cust_warn_sgn_concentration",
    ),
    ObjectTypeDef(
        name="WarningDerive",
        api_name="warning_derive",
        description="WarningDerive（客户衍生预警信号表，源 p_erms_cust_warn_sgn_derive）",
        model=WarningDerive,
        pk_field="derive_warning_id",
        title_field="derive_warning_id",
        source_table="p_erms_cust_warn_sgn_derive",
    ),
    ObjectTypeDef(
        name="WarningDeviation",
        api_name="warning_deviation",
        description="WarningDeviation（客户背离预警信号表，源 p_erms_cust_warn_sgn_deviation）",
        model=WarningDeviation,
        pk_field="deviation_signal_id",
        title_field="deviation_signal_id",
        source_table="p_erms_cust_warn_sgn_deviation",
    ),
    ObjectTypeDef(
        name="DeviationScore",
        api_name="deviation_score",
        description="DeviationScore（趋势背离预警评分模型结果表，源 p_erms_deviation_cust_warn_score）",
        model=DeviationScore,
        pk_field="deviation_warn_score_id",
        title_field="deviation_warn_score_id",
        source_table="p_erms_deviation_cust_warn_score",
    ),
    ObjectTypeDef(
        name="ApproveTodo",
        api_name="approve_todo",
        description="ApproveTodo（用户待办任务表，源 p_erms_approve_todo）",
        model=ApproveTodo,
        pk_field="approve_todo_id",
        title_field="approve_todo_id",
        source_table="p_erms_approve_todo",
    ),
    ObjectTypeDef(
        name="ApproveOperLog",
        api_name="approve_oper_log",
        description="ApproveOperLog（审批操作日志表，源 p_erms_approve_oper_log）",
        model=ApproveOperLog,
        pk_field="approve_log_id",
        title_field="approve_log_id",
        source_table="p_erms_approve_oper_log",
    ),
]
