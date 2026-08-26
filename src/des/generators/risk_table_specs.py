"""金融风控 54 表注册表 RISK_TABLE_SPECS（表 → DDL + 行生成器 + 主键 + 依赖）。

脊柱 12 表（generate_ap_*_rows 在 risk_table_generators）+ M1b 全量补全 42 表
（risk_table_generators_customer/risk/approval/base）。generate.build_enterprise 按拓扑序消费。
拆出本模块以保持 risk_table_generators.py ≤800 行（工程约束）。
"""

from __future__ import annotations

from typing import Any

from .risk_ddl import RISK_DDL
from .risk_table_generators import (
    generate_ap_approve_node_rows,
    generate_ap_approve_order_rows,
    generate_ap_approve_task_rows,
    generate_ap_concentration_limit_rows,
    generate_ap_customer_rows,
    generate_ap_dim_metric_rows,
    generate_ap_disposal_detail_rows,
    generate_ap_disposal_rows,
    generate_ap_group_customer_rows,
    generate_ap_risk_project_rows,
    generate_ap_warning_disposal_rows,
    generate_ap_warning_signal_rows,
)
from .risk_table_generators_approval import (
    generate_ap_approve_oper_log_rows,
    generate_ap_approve_todo_rows,
    generate_ap_approve_warn_rel_rows,
    generate_ap_codebt_customer_rows,
    generate_ap_codebt_warn_score_rows,
    generate_ap_concentration_limit_adj_rows,
    generate_ap_concentration_warn_adj_rows,
    generate_ap_cust_query_log_rows,
    generate_ap_serial_counter_rows,
)
from .risk_table_generators_base import (
    generate_ap_biz_dict_rows,
    generate_ap_custom_param_rows,
    generate_ap_data_dict_rows,
    generate_ap_dim_rank_rows,
    generate_ap_metric_std_rows,
    generate_ap_org_rows,
    generate_ap_preference_file_rows,
    generate_ap_supervise_opinion_rows,
    generate_ap_sys_param_rows,
    generate_ap_top_query_log_rows,
    generate_ap_user_rows,
)
from .risk_table_generators_customer import (
    generate_ap_bank_pledge_detail_rows,
    generate_ap_collateral_rows,
    generate_ap_customer_assets_rows,
    generate_ap_customer_invest_dist_rows,
    generate_ap_customer_relation_rows,
    generate_ap_customer_relation_tree_rows,
    generate_ap_important_customer_list_rows,
    generate_ap_securities_pledge_detail_rows,
    generate_ap_subsidiary_credit_detail_rows,
    generate_ap_subsidiary_mortgage_rows,
    generate_ap_top500_customer_risk_rows,
)
from .risk_table_generators_risk import (
    generate_ap_audit_detail_rows,
    generate_ap_compliance_risk_ledger_rows,
    generate_ap_compliance_risk_ledger_tmp_rows,
    generate_ap_deviation_warn_score_rows,
    generate_ap_regulatory_penalty_rows,
    generate_ap_warn_derive_deal_detail_rows,
    generate_ap_warn_derive_sub_push_rows,
    generate_ap_warn_signal_concentration_rows,
    generate_ap_warn_signal_derive_rows,
    generate_ap_warn_signal_deviation_rows,
    generate_ap_warning_push_rows,
)

