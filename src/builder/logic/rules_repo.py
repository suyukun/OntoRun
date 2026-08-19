"""logic_rules 表仓储（蓝图 v0.3 §4 / P4-T1）。

行结构：id/ontology_id/name/logic_type(state_machine|precondition|threshold|
invariant)/expression(JSON 结构化可机器执行)/severity(info|warning|error|fatal)/
status(draft->reviewed->published)。

状态流转复用 src.builder.status_machine（E4）；非法流转抛
IllegalTransitionError，API 层映射 BUILDER_INVALID_STATUS_TRANSITION(4xx)。
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.builder.status_machine import (
    ALL_STATUSES,
    DRAFT,
    assert_transition,
)

LOGIC_TYPES: tuple[str, ...] = (
    "state_machine",
    "precondition",
    "threshold",
    "invariant",
)
SEVERITIES: tuple[str, ...] = ("info", "warning", "error", "fatal")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"lr_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class LogicRuleRow:
    """logic_rules 表行（frozen；更新返回新对象）。"""

    id: str
    ontology_id: str
    name: str
    logic_type: str
    expression: dict
    severity: str
    status: str
    created_at: str
    updated_at: str


def _load_json(raw, default):
    if raw is None:
        return default
    if isinstance(raw, (str, bytes, bytearray)):
        return json.loads(raw) if raw else default
    if isinstance(raw, dict):
        return raw
    return default


def _row_factory(row: sqlite3.Row) -> LogicRuleRow:
    return LogicRuleRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        logic_type=row["logic_type"],
        expression=_load_json(row["expression_json"], {}),
        severity=row["severity"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ----------------------------------------------------------------------
# CRUD
# ----------------------------------------------------------------------


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    logic_type: str,
    expression: dict,
    severity: str,
) -> LogicRuleRow:
    """建一条 draft 行（discovery 产出；severity/logic_type 越界由调用方校验）。"""
    if logic_type not in LOGIC_TYPES:
        raise ValueError(f"logic_type 非法: {logic_type}")
    if severity not in SEVERITIES:
        raise ValueError(f"severity 非法: {severity}")
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO logic_rules (id, ontology_id, name, logic_type, "
        "expression_json, severity, status, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            logic_type,
            json.dumps(expression, ensure_ascii=False),
            severity,
            DRAFT,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def get(conn: sqlite3.Connection, rule_id: str) -> LogicRuleRow | None:
    row = conn.execute("SELECT * FROM logic_rules WHERE id = ?", (rule_id,)).fetchone()
    return _row_factory(row) if row else None


def get_by_name(conn: sqlite3.Connection, name: str) -> LogicRuleRow | None:
    """按规则名取最近一条（discovery 生成的 name 语义唯一，重复发现幂等跳过）。"""
    row = conn.execute(
        "SELECT * FROM logic_rules WHERE name = ? ORDER BY created_at DESC LIMIT 1",
        (name,),
    ).fetchone()
    return _row_factory(row) if row else None


def resolve(conn: sqlite3.Connection, ref: str) -> LogicRuleRow | None:
    """id 优先、name 兜底（与 P3 get_extraction 的解析约定一致）。"""
    row = get(conn, ref)
    if row is not None:
        return row
    return get_by_name(conn, ref)


def list_all(
    conn: sqlite3.Connection,
    *,
    logic_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[LogicRuleRow], int]:
    where: list[str] = []
    params: list = []
    if logic_type:
        where.append("logic_type = ?")
        params.append(logic_type)
    if severity:
        where.append("severity = ?")
        params.append(severity)
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM logic_rules {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM logic_rules {where_sql} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def list_published(conn: sqlite3.Connection) -> list[LogicRuleRow]:
    rows = conn.execute(
        "SELECT * FROM logic_rules WHERE status = 'published' ORDER BY name"
    ).fetchall()
    return [_row_factory(r) for r in rows]


def find_same_expression(
    conn: sqlite3.Connection, name: str, expression: dict
) -> LogicRuleRow | None:
    """同名同 expression 的既有规则（任意状态）：discovery 幂等去重锚点。"""
    row = get_by_name(conn, name)
    if row is not None and row.expression == expression:
        return row
    return None


def transition_status(
    conn: sqlite3.Connection, rule_id: str, target: str
) -> LogicRuleRow | None:
    """流转状态（draft->reviewed->published）；非法流转抛 IllegalTransitionError。"""
    row = get(conn, rule_id)
    if row is None:
        return None
    assert_transition(row.status, target)
    if target not in ALL_STATUSES:
        raise ValueError(f"target 非法: {target}")
    conn.execute(
        "UPDATE logic_rules SET status = ?, updated_at = ? WHERE id = ?",
        (target, _now(), rule_id),
    )
    conn.commit()
    return get(conn, rule_id)


def row_to_dict(row: LogicRuleRow) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "logic_type": row.logic_type,
        "expression": row.expression,
        "severity": row.severity,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


__all__ = [
    "LOGIC_TYPES",
    "SEVERITIES",
    "LogicRuleRow",
    "create",
    "find_same_expression",
    "get",
    "get_by_name",
    "list_all",
    "list_published",
    "resolve",
    "row_to_dict",
    "transition_status",
]
