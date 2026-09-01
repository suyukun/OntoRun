"""S4 M3a 证据链载荷服务 —— 七幕剧本查询的「答案+证据」统一载荷（口径包 v0.3 §六/§七）。

定位：Agent 对话是演示一级入口（§六「Agent 对话框唯一一级入口，对象/链接/图谱降为对话
证据链展开态」），每个答案统一附证据链载荷：
    { 结论 conclusion, 依据表名 basis_tables, 命中规则+条款引用 rules_hits,
      分母说明 denominator, 明细行引用 detail_rows }
数据全部从 ap_anping 六库实算 + M2 规则引擎（src.runtime.risk_rules）实算，禁 mock
（红队玩具分水岭条款：证据链点开必须真数据联动、真表/真规则/真分母，非查表回显）。

消费方：
- RiskAgent 剧本工具（risk_group_reveal / risk_related_reveal / risk_approval_chain），
  工具结果携带 data + evidence，随对话答案返回（src/agent/risk_agent.py）；
- /risk/evidence/* 只读端点（src/api/risk_evidence_api.py，前端证据链展开态复用）。

口径回链 docs/v0.4-核心链口径包-v0.3.md：
- §一 资本常量（并表 800 / 银行 600·60 / 证券参考线分母 400 / 资管参考线分母 200）
  → 落 base.ap_sys_param（与 risk_script_props.CAPITAL_PARAMS / risk_reporting 同源）；
- §三 R1a 三线（关注 9% / 预警 10% / 内部限额 12%）+ R2 关联纳入（恒昌三线索）；
- §七 第 1 幕逐家单看都安全 → 归集 86.4/800 = 10.8% 橙；第 2 幕三线索 + R2 重算
  102.4/800 = 12.8% 红；第 4 幕双签驳回（2023 关联交易办法第二十三条 禁止隐匿关联
  关系拆分交易 → 退回重新起草）。
"""

from __future__ import annotations

import sqlite3
from typing import Any

from src.runtime.risk_db import RiskStore
from src.runtime.risk_rules import (
    LEVEL_NONE,
    R1A_RULE_MARKER,
    evaluate_group_concentration,
    has_concentration_ledger,
    level_for_ratio,
)

# ---------------------------------------------------------------------------
# 常量与条款引用（口径包§一/§三/§七；参数 id 与 risk_reporting / risk_script_props 同源）
# ---------------------------------------------------------------------------
PARAM_GROUP_CONSOLIDATED = "CAP_GROUP_CONSOLIDATED"  # 集团并表资本（亿）= 800
PARAM_BANK_NET = "CAP_BANK_NET"  # 安平银行资本净额（亿）= 600
PARAM_BANK_INTERNAL_LIMIT = "CAP_BANK_INTERNAL_LIMIT"  # 行内内部限额（亿）= 60
PARAM_SECURITIES_DENOM = "CAP_SECURITIES_DENOM"  # 证券参考线分母（亿）= 400
PARAM_SECURITIES_REF_LINE = "CAP_SECURITIES_REF_LINE"  # 证券参考线内融资占比（5.5%）
PARAM_AM_DENOM = "CAP_AM_DENOM"  # 资管参考线分母（亿）= 200
PARAM_AM_REF_LINE = "CAP_AM_REF_LINE"  # 资管参考线内融资占比（8.2%）
PARAM_CONCERN_LINE = "CAP_CONCERN_LINE"  # R1a 关注线（9%，黄）
PARAM_WARN_LINE = "CAP_WARN_LINE"  # R1a 预警线（10%，橙）
PARAM_INTERNAL_LIMIT_RATIO = "CAP_INTERNAL_LIMIT_RATIO"  # R1a 内部限额（12%，红须 >）

# 各附属机构参考线分母（口径包§一「单看都安全」分母；其余机构不套用参考线）
_ORG_REFERENCE_DENOM: dict[str, str] = {
    "安平银行": PARAM_BANK_NET,
    "安平证券": PARAM_SECURITIES_DENOM,
    "安平资产管理": PARAM_AM_DENOM,
}

# 恒昌三线索关键词（口径包§七：股权代持线索/交叉担保链/资金往来异动；与 risk_rules 同源）
CLUE_KEYWORDS: tuple[str, ...] = ("股权代持", "交叉担保", "资金往来")

# R1a 条款引用（口径包§三）
R1A_CLAUSE = "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部口径）"
R1A_LINES = "关注 9%（黄）/ 预警 10%（橙）/ 内部限额 12%（红，须 >12%）"
# R1b 对照条款引用（口径包§三：银行层对照，不注册仅对照）
R1B_CLAUSE = (
    "《商业银行大额风险暴露管理办法》（2018）第七/八条 + 2003 指引第十二条（修订）"
)
R1B_LINES = "监管红线 15% / 行内限额 10%（60 亿）"
# R2 条款引用
R2_CLAUSE = "《商业银行大额风险暴露管理办法》（2018）附件 1 + 金控办法第三十三条"
R2_DESC = "经联合授信机制识别隐性关联/一致行动人（三线索交叉）后纳入归集，按 R1a 重算"

# 2023 关联交易办法第二十三条（中国人民银行令〔2023〕第 1 号，gov.cn 原文 §（三））
ARTICLE_2023_23 = (
    "第二十三条 金融控股公司及其附属机构不得进行以下关联交易："
    "（三）通过隐匿关联关系、拆分交易、设计复杂交易结构等各种隐蔽方式规避内部审查、"
    "外部监管以及报告披露义务，为关联方违规提供融资、隐藏风险等。"
)

# 受限多跳分析 → 依据表（risk_query_spec.ANALYTIC_SQL 的源表，证据链 basis_tables）
ANALYTIC_TABLES: dict[str, list[str]] = {
    "warning_approval_step": [
        "ap_warning_signal",
        "ap_warning_disposal",
        "approval.ap_approve_order",
        "approval.ap_approve_task",
        "approval.ap_approve_node",
        "customer.ap_group_customer",
    ],
    "group_concentration_limits": [
        "concentration.ap_concentration_limit",
        "customer.ap_customer",
    ],
    "related_party_of": [
        "customer.ap_customer_relation_tree",
        "customer.ap_subsidiary_credit_detail",
    ],
}

