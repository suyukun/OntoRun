"""S4 M3a 独立前置包 · 读侧端点：监管报送初稿 + 全局督办看板。

独立于既有风险读引擎（RiskQuery）与动作写回链（risk_actions_impl / risk_agent），
仅做只读聚合，供演示第 5 幕（监管动作：大额风险暴露口径报送初稿）与第 6 幕
（全局督办看板）消费。数据全部从 ap_anping 六库实算（读侧），禁 mock。

口径回链 docs/v0.4-核心链口径包-v0.3.md：
- §一 资本常量（集团并表资本 800 亿；银行层 600/480/60；证券分母 400/资管分母 200）
  —— 落 base.ap_sys_param（与 risk_script_props.CAPITAL_PARAMS 同源）；
- §三 R1a 三线（关注 9% / 预警 10% / 内部限额 12%）；R2 关联客户组归集（恒昌三线索）；
- §七 第 5 幕：红色预警触发大额风险暴露口径监管报送初稿（2018 办法第三十七/三十四条文案）；
- §七 第 6 幕：全局督办看板（前十大集团集中度 / 七态计数 / 待确认·处置中超期数 / 附属机构响应时效）。

口径说明（归集余额）：
- 归集余额 = 联合授信台账 ap_subsidiary_credit_detail.business_balance（单位=万元）按
  ap_customer.customer_name 关联出真实集团身份（group_customer_no）后求和，/10000 → 亿；
- 看板「前十大集团客户集中度排名」排名对象 = concentration.ap_concentration_limit 按集团
  聚合的归集余额（口径包§一 集团层归集监测）+ R2 隐性关联方归集（口径包§七 第 2 幕），
  ÷ 集团并表资本 800 亿；天晟 = 自身 86.4 + 恒昌 16 = 102.4 亿 → 12.8% 红、瑞华 9.4% 黄
  （与 verify_demo_numbers.py 实算一致），其后为小额背景集团（级别按 R1a 实算，<9% 不标红/橙）；
- 报送初稿归集 = 集团自身归集 + 经 ap_customer_relation_tree 识别的隐性关联方归集（R2），
  天晟红色案例 = 86.4 + 恒昌 16 = 102.4 亿 → 12.8%。
"""

from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.runtime.risk_db import RiskStore
from src.runtime.risk_rules import (
    LEVEL_NONE,
    R1A_RULE_MARKER,
    R1aConfig,
    concentration_ledger_aggregation_yi,
    evaluate_group_concentration,
    pct_display,
)

# ---------------------------------------------------------------------------
# 资本与限额常量 id（口径包§一/§三，读 base.ap_sys_param，单一来源）
# ---------------------------------------------------------------------------
PARAM_GROUP_CONSOLIDATED = "CAP_GROUP_CONSOLIDATED"  # 集团并表资本（亿）=800
PARAM_BANK_NET = "CAP_BANK_NET"  # 安平银行资本净额（亿）=600
PARAM_BANK_TIER1 = "CAP_BANK_TIER1"  # 安平银行一级资本净额（亿）=480
PARAM_BANK_INTERNAL_LIMIT = "CAP_BANK_INTERNAL_LIMIT"  # 行内内部限额（亿）=60
PARAM_SECURITIES_DENOM = "CAP_SECURITIES_DENOM"  # 证券参考线分母（亿）=400
PARAM_AM_DENOM = "CAP_AM_DENOM"  # 资管参考线分母（亿）=200
PARAM_CONCERN_LINE = "CAP_CONCERN_LINE"  # R1a 关注线 9%（黄）
PARAM_WARN_LINE = "CAP_WARN_LINE"  # R1a 预警线 10%（橙）
PARAM_INTERNAL_LIMIT_RATIO = "CAP_INTERNAL_LIMIT_RATIO"  # R1a 内部限额 12%（红）

