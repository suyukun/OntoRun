"""GET /api/trial/{rule_id} 只读试算装配：语义查询链路 + 当日缓存（T204）。

图表明细同源铁律（B2-4）：数字必须来自查询链路真实执行（compiler.run_query，
与 ChatBI 图表同源），禁止硬编码/静态快照/前端算；语义层 compiler/query
只调用不改。查询链路任何失败 -> 503 {"detail": "trial_unavailable"}
（B3 契约；A4-4 不阻塞确认主流程，内部错误细节不外泄，绝不 500 裸栈）。
当日缓存按日期粒度跨天失效（进程内 dict，B2-4 简单实现，不引外部依赖）。
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException

from src.fortune_admin import ontology
from src.fortune_admin.ontology import TrialResult
from src.fortune_semantic.compiler import parse_request, run_query

router = APIRouter()  # 无 prefix：/api 由 router.py 统一提供，防叠加

# month 查询参数格式：YYYY-MM（缺省当月）。
_MONTH_RE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")

# 规则 -> 试算度量（装配层登记，模式同 ontology._DIVERGENCES：registry 规则
# 块无度量映射字段且语义层只读不改；对应关系取规则描述点名的口径锚度量：
# R1-R4 注册/激活明细规则锚注册用户数，R5/R6 锚实名，R7-R9 锚授权，R10 锚转化率）。
_RULE_MEASURES = {
    "R1": "reg_user_cnt",
    "R2": "reg_user_cnt",
    "R3": "reg_user_cnt",
    "R4": "reg_user_cnt",
    "R5": "real_name_user_cnt",
    "R6": "real_name_user_cnt",
    "R7": "auth_user_cnt",
    "R8": "auth_user_cnt",
    "R9": "auth_user_cnt",
    "R10": "reg_to_real_rate",
}

# 度量 -> 单位（registry 度量无 unit 字段，装配层补齐 TrialResult.unit）。
_MEASURE_UNITS = {
    "reg_user_cnt": "户",
    "real_name_user_cnt": "户",
    "auth_user_cnt": "户",
    "reg_to_real_rate": "%",
    "reg_to_auth_rate": "%",
}

# 当日缓存：(rule_id, month) -> (生效日期, TrialResult)；同参当日二调起
# source="cache"，跨天失效。
_trial_cache: dict[tuple[str, str], tuple[date, TrialResult]] = {}


def _month_range(month: str) -> tuple[str, str]:
    """YYYY-MM ->（首日, 末日）ISO 日期，作为查询链路时间窗。"""
    year, mon = int(month[:4]), int(month[5:7])
    last_day = calendar.monthrange(year, mon)[1]
    return f"{month}-01", f"{month}-{last_day:02d}"


def _query_value(measure_id: str, month: str) -> float:
    """走既有语义查询链路真实算数（唯一取数路径，禁静态快照）。"""
    time_from, time_to = _month_range(month)
    result = run_query(
        parse_request(
            {"measure": measure_id, "time_from": time_from, "time_to": time_to}
        )
    )
    rows = result["rows"]
    if len(rows) != 1 or len(rows[0]) != 1 or rows[0][0] is None:
        # 无分组聚合恒返一行；NULL（比率分母 0/缺失，R10）视为试算不可用
        raise ValueError(f"unexpected trial rows for {measure_id}: {rows!r}")
    return float(rows[0][0])


@router.get("/trial/{rule_id}")
def get_trial(rule_id: str, month: str | None = None) -> TrialResult:
    if month is None:
        month = date.today().strftime("%Y-%m")
    elif not _MONTH_RE.match(month):
        raise HTTPException(422, f"month 格式必须为 YYYY-MM，收到: {month}")

    if rule_id not in ontology.load_registry().rules:
        raise HTTPException(404, f"规则不存在: {rule_id}")

    today = date.today()
    cached = _trial_cache.get((rule_id, month))
    if cached is not None and cached[0] == today:
        return cached[1].model_copy(update={"source": "cache"})

    measure_id = _RULE_MEASURES.get(rule_id)
    if measure_id is None:
        raise HTTPException(503, "trial_unavailable")
    try:
        value = _query_value(measure_id, month)
        unit = _MEASURE_UNITS[measure_id]
    except Exception:  # 查询链路任何失败（含超时类异常）-> 503，绝不 500 裸栈
        raise HTTPException(503, "trial_unavailable") from None

    result = TrialResult(
        rule_id=rule_id,
        month=month,
        value=value,
        unit=unit,
        generated_at=datetime.now(timezone.utc).astimezone(),  # 风格同 confirm_store
        source="semantic_query",
    )
    _trial_cache[(rule_id, month)] = (today, result)
    return result
