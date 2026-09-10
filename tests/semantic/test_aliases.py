"""M1 别名层测试：候选展开正确性 + 全半角归一 + 长词优先消费 + 值加载降级。

问法样例取自 tests/fixtures/问法压力测试集_v0.1.json（30 条）。
"""

from pathlib import Path

import pytest

from src.fortune_semantic.registry import REGISTRY
from src.semantic import aliases
from src.semantic.aliases import (
    ALIAS_TABLE,
    BUILTIN_CHANNEL_VALUES,
    expand_candidates,
    normalize_text,
)

MIRROR_DB = (
    Path(aliases.__file__).resolve().parents[2] / "data" / "fortune_mirror.duckdb"
)


@pytest.fixture(autouse=True)
def _fresh_value_cache():
    """用例前后清渠道值缓存：MIRROR_DB 打桩互不污染，不外溢到其他测试模块。"""
    aliases._channel_values.cache_clear()
    yield
    aliases._channel_values.cache_clear()


# ----------------------------------------------------------------------
# normalize_text：全半角 / 空白 / 大小写归一
# ----------------------------------------------------------------------


def test_normalize_fullwidth_plus():
    assert normalize_text("优享＋线上渠道") == "优享+线上渠道"


def test_normalize_strips_whitespace_and_fullwidth_digits():
    assert normalize_text("８月１号 到　３１号 注册") == "8月1号到31号注册"


def test_normalize_lowercases_ascii():
    assert normalize_text("银行APP注册") == "银行app注册"
    assert normalize_text("优享 PLUS 渠道") == "优享plus渠道"


# ----------------------------------------------------------------------
# ALIAS_TABLE 资产形状（契约：按类别查询 + 目标全部已注册）
# ----------------------------------------------------------------------


def test_alias_table_shape():
    assert set(ALIAS_TABLE) == {"measure", "dimension", "value"}
    for table in ALIAS_TABLE.values():
        for keyword, targets in table.items():
            assert isinstance(targets, tuple) and targets
            assert all(isinstance(t, str) for t in targets)
            assert normalize_text(keyword) == keyword  # 关键词已归一


def test_targets_all_registered():
    for targets in ALIAS_TABLE["measure"].values():
        for target in targets:
            assert target in REGISTRY.measures or target in REGISTRY.ratios
    for targets in ALIAS_TABLE["dimension"].values():
        for target in targets:
            assert target.split("=")[0] in REGISTRY.dimensions


# ----------------------------------------------------------------------
# expand_candidates：度量口语
# ----------------------------------------------------------------------


def test_registration_colloquial_phrases():
    for question in (
        "上个月注册了多少人",
        "8月1号到31号新增用户有多少",
        "2026年8月各渠道注册用户数",
        "帮我看下上个月各渠道新增注册",
    ):
        assert "reg_user_cnt" in expand_candidates(question)["measure_hints"]


def test_laile_duoshao_with_mcdonald_value():
    hints = expand_candidates("8月麦当劳来了多少人")
    assert hints == {
        "measure_hints": ["reg_user_cnt"],
        "dimension_hints": [],
        "value_hints": ["麦当劳"],
    }


def test_real_name_active_since_t2_registered():
    assert expand_candidates("8月实名了多少人")["measure_hints"] == [
        "real_name_user_cnt"
    ]


def test_auth_measure_with_generic_channel():
    hints = expand_candidates("上个月授权用户数分渠道")
    assert hints["measure_hints"] == ["auth_user_cnt"]
    assert hints["dimension_hints"] == ["channel_l2"]
    assert hints["value_hints"] == []


def test_ratio_longest_match_wins():
    # "注册到实名的转化率" 长词整体消费，不得再命中裸"转化率"导致双候选
    assert expand_candidates("注册到实名的转化率")["measure_hints"] == [
        "reg_to_real_rate"
    ]


def test_bare_ratio_yields_two_candidates():
    assert expand_candidates("转化率是多少")["measure_hints"] == [
        "reg_to_real_rate",
        "reg_to_auth_rate",
    ]


