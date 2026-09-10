#!/usr/bin/env python
"""Build data/fortune_mirror.duckdb — a DuckDB mirror of the Fortune Plaza DWS warehouse.

Parses the two HUAWEI-DWS (PG-flavored) DDL dumps, converts types to DuckDB,
and creates all 22 tables under their original schemas (ods / cdm / rec).
Rerunnable: drops and recreates the database file every run.

Usage: .venv/bin/python scripts/fortune_mock/build_mirror.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[2]
DDL_DIR = REPO / "materials" / "fortune-warehouse-input" / "2026-09-10-数仓ddl及脚本"
DDL_FILES = ["crt_tab_ddl.sql", "crt_tab_ddl002.sql"]
DB_PATH = REPO / "data" / "fortune_mirror.duckdb"

RE_SEARCH_PATH = re.compile(r"(?im)^SET\s+search_path\s*=\s*([a-z_]+)\s*;")
RE_CREATE = re.compile(r"(?is)CREATE\s+TABLE\s+([a-z_0-9]+)\s*\((.*?)\)\s*WITH\b")
RE_COL = re.compile(r"^([a-z_0-9]+)\s+(.+)$", re.I)
RE_COMMENT_TABLE = re.compile(r"(?im)^COMMENT\s+ON\s+TABLE\s+([a-z_0-9]+)\s+IS\s+'((?:[^']|'')*)'\s*;")
RE_COMMENT_COLUMN = re.compile(
    r"(?im)^COMMENT\s+ON\s+COLUMN\s+([a-z_0-9]+)\.([a-z_0-9]+)\s+IS\s+'((?:[^']|'')*)'\s*;"
)

# PG/DWS -> DuckDB type mapping (only the types that appear in these dumps).
TYPE_MAP = [
    # (regex on normalized lower-case type, duckdb type)
    (r"^character varying(\s*\(\s*\d+\s*\))?$", "VARCHAR"),
    (r"^varchar(\s*\(\s*\d+\s*\))?$", "VARCHAR"),
    (r"^text$", "VARCHAR"),
    (r"^character(\s*\(\s*\d+\s*\))?$", "VARCHAR"),
    (r"^timestamp(\s*\(\s*\d+\s*\))?\s+without\s+time(\s+zone)?$", "TIMESTAMP"),
    (r"^timestamp(\s*\(\s*\d+\s*\))?$", "TIMESTAMP"),
    (r"^timestamp with(time\s+)?zone$", "TIMESTAMP"),
    (r"^date$", "DATE"),
    (r"^time(\s*\(\s*\d+\s*\))?\s+without\s+time(\s+zone)?$", "TIME"),
    (r"^bigint$", "BIGINT"),
    (r"^integer$", "INTEGER"),
    (r"^smallint$", "SMALLINT"),
    (r"^numeric(\s*\(\s*\d+\s*,\s*\d+\s*\))?$", "DECIMAL"),
    (r"^number$", "DECIMAL"),
    (r"^decimal(\s*\(\s*\d+\s*,\s*\d+\s*\))?$", "DECIMAL"),
    (r"^double precision$", "DOUBLE"),
    (r"^real$", "FLOAT"),
    (r"^boolean$", "BOOLEAN"),
]


def to_duckdb_type(pg_type: str) -> str:
    t = " ".join(pg_type.split()).lower()
    for pattern, duck_type in TYPE_MAP:
        if re.match(pattern, t):
            return duck_type
    raise ValueError(f"unmapped DWS type: {pg_type!r}")


def split_top_level(body: str) -> list[str]:
    """Split a CREATE TABLE column body on commas not nested inside parens/quotes."""
    parts, cur, depth, in_str = [], [], 0, False
    for ch in body:
        if in_str:
            cur.append(ch)
            if ch == "'":
                in_str = False
            continue
        if ch == "'":
            in_str = True
            cur.append(ch)
        elif ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return parts


def parse_ddl_file(path: Path) -> dict[str, dict]:
    """Parse one DWS DDL dump into {table: {schema, columns, table_comment}}."""
    text = path.read_text(encoding="utf-8")
    schema_events = [(m.start(), m.group(1)) for m in RE_SEARCH_PATH.finditer(text)]
    tables: dict[str, dict] = {}

    for m in RE_CREATE.finditer(text):
        schema = None
        for pos, sch in schema_events:
            if pos < m.start():
                schema = sch
            else:
                break
        name, body = m.group(1), m.group(2)
        columns = []
        for raw in split_top_level(body):
            stmt = " ".join(raw.split())
            cm = RE_COL.match(stmt)
            if not cm:
                continue  # skip stray constraints; these dumps have none in-column
            col_name, col_type = cm.group(1).lower(), cm.group(2)
            columns.append([col_name, col_type, to_duckdb_type(col_type), None])
        tables[name] = {"schema": schema, "columns": columns, "table_comment": None}

    for m in RE_COMMENT_TABLE.finditer(text):
        if m.group(1) in tables:
            tables[m.group(1)]["table_comment"] = m.group(2).replace("''", "'")

    for m in RE_COMMENT_COLUMN.finditer(text):
        tbl, col = m.group(1), m.group(2).lower()
        if tbl in tables:
            for column in tables[tbl]["columns"]:
                if column[0] == col:
                    column[3] = m.group(3).replace("''", "'")
    return tables


def build() -> None:
    all_tables: dict[str, dict] = {}
    for fname in DDL_FILES:
        parsed = parse_ddl_file(DDL_DIR / fname)
        overlap = set(all_tables) & set(parsed)
        if overlap:
            raise SystemExit(f"duplicate table across DDL files: {sorted(overlap)}")
        all_tables.update(parsed)

    if DB_PATH.exists():
        DB_PATH.unlink()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    schemas = sorted({t["schema"] for t in all_tables.values()})
    for s in schemas:
        con.execute(f"CREATE SCHEMA {s}")

    for name, spec in all_tables.items():
        col_defs = ", ".join(f"{c[0]} {c[2]}" for c in spec["columns"])
        con.execute(f"CREATE TABLE {spec['schema']}.{name} ({col_defs})")
        for column in spec["columns"]:
            if column[3]:
                note = column[3].replace("'", "''")
                con.execute(
                    f"COMMENT ON COLUMN {spec['schema']}.{name}.{column[0]} IS '{note}'"
                )

    print(f"DB: {DB_PATH}")
    print(f"schemas: {', '.join(schemas)}")
    print(f"tables created: {len(all_tables)}\n")

    print(f"{'schema.table':<42}{'cols':>5}  table_comment")
    print("-" * 100)
    for name in sorted(all_tables, key=lambda n: (all_tables[n]["schema"], n)):
        spec = all_tables[name]
        print(
            f"{spec['schema'] + '.' + name:<42}{len(spec['columns']):>5}  "
            f"{spec['table_comment'] or ''}"
        )

    # verification: count tables actually present in the duckdb catalog
    (n_tables,) = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN "
        "('main','information_schema','pg_catalog')"
    ).fetchone()
    print(f"\nverified in duckdb catalog: {n_tables} tables")
    if n_tables != len(all_tables):
        raise SystemExit("mirror table count mismatch")
    con.close()


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}", file=sys.stderr)
        raise
