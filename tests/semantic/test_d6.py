"""T5/D6 tests: template scheme + number-consistency hard gate (§5-D6/§5-D9).

Templates are keyed by query shape over the L2 registry output. Env overrides
mirror test_core (isolated tmp stores, keyword routing); the first import pins
package config, so these tests never touch real stores.
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
CHANNEL = "2026年8月分渠道注册用户数"
GENDER = "2026年8月注册用户男女比例"
M = "reg_user_cnt"


def _final(frames):
    finals = [f for f in frames if f["kind"] == "final"]
    assert len(finals) == 1
    return finals[0]["result"]


def test_template_slot_filling():
    """Shape-keyed templates render deterministic sentences; numbers come from rows only."""
    assert templates.render(M, (), [{M: 1234}],
                            {"time_from": "2026-08-01", "time_to": "2026-08-31"}) \
        == "2026-08 月注册 1,234 人。"
    rows = [{"channel_l2": "app", M: 20}, {"channel_l2": "web", M: 10},
            {"channel_l2": "h5", M: 6}, {"channel_l2": "mini", M: 4}]
    assert templates.render(M, ("channel_l2",), rows, {}) == "共 40 人，TOP3：app 20、web 10、h5 6。"
    ratio = [{"gender": "女", M: 24}, {"gender": "男", M: 12}]
    assert templates.render(M, ("gender",), ratio, {}) \
        == "女 24（66.7%）、男 12（33.3%）。合计 36 人。"
    assert templates.render(M, ("region",), ratio, {}) == ""  # unrendered shape -> ''


def test_iter_query_answer_is_template_rendered_from_rows():
    """Answer must equal template render over the snapshot rows (no free-text numbers)."""
    for question in (HOT, CHANNEL):
        result = _final(list(engine.iter_query(question)))
        assert result["state"] in ("success", "success_warning"), (question, result["state"])
        expected = templates.render(result["measure"], result["dimensions"],
                                    result["rows"], result["params"])
        assert result["answer"].startswith(expected), (question, result["answer"])


def test_gender_live_answer_traceable():
    """当前镜像 usr_sex 已填充（F/M/None）：真实分布 + 每个数字可溯源。"""
    result = _final(list(engine.iter_query(GENDER)))
    assert result["path"] == "semantic_pushdown"
    assert result["state"] in ("success", "success_warning")  # keyword 路由 → warning
    assert result["rows"] and {r["gender"] for r in result["rows"]} <= {"F", "M", None}
    allowed = engine.traceable_numbers(
        result["measure"], result["dimensions"], result["rows"], result["params"])
    validate_numbers(result["answer"], allowed)  # percents 全部来自 rows
    assert "未知" in result["answer"]  # NULL 组如实标注，不静默丢弃


def test_gender_dimension_degrades_honestly(monkeypatch, tmp_path):
    """维度已建模、镜像字段未填充（usr_sex 全 NULL）→ 诚实降级，不出假分布。

    用最小 fixture 镜像（注册表原语同构）锁降级路径；真实镜像恢复空值时同路径生效。
    """
    import duckdb
    from src.semantic import config

    fixture = tmp_path / "fixture_mirror.duckdb"
    conn = duckdb.connect(str(fixture))
    conn.execute("CREATE SCHEMA cdm")
    conn.execute(
        "CREATE TABLE cdm.dwd_cu_rgst_fin_di "
        "(usr_id VARCHAR, rgst_chnl_id VARCHAR, rgst_dt TIMESTAMP, rgst_num INTEGER)")
    conn.execute(
        "CREATE TABLE cdm.dim_cu_usr_info_df (usr_id VARCHAR, usr_sex VARCHAR, ds TIMESTAMP)")
    conn.execute(
        "CREATE TABLE cdm.dim_ch_chl_df "
        "(chnl_id VARCHAR, sec_chnl_nm VARCHAR, ds TIMESTAMP)")
    conn.execute("INSERT INTO cdm.dwd_cu_rgst_fin_di VALUES "
                 "('u1', 'CHN01', TIMESTAMP '2026-08-05 10:00:00', 1), "
                 "('u2', 'CHN02', TIMESTAMP '2026-08-06 11:00:00', 1)")
    conn.execute("INSERT INTO cdm.dim_cu_usr_info_df VALUES "
                 "('u1', NULL, TIMESTAMP '2026-08-31 00:00:00'), "
                 "('u2', NULL, TIMESTAMP '2026-08-31 00:00:00')")
    conn.close()

    monkeypatch.setattr(config, "MIRROR_DB", fixture)
    result = _final(list(engine.iter_query(GENDER)))
    assert result["path"] == "semantic_pushdown"
    assert result["state"] == "success_warning"  # degraded, not failed
    assert result["degraded"] is True
    assert result["degraded_reason"] == "dimension_unfilled"
    assert "维度已建模、仿真数据未填充" in result["answer"]
    assert not any(ch.isdigit() for ch in result["answer"])  # 不编造分布
    assert result["rows"] and all(r["gender"] is None for r in result["rows"])


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
