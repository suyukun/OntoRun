"""S3 M3b 风险读引擎 —— 受限契约规格（白名单/字段映射/护栏，与执行器解耦）。

本模块 = 读引擎的「可表达集」单一真相：LLM 只能引用这里声明的 对象/字段/操作符/
聚合/analytic。执行器（src.runtime.risk_query.RiskQuery）只消费本规格，不做任何
自由 SQL 拼接面。改动本规格即改变可表达集（域外范围），须随评审。

- RISK_QUERY_FIELDS：可查询对象 → 可查询字段（本体字段名 → 源列名），仅含源表真实列；
- RISK_QUERY_DERIVED：派生字段（scalar 子查询，{t} = 主表别名）；
- NOT_QUERYABLE_OBJECTS：已注册但无源表/未物化的对象（命中即 fail-closed 拒答）；
- ANALYTIC_*：受限多跳查询白名单（固定参数化 SQL + 参数模型，无自由 SQL）。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.runtime.risk_db import (
    DISPOSAL_STATUS_FROM_CN,
    DISPOSAL_STATUS_TO_CN,
    SIGNAL_STATUS_FROM_CN,
    SIGNAL_STATUS_TO_CN,
)

# ---- 执行护栏 ----
MAX_ITEMS = 200
MAX_GROUPS = 200
MAX_ANALYTIC_ROWS = 10
MAX_FILTERS = 12
MAX_LIMIT = 200  # 列表型答案上限（R11 集中度超限名单等），护栏仍在 MAX_ITEMS 内

# ---- 操作符 / 聚合函数白名单（LLM 只能从中取值） ----
FILTER_OPS: tuple[str, ...] = (
    "eq",
    "ne",
    "gt",
    "ge",
    "lt",
    "le",
    "contains",
    "in",
    "is_null",
    "is_not_null",
)
AGG_FUNCTIONS: tuple[str, ...] = ("count", "sum", "avg", "min", "max", "count_distinct")

# 状态字段值适配（本体规范态 ↔ 源系统中文值；LLM 填英文或中文均归一化到中文落查询）
STATUS_TO_CN: dict[str, dict[str, str]] = {
    "signal_status": SIGNAL_STATUS_TO_CN,
    "disposal_status": DISPOSAL_STATUS_TO_CN,
}
STATUS_FROM_CN: dict[str, dict[str, str]] = {
    "signal_status": SIGNAL_STATUS_FROM_CN,
    "disposal_status": DISPOSAL_STATUS_FROM_CN,
}

# ---- 可查询对象 → 可查询字段（本体字段名 → 源列名） ----
RISK_QUERY_FIELDS: dict[str, dict[str, str]] = {
    "risk_customer": {
        "customer_id": "customer_id",
        "customer_no": "customer_no",
        "customer_name": "customer_name",
        "group_customer_no": "group_customer_no",
        "org_id": "org_id",
        "org_name": "org_name",
        "cert_type": "cert_type",
        "cert_no": "cert_no",
        "internal_level": "internal_level",
        "external_level": "external_level",
        "industry_name": "industry_name",
        "asset_quality_level": "asset_quality_level",
        "establish_time": "establish_time",
        "registered_capital": "registered_capital",
        "chairman_name": "chairman_name",
        "customer_status": "customer_status",
    },
    "group_customer": {
        "group_customer_no": "group_customer_no",
        "group_customer_name": "group_customer_name",
        "group_peer_flag": "group_peer_flag",
        "customer_status": "customer_status",
        "asset_quality_level": "asset_quality_level",
    },
    "warning_signal": {
        "warning_id": "warning_id",
        "customer_id": "customer_id",
        "customer_name": "customer_name",
        "group_customer_no": "group_customer_no",
        "org_id": "org_id",
        "org_name": "org_name",
        "warn_level": "warn_level",
        "event_type": "event_type",
        "warn_source": "warn_source",
        "warn_reason": "warn_reason",
        "signal_id": "signal_id",
        "signal_name": "signal_name",
        "signal_status": "signal_status",
        "signal_level1_topic": "signal_level1_topic",
        "signal_level2_topic": "signal_level2_topic",
        "signal_description": "signal_description",
        "signal_generate_date": "signal_generate_date",
        "risk_exposure": "risk_exposure",
        "invest_balance": "invest_balance",
    },
    "metric": {
        "dim_metric_id": "dim_metric_id",
        "data_date": "data_date",
        "org_id": "org_id",
        "dim_type_code": "dim_type_code",
        "dim_type_name": "dim_type_name",
        "customer_no": "customer_no",
        "customer_name": "customer_name",
        "group_customer_no": "group_customer_no",
        "business_type_code": "business_type_code",
        "business_product_code": "business_product_code",
        "index_id": "index_id",
        "index_name": "index_name",
        "index_value": "index_value",
        "index_unit": "index_unit",
        "currency_name": "currency_name",
    },
    "disposal": {
        "disposal_id": "disposal_id",
        "warning_id": "warning_id",
        "disposal_status": "disposal_status",
    },
    "approve_order": {
        "approve_order_id": "approve_order_id",
        "approve_order_type": "approve_order_type",
        "approve_order_title": "approve_order_title",
        "apply_user_id": "apply_user_id",
        "approved_user_id": "approved_user_id",
        "apply_time": "apply_time",
        "approve_time": "approve_time",
        "approve_order_status": "approve_order_status",
        "business_type": "business_type",
        "remark": "remark",
        "opinion_description": "opinion_description",
    },
    "approve_task": {
        "approve_task_id": "approve_task_id",
        "approve_order_id": "approve_order_id",
        "approve_node_id": "approve_node_id",
        "post_id": "post_id",
        "approve_task_status": "approve_task_status",
        "approve_result": "approve_result",
        "approve_remark": "approve_remark",
        "approve_time": "approve_time",
    },
    "concentration_limit": {
        "concentration_limit_id": "concentration_limit_id",
        "customer_no": "customer_no",
        "customer_name": "customer_name",
        "warning_value": "warning_value",
        "concentration_limit": "concentration_limit",
        "concentration_limit_old": "concentration_limit_old",
        "current_status": "current_status",
    },
    "risk_project": {
        "risk_project_id": "risk_project_id",
        "group_customer_name": "group_customer_name",
        "division": "division",
        "project_name": "project_name",
        "business_type": "business_type",
        "credit_subject": "credit_subject",
        "business_balance": "business_balance",
        "risk_exposure_balance": "risk_exposure_balance",
        "impairment_provision": "impairment_provision",
        "five_classification": "five_classification",
        "guarantee_method": "guarantee_method",
        "project_progress": "project_progress",
        "create_time": "create_time",
        "org_name_1": "org_name_1",
    },
}

# 派生字段（scalar 子查询，{t} = 主表别名；仅白名单内可算派生可查/可返回）
RISK_QUERY_DERIVED: dict[str, dict[str, str]] = {
    "group_customer": {
        "member_count": (
            "(SELECT COUNT(*) FROM customer.ap_customer c "
            "WHERE c.group_customer_no = {t}.group_customer_no)"
        ),
    },
    "approve_task": {
        "approve_node_name": (
            "(SELECT n.approve_node_name FROM approval.ap_approve_node n "
            "WHERE n.approve_node_id = {t}.approve_node_id)"
        ),
    },
}

# 不可查询对象（无源表/未物化）：命中即 fail-closed 拒答
NOT_QUERYABLE_OBJECTS: dict[str, str] = {
    "collateral": "押品（ap_collateral 未在源系统映射，暂不可查）",
    "codebt_customer": "共债客户（ap_codebt_customer 未在源系统映射，暂不可查）",
    "organization": "机构（ap_org 未在源系统映射，暂不可查）",
    "user": "用户/岗位（ap_user 未在源系统映射，暂不可查）",
}

# ---- Analytics 参数模型（LLM 输出不可信：类型/长度经 Pydantic 校验） ----


class ApprovalStepParams(BaseModel):
    group_customer_name: str = Field(
        min_length=1, max_length=100, description="集团客户名称"
    )
    signal_id: str | None = Field(
        default=None,
        max_length=64,
        description="可选：指定预警信号号（SGN-...）精确查询",
    )


class GroupConcentrationParams(BaseModel):
    group_customer_name: str = Field(
        min_length=1, max_length=100, description="集团客户名称"
    )


ANALYTIC_PARAMS: dict[str, type[BaseModel]] = {
    "warning_approval_step": ApprovalStepParams,
    "group_concentration_limits": GroupConcentrationParams,
}

# 受限多跳查询 SQL 模板（{params} 由执行器按 param_names 顺序绑定；值一律 ? 参数化）。
# 仅注册表/本模块派生的常量表名与列名，无用户输入拼接面。
ANALYTIC_SQL: dict[str, tuple[str, tuple[str, ...]]] = {
    "warning_approval_step": (
        (
            "SELECT g.group_customer_name, w.signal_id, w.warning_id, w.warn_level, "
            "o.approve_order_id, o.approve_order_status, t.approve_task_id, t.approve_task_status, "
            "n.approve_node_name, n.approve_node_seq, t.post_id, t.approve_remark "
            "FROM ap_warning_signal w "
            "JOIN customer.ap_group_customer g ON w.group_customer_no = g.group_customer_no "
            "JOIN ap_warning_disposal wd ON w.warning_id = wd.warning_id "
            "JOIN approval.ap_approve_order o ON o.remark LIKE '%' || w.signal_id || '%' "
            "JOIN approval.ap_approve_task t ON t.approve_order_id = o.approve_order_id "
            "AND t.approve_task_status = 'PENDING' "
            "JOIN approval.ap_approve_node n ON t.approve_node_id = n.approve_node_id "
            "WHERE g.group_customer_name = ? {signal_clause} "
            "ORDER BY n.approve_node_seq LIMIT ?"
        ),
        ("group_customer_name", "signal_id", "limit"),
    ),
    "group_concentration_limits": (
        (
            "SELECT cl.customer_no, cl.customer_name, cl.concentration_limit, "
            "cl.warning_value, cl.current_status, c.group_customer_no "
            "FROM concentration.ap_concentration_limit cl "
            "JOIN customer.ap_customer c ON cl.customer_no = c.customer_no "
            "WHERE c.group_customer_name = ? ORDER BY cl.concentration_limit DESC LIMIT ?"
        ),
        ("group_customer_name", "limit"),
    ),
}


def adapt_status(field: str, value: Any) -> Any:
    """状态字段值归一化：本体英文态/源中文值 → 源系统中文值（LLM 填哪个都行）。"""
    to_cn = STATUS_TO_CN.get(field)
    if to_cn is None:
        return value
    if value in to_cn:
        return to_cn[value]
    return value


__all__ = [
    "AGG_FUNCTIONS",
    "ANALYTIC_PARAMS",
    "ANALYTIC_SQL",
    "FILTER_OPS",
    "MAX_ANALYTIC_ROWS",
    "MAX_FILTERS",
    "MAX_GROUPS",
    "MAX_ITEMS",
    "MAX_LIMIT",
    "NOT_QUERYABLE_OBJECTS",
    "RISK_QUERY_DERIVED",
    "RISK_QUERY_FIELDS",
    "STATUS_FROM_CN",
    "STATUS_TO_CN",
    "adapt_status",
]
