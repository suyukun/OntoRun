"""link_types 仓储（重写蓝图 v0.3 §4 + §5）。

与 object_types 同构：直接 SQL、frozen dataclass、E4 状态机由 status_machine 校验。
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.builder.status_machine import (
    ALL_STATUSES,
    DRAFT,
    PUBLISHED,
    assert_transition,
)


@dataclass(frozen=True)
class LinkTypeRow:
    """link_types 表行。"""

    id: str
    ontology_id: str
    name: str
    semantic_name: str
    category: str
    source_type_id: str
    target_type_id: str
    cardinality: str
    fk_field: str
    status: str
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"lt_{uuid.uuid4().hex[:12]}"


def _row_factory(row: sqlite3.Row) -> LinkTypeRow:
    # fk_field 列在 P2 加入（store.migrate idempotent ALTER TABLE ADD COLUMN）。
    # 旧库可能缺列，SELECT * 报 KeyError — 用 try/except 兜底，保持向后兼容。
    fk_value = ""
    try:
        fk_value = row["fk_field"] or ""
    except (IndexError, KeyError):
        fk_value = ""
    return LinkTypeRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        semantic_name=row["semantic_name"] or "",
        category=row["category"],
        source_type_id=row["source_type_id"],
        target_type_id=row["target_type_id"],
        cardinality=row["cardinality"],
        fk_field=fk_value,
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    semantic_name: str,
    category: str,
    source_type_id: str,
    target_type_id: str,
    cardinality: str,
    fk_field: str = "",
) -> LinkTypeRow:
    """建一条 draft 行。fk_field 在 BUILDER_SCHEMA 中无对应列（任务边界不改 DDL），
    仅在 LinkTypeRow 上保留供 P2 映射 apply 阶段使用。
    """
    if category not in {"semantic", "fk_inferred", "structural"}:
        raise ValueError(f"link category 非法: {category}")
    if cardinality not in {"1:1", "1:N", "N:1", "N:M"}:
        raise ValueError(f"cardinality 非法: {cardinality}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO link_types (id, ontology_id, name, semantic_name, category, "
        "source_type_id, target_type_id, cardinality, fk_field, status, "
        "created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            semantic_name,
            category,
            source_type_id,
            target_type_id,
            cardinality,
            fk_field or "",
            DRAFT,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, lt_id: str) -> LinkTypeRow | None:
    row = conn.execute("SELECT * FROM link_types WHERE id = ?", (lt_id,)).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[LinkTypeRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM link_types {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM link_types {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def update(
    conn: sqlite3.Connection, lt_id: str, patch: dict[str, Any]
) -> LinkTypeRow | None:
    row = get(conn, lt_id)
    if row is None:
        return None
    if row.status != DRAFT:
        raise PermissionError(f"仅 draft 可改，当前 {row.status}")
    editable = {
        "name",
        "semantic_name",
        "category",
        "source_type_id",
        "target_type_id",
        "cardinality",
        "fk_field",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in patch.items():
        if k not in editable:
            continue
        sets.append(f"{k} = ?")
        params.append(v)
    if not sets:
        return row
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(lt_id)
    conn.execute(
        f"UPDATE link_types SET {', '.join(sets)} WHERE id = ?", params
    )
    conn.commit()
    return get(conn, lt_id)


def delete(conn: sqlite3.Connection, lt_id: str) -> bool:
    row = get(conn, lt_id)
    if row is None:
        return False
    if row.status == PUBLISHED:
        raise PermissionError("published 不可删")
    conn.execute("DELETE FROM link_types WHERE id = ?", (lt_id,))
    conn.commit()
    return True


def transition_status(
    conn: sqlite3.Connection, lt_id: str, target: str
) -> LinkTypeRow | None:
    row = get(conn, lt_id)
    if row is None:
        return None
    assert_transition(row.status, target)
    if target not in ALL_STATUSES:
        raise ValueError(f"target 非法: {target}")
    conn.execute(
        "UPDATE link_types SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), lt_id),
    )
    conn.commit()
    return get(conn, lt_id)


def list_published(conn: sqlite3.Connection) -> list[LinkTypeRow]:
    rows = conn.execute(
        "SELECT * FROM link_types WHERE status = ? ORDER BY name",
        (PUBLISHED,),
    ).fetchall()
    return [_row_factory(r) for r in rows]
