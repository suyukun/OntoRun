"""金融风控 12 张核心表行生成器 —— 依赖 risk_generators（编码/DMN 规则/上下文工具）与 risk_ddl（DDL）。

每个生成器按 des_risk_industry_template.yaml 的拓扑序执行，引用 ctx 缓存的上游表确定性输出；
表注册表 RISK_TABLE_SPECS 由 generate.build_enterprise 消费（与制造业 TABLE_SPECS 合并）。
"""

from __future__ import annotations

import random
from typing import Any

from .risk_generators import (
    APPROVE_POST_DEFS,
    BUSINESS_TYPE_POOL,
    BUSINESS_TYPE_WEIGHTS,
    CERT_TYPE_CODE,
    CONCENTRATION_NORMAL,
    CONCENTRATION_WARN,
    CUST_NAME_MID,
    CUST_NAME_POOL,
    CUST_NAME_SUFFIX,
    DATA_SOURCE_POOL,
    DEAL_TYPE_POOL,
    DISPOSAL_STATUS_POOL,
    DIVISION_POOL,
    ENTERPRISE_NATURE_POOL,
    ENTERPRISE_SCALE_POOL,
    ESTAB_END,
    ESTAB_START,
    EVENT_TYPE_DIST,
    EXTERNAL_LEVEL_POOL,
    FIVE_CLASS_DIST,
    GROUP_SUFFIX,
    GUARANTEE_METHOD_POOL,
    INDUSTRY_LEVEL_POOL,
    INDUSTRY_POOL,
    INTERNAL_LEVEL_POOL,
    LEVEL2_BY_L1,
    METRIC_DEFS,
    ORDER_STATUS_DIST,
    ORG_POOL,
    SCORE_LEVEL_POOL,
    SIGNAL_STATUS_DIST,
    SIGNAL_WAY_POOL,
    WARN_LEVEL_DIST,
    WARN_SOURCE_POOL,
    ZONE_LEVEL_POOL,
    _asset_quality,
    _concentration_ratio,
    _distribute_counts,
    _driver_for_topic,
    _five_class_inputs,
    _industry,
    _invest_block,
    _lifecycle_fields,
    _person_name,
    _row_count,
    _shareholder_block,
    _uscc,
    _warn_inputs_for_level,
    _warn_reason,
    _weighted,
    _zone,
    anping_app_no,
    anping_cust_no,
    anping_dsp_no,
    anping_grp_no,
    anping_proj_no,
    anping_sgn_no,
    approve_flow,
    codebt_link,
    concentration_calc,
    exposure_sim,
    random_date,
)


# 行生成器（每表独立 RNG 流；引用 ctx 缓存的上游表确定性输出）
# ---------------------------------------------------------------------------
def _group_name(rng: random.Random) -> str:
    """P1-3 集团名池再洗：自然长度 ≤9 字（基名+中缀+后缀过长则收敛为「集团」），
    避免「翔宇电子华北实业集团」这类失真长名。"""
    base = rng.choice(CUST_NAME_POOL)
    mid = rng.choice(CUST_NAME_MID)
    cand = f"{base}{mid}{rng.choice(GROUP_SUFFIX)}"
    if len(cand) <= 9:
        return cand
    return f"{base}{mid}集团"


