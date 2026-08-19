"""pipelines 仓储（蓝图 v0.3 §9-P2 / §3 pipelines 表）。

P2 范围：pipelines 表 CRUD（DAG JSON 整体存）。
runs 状态走 in-memory（pipeline_runs 表不在 BUILDER_SCHEMA_V1 10 表内，
任务边界延续 P1；smoke 级用模块级 dict 即可）。
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

ALLOWED_STATUSES: tuple[str, ...] = ("draft", "active", "archived")


@dataclass(frozen=True)
class PipelineRow:
    id: str
    ontology_id: str
    name: str
    dag_json: dict
    status: str
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"pl_{uuid.uuid4().hex[:12]}"


def _row_factory(row: sqlite3.Row) -> PipelineRow:
    raw = row["dag_json"]
    if isinstance(raw, (str, bytes, bytearray)):
        parsed: dict = json.loads(raw) if raw else {}
    elif isinstance(raw, dict):
        parsed = raw
    else:
        parsed = {}
    return PipelineRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        dag_json=parsed,
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    dag_json: dict,
    status: str = "draft",
) -> PipelineRow:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"status 非法: {status}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO pipelines (id, ontology_id, name, dag_json, status, "
        "created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            json.dumps(dag_json, ensure_ascii=False),
            status,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, pl_id: str) -> PipelineRow | None:
    row = conn.execute(
        "SELECT * FROM pipelines WHERE id = ?", (pl_id,)
    ).fetchone()
    return _row_factory(row) if row else None


def get_by_name(conn: sqlite3.Connection, name: str) -> PipelineRow | None:
    row = conn.execute(
        "SELECT * FROM pipelines WHERE name = ? ORDER BY created_at DESC LIMIT 1",
        (name,),
    ).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PipelineRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM pipelines {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM pipelines {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def update(
    conn: sqlite3.Connection, pl_id: str, patch: dict[str, Any]
) -> PipelineRow | None:
    row = get(conn, pl_id)
    if row is None:
        return None
    editable = {"name", "dag_json", "status"}
    sets: list[str] = []
    params: list[Any] = []
    for k, v in patch.items():
        if k not in editable:
            continue
        if k == "dag_json" and isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        if k == "status" and v not in ALLOWED_STATUSES:
            raise ValueError(f"status 非法: {v}")
        sets.append(f"{k} = ?")
        params.append(v)
    if not sets:
        return row
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(pl_id)
    conn.execute(
        f"UPDATE pipelines SET {', '.join(sets)} WHERE id = ?", params
    )
    conn.commit()
    return get(conn, pl_id)


def delete(conn: sqlite3.Connection, pl_id: str) -> bool:
    row = get(conn, pl_id)
    if row is None:
        return False
    conn.execute("DELETE FROM pipelines WHERE id = ?", (pl_id,))
    conn.commit()
    return True


def row_to_dict(row: PipelineRow) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "dag_json": row.dag_json,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


# ----------------------------------------------------------------------
# In-memory runs（蓝图 §9-P2：POST /pipelines/{name}/run 同步执行）
# ----------------------------------------------------------------------


@dataclass
class PipelineRunRecord:
    """单次管道执行记录（in-memory）。"""

    run_id: str
    pipeline_id: str
    pipeline_name: str
    started_at: str
    finished_at: str | None
    final_status: str  # succeeded / failed / partial
    node_results: list[dict] = field(default_factory=list)
    curated_dataset_id: str | None = None
    error: str | None = None


# module-level：进程内全局
_RUNS: dict[str, list[PipelineRunRecord]] = {}


def record_run(rec: PipelineRunRecord) -> None:
    _RUNS.setdefault(rec.pipeline_name, []).append(rec)


def list_runs(pipeline_name: str) -> list[PipelineRunRecord]:
    return list(_RUNS.get(pipeline_name, []))


def clear_runs() -> None:
    """测试辅助：清空全局 runs。"""
    _RUNS.clear()
