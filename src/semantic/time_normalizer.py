"""M2 时间解析器：LLM 标准化时间槽 → 真实日期区间（确定性代码）。

链路位置：LLM 只输出标准化时间槽（模式 + 参数），禁止直出日期（DateLogicQA
实证 LLM 直出日期有系统性偏差）；真实区间由本模块计算，失败抛 ValueError，
llm_route 归为可重试错误。

契约（并行任务依赖，勿改名）：
    normalize_time(slot: dict, today: date) -> {"time_from": "YYYY-MM-DD",
                                                "time_to": "YYYY-MM-DD"}
    slot 形态（mode 为键，参数见各 handler；多余键忽略）：
      {"mode": "absolute", "from": "2026-08-01", "to": "2026-08-31"}
      {"mode": "last_n_days", "n": 7}                     # 含今日滚动 N 天
      {"mode": "prev_month"} | {"mode": "this_month", "ref"?: "2026-08"}
      {"mode": "prev_week"} | {"mode": "this_week"}
      {"mode": "today"} | {"mode": "yesterday"}
      {"mode": "this_year", "ref"?: "2026"} | {"mode": "prev_year"}
      {"mode": "this_quarter", "ref"?: "2026-Q3"|"Q3"|"2026-08"}
      {"mode": "quarter_of", "ref": "2026-Q3"|"Q3"|"2026-08"}
      {"mode": "month_of", "ref": "2026-08"} | {"mode": "month_end", "ref"?: "2026-08"}
      {"mode": "half_of", "ref": "2026-H1"|"H2"}

  口语问句补充入口（T-N5）：extract_oral_month(question, today) 把问句里的中文
  数字月份（「八月份」）解析为当月整月真实区间——解析权在代码，不交给 LLM。

口径决策（属口径包，默认自然语义；见 docs/即兴问答鲁棒性方案_v0.1.md M2）：
- 自然期间 vs 滚动窗口："上个月"=自然月整段（2026-08-01~08-31）；
  "最近N天"=含今日的滚动 N 天——两者是不同口径，中文都叫"30天"；
- 进行中期间（this_* 无 ref）= 起点至今日（MTD/YTD，"今年"=~今）；
  带 ref 视为显式历史期间，返回完整期间（数据覆盖窗截断由引擎负责）；
- 周一为一周起点（对齐注册表 time_grain week 口径）；
- "月初至今"=this_month（MTD）；"8月底"=month_end（月末时点，from=to）。
"""

import calendar
import re
from collections.abc import Callable
from datetime import date, timedelta

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_MONTH_RE = re.compile(r"(\d{4})[-/](\d{1,2})")
_QUARTER_RE = re.compile(r"(?:(\d{4})[-/])?q([1-4])", re.IGNORECASE)
_HALF_RE = re.compile(r"(?:(\d{4})[-/])?h([12])", re.IGNORECASE)
_YEAR_RE = re.compile(r"\d{4}")


def _fullmatch(pattern: re.Pattern, text: object) -> re.Match | None:
    if isinstance(text, str):
        return pattern.fullmatch(text.strip())
    return None


def _parse_date(value: object, field: str) -> date:
    match = _fullmatch(_DATE_RE, value)
    if match is None:
        raise ValueError(f"{field} 必须是 YYYY-MM-DD 格式: {value!r}")
    try:
        return date.fromisoformat(match.group(0))
    except ValueError as exc:
        raise ValueError(f"{field} 不是合法日期: {value!r}") from exc


def _parse_year_month(value: object, field: str) -> tuple[int, int]:
    match = _fullmatch(_MONTH_RE, value)
    if match is None:
        raise ValueError(f"{field} 必须是 YYYY-MM 格式: {value!r}")
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        raise ValueError(f"{field} 月份越界(1-12): {value!r}")
    return year, month


def _parse_quarter(value: object, today: date) -> tuple[int, int]:
    """'2026-Q3'/'2026q3'（显式年）、'Q3'（默认当年）、'2026-08'（按月推季度）。"""
    match = _fullmatch(_QUARTER_RE, value)
    if match is not None:
        year = int(match.group(1)) if match.group(1) else today.year
        return year, int(match.group(2))
    year, month = _parse_year_month(value, "ref")
    return year, (month - 1) // 3 + 1


