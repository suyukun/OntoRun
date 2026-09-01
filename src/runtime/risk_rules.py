"""S4 M2 金控演示核心规则 —— R1a 集团层归集集中度 + R2 关联纳入重算（口径包 v0.3 §三）。

职责：把「剧本命中的 R1a/R2」注册进本体运行时校验体系，成为可机器验证的规则：
- R1a 三档：归集余额 / 集团并表资本 ≥9% 黄（关注）/ ≥10% 橙（预警线）/ >12% 红（内部限额）。
  三线阈值**禁硬编码**：全部从 base.ap_sys_param 读取（param_type_code=R1A_LINE/CAPITAL，
  与生成器 risk_script_props.CAPITAL_PARAMS 同源），缺失即 fail-closed 抛 RuleConfigError。
- R2 关联纳入重算：经 customer_relation_tree 三线索（股权代持/交叉担保/资金往来）识别隐性
  一致行动人，纳入归集后按 R1a 重算（天晟 86.4 亿→10.8% 橙；+恒昌 16 亿→102.4 亿→12.8% 红）。
- R1b/R3-R6 仅登记「预留已定义」（RESERVED_RULES），不注册（口径包 M2 注册范围=防过度设计）。

本模块 = 纯规则引擎（只依赖 sqlite3 + risk_db 的连接/常量，不依赖 action_engine），
可独立单测；动作校验挂接见 src/runtime/risk_rules_validation.py。

作用域说明（防误伤）：ap_anping 的 RNG 信号 warn_reason 内嵌的是合成百分比，与源库归集
实算不一致；而道具信号 warn_reason 内嵌规则引用「R1a」（口径包设计即如此）。因此规则约束
以「信号 warn_reason 引用 R1a」为作用域标记（R1A_RULE_MARKER）——这正是口径包「只注册剧本
命中的 R1a/R2」的落地，RNG 信号无引用 → 不纳入，行为不变。
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from src.runtime.risk_db import RiskStore

# ---------------------------------------------------------------------------
# R1a 阈值参数（禁硬编码：落 base.ap_sys_param，param_id 与生成器 CAPITAL_PARAMS 同源）
# ---------------------------------------------------------------------------
PARAM_ID_GROUP_CAPITAL = "CAP_GROUP_CONSOLIDATED"  # 集团并表资本（亿元，分母）
PARAM_ID_CONCERN_LINE = "CAP_CONCERN_LINE"  # 关注线（9%，黄）
PARAM_ID_WARN_LINE = "CAP_WARN_LINE"  # 预警线（10%，橙）
PARAM_ID_INTERNAL_LIMIT = "CAP_INTERNAL_LIMIT_RATIO"  # 内部限额（12%，红须 >）
PARAM_TYPE_CAPITAL = "CAPITAL"
PARAM_TYPE_R1A = "R1A_LINE"

# R1a 规则作用域标记：信号 warn_reason 引用「R1a」即受本规则约束（见模块 docstring）。
R1A_RULE_MARKER = "R1a"
# R2 引用标记：warn_reason 引用「R2」表示该信号已含关联方纳入（管辖级别 = R1a+R2 全口径）。
R2_RULE_MARKER = "R2"

# 等级次序（黄 < 橙 < 红；「无」= 关注线以下不触发预警）
LEVEL_ORDER: dict[str, int] = {"黄": 1, "橙": 2, "红": 3}
LEVEL_NONE = "无"

# business_balance 单位 = 万元 → 亿元
_WAN_TO_YI = 10000.0


def pct_display(ratio: float) -> str:
    """百分比展示统一两位小数（F6/F12 全链单一实现）：尾部零不冗余。

    1.03% 不被截断为 1.0%；10.8% / 8.0% 等恰好一位小数的值保持一位小数
    （不显示 10.80% / 8.00%），与既有断言（8.0% / 10.8% / 12.8%）兼容。
    evidence / reporting / rules 全链共用本函数（F12 补齐漏网点）。
    """
    x = round(ratio * 100, 2)
    if abs(x - round(x, 1)) < 1e-9:
        return f"{x:.1f}%"
    return f"{x:.2f}%"


# R2 三线索关键词（口径包§七：股权代持线索/交叉担保链/资金往来异动）
_CLUE_KEYWORDS: tuple[str, ...] = ("股权代持", "交叉担保", "资金往来")

# 口径包 M2 注册范围：R1b/R3-R6 标「预留已定义」，不注册（仅登记，防过度设计）。
RESERVED_RULES: tuple[tuple[str, str, str], ...] = (
    ("R1b", "银行层授信集中度（对照，15% 监管红线 / 10% 行内限额）", "附属机构层对照"),
    ("R3", "单一客户贷款集中度（>10% 红，天晟案例不触发防混算）", "对照/兜底"),
    ("R4", "重大关联交易合规预警（净资产 1% 或 >10 亿；年度 ≥5% 或 >50 亿）", "橙"),
    ("R5", "对外担保/关联融资集中度（担保/净资产 >10%；关联融资双向阈值）", "红"),
    ("R6", "行为类预警（欠息/逃废债/虚假资料/涉诉/关键人员变动）", "红"),
)


class RuleConfigError(RuntimeError):
    """R1a 阈值配置缺失/非法（fail-closed：规则必须可配置，禁硬编码兜底）。"""


@dataclass(frozen=True)
class R1aConfig:
    """R1a 阈值配置（全部来自 base.ap_sys_param，非硬编码）。"""

    concern_line: float  # 关注线（黄，≥）
    warn_line: float  # 预警线（橙，≥）
    internal_limit: float  # 内部限额（红，须 >）
    group_capital_yi: float  # 集团并表资本（亿元，归集分母）
    source: dict[str, str] | None = None  # 参数来源（param_id → param_value，留证据链）

    @classmethod
    def from_sys_param(cls, rows: dict[str, str]) -> R1aConfig:
        try:
            return cls(
                concern_line=float(rows[PARAM_ID_CONCERN_LINE]),
                warn_line=float(rows[PARAM_ID_WARN_LINE]),
                internal_limit=float(rows[PARAM_ID_INTERNAL_LIMIT]),
                group_capital_yi=float(rows[PARAM_ID_GROUP_CAPITAL]),
                source=dict(rows),
            )
        except KeyError as exc:  # 缺失 → fail-closed
            raise RuleConfigError(
                f"R1a 阈值参数缺失（base.ap_sys_param）: {exc.args[0]}"
            ) from exc
        except ValueError as exc:  # 非法数值 → fail-closed
            raise RuleConfigError(f"R1a 阈值参数非法: {exc}") from exc

    @classmethod
    def load(cls, conn: sqlite3.Connection) -> R1aConfig:
        rows = {
            r["param_id"]: r["param_value"]
            for r in conn.execute(
                "SELECT param_id, param_value FROM base.ap_sys_param "
                "WHERE param_type_code IN (?, ?)",
                (PARAM_TYPE_CAPITAL, PARAM_TYPE_R1A),
            )
        }
        return cls.from_sys_param(rows)


def level_for_ratio(ratio: float, cfg: R1aConfig) -> str:
    """R1a 三档定级：>12% 红 / ≥10% 橙 / ≥9% 黄 / 其余无警（口径包§三）。

    边界严格对齐：9% 命中黄、10% 命中橙、12% 仍为橙（红须 >12%）、12.8% 红。
    """
    if ratio > cfg.internal_limit:
        return "红"
    if ratio >= cfg.warn_line:
        return "橙"
    if ratio >= cfg.concern_line:
        return "黄"
    return LEVEL_NONE


def group_aggregation_yi(conn: sqlite3.Connection, group_name: str) -> float:
    """集团自身归集余额（亿元）：ap_subsidiary_credit_detail 按 group_customer_name 汇总。"""
    row = conn.execute(
        "SELECT COALESCE(SUM(business_balance), 0) AS s "
        "FROM customer.ap_subsidiary_credit_detail WHERE group_customer_name=?",
        (group_name,),
    ).fetchone()
    return (row[0] if row else 0.0) / _WAN_TO_YI


def concentration_ledger_aggregation_yi(
    conn: sqlite3.Connection, group_no: str
) -> float:
    """ap_concentration_limit 台账按集团编号聚合归集余额（亿元，与看板/报送同源，F7）。

    口径包§一 集团层归集监测 = concentration.ap_concentration_limit 按
    customer.group_customer_no 聚合（含 R2 隐性关联方后 ÷ 集团并表资本）。
    证据链（group-reveal/related-upgrade/verify-reason）与看板统一走本函数，
    消除「两套分子源」跨端不一致（F7 P0）。
    """
    row = conn.execute(
        "SELECT COALESCE(SUM(cl.concentration_limit), 0) AS s "
        "FROM concentration.ap_concentration_limit cl "
        "JOIN customer.ap_customer c ON c.customer_no = cl.customer_no "
        "WHERE c.group_customer_no = ?",
        (group_no,),
    ).fetchone()
    return (row["s"] if row else 0.0) / _WAN_TO_YI


def has_concentration_ledger(conn: sqlite3.Connection, group_no: str) -> bool:
    """集团是否含集中度台账（ap_concentration_limit 有行）——证据链同源判定（F7）。

    无台账集团保持 fail-closed 400（无台账不回显 0% 玩具结果）；有台账即可查
    （rank5 GRP-2026-001234 台账 8.16 亿，修复前 group-reveal 误报 400）。
    """
    row = conn.execute(
        "SELECT 1 FROM concentration.ap_concentration_limit cl "
        "JOIN customer.ap_customer c ON c.customer_no = cl.customer_no "
        "WHERE c.group_customer_no = ? LIMIT 1",
        (group_no,),
    ).fetchone()
    return row is not None


@dataclass
class GroupConcentration:
    """R1a 集团层集中度（ap_concentration_limit 台账口径 + R2 隐性关联纳入，与看板同源，F7）。

    分子 = 集中度台账归集（自身）+ 经 customer_relation_tree 三线索识别的隐性关联方；
    分母 = 集团并表资本（base.ap_sys_param）；按 R1a 三线定级。证据链三端点共用。
    """

    group_customer_no: str
    group_customer_name: str
    own_balance_yi: float  # ap_concentration_limit 台账归集（亿，自身）
    related_balance_yi: float  # R2 隐性关联方（亿）
    total_yi: float  # 归集合计（亿）
    ratio: float  # total_yi / 集团并表资本
    level: str  # 黄/橙/红/无
    config: R1aConfig
    related_parties: list[RelatedParty] = field(default_factory=list)


def evaluate_group_concentration(
    conn: sqlite3.Connection,
    group_no: str,
    group_name: str,
    *,
    include_related: bool = True,
    config: R1aConfig | None = None,
) -> GroupConcentration:
    """对集团执行 R1a 归集集中度（ap_concentration_limit 台账口径，可选含 R2 隐性关联）。

    与看板 _concentration_ranking 同源（F7 P0：两套分子源统一）；conn 须含
    customer./concentration./base. 别名（用 RiskStore.source_conn()）。
    """
    cfg = config or R1aConfig.load(conn)
    own = concentration_ledger_aggregation_yi(conn, group_no)
    parties = related_parties(conn, group_name) if include_related else []
    rel = sum(p.balance_yi for p in parties)
    total = own + rel
    ratio = total / cfg.group_capital_yi if cfg.group_capital_yi else 0.0
    return GroupConcentration(
        group_customer_no=group_no,
        group_customer_name=group_name,
        own_balance_yi=own,
        related_balance_yi=rel,
        total_yi=total,
        ratio=ratio,
        level=level_for_ratio(ratio, cfg),
        config=cfg,
        related_parties=parties,
    )


def related_parties(conn: sqlite3.Connection, group_name: str) -> list[RelatedParty]:
    """R2 关联方识别（customer_relation_tree 三线索交叉）并汇总其授信余额（亿元）。

    一个关联客户可有多个关系树行（每行一条线索），按客户聚合线索与余额；
    仅含至少一条线索（clear_remark_1/2/3 非空）的客户，即「经联合授信机制识别」。
    """
    rows = conn.execute(
        "SELECT customer_name, clear_remark_1, clear_remark_2, clear_remark_3 "
        "FROM customer.ap_customer_relation_tree WHERE group_customer_name=? "
        "AND (clear_remark_1 IS NOT NULL OR clear_remark_2 IS NOT NULL "
        "     OR clear_remark_3 IS NOT NULL)",
        (group_name,),
    ).fetchall()
    clues_by_cust: dict[str, list[str]] = {}
    for r in rows:
        cust = r[0]
        if not cust:
            continue
        for idx in range(1, 4):
            text = r[idx]
            if not text:
                continue
            name = next((kw for kw in _CLUE_KEYWORDS if kw in text), f"线索{idx}")
            clues = clues_by_cust.setdefault(cust, [])
            if name not in clues:
                clues.append(name)
    parties: list[RelatedParty] = []
    for cust, clues in clues_by_cust.items():
        bal = 0.0
        for r in conn.execute(
            "SELECT COALESCE(SUM(business_balance), 0) AS s "
            "FROM customer.ap_subsidiary_credit_detail WHERE customer_name=?",
            (cust,),
        ):
            bal = (r[0] or 0.0) / _WAN_TO_YI
        parties.append(RelatedParty(customer_name=cust, balance_yi=bal, clues=clues))
    return parties


@dataclass
class RelatedParty:
    customer_name: str
    balance_yi: float
    clues: list[str]


@dataclass
class R1aResult:
    """R1a 一次定级结果（含分子分母与规则依据，供校验/证据链/报告消费）。"""

    group_name: str
    base_aggregation_yi: float  # 集团自身归集（亿元）
    related_balance_yi: float  # 关联方纳入（亿元，R2）
    total_yi: float  # 归集合计（亿元）
    ratio: float  # total_yi / 集团并表资本
    level: str  # 黄/橙/红/无
    config: R1aConfig
    related_parties: list[RelatedParty] = field(default_factory=list)

    def rule_basis(self) -> str:
        """规则依据文本：分子分母、三线阈值与定级全带（拒绝消息/证据链用）。"""
        cfg = self.config
        rel_txt = (
            f" + 关联方 {self.related_balance_yi:.1f} 亿"
            if self.related_balance_yi
            else ""
        )
        return (
            f"R1a 集团层归集集中度实算：归集 {self.total_yi:.1f} 亿元"
            f"（集团自身 {self.base_aggregation_yi:.1f} 亿{rel_txt}）"
            f" ÷ 集团并表资本 {cfg.group_capital_yi:.0f} 亿元 = {pct_display(self.ratio)}；"
            f"阈值（base.ap_sys_param）关注线 {cfg.concern_line * 100:.0f}%（黄）/"
            f"预警线 {cfg.warn_line * 100:.0f}%（橙）/内部限额 {cfg.internal_limit * 100:.0f}%"
            f"（红，须 >{cfg.internal_limit * 100:.0f}%）；规则定级：{self.level}"
        )


def evaluate(
    conn: sqlite3.Connection,
    group_name: str,
    *,
    include_related: bool = True,
    config: R1aConfig | None = None,
) -> R1aResult:
    """对集团执行 R1a 归集集中度计算（可选含 R2 关联纳入）。conn 须含 customer./base. 别名
    （用 RiskStore.source_conn()）。"""
    cfg = config or R1aConfig.load(conn)
    base = group_aggregation_yi(conn, group_name)
    parties = related_parties(conn, group_name) if include_related else []
    rel = sum(p.balance_yi for p in parties)
    total = base + rel
    ratio = total / cfg.group_capital_yi if cfg.group_capital_yi else 0.0
    return R1aResult(
        group_name=group_name,
        base_aggregation_yi=base,
        related_balance_yi=rel,
        total_yi=total,
        ratio=ratio,
        level=level_for_ratio(ratio, cfg),
        config=cfg,
        related_parties=parties,
    )


def resolve_group_name(conn: sqlite3.Connection, warning: dict[str, Any]) -> str:
    """信号 → 集团名：优先 belong_group，回退 group_customer_no → ap_group_customer。"""
    group = (warning.get("belong_group") or "").strip()
    if group:
        return group
    gno = warning.get("group_customer_no")
    if gno:
        row = conn.execute(
            "SELECT group_customer_name FROM customer.ap_group_customer "
            "WHERE group_customer_no=?",
            (gno,),
        ).fetchone()
        if row and row[0]:
            return row[0]
    return ""


def evaluate_warning(
    conn: sqlite3.Connection, warning: dict[str, Any]
) -> tuple[R1aResult | None, R1aResult | None]:
    """对信号所属集团计算 R1a-only 与 R1a+R2 两口径；无法解析集团返回 (None, None)。"""
    group = resolve_group_name(conn, warning)
    if not group:
        return None, None
    return (
        evaluate(conn, group, include_related=False),
        evaluate(conn, group, include_related=True),
    )


def is_r1a_governed(warning: dict[str, Any]) -> bool:
    """信号是否受 R1a 规则约束：warn_reason 引用「R1a」（口径包 M2 注册范围=剧本命中）。"""
    return R1A_RULE_MARKER in (warning.get("warn_reason") or "")


def governing_level(warning: dict[str, Any], r1a_level: str, r1a_r2_level: str) -> str:
    """信号管辖级别：reason 引用 R2（已含关联纳入）→ 全口径 R1a+R2；否则 R1a 自身口径。"""
    return (
        r1a_r2_level
        if R2_RULE_MARKER in (warning.get("warn_reason") or "")
        else r1a_level
    )


@dataclass(frozen=True)
class RuleViolation:
    """规则违反结果（轻量，供 action_engine.Violation 转换；保持本模块无引擎依赖）。"""

    error_code: str
    message: str
    detail: dict[str, Any] | None = None


def check_adjust_level(r1a_r2: R1aResult, target_level: str) -> RuleViolation | None:
    """adjust_warning_level 规则校验：目标等级不得高于 R1a+R2 定级（升级红须 >12% 命中）。"""
    supported = r1a_r2.level
    if LEVEL_ORDER.get(target_level, 0) > LEVEL_ORDER.get(supported, 0):
        return RuleViolation(
            error_code="WARNING_LEVEL_NOT_SUPPORTED_BY_R1A",
            message=(
                "预警等级超出 R1a 归集集中度规则支持范围"
                "（升级红须 >12% 命中，否则拒绝）"
            ),
            detail={
                "rule": "R1a",
                "group_name": r1a_r2.group_name,
                "target_level": target_level,
                "supported_level": supported,
                "ratio": round(r1a_r2.ratio, 4),
                "aggregation_yi": round(r1a_r2.total_yi, 2),
                "related_balance_yi": round(r1a_r2.related_balance_yi, 2),
                "basis": r1a_r2.rule_basis(),
            },
        )
    return None


def check_level_consistency(
    governing: str,
    stored_level: str,
    r1a: R1aResult,
    r1a_r2: R1aResult,
) -> RuleViolation | None:
    """confirm/submit 规则校验：信号存储等级须等于其管辖级别（与 R1a 状态一致）。"""
    if stored_level != governing:
        result = r1a_r2 if r1a_r2.ratio >= r1a.ratio else r1a
        return RuleViolation(
            error_code="WARNING_LEVEL_INCONSISTENT_WITH_R1A",
            message="预警等级与 R1a 归集集中度实算不一致，请核对归集口径",
            detail={
                "rule": "R1a",
                "group_name": result.group_name,
                "stored_level": stored_level,
                "governing_level": governing,
                "ratio": round(result.ratio, 4),
                "aggregation_yi": round(result.total_yi, 2),
                "related_balance_yi": round(result.related_balance_yi, 2),
                "basis": result.rule_basis(),
            },
        )
    return None


def open_rules_conn() -> sqlite3.Connection:
    """打开带 customer./base. 别名的只读连接（RiskStore 六库一体，供引擎/脚本消费）。"""
    return RiskStore().source_conn()


__all__ = [
    "LEVEL_NONE",
    "LEVEL_ORDER",
    "PARAM_ID_CONCERN_LINE",
    "PARAM_ID_GROUP_CAPITAL",
    "PARAM_ID_INTERNAL_LIMIT",
    "PARAM_ID_WARN_LINE",
    "R1A_RULE_MARKER",
    "R2_RULE_MARKER",
    "RESERVED_RULES",
    "GroupConcentration",
    "R1aConfig",
    "R1aResult",
    "RelatedParty",
    "RuleConfigError",
    "RuleViolation",
    "check_adjust_level",
    "check_level_consistency",
    "concentration_ledger_aggregation_yi",
    "evaluate",
    "evaluate_group_concentration",
    "evaluate_warning",
    "governing_level",
    "group_aggregation_yi",
    "has_concentration_ledger",
    "is_r1a_governed",
    "level_for_ratio",
    "open_rules_conn",
    "pct_display",
    "related_parties",
    "resolve_group_name",
]
