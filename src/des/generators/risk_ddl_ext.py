"""S3 M1b 全量补全：42 张新表 DDL（脱敏后字段，数据字典 = docs/S3-M1a-字段脱敏映射-全量42表.json）。
本文件由 scripts/s3_m1b_scaffold_risk_ext.py 生成（类型推断 + 覆盖）；改动请改脚手架后重新生成。
字段名 = renamed（ap_ 脱敏名），注释 = field_comments；表名 = 脱敏名，原型表名只作溯源注释。
"""


# customer.ap_customer_relation —— 客户关系表（切片）（原型 o_a_erms_cust_relation，25 字段）
AP_CUSTOMER_RELATION_DDL = """
CREATE TABLE ap_customer_relation (
  customer_relation_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  upstream_update_time TEXT NOT NULL,  -- 更新时间（上游）
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  cert_type_code TEXT NOT NULL,  -- 客户证件类型
  cert_no TEXT NOT NULL,  -- 客户证件号
  customer_name TEXT NOT NULL,  -- 客户名称
  internal_customer_no TEXT NOT NULL,  -- 客户编号
  group_cert_type_code TEXT NOT NULL,  -- 集团客户证件类型
  group_cert_no TEXT NOT NULL,  -- 集团客户证件号
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  data_source TEXT NOT NULL,  -- 数据来源
  operate_type TEXT NOT NULL,  -- 操作类型
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  clear_remark_3 TEXT,  -- 备注3（占位，语义不明）
  clear_remark_4 TEXT,  -- 备注4（占位，语义不明）
  create_time TEXT NOT NULL,  -- 创建时间
  create_org_no TEXT NOT NULL,  -- 创建机构
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL  -- 多实体标识
);
"""

# customer.ap_customer_relation_tree —— 客户关系树（应用写入）（原型 o_a_erms_cust_relation_opt，28 字段）
AP_CUSTOMER_RELATION_TREE_DDL = """
CREATE TABLE ap_customer_relation_tree (
  customer_relation_tree_id TEXT NOT NULL,  -- 主键ID
  upstream_update_time TEXT NOT NULL,  -- 更新时间（上游）
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  cert_type_code TEXT NOT NULL,  -- 客户证件类型
  cert_no TEXT NOT NULL,  -- 客户证件号
  customer_name TEXT NOT NULL,  -- 客户名称
  internal_customer_no TEXT NOT NULL,  -- 客户编号
  group_cert_type_code TEXT NOT NULL,  -- 集团客户证件类型
  group_cert_no TEXT NOT NULL,  -- 集团客户证件号
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  data_source TEXT NOT NULL,  -- 数据来源
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  clear_remark_3 TEXT,  -- 备注3（占位，语义不明）
  clear_remark_4 TEXT,  -- 备注4（占位，语义不明）
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  create_org_no TEXT NOT NULL,  -- 创建机构
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  is_important_group_customer INTEGER NOT NULL,  -- 重要集团客户标识
  effective_date TEXT NOT NULL,  -- 生效日期
  invalid_date TEXT NOT NULL,  -- 失效日期
  current_status TEXT NOT NULL,  -- 当前状态
  cert_type_code_from_bank TEXT NOT NULL,  -- 客户证件类型(来源为银行报送的关系树)
  cert_no_from_bank TEXT NOT NULL  -- 客户证件号(来源为银行报送的关系树)
);
"""

# customer.ap_important_customer_list —— 重要客户名单管理表（原型 o_a_erms_cust_list，18 字段）
AP_IMPORTANT_CUSTOMER_LIST_DDL = """
CREATE TABLE ap_important_customer_list (
  important_customer_id TEXT NOT NULL,  -- 主键ID
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  important_customer_flag INTEGER NOT NULL,  -- 大额客户标识
  risk_customer_flag INTEGER NOT NULL,  -- 大额风险客户标识
  custom_customer_flag INTEGER NOT NULL,  -- 自定义客户标识
  status TEXT NOT NULL,  -- 状态
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  clear_remark_3 TEXT,  -- 备注3（占位，语义不明）
  clear_remark_4 TEXT,  -- 备注4（占位，语义不明）
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  customer_short_name TEXT NOT NULL,  -- 客户简称
  is_real_estate INTEGER NOT NULL,  -- 是否房地产
  belong_industry TEXT NOT NULL,  -- 所属行业
  is_high_leverage INTEGER NOT NULL  -- 是否高杠杆
);
"""

# customer.ap_top500_customer_risk —— 前500大客户风险投融资结果表（原型 o_a_erms_top500_cust_info，24 字段）
AP_TOP500_CUSTOMER_RISK_DDL = """
CREATE TABLE ap_top500_customer_risk (
  top500_customer_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  org_id TEXT NOT NULL,  -- 机构编码
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  group_customer_no TEXT NOT NULL,  -- 客户所属集团编号
  group_customer_name TEXT NOT NULL,  -- 客户所属集团名称
  customer_type TEXT NOT NULL,  -- 客户类型
  group_member_count INTEGER NOT NULL,  -- 集团成员数
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  risk_asset_balance REAL NOT NULL,  -- 风险类资产规模
  concentration_degree REAL NOT NULL,  -- 集中度监测
  risk_exposure_rank_no TEXT NOT NULL,  -- 风险暴露排名
  asset_quality_level TEXT NOT NULL,  -- 资产质量（代码说明：A009）
  warn_flag INTEGER NOT NULL,  -- 预警标识(1:是，0:否)
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL,  -- 多实体标识
  invest_balance_new REAL NOT NULL  -- 投融资余额-新
);
"""

