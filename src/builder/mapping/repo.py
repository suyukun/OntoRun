"""mappings 表仓储（蓝图 v0.3 §4 mappings / 补丁 v0.3.1）。

mappings 表结构（BUILDER_SCHEMA 已建）：
  id, ontology_id, entity_class, source_table,
  field_mapping_json (JSON 数组：每项 {column, property_name, is_technical, inferred_type, is_pk}),
  fk_mappings_json   (JSON 数组：每项 {link_id, source_field, target_field, target_table, cardinality, detection_method}),
  cardinalities_json (JSON dict: {link_id -> cardinality}),
  status (draft/reviewed/published) -- 与 object_types 同样的状态机
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.builder.status_machine import DRAFT, PUBLISHED, assert_transition


@dataclass(frozen=True)
class MappingRow:
    id: str
    ontology_id: str
    entity_class: str
    source_table: str
    field_mapping: list[dict]
    fk_mappings: list[dict]
    cardinalities: dict
    status: str
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"mp_{uuid.uuid4().hex[:12]}"


def _row_factory(row: sqlite3.Row) -> MappingRow:
    def _load_json(raw: Any, default: Any) -> Any:
        if raw is None:
            return default
        if isinstance(raw, (str, bytes, bytearray)):
            return json.loads(raw) if raw else default
        if isinstance(raw, (list, dict)):
            return raw
        return default
    return MappingRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        entity_class=row["entity_class"],
        source_table=row["source_table"],
        field_mapping=_load_json(row["field_mapping_json"], []),
        fk_mappings=_load_json(row["fk_mappings_json"], []),
        cardinalities=_load_json(row["cardinalities_json"], {}),
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    entity_class: str,
    source_table: str,
    field_mapping: list[dict],
    fk_mappings: list[dict] | None = None,
    cardinalities: dict | None = None,
    status: str = DRAFT,
    commit: bool = True,
) -> MappingRow:
    """落血缘行；commit=False 时由调用方在同一事务内批量提交（P2-7 发布血缘先落同事务）。"""
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO mappings (id, ontology_id, entity_class, source_table, "
        "field_mapping_json, fk_mappings_json, cardinalities_json, status, "
        "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            entity_class,
            source_table,
            json.dumps(field_mapping, ensure_ascii=False),
            json.dumps(fk_mappings or [], ensure_ascii=False),
            json.dumps(cardinalities or {}, ensure_ascii=False),
            status,
            now,
            now,
        ),
    )
    if commit:
        conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, mp_id: str) -> MappingRow | None:
    row = conn.execute("SELECT * FROM mappings WHERE id = ?", (mp_id,)).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    entity_class: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[MappingRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if entity_class:
        where.append("entity_class = ?")
        params.append(entity_class)
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM mappings {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM mappings {where_sql} ORDER BY created_at DESC "
        f"LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def transition_status(
    conn: sqlite3.Connection, mp_id: str, target: str
) -> MappingRow | None:
    row = get(conn, mp_id)
    if row is None:
        return None
    assert_transition(row.status, target)
    conn.execute(
        "UPDATE mappings SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), mp_id),
    )
    conn.commit()
    return get(conn, mp_id)


def row_to_dict(row: MappingRow) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "entity_class": row.entity_class,
        "source_table": row.source_table,
        "field_mapping": row.field_mapping,
        "fk_mappings": row.fk_mappings,
        "cardinalities": row.cardinalities,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


__all__ = [
    "DRAFT",
    "PUBLISHED",
    "MappingRow",
    "create",
    "get",
    "list_all",
    "row_to_dict",
    "transition_status",
]
