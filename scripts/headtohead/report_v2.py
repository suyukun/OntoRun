"""P2 head-to-head 实验报告 v2 生成（语义面增补后重跑）。
写 docs/P2-headtohead-实验报告v2.md —— 与 v1（首轮，docs/P2-headtohead-实验报告.md）对比。
"""
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

REPORT = ROOT / "docs" / "P2-headtohead-实验报告v2.md"

PRICE_IN = 3.0
PRICE_OUT = 9.0

# 语义面口径发散（v2 §6 专项）：即使参考契约正确执行也必 wrong 的 3 问 + 原因
DIVERGENT = {
    "J1": "零单客户缺口：order_count_by_customer 只含下过单的 9,823 客户，GT 为 LEFT JOIN 含 0 单客户的 10,000 行（指标无 LEFT JOIN 语义）",
    "A2": "join 路径分歧：cofv_qty_by_matkl_werks_month 以 COFV.MATNR→MARA 取物料组，GT 以 AUFK.MATNR→MARA；demo 数据 COFV.MATNR 与 AUFK.MATNR 几乎全不同（179,976/180,000 行），数值大幅偏差",
    "T4": "呈现标签差异：refund_amount_by_month 返回月份标签（2026-11/2026-12），GT 为 cur/prev 标签；数值一致仅标签不同（key 精确比较失败）",
}

# 问法歧义（GT 全量排行 vs B Top-N 截断），非形式/语义面之错
AMBIGUOUS = {
    "J3": "「到货准时率最高」口径歧义：GT 返回全部 4,962 供应商按量降序，LLM 将「最高」解读为 Top-N（topN=10）→ 行数不一致",
}


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


