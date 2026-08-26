"""金融风控 M1b 全量补全 —— concentration(4) + approval(3) + project(2) 系统新表行生成器。

依赖 risk_generators（编码/DMN 规则/共享业务池）与 risk_ddl_ext2（DDL）。
覆盖集中度限额/预警调整、共债明细/评分、审批操作日志/待办/预警关联、查询日志、流水号计数器。
FK 引用真实：concentration_limit_id → ap_concentration_limit、customer_no → ap_customer、
customer_name → ap_customer、approve_order_id/task_id → ap_approve_order/ap_approve_task、
warning_id → ap_warning_signal。原型表名（o_a_erms_*/p_erms_*）只在 docstring 溯源。
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from .risk_ddl_ext2 import RISK_EXT_DDL_2
from .risk_generators import (
    LEVEL2_BY_L1,
    WARN_LEVEL_DIST,
    _industry,
    _person_name,
    _row_count,
    _weighted,
    random_date,
)


def generate_ap_concentration_limit_adj_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """concentration.ap_concentration_limit_adj 集中度限额调整（原型 o_a_erms_larg_cust_limit_adj）：
    FK concentration_limit_id → ap_concentration_limit、customer_no → ap_customer.customer_no。"""
    year = ctx["year"]
    limits = ctx["concentration.ap_concentration_limit"]
    rows: list[dict[str, Any]] = []
    for seq in range(
        1, _row_count(ctx, "concentration.ap_concentration_limit_adj") + 1
    ):
        lim = rng.choice(limits)
        new_limit = round(lim["concentration_limit"] * rng.uniform(0.8, 1.2), 2)
        rows.append(
            {
                "concentration_limit_adj_id": f"CLA-{year:04d}-{seq:08d}",
                "concentration_limit_id": lim["concentration_limit_id"],
                "customer_no": lim["customer_no"],
                "customer_name": lim["customer_name"],
                "concentration_limit": new_limit,
                "concentration_limit_old": lim["concentration_limit"],
                "current_status": rng.choice(("待维护", "维护中", "已生效", "已失效")),
                "approve_status": rng.choice(("PROCESS", "APPROVED", "REJECTED")),
                "approve_comment": rng.choice(
                    ("同意调整限额", "驳回，限额过高", "同意，加强监测", "")
                ),
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_concentration_warn_adj_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """concentration.ap_concentration_warn_adj 集中度预警调整（原型 o_a_erms_larg_cust_warn_adj）：
    FK concentration_limit_id → ap_concentration_limit、customer_no → ap_customer.customer_no。"""
    year = ctx["year"]
    limits = ctx["concentration.ap_concentration_limit"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "concentration.ap_concentration_warn_adj") + 1):
        lim = rng.choice(limits)
        new_line = round(lim["warning_value"] * rng.uniform(0.8, 1.2), 2)
        rows.append(
            {
                "concentration_warn_adj_id": f"CWA-{year:04d}-{seq:08d}",
                "concentration_limit_id": lim["concentration_limit_id"],
                "customer_no": lim["customer_no"],
                "customer_name": lim["customer_name"],
                "concentration_warn_line": new_line,
                "concentration_warn_line_old": lim["warning_value"],
                "current_status": rng.choice(("待维护", "维护中", "已生效", "已失效")),
                "approve_status": rng.choice(("PROCESS", "APPROVED", "REJECTED")),
                "approve_comment": rng.choice(("同意调整预警线", "驳回，重新测算", "")),
                "create_user": _person_name(rng),
                "create_time": random_date(rng),
                "update_user": _person_name(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_codebt_customer_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """concentration.ap_codebt_customer 共债客户明细（原型 p_erms_codebt_cust_info）：
    FK customer_name → ap_customer.customer_name；跨子公司敞口 exposure_sim。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "concentration.ap_codebt_customer") + 1):
        cust = rng.choice(customers)
        rows.append(
            {
                "codebt_customer_id": f"CB-{year:04d}-{seq:08d}",
                "customer_name": cust["customer_name"],
                "data_date": random_date(rng),
                "customer_type": rng.choice(("01", "02")),
                "group_member_count": rng.randint(1, 20),
                "subsidiary_count": rng.randint(1, 8),
                "org_id": cust["org_id"],
                "invest_balance": round(rng.uniform(1000, 500000), 2),
                "risk_exposure": round(rng.uniform(100, 200000), 2),
                "is_deleted": 0,
                "create_time": random_date(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_codebt_warn_score_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """concentration.ap_codebt_warn_score 共债客户风险预警评分（原型 p_erms_codebt_cust_warn_score）：
    FK customer_name → ap_customer.customer_name；信号计数/评分派生自集中度规则。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "concentration.ap_codebt_warn_score") + 1):
        cust = rng.choice(customers)
        level = _weighted(rng, WARN_LEVEL_DIST)
        n = rng.randint(1, 15)
        red = rng.randint(0, max(0, n))
        yellow = rng.randint(0, max(0, n - red))
        blue = max(0, n - red - yellow)
        inds_id, inds_name = _industry(rng)
        score = round(min(100, max(0, 40 + red * 12 + yellow * 5)), 1)
        rows.append(
            {
                "codebt_warn_score_id": f"CBS-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "signal_generate_date": random_date(rng),
                "customer_name": cust["customer_name"],
                "customer_type": "01",
                "risk_exposure": round(rng.uniform(100, 200000), 2),
                "invest_balance": round(rng.uniform(1000, 500000), 2),
                "industry_id": inds_id,
                "industry_name": inds_name,
                "warn_level": level,
                "signal_level2_topic": rng.choice(LEVEL2_BY_L1["信用风险"]),
                "signal_count": n,
                "red_signal_count": red,
                "blue_signal_count": blue,
                "yellow_signal_count": yellow,
                "subsidiary_count": rng.randint(1, 8),
                "top10_risk_exposure_avg": round(rng.uniform(100, 5000), 2),
                "score": score,
                "calc_detail": f"红{red}黄{yellow}蓝{blue} → 评分{score:.1f}",
                "create_time": random_date(rng),
            }
        )
    return rows


def generate_ap_approve_oper_log_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_oper_log 审批操作日志（原型 p_erms_approve_oper_log）：
    FK approve_order_id → ap_approve_order、approve_task_id → ap_approve_task。"""
    year = ctx["year"]
    orders = ctx["approval.ap_approve_order"]
    tasks = ctx["approval.ap_approve_task"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "approval.ap_approve_oper_log") + 1):
        order = rng.choice(orders)
        task = rng.choice(tasks)
        rows.append(
            {
                "approve_log_id": f"ALG-{year:04d}-{seq:08d}",
                "approve_order_id": order["approve_order_id"],
                "approve_task_id": task["approve_task_id"],
                "operator_user_id": f"U{rng.randint(1, 5000):05d}",
                "operate_type": rng.choice(("SUBMIT", "APPROVE", "REJECT")),
                "operate_remark": rng.choice(
                    ("提交审批", "审批通过", "审批驳回", "退回补充")
                ),
                "operate_time": random_date(rng),
                "ext": None,
            }
        )
    return rows


def generate_ap_approve_warn_rel_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_warn_rel 审批单预警信号关联（原型 p_erms_approve_order_warn_rel）：
    FK approve_order_id → ap_approve_order、warning_id → ap_warning_signal.warning_id。"""
    year = ctx["year"]
    orders = ctx["approval.ap_approve_order"]
    signals = ctx["risk.ap_warning_signal"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "approval.ap_approve_warn_rel") + 1):
        order = rng.choice(orders)
        sig = rng.choice(signals)
        rows.append(
            {
                "approve_warn_rel_id": f"AWR-{year:04d}-{seq:08d}",
                "approve_order_id": order["approve_order_id"],
                "warning_id": sig["warning_id"],
                "is_deleted": 0,
                "create_time": random_date(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_approve_todo_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """approval.ap_approve_todo 用户待办任务（原型 p_erms_approve_todo）：
    FK approve_task_id → ap_approve_task.approve_task_id。"""
    year = ctx["year"]
    tasks = ctx["approval.ap_approve_task"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "approval.ap_approve_todo") + 1):
        task = rng.choice(tasks)
        rows.append(
            {
                "approve_todo_id": f"TODO-{year:04d}-{seq:08d}",
                "approve_task_id": task["approve_task_id"],
                "user_id": f"U{rng.randint(1, 5000):05d}",
                "approve_todo_status": rng.choice(("UNHANDLED", "HANDLED", "INVALID")),
                "is_deleted": 0,
                "create_time": random_date(rng),
                "update_time": random_date(rng),
            }
        )
    return rows


def generate_ap_cust_query_log_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """project.ap_cust_query_log 客户查询记录日志（原型 p_erms_top_query_log）：独立日志，无 FK。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "project.ap_cust_query_log") + 1):
        rows.append(
            {
                "cust_query_log_id": f"QL-{year:04d}-{seq:08d}",
                "query_keyword": rng.choice(
                    (
                        "宏远",
                        "泰和",
                        "恒达",
                        "华夏新能源",
                        "集团授信",
                        "集中度",
                        "不良",
                        "押品",
                    )
                ),
                "create_user": f"U{rng.randint(1, 5000):05d}",
                "create_time": random_date(rng),
                "data_flag": rng.choice(("1", "2")),
            }
        )
    return rows


