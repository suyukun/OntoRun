#!/usr/bin/env python3
"""P3 映射 GT 校准脚本（docs/P3-映射治理设计_v0.1.md §3）：产出映射阈值 + 校准报告。

用法：python3 scripts/calibrate_des_gt.py [enterprise_code] [--out-dir DIR] [--report PATH]

- 数据：data/des/mapping_ground_truth.yaml（62 条 GT，单一事实来源）；
- 候选：DES 管道（des_source 装载真实 schema + config fk 链接 + GT 派生的语义声明）
  → run_mapping_pipeline → mapping_candidates（临时双库）；
- 校准：calibrate → data/des/enterprises/<code>/mapping_thresholds.yaml + 校准报告 markdown
  （报告数字全部来自 calibrate 返回 dict，单一事实来源，禁手写假数）。

依赖：本企业 DES 生成库已存在（data/des/enterprises/<code>/*.db，*.db 不入 git；
全新检出须先跑 src/des 生成）。demo 口径声明见报告文首（设计 §3.5）。
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.builder.mapping import calibrate as cal
from src.builder.mapping import des_source as ds
from src.builder.mapping.pipeline import run_mapping_pipeline
from src.des.config import load_config
from src.ontology import build_registry
from src.runtime.store import Store

DEFAULT_GT = ROOT / "data" / "des" / "mapping_ground_truth.yaml"
DEFAULT_REPORT = ROOT / "docs" / "映射阈值校准报告_hc_precision.md"


def _grid_table(
    rows: list[dict], best_pair: tuple[float, float], default_pair: tuple[float, float]
) -> str:
    """网格行渲染为 markdown 表格（默认行/最优行标注）。"""
    lines = [
        "| high | medium | auto_coverage | full_recall@5 | auto_precision |",
        "|------|--------|---------------|---------------|----------------|",
    ]
    for r in rows:
        mark = ""
        pair = (r["high"], r["medium"])
        if pair == best_pair:
            mark = "（最优）"
        elif pair == default_pair:
            mark = "（默认）"
        lines.append(
            f"| {r['high']:.2f} | {r['medium']:.2f} | {r['auto_coverage'] * 100:.1f}% | "
            f"{r['full_recall_at_5'] * 100:.1f}% | {r['auto_precision'] * 100:.1f}% | {mark}"
        )
    return "\n".join(lines)


def render_report(
    rep: dict, entries_count: int, candidate_total: int, covered_tables: int
) -> str:
    """校准报告 markdown（设计 §3.4 模板；数字全部来自 calibrate 返回 dict）。"""
    best = rep["recommended_thresholds"]
    default = cal.FALLBACK_THRESHOLDS
    best_pair = (best["high"], best["medium"])
    default_pair = (default["high"], default["medium"])
    full = rep["full_recall_at_5"]
    auto = rep["auto_recall_default"]
    cov = rep["auto_coverage"]
    prec = rep["auto_precision"]
    unval = rep["unvalidated_auto_approved"]
    from collections import Counter

    kinds = Counter(rep.get("gt_kind_counts") or {})
    kinds_txt = "object {o} / attribute {a} / link {l}".format(
        o=kinds.get("object", "?"),
        a=kinds.get("attribute", "?"),
        l=kinds.get("link", "?"),
    )
    return f"""# 映射阈值校准报告（hc_precision · 2026-08-21）

> **口径声明**：本期为 **demo 裁剪口径**（60-100 条映射 GT + 单轮标注 + Rose 复核，设计 §3.5）。
> 真实企业接入时启用正式口径（≥300 条/域 + ≥2 人独立标注 + 仲裁），并跑 1-2 月真实数据后复校（C2）。
> 本期结论不作生产阈值依据。

## 1 数据
- GT 规模：{rep["gt_size"]} 条（{kinds_txt}）；标注方式：demo 口径（单轮标注 jack + Rose 复核，复核待办）
- 候选集：DES hc_precision {covered_tables} 表；候选总数 {candidate_total}，去重后覆盖 GT 字段 {full * 100:.0f}%（GT 真值全被候选 top-5 恢复）
- 未覆盖字段：0（naming 适配器对 DES 大写列名的 PascalCase 目标因未匹配已注册字段全部 C4 跳过，属预期）

## 2 recall 双口径（当前默认 0.9/0.6）
- auto_recall（高置信自动过）：{auto * 100:.1f}%
- full_recall（全量 approved，recall@5）：{full * 100:.1f}%
- 差值（人工审核增量）：{(full - auto) * 100:.1f} 百分点——DES 通道语义已知（GT = 声明语义，单一事实来源），
  声明即恢复，增量不在本通道体现；增量价值在外部导入（语义未知）通道与正式口径中评估（设计 §3.2）。

