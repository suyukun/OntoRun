"""重评估：对已存 SQL/契约用修正后 GT + 容差重新执行与比对（不烧 LLM）。

修正项：T6 季度 GT 整数格式；数值容差 1e-4 -> 5e-3（吸收显示舍入，仍抓住真实错误）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.headtohead.questions import BY_ID, QUESTIONS
from scripts.headtohead.runner import compare_answer, exec_a, guard_sql
from src.des.contract import ContractError, ContractExecutor, PermissionContext
from src.des.materialize import materialize_des
from src.des.metrics import load_metrics
from src.ontology import build_registry

RESULTS = HERE / "results.json"
GT_FILE = HERE / "gt_results.json"


def _clean(v):
    if isinstance(v, float):
        return round(v, 6)
    return v


def main() -> None:
    gt = json.loads(GT_FILE.read_text(encoding="utf-8"))
    for q in QUESTIONS:
        q["_gt_rows"] = [[_clean(v) for v in r] for r in gt[q["id"]]["rows"]]
        q["gt_cols"] = gt[q["id"]]["cols"]

    reg = build_registry()
    mz = materialize_des("hc_precision", registry=reg)
    metrics = load_metrics(config=mz.config)
    executor = ContractExecutor(mz, reg, metrics=metrics, permission_ctx=PermissionContext.allow_all())

    state = json.loads(RESULTS.read_text(encoding="utf-8"))
    changed = []
    for r in state["runs"]:
        q = BY_ID[r["qid"]]
        if r["form"] == "A":
            sql = r.get("sql")
            if not sql:
                continue  # LLM 失败/输出无效，保持原样
            v = guard_sql(sql)
            if v:
                r["outcome"] = "refusal"
                r["detail"] = "守卫拒答: " + "; ".join(v)
                r["exec_ms"] = None
                changed.append(r["qid"])
                continue
            rows, errs, ms = exec_a(sql)
            r["exec_ms"] = round(ms, 1)
            if errs:
                r["outcome"] = "error" if "执行错误" in errs[0] else "refusal"
                r["detail"] = "; ".join(errs)
                changed.append(r["qid"])
                continue
            ok, reason = compare_answer(q, rows)
            r["outcome"] = "correct" if ok else "wrong"
            r["detail"] = "" if ok else reason
            changed.append(r["qid"])
        else:  # B
            contract = r.get("contract")
            if not contract or r.get("outcome") == "refusal":
                continue  # LLM 拒答 或 无契约
            try:
                res = executor.execute(contract)
            except ContractError as e:
                r["outcome"] = "refusal"
                r["detail"] = f"校验/执行拒答(fail-closed): {str(e)[:200]}"
                changed.append(r["qid"])
                continue
            except Exception as e:  # noqa: BLE001 — 契约执行异常如实记录
                r["outcome"] = "error"
                r["detail"] = f"执行异常: {repr(e)[:200]}"
                changed.append(r["qid"])
                continue
            ok, reason = compare_answer(q, res, form="B")
            r["outcome"] = "correct" if ok else "wrong"
            r["detail"] = "" if ok else reason
            changed.append(r["qid"])

    RESULTS.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    mz.duckdb.close()
    from collections import Counter
    print("re-eval changed qids:", sorted(set(changed)))
    print("A:", Counter(r["outcome"] for r in state["runs"] if r["form"] == "A"))
    print("B:", Counter(r["outcome"] for r in state["runs"] if r["form"] == "B"))


if __name__ == "__main__":
    main()
