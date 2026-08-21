"""P3 阈值校准（设计 §3）：ground truth + recall@5 / auto_coverage 双口径 + 网格扫描。

- load_ground_truth：YAML {candidate_key: true_target}，candidate_key = "source_table|source_field|kind"
  （兼容 entries 列表形态：{source_table, source_field, kind, gt_target}）；
- recall_at_k（= full_recall@5，门禁口径）：GT 真值命中候选按 score 降序 top-k 的比例，
  阈值无关（人工审核可补齐），不设硬门之外只显式报告；
- auto_coverage(high)：GT 目标被 score≥high 的候选覆盖的比例 = 人工负载反向指标；
- auto_precision(high)：自动过（score≥high）的 GT 键中命中真值的比例，防自动错批扩散；
- 网格扫描：high ∈ [0.70,0.95] × medium ∈ [0.40,0.70] step 0.05，约束 medium≤high，
  在 full_recall@5 ≥ 0.80 前提下选 auto_coverage 最大；无解如实回退默认 (0.9,0.6)；
- 输出 mapping_thresholds.yaml（配置不写死，C2）+ CalibrationReport dict。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.builder.mapping.annotate import MappingCandidate
from src.runtime.store import Store

# 网格范围（任务规格，可参数化）：high 0.7-0.95 / medium 0.4-0.7 step 0.05
HIGH_MIN = 0.70
HIGH_MAX = 0.95
MEDIUM_MIN = 0.40
MEDIUM_MAX = 0.70
STEP = 0.05
RECALL_GATE = 0.80  # 门禁：full_recall@5 ≥ 0.80（S2 计划保留）
FALLBACK_THRESHOLDS = {"high": 0.9, "medium": 0.6}  # 无解回退（P1.5 默认）
RECALL_K = 5
KINDS = frozenset({"object", "attribute", "link"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_key(key: str) -> tuple[str, str, str]:
    parts = key.split("|")
    if len(parts) != 3 or not parts[0] or not parts[1] or parts[2] not in KINDS:
        raise ValueError(
            f"candidate_key 非法（须 source_table|source_field|kind）: {key!r}"
        )
    return parts[0], parts[1], parts[2]


def load_ground_truth(path: str | Path) -> dict[str, str]:
    """加载 GT（YAML {candidate_key: true_target}），加载即校验，非法 fail-fast。"""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("GT 文件根必须是映射 {candidate_key: true_target}")
    entries = raw.get("entries", raw)
    if isinstance(entries, list):
        # 兼容设计 §3.1 条目列表形态
        mapping: dict[str, Any] = {}
        for item in entries:
            key = f"{item['source_table']}|{item['source_field']}|{item.get('kind', '')}"
            mapping[key] = item["gt_target"]
        entries = mapping
    if not isinstance(entries, dict):
        raise TypeError("GT entries 必须是映射或条目列表")
    gt: dict[str, str] = {}
    for key, target in entries.items():
        key = str(key)
        _parse_key(key)
        if not isinstance(target, str) or not target.strip():
            raise ValueError(f"GT 条目 {key!r} 缺 true_target")
        if key in gt:
            raise ValueError(f"GT 条目重复: {key}")
        gt[key] = target.strip()
    return gt


def _candidate_from_row(row) -> MappingCandidate:
    return MappingCandidate(
        candidate_id=row["candidate_id"],
        kind=row["kind"],
        source_table=row["source_table"],
        source_field=row["source_field"],
        target=row["target"],
        confidence_score=row["confidence_score"],
        confidence_level=row["confidence_level"],
        review_status=row["review_status"],
        auto_approved=bool(row["auto_approved"]),
        evidence_json=json.loads(row["evidence_json"] or "{}"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def candidates_for(store: Store, source_table: str, source_field: str, kind: str) -> list[MappingCandidate]:
    """某 (source_table, source_field, kind) 的候选，按 score 降序（C_i，设计 §3.2）。"""
    conn = store.ontology_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM mapping_candidates WHERE source_table=? AND source_field=? "
            "AND kind=? ORDER BY confidence_score DESC",
            (source_table, source_field, kind),
        ).fetchall()
        return [_candidate_from_row(r) for r in rows]
    finally:
        conn.close()


def _matching_score(cands: list[MappingCandidate], target: str) -> float | None:
    """GT 真值命中候选的最大 score；未命中返回 None。"""
    scores = [c.confidence_score for c in cands if c.target == target]
    return max(scores) if scores else None


def recall_at_k(store: Store, gt: dict[str, str], *, k: int = RECALL_K) -> float:
    """full_recall@k：GT 真值 ∈ 候选按 score 降序前 k 名的比例（阈值无关）。"""
    if not gt:
        return 0.0
    hits = 0
    for key, target in gt.items():
        cands = candidates_for(store, *_parse_key(key))
        if target in {c.target for c in cands[:k]}:
            hits += 1
    return hits / len(gt)


def auto_coverage(store: Store, gt: dict[str, str], high: float) -> float:
    """auto_coverage：GT 目标被 score≥high 候选覆盖的比例（= 人工负载反向指标）。"""
    if not gt:
        return 0.0
    covered = 0
    for key, target in gt.items():
        score = _matching_score(candidates_for(store, *_parse_key(key)), target)
        if score is not None and score >= high:
            covered += 1
    return covered / len(gt)


def auto_precision(store: Store, gt: dict[str, str], high: float) -> float:
    """auto_precision：score≥high 的 GT 键中命中真值的比例（防自动错批扩散）。"""
    if not gt:
        return 0.0
    tp = 0
    auto_total = 0
    for key, target in gt.items():
        auto = [c for c in candidates_for(store, *_parse_key(key)) if c.confidence_score >= high]
        if not auto:
            continue
        auto_total += 1
        if any(c.target == target for c in auto):
            tp += 1
    return tp / auto_total if auto_total else 0.0


def _frange(start: float, stop: float, step: float) -> list[float]:
    """step 网格（整数计数避免浮点累积误差）。"""
    values: list[float] = []
    i = 0
    while True:
        v = round(start + i * step, 3)
        if v > stop + 1e-9:
            break
        values.append(v)
        i += 1
    return values


def grid_scan(
    store: Store,
    gt: dict[str, str],
    *,
    high_min: float = HIGH_MIN,
    high_max: float = HIGH_MAX,
    medium_min: float = MEDIUM_MIN,
    medium_max: float = MEDIUM_MAX,
    step: float = STEP,
    recall_gate: float = RECALL_GATE,
    k: int = RECALL_K,
) -> dict[str, Any]:
    """网格扫描：medium≤high 下逐 (high, medium) 计三口径，选满 recall 下 auto_coverage 最大。"""
    full_recall = recall_at_k(store, gt, k=k)
    rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for high in _frange(high_min, high_max, step):
        for medium in _frange(medium_min, medium_max, step):
            if medium > high:
                continue
            row = {
                "high": high,
                "medium": medium,
                "auto_coverage": round(auto_coverage(store, gt, high), 4),
                "full_recall_at_5": round(full_recall, 4),
                "auto_precision": round(auto_precision(store, gt, high), 4),
            }
            rows.append(row)
            if full_recall >= recall_gate and (
                best is None or row["auto_coverage"] > best["auto_coverage"]
            ):
                best = row
    return {
        "full_recall_at_5": round(full_recall, 4),
        "rows": rows,
        "best": best,
    }


def _build_report(
    store: Store,
    gt: dict[str, str],
    scan: dict[str, Any],
    best: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gt_size": len(gt),
        "full_recall_at_5": scan["full_recall_at_5"],
        "auto_recall_default": round(auto_coverage(store, gt, FALLBACK_THRESHOLDS["high"]), 4),
        "recommended_thresholds": {"high": best["high"], "medium": best["medium"]},
        "auto_coverage": best["auto_coverage"],
        "auto_precision": best["auto_precision"],
        "fallback": bool(best.get("fallback")),
        "grid_rows": scan["rows"],
        "calibrated_at": _now(),
    }


def _write_thresholds(
    out_path: str | Path,
    thresholds: dict[str, Any],
    report: dict[str, Any],
) -> None:
    doc = {
        "version": "0.1",
        "domain": "mapping-thresholds",
        "calibrated_at": report["calibrated_at"],
        "gt_size": report["gt_size"],
        "full_recall_at_5": report["full_recall_at_5"],
        "auto_coverage": report["auto_coverage"],
        "thresholds": thresholds,
        "selection": "满 full_recall@5>=0.80 下 auto_coverage 最大；无解回退 0.9/0.6（C2 不写死）",
        "fallback": report["fallback"],
    }
    Path(out_path).write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def calibrate(
    store: Store,
    gt_path: str | Path,
    out_path: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """GT 校准入口：加载 → 扫描 → 选优（无解回退）→ 写 mapping_thresholds.yaml + 报告。

    kwargs 透传 grid_scan（high/medium 范围、step、recall_gate 等可配）。
    """
    gt = load_ground_truth(gt_path)
    scan = grid_scan(store, gt, **kwargs)
    if scan["best"] is None:
        # 无解：如实回退默认阈值并标注（设计 §3.3，不静默）
        best = {
            "high": FALLBACK_THRESHOLDS["high"],
            "medium": FALLBACK_THRESHOLDS["medium"],
            "auto_coverage": round(auto_coverage(store, gt, FALLBACK_THRESHOLDS["high"]), 4),
            "full_recall_at_5": scan["full_recall_at_5"],
            "auto_precision": round(auto_precision(store, gt, FALLBACK_THRESHOLDS["high"]), 4),
            "fallback": True,
        }
    else:
        best = dict(scan["best"])
        best.setdefault("fallback", False)
    report = _build_report(store, gt, scan, best)
    if out_path is not None:
        _write_thresholds(
            out_path, {"high": best["high"], "medium": best["medium"]}, report
        )
    return report


__all__ = [
    "FALLBACK_THRESHOLDS",
    "auto_coverage",
    "auto_precision",
    "calibrate",
    "candidates_for",
    "grid_scan",
    "load_ground_truth",
    "recall_at_k",
]