def generate_ap_group_customer_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_group_customer 集团客户主数据：资产质量按规则 2 分布，编码 GRP-YYYY-XXXXXX。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_group_customer") + 1):
        code, name = _asset_quality(rng)
        rows.append(
            {
                "group_customer_no": anping_grp_no(year, seq),
                "data_date": random_date(rng),
                "group_customer_name": _group_name(rng),
                "customer_status": rng.choice(("正常", "关注", "注销", "吊销")),
                "group_peer_flag": rng.randint(0, 1),
                "asset_quality_level_code": code,
                "asset_quality_level": name,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "create_org_no": rng.choice(ORG_POOL),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": rng.choice(ORG_POOL),
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def generate_ap_customer_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """customer.ap_customer 单一客户主数据：客户号 CUST-YYYY-XXXXXX，归属集团（FK→集团），工商/股东/投资齐全。"""
    year = ctx["year"]
    groups = ctx["customer.ap_group_customer"]
    group_names = {g["group_customer_no"]: g["group_customer_name"] for g in groups}
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "customer.ap_customer") + 1):
        grp = rng.choice(groups)["group_customer_no"]
        zone_id, zone_name = _zone(rng)
        inds_id, inds_name = _industry(rng)
        qual_code, qual_name = _asset_quality(rng)
        score = rng.randint(20, 100)
        row: dict[str, Any] = {
            "customer_id": f"CID-{year:04d}-{seq:08d}",
            "data_date": random_date(rng),
            "upstream_update_time": random_date(rng),
            "org_id": f"ORG{rng.randint(1, 99):03d}",
            "org_name": rng.choice(ORG_POOL),
            "customer_no": anping_cust_no(year, seq),
            "customer_name": f"{rng.choice(CUST_NAME_POOL)}{rng.choice(CUST_NAME_MID)}{rng.choice(CUST_NAME_SUFFIX)}",
            "group_customer_no": grp,
            "group_customer_name": group_names[grp],
            "cert_type": CERT_TYPE_CODE,
            "cert_no": _uscc(rng),
            "internal_customer_no": f"APIN-{year:04d}-{seq:08d}",
            "internal_level": rng.choice(INTERNAL_LEVEL_POOL),
            "external_level": rng.choice(EXTERNAL_LEVEL_POOL),
            "zone_id": zone_id,
            "zone_name": zone_name,
            "zone_level": rng.choice(ZONE_LEVEL_POOL),
            "country_id": "CN",
            "country_name": "中国",
            "industry_id": inds_id,
            "industry_name": inds_name,
            "industry_level": rng.choice(INDUSTRY_LEVEL_POOL),
            "asset_quality_level_code": qual_code,
            "asset_quality_level": qual_name,
            "related_party_ind": rng.randint(0, 1),
            "peer_flag": rng.randint(0, 1),
            "enterprise_nature": rng.choice(ENTERPRISE_NATURE_POOL),
            "enterprise_scale": rng.choice(ENTERPRISE_SCALE_POOL),
            "establish_time": f"{rng.randint(ESTAB_START, ESTAB_END):04d}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "registered_capital": round(rng.uniform(100, 200000), 2),
            "chairman_name": _person_name(rng),
            "supervisor_name": _person_name(rng),
            "finance_head_name": _person_name(rng),
            "general_manager_name": _person_name(rng),
            "customer_status": rng.choice(("正常", "关注", "注销", "吊销")),
            "final_score": score,
            "final_score_level": "高"
            if score >= 80
            else ("中" if score >= 60 else "低"),
            "industry_commerce_score_level": rng.choice(SCORE_LEVEL_POOL),
            "trading_score_level": rng.choice(SCORE_LEVEL_POOL),
            "credit_score_level": rng.choice(SCORE_LEVEL_POOL),
            "credit_reference_score_level": rng.choice(SCORE_LEVEL_POOL),
            "financial_score_level": rng.choice(SCORE_LEVEL_POOL),
            "industry_commerce_index": round(rng.uniform(0, 100), 2),
            "trading_index": round(rng.uniform(0, 100), 2),
            "credit_index": round(rng.uniform(0, 100), 2),
            "credit_reference_index": round(rng.uniform(0, 100), 2),
            "financial_index": round(rng.uniform(0, 100), 2),
            "clear_remark_1": None,
            "clear_remark_2": None,
            "clear_remark_3": None,
            "clear_remark_4": None,
            "create_user": "SYSTEM",
            "create_time": random_date(rng),
            "create_org_no": rng.choice(ORG_POOL),
            "update_user": "SYSTEM",
            "update_time": random_date(rng),
            "update_org_no": rng.choice(ORG_POOL),
            "version": "1.0",
            "tenant_id": "AP001",
        }
        row.update(_shareholder_block(rng, 1))
        row.update(_shareholder_block(rng, 2))
        row.update(_shareholder_block(rng, 3))
        row.update(_invest_block(rng, 1))
        row.update(_invest_block(rng, 2))
        row.update(_invest_block(rng, 3))
        rows.append(row)
    return rows


