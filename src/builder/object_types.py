"""object_types 仓储。

直接 SQL 操作本体库 object_types 表；返回 dataclass / dict 给 API 层组装信封。
状态流转由 src.builder.status_machine 校验。
"""

from __future__ import annotations

import json
import re
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
class ObjectTypeRow:
    """object_types 表行（frozen；更新返回新对象）。"""

    id: str
    ontology_id: str
    name: str
    name_cn: str
    description: str
    category: str
    property_schema: dict
    status: str
    pk_field: str
    title_field: str
    source_table: str
    created_at: str
    updated_at: str

    @property
    def api_name(self) -> str:
        # snake_case 化：P2_Test_Customer -> p2_test_customer（修复 P2 bug：
        # 旧实现 "".join(...).lstrip('_') 会让已有下划线变成重复，如 P2_Test_Customer
        # -> p2__test__customer，被 P3 派生 link 名复用时撞名）。
        # 算法：先在 小写/数字 后跟 大写 的边界插下划线；再统一小写；最后 collapse 重复下划线。
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", self.name)
        s = s.lower()
        s = re.sub(r"_+", "_", s)
        return s.strip("_")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _row_factory(row: sqlite3.Row) -> ObjectTypeRow:
    raw_schema = row["property_schema"]
    if isinstance(raw_schema, (str, bytes, bytearray)):
        parsed: dict = json.loads(raw_schema) if raw_schema else {}
    elif isinstance(raw_schema, dict):
        parsed = raw_schema
    else:
        parsed = {}
    # pk_field / title_field / source_table 不在 BUILDER_SCHEMA（任务边界：不改 DDL）。
    # 派生规则：pk_field = property_schema.required 第一项；title_field = pk_field；
    # source_table 在 builder 阶段为空（构建产物只读，运行时零写回——补丁 A2）。
    pk_field = _derive_pk_field(parsed)
    title_field = pk_field
    return ObjectTypeRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        name_cn=row["name_cn"],
        description=row["description"],
        category=row["category"],
        property_schema=parsed,
        status=row["status"],
        pk_field=pk_field,
        title_field=title_field,
        source_table="",
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _derive_pk_field(schema: dict) -> str:
    required = schema.get("required") or []
    if isinstance(required, list) and required:
        return str(required[0])
    props = schema.get("properties") or {}
    if isinstance(props, dict) and props:
        return str(next(iter(props.keys())))
    return "id"


def _new_id() -> str:
    return f"ot_{uuid.uuid4().hex[:12]}"


# ----------------------------------------------------------------------
# CRUD
# ----------------------------------------------------------------------


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    name_cn: str,
    description: str,
    category: str,
    property_schema: dict,
) -> ObjectTypeRow:
    """建一条 draft 行。

    注意：pk_field / title_field / source_table 不在 BUILDER_SCHEMA（P1 任务边界
    不改 DDL），由 _row_factory 从 property_schema 派生（pk = required[0]，
    title = pk，source_table = ""；构建产物只读，运行时零写回——补丁 A2）。
    """
    if category not in {"domain", "artifact", "conceptual"}:
        raise ValueError(f"category 非法: {category}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO object_types (id, ontology_id, name, name_cn, description, "
        "category, property_schema, status, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            name_cn,
            description,
            category,
            json.dumps(property_schema, ensure_ascii=False),
            DRAFT,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, ot_id: str) -> ObjectTypeRow | None:
    row = conn.execute(
        "SELECT * FROM object_types WHERE id = ?", (ot_id,)
    ).fetchone()
    return _row_factory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    *,
    category: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ObjectTypeRow], int]:
    where: list[str] = []
    params: list[Any] = []
    if category:
        where.append("category = ?")
        params.append(category)
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM object_types {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM object_types {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def update(
    conn: sqlite3.Connection, ot_id: str, patch: dict[str, Any]
) -> ObjectTypeRow | None:
    """仅 draft 可改（status 字段走独立 transition 路径）。"""
    row = get(conn, ot_id)
    if row is None:
        return None
    if row.status != DRAFT:
        raise PermissionError(f"仅 draft 可改，当前 {row.status}")
    editable = {
        "name",
        "name_cn",
        "description",
        "category",
        "property_schema",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in patch.items():
        if k not in editable:
            continue
        if k == "property_schema" and isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        sets.append(f"{k} = ?")
        params.append(v)
    if not sets:
        return row
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(ot_id)
    conn.execute(
        f"UPDATE object_types SET {', '.join(sets)} WHERE id = ?", params
    )
    conn.commit()
    return get(conn, ot_id)


def delete(conn: sqlite3.Connection, ot_id: str) -> bool:
    row = get(conn, ot_id)
    if row is None:
        return False
    if row.status == PUBLISHED:
        raise PermissionError("published 不可删")
    conn.execute("DELETE FROM object_types WHERE id = ?", (ot_id,))
    conn.commit()
    return True


def transition_status(
    conn: sqlite3.Connection, ot_id: str, target: str
) -> ObjectTypeRow | None:
    """流转状态（draft->reviewed->published）。非法流转抛 IllegalTransitionError。"""
    row = get(conn, ot_id)
    if row is None:
        return None
    assert_transition(row.status, target)
    if target not in ALL_STATUSES:
        raise ValueError(f"target 非法: {target}")
    conn.execute(
        "UPDATE object_types SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), ot_id),
    )
    conn.commit()
    return get(conn, ot_id)


def list_published(conn: sqlite3.Connection) -> list[ObjectTypeRow]:
    rows = conn.execute(
        "SELECT * FROM object_types WHERE status = ? ORDER BY name",
        (PUBLISHED,),
    ).fetchall()
    return [_row_factory(r) for r in rows]
