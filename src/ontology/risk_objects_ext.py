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


class CustomerRelation(BaseModel):
    """客户关系表（切片）。PK/Title = customer_relation_id（源 o_a_erms_cust_relation）。"""

    customer_relation_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    upstream_update_time: datetime = own(OWN_SOURCE, "更新时间（上游）")
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称")
    cert_type_code: str = own(OWN_SOURCE, "客户证件类型")
    cert_no: str = own(OWN_SOURCE, "客户证件号（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    internal_customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    group_cert_type_code: str = own(OWN_SOURCE, "集团客户证件类型")
    group_cert_no: str = own(OWN_SOURCE, "集团客户证件号（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    data_source: str = own(OWN_SOURCE, "数据来源")
    operate_type: str = own(OWN_SOURCE, "操作类型")
    clear_remark_1: str = own(OWN_SOURCE, "备注1（占位，语义不明）")
    clear_remark_2: str = own(OWN_SOURCE, "备注2（占位，语义不明）")
    clear_remark_3: str = own(OWN_SOURCE, "备注3（占位，语义不明）")
    clear_remark_4: str = own(OWN_SOURCE, "备注4（占位，语义不明）")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    create_org_no: str = own(OWN_SOURCE, "创建机构")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_org_no: str = own(OWN_SOURCE, "更新机构")
    version: str = own(OWN_SOURCE, "框架版本号")
    tenant_id: str = own(OWN_SOURCE, "多实体标识")


class CustomerRelationTree(BaseModel):
    """客户关系树（应用写入）。PK/Title = customer_relation_tree_id（源 o_a_erms_cust_relation_opt）。"""

    customer_relation_tree_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    upstream_update_time: datetime = own(OWN_SOURCE, "更新时间（上游）")
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称")
    cert_type_code: str = own(OWN_SOURCE, "客户证件类型")
    cert_no: str = own(OWN_SOURCE, "客户证件号（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    internal_customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    group_cert_type_code: str = own(OWN_SOURCE, "集团客户证件类型")
    group_cert_no: str = own(OWN_SOURCE, "集团客户证件号（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    data_source: str = own(OWN_SOURCE, "数据来源")
    clear_remark_1: str = own(OWN_SOURCE, "备注1（占位，语义不明）")
    clear_remark_2: str = own(OWN_SOURCE, "备注2（占位，语义不明）")
    clear_remark_3: str = own(OWN_SOURCE, "备注3（占位，语义不明）")
    clear_remark_4: str = own(OWN_SOURCE, "备注4（占位，语义不明）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    create_org_no: str = own(OWN_SOURCE, "创建机构")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_org_no: str = own(OWN_SOURCE, "更新机构")
    is_important_group_customer: int = own(OWN_SOURCE, "重要集团客户标识")
    effective_date: date = own(OWN_SOURCE, "生效日期")
    invalid_date: date = own(OWN_SOURCE, "失效日期")
    current_status: str = own(OWN_SOURCE, "当前状态")
    cert_type_code_from_bank: str = own(
        OWN_SOURCE, "客户证件类型(来源为银行报送的关系树)"
    )
    cert_no_from_bank: str = own(
        OWN_SOURCE, "客户证件号(来源为银行报送的关系树)（脱敏）"
    )


class ImportantCustomerList(BaseModel):
    """重要客户名单管理表。PK/Title = important_customer_id（源 o_a_erms_cust_list）。"""

    important_customer_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    group_customer_name: str = own(OWN_SOURCE, "集团客户名称（脱敏）")
    important_customer_flag: int = own(OWN_SOURCE, "大额客户标识")
    risk_customer_flag: int = own(OWN_SOURCE, "大额风险客户标识")
    custom_customer_flag: int = own(OWN_SOURCE, "自定义客户标识")
    status: str = own(OWN_SOURCE, "状态")
    clear_remark_1: str = own(OWN_SOURCE, "备注1（占位，语义不明）")
    clear_remark_2: str = own(OWN_SOURCE, "备注2（占位，语义不明）")
    clear_remark_3: str = own(OWN_SOURCE, "备注3（占位，语义不明）")
    clear_remark_4: str = own(OWN_SOURCE, "备注4（占位，语义不明）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    customer_short_name: str = own(OWN_SOURCE, "客户简称（脱敏）")
    is_real_estate: int = own(OWN_SOURCE, "是否房地产")
    belong_industry: str = own(OWN_SOURCE, "所属行业")
    is_high_leverage: int = own(OWN_SOURCE, "是否高杠杆")


class Top500CustomerRisk(BaseModel):
    """前500大客户风险投融资结果表。PK/Title = top500_customer_id（源 o_a_erms_top500_cust_info）。"""

    top500_customer_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    org_id: str = own(OWN_SOURCE, "机构编码")
    customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    group_customer_no: str = own(
        OWN_SOURCE, "客户所属集团编号（FK→GroupCustomer.group_customer_no）（脱敏）"
    )
    group_customer_name: str = own(OWN_SOURCE, "客户所属集团名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    group_member_count: int = own(OWN_SOURCE, "集团成员数")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    risk_asset_balance: float = own(OWN_SOURCE, "风险类资产规模（脱敏）")
    concentration_degree: float = own(OWN_SOURCE, "集中度监测（脱敏）")
    risk_exposure_rank_no: str = own(OWN_SOURCE, "风险暴露排名")
    asset_quality_level: str = own(OWN_SOURCE, "资产质量（代码说明：A009）")
    warn_flag: int = own(OWN_SOURCE, "预警标识(1:是，0:否)")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_org_no: str = own(OWN_SOURCE, "更新机构")
    version: str = own(OWN_SOURCE, "框架版本号")
    tenant_id: str = own(OWN_SOURCE, "多实体标识")
    invest_balance_new: float = own(OWN_SOURCE, "投融资余额-新（脱敏）")


class CustomerAssets(BaseModel):
    """资产结构结果表。PK/Title = customer_assets_id（源 o_a_erms_cust_assets）。"""

    customer_assets_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称")
    customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    business_type_code: str = own(OWN_SOURCE, "业务类型代码")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    risk_asset_balance: float = own(OWN_SOURCE, "不良余额（脱敏）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_org_no: str = own(OWN_SOURCE, "更新机构")
    version: str = own(OWN_SOURCE, "框架版本号")
    tenant_id: str = own(OWN_SOURCE, "多实体标识")
    invest_balance_new: float = own(OWN_SOURCE, "投融资余额-新（脱敏）")


class InvestDistribution(BaseModel):
    """投资分布结果表。PK/Title = customer_invest_dist_id（源 o_a_erms_cust_sub_org_invest）。"""

    customer_invest_dist_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    org_id: str = own(OWN_SOURCE, "机构编号")
    org_name: str = own(OWN_SOURCE, "机构名称")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    risk_asset_balance: float = own(OWN_SOURCE, "不良余额（脱敏）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    update_org_no: str = own(OWN_SOURCE, "更新机构")
    version: str = own(OWN_SOURCE, "框架版本号")
    tenant_id: str = own(OWN_SOURCE, "多实体标识")
    risk_bad_balance: float = own(OWN_SOURCE, "不良风险暴露余额（脱敏）")
    invest_balance_new: float = own(OWN_SOURCE, "全口径投融资业务余额（脱敏）")


class SubsidiaryCreditDetail(BaseModel):
    """集团加工后子公司明细表。PK/Title = project_id（源 o_a_erms_credit_detail_1）。"""

    project_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    upstream_update_time: datetime = own(OWN_SOURCE, "更新时间（上游）")
    org_id: str = own(OWN_SOURCE, "机构编码")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    project_name: str = own(OWN_SOURCE, "项目名称（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "客户所属集团名称（脱敏）")
    group_customer_name_processed: str = own(
        OWN_SOURCE, "集团加工的所属集团名称（脱敏）"
    )
    group_peer_flag: int = own(OWN_SOURCE, "集团客户同业标识")
    cert_type_code: str = own(OWN_SOURCE, "客户证件类型代码")
    cert_type: str = own(OWN_SOURCE, "客户证件类型名称")
    cert_no: str = own(OWN_SOURCE, "客户证件号码（脱敏）")
    internal_customer_no: str = own(
        OWN_SOURCE, "内部客户号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    internal_level: str = own(OWN_SOURCE, "客户内部评级")
    external_level: str = own(OWN_SOURCE, "客户外部评级")
    zone_id: str = own(OWN_SOURCE, "区域（境内）代码")
    zone_name: str = own(OWN_SOURCE, "区域（境内）名称")
    zone_level: str = own(OWN_SOURCE, "区域评级")
    country_id: str = own(OWN_SOURCE, "区域（境外）代码")
    country_name: str = own(OWN_SOURCE, "区域（境外）名称")
    industry_id: str = own(OWN_SOURCE, "行业代码")
    industry_name: str = own(OWN_SOURCE, "行业名称")
    industry_level: str = own(OWN_SOURCE, "行业评级")
    related_party_ind: int = own(OWN_SOURCE, "关联方标识")
    peer_flag: int = own(OWN_SOURCE, "单一客户同业标识")
    enterprise_nature_code: str = own(OWN_SOURCE, "企业性质代码")
    enterprise_nature: str = own(OWN_SOURCE, "企业性质")
    enterprise_scale: str = own(OWN_SOURCE, "企业规模")
    establish_time: datetime = own(OWN_SOURCE, "成立时间")
    registered_capital: float = own(OWN_SOURCE, "注册资本（脱敏）")
    business_type_code: str = own(OWN_SOURCE, "业务类型代码")
    business_type: str = own(OWN_SOURCE, "业务类型名称")
    business_product_code: str = own(OWN_SOURCE, "业务品种代码")
    business_product_name: str = own(OWN_SOURCE, "业务品种名称")
    internal_business_product_code: str = own(OWN_SOURCE, "内部业务品种代码")
    internal_business_product_name: str = own(OWN_SOURCE, "内部业务品种名称")
    currency_id: str = own(OWN_SOURCE, "币种代码")
    index_unit: str = own(OWN_SOURCE, "单位")
    business_balance: float = own(OWN_SOURCE, "投融资业务余额（脱敏）")
    risk_exposure: float = own(OWN_SOURCE, "风险暴露（脱敏）")
    pledge_value: float = own(OWN_SOURCE, "合格抵质押金额（脱敏）")
    guarantee_value: float = own(OWN_SOURCE, "合格保证金额（脱敏）")
    impairment_provision: float = own(OWN_SOURCE, "已计提减值（脱敏）")
    principal_overdue_days: int = own(OWN_SOURCE, "本金逾期天数")
    interest_overdue_days: int = own(OWN_SOURCE, "利息逾期天数")
    asset_quality_level_code: str = own(OWN_SOURCE, "资产质量分类代码")
    asset_quality_level: str = own(OWN_SOURCE, "资产质量分类名称")
    limit_value: float = own(OWN_SOURCE, "限额（脱敏）")
    shareholder_name_1: str = own(OWN_SOURCE, "第一大股东（脱敏）")
    shareholder_ratio_1: float = own(OWN_SOURCE, "第一大股东出资比例")
    shareholder_name_2: str = own(OWN_SOURCE, "第二大股东（脱敏）")
    shareholder_ratio_2: float = own(OWN_SOURCE, "第二大股东出资比例")
    shareholder_name_3: str = own(OWN_SOURCE, "第三大股东（脱敏）")
    shareholder_ratio_3: float = own(OWN_SOURCE, "第三大股东出资比例")
    chairman_name: str = own(OWN_SOURCE, "董事长（脱敏）")
    supervisor_name: str = own(OWN_SOURCE, "监事长（脱敏）")
    finance_head_name: str = own(OWN_SOURCE, "财务负责人（脱敏）")
    general_manager_name: str = own(OWN_SOURCE, "总经理（脱敏）")
    invest_company_1: str = own(OWN_SOURCE, "对外投资公司1（脱敏）")
    invest_amount_1: float = own(OWN_SOURCE, "投资金额1(万元)（脱敏）")
    invest_currency_name_1: str = own(OWN_SOURCE, "投资币种名称1")
    invest_ratio_1: float = own(OWN_SOURCE, "出资比例1")
    invest_company_2: str = own(OWN_SOURCE, "对外投资公司2（脱敏）")
    invest_amount_2: float = own(OWN_SOURCE, "投资金额2(万元)（脱敏）")
    invest_currency_name_2: str = own(OWN_SOURCE, "投资币种名称2")
    invest_ratio_2: float = own(OWN_SOURCE, "出资比例2")
    invest_company_3: str = own(OWN_SOURCE, "对外投资公司3（脱敏）")
    invest_amount_3: float = own(OWN_SOURCE, "投资金额3(万元)（脱敏）")
    invest_currency_name_3: str = own(OWN_SOURCE, "投资币种名称3")
    invest_ratio_3: float = own(OWN_SOURCE, "出资比例3")
    customer_status: str = own(OWN_SOURCE, "客户状态")
    final_score: float = own(OWN_SOURCE, "最终模型分数（含预警）")
    final_score_level: str = own(OWN_SOURCE, "客户最终评级")
    industry_commerce_score_level: str = own(OWN_SOURCE, "工商子模型等级")
    trading_score_level: str = own(OWN_SOURCE, "交易子模型等级")
    credit_score_level: str = own(OWN_SOURCE, "信贷子模型等级")
    credit_reference_score_level: str = own(OWN_SOURCE, "征信子模型等级")
    financial_score_level: str = own(OWN_SOURCE, "财务子模型等级")
    industry_commerce_index: float = own(OWN_SOURCE, "工商模型有效指数")
    trading_index: float = own(OWN_SOURCE, "交易模型有效指数")
    credit_index: float = own(OWN_SOURCE, "信贷模型有效指数")
    credit_reference_index: float = own(OWN_SOURCE, "征信模型有效指数")
    financial_index: float = own(OWN_SOURCE, "财务模型有效指数")
    operate_type: str = own(OWN_SOURCE, "操作类型")
    clear_remark_1: str = own(OWN_SOURCE, "备注1（占位，语义不明）")
    clear_remark_2: str = own(OWN_SOURCE, "备注2（占位，语义不明）")
    clear_remark_3: str = own(OWN_SOURCE, "备注3（占位，语义不明）")
    clear_remark_4: str = own(OWN_SOURCE, "备注4（占位，语义不明）")


class BankPledgeDetail(BaseModel):
    """押品明细（银行业）。PK/Title = bank_pledge_id（源 o_a_erms_pledge_bankdetail）。"""

    bank_pledge_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期（报送）")
    org_id: str = own(OWN_SOURCE, "机构编号")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    project_id: str = own(OWN_SOURCE, "项目编号")
    project_name: str = own(OWN_SOURCE, "项目名称（脱敏）")
    customer_credit_code: str = own(OWN_SOURCE, "客户统一社会信用代码（脱敏）")
    customer_name: str = own(OWN_SOURCE, "单一客户名称（脱敏）")
    group_customer_name: str = own(OWN_SOURCE, "客户所属集团名称（脱敏）")
    business_product_code: str = own(OWN_SOURCE, "金控层级业务类型代码")
    business_product_name: str = own(OWN_SOURCE, "金控层级业务类型名称")
    guarantee_contract_id: str = own(OWN_SOURCE, "担保合同编号")
    guarantee_contract_name: str = own(OWN_SOURCE, "担保合同名称（脱敏）")
    guarantee_contract_amount: float = own(OWN_SOURCE, "担保合同金额（脱敏）")
    guarantee_contract_balance: float = own(OWN_SOURCE, "担保合同余额（脱敏）")
    internal_pledge_no: str = own(OWN_SOURCE, "内部押品编码")
    pledge_name: str = own(OWN_SOURCE, "抵质押物名称（脱敏）")
    guarantee_repay_order: int = own(OWN_SOURCE, "担保清偿顺位")
    mortgage_ind: int = own(OWN_SOURCE, "抵质押标识")
    mortgage_property_type: str = own(OWN_SOURCE, "抵质押物类型")
    internal_mortgage_property_type: str = own(OWN_SOURCE, "内部抵质押物类型")
    is_have_external_estimate_org: int = own(OWN_SOURCE, "是否有外部评估机构")
    pledge_location: str = own(OWN_SOURCE, "抵押物位置（脱敏）")
    estimate_org_name: str = own(OWN_SOURCE, "评估机构名称（脱敏）")
    initial_estimate_value: float = own(OWN_SOURCE, "初始评估价值（脱敏）")
    initial_estimate_date: date = own(OWN_SOURCE, "初始评估日期")
    latest_estimate_value: float = own(OWN_SOURCE, "最新评估价值（脱敏）")
    latest_estimate_date: date = own(OWN_SOURCE, "评估日期")
    disposal_value: float = own(OWN_SOURCE, "处置价值（脱敏）")
    disposal_date: date = own(OWN_SOURCE, "处置日期")
    mortgaged_value: float = own(OWN_SOURCE, "已抵押价值（脱敏）")
    mortgage_rate: float = own(OWN_SOURCE, "抵质押率")
    maintenance_rate: float = own(OWN_SOURCE, "维保比")
    owner_name: str = own(OWN_SOURCE, "抵质押物所有权人名称（脱敏）")
    owner_cert_type: str = own(OWN_SOURCE, "抵质押物所有人证件类型")
    owner_cert_no: str = own(OWN_SOURCE, "抵质押物所有人证件号码（脱敏）")
    warrant_no: str = own(OWN_SOURCE, "权证号（脱敏）")
    is_mortgage_registered: int = own(OWN_SOURCE, "是否办理抵押登记")
    register_date: date = own(OWN_SOURCE, "登记日期")
    right_register_org_name: str = own(OWN_SOURCE, "权利登记机构名称（脱敏）")
    register_org_credit_code: str = own(OWN_SOURCE, "登记机构统一社会信用代码（脱敏）")
    pledge_status: str = own(OWN_SOURCE, "押品状态")
    biz_date: date = own(OWN_SOURCE, "业务日期(网关自动填充)")
    company_partition: str = own(OWN_SOURCE, "公司划分(网关自动填充)")


class SecuritiesPledgeDetail(BaseModel):
    """押品明细（证券业）。PK/Title = securities_pledge_id（源 o_a_erms_pledge_securitiesdetail）。"""

    securities_pledge_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据期次")
    org_id: str = own(OWN_SOURCE, "填报机构id")
    org_name: str = own(OWN_SOURCE, "填报机构名称（脱敏）")
    ecif_no: str = own(OWN_SOURCE, "客户ECF编码")
    customer_credit_code: str = own(OWN_SOURCE, "客户统一社会信用代码（脱敏）")
    customer_name: str = own(OWN_SOURCE, "单一客户名称（脱敏）")
    business_product_code: str = own(OWN_SOURCE, "金控层级业务类型代码")
    business_product_name: str = own(OWN_SOURCE, "金控层级业务类型名称")
    invest_value: float = own(OWN_SOURCE, "融资规模(元)（脱敏）")
    pledge_subject_code: str = own(OWN_SOURCE, "质押标的证券代码")
    pledge_subject_name: str = own(OWN_SOURCE, "质押标的证券名称（脱敏）")
    pledge_subject_value: float = own(OWN_SOURCE, "质押标的证券市值(元)（脱敏）")
    bonus_amount: float = own(OWN_SOURCE, "质押红利金额(元)（脱敏）")
    maintenance_rate: float = own(OWN_SOURCE, "维保比")
    pledge_status: str = own(OWN_SOURCE, "押品状态")
    biz_date: date = own(OWN_SOURCE, "业务日期(网关自动填充)")
    company_partition: str = own(OWN_SOURCE, "公司划分(网关自动填充)")
    partition_date: date = own(OWN_SOURCE, "分区统计日期")


class SubsidiaryMortgage(BaseModel):
    """子公司抵质押物信息。PK/Title = subsidiary_mortgage_id（源 o_a_erms_org_mrtg_prop_info）。"""

    subsidiary_mortgage_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    org_id: str = own(OWN_SOURCE, "机构id")
    org_name: str = own(OWN_SOURCE, "机构名称（脱敏）")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    customer_type: str = own(OWN_SOURCE, "客户类型")
    mortgage_ind: int = own(OWN_SOURCE, "抵质押标识")
    total_count: int = own(OWN_SOURCE, "总数")
    estimate_value: float = own(OWN_SOURCE, "评估价值（脱敏）")
    corp_identify_value: float = own(OWN_SOURCE, "公司认定价值（脱敏）")
    mortgaged_value: float = own(OWN_SOURCE, "已抵押价值（脱敏）")
    estimate_quantity: int = own(OWN_SOURCE, "近两年评估数量")
    percent_value: float = own(OWN_SOURCE, "占比")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")
    clear_remark_1: str = own(OWN_SOURCE, "备注1（占位，语义不明）")
    clear_remark_2: str = own(OWN_SOURCE, "备注2（占位，语义不明）")


class WarningPush(BaseModel):
    """预警推送表。PK/Title = warning_push_id（源 o_a_erms_cust_warn_sgn_push）。"""

    warning_push_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    warning_id: str = own(OWN_SOURCE, "预警ID（FK→WarningSignal.warning_id）")
    push_warn_reason: str = own(OWN_SOURCE, "推送预警事由（脱敏）")
    push_person: str = own(OWN_SOURCE, "推送人（脱敏）")
    push_time: datetime = own(OWN_SOURCE, "推送时间")
    receive_person: str = own(OWN_SOURCE, "接收人（脱敏）")
    receive_instruction: str = own(OWN_SOURCE, "接收批示（脱敏）")
    receive_time: datetime = own(OWN_SOURCE, "接收时间")


class CoDebtScore(BaseModel):
    """共债客户风险预警评分表。PK/Title = codebt_warn_score_id（源 p_erms_codebt_cust_warn_score）。"""

    codebt_warn_score_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    data_date: date = own(OWN_SOURCE, "数据日期")
    signal_generate_date: date = own(OWN_SOURCE, "预警信号生成日期")
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    customer_type: Literal["01", "02"] = own(
        OWN_SOURCE, "客户类型 01 单一客户，02集团客户"
    )
    risk_exposure: float = own(OWN_SOURCE, "风险暴露额（脱敏）")
    invest_balance: float = own(OWN_SOURCE, "投融资余额（脱敏）")
    industry_id: str = own(OWN_SOURCE, "客户所属行业ID")
    industry_name: str = own(OWN_SOURCE, "行业名称")
    warn_level: str = own(OWN_SOURCE, "预警信号等级")
    signal_level2_topic: str = own(OWN_SOURCE, "预警信号二级主题")
    signal_count: int = own(OWN_SOURCE, "有效信号个数")
    red_signal_count: int = own(OWN_SOURCE, "红色信号个数")
    blue_signal_count: int = own(OWN_SOURCE, "蓝色信号个数")
    yellow_signal_count: int = own(OWN_SOURCE, "黄色信号个数")
    subsidiary_count: int = own(OWN_SOURCE, "子公司数量")
    top10_risk_exposure_avg: float = own(OWN_SOURCE, "集团前10大客户平均风险暴露")
    score: float = own(OWN_SOURCE, "得分")
    calc_detail: str = own(OWN_SOURCE, "计算过程（脱敏）")
    create_time: datetime = own(OWN_SOURCE, "创建时间")


class ConcentrationLimitAdj(BaseModel):
    """集中度限额调整表。PK/Title = concentration_limit_adj_id（源 o_a_erms_larg_cust_limit_adj）。"""

    concentration_limit_adj_id: str = own(OWN_SOURCE, "主键ID（PK/Title）")
    concentration_limit_id: str = own(
        OWN_SOURCE, "集中度限额编号（FK→ConcentrationLimit.concentration_limit_id）"
    )
    customer_no: str = own(
        OWN_SOURCE, "客户编号（FK→RiskCustomer.customer_no）（脱敏）"
    )
    customer_name: str = own(OWN_SOURCE, "客户名称（脱敏）")
    concentration_limit: float = own(OWN_SOURCE, "集中度限额（脱敏）")
    concentration_limit_old: str = own(OWN_SOURCE, "集中度限额-更新前的值（脱敏）")
    current_status: str = own(OWN_SOURCE, "集团限额维护-状态")
    approve_status: str = own(OWN_SOURCE, "审批状态")
    approve_comment: str = own(OWN_SOURCE, "审批意见（脱敏）")
    create_user: str = own(OWN_SOURCE, "创建人")
    create_time: datetime = own(OWN_SOURCE, "创建时间")
    update_user: str = own(OWN_SOURCE, "更新人")
    update_time: datetime = own(OWN_SOURCE, "更新时间")


RISK_OBJECT_TYPES_EXT_1: list[ObjectTypeDef] = [
    ObjectTypeDef(
        name="CustomerRelation",
        api_name="customer_relation",
        description="CustomerRelation（客户关系表（切片），源 o_a_erms_cust_relation）",
        model=CustomerRelation,
        pk_field="customer_relation_id",
        title_field="customer_relation_id",
        source_table="o_a_erms_cust_relation",
    ),
    ObjectTypeDef(
        name="CustomerRelationTree",
        api_name="customer_relation_tree",
        description="CustomerRelationTree（客户关系树（应用写入），源 o_a_erms_cust_relation_opt）",
        model=CustomerRelationTree,
        pk_field="customer_relation_tree_id",
        title_field="customer_relation_tree_id",
        source_table="o_a_erms_cust_relation_opt",
    ),
    ObjectTypeDef(
        name="ImportantCustomerList",
        api_name="important_customer_list",
        description="ImportantCustomerList（重要客户名单管理表，源 o_a_erms_cust_list）",
        model=ImportantCustomerList,
        pk_field="important_customer_id",
        title_field="important_customer_id",
        source_table="o_a_erms_cust_list",
    ),
    ObjectTypeDef(
        name="Top500CustomerRisk",
        api_name="top500_customer_risk",
        description="Top500CustomerRisk（前500大客户风险投融资结果表，源 o_a_erms_top500_cust_info）",
        model=Top500CustomerRisk,
        pk_field="top500_customer_id",
        title_field="top500_customer_id",
        source_table="o_a_erms_top500_cust_info",
    ),
    ObjectTypeDef(
        name="CustomerAssets",
        api_name="customer_assets",
        description="CustomerAssets（资产结构结果表，源 o_a_erms_cust_assets）",
        model=CustomerAssets,
        pk_field="customer_assets_id",
        title_field="customer_assets_id",
        source_table="o_a_erms_cust_assets",
    ),
    ObjectTypeDef(
        name="InvestDistribution",
        api_name="invest_distribution",
        description="InvestDistribution（投资分布结果表，源 o_a_erms_cust_sub_org_invest）",
        model=InvestDistribution,
        pk_field="customer_invest_dist_id",
        title_field="customer_invest_dist_id",
        source_table="o_a_erms_cust_sub_org_invest",
    ),
    ObjectTypeDef(
        name="SubsidiaryCreditDetail",
        api_name="subsidiary_credit_detail",
        description="SubsidiaryCreditDetail（集团加工后子公司明细表，源 o_a_erms_credit_detail_1）",
        model=SubsidiaryCreditDetail,
        pk_field="project_id",
        title_field="project_id",
        source_table="o_a_erms_credit_detail_1",
    ),
    ObjectTypeDef(
        name="BankPledgeDetail",
        api_name="bank_pledge_detail",
        description="BankPledgeDetail（押品明细（银行业），源 o_a_erms_pledge_bankdetail）",
        model=BankPledgeDetail,
        pk_field="bank_pledge_id",
        title_field="bank_pledge_id",
        source_table="o_a_erms_pledge_bankdetail",
    ),
    ObjectTypeDef(
        name="SecuritiesPledgeDetail",
        api_name="securities_pledge_detail",
        description="SecuritiesPledgeDetail（押品明细（证券业），源 o_a_erms_pledge_securitiesdetail）",
        model=SecuritiesPledgeDetail,
        pk_field="securities_pledge_id",
        title_field="securities_pledge_id",
        source_table="o_a_erms_pledge_securitiesdetail",
    ),
    ObjectTypeDef(
        name="SubsidiaryMortgage",
        api_name="subsidiary_mortgage",
        description="SubsidiaryMortgage（子公司抵质押物信息，源 o_a_erms_org_mrtg_prop_info）",
        model=SubsidiaryMortgage,
        pk_field="subsidiary_mortgage_id",
        title_field="subsidiary_mortgage_id",
        source_table="o_a_erms_org_mrtg_prop_info",
    ),
    ObjectTypeDef(
        name="WarningPush",
        api_name="warning_push",
        description="WarningPush（预警推送表，源 o_a_erms_cust_warn_sgn_push）",
        model=WarningPush,
        pk_field="warning_push_id",
        title_field="warning_push_id",
        source_table="o_a_erms_cust_warn_sgn_push",
    ),
    ObjectTypeDef(
        name="CoDebtScore",
        api_name="codebt_score",
        description="CoDebtScore（共债客户风险预警评分表，源 p_erms_codebt_cust_warn_score）",
        model=CoDebtScore,
        pk_field="codebt_warn_score_id",
        title_field="codebt_warn_score_id",
        source_table="p_erms_codebt_cust_warn_score",
    ),
    ObjectTypeDef(
        name="ConcentrationLimitAdj",
        api_name="concentration_limit_adj",
        description="ConcentrationLimitAdj（集中度限额调整表，源 o_a_erms_larg_cust_limit_adj）",
        model=ConcentrationLimitAdj,
        pk_field="concentration_limit_adj_id",
        title_field="concentration_limit_adj_id",
        source_table="o_a_erms_larg_cust_limit_adj",
    ),
]
