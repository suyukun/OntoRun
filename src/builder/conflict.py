"""冲突检测（重写蓝图 v0.3 / 补丁 A1）。

独立模块：检测 builder 表行与内置 OBJECT_TYPES / LINK_TYPES 是否同名。
返回 issue 列表（dict），由 main.py / API 层聚合。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.ontology.links import LINK_TYPES
from src.ontology.objects import OBJECT_TYPES


def check_object_type_name_conflict(
    conn: sqlite3.Connection, name: str
) -> dict[str, str] | None:
    """检查 name 是否与内置 OBJECT_TYPES 之一同名。是则返回 issue dict，否则 None。"""
    builtin = {o.name for o in OBJECT_TYPES}
    if name in builtin:
        return {
            "code": "BUILDER_NAME_CONFLICT",
            "severity": "error",
            "message": f"object_type 名 {name!r} 与内置类型同名，拒绝 publish",
        }
    return None


def check_link_type_name_conflict(
    conn: sqlite3.Connection, name: str
) -> dict[str, str] | None:
    builtin = {l.name for l in LINK_TYPES}
    if name in builtin:
        return {
            "code": "BUILDER_NAME_CONFLICT",
            "severity": "error",
            "message": f"link_type 名 {name!r} 与内置链接同名，拒绝 publish",
        }
    return None


def scan_all_published(ontology_db_path: str | Path) -> list[dict[str, str]]:
    """扫整库：列出所有与内置同名的 published 行（运维/迁移用）。"""
    conn = sqlite3.connect(ontology_db_path)
    conn.row_factory = sqlite3.Row
    issues: list[dict[str, str]] = []
    try:
        rows = conn.execute(
            "SELECT name FROM object_types WHERE status='published'"
        ).fetchall()
        for r in rows:
            i = check_object_type_name_conflict(conn, r["name"])
            if i:
                issues.append(i)
        rows = conn.execute(
            "SELECT name FROM link_types WHERE status='published'"
        ).fetchall()
        for r in rows:
            i = check_link_type_name_conflict(conn, r["name"])
            if i:
                issues.append(i)
    finally:
        conn.close()
    return issues
