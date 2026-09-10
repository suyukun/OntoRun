"""GET /api/objects/{kind}/{id} 数据装配：定义 + 关联口径规则 + 上下游血缘边。

kind = measure | dimension | table。度量/维度定义取 registry 原语，
表定义 = 该表在 lineage_edges.json 中的边 + 绑定到它的度量/维度。
血缘边与未确认高亮复用 lineage_payload，保证与图谱页视觉一致。
"""

from __future__ import annotations

from src.fortune_admin import lineage, ontology


def _matches(full_id: str, short: str) -> bool:
    """表 ID 匹配：注册表/度量用全名（cdm.x），规则出处提短名（x），互相包含即同一张表。"""
    return short in full_id or full_id in short


def _rules_for(rules: list[dict], table_ids: list[str]) -> list[dict]:
    return [
        r
        for r in rules
        if any(_matches(t, rt) for t in table_ids for rt in r["related_tables"])
    ]


def _edges_for(edges: list[dict], table_id: str) -> tuple[list[dict], list[dict]]:
    upstream = [e for e in edges if _matches(e["target"], table_id)]
    downstream = [e for e in edges if _matches(e["source"], table_id)]
    return upstream, downstream


def _find_table_id(object_id: str, table_ids: list[str]) -> str | None:
    """表 ID 解析：全名精确优先，短名唯一命中兜底；找不到或有歧义都算不存在。"""
    if object_id in table_ids:
        return object_id
    hits = [t for t in table_ids if _matches(t, object_id)]
    return hits[0] if len(hits) == 1 else None


def _primitive(
    kind: str, object_id: str, payload: dict
) -> tuple[str, list[str], dict] | None:
    """度量/维度 -> (人话描述, 绑定表列表, 定义原语)；找不到返回 None。"""
    if kind == "measure":
        m = next((x for x in payload["measures"] if x["id"] == object_id), None)
        if m is None:
            return None
        definition = {
            "expression": m["expression"],
            "source_table": m["source_table"],
            "source_alias": m["source_alias"],
            "time_field": m["time_field"],
            "filters": m["filters"],
        }
        return m["description"], [m["source_table"]], definition

    d = next((x for x in payload["dimensions"] if x["id"] == object_id), None)
    if d is None:
        return None
    definition = {
        "expression": d["expression"],
        "join": d["join"],
        "grains": d["grains"],
    }
    bind = [d["join"]["table"]] if d["join"] else []
    return d["description"], bind, definition


def object_payload(kind: str, object_id: str) -> dict | None:
    payload = ontology.ontology_payload()
    unconfirmed_tables = [
        t
        for r in payload["rules"]
        if r["status"] != "confirmed"
        for t in r["related_tables"]
    ]
    lin = lineage.lineage_payload(unconfirmed_tables)

    if kind == "table":
        table_id = _find_table_id(object_id, [n["id"] for n in lin["nodes"]])
        if table_id is None:
            return None
        node = next(n for n in lin["nodes"] if n["id"] == table_id)
        upstream, downstream = _edges_for(lin["edges"], table_id)
        return {
            "kind": kind,
            "id": table_id,
            "description": "",
            "layer": node["layer"],
            "unconfirmed": node["unconfirmed"],
            "definition": {
                "bound_measures": [
                    {"id": m["id"], "description": m["description"]}
                    for m in payload["measures"]
                    if _matches(m["source_table"], table_id)
                ],
                "bound_dimensions": [
                    {"id": d["id"], "description": d["description"]}
                    for d in payload["dimensions"]
                    if d["join"] and _matches(d["join"]["table"], table_id)
                ],
            },
            "rules": _rules_for(payload["rules"], [table_id]),
            "upstream": upstream,
            "downstream": downstream,
        }

    if kind not in ("measure", "dimension"):
        return None
    found = _primitive(kind, object_id, payload)
    if found is None:
        return None
    description, bind_tables, definition = found
    if bind_tables:
        upstream, downstream = _edges_for(lin["edges"], bind_tables[0])
        node = next((n for n in lin["nodes"] if n["id"] == bind_tables[0]), None)
        layer = lineage.classify(bind_tables[0]) if node else None
        unconfirmed = node["unconfirmed"] if node else False
    else:
        upstream, downstream = [], []
        layer, unconfirmed = None, False
    return {
        "kind": kind,
        "id": object_id,
        "description": description,
        "layer": layer,
        "unconfirmed": unconfirmed,
        "definition": definition,
        "rules": _rules_for(payload["rules"], bind_tables),
        "upstream": upstream,
        "downstream": downstream,
    }
