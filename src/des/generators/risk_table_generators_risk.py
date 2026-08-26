"""金融风控 M1b 全量补全 —— risk 系统 11 张新表行生成器（脱敏后 ap_* 表）。

依赖 risk_generators（编码/DMN 规则/共享业务池）与 risk_ddl_ext（DDL）。
覆盖预警推送/集中度预警/衍生预警/背离预警/衍生处置/子公司推送/合规审计/监管处罚。
FK 引用真实：warning_id → ap_warning_signal、customer_id → ap_customer、top500_customer_id →
ap_top500_customer_risk、approve_order_id → ap_approve_order。原型表名（o_a_erms_*/p_erms_*）只在 docstring 溯源。
"""

from __future__ import annotations

import random
from typing import Any

from .risk_ddl_ext import RISK_EXT_DDL_1
from .risk_generators import (
    AUDIT_TYPE_POOL,
    CASE_TYPE_POOL,
    DATA_SOURCE_POOL,
    DEAL_SUGGESTION_POOL,
    LEVEL1_TOPICS,
    LEVEL2_BY_L1,
    PENALTY_FORM_POOL,
    PUSH_STATUS_POOL,
    RISK_TYPE_DETERMINE_POOL,
    SIGNAL_STATUS_POOL,
    SIGNAL_STATUS_POOL_FULL,
    SIGNAL_WAY_POOL,
    WARN_LEVEL_DIST,
    WARN_MODEL_POOL,
    WARN_SOURCE_POOL,
    _driver_for_topic,
    _person_name,
    _row_count,
    _warn_inputs_for_level,
    _warn_reason,
    _warn_text,
    _weighted,
    concentration_calc,
    random_date,
)