# 表注册表（表 → DDL + 行生成器 + 主键 + 依赖；generate.build_enterprise 按拓扑序执行）
# ---------------------------------------------------------------------------
RISK_TABLE_SPECS: dict[str, dict[str, Any]] = {
    # —— 脊柱 12 表（M1b 保留，不改）——
    "customer.ap_group_customer": {
        "ddl": RISK_DDL["customer.ap_group_customer"],
        "gen": generate_ap_group_customer_rows,
        "pk": ["group_customer_no"],
        "depends_on": [],
    },
    "customer.ap_customer": {
        "ddl": RISK_DDL["customer.ap_customer"],
        "gen": generate_ap_customer_rows,
        "pk": ["customer_id"],
        "depends_on": ["customer.ap_group_customer"],
    },
    "risk.ap_warning_signal": {
        "ddl": RISK_DDL["risk.ap_warning_signal"],
        "gen": generate_ap_warning_signal_rows,
        "pk": ["warning_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    "risk.ap_warning_disposal": {
        "ddl": RISK_DDL["risk.ap_warning_disposal"],
        "gen": generate_ap_warning_disposal_rows,
        "pk": ["disposal_id"],
        "depends_on": ["risk.ap_warning_signal"],
    },
    "risk.ap_disposal": {
        "ddl": RISK_DDL["risk.ap_disposal"],
        "gen": generate_ap_disposal_rows,
        "pk": ["disposal_id"],
        "depends_on": ["risk.ap_warning_signal"],
    },
    "risk.ap_disposal_detail": {
        "ddl": RISK_DDL["risk.ap_disposal_detail"],
        "gen": generate_ap_disposal_detail_rows,
        "pk": ["disposal_detail_id"],
        "depends_on": ["risk.ap_disposal", "risk.ap_warning_signal"],
    },
    "concentration.ap_concentration_limit": {
        "ddl": RISK_DDL["concentration.ap_concentration_limit"],
        "gen": generate_ap_concentration_limit_rows,
        "pk": ["concentration_limit_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "approval.ap_approve_node": {
        "ddl": RISK_DDL["approval.ap_approve_node"],
        "gen": generate_ap_approve_node_rows,
        "pk": ["approve_node_id"],
        "depends_on": [],
    },
    "approval.ap_approve_order": {
        "ddl": RISK_DDL["approval.ap_approve_order"],
        "gen": generate_ap_approve_order_rows,
        "pk": ["approve_order_id"],
        "depends_on": ["risk.ap_warning_signal"],
    },
    "approval.ap_approve_task": {
        "ddl": RISK_DDL["approval.ap_approve_task"],
        "gen": generate_ap_approve_task_rows,
        "pk": ["approve_task_id"],
        "depends_on": ["approval.ap_approve_order", "approval.ap_approve_node"],
    },
    "project.ap_risk_project": {
        "ddl": RISK_DDL["project.ap_risk_project"],
        "gen": generate_ap_risk_project_rows,
        "pk": ["risk_project_id"],
        "depends_on": ["customer.ap_group_customer", "customer.ap_customer"],
    },
    "base.ap_dim_metric": {
        "ddl": RISK_DDL["base.ap_dim_metric"],
        "gen": generate_ap_dim_metric_rows,
        "pk": ["dim_metric_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    # —— M1b 全量补全：42 张新表 ——
    "customer.ap_customer_relation": {
        "ddl": RISK_DDL["customer.ap_customer_relation"],
        "gen": generate_ap_customer_relation_rows,
        "pk": ["customer_relation_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "customer.ap_customer_relation_tree": {
        "ddl": RISK_DDL["customer.ap_customer_relation_tree"],
        "gen": generate_ap_customer_relation_tree_rows,
        "pk": ["customer_relation_tree_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "customer.ap_important_customer_list": {
        "ddl": RISK_DDL["customer.ap_important_customer_list"],
        "gen": generate_ap_important_customer_list_rows,
        "pk": ["important_customer_id"],
        "depends_on": ["customer.ap_group_customer"],
    },
    "customer.ap_top500_customer_risk": {
        "ddl": RISK_DDL["customer.ap_top500_customer_risk"],
        "gen": generate_ap_top500_customer_risk_rows,
        "pk": ["top500_customer_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    "customer.ap_customer_assets": {
        "ddl": RISK_DDL["customer.ap_customer_assets"],
        "gen": generate_ap_customer_assets_rows,
        "pk": ["customer_assets_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "customer.ap_customer_invest_dist": {
        "ddl": RISK_DDL["customer.ap_customer_invest_dist"],
        "gen": generate_ap_customer_invest_dist_rows,
        "pk": ["customer_invest_dist_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "customer.ap_subsidiary_credit_detail": {
        "ddl": RISK_DDL["customer.ap_subsidiary_credit_detail"],
        "gen": generate_ap_subsidiary_credit_detail_rows,
        "pk": ["project_id"],
        "depends_on": ["customer.ap_group_customer", "customer.ap_customer"],
    },
    "customer.ap_collateral": {
        "ddl": RISK_DDL["customer.ap_collateral"],
        "gen": generate_ap_collateral_rows,
        "pk": ["collateral_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    "customer.ap_subsidiary_mortgage": {
        "ddl": RISK_DDL["customer.ap_subsidiary_mortgage"],
        "gen": generate_ap_subsidiary_mortgage_rows,
        "pk": ["subsidiary_mortgage_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "customer.ap_bank_pledge_detail": {
        "ddl": RISK_DDL["customer.ap_bank_pledge_detail"],
        "gen": generate_ap_bank_pledge_detail_rows,
        "pk": ["bank_pledge_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    "customer.ap_securities_pledge_detail": {
        "ddl": RISK_DDL["customer.ap_securities_pledge_detail"],
        "gen": generate_ap_securities_pledge_detail_rows,
        "pk": ["securities_pledge_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "risk.ap_warning_push": {
        "ddl": RISK_DDL["risk.ap_warning_push"],
        "gen": generate_ap_warning_push_rows,
        "pk": ["warning_push_id"],
        "depends_on": ["risk.ap_warning_signal"],
    },
    "risk.ap_audit_detail": {
        "ddl": RISK_DDL["risk.ap_audit_detail"],
        "gen": generate_ap_audit_detail_rows,
        "pk": ["audit_id"],
        "depends_on": [],
    },
    "risk.ap_compliance_risk_ledger": {
        "ddl": RISK_DDL["risk.ap_compliance_risk_ledger"],
        "gen": generate_ap_compliance_risk_ledger_rows,
        "pk": ["compliance_risk_id"],
        "depends_on": [],
    },
    "risk.ap_compliance_risk_ledger_tmp": {
        "ddl": RISK_DDL["risk.ap_compliance_risk_ledger_tmp"],
        "gen": generate_ap_compliance_risk_ledger_tmp_rows,
        "pk": ["compliance_risk_tmp_id"],
        "depends_on": [],
    },
    "risk.ap_regulatory_penalty": {
        "ddl": RISK_DDL["risk.ap_regulatory_penalty"],
        "gen": generate_ap_regulatory_penalty_rows,
        "pk": ["penalty_id"],
        "depends_on": [],
    },
    "risk.ap_warn_signal_concentration": {
        "ddl": RISK_DDL["risk.ap_warn_signal_concentration"],
        "gen": generate_ap_warn_signal_concentration_rows,
        "pk": ["concentration_signal_id"],
        "depends_on": [
            "customer.ap_top500_customer_risk",
            "customer.ap_customer",
            "customer.ap_group_customer",
        ],
    },
    "risk.ap_warn_signal_derive": {
        "ddl": RISK_DDL["risk.ap_warn_signal_derive"],
        "gen": generate_ap_warn_signal_derive_rows,
        "pk": ["derive_warning_id"],
        "depends_on": ["customer.ap_customer", "approval.ap_approve_order"],
    },
    "risk.ap_warn_derive_deal_detail": {
        "ddl": RISK_DDL["risk.ap_warn_derive_deal_detail"],
        "gen": generate_ap_warn_derive_deal_detail_rows,
        "pk": ["derive_deal_detail_id"],
        "depends_on": ["risk.ap_warn_signal_derive"],
    },
    "risk.ap_warn_derive_sub_push": {
        "ddl": RISK_DDL["risk.ap_warn_derive_sub_push"],
        "gen": generate_ap_warn_derive_sub_push_rows,
        "pk": ["derive_sub_push_id"],
        "depends_on": ["risk.ap_warn_signal_derive", "customer.ap_customer"],
    },
    "risk.ap_warn_signal_deviation": {
        "ddl": RISK_DDL["risk.ap_warn_signal_deviation"],
        "gen": generate_ap_warn_signal_deviation_rows,
        "pk": ["deviation_signal_id"],
        "depends_on": [
            "customer.ap_customer",
            "customer.ap_group_customer",
            "approval.ap_approve_order",
        ],
    },
    "risk.ap_deviation_warn_score": {
        "ddl": RISK_DDL["risk.ap_deviation_warn_score"],
        "gen": generate_ap_deviation_warn_score_rows,
        "pk": ["deviation_warn_score_id"],
        "depends_on": ["customer.ap_group_customer"],
    },
    "concentration.ap_concentration_limit_adj": {
        "ddl": RISK_DDL["concentration.ap_concentration_limit_adj"],
        "gen": generate_ap_concentration_limit_adj_rows,
        "pk": ["concentration_limit_adj_id"],
        "depends_on": ["concentration.ap_concentration_limit", "customer.ap_customer"],
    },
    "concentration.ap_concentration_warn_adj": {
        "ddl": RISK_DDL["concentration.ap_concentration_warn_adj"],
        "gen": generate_ap_concentration_warn_adj_rows,
        "pk": ["concentration_warn_adj_id"],
        "depends_on": ["concentration.ap_concentration_limit", "customer.ap_customer"],
    },
    "concentration.ap_codebt_customer": {
        "ddl": RISK_DDL["concentration.ap_codebt_customer"],
        "gen": generate_ap_codebt_customer_rows,
        "pk": ["codebt_customer_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "concentration.ap_codebt_warn_score": {
        "ddl": RISK_DDL["concentration.ap_codebt_warn_score"],
        "gen": generate_ap_codebt_warn_score_rows,
        "pk": ["codebt_warn_score_id"],
        "depends_on": ["customer.ap_customer"],
    },
    "approval.ap_approve_oper_log": {
        "ddl": RISK_DDL["approval.ap_approve_oper_log"],
        "gen": generate_ap_approve_oper_log_rows,
        "pk": ["approve_log_id"],
        "depends_on": ["approval.ap_approve_order", "approval.ap_approve_task"],
    },
    "approval.ap_approve_warn_rel": {
        "ddl": RISK_DDL["approval.ap_approve_warn_rel"],
        "gen": generate_ap_approve_warn_rel_rows,
        "pk": ["approve_warn_rel_id"],
        "depends_on": ["approval.ap_approve_order", "risk.ap_warning_signal"],
    },
    "approval.ap_approve_todo": {
        "ddl": RISK_DDL["approval.ap_approve_todo"],
        "gen": generate_ap_approve_todo_rows,
        "pk": ["approve_todo_id"],
        "depends_on": ["approval.ap_approve_task"],
    },
    "project.ap_cust_query_log": {
        "ddl": RISK_DDL["project.ap_cust_query_log"],
        "gen": generate_ap_cust_query_log_rows,
        "pk": ["cust_query_log_id"],
        "depends_on": [],
    },
    "project.ap_serial_counter": {
        "ddl": RISK_DDL["project.ap_serial_counter"],
        "gen": generate_ap_serial_counter_rows,
        "pk": ["serial_counter_id"],
        "depends_on": [],
    },
    "base.ap_metric_std": {
        "ddl": RISK_DDL["base.ap_metric_std"],
        "gen": generate_ap_metric_std_rows,
        "pk": ["index_id"],
        "depends_on": [],
    },
    "base.ap_dim_rank": {
        "ddl": RISK_DDL["base.ap_dim_rank"],
        "gen": generate_ap_dim_rank_rows,
        "pk": ["dim_rank_id"],
        "depends_on": ["customer.ap_customer", "customer.ap_group_customer"],
    },
    "base.ap_custom_param": {
        "ddl": RISK_DDL["base.ap_custom_param"],
        "gen": generate_ap_custom_param_rows,
        "pk": ["custom_param_id"],
        "depends_on": [],
    },
    "base.ap_preference_file": {
        "ddl": RISK_DDL["base.ap_preference_file"],
        "gen": generate_ap_preference_file_rows,
        "pk": ["preference_file_id"],
        "depends_on": [],
    },
    "base.ap_supervise_opinion": {
        "ddl": RISK_DDL["base.ap_supervise_opinion"],
        "gen": generate_ap_supervise_opinion_rows,
        "pk": ["supervise_opinion_id"],
        "depends_on": [],
    },
    "base.ap_top_query_log": {
        "ddl": RISK_DDL["base.ap_top_query_log"],
        "gen": generate_ap_top_query_log_rows,
        "pk": ["top_query_log_id"],
        "depends_on": [],
    },
    "base.ap_data_dict": {
        "ddl": RISK_DDL["base.ap_data_dict"],
        "gen": generate_ap_data_dict_rows,
        "pk": ["dict_id"],
        "depends_on": [],
    },
    "base.ap_sys_param": {
        "ddl": RISK_DDL["base.ap_sys_param"],
        "gen": generate_ap_sys_param_rows,
        "pk": ["sys_param_id"],
        "depends_on": [],
    },
    "base.ap_org": {
        "ddl": RISK_DDL["base.ap_org"],
        "gen": generate_ap_org_rows,
        "pk": ["org_id"],
        "depends_on": [],
    },
    "base.ap_user": {
        "ddl": RISK_DDL["base.ap_user"],
        "gen": generate_ap_user_rows,
        "pk": ["user_id"],
        "depends_on": [],
    },
    "base.ap_biz_dict": {
        "ddl": RISK_DDL["base.ap_biz_dict"],
        "gen": generate_ap_biz_dict_rows,
        "pk": ["biz_dict_id"],
        "depends_on": [],
    },
}