# customer.ap_customer_assets —— 资产结构结果表（原型 o_a_erms_cust_assets，19 字段）
AP_CUSTOMER_ASSETS_DDL = """
CREATE TABLE ap_customer_assets (
  customer_assets_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  customer_type TEXT NOT NULL,  -- 客户类型
  business_type_code TEXT NOT NULL,  -- 业务类型代码
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  risk_asset_balance REAL NOT NULL,  -- 不良余额
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL,  -- 多实体标识
  invest_balance_new REAL NOT NULL  -- 投融资余额-新
);
"""

# customer.ap_customer_invest_dist —— 投资分布结果表（原型 o_a_erms_cust_sub_org_invest，19 字段）
AP_CUSTOMER_INVEST_DIST_DDL = """
CREATE TABLE ap_customer_invest_dist (
  customer_invest_dist_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  customer_type TEXT NOT NULL,  -- 客户类型
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  risk_asset_balance REAL NOT NULL,  -- 不良余额
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL,  -- 多实体标识
  risk_bad_balance REAL NOT NULL,  -- 不良风险暴露余额
  invest_balance_new REAL NOT NULL  -- 全口径投融资业务余额
);
"""

# customer.ap_subsidiary_credit_detail —— 集团加工后子公司明细表（原型 o_a_erms_credit_detail_1，89 字段）
AP_SUBSIDIARY_CREDIT_DETAIL_DDL = """
CREATE TABLE ap_subsidiary_credit_detail (
  project_id TEXT NOT NULL,  -- 项目编号
  data_date TEXT NOT NULL,  -- 数据日期
  upstream_update_time TEXT NOT NULL,  -- 更新时间（上游）
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  project_name TEXT NOT NULL,  -- 项目名称
  customer_name TEXT NOT NULL,  -- 客户名称
  group_customer_name TEXT NOT NULL,  -- 客户所属集团名称
  group_customer_name_processed TEXT NOT NULL,  -- 集团加工的所属集团名称
  group_peer_flag INTEGER NOT NULL,  -- 集团客户同业标识
  cert_type_code TEXT NOT NULL,  -- 客户证件类型代码
  cert_type TEXT NOT NULL,  -- 客户证件类型名称
  cert_no TEXT NOT NULL,  -- 客户证件号码
  internal_customer_no TEXT NOT NULL,  -- 内部客户号
  internal_level TEXT NOT NULL,  -- 客户内部评级
  external_level TEXT NOT NULL,  -- 客户外部评级
  zone_id TEXT NOT NULL,  -- 区域（境内）代码
  zone_name TEXT NOT NULL,  -- 区域（境内）名称
  zone_level TEXT NOT NULL,  -- 区域评级
  country_id TEXT NOT NULL,  -- 区域（境外）代码
  country_name TEXT NOT NULL,  -- 区域（境外）名称
  industry_id TEXT NOT NULL,  -- 行业代码
  industry_name TEXT NOT NULL,  -- 行业名称
  industry_level TEXT NOT NULL,  -- 行业评级
  related_party_ind INTEGER NOT NULL,  -- 关联方标识
  peer_flag INTEGER NOT NULL,  -- 单一客户同业标识
  enterprise_nature_code TEXT NOT NULL,  -- 企业性质代码
  enterprise_nature TEXT NOT NULL,  -- 企业性质
  enterprise_scale TEXT NOT NULL,  -- 企业规模
  establish_time TEXT NOT NULL,  -- 成立时间
  registered_capital REAL NOT NULL,  -- 注册资本
  business_type_code TEXT NOT NULL,  -- 业务类型代码
  business_type TEXT NOT NULL,  -- 业务类型名称
  business_product_code TEXT NOT NULL,  -- 业务品种代码
  business_product_name TEXT NOT NULL,  -- 业务品种名称
  internal_business_product_code TEXT NOT NULL,  -- 内部业务品种代码
  internal_business_product_name TEXT NOT NULL,  -- 内部业务品种名称
  currency_id TEXT NOT NULL,  -- 币种代码
  index_unit TEXT NOT NULL,  -- 单位
  business_balance REAL NOT NULL,  -- 投融资业务余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  pledge_value REAL NOT NULL,  -- 合格抵质押金额
  guarantee_value REAL NOT NULL,  -- 合格保证金额
  impairment_provision REAL NOT NULL,  -- 已计提减值
  principal_overdue_days INTEGER NOT NULL,  -- 本金逾期天数
  interest_overdue_days INTEGER NOT NULL,  -- 利息逾期天数
  asset_quality_level_code TEXT NOT NULL,  -- 资产质量分类代码
  asset_quality_level TEXT NOT NULL,  -- 资产质量分类名称
  limit_value REAL NOT NULL,  -- 限额
  shareholder_name_1 TEXT NOT NULL,  -- 第一大股东
  shareholder_ratio_1 REAL NOT NULL,  -- 第一大股东出资比例
  shareholder_name_2 TEXT NOT NULL,  -- 第二大股东
  shareholder_ratio_2 REAL NOT NULL,  -- 第二大股东出资比例
  shareholder_name_3 TEXT NOT NULL,  -- 第三大股东
  shareholder_ratio_3 REAL NOT NULL,  -- 第三大股东出资比例
  chairman_name TEXT NOT NULL,  -- 董事长
  supervisor_name TEXT NOT NULL,  -- 监事长
  finance_head_name TEXT NOT NULL,  -- 财务负责人
  general_manager_name TEXT NOT NULL,  -- 总经理
  invest_company_1 TEXT NOT NULL,  -- 对外投资公司1
  invest_amount_1 REAL NOT NULL,  -- 投资金额1(万元)
  invest_currency_name_1 TEXT NOT NULL,  -- 投资币种名称1
  invest_ratio_1 REAL NOT NULL,  -- 出资比例1
  invest_company_2 TEXT NOT NULL,  -- 对外投资公司2
  invest_amount_2 REAL NOT NULL,  -- 投资金额2(万元)
  invest_currency_name_2 TEXT NOT NULL,  -- 投资币种名称2
  invest_ratio_2 REAL NOT NULL,  -- 出资比例2
  invest_company_3 TEXT NOT NULL,  -- 对外投资公司3
  invest_amount_3 REAL NOT NULL,  -- 投资金额3(万元)
  invest_currency_name_3 TEXT NOT NULL,  -- 投资币种名称3
  invest_ratio_3 REAL NOT NULL,  -- 出资比例3
  customer_status TEXT NOT NULL,  -- 客户状态
  final_score REAL NOT NULL,  -- 最终模型分数（含预警）
  final_score_level TEXT NOT NULL,  -- 客户最终评级
  industry_commerce_score_level TEXT NOT NULL,  -- 工商子模型等级
  trading_score_level TEXT NOT NULL,  -- 交易子模型等级
  credit_score_level TEXT NOT NULL,  -- 信贷子模型等级
  credit_reference_score_level TEXT NOT NULL,  -- 征信子模型等级
  financial_score_level TEXT NOT NULL,  -- 财务子模型等级
  industry_commerce_index REAL NOT NULL,  -- 工商模型有效指数
  trading_index REAL NOT NULL,  -- 交易模型有效指数
  credit_index REAL NOT NULL,  -- 信贷模型有效指数
  credit_reference_index REAL NOT NULL,  -- 征信模型有效指数
  financial_index REAL NOT NULL,  -- 财务模型有效指数
  operate_type TEXT NOT NULL,  -- 操作类型
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  clear_remark_3 TEXT,  -- 备注3（占位，语义不明）
  clear_remark_4 TEXT  -- 备注4（占位，语义不明）
);
"""

