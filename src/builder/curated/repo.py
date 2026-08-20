"""curated_datasets 仓储。

状态机：draft -> reviewed -> approved（与 object_types/link_types 独立，
ALL_STATUSES_REVIEW = (DRAFT, REVIEWED, APPROVED)）。
quality_score JSON 由管道 run 末尾节点填入，MVP 阶段含：
  - row_count（行数）
  - duplicate_rate（重复率，0.0-1.0）
  - completeness（非空率均值）
  - source_path / pipeline_run_id（来源溯源）
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DRAFT = "draft"
REVIEWED = "reviewed"
APPROVED = "approved"
ALL_STATUSES: tuple[str, ...] = (DRAFT, REVIEWED, APPROVED)

_TRANSITIONS: dict[str, frozenset[str]] = {
    DRAFT: frozenset({REVIEWED}),
    REVIEWED: frozenset({APPROVED}),
    APPROVED: frozenset(),  # 终态
}


class IllegalTransitionError(ValueError):
    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(f"curated 非法状态流转: {current} -> {target}")


def assert_transition(current: str, target: str) -> None:
    if current not in _TRANSITIONS:
        raise IllegalTransitionError(current, target)
    if target not in _TRANSITIONS[current]:
        raise IllegalTransitionError(current, target)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"cur_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class CuratedRow:
    """curated_datasets 表行。"""

    id: str
    dataset_id: str
    quality_json: dict
    status: str
    version: int
    row_count: int
    created_at: str
    updated_at: str


def _row_factory(row: sqlite3.Row) -> CuratedRow:
    raw = row["quality_json"]
    if isinstance(raw, (str, bytes, bytearray)):
        parsed: dict = json.loads(raw) if raw else {}
    elif isinstance(raw, dict):
        parsed = raw
    else:
        parsed = {}
    return CuratedRow(
        id=row["id"],
        dataset_id=row["dataset_id"],
        quality_json=parsed,
        status=row["status"],
        version=row["version"],
        row_count=row["row_count"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ----------------------------------------------------------------------
# CRUD
# ----------------------------------------------------------------------


def get_by_id(conn: sqlite3.Connection, cur_id: str) -> CuratedRow | None:
    row = conn.execute(
        "SELECT * FROM curated_datasets WHERE id = ?", (cur_id,)
    ).fetchone()
    return _row_factory(row) if row else None


def get_by_dataset_id(
    conn: sqlite3.Connection, dataset_id: str
) -> CuratedRow | None:
    row = conn.execute(
        "SELECT * FROM curated_datasets WHERE dataset_id = ? "
        "ORDER BY created_at DESC LIMIT 1",
        (dataset_id,),
    ).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[CuratedRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM curated_datasets {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM curated_datasets {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def upsert_from_run(
    conn: sqlite3.Connection,
    *,
    dataset_id: str,
    quality: dict,
    row_count: int,
) -> CuratedRow:
    """管道 run 末尾调：dataset_id 已存在 -> 升 version + 更新 quality；否则建 draft。

    P2 简化：每次 run 累加 version（同 dataset_id），便于对比历史质量。
    """
    existing = get_by_dataset_id(conn, dataset_id)
    if existing is None:
        new_id = _new_id()
        now = _now()
        conn.execute(
            "INSERT INTO curated_datasets (id, dataset_id, quality_json, status, "
            "version, row_count, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                new_id,
                dataset_id,
                json.dumps(quality, ensure_ascii=False),
                DRAFT,
                1,
                row_count,
                now,
                now,
            ),
        )
        conn.commit()
        return get_by_id(conn, new_id)  # type: ignore[return-value]
    # 已有：version++ + 质量覆盖 + status 退回 draft（重新审核）
    new_version = existing.version + 1
    now = _now()
    conn.execute(
        "UPDATE curated_datasets SET quality_json = ?, status = ?, "
        "version = ?, row_count = ?, updated_at = ? WHERE id = ?",
        (
            json.dumps(quality, ensure_ascii=False),
            DRAFT,
            new_version,
            row_count,
            now,
            existing.id,
        ),
    )
    conn.commit()
    return get_by_id(conn, existing.id)  # type: ignore[return-value]


def transition_status(
    conn: sqlite3.Connection, cur_id: str, target: str
) -> CuratedRow | None:
    row = get_by_id(conn, cur_id)
    if row is None:
        return None
    assert_transition(row.status, target)
    if target not in ALL_STATUSES:
        raise ValueError(f"target 非法: {target}")
    conn.execute(
        "UPDATE curated_datasets SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), cur_id),
    )
    conn.commit()
    return get_by_id(conn, cur_id)


def _row_to_dict(row: CuratedRow) -> dict:
    return {
        "id": row.id,
        "dataset_id": row.dataset_id,
        "quality": row.quality_json,
        "status": row.status,
        "version": row.version,
        "row_count": row.row_count,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


row_to_dict = _row_to_dict  # 公开别名，供 API 层使用