# R1a 阈值/资本参数元数据（P0-1：可答「谁定的、怎么改」；与 risk_script_props.CAPITAL_PARAMS 同源）
PARAM_META: dict[str, dict[str, str]] = {
    PARAM_GROUP_CONSOLIDATED: {
        "param_type_code": "CAPITAL",
        "param_value": "800",
        "param_description": "集团并表资本（亿元，集团层归集集中度分母）",
        "param_source": "安平金控集团并表资本核算口径（2025 年度经审计并表）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元，集团层分母）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项（不含保证金存款及国债存单净额项）",
        "version": "v3",
        "update_time": "2026-11-30",
    },
    PARAM_CONCERN_LINE: {
        "param_type_code": "R1A_LINE",
        "param_value": "0.09",
        "param_description": "集团层关注线（9%，黄）",
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
        "version": "v3",
        "update_time": "2026-11-30",
    },
    PARAM_WARN_LINE: {
        "param_type_code": "R1A_LINE",
        "param_value": "0.10",
        "param_description": "集团层预警线（10%，橙）",
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
        "version": "v3",
        "update_time": "2026-11-30",
    },
    PARAM_INTERNAL_LIMIT_RATIO: {
        "param_type_code": "R1A_LINE",
        "param_value": "0.12",
        "param_description": "集团层内部限额（12%，红）",
        "param_source": "《金融控股公司监督管理试行办法》第三十二/三十三条（安平内部自设口径）",
        "param_approver": "安平金控风险管理部（2025-06-30 审批，版本 v3）",
        "numerator_desc": "归集余额（联合授信台账合计数，含表外承诺扣净额项）",
        "denominator_desc": "集团并表资本（800 亿元）",
        "netting_rule": "分子扣除 2010 修订第十二条允许的净额项",
        "version": "v3",
        "update_time": "2026-11-30",
    },
}

_WAN_TO_YI = 10000.0  # business_balance 单位 = 万元 → 亿元


def _pct_display(ratio: float) -> str:
    """百分比展示统一两位小数（尾部零不冗余）：F6 修复「1.0% vs 1.03% 取整两貌」。

    1.03% 不再被截断为 1.0%；10.8% / 8.0% 等恰好一位小数的值保持一位小数（不显示
    10.80% / 8.00%），与既有断言（8.0% / 10.8% / 12.8%）兼容。
    """
    x = round(ratio * 100, 2)
    if abs(x - round(x, 1)) < 1e-9:
        return f"{x:.1f}%"
    return f"{x:.2f}%"


class EvidenceError(RuntimeError):
    """证据链查询输入非法/未命中（fail-closed，拒答而非瞎编）。"""


# ---------------------------------------------------------------------------
# 证据链载荷服务（只读；全部真数据 + M2 引擎实算）
# ---------------------------------------------------------------------------


