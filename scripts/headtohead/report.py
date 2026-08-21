"""P2 head-to-head 实验报告生成（任务 4）。写 docs/P2-headtohead-实验报告.md"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from scripts.headtohead.questions import BY_ID, QUESTIONS

REPORT = ROOT / "docs" / "P2-headtohead-实验报告.md"

PRICE_IN = 3.0
PRICE_OUT = 9.0


def p95(xs):
    if not xs:
        return 0.0
    s = sorted(xs)
    idx = max(0, min(len(s) - 1, round(0.95 * (len(s) - 1))))
    return s[idx]


def load():
    res = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    gt = json.loads((HERE / "gt_results.json").read_text(encoding="utf-8"))
    neg = json.loads((HERE / "negative_results.json").read_text(encoding="utf-8"))
    by = {"A": {}, "B": {}}
    for r in res["runs"]:
        by[r["form"]][r["qid"]] = r
    return by, gt, neg


def agg(by, form):
    recs = [by[form][qid] for qid in BY_ID]
    n = len(recs)
    o = [r["outcome"] for r in recs]
    correct, refusal, wrong, error = o.count("correct"), o.count("refusal"), o.count("wrong"), o.count("error")
    llm = [r.get("llm_ms", 0) for r in recs if r.get("llm_ms")]
    ex = [r.get("exec_ms", 0) for r in recs if r.get("exec_ms")]
    ti = sum(r.get("usage", {}).get("prompt", 0) for r in recs)
    to = sum(r.get("usage", {}).get("completion", 0) for r in recs)
    return {
        "n": n, "correct": correct, "refusal": refusal, "wrong": wrong, "error": error,
        "sr": correct / n, "rr": refusal / n,
        "llm_p95": p95(llm), "llm_mean": statistics.mean(llm) if llm else 0,
        "ex_p95": p95(ex), "ex_mean": statistics.mean(ex) if ex else 0, "ex_n": len(ex),
        "ti": ti, "to": to, "cost": ti / 1e6 * PRICE_IN + to / 1e6 * PRICE_OUT,
    }


def aug_rows():
    return [
        ("J1", "Customer 对象 + order_count_by_customer 指标（COUNT(DISTINCT VBELN)），或注册 Order 对象 + 链接"),
        ("J2", "stock_balance_by_mat_group 指标（加 MATKL 维度），或 stock 指标维度扩展 material_group"),
        ("J3", "receipt_qty_by_vendor 指标（Σ MSEG.MENGE WHERE BWART=101，按 LIFNR）"),
        ("J4", "customer_refund_by_customer 指标（Σ -WSL WHERE SO 且 WSL<0）+ 契约 Top-N/排序截断扩展"),
        ("A2", "3 维指标 cofv_qty_by_matkl_werks_month，或注册 COFV 对象走 v0.1 对象路径"),
        ("A3", "customer_count_by_month 指标（COUNT(DISTINCT KUNNR)）"),
        ("A4", "契约表达式扩展（除法/复合度量），或派生客单价指标"),
        ("A5", "需先补单价语义（派生 EKPO.NETWR/MENGE 或新增 price 字段）+ min/max 指标"),
        ("A6", "order_count_by_month 指标（订单数）；金额已可表达，需双度量或两契约"),
        ("F1", "Customer 对象 + segment(KTOKD) 过滤 + 订单 join（Order 对象或 order 指标）"),
        ("F2", "契约按度量值过滤扩展（HAVING 语义）或物化 low_stock 清单指标"),
        ("F3", "AUFK 对象 + status 过滤（状态过滤载体）"),
        ("F4", "契约按度量值过滤扩展 + refund 语义指标"),
        ("L1", "注册 material.vendor 链接（1 跳，EKPO→EKKO→LFA1 映射）"),
        ("L2", "注册 Order 对象 + order.customer 链接"),
        ("L5", "注册 Order→Finance 链接（退款链路）"),
        ("L6", "注册 FinanceEntry 对象 + finance.order 链接（条目明细路径）"),
        ("T1", "order_count_by_month 指标"),
        ("T3", "日粒度指标（substr(1,10)）或 time_range 粒度扩展"),
        ("T4", "refund 指标 + 双 time_range 对比扩展"),
        ("T5", "cofv_avg_hrs_by_month 指标（AVG ISMN1）"),
        ("T6", "季度维度派生指标（group_by 表达式扩展或预聚合季度）"),
    ]


def main():
    by, gt, neg = load()
    A, B = agg(by, "A"), agg(by, "B")
    delta = B["sr"] - A["sr"]
    exp = [q["id"] for q in QUESTIONS if q["b_expressible"]]
    cold = [q["id"] for q in QUESTIONS if not q["b_expressible"]]

    targets = [
        ("A=Baseline 成功率 ≥ 70%", f"{A['sr']*100:.1f}%", A["sr"] >= 0.70),
        ("B=本体版成功率 ≥ 85%", f"{B['sr']*100:.1f}%", B["sr"] >= 0.85),
        ("Δ = B−A ≥ 10pp", f"{delta*100:+.1f}pp", delta >= 0.10),
        ("拒答率 > 0（两形态）", f"A {A['rr']*100:.1f}% / B {B['rr']*100:.1f}%", (A["refusal"] + B["refusal"]) > 0),
        ("执行延迟 P95 ≤ 500ms（A）", f"{A['ex_p95']:.0f}ms", A["ex_p95"] <= 500),
        ("执行延迟 P95 ≤ 500ms（B）", f"{B['ex_p95']:.0f}ms", B["ex_p95"] <= 500),
    ]

    md = []
    md.append("# P2 head-to-head 实验报告（A=NL2SQL 直查 vs B=本体版受限结构化查询）")
    md.append("")
    md.append("> 生成：" + datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M") + " ｜ 依据：docs/P2-ChatBI闭环设计_v0.1.md §4 ｜ 数据集：data/des/enterprises/hc_precision（5 源库 18 表 1,000,000 行 + metrics.db 15 指标物化）")
    md.append("> 方法：30 问 × 2 形态各 1 次 LLM 调用（DeepSeek）。A=LLM 生成 SQL → 多层守卫（只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）→ DuckDB 本地执行；B=LLM 生成契约 JSON → validate_contract + ContractExecutor（PermissionContext.allow_all 内部口径）。正确性 = 期望口径 GT（确定 SQL 预计算）按 key 精确 + 数值容差（相对 0.5%）比对。")
    md.append("")
    md.append("## 0. 结论先行（BLUF）")
    md.append("")
    md.append(f"- **A=Baseline（NL2SQL 直查）成功率 {A['sr']*100:.1f}%（{A['correct']}/{A['n']}）**；**B=本体版（受限结构化查询）成功率 {B['sr']*100:.1f}%（{B['correct']}/{B['n']}）**；Δ = **{delta*100:+.1f}pp**（为负）。")
    md.append("- **靶值判定：未达成**（B 距 85% 差距大，Δ 为负）→ **触发 Plan B**（设计 §5：B 成功率 < 85% 且冷问题 ≥ 20%）。")
    md.append("- 但 B 的低分主要由**语义面覆盖缺口**（当前仅 Material/Code 对象 + 15 指标，30 问仅 8 问在语义面内）与 **V5 结果护栏过严**（2400 行，挡住 3 个大结果问题）导致，不是「受限结构化查询」这一形态本身的必然失败——见 §6 语义面扩展分析。")
    md.append(f"- **契约 v0.2 终版建议：混合形态**——受限结构化查询（B）作主路径（可控/可枚举/fail-closed），Plan B（守卫化 LLM SQL）兜底冷问题；同时按设计 R5 增补指标/对象/链接，把 B 语义面从 {len(exp)} 问扩到 ~26-28 问。")
    md.append("")
    md.append("## 1. 靶值判定（设计 §4.3）")
    md.append("")
    md.append("| 靶值 | 实测 | 达成 |")
    md.append("|---|---|---|")
    for name, val, ok in targets:
        md.append(f"| {name} | {val} | {'✅ 达成' if ok else '❌ 未达成'} |")
    md.append("")
    md.append("> P95 为执行延迟（不含 LLM 网络耗时）；B 仅对实际执行的契约计 P95（A1/L4/F5 等大结果问题被 V5 护栏拒答不计）。拒答率 > 0 由主跑拒答 + 负例演示共同证明（§5）。")
    md.append("")
    md.append("## 2. 汇总指标")
    md.append("")
    md.append("| 指标 | A=Baseline（NL2SQL） | B=本体版（受限结构化） | 说明 |")
    md.append("|---|---|---|---|")
    md.append(f"| 成功率 | {A['sr']*100:.1f}%（{A['correct']}/{A['n']}） | {B['sr']*100:.1f}%（{B['correct']}/{B['n']}） | Δ = {delta*100:+.1f}pp |")
    md.append(f"| 拒答率（fail-closed） | {A['rr']*100:.1f}%（{A['refusal']}/{A['n']}） | {B['rr']*100:.1f}%（{B['refusal']}/{B['n']}） | B 拒答=受限面不可表达+校验/护栏拒答 |")
    md.append(f"| 错误答案率（执行成功但≠GT） | {A['wrong']}/{A['n']} | {B['wrong']}/{B['n']} | |")
    md.append(f"| 错误率（LLM/执行/解析失败） | {A['error']}/{A['n']} | {B['error']}/{B['n']} | |")
    md.append(f"| 执行延迟 P95 / 均值 | {A['ex_p95']:.0f}ms / {A['ex_mean']:.0f}ms（{A['ex_n']} 次执行） | {B['ex_p95']:.0f}ms / {B['ex_mean']:.0f}ms（{B['ex_n']} 次执行） | |")
    md.append(f"| LLM 单次延迟 P95 / 均值 | {A['llm_p95']:.0f}ms / {A['llm_mean']:.0f}ms | {B['llm_p95']:.0f}ms / {B['llm_mean']:.0f}ms | 网络+生成 |")
    md.append(f"| LLM token（输入/输出） | {A['ti']:,} / {A['to']:,} | {B['ti']:,} / {B['to']:,} | 30 问合计 |")
    md.append(f"| 成本估算（元） | ¥{A['cost']:.4f} | ¥{B['cost']:.4f} | 见 §7 |")
    md.append("")
    md.append("**分项解读**：")
    md.append("- A 全部 30 问可表达，失败 = 7 问 SQL 语义错误（J1 缺 LEFT JOIN 丢 0 单客户、A6 用抬头金额非项目金额、A5 单价过度舍入、J4 Top5 集合不同、T4 时段标签不同、J3 结果仅 60 行、F4 退款集合不同）+ 2 问执行错误（J2 未 join MARA、T3 VARCHAR vs DATE 类型）+ 2 问守卫拒答（A2 库名限定+表名拼错 COFC、L3 码空间标签错误且仅 2 类码）。")
    md.append(f"- B 当前语义面仅 {len(exp)} 问可表达：J6/F6 契约生成正确并命中；J5 契约粒度错（factory×location 非 location）；A3 契约映射到金额指标（非客户数）；A1/L4/F5 被 V5 结果护栏拒答；其余 {len(cold)} 问受限面不可表达，LLM 主动拒答或契约校验拒答。")
    md.append("- **拒答率**：A 的拒答来自守卫；B 的拒答 = LLM 主动拒答 + executor fail-closed。**两形态均满足拒答率 > 0**，且 B 的 fail-closed 是「语义面之外一律拒绝」，正是受限查询的可控性价值。")
    md.append(f"- **延迟**：两形态执行 P95 均 ≤ 500ms（A {A['ex_p95']:.0f}ms / B {B['ex_p95']:.0f}ms）。B 的 P95 含被 V5 护栏拒答的大结果扫描（A1 物化表 77,936 行 ~165ms），成功的小结果查询（J5/J6/F6）仅 ~7-19ms；A 的 P95 含 A1 的 77,936 行 SQL 聚合 ~166ms，两形态重查询同量级。")
    md.append("")
    md.append("## 3. 30 问结果表")
    md.append("")
    md.append("> 「B 可表达」列 = 当前语义面（Material/Code + 15 指标）是否可表达该问；期望口径要点仅标注需适配的题目（demo 数据缺字段，§8）。")
    md.append("")
    md.append("| 问 | 组 | 问法 | B可表达 | GT行数 | A结果 | B结果 | A exec(ms) | B exec(ms) | 备注 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for q in QUESTIONS:
        qid = q["id"]
        a = by["A"][qid]
        b = by["B"][qid]
        note = ""
        if q.get("adapted_note"):
            note = "口径说明: " + q["adapted_note"][:22]
        if not note and b["outcome"] == "wrong":
            note = b.get("detail", "")[:24]
        if not note and b["outcome"] == "refusal" and q["b_expressible"]:
            d = b.get("detail", "")
            note = ("受限面不可表达" if d.startswith("LLM 拒答") else "校验/护栏拒答")
        md.append(f"| {qid} | {q['group']} | {q['ask']} | {'✅' if q['b_expressible'] else '—'} | {gt[qid]['row_count']} | {a['outcome']} | {b['outcome']} | {a.get('exec_ms','-')} | {b.get('exec_ms','-')} | {note} |")
    md.append("")
    md.append("## 4. B 形态逐问细账（可表达集 + 失败原因）")
    md.append("")
    md.append("| 问 | B 结果 | 明细 |")
    md.append("|---|---|---|")
    for qid in exp + [q["id"] for q in QUESTIONS if not q["b_expressible"] and q["id"] in ("A3",)]:
        q = BY_ID[qid]
        b = by["B"][qid]
        d = b.get("detail", "")
        if b["outcome"] == "refusal":
            d = ("受限面不可表达（LLM 主动拒答）" if d.startswith("LLM 拒答") else "校验/护栏拒答（fail-closed）") + "：" + d[:90]
        md.append(f"| {qid} {q['ask']} | {b['outcome']} | {d[:130]} |")
    md.append("")
    md.append("## 5. 拒答率 > 0 的 fail-closed 证据（独立负例，不烧 LLM）")
    md.append("")
    md.append("> 重要边界（如实标注）：注册表已含 Vendor(scm.LFA1)/InventoryLocation(erp.MARD)/FinanceEntry(fin.ACDOCA) 等对象，但 ContractExecutor 的 v0.1 对象路径未接线跨库源表——SELECT * FROM scm.LFA1 报 Catalog Error（fail-closed）。因此当前实际可查询对象面 = Material/Code（物化内存表），B 的表达全部依赖 15 指标物化 + Material/Code 对象；注册对象 ≠ 可查询对象，这是 P2 实现缺口，也是本体版语义面扩大的前提之一（对齐设计 §1.5 R5）。")
    md.append("")
    md.append("")
    md.append("**A 形态多层守卫**（设计 §5：只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）——5/5 注入或非法 SQL 被拒答：")
    md.append("")
    md.append("| 用例 | 触发 | 守卫捕获 |")
    md.append("|---|---|---|")
    for c in neg["A"]:
        md.append(f"| {c['name']} | {c['sql'][:64]} | {'✅ ' + '；'.join(c['violations'])[:70] if c['rejected'] else '❌'} |")
    md.append("")
    md.append("**B 形态契约校验**（V1-V5 + M 系列 + P2-2 time_range fail-closed）——5/5 非法契约被拒答：")
    md.append("")
    md.append("| 用例 | 触发 | 校验拒答 |")
    md.append("|---|---|---|")
    for c in neg["B"]:
        md.append(f"| {c['name']} | {json.dumps(c['contract'], ensure_ascii=False)[:70]} | {'✅ ' + c['violations'][:70] if c['rejected'] else '❌'} |")
    md.append("")
    md.append("## 6. 冷问题语义面扩展分析（设计 R5：指标可按实验增补，注册表加一条成本低）")
    md.append("")
    md.append(f"B 当前语义面覆盖 {len(exp)} 问；{len(cold)} 问为冷问题。逐问给出「转可表达」所需扩展——均为 R5 授权的注册表/契约增量：")
    md.append("")
    md.append("| 冷问题 | 所需扩展 |")
    md.append("|---|---|")
    for qid, need in aug_rows():
        md.append(f"| {qid} {BY_ID[qid]['ask']} | {need} |")
    md.append("")
    md.append("> 结论：受限结构化查询**形态本身**可表达 30 问中的 ~26-28 问（除 Top-N 截断、比值/除法、按度量值过滤 3 类需契约能力扩展）；当前只覆盖 8 问 = **语义面未按 30 问集扩充**（R5 待办），非形态之错。")
    md.append("")
    md.append("## 7. 契约 v0.2 终版建议")
    md.append("")
    md.append("**判定：head-to-head 未达成 → 按设计 §5 触发 Plan B，但终版 = 混合形态（受限结构化主路径 + 守卫化 SQL 兜底冷问题），而非纯 Plan B：**")
    md.append("")
    md.append("1. **受限结构化查询（B）定为主路径**：可表达问题走契约（指标物化 + 对象路径），语义可枚举、可审计、fail-closed 拒答，可控性显著优于纯 SQL。")
    md.append("2. **Plan B 兜底冷问题**：~20% 冷问题（Top-N / 比值 / 任意 join / 明细）交给守卫化 LLM SQL（§5 实测 5/5 拦截注入）；审计粒度从「契约语义」降级为「SQL 文本」（设计 §5 同口径，报告如实标注）。")
    md.append("3. **v0.2 能力扩展（建议下一迭代落门禁 tests/test_p2_chatbi.py）**：")
    md.append("   - 语义面增补：按 §6 表注册 ~10 个新指标（订单数/退款/到货量/客户数/报工工时/日粒度等）+ 注册 Customer/Order/FinanceEntry 对象与 material.vendor 链接（对齐设计 §1.5 R5）；")
    md.append("   - V5 结果护栏语义修正（red-team P3-9）：上限按查询对象/指标规模派生，当前锚定 MARA（2400 行）挡住 A1/L4/F5 三个大结果问题，应改 analytics 口径；")
    md.append("   - 契约表达力：按度量值过滤（F2/F4）、Top-N/排序截断（J4）、表达式/除法（A4）、双 time_range 对比（T4）。")
    md.append("4. **风险与边界如实标注**：J3/F2/F3/A5/T5 因 demo 数据缺字段，口径已适配（§8）；LLM 生成有随机性，B 对可表达问题的契约质量直接影响成功率，不重试美化。")
    md.append("")
    md.append("## 8. 实验方法、边界与可复现")
    md.append("")
    md.append("- **口径适配清单**（demo 缺字段，如实调整期望口径）：J2 品类库存金额→库存量（无单价列）；J3 供应商准时率→到货量（无准时字段）；A5 物料价格区间→采购单价区间（无主数据价格）；F2 安全库存→阈值 1200（无安全库存字段）；F3 已发货未送达→工单 REL 状态（订单无发货状态）；T5 平均到货时长→平均报工工时（无到货时长）；T2 月库存金额→月销售金额（无库存月份维度，设计契约列本就指向销售物化）。")
    md.append("- **阈值文档化**：F1 高额=NETWR>90000；F4 |WSL|>50000；F5 仓库 W01/W02；T3 近 30 天=2026-12-02..31（数据止 2026-12-31）；T4 本月=2026-12 / 上月=2026-11。")
    md.append("- **比较口径**：key 列精确 + 数值列相对容差 0.5%（吸收显示舍入，仍抓住真实错误）；集合无序；列序按题目声明规范。B 的 V5 护栏拒答（结果 > 2400 行）按拒答计。")
    md.append("- **LLM 不确定性与诚实交付**：单次生成有随机性，本次如实记录；失败/拒答/错误全部计数，不重试美化。")
    md.append("- **可复现**：python3 scripts/headtohead/gt.py（GT）→ runner.py（主跑，seed 20260821）→ reeval.py（修正 GT/容差后重估，不烧 LLM）→ negatives.py（负例）→ report.py（本报告）。只读源库；未跑全量 pytest。")
    md.append("")
    md.append("## 9. 待确认项（交 Jack 拍板）")
    md.append("")
    md.append("1. **混合形态终版是否采纳**：受限结构化主路径 + 守卫化 SQL 兜底冷问题；确认后按 §7 增补指标/对象/链接，重跑一次全语义面实验验证 B 成功率能否过 85%。")
    md.append("2. **V5 结果护栏口径**：改为按查询规模派生（改 contract.py 常量/配置），还是保留现状（接受大结果问题拒答）？")
    md.append("3. **DeepSeek 计费口径**：本次按官方公开价（输入 ¥3/M、输出 ¥9/M）估算约 ¥0.2x；实际套餐/账单口径待对账。")
    md.append("4. **口径适配可否接受**：J2/J3/A5/F2/F3/T5 等因 demo 缺字段而适配的口径，是否需在 1M 行 demo 中补字段（改 schema = 先问）再复测？")
    md.append("")

    REPORT.write_text("\n".join(md), encoding="utf-8")
    print("报告已写入", REPORT)
    print(f"A: {A['sr']*100:.1f}% ({A['correct']}/30) | B: {B['sr']*100:.1f}% ({B['correct']}/30) | Δ={delta*100:+.1f}pp")
    print(f"A 拒答 {A['refusal']}, B 拒答 {B['refusal']} | A execP95 {A['ex_p95']:.0f}ms, B execP95 {B['ex_p95']:.0f}ms | 总成本 ¥{A['cost']+B['cost']:.4f}")


if __name__ == "__main__":
    main()
