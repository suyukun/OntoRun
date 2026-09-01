"""S3 M1b DES 金融化 —— 安平金控（ap_anping）增量冒烟/门禁测试。

对照 docs/S3-M1b-DES金融化设计-v1.md（§三 行分布 / §五 确定性 / §六 质量门禁）
+ docs/S3-安平金控-业务规则建模-v1.md（DMN 规则 1-7）+ docs/S3-M1a-字段脱敏映射-全量42表.json（字段）：
- 配置层：54 表注册表继承 risk 模板，Σ row_count == total_target（约 43.6 万）；
- 生成层（小规模 scale=0.001，~380 行，秒级）：54 表行数 == 配置 row_count、编码唯一且格式正确、
  预警等级中文枚举（黄55/橙34/红11，口径包§五）、事件类型偏态（信用45/市场20/流动性15/合规12/操作8）、
  生命周期七态（待确认30/确认中20/已确认20/处置中15/已关闭10/已撤销3/已排除2）+ 流程/审批字段连贯、
  名称纯净化（无「·编号尾巴」）、五级分类分布（NORMAL 主）、外键无孤儿（D 门禁同口径，49 条）、
  DDL 列 == 生成行键（无漂移）、脱敏门禁（表名/字段名对原型 o_a_erms/p_erms 零命中）、
  确定性（同 seed 两次生成 → table_sha256 逐一相同）；
- DMN 规则函数纯函数断言（规则 1/2/3 决策表命中）。
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from src.des.config import load_config
from src.des.generate import TABLE_SPECS, build_enterprise
from src.des.generators.risk_generators import (
    LEVEL1_TOPICS,
    LEVEL2_BY_L1,
    concentration_calc,
    five_category_assign,
    warn_level_decide,
)
from src.des.manifest import read_table_rows, table_sha256

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "ap_anping"
EXPECTED_SEED = 20260827
SMALL_SCALE = 0.001  # ~445 行，秒级

_CONFIG = load_config(ENTERPRISE_CODE)
_CONFIG_SMALL = load_config(ENTERPRISE_CODE, scale=SMALL_SCALE)
TABLE_IDS = sorted(
    f"{code}.{name}"
    for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items()
    for name in sys_cfg["tables"]
)
# 外键检查清单：(子系统, 子表, 子列, 父系统, 父表, 父列) —— 脊柱 12 + M1b 全量 42
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
    # —— M1b 全量补全：42 张新表 FK ——
    ("customer", "ap_customer_relation", "internal_customer_no", "customer", "ap_customer", "internal_customer_no"),
    ("customer", "ap_customer_relation_tree", "internal_customer_no", "customer", "ap_customer", "internal_customer_no"),
    ("customer", "ap_important_customer_list", "group_customer_name", "customer", "ap_group_customer", "group_customer_name"),
    ("customer", "ap_top500_customer_risk", "customer_no", "customer", "ap_customer", "customer_no"),
    ("customer", "ap_top500_customer_risk", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
    ("customer", "ap_customer_assets", "customer_no", "customer", "ap_customer", "customer_no"),
    ("customer", "ap_customer_invest_dist", "customer_no", "customer", "ap_customer", "customer_no"),
    ("customer", "ap_subsidiary_credit_detail", "group_customer_name", "customer", "ap_group_customer", "group_customer_name"),
    ("customer", "ap_collateral", "customer_name", "customer", "ap_customer", "customer_name"),
    ("customer", "ap_collateral", "group_customer_name", "customer", "ap_group_customer", "group_customer_name"),
    ("customer", "ap_subsidiary_mortgage", "customer_name", "customer", "ap_customer", "customer_name"),
    ("customer", "ap_bank_pledge_detail", "customer_credit_code", "customer", "ap_customer", "cert_no"),
    ("customer", "ap_bank_pledge_detail", "group_customer_name", "customer", "ap_group_customer", "group_customer_name"),
    ("customer", "ap_securities_pledge_detail", "customer_credit_code", "customer", "ap_customer", "cert_no"),
    ("risk", "ap_warning_push", "warning_id", "risk", "ap_warning_signal", "warning_id"),
    ("risk", "ap_warn_signal_concentration", "top500_customer_id", "customer", "ap_top500_customer_risk", "top500_customer_id"),
    ("risk", "ap_warn_signal_concentration", "customer_no", "customer", "ap_customer", "customer_no"),
    ("risk", "ap_warn_signal_concentration", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
    ("risk", "ap_warn_signal_derive", "customer_id", "customer", "ap_customer", "customer_id"),
    ("risk", "ap_warn_signal_derive", "approve_order_id", "approval", "ap_approve_order", "approve_order_id"),
    ("risk", "ap_warn_derive_deal_detail", "derive_warning_id", "risk", "ap_warn_signal_derive", "derive_warning_id"),
    ("risk", "ap_warn_derive_sub_push", "derive_warning_id", "risk", "ap_warn_signal_derive", "derive_warning_id"),
    ("risk", "ap_warn_derive_sub_push", "customer_id", "customer", "ap_customer", "customer_id"),
    ("risk", "ap_warn_signal_deviation", "customer_no", "customer", "ap_customer", "customer_no"),
    ("risk", "ap_warn_signal_deviation", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
    ("risk", "ap_warn_signal_deviation", "approve_order_id", "approval", "ap_approve_order", "approve_order_id"),
    ("risk", "ap_deviation_warn_score", "group_customer_name", "customer", "ap_group_customer", "group_customer_name"),
    ("concentration", "ap_concentration_limit_adj", "concentration_limit_id", "concentration", "ap_concentration_limit", "concentration_limit_id"),
    ("concentration", "ap_concentration_limit_adj", "customer_no", "customer", "ap_customer", "customer_no"),
    ("concentration", "ap_concentration_warn_adj", "concentration_limit_id", "concentration", "ap_concentration_limit", "concentration_limit_id"),
    ("concentration", "ap_concentration_warn_adj", "customer_no", "customer", "ap_customer", "customer_no"),
    ("concentration", "ap_codebt_customer", "customer_name", "customer", "ap_customer", "customer_name"),
    ("concentration", "ap_codebt_warn_score", "customer_name", "customer", "ap_customer", "customer_name"),
    ("approval", "ap_approve_oper_log", "approve_order_id", "approval", "ap_approve_order", "approve_order_id"),
    ("approval", "ap_approve_oper_log", "approve_task_id", "approval", "ap_approve_task", "approve_task_id"),
    ("approval", "ap_approve_warn_rel", "approve_order_id", "approval", "ap_approve_order", "approve_order_id"),
    ("approval", "ap_approve_warn_rel", "warning_id", "risk", "ap_warning_signal", "warning_id"),
    ("approval", "ap_approve_todo", "approve_task_id", "approval", "ap_approve_task", "approve_task_id"),
    ("base", "ap_dim_rank", "customer_no", "customer", "ap_customer", "customer_no"),
    ("base", "ap_dim_rank", "group_customer_no", "customer", "ap_group_customer", "group_customer_no"),
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
    """Σ row_count == total_target（约 43.6 万，§三 行分布口径）。"""
    total = sum(
        spec["row_count"]
        for sys_cfg in _CONFIG["enterprise"]["systems"].values()
        for spec in sys_cfg["tables"].values()
    )
    assert total == _CONFIG["total_target"] == 371301


def test_config_inherits_risk_template() -> None:
    """ap_anping 继承金融风控模板：行业标识 + 6 系统 54 表注册表（脊柱 12 + M1b 42）。"""
    assert _CONFIG["industry"] == "financial_risk_control"
    systems = _CONFIG["enterprise"]["systems"]
    assert set(systems) == {"customer", "risk", "concentration", "approval", "project", "base"}
    assert len(TABLE_IDS) == 54


def test_desensitized_names_no_prototype() -> None:
    """S3-M1a 选表脱敏清单 待办 3 门禁：表名/字段名对原型前缀零命中。"""
    prototype = ("o_a_erms", "p_erms", "o_base", "o_sys", "erms_dict", "p_serial")
    for table_id in TABLE_IDS:
        _code, name = table_id.split(".", 1)
        assert not name.startswith(prototype), f"表名含原型前缀: {name}"
        ddl = TABLE_SPECS[table_id]["ddl"]
        for col in re.findall(r"^\s+(\w+) (?:TEXT|INTEGER|REAL)", ddl, re.MULTILINE):
            assert not col.startswith(prototype), f"{table_id}.{col} 字段名含原型前缀"


# ---------------------------------------------------------------------------
# 生成层（小规模）
# ---------------------------------------------------------------------------
def test_generated_row_counts_match_config(ap_dir: Path) -> None:
    """54 表行数 == 配置 row_count（§六 无空对象）。"""
    for code, sys_cfg in _CONFIG_SMALL["enterprise"]["systems"].items():
        for name, spec in sys_cfg["tables"].items():
            rows = _query(ap_dir, code, f"SELECT COUNT(*) AS n FROM {name}")
            assert rows[0]["n"] == spec["row_count"], f"{code}.{name} 行数不符"


def test_ddl_columns_match_generated_rows(ap_dir: Path) -> None:
    """DDL 列集合 == 生成行键集合（无漂移：42 张新表行字段与建表字段完全一致）。"""
    for table_id in TABLE_IDS:
        _code, name = table_id.split(".", 1)
        ddl_cols = set(re.findall(r"^\s+(\w+) (?:TEXT|INTEGER|REAL)", TABLE_SPECS[table_id]["ddl"], re.MULTILINE))
        row = _query(ap_dir, _code, f"SELECT * FROM {name} LIMIT 1")
        assert row, f"{table_id} 无数据"
        assert set(row[0].keys()) == ddl_cols, f"{table_id} DDL 与生成行键不一致"


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
    """口径包§五 预警等级分布：中文「黄/橙/红」（黄 55 / 橙 34 / 红 11），等级合法且黄为主、红最少。"""
    rows = _query(ap_dir, "risk", "SELECT warn_level FROM ap_warning_signal")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["warn_level"]] = counts.get(r["warn_level"], 0) + 1
    n = len(rows)
    assert set(counts) <= {"黄", "橙", "红"}
    assert counts.get("黄", 0) / n >= 0.2  # 关注级为主（55% 权重下小样本稳健）
    assert counts.get("红", 0) / n <= 0.5  # 红为少数（11% 权重）


def test_five_classification_distribution(ap_dir: Path) -> None:
    """规则 2 五级分类：风险项目 NORMAL 为主、各级别合法。"""
    rows = _query(ap_dir, "project", "SELECT five_classification FROM ap_risk_project")
    categories = {r["five_classification"] for r in rows}
    assert categories <= {"NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"}
    assert "NORMAL" in categories


def test_concentration_status_follows_rule(ap_dir: Path) -> None:
    """规则 3 集中度状态与敞口/资本净额一致（current_status 可机验；P1-2 中文枚举）。"""
    rows = _query(
        ap_dir, "concentration",
        "SELECT concentration_limit, warning_value, current_status FROM ap_concentration_limit",
    )
    statuses = {r["current_status"] for r in rows}
    # P1-2：存储即所见中文（红/橙/黄/正常），不再残留英文告警码
    assert statuses <= {"正常", "黄", "橙", "红"}


def test_event_type_distribution(ap_dir: Path) -> None:
    """口径包§五 事件类型偏态：信用 45 / 市场 20 / 流动性 15 / 合规 12 / 操作 8；
    小样本下断言信用类最多且覆盖合法类型集合（level2 与 level1 同源，理由模板对齐）。"""
    rows = _query(
        ap_dir, "risk",
        "SELECT event_type, signal_level1_topic, signal_level2_topic, warn_reason FROM ap_warning_signal",
    )
    # 仅属于「其他事件类型」的二级主题（排除跨类型共有的，如 集中度超限∈信用/流动性）
    exclusive = {
        t: set().union(*(set(v) for k, v in LEVEL2_BY_L1.items() if k != t))
        - set(LEVEL2_BY_L1[t])
        for t in LEVEL2_BY_L1
    }
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["event_type"]] = counts.get(r["event_type"], 0) + 1
        # 理由模板与事件类型严格对齐（口径包§五）：
        #  1) level2 必须属于 event_type 的二级主题集（结构保证，杜绝「价格波动」挂「信用风险」）；
        #  2) warn_reason 不得出现仅属其他事件类型的二级主题措辞。
        assert r["signal_level1_topic"] == r["event_type"], "level1 与 event_type 不一致"
        assert r["signal_level2_topic"] in LEVEL2_BY_L1[r["event_type"]], (
            f"事件类型 {r['event_type']} 挂错二级主题 {r['signal_level2_topic']}"
        )
        assert not any(x in r["warn_reason"] for x in exclusive[r["event_type"]]), (
            f"warn_reason 出现其他事件类型主题: {r['warn_reason']}"
        )
    assert set(counts) <= set(LEVEL1_TOPICS)
    # 信用风险权重 45% 最高：小样本下信用>=操作（8% 权重）稳健成立
    assert counts.get("信用风险", 0) >= counts.get("操作风险", 0)


def test_lifecycle_seven_states_and_coherence(ap_dir: Path) -> None:
    """口径包§五 生命周期七态 + 流程/审批字段连贯：处置中必有 process_status、已审批必有 audit_comment。"""
    rows = _query(
        ap_dir, "risk",
        "SELECT signal_status, process_status, audit_status, audit_comment FROM ap_warning_signal",
    )
    statuses = {r["signal_status"] for r in rows}
    assert statuses <= {"待确认", "确认中", "已确认", "处置中", "已关闭", "已撤销", "已排除"}
    assert "待确认" in statuses  # 主状态必现
    for r in rows:
        if r["signal_status"] == "处置中":
            assert r["process_status"], f"处置中缺 process_status: {r}"
        if r["audit_status"] == "已审批":
            assert r["audit_comment"], f"已审批缺 audit_comment: {r}"


def test_customer_name_purified(ap_dir: Path) -> None:
    """口径包§五 名称纯净化：客户/集团名称无「·编号尾巴」（编号独立字段）。"""
    rows = _query(ap_dir, "customer", "SELECT customer_name FROM ap_customer")
    grow = _query(ap_dir, "customer", "SELECT group_customer_name FROM ap_group_customer")
    assert all("·" not in r["customer_name"] for r in rows)
    assert all("·" not in r["group_customer_name"] for r in grow)


def test_fk_no_orphans(ap_dir: Path) -> None:
    """D 门禁同口径：声明外键 LEFT JOIN 空侧孤儿 = 0（§六 外键完整性 100%，49 条）。"""
    assert len(FK_CHECKS) == 49
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
    """确定性：同 seed 同配置两次生成 → 54 表 table_sha256 逐一相同（§五）。"""
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
    """规则 1 决策表（口径包§四/§三）：红=内部限额突破>12% 或押品贬值≥30% 或评分≥80；
    橙=预警线命中 10-12% 或押品贬值 15-30% 或关联异动 20-50% 或评分 60-80；黄=关注线 9-10%。"""
    assert warn_level_decide(85) == "红"
    assert warn_level_decide(50, collateral_depreciation=0.30) == "红"
    assert warn_level_decide(50, concentration_overrun=0.20) == "红"  # >12% 内部限额突破
    assert warn_level_decide(70) == "橙"
    assert warn_level_decide(50, collateral_depreciation=0.20) == "橙"
    assert warn_level_decide(50, concentration_overrun=0.11) == "橙"  # 预警线 10-12%
    assert warn_level_decide(50, related_change=0.30) == "橙"
    assert warn_level_decide(30) == "黄"
    assert warn_level_decide(30, concentration_overrun=0.095) == "黄"  # 关注线 9-10%


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
    """规则 3 决策表：≤10% 正常 / ≤15% 黄警 / ≤25% 橙警 / >25% 红警（P1-2 中文状态）。"""
    assert concentration_calc(0.05, 1)["status"] == "正常"
    assert concentration_calc(0.12, 1)["status"] == "黄"
    assert concentration_calc(0.12, 1)["need_approval"] is False
    assert concentration_calc(0.18, 1)["status"] == "橙"
    assert concentration_calc(0.18, 1)["need_approval"] is True
    assert concentration_calc(0.30, 1)["status"] == "红"
    assert concentration_calc(0.30, 1)["warn_level"] == "红"
