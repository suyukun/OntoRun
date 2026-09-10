"""GET /api/lineage 数据装配：54 条血缘边 + 表清单 + 层域划分 + 未确认高亮映射。"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINEAGE_PATH = (
    REPO_ROOT / "scripts/fortune_lineage/lineage_edges.json"
)

# 层域：ODS 贴源 / CDM 明细与维表 / ADS 应用汇总 / DIM 外部公共维表（真实数据
# 里还有 cfgl_* 与 <default> 前缀的日期维表，归入 DIM，不硬塞进三色）。
LAYERS = {
    "ODS": {"color": "#1677ff", "label": "ODS 贴源"},
    "CDM": {"color": "#52c41a", "label": "CDM 明细/维表"},
    "ADS": {"color": "#fa8c16", "label": "ADS 应用"},
    "DIM": {"color": "#722ed1", "label": "DIM 外部维表"},
}


def classify(table_id: str) -> str:
    if table_id.startswith("ods."):
        return "ODS"
    if table_id.startswith("cdm."):
        return "CDM"
    if ".ads_" in table_id:
        return "ADS"
    return "DIM"


def lineage_payload(unconfirmed_tables: list[str]) -> dict:
    edges_raw = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    table_ids = sorted({e["source"] for e in edges_raw} | {e["target"] for e in edges_raw})

    bad = {t for t in unconfirmed_tables if any(t in tid for tid in table_ids)}
    nodes = [
        {
            "id": tid,
            "label": tid,
            "layer": classify(tid),
            "unconfirmed": any(t in tid for t in bad),
        }
        for tid in table_ids
    ]
    edges = []
    for e in edges_raw:
        related = [t for t in bad if t in e["source"] or t in e["target"]]
        edges.append(
            {
                "source": e["source"],
                "target": e["target"],
                "via_script": e["via_script"],
                "unconfirmed": bool(related),
            }
        )
    return {
        "nodes": nodes,
        "edges": edges,
        "layers": LAYERS,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "unconfirmed_edges": sum(1 for e in edges if e["unconfirmed"]),
        },
    }
