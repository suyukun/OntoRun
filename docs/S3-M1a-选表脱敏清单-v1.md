# S3 M1a 选表清单 + 脱敏映射（v1 草案）

> 依据：数据字典.xlsx 211 张表完整目录 + 业务链路还原。
> 选表原则：只选"业务数据表"（贴源层 34 + 应用层业务 19 + 业务字典 1 = 54 张），
> 排除技术底座（流程引擎 30 act_* / 决策引擎 91 rules_* / 系统管理 20 sys_* / Quartz 13 qrtz_* / 应用开发 dev_* / flw_*）。
> 脱敏规则（Jack 拍板）：语义保留 + 名称全改；表名 ap_ 前缀；组织/库/表名看不出原型。

## 一、贴源层 34 张（o_a_erms_* / o_base_* / o_sys_*）

### 客户域（核心）
| 原名 | 中文名 | 脱敏名 | 链路角色 |
|---|---|---|---|
| o_a_erms_cust_info | 单一客户基本信息表 | ap_customer | 主数据：客户 |
| o_a_erms_grp_cust_info | 集团客户基本信息表 | ap_group_customer | 主数据：集团客户 |
| o_a_erms_cust_relation | 客户关系表（切片） | ap_customer_relation | 客户间关系 |
| o_a_erms_cust_relation_opt | 客户关系树（应用写入） | ap_customer_relation_tree | 关系树 |
| o_a_erms_cust_list | 重要客户名单管理表 | ap_important_customer_list | 名单管理 |
| o_a_erms_top500_cust_info | 前500大客户风险投融资结果表 | ap_top500_customer_risk | 大客户风险 |

### 资产/投融资域
| o_a_erms_cust_assets | 资产结构结果表 | ap_customer_assets | 客户资产结构 |
| o_a_erms_cust_sub_org_invest | 投资分布结果表 | ap_customer_invest_dist | 投资分布 |
| o_a_erms_credit_detail_1 | 集团加工后子公司明细表 | ap_subsidiary_credit_detail | 子公司授信明细 |

### 预警域（核心）
| o_a_erms_cust_warn_sgn | 客户预警信号表 | ap_warning_signal | **预警信号（主表）** |
| o_a_erms_cust_warn_sgn_disp | 预警处置信息表 | ap_warning_disposal | 预警处置 |
| o_a_erms_cust_warn_sgn_push | 预警推送表 | ap_warning_push | 预警推送 |

### 集中度/限额域（核心）
| o_a_erms_larg_cust_limit | 大额客户集中度限额表 | ap_concentration_limit | 集中度限额 |
| o_a_erms_larg_cust_limit_adj | 集中度限额调整表 | ap_concentration_limit_adj | 限额调整 |
| o_a_erms_larg_cust_warn_adj | 集中度预警调整表 | ap_concentration_warn_adj | 集中度预警调整 |

### 押品域
| o_a_erms_negot_info | 押品信息表 | ap_collateral | 押品 |
| o_a_erms_org_mrtg_prop_info | 子公司抵质押物信息 | ap_subsidiary_mortgage | 子公司押品 |
| o_a_erms_pledge_bankdetail | 押品明细（银行业） | ap_bank_pledge_detail | 银行押品 |
| o_a_erms_pledge_securitiesdetail | 押品明细（证券业） | ap_securities_pledge_detail | 证券押品 |

### 合规/审计域
| o_a_erms_audit_detail | 合规内控审计记录表 | ap_audit_detail | 审计 |
| o_a_erms_compliance_risk_ledger | 潜在合规风险摸排台账 | ap_compliance_risk_ledger | 合规台账 |
| o_a_erms_compliance_risk_ledger_tmp | 合规风险摸排台账(tmp) | ap_compliance_risk_ledger_tmp | 合规台账临时 |
| o_a_erms_custd_pnsh | 监管处罚记录表 | ap_regulatory_penalty | 监管处罚 |

### 指标/排名域（核心，ChatBI 底座）
| o_a_erms_comb_dim_index | 组合维度指标表 | ap_dim_metric | **指标库（主表）** |
| o_a_erms_index_list_std | 标准化指标信息表（切片） | ap_metric_std | 指标标准 |
| o_a_erms_dim_rank | 分维度排名信息表 | ap_dim_rank | 维度排名 |