# 2018 办法（银保监会令 2018 年第 1 号《商业银行大额风险暴露管理办法》）
# 依据条款文案（gov.cn 国务院公报 2018 年第 20 号原文）—— 报送初稿固定引用
ARTICLE_2018_37 = (
    "第三十七条 商业银行突破大额风险暴露监管要求的，应立即报告银行业监督管理机构。"
)
ARTICLE_2018_34 = (
    "第三十四条 银行业监督管理机构定期评估商业银行大额风险暴露管理状况及效果，"
    "包括制度执行、系统建设、限额遵守、风险管控等，将评估意见反馈商业银行董事会和"
    "高级管理层，并将评估结果作为监管评级的重要参考。"
)

# 预警级别排序（红 > 橙 > 黄），取组内最高级信号
_LEVEL_RANK = {"红": 0, "橙": 1, "黄": 2}

# 各附属机构参考线分母（口径包§一「单看都安全」分母；其余机构不套用参考线）
_ORG_REFERENCE_DENOM: dict[str, str] = {
    "安平银行": PARAM_BANK_NET,
    "安平证券": PARAM_SECURITIES_DENOM,
    "安平资产管理": PARAM_AM_DENOM,
}

# 未销号（open）生命周期态（看板/超期口径）
_OPEN_STATUSES = ("待确认", "确认中", "已确认", "处置中")


def _pct_display(ratio: float) -> str:
    """百分比展示统一两位小数（F12：单一实现 = risk_rules.pct_display，全链同源）。"""
    return pct_display(ratio)


# F13 勾稽说明（口径包§一 内部抵销注记；与 risk_evidence.RECONCILIATION_NOTE 同源）
RECONCILIATION_NOTE = (
    "成员间交叉授信/内部融资已按并表口径抵销，归集数为抵销后外部净敞口；"
    "明细为单家口径（各附属机构外部融资逐家加总，未抵销），二者不可直接对比"
)


