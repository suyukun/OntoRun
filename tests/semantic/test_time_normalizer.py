"""M2 时间解析器测试：槽位→区间确定性 + 中文表达覆盖（≥25 种）+ 边界。

锚点 today = 2026-09-10（周四，与压力测试集/镜像分区 2026-08-31 对齐）。
中文表达列只做"表达 → 标准槽位"的约定记录（槽位抽取属 LLM/M5），
区间计算断言本模块结果。
"""

import re
from datetime import date

import pytest

from src.semantic.time_normalizer import normalize_time

TODAY = date(2026, 9, 10)
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")

# (中文表达, LLM 标准槽位, (time_from, time_to))
EXPRESSIONS = [
    ("上个月", {"mode": "prev_month"}, ("2026-08-01", "2026-08-31")),
    ("上月", {"mode": "prev_month"}, ("2026-08-01", "2026-08-31")),
    ("这个月", {"mode": "this_month"}, ("2026-09-01", "2026-09-10")),
    ("本月", {"mode": "this_month"}, ("2026-09-01", "2026-09-10")),
    ("当月", {"mode": "this_month"}, ("2026-09-01", "2026-09-10")),
    ("月初至今", {"mode": "this_month"}, ("2026-09-01", "2026-09-10")),
    ("上礼拜", {"mode": "prev_week"}, ("2026-08-31", "2026-09-06")),
    ("上周", {"mode": "prev_week"}, ("2026-08-31", "2026-09-06")),
    ("这周", {"mode": "this_week"}, ("2026-09-07", "2026-09-10")),
    ("本周", {"mode": "this_week"}, ("2026-09-07", "2026-09-10")),
    ("这个礼拜", {"mode": "this_week"}, ("2026-09-07", "2026-09-10")),
    ("最近7天", {"mode": "last_n_days", "n": 7}, ("2026-09-04", "2026-09-10")),
    ("近7天", {"mode": "last_n_days", "n": 7}, ("2026-09-04", "2026-09-10")),
    ("最近30天", {"mode": "last_n_days", "n": 30}, ("2026-08-12", "2026-09-10")),
    ("近30日", {"mode": "last_n_days", "n": 30}, ("2026-08-12", "2026-09-10")),
    ("过去14天", {"mode": "last_n_days", "n": 14}, ("2026-08-28", "2026-09-10")),
    ("今天", {"mode": "today"}, ("2026-09-10", "2026-09-10")),
    ("今日", {"mode": "today"}, ("2026-09-10", "2026-09-10")),
    ("昨天", {"mode": "yesterday"}, ("2026-09-09", "2026-09-09")),
    ("昨日", {"mode": "yesterday"}, ("2026-09-09", "2026-09-09")),
    ("今年", {"mode": "this_year"}, ("2026-01-01", "2026-09-10")),
    ("去年", {"mode": "prev_year"}, ("2025-01-01", "2025-12-31")),
    ("上半年", {"mode": "half_of", "ref": "2026-H1"}, ("2026-01-01", "2026-06-30")),
    ("下半年", {"mode": "half_of", "ref": "H2"}, ("2026-07-01", "2026-12-31")),
    ("三季度", {"mode": "quarter_of", "ref": "Q3"}, ("2026-07-01", "2026-09-30")),
    ("Q3", {"mode": "quarter_of", "ref": "Q3"}, ("2026-07-01", "2026-09-30")),
    ("q3", {"mode": "quarter_of", "ref": "q3"}, ("2026-07-01", "2026-09-30")),
    ("第三季度", {"mode": "quarter_of", "ref": "Q3"}, ("2026-07-01", "2026-09-30")),
    (
        "2025年四季度",
        {"mode": "quarter_of", "ref": "2025-Q4"},
        ("2025-10-01", "2025-12-31"),
    ),
    ("8月", {"mode": "month_of", "ref": "2026-08"}, ("2026-08-01", "2026-08-31")),
    ("2026年8月", {"mode": "month_of", "ref": "2026-08"}, ("2026-08-01", "2026-08-31")),
    (
        "2024年2月（闰年）",
        {"mode": "month_of", "ref": "2024-02"},
        ("2024-02-01", "2024-02-29"),
    ),
    (
        "8月1号到31号",
        {"mode": "month_of", "ref": "2026-08"},
        ("2026-08-01", "2026-08-31"),
    ),
    ("8月底", {"mode": "month_end", "ref": "2026-08"}, ("2026-08-31", "2026-08-31")),
    ("上月底", {"mode": "month_end", "ref": "2026-08"}, ("2026-08-31", "2026-08-31")),
]