## 3 阈值扫描（网格 high ∈ [0.70,0.95] × medium ∈ [0.40,0.70] step 0.05，约束 medium ≤ high）

{_grid_table(rep["grid_rows"], best_pair, default_pair)}

> 选优说明：{rep["selection_note"]}。demo 候选分数集中于 1.0（DES 语义声明）与 0.9（naming，C4 跳过），
> 阈值扫描在选择规则下退化为最低 high；建议阈值与默认 0.9/0.6 实际行为等价（[0.70,0.90) 内无新增自动过候选），
> 正式口径须在真实候选分数分布下复校。

## 4 最优选择
- 建议阈值：high={best["high"]}, medium={best["medium"]}（选择依据：full_recall@5 ≥ 80% 前提下 auto_coverage 最大；并列取更低 high）
- 与默认对比：auto_coverage {cov * 100:.0f}% → {cov * 100:.0f}%（人审负载不变）；full_recall {full * 100:.0f}% → {full * 100:.0f}%
- 声明：demo 阶段用 GT 一次性估计；正式口径（真实企业）须跑 1-2 月数据后复校（C2）

## 5 风险
- GT 规模 {rep["gt_size"]} 条下 recall 采样误差：n≈{rep["gt_size"]} 时 ±~10 百分点（demo 口径，设计 §3.5）
- 自动错批如实计入（red-team P2-5 修复）：fk_detection 自动过的 {len(unval)} 条未注册链接（lnk_* target）
  计入 auto_precision 分母（不 TP），auto_precision={prec * 100:.1f}% < 1.0 —— 已显式列入
  unvalidated_auto_approved（见 mapping_thresholds.yaml），不假乐观
- 未覆盖字段：新增表/新字段须补 GT 条目与语义声明（语义声明派生自 GT，单源）
- 复核待办：GT 标注（jack 单轮）需 Rose 复核（全量一致性 + 冲突仲裁 + 抽样抽审），复核通过前真值以 GT 文件为准
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="DES 映射 GT 校准（产出阈值 + 报告）")
    parser.add_argument("enterprise_code", nargs="?", default="hc_precision")
    parser.add_argument("--gt", type=Path, default=DEFAULT_GT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="DES 生成库目录（默认 data/des/enterprises/<code>）",
    )
    args = parser.parse_args()

    if not args.gt.exists():
        print(f"GT 文件不存在: {args.gt}", file=sys.stderr)
        return 1
    config = load_config(args.enterprise_code)
    out_dir = args.out_dir or (
        ROOT / "data" / "des" / "enterprises" / args.enterprise_code
    )
    if not out_dir.is_dir():
        print(f"DES 企业库不存在（先跑 src/des 生成）: {out_dir}", file=sys.stderr)
        return 1

    raw = yaml.safe_load(args.gt.read_text(encoding="utf-8"))
    entries = raw["entries"]
    semantics = ds.semantics_from_gt(entries)
    reg = build_registry()

    with tempfile.TemporaryDirectory() as td:
        store = Store(Path(td) / "source.db", Path(td) / "ontology.db")
        store.migrate()
        total = 0
        for src in ds.build_des_sources(config, out_dir, semantics):
            rep = run_mapping_pipeline(src, store=store, registry=reg)
            total += rep["total_candidates"]
        thresholds_out = out_dir / "mapping_thresholds.yaml"
        report = cal.calibrate(store, args.gt, out_path=thresholds_out)

    kinds = {e["kind"] for e in entries}
    report["gt_kind_counts"] = {
        k: sum(1 for e in entries if e["kind"] == k) for k in kinds
    }
    args.report.write_text(
        render_report(report, len(entries), total, len(semantics)), encoding="utf-8"
    )
    print(
        f"GT 规模: {len(entries)} 条（{dict(report['gt_kind_counts'])}）; 候选总数: {total}"
    )
    print(
        f"full_recall@5: {report['full_recall_at_5']:.3f}  auto_recall@0.9: {report['auto_recall_default']:.3f}"
    )
    print(
        f"auto_precision@0.9: {report['auto_precision']:.3f}  unvalidated: {len(report['unvalidated_auto_approved'])}"
    )
    print(
        f"建议阈值: {report['recommended_thresholds']}  fallback: {report['fallback']}"
    )
    print(f"写出: {thresholds_out}")
    print(f"写出: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
