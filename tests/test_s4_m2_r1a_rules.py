"""S4 M2 增量测试：R1a 集团层归集集中度引擎 + R2 关联纳入重算 + 三动作规则校验挂接。

只跑本文件（增量，禁全量 pytest）：
    /opt/anaconda3/bin/python3 -m pytest tests/test_s4_m2_r1a_rules.py -q

覆盖（口径包 v0.3 §三/§七）：
- 阈值配置从 base.ap_sys_param 读取（禁硬编码），缺失 fail-closed；
- 三档边界：8.9% 无警 / 9% 黄 / 10% 橙 / 10.8% 橙 / 12% 橙（红须 >12%）/ 12.8% 红；
- R2 重算：天晟 86.4 亿 → 10.8% 橙；+恒昌（三线索）16 亿 → 102.4 亿 → 12.8% 红；
- 三动作校验挂接：升级红须 >12% 命中（否则拒绝并给规则依据）；confirm/submit 与 R1a 一致。

数据源 = ap_anping 真实库（只读）；动作校验走 dry_run（管道全走、零写回），源库零变更。
"""

from __future__ import annotations

import pytest

from src.runtime.risk_actions_impl import build_risk_engine
from src.runtime.risk_db import RiskStore
from src.runtime.risk_rules import (
    RESERVED_RULES,
    R1aConfig,
    RuleConfigError,
    check_adjust_level,
    check_level_consistency,
    evaluate,
    evaluate_warning,
    governing_level,
    is_r1a_governed,
    level_for_ratio,
)

TIANSHENG = "天晟集团有限公司"
RUIHUA = "瑞华能源集团有限公司"
TS_ORANGE = "WS-2026-90000001"  # 天晟 橙（R1a 自身口径）
TS_RED = "WS-2026-90000002"  # 天晟 红（R1a+R2）
RH_YELLOW = "WS-2026-90000003"  # 瑞华 黄


@pytest.fixture(scope="module")
def conn():
    store = RiskStore()
    c = store.source_conn()
    yield c
    c.close()