def generate_ap_warning_signal_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warning_signal 预警信号事实表（口径包§五）：等级中文「黄55/橙34/红11」、
    事件类型偏态（信用45/市场20/流动性15/合规12/操作8）、生命周期七态分布；
    warn_reason 与事件类型（level1/level2 同源）严格对齐；流程/审批字段按状态连贯。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_warning_signal") + 1):
        cust = rng.choice(customers)
        event_type = _weighted(rng, EVENT_TYPE_DIST)
        level2 = rng.choice(LEVEL2_BY_L1[event_type])
        driver = _driver_for_topic(level2)
        level = _weighted(rng, WARN_LEVEL_DIST)
        inputs = _warn_inputs_for_level(rng, level, driver)
        if driver == "collateral":
            risk_exp = round(
                rng.uniform(100, 50000) * (1 - inputs["collateral_depreciation"]), 2
            )
        else:
            risk_exp = round(rng.uniform(100, 50000) * rng.uniform(0.95, 1.20), 2)
        sig_status = _weighted(rng, SIGNAL_STATUS_DIST)
        lc = _lifecycle_fields(sig_status)
        # P0-3 时间单调：update_time / signal_update_date ≥ signal_generate_date
        gen_date = random_date(rng)
        est_date = max(gen_date, random_date(rng))
        upd_date = max(gen_date, random_date(rng))
        # P0-3 处置对齐：disposal_status 按生命周期（处置中→处置中；已关闭→已处置；其余→未处置）
        disp_by_status = {
            "待确认": "未处置",
            "确认中": "未处置",
            "已确认": "未处置",
            "处置中": "处置中",
            "已关闭": "已处置",
            "已撤销": "未处置",
            "已排除": "未处置",
        }
        rows.append(
            {
                "warning_id": f"WS-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "customer_id": cust["customer_id"],
                "customer_name": cust["customer_name"],
                "org_id": cust["org_id"],
                "org_name": cust["org_name"],
                "belong_group": cust["group_customer_name"],
                "warn_level": level,
                "event_type": event_type,
                "warn_source": rng.choice(WARN_SOURCE_POOL),
                "warn_reason": _warn_reason(level, level2, inputs),
                "signal_way": rng.choice(SIGNAL_WAY_POOL),
                "sys_proposal_signal_grade": level,
                "signal_id": anping_sgn_no(year, seq),
                "signal_name": f"{event_type}-{level2}预警信号",
                "signal_status": sig_status,
                "signal_level1_topic": event_type,
                "signal_level2_topic": level2,
                "signal_description": f"{cust['customer_name']} {event_type}（{level2}）监测异常，建议关注",
                "signal_generate_date": gen_date,
                "signal_establish_date": est_date,
                "signal_establish_operator": _person_name(rng),
                "signal_update_date": upd_date,
                "data_source": rng.choice(DATA_SOURCE_POOL),
                "is_important_customer": 1 if rng.random() < 0.10 else 0,
                "info_type": rng.randint(0, 1),
                "user_num": f"U{rng.randint(1, 5000):05d}",
                "to_user": f"U{rng.randint(1, 5000):05d}",
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "update_time": upd_date,
                "update_user": _person_name(rng),
                "del_ind": 0,
                "push_warn_reason": _warn_reason(level, level2, inputs),
                "invest_balance": round(rng.uniform(1000, 500000), 2),
                "cert_type_code": CERT_TYPE_CODE,
                "cert_no": cust["cert_no"],
                "biz_date": random_date(rng),
                "group_customer_no": cust["group_customer_no"],
                "group_customer_type": rng.choice(
                    ("单一集团", "关联集团", "一致行动人")
                ),
                "risk_exposure": risk_exp,
                "disposal_status": disp_by_status[sig_status],
                "disposal_demand": rng.choice(
                    ("3 个工作日内反馈", "10 个工作日内处置完毕", "立即处置")
                ),
                "apply_no": None,
                "apply_comment": None,
                "process_status": lc["process_status"],
                "audit_status": lc["audit_status"],
                "audit_comment": lc["audit_comment"],
                "is_shared": rng.randint(0, 1),
            }
        )
    return rows


