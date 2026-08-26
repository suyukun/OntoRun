"""S3 金控风险预警场景本体 —— 核心脊柱对象（M2 设计 v1，12 个核心 + 1 个支撑对象）。

全量补全（M1b）：risk_objects_ext.py + risk_objects_ext2.py 再注册 20 个全量对象
（客户关系/资产/押品/集中度调整/预警派生/共债评分/审批待办等，源自 42 表脱敏映射），
RISK_OBJECT_TYPES 合计 33 个（脊柱 13 + 扩展 20）；本模块仅做拼接与统一注册。

对象/字段来源：docs/S3-M1a-字段脱敏映射-脊柱12表.json（字段名 = renamed 新英文名，
description = field_comments 中文注释；value_desensitize 命中的字段在注释标注「（脱敏）」）。
M1a 未覆盖的三张脊柱表（ap_collateral / ap_codebt_customer / ap_org）与支撑表（ap_user）
按 M2 设计文档字段清单 + 业务语义补全，注释标注「（M1a 未覆盖，按 M2 设计补全）」。
PK 命名遵循 M1a「<类型>_id = 主键ID」模式；GroupCustomer 例外：源表 o_a_erms_grp_cust_info
无独立主键列，业务主键即 group_customer_no（全链路 FK 均以 group_customer_no 引用，
故 M2 草案的 group_customer_id 落地为 group_customer_no，见下）。

注册形态：本模块是自洽的独立注册体——新建 Registry() 后调用 register_risk_objects(reg) 即可。
【M3 挂载适配（已落地）】类型名/模型类统一用 RiskCustomer（对齐 DES ErpCustomer 先例，
避免与 S1 零售 Customer 同名冲突）；链接 inverse_name 前缀随之用 risk_customer.
（self_check 按目标 api_name 校验前缀）；ActionEngine 的 9 个风险动作写回 handler 已由
src/runtime/risk_actions_impl.register_risk_action_handlers 注入（M3 写引擎）。

状态归属沿用 S1 模式（src/ontology/objects.py）：own(OWN_SOURCE/OWN_ONTOLOGY/OWN_DERIVED)。
- source-backed：源系统权威，动作写回；
- ontology-owned：本体自有状态（源系统无此列，如 WarningSignal.warn_adjust_reason）；
- derived：计算态，永不写（如 GroupCustomer.member_count）。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from src.ontology.objects import (
    OWN_DERIVED,
    OWN_ONTOLOGY,
    OWN_SOURCE,
    ObjectTypeDef,
    own,
)
from src.ontology.risk_actions import RISK_ACTIONS
from src.ontology.risk_links import RISK_LINK_TYPES

# ---- 脊柱共享枚举（M2 设计 §1） ----
WarnLevel = Literal["RED", "YELLOW", "BLUE"]  # 预警等级
SignalStatus = Literal[  # 信号状态机：生成→确认→定级→处置中→关闭
    "GENERATED", "CONFIRMED", "GRADED", "IN_DISPOSAL", "CLOSED"
]
DisposalStatus = Literal[  # 处置状态机：草稿→提交→审批中→通过/驳回→执行→完成
    "DRAFT", "SUBMITTED", "APPROVING", "APPROVED", "REJECTED", "EXECUTING", "DONE"
]
ApproveOrderStatus = Literal["PROCESS", "APPROVED", "REJECTED"]  # 审批单状态（字典 P061）
FiveClassification = Literal[  # 五级分类
    "NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"
]


class RiskCustomer(BaseModel):
    """单一客户（金控风险预警）。PK/Title = customer_id（源 o_a_erms_cust_info）。

    与 S1 零售 Customer 区分：金控风控单一客户独立对象（对齐 DES ErpCustomer 先例），
    避免与 S1 零售客户同名冲突，风险独立注册表内注册名 = RiskCustomer。
    """

    customer_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    customer_no: str = own(OWN_SOURCE, "单一客户编号（脱敏）")
    customer_name: str = own(OWN_SOURCE, "单一客户名称（脱敏）")
    group_customer_no: str | None = own(
        OWN_SOURCE,
        "所属集团编号（FK→GroupCustomer.group_customer_no）（脱敏）",
        default=None,
    )
    org_id: str = own(OWN_SOURCE, "机构编码（FK→Organization.org_id）")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    cert_type: str = own(OWN_SOURCE, "单一客户证件类型")
    cert_no: str = own(OWN_SOURCE, "单一客户证件号（脱敏）")
    internal_level: str = own(OWN_SOURCE, "客户内部评级")
    external_level: str = own(OWN_SOURCE, "客户外部评级")
    industry_name: str = own(OWN_SOURCE, "行业名称")
    asset_quality_level: str = own(OWN_SOURCE, "资产质量")
    establish_time: date = own(OWN_SOURCE, "成立时间")
    registered_capital: float = own(OWN_SOURCE, "注册资本（脱敏）")
    chairman_name: str = own(OWN_SOURCE, "董事长（脱敏）")
    legal_rep: str = own(
        OWN_SOURCE, "法定代表人（脱敏）（M1a 未覆盖，按 M2 设计补全）"
    )
    address: str = own(OWN_SOURCE, "注册地址（脱敏）（M1a 未覆盖，按 M2 设计补全）")
    customer_status: str = own(OWN_SOURCE, "客户状态")


class GroupCustomer(BaseModel):
    """集团客户。PK/Title = group_customer_no（源 o_a_erms_grp_cust_info）。

    M2 草案 PK 名 group_customer_id 落地为 group_customer_no：源表无独立主键列，
    GRP_CUST_NO 即业务主键，且 ap_customer.group_customer_no 全链路以其为 FK。
    """

    group_customer_no: str = own(OWN_SOURCE, "集团编号（PK/Title，业务主键）（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "集团名称（脱敏）")
    group_customer_type: str = own(OWN_SOURCE, "所属集团类型（源 ap_warning_signal.GRP_CUST_TYPE）")
    group_peer_flag: str = own(OWN_SOURCE, "集团同业标识")
    customer_status: str = own(OWN_SOURCE, "客户状态")
    asset_quality_level: str = own(OWN_SOURCE, "资产质量分类名称")
    member_count: int = own(
        OWN_DERIVED, "成员客户数 = COUNT(集团下 Customer)（计算态，永不写）"
    )
    total_exposure: float = own(
        OWN_DERIVED, "集团总敞口 = Σ 成员客户风险敞口（计算态，永不写）（脱敏）"
    )
    risk_level: str = own(
        OWN_ONTOLOGY, "集团风险等级（本体自有，由预警/评级合成，源系统无此列）"
    )


class WarningSignal(BaseModel):
    """预警信号。PK/Title = warning_id（源 o_a_erms_cust_warn_sgn）。"""

    warning_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    customer_id: str | None = own(
        OWN_SOURCE,
        "客户编号（外键→ap_customer.customer_id，客户级预警非空）（脱敏）",
        default=None,
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    group_customer_no: str | None = own(
        OWN_SOURCE,
        "所属集团编码（FK→GroupCustomer.group_customer_no，集团级预警非空）（脱敏）",
        default=None,
    )
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    warn_level: WarnLevel = own(OWN_SOURCE, "预警等级（RED/YELLOW/BLUE）")
    event_type: str = own(OWN_SOURCE, "信号类型")
    warn_source: str = own(OWN_SOURCE, "预警信息来源")
    warn_reason: str = own(OWN_SOURCE, "预警事由（脱敏）")
    signal_id: str = own(OWN_SOURCE, "信号编号")
    signal_name: str = own(OWN_SOURCE, "信号名称")
    signal_status: SignalStatus = own(
        OWN_SOURCE, "信号状态（GENERATED/CONFIRMED/GRADED/IN_DISPOSAL/CLOSED）"
    )
    signal_level1_topic: str = own(OWN_SOURCE, "信号一级主题")
    signal_level2_topic: str = own(OWN_SOURCE, "信号二级主题")
    signal_description: str = own(OWN_SOURCE, "信号描述（脱敏）")
    signal_generate_date: date = own(OWN_SOURCE, "信号生成日期")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露额（脱敏）")
    invest_balance: float = own(OWN_SOURCE, "集团的投融资余额（脱敏）")
    warn_adjust_reason: str | None = own(
        OWN_ONTOLOGY,
        "预警等级调整原因（本体自有，adjust_warning_level 写入，源系统无此列）",
        default=None,
    )
    push_at: datetime | None = own(
        OWN_ONTOLOGY,
        "推送时间（本体自有，push_warning 写入，源系统无此列）",
        default=None,
    )


class Metric(BaseModel):
    """维度指标（comb_dim_index 全部维度指标物化预聚合）。PK/Title = dim_metric_id。"""

    dim_metric_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    org_id: str = own(OWN_SOURCE, "机构编码")
    dim_type_code: str = own(OWN_SOURCE, "维度类型代码")
    dim_type_name: str = own(OWN_SOURCE, "维度类型名称")
    customer_no: str = own(OWN_SOURCE, "单一客户编号（FK→RiskCustomer.customer_no）（脱敏）")
    customer_name: str = own(OWN_SOURCE, "单一客户名称（脱敏）")
    group_customer_no: str | None = own(
        OWN_SOURCE, "所属集团编号（脱敏）", default=None
    )
    business_type_code: str = own(OWN_SOURCE, "业务类型代码")
    business_product_code: str = own(OWN_SOURCE, "业务品种代码")
    index_id: str = own(OWN_SOURCE, "指标编号")
    index_name: str = own(OWN_SOURCE, "指标名称")
    index_value: float = own(OWN_SOURCE, "指标数值")
    index_unit: str = own(OWN_SOURCE, "单位")
    currency_name: str = own(OWN_SOURCE, "币种名称")


class Disposal(BaseModel):
    """预警处置。PK/Title = disposal_id（源 p_erms_sgn_deal）。"""

    disposal_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    warning_id: str = own(
        OWN_SOURCE, "关联预警 ID（FK→WarningSignal.warning_id，源 p_erms_sgn_deal 无此列，"
        "关联承载于 o_a_erms_cust_warn_sgn_disp.WARN_ID）"
    )
    business_type: str = own(OWN_SOURCE, "业务类型（字典项P060：SGN_DERIVE/SGN_DEVIATION/SGN_CONCENTRAT）")
    deal_type: str = own(OWN_SOURCE, "处置类型（字典项P066）")
    disposal_status: DisposalStatus = own(
        OWN_SOURCE,
        "处置状态（DRAFT/SUBMITTED/APPROVING/APPROVED/REJECTED/EXECUTING/DONE）",
    )
    comment: str = own(OWN_SOURCE, "处置事由（脱敏）")
    deal_user_id: str = own(OWN_SOURCE, "处置人ID（脱敏）")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_time: datetime = own(OWN_SOURCE, "更新时间（源字段拼写 UPDATE_IME）")


class Collateral(BaseModel):
    """押品。PK/Title = collateral_id（源 ap_collateral，M1a 未覆盖，按 M2 设计补全）。"""

    collateral_id: str = own(OWN_SOURCE, "押品记录号（PK/Title）")
    customer_id: str = own(OWN_SOURCE, "所属客户（FK→RiskCustomer.customer_id）（脱敏）")
    collateral_type: str = own(OWN_SOURCE, "押品类型（如 银行存单/证券/房产/其他）")
    estimated_value: float = own(OWN_SOURCE, "评估价值（万元）（脱敏）")
    appraisal_date: date = own(OWN_SOURCE, "评估日期")
    valuation_status: str = own(OWN_SOURCE, "估值状态（有效/过期/重估中）")
    bank_detail: str = own(OWN_SOURCE, "银行押品明细（脱敏）")
    securities_detail: str = own(OWN_SOURCE, "证券押品明细（脱敏）")


class ApproveOrder(BaseModel):
    """审批单。PK/Title = approve_order_id（源 p_erms_approve_order）。"""

    approve_order_id: str = own(OWN_SOURCE, "审批单ID（PK/Title）")
    approve_order_type: str = own(OWN_SOURCE, "审批类型（字典项P062：WARN_SGN 预警审批）")
    approve_order_title: str = own(OWN_SOURCE, "审批单标题（字典项P060）")
    apply_user_id: str = own(OWN_SOURCE, "申请人ID（脱敏）")
    approved_user_id: str = own(OWN_SOURCE, "审批人ID（脱敏）")
    apply_time: datetime = own(OWN_SOURCE, "申请时间")
    approve_time: datetime | None = own(OWN_SOURCE, "审核时间", default=None)
    approve_order_status: ApproveOrderStatus = own(
        OWN_SOURCE, "审批单状态（字典项P061：PROCESS/APPROVED/REJECTED）"
    )
    business_type: str = own(OWN_SOURCE, "业务类型（字典项P060）")
    remark: str = own(OWN_SOURCE, "申请备注（脱敏）")
    opinion_description: str = own(OWN_SOURCE, "审批意见（脱敏）")
    disposal_id: str | None = own(
        OWN_SOURCE,
        "关联处置单（FK→Disposal.disposal_id，处置审批单非空）",
        default=None,
    )
    risk_project_id: str | None = own(
        OWN_SOURCE,
        "关联风险项目（FK→RiskProject.risk_project_id，风险项目审批单非空）",
        default=None,
    )


class ApproveTask(BaseModel):
    """审批任务。PK/Title = approve_task_id（源 p_erms_approve_task）。"""

    approve_task_id: str = own(OWN_SOURCE, "任务ID（PK/Title）")
    approve_order_id: str = own(
        OWN_SOURCE, "关联审批单ID（FK→ApproveOrder.approve_order_id）"
    )
    approve_node_id: str = own(
        OWN_SOURCE, "审批节点ID（外键→ap_approve_node.approve_node_id）"
    )
    node_name: str = own(
        OWN_SOURCE, "节点名称（M1a 未覆盖，按 M2 设计补全，节点表承载）"
    )
    node_seq: int = own(
        OWN_SOURCE, "节点序号（M1a 未覆盖，按 M2 设计补全）"
    )
    post_id: str = own(OWN_SOURCE, "岗位ID")
    approve_task_status: Literal["PENDING", "COMPLETED"] = own(
        OWN_SOURCE, "任务状态（字典项P063：PENDING待处理/COMPLETED已处理）"
    )
    approve_result: Literal["APPROVED", "REJECTED"] = own(
        OWN_SOURCE, "审批结果（字典项P064：APPROVED通过/REJECTED驳回）"
    )
    approve_remark: str = own(OWN_SOURCE, "审核意见（脱敏）")
    approve_time: datetime | None = own(OWN_SOURCE, "审批时间", default=None)
    assignee: str = own(
        OWN_SOURCE, "处理人（M1a 未覆盖，按 M2 设计补全）（脱敏）"
    )


class ConcentrationLimit(BaseModel):
    """集中度限额。PK/Title = concentration_limit_id（源 o_a_erms_larg_cust_limit）。"""

    concentration_limit_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    warning_value: float = own(OWN_SOURCE, "预警阈值（脱敏）")
    concentration_limit: float = own(OWN_SOURCE, "集中度限额（脱敏）")
    concentration_limit_old: float = own(
        OWN_SOURCE, "集中度限额-更新前的值（脱敏）"
    )
    current_status: str = own(OWN_SOURCE, "当前状态")
    approve_status: str | None = own(
        OWN_ONTOLOGY,
        "限额调整审批状态（本体自有，源系统无此列）",
        default=None,
    )
    approve_comment: str | None = own(
        OWN_ONTOLOGY,
        "限额调整审批意见（本体自有，源系统无此列）",
        default=None,
    )


class CoDebtCustomer(BaseModel):
    """共债客户。PK/Title = codebt_id（源 ap_codebt_customer，M1a 未覆盖，按 M2 设计补全）。"""

    codebt_id: str = own(OWN_SOURCE, "共债记录号（PK/Title）")
    customer_id: str = own(OWN_SOURCE, "客户（FK→RiskCustomer.customer_id）（脱敏）")
    codebt_count: int = own(OWN_SOURCE, "共债客户数")
    total_debt: float = own(OWN_SOURCE, "共债总额（万元）（脱敏）")
    risk_score: float = own(OWN_SOURCE, "共债风险评分")
    data_date: date = own(OWN_SOURCE, "数据日期")


class RiskProject(BaseModel):
    """风险项目。PK/Title = risk_project_id（源 p_erms_risk_project_info）。"""

    risk_project_id: str = own(OWN_SOURCE, "主键id（PK/Title，自增）")
    group_customer_no: str | None = own(
        OWN_SOURCE,
        "所属集团编号（FK→GroupCustomer.group_customer_no；M1a 仅有集团名称，"
        "补编号字段用于 for_group 关联）",
        default=None,
    )
    group_customer_name: str = own(OWN_SOURCE, "集团名称（脱敏）")
    division: str = own(OWN_SOURCE, "分工（部门）")
    project_name: str = own(OWN_SOURCE, "项目名称（脱敏）")
    business_type: str = own(OWN_SOURCE, "业务类型")
    credit_subject: str = own(OWN_SOURCE, "授信/融资主体（脱敏）")
    business_balance: float = own(OWN_SOURCE, "业务余额（单位：亿元）（脱敏）")
    risk_exposure_balance: float = own(OWN_SOURCE, "风险暴露余额（单位：亿元）（脱敏）")
    impairment_provision: float = own(OWN_SOURCE, "已计提减值（单位：亿元）（脱敏）")
    five_classification: FiveClassification = own(
        OWN_SOURCE, "五级分类（NORMAL/ATTENTION/SECONDARY/DOUBTFUL/LOSS）"
    )
    guarantee_method: str = own(OWN_SOURCE, "担保方式")
    project_progress: str = own(OWN_SOURCE, "项目情况及进展（脱敏）")
    create_time: datetime = own(OWN_SOURCE, "创建时间")


class Organization(BaseModel):
    """机构（集团/银行/证券/保险/信托/租赁/基金）。PK/Title = org_id（源 ap_org，M1a 未覆盖）。"""

    org_id: str = own(OWN_SOURCE, "机构编码（PK/Title）")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    org_type: Literal[
        "GROUP", "BANK", "SECURITIES", "INSURANCE", "TRUST", "LEASE", "FUND"
    ] = own(OWN_SOURCE, "机构类型：集团/银行/证券/保险/信托/租赁/基金")
    parent_id: str | None = own(
        OWN_SOURCE, "上级机构（FK→Organization.org_id，金控总部为空）", default=None
    )
    risk_role: str = own(
        OWN_SOURCE, "风险管理职能角色（如 牵头机构/配合机构/数据报送）"
    )


class User(BaseModel):
    """用户/岗位（支撑对象，M2 设计 §2 第 13 项；随脊柱注册使 org.has_users 链接可解析）。"""

    user_id: str = own(OWN_SOURCE, "用户号（PK/Title，源 ap_user）")
    user_name: str = own(OWN_SOURCE, "用户姓名（脱敏）")
    org_id: str = own(OWN_SOURCE, "所属机构（FK→Organization.org_id）")
    post_id: str = own(OWN_SOURCE, "岗位ID")
    role: str = own(OWN_SOURCE, "角色（如 风险处置员/审批人/管理员）")


RISK_OBJECT_TYPES: list[ObjectTypeDef] = [
    ObjectTypeDef(
        name="RiskCustomer",
        api_name="risk_customer",
        description="单一客户（金控风险预警，源 o_a_erms_cust_info；M3 挂载改名为 RiskCustomer）",
        model=RiskCustomer,
        pk_field="customer_id",
        title_field="customer_id",
        source_table="o_a_erms_cust_info",
    ),
    ObjectTypeDef(
        name="GroupCustomer",
        api_name="group_customer",
        description="集团客户（金控风险预警，源 o_a_erms_grp_cust_info）",
        model=GroupCustomer,
        pk_field="group_customer_no",
        title_field="group_customer_no",
        source_table="o_a_erms_grp_cust_info",
    ),
    ObjectTypeDef(
        name="WarningSignal",
        api_name="warning_signal",
        description="预警信号（金控风险预警，源 o_a_erms_cust_warn_sgn）",
        model=WarningSignal,
        pk_field="warning_id",
        title_field="warning_id",
        source_table="o_a_erms_cust_warn_sgn",
    ),
    ObjectTypeDef(
        name="Metric",
        api_name="metric",
        description="维度指标（comb_dim_index 物化预聚合，源 o_a_erms_comb_dim_index）",
        model=Metric,
        pk_field="dim_metric_id",
        title_field="dim_metric_id",
        source_table="o_a_erms_comb_dim_index",
    ),
    ObjectTypeDef(
        name="Disposal",
        api_name="disposal",
        description="预警处置（金控风险预警，源 p_erms_sgn_deal）",
        model=Disposal,
        pk_field="disposal_id",
        title_field="disposal_id",
        source_table="p_erms_sgn_deal",
    ),
    ObjectTypeDef(
        name="Collateral",
        api_name="collateral",
        description="押品（金控风险预警，源 ap_collateral）",
        model=Collateral,
        pk_field="collateral_id",
        title_field="collateral_id",
        source_table="ap_collateral",
    ),
    ObjectTypeDef(
        name="ApproveOrder",
        api_name="approve_order",
        description="审批单（金控风险预警，源 p_erms_approve_order）",
        model=ApproveOrder,
        pk_field="approve_order_id",
        title_field="approve_order_id",
        source_table="p_erms_approve_order",
    ),
    ObjectTypeDef(
        name="ApproveTask",
        api_name="approve_task",
        description="审批任务（金控风险预警，源 p_erms_approve_task）",
        model=ApproveTask,
        pk_field="approve_task_id",
        title_field="approve_task_id",
        source_table="p_erms_approve_task",
    ),
    ObjectTypeDef(
        name="ConcentrationLimit",
        api_name="concentration_limit",
        description="集中度限额（金控风险预警，源 o_a_erms_larg_cust_limit）",
        model=ConcentrationLimit,
        pk_field="concentration_limit_id",
        title_field="concentration_limit_id",
        source_table="o_a_erms_larg_cust_limit",
    ),
    ObjectTypeDef(
        name="CoDebtCustomer",
        api_name="codebt_customer",
        description="共债客户（金控风险预警，源 ap_codebt_customer）",
        model=CoDebtCustomer,
        pk_field="codebt_id",
        title_field="codebt_id",
        source_table="ap_codebt_customer",
    ),
    ObjectTypeDef(
        name="RiskProject",
        api_name="risk_project",
        description="风险项目（金控风险预警，源 p_erms_risk_project_info）",
        model=RiskProject,
        pk_field="risk_project_id",
        title_field="risk_project_id",
        source_table="p_erms_risk_project_info",
    ),
    ObjectTypeDef(
        name="Organization",
        api_name="organization",
        description="机构（集团/银行/证券/保险/信托/租赁/基金，源 ap_org）",
        model=Organization,
        pk_field="org_id",
        title_field="org_id",
        source_table="ap_org",
    ),
    ObjectTypeDef(
        name="User",
        api_name="user",
        description="用户/岗位（支撑对象，源 ap_user，使 org.has_users 链接可解析）",
        model=User,
        pk_field="user_id",
        title_field="user_id",
        source_table="ap_user",
    ),
]


# ---- 全量补全拼接（M1b 42 表 → M2，脊柱 13 + 扩展 20 = 33） ----
from src.ontology.risk_objects_ext import RISK_OBJECT_TYPES_EXT_1
from src.ontology.risk_objects_ext2 import RISK_OBJECT_TYPES_EXT_2

RISK_OBJECT_TYPES: list[ObjectTypeDef] = [
    *RISK_OBJECT_TYPES,
    *RISK_OBJECT_TYPES_EXT_1,
    *RISK_OBJECT_TYPES_EXT_2,
]


def register_risk_objects(registry) -> None:
    """安装 S3 金控风控本体（脊柱 13 + 全量扩展 20 = 33 对象 + 35 链接 + 9 动作）到 Registry。

    用法：新建独立注册表（reg = Registry(); register_risk_objects(reg)）供 S3 演示用，
    self_check 全绿。挂载点 = src/ontology/__init__.py 的 build_registry()（src/app/main.py
    与 src/api/main.py 统一入口）；因 ActionEngine 要求每个动作有运行时 handler（M3 写回），
    暂不并入共享注册表，M3 接线时按模块 docstring 的三条适配做。重复注册会报错（防静默覆盖）。
    """
    for obj in RISK_OBJECT_TYPES:
        registry.register_object_type(obj)
    for link in RISK_LINK_TYPES:
        registry.register_link_type(link)
    for action in RISK_ACTIONS:
        registry.register_action_type(action)