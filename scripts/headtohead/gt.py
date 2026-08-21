"""Ground truth：对 30 问用确定 SQL 从 1M 行 demo 库算出期望答案（设计任务 1）。

只读：DuckDB sqlite_scan 直读 5 源库，不写任何源库/物化库。
输出：scripts/headtohead/gt_results.json（问题 id -> 期望答案 + 元信息）。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.headtohead.questions import BY_ID

ENTERPRISE = "hc_precision"
D = ROOT / "data" / "des" / "enterprises" / ENTERPRISE


def run_gt() -> dict:
    con = duckdb.connect()
    con.execute("LOAD sqlite")
    out: dict = {}
    t0 = time.time()
    for qid, q in BY_ID.items():
        sql = q["gt_sql"].format(D=str(D))
        t1 = time.time()
        rows = con.execute(sql).fetchall()
        dt = (time.time() - t1) * 1000
        # 归一化为 list[list]
        cols = [d[0] for d in con.description]
        norm = [[_clean(v) for v in r] for r in rows]
        out[qid] = {
            "cols": cols,
            "kind": q["kind"],
            "key_idx": q.get("key_idx", []),
            "val_idx": q.get("val_idx", []),
            "rows": norm,
            "row_count": len(rows),
            "ms": round(dt, 1),
        }
    con.close()
    out["_meta"] = {"n": len(BY_ID), "total_ms": round((time.time() - t0) * 1000, 1)}
    return out


def _clean(v):
    if isinstance(v, float):
        return round(v, 6)
    return v


def main() -> None:
    res = run_gt()
    dest = HERE / "gt_results.json"
    dest.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"GT computed for {len(res)-1} questions -> {dest}")
    for qid, r in sorted(res.items()):
        if qid == "_meta":
            continue
        print(f"  {qid}: {r['row_count']} rows, {r['ms']}ms, cols={r['cols']}")


if __name__ == "__main__":
    main()