def generate_ap_warning_disposal_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_warning_disposal 预警处置跟踪：对抽样预警信号的处置状态/进展记录（FK→预警 warning_id）。"""
    year = ctx["year"]
    signals = ctx["risk.ap_warning_signal"]
    chosen = rng.sample(
        signals, min(_row_count(ctx, "risk.ap_warning_disposal"), len(signals))
    )
    rows: list[dict[str, Any]] = []
    # P0-3 处置对齐：progress 按 status 收敛（已处置→完成/解除；处置中→执行中；未处置→待制定）
    progress_by_status = {
        "未处置": "待制定处置方案",
        "处置中": ("方案执行中", "已制定处置方案", "已上报集团", "待评估"),
        "暂缓处置": ("暂缓处置，待补充材料", "待重新制定方案"),
        "已处置": ("已完成处置", "已解除并销号", "风险敞口已压降"),
    }
    for seq, sig in enumerate(chosen, start=1):
        status = rng.choice(DISPOSAL_STATUS_POOL)
        opts = progress_by_status[status]
        progress = rng.choice(opts) if isinstance(opts, tuple) else opts
        d_time = random_date(rng)
        o_time = max(d_time, random_date(rng))  # P0-3 时间单调：operate ≥ disposal
        rows.append(
            {
                "disposal_id": f"WD-{year:04d}-{seq:08d}",
                "warning_id": sig["warning_id"],
                "disposal_status": status,
                "disposal_progress": progress,
                "disposal_time": d_time,
                "operator_user": _person_name(rng),
                "operate_time": o_time,
            }
        )
    return rows


def generate_ap_disposal_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_disposal 信号处置动作：每动作一条，batch_id 每 5 条一组（明细按 batch 关联），处置类型按规则 6。"""
    year = ctx["year"]
    signals = ctx["risk.ap_warning_signal"]
    chosen = rng.sample(signals, min(_row_count(ctx, "risk.ap_disposal"), len(signals)))
    rows: list[dict[str, Any]] = []
    for seq, sig in enumerate(chosen, start=1):
        btype = _weighted(rng, tuple(zip(BUSINESS_TYPE_POOL, BUSINESS_TYPE_WEIGHTS)))
        rows.append(
            {
                "disposal_id": anping_dsp_no(year, seq),
                "batch_id": f"BATCH-{year:04d}-{(seq - 1) // 5 + 1:06d}",
                "business_type": btype,
                "deal_type": rng.choice(DEAL_TYPE_POOL),
                "comment": f"针对 {sig['customer_name']} {sig['warn_reason']} 执行处置",
                "deal_user_id": f"U{rng.randint(1, 5000):05d}",
                "is_deleted": 0,
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": _person_name(rng),
            }
        )
    return rows


def generate_ap_disposal_detail_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """risk.ap_disposal_detail 处置明细：每条引用处置批次（FK→batch）与预警信号号（FK→signal_id）。"""
    year = ctx["year"]
    disposals = ctx["risk.ap_disposal"]
    signals = ctx["risk.ap_warning_signal"]
    signal_ids = [s["signal_id"] for s in signals]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "risk.ap_disposal_detail") + 1):
        disp = rng.choice(disposals)
        rows.append(
            {
                "disposal_detail_id": f"DD-{year:04d}-{seq:08d}",
                "batch_id": disp["batch_id"],
                "business_type": disp["business_type"],
                "signal_id": rng.choice(signal_ids),
                "is_deleted": 0,
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": _person_name(rng),
            }
        )
    return rows