@pytest.fixture(scope="module")
def engine(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("s4m2_ontology")
    store = RiskStore(ontology_path=tmp / "ontology.db")
    eng = build_risk_engine(store=store)
    return eng


# ---------------------------------------------------------------------------
# 1. 阈值配置（base.ap_sys_param，禁硬编码）
# ---------------------------------------------------------------------------


def test_config_loaded_from_sys_param(conn) -> None:
    cfg = R1aConfig.load(conn)
    assert cfg.concern_line == pytest.approx(0.09)
    assert cfg.warn_line == pytest.approx(0.10)
    assert cfg.internal_limit == pytest.approx(0.12)
    assert cfg.group_capital_yi == pytest.approx(800.0)
    # 来源留痕：三线参数来自 R1A_LINE 类型
    assert cfg.source["CAP_CONCERN_LINE"] == "0.09"


def test_config_missing_param_fails_closed() -> None:
    with pytest.raises(RuleConfigError):
        R1aConfig.from_sys_param({"CAP_CONCERN_LINE": "0.09"})


# ---------------------------------------------------------------------------
# 2. 三档边界（8.9 无警 / 9 黄 / 10 橙 / 12 橙 / 12.8 红）
# ---------------------------------------------------------------------------


def test_level_boundaries() -> None:
    cfg = R1aConfig(
        concern_line=0.09, warn_line=0.10, internal_limit=0.12, group_capital_yi=800.0
    )
    assert level_for_ratio(0.089, cfg) == "无"  # 关注线以下不触发
    assert level_for_ratio(0.09, cfg) == "黄"  # ≥9% 黄
    assert level_for_ratio(0.10, cfg) == "橙"  # ≥10% 橙
    assert level_for_ratio(0.108, cfg) == "橙"  # 天晟 10.8% 橙
    assert level_for_ratio(0.12, cfg) == "橙"  # 12% 仍橙（红须 >12%）
    assert level_for_ratio(0.128, cfg) == "红"  # 12.8% 红


# ---------------------------------------------------------------------------
# 3. 引擎实算（与库内道具一致）+ R2 重算
# ---------------------------------------------------------------------------


def test_tiansheng_r1a_only(conn) -> None:
    res = evaluate(conn, TIANSHENG, include_related=False)
    assert res.base_aggregation_yi == pytest.approx(86.4)
    assert res.related_balance_yi == pytest.approx(0.0)
    assert res.ratio == pytest.approx(0.108)
    assert res.level == "橙"


def test_tiansheng_r2_recompute(conn) -> None:
    res = evaluate(conn, TIANSHENG, include_related=True)
    # R2 关联纳入：恒昌贸易 16 亿，三线索交叉
    assert any("恒昌" in p.customer_name for p in res.related_parties)
    hc = next(p for p in res.related_parties if "恒昌" in p.customer_name)
    assert hc.balance_yi == pytest.approx(16.0)
    assert len(hc.clues) == 3  # 股权代持/交叉担保/资金往来
    assert res.related_balance_yi == pytest.approx(16.0)
    assert res.total_yi == pytest.approx(102.4)
    assert res.ratio == pytest.approx(0.128)
    assert res.level == "红"


def test_ruihua_yellow(conn) -> None:
    res = evaluate(conn, RUIHUA, include_related=True)
    assert res.total_yi == pytest.approx(75.2)
    assert res.ratio == pytest.approx(0.094)
    assert res.level == "黄"


def test_evaluate_warning_group_resolution(conn) -> None:
    r1a, r1a_r2 = evaluate_warning(
        conn, {"belong_group": TIANSHENG, "warn_reason": "x"}
    )
    assert r1a.level == "橙"
    assert r1a_r2.level == "红"


# ---------------------------------------------------------------------------
# 4. 作用域标记与管辖级别
# ---------------------------------------------------------------------------


def test_r1a_governed_marker() -> None:
    assert is_r1a_governed(
        {"warn_reason": "10.8% 触发橙色预警（R1a 集团层归集集中度）"}
    )
    # F8：RNG 浓度类事由已剥离「集团集中度敞口超限」→ 监测语气「集团集中度指标异动」
    assert not is_r1a_governed({"warn_reason": "集团集中度指标异动，触发橙色预警"})


def test_governing_level() -> None:
    # reason 引用 R2 → 全口径 R1a+R2；否则 R1a 自身口径
    assert (
        governing_level({"warn_reason": "（R1a+R2 关联客户组归集）"}, "橙", "红")
        == "红"
    )
    assert (
        governing_level({"warn_reason": "（R1a 集团层归集集中度）"}, "橙", "红") == "橙"
    )


# ---------------------------------------------------------------------------
# 5. 纯函数校验：升级红须 >12% 命中 / 一致性
# ---------------------------------------------------------------------------


def _cfg() -> R1aConfig:
    return R1aConfig(
        concern_line=0.09, warn_line=0.10, internal_limit=0.12, group_capital_yi=800.0
    )


def test_check_adjust_level_reject_when_below_red() -> None:
    cfg = _cfg()
    from src.runtime.risk_rules import R1aResult

    rui = R1aResult(
        group_name=RUIHUA,
        base_aggregation_yi=75.2,
        related_balance_yi=0.0,
        total_yi=75.2,
        ratio=0.094,
        level="黄",
        config=cfg,
    )
    v = check_adjust_level(rui, "红")
    assert v is not None
    assert v.error_code == "WARNING_LEVEL_NOT_SUPPORTED_BY_R1A"
    assert "9.4%" in v.detail["basis"] and "内部限额" in v.detail["basis"]


def test_check_adjust_level_allow_when_red_hit() -> None:
    cfg = _cfg()
    from src.runtime.risk_rules import R1aResult

    ts = R1aResult(
        group_name=TIANSHENG,
        base_aggregation_yi=86.4,
        related_balance_yi=16.0,
        total_yi=102.4,
        ratio=0.128,
        level="红",
        config=cfg,
    )
    assert check_adjust_level(ts, "红") is None  # 12.8% > 12% 命中 → 允许
    assert check_adjust_level(ts, "橙") is None  # 降级/同级均允许


def test_check_consistency() -> None:
    cfg = _cfg()
    from src.runtime.risk_rules import R1aResult

    ts_r1a = R1aResult(TIANSHENG, 86.4, 0.0, 86.4, 0.108, "橙", cfg)
    ts_r2 = R1aResult(TIANSHENG, 86.4, 16.0, 102.4, 0.128, "红", cfg)
    assert check_level_consistency("橙", "橙", ts_r1a, ts_r2) is None
    v = check_level_consistency("红", "橙", ts_r1a, ts_r2)  # 存橙但 R1a+R2 管辖红
    assert v is not None and v.error_code == "WARNING_LEVEL_INCONSISTENT_WITH_R1A"


# ---------------------------------------------------------------------------
# 6. 动作校验挂接（dry_run：管道全走、零写回、源库零变更）
# ---------------------------------------------------------------------------


def test_action_adjust_upgrade_to_red_rejected_with_rule_basis(engine) -> None:
    res = engine.execute(
        "adjust_warning_level",
        {"warning_id": RH_YELLOW, "new_level": "红", "reason": "t"},
        actor="human",
        dry_run=True,
    )
    assert res.outcome == "rejected"
    assert res.error_code == "WARNING_LEVEL_NOT_SUPPORTED_BY_R1A"
    assert res.detail["ratio"] == pytest.approx(0.094)
    assert "9.4%" in res.detail["basis"]  # 拒绝给规则依据


def test_action_adjust_upgrade_to_red_allowed_by_r2(engine) -> None:
    # 天晟 橙→红：R1a+R2=12.8% 红 支持升级 → R1a 门通过，落到状态门（信号处置中）
    res = engine.execute(
        "adjust_warning_level",
        {"warning_id": TS_ORANGE, "new_level": "红", "reason": "R2 纳入重算"},
        actor="human",
        dry_run=True,
    )
    assert res.error_code != "WARNING_LEVEL_NOT_SUPPORTED_BY_R1A"
    assert res.error_code == "WARNING_NOT_ADJUSTABLE"


def test_action_confirm_and_submit_consistent_with_r1a(engine) -> None:
    # confirm：天晟橙（R1a 管辖=橙）一致 → R1a 门通过，落状态门
    c = engine.execute(
        "confirm_warning", {"warning_id": TS_ORANGE}, actor="human", dry_run=True
    )
    assert c.error_code != "WARNING_LEVEL_INCONSISTENT_WITH_R1A"
    assert c.error_code == "WARNING_NOT_CONFIRMABLE"
    # submit：天晟橙 关联信号一致 → R1a 门通过，落状态门
    s = engine.execute(
        "submit_disposal",
        {
            "disposal_id": "WD-2026-900001",
            "deal_type": "PUSH_SUBSIDIARY",
            "comment": "t",
        },
        actor="human",
        dry_run=True,
    )
    assert s.error_code != "WARNING_LEVEL_INCONSISTENT_WITH_R1A"
    assert s.error_code == "DISPOSAL_NOT_SUBMITTABLE"


def test_dry_run_does_not_mutate_source(engine, conn) -> None:
    before = conn.execute(
        "SELECT warn_level FROM ap_warning_signal WHERE warning_id=?", (RH_YELLOW,)
    ).fetchone()[0]
    engine.execute(
        "adjust_warning_level",
        {"warning_id": RH_YELLOW, "new_level": "红", "reason": "t"},
        actor="human",
        dry_run=True,
    )
    after = conn.execute(
        "SELECT warn_level FROM ap_warning_signal WHERE warning_id=?", (RH_YELLOW,)
    ).fetchone()[0]
    assert before == after


# ---------------------------------------------------------------------------
# 7. 预留规则登记（R1b/R3-R6 只注册不注册，防过度设计）
# ---------------------------------------------------------------------------


def test_reserved_rules_registered() -> None:
    ids = [r[0] for r in RESERVED_RULES]
    assert ids == ["R1b", "R3", "R4", "R5", "R6"]
