"""action_runs 表仓储 + E6 快照审计编排（蓝图 v0.3 §4/E6 / P4-T3）。

职责：
- 经 /actions/{name}/run 执行（真实 run 与 dry_run）时写 action_runs：
  before_snapshot_json（引擎事务内 load_snapshot 的相关对象状态）、
  after_snapshot_json、status(applied/rejected/failed/dry_run)、error、
  executed_by（透传 actor，白名单 human/llm/api）、audit_ref；
- 与 audit_log 的关系：audit_log 是运行时审计权威，action_runs 是构建侧
  动作审计证据面；action_runs.audit_ref 引用 audit_log.audit_id（对账锚点），
  不复制审计真相（不双轨漂移）。dry_run 无 runtime 审计记录，audit_ref 为空；
- rejected/failed 路径同样落 action_runs（源库零变更但审计有记录），对齐
  引擎"拒绝路径早退仍审计"的设计；
- 错误信息只落错误码/业务消息（与 audit_log 同源），不回显 SQL 参数等敏感数据。
"""

from __future__ import annotations

import copy
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.runtime.action_engine import (
    FAILED_CODE_EXECUTION,
    ActionResult,
    Snapshot,
)

logger = logging.getLogger(__name__)

RUN_STATUSES: tuple[str, ...] = ("applied", "rejected", "failed", "dry_run")

# 引擎 outcome -> action_runs.status（一致命名，dry_run 由引擎 E6 扩展产生）
_OUTCOME_TO_STATUS = {
    "applied": "applied",
    "rejected": "rejected",
    "failed": "failed",
    "dry_run": "dry_run",
}