def generate_ap_concentration_limit_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """concentration.ap_concentration_limit 大额客户集中度限额：敞口/资本净额按规则 3 → 状态/预警/审批。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    chosen = rng.sample(
        customers,
        min(_row_count(ctx, "concentration.ap_concentration_limit"), len(customers)),
    )
    rows: list[dict[str, Any]] = []
    for seq, cust in enumerate(chosen, start=1):
        net_capital = round(rng.uniform(50000, 200000), 2)  # 集团资本净额（万元）
        exposure = round(net_capital * _concentration_ratio(rng), 2)
        result = concentration_calc(exposure, net_capital)
        limit = round(net_capital * CONCENTRATION_NORMAL, 2)
        rows.append(
            {
                "concentration_limit_id": f"CL-{year:04d}-{seq:08d}",
                "customer_no": cust["customer_no"],
                "customer_name": cust["customer_name"],
                "warning_value": round(net_capital * CONCENTRATION_WARN, 2),
                "concentration_limit": limit,
                "concentration_limit_old": round(limit * rng.uniform(0.8, 1.2), 2),
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "version": "1.0",
                "tenant_id": "AP001",
                "current_status": result["status"],
            }
        )
    return rows


def generate_ap_approve_node_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_node 审批节点配置（规则 7 岗位链：NODE_SEQ 1-3 循环铺开）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "approval.ap_approve_node") + 1):
        node_seq, post_id, node_name, rule = APPROVE_POST_DEFS[
            (seq - 1) % len(APPROVE_POST_DEFS)
        ]
        rows.append(
            {
                "approve_node_id": f"NODE-{year:04d}-{seq:06d}",
                "approve_order_type": "WARN_SGN",
                "approve_node_seq": node_seq,
                "post_id": post_id,
                "approve_node_name": node_name,
                "approve_rule": rule,
                "is_deleted": 0,
                "create_time": random_date(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_approve_order_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_order 预警审批单：状态推进 PROCESS/APPROVED/REJECTED，衍生预警等级随信号。"""
    year = ctx["year"]
    signals = ctx["risk.ap_warning_signal"]
    chosen = rng.sample(
        signals, min(_row_count(ctx, "approval.ap_approve_order"), len(signals))
    )
    rows: list[dict[str, Any]] = []
    for seq, sig in enumerate(chosen, start=1):
        status = _weighted(rng, ORDER_STATUS_DIST)
        btype = _weighted(rng, tuple(zip(BUSINESS_TYPE_POOL, BUSINESS_TYPE_WEIGHTS)))
        rows.append(
            {
                "approve_order_id": anping_app_no(year, seq),
                "approve_order_type": "WARN_SGN",
                "approve_order_title": f"{btype}预警处置审批",
                "apply_user_id": f"U{rng.randint(1, 5000):05d}",
                "approved_user_id": f"U{rng.randint(1, 5000):05d}"
                if status != "PROCESS"
                else "",
                "apply_time": random_date(rng),
                "approve_time": random_date(rng) if status != "PROCESS" else None,
                "approve_order_status": status,
                "business_type": btype,
                "remark": f"对预警信号 {sig['signal_id']} 申请处置审批",
                "is_deleted": 0,
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "derive_warn_level_red": 1 if sig["warn_level"] == "红" else 0,
                "derive_warn_level_yellow": 1 if sig["warn_level"] in ("黄", "橙") else 0,
                "derive_warn_level_blue": 0,  # 口径包三级制（黄/橙/红）无蓝档
                "opinion_description": (
                    rng.choice(
                        (
                            "同意",
                            "同意，按处置方案执行",
                            "驳回，补充材料后再报",
                            "同意，加强贷后监控",
                        )
                    )
                    if status != "PROCESS"
                    else None
                ),
            }
        )
    return rows


