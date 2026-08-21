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
import re
from pathlib import Path
from typing import Any

from src.builder.mapping.annotate import (
    APPROVED,
    REJECTED,
    REVIEWING,
    MappingCandidateService,
)
from src.ontology import build_registry
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.permissions import PermissionService, resolve_human_subject
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

# corrected_target 格式白名单（P1-3 ③：写入前格式 + C4 注册表校验）
_OBJECT_TARGET_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_ATTR_TARGET_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_LINK_TARGET_RE = re.compile(r"^[a-z][a-z0-9_.]*$")


def _service(store: Store) -> MappingCandidateService:
    """CLI 服务：registry 用 build_registry（本体已知对象集），供 corrected_target 的 C4
    校验（P1-3 ③）对「已注册对象/字段」放行；list/get/transition 不依赖 registry。"""
    return MappingCandidateService(store, build_registry())


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
    permission: PermissionService | None = None,
) -> dict[str, Any]:
    """导入裁决 CSV，逐候选原子更新；失败行记入 failures 不静默。

    permission：approve 权限门判定器（P1-3 ①）；不传时从 store 的 permission_policies
    表自动加载（gate 恒开，fail-closed：无 approve 策略即拒）。
    """
    audit = AuditLog(store)
    service = _service(store)
    perm = permission or _permission_service(store)
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
                    store, service, audit, perm, candidate_id, decision, corrected, note,
                    reviewer, report,
                )
            except Exception as exc:  # noqa: BLE001 —— 逐行原子，异常记失败不中断批次
                _fail(report, line_no, f"{type(exc).__name__}: {exc}")
    return report


def _permission_service(store: Store) -> PermissionService:
    """默认 approve 权限判定器：从 store 的 permission_policies 表加载（gate 恒开）。"""
    return PermissionService(store, Registry())


def _validate_corrected_target(
    service: MappingCandidateService, cand, corrected: str
) -> None:
    """corrected_target 写入前校验（P1-3 ③）：格式白名单 + C4 注册表（复用 check_c4）。"""
    if not corrected:
        raise ValueError("corrected_target 不能为空")
    if cand.kind == "object":
        if not _OBJECT_TARGET_RE.match(corrected):
            raise ValueError(f"object 目标格式非法: {corrected!r}")
        errors = service.check_c4("object", corrected)
    elif cand.kind == "attribute":
        if not _ATTR_TARGET_RE.match(corrected):
            raise ValueError(f"attribute 目标格式非法: {corrected!r}")
        errors = service.check_c4("attribute", corrected)
    else:  # link：C4 不校验（publish 阶段校验端点），只查格式
        if not _LINK_TARGET_RE.match(corrected):
            raise ValueError(f"link 目标格式非法: {corrected!r}")
        errors = []
    if errors:
        raise ValueError("；".join(errors))


def _fail(report: dict[str, Any], line_no: int, reason: str) -> None:
    report["failed"] += 1
    report["failures"].append({"line": line_no, "reason": reason})


def _apply_decision(
    store: Store,
    service: MappingCandidateService,
    audit: AuditLog,
    perm: PermissionService,
    candidate_id: str,
    decision: str,
    corrected: str | None,
    note: str,
    reviewer: str,
    report: dict[str, Any],
) -> None:
    """逐候选原子应用裁决：approve 权限门 + corrected 校验 + 单连接单事务（P1-3/P2-6）。"""
    cand = service.get(candidate_id)
    if cand is None:
        raise KeyError(f"候选不存在: {candidate_id}")
    subject = _preflight(service, perm, cand, decision, corrected, reviewer)
    detail = {
        "candidate_id": candidate_id,
        "kind": cand.kind,
        "source_table": cand.source_table,
        "source_field": cand.source_field,
        "target_from": cand.target,
        "corrected_target": corrected,
        "note": note,
    }
    conn = store.ontology_conn()
    try:
        _apply_decision_txn(
            conn, service, audit, cand, decision, corrected, note, reviewer, subject, detail, report,
        )
        report["processed"] += 1
        conn.commit()  # 改 target + 流转 + history + audit 单事务提交（P2-6 原子）
    except Exception:
        conn.rollback()  # 任一步失败整体回滚，不落中间态
        raise
    finally:
        conn.close()


def _preflight(service, perm, cand, decision, corrected, reviewer) -> Any:
    """P1-3 前置校验：approved 终态锁 target → corrected 格式/C4 → approve 权限门（human 专属）。"""
    if (
        decision == "accept"
        and cand.review_status == APPROVED
        and corrected
        and corrected != cand.target
    ):
        raise ValueError(f"approved 终态不可改 target，变更须新建候选: {cand.candidate_id}")
    if decision == "accept" and corrected:
        _validate_corrected_target(service, cand, corrected)
    subject = resolve_human_subject(reviewer)  # V9：agent 一律拒
    effective_target = corrected if (decision == "accept" and corrected) else cand.target
    if not perm.decide(subject, effective_target, "approve").allowed:
        raise ValueError(
            f"approve 权限不足: {subject.id} 对 {effective_target} 无 approve 权限"
        )
    return subject


def _apply_decision_txn(
    conn, service, audit, cand, decision, corrected, note, reviewer, subject, detail, report,
) -> None:
    """单连接单事务内应用裁决（accept/reject/conflict + 审计）；commit/rollback 由调用方负责。"""
    if decision == "accept":
        if cand.review_status == APPROVED:
            # approved 为终态：接受为幂等确认（改 target 已在前置校验拒绝）
            _audit_review(conn, audit, reviewer, "applied", detail, note)
        else:
            if corrected:
                service.update_target_on(conn, cand.candidate_id, corrected)
            service.transition_on(
                conn, cand.candidate_id, APPROVED, reviewer, note, from_status=cand.review_status
            )
            _audit_review(conn, audit, reviewer, "applied", detail, note)
        report["accepted"] += 1
    elif decision == "reject":
        if cand.review_status == "draft":
            # 状态机无 draft→rejected，先转 reviewing 再拒绝（设计 §2.1）；
            # 事务内两跳，from_status 显式传值防重读新连接看不到中间态
            service.transition_on(
                conn, cand.candidate_id, REVIEWING, reviewer,
                "draft→reviewing 前置流转", from_status=cand.review_status,
            )
            service.transition_on(
                conn, cand.candidate_id, REJECTED, reviewer, note, from_status=REVIEWING
            )
        else:
            service.transition_on(
                conn, cand.candidate_id, REJECTED, reviewer, note, from_status=cand.review_status
            )
        _audit_review(conn, audit, reviewer, "rejected", detail, note)
        report["rejected"] += 1
    else:  # conflict：不流转，留队列 + MAPPING_CONFLICT 审计（设计 §2.4）
        _audit_review(
            conn, audit, reviewer, "rejected", detail, note,
            error_code="MAPPING_CONFLICT",
        )
        report["conflicts"] += 1


def _audit_review(
    conn,
    audit: AuditLog,
    reviewer: str,
    outcome: str,
    detail: dict[str, Any],
    note: str,
    *,
    error_code: str | None = None,
) -> None:
    """落 source='review' 审计（P2-6：走调用方单连接单事务，commit 由外部负责）。"""
    audit.append_on(
        conn,
        AuditRecord(
            action_name=AUDIT_ACTION_REVIEW,
            actor=AUDIT_ACTOR,
            actor_detail=f"cli:{reviewer}",
            outcome=outcome,
            error_code=error_code,
            message=note or None,
            detail_json=json.dumps(detail, ensure_ascii=False),
            source=AUDIT_SOURCE_REVIEW,
        ),
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
