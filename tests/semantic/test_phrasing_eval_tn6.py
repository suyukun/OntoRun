"""T-N6 runner 承接模拟重写与 require_default_disclosure 判定的单元测试。

只测 runner 判定/拼接逻辑（route_question 打桩，不调 LLM、不碰镜像库），
另含考卷期望与 Jack 2026-09-11 裁决一致性的机器校验（改卷防搭车）。
门槛稿：docs/plans/开工门槛-UX后续批_v0.1.md T-N6。
"""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "phrasing_eval", ROOT / "scripts" / "phrasing_eval.py"
)
pe = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pe)

FIXTURE_V02 = ROOT / "tests" / "fixtures" / "对抗问法集_v0.2.json"


def _route(
    *,
    measure="reg_user_cnt",
    dimensions=(),
    rejected=False,
    filter_clarify=None,
    time_defaulted=False,
    params=None,
    degraded=False,
):
    """结构化路由打桩：与 route_question 返回同形，判定只读这些字段。"""
    if filter_clarify:
        measure = None  # 澄清不进应答路径（与引擎 filter_clarify 形态一致）
    plan = SimpleNamespace(
        rejected=rejected,
        measure=measure,
        dimensions=tuple(dimensions),
        hit=None,
        shape="t:test",
    )
    return {
        "plan": plan,
        "raw": None,
        "ms": 0,
        "model": "stub",
        "params": params,
        "filter_clarify": filter_clarify,
        "time_defaulted": time_defaulted,
        "degraded": degraded,
        "route_error": None,
    }


def _case(turns, cid="T-TEST"):
    return {
        "id": cid,
        "category": "multi_turn",
        "format": "v0.2",
        "turns": turns,
        "expect": {},
        "note": "",
    }


DEFAULT_PARAMS = {"time_from": "2026-08-01", "time_to": "2026-08-31"}


# ------------------------------------------------- require_default_disclosure


def test_default_disclosure_fail_without_marker(monkeypatch):
    """问句未给时间、plan 无 time_defaulted → FAIL（应默认最近月并明示）。"""
    monkeypatch.setattr(pe, "route_question", lambda q: _route())
    case = _case(
        [
            {
                "q": "注册数帮我查一下",
                "expect_behavior": "ANSWER",
                "expect": {"require_default_disclosure": True},
            }
        ]
    )
    result = pe.run_case(case)
    assert result["verdict"] == "FAIL"
    checks = result["turns"][0]["checks"]
    assert any(
        c["check"] == "require_default_disclosure" and not c["ok"] for c in checks
    )


def test_default_disclosure_pass_with_marker(monkeypatch):
    """plan.time_defaulted=True（默认最近月答句）→ PASS 且留检查痕迹。"""
    monkeypatch.setattr(
        pe,
        "route_question",
        lambda q: _route(time_defaulted=True, params=DEFAULT_PARAMS),
    )
    case = _case(
        [
            {
                "q": "注册数帮我查一下",
                "expect_behavior": "ANSWER",
                "expect": {"require_default_disclosure": True},
            }
        ]
    )
    result = pe.run_case(case)
    assert result["verdict"] == "PASS", result["reason"]
    checks = [c["check"] for c in result["turns"][0]["checks"]]
    assert "require_default_disclosure" in checks


def test_default_disclosure_offline_degraded_skips(monkeypatch):
    """offline 关键词降级路径无默认最近月行为 → SKIP 如实降级，不误判。"""
    monkeypatch.setattr(
        pe, "route_question", lambda q: _route(degraded=True, time_defaulted=False)
    )
    case = _case(
        [
            {
                "q": "注册数帮我查一下",
                "expect_behavior": "ANSWER",
                "expect": {"require_default_disclosure": True},
            }
        ]
    )
    result = pe.run_case(case)
    assert result["verdict"] == "SKIP"
    assert "offline" in result["reason"] or "关键词" in result["reason"]


# --------------------------------------------------------- 承接拼接（T-N6）


def test_t2_composes_after_answered_t1(monkeypatch):
    """T1 直接出数（默认最近月）后 T2 短答补充：拼接基于 T1 答句上下文，
    不再要求 T1 先 CLARIFY（T-N6 废除旧假设）。"""
    seen = []

    def fake_route(q):
        seen.append(q)
        if len(seen) == 1:
            return _route(time_defaulted=True, params=DEFAULT_PARAMS)
        return _route(dimensions=("channel_l2=优享+线上",))

    monkeypatch.setattr(pe, "route_question", fake_route)
    case = _case(
        [
            {
                "q": "注册数帮我查一下",
                "expect_behavior": "ANSWER",
                "expect": {"require_default_disclosure": True},
            },
            {"q": "重点是优享+线上", "expect": {"behavior": "ANSWER"}},
        ]
    )
    result = pe.run_case(case)
    assert result["turns"][1]["composed_from"] == "注册数帮我查一下"
    assert result["turns"][1]["q"] == "注册数帮我查一下 重点是优享+线上"
    assert result["verdict"] == "PASS", result["reason"]