### 其他/支撑
| o_a_erms_custom_param | 自定义参数表 | ap_custom_param | 参数 |
| o_a_erms_pref_info_file_tab | 偏好陈述信息附件表 | ap_preference_file | 附件 |
| o_a_erms_supervise_opinion_classify | 监管意见分类展示 | ap_supervise_opinion | 监管意见 |
| o_a_erms_top_query_log | 客户查询历史记录表 | ap_top_query_log | 查询日志 |
| o_base_ddct | 数据字典 | ap_data_dict | 字典 |
| o_base_stm_parm | 系统参数 | ap_sys_param | 参数 |
| o_sys_organization | 系统机构表 | ap_org | **机构** |
| o_sys_user | 系统用户信息表 | ap_user | **用户** |

## 二、应用层业务 19 张（p_erms_* / p_serial_*）

### 审批域（核心）
| p_erms_approve_node | 审批节点定义表 | ap_approve_node | 审批节点配置 |
| p_erms_approve_oper_log | 审批操作日志表 | ap_approve_oper_log | 审批日志 |
| p_erms_approve_order | 审批单表 | ap_approve_order | **审批单（主表）** |
| p_erms_approve_order_warn_rel | 审批单预警信号关联表 | ap_approve_warn_rel | 审批-预警关联 |
| p_erms_approve_task | 审批节点任务表（岗位级） | ap_approve_task | 审批任务 |
| p_erms_approve_todo | 用户待办任务表 | ap_approve_todo | 待办 |

### 共债域
| p_erms_codebt_cust_info | 共债客户明细表 | ap_codebt_customer | 共债客户 |
| p_erms_codebt_cust_warn_score | 共债客户风险预警评分表 | ap_codebt_warn_score | 共债评分 |

### 预警派生域
| p_erms_cust_warn_sgn_concentration | 客户集中度预警信号表 | ap_warn_signal_concentration | 集中度预警 |
| p_erms_cust_warn_sgn_derive | 客户衍生预警信号表 | ap_warn_signal_derive | 衍生预警 |
| p_erms_cust_warn_sgn_derive_deal_detail | 衍生预警处置详情表 | ap_warn_derive_deal_detail | 衍生处置 |
| p_erms_cust_warn_sgn_derive_sub_push | 衍生预警子公司推送表 | ap_warn_derive_sub_push | 衍生推送 |
| p_erms_cust_warn_sgn_deviation | 客户背离预警信号表 | ap_warn_signal_deviation | 背离预警 |
| p_erms_deviation_cust_warn_score | 趋势背离预警评分模型结果表 | ap_deviation_warn_score | 背离评分 |

### 风险项目域（核心）
| p_erms_risk_project_info | 企业风险项目信息表 | ap_risk_project | **风险项目** |
| p_erms_sgn_deal | 业务处置表 | ap_disposal | **处置** |
| p_erms_sgn_deal_detail | 业务处置详情表 | ap_disposal_detail | 处置详情 |
| p_erms_top_query_log | 客户查询记录日志表 | ap_cust_query_log | 查询日志 |
| p_serial_number_counter | 分布式流水号计数器表 | ap_serial_counter | 流水号 |

## 三、普通业务 1 张
| erms_dict_biz | 业务字典表 | ap_biz_dict | **业务字典** |

## 汇总
- 贴源层 34 + 应用层 19 + 业务字典 1 = **54 张核心业务表**
- 覆盖域：客户/集团/资产/预警/集中度/押品/合规/指标/审批/共债/衍生/风险项目/处置/机构/用户/字典
- 演示主线（华夏新能源集团）：ap_group_customer → ap_warning_signal → ap_warning_disposal → ap_disposal → ap_approve_order → ap_risk_project

## 待办（子代理细化）
1. 每张表字段级脱敏映射（原字段→新字段名，语义保留，ap_ 对象视角）
2. 字段值脱敏规则（人名/金额/机构名/证件号）
3. 门禁校验脚本（新表名/字段名对原型 o_a_erms/p_erms 零命中）
