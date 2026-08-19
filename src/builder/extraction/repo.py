"""extraction_tasks 表仓储（蓝图 v0.3 §4 extraction_tasks / 补丁 C3）。

extraction_tasks 表结构（BUILDER_SCHEMA 已建）：
  id, ontology_id, status (pending/running/succeeded/failed/rejected),
  result_summary_json, validation_report_json,
  source_path, provider, created_at, updated_at

P3 范围：CRUD + status 流转（同步执行；succeeded / failed / rejected）。
P4/P5 增 run 与进度语义。
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

ALLOWED_STATUSES: tuple[str, ...] = (
    "pending",
    "running",
    "succeeded",
    "failed",
    "rejected",
)
_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"running", "succeeded", "failed", "rejected"}),
    "running": frozenset({"succeeded", "failed", "rejected"}),
    "succeeded": frozenset(),
    "failed": frozenset(),
    "rejected": frozenset(),
}


class IllegalTransitionError(ValueError):
    def __init__(self, current, target):
        self.current = current
        self.target = target
        super().__init__(f"extraction_task 非法状态流转: {current} -> {target}")


def _assert_transition(current, target):
    if current not in _TRANSITIONS:
        raise IllegalTransitionError(current, target)
    if target not in _TRANSITIONS[current]:
        raise IllegalTransitionError(current, target)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id():
    return f"et_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class ExtractionTaskRow:
    id: str
    ontology_id: str
    status: str
    result_summary: dict
    validation_report: dict
    source_path: str
    provider: str
    created_at: str
    updated_at: str


def _load_json(raw, default):
    if raw is None:
        return default
    if isinstance(raw, (str, bytes, bytearray)):
        return json.loads(raw) if raw else default
    if isinstance(raw, (list, dict)):
        return raw
    return default


def _row_factory(row):
    return ExtractionTaskRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        status=row["status"],
        result_summary=_load_json(row["result_summary_json"], {}),
        validation_report=_load_json(row["validation_report_json"], {}),
        source_path=row["source_path"] or "",
        provider=row["provider"] or "",
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create(
    conn,
    *,
    ontology_id="default",
    status="pending",
    result_summary=None,
    validation_report=None,
    source_path="",
    provider="",
):
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"status 非法: {status}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO extraction_tasks (id, ontology_id, status, "
        "result_summary_json, validation_report_json, source_path, provider, "
        "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            status,
            json.dumps(result_summary or {}, ensure_ascii=False),
            json.dumps(validation_report or {}, ensure_ascii=False),
            source_path,
            provider,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)


def get(conn, et_id):
    row = conn.execute(
        "SELECT * FROM extraction_tasks WHERE id = ?", (et_id,)
    ).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn,
    *,
    status=None,
    page=1,
    page_size=20,
):
    where = []
    params = []
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM extraction_tasks {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM extraction_tasks {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def transition_status(conn, et_id, target):
    row = get(conn, et_id)
    if row is None:
        return None
    _assert_transition(row.status, target)
    if target not in ALLOWED_STATUSES:
        raise ValueError(f"target 非法: {target}")
    conn.execute(
        "UPDATE extraction_tasks SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), et_id),
    )
    conn.commit()
    return get(conn, et_id)


def update_result(
    conn,
    et_id,
    *,
    result_summary=None,
    validation_report=None,
    status=None,
):
    row = get(conn, et_id)
    if row is None:
        return None
    sets = []
    params = []
    if result_summary is not None:
        sets.append("result_summary_json = ?")
        params.append(json.dumps(result_summary, ensure_ascii=False))
    if validation_report is not None:
        sets.append("validation_report_json = ?")
        params.append(json.dumps(validation_report, ensure_ascii=False))
    if status is not None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"status 非法: {status}")
        _assert_transition(row.status, status)
        sets.append("status = ?")
        params.append(status)
    if not sets:
        return row
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(et_id)
    conn.execute(
        f"UPDATE extraction_tasks SET {', '.join(sets)} WHERE id = ?",
        params,
    )
    conn.commit()
    return get(conn, et_id)


def row_to_dict(row):
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "status": row.status,
        "result_summary": row.result_summary,
        "validation_report": row.validation_report,
        "source_path": row.source_path,
        "provider": row.provider,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


__all__ = [
    "ALLOWED_STATUSES",
    "ExtractionTaskRow",
    "IllegalTransitionError",
    "create",
    "get",
    "list_all",
    "row_to_dict",
    "transition_status",
    "update_result",
]