def generate_ap_warning_push_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warning_push 预警推送表（原型 o_a_erms_cust_warn_sgn_push）：
    FK warning_id → ap_warning_signal.warning_id；推送事由随信号等级。"""
    year = ctx["year"]
    signals = ctx["risk.ap_warning_signal"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warning_push") + 1):
        sig = rng.choice(signals)
        rows.append(
            {
                "warning_push_id": f"WP-{year:04d}-{seq:08d}",
                "warning_id": sig["warning_id"],
                "push_warn_reason": sig["push_warn_reason"],
                "push_person": _person_name(rng),
                "push_time": random_date(rng),
                "receive_person": _person_name(rng),
                "receive_instruction": rng.choice(
                    ("已阅，请跟踪处置", "转风险条线复核", "要求子公司限期反馈", "无")
                ),
                "receive_time": random_date(rng),
            }
        )
    return rows


def generate_ap_audit_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_audit_detail 合规内控审计记录（原型 o_a_erms_audit_detail）：独立审计记录，无 FK。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_audit_detail") + 1):
        rows.append(
            {
                "audit_id": f"AUD-{year:04d}-{seq:08d}",
                "declare_unit": rng.choice(
                    (
                        "安平银行",
                        "安平证券",
                        "安平信托",
                        "安平保险",
                        "安平租赁",
                        "安平集团总部",
                    )
                ),
                "question_id": f"Q-{year:04d}-{seq:08d}",
                "audit_type": rng.choice(AUDIT_TYPE_POOL),
                "audit_start_time": random_date(rng),
                "audit_end_time": random_date(rng),
                "audit_org_name": rng.choice(
                    ("安平集团审计部", "外部会计师事务所", "监管现场检查")
                ),
                "audit_aim": rng.choice(
                    ("评估内控有效性", "检查合规执行情况", "专项风险排查")
                ),
                "audit_object_name": f"{rng.choice(('授信业务', '同业业务', '投资业务', '担保业务'))}专项",
                "audit_content": rng.choice(
                    (
                        "检查授信审批流程合规性",
                        "核查资金流向真实性",
                        "评估反洗钱措施执行",
                        "检查关联交易管理",
                    )
                ),
                "audit_basis": rng.choice(
                    (
                        "《商业银行内部控制指引》",
                        "《关于防范金融风险的通知》",
                        "集团内部审计制度",
                    )
                ),
                "audit_member": _person_name(rng),
                "audit_question_title": rng.choice(
                    (
                        "审批材料缺失",
                        "贷后检查频率不足",
                        "抵押登记未及时办理",
                        "风险分类调整滞后",
                    )
                ),
                "audit_question_memo": rng.choice(
                    (
                        "存在 3 笔业务材料不完整",
                        "贷后检查间隔超过规定",
                        "个别押品未办妥登记",
                        "分类结果与实质风险不符",
                    )
                ),
                "qualitative_basis": rng.choice(
                    ("属于一般性问题", "属于重要问题", "属于重大问题")
                ),
                "rectification_requirement": rng.choice(
                    ("限期一个月内整改完毕", "立行立改", "限期两个季度整改")
                ),
                "duty_org_dept": rng.choice(
                    ("风险管理部", "授信管理部", "运营管理部", "合规部")
                ),
                "deadline_requirement": "2026-12-31",
                "supervise_unit": "安平集团审计部",
                "rectification_measure": rng.choice(
                    (
                        "补充完善审批材料",
                        "加强贷后检查频次",
                        "补办抵押登记手续",
                        "重新分类调整",
                    )
                ),
                "completion_status": rng.choice(
                    ("已整改", "整改中", "未整改", "待评估")
                ),
                "operator_user": _person_name(rng),
                "operate_time": random_date(rng),
            }
        )
    return rows


def generate_ap_compliance_risk_ledger_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_compliance_risk_ledger 潜在合规风险摸排台账（原型 o_a_erms_compliance_risk_ledger）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_compliance_risk_ledger") + 1):
        rows.append(
            {
                "compliance_risk_id": f"CRL-{year:04d}-{seq:08d}",
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "org_name": rng.choice(
                    ("安平银行", "安平证券", "安平信托", "安平保险", "安平租赁")
                ),
                "dept_line": rng.choice(
                    ("信贷业务条线", "同业业务条线", "投资业务条线", "运营条线")
                ),
                "business_type": rng.choice(
                    ("流动资金贷款", "同业拆借", "股权投资", "票据业务", "担保业务")
                ),
                "event_overview": rng.choice(
                    (
                        "存量授信未做贷后重检",
                        "个别客户准入材料不合规",
                        "反洗钱系统升级未完成",
                        "押品重估周期超限",
                    )
                ),
                "self_check": rng.choice(
                    ("已开展自查并形成报告", "自查进行中", "未开展自查")
                ),
                "land_time": random_date(rng),
                "expect_land_time": random_date(rng),
                "penalty_percent": round(rng.uniform(0.01, 0.8), 4),
                "expect_penalty_amount": round(rng.uniform(0, 500), 2),
                "expect_other_penalty": rng.choice(
                    ("责令整改", "暂停相关业务", "无", "通报批评")
                ),
                "remark": rng.choice(("需持续跟踪", "已纳入整改计划", "风险可控", "")),
                "risk_status": rng.choice(("待摸排", "摸排中", "已排查", "已销号")),
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_compliance_risk_ledger_tmp_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_compliance_risk_ledger_tmp 合规风险摸排台账（临时表，原型 o_a_erms_compliance_risk_ledger_tmp）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_compliance_risk_ledger_tmp") + 1):
        rows.append(
            {
                "compliance_risk_tmp_id": f"CRT-{year:04d}-{seq:08d}",
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "org_name": rng.choice(
                    ("安平银行", "安平证券", "安平信托", "安平保险", "安平租赁")
                ),
                "dept_line": rng.choice(
                    ("信贷业务条线", "同业业务条线", "投资业务条线", "运营条线")
                ),
                "business_type": rng.choice(
                    ("流动资金贷款", "同业拆借", "股权投资", "票据业务", "担保业务")
                ),
                "event_overview": rng.choice(
                    (
                        "临时摸排：客户涉诉",
                        "临时摸排：媒体报道",
                        "临时摸排：监管问询",
                        "临时摸排：数据异常",
                    )
                ),
                "self_check": rng.choice(
                    ("已开展自查并形成报告", "自查进行中", "未开展自查")
                ),
                "land_time": random_date(rng),
                "expect_land_time": random_date(rng),
                "penalty_percent": round(rng.uniform(0.01, 0.8), 4),
                "expect_penalty_amount": round(rng.uniform(0, 500), 2),
                "expect_other_penalty": rng.choice(
                    ("责令整改", "暂停相关业务", "无", "通报批评")
                ),
                "remark": rng.choice(("待转正式台账", "已转正式台账", "")),
                "risk_status": rng.choice(("待摸排", "摸排中", "已排查")),
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_regulatory_penalty_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_regulatory_penalty 监管处罚记录（原型 o_a_erms_custd_pnsh）：独立监管处罚台账。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_regulatory_penalty") + 1):
        rows.append(
            {
                "penalty_id": f"PN-{year:04d}-{seq:08d}",
                "declare_unit": rng.choice(
                    ("安平银行", "安平证券", "安平信托", "安平保险", "安平租赁")
                ),
                "penalty_decision_date": random_date(rng),
                "penalty_decision_no": f"银罚决字〔2026〕{rng.randint(1, 999)}号",
                "penalty_decision_org": rng.choice(
                    ("国家金融监督管理总局", "当地金融监管局", "人民银行分支机构")
                ),
                "penalty_object": rng.choice(
                    ("安平银行股份有限公司", "安平证券有限责任公司", "安平信托有限公司")
                ),
                "major_violation_fact": rng.choice(
                    (
                        "未按规定报送监管数据",
                        "贷款三查不尽职",
                        "违规发放流动资金贷款",
                        "未按规定履行反洗钱义务",
                    )
                ),
                "penalty_basis": rng.choice(
                    ("《银行业监督管理法》", "《商业银行法》", "《反洗钱法》")
                ),
                "case_type": rng.choice(CASE_TYPE_POOL),
                "problem_category": rng.choice(
                    ("数据治理", "授信管理", "反洗钱", "合规经营")
                ),
                "penalty_form": rng.choice(PENALTY_FORM_POOL),
                "penalty_amount": round(rng.uniform(20, 500), 2),
                "confiscation_amount": round(rng.uniform(0, 200), 2),
                "disposal_status": rng.choice(("已缴纳", "分期缴纳", "待缴纳")),
                "memo": rng.choice(("已按期整改", "整改中", "")),
                "operator_user": _person_name(rng),
                "operate_time": random_date(rng),
                "effect": rng.choice(("一般影响", "较大影响", "重大影响")),
                "problem_category_new": rng.choice(
                    ("数据治理", "授信管理", "反洗钱", "合规经营")
                ),
                "rectification_plan_finish_time": random_date(rng),
                "rectification_complete_flag": rng.randint(0, 1),
                "accountability_result": rng.choice(
                    ("内部通报", "经济处罚", "纪律处分", "无")
                ),
                "data_status": rng.choice(("有效", "已归档")),
            }
        )
    return rows


def generate_ap_warn_signal_concentration_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warn_signal_concentration 客户集中度预警信号（原型 p_erms_cust_warn_sgn_concentration）：
    FK top500_customer_id → ap_top500_customer_risk、customer_no/group_customer_no → ap_customer/ap_group_customer；
    集中度等级按规则 3。"""
    year = ctx["year"]
    top500s = ctx["customer.ap_top500_customer_risk"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warn_signal_concentration") + 1):
        t5 = rng.choice(top500s)
        result = concentration_calc(
            t5["risk_exposure"], round(rng.uniform(50000, 200000), 2)
        )
        warn_level = (
            "RED"
            if result["warn_level"] == "RED"
            else ("YELLOW" if result["warn_level"] in ("ORANGE", "YELLOW") else "BLUE")
        )
        rows.append(
            {
                "concentration_signal_id": f"CS-{year:04d}-{seq:08d}",
                "top500_customer_id": t5["top500_customer_id"],
                "data_date": random_date(rng),
                "org_id": t5["org_id"],
                "customer_no": t5["customer_no"],
                "customer_name": t5["customer_name"],
                "group_customer_no": t5["group_customer_no"],
                "group_customer_name": t5["group_customer_name"],
                "customer_type": t5["customer_type"],
                "group_member_count": t5["group_member_count"],
                "invest_balance": t5["invest_balance"],
                "risk_exposure": t5["risk_exposure"],
                "concentration_degree": t5["concentration_degree"],
                "signal_name": f"集中度预警-{t5['group_customer_name']}",
                "warn_reason": _warn_text(rng, warn_level, "集中度敞口"),
                "concentration_limit": round(rng.uniform(10000, 50000), 2),
                "risk_warning_threshold": round(rng.uniform(0.1, 0.25), 4),
                "warn_rule": rng.choice(("B1", "B2", "A1", "A2")),
                "signal_establish_date": random_date(rng),
                "signal_status": rng.choice(SIGNAL_STATUS_POOL_FULL),
                "comp_lead_push_status": rng.choice(PUSH_STATUS_POOL),
                "sub_company_push_status": rng.choice(PUSH_STATUS_POOL),
                "sub_company_push_time": random_date(rng),
                "warn_level": warn_level,
                "is_deleted": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
            }
        )
    return rows


def generate_ap_warn_signal_derive_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warn_signal_derive 客户衍生预警信号（原型 p_erms_cust_warn_sgn_derive，48 字段）：
    FK customer_id → ap_customer.customer_id、approve_order_id → ap_approve_order.approve_order_id。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    orders = ctx["approval.ap_approve_order"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warn_signal_derive") + 1):
        cust = rng.choice(customers)
        level1 = rng.choice(LEVEL1_TOPICS)
        level2 = rng.choice(LEVEL2_BY_L1[level1])
        level = _weighted(rng, WARN_LEVEL_DIST)
        inputs = _warn_inputs_for_level(rng, level, _driver_for_topic(level2))
        order = rng.choice(orders)
        rows.append(
            {
                "derive_warning_id": f"DW-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "customer_id": cust["customer_id"],
                "customer_name": cust["customer_name"],
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "belong_group": cust["group_customer_name"],
                "warn_level": level,
                "event_type": level1,
                "warn_source": rng.choice(WARN_SOURCE_POOL),
                "warn_reason": _warn_reason(level, level2, inputs),
                "signal_way": rng.choice(SIGNAL_WAY_POOL),
                "sys_proposal_signal_grade": level,
                "signal_id": f"SD-{year:04d}-{seq:08d}",
                "signal_name": f"{level1}-{level2}衍生预警",
                "signal_status": rng.choice(SIGNAL_STATUS_POOL),
                "signal_level1_topic": level1,
                "signal_level2_topic": level2,
                "signal_description": _warn_text(rng, level, f"{level1}-{level2}"),
                "signal_generate_date": random_date(rng),
                "signal_establish_date": random_date(rng),
                "signal_establish_operator": _person_name(rng),
                "signal_update_date": random_date(rng),
                "data_source": rng.choice(DATA_SOURCE_POOL),
                "derive_signal_level1_topic": level1,
                "derive_signal_level2_topic": level2,
                "derive_warn_level": level,
                "derive_establish_date": random_date(rng),
                "warn_model": rng.choice(WARN_MODEL_POOL),
                "ai_data": f"AI评分{round(rng.uniform(40, 95), 1)}分",
                "derive_risk_type_determine": rng.choice(RISK_TYPE_DETERMINE_POOL),
                "assess_extent_impact": rng.choice(("轻微", "一般", "较大", "重大")),
                "deal_suggestion": rng.choice(DEAL_SUGGESTION_POOL),
                "derive_signal_status": rng.choice(SIGNAL_STATUS_POOL_FULL),
                "comp_lead_push_status": rng.choice(PUSH_STATUS_POOL),
                "warn_reason_update_status": rng.choice(("未修改", "已修改")),
                "warn_reason_updated": None
                if rng.random() < 0.6
                else _warn_reason(level, level2, inputs),
                "sub_company_push_status": rng.choice(PUSH_STATUS_POOL),
                "sub_company_push_time": random_date(rng),
                "is_deleted": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
                "opinion_description": rng.choice(
                    ("同意", "同意，按建议执行", "驳回补充材料", None)
                ),
                "approve_order_status": order["approve_order_status"],
                "approve_order_id": order["approve_order_id"],
                "is_holding_add": rng.randint(0, 1),
            }
        )
    return rows


def generate_ap_warn_derive_deal_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warn_derive_deal_detail 衍生预警处置详情（原型 p_erms_cust_warn_sgn_derive_deal_detail）：
    FK derive_warning_id → ap_warn_signal_derive.derive_warning_id。"""
    year = ctx["year"]
    derives = ctx["risk.ap_warn_signal_derive"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warn_derive_deal_detail") + 1):
        d = rng.choice(derives)
        rows.append(
            {
                "derive_deal_detail_id": f"DDD-{year:04d}-{seq:08d}",
                "batch_id": f"DB-{year:04d}-{(seq - 1) // 5 + 1:06d}",
                "derive_warning_id": d["derive_warning_id"],
                "is_deleted": 0,
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": _person_name(rng),
            }
        )
    return rows


def generate_ap_warn_derive_sub_push_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warn_derive_sub_push 衍生预警子公司推送（原型 p_erms_cust_warn_sgn_derive_sub_push）：
    FK derive_warning_id → ap_warn_signal_derive、customer_id → ap_customer.customer_id。"""
    year = ctx["year"]
    derives = ctx["risk.ap_warn_signal_derive"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warn_derive_sub_push") + 1):
        d = rng.choice(derives)
        cust = rng.choice(customers)
        rows.append(
            {
                "derive_sub_push_id": f"DSP-{year:04d}-{seq:08d}",
                "derive_warning_id": d["derive_warning_id"],
                "signal_establish_date": random_date(rng),
                "customer_id": cust["customer_id"],
                "customer_name": cust["customer_name"],
                "signal_name": d["signal_name"],
                "signal_level1_topic": d["signal_level1_topic"],
                "signal_level2_topic": d["signal_level2_topic"],
                "derive_warn_level": d["derive_warn_level"],
                "warn_reason_updated": d["warn_reason_updated"] or d["warn_reason"],
                "etl_job_flag": rng.choice(("0", "1", "2")),
                "is_deleted": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
            }
        )
    return rows


def generate_ap_warn_signal_deviation_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warn_signal_deviation 客户背离预警信号（原型 p_erms_cust_warn_sgn_deviation）：
    FK customer_no/group_customer_no → ap_customer/ap_group_customer、approve_order_id → ap_approve_order。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    orders = ctx["approval.ap_approve_order"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warn_signal_deviation") + 1):
        cust = rng.choice(customers)
        order = rng.choice(orders)
        mom = round(rng.uniform(0.05, 1.5), 4)
        ytd = round(rng.uniform(0.05, 2.0), 4)
        mgr = round(rng.uniform(0.05, 1.8), 4)
        warn_rule = rng.choice(("A", "B", "C"))
        level = (
            "RED"
            if max(mom, ytd, mgr) > 1.0
            else ("YELLOW" if max(mom, ytd, mgr) > 0.5 else "BLUE")
        )
        rows.append(
            {
                "deviation_signal_id": f"DV-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "customer_no": cust["customer_no"],
                "customer_name": cust["customer_name"],
                "group_customer_no": cust["group_customer_no"],
                "group_customer_name": cust["group_customer_name"],
                "customer_type": "单一客户",
                "group_member_count": rng.randint(1, 20),
                "invest_balance": round(rng.uniform(1000, 500000), 2),
                "risk_exposure": round(rng.uniform(100, 200000), 2),
                "signal_name": f"趋势背离预警-{cust['customer_name']}",
                "warn_reason": f"{cust['customer_name']}投融资余额环比/单月增幅/较年初出现显著背离，触发{level}预警",
                "signal_establish_date": random_date(rng),
                "mom": mom,
                "mgr": mgr,
                "ytd": ytd,
                "warn_rule": warn_rule,
                "deviation_signal_status": rng.choice(SIGNAL_STATUS_POOL_FULL),
                "comp_lead_push_status": rng.choice(PUSH_STATUS_POOL),
                "sub_company_push_status": rng.choice(PUSH_STATUS_POOL),
                "sub_company_push_time": random_date(rng),
                "is_deleted": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
                "opinion_description": rng.choice(
                    ("同意", "同意，按建议执行", "驳回补充材料", None)
                ),
                "approve_order_status": order["approve_order_status"],
                "approve_order_id": order["approve_order_id"],
            }
        )
    return rows


def generate_ap_deviation_warn_score_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_deviation_warn_score 趋势背离预警评分模型结果（原型 p_erms_deviation_cust_warn_score）：
    FK group_customer_name → ap_group_customer.group_customer_name。"""
    year = ctx["year"]
    groups = ctx["customer.ap_group_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_deviation_warn_score") + 1):
        grp = rng.choice(groups)
        mom = round(rng.uniform(0.05, 1.5), 4)
        ytd = round(rng.uniform(0.05, 2.0), 4)
        mgr = round(rng.uniform(0.05, 1.8), 4)
        variation = round(mgr * round(rng.uniform(1000, 500000), 2), 2)
        score = round(min(100, max(0, 40 + variation / 5000)), 1)
        warn_level = "RED" if score >= 80 else ("YELLOW" if score >= 60 else "BLUE")
        rows.append(
            {
                "deviation_warn_score_id": f"DWS-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "group_customer_name": grp["group_customer_name"],
                "customer_type": "02",
                "signal_name": f"趋势背离预警-{grp['group_customer_name']}",
                "risk_exposure": round(rng.uniform(1, 50), 2),
                "invest_balance": round(rng.uniform(1, 100), 2),
                "mom": mom,
                "ytd": ytd,
                "mgr": mgr,
                "warn_reason": f"{grp['group_customer_name']}融资趋势背离，建议关注",
                "customer_level": grp["asset_quality_level"],
                "score": score,
                "warn_level_code": warn_level,
                "warn_level": {"RED": "红色", "YELLOW": "黄色", "BLUE": "蓝色"}[
                    warn_level
                ],
                "exposure_change": round(rng.uniform(-0.3, 1.0), 4),
                "signal_strength": rng.choice(("强", "中", "弱")),
                "disposal_priority": rng.choice(("高", "中", "低")),
                "involved_amount_level": rng.choice(("大额", "中额", "小额")),
                "is_disposal_needed": rng.randint(0, 1),
                "suggest_actions": rng.choice(DEAL_SUGGESTION_POOL),
                "variation": variation,
                "calc_detail": f"mgr={mgr:.4f} × 余额 → 变化 {variation:.2f}",
                "create_time": random_date(rng),
            }
        )
    return rows


# 本模块 11 表 DDL 注册（供 RISK_TABLE_SPECS 复用，字典 key = {system}.{table}）
RISK_EXT_DDL: dict[str, str] = {
    "risk.ap_warning_push": RISK_EXT_DDL_1["risk.ap_warning_push"],
    "risk.ap_audit_detail": RISK_EXT_DDL_1["risk.ap_audit_detail"],
    "risk.ap_compliance_risk_ledger": RISK_EXT_DDL_1["risk.ap_compliance_risk_ledger"],
    "risk.ap_compliance_risk_ledger_tmp": RISK_EXT_DDL_1[
        "risk.ap_compliance_risk_ledger_tmp"
    ],
    "risk.ap_regulatory_penalty": RISK_EXT_DDL_1["risk.ap_regulatory_penalty"],
    "risk.ap_warn_signal_concentration": RISK_EXT_DDL_1[
        "risk.ap_warn_signal_concentration"
    ],
    "risk.ap_warn_signal_derive": RISK_EXT_DDL_1["risk.ap_warn_signal_derive"],
    "risk.ap_warn_derive_deal_detail": RISK_EXT_DDL_1[
        "risk.ap_warn_derive_deal_detail"
    ],
    "risk.ap_warn_derive_sub_push": RISK_EXT_DDL_1["risk.ap_warn_derive_sub_push"],
    "risk.ap_warn_signal_deviation": RISK_EXT_DDL_1["risk.ap_warn_signal_deviation"],
    "risk.ap_deviation_warn_score": RISK_EXT_DDL_1["risk.ap_deviation_warn_score"],
}
