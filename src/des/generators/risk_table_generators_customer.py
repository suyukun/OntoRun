"""金融风控 M1b 全量补全 —— customer 系统 11 张新表行生成器（脱敏后 ap_* 表）。

依赖 risk_generators（编码/DMN 规则/共享业务池）与 risk_ddl_ext（DDL）。
每表独立 RNG 流、引用 ctx 缓存的上游表确定性输出；FK 引用真实（如 customer_no/customer_name
指向已生成的 ap_customer / ap_group_customer）。原型表名（o_a_erms_*）只在 docstring 溯源。
"""

from __future__ import annotations

import random
from typing import Any

from .risk_ddl_ext import RISK_EXT_DDL_1
from .risk_generators import (
    COLLATERAL_STATUS_POOL,
    DATA_SOURCE_POOL,
    ENTERPRISE_NATURE_POOL,
    ESTIMATE_ORG_POOL,
    INTERNAL_PRODUCT_CODE_POOL,
    ORG_POOL,
    PLEDGE_PROPERTY_POOL,
    PLEDGE_STATUS_POOL,
    PRODUCT_CODE_POOL,
    _asset_quality,
    _concentration_ratio,
    _idcard,
    _invest_block,
    _person_name,
    _row_count,
    _shareholder_block,
    _uscc,
    anping_col_no,
    collateral_val,
    concentration_calc,
    exposure_sim,
    random_date,
)


def _cust_base(rng: random.Random, cust: dict[str, Any], year: int) -> dict[str, Any]:
    """从 ap_customer 抽取共用字段块（org/证件/评级/工商/股东/投资/评分），供明细表复用。"""
    return {
        "org_id": cust["org_id"],
        "org_name": cust["org_name"],
        "cert_type_code": cust["cert_type"],
        "cert_type": cust["cert_type"],
        "cert_no": cust["cert_no"],
        "internal_customer_no": cust["internal_customer_no"],
        "internal_level": cust["internal_level"],
        "external_level": cust["external_level"],
        "zone_id": cust["zone_id"],
        "zone_name": cust["zone_name"],
        "zone_level": cust["zone_level"],
        "country_id": cust["country_id"],
        "country_name": cust["country_name"],
        "industry_id": cust["industry_id"],
        "industry_name": cust["industry_name"],
        "industry_level": cust["industry_level"],
        "related_party_ind": cust["related_party_ind"],
        "peer_flag": cust["peer_flag"],
        "enterprise_scale": cust["enterprise_scale"],
        "establish_time": cust["establish_time"],
        "registered_capital": cust["registered_capital"],
        "shareholder_name_1": cust["shareholder_name_1"],
        "shareholder_ratio_1": cust["shareholder_ratio_1"],
        "shareholder_name_2": cust["shareholder_name_2"],
        "shareholder_ratio_2": cust["shareholder_ratio_2"],
        "shareholder_name_3": cust["shareholder_name_3"],
        "shareholder_ratio_3": cust["shareholder_ratio_3"],
        "chairman_name": cust["chairman_name"],
        "supervisor_name": cust["supervisor_name"],
        "finance_head_name": cust["finance_head_name"],
        "general_manager_name": cust["general_manager_name"],
        "invest_company_1": cust["invest_company_1"],
        "invest_amount_1": cust["invest_amount_1"],
        "invest_currency_name_1": cust["invest_currency_name_1"],
        "invest_ratio_1": cust["invest_ratio_1"],
        "invest_company_2": cust["invest_company_2"],
        "invest_amount_2": cust["invest_amount_2"],
        "invest_currency_name_2": cust["invest_currency_name_2"],
        "invest_ratio_2": cust["invest_ratio_2"],
        "invest_company_3": cust["invest_company_3"],
        "invest_amount_3": cust["invest_amount_3"],
        "invest_currency_name_3": cust["invest_currency_name_3"],
        "invest_ratio_3": cust["invest_ratio_3"],
        "final_score": cust["final_score"],
        "final_score_level": cust["final_score_level"],
        "industry_commerce_score_level": cust["industry_commerce_score_level"],
        "trading_score_level": cust["trading_score_level"],
        "credit_score_level": cust["credit_score_level"],
        "credit_reference_score_level": cust["credit_reference_score_level"],
        "financial_score_level": cust["financial_score_level"],
        "industry_commerce_index": cust["industry_commerce_index"],
        "trading_index": cust["trading_index"],
        "credit_index": cust["credit_index"],
        "credit_reference_index": cust["credit_reference_index"],
        "financial_index": cust["financial_index"],
    }


