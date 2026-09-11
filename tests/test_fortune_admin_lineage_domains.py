"""T401 增量测试：lineage payload 域装配 + 域间聚合边（M2 US3 域图数据源）。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §A2-US3 / §A3（edge_aggregation_severity /
domain_graph_nodes / qc6）/ §B1-T401 / §B3；口径依据
docs/research/数据域划分调研-管理台域图_v0.1.md §9（Jack 七条裁决）。

判据四条：
① 22 登记表 nodes[].domain 与 TABLE_DOMAINS 一致、8 张 rec.ads_* domain=null
   （裁决 4：ADS 应用层不登记，禁表名前缀猜测兜底 A4-5）；
② domains 汇总含全 10 域，有表 5 域 table_count 按逻辑表口径（pb=3：date_yf
   三 schema 副本算 1 张，裁决 5），0 表 5 域 table_count=0——裁决 2「有才显示」
   的隐藏由前端过滤，payload 保留域框架全集（0 表域=金控开放分类的扩展位，
   前端过滤零契约改动，扩表零改图）；
③ 域间聚合边 weight=聚合的表级边数 N、severity 三级（settled/pending/divergent）
   各能构造并断言（divergent 经合成规则状态构造；同域内部边与未登记表边不进聚合）；
④ ads_metric_count（裁决 7 指标位）与血缘可追溯：测试内从 lineage_edges.json
   独立重算同源对账，不手填假数字。

跑法（禁跑全量）：
    pytest tests/test_fortune_admin_lineage_domains.py -q
回归：pytest tests/test_fortune_domains.py -q
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.fortune_admin import lineage
from src.fortune_semantic.registry import DOMAINS, TABLE_DOMAINS

LINEAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "fortune_lineage"
    / "lineage_edges.json"
)

DOMAIN_KEYS = {d.key for d in DOMAINS}

# 与 lineage_edges.json via_script 文件名对齐的四个关键脚本（构造 severity 用）
SC_RLTV = "脚本dwd_ch_usr_rltv_df.sql"  # ch->cu 一条（无规则关联 = settled 基底）
SC_ACTV = "脚本dwd_cu_actv_df.sql"  # ch->cu ×1 + cu 域内 ×3
SC_USR = "脚本dim_cu_usr_info_df.sql"  # lm->cu、ac->cu（+cu 域内）
SC_CHL = "脚本dim_ch_chl_df.sql"  # cu->ch


def _raw_edges() -> list[dict]:
    return json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))


def _payload() -> dict:
    return lineage.lineage_payload([])


# ---- ① 节点域字段 ----


def test_registered_tables_get_domain_and_ads_get_none():
    payload = _payload()
    domain_by_id = {n["id"]: n["domain"] for n in payload["nodes"]}
    assert len(domain_by_id) == 30
    # 22 登记表：域 key 与 TABLE_DOMAINS 逐表一致（不猜测、不兜底）
    assert len(TABLE_DOMAINS) == 22
    for tid, key in TABLE_DOMAINS.items():
        assert domain_by_id[tid] == key, tid
    # 8 张 ADS：domain=None（裁决 4，禁表名前缀猜测兜底 A4-5）
    ads_ids = [tid for tid in domain_by_id if lineage.classify(tid) == "ADS"]
    assert len(ads_ids) == 8
    assert all(tid.startswith("rec.ads_") for tid in ads_ids)
    assert all(domain_by_id[tid] is None for tid in ads_ids)
    assert sum(1 for v in domain_by_id.values() if v is not None) == 22


# ---- ② domains 汇总（逻辑表口径 + 空域处理）----


def test_domains_summary_logical_table_counts():
    domains = {d["key"]: d for d in _payload()["domains"]}
    # payload 含全 10 域；0 表域 table_count=0，隐藏由前端过滤（裁决 2）
    assert set(domains) == DOMAIN_KEYS
    # 逻辑表口径（裁决 5）：同表名多 schema 副本算 1 张——测试内从
    # TABLE_DOMAINS 同源重算（去 schema 前缀去重），不手填假数字
    bare_names: dict[str, set[str]] = {}
    for tid, key in TABLE_DOMAINS.items():
        bare_names.setdefault(key, set()).add(tid.split(".", 1)[1])
    for key in DOMAIN_KEYS:
        assert domains[key]["table_count"] == len(bare_names.get(key, ())), key
    # 判据点名：pb 物理 5（date_yf 三副本）-> 逻辑 3；有表域合计 20 逻辑表
    assert domains["pb"]["replicas"] == 5
    assert domains["pb"]["table_count"] == 3
    assert sum(d["table_count"] for d in domains.values()) == 20
    # 无多 schema 副本的域：replicas == table_count
    for key in ("cu", "ch", "lm", "ac"):
        assert domains[key]["replicas"] == domains[key]["table_count"], key
    # 0 表域：计数归零
    for key in ("or", "bs", "rc", "ps", "tr"):
        assert domains[key]["table_count"] == domains[key]["replicas"] == 0, key
    # 域名透传（双编码：专业词 + 人话副标 qc11）
    assert domains["cu"]["name"] == "用户域"
    assert domains["pb"]["name"] == "公共域"


# ---- ③ 域间聚合边：weight + severity 三级 ----


def test_domain_edges_weight_and_aggregation_scope():
    view = lineage.domain_view(_raw_edges(), [])
    edges = {(e["source"], e["target"]): e for e in view["domain_edges"]}
    # 实盘跨域对：(ch,cu) ×3、(cu,ch) / (lm,cu) / (ac,cu) 各 ×1
    assert set(edges) == {("ch", "cu"), ("cu", "ch"), ("lm", "cu"), ("ac", "cu")}
    assert edges[("ch", "cu")]["weight"] == 3
    for pair in (("cu", "ch"), ("lm", "cu"), ("ac", "cu")):
        assert edges[pair]["weight"] == 1, pair
    assert sum(e["weight"] for e in view["domain_edges"]) == 6
    # 同域内部边不进聚合（域内关系归域内图）
    assert all(src != dst for src, dst in edges)
    # 涉及未登记表（rec.ads_*）的表级血缘不进域间聚合（裁决 4：无域可聚）
    assert all(
        not src.startswith("rec.ads_") and not dst.startswith("rec.ads_")
        for src, dst in edges
    )


def test_domain_edges_severity_three_levels_constructed():
    # divergent > pending > settled：合成规则状态构造三级（divergent 实盘无未裁
    # 分歧，经注入构造；关联路径 = via_script 文件名 == 规则出处脚本文件名）
    # 第一幕：仅 pending 规则 -> 涉及的聚合边橙虚线，其余灰实线
    view = lineage.domain_view(
        _raw_edges(), [{"script": SC_ACTV, "pending": True, "divergent": False}]
    )
    edges = {(e["source"], e["target"]): e for e in view["domain_edges"]}
    assert edges[("ch", "cu")]["severity"] == "pending"  # 组内 1 条表级边涉 R3/R4 同款
    for pair in (("cu", "ch"), ("lm", "cu"), ("ac", "cu")):
        assert edges[pair]["severity"] == "settled", pair
    # 第二幕：同一组混入 divergent 规则（SC_USR 产出 dim_cu_usr_info_df，
    # 其表级边同时落在 ch->cu / lm->cu / ac->cu 三组）-> 升格红虚线（优先级）
    states_mixed = [
        {"script": SC_ACTV, "pending": True, "divergent": False},
        {"script": SC_USR, "pending": False, "divergent": True},
    ]
    mixed = {
        (e["source"], e["target"]): e
        for e in lineage.domain_view(_raw_edges(), states_mixed)["domain_edges"]
    }
    assert mixed[("ch", "cu")]["severity"] == "divergent"
    assert mixed[("lm", "cu")]["severity"] == "divergent"
    assert mixed[("ac", "cu")]["severity"] == "divergent"  # 同脚本跨组传染
    assert mixed[("cu", "ch")]["severity"] == "settled"  # 无规则关联 = 灰实线


def test_table_edge_severity_via_script_linkage():
    payload = lineage.lineage_payload(
        [],
        edges_raw=_raw_edges(),
        states=[{"script": SC_ACTV, "pending": True, "divergent": False}],
    )
    by_severity = Counter(e["severity"] for e in payload["edges"])
    # actv 脚本产出 4 条表级边（1 跨域 + 3 域内），全部 pending
    assert by_severity["pending"] == 4
    assert sum(by_severity.values()) == len(payload["edges"])
    assert set(by_severity) <= {"settled", "pending", "divergent"}


def test_rule_states_pending_divergent_escalate_semantics():
    """pending/divergent 推导：escalate 只留痕不翻转 -> 分歧仍算未裁（A4-7/US2）。"""
    base = {
        "source_script": "x/脚本a.sql",
        "status": "unverified",
        "divergence": [{"key": "account"}],
    }
    states = lineage.rule_states(
        [
            dict(base),  # 有分歧未裁
            {**base, "decision": {"option_key": "escalate"}},  # 升级留痕 = 仍未裁
            {
                **base,
                "status": "confirmed",
                "decision": {"option_key": "user"},  # 有效裁决 = 消解
            },
            {
                "source_script": "x/脚本b.sql",
                "status": "unverified",
                "divergence": None,
            },  # 普通待确认（无分歧，另一脚本）
        ]
    )
    assert [s["divergent"] for s in states] == [True, True, False, False]
    assert [s["pending"] for s in states] == [True, True, False, True]
    assert [s["script"] for s in states] == ["脚本a.sql"] * 3 + ["脚本b.sql"]


# ---- ④ ads_metric_count 指标位（裁决 7）----


def test_ads_metric_count_traceable_to_lineage():
    domains = {d["key"]: d for d in _payload()["domains"]}
    # 同源对账：每张 ADS 表按直接上游源表登记域各 +1（一跳），独立重算比对
    raw = _raw_edges()
    upstream: dict[str, set[str]] = {}
    for e in raw:
        upstream.setdefault(e["target"], set()).add(e["source"])
    ads_ids = {
        t
        for e in raw
        for t in (e["source"], e["target"])
        if lineage.classify(t) == "ADS"
    }
    assert len(ads_ids) == 8
    expected: Counter[str] = Counter()
    for ads in ads_ids:
        for key in {
            TABLE_DOMAINS[s] for s in upstream.get(ads, ()) if s in TABLE_DOMAINS
        }:
            expected[key] += 1
    for key in DOMAIN_KEYS:
        assert domains[key]["ads_metric_count"] == expected.get(key, 0), key
    # 至少一域 >0，且计数与逐表血缘可追溯：cu 覆盖全部 8 张 ADS、
    # lm 仅经 dwd_lm_pv_df 进入综合漏斗表
    assert expected["cu"] == 8
    assert expected == Counter({"cu": 8, "pb": 6, "ch": 4, "lm": 1})
    lm_trace = [
        e
        for e in raw
        if e["target"] == "rec.ads_chnl_rgst_to_real_auth_dau_df"
        and e["source"] == "cdm.dwd_lm_pv_df"
    ]
    assert len(lm_trace) == 1


# ---- 装配集成：既有契约不变（只增不改）----


def test_payload_contract_additive_only():
    payload = _payload()
    assert set(payload) >= {
        "nodes",
        "edges",
        "domains",
        "domain_edges",
        "layers",
        "stats",
    }
    node = payload["nodes"][0]
    assert set(node) == {"id", "label", "layer", "domain", "unconfirmed"}
    edge = payload["edges"][0]
    assert set(edge) == {"source", "target", "via_script", "unconfirmed", "severity"}
    assert set(payload["layers"]) == {"ODS", "CDM", "ADS", "DIM"}
    assert payload["stats"]["nodes"] == len(payload["nodes"]) == 30
    assert payload["stats"]["edges"] == len(payload["edges"]) == len(_raw_edges())
    # 空未确认清单：高亮全 False（既有行为不回归）
    assert not any(e["unconfirmed"] for e in payload["edges"])
    # 域汇总条目形状
    assert set(payload["domains"][0]) == {
        "key",
        "name",
        "table_count",
        "replicas",
        "pending",
        "divergent",
        "ads_metric_count",
    }
    assert set(payload["domain_edges"][0]) == {"source", "target", "weight", "severity"}
