"""datasets 仓储（蓝图 v0.3 §9-P2 / §3 datasets 表）。

P2 范围：datasets 表 CRUD + 文件路径管理（uploads 目录）。
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.builder.status_machine import (
    ALL_STATUSES as _IGNORE,  # noqa: F401  # 状态集复用 builder 全局
)

ALLOWED_KINDS: tuple[str, ...] = ("csv", "excel", "json", "md", "pdf", "docx")
ALLOWED_STATUSES: tuple[str, ...] = ("uploaded", "ingested", "failed")


@dataclass(frozen=True)
class DatasetRow:
    id: str
    ontology_id: str
    name: str
    kind: str
    status: str
    row_count: int
    schema_json: dict
    source_path: str
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"ds_{uuid.uuid4().hex[:12]}"


def _row_factory(row: sqlite3.Row) -> DatasetRow:
    raw = row["schema_json"]
    if isinstance(raw, (str, bytes, bytearray)):
        parsed: dict = json.loads(raw) if raw else {}
    elif isinstance(raw, dict):
        parsed = raw
    else:
        parsed = {}
    return DatasetRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        kind=row["kind"],
        status=row["status"],
        row_count=row["row_count"],
        schema_json=parsed,
        source_path=row["source_path"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    kind: str,
    source_path: str,
    status: str = "uploaded",
    row_count: int = 0,
    schema_json: dict | None = None,
) -> DatasetRow:
    """建一条 dataset 行。"""
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"kind 非法: {kind}，应为 {ALLOWED_KINDS}")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"status 非法: {status}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO datasets (id, ontology_id, name, kind, status, row_count, "
        "schema_json, source_path, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            kind,
            status,
            row_count,
            json.dumps(schema_json or {}, ensure_ascii=False),
            source_path,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, ds_id: str) -> DatasetRow | None:
    row = conn.execute("SELECT * FROM datasets WHERE id = ?", (ds_id,)).fetchone()
    return _row_factory(row) if row else None


def get_by_name(conn: sqlite3.Connection, name: str) -> DatasetRow | None:
    row = conn.execute(
        "SELECT * FROM datasets WHERE name = ? ORDER BY created_at DESC LIMIT 1",
        (name,),
    ).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    kind: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DatasetRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if kind:
        where.append("kind = ?")
        params.append(kind)
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM datasets {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM datasets {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def update_status(
    conn: sqlite3.Connection, ds_id: str, status: str, row_count: int | None = None
) -> DatasetRow | None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"status 非法: {status}")
    row = get(conn, ds_id)
    if row is None:
        return None
    if row_count is None:
        conn.execute(
            "UPDATE datasets SET status = ?, updated_at = ? WHERE id = ?",
            (status, _now(), ds_id),
        )
    else:
        conn.execute(
            "UPDATE datasets SET status = ?, row_count = ?, updated_at = ? WHERE id = ?",
            (status, row_count, _now(), ds_id),
        )
    conn.commit()
    return get(conn, ds_id)


def update_schema(
    conn: sqlite3.Connection, ds_id: str, schema_json: dict
) -> DatasetRow | None:
    conn.execute(
        "UPDATE datasets SET schema_json = ?, updated_at = ? WHERE id = ?",
        (json.dumps(schema_json, ensure_ascii=False), _now(), ds_id),
    )
    conn.commit()
    return get(conn, ds_id)


def row_to_dict(row: DatasetRow) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "kind": row.kind,
        "status": row.status,
        "row_count": row.row_count,
        "schema": row.schema_json,
        "source_path": row.source_path,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


# ----------------------------------------------------------------------
# 文件路径辅助：uploads 目录默认在 data/builder_uploads/，可被覆盖
# ----------------------------------------------------------------------

DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "builder_uploads"


def upload_path(upload_dir: Path, name: str, suffix: str) -> Path:
    """生成唯一上传路径：{upload_dir}/{name}{suffix}，避免覆盖。"""
    upload_dir.mkdir(parents=True, exist_ok=True)
    base = upload_dir / f"{name}{suffix}"
    if not base.exists():
        return base
    # 冲突：加 _2 / _3 ...
    i = 2
    while True:
        cand = upload_dir / f"{name}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1
