#!/usr/bin/env python
"""Full-run table-level lineage extraction for all Fortune warehouse ETL scripts.

Reuses the POC-proven pipeline in parse_lineage.py: substitute the scheduler
variable -> (postgres) parse -> on unparsable SQL strip DWS-only DDL tail
clauses -> retry -> exclude in-script CREATE TEMPORARY tables.

Authorised extra fallback (keeps total workarounds within the POC discipline):
the date-dimension script is Hive-flavoured (INSERT OVERWRITE ... PARTITION),
so dialect=hive is tried after the postgres chain.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parse_lineage import (
    _simple_name,
    find_temp_tables,
    load_sql,
)
from sqllineage.exceptions import InvalidSyntaxException
from sqllineage.runner import LineageRunner

BASE = Path("materials/fortune-warehouse-input/2026-09-10-数仓ddl及脚本")
SCRIPT_DIR = BASE / "01_财富管理脚本"
EXTRA_SCRIPTS = [BASE / "脚本dim_pb_date_yf.sql", BASE / "脚本dwd_lm_pv_df.sql"]
OUTPUT_JSON = Path(__file__).parent / "lineage_edges.json"

# Same strip idea as parse_lineage.DWS_DDL_TAIL_RE, extended to also cover the
# 'ON COMMIT DELETE ROWS' form that precedes DISTRIBUTE BY HASH in
# dim_ch_chl_df.sql (no WITH(...) options block there).
FULL_DWS_TAIL_RE = re.compile(
    r"(?:WITH\s*\([^)]*\)\s*)?(?:ON\s+COMMIT\s+(?:DELETE|PRESERVE)\s+ROWS\s*)?"
    r"DISTRIBUTE\s+BY\s+HASH\s*\([^)]*\)",
    re.IGNORECASE,
)

# (dialect, strip_dws_tail) attempt chain; first success wins.
ATTEMPT_CHAIN = [
    ("postgres", False),
    ("postgres", True),
    ("hive", False),
    ("hive", True),
]


def extract_lineage_full(sql: str) -> dict:
    """POC pipeline + authorised fallbacks. Raises the last InvalidSyntaxException
    (with the attempt log attached) when every attempt fails."""
    failures = []
    for dialect, strip in ATTEMPT_CHAIN:
        text = FULL_DWS_TAIL_RE.sub("", sql) if strip else sql
        try:
            runner = LineageRunner(text, dialect=dialect)
            _ = runner.source_tables  # property access forces the lazy parse here
        except InvalidSyntaxException as exc:
            failures.append(
                f"{dialect}{'+strip' if strip else ''}: {type(exc).__name__}"
            )
            continue
        temp_tables = find_temp_tables(sql)
        return {
            "sources": sorted(
                str(t)
                for t in runner.source_tables
                if _simple_name(str(t)) not in temp_tables
            ),
            "targets": sorted(
                str(t)
                for t in runner.target_tables
                if _simple_name(str(t)) not in temp_tables
            ),
            "temp_tables": sorted(temp_tables),
            "dialect": dialect,
            "stripped_dws_tail": strip,
            "attempts_failed": failures,
        }
    raise InvalidSyntaxException(
        "all parse attempts failed ["
        + "; ".join(failures)
        + "]: sql head = "
        + sql.strip()[:120].replace(chr(10), " ")
    )


def main() -> int:
    scripts = sorted(SCRIPT_DIR.rglob("*.sql")) + EXTRA_SCRIPTS
    edges = []
    failed = []
    print(f"scripts to parse: {len(scripts)}")
    for path in scripts:
        label = str(path.relative_to(BASE))
        try:
            sql = load_sql(path)
            result = extract_lineage_full(sql)
        except Exception as exc:  # noqa: BLE001 - report any failure honestly
            print(f"== {label}\n   PARSE FAILED: {type(exc).__name__}: {exc}")
            failed.append(label)
            continue
        note = ""
        if result["temp_tables"]:
            note += f" [temp excluded: {', '.join(result['temp_tables'])}]"
        if result["stripped_dws_tail"]:
            note += " [stripped DWS tail]"
        if result["dialect"] != "postgres":
            note += f" [dialect={result['dialect']}]"
        print(
            f"== {label}: {len(result['sources'])} sources -> {len(result['targets'])}"
            f" targets{note}"
        )
        for s in result["sources"]:
            print(f"     - {s}")
        for t in result["targets"]:
            print(f"     -> {t}")
        multi = len(result["targets"]) != 1
        if multi:
            print(
                "     NOTE: multi-target script; edges are source x target cross product"
            )
        for s in result["sources"]:
            for t in result["targets"]:
                edges.append({"source": s, "target": t, "via_script": label})

    OUTPUT_JSON.write_text(
        json.dumps(edges, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8"
    )
    tables = sorted({e["source"] for e in edges} | {e["target"] for e in edges})
    print()
    print(f"edges: {len(edges)}  tables: {len(tables)}  failed scripts: {len(failed)}")
    for f in failed:
        print("  FAILED:", f)
    print(f"json written: {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