def generate_ap_customer_relation_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_customer_relation 客户关系表（原型 o_a_erms_cust_relation）：客户间关系切片，
    FK internal_customer_no → ap_customer.internal_customer_no。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_customer_relation") + 1):
        cust = rng.choice(customers)
        rows.append(
            {
                "customer_relation_id": f"REL-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "upstream_update_time": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "cert_type_code": cust["cert_type"],
                "cert_no": cust["cert_no"],
                "customer_name": cust["customer_name"],
                "internal_customer_no": cust["internal_customer_no"],
                "group_cert_type_code": "统一社会信用代码",
                "group_cert_no": rng.choice(customers)["cert_no"],
                "group_customer_name": cust["group_customer_name"],
                "data_source": rng.choice(DATA_SOURCE_POOL),
                "operate_type": rng.choice(("新增", "修改", "删除")),
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "clear_remark_4": None,
                "create_time": random_date(rng),
                "create_org_no": f"ORG{rng.randint(1, 99):03d}",
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def generate_ap_customer_relation_tree_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_customer_relation_tree 客户关系树（原型 o_a_erms_cust_relation_opt）：
    应用层关系树快照，FK internal_customer_no → ap_customer.internal_customer_no。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_customer_relation_tree") + 1):
        cust = rng.choice(customers)
        rows.append(
            {
                "customer_relation_tree_id": f"RT-{year:04d}-{seq:08d}",
                "upstream_update_time": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "cert_type_code": cust["cert_type"],
                "cert_no": cust["cert_no"],
                "customer_name": cust["customer_name"],
                "internal_customer_no": cust["internal_customer_no"],
                "group_cert_type_code": "统一社会信用代码",
                "group_cert_no": rng.choice(customers)["cert_no"],
                "group_customer_name": cust["group_customer_name"],
                "data_source": rng.choice(DATA_SOURCE_POOL),
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "clear_remark_4": None,
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "create_org_no": f"ORG{rng.randint(1, 99):03d}",
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "is_important_group_customer": rng.randint(0, 1),
                "effective_date": random_date(rng),
                "invalid_date": random_date(rng),
                "current_status": rng.choice(("有效", "失效", "待生效")),
                "cert_type_code_from_bank": "统一社会信用代码",
                "cert_no_from_bank": _uscc(rng),
            }
        )
    return rows


def generate_ap_important_customer_list_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_important_customer_list 重要客户名单（原型 o_a_erms_cust_list）：
    FK group_customer_name → ap_group_customer.group_customer_name。"""
    year = ctx["year"]
    groups = ctx["customer.ap_group_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_important_customer_list") + 1):
        grp = rng.choice(groups)
        rows.append(
            {
                "important_customer_id": f"IC-{year:04d}-{seq:08d}",
                "group_customer_name": grp["group_customer_name"],
                "important_customer_flag": rng.randint(0, 1),
                "risk_customer_flag": rng.randint(0, 1),
                "custom_customer_flag": rng.randint(0, 1),
                "status": rng.choice(("有效", "失效")),
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "clear_remark_4": None,
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
                "customer_short_name": grp["group_customer_name"]
                .replace("集团有限公司", "")
                .replace("集团", ""),
                "is_real_estate": rng.randint(0, 1),
                "belong_industry": rng.choice(
                    ("制造业", "房地产", "批发零售", "交通运输", "信息技术")
                ),
                "is_high_leverage": rng.randint(0, 1),
            }
        )
    return rows


def generate_ap_top500_customer_risk_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_top500_customer_risk 前500大客户风险投融资结果（原型 o_a_erms_top500_cust_info）：
    FK customer_no/group_customer_no → ap_customer / ap_group_customer；row_count=500 与“前 500 大”语义一致。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    chosen = rng.sample(
        customers,
        min(_row_count(ctx, "customer.ap_top500_customer_risk"), len(customers)),
    )
    rows: list[dict[str, Any]] = []
    for seq, cust in enumerate(chosen, start=1):
        net_capital = round(rng.uniform(50000, 200000), 2)
        exposure = round(net_capital * _concentration_ratio(rng), 2)
        result = concentration_calc(exposure, net_capital)
        rows.append(
            {
                "top500_customer_id": f"T5-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": cust["org_id"],
                "customer_no": cust["customer_no"],
                "customer_name": cust["customer_name"],
                "group_customer_no": cust["group_customer_no"],
                "group_customer_name": cust["group_customer_name"],
                "customer_type": "单一客户",
                "group_member_count": rng.randint(1, 20),
                "invest_balance": round(rng.uniform(1000, 500000), 2),
                "risk_exposure": exposure,
                "risk_asset_balance": round(exposure * rng.uniform(0.2, 0.8), 2),
                "concentration_degree": round(result["ratio"], 4),
                "risk_exposure_rank_no": seq,
                "asset_quality_level": cust["asset_quality_level"],
                "warn_flag": 1 if result["warn_level"] in ("RED", "ORANGE") else 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
                "invest_balance_new": round(rng.uniform(1000, 500000), 2),
            }
        )
    return rows


def generate_ap_customer_assets_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_customer_assets 资产结构结果表（原型 o_a_erms_cust_assets）：
    FK customer_no → ap_customer.customer_no；敞口跨板块拆分 exposure_sim。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_customer_assets") + 1):
        cust = rng.choice(customers)
        base = round(rng.uniform(1000, 200000), 2)
        exposures = exposure_sim(rng, base)
        rows.append(
            {
                "customer_assets_id": f"AST-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "customer_no": cust["customer_no"],
                "customer_name": cust["customer_name"],
                "customer_type": "单一客户",
                "business_type_code": rng.choice([p[0] for p in PRODUCT_CODE_POOL]),
                "invest_balance": base,
                "risk_exposure": round(sum(e for _, e in exposures), 2),
                "risk_asset_balance": round(base * rng.uniform(0.01, 0.2), 2),
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
                "invest_balance_new": round(base * rng.uniform(0.9, 1.1), 2),
            }
        )
    return rows


def generate_ap_customer_invest_dist_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_customer_invest_dist 投资分布结果表（原型 o_a_erms_cust_sub_org_invest）：
    FK customer_no → ap_customer.customer_no；按子公司板块拆分敞口。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_customer_invest_dist") + 1):
        cust = rng.choice(customers)
        base = round(rng.uniform(1000, 200000), 2)
        exposures = exposure_sim(rng, base)
        org = rng.choice(ORG_POOL)
        rows.append(
            {
                "customer_invest_dist_id": f"INV-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "customer_no": cust["customer_no"],
                "customer_name": cust["customer_name"],
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "org_name": org,
                "customer_type": "单一客户",
                "invest_balance": base,
                "risk_exposure": round(sum(e for _, e in exposures), 2),
                "risk_asset_balance": round(base * rng.uniform(0.01, 0.2), 2),
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
                "risk_bad_balance": round(base * rng.uniform(0.001, 0.05), 2),
                "invest_balance_new": round(base * rng.uniform(0.9, 1.1), 2),
            }
        )
    return rows


def generate_ap_subsidiary_credit_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_subsidiary_credit_detail 集团加工后子公司授信明细（原型 o_a_erms_credit_detail_1，89 字段）：
    FK group_customer_name → ap_group_customer.group_customer_name；五级分类/减值随规则 2。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_subsidiary_credit_detail") + 1):
        cust = rng.choice(customers)
        base = _cust_base(rng, cust, year)
        pcode, pname = rng.choice(PRODUCT_CODE_POOL)
        ipcode, ipname = rng.choice(INTERNAL_PRODUCT_CODE_POOL)
        qual_code, qual_name = _asset_quality(rng)
        balance = round(rng.uniform(100, 200000), 2)
        row: dict[str, Any] = {
            "data_date": random_date(rng),
            "upstream_update_time": random_date(rng),
            "org_id": cust["org_id"],
            "org_name": cust["org_name"],
            "project_id": f"SC-{year:04d}-{seq:08d}",
            "project_name": f"{cust['customer_name']}{pname}授信项目",
            "customer_name": cust["customer_name"],
            "group_customer_name": cust["group_customer_name"],
            "group_customer_name_processed": cust["group_customer_name"],
            "group_peer_flag": rng.randint(0, 1),
            "cert_type_code": cust["cert_type"],
            "cert_type": cust["cert_type"],
            "cert_no": cust["cert_no"],
            "internal_customer_no": cust["internal_customer_no"],
            "enterprise_nature_code": rng.choice(("A", "B", "C", "D", "E")),
            "enterprise_nature": rng.choice(ENTERPRISE_NATURE_POOL),
            "business_type_code": pcode,
            "business_type": pname,
            "business_product_code": pcode,
            "business_product_name": pname,
            "internal_business_product_code": ipcode,
            "internal_business_product_name": ipname,
            "currency_id": "CNY",
            "index_unit": "万元",
            "business_balance": balance,
            "risk_exposure": round(balance * rng.uniform(0.5, 1.0), 2),
            "pledge_value": round(balance * rng.uniform(0.0, 0.6), 2),
            "guarantee_value": round(balance * rng.uniform(0.0, 0.4), 2),
            "impairment_provision": round(balance * rng.uniform(0.0, 0.15), 2),
            "principal_overdue_days": rng.randint(0, 400),
            "interest_overdue_days": rng.randint(0, 400),
            "asset_quality_level_code": qual_code,
            "asset_quality_level": qual_name,
            "limit_value": round(balance * rng.uniform(1.0, 1.5), 2),
            "customer_status": rng.choice(("正常", "关注", "注销", "吊销")),
            "operate_type": rng.choice(("新增", "修改")),
        }
        row.update(base)
        row.update(_shareholder_block(rng, 1))
        row.update(_shareholder_block(rng, 2))
        row.update(_shareholder_block(rng, 3))
        row.update(_invest_block(rng, 1))
        row.update(_invest_block(rng, 2))
        row.update(_invest_block(rng, 3))
        row["clear_remark_1"] = None
        row["clear_remark_2"] = None
        row["clear_remark_3"] = None
        row["clear_remark_4"] = None
        rows.append(row)
    return rows


def generate_ap_collateral_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_collateral 押品信息（原型 o_a_erms_negot_info）：FK customer_name/group_customer_name；
    押品估值含贬值注入（collateral_val → 规则 1 红档 ~6%）。编码 COL-YYYY-8 位（规则 4）。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_collateral") + 1):
        cust = rng.choice(customers)
        base_value = round(rng.uniform(50, 50000), 2)
        val = collateral_val(rng, base_value)
        rows.append(
            {
                "collateral_id": anping_col_no(year, seq),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "data_date": random_date(rng),
                "project_id": f"PRJ-{year:04d}-{seq:08d}",
                "project_name": f"{cust['customer_name']}授信项目",
                "customer_name": cust["customer_name"],
                "group_customer_name": cust["group_customer_name"],
                "guarantee_contract_id": f"GC-{year:04d}-{seq:08d}",
                "guarantee_contract_name": f"{cust['customer_name']}担保合同",
                "guarantee_contract_amount": base_value,
                "pledge_name": rng.choice(PLEDGE_PROPERTY_POOL),
                "guarantee_repay_order": rng.randint(1, 5),
                "mortgage_ind": rng.randint(0, 1),
                "mortgage_property_type": rng.choice(
                    ("不动产", "动产", "权利", "金融资产")
                ),
                "internal_mortgage_property_type": rng.choice(
                    ("房产", "土地", "设备", "存货", "股权", "应收账款")
                ),
                "is_have_external_estimate_org": rng.randint(0, 1),
                "estimate_org_name": rng.choice(ESTIMATE_ORG_POOL),
                "estimate_value": val["collateral_value"],
                "estimate_date": random_date(rng),
                "corp_identify_time": random_date(rng),
                "corp_identify_value": round(
                    val["collateral_value"] * rng.uniform(0.9, 1.1), 2
                ),
                "mortgaged_value": round(
                    val["collateral_value"] * rng.uniform(0.2, 0.9), 2
                ),
                "mortgage_rate": round(rng.uniform(0.1, 0.8), 4),
                "maintenance_rate": round(rng.uniform(0.8, 1.5), 4),
                "owner_name": _person_name(rng),
                "owner_cert_type": "身份证",
                "owner_cert_no": _idcard(rng),
                "warrant_no": f"WRT-{year:04d}-{rng.randint(100000, 999999)}",
                "internal_collateral_id": f"ICOL-{year:04d}-{seq:08d}",
                "is_mortgage_registered": rng.randint(0, 1),
                "register_date": random_date(rng),
                "right_register_org_name": "安平市不动产登记中心",
                "register_org_credit_code": _uscc(rng),
                "is_major_guarantee_collateral": rng.randint(0, 1),
                "collateral_status": rng.choice(COLLATERAL_STATUS_POOL),
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "clear_remark_1": None,
                "clear_remark_2": None,
            }
        )
    return rows


def generate_ap_subsidiary_mortgage_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_subsidiary_mortgage 子公司抵质押物信息（原型 o_a_erms_org_mrtg_prop_info）：
    FK customer_name → ap_customer.customer_name。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_subsidiary_mortgage") + 1):
        cust = rng.choice(customers)
        base_value = round(rng.uniform(50, 30000), 2)
        val = collateral_val(rng, base_value)
        rows.append(
            {
                "subsidiary_mortgage_id": f"SM-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "customer_name": cust["customer_name"],
                "customer_type": "单一客户",
                "mortgage_ind": rng.randint(0, 1),
                "total_count": rng.randint(1, 50),
                "estimate_value": val["collateral_value"],
                "corp_identify_value": round(
                    val["collateral_value"] * rng.uniform(0.9, 1.1), 2
                ),
                "mortgaged_value": round(
                    val["collateral_value"] * rng.uniform(0.2, 0.9), 2
                ),
                "estimate_quantity": rng.randint(0, 10),
                "percent_value": round(rng.uniform(0.0, 1.0), 4),
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "clear_remark_1": None,
                "clear_remark_2": None,
            }
        )
    return rows


def generate_ap_bank_pledge_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_bank_pledge_detail 押品明细（银行业，原型 o_a_erms_pledge_bankdetail）：
    FK customer_credit_code → ap_customer.cert_no、group_customer_name → ap_group_customer。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_bank_pledge_detail") + 1):
        cust = rng.choice(customers)
        pcode, pname = rng.choice(PRODUCT_CODE_POOL)
        base_value = round(rng.uniform(50, 30000), 2)
        val = collateral_val(rng, base_value)
        rows.append(
            {
                "bank_pledge_id": f"BP-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "project_id": f"PRJ-{year:04d}-{seq:08d}",
                "project_name": f"{cust['customer_name']}授信项目",
                "customer_credit_code": cust["cert_no"],
                "customer_name": cust["customer_name"],
                "group_customer_name": cust["group_customer_name"],
                "business_product_code": pcode,
                "business_product_name": pname,
                "guarantee_contract_id": f"GC-{year:04d}-{seq:08d}",
                "guarantee_contract_name": f"{cust['customer_name']}担保合同",
                "guarantee_contract_amount": base_value,
                "guarantee_contract_balance": round(
                    base_value * rng.uniform(0.1, 1.0), 2
                ),
                "internal_pledge_no": f"IPL-{year:04d}-{seq:08d}",
                "pledge_name": rng.choice(PLEDGE_PROPERTY_POOL),
                "guarantee_repay_order": rng.randint(1, 5),
                "mortgage_ind": rng.randint(0, 1),
                "mortgage_property_type": rng.choice(
                    ("不动产", "动产", "权利", "金融资产")
                ),
                "internal_mortgage_property_type": rng.choice(
                    ("房产", "土地", "设备", "存货", "股权", "应收账款")
                ),
                "is_have_external_estimate_org": rng.randint(0, 1),
                "pledge_location": f"{rng.choice(('上海市', '杭州市', '深圳市', '北京市'))}{rng.choice(('浦东新区', '西湖区', '南山区', '朝阳区', '高新区'))}",
                "estimate_org_name": rng.choice(ESTIMATE_ORG_POOL),
                "initial_estimate_value": base_value,
                "initial_estimate_date": random_date(rng),
                "latest_estimate_value": val["collateral_value"],
                "latest_estimate_date": random_date(rng),
                "disposal_value": round(
                    val["collateral_value"] * rng.uniform(0.5, 0.95), 2
                ),
                "disposal_date": random_date(rng),
                "mortgaged_value": round(
                    val["collateral_value"] * rng.uniform(0.2, 0.9), 2
                ),
                "mortgage_rate": round(rng.uniform(0.1, 0.8), 4),
                "maintenance_rate": round(rng.uniform(0.8, 1.5), 4),
                "owner_name": _person_name(rng),
                "owner_cert_type": "身份证",
                "owner_cert_no": _idcard(rng),
                "warrant_no": f"WRT-{year:04d}-{rng.randint(100000, 999999)}",
                "is_mortgage_registered": rng.randint(0, 1),
                "register_date": random_date(rng),
                "right_register_org_name": "安平市不动产登记中心",
                "register_org_credit_code": _uscc(rng),
                "pledge_status": rng.choice(PLEDGE_STATUS_POOL),
                "biz_date": random_date(rng),
                "company_partition": rng.choice(
                    ("安平银行", "安平证券", "安平信托", "安平租赁")
                ),
            }
        )
    return rows


def generate_ap_securities_pledge_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_securities_pledge_detail 押品明细（证券业，原型 o_a_erms_pledge_securitiesdetail）：
    FK customer_credit_code → ap_customer.cert_no。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_securities_pledge_detail") + 1):
        cust = rng.choice(customers)
        pcode, pname = rng.choice(PRODUCT_CODE_POOL)
        rows.append(
            {
                "securities_pledge_id": f"SP-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "ecif_no": f"ECIF{year:04d}{seq:08d}",
                "customer_credit_code": cust["cert_no"],
                "customer_name": cust["customer_name"],
                "business_product_code": pcode,
                "business_product_name": pname,
                "invest_value": round(rng.uniform(10, 200000), 2),
                "pledge_subject_code": f"6{rng.randint(0, 9)}0{rng.randint(10000, 99999)}",
                "pledge_subject_name": rng.choice(
                    ("安平银行股份", "安平证券股份", "恒达地产", "泰和能源", "中科智造")
                ),
                "pledge_subject_value": round(rng.uniform(10, 200000), 2),
                "bonus_amount": round(rng.uniform(0, 5000), 2),
                "maintenance_rate": round(rng.uniform(1.0, 3.0), 4),
                "pledge_status": rng.choice(PLEDGE_STATUS_POOL),
                "biz_date": random_date(rng),
                "company_partition": "安平证券",
                "partition_date": random_date(rng),
            }
        )
    return rows


# 本模块 11 表 DDL 注册（供 RISK_TABLE_SPECS 复用，字典 key = {system}.{table}）
CUSTOMER_EXT_DDL: dict[str, str] = {
    "customer.ap_customer_relation": RISK_EXT_DDL_1["customer.ap_customer_relation"],
    "customer.ap_customer_relation_tree": RISK_EXT_DDL_1[
        "customer.ap_customer_relation_tree"
    ],
    "customer.ap_important_customer_list": RISK_EXT_DDL_1[
        "customer.ap_important_customer_list"
    ],
    "customer.ap_top500_customer_risk": RISK_EXT_DDL_1[
        "customer.ap_top500_customer_risk"
    ],
    "customer.ap_customer_assets": RISK_EXT_DDL_1["customer.ap_customer_assets"],
    "customer.ap_customer_invest_dist": RISK_EXT_DDL_1[
        "customer.ap_customer_invest_dist"
    ],
    "customer.ap_subsidiary_credit_detail": RISK_EXT_DDL_1[
        "customer.ap_subsidiary_credit_detail"
    ],
    "customer.ap_collateral": RISK_EXT_DDL_1["customer.ap_collateral"],
    "customer.ap_subsidiary_mortgage": RISK_EXT_DDL_1[
        "customer.ap_subsidiary_mortgage"
    ],
    "customer.ap_bank_pledge_detail": RISK_EXT_DDL_1["customer.ap_bank_pledge_detail"],
    "customer.ap_securities_pledge_detail": RISK_EXT_DDL_1[
        "customer.ap_securities_pledge_detail"
    ],
}