class _ReportService:
    """读侧聚合服务：全局督办看板 + 监管报送初稿（ap_anping 六库实算，只读）。"""

    def __init__(self, store: RiskStore | None = None) -> None:
        self._store = store or RiskStore()

    def _conn(self) -> sqlite3.Connection:
        return self._store.source_conn()

    # ---- 基础口径 ----

    def capital_params(self, conn: sqlite3.Connection) -> dict[str, float]:
        rows = conn.execute(
            "SELECT param_id, param_value FROM ap_sys_param "
            "WHERE param_type_code = 'CAPITAL' AND param_id IN ("
            "?,?,?,?,?,?,?,?,?)",
            (
                PARAM_GROUP_CONSOLIDATED,
                PARAM_BANK_NET,
                PARAM_BANK_TIER1,
                PARAM_BANK_INTERNAL_LIMIT,
                PARAM_SECURITIES_DENOM,
                PARAM_AM_DENOM,
                PARAM_CONCERN_LINE,
                PARAM_WARN_LINE,
                PARAM_INTERNAL_LIMIT_RATIO,
            ),
        ).fetchall()
        return {r["param_id"]: float(r["param_value"]) for r in rows}

    @staticmethod
    def as_of_date(conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT MAX(signal_generate_date) m FROM ap_warning_signal"
        ).fetchone()
        return row["m"] or "2026-12-31"

    # ---- 归集余额（亿）：与证据链同源（F7：ap_concentration_limit 台账聚合，
    # 见 risk_rules.concentration_ledger_aggregation_yi / evaluate_group_concentration） ----

    def hidden_related_yi(
        self, conn: sqlite3.Connection, group_name: str
    ) -> list[dict[str, Any]]:
        """经客户关系树识别并纳入归集的隐性关联方（R2，口径包§三）。"""
        names = conn.execute(
            "SELECT DISTINCT customer_name FROM ap_customer_relation_tree "
            "WHERE group_customer_name = ? AND customer_name IS NOT NULL "
            "AND (clear_remark_1 IS NOT NULL OR clear_remark_2 IS NOT NULL "
            "     OR clear_remark_3 IS NOT NULL)",
            (group_name,),
        ).fetchall()
        out: list[dict[str, Any]] = []
        for r in names:
            name = r["customer_name"]
            bal = conn.execute(
                "SELECT SUM(business_balance) t FROM ap_subsidiary_credit_detail "
                "WHERE customer_name = ?",
                (name,),
            ).fetchone()
            clues = conn.execute(
                "SELECT clear_remark_1, clear_remark_2, clear_remark_3 "
                "FROM ap_customer_relation_tree WHERE customer_name = ? "
                "AND group_customer_name = ?",
                (name, group_name),
            ).fetchall()
            remark = [
                c[k]
                for c in clues
                for k in ("clear_remark_1", "clear_remark_2", "clear_remark_3")
                if c[k]
            ]
            out.append(
                {
                    "customer_name": name,
                    "balance_yi": round((bal["t"] or 0.0) / 10000.0, 4),
                    "relation_clues": list(dict.fromkeys(remark)),
                }
            )
        return out

    def group_credit_breakdown(
        self, conn: sqlite3.Connection, group_no: str, denoms: dict[str, float]
    ) -> list[dict[str, Any]]:
        # 按唯一 cert_no 关联真实集团身份（group_customer_no），杜绝同名客户跨集团串号
        # F13：明细行区分「外部融资敞口」与「集团内部成员间交叉授信」（并表口径下
        # 集团内部融资须抵销，不并入归集分子）——以融资对手方是否为安平金控成员判定。
        rows = conn.execute(
            "SELECT s.org_name, SUM(s.business_balance) t, "
            "SUM(CASE WHEN s.customer_name LIKE '安平%' "
            "     THEN s.business_balance ELSE 0 END) AS internal_t "
            "FROM ap_subsidiary_credit_detail s "
            "JOIN ap_customer c ON s.cert_no = c.cert_no "
            "WHERE c.group_customer_no = ? GROUP BY s.org_name ORDER BY t DESC",
            (group_no,),
        ).fetchall()
        out = []
        for r in rows:
            raw_yi = (r["t"] or 0.0) / 10000.0
            internal_yi = round((r["internal_t"] or 0.0) / 10000.0, 4)
            yi = round(raw_yi, 4)
            denom = denoms.get(r["org_name"])
            item: dict[str, Any] = {
                "org_name": r["org_name"],
                "balance_yi": yi,
                "external_balance_yi": round(raw_yi - internal_yi, 4),
                "internal_balance_yi": internal_yi,
                "is_internal": internal_yi > 0,
            }
            if denom:
                item["reference_denom_yi"] = denom
                item["org_reference_ratio"] = round(yi / denom, 4)
            out.append(item)
        return out

    # ---- 看板 ----

    def dashboard(self, overdue_days: int = 30) -> dict[str, Any]:
        if overdue_days < 1 or overdue_days > 365:
            raise ValueError(f"overdue_days 必须在 1..365（收到 {overdue_days}）")
        with self._conn() as conn:
            cap = self.capital_params(conn)
            as_of = self.as_of_date(conn)
            as_of_date = date.fromisoformat(as_of)
            cutoff = (as_of_date - timedelta(days=overdue_days)).isoformat()
            conc = self._concentration_ranking(conn, cap)
            return {
                "as_of_date": as_of,
                "capital": self._capital_block(cap),
                "overdue_days_threshold": overdue_days,
                "group_concentration_ranking": conc["ranking"],
                "non_concentration_warnings": conc["non_concentration_warnings"],
                "signal_status_distribution": self._signal_status_dist(conn),
                "overdue": self._overdue(conn, cutoff),
                "subsidiary_response": self._subsidiary_response(conn, as_of),
            }

    @staticmethod
    def _capital_block(cap: dict[str, float]) -> dict[str, float]:
        return {
            "group_consolidated_capital_yi": cap[PARAM_GROUP_CONSOLIDATED],
            "bank_net_capital_yi": cap[PARAM_BANK_NET],
            "bank_tier1_capital_yi": cap[PARAM_BANK_TIER1],
            "bank_internal_limit_yi": cap[PARAM_BANK_INTERNAL_LIMIT],
            "concern_line": cap[PARAM_CONCERN_LINE],
            "warn_line": cap[PARAM_WARN_LINE],
            "internal_limit_ratio": cap[PARAM_INTERNAL_LIMIT_RATIO],
        }

    def _concentration_ranking(
        self, conn: sqlite3.Connection, cap: dict[str, float]
    ) -> dict[str, Any]:
        """前十大集团客户集中度排名（P0-3 看板自洽修复）。

        - 分子 = **R2 纳入后口径**：自身归集 + 隐性关联方归集（恒昌→天晟 16 亿），
          天晟 102.4 亿 → 12.8% 红（口径包§七 第 2 幕，不再显示 10.8% 红矛盾）；
        - 级别展示与比例校验一致：concentration_level 由 R1a 按 computed ratio 实算
          （<9% 定级「无」，绝不标红/橙）；
        - 非集中度类预警（行为/合规等硬规则命中，级别高于集中度实算）→ 分列维度
          non_concentration_warnings，不再混进集中度排名的级别列。
        """
        cfg = R1aConfig.load(conn)
        rows = conn.execute(
            "SELECT a.group_customer_no AS gno, a.group_customer_name AS gname "
            "FROM concentration.ap_concentration_limit cl "
            "JOIN customer.ap_customer a ON a.customer_no = cl.customer_no "
            "GROUP BY gno ORDER BY SUM(cl.concentration_limit) DESC LIMIT 20"
        ).fetchall()
        ranking = []
        non_conc: list[dict[str, Any]] = []
        for r in rows:
            gno = r["gno"]
            gname = r["gname"]
            # F7：归集/隐性关联/定级统一走 evaluate_group_concentration（与证据链同源，
            # ap_concentration_limit 台账聚合 + R2，单一事实来源）
            gc = evaluate_group_concentration(
                conn, gno, gname, include_related=True, config=cfg
            )
            own_yi = round(gc.own_balance_yi, 4)
            hidden_yi = round(gc.related_balance_yi, 4)
            total_yi = round(gc.total_yi, 4)
            ratio = round(gc.ratio, 4)
            conc_level = gc.level
            sig = conn.execute(
                "SELECT signal_id, warn_level, signal_status, warn_reason "
                "FROM ap_warning_signal WHERE group_customer_no = ? ORDER BY "
                "CASE warn_level WHEN '红' THEN 0 WHEN '橙' THEN 1 "
                "WHEN '黄' THEN 2 ELSE 3 END LIMIT 1",
                (gno,),
            ).fetchone()
            n_sig = conn.execute(
                "SELECT COUNT(*) n FROM ap_warning_signal WHERE group_customer_no = ?",
                (gno,),
            ).fetchone()["n"]
            sig_level = sig["warn_level"] if sig else None
            # 维度判定：最新信号为红/橙但集中度实算无警，且非 R1a 标记（R5/R6 硬规则等）
            # → 非集中度类预警，分列维度
            is_r1a = sig is not None and (R1A_RULE_MARKER in (sig["warn_reason"] or ""))
            is_non_conc = (
                sig is not None
                and sig_level in ("红", "橙")
                and conc_level == LEVEL_NONE
                and not is_r1a
            )
            item: dict[str, Any] = {
                "group_customer_no": gno,
                "group_customer_name": gname,
                "own_balance_yi": round(own_yi, 4),
                "hidden_related_balance_yi": hidden_yi,
                "consolidated_balance_yi": total_yi,
                "concentration_ratio": ratio,
                "concentration_level": conc_level,
                "latest_warn_level": sig_level,
                "latest_signal_status": sig["signal_status"] if sig else None,
                "signal_count": n_sig,
                "warning_dimension": (
                    "non_concentration" if is_non_conc else "concentration"
                ),
            }
            ranking.append(item)
            if is_non_conc:
                non_conc.append(
                    {
                        "group_customer_no": gno,
                        "group_customer_name": gname,
                        "concentration_ratio": ratio,
                        "signal_id": sig["signal_id"],
                        "warn_level": sig_level,
                        "signal_status": sig["signal_status"],
                        "warn_reason": sig["warn_reason"],
                    }
                )
        ranking.sort(key=lambda g: g["concentration_ratio"], reverse=True)
        for i, g in enumerate(ranking, start=1):
            g["rank"] = i
        return {"ranking": ranking[:10], "non_concentration_warnings": non_conc}

    @staticmethod
    def _signal_status_dist(conn: sqlite3.Connection) -> dict[str, int]:
        dist: dict[str, int] = {}
        for r in conn.execute(
            "SELECT signal_status, COUNT(*) n FROM ap_warning_signal "
            "GROUP BY signal_status"
        ):
            dist[r["signal_status"]] = r["n"]
        return dist

    @staticmethod
    def _overdue(conn: sqlite3.Connection, cutoff: str) -> dict[str, Any]:
        def cnt(where: str) -> int:
            return conn.execute(
                f"SELECT COUNT(*) n FROM ap_warning_signal WHERE {where}",
                (cutoff,),
            ).fetchone()["n"]

        pending = cnt("signal_status = '待确认' AND signal_generate_date < ?")
        disposal = cnt("signal_status = '处置中' AND signal_establish_date < ?")
        return {
            "pending_confirm_overdue": pending,
            "in_disposal_overdue": disposal,
            "cutoff_date": cutoff,
        }

    @staticmethod
    def _subsidiary_response(
        conn: sqlite3.Connection, as_of: str
    ) -> list[dict[str, Any]]:
        """各附属机构响应时效：open 信号平均滞留天数（拖沓度）+ 处置平均时长。"""
        open_rows = conn.execute(
            f"SELECT org_name, COUNT(*) n, "
            f"AVG(julianday(?) - julianday(signal_generate_date)) avg_age "
            f"FROM ap_warning_signal WHERE signal_status IN "
            f"({','.join('?' * len(_OPEN_STATUSES))}) GROUP BY org_name",
            (as_of, *_OPEN_STATUSES),
        ).fetchall()
        disp_rows = conn.execute(
            "SELECT s.org_name, COUNT(*) n, "
            "AVG(julianday(d.operate_time) - julianday(s.signal_generate_date)) avg_days "
            "FROM ap_warning_disposal d JOIN ap_warning_signal s "
            "ON d.warning_id = s.warning_id WHERE d.disposal_status = '已处置' "
            "AND d.operate_time IS NOT NULL AND s.signal_generate_date IS NOT NULL "
            "AND julianday(d.operate_time) >= julianday(s.signal_generate_date) "
            "GROUP BY s.org_name",
        ).fetchall()
        by_org = {
            r["org_name"]: {
                "org_name": r["org_name"],
                "open_signal_count": r["n"],
                "avg_open_age_days": round(r["avg_age"], 1) if r["avg_age"] else 0.0,
            }
            for r in open_rows
        }
        for r in disp_rows:
            item = by_org.setdefault(
                r["org_name"],
                {
                    "org_name": r["org_name"],
                    "open_signal_count": 0,
                    "avg_open_age_days": 0.0,
                },
            )
            item["completed_disposal_count"] = r["n"]
            item["avg_disposal_days"] = (
                round(r["avg_days"], 1) if r["avg_days"] else 0.0
            )
        out = sorted(
            by_org.values(), key=lambda g: g["avg_open_age_days"], reverse=True
        )
        for item in out:
            item.setdefault("completed_disposal_count", 0)
            item.setdefault("avg_disposal_days", 0.0)
        return out

    # ---- 监管报送初稿（口径包§七 第 5 幕）----

    def reporting_draft(
        self,
        *,
        warning_id: str | None = None,
        signal_id: str | None = None,
        group_customer_no: str | None = None,
    ) -> dict[str, Any]:
        with self._conn() as conn:
            cap = self.capital_params(conn)
            group_cap = cap[PARAM_GROUP_CONSOLIDATED]
            signal = self._resolve_red_signal(
                conn,
                warning_id=warning_id,
                signal_id=signal_id,
                group_customer_no=group_customer_no,
            )
            gno = signal["group_customer_no"] or group_customer_no
            name_row = conn.execute(
                "SELECT group_customer_name FROM ap_group_customer "
                "WHERE group_customer_no = ?",
                (gno,),
            ).fetchone()
            group_name = name_row["group_customer_name"] if name_row else None
            # F7：报送归集分子与看板/证据链同源（ap_concentration_limit 台账聚合）
            own_yi = concentration_ledger_aggregation_yi(conn, gno)
            hidden = self.hidden_related_yi(conn, group_name) if group_name else []
            hidden_yi = round(sum(h["balance_yi"] for h in hidden), 4)
            total_yi = round(own_yi + hidden_yi, 4)
            ratio = round(total_yi / group_cap, 4) if group_cap else 0.0
            breakdown = self.group_credit_breakdown(
                conn,
                gno,
                {org: cap[denom] for org, denom in _ORG_REFERENCE_DENOM.items()},
            )
            # 双时钟统一（R2-P0-C）：数据时钟保持不动（生成器 ANCHOR 既定设计），
            # generated_at / data_as_of 一律取数据内时钟（MAX(signal_generate_date)），
            # 不再混用真实 UTC 时钟（否则 2026-09 真实时钟 vs 2026-12 数据时钟两套并存）。
            as_of = self.as_of_date(conn)
            return {
                "report_title": "大额风险暴露口径监管报送初稿",
                "generated_at": f"{as_of}T08:00:00+08:00",
                "data_as_of": as_of,
                "warning": {
                    "warning_id": signal["warning_id"],
                    "signal_id": signal["signal_id"],
                    "warn_level": signal["warn_level"],
                    "signal_status": signal["signal_status"],
                    "warn_reason": signal["warn_reason"],
                },
                "group_customer": {
                    "group_customer_no": gno,
                    "group_customer_name": group_name,
                },
                "consolidated_exposure": {
                    "own_balance_yi": own_yi,
                    "hidden_related_party_balance_yi": hidden_yi,
                    "total_balance_yi": total_yi,
                    "group_consolidated_capital_yi": group_cap,
                    "concentration_ratio": ratio,
                    "ratio_display": _pct_display(ratio),  # F6：展示统一两位小数
                    # F13：归集数为并表抵销后口径（成员间交叉授信/内部融资已抵销）
                    "caliber_note": RECONCILIATION_NOTE,
                },
                "breakdown": breakdown,
                "hidden_related_parties": hidden,
                "trigger_rules": [
                    {
                        "rule": "R1a",
                        "name": "集团层归集集中度",
                        "basis": "金控办法第三十二/三十三条（安平内部口径）",
                        "lines": "关注 9% / 预警 10% / 内部限额 12%",
                    },
                    {
                        "rule": "R2",
                        "name": "关联客户组归集",
                        "basis": "2018 办法附件 1 + 金控办法第三十三条",
                        "desc": "经联合授信识别隐性关联/一致行动人后纳入归集，按 R1a 重算",
                    },
                ],
                "regulatory_basis": [
                    {"article": "2018 办法第三十七条", "text": ARTICLE_2018_37},
                    {"article": "2018 办法第三十四条", "text": ARTICLE_2018_34},
                ],
            }

    @staticmethod
    def _resolve_red_signal(
        conn: sqlite3.Connection,
        *,
        warning_id: str | None,
        signal_id: str | None,
        group_customer_no: str | None,
    ) -> dict[str, Any]:
        if warning_id:
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, "
                "warn_reason, group_customer_no, customer_name "
                "FROM ap_warning_signal WHERE warning_id = ?",
                (warning_id,),
            ).fetchone()
        elif signal_id:
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, "
                "warn_reason, group_customer_no, customer_name "
                "FROM ap_warning_signal WHERE signal_id = ?",
                (signal_id,),
            ).fetchone()
        elif group_customer_no:
            row = conn.execute(
                "SELECT warning_id, signal_id, warn_level, signal_status, "
                "warn_reason, group_customer_no, customer_name "
                "FROM ap_warning_signal WHERE group_customer_no = ? "
                "AND warn_level = '红' ORDER BY signal_generate_date DESC LIMIT 1",
                (group_customer_no,),
            ).fetchone()
        else:
            raise ValueError("必须提供 warning_id / signal_id / group_customer_no 之一")
        if row is None:
            raise ValueError("未找到对应预警信号")
        if row["warn_level"] != "红":
            raise ValueError(
                f"监管报送初稿仅对红色预警生成（当前 {row['warn_level']}，"
                f"warning_id={row['warning_id']}）"
            )
        return dict(row)