class EvidenceService:
    """七幕剧本查询的证据链载荷：真表/真规则/真分母，禁 mock。

    幂等只读：全部方法开只读连接（RiskStore.source_conn），零写回，可安全复跑。
    """

    def __init__(self, store: RiskStore | None = None) -> None:
        self._store = store or RiskStore()

    def _conn(self) -> sqlite3.Connection:
        return self._store.source_conn()

    # ---- 基础设施 ----

    @staticmethod
    def _capital_params(conn: sqlite3.Connection) -> dict[str, float]:
        """资本/参考线分母（亿）与 R1a 三线，来自 base.ap_sys_param（单一来源）。"""
        rows = conn.execute(
            "SELECT param_id, param_value FROM base.ap_sys_param "
            "WHERE param_type_code = 'CAPITAL' AND param_id IN (?,?,?,?,?,?,?,?,?,?)",
            (
                PARAM_GROUP_CONSOLIDATED,
                PARAM_BANK_NET,
                PARAM_BANK_INTERNAL_LIMIT,
                PARAM_SECURITIES_DENOM,
                PARAM_SECURITIES_REF_LINE,
                PARAM_AM_DENOM,
                PARAM_AM_REF_LINE,
                "CAP_CONCERN_LINE",
                "CAP_WARN_LINE",
                "CAP_INTERNAL_LIMIT_RATIO",
            ),
        ).fetchall()
        return {r["param_id"]: float(r["param_value"]) for r in rows}

    @staticmethod
    def _ratio_display(ratio: float) -> str:
        return _pct_display(ratio)

    @staticmethod
    def _r1a_comparison_text(ratio: float, cfg: Any) -> str:
        """由 computed ratio 与 R1a 三线阈值生成真实比较短语（结论与定级严格一致）。

        P0-2 修复：结论模板不再写死「> 12% / ≥ 10%」——比较符与阈值按
        computed.ratio 实际判断生成（如 2.0% → 「< 关注线 9%」，杜绝
        「2.0% > 12% → 无」类数学错误）；F6 展示统一两位小数。
        """
        display = _pct_display(ratio)
        if ratio > cfg.internal_limit:
            return f"{display} > 内部限额 {cfg.internal_limit * 100:.0f}%"
        if ratio >= cfg.warn_line:
            return f"{display} ≥ 预警线 {cfg.warn_line * 100:.0f}%"
        if ratio >= cfg.concern_line:
            return f"{display} ≥ 关注线 {cfg.concern_line * 100:.0f}%"
        return f"{display} < 关注线 {cfg.concern_line * 100:.0f}%"

    @staticmethod
    def _assert_level_consistent(ratio: float, cfg: Any, level: str, ctx: str) -> None:
        """结论自检：computed ratio 的 R1a 定级须与结论声明的 level 一致，不一致即抛错。

        防模板写死回归（比较符/结论与 computed 不一致）——结论模板必须由
        computed.ratio 实际计算生成，任何声称的定级与实算不符都直接失败。
        """
        implied = level_for_ratio(ratio, cfg)
        if implied != level:
            raise AssertionError(
                f"{ctx} 结论自检失败：computed ratio {ratio * 100:.1f}% 的 R1a 定级为 "
                f"「{implied}」，与结论声明的「{level}」不一致（结论模板须由实算生成）"
            )

    @staticmethod
    def _resolve_group(
        conn: sqlite3.Connection,
        *,
        group_customer_no: str | None = None,
        group_customer_name: str | None = None,
    ) -> tuple[str, str]:
        """按 group_customer_no 定位集团（名称仅展示，根因一串号修复）：no → 唯一名称。

        兼容按名回退（展示层/旧调用）：名称必须唯一——同名集团须带编号后缀区分
        （如 翔宇电子华北集团（07））；重名时 fail-closed 拒答并要求用 group_customer_no
        精确定位，杜绝跨同名集团 SUM 串号。同时核验集团有授信台账（防 0% 玩具结果）。
        返回 (group_customer_no, group_customer_name)。
        """
        if group_customer_no:
            gno = (group_customer_no or "").strip()
            row = conn.execute(
                "SELECT group_customer_name FROM customer.ap_group_customer "
                "WHERE group_customer_no=?",
                (gno,),
            ).fetchone()
            if row is None or not row["group_customer_name"]:
                raise EvidenceError(f"集团不存在: {gno}")
            name = row["group_customer_name"]
        elif group_customer_name:
            name = (group_customer_name or "").strip()
            if not name:
                raise EvidenceError("group_customer_no 不能为空")
            rows = conn.execute(
                "SELECT group_customer_no FROM customer.ap_group_customer "
                "WHERE group_customer_name=?",
                (name,),
            ).fetchall()
            if not rows:
                raise EvidenceError(f"集团不存在或无授信台账: {name}")
            if len(rows) > 1:
                raise EvidenceError(
                    f"集团名「{name}」不唯一（{len(rows)} 个同名集团），"
                    "请用 group_customer_no 精确定位（同名集团须带编号后缀区分）"
                )
            gno = rows[0]["group_customer_no"]
        else:
            raise EvidenceError("必须提供 group_customer_no")
        return gno, name

    # ---- P0-1：R1a 阈值可查询（谁定的/怎么改；sys_param 可查询对象 + 元数据列）----

    def thresholds(self) -> dict[str, Any]:
        """R1a 三线 + 集团并表资本阈值载荷（真库参数行 + 元数据列）。

        P0-1 修复：阈值不再是查不到的黑盒——返回每条参数的
        {param_id/值/出处条款/版本/审批人/更新时间/分子构成/分母/净额规则}，
        供「预警线谁定的、怎么改」直接原文回显（口径包§三 金控办法第三十二/三十三条自设口径）。
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT sys_param_id, param_id, param_value, param_description, "
                "param_type_code, version, update_time, update_user, "
                "param_source, param_approver, numerator_desc, denominator_desc, netting_rule "
                "FROM base.ap_sys_param "
                "WHERE param_id IN (?,?,?,?)",
                (
                    PARAM_CONCERN_LINE,
                    PARAM_WARN_LINE,
                    PARAM_INTERNAL_LIMIT_RATIO,
                    PARAM_GROUP_CONSOLIDATED,
                ),
            ).fetchall()
            params = []
            for r in rows:
                pid = r["param_id"]
                meta = PARAM_META.get(pid, {})
                params.append(
                    {
                        "param_id": pid,
                        "param_value": r["param_value"],
                        "param_description": r["param_description"],
                        "param_type_code": r["param_type_code"] or meta.get("param_type_code"),
                        "param_source": r["param_source"] or meta.get("param_source"),
                        "param_approver": r["param_approver"] or meta.get("param_approver"),
                        "numerator_desc": r["numerator_desc"] or meta.get("numerator_desc"),
                        "denominator_desc": r["denominator_desc"] or meta.get("denominator_desc"),
                        "netting_rule": r["netting_rule"] or meta.get("netting_rule"),
                        "version": r["version"] or meta.get("version"),
                        "update_time": r["update_time"] or meta.get("update_time"),
                        "update_user": r["update_user"] or "SYSTEM",
                    }
                )
        by_id = {p["param_id"]: p for p in params}
        return {
            "intent": "thresholds_r1a",
            "conclusion": (
                "R1a 集团层归集集中度三线（安平内部口径，金控办法第三十二/三十三条自设）："
                "关注线 9%（黄）/ 预警线 10%（橙）/ 内部限额 12%（红，须 >12%）；"
                "分母 = 集团并表资本 800 亿元。"
            ),
            "basis_tables": ["base.ap_sys_param"],
            "rules_hits": [
                {
                    "rule": "R1a",
                    "name": "集团层归集集中度",
                    "clause": R1A_CLAUSE,
                    "lines": R1A_LINES,
                    "note": "三线阈值配置于系统参数表（base.ap_sys_param），调整参数即调整预警线，全行统一、留痕可追溯",
                }
            ],
            "denominator": {
                "name": "集团并表资本",
                "value_yi": float(by_id[PARAM_GROUP_CONSOLIDATED]["param_value"]),
                "source": f"base.ap_sys_param.{PARAM_GROUP_CONSOLIDATED}",
            },
            "detail_rows": params,
        }

    @staticmethod
    def _group_signals(
        conn: sqlite3.Connection, group_customer_no: str
    ) -> list[dict[str, Any]]:
        """集团当前预警信号（证据链「明细行引用」：按 group_customer_no 定位，串号防护）。"""
        rows = conn.execute(
            "SELECT warning_id, signal_id, warn_level, signal_status, warn_reason "
            "FROM ap_warning_signal WHERE group_customer_no=? "
            "ORDER BY CASE warn_level WHEN '红' THEN 0 WHEN '橙' THEN 1 "
            "WHEN '黄' THEN 2 ELSE 3 END",
            (group_customer_no,),
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def _has_credit(conn: sqlite3.Connection, group_no: str) -> bool:
        """集团是否含集中度台账（第 1/2 幕 fail-closed：无台账不回显 0% 玩具结果）。

        F7：台账判定改指 concentration.ap_concentration_limit（与看板/归集同源）——
        修复前按 ap_subsidiary_credit_detail 判定，rank5（GRP-2026-001234 台账 8.16 亿）
        无明细行被误报「无授信台账」400。
        """
        return has_concentration_ledger(conn, group_no)

    @staticmethod
    def _org_single_safety(
        d: dict[str, Any], cap: dict[str, float]
    ) -> tuple[str, bool]:
        """单家附属机构是否在其参考线内（实算），返回 (单家描述, 是否安全)。

        F1/F3 修复：逐家安全断言按各自参考线实算——安平银行对行内限额（绝对额 60 亿）、
        安平证券/资管对参考线内融资占比（5.5% / 8.2%）；无参考线机构不参与「单看均安全」
        断言（仅列余额）。杜绝「银行 12.5%，低于行内限额 60 亿」类算术矛盾（75.2 亿
        实超 60 亿却被模板写死「低于」）。
        """
        org = d["org_name"]
        balance = d["balance_yi"]
        if org == "安平银行":
            limit_yi = cap[PARAM_BANK_INTERNAL_LIMIT]
            ok = balance <= limit_yi
            mark = "行内限额内" if ok else f"超行内限额 {limit_yi:.0f} 亿"
            return f"{org} {balance:.1f} 亿（{mark}）", ok
        denom = _ORG_REFERENCE_DENOM.get(org)
        if denom in (PARAM_SECURITIES_DENOM, PARAM_AM_DENOM):
            line_id = (
                PARAM_SECURITIES_REF_LINE
                if denom == PARAM_SECURITIES_DENOM
                else PARAM_AM_REF_LINE
            )
            ref_ratio = cap[line_id]
            ratio = d.get("org_reference_ratio")
            ok = ratio is not None and ratio <= ref_ratio
            display = EvidenceService._ratio_display(ratio) if ratio is not None else "-"
            mark = f"参考线 {ref_ratio * 100:.1f}% 内" if ok else f"超参考线 {ref_ratio * 100:.1f}%"
            return f"{org} {display}（{mark}）", ok
        return f"{org} {balance:.1f} 亿", True

    # ---- 第 1 幕：揭示（逐家单看都安全 → 归集 10.8% 橙）----

    def group_reveal(
        self,
        *,
        group_customer_no: str | None = None,
        group_customer_name: str | None = None,
    ) -> dict[str, Any]:
        """第 1 幕揭示查询：逐家附属机构融资（真分母单看都安全）+ 归集集中度实算。

        定位：以 group_customer_no 为主键（名称仅展示，根因一串号修复）。F7 P0：归集
        分子统一为 concentration.ap_concentration_limit 台账按集团聚合 + R2 隐性关联
        纳入（与看板/verify-reason/报送同源，risk_rules.evaluate_group_concentration），
        分母 = 集团并表资本；rank5（GRP-2026-001234 台账 8.16 亿）可查，无台账集团保持
        fail-closed 400。F7b：证据链显式给出 pre_R2（纳入隐性关联前）与 post_R2（纳入后）
        两行 + 说明文案「纳入隐性关联前后」，消除与看板 12.8% 的裸对比矛盾。
        """
        if not group_customer_no and not group_customer_name:
            raise EvidenceError("必须提供 group_customer_no")
        with self._conn() as conn:
            gno, group = self._resolve_group(
                conn,
                group_customer_no=group_customer_no,
                group_customer_name=group_customer_name,
            )
            if not self._has_credit(conn, gno):
                raise EvidenceError(f"集团无集中度台账: {group}")
            cap = self._capital_params(conn)
            # F7：两口径均由 ap_concentration_limit 台账聚合（与看板同源）
            pre = evaluate_group_concentration(
                conn, gno, group, include_related=False
            )  # pre_R2：纳入隐性关联前
            post = evaluate_group_concentration(
                conn, gno, group, include_related=True
            )  # post_R2：纳入隐性关联后
            cfg = pre.config
            group_cap = cfg.group_capital_yi
            # 逐家附属机构单看明细（口径包§七 第 1 幕「联合授信台账逐家亮出」）
            org_rows = conn.execute(
                "SELECT s.org_name, SUM(s.business_balance) AS t "
                "FROM customer.ap_subsidiary_credit_detail s "
                "JOIN customer.ap_customer c ON s.cert_no = c.cert_no "
                "WHERE c.group_customer_no=? GROUP BY s.org_name ORDER BY t DESC",
                (gno,),
            ).fetchall()
            detail: list[dict[str, Any]] = []
            for r in org_rows:
                yi = round((r["t"] or 0.0) / _WAN_TO_YI, 2)
                item: dict[str, Any] = {
                    "row_ref": (
                        f"customer.ap_subsidiary_credit_detail"
                        f"#group={gno}&org={r['org_name']}"
                    ),
                    "org_name": r["org_name"],
                    "balance_yi": yi,
                }
                denom_id = _ORG_REFERENCE_DENOM.get(r["org_name"])
                denom_yi = cap.get(denom_id) if denom_id else None
                if denom_yi:
                    item["reference_denom_yi"] = denom_yi
                    item["org_reference_ratio"] = round(yi / denom_yi, 4)
                    item["ratio_display"] = self._ratio_display(yi / denom_yi)
                detail.append(item)
            signals = self._group_signals(conn, gno)
        # P0-2 结论自检：比较短语由 computed ratio 实算生成，且与定级严格一致（不一致即抛错）
        compare_pre = self._r1a_comparison_text(pre.ratio, cfg)
        self._assert_level_consistent(
            pre.ratio, cfg, pre.level, "第 1 幕 group_reveal(pre_R2)"
        )
        self._assert_level_consistent(
            post.ratio, cfg, post.level, "第 1 幕 group_reveal(post_R2)"
        )
        warn = next((s for s in signals if s["warn_level"] == "橙"), None)
        # F1/F3 结论模板按实算：逐家安全断言由 _org_single_safety 对各自参考线实算，
        # 不再写死「银行 …低于行内限额 60 亿」（非道具组无 ratio_display 曾致 KeyError 500；
        # 瑞华 75.2 亿单挂安平银行实超 60 亿却断言「均安全」系算术矛盾）。
        all_safe = True
        if detail:
            org_parts: list[str] = []
            for item in detail:
                txt, ok = self._org_single_safety(item, cap)
                org_parts.append(txt)
                if "reference_denom_yi" in item and not ok:
                    all_safe = False
            safety = "；".join(org_parts)
            head = (
                f"{group} 逐家附属机构单看均安全（{safety}）"
                if all_safe
                else f"{group} 逐家附属机构单看已有超参考线（{safety}）"
            )
        else:
            head = f"{group} 集中度台账归集（无逐家明细行）"
        # F7b：第 1 幕结论标注「本行为纳入隐性关联前的归集口径」（pre_R2）
        conclusion = (
            f"{head}；归集实算 {pre.total_yi:.1f} 亿元 ÷ 集团并表资本 "
            f"{group_cap:.0f} 亿元 = {compare_pre} → R1a 定级「{pre.level}」"
            f"（本行为纳入隐性关联前的归集口径）"
            + ("，橙色预警信号已生成" if warn else "")
        )
        # F7b：证据链显式给出 pre_R2 / post_R2 两行 + 「纳入隐性关联前后」说明
        r2_levels = {
            "pre_r2": {
                "label": "纳入隐性关联前（R2 纳入前）",
                "numerator_yi": round(pre.total_yi, 2),
                "denominator_yi": group_cap,
                "ratio": round(pre.ratio, 4),
                "ratio_display": self._ratio_display(pre.ratio),
                "level": pre.level,
            },
            "post_r2": {
                "label": "纳入隐性关联后（R2 纳入后）",
                "numerator_yi": round(post.total_yi, 2),
                "denominator_yi": group_cap,
                "ratio": round(post.ratio, 4),
                "ratio_display": self._ratio_display(post.ratio),
                "level": post.level,
            },
            "note": (
                "纳入隐性关联（恒昌贸易）前后的归集口径对比；"
                "看板/报送口径为纳入隐性关联后（post_R2）"
            ),
        }
        return {
            "intent": "act1_group_reveal",
            "conclusion": conclusion,
            "basis_tables": [
                "concentration.ap_concentration_limit",
                "customer.ap_subsidiary_credit_detail",
                "base.ap_sys_param",
                "ap_warning_signal",
            ],
            "rules_hits": [
                {
                    "rule": "R1a",
                    "name": "集团层归集集中度",
                    "clause": R1A_CLAUSE,
                    "lines": R1A_LINES,
                    "computed": {
                        "numerator_yi": round(pre.total_yi, 2),
                        "denominator_yi": group_cap,
                        "ratio": round(pre.ratio, 4),
                        "ratio_display": self._ratio_display(pre.ratio),
                        "level": pre.level,
                    },
                },
                {
                    "rule": "R1b",
                    "name": "银行层授信集中度（对照）",
                    "clause": R1B_CLAUSE,
                    "lines": R1B_LINES,
                    "note": (
                        "对照口径：逐家单看均低于各自参考线/限额"
                        if all_safe
                        else "对照口径：逐家单看已有机构接近/超过参考线"
                    ),
                },
            ],
            "denominator": {
                "name": "集团并表资本",
                "value_yi": group_cap,
                "source": f"base.ap_sys_param.{PARAM_GROUP_CONSOLIDATED}",
            },
            "detail_rows": detail,
            "signals": signals,
            "r2_levels": r2_levels,
        }

    # ---- 第 2 幕：升级识别（恒昌三线索 + R2 纳入重算 12.8% 红）----

    def related_upgrade(
        self,
        *,
        group_customer_no: str | None = None,
        group_customer_name: str | None = None,
    ) -> dict[str, Any]:
        """第 2 幕升级识别：客户关系树三线索 + R2 纳入归集重算（与看板同源，F7）。

        定位：以 group_customer_no 为主键（名称仅展示，根因一串号修复）；线索明细 =
        customer.ap_customer_relation_tree（clear_remark_1/2/3）；重算 = risk_rules.
        evaluate_group_concentration(include_related=True)（ap_concentration_limit 台账
        口径，与看板同源）→ 天晟 102.4/800 = 12.8% 红。F7b：证据链显式给出 pre_R2/post_R2
        两行 + 「纳入隐性关联前后」说明。
        """
        if not group_customer_no and not group_customer_name:
            raise EvidenceError("必须提供 group_customer_no")
        with self._conn() as conn:
            gno, group = self._resolve_group(
                conn,
                group_customer_no=group_customer_no,
                group_customer_name=group_customer_name,
            )
            if not self._has_credit(conn, gno):
                raise EvidenceError(f"集团无集中度台账: {group}")
            # F7：post_R2（纳入后，本幕焦点）与 pre_R2（纳入前，第 1 幕口径）均由台账聚合
            r2 = evaluate_group_concentration(conn, gno, group, include_related=True)
            pre = evaluate_group_concentration(conn, gno, group, include_related=False)
            cfg = r2.config
            group_cap = cfg.group_capital_yi
            detail: list[dict[str, Any]] = []
            for p in r2.related_parties:
                tree_rows = conn.execute(
                    "SELECT customer_relation_tree_id, clear_remark_1, clear_remark_2, "
                    "clear_remark_3 FROM customer.ap_customer_relation_tree "
                    "WHERE customer_name=? AND group_customer_name=? "
                    "AND (clear_remark_1 IS NOT NULL OR clear_remark_2 IS NOT NULL "
                    "     OR clear_remark_3 IS NOT NULL)",
                    (p.customer_name, group),
                ).fetchall()
                clue_rows: list[dict[str, Any]] = []
                for t in tree_rows:
                    for i in range(1, 4):
                        text = t[f"clear_remark_{i}"]
                        if text:
                            clue_rows.append(
                                {
                                    "clue": next(
                                        (k for k in CLUE_KEYWORDS if k in text),
                                        f"线索{i}",
                                    ),
                                    "text": text,
                                    "column": f"clear_remark_{i}",
                                    "row_ref": (
                                        "customer.ap_customer_relation_tree"
                                        f"#{t['customer_relation_tree_id']}"
                                    ),
                                }
                            )
                detail.append(
                    {
                        "customer_name": p.customer_name,
                        "balance_yi": round(p.balance_yi, 2),
                        "clue_names": p.clues,
                        "relation_clues": clue_rows,
                    }
                )
            signals = self._group_signals(conn, gno)
        base = round(r2.own_balance_yi, 2)
        rel = round(r2.related_balance_yi, 2)
        # P0-2 结论自检：R2 纳入后比较短语由 computed ratio 实算生成（杜绝「>12% 却定级非红」）
        compare = self._r1a_comparison_text(r2.ratio, cfg)
        self._assert_level_consistent(r2.ratio, cfg, r2.level, "第 2 幕 related_upgrade")
        red = next((s for s in signals if s["warn_level"] == "红"), None)
        party_txt = "、".join(
            f"{d['customer_name']}（{d['balance_yi']:.1f} 亿，{('、'.join(d['clue_names']))}）"
            for d in detail
        )
        conclusion = (
            f"经客户关系树三线索交叉识别隐性一致行动人：{party_txt or '无'}。"
            f"纳入归集重算：{group} 自身 {base:.1f} 亿 + 关联方 {rel:.1f} 亿 = "
            f"{r2.total_yi:.1f} 亿元 ÷ 集团并表资本 {group_cap:.0f} 亿元 = "
            f"{compare} → R1a+R2 定级「{r2.level}」"
            + ("，红色预警信号已生成" if red else "")
        )
        # F7b：pre_R2 / post_R2 两行（与第 1 幕揭示同构，说明「纳入隐性关联前后」）
        r2_levels = {
            "pre_r2": {
                "label": "纳入隐性关联前（R2 纳入前）",
                "numerator_yi": round(pre.total_yi, 2),
                "denominator_yi": group_cap,
                "ratio": round(pre.ratio, 4),
                "ratio_display": self._ratio_display(pre.ratio),
                "level": pre.level,
            },
            "post_r2": {
                "label": "纳入隐性关联后（R2 纳入后）",
                "numerator_yi": round(r2.total_yi, 2),
                "denominator_yi": group_cap,
                "ratio": round(r2.ratio, 4),
                "ratio_display": self._ratio_display(r2.ratio),
                "level": r2.level,
            },
            "note": (
                "纳入隐性关联（恒昌贸易）前后的归集口径对比；"
                "看板/报送口径为纳入隐性关联后（post_R2）"
            ),
        }
        return {
            "intent": "act2_related_upgrade",
            "conclusion": conclusion,
            "basis_tables": [
                "customer.ap_customer_relation_tree",
                "concentration.ap_concentration_limit",
                "customer.ap_subsidiary_credit_detail",
                "base.ap_sys_param",
                "ap_warning_signal",
            ],
            "rules_hits": [
                {
                    "rule": "R2",
                    "name": "关联客户组归集",
                    "clause": R2_CLAUSE,
                    "lines": R2_DESC,
                    "computed": {
                        "related_balance_yi": rel,
                        "related_parties": [
                            {
                                "customer_name": d["customer_name"],
                                "balance_yi": d["balance_yi"],
                            }
                            for d in detail
                        ],
                    },
                },
                {
                    "rule": "R1a",
                    "name": "集团层归集集中度（R2 纳入后重算）",
                    "clause": R1A_CLAUSE,
                    "lines": R1A_LINES,
                    "computed": {
                        "numerator_yi": round(r2.total_yi, 2),
                        "denominator_yi": group_cap,
                        "ratio": round(r2.ratio, 4),
                        "ratio_display": self._ratio_display(r2.ratio),
                        "level": r2.level,
                    },
                },
            ],
            "denominator": {
                "name": "集团并表资本",
                "value_yi": group_cap,
                "source": f"base.ap_sys_param.{PARAM_GROUP_CONSOLIDATED}",
            },
            "detail_rows": detail,
            "signals": signals,
            "r2_levels": r2_levels,
        }

    # ---- 质疑/复核实查（R2-P0-A）：标红/橙行的真实原因维度（集中度 vs 非集中度）----

    def verify_red_reason(
        self,
        *,
        group_customer_no: str | None = None,
        group_customer_name: str | None = None,
    ) -> dict[str, Any]:
        """质疑/复核实查：被质疑「rank3 才 1% 凭什么挂红」时，先查库实算再开口。

        定位：以 group_customer_no 为主键（名称仅展示，根因一串号修复）。集中度口径与
        看板 _concentration_ranking 完全一致——concentration.ap_concentration_limit
        按集团编号聚合 + R2 隐性关联方（ap_customer_relation_tree 三线索）纳入，
        ÷ 集团并表资本，R1a 三线定级；warning_dimension = non_concentration
        当且仅当信号红/橙但集中度实算无警（杜绝「低比例却挂红」套集中度逻辑错答）。
        查无实据 → fail-closed 拒答。
        """
        if not group_customer_no and not group_customer_name:
            raise EvidenceError("必须提供 group_customer_no")
        with self._conn() as conn:
            gno, group = self._resolve_group(
                conn,
                group_customer_no=group_customer_no,
                group_customer_name=group_customer_name,
            )
            cap = self._capital_params(conn)
            group_cap = cap[PARAM_GROUP_CONSOLIDATED]
            # F7：集中度实算统一走 evaluate_group_concentration（台账聚合 + R2，与看板同源）
            gc = evaluate_group_concentration(conn, gno, group, include_related=True)
            cfg = gc.config
            own_yi = round(gc.own_balance_yi, 4)
            hidden_yi = round(gc.related_balance_yi, 4)
            total_yi = round(gc.total_yi, 4)
            ratio = gc.ratio
            conc_level = gc.level
            hidden = gc.related_parties
            signals = self._group_signals(conn, gno)
            sig = signals[0] if signals else None
        sig_level = sig["warn_level"] if sig else None
        is_r1a = sig is not None and (R1A_RULE_MARKER in (sig["warn_reason"] or ""))
        is_non_conc = (
            sig is not None
            and sig_level in ("红", "橙")
            and conc_level == LEVEL_NONE
            and not is_r1a
        )
        dimension = "non_concentration" if is_non_conc else "concentration"
        compare = self._r1a_comparison_text(ratio, cfg)
        reason_text = (sig["warn_reason"] or "") if sig else ""
        # F2 修复：verify-reason 先查 warning_dimension 再答——
        # ① 颜色按信号实级（「标红/标橙」），杜绝「橙说成红」；
        # ② 非集中度维度下，浓度类文案不得硬归「行为/内控/模型评分」维度（循环自指）：
        #    文案提及集中度但实算未达关注线 → 明说口径不一致、以实算为准。
        if is_non_conc:
            color = sig_level or "红/橙"
            if "集中度" in reason_text:
                trigger = (
                    f"信号登记事由 = 「{reason_text}」（提及集中度，但实算集中度 "
                    f"{self._ratio_display(ratio)} 未达关注线 "
                    f"{cfg.concern_line * 100:.0f}%，按预警维度归类为非集中度类，"
                    "口径以实算为准）"
                )
            else:
                trigger = (
                    f"真实触发 = 「{reason_text}」（行为/内控/模型评分类硬规则命中）"
                )
            conclusion = (
                f"该行标{color}原因是非集中度维度：{group} 集中度实算 "
                f"{self._ratio_display(ratio)}（{compare}，R1a 定级「{conc_level}」），"
                f"与集中度阈值无关；{trigger}。"
            )
        elif sig_level in ("红", "橙"):
            conclusion = (
                f"该行标{sig_level}原因是集中度维度：{group} 集中度实算 "
                f"{self._ratio_display(ratio)}（{compare}，R1a 定级「{conc_level}」），"
                f"预警信号 = 「{reason_text}」。"
            )
        else:
            conclusion = (
                f"{group} 当前无红/橙预警信号（最新信号等级 = {sig_level or '无'}）；"
                f"集中度实算 {self._ratio_display(ratio)}（{compare}，R1a 定级「{conc_level}」）。"
                "用户所指标红行若无对应信号，请核对集团编号与看板列。"
            )
        rules_hits = [
            {
                "rule": "R1a",
                "name": "集团层归集集中度（实查比对）",
                "clause": R1A_CLAUSE,
                "lines": R1A_LINES,
                "computed": {
                    "numerator_yi": round(total_yi, 2),
                    "denominator_yi": group_cap,
                    "ratio": ratio,
                    "ratio_display": self._ratio_display(ratio),
                    "level": conc_level,
                },
            }
        ]
        if is_non_conc:
            if "集中度" in reason_text:
                n1_clause = "非集中度预警维度（文案与集中度实算不一致，以实算为准）"
                n1_note = (
                    "信号文案提及集中度但实算未达关注线，按预警维度归类为非集中度类，"
                    "口径以实算为准（防文案与实算脱钩）"
                )
            else:
                n1_clause = "非集中度预警维度（行为/内控/模型评分硬规则命中）"
                n1_note = "该集团集中度实算无警却标红/橙，真实触发见 warn_reason"
            rules_hits.append(
                {
                    "rule": "N1",
                    "name": "非集中度预警维度（真实原因）",
                    "clause": n1_clause,
                    "text": reason_text,
                    "note": n1_note,
                }
            )
        return {
            "intent": "risk_verify_reason",
            "conclusion": conclusion,
            "basis_tables": [
                "concentration.ap_concentration_limit",
                "customer.ap_customer_relation_tree",
                "customer.ap_subsidiary_credit_detail",
                "base.ap_sys_param",
                "ap_warning_signal",
            ],
            "rules_hits": rules_hits,
            "denominator": {
                "name": "集团并表资本",
                "value_yi": group_cap,
                "source": f"base.ap_sys_param.{PARAM_GROUP_CONSOLIDATED}",
            },
            "detail_rows": [
                {
                    "group_customer_name": group,
                    "own_balance_yi": round(own_yi, 4),
                    "hidden_related_balance_yi": hidden_yi,
                    "consolidated_balance_yi": total_yi,
                    "concentration_ratio": ratio,
                    "concentration_level": conc_level,
                    "warning_dimension": dimension,
                    "signals": signals,
                    "related_parties": [
                        {"customer_name": p.customer_name, "balance_yi": p.balance_yi}
                        for p in hidden
                    ],
                }
            ],
            "warning_dimension": dimension,
        }

    # ---- 第 4 幕：双签驳回（处置审批链 + 2023 办法第二十三条驳回依据）----

    def approval_chain(
        self,
        *,
        group_customer_no: str | None = None,
        group_customer_name: str | None = None,
        signal_id: str | None = None,
        warning_id: str | None = None,
    ) -> dict[str, Any]:
        """第 4 幕双签驳回证据：处置方案 + 审批单/审批任务链（真数据）+ 驳回依据条款。

        定位任一预警信号（warning_id / signal_id / 集团编号），沿
        ap_warning_disposal → ap_approve_order（remark 内嵌信号号）→ ap_approve_task
        展开审批链；集团定位以 group_customer_no 为主键（名称仅展示，根因一串号修复）；
        固定携带 2023 关联交易办法第二十三条（驳回「拆分授信绕开归集」的依据）。
        """
        with self._conn() as conn:
            signal = self._resolve_signal(
                conn,
                warning_id=warning_id,
                signal_id=signal_id,
                group_customer_no=group_customer_no,
                group_name=group_customer_name,
            )
            if signal is None:
                raise EvidenceError(
                    "未找到对应预警信号（请提供 warning_id / signal_id / 集团名）"
                )
            disposal = None
            d = conn.execute(
                "SELECT * FROM ap_warning_disposal WHERE warning_id=?",
                (signal["warning_id"],),
            ).fetchone()
            if d:
                disposal = dict(d)
            orders = conn.execute(
                "SELECT * FROM approval.ap_approve_order "
                "WHERE substr(remark, instr(remark, 'SGN-'), 17) = ?",
                (signal["signal_id"],),
            ).fetchall()
            order_rows: list[dict[str, Any]] = []
            for o in orders:
                tasks = conn.execute(
                    "SELECT * FROM approval.ap_approve_task WHERE approve_order_id=? "
                    "ORDER BY approve_task_id",
                    (o["approve_order_id"],),
                ).fetchall()
                order_rows.append({"order": dict(o), "tasks": [dict(t) for t in tasks]})
        status = signal["signal_status"]
        disp_txt = (
            f"处置方案（{disposal['disposal_id']}）状态 = {disposal['disposal_status']}"
            if disposal
            else "无处置方案"
        )
        # F4 预置驳回态文案：REJECTED 单展示驳回意见（2023 办法第二十三条）+ 审计回放；
        # PROCESS 单提示可驳回；办结单给出结论。
        if order_rows:
            o0 = order_rows[0]["order"]
            o_status = o0["approve_order_status"]
            if o_status == "REJECTED":
                opinion = (o0.get("opinion_description") or "").strip()
                chain_txt = (
                    f"审批单 {o0['approve_order_id']} 状态 = REJECTED（已驳回"
                    + (f"，意见：{opinion}" if opinion else "")
                    + f"，任务 {len(order_rows[0]['tasks'])} 条）"
                )
                rejection_hint = (
                    "驳回依据 = 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易），"
                    "处置已退回重新起草。"
                )
            elif o_status == "PROCESS":
                chain_txt = (
                    f"审批单 {o0['approve_order_id']} 状态 = PROCESS"
                    f"（任务 {len(order_rows[0]['tasks'])} 条）"
                )
                rejection_hint = (
                    "审批人可依 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）"
                    "以 approve_disposal decision=REJECTED 驳回，处置退回重新起草。"
                )
            else:
                chain_txt = (
                    f"审批单 {o0['approve_order_id']} 状态 = {o_status}"
                    f"（任务 {len(order_rows[0]['tasks'])} 条）"
                )
                rejection_hint = "审批已办结。"
        else:
            chain_txt = "暂无待审批单"
            rejection_hint = ""
        # F4/F6：审批链审计回放——按审批单号取 approve_disposal 审计行（风险本体库，WORM）
        audit_trail: list[dict[str, Any]] = []
        order_ids = {o["order"]["approve_order_id"] for o in order_rows}
        if order_ids:
            try:
                oconn = self._store.ontology_conn()
                rows = oconn.execute(
                    "SELECT audit_id, ts, action_name, actor, actor_detail, outcome, "
                    "params_json, message FROM audit_log "
                    "WHERE action_name='approve_disposal' ORDER BY seq"
                ).fetchall()
                for r in rows:
                    params = r["params_json"] or ""
                    if any(oid in params for oid in order_ids):
                        audit_trail.append(dict(r))
            except Exception:  # noqa: BLE001  # 审计回放尽力而为：本体审计库不可读时证据链仍须返回
                audit_trail = []
            finally:
                oconn.close()
        conclusion = (
            f"预警 {signal['signal_id']}（等级 {signal['warn_level']}，状态 {status}）；"
            f"{disp_txt}；{chain_txt}。{rejection_hint}"
        )
        return {
            "intent": "act4_approval_chain",
            "conclusion": conclusion,
            "basis_tables": [
                "ap_warning_signal",
                "ap_warning_disposal",
                "approval.ap_approve_order",
                "approval.ap_approve_task",
                "audit_log",
            ],
            "rules_hits": [
                {
                    "rule": "2023 关联交易办法第二十三条",
                    "name": "禁止隐匿关联关系拆分交易",
                    "clause": "《金融控股公司关联交易管理办法》（中国人民银行令〔2023〕第 1 号）第二十三条",
                    "text": ARTICLE_2023_23,
                    "note": "AI 提议「拆分授信至非关联第三方通道主体绕开归集」即命中本条，审批人据此驳回",
                }
            ],
            "denominator": None,
            "detail_rows": [
                {
                    "signal": signal,
                    "disposal": disposal,
                    "approve_orders": order_rows,
                    "audit_trail": audit_trail,
                }
            ],
        }

    @staticmethod
    def _resolve_signal(
        conn: sqlite3.Connection,
        *,
        warning_id: str | None,
        signal_id: str | None,
        group_customer_no: str | None,
        group_name: str | None = None,
    ) -> dict[str, Any] | None:
        if warning_id:
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, warn_reason "
                "FROM ap_warning_signal WHERE warning_id=?",
                (warning_id,),
            ).fetchone()
        elif signal_id:
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, warn_reason "
                "FROM ap_warning_signal WHERE signal_id=?",
                (signal_id,),
            ).fetchone()
        elif group_customer_no or group_name:
            if group_customer_no:
                gno = group_customer_no
            else:
                rows = conn.execute(
                    "SELECT group_customer_no FROM customer.ap_group_customer "
                    "WHERE group_customer_name=?",
                    (group_name,),
                ).fetchall()
                if not rows:
                    return None
                if len(rows) > 1:
                    raise EvidenceError(
                        f"集团名「{group_name}」不唯一，请用 group_customer_no 精确定位"
                    )
                gno = rows[0]["group_customer_no"]
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, warn_reason "
                "FROM ap_warning_signal WHERE group_customer_no=? "
                "ORDER BY CASE warn_level WHEN '红' THEN 0 WHEN '橙' THEN 1 "
                "WHEN '黄' THEN 2 ELSE 3 END LIMIT 1",
                (gno,),
            ).fetchone()
        else:
            raise EvidenceError(
                "必须提供 warning_id / signal_id / group_customer_no 之一"
            )
        return dict(row) if row else None

    # ---- 通用：risk_query 受限契约结果 → 最小证据链载荷 ----

    def query_evidence(
        self, registry: Any, contract: dict, result: dict
    ) -> dict[str, Any] | None:
        """risk_query 契约 → 最小证据链载荷（依据表名/明细行引用；「每个答案都带证据链」）。

        剧本工具（group_reveal/related_upgrade/approval_chain）返回全量证据；
        普通 risk_query 查询在此合成最小载荷——证据链点开同样落到真实源表。
        """
        if not isinstance(result, dict):
            return None
        if contract.get("analytic"):
            name = contract.get("analytic")
            return {
                "intent": f"risk_query:{name}",
                "conclusion": f"受限多跳分析 {name} 返回 {len(result.get('rows', []))} 行",
                "basis_tables": ANALYTIC_TABLES.get(name, []),
                "rules_hits": [],
                "denominator": None,
                "detail_rows": result.get("rows", [])[:5],
            }
        api_name = contract.get("object_type")
        if not api_name:
            return None
        obj = next((o for o in registry.object_types() if o.api_name == api_name), None)
        table = obj.source_table if obj else api_name
        count = (
            result.get("count")
            if result.get("count") is not None
            else result.get("row_count", 0)
        )
        detail = [
            {
                "pk": item.get("pk"),
                "row_ref": f"{table}#{item.get('pk')}" if item.get("pk") else table,
            }
            for item in result.get("items", [])[:5]
        ]
        return {
            "intent": f"risk_query:{api_name}",
            "conclusion": f"查询 {api_name} 命中 {count} 行（源表 {table}）",
            "basis_tables": [table],
            "rules_hits": [],
            "denominator": None,
            "detail_rows": detail,
        }


__all__ = [
    "ANALYTIC_TABLES",
    "ARTICLE_2023_23",
    "CLUE_KEYWORDS",
    "R1A_CLAUSE",
    "R1A_LINES",
    "R1B_CLAUSE",
    "R1B_LINES",
    "R2_CLAUSE",
    "R2_DESC",
    "EvidenceError",
    "EvidenceService",
]