def main():
    by, gt, neg = load()
    A, B = agg(by, "A"), agg(by, "B")
    delta = B["sr"] - A["sr"]
    exp = [q["id"] for q in QUESTIONS if q["b_expressible"]]
    cold = [q["id"] for q in QUESTIONS if not q["b_expressible"]]
    # 本轮 B 的拒答中「语义面不可表达」= cold 拒答 + 可表达但 LLM 拒答 分开计
    b_refused = [qid for qid in BY_ID if by["B"][qid]["outcome"] == "refusal"]
    b_wrong = [qid for qid in BY_ID if by["B"][qid]["outcome"] == "wrong"]
    b_correct = [qid for qid in BY_ID if by["B"][qid]["outcome"] == "correct"]
    b_correct_set = set(b_correct)
    exp_set_sr = len([q for q in exp if q in b_correct_set]) / len(exp) if exp else 0.0  # 可表达集内成功率
    newly_expressible = [q for q in exp if q not in {"J5", "J6", "A1", "F5", "F6", "L3", "L4", "T2"}]

    targets = [
        ("A=Baseline 成功率 ≥ 70%", f"{A['sr']*100:.1f}%", A["sr"] >= 0.70),
        ("B=本体版成功率 ≥ 85%", f"{B['sr']*100:.1f}%", B["sr"] >= 0.85),
        ("Δ = B−A ≥ 10pp", f"{delta*100:+.1f}pp", delta >= 0.10),
        ("拒答率 > 0（两形态）", f"A {A['rr']*100:.1f}% / B {B['rr']*100:.1f}%", (A["refusal"] + B["refusal"]) > 0),
        ("执行延迟 P95 ≤ 500ms（A）", f"{A['ex_p95']:.0f}ms", A["ex_p95"] <= 500),
        ("执行延迟 P95 ≤ 500ms（B）", f"{B['ex_p95']:.0f}ms", B["ex_p95"] <= 500),
    ]
    # 天花板测算：语义面可表达 20 问，其中 3 问口径发散必 wrong（J1/A2/T4）→ 完美契约上限
    ceiling = len(exp) - len(DIVERGENT)

    md = []
    md.append("# P2 head-to-head 实验报告 v2（语义面增补后重跑：26 指标 + 对象接线 + topN + 度量过滤）")
    md.append("")
    md.append("> 生成：" + datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M") + " ｜ 依据：docs/P2-ChatBI闭环设计_v0.1.md §4 ｜ 数据集：data/des/enterprises/hc_precision（5 源库 18 表 1,000,000 行 + metrics.db 26 指标物化）")
    md.append("> 方法：30 问 × 2 形态各 1 次 LLM 调用（DeepSeek deepseek-chat，seed 20260822）。A=LLM 生成 SQL → 多层守卫 → DuckDB 本地执行；B=LLM 生成契约 JSON → validate_contract + ContractExecutor（PermissionContext.allow_all 内部口径）。正确性 = 期望口径 GT（确定 SQL 预计算）按 key 精确 + 数值容差（相对 0.5%）比对。本轮 B 提示词同步语义面：26 指标目录（含定义）、对象接线（Material/Code/Customer/Vendor/InventoryLocation/FinanceEntry）、topN、度量过滤、time_range、口径说明。")
    md.append("")
    md.append("## 0. 结论先行（BLUF）")
    md.append("")
    md.append(f"- **A=Baseline（NL2SQL 直查）成功率 {A['sr']*100:.1f}%（{A['correct']}/{A['n']}）**；**B=本体版（受限结构化查询）成功率 {B['sr']*100:.1f}%（{B['correct']}/{B['n']}）**；Δ = **{delta*100:+.1f}pp**。")
    md.append(f"- **靶值判定：B≥85% 未达成**。B 成功率 {B['sr']*100:.1f}% 距 85% 仍有差距；且当前语义面存在**结构性天花板**——30 问中 10 问冷问题不可表达 + 3 问可表达但口径发散（J1 零单客户 / A2 join 路径 / T4 标签），**即使契约生成完美，B 上限也只有 {ceiling}/30 = {ceiling/30*100:.1f}%**，85% 靶值在现有 30 问集上不可达（需先扩展语义面 + 修口径，见 §6/§7）。")
    md.append(f"- 但 v1 主要归因已修复并验证：**语义面覆盖从 8 问扩到 {len(exp)} 问**（v1 22 问拒答中本轮新可表达 {len(newly_expressible)} 问）；**V5 护栏按规模派生后 A1/L4/F5 三个大结果问题不再误拒**；topN（J4）、度量过滤（F4）、time_range（T3）、对象接线（L6）均落地且命中。B 拒答率从 v1 86.7% 降至本轮 {B['rr']*100:.1f}%。")
    md.append(f"- B 剩余拒答 {len(b_refused)} 问主要为 {len(cold)} 问冷问题（受限面不可表达）+ 少量 LLM 主动拒答/契约校验拒答；B 错答 {len(b_wrong)} 问含 3 问口径发散 + 其余为 LLM 契约质量问题（如实记录，不重试美化）。")
    md.append("")
    md.append("## 1. 靶值判定（设计 §4.3）")
    md.append("")
    md.append("| 靶值 | 实测 | 达成 |")
    md.append("|---|---|---|")
    for name, val, ok in targets:
        md.append(f"| {name} | {val} | {'✅ 达成' if ok else '❌ 未达成'} |")
    md.append("")
    md.append("> 执行延迟 P95 不含 LLM 网络耗时；B 仅对实际执行的契约计 P95。拒答率 > 0 由主跑拒答 + 负例演示共同证明（§5）。")
    md.append("")
    md.append("## 2. 汇总指标（vs v1 对比）")
    md.append("")
    md.append("| 指标 | A=Baseline | B=本体版 | v1 B（参考） | 说明 |")
    md.append("|---|---|---|---|---|")
    md.append(f"| 成功率 | {A['sr']*100:.1f}%（{A['correct']}/{A['n']}） | {B['sr']*100:.1f}%（{B['correct']}/{B['n']}） | 6.7%（2/30） | Δ = {delta*100:+.1f}pp |")
    md.append(f"| 拒答率（fail-closed） | {A['rr']*100:.1f}%（{A['refusal']}/{A['n']}） | {B['rr']*100:.1f}%（{B['refusal']}/{B['n']}） | 86.7%（26/30） | B 拒答=受限面不可表达+校验/护栏拒答 |")
    md.append(f"| 错误答案率（执行成功但≠GT） | {A['wrong']}/{A['n']} | {B['wrong']}/{B['n']} | 2/30 | |")
    md.append(f"| 错误率（LLM/执行/解析失败） | {A['error']}/{A['n']} | {B['error']}/{B['n']} | 0/30 | |")
    md.append(f"| 执行延迟 P95 / 均值 | {A['ex_p95']:.0f}ms / {A['ex_mean']:.0f}ms（{A['ex_n']} 次） | {B['ex_p95']:.0f}ms / {B['ex_mean']:.0f}ms（{B['ex_n']} 次） | 165ms / 28ms | |")
    md.append(f"| LLM 单次延迟 P95 / 均值 | {A['llm_p95']:.0f}ms / {A['llm_mean']:.0f}ms | {B['llm_p95']:.0f}ms / {B['llm_mean']:.0f}ms | 1739ms / 1206ms | 网络+生成 |")
    md.append(f"| LLM token（输入/输出） | {A['ti']:,} / {A['to']:,} | {B['ti']:,} / {B['to']:,} | 31,063 / 2,272 | 30 问合计 |")
    md.append(f"| 成本估算（元） | ¥{A['cost']:.4f} | ¥{B['cost']:.4f} | ¥0.1136 | 见 §8 |")
    md.append("")
    md.append("**分项解读**：")
    md.append(f"- B 语义面从 v1 的 8 问扩到 {len(exp)} 问（+12），本轮 B 正确 {len(b_correct)} 问 / 错答 {len(b_wrong)} 问 / 拒答 {len(b_refused)} 问。v1 拒答的 22 问中，本轮新可表达 12 问（{('、'.join(newly_expressible))}），其中命中正确 {len([q for q in newly_expressible if q in b_correct_set])} 问（{('、'.join(q for q in newly_expressible if q in b_correct_set))}）。")
    md.append(f"- B 错答 {len(b_wrong)} 问构成：3 问语义面口径发散（J1/A2/T4，见 §6.2）+ 其余为 LLM 契约生成质量问题（如 {('、'.join(q for q in b_wrong if q not in DIVERGENT)[:60]) if any(q for q in b_wrong if q not in DIVERGENT) else '无'}）。")
    md.append(f"- B 拒答 {len(b_refused)} 问构成：{len(cold)} 问冷问题受限面不可表达 + 其余为 LLM 主动拒答或契约校验 fail-closed（拒答本身 = 受限面可控性价值，不视为错误）。")
    md.append(f"- 延迟：两形态执行 P95 均 ≤ 500ms（A {A['ex_p95']:.0f}ms / B {B['ex_p95']:.0f}ms）。B 的 P95 含大结果物化查询（A1 77,936 / L4 24,000 / F5 16,000 / L6 16,400 行），小查询（J6/F6 等）毫秒级。")
    md.append("")
    md.append("## 3. 30 问结果表")
    md.append("")
    md.append("> 「B可表达」= 本轮语义面（26 指标 + 5 对象 + topN/度量过滤/time_range）是否可表达；GT 行数来自预计算 GT；备注列标注口径说明/失败原因。")
    md.append("")
    md.append("| 问 | 组 | 问法 | B可表达 | GT行数 | A结果 | B结果 | A exec(ms) | B exec(ms) | 备注 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for q in QUESTIONS:
        qid = q["id"]
        a = by["A"][qid]
        b = by["B"][qid]
        note = ""
        if b["outcome"] == "wrong" and qid in DIVERGENT:
            note = "口径发散"
        elif b["outcome"] == "wrong":
            note = b.get("detail", "")[:22]
        elif q.get("adapted_note"):
            note = "口径说明: " + q["adapted_note"][:20]
        elif b["outcome"] == "refusal" and q["b_expressible"]:
            d = b.get("detail", "")
            note = ("LLM 拒答" if d.startswith("LLM 拒答") else "校验/护栏拒答")
        elif not q["b_expressible"]:
            note = "受限面不可表达"
        md.append(f"| {qid} | {q['group']} | {q['ask']} | {'✅' if q['b_expressible'] else '—'} | {gt[qid]['row_count']} | {a['outcome']} | {b['outcome']} | {a.get('exec_ms','-')} | {b.get('exec_ms','-')} | {note} |")
    md.append("")
    md.append("## 4. B 形态逐问细账（可表达集 + 失败/拒答原因）")
    md.append("")
    md.append("| 问 | B 结果 | 明细 |")
    md.append("|---|---|---|")
    for qid in exp + [q["id"] for q in QUESTIONS if not q["b_expressible"] and q["id"] in ("A6", "F2")]:
        q = BY_ID[qid]
        b = by["B"][qid]
        d = b.get("detail", "")
        if b["outcome"] == "refusal":
            d = ("受限面不可表达（LLM 主动拒答）" if d.startswith("LLM 拒答") else "校验/护栏拒答（fail-closed）") + "：" + d[:80]
        elif qid in DIVERGENT:
            d = "语义面口径发散：" + DIVERGENT[qid][:90] + (" | 实际：" + d[:40] if d else "")
        md.append(f"| {qid} {q['ask']} | {b['outcome']} | {d[:130]} |")
    md.append("")
    md.append("## 5. 拒答率 > 0 的 fail-closed 证据（独立负例，不烧 LLM）")
    md.append("")
    md.append("**A 形态多层守卫**（只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）：")
    md.append("")
    md.append("| 用例 | 触发 | 守卫捕获 |")
    md.append("|---|---|---|")
    for c in neg["A"]:
        md.append(f"| {c['name']} | {c['sql'][:64]} | {'✅ ' + '；'.join(c['violations'])[:70] if c['rejected'] else '❌'} |")
    md.append("")
    md.append("**B 形态契约校验**（V1-V5 + M 系列 + P2-2 time_range fail-closed）：")
    md.append("")
    md.append("| 用例 | 触发 | 校验拒答 |")
    md.append("|---|---|---|")
    for c in neg["B"]:
        md.append(f"| {c['name']} | {json.dumps(c['contract'], ensure_ascii=False)[:70]} | {'✅ ' + c['violations'][:70] if c['rejected'] else '❌'} |")
    md.append("")
    md.append("> 本轮对象接线已修复 v1 的「注册对象≠可查询对象」缺口：Vendor/InventoryLocation/FinanceEntry 的 v0.1 对象路径可查（物化表 vendor/inventory_location/finance_entry）。")
    md.append("")
    md.append("## 6. 剩余缺口分析（B 为何仍未过 85%）")
    md.append("")
    md.append("### 6.1 结构性天花板：30 问集的语义面上限")
    md.append("")
    md.append(f"- **10 问冷问题（受限面不可表达）**：{('、'.join(cold))}。逐问所需扩展：")
    md.append("| 冷问题 | 所需扩展 |")
    md.append("|---|---|")
    md.append("| A4 整体客单价 | 契约表达式/除法扩展（Σ金额 / COUNT DISTINCT 客户），或派生客单价指标 |")
    md.append("| A5 物料价格区间 | 补单价语义（EKPO.NETWR/MENGE 派生 price）+ min/max 指标 |")
    md.append("| A6 各月订单量与金额 | 双度量契约（单 metric 契约只能一个度量）或 order+sales 复合指标 |")
    md.append("| F1 corporate 高额订单 | Customer.segment(KTOKD) 过滤 + Order 对象/链接（订单 join） |")
    md.append("| F2 低库存清单 | 分组后度量过滤（HAVING 语义）；当前度量过滤仅物化粒度行级 WHERE |")
    md.append("| F3 已发货未送达 | AUFK 对象 + status 过滤（状态过滤载体） |")
    md.append("| L1 某物料供应商 | material.vendor 链接（1 跳，EKPO→EKKO→LFA1 映射） |")
    md.append("| L2 订单对应客户及金额 | Order 对象 + order.customer 链接 |")
    md.append("| L5 订单→退款链路 | 需 订单号+客户+退款 三联指标（refund+customer+vbeln 合一）或 Order→Finance 链接 |")
    md.append("| T6 季度汇总 | 季度派生维度指标（group_by 表达式扩展或预聚合季度） |")
    md.append("")
    md.append("- **3 问可表达但口径发散（参考契约执行也必 wrong）**：J1 零单客户缺口 / A2 join 路径发散 / T4 标签呈现差异（详见 §4 与 §6.2）。")
    md.append(f"- **结论：B 完美契约上限 = {ceiling}/30 = {ceiling/30*100:.1f}%**，低于 85% 靶值（25.5/30）。要在 30 问集达成 85%，需把上述 10 问冷问题转可表达（≥8 问）+ 修 3 问口径发散 + 保持 B 契约生成质量。")
    md.append(f"- **可表达集内成功率**（仅计 {len(exp)} 问可表达集）：本轮 {exp_set_sr*100:.1f}%（{len([q for q in exp if q in b_correct_set])}/{len(exp)}）；剩余失败 = 4 问 LLM 契约质量问题（J5/F5/T1/T2）+ 2 问冗余 group_by 拒答（A3/T5）+ 3 问口径发散/缺口（J1/A2/T4）+ 1 问口径歧义（J3），见 §4/§6.3。")
    md.append("")
    md.append("### 6.2 语义面口径发散专项（新发现，v1 未暴露）")
    md.append("")
    md.append("| 问 | 发散点 | 影响 |")
    md.append("|---|---|---|")
    md.append("| J1 每客户下单数 | 指标 order_count_by_customer 只含 ≥1 单的 9,823 客户，无 LEFT JOIN（0 单客户）语义 | B 少 177 行 → 行数不一致必 wrong |")
    md.append("| A2 品类×工厂×月 | cofv_qty_by_matkl_werks_month 以 COFV.MATNR 取物料组，GT 以 AUFK.MATNR；demo 两列几乎全不同 | 数值偏差 ~14% 必 wrong（指标口径需拍板） |")
    md.append("| T4 本月vs上月退款 | refund_amount_by_month 返回月份标签，GT 为 cur/prev 标签；数值一致 | key 精确比较失败；标签归一化后可判对 |")
    md.append("| J3 供应商到货准时率 | 「最高」口径歧义：GT 全量 4,962 供应商按量降序，LLM 读成 Top-N（topN=10） | 行数不一致必 wrong；两形态同受此歧义影响（A 本轮也 wrong） |")
    md.append("")
    md.append("### 6.3 B 契约生成质量（LLM 随机性如实记录）")
    md.append("")
    md.append("B 在可表达 20 问上，正确/错答/拒答分布见 §2；单次生成有随机性（seed 20260822），不重试美化。契约质量受提示词语义面完整度影响，本轮已含指标定义/对象/示例契约，仍存在 LLM 选错指标粒度或 group_by 越界等偶发（见 §4 明细）。")
    md.append("")
    md.append("## 7. 结论与建议")
    md.append("")
    md.append("1. **混合形态终版方向不变，但 85% 靶值需重新对齐**：B 语义面从 8→20 问、V5 误拒修复、topN/度量过滤/对象接线均落地验证，受限结构化查询（B）作主路径的能力成立；但当前 30 问集上 B 有 ~10 问冷问题 + 3 问口径发散，**85% 成功率的靶值在现有语义面下不可达**——建议按 §6.1 扩展（8 问）并修 §6.2 口径（3 问）后重跑，或将靶值对齐「可表达问题集内成功率」。")
    md.append("2. **口径发散需 Jack 拍板**：A2 cofv 指标 join 路径（COFV.MATNR vs AUFK.MATNR）、T4 标签口径（月份 vs cur/prev）、J1 零单客户（指标补 LEFT JOIN 语义或调整 GT 口径）。")
    md.append("3. **V5 护栏已按规模派生**（red-team P3-9 落地）：A1/L4/F5 大结果问题从 v1 误拒改为放行，不再掩盖语义面表达力。")
    md.append("4. **拒答即可控性**：B 的 fail-closed 拒答（冷问题/非法契约）是受限查询的核心价值，本轮负例 5/5 拦截保持。")
    md.append("")
    md.append("## 8. 方法、边界与可复现")
    md.append("")
    md.append("- **口径适配清单**（与 v1 相同，demo 缺字段如实调整）：J2 品类库存金额→库存量；J3 供应商准时率→到货量；A5 物料价格区间→采购单价区间；F2 安全库存→阈值 1200；F3 已发货未送达→工单 REL 状态；T5 平均到货时长→平均报工工时；T2 月库存金额→月销售金额（设计契约列本就指向销售物化）。")
    md.append("- **阈值文档化**：F1 高额=NETWR>90000；F4 |WSL|>50000；F5 仓库 W01/W02；T3 近 30 天=2026-12-02..31；T4 本月=2026-12 / 上月=2026-11。")
    md.append("- **比较口径**：key 列精确 + 数值列相对容差 0.5%；集合无序；列序按题目声明。B 的 fail-closed（校验/护栏）按拒答计，LLM 主动拒答按拒答计。")
    md.append("- **成本估算**：DeepSeek 官方公开价 输入 ¥3/M、输出 ¥9/M；本轮 B 提示词含 26 指标目录更长，token/成本较 v1 略增，合计仍个位数元。")
    md.append("- **LLM 不确定性与诚实交付**：单次生成有随机性（seed 20260822），失败/拒答/错误全部计数，不重试美化；对比 v1（seed 20260821）如实标注。")
    md.append("- **可复现**：gt.py（GT）→ runner.py 20260822（主跑）→ negatives.py（负例）→ report_v2.py（本报告）。只读源库；未跑全量 pytest。harness 改动点见 §9.4。")
    md.append("")
    md.append("## 9. 待确认项（交 Jack 拍板）")
    md.append("")
    md.append(f"1. **85% 靶值的口径**：继续按 30 问集扩展语义面（§6.1 10 问转可表达 + §6.2 3 问修口径）后重跑冲 85%，还是先把靶值对齐「可表达问题集内成功率」（本轮可表达 {len(exp)} 问集内为 {exp_set_sr*100:.1f}% = {len([q for q in exp if q in b_correct_set])}/{len(exp)}）？")
    md.append("2. **A2 cofv 指标 join 路径**：COFV.MATNR vs AUFK.MATNR 以哪个为准（demo 数据两列几乎全不同，涉及报工物料归属语义）？")
    md.append("3. **T4 标签口径**：退款对比的 key 用月份标签还是 cur/prev 标签（呈现层 vs 数据层）？")
    md.append("4. **harness 改动点**（Rose 复核）：scripts/headtohead/questions.py（20 问 b_expressible/b_contract/b_note 更新）、prompts.py（B 语义面/对象/契约 schema 示例/口径注入）、runner.py（L6 对象明细提取 + B 提示词带口径）。未改 src/des/* 与 GT。")
    md.append("")

    REPORT.write_text("\n".join(md), encoding="utf-8")
    print("报告已写入", REPORT)
    print(f"A: {A['sr']*100:.1f}% ({A['correct']}/30) | B: {B['sr']*100:.1f}% ({B['correct']}/30) | Δ={delta*100:+.1f}pp")
    print(f"A 拒答 {A['refusal']}, B 拒答 {B['refusal']} | 总成本 ¥{A['cost']+B['cost']:.4f} | B 天花板 {ceiling}/30={ceiling/30*100:.1f}%")


if __name__ == "__main__":
    main()
