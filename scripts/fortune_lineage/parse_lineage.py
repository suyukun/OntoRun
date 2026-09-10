#!/usr/bin/env python
"""Table-level lineage extraction for archived Fortune warehouse ETL scripts (POC).

Pipeline: read .sql file -> substitute the scheduling variable (the quoted
'data_ds' literal) -> extract table-level lineage (source tables -> target
table) with sqllineage.

Dialect: postgres (closest to the DWS / GaussDB flavour these scripts use).
DWS-only temp-table DDL options 'WITH (...) DISTRIBUTE BY HASH (...)' are
stripped before parsing when the raw script is unparsable; such in-script
temporary tables are reported separately and excluded from the final
sources/targets.
"""

import argparse
import re
import sys
from pathlib import Path

from sqllineage.exceptions import InvalidSyntaxException
from sqllineage.runner import LineageRunner

DATA_DS_PLACEHOLDER = "'$" + "{data_ds}'"
SUBSTITUTION_VALUE = "2026-08-25"
DEFAULT_DIALECT = "postgres"

# DWS-only clauses that follow a CREATE ... TABLE column list and that neither
# the ansi nor the postgres parser accepts: WITH (...options...) DISTRIBUTE BY HASH (col)
DWS_DDL_TAIL_RE = re.compile(
    r"WITH\s*\([^)]*\)\s*DISTRIBUTE\s+BY\s+HASH\s*\([^)]*\)",
    re.IGNORECASE,
)

# In-script temporary tables (created via CREATE [LOCAL|GLOBAL] TEMP[ORARY] TABLE).
CREATE_TEMP_TABLE_RE = re.compile(
    r"CREATE\s+(?:LOCAL\s+|GLOBAL\s+)?TEMP(?:ORARY)?\s+TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][\w.$]*)",
    re.IGNORECASE,
)


def load_sql(path: Path) -> str:
    """Read a .sql file and substitute the scheduler variable placeholder."""
    text = path.read_text(encoding="utf-8")
    return text.replace(DATA_DS_PLACEHOLDER, "'" + SUBSTITUTION_VALUE + "'")


def find_temp_tables(sql: str) -> set:
    """Names of temporary tables created inside the script (lowercased)."""
    return {m.group(1).lower() for m in CREATE_TEMP_TABLE_RE.finditer(sql)}


def _simple_name(qualified: str) -> str:
    """'cdm.t' or '<default>.t' -> short lowercased name for temp-table matching."""
    return qualified.split(".")[-1].lower()


def extract_lineage(sql: str, dialect: str = DEFAULT_DIALECT) -> dict:
    """Return {sources, targets, temp_tables, preprocessed} for one script."""
    preprocessed = False
    try:
        runner = LineageRunner(sql, dialect=dialect)
        _ = runner.source_tables  # property access forces the lazy parse here
    except InvalidSyntaxException:
        # Workaround (attempt 1): drop DWS-only DDL tail clauses, keep everything else.
        stripped = DWS_DDL_TAIL_RE.sub("", sql)
        runner = LineageRunner(stripped, dialect=dialect)
        preprocessed = True

    temp_tables = find_temp_tables(sql)
    sources = sorted(
        str(t) for t in runner.source_tables if _simple_name(str(t)) not in temp_tables
    )
    targets = sorted(
        str(t) for t in runner.target_tables if _simple_name(str(t)) not in temp_tables
    )
    return {
        "sources": sources,
        "targets": targets,
        "temp_tables": sorted(temp_tables),
        "preprocessed": preprocessed,
    }


def print_report(label: str, result: dict) -> None:
    print(f"== {label}")
    print("target: " + (", ".join(result["targets"]) or "<none>"))
    print("sources:")
    for s in result["sources"]:
        print(f"  - {s}")
    if result["temp_tables"]:
        print(
            "(in-script temp tables excluded: " + ", ".join(result["temp_tables"]) + ")"
        )
    if result["preprocessed"]:
        print("(preprocessed: stripped DWS WITH(...)/DISTRIBUTE BY HASH DDL clauses)")
    print(
        "lineage: "
        + " + ".join(result["sources"])
        + " -> "
        + (", ".join(result["targets"]) or "<none>")
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_files", nargs="+", type=Path, help=".sql ETL script paths")
    parser.add_argument(
        "--dialect",
        default=DEFAULT_DIALECT,
        help="sqllineage dialect (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.sql_files:
        if not path.is_file():
            print(f"== {path}", file=sys.stderr)
            print("ERROR: file not found", file=sys.stderr)
            failed = True
            continue
        try:
            sql = load_sql(path)
            result = extract_lineage(sql, dialect=args.dialect)
        except Exception as exc:  # noqa: BLE001 - report any failure honestly, no fabrication
            print(f"== {path}", file=sys.stderr)
            print(f"PARSE FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
            failed = True
            continue
        print_report(str(path), result)
        print()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