@pytest.mark.parametrize(("expr", "slot", "expected"), EXPRESSIONS)
def test_chinese_expression_coverage(expr, slot, expected):
    """≥25 种中文表达 → 标准槽位 → 确定区间（格式恒 YYYY-MM-DD）。"""
    result = normalize_time(slot, TODAY)
    assert result == {"time_from": expected[0], "time_to": expected[1]}
    assert len(EXPRESSIONS) >= 25


def test_natural_month_vs_rolling_30_days():
    """口径分水岭：'上个月'=自然月整段；'最近30天'=含今日滚动——不同窗口。"""
    prev_month = normalize_time({"mode": "prev_month"}, TODAY)
    rolling = normalize_time({"mode": "last_n_days", "n": 30}, TODAY)
    assert prev_month == {"time_from": "2026-08-01", "time_to": "2026-08-31"}
    assert rolling == {"time_from": "2026-08-12", "time_to": "2026-09-10"}
    assert prev_month != rolling


def test_this_quarter_mtd_but_explicit_ref_is_full_quarter():
    assert normalize_time({"mode": "this_quarter"}, TODAY) == {
        "time_from": "2026-07-01",
        "time_to": "2026-09-10",
    }
    # 显式 ref（含按月推季）→ 完整季度，数据覆盖窗截断交给引擎
    assert normalize_time({"mode": "this_quarter", "ref": "2026-08"}, TODAY) == {
        "time_from": "2026-07-01",
        "time_to": "2026-09-30",
    }


def test_quarter_ref_via_month_and_q4_boundary():
    assert normalize_time({"mode": "quarter_of", "ref": "2026-01"}, TODAY) == {
        "time_from": "2026-01-01",
        "time_to": "2026-03-31",
    }
    assert normalize_time({"mode": "quarter_of", "ref": "2026-Q4"}, TODAY) == {
        "time_from": "2026-10-01",
        "time_to": "2026-12-31",
    }


def test_absolute_passthrough_keeps_format():
    assert normalize_time(
        {"mode": "absolute", "from": "2026-08-01", "to": "2026-08-31"}, TODAY
    ) == {"time_from": "2026-08-01", "time_to": "2026-08-31"}


@pytest.mark.parametrize(
    "slot",
    [
        {"mode": "absolute", "from": "2026-08-10", "to": "2026-08-01"},  # from>to
        {"mode": "absolute", "from": "2026/08/01", "to": "2026-08-31"},  # 格式
        {"mode": "absolute", "from": "2026-08-01", "to": "08-31"},  # 缺年
        {"mode": "absolute", "from": "2026-02-30", "to": "2026-08-31"},  # 非法日
        {"mode": "month_of", "ref": "2026-13"},  # 月份越界
        {"mode": "month_of", "ref": "2026-00"},
        {"mode": "month_of"},  # 缺 ref
        {"mode": "last_n_days", "n": 0},
        {"mode": "last_n_days", "n": -3},
        {"mode": "last_n_days", "n": "7"},
        {"mode": "last_n_days", "n": 7.5},
        {"mode": "last_n_days", "n": True},  # bool 是 int 子类，须拒
        {"mode": "half_of", "ref": "2026-H3"},
        {"mode": "this_year", "ref": "26"},
        {"mode": "warp_speed"},  # 未知模式
        {"mode": 123},
        "2026-08",  # 槽位非 dict
        None,
    ],
)
def test_invalid_slots_raise_value_error(slot):
    with pytest.raises(ValueError):
        normalize_time(slot, TODAY)


def test_today_must_be_date():
    with pytest.raises(ValueError):
        normalize_time({"mode": "prev_month"}, "2026-09-10")


def test_prev_month_year_boundary():
    result = normalize_time({"mode": "prev_month"}, date(2026, 1, 15))
    assert result == {"time_from": "2025-12-01", "time_to": "2025-12-31"}


def test_prev_week_year_boundary():
    # 2026-01-01 周四 → 上周 = 2025-12-22（周一）~ 2025-12-28（周日）
    result = normalize_time({"mode": "prev_week"}, date(2026, 1, 1))
    assert result == {"time_from": "2025-12-22", "time_to": "2025-12-28"}


def test_leap_year_month_end():
    assert normalize_time({"mode": "month_end", "ref": "2024-02"}, TODAY) == {
        "time_from": "2024-02-29",
        "time_to": "2024-02-29",
    }
    assert normalize_time({"mode": "month_end"}, TODAY) == {
        "time_from": "2026-09-30",
        "time_to": "2026-09-30",
    }


def test_extra_keys_ignored_and_output_always_iso():
    result = normalize_time({"mode": "prev_month", "grain": "day", "x": 1}, TODAY)
    assert set(result) == {"time_from", "time_to"}
    assert ISO.fullmatch(result["time_from"]) and ISO.fullmatch(result["time_to"])
