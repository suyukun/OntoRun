"""GET /api/lineage 数据装配：血缘边 + 表清单 + 层域划分 + 未确认高亮 + 域装配。

T401 域装配（M2 US3 域图数据源），口径依据：
- docs/plans/开工门槛-管理台重构_v0.2.md §A2-US3 / §A3 / §B3 / §附域框架改判记录；
- docs/research/数据域划分调研-管理台域图_v0.1.md §9（Jack 七条裁决：
  裁决 2 空域隐藏归前端渲染层 / 裁决 4 ADS 不按数据域登记 / 裁决 5 逻辑表
  口径 / 裁决 7 ADS 指标位 ads_metric_count）。
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.fortune_admin.ontology import ontology_payload
from src.fortune_semantic.registry import DOMAINS, TABLE_DOMAINS

REPO_ROOT = Path(__file__).resolve().parents[2]
LINEAGE_PATH = REPO_ROOT / "scripts/fortune_lineage/lineage_edges.json"

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


def _logical_table_name(table_id: str) -> str:
    """逻辑表名 = 去 schema 前缀：dim_pb_date_yf 三 schema 副本算 1 张（§9 裁决 5）。"""
    return table_id.split(".", 1)[1] if "." in table_id else table_id


def rule_states(rules: list[dict]) -> list[dict]:
    """口径规则 -> [{script, pending, divergent}]（口径跟随 ontology payload 既有推导）。

    - pending = status != "confirmed"（与 /api/ontology summary.pending、router
      未确认表清单同口径）；
    - divergent = 有分歧候选且未有效裁决。有效裁决 = 最新确认记录内嵌 decision
      且 option_key != "escalate"——escalate 只留痕不翻转（A4-7），分歧仍算未裁，
      域图红虚线不消解（§A2-US2）；
    - script = 出处脚本文件名。规则挂表/挂边一律按「出处脚本文件名 == 边
      via_script 文件名」联结（via_script 即产出目标表的脚本），不做表名猜测。
    """
    states = []
    for r in rules:
        decision = r.get("decision")
        resolved = decision is not None and decision.get("option_key") != "escalate"
        states.append(
            {
                "script": Path(r["source_script"]).name,
                "pending": r["status"] != "confirmed",
                "divergent": r.get("divergence") is not None and not resolved,
            }
        )
    return states


def _pick_severity(involved: list[dict]) -> str:
    """三级判定：涉及规则有未裁分歧 -> divergent；有待确认 -> pending；否则 settled。"""
    if any(s["divergent"] for s in involved):
        return "divergent"
    if any(s["pending"] for s in involved):
        return "pending"
    return "settled"


def domain_view(edges_raw: list[dict], states: list[dict]) -> dict:
    """域装配纯函数：表级血缘 + 规则状态 -> 域字段 / 域汇总 / 域间聚合边。

    口径自述（§9 裁决落点）：
    - node_domain：TABLE_DOMAINS 登记表 -> 域 key；未登记 ADS 表 -> None
      （裁决 4：ADS 应用层不按数据域登记；禁表名前缀猜测兜底，A4-5）。
    - domains[].table_count 按**逻辑表**计（裁决 5）：同表名多 schema 副本算
      1 张（dim_pb_date_yf 三副本 = 1）；replicas 附物理登记表数，供详情页列
      物理副本清单。含全 10 域、0 表域 table_count=0——「有才显示」的隐藏是
      前端渲染责任（裁决 2），payload 保留金控 10 域开放框架全集（0 表域 =
      扩展位），前端过滤零契约改动。
    - domains[].pending / divergent：该域关联规则的待确认数 / 未裁分歧数。
      规则挂域路径 = 规则出处脚本（文件名）-> 血缘中该脚本产出的目标表 ->
      目标表登记域；产出 ADS 的规则（R5-R10）不挂任何域（裁决 4 同源）。
    - domains[].ads_metric_count（裁决 7 指标位）：每张 ADS 表按其**直接上游**
      血缘源表所登记的域各 +1（一张 ADS 连多域则多域各 +1；上游源表未登记域
      的不计，含上游 ADS 表）。只走一跳不递归：ADS->ADS 中间表的上游域已由
      各自的直接上游覆盖，递归不改变计数且不可直读。
    - 域间聚合边：表级血缘按 (源域, 目标域) 聚合为 1 条边，weight = 聚合的
      表级边数 N（前端 ×N 角标）；同域内部边与涉及未登记表的边不进聚合
      （域内关系归域内图，未登记表无域可聚）。
    - severity 三级（§A2-US3 灰实线 / 橙虚线 / 红虚线）：聚合边按其全部表级边
      涉及的规则合并判定；表级边按其 via_script 关联的规则判定；无规则关联
      的边 settled。
    """
    rules_by_script: dict[str, list[dict]] = {}
    for st in states:
        rules_by_script.setdefault(st["script"], []).append(st)

    all_tables = sorted(
        {e["source"] for e in edges_raw} | {e["target"] for e in edges_raw}
    )
    node_domain = {tid: TABLE_DOMAINS.get(tid) for tid in all_tables}

    # 规则挂域：脚本 -> 其产出的目标表集合 -> 目标表登记域
    domains_by_script: dict[str, set[str]] = {}
    for e in edges_raw:
        target_domain = TABLE_DOMAINS.get(e["target"])
        if target_domain is not None:
            domains_by_script.setdefault(Path(e["via_script"]).name, set()).add(
                target_domain
            )

    pending_by_domain: Counter[str] = Counter()
    divergent_by_domain: Counter[str] = Counter()
    for st in states:
        for key in domains_by_script.get(st["script"], ()):
            if st["pending"]:
                pending_by_domain[key] += 1
            if st["divergent"]:
                divergent_by_domain[key] += 1

    # 逻辑表口径（裁决 5）：table_count 按去 schema 前缀后的逻辑名去重；
    # replicas = 物理登记表数（date_yf 三副本 -> pb 域 5 物理 / 3 逻辑）
    logical_names: dict[str, set[str]] = {}
    physical_by_domain: Counter[str] = Counter()
    for tid, key in TABLE_DOMAINS.items():
        physical_by_domain[key] += 1
        logical_names.setdefault(key, set()).add(_logical_table_name(tid))

    # ADS 指标位（裁决 7）：每张 ADS 表按直接上游源表的登记域各 +1（一跳，不递归）
    upstream: dict[str, set[str]] = {}
    for e in edges_raw:
        upstream.setdefault(e["target"], set()).add(e["source"])
    ads_metric: Counter[str] = Counter()
    for tid in all_tables:
        if classify(tid) != "ADS":
            continue
        for key in {
            TABLE_DOMAINS[s] for s in upstream.get(tid, ()) if s in TABLE_DOMAINS
        }:
            ads_metric[key] += 1

    domains = [
        {
            "key": d.key,
            "name": d.name,
            "table_count": len(logical_names.get(d.key, ())),
            "replicas": physical_by_domain.get(d.key, 0),
            "pending": pending_by_domain.get(d.key, 0),
            "divergent": divergent_by_domain.get(d.key, 0),
            "ads_metric_count": ads_metric.get(d.key, 0),
        }
        for d in DOMAINS
    ]

    # 域间聚合边：同域内部边与涉及未登记表的边不进聚合
    agg: dict[tuple[str, str], dict] = {}
    for e in edges_raw:
        src_key = TABLE_DOMAINS.get(e["source"])
        dst_key = TABLE_DOMAINS.get(e["target"])
        if src_key is None or dst_key is None or src_key == dst_key:
            continue
        entry = agg.setdefault((src_key, dst_key), {"weight": 0, "states": []})
        entry["weight"] += 1
        entry["states"].extend(rules_by_script.get(Path(e["via_script"]).name, []))
    domain_edges = [
        {
            "source": src,
            "target": dst,
            "weight": entry["weight"],
            "severity": _pick_severity(entry["states"]),
        }
        for (src, dst), entry in sorted(agg.items())
    ]

    severity_by_script = {
        Path(e["via_script"]).name: _pick_severity(
            rules_by_script.get(Path(e["via_script"]).name, [])
        )
        for e in edges_raw
    }
    return {
        "node_domain": node_domain,
        "severity_by_script": severity_by_script,
        "domains": domains,
        "domain_edges": domain_edges,
    }


def lineage_payload(
    unconfirmed_tables: list[str],
    edges_raw: list[dict] | None = None,
    states: list[dict] | None = None,
) -> dict:
    """装配 /api/lineage payload：既有表级图字段不变，T401 增域装配三块。

    edges_raw / states 可注入（测试构造 divergent 场景用）；缺省 = 实盘血缘
    文件 + ontology_payload() 现场规则状态（registry 运行期被确认写路径改写，
    与 /api/ontology 同源，绝不复用进程内旧状态）。
    """
    if edges_raw is None:
        edges_raw = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    if states is None:
        states = rule_states(ontology_payload()["rules"])
    view = domain_view(edges_raw, states)

    table_ids = sorted(
        {e["source"] for e in edges_raw} | {e["target"] for e in edges_raw}
    )

    bad = {t for t in unconfirmed_tables if any(t in tid for tid in table_ids)}
    nodes = [
        {
            "id": tid,
            "label": tid,
            "layer": classify(tid),
            "domain": view["node_domain"][tid],
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
                "severity": view["severity_by_script"][Path(e["via_script"]).name],
            }
        )
    return {
        "nodes": nodes,
        "edges": edges,
        "domains": view["domains"],
        "domain_edges": view["domain_edges"],
        "layers": LAYERS,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "unconfirmed_edges": sum(1 for e in edges if e["unconfirmed"]),
        },
    }