# customer.ap_collateral —— 押品信息表（原型 o_a_erms_negot_info，42 字段）
AP_COLLATERAL_DDL = """
CREATE TABLE ap_collateral (
  collateral_id TEXT NOT NULL,  -- 主键ID
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  data_date TEXT NOT NULL,  -- 数据日期（报送）
  project_id TEXT NOT NULL,  -- 项目编号
  project_name TEXT NOT NULL,  -- 项目名称
  customer_name TEXT NOT NULL,  -- 单一客户名称
  group_customer_name TEXT NOT NULL,  -- 客户所属集团名称
  guarantee_contract_id TEXT NOT NULL,  -- 担保合同编号
  guarantee_contract_name TEXT NOT NULL,  -- 担保合同名称
  guarantee_contract_amount REAL NOT NULL,  -- 担保合同金额
  pledge_name TEXT NOT NULL,  -- 抵押物名称
  guarantee_repay_order INTEGER NOT NULL,  -- 担保清偿顺位
  mortgage_ind INTEGER NOT NULL,  -- 抵质押标识
  mortgage_property_type TEXT NOT NULL,  -- 抵质押物类型
  internal_mortgage_property_type TEXT NOT NULL,  -- 内部抵质押物类型
  is_have_external_estimate_org INTEGER NOT NULL,  -- 是否有外部评估机构
  estimate_org_name TEXT NOT NULL,  -- 评估机构名称
  estimate_value REAL NOT NULL,  -- 评估价值
  estimate_date TEXT NOT NULL,  -- 评估日期
  corp_identify_time TEXT NOT NULL,  -- 公司认定时间
  corp_identify_value REAL NOT NULL,  -- 公司认定价值
  mortgaged_value REAL NOT NULL,  -- 已抵押价值
  mortgage_rate REAL NOT NULL,  -- 抵质押率
  maintenance_rate REAL NOT NULL,  -- 维保比
  owner_name TEXT NOT NULL,  -- 抵质押物所有权人名称
  owner_cert_type TEXT NOT NULL,  -- 抵质押物所有人证件类型
  owner_cert_no TEXT NOT NULL,  -- 抵质押物所有人证件号码
  warrant_no TEXT NOT NULL,  -- 权证号
  internal_collateral_id TEXT NOT NULL,  -- 内部押品编号
  is_mortgage_registered INTEGER NOT NULL,  -- 是否办理抵押登记
  register_date TEXT NOT NULL,  -- 登记日期
  right_register_org_name TEXT NOT NULL,  -- 权利登记机构名称
  register_org_credit_code TEXT NOT NULL,  -- 登记机构统一社会信用代码
  is_major_guarantee_collateral INTEGER NOT NULL,  -- 是否主要担保措施押品
  collateral_status TEXT NOT NULL,  -- 押品状态
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT  -- 备注2（占位，语义不明）
);
"""

