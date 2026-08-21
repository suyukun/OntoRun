"""拒答率>0 的 fail-closed 演示（独立于 30 问主跑，不烧 LLM）：
A：注入式 SQL（多语句/DDL）被守卫拒答；B：非法契约（未知 metric / 注入值）被校验拒答。
输出：scripts/headtohead/negative_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.headtohead.runner import guard_sql
from src.des.contract import ContractError, ContractExecutor, PermissionContext
from src.des.materialize import materialize_des
from src.des.metrics import load_metrics
from src.ontology import build_registry


def main() -> None:
    out: dict = {"A": [], "B": []}

    # ---- A 形态守卫 fail-closed 演示（不执行，只验守卫）----
    a_cases = [
        ("注入多语句", "SELECT * FROM MARA; DROP TABLE MARA"),
        ("注入注释逃逸", "SELECT * FROM MARA WHERE MATNR='x' --' OR 1=1"),
        ("写库 DML", "DELETE FROM MARA WHERE MATNR='MAT-2026-0001-K4V'"),
        ("非白名单表", "SELECT * FROM sys.sensitive"),
        ("外部数据源", "SELECT * FROM read_csv('/etc/passwd')"),
    ]
    for name, sql in a_cases:
        v = guard_sql(sql)
        out["A"].append({"name": name, "sql": sql, "rejected": bool(v), "violations": v})

    # ---- B 形态校验 fail-closed 演示 ----
    reg = build_registry()
    mz = materialize_des("hc_precision", registry=reg)
    metrics = load_metrics(config=mz.config)
    ex = ContractExecutor(mz, reg, metrics=metrics, permission_ctx=PermissionContext.allow_all())
    b_cases = [
        ("未知 metric_id", {"contract_version": "0.2", "metric": {"metric_id": "not_a_metric"}}),
        ("未知对象（V1 白名单）", {"contract_version": "0.1", "object_type": "FooObject", "filters": {}, "aggregations": [], "group_by": [], "link_traversal": None}),
        ("已注册对象但源表未接线（fail-closed）", {"contract_version": "0.1", "object_type": "Vendor", "filters": {}, "aggregations": [{"function": "count", "field": "*"}], "group_by": [], "link_traversal": None}),
        ("非 metric 契约带 time_range（P2-2 fail-closed）", {"contract_version": "0.1", "object_type": "Material", "filters": {}, "aggregations": [], "group_by": [], "link_traversal": None, "time_range": {"from": "2026-01-01", "to": "2026-01-31"}}),
        ("维度过滤值注入", {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month", "dimension_filters": {"matnr": {"op": "eq", "value": "MAT-2026-0001-K4V'; DROP TABLE x--"}}}}),
        ("time_range 非法", {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month", "time_range": {"from": "2026-02-01", "to": "2026-01-01"}}}),
    ]
    for name, c in b_cases:
        try:
            ex.execute(c)
            rejected = False
            violations = "未拒答（不应发生）"
        except ContractError as e:
            rejected = True
            violations = str(e)[:180]
        out["B"].append({"name": name, "contract": c, "rejected": rejected, "violations": violations})
    mz.duckdb.close()

    dest = HERE / "negative_results.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
