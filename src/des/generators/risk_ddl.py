"""金融风控 12 张核心表 DDL（脱敏后字段）—— 数据字典 = docs/S3-M1a-字段脱敏映射-脊柱12表.json。

与制造业 generate.py 的 DDL 同风格：SQLite 方言，主键唯一、数值字段用 REAL/INTEGER、日期 TEXT。
字段名/类型/枚举均按脱敏映射 JSON 的 renamed + field_comments 定义。
"""

# ---------------------------------------------------------------------------
# customer 系统（customer.db）
# ---------------------------------------------------------------------------
AP_GROUP_CUSTOMER_DDL = """
CREATE TABLE ap_group_customer (
  group_customer_no TEXT PRIMARY KEY,
  data_date TEXT NOT NULL,
  group_customer_name TEXT NOT NULL,
  customer_status TEXT NOT NULL,
  group_peer_flag INTEGER NOT NULL,
  asset_quality_level_code TEXT NOT NULL,
  asset_quality_level TEXT NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  create_org_no TEXT NOT NULL,
  update_user TEXT NOT NULL,
  update_time TEXT NOT NULL,
  update_org_no TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL
);
"""

AP_CUSTOMER_DDL = """
CREATE TABLE ap_customer (
  customer_id TEXT PRIMARY KEY,
  data_date TEXT NOT NULL,
  upstream_update_time TEXT NOT NULL,
  org_id TEXT NOT NULL,
  org_name TEXT NOT NULL,
  customer_no TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  group_customer_no TEXT NOT NULL,
  group_customer_name TEXT NOT NULL,
  cert_type TEXT NOT NULL,
  cert_no TEXT NOT NULL,
  internal_customer_no TEXT NOT NULL,
  internal_level TEXT NOT NULL,
  external_level TEXT NOT NULL,
  zone_id TEXT NOT NULL,
  zone_name TEXT NOT NULL,
  zone_level TEXT NOT NULL,
  country_id TEXT NOT NULL,
  country_name TEXT NOT NULL,
  industry_id TEXT NOT NULL,
  industry_name TEXT NOT NULL,
  industry_level TEXT NOT NULL,
  asset_quality_level_code TEXT NOT NULL,
  asset_quality_level TEXT NOT NULL,
  related_party_ind INTEGER NOT NULL,
  peer_flag INTEGER NOT NULL,
  enterprise_nature TEXT NOT NULL,
  enterprise_scale TEXT NOT NULL,
  establish_time TEXT NOT NULL,
  registered_capital REAL NOT NULL,
  shareholder_name_1 TEXT NOT NULL,
  shareholder_ratio_1 REAL NOT NULL,
  shareholder_name_2 TEXT NOT NULL,
  shareholder_ratio_2 REAL NOT NULL,
  shareholder_name_3 TEXT NOT NULL,
  shareholder_ratio_3 REAL NOT NULL,
  chairman_name TEXT NOT NULL,
  supervisor_name TEXT NOT NULL,
  finance_head_name TEXT NOT NULL,
  general_manager_name TEXT NOT NULL,
  invest_company_1 TEXT NOT NULL,
  invest_amount_1 REAL NOT NULL,
  invest_currency_name_1 TEXT NOT NULL,
  invest_ratio_1 REAL NOT NULL,
  invest_company_2 TEXT NOT NULL,
  invest_amount_2 REAL NOT NULL,
  invest_currency_name_2 TEXT NOT NULL,
  invest_ratio_2 REAL NOT NULL,
  invest_company_3 TEXT NOT NULL,
  invest_amount_3 REAL NOT NULL,
  invest_currency_name_3 TEXT NOT NULL,
  invest_ratio_3 REAL NOT NULL,
  customer_status TEXT NOT NULL,
  final_score REAL NOT NULL,
  final_score_level TEXT NOT NULL,
  industry_commerce_score_level TEXT NOT NULL,
  trading_score_level TEXT NOT NULL,
  credit_score_level TEXT NOT NULL,
  credit_reference_score_level TEXT NOT NULL,
  financial_score_level TEXT NOT NULL,
  industry_commerce_index REAL NOT NULL,
  trading_index REAL NOT NULL,
  credit_index REAL NOT NULL,
  credit_reference_index REAL NOT NULL,
  financial_index REAL NOT NULL,
  clear_remark_1 TEXT,
  clear_remark_2 TEXT,
  clear_remark_3 TEXT,
  clear_remark_4 TEXT,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  create_org_no TEXT NOT NULL,
  update_user TEXT NOT NULL,
  update_time TEXT NOT NULL,
  update_org_no TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# risk 系统（risk.db）
# ---------------------------------------------------------------------------
AP_WARNING_SIGNAL_DDL = """
CREATE TABLE ap_warning_signal (
  warning_id TEXT PRIMARY KEY,
  data_date TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  org_id TEXT NOT NULL,
  org_name TEXT NOT NULL,
  belong_group TEXT NOT NULL,
  warn_level TEXT NOT NULL,
  event_type TEXT NOT NULL,
  warn_source TEXT NOT NULL,
  warn_reason TEXT NOT NULL,
  signal_way TEXT NOT NULL,
  sys_proposal_signal_grade TEXT NOT NULL,
  signal_id TEXT NOT NULL,
  signal_name TEXT NOT NULL,
  signal_status TEXT NOT NULL,
  signal_level1_topic TEXT NOT NULL,
  signal_level2_topic TEXT NOT NULL,
  signal_description TEXT NOT NULL,
  signal_generate_date TEXT NOT NULL,
  signal_establish_date TEXT NOT NULL,
  signal_establish_operator TEXT NOT NULL,
  signal_update_date TEXT NOT NULL,
  data_source TEXT NOT NULL,
  is_important_customer INTEGER NOT NULL,
  info_type INTEGER NOT NULL,
  user_num TEXT NOT NULL,
  to_user TEXT NOT NULL,
  clear_remark_1 TEXT,
  clear_remark_2 TEXT,
  clear_remark_3 TEXT,
  update_time TEXT NOT NULL,
  update_user TEXT NOT NULL,
  del_ind INTEGER NOT NULL,
  push_warn_reason TEXT NOT NULL,
  invest_balance REAL NOT NULL,
  cert_type_code TEXT NOT NULL,
  cert_no TEXT NOT NULL,
  biz_date TEXT NOT NULL,
  group_customer_no TEXT NOT NULL,
  group_customer_type TEXT NOT NULL,
  risk_exposure REAL NOT NULL,
  disposal_status TEXT NOT NULL,
  disposal_demand TEXT NOT NULL,
  apply_no TEXT,
  apply_comment TEXT,
  process_status TEXT,
  audit_status TEXT,
  audit_comment TEXT,
  is_shared INTEGER NOT NULL
);
"""

AP_WARNING_DISPOSAL_DDL = """
CREATE TABLE ap_warning_disposal (
  disposal_id TEXT PRIMARY KEY,
  warning_id TEXT NOT NULL,
  disposal_status TEXT NOT NULL,
  disposal_progress TEXT NOT NULL,
  disposal_time TEXT NOT NULL,
  operator_user TEXT NOT NULL,
  operate_time TEXT NOT NULL
);
"""

AP_DISPOSAL_DDL = """
CREATE TABLE ap_disposal (
  disposal_id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL,
  business_type TEXT NOT NULL,
  deal_type TEXT NOT NULL,
  comment TEXT NOT NULL,
  deal_user_id TEXT NOT NULL,
  is_deleted INTEGER NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL,
  update_user TEXT NOT NULL
);
"""

AP_DISPOSAL_DETAIL_DDL = """
CREATE TABLE ap_disposal_detail (
  disposal_detail_id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL,
  business_type TEXT NOT NULL,
  signal_id TEXT NOT NULL,
  is_deleted INTEGER NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL,
  update_user TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# concentration 系统（concentration.db）
# ---------------------------------------------------------------------------
AP_CONCENTRATION_LIMIT_DDL = """
CREATE TABLE ap_concentration_limit (
  concentration_limit_id TEXT PRIMARY KEY,
  customer_no TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  warning_value REAL NOT NULL,
  concentration_limit REAL NOT NULL,
  concentration_limit_old REAL NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  update_user TEXT NOT NULL,
  update_time TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  current_status TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# approval 系统（approval.db）
# ---------------------------------------------------------------------------
AP_APPROVE_NODE_DDL = """
CREATE TABLE ap_approve_node (
  approve_node_id TEXT PRIMARY KEY,
  approve_order_type TEXT NOT NULL,
  approve_node_seq INTEGER NOT NULL,
  post_id TEXT NOT NULL,
  approve_node_name TEXT NOT NULL,
  approve_rule TEXT NOT NULL,
  is_deleted INTEGER NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL
);
"""

AP_APPROVE_ORDER_DDL = """
CREATE TABLE ap_approve_order (
  approve_order_id TEXT PRIMARY KEY,
  approve_order_type TEXT NOT NULL,
  approve_order_title TEXT NOT NULL,
  apply_user_id TEXT NOT NULL,
  approved_user_id TEXT NOT NULL,
  apply_time TEXT NOT NULL,
  approve_time TEXT,
  approve_order_status TEXT NOT NULL,
  business_type TEXT NOT NULL,
  remark TEXT NOT NULL,
  is_deleted INTEGER NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL,
  derive_warn_level_red INTEGER NOT NULL,
  derive_warn_level_yellow INTEGER NOT NULL,
  derive_warn_level_blue INTEGER NOT NULL,
  opinion_description TEXT
);
"""

AP_APPROVE_TASK_DDL = """
CREATE TABLE ap_approve_task (
  approve_task_id TEXT PRIMARY KEY,
  approve_order_id TEXT NOT NULL,
  approve_node_id TEXT NOT NULL,
  post_id TEXT NOT NULL,
  approve_task_status TEXT NOT NULL,
  approve_result TEXT,
  approve_remark TEXT,
  approve_time TEXT,
  is_deleted INTEGER NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# project 系统（project.db）
# ---------------------------------------------------------------------------
AP_RISK_PROJECT_DDL = """
CREATE TABLE ap_risk_project (
  risk_project_id TEXT PRIMARY KEY,
  sort_no INTEGER NOT NULL,
  group_customer_name TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  division TEXT NOT NULL,
  enterprise_overview TEXT NOT NULL,
  org_id_1 TEXT NOT NULL,
  org_name_1 TEXT NOT NULL,
  project_name TEXT NOT NULL,
  org_id_2 TEXT NOT NULL,
  org_name_2 TEXT NOT NULL,
  business_type TEXT NOT NULL,
  credit_subject TEXT NOT NULL,
  business_balance REAL NOT NULL,
  risk_exposure_balance REAL NOT NULL,
  impairment_provision REAL NOT NULL,
  five_classification TEXT NOT NULL,
  guarantee_method TEXT NOT NULL,
  project_progress TEXT NOT NULL,
  is_deleted INTEGER NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL,
  update_user TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# base 系统（base.db）
# ---------------------------------------------------------------------------
AP_DIM_METRIC_DDL = """
CREATE TABLE ap_dim_metric (
  dim_metric_id TEXT PRIMARY KEY,
  data_date TEXT NOT NULL,
  org_id TEXT NOT NULL,
  dim_type_code TEXT NOT NULL,
  dim_type_name TEXT NOT NULL,
  customer_no TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  group_customer_no TEXT NOT NULL,
  group_customer_name TEXT NOT NULL,
  business_type_code TEXT NOT NULL,
  business_product_code TEXT NOT NULL,
  index_id TEXT NOT NULL,
  index_name TEXT NOT NULL,
  index_value REAL NOT NULL,
  index_unit TEXT NOT NULL,
  currency_id TEXT NOT NULL,
  currency_name TEXT NOT NULL,
  create_user TEXT NOT NULL,
  create_time TEXT NOT NULL,
  update_user TEXT NOT NULL,
  update_time TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL
);
"""

# M1b 全量补全：42 张新表 DDL（由 scripts/s3_m1b_scaffold_risk_ext.py 生成，字典 key = {system}.{table}）。
from .risk_ddl_ext import RISK_EXT_DDL_1
from .risk_ddl_ext2 import RISK_EXT_DDL_2

RISK_DDL: dict[str, str] = {
    "customer.ap_group_customer": AP_GROUP_CUSTOMER_DDL,
    "customer.ap_customer": AP_CUSTOMER_DDL,
    "risk.ap_warning_signal": AP_WARNING_SIGNAL_DDL,
    "risk.ap_warning_disposal": AP_WARNING_DISPOSAL_DDL,
    "risk.ap_disposal": AP_DISPOSAL_DDL,
    "risk.ap_disposal_detail": AP_DISPOSAL_DETAIL_DDL,
    "concentration.ap_concentration_limit": AP_CONCENTRATION_LIMIT_DDL,
    "approval.ap_approve_node": AP_APPROVE_NODE_DDL,
    "approval.ap_approve_order": AP_APPROVE_ORDER_DDL,
    "approval.ap_approve_task": AP_APPROVE_TASK_DDL,
    "project.ap_risk_project": AP_RISK_PROJECT_DDL,
    "base.ap_dim_metric": AP_DIM_METRIC_DDL,
    **RISK_EXT_DDL_1,
    **RISK_EXT_DDL_2,
}