def generate_ap_approve_task_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_task 审批任务：按审批单分布任务数（ANY_ONE 短链合法），状态随 approve_flow。"""
    year = ctx["year"]
    orders = ctx["approval.ap_approve_order"]
    nodes = ctx["approval.ap_approve_node"]
    nodes_by_seq = {
        s: [nd for nd in nodes if nd["approve_node_seq"] == s] for s in (1, 2, 3)
    }
    counts = _distribute_counts(
        rng, len(orders), _row_count(ctx, "approval.ap_approve_task"), 1, 3
    )
    rows: list[dict[str, Any]] = []
    seq = 0
    for order, k in zip(orders, counts):
        outcomes = approve_flow(rng, order["approve_order_status"], k)
        for i, (tstatus, aresult) in enumerate(outcomes, start=1):
            seq += 1
            node = rng.choice(
                nodes_by_seq.get(i) or nodes_by_seq[1]
            )  # 小 scale 下缺高序节点时回退首节点
            rows.append(
                {
                    "approve_task_id": f"AT-{year:04d}-{seq:08d}",
                    "approve_order_id": order["approve_order_id"],
                    "approve_node_id": node["approve_node_id"],
                    "post_id": node["post_id"],
                    "approve_task_status": tstatus,
                    "approve_result": aresult,
                    "approve_remark": (
                        "同意"
                        if aresult == "APPROVED"
                        else ("驳回" if aresult == "REJECTED" else None)
                    ),
                    "approve_time": random_date(rng)
                    if tstatus == "COMPLETED"
                    else None,
                    "is_deleted": 0,
                    "create_time": random_date(rng),
                    "update_time": random_date(rng),
                }
            )
    return rows


def generate_ap_risk_project_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """project.ap_risk_project 风险项目：按集团生成、五级分类按规则 2、减值随分类、跨板块敞口 exposure_sim。"""
    year = ctx["year"]
    groups = ctx["customer.ap_group_customer"]
    members_by_grp: dict[str, list[dict[str, Any]]] = {}
    for c in ctx["customer.ap_customer"]:
        members_by_grp.setdefault(c["group_customer_no"], []).append(c)
    chosen = rng.sample(
        groups, min(_row_count(ctx, "project.ap_risk_project"), len(groups))
    )
    rows: list[dict[str, Any]] = []
    for seq, grp in enumerate(chosen, start=1):
        category = _weighted(rng, FIVE_CLASS_DIST)
        finp = _five_class_inputs(rng, category)
        members = members_by_grp.get(grp["group_customer_no"], [])[:6]
        linked = codebt_link(rng, members) if members else []
        base_balance = round(rng.uniform(0.5, 50), 2)  # 业务余额（亿元）
        exposures = exposure_sim(rng, base_balance)
        rows.append(
            {
                "risk_project_id": anping_proj_no(year, seq),
                "sort_no": seq,
                "group_customer_name": grp["group_customer_name"],
                "batch_id": f"RP-BATCH-{year:04d}-{(seq - 1) // 50 + 1:04d}",
                "division": rng.choice(DIVISION_POOL),
                "enterprise_overview": f"{grp['group_customer_name']} 主营{rng.choice(INDUSTRY_POOL)[1]}，敞口分散于安平体系多个子公司",
                "org_id_1": f"ORG{rng.randint(1, 99):03d}",
                "org_name_1": rng.choice(ORG_POOL[1:]),
                "project_name": f"{grp['group_customer_name']}{rng.choice(('集团授信', '供应链融资', '项目贷款', '并购贷款'))}",
                "org_id_2": f"ORG{rng.randint(1, 99):03d}",
                "org_name_2": rng.choice(ORG_POOL[1:]),
                "business_type": rng.choice(
                    ("流动资金贷款", "项目贷款", "并购贷款", "贸易融资", "银团贷款")
                ),
                "credit_subject": "、".join([grp["group_customer_name"]] + linked)
                or grp["group_customer_name"],
                "business_balance": base_balance,
                "risk_exposure_balance": round(sum(e for _, e in exposures), 2),
                "impairment_provision": round(
                    base_balance * finp["impairment_ratio"], 2
                ),
                "five_classification": category,
                "guarantee_method": rng.choice(GUARANTEE_METHOD_POOL),
                "project_progress": f"逾期 {finp['overdue_days']} 天，处置中"
                if finp["overdue_days"] > 0
                else "正常还款",
                "is_deleted": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
            }
        )
    return rows


def generate_ap_dim_metric_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_dim_metric 指标明细：单一客户/集团维度 × 指标库快照（跨库 FK 由客户号/集团号承载）。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    groups = ctx["customer.ap_group_customer"]
    grp_names = {g["group_customer_no"]: g["group_customer_name"] for g in groups}
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_dim_metric") + 1):
        mid, mname, munit = rng.choice(METRIC_DEFS)
        if rng.random() < 0.5:
            grp = rng.choice(groups)
            cust_no, cust_nm, grp_no, grp_nm = (
                "",
                "",
                grp["group_customer_no"],
                grp["group_customer_name"],
            )
            dim_code, dim_name = "DIM_GROUP", "集团客户"
        else:
            cust = rng.choice(customers)
            cust_no, cust_nm = cust["customer_no"], cust["customer_name"]
            grp_no, grp_nm = (
                cust["group_customer_no"],
                grp_names[cust["group_customer_no"]],
            )
            dim_code, dim_name = "DIM_CUST", "单一客户"
        rows.append(
            {
                "dim_metric_id": f"DM-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "dim_type_code": dim_code,
                "dim_type_name": dim_name,
                "customer_no": cust_no,
                "customer_name": cust_nm,
                "group_customer_no": grp_no,
                "group_customer_name": grp_nm,
                "business_type_code": rng.choice(
                    ("LOAN", "GUARANTEE", "BILL", "LEASE")
                ),
                "business_product_code": rng.choice(
                    ("PROD-001", "PROD-002", "PROD-003")
                ),
                "index_id": mid,
                "index_name": mname,
                "index_value": round(rng.uniform(1, 1000), 2),
                "index_unit": munit,
                "currency_id": "CNY",
                "currency_name": "人民币",
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


# ---------------------------------------------------------------------------
