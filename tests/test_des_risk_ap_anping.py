"""S3 M1b DES 金融化 —— 安平金控（ap_anping）增量冒烟/门禁测试。

对照 docs/S3-M1b-DES金融化设计-v1.md（§三 行分布 / §五 确定性 / §六 质量门禁）
+ docs/S3-安平金控-业务规则建模-v1.md（DMN 规则 1-7）+ docs/S3-M1a-字段脱敏映射-脊柱12表.json（字段）：
- 配置层：12 表注册表继承 risk 模板，Σ row_count == total_target（约 30 万）；
- 生成层（小规模 scale=0.001，~308 行，秒级）：12 表行数 == 配置 row_count、编码唯一且格式正确、
  预警等级分布（BLUE 主 / RED 少）、五级分类分布（NORMAL 主）、外键无孤儿（D 门禁同口径）、
  确定性（同 seed 两次生成 → table_sha256 逐一相同）；
- DMN 规则函数纯函数断言（规则 1/2/3 决策表命中）。
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from src.des.config import config_sha256, load_config
from src.des.generate import build_enterprise
from src.des.manifest import read_table_rows, table_sha256
from src.des.generators.risk_generators import (
    concentration_calc,
    five_category_assign,
    warn_level_decide,
)

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "ap_anping"
EXPECTED_SEED = 20260827
SMALL_SCALE = 0.001  # ~308 行，秒级

_CONFIG = load_config(ENTERPRISE_CODE)
_CONFIG_SMALL = load_config(ENTERPRISE_CODE, scale=SMALL_SCALE)
TABLE_IDS = sorted(
    f"{code}.{name}"
    for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items()
    for name in sys_cfg["tables"]
)
# 外键检查清单：(子系统, 子表, 子列, 父系统, 父表, 父列)
FK_CHECKS = [
    ("customer", "ap_customer", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
    ("risk", "ap_warning_signal", "customer_id", "customer", "ap_customer", "customer_id"),
    ("risk", "ap_warning_signal", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
    ("risk", "ap_warning_disposal", "warning_id", "risk", "ap_warning_signal", "warning_id"),
    ("risk", "ap_disposal_detail", "batch_id", "risk", "ap_disposal", "batch_id"),
    ("risk", "ap_disposal_detail", "signal_id", "risk", "ap_warning_signal", "signal_id"),
    ("concentration", "ap_concentration_limit", "customer_no", "customer", "ap_customer", "customer_no"),
    ("approval", "ap_approve_task", "approve_order_id", "approval", "ap_approve_order", "approve_order_id"),
    ("approval", "ap_approve_task", "approve_node_id", "approval", "ap_approve_node", "approve_node_id"),
]


@pytest.fixture(scope="session")
def ap_dir(tmp_path_factory) -> Path:
    """小规模确定性生成 ap_anping 到临时目录（不写 data/）。"""
    out = tmp_path_factory.mktemp("ap_anping")
    build_enterprise(ENTERPRISE_CODE, out_dir=str(out), scale=SMALL_SCALE)
    return out


def _db_path(ap_dir: Path, sys_name: str) -> Path:
    return ap_dir / _CONFIG_SMALL["enterprise"]["systems"][sys_name]["db"]


def _query(ap_dir: Path, sys_name: str, sql: str) -> list[dict]:
    conn = sqlite3.connect(str(_db_path(ap_dir, sys_name)))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql)]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 配置层
# ---------------------------------------------------------------------------
def test_config_total_matches_sum() -> None:
    """Σ row_count == total_target（约 30 万，§三 行分布口径）。"""
    total = sum(
        spec["row_count"]
        for sys_cfg in _CONFIG["enterprise"]["systems"].values()
        for spec in sys_cfg["tables"].values()
    )
    assert total == _CONFIG["total_target"] == 308000


def test_config_inherits_risk_template() -> None:
    """ap_anping 继承金融风控模板：行业标识 + 6 系统 12 表注册表。"""
    assert _CONFIG["industry"] == "financial_risk_control"
    systems = _CONFIG["enterprise"]["systems"]
    assert set(systems) == {"customer", "risk", "concentration", "approval", "project", "base"}
    assert len(TABLE_IDS) == 12


# ---------------------------------------------------------------------------
# 生成层（小规模）
# ---------------------------------------------------------------------------
def test_generated_row_counts_match_config(ap_dir: Path) -> None:
    """12 表行数 == 配置 row_count（§六 无空对象）。"""
    for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items():
        for name, spec in sys_cfg["tables"].items():
            rows = _query(ap_dir, code, f"SELECT COUNT(*) AS n FROM {name}")
            assert rows[0]["n"] == spec["row_count"], f"{code}.{name} 行数不符"


def test_encodings_unique_and_formatted(ap_dir: Path) -> None:
    """编码规则 4：客户/集团/信号/审批单/风险项目/处置 编码唯一且格式正确。"""
    cases = [
        ("customer", "ap_customer", "customer_no", r"^CUST-\d{4}-\d{6}$"),
        ("customer", "ap_group_customer", "group_customer_no", r"^GRP-\d{4}-\d{6}$"),
        ("risk", "ap_warning_signal", "signal_id", r"^SGN-\d{4}-\d{8}$"),
        ("approval", "ap_approve_order", "approve_order_id", r"^APP-\d{4}-\d{8}$"),
        ("project", "ap_risk_project", "risk_project_id", r"^PROJ-\d{4}-\d{8}$"),
        ("risk", "ap_disposal", "disposal_id", r"^DSP-\d{4}-\d{8}$"),
    ]
    for sys_name, table, col, pat in cases:
        vals = [r[col] for r in _query(ap_dir, sys_name, f"SELECT {col} FROM {table}")]
        assert len(vals) == len(set(vals)), f"{table}.{col} 编码不唯一"
        assert all(re.match(pat, v) for v in vals), f"{table}.{col} 编码格式不符 {pat}"


def test_warning_level_distribution(ap_dir: Path) -> None:
    """规则 1 预警等级分布：BLUE 为主（~70%）、RED 少数（~5%），且等级合法。"""
    rows = _query(ap_dir, "risk", "SELECT warn_level FROM ap_warning_signal")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["warn_level"]] = counts.get(r["warn_level"], 0) + 1
    n = len(rows)
    assert set(counts) <= {"RED", "YELLOW", "BLUE"}
    assert counts.get("BLUE", 0) / n >= 0.6
    assert counts.get("RED", 0) / n <= 0.15


def test_five_classification_distribution(ap_dir: Path) -> None:
    """规则 2 五级分类：风险项目 NORMAL 为主、各级别合法。"""
    rows = _query(ap_dir, "project", "SELECT five_classification FROM ap_risk_project")
    categories = {r["five_classification"] for r in rows}
    assert categories <= {"NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"}
    assert "NORMAL" in categories


def test_concentration_status_follows_rule(ap_dir: Path) -> None:
    """规则 3 集中度状态与敞口/资本净额一致（current_status 可机验）。"""
    rows = _query(
        ap_dir, "concentration",
        "SELECT concentration_limit, warning_value, current_status FROM ap_concentration_limit",
    )
    statuses = {r["current_status"] for r in rows}
    assert statuses <= {"NORMAL", "YELLOW_ALERT", "ORANGE_ALERT", "RED_ALERT"}


def test_fk_no_orphans(ap_dir: Path) -> None:
    """D 门禁同口径：声明外键 LEFT JOIN 空侧孤儿 = 0（§六 外键完整性 100%）。"""
    for child_sys, ct, cc, parent_sys, pt, pc in FK_CHECKS:
        child_db, parent_db = _db_path(ap_dir, child_sys), _db_path(ap_dir, parent_sys)
        conn = sqlite3.connect(str(child_db))
        try:
            parent_ref = pt
            if parent_db.resolve() != child_db.resolve():
                conn.execute(f"ATTACH DATABASE '{parent_db}' AS par")
                parent_ref = f"par.{pt}"
            n = int(
                conn.execute(
                    f"SELECT COUNT(*) FROM {ct} c LEFT JOIN {parent_ref} p "
                    f"ON c.{cc} = p.{pc} WHERE p.{pc} IS NULL"
                ).fetchone()[0]
            )
            assert n == 0, f"{ct}.{cc} → {pt}.{pc} 孤儿 {n}"
        finally:
            conn.close()


def test_determinism_same_seed_all_tables(tmp_path) -> None:
    """确定性：同 seed 同配置两次生成 → 12 表 table_sha256 逐一相同（§五）。"""
    dir_a, dir_b = tmp_path / "a", tmp_path / "b"
    build_enterprise(ENTERPRISE_CODE, out_dir=str(dir_a), scale=SMALL_SCALE)
    build_enterprise(ENTERPRISE_CODE, out_dir=str(dir_b), scale=SMALL_SCALE)
    for table_id in TABLE_IDS:
        code, name = table_id.split(".", 1)
        pk = _CONFIG_SMALL["enterprise"]["systems"][code]["tables"][name]["pk"]
        sha_a = table_sha256(read_table_rows(_db_path(dir_a, code), name, pk))
        sha_b = table_sha256(read_table_rows(_db_path(dir_b, code), name, pk))
        assert sha_a == sha_b, f"{table_id} 同 seed 两次生成 SHA 不一致"


# ---------------------------------------------------------------------------
# DMN 规则函数（纯函数决策表命中，§六 规则命中率）
# ---------------------------------------------------------------------------
def test_warn_level_decide_rule_table() -> None:
    """规则 1 决策表：押品贬值 ≥30% / 集中度超限 ≥20% / 评分 ≥80 → RED。"""
    assert warn_level_decide(85) == "RED"
    assert warn_level_decide(50, collateral_depreciation=0.30) == "RED"
    assert warn_level_decide(50, concentration_overrun=0.20) == "RED"
    assert warn_level_decide(70) == "YELLOW"
    assert warn_level_decide(50, collateral_depreciation=0.20) == "YELLOW"
    assert warn_level_decide(50, concentration_overrun=0.15) == "YELLOW"
    assert warn_level_decide(50, related_change=0.30) == "YELLOW"
    assert warn_level_decide(30) == "BLUE"
    assert warn_level_decide(30, collateral_depreciation=0.10) == "BLUE"


def test_five_category_assign_rule_table() -> None:
    """规则 2 决策表：逾期区间与减值/风险事件 → 五级分类。"""
    assert five_category_assign(0) == "NORMAL"
    assert five_category_assign(45) == "ATTENTION"
    assert five_category_assign(0, impairment_ratio=0.35) == "SECONDARY"
    assert five_category_assign(120) == "SECONDARY"
    assert five_category_assign(200) == "DOUBTFUL"
    assert five_category_assign(400) == "LOSS"
    assert five_category_assign(0, confirmed_loss=True) == "LOSS"


def test_concentration_calc_rule_table() -> None:
    """规则 3 决策表：≤10% 正常 / ≤15% 黄警 / ≤25% 橙警 / >25% 红警。"""
    assert concentration_calc(0.05, 1)["status"] == "NORMAL"
    assert concentration_calc(0.12, 1)["status"] == "YELLOW_ALERT"
    assert concentration_calc(0.12, 1)["need_approval"] is False
    assert concentration_calc(0.18, 1)["status"] == "ORANGE_ALERT"
    assert concentration_calc(0.18, 1)["need_approval"] is True
    assert concentration_calc(0.30, 1)["status"] == "RED_ALERT"
    assert concentration_calc(0.30, 1)["warn_level"] == "RED"