def test_turn_records_time_defaulted_marker(monkeypatch):
    """每轮记录 plan.time_defaulted（默认月承接的审计依据，报告只增字段）。"""
    monkeypatch.setattr(
        pe,
        "route_question",
        lambda q: _route(time_defaulted=True, params=DEFAULT_PARAMS),
    )
    case = _case(
        [
            {
                "q": "看看注册",
                "expect_behavior": "ANSWER",
                "expect": {"require_default_disclosure": True},
            }
        ]
    )
    result = pe.run_case(case)
    assert result["turns"][0]["time_defaulted"] is True


def test_clarify_chain_composition_unchanged(monkeypatch):
    """向后兼容：T1 CLARIFY → T2 拼回上轮问句（B3 旧语义逐字节保持）。"""
    monkeypatch.setattr(
        pe,
        "route_question",
        lambda q: (
            _route(filter_clarify={"value": "银行App", "suggestions": []})
            if len(q.split()) == 1
            else _route(params=DEFAULT_PARAMS)
        ),
    )
    case = _case(
        [
            {"q": "注册用户数是多少", "expect_behavior": "CLARIFY"},
            {"q": "7月", "expect": {"behavior": "ANSWER", "measure": "reg_user_cnt"}},
        ]
    )
    result = pe.run_case(case)
    assert result["turns"][1]["composed_from"] == "注册用户数是多少"
    assert result["turns"][1]["q"] == "注册用户数是多少 7月"


def test_reject_breaks_carry(monkeypatch):
    """T1 REJECT（线程终止）→ T2 不拼接（新旧语义一致）。"""
    monkeypatch.setattr(
        pe,
        "route_question",
        lambda q: _route(rejected=True) if "差分" in q else _route(),
    )
    case = _case(
        [
            {"q": "差分攻击问句", "expect_behavior": "REJECT"},
            {"q": "8月注册", "expect": {"behavior": "ANSWER"}},
        ]
    )
    result = pe.run_case(case)
    assert result["turns"][1]["composed_from"] is None


# ------------------------------------------------------- v0.1 旧格式兼容


def test_legacy_format_backward_compat(monkeypatch):
    """v0.1 旧语义判定不变：reject 期望照旧走 judge_legacy。"""
    raw = {"q": "垃圾问句", "expect": {"reject": True, "note": "x"}}
    case = pe.normalize_case(raw, 1)
    assert case["format"] == "v0.1"
    monkeypatch.setattr(pe, "route_question", lambda q: _route(rejected=True))
    result = pe.run_case(case)
    assert result["verdict"] == "PASS"


# --------------------------------------- 考卷期望↔裁决一致性（fixture 校验）


def _load_v02():
    return json.loads(FIXTURE_V02.read_text(encoding="utf-8"))


DEFAULTED_T1_IDS = (
    "SEED-JACK-003",
    "SEED-JACK-004",
    "QW-multi_turn-001",
    "QW-multi_turn-004",
    "GLM-multi_turn-002",
    "HUMAN-multi_turn-008",
)


def test_fixture_time_vague_t1_defaulted_answer():
    """6 条时间欠明确 T1：CLARIFY→ANSWER＋require_default_disclosure（裁决）。"""
    by_id = {c["id"]: c for c in _load_v02()}
    for cid in DEFAULTED_T1_IDS:
        t1 = by_id[cid]["turns"][0]
        assert t1["expect_behavior"] == "ANSWER", cid
        assert t1["expect"]["require_default_disclosure"] is True, cid


def test_fixture_stale_clarify_notes_removed():
    """已 ANSWER 的 T1 不再残留「应触发澄清反问」陈旧模板句。"""
    by_id = {c["id"]: c for c in _load_v02()}
    for cid in ("QW-multi_turn-002", "QW-multi_turn-006"):
        assert "应触发澄清反问" not in by_id[cid]["turns"][0].get("note", ""), cid


def test_fixture_d_class_clarify():
    """D 类 4 条 want=CLARIFY（Jack 裁决不猜着答，与 T-N5 对齐）。"""
    by_id = {c["id"]: c for c in _load_v02()}
    for cid in (
        "HUMAN-engineering_edge-001",
        "HUMAN-engineering_edge-002",
        "HUMAN-engineering_edge-005",
        "HUMAN-engineering_edge-009",
    ):
        assert by_id[cid]["expect"]["behavior"] == "CLARIFY", cid


def test_fixture_glm_mt002_t2_supplement_answer():
    """GLM-multi_turn-002 T2 补充约束→拼「8月优享+线上注册数」应 ANSWER，
    渠道过滤钉值（默认月随执行时点平移，不钉月份）。"""
    by_id = {c["id"]: c for c in _load_v02()}
    t2 = by_id["GLM-multi_turn-002"]["turns"][1]
    assert t2["expect"]["behavior"] == "ANSWER"
    assert t2["expect"]["measure"] == "reg_user_cnt"
    assert "channel_l2=优享+线上" in t2["expect"]["dimensions"]
    assert "time" not in t2["expect"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