def generate_ap_serial_counter_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """project.ap_serial_counter 分布式流水号计数器（原型 p_serial_number_counter）：
    row_count=365 = 一年每日一条，current_counter 当日已用流水号。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    start = date(year, 1, 1)
    for seq in range(1, _row_count(ctx, "project.ap_serial_counter") + 1):
        day = start + timedelta(days=seq - 1)
        rows.append(
            {
                "serial_counter_id": f"SC-{year:04d}-{seq:03d}",
                "date_str": day.strftime("%Y%m%d"),
                "current_counter": rng.randint(1, 5000),
                "create_time": f"{day.isoformat()} 08:00:00",
                "update_time": f"{day.isoformat()} 18:00:00",
            }
        )
    return rows


# 本模块 9 表 DDL 注册（供 RISK_TABLE_SPECS 复用，字典 key = {system}.{table}）
APPROVAL_EXT_DDL: dict[str, str] = {
    "concentration.ap_concentration_limit_adj": RISK_EXT_DDL_2[
        "concentration.ap_concentration_limit_adj"
    ],
    "concentration.ap_concentration_warn_adj": RISK_EXT_DDL_2[
        "concentration.ap_concentration_warn_adj"
    ],
    "concentration.ap_codebt_customer": RISK_EXT_DDL_2[
        "concentration.ap_codebt_customer"
    ],
    "concentration.ap_codebt_warn_score": RISK_EXT_DDL_2[
        "concentration.ap_codebt_warn_score"
    ],
    "approval.ap_approve_oper_log": RISK_EXT_DDL_2["approval.ap_approve_oper_log"],
    "approval.ap_approve_warn_rel": RISK_EXT_DDL_2["approval.ap_approve_warn_rel"],
    "approval.ap_approve_todo": RISK_EXT_DDL_2["approval.ap_approve_todo"],
    "project.ap_cust_query_log": RISK_EXT_DDL_2["project.ap_cust_query_log"],
    "project.ap_serial_counter": RISK_EXT_DDL_2["project.ap_serial_counter"],
}