# customer.ap_subsidiary_mortgage —— 子公司抵质押物信息（原型 o_a_erms_org_mrtg_prop_info，19 字段）
AP_SUBSIDIARY_MORTGAGE_DDL = """
CREATE TABLE ap_subsidiary_mortgage (
  subsidiary_mortgage_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  org_id TEXT NOT NULL,  -- 机构id
  org_name TEXT NOT NULL,  -- 机构名称
  customer_name TEXT NOT NULL,  -- 客户名称
  customer_type TEXT NOT NULL,  -- 客户类型
  mortgage_ind INTEGER NOT NULL,  -- 抵质押标识
  total_count INTEGER NOT NULL,  -- 总数
  estimate_value REAL NOT NULL,  -- 评估价值
  corp_identify_value REAL NOT NULL,  -- 公司认定价值
  mortgaged_value REAL NOT NULL,  -- 已抵押价值
  estimate_quantity INTEGER NOT NULL,  -- 近两年评估数量
  percent_value REAL NOT NULL,  -- 占比
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT  -- 备注2（占位，语义不明）
);
"""

# customer.ap_bank_pledge_detail —— 押品明细（银行业）（原型 o_a_erms_pledge_bankdetail，44 字段）
AP_BANK_PLEDGE_DETAIL_DDL = """
CREATE TABLE ap_bank_pledge_detail (
  bank_pledge_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期（报送）
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  project_id TEXT NOT NULL,  -- 项目编号
  project_name TEXT NOT NULL,  -- 项目名称
  customer_credit_code TEXT NOT NULL,  -- 客户统一社会信用代码
  customer_name TEXT NOT NULL,  -- 单一客户名称
  group_customer_name TEXT NOT NULL,  -- 客户所属集团名称
  business_product_code TEXT NOT NULL,  -- 金控层级业务类型代码
  business_product_name TEXT NOT NULL,  -- 金控层级业务类型名称
  guarantee_contract_id TEXT NOT NULL,  -- 担保合同编号
  guarantee_contract_name TEXT NOT NULL,  -- 担保合同名称
  guarantee_contract_amount REAL NOT NULL,  -- 担保合同金额
  guarantee_contract_balance REAL NOT NULL,  -- 担保合同余额
  internal_pledge_no TEXT NOT NULL,  -- 内部押品编码
  pledge_name TEXT NOT NULL,  -- 抵质押物名称
  guarantee_repay_order INTEGER NOT NULL,  -- 担保清偿顺位
  mortgage_ind INTEGER NOT NULL,  -- 抵质押标识
  mortgage_property_type TEXT NOT NULL,  -- 抵质押物类型
  internal_mortgage_property_type TEXT NOT NULL,  -- 内部抵质押物类型
  is_have_external_estimate_org INTEGER NOT NULL,  -- 是否有外部评估机构
  pledge_location TEXT NOT NULL,  -- 抵押物位置
  estimate_org_name TEXT NOT NULL,  -- 评估机构名称
  initial_estimate_value REAL NOT NULL,  -- 初始评估价值
  initial_estimate_date TEXT NOT NULL,  -- 初始评估日期
  latest_estimate_value REAL NOT NULL,  -- 最新评估价值
  latest_estimate_date TEXT NOT NULL,  -- 评估日期
  disposal_value REAL NOT NULL,  -- 处置价值
  disposal_date TEXT NOT NULL,  -- 处置日期
  mortgaged_value REAL NOT NULL,  -- 已抵押价值
  mortgage_rate REAL NOT NULL,  -- 抵质押率
  maintenance_rate REAL NOT NULL,  -- 维保比
  owner_name TEXT NOT NULL,  -- 抵质押物所有权人名称
  owner_cert_type TEXT NOT NULL,  -- 抵质押物所有人证件类型
  owner_cert_no TEXT NOT NULL,  -- 抵质押物所有人证件号码
  warrant_no TEXT NOT NULL,  -- 权证号
  is_mortgage_registered INTEGER NOT NULL,  -- 是否办理抵押登记
  register_date TEXT NOT NULL,  -- 登记日期
  right_register_org_name TEXT NOT NULL,  -- 权利登记机构名称
  register_org_credit_code TEXT NOT NULL,  -- 登记机构统一社会信用代码
  pledge_status TEXT NOT NULL,  -- 押品状态
  biz_date TEXT NOT NULL,  -- 业务日期(网关自动填充)
  company_partition TEXT NOT NULL  -- 公司划分(网关自动填充)
);
"""

