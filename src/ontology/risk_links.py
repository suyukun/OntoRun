"""S3 金控风险预警场景本体 —— 链接类型定义（14 条，M2 设计 §1）。

对齐 S1 约定（src/ontology/links.py 头注释）：外键位置由基数决定，
N:1 → 外键在 source（多对一，多的那侧持 FK）；1:N → 外键在 target。
双向命名约定：inverse_name = "<target_api_name>.<惯用名>"（如
warning.for_customer 的反向 = customer.warning_signals）。

source_table 语义说明：本模块只声明拓扑，不校验 FK 值是否等于目标 PK
（数据一致性由物化/接线层保证）；self_check 只校验 FK 字段存在于承载侧模型。
"""

from src.ontology.links import LinkTypeDef

RISK_LINK_TYPES: list[LinkTypeDef] = [
    # ---- 客户域 ----
    LinkTypeDef(
        name="customer.belongs_to_group",
        source_type="Customer",
        target_type="GroupCustomer",
        cardinality="N:1",
        fk_field="group_customer_no",
        inverse_name="group_customer.customers",
        description="归属集团：一个单一客户属于一个集团客户（FK 在 Customer）",
    ),
    LinkTypeDef(
        name="collateral.for_customer",
        source_type="Collateral",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_id",
        inverse_name="customer.collateral",
        description="押品归属：押品记录对应一个客户",
    ),
    LinkTypeDef(
        name="concentration.for_customer",
        source_type="ConcentrationLimit",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_no",
        inverse_name="customer.concentration_limits",
        description="集中度限额：限额记录对应一个客户（FK 用源表业务键 customer_no）",
    ),
    LinkTypeDef(
        name="codebt.for_customer",
        source_type="CoDebtCustomer",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_id",
        inverse_name="customer.codebt_records",
        description="共债：共债记录对应一个客户",
    ),
    LinkTypeDef(
        name="metric.for_customer",
        source_type="Metric",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_no",
        inverse_name="customer.metrics",
        description="维度指标：指标行对应一个客户（FK 用源表业务键 customer_no）",
    ),
    # ---- 风险监测域 ----
    LinkTypeDef(
        name="warning.for_customer",
        source_type="WarningSignal",
        target_type="Customer",
        cardinality="N:1",
        fk_field="customer_id",
        inverse_name="customer.warning_signals",
        description="客户预警：客户级预警信号对应一个客户",
    ),
    LinkTypeDef(
        name="warning.for_group",
        source_type="WarningSignal",
        target_type="GroupCustomer",
        cardinality="N:1",
        fk_field="group_customer_no",
        inverse_name="group_customer.warning_signals",
        description="集团预警：集团级预警信号对应一个集团客户",
    ),
    # ---- 预警处置域 ----
    LinkTypeDef(
        name="disposal.for_warning",
        source_type="Disposal",
        target_type="WarningSignal",
        cardinality="N:1",
        fk_field="warning_id",
        inverse_name="warning_signal.disposals",
        description="处置归属：一个处置针对一个预警信号",
    ),
    LinkTypeDef(
        name="disposal.has_approval",
        source_type="Disposal",
        target_type="ApproveOrder",
        cardinality="1:N",
        fk_field="disposal_id",
        inverse_name="approve_order.disposal",
        description="审批：一个处置可发起多个审批单（FK 在 ApproveOrder）",
    ),
    LinkTypeDef(
        name="approve.has_tasks",
        source_type="ApproveOrder",
        target_type="ApproveTask",
        cardinality="1:N",
        fk_field="approve_order_id",
        inverse_name="approve_task.approve_order",
        description="任务拆分：一个审批单含多个审批任务节点（FK 在 ApproveTask）",
    ),
    # ---- 风险项目域 ----
    LinkTypeDef(
        name="risk_project.for_group",
        source_type="RiskProject",
        target_type="GroupCustomer",
        cardinality="N:1",
        fk_field="group_customer_no",
        inverse_name="group_customer.risk_projects",
        description="风险项目归属：一个风险项目对应一个集团客户",
    ),
    LinkTypeDef(
        name="risk_project.has_approval",
        source_type="RiskProject",
        target_type="ApproveOrder",
        cardinality="1:N",
        fk_field="risk_project_id",
        inverse_name="approve_order.risk_project",
        description="审批：一个风险项目可发起多个审批单（FK 在 ApproveOrder）",
    ),
    # ---- 机构/用户域 ----
    LinkTypeDef(
        name="org.has_users",
        source_type="Organization",
        target_type="User",
        cardinality="1:N",
        fk_field="org_id",
        inverse_name="user.organization",
        description="人员：一个机构下辖多个用户（FK 在 User）",
    ),
    LinkTypeDef(
        name="org.is_risk_monitor_of",
        source_type="Organization",
        target_type="Customer",
        cardinality="1:N",
        fk_field="org_id",
        inverse_name="customer.risk_monitor_org",
        description="风险管理：一个机构负责监测多个客户（FK 在 Customer.org_id）",
    ),
]
