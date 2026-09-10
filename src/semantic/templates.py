"""D6 answer layer (P0 template scheme, product doc §5-D6/§5-D9).

Templates are keyed by query SHAPE (dimension set over the L2 registry
output), not by legacy rule ids. Slot values are computed from rows/params
only — neither the LLM nor glue code may invent a number. validate_numbers
is the hard gate: every number printed in an answer must be traceable to
the semantic-layer number set (percent/unit conversions allowed), otherwise
the whole answer is rejected and the caller routes to validation_failed.
"""

import re


def _slots_total(rows, params, mcol, _dim):
    return {"month": params["time_from"][:7], "total": f"{rows[0][mcol]:,}"}


def _slots_channel(rows, _params, mcol, dim):
    total = sum(r[mcol] for r in rows)
    top3 = "、".join(f"{r[dim]} {r[mcol]:,}" for r in rows[:3])
    return {"total": f"{total:,}", "top3": top3}


def _slots_gender(rows, _params, mcol, dim):
    total = sum(r[mcol] for r in rows)
    distribution = "、".join(
        f"{r[dim] or '未知'} {r[mcol]:,}（{100 * r[mcol] / total:.1f}%）" for r in rows)
    return {"distribution": distribution, "total": f"{total:,}"}


_GRAIN_LABEL = {"day": "日", "week": "周", "month": "月"}


def _slots_trend(rows, _params, mcol, dim):
    grain = dim.split("=", 1)[1]
    points = "、".join(f"{r[dim]} {r[mcol]:,}" for r in rows)
    return {"grain": _GRAIN_LABEL.get(grain, grain), "points": points}


def render(measure_col: str, dims, rows: list, params: dict) -> str:
    """Shape-keyed template selection + number-slot filling (D6 P0).
    Unknown shape or empty rows -> '' (caller falls back to a number-free
    sentence; the table itself renders the rows)."""
    if not rows:
        return ""
    if not dims:
        return "{month} 月注册 {total} 人。".format(
            **_slots_total(rows, params, measure_col, None))
    first = dims[0]
    if first.startswith("channel_l"):
        return "共 {total} 人，TOP3：{top3}。".format(
            **_slots_channel(rows, params, measure_col, first))
    if first == "gender":
        return "{distribution}。合计 {total} 人。".format(
            **_slots_gender(rows, params, measure_col, first))
    if first.startswith("time_grain"):
        return "按{grain}趋势：{points}。".format(
            **_slots_trend(rows, params, measure_col, first))
    return ""


# --------------------------------------------------------------- number gate

# Same token shape as tests/semantic (labels like "TOP3" excluded by lookbehind);
# optional trailing unit: percent or 万.
_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])(\d[\d,]*\.?\d*)\s*(%|万)?")


class NumberValidationError(Exception):
    """D6 hard gate: the answer printed a number outside the traceable set."""

    def __init__(self, offender: str, allowed: set[str]):
        self.offender = offender
        self.allowed = sorted(allowed)
        super().__init__(
            f"回答含不可溯源数字「{offender}」；语义层可溯源集合 = {self.allowed}")


def _float(text: str) -> float | None:
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _matches(token: str, unit: str | None, allowed: set[str], vals: list[float]) -> bool:
    if token in allowed:  # exact printed form (keeps leading zeros like "08")
        return True
    value = _float(token)
    if value is None:
        return False
    candidates = [value]
    if unit == "%":  # percent of a semantic-layer fraction
        candidates.append(value / 100)
    elif unit == "万":  # 万-scaled count
        candidates.append(value * 10000)
    return any(abs(c - v) <= 1e-6 * max(1.0, abs(c), abs(v))
               for c in candidates for v in vals)


def validate_numbers(answer: str, numbers: set[str]) -> list[str]:
    """Extract every number in `answer`, compare with the semantic-layer set.
    Percent/unit conversions count as traceable; any untraceable number raises
    NumberValidationError (numeric comparison included, caller -> validation_failed).
    Returns the extracted number tokens on success."""
    allowed = {n.replace(",", "") for n in numbers}
    vals = [v for v in (_float(n) for n in allowed) if v is not None]
    found = []
    for match in _TOKEN_RE.finditer(answer):
        token, unit = match.group(1).replace(",", ""), match.group(2)
        if not _matches(token, unit, allowed, vals):
            raise NumberValidationError(match.group(1), numbers)
        found.append(token)
    return found