def _month_range(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _quarter_range(year: int, quarter: int) -> tuple[date, date]:
    start_month = 3 * (quarter - 1) + 1
    end_month = start_month + 2
    end = date(year, end_month, calendar.monthrange(year, end_month)[1])
    return date(year, start_month, 1), end


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


def _h_absolute(slot: dict, today: date) -> tuple[date, date]:
    return _parse_date(slot.get("from"), "from"), _parse_date(slot.get("to"), "to")


def _h_last_n_days(slot: dict, today: date) -> tuple[date, date]:
    n = slot.get("n")
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        raise ValueError(f"n 必须是正整数: {n!r}")
    return today - timedelta(days=n - 1), today


def _h_today(slot: dict, today: date) -> tuple[date, date]:
    return today, today


def _h_yesterday(slot: dict, today: date) -> tuple[date, date]:
    day = today - timedelta(days=1)
    return day, day


def _h_this_week(slot: dict, today: date) -> tuple[date, date]:
    return today - timedelta(days=today.weekday()), today


def _h_prev_week(slot: dict, today: date) -> tuple[date, date]:
    monday = today - timedelta(days=today.weekday() + 7)
    return monday, monday + timedelta(days=6)


def _h_this_month(slot: dict, today: date) -> tuple[date, date]:
    if slot.get("ref") is None:  # 本月=月内至今（MTD）
        return date(today.year, today.month, 1), today
    return _month_range(*_parse_year_month(slot.get("ref"), "ref"))


def _h_prev_month(slot: dict, today: date) -> tuple[date, date]:
    return _month_range(*_add_months(today.year, today.month, -1))


def _h_month_of(slot: dict, today: date) -> tuple[date, date]:
    return _month_range(*_parse_year_month(slot.get("ref"), "ref"))


def _h_month_end(slot: dict, today: date) -> tuple[date, date]:
    ref = slot.get("ref")
    year, month = (
        (today.year, today.month) if ref is None else _parse_year_month(ref, "ref")
    )
    end = _month_range(year, month)[1]
    return end, end


def _h_this_quarter(slot: dict, today: date) -> tuple[date, date]:
    ref = slot.get("ref")
    if ref is None:  # 本季度=季内至今
        start_month = 3 * ((today.month - 1) // 3) + 1
        return date(today.year, start_month, 1), today
    return _quarter_range(*_parse_quarter(ref, today))


def _h_quarter_of(slot: dict, today: date) -> tuple[date, date]:
    return _quarter_range(*_parse_quarter(slot.get("ref"), today))


def _h_half_of(slot: dict, today: date) -> tuple[date, date]:
    match = _fullmatch(_HALF_RE, slot.get("ref"))
    if match is None:
        raise ValueError(f"ref 必须是 YYYY-H1/H2 或 H1/H2 格式: {slot.get('ref')!r}")
    year = int(match.group(1)) if match.group(1) else today.year
    start_month = 1 + 6 * (int(match.group(2)) - 1)
    end = date(year, start_month + 5, calendar.monthrange(year, start_month + 5)[1])
    return date(year, start_month, 1), end


def _h_this_year(slot: dict, today: date) -> tuple[date, date]:
    ref = slot.get("ref")
    if ref is None:  # 今年=年内至今（YTD）
        return date(today.year, 1, 1), today
    match = _fullmatch(_YEAR_RE, ref)
    if match is None:
        raise ValueError(f"ref 必须是 YYYY 格式: {ref!r}")
    year = int(match.group(0))
    return date(year, 1, 1), date(year, 12, 31)


def _h_prev_year(slot: dict, today: date) -> tuple[date, date]:
    year = today.year - 1
    return date(year, 1, 1), date(year, 12, 31)


_HANDLERS: dict[str, Callable[[dict, date], tuple[date, date]]] = {
    "absolute": _h_absolute,
    "last_n_days": _h_last_n_days,
    "today": _h_today,
    "yesterday": _h_yesterday,
    "this_week": _h_this_week,
    "prev_week": _h_prev_week,
    "this_month": _h_this_month,
    "prev_month": _h_prev_month,
    "month_of": _h_month_of,
    "month_end": _h_month_end,
    "this_quarter": _h_this_quarter,
    "quarter_of": _h_quarter_of,
    "half_of": _h_half_of,
    "this_year": _h_this_year,
    "prev_year": _h_prev_year,
}


def normalize_time(slot: dict, today: date) -> dict:
    """标准化时间槽 → {"time_from", "time_to"}（恒为 YYYY-MM-DD）。

    未知模式 / 参数非法 / from>to 抛 ValueError（llm_route 归为可重试错误）。
    """
    if not isinstance(slot, dict):
        raise ValueError(f"时间槽必须是 dict: {slot!r}")  # noqa: TRY004 契约统一 ValueError
    if not isinstance(today, date):
        raise ValueError(f"today 必须是 date: {today!r}")  # noqa: TRY004 契约统一 ValueError
    handler = _HANDLERS.get(slot.get("mode"))
    if handler is None:
        known = ", ".join(sorted(_HANDLERS))
        raise ValueError(f"未知时间槽模式: {slot.get('mode')!r}（已知: {known}）")
    start, end = handler(slot, today)
    if start > end:
        raise ValueError(f"时间区间 from>to: {start} > {end}")
    return {"time_from": start.isoformat(), "time_to": end.isoformat()}


# 口语中文数字月份（T-N5「八月份」类语音说法）；数字月份不在此列（引擎
# extract_params 已处理），非常规写法（「廿八」）不猜。
_ORAL_MONTH_RE = re.compile(r"([一二三四五六七八九十]{1,2})月份?")
_ORAL_MONTH_NUM = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "十一": 11,
    "十二": 12,
}


def extract_oral_month(question: str, today: date) -> dict | None:
    """口语问句 → 中文数字月份的真实区间（T-N5）：「八月份」→ 当年 8 月整月。
    无中文数字月份 / 写法不识别 → None（调用方交回既有时间链路，不猜）。"""
    match = _ORAL_MONTH_RE.search(str(question))
    if match is None:
        return None
    month = _ORAL_MONTH_NUM.get(match.group(1))
    if month is None:
        return None
    start, end = _month_range(today.year, month)
    return {"time_from": start.isoformat(), "time_to": end.isoformat()}