# customer.ap_securities_pledge_detail —— 押品明细（证券业）（原型 o_a_erms_pledge_securitiesdetail，19 字段）
AP_SECURITIES_PLEDGE_DETAIL_DDL = """
CREATE TABLE ap_securities_pledge_detail (
  securities_pledge_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据期次
  org_id TEXT NOT NULL,  -- 填报机构id
  org_name TEXT NOT NULL,  -- 填报机构名称
  ecif_no TEXT NOT NULL,  -- 客户ECF编码
  customer_credit_code TEXT NOT NULL,  -- 客户统一社会信用代码
  customer_name TEXT NOT NULL,  -- 单一客户名称
  business_product_code TEXT NOT NULL,  -- 金控层级业务类型代码
  business_product_name TEXT NOT NULL,  -- 金控层级业务类型名称
  invest_value REAL NOT NULL,  -- 融资规模(元)
  pledge_subject_code TEXT NOT NULL,  -- 质押标的证券代码
  pledge_subject_name TEXT NOT NULL,  -- 质押标的证券名称
  pledge_subject_value REAL NOT NULL,  -- 质押标的证券市值(元)
  bonus_amount REAL NOT NULL,  -- 质押红利金额(元)
  maintenance_rate REAL NOT NULL,  -- 维保比
  pledge_status TEXT NOT NULL,  -- 押品状态
  biz_date TEXT NOT NULL,  -- 业务日期(网关自动填充)
  company_partition TEXT NOT NULL,  -- 公司划分(网关自动填充)
  partition_date TEXT NOT NULL  -- 分区统计日期
);
"""

# risk.ap_warning_push —— 预警推送表（原型 o_a_erms_cust_warn_sgn_push，8 字段）
AP_WARNING_PUSH_DDL = """
CREATE TABLE ap_warning_push (
  warning_push_id TEXT NOT NULL,  -- 主键ID
  warning_id TEXT NOT NULL,  -- 预警ID（外键→ap_warning_signal.warning_id）
  push_warn_reason TEXT NOT NULL,  -- 推送预警事由
  push_person TEXT NOT NULL,  -- 推送人
  push_time TEXT NOT NULL,  -- 推送时间
  receive_person TEXT NOT NULL,  -- 接收人
  receive_instruction TEXT NOT NULL,  -- 接收批示
  receive_time TEXT NOT NULL  -- 接收时间
);
"""

# risk.ap_audit_detail —— 合规内控审计记录表（原型 o_a_erms_audit_detail，23 字段）
AP_AUDIT_DETAIL_DDL = """
CREATE TABLE ap_audit_detail (
  audit_id TEXT NOT NULL,  -- 主键ID
  declare_unit TEXT NOT NULL,  -- 填报单位
  question_id TEXT NOT NULL,  -- 问题编号
  audit_type TEXT NOT NULL,  -- 审计类型
  audit_start_time TEXT NOT NULL,  -- 审计开始时间
  audit_end_time TEXT NOT NULL,  -- 审计结束时间
  audit_org_name TEXT NOT NULL,  -- 审计机关名称
  audit_aim TEXT NOT NULL,  -- 审计目的
  audit_object_name TEXT NOT NULL,  -- 审计对象名称
  audit_content TEXT NOT NULL,  -- 审计内容
  audit_basis TEXT NOT NULL,  -- 审计依据
  audit_member TEXT NOT NULL,  -- 审计组成员
  audit_question_title TEXT NOT NULL,  -- 审计问题标题
  audit_question_memo TEXT NOT NULL,  -- 审计问题摘要
  qualitative_basis TEXT NOT NULL,  -- 定性依据
  rectification_requirement TEXT NOT NULL,  -- 整改要求
  duty_org_dept TEXT NOT NULL,  -- 整改责任机构/部门
  deadline_requirement TEXT NOT NULL,  -- 整改时限要求
  supervise_unit TEXT NOT NULL,  -- 督办单位
  rectification_measure TEXT NOT NULL,  -- 整改措施
  completion_status TEXT NOT NULL,  -- 整改完成情况
  operator_user TEXT NOT NULL,  -- 操作人
  operate_time TEXT NOT NULL  -- 操作时间
);
"""