class _ReportingDraftRequest(BaseModel):
    warning_id: str | None = Field(
        None, description="红色预警信号 warning_id（ap_warning_signal.warning_id）"
    )
    signal_id: str | None = Field(
        None, description="红色预警信号 signal_id（ap_warning_signal.signal_id）"
    )
    group_customer_no: str | None = Field(
        None, description="集团客户编号（取该集团红色预警生成报送初稿）"
    )


def _envelope(data: dict[str, Any]) -> JSONResponse:
    return JSONResponse(
        content={"request_id": "", "outcome": "ok", "data": data, "error": None}
    )


def _envelope_error(code: str, message: str, detail: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "request_id": "",
            "outcome": "error",
            "error": {"code": code, "message": message, "detail": detail},
        },
    )


def register_risk_reporting_routes(app: FastAPI) -> None:
    """挂载读侧端点（可在任意 FastAPI 实例上复用）：

    - GET  /risk/dashboard            全局督办看板聚合
    - GET  /risk/reporting/draft      监管报送初稿（红色预警，query 参数）
    - POST /risk/reporting/draft      监管报送初稿（红色预警，JSON body）
    """
    service = _ReportService()

    @app.get("/risk/dashboard")
    def risk_dashboard(request: Request):
        try:
            overdue_days = int(request.query_params.get("overdue_days", 30))
        except ValueError:
            return _envelope_error("INVALID_PARAM", "overdue_days 必须是整数")
        try:
            data = service.dashboard(overdue_days=overdue_days)
        except ValueError as exc:
            return _envelope_error("INVALID_PARAM", str(exc))
        return _envelope(data)

    @app.get("/risk/reporting/draft")
    def risk_reporting_draft_get(request: Request):
        return _build_draft(
            service,
            warning_id=request.query_params.get("warning_id"),
            signal_id=request.query_params.get("signal_id"),
            group_customer_no=request.query_params.get("group_customer_no"),
        )

    @app.post("/risk/reporting/draft")
    def risk_reporting_draft_post(body: _ReportingDraftRequest):
        return _build_draft(
            service,
            warning_id=body.warning_id,
            signal_id=body.signal_id,
            group_customer_no=body.group_customer_no,
        )


def _build_draft(
    service: _ReportService,
    *,
    warning_id: str | None,
    signal_id: str | None,
    group_customer_no: str | None,
) -> JSONResponse:
    try:
        data = service.reporting_draft(
            warning_id=warning_id,
            signal_id=signal_id,
            group_customer_no=group_customer_no,
        )
    except ValueError as exc:
        msg = str(exc)
        if "必须提供" in msg:
            code = "MISSING_IDENTIFIER"
        elif "未找到" in msg:
            code = "SIGNAL_NOT_FOUND"
        else:
            code = "NOT_RED_WARNING"
        return _envelope_error(code, msg)
    return _envelope(data)


__all__ = [
    "ARTICLE_2018_34",
    "ARTICLE_2018_37",
    "register_risk_reporting_routes",
]
