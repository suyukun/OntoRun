"""导出 S3 金控风险演示物化快照（web/public/risk-demo/risk-snapshot.json）。

用途：风险数据浏览页的演示数据源。数据从 ap_anping 真实库同源生成（非手写假数字），
对应演示剧本的「预热/物化缓存」设计：前端默认加载本快照，将来后端暴露
/objects/risk_* 端点后可切换为实时查询（web/src/risk/riskData.ts 已抽象数据层）。

快照内容：
- meta: 对象/链接/动作 schema（来自风险独立注册表 build_risk_source_registry，与后端同源）
- totals: 各对象真实总数
- items: 围绕演示锚点集团 + 处置/审批链路的连贯切片样本（真实行，确定性可再生成）
- edges: 切片内的真实链接边（真实外键/关联解析），保证「无孤岛」可遍历
- group_metrics: 锚点集团的维度指标摘要（真实聚合，来自 ap_dim_metric）

运行：/opt/anaconda3/bin/python scripts/export_risk_demo_snapshot.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.runtime.risk_db import (
    AP_ANPING_DIR,
    SOURCE_TABLE_MAP,
    build_risk_source_registry,
)

OUT = Path(__file__).resolve().parents[1] / "web" / "public" / "risk-demo" / "risk-snapshot.json"

# ---- 演示锚点集团（中科智造 + 各业态代表，跨银行/证券/租赁/制造等） ----
ANCHOR_GROUPS = [
    "GRP-2026-000001",  # 中科智造产业发展集团（演示主线）
    "GRP-2026-000002",
    "GRP-2026-000003",
    "GRP-2026-000004",
    "GRP-2026-000005",
    "GRP-2026-000006",
    "GRP-2026-000013",
    "GRP-2026-000015",
    "GRP-2026-000021",
    "GRP-2026-000023",
    "GRP-2026-000029",
    "GRP-2026-000061",
]

MAX_CUSTOMERS = 60
MAX_WARNINGS = 150
MAX_ORDERS = 15
MAX_TASKS = 25
MAX_CONCENTRATION = 14
MAX_PROJECTS = 15
MAX_METRICS = 60

_SIGNAL_ID_RE = re.compile(r"SGN-\d{4}-\d{8}")


class _DB:
    def __init__(self) -> None:
        self._conns: dict[str, sqlite3.Connection] = {}

    def conn(self, db: str) -> sqlite3.Connection:
        if db not in self._conns:
            conn = sqlite3.connect(str(AP_ANPING_DIR / f"{db}.db"))
            conn.row_factory = sqlite3.Row
            self._conns[db] = conn
        return self._conns[db]

    def rows(self, db: str, sql: str, args: Any = ()) -> list[dict]:
        return [dict(r) for r in self.conn(db).execute(sql, args).fetchall()]

    def close(self) -> None:
        for c in self._conns.values():
            c.close()


def _columns(db: _DB, dbname: str, table: str) -> set[str]:
    return {c[1] for c in db.conn(dbname).execute(f"PRAGMA table_info({table})").fetchall()}


def _to_arrow(table: str) -> tuple[str, str]:
    if "." in table:
        db, tbl = table.split(".", 1)
        return db, tbl
    return "risk", table


def build_meta() -> dict:
    reg = build_risk_source_registry()
    objects: list[dict] = []
    for o in reg.object_types():
        props = o.model.model_json_schema()["properties"]
        properties: dict[str, Any] = {}
        for name, p in props.items():
            entry: dict[str, Any] = {"title": p.get("description", name), "type": p.get("type", "string")}
            if "enum" in p:
                entry["enum"] = p["enum"]
            properties[name] = entry
        objects.append(
            {
                "name": o.name,
                "api_name": o.api_name,
                "description": o.description,
                "pk_field": o.pk_field,
                "title_field": o.title_field or o.pk_field,
                "source_table": o.source_table,
                "properties": properties,
            }
        )
    links = [l.model_dump() for l in reg.link_types()]
    actions: list[dict] = []
    for a in reg.actions():
        actions.append(
            {
                "name": a.name,
                "description": a.description,
                "high_risk": a.high_risk,
                "params_schema": a.params_model.model_json_schema(),
            }
        )
    return {"objects": objects, "links": links, "actions": actions}


def main() -> None:
    db = _DB()
    meta = build_meta()
    api_names = [o["api_name"] for o in meta["objects"]]
    items: dict[str, list[dict]] = {a: [] for a in api_names}
    totals: dict[str, int] = {}
    edges: list[dict] = []
    group_metrics: dict[str, list[dict]] = {}

    # ---- 总数（真实计数） ----
    for o in meta["objects"]:
        real = SOURCE_TABLE_MAP.get(o["name"])
        if not real:
            continue
        dbt, tbl = _to_arrow(real)
        totals[o["api_name"]] = db.rows(dbt, f"SELECT COUNT(*) c FROM {tbl}")[0]["c"]

    # ---- 锚点集团 ----
    groups = []
    for g in ANCHOR_GROUPS:
        rows = db.rows("customer", "SELECT * FROM ap_group_customer WHERE group_customer_no=?", (g,))
        if rows:
            groups.append(rows[0])
    groups.sort(key=lambda r: r["group_customer_no"])
    group_ids = {r["group_customer_no"] for r in groups}
    group_names = {r["group_customer_name"] for r in groups}

    # ---- 成员客户 ----
    customers: list[dict] = []
    seen_c = set()
    for g in groups:
        for r in db.rows(
            "customer",
            "SELECT * FROM ap_customer WHERE group_customer_no=? ORDER BY customer_id LIMIT 8",
            (g["group_customer_no"],),
        ):
            if r["customer_id"] not in seen_c and len(customers) < MAX_CUSTOMERS:
                seen_c.add(r["customer_id"])
                customers.append(r)
    customer_ids = {r["customer_id"] for r in customers}
    customer_nos = {r["customer_no"] for r in customers}
    cust_by_no = {r["customer_no"]: r["customer_id"] for r in customers}

    # ---- 预警样本：处置/审批链路种子优先 + 锚点（客户级 + 集团级）+ 近期红色 ----
    warnings: list[dict] = []
    seen_w = set()

    def add_warning(w: dict) -> None:
        if w["warning_id"] not in seen_w and len(warnings) < MAX_WARNINGS:
            seen_w.add(w["warning_id"])
            warnings.append(w)

    if customer_ids:
        for r in db.rows(
            "risk",
            "SELECT * FROM ap_warning_signal WHERE customer_id IN (%s) ORDER BY warning_id LIMIT %d"
            % (",".join("?" * len(customer_ids)), 3 * len(customer_ids)),
            tuple(customer_ids),
        ):
            add_warning(r)
    for g in groups:
        for r in db.rows(
            "risk",
            "SELECT * FROM ap_warning_signal WHERE group_customer_no=? ORDER BY warning_id LIMIT 4",
            (g["group_customer_no"],),
        ):
            add_warning(r)
    # 近期红色预警（让「本月红色预警」有样本可看）
    for r in db.rows(
        "risk",
        "SELECT * FROM ap_warning_signal WHERE warn_level='RED' AND signal_generate_date >= '2026-12-01' ORDER BY warning_id LIMIT 8",
    ):
        add_warning(r)

    # 链路种子：有处置 + 被审批单引用 的预警（打通 处置→审批 边）
    disp_warn_ids = {r["warning_id"] for r in db.rows("risk", "SELECT warning_id FROM ap_warning_disposal")}
    order_signal_ids = set()
    for r in db.rows("approval", "SELECT remark FROM ap_approve_order WHERE remark LIKE '%SGN-%'"):
        m = _SIGNAL_ID_RE.search(r.get("remark") or "")
        if m:
            order_signal_ids.add(m.group(0))
    if disp_warn_ids:
        for r in db.rows(
            "risk",
            "SELECT * FROM ap_warning_signal WHERE warning_id IN (%s) ORDER BY warning_id"
            % ",".join("?" * len(disp_warn_ids)),
            tuple(disp_warn_ids),
        ):
            if r.get("signal_id") in order_signal_ids:
                add_warning(r)
    warning_ids = {r["warning_id"] for r in warnings}
    signal_ids = {r["signal_id"] for r in warnings}

    # ---- 处置（含链路种子预警的处置） ----
    disposals = []
    if warning_ids:
        disposals = db.rows(
            "risk",
            "SELECT * FROM ap_warning_disposal WHERE warning_id IN (%s) ORDER BY disposal_id"
            % ",".join("?" * len(warning_ids)),
            tuple(warning_ids),
        )
    disposal_ids = {r["disposal_id"] for r in disposals}

    # ---- 审批单：优先「remark 关联到样本预警」 ----
    orders: list[dict] = []
    seen_o = set()
    all_orders = db.rows(
        "approval",
        "SELECT * FROM ap_approve_order WHERE remark LIKE '%SGN-%' ORDER BY approve_order_id",
    )
    linked_first = [
        r
        for r in all_orders
        if (m := _SIGNAL_ID_RE.search(r.get("remark") or "")) and m.group(0) in signal_ids
    ]
    for r in linked_first:
        if r["approve_order_id"] not in seen_o and len(orders) < MAX_ORDERS:
            seen_o.add(r["approve_order_id"])
            orders.append(r)
    if len(orders) < 6:
        for r in all_orders:
            if r["approve_order_id"] not in seen_o and len(orders) < MAX_ORDERS:
                seen_o.add(r["approve_order_id"])
                orders.append(r)
    orders.sort(key=lambda r: r["approve_order_id"])
    order_ids = {r["approve_order_id"] for r in orders}

    # ---- 审批任务 ----
    tasks = []
    if order_ids:
        tasks = db.rows(
            "approval",
            "SELECT * FROM ap_approve_task WHERE approve_order_id IN (%s) ORDER BY approve_task_id"
            % ",".join("?" * len(order_ids)),
            tuple(order_ids),
        )
        if len(tasks) > MAX_TASKS:
            tasks = tasks[:MAX_TASKS]

    # ---- 集中度限额 / 风险项目 / 维度指标 ----
    concentration = []
    if customer_nos:
        concentration = db.rows(
            "concentration",
            "SELECT * FROM ap_concentration_limit WHERE customer_no IN (%s) ORDER BY concentration_limit_id LIMIT %d"
            % (",".join("?" * len(customer_nos)), MAX_CONCENTRATION),
            tuple(customer_nos),
        )
    projects = []
    seen_p = set()
    marks = ",".join("?" * len(group_names))
    for r in db.rows(
        "project",
        "SELECT * FROM ap_risk_project WHERE group_customer_name IN (%s) ORDER BY risk_project_id LIMIT %d"
        % (marks, MAX_PROJECTS),
        tuple(sorted(group_names)),
    ):
        if r["risk_project_id"] not in seen_p:
            seen_p.add(r["risk_project_id"])
            projects.append(r)

    metrics = []
    seen_m = set()
    for g in groups:
        for r in db.rows(
            "base",
            "SELECT * FROM ap_dim_metric WHERE dim_type_name='集团客户' AND group_customer_no=? "
            "AND index_name IN ('风险暴露额','集团对外融资余额','集中度敞口占比','不良贷款率') "
            "ORDER BY index_id LIMIT 8",
            (g["group_customer_no"],),
        ):
            if r["dim_metric_id"] not in seen_m and len(metrics) < MAX_METRICS:
                seen_m.add(r["dim_metric_id"])
                metrics.append(r)
    if customer_nos:
        for r in db.rows(
            "base",
            "SELECT * FROM ap_dim_metric WHERE customer_no IN (%s) AND index_name IN ('风险暴露额','集中度敞口占比') ORDER BY dim_metric_id LIMIT 20"
            % ",".join("?" * len(customer_nos)),
            tuple(customer_nos),
        ):
            if r["dim_metric_id"] not in seen_m and len(metrics) < MAX_METRICS:
                seen_m.add(r["dim_metric_id"])
                metrics.append(r)
    metrics.sort(key=lambda r: r["dim_metric_id"])

    # ---- 组指标摘要（真实聚合） ----
    for g in groups:
        rows = db.rows(
            "base",
            "SELECT index_name, index_value, index_unit FROM ap_dim_metric "
            "WHERE dim_type_name='集团客户' AND group_customer_no=? "
            "AND index_name IN ('风险暴露额','集团对外融资余额','集中度敞口占比','不良贷款率') ORDER BY index_id",
            (g["group_customer_no"],),
        )
        if rows:
            group_metrics[g["group_customer_no"]] = rows

    # ---- 写入 items ----
    sample_src = {
        "RiskCustomer": customers,
        "GroupCustomer": groups,
        "WarningSignal": warnings,
        "Disposal": disposals,
        "ApproveOrder": orders,
        "ApproveTask": tasks,
        "ConcentrationLimit": concentration,
        "RiskProject": projects,
        "Metric": metrics,
    }
    for o in meta["objects"]:
        real = SOURCE_TABLE_MAP.get(o["name"])
        if not real:
            continue
        dbt, tbl = _to_arrow(real)
        cols = _columns(db, dbt, tbl)
        pk = o["pk_field"]
        rows = sample_src.get(o["name"])
        if rows is None:
            # 兜底采样：主线外对象也从真实表取样例行，保证前端 33 对象
            # 全部有点得开的数据（不空表）；属性仍按 cols 交集投影，
            # edges 不覆盖这些行（详情页已有「暂无关联」文案兜底）。
            rows = db.rows(dbt, f"SELECT * FROM {tbl} ORDER BY {pk} LIMIT 12")
        for r in rows:
            props = {}
            for f in o["properties"]:
                if f in cols and r.get(f) is not None:
                    props[f] = r[f]
            if o["name"] == "GroupCustomer":
                props["member_count"] = db.rows(
                    "customer", "SELECT COUNT(*) c FROM ap_customer WHERE group_customer_no=?", (r[pk],)
                )[0]["c"]
            items[o["api_name"]].append({"pk": str(r[pk]), "properties": props})
        items[o["api_name"]].sort(key=lambda x: x["pk"])

    # ---- edges ----
    def add(link: str, s: str, spk: str, t: str, tpk: str) -> None:
        edges.append({"source": s, "source_pk": spk, "link": link, "target": t, "target_pk": tpk})

    for c in customers:
        if c.get("group_customer_no") in group_ids:
            add("risk_customer.belongs_to_group", "risk_customer", c["customer_id"], "group_customer", c["group_customer_no"])
    for w in warnings:
        if w.get("customer_id") in customer_ids:
            add("warning.for_customer", "warning_signal", w["warning_id"], "risk_customer", w["customer_id"])
        if w.get("group_customer_no") in group_ids:
            add("warning.for_group", "warning_signal", w["warning_id"], "group_customer", w["group_customer_no"])
    for d in disposals:
        if d.get("warning_id") in warning_ids:
            add("disposal.for_warning", "disposal", d["disposal_id"], "warning_signal", d["warning_id"])
    for t in tasks:
        if t.get("approve_order_id") in order_ids:
            add("approve.has_tasks", "approve_order", t["approve_order_id"], "approve_task", t["approve_task_id"])
    for cc in concentration:
        cid = cust_by_no.get(cc.get("customer_no"))
        if cid:
            add("concentration.for_customer", "concentration_limit", cc["concentration_limit_id"], "risk_customer", cid)
    for m in metrics:
        cid = cust_by_no.get(m.get("customer_no"))
        if cid:
            add("metric.for_customer", "metric", m["dim_metric_id"], "risk_customer", cid)
    for p in projects:
        for g in groups:
            if g["group_customer_name"] == p.get("group_customer_name"):
                add("risk_project.for_group", "risk_project", p["risk_project_id"], "group_customer", g["group_customer_no"])
                break
    sig2warning = {w["signal_id"]: w["warning_id"] for w in warnings}
    for o in orders:
        m = _SIGNAL_ID_RE.search(o.get("remark") or "")
        if not m:
            continue
        wid = sig2warning.get(m.group(0))
        if not wid:
            continue
        for d in disposals:
            if d.get("warning_id") == wid:
                add("disposal.has_approval", "disposal", d["disposal_id"], "approve_order", o["approve_order_id"])
                break

    # ---- 序列化 ----
    import datetime

    payload = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "风险演示物化快照：从 ap_anping 真实数据同源生成（scripts/export_risk_demo_snapshot.py），"
        "非手写数字；对应演示剧本「预热/物化缓存」设计。",
        "meta": meta,
        "totals": totals,
        "items": items,
        "edges": edges,
        "group_metrics": group_metrics,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    db.close()

    print("totals:", json.dumps(totals, ensure_ascii=False))
    print("sample counts:", json.dumps({k: len(v) for k, v in items.items()}, ensure_ascii=False))
    print("edges:", len(edges))
    print("group_metrics groups:", len(group_metrics))
    print("written:", OUT)


if __name__ == "__main__":
    main()

