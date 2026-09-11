"""主动洞察规则引擎（T-U2，UX v0.2 US2）：统计规则检测，非 LLM（Tableau Pulse 模式，B2）。

三条规则（全部日环比、近 7 日窗、最小样本 5 日）：
- channel_day_over_day    渠道日环比突变：单渠道末日 vs 前一有数日，|环比| ≥ 阈值；
- total_day_over_day      总量突变：全渠道合计同口径对比；
- contribution_day_over_day 贡献度突变：单渠道占比（%）的相对变化 ≥ 阈值。

铁律：
- 规则命中才出洞察，无命中不出卡（宁缺毋滥，禁止凑数）；
- 只报事实不归因（无事件日历，因果沉默=诚实铁律）；
- 阈值为模块级数值常量（NC-U2 裁决默认，可配）；端点零请求参数，
  无用户输入进查询——时间边界走绑定参数、标识符来自注册表绑定（防注入）。

数据源：镜像库（config.MIRROR_DB）只读；查询经 fortune_semantic.compiler
（单一来源：表名/列名/过滤全部注册表绑定，禁止本地复制）。
"""

import datetime as dt
from pathlib import Path

from src.fortune_semantic.compiler import QueryRequest, run_query
from src.fortune_semantic.registry import REGISTRY
from src.semantic import config

# ---- 阈值常量（NC-U2 已裁决默认值；调这里即全局生效）----
DELTA_PCT_THRESHOLD = 30.0   # |日环比| ≥ 30%
WINDOW_DAYS = 7              # 近 7 日
MIN_SAMPLE_DAYS = 5          # 窗口内最少有数天数（不足不出卡）
MAX_INSIGHTS = 3             # 置顶卡上限（防卡海，按 |环比| 降序取前 N）

# 洞察锚定口径：主度量 + 渠道维度（注册表单一来源，勿本地复制表名列名）
MEASURE_ID = "reg_user_cnt"
CHANNEL_DIM = "channel_l2"

_TIME_GRAIN_DAY = "time_grain=day"  # 编译器日粒度维度条目（grains 注册值）


def _metric_label() -> str:
    """度量人话名（description 冒号前段，与注册表单一来源）。"""
    return REGISTRY.get_measure(MEASURE_ID).description.split("：", 1)[0]


def _daily_series(conn) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """窗口内 (渠道, 日) 序列与总量序列：{日: {渠道: 值}} / {日: 总量}。"""
    measure = REGISTRY.get_measure(MEASURE_ID)
    row = conn.execute(
        f"SELECT CAST(MAX({measure.time_field}) AS DATE) FROM {measure.source_table}"
    ).fetchone()
    if row is None or row[0] is None:
        return {}, {}  # 空库：无锚日 → 无洞察（兜底态）
    anchor = row[0] if isinstance(row[0], dt.date) else dt.date.fromisoformat(str(row[0]))
    # 数据末日为参照日（镜像为静态快照，不锚"今天"）；窗口 = 参照日往前 WINDOW_DAYS 天
    window_from = (anchor - dt.timedelta(days=WINDOW_DAYS - 1)).isoformat()
    window_to = anchor.isoformat()

    def _request(dimensions: tuple[str, ...]) -> QueryRequest:
        return QueryRequest(
            measure=MEASURE_ID, dimensions=dimensions,
            time_from=window_from, time_to=window_to,
        )

    by_channel: dict[str, dict[str, float]] = {}
    for channel, day, value in run_query(_request((CHANNEL_DIM, _TIME_GRAIN_DAY)), conn=conn)["rows"]:
        if channel is None:
            continue  # 未匹配渠道的明细计入总量序列，不参与点名规则
        by_channel.setdefault(str(day), {})[channel] = float(value)
    totals: dict[str, float] = {}
    for day, value in run_query(_request((_TIME_GRAIN_DAY,)), conn=conn)["rows"]:
        totals[str(day)] = float(value)
    return by_channel, totals


def _pct_change(current: float, baseline: float) -> float | None:
    """环比百分比（基线 ≤ 0 不算，避免除零与无意义方向）。"""
    if baseline <= 0:
        return None
    return round((current - baseline) / baseline * 100, 1)


def _num(value: float) -> float | int:
    """整数值计数存 int（35 而非 35.0），小数占比保留浮点。"""
    return int(value) if float(value).is_integer() else value


def _insight(
    type_: str, channel: str | None, current: float, baseline: float,
    delta_pct: float, by_channel_dim: bool, days: list[str],
) -> dict:
    """B3 冻结契约的一条洞察（字段名勿改；drilldown 供「看分解」走既有语义接口）。"""
    return {
        "type": type_,
        "channel": channel,
        "metric": _metric_label(),
        "current": _num(current),
        "baseline": _num(baseline),
        "delta_pct": delta_pct,
        "drilldown": {
            "measure": MEASURE_ID,
            "dimensions": [CHANNEL_DIM] if by_channel_dim else [],
            "time": {"from": days[0], "to": days[-1]},
        },
    }


def detect_insights(db_path: Path | None = None) -> list[dict]:
    """规则检测入口：命中列表按 |环比| 降序（上限 MAX_INSIGHTS）；无命中 → []。

    连接失败由调用方处理（端点转兜底态），本函数不吞异常（不静默）。
    """
    import duckdb

    path = db_path or config.MIRROR_DB
    conn = duckdb.connect(str(path), read_only=True)
    try:
        by_channel, totals = _daily_series(conn)
    finally:
        conn.close()

    days = sorted(totals)  # 有数日升序
    if len(days) < MIN_SAMPLE_DAYS:
        return []  # 样本不足：宁缺毋滥
    cur_day, prev_day = days[-1], days[-2]

    found: list[dict] = []
    threshold = DELTA_PCT_THRESHOLD
    total_cur, total_prev = totals[cur_day], totals[prev_day]

    total_delta = _pct_change(total_cur, total_prev)
    if total_delta is not None and abs(total_delta) >= threshold:
        found.append(_insight(
            "total_day_over_day", None, total_cur, total_prev, total_delta,
            by_channel_dim=False, days=days,
        ))

    for channel in sorted(by_channel.get(cur_day, {})):
        c_cur = by_channel[cur_day].get(channel, 0.0)
        c_prev = by_channel[prev_day].get(channel, 0.0)
        if c_cur <= 0 or c_prev <= 0:
            continue  # 缺数/零值不出卡（不猜）
        delta = _pct_change(c_cur, c_prev)
        if delta is not None and abs(delta) >= threshold:
            found.append(_insight(
                "channel_day_over_day", channel, c_cur, c_prev, delta,
                by_channel_dim=True, days=days,
            ))
        # 贡献度：占比（%）的相对变化；总量缺失/为 0 时不算（不猜）
        if total_cur <= 0 or total_prev <= 0:
            continue
        share_cur = c_cur / total_cur * 100
        share_prev = c_prev / total_prev * 100
        share_delta = _pct_change(share_cur, share_prev)
        if share_delta is not None and abs(share_delta) >= threshold:
            found.append(_insight(
                "contribution_day_over_day", channel,
                round(share_cur, 1), round(share_prev, 1), share_delta,
                by_channel_dim=True, days=days,
            ))

    found.sort(key=lambda i: abs(i["delta_pct"]), reverse=True)
    return found[:MAX_INSIGHTS]