# TD-11：after 快照重读异常时的降级文案（F1 口径安全摘要：不回显原始异常/SQL 细节；
# 引擎侧审计已落，action_runs 保留 audit_ref 对账锚点，源库状态以直查为准）。
_FAILED_SNAPSHOT_MESSAGE = (
    "动作已执行且审计已落库，但 after 快照重读失败（快照降级，源库状态以直查为准）"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"arun_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class ActionRunRow:
    """action_runs 表行（frozen）。动作名经 action_type_id 关联 action_types。"""

    id: str
    action_type_id: str
    before_snapshot: dict
    after_snapshot: dict
    status: str
    error: str
    executed_by: str
    audit_ref: str
    created_at: str


def _load_json(raw, default):
    if raw is None:
        return default
    if isinstance(raw, (str, bytes, bytearray)):
        return json.loads(raw) if raw else default
    if isinstance(raw, dict):
        return raw
    return default


def _row_factory(row: sqlite3.Row) -> ActionRunRow:
    return ActionRunRow(
        id=row["id"],
        action_type_id=row["action_type_id"],
        before_snapshot=_load_json(row["before_snapshot_json"], {}),
        after_snapshot=_load_json(row["after_snapshot_json"], {}),
        status=row["status"],
        error=row["error"] or "",
        executed_by=row["executed_by"],
        audit_ref=row["audit_ref"],
        created_at=row["created_at"],
    )


def insert(
    conn: sqlite3.Connection,
    *,
    action_type_id: str,
    before_snapshot: dict,
    after_snapshot: dict,
    status: str,
    error: str = "",
    executed_by: str = "api",
    audit_ref: str = "",
) -> ActionRunRow:
    if status not in RUN_STATUSES:
        raise ValueError(f"status 非法: {status}")
    new_id = _new_id()
    conn.execute(
        "INSERT INTO action_runs (id, action_type_id, before_snapshot_json, "
        "after_snapshot_json, status, error, executed_by, audit_ref, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            action_type_id,
            json.dumps(before_snapshot, ensure_ascii=False, default=str),
            json.dumps(after_snapshot, ensure_ascii=False, default=str),
            status,
            error,
            executed_by,
            audit_ref,
            _now(),
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, run_id: str) -> ActionRunRow | None:
    row = conn.execute("SELECT * FROM action_runs WHERE id = ?", (run_id,)).fetchone()
    return _row_factory(row) if row else None


def list_by_action(
    conn: sqlite3.Connection,
    action_type_id: str,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ActionRunRow], int]:
    total = conn.execute(
        "SELECT COUNT(*) AS c FROM action_runs WHERE action_type_id = ?",
        (action_type_id,),
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        "SELECT * FROM action_runs WHERE action_type_id = ? "
        "ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
        (action_type_id, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def row_to_dict(row: ActionRunRow) -> dict:
    return {
        "id": row.id,
        "action_type_id": row.action_type_id,
        "before_snapshot": row.before_snapshot,
        "after_snapshot": row.after_snapshot,
        "status": row.status,
        "error": row.error,
        "executed_by": row.executed_by,
        "audit_ref": row.audit_ref,
        "created_at": row.created_at,
    }


# ----------------------------------------------------------------------
# E6 快照构造
# ----------------------------------------------------------------------


def _effect_pairs(result: ActionResult) -> list[tuple[str, str]]:
    return list({(e.object_type, str(e.pk)) for e in result.effects})


def _reread_records(store, registry, pairs: list[tuple[str, str]]) -> dict:
    """提交后按 effects 覆盖对象重读源记录（after 快照的权威来源）。

    只吞 KeyError（对象类型/主键在重读时消失，记录为 None）；其余异常上抛，
    由 run_action 的兜底降级（TD-11），保证 action_runs 不丢行（对账缺口）。
    """
    records: dict[str, dict] = {}
    conn = store.source_conn()
    try:
        reader = Snapshot(conn, registry)
        for object_type, pk in pairs:
            bucket = records.setdefault(object_type, {})
            try:
                bucket[pk] = reader.get(object_type, pk)
            except KeyError:
                bucket[pk] = None
    finally:
        conn.close()
    return records


def _build_after_snapshot(
    result: ActionResult,
    store,
    registry,
    before_snapshot: dict,
) -> dict:
    """按结局构造 after 快照。

    - applied：按 effects 覆盖对象重读源记录（真实变更）；
    - dry_run：重读（未变更）+ effects 新值叠加（simulated=true）；
    - rejected：与 before 完全一致（源库零变更）；
    - failed：有 effects（源库已提交但本体同步失败等）则重读，否则等于 before。
    """
    pairs = _effect_pairs(result)
    if result.outcome == "applied":
        return {
            "records": _reread_records(store, registry, pairs),
            "effects": [e.model_dump() for e in result.effects],
        }
    if result.outcome == "dry_run":
        return {
            "simulated": True,
            "records": _simulate_records(
                _reread_records(store, registry, pairs), result
            ),
            "effects": [e.model_dump() for e in result.effects],
        }
    if result.outcome == "failed" and pairs:
        return {
            "records": _reread_records(store, registry, pairs),
            "effects": [e.model_dump() for e in result.effects],
        }
    # rejected / 无 effects 的 failed：源库零变更，after == before
    return copy.deepcopy(before_snapshot)


def _simulate_records(records: dict, result: ActionResult) -> dict:
    """dry_run 演算：重读记录（未变更）叠加 effects 新值 = would-be 状态。"""
    simulated = copy.deepcopy(records)
    for eff in result.effects:
        bucket = simulated.setdefault(eff.object_type, {})
        rec = bucket.get(str(eff.pk))
        if not isinstance(rec, dict):
            rec = {}
            bucket[str(eff.pk)] = rec
        rec[eff.prop] = eff.new
    return simulated


def _error_text(result: ActionResult) -> str:
    """错误文本：业务码 + 消息（与 audit_log 同源；不回显 SQL/参数/原始异常）。"""
    if result.outcome == "rejected" and result.error_code:
        return f"{result.error_code}: {result.message or ''}".strip()
    if result.outcome == "failed":
        # failed 的 message 已是引擎侧安全摘要（F1：原始异常只进日志）
        if result.error_code:
            return f"{result.error_code}: {result.message or ''}".strip()
        return result.message or "failed"
    return ""


def run_action(
    store,
    registry,
    engine,
    ontology_conn: sqlite3.Connection,
    *,
    action_type_id: str,
    action_name: str,
    params: dict[str, Any],
    actor: str,
    dry_run: bool,
    request_id: str = "",
) -> tuple[ActionResult, ActionRunRow]:
    """执行动作并落 action_runs（E6 证据面）。

    before = 引擎事务内 handler 快照（相关对象执行前状态；参数校验失败等
    早退路径下 objects 为 None）。after 按结局构造：
    - applied：按 effects 覆盖对象重读源记录（真实变更）；
    - dry_run：重读（未变更）+ effects 新值叠加（simulated=true）；
    - rejected：与 before 完全一致（源库零变更）；
    - failed：有 effects（源库已提交但本体同步失败等）则重读，否则等于 before。
    重读/快照构造抛异常时不冒泡丢行（TD-11）：降级为 failed run，保留
    audit_ref 对账锚点，after_snapshot 标记 degraded（源库状态以直查为准）。
    """
    before_objects: dict | None = None

    def _observe(snapshot: dict) -> None:
        nonlocal before_objects
        before_objects = snapshot

    result = engine.execute(
        action_name,
        params,
        actor=actor,
        request_id=request_id,
        dry_run=dry_run,
        snapshot_observer=_observe,
    )
    before_snapshot: dict = {"action": action_name, "params": params}
    if before_objects is not None:
        before_snapshot["objects"] = before_objects

    try:
        after_snapshot = _build_after_snapshot(result, store, registry, before_snapshot)
    except Exception:  # TD-11 兜底：快照构造异常不冒泡丢行
        # 引擎侧已提交 + 审计已落（applied/rejected/failed 均落 audit_log）；
        # 此处降级为 failed action_run 并保留 audit_ref 锚点，闭合对账缺口。
        # 原始异常只进日志（F1 口径：对外 error 用稳定安全摘要，不回显 SQL 细节）。
        logger.exception(
            "after 快照重读失败（快照降级为 failed run）: action=%s audit_ref=%s",
            action_name,
            result.audit_id or "",
        )
        result = result.model_copy(
            update={
                "outcome": "failed",
                "error_code": FAILED_CODE_EXECUTION,
                "message": _FAILED_SNAPSHOT_MESSAGE,
            }
        )
        after_snapshot = {
            "degraded": True,
            "reason": "after-snapshot reread failed; audit already recorded",
        }

    run_row = insert(
        ontology_conn,
        action_type_id=action_type_id,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
        status=_OUTCOME_TO_STATUS.get(result.outcome, "failed"),
        error=_error_text(result),
        executed_by=actor,
        audit_ref=result.audit_id or "",
    )
    return result, run_row


__all__ = [
    "RUN_STATUSES",
    "ActionRunRow",
    "get",
    "insert",
    "list_by_action",
    "row_to_dict",
    "run_action",
]
