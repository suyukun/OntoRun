"""D6 answer layer (P0 template scheme, product doc §5-D6/§5-D9).

Per-rule sentence templates with number slots + the number-consistency
validator. Slot values are computed from rows/params only — neither the LLM
nor glue code may invent a number. validate_numbers is the hard gate: every
number printed in an answer must be traceable to the semantic-layer number
set (percent/unit conversions allowed), otherwise the whole answer is
rejected and the caller routes to validation_failed.
"""

import re


# Answer templates per rule: (sentence pattern with {slots}, slot builder).
# Slot builders receive the post-PII rows and query params; they format the
# numbers for display and return placeholder -> rendered-text dicts.
def _slots_reg_total(rows, params):
    return {"month": params["start"][:7], "total": f"{rows[0]['total']:,}"}


def _slots_reg_by_channel(rows, params):
    total = sum(r["cnt"] for r in rows)
    top3 = "、".join(f"{r['channel']} {r['cnt']:,}" for r in rows[:3])
    return {"total": f"{total:,}", "top3": top3}


def _slots_gender_ratio(rows, params):
    total = sum(r["cnt"] for r in rows)
    distribution = "、".join(
        f"{r['gender']} {r['cnt']:,}（{100 * r['cnt'] / total:.1f}%）" for r in rows)
    return {"distribution": distribution, "total": f"{total:,}"}


TEMPLATES = {
    "REG_TOTAL": ("{month} 月注册 {total} 人。", _slots_reg_total),
    "REG_BY_CHANNEL": ("共 {total} 人，TOP3：{top3}。", _slots_reg_by_channel),
    "GENDER_RATIO": ("{distribution}。合计 {total} 人。", _slots_gender_ratio),
}


def render(rule_id: str, rows: list, params: dict) -> str:
    """Template selection + number-slot filling (D6 P0). Unknown rule -> ''."""
    entry = TEMPLATES.get(rule_id)
    if entry is None:
        return ""
    pattern, slots = entry
    return pattern.format(**slots(rows, params))


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
