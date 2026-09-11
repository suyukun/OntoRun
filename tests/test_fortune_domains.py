"""T0c 域声明块硬断言：DOMAINS 7 域 + TABLE_DOMAINS 30 表登记完整性。

登记来源：docs/design/管理台重设计-域级总览图专项_v0.1.md §1.3（7 域框架
Jack 已认可，门槛稿 NC「域框架」行）；已注册表集合 = lineage_edges.json
实盘 30 张（与 fortune_admin/lineage.py 同源同推导，schema 前缀齐全）。

跑法（禁跑全量）：
    uv run pytest tests/test_fortune_domains.py -q
"""

import json
from collections import Counter
from pathlib import Path

from src.fortune_semantic.registry import DOMAINS, TABLE_DOMAINS

LINEAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "fortune_lineage"
    / "lineage_edges.json"
)

# 门槛稿 NC「域框架」行：注册7/实名4/授权4/渠道5/客户主数据3/公共维表5/行为埋点2
EXPECTED_TABLE_COUNTS = {
    "reg": 7,
    "real": 4,
    "auth": 4,
    "chnl": 5,
    "cust": 3,
    "pub": 5,
    "behav": 2,
}


def _registered_tables():
    edges = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    return {e["source"] for e in edges} | {e["target"] for e in edges}


def test_domains_exactly_seven():
    assert len(DOMAINS) == 7


def test_table_domains_cover_registered_tables_exactly():
    """集合相等：无遗漏（每张已注册表都有域）、无悬空（key 不指向不存在的表）。"""
    assert set(TABLE_DOMAINS) == _registered_tables()


def test_table_domain_keys_are_registered_domains():
    """每表域 key ∈ DOMAINS 的 key 集合。"""
    assert set(TABLE_DOMAINS.values()) <= {d.key for d in DOMAINS}


def test_per_domain_table_counts_match_framework():
    assert dict(Counter(TABLE_DOMAINS.values())) == EXPECTED_TABLE_COUNTS
