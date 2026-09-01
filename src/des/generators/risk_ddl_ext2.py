"""S3 M1b 全量补全：42 张新表 DDL（脱敏后字段，数据字典 = docs/S3-M1a-字段脱敏映射-全量42表.json）。
本文件由 scripts/s3_m1b_scaffold_risk_ext.py 生成（类型推断 + 覆盖）；改动请改脚手架后重新生成。
字段名 = renamed（ap_ 脱敏名），注释 = field_comments；表名 = 脱敏名，原型表名只作溯源注释。
"""


# concentration.ap_concentration_limit_adj —— 集中度限额调整表（原型 o_a_erms_larg_cust_limit_adj，13 字段）
AP_CONCENTRATION_LIMIT_ADJ_DDL = """
CREATE TABLE ap_concentration_limit_adj (
  concentration_limit_adj_id TEXT NOT NULL,  -- 主键ID
  concentration_limit_id TEXT NOT NULL,  -- 集中度限额编号（外键→ap_concentration_limit.concentration_limit_id）
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  concentration_limit REAL NOT NULL,  -- 集中度限额
  concentration_limit_old TEXT NOT NULL,  -- 集中度限额-更新前的值
  current_status TEXT NOT NULL,  -- 集团限额维护-状态
  approve_status TEXT NOT NULL,  -- 审批状态
  approve_comment TEXT NOT NULL,  -- 审批意见
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# concentration.ap_concentration_warn_adj —— 集中度预警调整表（原型 o_a_erms_larg_cust_warn_adj，13 字段）
AP_CONCENTRATION_WARN_ADJ_DDL = """
CREATE TABLE ap_concentration_warn_adj (
  concentration_warn_adj_id TEXT NOT NULL,  -- 主键ID
  concentration_limit_id TEXT NOT NULL,  -- 集中度预警调整编号（外键→ap_concentration_limit.concentration_limit_id）
  customer_no TEXT NOT NULL,  -- 客户编号
  customer_name TEXT NOT NULL,  -- 客户名称
  concentration_warn_line TEXT NOT NULL,  -- 风险预警线
  concentration_warn_line_old TEXT NOT NULL,  -- 风险预警线-更新前的值
  current_status TEXT NOT NULL,  -- 集团预警维护-状态
  approve_status TEXT NOT NULL,  -- 审批状态
  approve_comment TEXT NOT NULL,  -- 审批意见
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# concentration.ap_codebt_customer —— 共债客户明细表（原型 p_erms_codebt_cust_info，12 字段）
AP_CODEBT_CUSTOMER_DDL = """
CREATE TABLE ap_codebt_customer (
  codebt_customer_id TEXT NOT NULL,  -- 自增主键
  customer_name TEXT NOT NULL,  -- 客户名称
  data_date TEXT NOT NULL,  -- 数据日期（格式：yyyy-mm-dd）
  customer_type TEXT NOT NULL,  -- 客户类型（01/02：单一对公客户）
  group_member_count INTEGER NOT NULL,  -- 集团成员数
  subsidiary_count INTEGER NOT NULL,  -- 跨子公司数
  org_id TEXT NOT NULL,  -- 子公司机构编码
  invest_balance REAL NOT NULL,  -- 投融资余额
  risk_exposure REAL NOT NULL,  -- 风险暴露金额
  is_deleted INTEGER NOT NULL,  -- 0:未删除,1:删除
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# concentration.ap_codebt_warn_score —— 共债客户风险预警评分表（原型 p_erms_codebt_cust_warn_score，20 字段）
AP_CODEBT_WARN_SCORE_DDL = """
CREATE TABLE ap_codebt_warn_score (
  codebt_warn_score_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  signal_generate_date TEXT NOT NULL,  -- 预警信号生成日期
  customer_name TEXT NOT NULL,  -- 客户名称
  customer_type TEXT NOT NULL,  -- 客户类型 01 单一客户，02集团客户
  risk_exposure REAL NOT NULL,  -- 风险暴露额
  invest_balance REAL NOT NULL,  -- 投融资余额
  industry_id TEXT NOT NULL,  -- 客户所属行业ID
  industry_name TEXT NOT NULL,  -- 行业名称
  warn_level TEXT NOT NULL,  -- 预警信号等级
  signal_level2_topic TEXT NOT NULL,  -- 预警信号二级主题
  signal_count INTEGER NOT NULL,  -- 有效信号个数
  red_signal_count INTEGER NOT NULL,  -- 红色信号个数
  blue_signal_count INTEGER NOT NULL,  -- 蓝色信号个数
  yellow_signal_count INTEGER NOT NULL,  -- 黄色信号个数
  subsidiary_count INTEGER NOT NULL,  -- 子公司数量
  top10_risk_exposure_avg REAL NOT NULL,  -- 集团前10大客户平均风险暴露
  score REAL NOT NULL,  -- 得分
  calc_detail TEXT NOT NULL,  -- 计算过程
  create_time TEXT NOT NULL  -- 创建时间
);
"""

# approval.ap_approve_oper_log —— 审批操作日志表（原型 p_erms_approve_oper_log，8 字段）
AP_APPROVE_OPER_LOG_DDL = """
CREATE TABLE ap_approve_oper_log (
  approve_log_id TEXT NOT NULL,  -- 日志ID
  approve_order_id TEXT NOT NULL,  -- 审批单ID（外键→ap_approve_order.approve_order_id）
  approve_task_id TEXT NOT NULL,  -- 审批任务ID（外键→ap_approve_task.approve_task_id）
  operator_user_id TEXT NOT NULL,  -- 操作人ID
  operate_type TEXT NOT NULL,  -- 操作类型：SUBMIT-提交 APPROVE-审批通过 REJECT-审批驳回
  operate_remark TEXT NOT NULL,  -- 操作备注
  operate_time TEXT NOT NULL,  -- 操作时间
  ext TEXT  -- 扩展字段
);
"""

# approval.ap_approve_warn_rel —— 审批单预警信号关联表（原型 p_erms_approve_order_warn_rel，6 字段）
AP_APPROVE_WARN_REL_DDL = """
CREATE TABLE ap_approve_warn_rel (
  approve_warn_rel_id TEXT NOT NULL,  -- 关联ID
  approve_order_id TEXT NOT NULL,  -- 审批单ID（外键→ap_approve_order.approve_order_id）
  warning_id TEXT NOT NULL,  -- 预警信号ID（外键→ap_warning_signal.warning_id）
  is_deleted INTEGER NOT NULL,  -- 是否删除 0-未删 1-已删
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# approval.ap_approve_todo —— 用户待办任务表（原型 p_erms_approve_todo，7 字段）
AP_APPROVE_TODO_DDL = """
CREATE TABLE ap_approve_todo (
  approve_todo_id TEXT NOT NULL,  -- 待办ID
  approve_task_id TEXT NOT NULL,  -- 关联审批任务ID（岗位级，外键→ap_approve_task.approve_task_id）
  user_id TEXT NOT NULL,  -- 待办用户ID
  approve_todo_status TEXT NOT NULL,  -- 待办状态 字典项P065：UNHANDLED-未处理 HANDLED-已处理 INVALID-已失效
  is_deleted INTEGER NOT NULL,  -- 是否删除 0-未删 1-已删
  create_time TEXT NOT NULL,  -- 创建时间
  update_time TEXT NOT NULL  -- 更新时间
);
"""

# project.ap_cust_query_log —— 客户查询记录日志表（原型 p_erms_top_query_log，5 字段）
AP_CUST_QUERY_LOG_DDL = """
CREATE TABLE ap_cust_query_log (
  cust_query_log_id TEXT NOT NULL,  -- 主键ID（自增）
  query_keyword TEXT NOT NULL,  -- 查询关键词
  create_user TEXT NOT NULL,  -- 创建人/操作用户
  create_time TEXT NOT NULL,  -- 创建时间/查询时间
  data_flag INTEGER NOT NULL  -- 1 集团客户 2 单一客户
);
"""

# project.ap_serial_counter —— 分布式流水号计数器表（原型 p_serial_number_counter，5 字段）
AP_SERIAL_COUNTER_DDL = """
CREATE TABLE ap_serial_counter (
  serial_counter_id TEXT NOT NULL,  -- 主键ID
  date_str TEXT NOT NULL,  -- 日期字符串（格式：yyyyMMdd，如20251223）
  current_counter INTEGER NOT NULL,  -- 当日当前计数器值（初始为1，原子自增）
  create_time TEXT NOT NULL,  -- 记录创建时间
  update_time TEXT NOT NULL  -- 记录更新时间
);
"""

# base.ap_metric_std —— 标准化指标信息表（切片）（原型 o_a_erms_index_list_std，30 字段）
AP_METRIC_STD_DDL = """
CREATE TABLE ap_metric_std (
  index_id TEXT NOT NULL,  -- 映射后编号
  data_date TEXT NOT NULL,  -- 数据日期
  upstream_update_time TEXT NOT NULL,  -- 更新时间（上游）
  org_id TEXT NOT NULL,  -- 机构编码
  org_name TEXT NOT NULL,  -- 机构名称
  index_level_id TEXT NOT NULL,  -- 指标层级ID
  index_level_name TEXT NOT NULL,  -- 指标层级名称
  index_type_id TEXT NOT NULL,  -- 指标类别ID
  index_type_name TEXT NOT NULL,  -- 指标类别名称
  original_index_id TEXT NOT NULL,  -- 指标编号
  original_index_name TEXT NOT NULL,  -- 指标名称
  index_name TEXT NOT NULL,  -- 映射后指标名称
  index_value REAL NOT NULL,  -- 指标数值
  index_unit TEXT NOT NULL,  -- 单位
  currency_id TEXT NOT NULL,  -- 币种代码
  currency_name TEXT NOT NULL,  -- 币种名称
  index_frequency TEXT NOT NULL,  -- 报送频率
  index_type_code TEXT NOT NULL,  -- 报送类型
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
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL  -- 多实体标识
);
"""

# base.ap_dim_rank —— 分维度排名信息表（原型 o_a_erms_dim_rank，21 字段）
AP_DIM_RANK_DDL = """
CREATE TABLE ap_dim_rank (
  dim_rank_id TEXT NOT NULL,  -- 主键ID
  org_id TEXT NOT NULL,  -- 机构编码
  dim_type_code TEXT NOT NULL,  -- 维度类型代码
  dim_type_name TEXT NOT NULL,  -- 维度类型名称
  customer_no TEXT NOT NULL,  -- 单一客户编号
  customer_name TEXT NOT NULL,  -- 单一客户名称
  group_customer_no TEXT NOT NULL,  -- 所属集团编号
  group_customer_name TEXT NOT NULL,  -- 所属集团名称
  business_type_code TEXT NOT NULL,  -- 业务类型代码
  index_value REAL NOT NULL,  -- 指标数值
  index_unit TEXT NOT NULL,  -- 单位
  currency_id TEXT NOT NULL,  -- 币种代码
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  create_org_no TEXT NOT NULL,  -- 创建机构
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL,  -- 多实体标识
  data_date TEXT NOT NULL  -- 数据日期
);
"""

# base.ap_custom_param —— 自定义参数表（原型 o_a_erms_custom_param，17 字段）
AP_CUSTOM_PARAM_DDL = """
CREATE TABLE ap_custom_param (
  custom_param_id TEXT NOT NULL,  -- 主键ID
  data_date TEXT NOT NULL,  -- 数据日期
  org_id TEXT NOT NULL,  -- 组织机构ID
  index_id TEXT NOT NULL,  -- 指标ID
  index_value REAL NOT NULL,  -- 指标数值
  index_description TEXT NOT NULL,  -- 指标描述
  del_ind INTEGER NOT NULL,  -- 删除标识
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL,  -- 创建时间
  create_org_no TEXT NOT NULL,  -- 创建机构
  update_user TEXT NOT NULL,  -- 更新人
  update_time TEXT NOT NULL,  -- 更新时间
  update_org_no TEXT NOT NULL,  -- 更新机构
  version TEXT NOT NULL,  -- 框架版本号
  tenant_id TEXT NOT NULL  -- 多实体标识
);
"""

# base.ap_preference_file —— 偏好陈述信息附件表（原型 o_a_erms_pref_info_file_tab，15 字段）
AP_PREFERENCE_FILE_DDL = """
CREATE TABLE ap_preference_file (
  preference_file_id TEXT NOT NULL,  -- 主键ID
  business_type TEXT NOT NULL,  -- 业务模块
  business_id TEXT NOT NULL,  -- 业务编号
  file_id TEXT NOT NULL,  -- 文件编号
  file_name TEXT NOT NULL,  -- 文件名称
  file_suffix TEXT NOT NULL,  -- 文件后缀
  file_type TEXT NOT NULL,  -- 文件类型
  file_path TEXT NOT NULL,  -- 文件路径
  operator_user TEXT NOT NULL,  -- 操作人
  operate_time TEXT NOT NULL,  -- 操作时间
  attachment_belong TEXT NOT NULL,  -- 附件归属（占位，语义不明，冗余保留）
  belong_dept TEXT NOT NULL,  -- 归属部门（占位，语义不明，冗余保留）
  clear_remark_1 TEXT,  -- 备注1（占位，语义不明）
  clear_remark_2 TEXT,  -- 备注2（占位，语义不明）
  clear_remark_3 TEXT  -- 备注3（占位，语义不明）
);
"""

# base.ap_supervise_opinion —— 监管意见分类展示（原型 o_a_erms_supervise_opinion_classify，11 字段）
AP_SUPERVISE_OPINION_DDL = """
CREATE TABLE ap_supervise_opinion (
  supervise_opinion_id TEXT NOT NULL,  -- 主键ID
  org_id TEXT NOT NULL,  -- 机构编号
  org_name TEXT NOT NULL,  -- 机构名称
  year_time TEXT NOT NULL,  -- 年份
  first_directory TEXT NOT NULL,  -- 一级目录
  second_directory TEXT NOT NULL,  -- 二级目录
  problem_areas TEXT NOT NULL,  -- 问题领域
  basic_matter TEXT NOT NULL,  -- 基本事项
  industry_self TEXT NOT NULL,  -- 行业/自身
  update_time TEXT NOT NULL,  -- 更新时间
  remark TEXT NOT NULL  -- 备注
);
"""

# base.ap_top_query_log —— 客户查询历史记录表（原型 o_a_erms_top_query_log，4 字段）
AP_TOP_QUERY_LOG_DDL = """
CREATE TABLE ap_top_query_log (
  top_query_log_id TEXT NOT NULL,  -- 主键ID
  query_keyword TEXT NOT NULL,  -- 客户查询关键词
  create_user TEXT NOT NULL,  -- 创建人
  create_time TEXT NOT NULL  -- 创建时间
);
"""

# base.ap_data_dict —— 数据字典（原型 o_base_ddct，19 字段）
AP_DATA_DICT_DDL = """
CREATE TABLE ap_data_dict (
  dict_id TEXT NOT NULL,  -- 主键ID
  dict_key TEXT NOT NULL,  -- 字典键
  dict_type_code TEXT NOT NULL,  -- 字典类型
  dict_type_name TEXT NOT NULL,  -- 字典类型名称
  dict_value TEXT NOT NULL,  -- 字典值
  dict_value_name TEXT NOT NULL,  -- 字典值名称
  dict_group TEXT NOT NULL,  -- 字典组
  dict_description TEXT NOT NULL,  -- 字典描述
  dict_seq INTEGER NOT NULL,  -- 字典排序
  status_code INTEGER NOT NULL,  -- 状态：无效0有效1
  create_time TEXT NOT NULL,  -- 创建时间
  create_user TEXT NOT NULL,  -- 创建人
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL,  -- 更新人
  extended_id TEXT,  -- 扩展编号
  del_ind INTEGER NOT NULL,  -- 删除标志
  version TEXT NOT NULL,  -- 版本号
  tenant_id TEXT NOT NULL,  -- 租户id
  system_id TEXT NOT NULL  -- 系统ID
);
"""

# base.ap_sys_param —— 系统参数（原型 o_base_stm_parm，20 字段；P0-1 增元数据列）
AP_SYS_PARAM_DDL = """
CREATE TABLE ap_sys_param (
  sys_param_id TEXT NOT NULL,  -- 主键ID
  param_type_code TEXT NOT NULL,  -- 参数类型
  param_type_name TEXT NOT NULL,  -- 参数类型名称
  param_id TEXT NOT NULL,  -- 参数编码
  param_value TEXT NOT NULL,  -- 参数值
  param_description TEXT NOT NULL,  -- 参数描述
  whether_cache INTEGER NOT NULL,  -- 是否缓存（否0是1）
  create_time TEXT NOT NULL,  -- 创建时间
  create_user TEXT NOT NULL,  -- 创建人
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL,  -- 更新人
  extended_id TEXT,  -- 扩展编号
  del_ind INTEGER NOT NULL,  -- 删除标志
  version TEXT NOT NULL,  -- 版本号
  tenant_id TEXT NOT NULL,  -- 租户编号
  param_source TEXT,  -- 出处（依据条款/口径来源，P0-1）
  param_approver TEXT,  -- 定值/审批人（P0-1）
  numerator_desc TEXT,  -- 分子构成（P0-1）
  denominator_desc TEXT,  -- 分母说明（P0-1）
  netting_rule TEXT  -- 净额规则（P0-1）
);
"""

# base.ap_org —— 系统机构表（原型 o_sys_organization，18 字段）
AP_ORG_DDL = """
CREATE TABLE ap_org (
  org_id TEXT NOT NULL,  -- 主键ID
  org_code TEXT NOT NULL,  -- 机构代码
  org_name TEXT NOT NULL,  -- 机构名称
  parent_org_code TEXT,  -- 父节点机构代码
  org_level_code TEXT NOT NULL,  -- 机构等级
  sort_no INTEGER NOT NULL,  -- 排序
  ext_json_data TEXT,  -- 扩展数据
  status_code TEXT NOT NULL,  -- 状态
  remark TEXT NOT NULL,  -- 备注
  del_ind INTEGER NOT NULL,  -- 删除标志:0-未删除；1-删除
  create_user TEXT NOT NULL,  -- 创建者
  create_time TEXT NOT NULL,  -- 创建时间
  update_user TEXT NOT NULL,  -- 更新者
  update_time TEXT NOT NULL,  -- 更新时间
  extended_id TEXT,  -- 扩展编号
  version TEXT NOT NULL,  -- 版本号
  tenant_id TEXT NOT NULL,  -- 租户编号
  client_id TEXT NOT NULL  -- 客户端编号
);
"""

# base.ap_user —— 系统用户信息表（原型 o_sys_user，37 字段）
AP_USER_DDL = """
CREATE TABLE ap_user (
  user_id TEXT NOT NULL,  -- 主键
  user_num TEXT NOT NULL,  -- 用户编号
  real_name TEXT NOT NULL,  -- 用户名
  login_name TEXT NOT NULL,  -- 用户登录名
  password TEXT NOT NULL,  -- 密码
  salt TEXT NOT NULL,  -- 盐
  status_code TEXT NOT NULL,  -- 状态STATUS:无效0/有效1
  sex_code TEXT NOT NULL,  -- 性别(SEX:男1女2)
  cert_type_code TEXT NOT NULL,  -- 证件类型(CERTIFICATE_TYPE:身份证0学生证1工作证2士兵证3军官证4护照5)
  cert_no TEXT NOT NULL,  -- 证件号码
  qq TEXT NOT NULL,  -- QQ
  wechat TEXT NOT NULL,  -- 微信
  telephone TEXT NOT NULL,  -- 固定电话
  mobile TEXT NOT NULL,  -- 手机号
  email TEXT NOT NULL,  -- 邮箱
  fax TEXT NOT NULL,  -- 传真
  pass_error_count INTEGER NOT NULL,  -- 密码错误次数
  login_succ_count INTEGER NOT NULL,  -- 登录成功次数
  lock_time TEXT NOT NULL,  -- 锁定时间
  remark TEXT NOT NULL,  -- 备注
  province TEXT NOT NULL,  -- 省级
  city TEXT NOT NULL,  -- 城市级
  district TEXT NOT NULL,  -- 区域级
  address TEXT NOT NULL,  -- 地址
  client_id TEXT NOT NULL,  -- 客户端编号
  client_name TEXT NOT NULL,  -- 客户端名称
  create_time TEXT NOT NULL,  -- 创建时间
  create_user TEXT NOT NULL,  -- 创建人
  update_time TEXT NOT NULL,  -- 更新时间
  update_user TEXT NOT NULL,  -- 更新人
  extended_id TEXT,  -- 扩展编号
  del_ind INTEGER NOT NULL,  -- 删除标志
  version TEXT NOT NULL,  -- 版本号
  tenant_id TEXT NOT NULL,  -- 租户编号
  last_login_time TEXT NOT NULL,  -- 上次登录时间
  grayscale_version TEXT NOT NULL,  -- 灰度版本号
  cipher TEXT NOT NULL  -- 密码摘要（占位，冗余保留）
);
"""

# base.ap_biz_dict —— 业务字典表（原型 erms_dict_biz，19 字段）
AP_BIZ_DICT_DDL = """
CREATE TABLE ap_biz_dict (
  biz_dict_id TEXT NOT NULL,  -- 主键
  tenant_id TEXT NOT NULL,  -- 租户ID
  parent_id TEXT NOT NULL,  -- 父主键
  code TEXT NOT NULL,  -- 字典码
  dict_key TEXT NOT NULL,  -- 字典值
  dict_value TEXT NOT NULL,  -- 字典名称
  sort_no INTEGER NOT NULL,  -- 排序
  remark TEXT NOT NULL,  -- 字典备注
  is_sealed INTEGER NOT NULL,  -- 是否已封存
  is_deleted INTEGER NOT NULL,  -- 是否已删除
  system_code TEXT NOT NULL,  -- 子系统编号
  extension_1 TEXT,  -- 扩展字段1
  extension_2 TEXT,  -- 扩展字段2
  extension_3 TEXT,  -- 扩展字段3
  extension_4 TEXT,  -- 扩展字段4
  extension_5 TEXT,  -- 扩展字段5
  dictionary_type TEXT NOT NULL,  -- 字典类型
  data_source_id TEXT NOT NULL,  -- 数据源
  sql_sentence TEXT  -- sql语句
);
"""

RISK_EXT_DDL_2: dict[str, str] = {
    "concentration.ap_concentration_limit_adj": AP_CONCENTRATION_LIMIT_ADJ_DDL,
    "concentration.ap_concentration_warn_adj": AP_CONCENTRATION_WARN_ADJ_DDL,
    "concentration.ap_codebt_customer": AP_CODEBT_CUSTOMER_DDL,
    "concentration.ap_codebt_warn_score": AP_CODEBT_WARN_SCORE_DDL,
    "approval.ap_approve_oper_log": AP_APPROVE_OPER_LOG_DDL,
    "approval.ap_approve_warn_rel": AP_APPROVE_WARN_REL_DDL,
    "approval.ap_approve_todo": AP_APPROVE_TODO_DDL,
    "project.ap_cust_query_log": AP_CUST_QUERY_LOG_DDL,
    "project.ap_serial_counter": AP_SERIAL_COUNTER_DDL,
    "base.ap_metric_std": AP_METRIC_STD_DDL,
    "base.ap_dim_rank": AP_DIM_RANK_DDL,
    "base.ap_custom_param": AP_CUSTOM_PARAM_DDL,
    "base.ap_preference_file": AP_PREFERENCE_FILE_DDL,
    "base.ap_supervise_opinion": AP_SUPERVISE_OPINION_DDL,
    "base.ap_top_query_log": AP_TOP_QUERY_LOG_DDL,
    "base.ap_data_dict": AP_DATA_DICT_DDL,
    "base.ap_sys_param": AP_SYS_PARAM_DDL,
    "base.ap_org": AP_ORG_DDL,
    "base.ap_user": AP_USER_DDL,
    "base.ap_biz_dict": AP_BIZ_DICT_DDL,
}
