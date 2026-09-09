"""T5/D6 tests: template scheme + number-consistency hard gate (§5-D6/§5-D9).

Env overrides mirror test_core (isolated tmp stores, keyword routing); the
first import pins package config, so these tests never touch real stores.
"""

import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="semantic-d6-"))
os.environ.setdefault("SEMANTIC_APP_DB", str(_TMP / "app.db"))
os.environ.setdefault("SEMANTIC_TRACE_LOG", str(_TMP / "trace.jsonl"))
os.environ.setdefault("SEMANTIC_DISABLE_LLM", "1")

import pytest

from src.semantic import engine, errors, storage, templates
from src.semantic.templates import NumberValidationError, validate_numbers

storage.migrate()

HOT = "2026年8月注册用户数是多少？"


def _final(frames):
    finals = [f for f in frames if f["kind"] == "final"]
    assert len(finals) == 1
    return finals[0]["result"]


def test_template_slot_filling():
    """Registry templates render deterministic sentences; numbers come from rows only."""
    assert templates.render("REG_TOTAL", [{"total": 1234}],
                            {"start": "2026-08-01", "end": "2026-08-31"}) \
        == "2026-08 月注册 1,234 人。"
    rows = [{"channel": "app", "cnt": 20}, {"channel": "web", "cnt": 10},
            {"channel": "h5", "cnt": 6}, {"channel": "mini", "cnt": 4}]
    assert templates.render("REG_BY_CHANNEL", rows, {}) == "共 40 人，TOP3：app 20、web 10、h5 6。"
    ratio = [{"gender": "女", "cnt": 24}, {"gender": "男", "cnt": 12}]
    assert templates.render("GENDER_RATIO", ratio, {}) \
        == "女 24（66.7%）、男 12（33.3%）。合计 36 人。"
    assert templates.render("UNREGISTERED", ratio, {}) == ""


def test_iter_query_answer_is_template_rendered_from_rows():
    """Answer must equal template render over the snapshot rows (no free-text numbers)."""
    for question in (HOT, "2026年8月分渠道注册用户数", "2026年8月注册用户男女比例"):
        result = _final(list(engine.iter_query(question)))
        assert result["state"] in ("success", "success_warning"), (question, result["state"])
        expected = templates.render(result["rule"], result["rows"], result["params"])
        assert result["answer"].startswith(expected), (question, result["answer"])


def test_injected_untraceable_number_is_blocked():
    """Constructed injection: a poisoned answer fails the D6 gate -> validation_failed."""
    probe = _final(list(engine.iter_query(HOT)))
    assert probe["state"] in ("success", "success_warning")
    original = engine.answer_assemble
    engine.answer_assemble = lambda *args: "共 999 人，其中 VIP 888 人。"
    try:
        result = _final(list(engine.iter_query(HOT)))
    finally:
        engine.answer_assemble = original
    assert result["path"] == "validation_failed"
    assert result["state"] == "validation_failed"
    assert result["error_code"] == errors.E_VALIDATION
    assert result["answer"] == errors.user_message(errors.E_VALIDATION)
    assert "999" not in result["answer"] and "888" not in result["answer"]  # 拦截，不透出
    failed = [s for s in result["steps"] if s["title"] == "数字校验" and s["status"] == "fail"]
    assert failed and "999" in failed[0]["detail"]  # 数值对照只进 trace/详情


def test_converted_numbers_are_traceable():
    """Percent/unit conversions pass; untraceable numbers raise with the comparison."""
    validate_numbers("新增占比 12.5%。", {"0.125"})  # fraction -> percent
    validate_numbers("男 12（33.3%）。", {"12", "33.3"})  # semantic-layer percent, direct
    validate_numbers("共 1.2万人。", {"12000"})  # 万-unit
    validate_numbers("2026-08 月注册 1,234 人。", {"1234", "2026", "08"})
    with pytest.raises(NumberValidationError) as exc:
        validate_numbers("共 999 人。", {"1,234"})
    assert exc.value.offender == "999"
    assert "1,234" in exc.value.allowed  # 对照保留原始印出形式
    assert "999" in str(exc.value)


def test_live_gender_ratio_percents_traceable():
    """Live cold-adhoc answer: every percent derives from rows (task case 3)."""
    result = _final(list(engine.iter_query("2026年8月注册用户男女比例")))
    assert result["rows"]
    allowed = engine.traceable_numbers(result["rule"], result["rows"], result.get("params"))
    validate_numbers(result["answer"], allowed)