# risk.ap_compliance_risk_ledger —— 潜在合规风险摸排台账（原型 o_a_erms_compliance_risk_ledger，18 字段）
AP_COMPLIANCE_RISK_LEDGER_DDL = """
CREATE TABLE ap_compliance_risk_ledger (
  compliance_risk_id TEXT NOT NULL,  -- 主键ID
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  dept_line TEXT NOT NULL,  -- 部门/条线
  business_type TEXT NOT NULL,  -- 业务类型
  event_overview TEXT NOT NULL,  -- 事件概述
  self_check TEXT NOT NULL,  -- 自查情况
  land_time TEXT NOT NULL,  -- 落地时间
  expect_land_time TEXT NOT NULL,  -- 预计落地时间
  penalty_percent REAL NOT NULL,  -- 被罚概率
  expect_penalty_amount REAL NOT NULL,  -- 预计处罚金额
  expect_other_penalty TEXT NOT NULL,  -- 预计其他处罚形式
  remark TEXT NOT NULL,  -- 备注
  risk_status TEXT NOT NULL,  -- 状态
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# risk.ap_compliance_risk_ledger_tmp —— 合规风险摸排台账(tmp)（原型 o_a_erms_compliance_risk_ledger_tmp，18 字段）
AP_COMPLIANCE_RISK_LEDGER_TMP_DDL = """
CREATE TABLE ap_compliance_risk_ledger_tmp (
  compliance_risk_tmp_id TEXT NOT NULL,  -- 主键ID
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  dept_line TEXT NOT NULL,  -- 部门/条线
  business_type TEXT NOT NULL,  -- 业务类型
  event_overview TEXT NOT NULL,  -- 事件概述
  self_check TEXT NOT NULL,  -- 自查情况
  land_time TEXT NOT NULL,  -- 落地时间
  expect_land_time TEXT NOT NULL,  -- 预计落地时间
  penalty_percent REAL NOT NULL,  -- 被罚概率
  expect_penalty_amount REAL NOT NULL,  -- 预计处罚金额
  expect_other_penalty TEXT NOT NULL,  -- 预计其他处罚形式
  remark TEXT NOT NULL,  -- 备注
  risk_status TEXT NOT NULL,  -- 状态
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# risk.ap_regulatory_penalty —— 监管处罚记录表（原型 o_a_erms_custd_pnsh，23 字段）
AP_REGULATORY_PENALTY_DDL = """
CREATE TABLE ap_regulatory_penalty (
  penalty_id TEXT NOT NULL,  -- 主键ID
  declare_unit TEXT NOT NULL,  -- 填报单位
  penalty_decision_date TEXT NOT NULL,  -- 处罚决定日期
  penalty_decision_no TEXT NOT NULL,  -- 处罚决定书文号
  penalty_decision_org TEXT NOT NULL,  -- 处罚决定机关
  penalty_object TEXT NOT NULL,  -- 被处罚对象
  major_violation_fact TEXT NOT NULL,  -- 主要违法违规事实
  penalty_basis TEXT NOT NULL,  -- 处罚依据
  case_type TEXT NOT NULL,  -- 案件类型
  problem_category TEXT NOT NULL,  -- 问题所属类别
  penalty_form TEXT NOT NULL,  -- 处罚形式
  penalty_amount REAL NOT NULL,  -- 处罚金额（万）
  confiscation_amount REAL NOT NULL,  -- 没收金额（万）
  disposal_status TEXT NOT NULL,  -- 处置情况
  memo TEXT NOT NULL,  -- 备注
  operator_user TEXT NOT NULL,  -- 操作人
  operate_time TEXT NOT NULL,  -- 操作时间
  effect TEXT NOT NULL,  -- 影响
  problem_category_new TEXT NOT NULL,  -- 问题所属类别（新）
  rectification_plan_finish_time TEXT NOT NULL,  -- 整改计划完成时间
  rectification_complete_flag INTEGER NOT NULL,  -- 整改是否完成
  accountability_result TEXT NOT NULL,  -- 问责结果
  data_status TEXT NOT NULL  -- 状态
);
"""

# risk.ap_warn_signal_concentration —— 客户集中度预警信号表（原型 p_erms_cust_warn_sgn_concentration，29 字段）
AP_WARN_SIGNAL_CONCENTRATION_DDL = """
CREATE TABLE ap_warn_signal_concentration (
  concentration_signal_id TEXT NOT NULL,  -- 主键ID
  top500_customer_id TEXT NOT NULL,  -- 前500大客户风险投融资结果表ID（外键→ap_top500_customer_risk.top500_customer_id）
  data_date TEXT NOT NULL,  -- 数据日期
  org_id TEXT NOT NULL,  -- 机构编码
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  group_customer_no TEXT NOT NULL,  -- 集团客户编号
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  customer_type TEXT NOT NULL,  -- 客户类型
  group_member_count INTEGER NOT NULL,  -- 集团成员数
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  concentration_degree REAL NOT NULL,  -- 集中度监测
  signal_name TEXT NOT NULL,  -- 集中度预警信号名称
  warn_reason TEXT NOT NULL,  -- 预警事由
  concentration_limit REAL NOT NULL,  -- 集中度限额
  risk_warning_threshold REAL NOT NULL,  -- 风险预警线
  warn_rule TEXT NOT NULL,  -- 集中度风险预警等级 字典项P082 红色预警B1和B2、黄色预警A1和A2
  signal_establish_date TEXT NOT NULL,  -- 预警建立日期
  signal_status TEXT NOT NULL,  -- 信号数据状态 字典项P055
  comp_lead_push_status TEXT NOT NULL,  -- 金控领导预警推送状态 字典项P057
  sub_company_push_status TEXT NOT NULL,  -- 子公司推送状态 字典项P059
  sub_company_push_time TEXT NOT NULL,  -- 子公司推送时间
  warn_level TEXT NOT NULL,  -- 集中度预警等级 字典项P081 红色预警RED、黄色预警YELLOW
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL  -- 更新人
);
"""

# risk.ap_warn_signal_derive —— 客户衍生预警信号表（原型 p_erms_cust_warn_sgn_derive，48 字段）
AP_WARN_SIGNAL_DERIVE_DDL = """
CREATE TABLE ap_warn_signal_derive (
  derive_warning_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  customer_id TEXT NOT NULL,  -- 客户编号（外键→ap_customer.customer_id）
  customer_name TEXT NOT NULL,  -- 客户名称
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  belong_group TEXT NOT NULL,  -- 所属集团
  warn_level TEXT NOT NULL,  -- 预警等级
  event_type TEXT NOT NULL,  -- 信号类型
  warn_source TEXT NOT NULL,  -- 预警信息来源
  warn_reason TEXT NOT NULL,  -- 预警事由
  signal_way TEXT NOT NULL,  -- 信号产生方式
  sys_proposal_signal_grade TEXT NOT NULL,  -- 系统建议信号等级
  signal_id TEXT NOT NULL,  -- 信号编号
  signal_name TEXT NOT NULL,  -- 信号名称
  signal_status TEXT NOT NULL,  -- 信号状态
  signal_level1_topic TEXT NOT NULL,  -- 信号一级主题
  signal_level2_topic TEXT NOT NULL,  -- 信号二级主题
  signal_description TEXT NOT NULL,  -- 信号描述
  signal_generate_date TEXT NOT NULL,  -- 信号生成日期
  signal_establish_date TEXT NOT NULL,  -- 信号建立日期
  signal_establish_operator TEXT NOT NULL,  -- 信号建立人
  signal_update_date TEXT NOT NULL,  -- 信号更新日期
  data_source TEXT NOT NULL,  -- 数据来源
  derive_signal_level1_topic TEXT NOT NULL,  -- 衍生信号一级主题 字典项P052
  derive_signal_level2_topic TEXT NOT NULL,  -- 衍生信号二级主题 字典项P051
  derive_warn_level TEXT NOT NULL,  -- 衍生预警等级 字典项P054
  derive_establish_date TEXT NOT NULL,  -- 衍生预警信号建立日期
  warn_model TEXT NOT NULL,  -- 预警模型
  ai_data TEXT NOT NULL,  -- AI智能体数据
  derive_risk_type_determine TEXT NOT NULL,  -- 风险类型判定 字典项P044
  assess_extent_impact TEXT NOT NULL,  -- 影响程度评估
  deal_suggestion TEXT NOT NULL,  -- 处置建议
  derive_signal_status TEXT NOT NULL,  -- 信号数据状态 字典项P055
  comp_lead_push_status TEXT NOT NULL,  -- 金控领导预警推送状态 字典项P057
  warn_reason_update_status TEXT NOT NULL,  -- 预警事由修改状态 字典项P058
  warn_reason_updated TEXT NOT NULL,  -- 修改后的预警事由
  sub_company_push_status TEXT NOT NULL,  -- 子公司推送状态 字典项P059
  sub_company_push_time TEXT NOT NULL,  -- 子公司推送时间
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL,  -- 更新人
  opinion_description TEXT NOT NULL,  -- 审批意见
  approve_order_status TEXT NOT NULL,  -- 字典项P061 PROCESS-审批中 APPROVED-已通过 REJECTED-已驳回
  approve_order_id TEXT NOT NULL,  -- 审批单ID（外键→ap_approve_order.approve_order_id）
  is_holding_add INTEGER NOT NULL  -- 是否金控新增 0-否、1-是
);
"""

# risk.ap_warn_derive_deal_detail —— 衍生预警处置详情表（原型 p_erms_cust_warn_sgn_derive_deal_detail，8 字段）
AP_WARN_DERIVE_DEAL_DETAIL_DDL = """
CREATE TABLE ap_warn_derive_deal_detail (
  derive_deal_detail_id TEXT NOT NULL,  -- 主键ID
  batch_id TEXT NOT NULL,  -- 批处理ID
  derive_warning_id TEXT NOT NULL,  -- 衍生预警信号ID（外键→ap_warn_signal_derive.derive_warning_id）
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL,  -- 更新时间（源字段拼写 UPDATE_IME）
  update_user TEXT NOT NULL  -- 更新人
);
"""

# risk.ap_warn_derive_sub_push —— 衍生预警子公司推送表（原型 p_erms_cust_warn_sgn_derive_sub_push，16 字段）
AP_WARN_DERIVE_SUB_PUSH_DDL = """
CREATE TABLE ap_warn_derive_sub_push (
  derive_sub_push_id TEXT NOT NULL,  -- 主键ID
  derive_warning_id TEXT NOT NULL,  -- 衍生预警信号ID（外键→ap_warn_signal_derive.derive_warning_id）
  signal_establish_date TEXT NOT NULL,  -- 信号建立日期
  customer_id TEXT NOT NULL,  -- 客户编号（外键→ap_customer.customer_id）
  customer_name TEXT NOT NULL,  -- 客户名称
  signal_name TEXT NOT NULL,  -- 信号名称
  signal_level1_topic TEXT NOT NULL,  -- 信号一级主题 字典项
  signal_level2_topic TEXT NOT NULL,  -- 信号二级主题 字典项
  derive_warn_level TEXT NOT NULL,  -- 衍生预警等级
  warn_reason_updated TEXT NOT NULL,  -- 修改后的预警事由
  etl_job_flag INTEGER NOT NULL,  -- etl执行flag 字典项 0未执行、1执行成功、2执行失败
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL,  -- 更新时间（源字段拼写 UPDATE_IME）
  update_user TEXT NOT NULL  -- 更新人
);
"""

# risk.ap_warn_signal_deviation —— 客户背离预警信号表（原型 p_erms_cust_warn_sgn_deviation，29 字段）
AP_WARN_SIGNAL_DEVIATION_DDL = """
CREATE TABLE ap_warn_signal_deviation (
  deviation_signal_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  group_customer_no TEXT NOT NULL,  -- 集团客户编号
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  customer_type TEXT NOT NULL,  -- 客户类型
  group_member_count INTEGER NOT NULL,  -- 集团成员数
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露
  signal_name TEXT NOT NULL,  -- 背离预警信号名称
  warn_reason TEXT NOT NULL,  -- 预警事由
  signal_establish_date TEXT NOT NULL,  -- 预警信号建立日期
  mom REAL NOT NULL,  -- 环比 Month-on-Month
  mgr REAL NOT NULL,  -- 单月增幅 Monthly Growth Rate
  ytd REAL NOT NULL,  -- 较年初 Growth Since the Beginning of the Year
  warn_rule TEXT NOT NULL,  -- 背离预警触发规则标识 字典项P080 环比A、单月增幅阈值B、较年初C
  deviation_signal_status TEXT NOT NULL,  -- 信号数据状态 字典项P055
  comp_lead_push_status TEXT NOT NULL,  -- 金控领导预警推送状态 字典项P057
  sub_company_push_status TEXT NOT NULL,  -- 子公司推送状态 字典项P059
  sub_company_push_time TEXT NOT NULL,  -- 子公司推送时间
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL,  -- 更新人
  opinion_description TEXT NOT NULL,  -- 审批意见
  approve_order_status TEXT NOT NULL,  -- 字典项P061 PROCESS-审批中 APPROVED-已通过 REJECTED-已驳回
  approve_order_id TEXT NOT NULL  -- 申请单ID（外键→ap_approve_order.approve_order_id）
);
"""

# risk.ap_deviation_warn_score —— 趋势背离预警评分模型结果表（原型 p_erms_deviation_cust_warn_score，24 字段）
AP_DEVIATION_WARN_SCORE_DDL = """
CREATE TABLE ap_deviation_warn_score (
  deviation_warn_score_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  group_customer_name TEXT NOT NULL,  -- 集团客户名称
  customer_type TEXT NOT NULL,  -- 客户类型 01 单一客户，02集团客户
  signal_name TEXT NOT NULL,  -- 背离预警信号名称
  risk_exposure REAL NOT NULL,  -- 风险暴露额(亿元)
  invest_balance REAL NOT NULL,  -- 投融资余额(亿元)
  mom REAL NOT NULL,  -- 环比 Month-on-Month
  ytd REAL NOT NULL,  -- 较年初 Growth Since the Beginning of the Year
  mgr REAL NOT NULL,  -- 单月增幅 Monthly Growth Rate
  warn_reason TEXT NOT NULL,  -- 预警事由
  customer_level TEXT NOT NULL,  -- 客户等级
  score REAL NOT NULL,  -- 风险评分
  warn_level_code TEXT NOT NULL,  -- 预警等级代码
  warn_level TEXT NOT NULL,  -- 预警等级
  exposure_change REAL NOT NULL,  -- 敞口变化
  signal_strength REAL NOT NULL,  -- 信号强度
  disposal_priority TEXT NOT NULL,  -- 处置优先级
  involved_amount_level TEXT NOT NULL,  -- 涉及金额等级
  is_disposal_needed INTEGER NOT NULL,  -- 是否需处置
  suggest_actions TEXT NOT NULL,  -- 建议动作
  variation REAL NOT NULL,  -- 金额×变化率
  calc_detail TEXT NOT NULL,  -- 计算过程
  create_time TEXT NOT NULL  -- 创建时间
);
"""

RISK_EXT_DDL_1: dict[str, str] = {
    "customer.ap_customer_relation": AP_CUSTOMER_RELATION_DDL,
    "customer.ap_customer_relation_tree": AP_CUSTOMER_RELATION_TREE_DDL,
    "customer.ap_important_customer_list": AP_IMPORTANT_CUSTOMER_LIST_DDL,
    "customer.ap_top500_customer_risk": AP_TOP500_CUSTOMER_RISK_DDL,
    "customer.ap_customer_assets": AP_CUSTOMER_ASSETS_DDL,
    "customer.ap_customer_invest_dist": AP_CUSTOMER_INVEST_DIST_DDL,
    "customer.ap_subsidiary_credit_detail": AP_SUBSIDIARY_CREDIT_DETAIL_DDL,
    "customer.ap_collateral": AP_COLLATERAL_DDL,
    "customer.ap_subsidiary_mortgage": AP_SUBSIDIARY_MORTGAGE_DDL,
    "customer.ap_bank_pledge_detail": AP_BANK_PLEDGE_DETAIL_DDL,
    "customer.ap_securities_pledge_detail": AP_SECURITIES_PLEDGE_DETAIL_DDL,
    "risk.ap_warning_push": AP_WARNING_PUSH_DDL,
    "risk.ap_audit_detail": AP_AUDIT_DETAIL_DDL,
    "risk.ap_compliance_risk_ledger": AP_COMPLIANCE_RISK_LEDGER_DDL,
    "risk.ap_compliance_risk_ledger_tmp": AP_COMPLIANCE_RISK_LEDGER_TMP_DDL,
    "risk.ap_regulatory_penalty": AP_REGULATORY_PENALTY_DDL,
    "risk.ap_warn_signal_concentration": AP_WARN_SIGNAL_CONCENTRATION_DDL,
    "risk.ap_warn_signal_derive": AP_WARN_SIGNAL_DERIVE_DDL,
    "risk.ap_warn_derive_deal_detail": AP_WARN_DERIVE_DEAL_DETAIL_DDL,
    "risk.ap_warn_derive_sub_push": AP_WARN_DERIVE_SUB_PUSH_DDL,
    "risk.ap_warn_signal_deviation": AP_WARN_SIGNAL_DEVIATION_DDL,
    "risk.ap_deviation_warn_score": AP_DEVIATION_WARN_SCORE_DDL,
}
