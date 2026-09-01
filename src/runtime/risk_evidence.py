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
from src.runtime.risk_rules import evaluate

# ---------------------------------------------------------------------------
# 常量与条款引用（口径包§一/§三/§七；参数 id 与 risk_reporting / risk_script_props 同源）
# ---------------------------------------------------------------------------
PARAM_GROUP_CONSOLIDATED = "CAP_GROUP_CONSOLIDATED"  # 集团并表资本（亿）= 800
PARAM_BANK_NET = "CAP_BANK_NET"  # 安平银行资本净额（亿）= 600
PARAM_BANK_INTERNAL_LIMIT = "CAP_BANK_INTERNAL_LIMIT"  # 行内内部限额（亿）= 60
PARAM_SECURITIES_DENOM = "CAP_SECURITIES_DENOM"  # 证券参考线分母（亿）= 400
PARAM_AM_DENOM = "CAP_AM_DENOM"  # 资管参考线分母（亿）= 200

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
}

_WAN_TO_YI = 10000.0  # business_balance 单位 = 万元 → 亿元


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
            "WHERE param_type_code = 'CAPITAL' AND param_id IN (?,?,?,?,?,?,?,?)",
            (
                PARAM_GROUP_CONSOLIDATED,
                PARAM_BANK_NET,
                PARAM_BANK_INTERNAL_LIMIT,
                PARAM_SECURITIES_DENOM,
                PARAM_AM_DENOM,
                "CAP_CONCERN_LINE",
                "CAP_WARN_LINE",
                "CAP_INTERNAL_LIMIT_RATIO",
            ),
        ).fetchall()
        return {r["param_id"]: float(r["param_value"]) for r in rows}

    @staticmethod
    def _ratio_display(ratio: float) -> str:
        return f"{ratio * 100:.1f}%"

    def _group_signals(
        self, conn: sqlite3.Connection, group_name: str
    ) -> list[dict[str, Any]]:
        """集团当前预警信号（证据链「明细行引用」：ap_warning_signal 行）。"""
        rows = conn.execute(
            "SELECT warning_id, signal_id, warn_level, signal_status, warn_reason "
            "FROM ap_warning_signal WHERE group_customer_no = "
            "(SELECT group_customer_no FROM customer.ap_group_customer "
            " WHERE group_customer_name=?) "
            "ORDER BY CASE warn_level WHEN '红' THEN 0 WHEN '橙' THEN 1 "
            "WHEN '黄' THEN 2 ELSE 3 END",
            (group_name,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ---- 第 1 幕：揭示（逐家单看都安全 → 归集 10.8% 橙）----

    def group_reveal(self, group_customer_name: str) -> dict[str, Any]:
        """第 1 幕揭示查询：逐家附属机构融资（真分母单看都安全）+ M2 引擎归集实算。

        分子逐家 = ap_subsidiary_credit_detail 按 org 汇总（与 verify_demo_numbers 同口径）；
        归集 = M2 引擎 risk_rules.evaluate(include_related=False) 实算（非查表回显）。
        """
        group = (group_customer_name or "").strip()
        if not group:
            raise EvidenceError("group_customer_name 不能为空")
        with self._conn() as conn:
            cap = self._capital_params(conn)
            r1a = evaluate(conn, group, include_related=False)  # M2 引擎实算
            cfg = r1a.config
            org_rows = conn.execute(
                "SELECT org_name, SUM(business_balance) AS t "
                "FROM customer.ap_subsidiary_credit_detail "
                "WHERE group_customer_name=? GROUP BY org_name ORDER BY t DESC",
                (group,),
            ).fetchall()
            detail: list[dict[str, Any]] = []
            for r in org_rows:
                yi = round((r["t"] or 0.0) / _WAN_TO_YI, 2)
                item: dict[str, Any] = {
                    "row_ref": (
                        f"customer.ap_subsidiary_credit_detail"
                        f"#group={group}&org={r['org_name']}"
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
            signals = self._group_signals(conn, group)
        group_cap = cfg.group_capital_yi
        warn = next((s for s in signals if s["warn_level"] == "橙"), None)
        conclusion = (
            f"{group} 逐家附属机构单看均安全（银行 {detail[0]['ratio_display'] if detail else '-'}"
            f"，低于行内限额 {cap[PARAM_BANK_INTERNAL_LIMIT]:.0f} 亿），但归集实算 "
            f"{r1a.total_yi:.1f} 亿元 ÷ 集团并表资本 {group_cap:.0f} 亿元 = "
            f"{self._ratio_display(r1a.ratio)} ≥ 预警线 10% → R1a 定级「{r1a.level}」"
            + ("，橙色预警信号已生成" if warn else "")
        )
        return {
            "intent": "act1_group_reveal",
            "conclusion": conclusion,
            "basis_tables": [
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
                        "numerator_yi": round(r1a.total_yi, 2),
                        "denominator_yi": group_cap,
                        "ratio": round(r1a.ratio, 4),
                        "ratio_display": self._ratio_display(r1a.ratio),
                        "level": r1a.level,
                    },
                },
                {
                    "rule": "R1b",
                    "name": "银行层授信集中度（对照）",
                    "clause": R1B_CLAUSE,
                    "lines": R1B_LINES,
                    "note": "对照口径：单看每家附属机构均安全（行内限额 60 亿内）",
                },
            ],
            "denominator": {
                "name": "集团并表资本",
                "value_yi": group_cap,
                "source": f"base.ap_sys_param.{PARAM_GROUP_CONSOLIDATED}",
            },
            "detail_rows": detail,
            "signals": signals,
        }

    # ---- 第 2 幕：升级识别（恒昌三线索 + R2 纳入重算 12.8% 红）----

    def related_upgrade(self, group_customer_name: str) -> dict[str, Any]:
        """第 2 幕升级识别：客户关系树三线索 + R2 纳入归集重算（M2 引擎实算）。

        线索明细 = customer.ap_customer_relation_tree（clear_remark_1/2/3）；
        重算 = risk_rules.evaluate(include_related=True) → 天晟 102.4/800 = 12.8% 红。
        """
        group = (group_customer_name or "").strip()
        if not group:
            raise EvidenceError("group_customer_name 不能为空")
        with self._conn() as conn:
            r2 = evaluate(conn, group, include_related=True)  # R1a+R2 实算
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
            signals = self._group_signals(conn, group)
        base = round(r2.base_aggregation_yi, 2)
        rel = round(r2.related_balance_yi, 2)
        red = next((s for s in signals if s["warn_level"] == "红"), None)
        party_txt = "、".join(
            f"{d['customer_name']}（{d['balance_yi']:.1f} 亿，{('、'.join(d['clue_names']))}）"
            for d in detail
        )
        conclusion = (
            f"经客户关系树三线索交叉识别隐性一致行动人：{party_txt or '无'}。"
            f"纳入归集重算：{group} 自身 {base:.1f} 亿 + 关联方 {rel:.1f} 亿 = "
            f"{r2.total_yi:.1f} 亿元 ÷ 集团并表资本 {group_cap:.0f} 亿元 = "
            f"{self._ratio_display(r2.ratio)} > 内部限额 12% → R1a+R2 定级「{r2.level}」"
            + ("，红色预警信号已生成" if red else "")
        )
        return {
            "intent": "act2_related_upgrade",
            "conclusion": conclusion,
            "basis_tables": [
                "customer.ap_customer_relation_tree",
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
        }

    # ---- 第 4 幕：双签驳回（处置审批链 + 2023 办法第二十三条驳回依据）----

    def approval_chain(
        self,
        *,
        group_customer_name: str | None = None,
        signal_id: str | None = None,
        warning_id: str | None = None,
    ) -> dict[str, Any]:
        """第 4 幕双签驳回证据：处置方案 + 审批单/审批任务链（真数据）+ 驳回依据条款。

        定位任一预警信号（warning_id / signal_id / 集团名），沿
        ap_warning_disposal → ap_approve_order（remark 内嵌信号号）→ ap_approve_task
        展开审批链；固定携带 2023 关联交易办法第二十三条（驳回「拆分授信绕开归集」的依据）。
        """
        with self._conn() as conn:
            signal = self._resolve_signal(
                conn,
                warning_id=warning_id,
                signal_id=signal_id,
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
        if order_rows:
            o0 = order_rows[0]["order"]
            chain_txt = (
                f"审批单 {o0['approve_order_id']} 状态 = {o0['approve_order_status']}"
                f"（任务 {len(order_rows[0]['tasks'])} 条）"
            )
            rejection_hint = (
                "审批人可依 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）"
                "以 approve_disposal decision=REJECTED 驳回，处置退回重新起草。"
                if o0["approve_order_status"] == "PROCESS"
                else "审批已办结。"
            )
        else:
            chain_txt = "暂无待审批单"
            rejection_hint = ""
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
                }
            ],
        }

    @staticmethod
    def _resolve_signal(
        conn: sqlite3.Connection,
        *,
        warning_id: str | None,
        signal_id: str | None,
        group_name: str | None,
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
        elif group_name:
            row = conn.execute(
                "SELECT w.warning_id, w.signal_id, w.warn_level, w.signal_status, "
                "w.warn_reason FROM ap_warning_signal w "
                "JOIN customer.ap_group_customer g ON w.group_customer_no = g.group_customer_no "
                "WHERE g.group_customer_name=? "
                "ORDER BY CASE w.warn_level WHEN '红' THEN 0 WHEN '橙' THEN 1 "
                "WHEN '黄' THEN 2 ELSE 3 END LIMIT 1",
                (group_name,),
            ).fetchone()
        else:
            raise EvidenceError(
                "必须提供 warning_id / signal_id / group_customer_name 之一"
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
