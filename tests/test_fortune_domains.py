"""T0c 域声明块硬断言：DOMAINS 金控 10 域 + TABLE_DOMAINS 非 ADS 22 表登记完整性。

登记来源（2026-09-11 Jack 终版改判重登记）：docs/research/数据域划分调研-管理台域图_v0.1.md
§5（逐表映射）+ §9（七条拍板）。登记口径 = 非 ADS（§9 裁决 4/6）：rec.ads_* 8 张
应用层表不按数据域登记；已登记表集合 = lineage_edges.json 实盘 30 张 − ADS
（与 fortune_admin/lineage.py 同源同推导，schema 前缀齐全）。

跑法（禁跑全量）：
    pytest tests/test_fortune_domains.py -q
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

# 调研文档 §9 终态：CU 11 / CH 3 / PB 5 / LM 2 / AC 1；
# or/bs/rc/ps/tr 5 域 0 表（BS 原映射 7 张全为 ADS，随裁决 4 出局）
EXPECTED_TABLE_COUNTS = {
    "cu": 11,
    "ch": 3,
    "pb": 5,
    "lm": 2,
    "ac": 1,
}

EMPTY_DOMAIN_KEYS = {"or", "bs", "rc", "ps", "tr"}

EXPECTED_LINEAGE_TABLES = 30
EXPECTED_NON_ADS_TABLES = 22


def _registered_tables():
    edges = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    return {e["source"] for e in edges} | {e["target"] for e in edges}


def _non_ads_tables():
    """§9 裁决 4/6：ADS 应用层表不按数据域登记，rec.ads_* 全部排除。"""
    return {t for t in _registered_tables() if not t.startswith("rec.ads_")}


def test_domains_exactly_ten():
    assert len(DOMAINS) == 10


def test_table_domains_cover_non_ads_tables_exactly():
    """集合双向相等：无遗漏（每张非 ADS 实盘表都有域）、无悬空（key 不指向不存在的表）。"""
    assert len(_registered_tables()) == EXPECTED_LINEAGE_TABLES
    assert len(_non_ads_tables()) == EXPECTED_NON_ADS_TABLES
    assert set(TABLE_DOMAINS) == _non_ads_tables()


def test_table_domain_keys_are_registered_domains():
    """每表域 key ∈ DOMAINS 的 key 集合。"""
    assert set(TABLE_DOMAINS.values()) <= {d.key for d in DOMAINS}


def test_per_domain_table_counts_match_ruling():
    assert dict(Counter(TABLE_DOMAINS.values())) == EXPECTED_TABLE_COUNTS
    assert {d.key for d in DOMAINS} - set(TABLE_DOMAINS.values()) == EMPTY_DOMAIN_KEYS