# ----------------------------------------------------------------------
# expand_candidates：维度口语
# ----------------------------------------------------------------------


def test_gender_variants():
    assert expand_candidates("注册的男女比例")["dimension_hints"] == ["gender"]
    assert expand_candidates("男的和女的注册各多少")["dimension_hints"] == ["gender"]


def test_l1_not_polluted_by_generic_channel():
    # "一级渠道" 长词优先消费，裸"渠道"不得再命中（避免假性多候选）
    hints = expand_candidates("分一级渠道统计下注册数")
    assert hints["dimension_hints"] == ["channel_l1"]
    assert hints["measure_hints"] == ["reg_user_cnt"]


def test_generic_channel_variants():
    assert expand_candidates("2026年8月各渠道注册用户数")["dimension_hints"] == [
        "channel_l2"
    ]
    assert expand_candidates("8月份注册人数按二级渠道分")["dimension_hints"] == [
        "channel_l2"
    ]


def test_time_grain_hints():
    assert expand_candidates("注册用户数 月度")["dimension_hints"] == [
        "time_grain=month"
    ]
    # 粒度词与趋势词并存 → 双候选属设计（裁决在路由层）
    assert set(expand_candidates("按周看看注册趋势")["dimension_hints"]) == {
        "time_grain=week",
        "time_grain=day",
    }
    assert expand_candidates("8月每天注册多少人")["dimension_hints"] == [
        "time_grain=day"
    ]


# ----------------------------------------------------------------------
# expand_candidates：渠道值变体（含特殊字符"优享+"）
# ----------------------------------------------------------------------


def test_youxiang_plus_variants():
    assert expand_candidates("优享plus渠道注册了多少")["value_hints"] == ["优享+线上"]
    # 全角＋经 NFKC 归一后命中规范值本身
    assert expand_candidates("优享＋线上渠道注册用户数")["value_hints"] == ["优享+线上"]


def test_youxiang_bare_yields_two_candidates():
    assert expand_candidates("优享+注册了多少")["value_hints"] == [
        "优享+线上",
        "优享+企微",
    ]


def test_jinjimen_maps_to_mcdonald():
    assert expand_candidates("金拱门注册了多少")["value_hints"] == ["麦当劳"]


def test_no_double_fire_on_overlap():
    # "优享+线上" 消费后，裸 "优享+" 不再命中
    assert expand_candidates("优享+线上")["value_hints"] == ["优享+线上"]


# ----------------------------------------------------------------------
# 渠道值加载：镜像实查 + 不可达降级
# ----------------------------------------------------------------------


@pytest.mark.skipif(not MIRROR_DB.exists(), reason="镜像库不存在（本地数据未就绪）")
def test_channel_values_loaded_from_mirror():
    values = aliases._channel_values()
    assert len(values) >= 20
    assert "麦当劳" in values  # sec
    assert "中信集团" in values  # fst
    assert "优享+线上" in values


def test_channel_values_fallback_when_mirror_unreachable(tmp_path, monkeypatch):
    monkeypatch.setattr(aliases.config, "MIRROR_DB", tmp_path / "missing.duckdb")
    assert aliases._channel_values() == BUILTIN_CHANNEL_VALUES
    assert "金拱门" not in BUILTIN_CHANNEL_VALUES  # 兜底名单是规范值而非别名


# ----------------------------------------------------------------------
# 边界：域外问题 / 空串
# ----------------------------------------------------------------------


def test_out_of_scope_question_yields_no_hints():
    empty = {"measure_hints": [], "dimension_hints": [], "value_hints": []}
    assert expand_candidates("今天天气怎么样") == empty
    assert expand_candidates("注册用户资产规模")["measure_hints"] == ["reg_user_cnt"]
    assert expand_candidates("注册用户资产规模")["dimension_hints"] == []


def test_empty_question_yields_no_hints():
    empty = {"measure_hints": [], "dimension_hints": [], "value_hints": []}
    assert expand_candidates("") == empty
