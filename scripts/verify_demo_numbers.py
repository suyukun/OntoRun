"""S4 金控演示数字核对表 —— 从再生后的 ap_anping 六库实算，口径包 v0.3 端到端可验算。

用法（工作目录 = OntoRun 根目录）：
    /opt/anaconda3/bin/python3 scripts/verify_demo_numbers.py

从库实算并核对（全部命中才算通过，退出码 0）：
- 资本常量（§一，落 base.ap_sys_param）：并表 800 亿 / 银行资本净额 600 / 一级 480 / 内部限额 60 /
  证券参考线 5.5%（分母 400）/ 资管 8.2%（分母 200）/ R1a 三线 9/10/12；
- 剧本道具（§七）：天晟 = 银行 48 亿(8.0%) + 证券 22 亿(5.5%) + 资管 16.4 亿(8.2%) = 归集 86.4 亿
  → 10.8% 橙；+ 隐性一致行动人恒昌贸易 16 亿 → 102.4 亿 → 12.8% 红；恒昌三条识别线索可从
  customer_relation_tree / customer_relation 回溯；瑞华 75.2 亿 → 9.4% 黄走完整解除闭环；
- 分布（§五）：预警级别 黄55/橙34/红11、事件类型 信用45/市场20/流动性15/合规12/操作8、
  生命周期七态 30/20/20/15/10/3/2；规模：信号 ~2 万 / 客户 ~5 万；名称纯净化（无「·编号尾巴」）；
  理由模板与事件类型严格对齐（level2 ∈ LEVEL2_BY_L1[event_type]）。
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
AP = ROOT / "data" / "des" / "enterprises" / "ap_anping"

from src.des.generators.risk_generators import LEVEL2_BY_L1  # noqa: E402 理由/事件类型同源集

# 口径包§一 期望常量（亿 / 参考线；与 risk_script_props.CAPITAL_PARAMS 同源）
EXPECT_CAPITAL = {
    "CAP_GROUP_CONSOLIDATED": "800",
    "CAP_BANK_NET": "600",
    "CAP_BANK_TIER1": "480",
    "CAP_BANK_INTERNAL_LIMIT": "60",
    "CAP_SECURITIES_REF_LINE": "0.055",
    "CAP_SECURITIES_DENOM": "400",
    "CAP_AM_REF_LINE": "0.082",
    "CAP_AM_DENOM": "200",
    "CAP_CONCERN_LINE": "0.09",
    "CAP_WARN_LINE": "0.10",
    "CAP_INTERNAL_LIMIT_RATIO": "0.12",
}


def _conn(db: str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(AP / f"{db}.db"))
    conn.row_factory = sqlite3.Row
    return conn


def _q(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, params))


def _close(*conns: sqlite3.Connection) -> None:
    for c in conns:
        c.close()


PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✓ {label} {detail}".rstrip())
    else:
        FAIL += 1
        print(f"  ✗ {label} {detail}".rstrip())


def near(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> int:
    print("===== S4 金控演示数字核对表（口径包 v0.3，库实算）=====")
    cust = _conn("customer")
    risk = _conn("risk")
    conc = _conn("concentration")
    base = _conn("base")

    # ---- 1. 资本常量（§一，base.ap_sys_param）----
    print("\n[1] 资本常量（§一，落 base.ap_sys_param）")
    rows = {r["param_id"]: r["param_value"] for r in _q(base, "SELECT param_id, param_value FROM ap_sys_param WHERE param_type_code='CAPITAL'")}
    for pid, expected in EXPECT_CAPITAL.items():
        check(f"常量 {pid}={expected}", rows.get(pid) == expected, f"(库值 {rows.get(pid)})")
    group_cap = float(rows.get("CAP_GROUP_CONSOLIDATED", 0))
    bank_net = float(rows.get("CAP_BANK_NET", 0))
    sec_denom = float(rows.get("CAP_SECURITIES_DENOM", 0))
    am_denom = float(rows.get("CAP_AM_DENOM", 0))

    # ---- 2. 剧本道具：天晟归集 10.8% 橙 / +恒昌 12.8% 红 / 9.4% 黄（§七）----
    print("\n[2] 剧本道具（§七，ap_subsidiary_credit_detail + ap_warning_signal 实算）")
    ts_group = "天晟集团有限公司"
    ts_rows = _q(
        cust,
        "SELECT org_name, business_balance FROM ap_subsidiary_credit_detail WHERE group_customer_name=?",
        (ts_group,),
    )
    bank_yi = sum(r["business_balance"] for r in ts_rows if r["org_name"] == "安平银行") / 10000
    sec_yi = sum(r["business_balance"] for r in ts_rows if r["org_name"] == "安平证券") / 10000
    am_yi = sum(r["business_balance"] for r in ts_rows if r["org_name"] == "安平资产管理") / 10000
    ts_total = bank_yi + sec_yi + am_yi
    hc_yi = sum(
        r["business_balance"]
        for r in _q(cust, "SELECT business_balance FROM ap_subsidiary_credit_detail WHERE customer_name=?", ("恒昌贸易有限公司",))
    ) / 10000
    rw_yi = sum(
        r["business_balance"]
        for r in _q(cust, "SELECT business_balance FROM ap_subsidiary_credit_detail WHERE customer_name=?", ("瑞华实业有限公司",))
    ) / 10000

    check("天晟@安平银行 48 亿", near(bank_yi, 48.0), f"(实算 {bank_yi} 亿)")
    check("天晟@安平证券 22 亿", near(sec_yi, 22.0), f"(实算 {sec_yi} 亿)")
    check("天晟@安平资管 16.4 亿", near(am_yi, 16.4), f"(实算 {am_yi} 亿)")
    check("天晟归集 86.4 亿", near(ts_total, 86.4), f"(实算 {ts_total} 亿)")
    check("恒昌贸易 16 亿", near(hc_yi, 16.0), f"(实算 {hc_yi} 亿)")
    check("瑞华 75.2 亿", near(rw_yi, 75.2), f"(实算 {rw_yi} 亿)")

    # 银行层单看都安全：48/600=8.0%（<行内限额 60 亿）；证券 22/400=5.5%；资管 16.4/200=8.2%
    check("银行层 8.0% = 48/600", near(bank_yi / bank_net, 0.080), f"(实算 {pct(bank_yi / bank_net)})")
    check("证券参考线 5.5% = 22/400", near(sec_yi / sec_denom, 0.055), f"(实算 {pct(sec_yi / sec_denom)})")
    check("资管参考线 8.2% = 16.4/200", near(am_yi / am_denom, 0.082), f"(实算 {pct(am_yi / am_denom)})")

    # 集团层归集：86.4/800 = 10.8% 橙；+恒昌 102.4/800 = 12.8% 红
    check("归集 10.8% = 86.4/800", near(ts_total / group_cap, 0.108), f"(实算 {pct(ts_total / group_cap)})")
    combined = ts_total + hc_yi
    check("归集(+恒昌) 12.8% = 102.4/800", near(combined / group_cap, 0.128), f"(实算 {pct(combined / group_cap)})")
    check("瑞华 9.4% = 75.2/800", near(rw_yi / group_cap, 0.094), f"(实算 {pct(rw_yi / group_cap)})")

    # 预警信号道具（warn_level + warn_reason 可验算）
    def _has_signal(level: str, fragment: str) -> bool:
        return bool(
            _q(
                risk,
                "SELECT warning_id FROM ap_warning_signal WHERE warn_level=? AND warn_reason LIKE ? LIMIT 1",
                (level, f"%{fragment}%"),
            )
        )

    check("橙色预警信号存在（10.8%≥预警线 10%）", _has_signal("橙", "10.8%"))
    check("红色预警信号存在（12.8%>内部限额 12%）", _has_signal("红", "12.8%"))
    check("黄色预警信号存在（9.4%≥关注线 9%）", _has_signal("黄", "9.4%"))

    # ---- 3. 恒昌三条识别线索可回溯（§七，客户关系树 + 相关表）----
    print("\n[3] 恒昌隐性一致行动人三线索回溯")
    clues = ["股权代持", "交叉担保", "资金往来"]
    for i, kw in enumerate(clues, start=1):
        col = f"clear_remark_{i}"
        tree_hit = _q(
            cust,
            f"SELECT customer_relation_tree_id FROM ap_customer_relation_tree "
            f"WHERE customer_name=? AND group_customer_name=? AND {col} LIKE ? AND {col} IS NOT NULL",
            ("恒昌贸易有限公司", ts_group, f"%{kw}%"),
        )
        rel_hit = _q(
            cust,
            f"SELECT customer_relation_id FROM ap_customer_relation "
            f"WHERE customer_name=? AND group_customer_name=? AND {col} LIKE ? AND {col} IS NOT NULL",
            ("恒昌贸易有限公司", ts_group, f"%{kw}%"),
        )
        check(f"线索{i}「{kw}」关系树可回溯", bool(tree_hit), f"(tree={len(tree_hit)}, rel={len(rel_hit)})")

    # ---- 4. 瑞华小额黄档完整解除闭环（§七 第 6 幕）----
    print("\n[4] 小额黄档完整解除闭环（瑞华）")
    rw_sig = _q(
        risk,
        "SELECT warning_id, signal_status, process_status, audit_status FROM ap_warning_signal "
        "WHERE warn_reason LIKE '%9.4%' LIMIT 1",
    )
    check("瑞华黄档信号存在", bool(rw_sig))
    if rw_sig:
        s = rw_sig[0]
        check("已走完闭环 → signal_status=已关闭", s["signal_status"] == "已关闭", f"(库值 {s['signal_status']})")
        check("解除标识 process_status=已解除", s["process_status"] == "已解除", f"(库值 {s['process_status']})")
        disp = _q(
            risk,
            "SELECT disposal_status, disposal_progress FROM ap_warning_disposal WHERE warning_id=?",
            (s["warning_id"],),
        )
        check("处置跟踪=已处置", bool(disp) and disp[0]["disposal_status"] == "已处置",
              f"(库值 {disp[0]['disposal_status'] if disp else None})")
        check("解除报告 progress 含「解除」", bool(disp) and "解除" in disp[0]["disposal_progress"])

    # ---- 5. 分布占比（§五）----
    print("\n[5] 分布占比（§五，全量实算）")
    n_sig = _q(risk, "SELECT COUNT(*) n FROM ap_warning_signal")[0]["n"]
    n_cust = _q(cust, "SELECT COUNT(*) n FROM ap_customer")[0]["n"]
    check("规模：预警信号 ~2 万", 19500 <= n_sig <= 20500, f"(实算 {n_sig})")
    check("规模：客户 ~5 万", 49000 <= n_cust <= 51000, f"(实算 {n_cust})")

    def _ratio(conn: sqlite3.Connection, table: str, col: str, val: str, total: int) -> float:
        return _q(conn, f"SELECT COUNT(*) n FROM {table} WHERE {col}=?", (val,))[0]["n"] / total

    check("预警级别 黄≈55%", abs(_ratio(risk, "ap_warning_signal", "warn_level", "黄", n_sig) - 0.55) <= 0.03,
          f"(实算 {pct(_ratio(risk, 'ap_warning_signal', 'warn_level', '黄', n_sig))})")
    check("预警级别 橙≈34%", abs(_ratio(risk, "ap_warning_signal", "warn_level", "橙", n_sig) - 0.34) <= 0.03,
          f"(实算 {pct(_ratio(risk, 'ap_warning_signal', 'warn_level', '橙', n_sig))})")
    check("预警级别 红≈11%", abs(_ratio(risk, "ap_warning_signal", "warn_level", "红", n_sig) - 0.11) <= 0.03,
          f"(实算 {pct(_ratio(risk, 'ap_warning_signal', 'warn_level', '红', n_sig))})")

    exp_evt = {"信用风险": 0.45, "市场风险": 0.20, "流动性风险": 0.15, "合规风险": 0.12, "操作风险": 0.08}
    for evt, w in exp_evt.items():
        check(f"事件类型 {evt}≈{int(w*100)}%", abs(_ratio(risk, "ap_warning_signal", "event_type", evt, n_sig) - w) <= 0.03,
              f"(实算 {pct(_ratio(risk, 'ap_warning_signal', 'event_type', evt, n_sig))})")

    exp_st = {"待确认": 0.30, "确认中": 0.20, "已确认": 0.20, "处置中": 0.15, "已关闭": 0.10, "已撤销": 0.03, "已排除": 0.02}
    for st, w in exp_st.items():
        check(f"生命周期 {st}≈{int(w*100)}%", abs(_ratio(risk, "ap_warning_signal", "signal_status", st, n_sig) - w) <= 0.03,
              f"(实算 {pct(_ratio(risk, 'ap_warning_signal', 'signal_status', st, n_sig))})")

    # ---- 6. 名称纯净化 + 理由模板对齐 ----
    print("\n[6] 名称纯净化与理由模板对齐")
    tail = _q(cust, "SELECT customer_name FROM ap_customer WHERE customer_name LIKE '%·%'")
    gtail = _q(cust, "SELECT group_customer_name FROM ap_group_customer WHERE group_customer_name LIKE '%·%'")
    check("客户名称无「·编号尾巴」", not tail and not gtail, f"(尾巴 {len(tail) + len(gtail)} 条)")
    # 理由对齐直接按 level2 ∈ 主题集（与生成器同源断言）
    l2_mismatch = 0
    for r in _q(risk, "SELECT event_type, signal_level2_topic FROM ap_warning_signal"):
        if r["signal_level2_topic"] not in LEVEL2_BY_L1[r["event_type"]]:
            l2_mismatch += 1
    check("理由/事件类型严格对齐（level2 同源）", l2_mismatch == 0, f"(错配 {l2_mismatch} 条)")

    _close(cust, risk, conc, base)
    print(f"\n===== 核对结果：通过 {PASS} 项 / 失败 {FAIL} 项 =====")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
