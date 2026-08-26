"""金融风控行业专用生成函数 —— 安平金控 12 张核心表（6 系统 6 库）确定性生成。

依据 docs/S3-M1b-DES金融化设计-v1.md（§四 金融专用生成函数）+ docs/S3-安平金控-业务规则建模-v1.md（DMN 规则 1-7）
+ docs/S3-M1a-字段脱敏映射-脊柱12表.json（字段）。复用 S2 确定性基建：每表独立 RNG 流、主键升序、
纯函数派生、拓扑序生成（ctx 缓存上游表确定性引用）；无外部依赖（标准库 random + 业务池）。
- 编码规则（规则 4）：CUST/GRP-YYYY-6 位；SGN/APP/PROJ/COL/DSP-YYYY-8 位；
- 预警等级（规则 1）：warn_level_decide + 按等级反推输入的 _warn_inputs_for_level（分布可机验）；
- 五级分类（规则 2）：five_category_assign + 按分类反推输入的 _five_class_inputs；
- 集中度（规则 3）：concentration_calc（敞口/资本净额 → 正常/黄警/橙警/红警 + 是否需审批）；
- 押品估值（含贬值注入）collateral_val、跨板块敞口 exposure_sim、审批链状态推进 approve_flow、
  共债关联 codebt_link（§四 函数清单）。
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# 确定性锚点
# ---------------------------------------------------------------------------
ANCHOR_START = date(2023, 1, 1)  # 业务数据窗口（信号/处置/审批）
ANCHOR_END = date(2026, 12, 31)
ESTAB_START, ESTAB_END = 1990, 2020  # 企业成立年份窗口

# ---------------------------------------------------------------------------
# 业务词表池（标准库 random 确定性生成；不依赖个人经验，来源 = 规则建模 + 通用业务认知）
# ---------------------------------------------------------------------------
ORG_POOL = (
    "安平集团总部",
    "安平银行",
    "安平证券",
    "安平信托",
    "安平保险",
    "安平租赁",
    "安平保理",
    "安平期货",
    "安平资产管理",
    "安平消费金融",
)
CUST_NAME_POOL = (
    "宏远实业",
    "泰和能源",
    "中科智造",
    "恒达地产",
    "远航物流",
    "金诚贸易",
    "蓝海科技",
    "华信建设",
    "鼎盛矿业",
    "瑞丰食品",
    "嘉源化工",
    "正大纺织",
    "盛世文旅",
    "东方商贸",
    "康德医药",
    "裕隆装备",
    "翔宇电子",
    "联发建材",
    "汇通汽贸",
    "天晟农业",
)
CUST_NAME_SUFFIX = ("有限公司", "集团", "股份公司", "有限责任公司", "控股集团")
GROUP_SUFFIX = ("集团有限公司", "控股集团有限公司", "产业发展集团", "实业集团")
FAMILY_NAMES = (
    "王",
    "李",
    "张",
    "刘",
    "陈",
    "杨",
    "黄",
    "赵",
    "周",
    "吴",
    "徐",
    "孙",
    "马",
    "朱",
)
GIVEN_NAMES = (
    "伟",
    "芳",
    "娜",
    "敏",
    "静",
    "磊",
    "军",
    "洋",
    "勇",
    "艳",
    "杰",
    "涛",
    "明",
    "超",
    "霞",
    "平",
    "刚",
    "华",
)
ZONE_POOL = (
    ("310000", "上海市"),
    ("330100", "杭州市"),
    ("320100", "南京市"),
    ("110000", "北京市"),
    ("440300", "深圳市"),
    ("440100", "广州市"),
    ("510100", "成都市"),
    ("370200", "青岛市"),
    ("210100", "沈阳市"),
    ("120000", "天津市"),
    ("420100", "武汉市"),
    ("500000", "重庆市"),
)
INDUSTRY_POOL = (
    ("C", "制造业"),
    ("D", "电力热力燃气及水生产和供应业"),
    ("E", "建筑业"),
    ("F", "批发和零售业"),
    ("G", "交通运输仓储和邮政业"),
    ("I", "信息传输软件和信息技术服务业"),
    ("K", "房地产业"),
    ("L", "租赁和商务服务业"),
    ("M", "科学研究和技术服务业"),
)
SCORE_LEVEL_POOL = ("优", "良", "中", "差")
ZONE_LEVEL_POOL = ("A", "B", "C")
INDUSTRY_LEVEL_POOL = ("朝阳", "稳定", "衰退")
ENTERPRISE_NATURE_POOL = ("民营", "国有", "外资", "股份制", "集体")
ENTERPRISE_SCALE_POOL = ("大型", "中型", "小型", "微型")
INTERNAL_LEVEL_POOL = ("AAA", "AA", "A", "BBB", "BB", "B", "CCC")
EXTERNAL_LEVEL_POOL = ("AAA", "AA", "A", "BBB", "BB")
# 资产质量分布（客户/集团，正常为主；代码 1-5）
CUST_QUALITY_DIST = (
    ("1", "正常", 0.85),
    ("2", "关注", 0.10),
    ("3", "次级", 0.03),
    ("4", "可疑", 0.015),
    ("5", "损失", 0.005),
)
# 预警等级分布（事实表整体：蓝为主）
WARN_LEVEL_DIST = (("BLUE", 0.70), ("YELLOW", 0.25), ("RED", 0.05))
# 五级分类分布（风险项目：明显偏险）
FIVE_CLASS_DIST = (
    ("NORMAL", 0.55),
    ("ATTENTION", 0.28),
    ("SECONDARY", 0.11),
    ("DOUBTFUL", 0.045),
    ("LOSS", 0.015),
)
# 预警一级/二级主题（规则 5）
LEVEL1_TOPICS = ("信用风险", "市场风险", "操作风险", "流动性风险", "合规风险")
LEVEL2_BY_L1 = {
    "信用风险": ("逾期", "欠息", "押品贬值", "关联交易", "涉诉", "评级下调"),
    "市场风险": ("价格波动", "汇率波动", "利率上升", "估值下跌"),
    "操作风险": ("内控缺陷", "人员舞弊", "系统故障", "数据异常"),
    "流动性风险": ("现金流缺口", "融资受阻", "集中度超限", "期限错配"),
    "合规风险": ("监管处罚", "诉讼", "资质缺失", "信息披露违规"),
}
WARN_SOURCE_POOL = (
    "行内监测",
    "征信系统",
    "工商信息",
    "司法涉诉",
    "媒体报道",
    "现场检查",
    "模型预警",
)
SIGNAL_WAY_POOL = ("系统自动", "人工录入", "批量导入")
DATA_SOURCE_POOL = ("内部系统", "外部数据", "监管报送")
SIGNAL_STATUS_POOL = ("待确认", "确认中", "已确认", "已关闭", "已撤销")
DISPOSAL_STATUS_POOL = ("未处置", "处置中", "已处置", "暂缓处置")
CERT_TYPE_CODE = "统一社会信用代码"
# 处置业务类型（字典项 P060）
BUSINESS_TYPE_POOL = ("SGN_DERIVE", "SGN_DEVIATION", "SGN_CONCENTRAT")
BUSINESS_TYPE_WEIGHTS = (0.5, 0.3, 0.2)
# 处置措施类型（规则 6）
DEAL_TYPE_POOL = (
    "SUBMIT_REVIEW",
    "MGMT_REVIEW",
    "SUBMIT_APPROVE",
    "DEPT_LEADER_APPROVE",
    "WARN_REASON_UPDATE",
    "PUSH_SUBSIDIARY",
    "PUSH_HOLDING_LEADER",
    "LEADER_OPINION",
)
# 审批岗位链（规则 7：NODE_SEQ 1-3）
APPROVE_POST_DEFS = (
    (1, "POST-RISK-MGMT", "风险预警管理岗审核", "ANY_ONE"),
    (2, "POST-RISK-DIR", "风控部门负责人审核", "ANY_ONE"),
    (3, "POST-GROUP-CRO", "集团风控领导审批", "ALL"),
)
ORDER_STATUS_DIST = (("APPROVED", 0.60), ("PROCESS", 0.30), ("REJECTED", 0.10))
DIVISION_POOL = ("授信管理部", "风险监控部", "合规部", "不良资产管理部", "集团风控部")
GUARANTEE_METHOD_POOL = ("信用", "抵押", "质押", "保证", "组合担保")
# 集中度监管阈值（规则 3）：≤10% 正常 / ≤15% 黄警 / ≤25% 橙警 / >25% 红警
CONCENTRATION_NORMAL, CONCENTRATION_WARN, CONCENTRATION_ORANGE = 0.10, 0.15, 0.25
# 指标库（base.ap_dim_metric 指标名/单位）
METRIC_DEFS = (
    ("M001", "集团对外融资余额", "亿元"),
    ("M002", "集中度敞口占比", "%"),
    ("M003", "逾期贷款余额", "亿元"),
    ("M004", "不良贷款率", "%"),
    ("M005", "拨备覆盖率", "%"),
    ("M006", "风险暴露额", "亿元"),
    ("M007", "押品估值覆盖率", "%"),
    ("M008", "预警信号数", "个"),
)


# ---------------------------------------------------------------------------
# 编码规则（DMN 规则 4）
# ---------------------------------------------------------------------------
def _code(prefix: str, year: int, seq: int, width: int) -> str:
    """通用定宽顺序码 {prefix}-{YYYY}-{NNNN…}（width 位流水）。"""
    return f"{prefix}-{year:04d}-{seq:0{width}d}"


def anping_cust_no(year: int, seq: int) -> str:
    """客户号 CUST-{YYYY}-{6位}（规则 4）。"""
    return _code("CUST", year, seq, 6)


def anping_grp_no(year: int, seq: int) -> str:
    """集团客户号 GRP-{YYYY}-{6位}。"""
    return _code("GRP", year, seq, 6)


def anping_sgn_no(year: int, seq: int) -> str:
    """预警信号号 SGN-{YYYY}-{8位}。"""
    return _code("SGN", year, seq, 8)


def anping_app_no(year: int, seq: int) -> str:
    """审批单号 APP-{YYYY}-{8位}。"""
    return _code("APP", year, seq, 8)


def anping_proj_no(year: int, seq: int) -> str:
    """风险项目号 PROJ-{YYYY}-{8位}。"""
    return _code("PROJ", year, seq, 8)


def anping_col_no(year: int, seq: int) -> str:
    """押品编号 COL-{YYYY}-{8位}。"""
    return _code("COL", year, seq, 8)


def anping_dsp_no(year: int, seq: int) -> str:
    """处置编号 DSP-{YYYY}-{8位}。"""
    return _code("DSP", year, seq, 8)


# ---------------------------------------------------------------------------
# DMN 规则函数（规则 1-3，纯函数可机验）
# ---------------------------------------------------------------------------
def warn_level_decide(
    risk_score: float,
    collateral_depreciation: float = 0.0,
    concentration_overrun: float = 0.0,
    related_change: float = 0.0,
) -> str:
    """规则 1 预警等级判定：押品贬值 ≥30% 或 集中度超限 ≥20% 或 风险评分 ≥80 → RED；
    押品贬值 15-30% 或 集中度超限 10-20% 或 关联异动 20-50% 或 风险评分 60-80 → YELLOW；否则 BLUE。"""
    if (
        collateral_depreciation >= 0.30
        or concentration_overrun >= 0.20
        or risk_score >= 80
    ):
        return "RED"
    if (
        0.15 <= collateral_depreciation < 0.30
        or 0.10 <= concentration_overrun < 0.20
        or 0.20 <= related_change < 0.50
        or 60 <= risk_score < 80
    ):
        return "YELLOW"
    return "BLUE"


def five_category_assign(
    overdue_days: int,
    impairment_ratio: float = 0.0,
    has_risk_event: bool = False,
    confirmed_loss: bool = False,
) -> str:
    """规则 2 五级分类：逾期 >360 或 已确认损失 → LOSS；181-360 → DOUBTFUL；
    91-180 或 减值 ≥30% → SECONDARY；1-90 或有预警未处置 → ATTENTION；否则 NORMAL。"""
    if overdue_days > 360 or confirmed_loss:
        return "LOSS"
    if 181 <= overdue_days <= 360:
        return "DOUBTFUL"
    if 91 <= overdue_days <= 180 or impairment_ratio >= 0.30:
        return "SECONDARY"
    if 1 <= overdue_days <= 90 or has_risk_event:
        return "ATTENTION"
    return "NORMAL"


def concentration_calc(exposure: float, net_capital: float) -> dict[str, Any]:
    """规则 3 大额客户集中度：敞口/资本净额 → {ratio,status,warn_level,need_approval}。"""
    ratio = exposure / net_capital if net_capital > 0 else 1.0
    if ratio > CONCENTRATION_ORANGE:
        return {
            "ratio": ratio,
            "status": "RED_ALERT",
            "warn_level": "RED",
            "need_approval": True,
        }
    if ratio > CONCENTRATION_WARN:
        return {
            "ratio": ratio,
            "status": "ORANGE_ALERT",
            "warn_level": "ORANGE",
            "need_approval": True,
        }
    if ratio > CONCENTRATION_NORMAL:
        return {
            "ratio": ratio,
            "status": "YELLOW_ALERT",
            "warn_level": "YELLOW",
            "need_approval": False,
        }
    return {
        "ratio": ratio,
        "status": "NORMAL",
        "warn_level": "NONE",
        "need_approval": False,
    }


# ---------------------------------------------------------------------------
# 金融专用生成函数（§四）
# ---------------------------------------------------------------------------
def collateral_val(rng: random.Random, base_value: float) -> dict[str, float]:
    """押品估值（含贬值注入）：~6% 概率大幅贬值 ≥30%（触发规则 1 红档），否则小幅波动。"""
    if rng.random() < 0.06:
        dep = round(rng.uniform(0.30, 0.50), 4)
    else:
        dep = round(rng.uniform(0.0, 0.14), 4)
    return {
        "collateral_value": round(base_value * (1 - dep), 2),
        "depreciation_rate": dep,
    }


def exposure_sim(rng: random.Random, base_balance: float) -> list[tuple[str, float]]:
    """跨板块敞口模拟：把一笔授信拆分到集团内多个子公司板块（安平体系），返回 (子公司, 敞口) 列表。"""
    n = rng.randint(1, 3)
    orgs = rng.sample(ORG_POOL[1:], n)  # 子公司板块（不含总部）
    weights = rng.sample(range(10, 90, 10), n)
    total = sum(weights)
    return [(org, round(base_balance * w / total, 2)) for org, w in zip(orgs, weights)]


def approve_flow(
    rng: random.Random, order_status: str, k: int = 3
) -> list[tuple[str, str | None]]:
    """审批链状态推进（NODE_SEQ 1-3，规则 7）：返回 k 个节点 (task_status, approve_result)。
    APPROVED → 全部完成且通过；REJECTED → 前 k-1 通过、第 k 驳回；PROCESS → 前 k-1 通过、第 k 待处理。"""
    if order_status == "APPROVED":
        return [("COMPLETED", "APPROVED") for _ in range(k)]
    if order_status == "REJECTED":
        return [("COMPLETED", "APPROVED") for _ in range(k - 1)] + [
            ("COMPLETED", "REJECTED")
        ]
    return [("COMPLETED", "APPROVED") for _ in range(k - 1)] + [("PENDING", None)]


def codebt_link(rng: random.Random, group_members: list[dict[str, Any]]) -> list[str]:
    """共债关联注入：从集团成员抽出 0-2 个关联共债主体，返回其客户名称列表。"""
    n = rng.randint(0, min(2, len(group_members)))
    return [m["customer_name"] for m in rng.sample(group_members, n)]


# ---------------------------------------------------------------------------
# 生成上下文工具（与 generate.py 对齐的本地副本，避免循环导入）
# ---------------------------------------------------------------------------
def _row_count(ctx: dict[str, Any], table_id: str) -> int:
    """从配置表注册表读某表 row_count（配置为单一事实来源）。"""
    code, name = table_id.split(".", 1)
    return ctx["config"]["enterprise"]["systems"][code]["tables"][name]["row_count"]


def random_date(rng: random.Random) -> str:
    """ANCHOR_START..ANCHOR_END 随机日期 YYYY-MM-DD（seed 确定性派生）。"""
    span = (ANCHOR_END - ANCHOR_START).days
    return (ANCHOR_START + timedelta(days=rng.randint(0, span))).strftime("%Y-%m-%d")


def _weighted(rng: random.Random, choices: tuple[tuple[str, float], ...]) -> str:
    """按权重挑选项（choices = (值, 权重) 元组序列），确定性。"""
    return rng.choices([c[0] for c in choices], weights=[c[1] for c in choices], k=1)[0]


def _person_name(rng: random.Random) -> str:
    """中文人名（姓 + 名，确定性池）。"""
    return f"{rng.choice(FAMILY_NAMES)}{rng.choice(GIVEN_NAMES)}"


def _uscc(rng: random.Random) -> str:
    """模拟统一社会信用代码（18 位，确定性伪码）。"""
    body = "".join(rng.choices("0123456789", k=6)) + "".join(
        rng.choices("0123456789ABCDEFGHJKLMNPQRTUWXY", k=10)
    )
    return f"91{body}"


def _asset_quality(rng: random.Random) -> tuple[str, str]:
    """资产质量（代码, 名称），正常为主（客户质量分布 CUST_QUALITY_DIST）。"""
    item = rng.choices(
        CUST_QUALITY_DIST, weights=[c[2] for c in CUST_QUALITY_DIST], k=1
    )[0]
    return item[0], item[1]


def _zone(rng: random.Random) -> tuple[str, str]:
    """(区域代码, 区域名称)。"""
    return rng.choice(ZONE_POOL)


def _industry(rng: random.Random) -> tuple[str, str]:
    """(行业代码, 行业名称)。"""
    return rng.choice(INDUSTRY_POOL)


def _distribute_counts(
    rng: random.Random, n: int, total: int, lo: int, hi: int
) -> list[int]:
    """把 total 行数分配到 n 个父单据（每份 ∈ [lo,hi]），确定性收敛（scale 鲁棒吸附）。"""
    lo, hi = int(lo), int(hi)
    if n <= 0:
        return []
    total = max(lo * n, min(total, hi * n))
    counts = [rng.randrange(lo, hi + 1) for _ in range(n)]
    diff = total - sum(counts)
    while diff > 0:
        i = rng.randrange(n)
        if counts[i] < hi:
            counts[i] += 1
            diff -= 1
    while diff < 0:
        i = rng.randrange(n)
        if counts[i] > lo:
            counts[i] -= 1
            diff += 1
    return counts


def _shareholder_block(rng: random.Random, i: int) -> dict[str, Any]:
    """第 i 大股东字段块（姓名 + 出资比例）。"""
    return {
        f"shareholder_name_{i}": _person_name(rng),
        f"shareholder_ratio_{i}": round(rng.uniform(0, 60), 2),
    }


def _invest_block(rng: random.Random, i: int) -> dict[str, Any]:
    """第 i 笔对外投资字段块（公司/金额/币种/比例）。"""
    return {
        f"invest_company_{i}": f"{rng.choice(CUST_NAME_POOL)}{rng.choice(CUST_NAME_SUFFIX)}",
        f"invest_amount_{i}": round(rng.uniform(0, 50000), 2),
        f"invest_currency_name_{i}": "人民币",
        f"invest_ratio_{i}": round(rng.uniform(0, 60), 2),
    }


_LEVEL_CN = {"RED": "红色", "YELLOW": "黄色", "BLUE": "蓝色"}


def _driver_for_topic(level2: str) -> str:
    """二级主题 → 规则 1 主驱动维度（押品贬值→贬值、集中度超限→超限、关联交易→关联异动、其余→评分）。"""
    if level2 == "押品贬值":
        return "collateral"
    if level2 == "集中度超限":
        return "concentration"
    if level2 == "关联交易":
        return "related"
    return "score"


def _warn_inputs_for_level(
    rng: random.Random, level: str, driver: str
) -> dict[str, float]:
    """为指定预警等级 + 主驱动维度生成输入，保证 warn_level_decide 命中 level（分布可机验）。"""
    score = rng.randint(20, 59)
    coll = round(rng.uniform(0.0, 0.14), 4)
    conc = round(rng.uniform(0.0, 0.09), 4)
    rel = round(rng.uniform(0.0, 0.19), 4)
    if level == "RED":
        if driver == "collateral":
            coll = round(rng.uniform(0.30, 0.50), 4)
        elif driver == "concentration":
            conc = round(rng.uniform(0.20, 0.35), 4)
        else:
            score = rng.randint(80, 100)
    elif level == "YELLOW":
        if driver == "collateral":
            coll = round(rng.uniform(0.15, 0.29), 4)
        elif driver == "concentration":
            conc = round(rng.uniform(0.10, 0.19), 4)
        elif driver == "related":
            rel = round(rng.uniform(0.20, 0.49), 4)
        else:
            score = rng.randint(60, 79)
    return {
        "risk_score": score,
        "collateral_depreciation": coll,
        "concentration_overrun": conc,
        "related_change": rel,
    }


def _warn_reason(level: str, level2: str, inputs: dict[str, float]) -> str:
    """按主题生成预警事由文本（真实感来源）。"""
    cn = _LEVEL_CN[level]
    if level2 == "押品贬值":
        return f"押品估值较上期下降 {inputs['collateral_depreciation'] * 100:.0f}%，触发{cn}预警"
    if level2 == "集中度超限":
        return f"集团集中度敞口超限 {inputs['concentration_overrun'] * 100:.0f}%，触发{cn}预警"
    if level2 == "关联交易":
        return f"关联交易异动幅度 {inputs['related_change'] * 100:.0f}%，触发{cn}预警"
    return f"{level2}异常，模型评分 {inputs['risk_score']}，触发{cn}预警"


def _five_class_inputs(rng: random.Random, category: str) -> dict[str, Any]:
    """为指定五级分类生成输入（逾期/减值/风险事件），保证 five_category_assign 命中 category。"""
    if category == "LOSS":
        return {
            "overdue_days": rng.randint(361, 720),
            "impairment_ratio": round(rng.uniform(0.5, 0.95), 4),
        }
    if category == "DOUBTFUL":
        return {
            "overdue_days": rng.randint(181, 360),
            "impairment_ratio": round(rng.uniform(0.3, 0.6), 4),
        }
    if category == "SECONDARY":
        return {
            "overdue_days": rng.randint(91, 180),
            "impairment_ratio": round(rng.uniform(0.15, 0.4), 4),
        }
    if category == "ATTENTION":
        return {
            "overdue_days": rng.randint(1, 90),
            "impairment_ratio": round(rng.uniform(0.01, 0.1), 4),
        }
    return {"overdue_days": 0, "impairment_ratio": round(rng.uniform(0.0, 0.005), 4)}


CONCENTRATION_RATIO_DIST = (
    ("normal", 0.60),
    ("yellow", 0.25),
    ("orange", 0.10),
    ("red", 0.05),
)


def _concentration_ratio(rng: random.Random) -> float:
    """按集中度分布生成敞口占比（规则 3 可机验：正常 ≤10% / 黄 10-15% / 橙 15-25% / 红 >25%）。"""
    band = _weighted(rng, CONCENTRATION_RATIO_DIST)
    if band == "red":
        return round(rng.uniform(0.26, 0.40), 4)
    if band == "orange":
        return round(rng.uniform(0.16, 0.25), 4)
    if band == "yellow":
        return round(rng.uniform(0.11, 0.15), 4)
    return round(rng.uniform(0.02, 0.10), 4)


# ---------------------------------------------------------------------------
# M1b 全量补全：共享业务池 + 新辅助函数（42 表业务词表；确定性 random 池）
# ---------------------------------------------------------------------------
BUSINESS_TYPE_NAME_POOL = (
    "流动资金贷款",
    "项目贷款",
    "并购贷款",
    "贸易融资",
    "银团贷款",
    "承兑汇票",
    "保函",
    "融资租赁",
)
# 业务品种（代码, 名称）—— 供资产/押品/集中度等表引用（字典项 P001）
PRODUCT_CODE_POOL = (
    ("PL01", "流动资金贷款"),
    ("PL02", "项目贷款"),
    ("PL03", "并购贷款"),
    ("PL04", "贸易融资"),
    ("PL05", "银团贷款"),
    ("PL06", "承兑汇票"),
    ("PL07", "保函"),
    ("PL08", "融资租赁"),
)
INTERNAL_PRODUCT_CODE_POOL = (
    ("IP01", "公司流贷"),
    ("IP02", "项目融资"),
    ("IP03", "并购贷款"),
    ("IP04", "银团贷款"),
    ("IP05", "贸易融资"),
    ("IP06", "票据贴现"),
)
PLEDGE_PROPERTY_POOL = (
    "房产",
    "土地使用权",
    "机器设备",
    "存货",
    "应收账款",
    "股权",
    "票据",
    "有价证券",
)
PLEDGE_STATUS_POOL = ("有效", "已解押", "待登记", "已处置", "冻结")
COLLATERAL_STATUS_POOL = ("在用", "闲置", "已处置", "待核销")
CERT_TYPE_NAME_POOL = ("统一社会信用代码", "营业执照注册号", "组织机构代码")
ESTIMATE_ORG_POOL = (
    "安平资产评估有限公司",
    "中联资产评估",
    "国众联评估",
    "中企华评估",
    "世联评估",
)
AUDIT_TYPE_POOL = ("合规审计", "内控审计", "专项审计", "经济责任审计")
PENALTY_FORM_POOL = (
    "警告",
    "罚款",
    "没收违法所得",
    "责令整改",
    "暂停业务",
    "吊销许可证",
)
CASE_TYPE_POOL = (
    "信贷风险",
    "市场风险",
    "操作风险",
    "洗钱风险",
    "信息科技风险",
    "消费者权益",
)
WARN_MODEL_POOL = ("集中度模型", "背离趋势模型", "衍生传导模型", "共债模型")
RISK_TYPE_DETERMINE_POOL = (
    "信用风险",
    "市场风险",
    "流动性风险",
    "操作风险",
    "合规风险",
)
SIGNAL_STATUS_POOL_FULL = ("待确认", "确认中", "已确认", "已关闭", "已撤销")
PUSH_STATUS_POOL = ("未推送", "已推送", "推送失败", "待推送")
DEAL_SUGGESTION_POOL = (
    "继续观察，加强贷后监控",
    "压缩敞口，逐步退出",
    "补充押品，降低风险敞口",
    "发起处置审批",
    "纳入重点监控名单",
)
# 指标字典（base.ap_metric_std 标准指标）
METRIC_STD_DEFS = (
    ("IDX-001", "集团对外融资余额", "亿元"),
    ("IDX-002", "集中度敞口占比", "%"),
    ("IDX-003", "逾期贷款余额", "亿元"),
    ("IDX-004", "不良贷款率", "%"),
    ("IDX-005", "拨备覆盖率", "%"),
    ("IDX-006", "风险暴露额", "亿元"),
    ("IDX-007", "押品估值覆盖率", "%"),
    ("IDX-008", "预警信号数", "个"),
    ("IDX-009", "资本充足率", "%"),
    ("IDX-010", "投资占比", "%"),
)
DICT_TYPE_DEFS = (
    ("P001", "业务品种"),
    ("P005", "证件类型"),
    ("P021", "行业分类"),
    ("P032", "资产质量"),
    ("P044", "风险类型"),
    ("P051", "衍生信号二级主题"),
    ("P052", "衍生信号一级主题"),
    ("P054", "衍生预警等级"),
    ("P055", "信号状态"),
    ("P057", "金控领导推送状态"),
    ("P058", "预警事由修改状态"),
    ("P059", "子公司推送状态"),
    ("P061", "审批状态"),
    ("P065", "待办状态"),
    ("P080", "背离触发规则"),
    ("P081", "集中度预警等级"),
    ("P082", "集中度风险预警等级"),
)
ORG_LEVEL_POOL = ("1", "2", "3", "4")
EXT_JSON_KEYS = ("risk_band", "region", "supervise", "sla", "auto_approve")


def _mobile(rng: random.Random) -> str:
    """11 位手机号（确定性池）。"""
    return "1" + rng.choice("3456789") + "".join(rng.choices("0123456789", k=9))


def _landline(rng: random.Random) -> str:
    """座机（区号-号码）。"""
    return f"0{rng.randint(10, 99)}-{rng.randint(10000000, 99999999)}"


def _email(rng: random.Random) -> str:
    """企业邮箱（anping 域，确定性池）。"""
    return f"user{rng.randint(1000, 99999)}@anping-group.com"


def _idcard(rng: random.Random) -> str:
    """18 位模拟身份证（确定性伪码，供 ap_user/押品所有权人等）。"""
    region = rng.randint(110000, 659000)
    year = rng.randint(1960, 2003)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    body = f"{region}{year:04d}{month:02d}{day:02d}{rng.randint(100, 999)}"
    return body + rng.choice("0123456789X")


def _warn_text(rng: random.Random, level: str, topic: str) -> str:
    """预警文本模板（等级 + 主题 → 事由/描述/推送事由等真实感文本）。"""
    cn = {"RED": "红色", "YELLOW": "黄色", "BLUE": "蓝色"}[level]
    return f"{topic}监测异常，触发{cn}预警，请相关条线关注并及时处置"


# ---------------------------------------------------------------------------
