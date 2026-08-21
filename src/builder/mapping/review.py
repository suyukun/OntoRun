"""P3 映射人工审核 CLI（设计 §2）：候选快照导出 → 人工裁决 CSV → 批量导入回写。

- export：mapping_candidates → CSV（只读快照，导入以 candidate_id 关联回权威）；
- import：裁决 CSV（candidate_id,decision,corrected_target,note）→ 逐候选原子更新：
  accept → approved（可先改 target）＋ history(reviewer=cli) ＋ audit(source='review')；
  reject → rejected（draft 先转 reviewing）；conflict → 留队列＋MAPPING_CONFLICT 审计。
  非法/缺失行记入失败清单不静默（fail-fast 于该行），汇总输出 ReviewBatchReport。
审核工作台 UI 后置（P5），CLI 是 P3 审核入口；审核痕迹权威 = mapping_review_history
（WORM），audit_log 为同步证据链（设计 §2.2）。
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.builder.mapping.annotate import (
    APPROVED,
    REJECTED,
    REVIEWING,
    MappingCandidateService,
)
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.store import Store

# 导出列（只读快照；导入仅用 candidate_id 回锚，decision/corrected_target/note 为裁决列）
EXPORT_COLUMNS = [
    "candidate_id",
    "kind",
    "source_table",
    "source_field",
    "target",
    "confidence_score",
    "confidence_level",
    "review_status",
    "evidence_json",
]
IMPORT_COLUMNS = ["candidate_id", "decision", "corrected_target", "note"]
VALID_DECISIONS = frozenset({"accept", "reject", "conflict"})

REVIEWER_CLI = "cli"  # 任务规格：CLI 导入 reviewer='cli'（写 review_history）
AUDIT_ACTOR = "human"  # audit_log.actor CHECK 白名单 ('human','llm','api')，cli 走 actor_detail
AUDIT_ACTION_REVIEW = "mapping_review"
AUDIT_SOURCE_REVIEW = "review"
PAGE_ALL = 1_000_000


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _service(store: Store) -> MappingCandidateService:
    """CLI 只用 list/get/transition，不触 C4 校验，registry 传空即可。"""
    return MappingCandidateService(store, Registry())


def export_candidates(
    store: Store,
    out_path: str | Path,
    *,
    status: str | None = None,
    level: str | None = None,
) -> dict[str, Any]:
    """导出 mapping_candidates 快照 CSV（过滤 status/level 可空）。空表也输出表头。"""
    rows, _total = _service(store).list(
        status=status, level=level, page=1, page_size=PAGE_ALL
    )
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        for c in rows:
            writer.writerow(
                {
                    "candidate_id": c.candidate_id,
                    "kind": c.kind,
                    "source_table": c.source_table,
                    "source_field": c.source_field or "",
                    "target": c.target,
                    "confidence_score": c.confidence_score,
                    "confidence_level": c.confidence_level,
                    "review_status": c.review_status,
                    "evidence_json": json.dumps(c.evidence_json, ensure_ascii=False),
                }
            )
    return {"path": str(out_path), "exported": len(rows)}


def import_decisions(
    store: Store,
    in_path: str | Path,
    *,
    reviewer: str = REVIEWER_CLI,
) -> dict[str, Any]:
    """导入裁决 CSV，逐候选原子更新；失败行记入 failures 不静默。"""
    audit = AuditLog(store)
    service = _service(store)
    report: dict[str, Any] = {
        "processed": 0,
        "accepted": 0,
        "rejected": 0,
        "conflicts": 0,
        "published_to_registry": 0,  # 改完即入注册表由 publish 阶段承接，此处占位
        "failed": 0,
        "failures": [],
    }
    with open(in_path, newline="", encoding="utf-8") as f:
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            candidate_id = (row.get("candidate_id") or "").strip()
            decision = (row.get("decision") or "").strip().lower()
            corrected = (row.get("corrected_target") or "").strip() or None
            note = (row.get("note") or "").strip()
            if not candidate_id or decision not in VALID_DECISIONS:
                _fail(report, line_no, f"非法/缺失 decision={decision!r} candidate={candidate_id!r}")
                continue
            try:
                _apply_decision(
                    store, service, audit, candidate_id, decision, corrected, note, reviewer, report
                )
            except Exception as exc:  # noqa: BLE001 —— 逐行原子，异常记失败不中断批次
                _fail(report, line_no, f"{type(exc).__name__}: {exc}")
    return report


def _fail(report: dict[str, Any], line_no: int, reason: str) -> None:
    report["failed"] += 1
    report["failures"].append({"line": line_no, "reason": reason})


def _apply_decision(
    store: Store,
    service: MappingCandidateService,
    audit: AuditLog,
    candidate_id: str,
    decision: str,
    corrected: str | None,
    note: str,
    reviewer: str,
    report: dict[str, Any],
) -> None:
    cand = service.get(candidate_id)
    if cand is None:
        raise KeyError(f"候选不存在: {candidate_id}")
    detail = {
        "candidate_id": candidate_id,
        "kind": cand.kind,
        "source_table": cand.source_table,
        "source_field": cand.source_field,
        "target_from": cand.target,
        "corrected_target": corrected,
        "note": note,
    }
    if decision == "accept":
        if cand.review_status == APPROVED:
            # approved 为终态：接受为幂等确认；改 target 则拒绝（变更走新候选重审）
            if corrected and corrected != cand.target:
                raise ValueError(f"approved 终态不可改 target，变更须新建候选: {candidate_id}")
            _audit_review(audit, reviewer, "applied", detail, note)
        else:
            if corrected:
                _update_target(store, candidate_id, corrected)
            service.transition(candidate_id, APPROVED, reviewer, note)
            _audit_review(audit, reviewer, "applied", detail, note)
        report["accepted"] += 1
    elif decision == "reject":
        if cand.review_status == "draft":
            # 状态机无 draft→rejected，先转 reviewing 再拒绝（设计 §2.1）
            service.transition(candidate_id, REVIEWING, reviewer, "draft→reviewing 前置流转")
        service.transition(candidate_id, REJECTED, reviewer, note)
        _audit_review(audit, reviewer, "rejected", detail, note)
        report["rejected"] += 1
    else:  # conflict：不流转，留队列 + MAPPING_CONFLICT 审计（设计 §2.4）
        _audit_review(
            audit, reviewer, "rejected", detail, note,
            error_code="MAPPING_CONFLICT",
        )
        report["conflicts"] += 1
    report["processed"] += 1


def _update_target(store: Store, candidate_id: str, target: str) -> None:
    """服务层无改 target 方法（annotate.py 不做改动，设计 §0.2），CLI 直写映射表。"""
    if not target:
        raise ValueError("corrected_target 不能为空")
    conn = store.ontology_conn()
    try:
        conn.execute(
            "UPDATE mapping_candidates SET target=?, updated_at=? WHERE candidate_id=?",
            (target, _now(), candidate_id),
        )
        conn.commit()
    finally:
        conn.close()


def _audit_review(
    audit: AuditLog,
    reviewer: str,
    outcome: str,
    detail: dict[str, Any],
    note: str,
    *,
    error_code: str | None = None,
) -> None:
    audit.append(
        AuditRecord(
            action_name=AUDIT_ACTION_REVIEW,
            actor=AUDIT_ACTOR,
            actor_detail=f"cli:{reviewer}",
            outcome=outcome,
            error_code=error_code,
            message=note or None,
            detail_json=json.dumps(detail, ensure_ascii=False),
            source=AUDIT_SOURCE_REVIEW,
        )
    )


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ontology-db", default=None, help="本体库路径（默认 data/ontology/ontology.db）")
    parser.add_argument("--source-db", default=None, help="源系统库路径（默认 data/sources/retail_source.db）")


def _make_store(args: argparse.Namespace) -> Store:
    return Store(
        source_path=args.source_db,
        ontology_path=args.ontology_db,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.builder.mapping.review",
        description="P3 映射人工审核 CLI：候选快照导出 / 裁决导入（设计 §2）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser("export", help="导出 mapping_candidates 快照 CSV")
    p_export.add_argument("--out", required=True, help="导出 CSV 路径")
    p_export.add_argument("--status", default=None, help="过滤状态（draft/reviewing/approved/rejected）")
    p_export.add_argument("--level", default=None, help="过滤档位（high/medium/low）")
    _add_common(p_export)

    p_import = sub.add_parser("import", help="导入裁决 CSV（accept/reject/conflict）")
    p_import.add_argument("--file", required=True, help="裁决 CSV 路径")
    p_import.add_argument("--reviewer", default=REVIEWER_CLI, help="审核人标识（默认 cli）")
    _add_common(p_import)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = _make_store(args)
    if args.command == "export":
        result = export_candidates(
            store, args.out, status=args.status, level=args.level
        )
    else:
        result = import_decisions(store, args.file, reviewer=args.reviewer)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
