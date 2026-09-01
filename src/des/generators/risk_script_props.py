"""S4 金控演示剧本道具数据 —— 口径包 v0.3 §一（资本常量）/§五（分布与案例常量）/§七（剧本道具数据）。

本模块 = S4 演示「端到端可验算」的确定性锚点（不依赖 RNG，可逐项回溯到口径包原文）：
- 资本常量（§一）：集团并表资本 800 亿；安平银行资本净额 600 亿/一级资本净额 480 亿、
  行内内部限额 60 亿；安平证券参考线内融资占比 5.5%（分母 400 亿）、安平资管 8.2%（分母 200 亿）；
  R1a 三线（§三）：关注线 9%（黄）/预警线 10%（橙）/内部限额 12%（红）。落 base.ap_sys_param。
- 剧本道具（§七）：天晟集团——安平银行 48 亿（8.0%）+安平证券 22 亿（5.5%）+安平资管 16.4 亿
  （8.2%）=归集 86.4 亿 → 10.8% 橙色预警；隐性一致行动人恒昌贸易 16 亿 → 102.4 亿 → 12.8% 红色预警；
  恒昌三条识别线索（股权代持线索/交叉担保链/资金往来异动）落客户关系树与相关表；小额黄档案例
  瑞华能源集团归集 75.2 亿（9.4%）走完整解除闭环（待确认→确认→处置→解除）。

金额单位约定：ap_subsidiary_credit_detail.business_balance 单位=万元（index_unit="万元"），
亿→万 = ×10000（如 48 亿 = 480000 万元）；口径包中 % 均为归集余额/集团并表资本 800 亿。

build_script_props(ctx) 由 generate.build_enterprise 在全量（scale=None）生成后调用，
把确定性道具行追加到 ctx 各表（RNG 表行数已在 _row_count 中扣除对应 prop 数，行数不变量保持）。
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 口径包 §一：资本常量（亿元 / 参考线，单位见注释；单一事实来源，落库 ap_sys_param）
# ---------------------------------------------------------------------------
# 集团并表资本（亿元）—— 集团层归集集中度分母
CAP_GROUP_CONSOLIDATED_YI = 800
# 安平银行：资本净额 / 一级资本净额 / 行内内部限额（银行层 10%）
CAP_BANK_NET_YI = 600
CAP_BANK_TIER1_YI = 480
CAP_BANK_INTERNAL_LIMIT_YI = 60
# 安平证券 / 安平资管：参考线内融资占比参考线 + 各自分母（参考线=融资额/分母）
CAP_SECURITIES_REF_LINE = 0.055  # 22 亿 / 400 亿 = 5.5%
CAP_SECURITIES_DENOM_YI = 400
CAP_AM_REF_LINE = 0.082  # 16.4 亿 / 200 亿 = 8.2%
CAP_AM_DENOM_YI = 200
# R1a 三线（集团层内部口径，§三）：关注线 9%（黄）/预警线 10%（橙）/内部限额 12%（红）
CAP_CONCERN_LINE = 0.09
CAP_WARN_LINE = 0.10
CAP_INTERNAL_LIMIT_RATIO = 0.12

# R1a 阈值/资本参数元数据（P0-1：可答「谁定的、怎么改」；param_id → 元数据列值）
PARAM_META: dict[str, dict[str, str]] = {
    "CAP_GROUP_CONSOLIDATED": {
        "param_source": "安平金控集团并表资本核算口径（2025 年度经审计并表）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元，集团层分母）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项（演示明细注明）",
    },
    "CAP_BANK_NET": {
        "param_source": "安平银行资本监管报表口径（2025 年末资本净额）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "单一集团客户授信余额（银行层口径）",
        "denominator_desc": "安平银行资本净额（600 亿元）",
        "netting_rule": "净额项按 2010 修订第十二条",
    },
    "CAP_BANK_TIER1": {
        "param_source": "安平银行大额风险暴露监管报表口径（2025 年末一级资本净额）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "风险暴露（大额风险暴露口径）",
        "denominator_desc": "安平银行一级资本净额（480 亿元）",
        "netting_rule": "2018 办法大额风险暴露口径",
    },
    "CAP_BANK_INTERNAL_LIMIT": {
        "param_source": "安平银行行内授信集中度内部限额（资本净额×10%）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "单一集团客户授信余额",
        "denominator_desc": "安平银行资本净额（600 亿元，×10% = 60 亿）",
        "netting_rule": "银行层内部限额（与集团层预警线 10% 同名不同分母，演示带绝对额）",
    },
    "CAP_SECURITIES_REF_LINE": {
        "param_source": "安平证券参考线内融资占比口径（融资额/参考线分母）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "证券子公司融资额",
        "denominator_desc": "证券参考线分母（400 亿元）",
        "netting_rule": "参考线口径（单看都安全）",
    },
    "CAP_SECURITIES_DENOM": {
        "param_source": "安平证券参考线分母（参考线内融资监测口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "证券子公司融资额",
        "denominator_desc": "证券参考线分母（400 亿元）",
        "netting_rule": "参考线口径",
    },
    "CAP_AM_REF_LINE": {
        "param_source": "安平资管参考线内融资占比口径（融资额/参考线分母）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "资管子公司融资额",
        "denominator_desc": "资管参考线分母（200 亿元）",
        "netting_rule": "参考线口径（单看都安全）",
    },
    "CAP_AM_DENOM": {
        "param_source": "安平资管参考线分母（参考线内融资监测口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "资管子公司融资额",
        "denominator_desc": "资管参考线分母（200 亿元）",
        "netting_rule": "参考线口径",
    },
    "CAP_CONCERN_LINE": {
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
    },
    "CAP_WARN_LINE": {
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
    },
    "CAP_INTERNAL_LIMIT_RATIO": {
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
    },
}

# 落库 base.ap_sys_param 的资本常量行（param_id → (类型, 值, 描述)）
CAPITAL_PARAMS: tuple[tuple[str, str, str, str], ...] = (
    ("CAP_GROUP_CONSOLIDATED", "GROUP_CAPITAL", "800",
     "集团并表资本（亿元，集团层归集集中度分母）"),
    ("CAP_BANK_NET", "GROUP_CAPITAL", "600", "安平银行资本净额（亿元，银行层 R1b 分母）"),
    ("CAP_BANK_TIER1", "GROUP_CAPITAL", "480", "安平银行一级资本净额（亿元，大额风险暴露分母）"),
    ("CAP_BANK_INTERNAL_LIMIT", "GROUP_CAPITAL", "60",
     "安平银行行内内部限额（亿元=资本净额×10%）"),
    ("CAP_SECURITIES_REF_LINE", "GROUP_CAPITAL", "0.055",
     "安平证券参考线内融资占比（5.5%=22亿/400亿）"),
    ("CAP_SECURITIES_DENOM", "GROUP_CAPITAL", "400", "安平证券参考线分母（亿元）"),
    ("CAP_AM_REF_LINE", "GROUP_CAPITAL", "0.082",
     "安平资管参考线内融资占比（8.2%=16.4亿/200亿）"),
    ("CAP_AM_DENOM", "GROUP_CAPITAL", "200", "安平资管参考线分母（亿元）"),
    ("CAP_CONCERN_LINE", "R1A_LINE", "0.09", "集团层关注线（9%，黄）"),
    ("CAP_WARN_LINE", "R1A_LINE", "0.10", "集团层预警线（10%，橙）"),
    ("CAP_INTERNAL_LIMIT_RATIO", "R1A_LINE", "0.12", "集团层内部限额（12%，红）"),
)

# ---------------------------------------------------------------------------
# 剧本道具主数据（§七）
# ---------------------------------------------------------------------------
# 集团（GRP-2026-9xxxxx，编码规则 4 定宽 6 位）
PROP_GROUPS = (
    ("GRP-2026-900001", "天晟集团有限公司"),
    ("GRP-2026-900002", "恒昌贸易集团有限公司"),
    ("GRP-2026-900003", "瑞华能源集团有限公司"),
)
# 单一客户（CID-2026-9xxxxxxx，8 位；internal_customer_no 同 8 位）
#   (customer_id, internal_customer_no, customer_no, name, group_no, group_name)
PROP_CUSTOMERS = (
    ("CID-2026-90000001", "APIN-2026-90000001", "CUST-2026-900001", "天晟实业有限公司", "GRP-2026-900001", "天晟集团有限公司"),
    ("CID-2026-90000002", "APIN-2026-90000002", "CUST-2026-900002", "恒昌贸易有限公司", "GRP-2026-900002", "恒昌贸易集团有限公司"),
    ("CID-2026-90000003", "APIN-2026-90000003", "CUST-2026-900003", "瑞华实业有限公司", "GRP-2026-900003", "瑞华能源集团有限公司"),
)
# 子公司授信明细（SC-2026-9xxxxx；amount 单位=万元；口径包 §七 数字道具）
#   (project_id, 客户customer_id, 客户名, 集团名, 机构名, business_balance万, 亿)
PROP_CREDITS = (
    ("SC-2026-900001", "CID-2026-90000001", "天晟实业有限公司", "天晟集团有限公司", "安平银行", 480000.0, 48.0),
    ("SC-2026-900002", "CID-2026-90000001", "天晟实业有限公司", "天晟集团有限公司", "安平证券", 220000.0, 22.0),
    ("SC-2026-900003", "CID-2026-90000001", "天晟实业有限公司", "天晟集团有限公司", "安平资产管理", 164000.0, 16.4),
    ("SC-2026-900004", "CID-2026-90000002", "恒昌贸易有限公司", "恒昌贸易集团有限公司", "安平银行", 160000.0, 16.0),
    ("SC-2026-900005", "CID-2026-90000003", "瑞华实业有限公司", "瑞华能源集团有限公司", "安平银行", 752000.0, 75.2),
)
# 剧本预警信号（WS-2026-9xxxxxxxx；level/事件/状态/事由 与口径包 §七 严格对应）
#   (warning_id, signal_id, customer_id, customer_name, group_no, group_name,
#    level, event_type, level2, signal_status, process_status, audit_status, warn_reason, risk_exposure万)
PROP_SIGNALS = (
    ("WS-2026-90000001", "SGN-2026-90000001", "CID-2026-90000001", "天晟实业有限公司",
     "GRP-2026-900001", "天晟集团有限公司", "橙", "信用风险", "集中度超限", "处置中",
     "方案执行中", "已审批",
     "天晟集团归集余额 86.4 亿元（安平银行 48 亿/安平证券 22 亿/安平资管 16.4 亿）÷ 集团并表资本 800 亿元 = 10.8% ≥ 预警线 10%，触发橙色预警（R1a 集团层归集集中度）",
     864000.0),
    ("WS-2026-90000002", "SGN-2026-90000002", "CID-2026-90000001", "天晟实业有限公司",
     "GRP-2026-900001", "天晟集团有限公司", "红", "信用风险", "集中度超限", "处置中",
     "已制定处置方案", "已审批",
     "经三条线索识别隐性一致行动人恒昌贸易（16 亿元）并纳入归集后，天晟归集余额 102.4 亿元 ÷ 800 亿元 = 12.8% > 内部限额 12%，触发红色预警（R1a+R2 关联客户组归集）",
     1024000.0),
    ("WS-2026-90000003", "SGN-2026-90000003", "CID-2026-90000003", "瑞华实业有限公司",
     "GRP-2026-900003", "瑞华能源集团有限公司", "黄", "信用风险", "集中度超限", "已关闭",
     "已解除", "已审批",
     "瑞华能源集团归集余额 75.2 亿元 ÷ 集团并表资本 800 亿元 = 9.4% ≥ 关注线 9%，触发黄色预警（R1a）；已走完确认→处置→解除闭环",
     752000.0),
)
# 恒昌三条识别线索（§七：股权代持线索/交叉担保链/资金往来异动；落客户关系树 + 相关表）
#   (tree_id, relation_id, clue_text, data_source)
PROP_CLUES = (
    ("RT-2026-900001", "REL-2026-900001",
     "股权代持线索：恒昌贸易大股东张伟与天晟实业存在股权代持关系（登记股东名义持股 35%，实控人系天晟方一致行动人）",
     "工商信息"),
    ("RT-2026-900002", "REL-2026-900002",
     "交叉担保链：恒昌贸易与天晟系企业互为担保人，交叉担保余额合计约 12 亿元，担保圈可闭环追溯",
     "征信系统"),
    ("RT-2026-900003", "REL-2026-900003",
     "资金往来异动：近 6 个月恒昌贸易与天晟系资金往来净额显著上升至约 8.6 亿元，超出历史均值 3 倍",
     "行内监测"),
)
# 集中度限额道具（concentration.ap_concentration_limit；归集余额/预警线 单位=万元）
#   (id, customer_no, customer_name, 归集余额万, 预警线万, 状态) —— 天晟 10.8% 橙 / 瑞华 9.4% 黄
#   P1-2：状态用中文「橙/黄」（口径包§八，不再用 ORANGE_ALERT/YELLOW_ALERT）
PROP_CONCENTRATION = (
    ("CL-2026-900001", "CUST-2026-900001", "天晟实业有限公司", 864000.0, 800000.0, "橙"),
    ("CL-2026-900002", "CUST-2026-900003", "瑞华实业有限公司", 752000.0, 720000.0, "黄"),
)
# 处置跟踪道具（ap_warning_disposal；瑞华走完整闭环=已处置，天晟结束于处置中/已督办）
#   (disposal_id, warning_id, disposal_status, disposal_progress)
PROP_DISPOSALS = (
    ("WD-2026-900001", "WS-2026-90000001", "处置中", "已制定处置方案，冻结未用额度并追加押品，向附属机构督办"),
    ("WD-2026-900002", "WS-2026-90000002", "处置中", "红色预警：立即报告监管+银团/联合贷款压降计划，按月催办"),
    ("WD-2026-900003", "WS-2026-90000003", "已处置", "已完成处置并解除（close_warning+解除报告），风险敞口已压降"),
)

# 剧本审批道具（§七 第 4 幕：天晟红警 WS-2026-90000002 下挂 PROCESS 审批单——
# AI 拆分授信提议 → 审批人按 2023 关联交易办法第二十三条 REJECTED + 审计落库）
#   (approve_order_id, title, apply_user_id, apply_time, status, business_type, remark, opinion)
PROP_APPROVE_ORDER = (
    ("APP-2026-90000002", "天晟集团处置方案审批（拆分授信提议）", "U90002",
     "2026-12-10", "PROCESS", "SGN_CONCENTRAT",
     "对预警信号 SGN-2026-90000002 申请处置审批：AI 提议将天晟部分授信拆分至非关联第三方通道主体，降低名义归集集中度",
     None),
)
#   (approve_task_id, approve_order_id, approve_task_status, approve_result, approve_remark)
# 待审批任务用 PENDING（与 RNG approve_flow 末节点一致；approve_disposal 只标记 PENDING 任务）
PROP_APPROVE_TASK = (
    ("AT-2026-90000002", "APP-2026-90000002", "PENDING", None, None),
)
#   (approve_warn_rel_id, approve_order_id, warning_id)
PROP_APPROVE_WARN_REL = (
    ("AWR-2026-90000002", "APP-2026-90000002", "WS-2026-90000002"),
)

# 各表道具行数（RNG 生成器行数 = 配置 row_count - 本表 prop 数；全量时注入）
SCRIPT_PROP_COUNTS: dict[str, int] = {
    "customer.ap_group_customer": len(PROP_GROUPS),
    "customer.ap_customer": len(PROP_CUSTOMERS),
    "customer.ap_subsidiary_credit_detail": len(PROP_CREDITS),
    "customer.ap_customer_relation_tree": len(PROP_CLUES),
    "customer.ap_customer_relation": len(PROP_CLUES),
    "risk.ap_warning_signal": len(PROP_SIGNALS),
    "risk.ap_warning_disposal": len(PROP_DISPOSALS),
    "concentration.ap_concentration_limit": len(PROP_CONCENTRATION),
    "approval.ap_approve_order": len(PROP_APPROVE_ORDER),
    "approval.ap_approve_task": len(PROP_APPROVE_TASK),
    "approval.ap_approve_warn_rel": len(PROP_APPROVE_WARN_REL),
    "base.ap_sys_param": len(CAPITAL_PARAMS),
}

# ---------------------------------------------------------------------------
# 道具行构建（全字段对齐 DDL，确定性无 RNG；build_script_props 返回 表 → 行列表）
# ---------------------------------------------------------------------------
_TS = "2026-01-01"
_CERTS = {
    "天晟实业有限公司": "91310000111122221",
    "恒昌贸易有限公司": "91310000333344442",
    "瑞华实业有限公司": "91310000555566663",
}
_INNER_BY_CID = {c[0]: c[1] for c in PROP_CUSTOMERS}


def _group_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (gno, gname) in enumerate(PROP_GROUPS, start=1):
        rows.append(
            {
                "group_customer_no": gno,
                "data_date": _TS,
                "group_customer_name": gname,
                "customer_status": "正常",
                "group_peer_flag": 0,
                "asset_quality_level_code": "1",
                "asset_quality_level": "正常",
                "create_user": "SYSTEM",
                "create_time": _TS,
                "create_org_no": f"ORG{seq:03d}",
                "update_user": "SYSTEM",
                "update_time": _TS,
                "update_org_no": f"ORG{seq:03d}",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def _customer_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (cid, inner, custno, cname, gno, gname) in enumerate(PROP_CUSTOMERS, start=1):
        rows.append(
            {
                "customer_id": cid,
                "data_date": _TS,
                "upstream_update_time": _TS,
                "org_id": f"ORG{seq:03d}",
                "org_name": "安平银行",
                "customer_no": custno,
                "customer_name": cname,
                "group_customer_no": gno,
                "group_customer_name": gname,
                "cert_type": "统一社会信用代码",
                "cert_no": _CERTS[cname],
                "internal_customer_no": inner,
                "internal_level": "AA",
                "external_level": "AA",
                "zone_id": "310000",
                "zone_name": "上海市",
                "zone_level": "A",
                "country_id": "CN",
                "country_name": "中国",
                "industry_id": "C",
                "industry_name": "制造业",
                "industry_level": "稳定",
                "asset_quality_level_code": "1",
                "asset_quality_level": "正常",
                "related_party_ind": 1,
                "peer_flag": 0,
                "enterprise_nature": "民营",
                "enterprise_scale": "大型",
                "establish_time": "2008-06-18",
                "registered_capital": 100000.0,
                "shareholder_name_1": "张伟",
                "shareholder_ratio_1": 35.0,
                "shareholder_name_2": "李强",
                "shareholder_ratio_2": 25.0,
                "shareholder_name_3": "王芳",
                "shareholder_ratio_3": 15.0,
                "chairman_name": "张伟",
                "supervisor_name": "李强",
                "finance_head_name": "王芳",
                "general_manager_name": "刘洋",
                "invest_company_1": "安平资产管理",
                "invest_amount_1": 50000.0,
                "invest_currency_name_1": "人民币",
                "invest_ratio_1": 30.0,
                "invest_company_2": "",
                "invest_amount_2": 0.0,
                "invest_currency_name_2": "人民币",
                "invest_ratio_2": 0.0,
                "invest_company_3": "",
                "invest_amount_3": 0.0,
                "invest_currency_name_3": "人民币",
                "invest_ratio_3": 0.0,
                "customer_status": "正常",
                "final_score": 72.0,
                "final_score_level": "中",
                "industry_commerce_score_level": "良",
                "trading_score_level": "良",
                "credit_score_level": "良",
                "credit_reference_score_level": "良",
                "financial_score_level": "良",
                "industry_commerce_index": 70.0,
                "trading_index": 65.0,
                "credit_index": 75.0,
                "credit_reference_index": 68.0,
                "financial_index": 72.0,
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "clear_remark_4": None,
                "create_user": "SYSTEM",
                "create_time": _TS,
                "create_org_no": f"ORG{seq:03d}",
                "update_user": "SYSTEM",
                "update_time": _TS,
                "update_org_no": f"ORG{seq:03d}",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows

def _credit_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (pid, cid, cname, gname, org, bal_wan, _yi) in enumerate(PROP_CREDITS, start=1):
        row = {
            "project_id": pid,
            "data_date": _TS,
            "upstream_update_time": _TS,
            "org_id": f"ORG{seq:03d}",
            "org_name": org,
            "project_name": f"{cname}{org}授信项目",
            "customer_name": cname,
            "group_customer_name": gname,
            "group_customer_name_processed": gname,
            "group_peer_flag": 0,
            "cert_type_code": "统一社会信用代码",
            "cert_type": "统一社会信用代码",
            "cert_no": _CERTS[cname],
            "internal_customer_no": _INNER_BY_CID[cid],
            "internal_level": "AA",
            "external_level": "AA",
            "zone_id": "310000",
            "zone_name": "上海市",
            "zone_level": "A",
            "country_id": "CN",
            "country_name": "中国",
            "industry_id": "C",
            "industry_name": "制造业",
            "industry_level": "稳定",
            "related_party_ind": 1,
            "peer_flag": 0,
            "enterprise_nature_code": "A",
            "enterprise_nature": "民营",
            "enterprise_scale": "大型",
            "establish_time": "2008-06-18",
            "registered_capital": 100000.0,
            "business_type_code": "PL01",
            "business_type": "流动资金贷款",
            "business_product_code": "PL01",
            "business_product_name": "流动资金贷款",
            "internal_business_product_code": "IP01",
            "internal_business_product_name": "公司流贷",
            "currency_id": "CNY",
            "index_unit": "万元",
            "business_balance": bal_wan,
            "risk_exposure": bal_wan,
            "pledge_value": round(bal_wan * 0.3, 2),
            "guarantee_value": round(bal_wan * 0.2, 2),
            "impairment_provision": 0.0,
            "principal_overdue_days": 0,
            "interest_overdue_days": 0,
            "asset_quality_level_code": "1",
            "asset_quality_level": "正常",
            "limit_value": bal_wan,
            "shareholder_name_1": "张伟",
            "shareholder_ratio_1": 35.0,
            "shareholder_name_2": "李强",
            "shareholder_ratio_2": 25.0,
            "shareholder_name_3": "王芳",
            "shareholder_ratio_3": 15.0,
            "chairman_name": "张伟",
            "supervisor_name": "李强",
            "finance_head_name": "王芳",
            "general_manager_name": "刘洋",
            "invest_company_1": "安平资产管理",
            "invest_amount_1": 50000.0,
            "invest_currency_name_1": "人民币",
            "invest_ratio_1": 30.0,
            "invest_company_2": "",
            "invest_amount_2": 0.0,
            "invest_currency_name_2": "人民币",
            "invest_ratio_2": 0.0,
            "invest_company_3": "",
            "invest_amount_3": 0.0,
            "invest_currency_name_3": "人民币",
            "invest_ratio_3": 0.0,
            "customer_status": "正常",
            "final_score": 72.0,
            "final_score_level": "中",
            "industry_commerce_score_level": "良",
            "trading_score_level": "良",
            "credit_score_level": "良",
            "credit_reference_score_level": "良",
            "financial_score_level": "良",
            "industry_commerce_index": 70.0,
            "trading_index": 65.0,
            "credit_index": 75.0,
            "credit_reference_index": 68.0,
            "financial_index": 72.0,
            "operate_type": "新增",
            "clear_remark_1": None,
            "clear_remark_2": None,
            "clear_remark_3": None,
            "clear_remark_4": None,
        }
        rows.append(row)
    return rows

def _signal_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (
        wid, sid, cid, cname, gno, gname, level, event_type, level2,
        sig_status, proc_status, audit_status, reason, risk_exp,
    ) in enumerate(PROP_SIGNALS, start=1):
        rows.append(
            {
                "warning_id": wid,
                "data_date": "2026-11-30",
                "customer_id": cid,
                "customer_name": cname,
                "org_id": f"ORG{seq:03d}",
                "org_name": "安平集团总部",
                "belong_group": gname,
                "warn_level": level,
                "event_type": event_type,
                "warn_source": "模型预警",
                "warn_reason": reason,
                "signal_way": "系统自动",
                "sys_proposal_signal_grade": level,
                "signal_id": sid,
                "signal_name": f"{event_type}-{level2}预警信号",
                "signal_status": sig_status,
                "signal_level1_topic": event_type,
                "signal_level2_topic": level2,
                "signal_description": f"{cname} {event_type}（{level2}）监测异常，{level}预警",
                "signal_generate_date": "2026-11-30",
                "signal_establish_date": "2026-11-30",
                "signal_establish_operator": "系统",
                "signal_update_date": "2026-12-15",
                "data_source": "内部系统",
                "is_important_customer": 1,
                "info_type": 1,
                "user_num": "U00001",
                "to_user": "U00001",
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "update_time": "2026-12-15",
                "update_user": "系统",
                "del_ind": 0,
                "push_warn_reason": reason,
                "invest_balance": risk_exp,
                "cert_type_code": "统一社会信用代码",
                "cert_no": _CERTS[cname],
                "biz_date": "2026-11-30",
                "group_customer_no": gno,
                "group_customer_type": "单一集团",
                "risk_exposure": risk_exp,
                "disposal_status": "处置中" if sig_status == "处置中" else "已处置",
                "disposal_demand": "立即处置" if level == "红" else "10 个工作日内处置完毕",
                "apply_no": None,
                "apply_comment": None,
                "process_status": proc_status,
                "audit_status": audit_status,
                "audit_comment": (
                    "预警已人工确认定级，审批通过，进入处置流程"
                    if audit_status == "已审批"
                    else None
                ),
                "is_shared": 1,
            }
        )
    return rows


def _relation_tree_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    hc = next(c for c in PROP_CUSTOMERS if c[3] == "恒昌贸易有限公司")
    for seq, (tid, _rel, clue, source) in enumerate(PROP_CLUES, start=1):
        rows.append(
            {
                "customer_relation_tree_id": tid,
                "upstream_update_time": _TS,
                "org_id": "ORG001",
                "org_name": "安平集团总部",
                "cert_type_code": "统一社会信用代码",
                "cert_no": _CERTS["恒昌贸易有限公司"],
                "customer_name": "恒昌贸易有限公司",
                "internal_customer_no": hc[1],
                "group_cert_type_code": "统一社会信用代码",
                "group_cert_no": _CERTS["天晟实业有限公司"],
                "group_customer_name": "天晟集团有限公司",
                "data_source": source,
                "clear_remark_1": clue if seq == 1 else None,
                "clear_remark_2": clue if seq == 2 else None,
                "clear_remark_3": clue if seq == 3 else None,
                "clear_remark_4": None,
                "create_user": "系统",
                "create_time": _TS,
                "create_org_no": "ORG001",
                "update_user": "系统",
                "update_time": _TS,
                "update_org_no": "ORG001",
                "is_important_group_customer": 1,
                "effective_date": _TS,
                "invalid_date": "2999-12-31",
                "current_status": "有效",
                "cert_type_code_from_bank": "统一社会信用代码",
                "cert_no_from_bank": _CERTS["恒昌贸易有限公司"],
            }
        )
    return rows


def _relation_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    hc = next(c for c in PROP_CUSTOMERS if c[3] == "恒昌贸易有限公司")
    for seq, (_tid, rel, clue, source) in enumerate(PROP_CLUES, start=1):
        rows.append(
            {
                "customer_relation_id": rel,
                "data_date": _TS,
                "upstream_update_time": _TS,
                "org_id": "ORG001",
                "org_name": "安平集团总部",
                "cert_type_code": "统一社会信用代码",
                "cert_no": _CERTS["恒昌贸易有限公司"],
                "customer_name": "恒昌贸易有限公司",
                "internal_customer_no": hc[1],
                "group_cert_type_code": "统一社会信用代码",
                "group_cert_no": _CERTS["天晟实业有限公司"],
                "group_customer_name": "天晟集团有限公司",
                "data_source": source,
                "operate_type": "新增",
                "clear_remark_1": clue if seq == 1 else None,
                "clear_remark_2": clue if seq == 2 else None,
                "clear_remark_3": clue if seq == 3 else None,
                "clear_remark_4": None,
                "create_time": _TS,
                "create_org_no": "ORG001",
                "update_user": "系统",
                "update_time": _TS,
                "update_org_no": "ORG001",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def _concentration_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (clid, custno, cname, balance, warn_line, status) in enumerate(
        PROP_CONCENTRATION, start=1
    ):
        rows.append(
            {
                "concentration_limit_id": clid,
                "customer_no": custno,
                "customer_name": cname,
                "warning_value": warn_line,
                "concentration_limit": balance,
                "concentration_limit_old": balance,
                "create_user": "SYSTEM",
                "create_time": _TS,
                "update_user": "SYSTEM",
                "update_time": _TS,
                "version": "1.0",
                "tenant_id": "AP001",
                "current_status": status,
            }
        )
    return rows


def _disposal_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, (did, wid, status, progress) in enumerate(PROP_DISPOSALS, start=1):
        rows.append(
            {
                "disposal_id": did,
                "warning_id": wid,
                "disposal_status": status,
                "disposal_progress": progress,
                "disposal_time": "2026-12-10",
                "operator_user": "系统",
                "operate_time": "2026-12-15",
            }
        )
    return rows


def _approve_order_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for _seq, (
        oid, title, apply_user, apply_time, status, btype, remark, opinion,
    ) in enumerate(PROP_APPROVE_ORDER, start=1):
        rows.append(
            {
                "approve_order_id": oid,
                "approve_order_type": "WARN_SGN",
                "approve_order_title": title,
                "apply_user_id": apply_user,
                "approved_user_id": "" if status == "PROCESS" else "U90003",
                "apply_time": apply_time,
                "approve_time": None if status == "PROCESS" else apply_time,
                "approve_order_status": status,
                "business_type": btype,
                "remark": remark,
                "is_deleted": 0,
                "create_time": apply_time,
                "update_time": apply_time,
                "derive_warn_level_red": 1,
                "derive_warn_level_yellow": 0,
                "derive_warn_level_blue": 0,
                "opinion_description": opinion,
            }
        )
    return rows


def _approve_task_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = ctx.get("approval.ap_approve_node") or []
    node = (
        {"approve_node_id": "NODE-2026-000001", "post_id": "POST-RISK-MGMT"}
        if not nodes
        else nodes[0]
    )
    rows = []
    for _seq, (tid, oid, status, result, remark) in enumerate(
        PROP_APPROVE_TASK, start=1
    ):
        rows.append(
            {
                "approve_task_id": tid,
                "approve_order_id": oid,
                "approve_node_id": node["approve_node_id"],
                "post_id": node["post_id"],
                "approve_task_status": status,
                "approve_result": result,
                "approve_remark": remark,
                "approve_time": None,
                "is_deleted": 0,
                "create_time": "2026-12-10",
                "update_time": "2026-12-10",
            }
        )
    return rows


def _approve_warn_rel_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for _seq, (rid, oid, wid) in enumerate(PROP_APPROVE_WARN_REL, start=1):
        rows.append(
            {
                "approve_warn_rel_id": rid,
                "approve_order_id": oid,
                "warning_id": wid,
                "is_deleted": 0,
                "create_time": "2026-12-10",
                "update_time": "2026-12-10",
            }
        )
    return rows


def _sys_param_rows(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    year = ctx["year"]
    rows = []
    for seq, (pid, ptype, value, desc) in enumerate(CAPITAL_PARAMS, start=1):
        meta = PARAM_META.get(pid, {})
        rows.append(
            {
                "sys_param_id": f"SP-{year:04d}-{900000 + seq:05d}",
                "param_type_code": "CAPITAL",
                "param_type_name": "资本与限额常量",
                "param_id": pid,
                "param_value": value,
                "param_description": desc,
                "whether_cache": 1,
                "create_time": _TS,
                "create_user": "SYSTEM",
                "update_time": "2026-11-30",  # 元数据：数据时点后的最近更新时间
                "update_user": "系统初始化",  # 根因二：SYSTEM 更新人改中性文案
                "extended_id": None,
                "del_ind": 0,
                "version": "v3",  # 根因二：版本 in-universe（安平风管部审批版本）
                "tenant_id": "AP001",
                "param_source": meta.get("param_source"),
                "param_approver": meta.get("param_approver"),
                "numerator_desc": meta.get("numerator_desc"),
                "denominator_desc": meta.get("denominator_desc"),
                "netting_rule": meta.get("netting_rule"),
            }
        )
    return rows


# 表 → 道具行构建器（仅含带道具的表）
_PROP_BUILDERS: dict[str, Any] = {
    "customer.ap_group_customer": _group_rows,
    "customer.ap_customer": _customer_rows,
    "customer.ap_subsidiary_credit_detail": _credit_rows,
    "customer.ap_customer_relation_tree": _relation_tree_rows,
    "customer.ap_customer_relation": _relation_rows,
    "risk.ap_warning_signal": _signal_rows,
    "risk.ap_warning_disposal": _disposal_rows,
    "concentration.ap_concentration_limit": _concentration_rows,
    "approval.ap_approve_order": _approve_order_rows,
    "approval.ap_approve_task": _approve_task_rows,
    "approval.ap_approve_warn_rel": _approve_warn_rel_rows,
    "base.ap_sys_param": _sys_param_rows,
}


def build_script_props(ctx: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """返回 表 → 确定性道具行列表（全量生成时追加到 ctx；小 scale 不调用）。"""
    return {tid: _PROP_BUILDERS[tid](ctx) for tid in SCRIPT_PROP_COUNTS}
