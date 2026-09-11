"""T-N5 确认式澄清路由硬化（开工门槛-UX后续批_v0.1.md T-N5，Jack 裁决
「不要猜着答，要确认」全量落地）——测试即规格。

不经 LLM、不触镜像库（test_adversarial_cases 同款零副作用约定；llm_route()
调用统一 monkeypatch SEMANTIC_DISABLE_LLM=1，确定性短路先于该开关生效）。
问句原文一律取自 tests/fixtures/对抗问法集_v0.2.json（判据唯一来源，门槛稿
T-N5 判据行已按 2026-09-11 勘误对齐 fixtures）：
① 错别字/未注册别名 → 确认式澄清（带候选名，不出数）：赢行App / 祖册数 / bank App；
② 口径歧义 → 确认式澄清：新客 / 新增 / 激活口径 / 上次汇报口径（系统无跨对话
   记忆，如实澄清不硬猜）；显式索求未注册口径（原始口径/留存率）→ REJECT 不确认；
③ 语流混乱复合问（各渠道 × 哪些渠道双问）→ 确认式澄清；
④ 域外零信息输入（？？？/930/转义炸弹）→ 澄清引导，不 REJECT；
⑤ 口语时间「八月份」→ 代码解析为当月整月应答；「优享加线上」→ 高置信符号
   变体（加↔+）直接映射出数；
⑥ 确认承接：应答「对/默认」或补成员值 → 按候选口径出数；
⑦ 防误伤：engineering_edge 既有应答问句零回退、纯月份短语/域外有信息问句
   维持原路径、安全差分特征优先于一切澄清判定。
"""

import json
from datetime import date
from pathlib import Path

import pytest

from src.semantic import llm_route
from src.semantic.llm_route import RoutePlan, channel_clarify_answer, keyword_route
from src.semantic.rules import keyword_route as plain_keyword_route
from src.semantic.time_normalizer import extract_oral_month

_FIXTURES = json.loads(
    (
        Path(__file__).resolve().parents[1] / "fixtures" / "对抗问法集_v0.2.json"
    ).read_text(encoding="utf-8")
)


def _fx_q(case_id: str) -> str:
    """fixture 原文问句（判据以对抗问法集 v0.2 为准）。"""
    return next(case["q"] for case in _FIXTURES if case["id"] == case_id)


def _route_offline(monkeypatch, question: str) -> dict:
    """offline 路由一次（确定性短路 + 关键词降级，绝不触网）。"""
    monkeypatch.setenv("SEMANTIC_DISABLE_LLM", "1")
    return llm_route.llm_route(question)


# ------------------------------------------------------------------ ① 别名错别字


def test_typo_channel_alias_confirms_with_candidate(monkeypatch):
    """HUMAN-engineering_edge-001：「赢行App」应确认式澄清并带候选名（银行App），
    SHALL NOT 直接出数（Jack 裁决：别名命中须确认，不自作主张）。"""
    out = _route_offline(monkeypatch, _fx_q("HUMAN-engineering_edge-001"))
    clarify = out.get("filter_clarify")
    assert clarify is not None  # 确认式澄清，不出数
    assert clarify["suggestions"] == ["银行App"]
    assert not out["plan"].rejected


def test_english_alias_confirms_not_answers(monkeypatch):
    """GLM-semantic_edge-002：bank App→银行App 属语义解释，应确认式澄清
    （原 ANSWER 判据废止）。"""
    out = _route_offline(monkeypatch, _fx_q("GLM-semantic_edge-002"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["银行App"]


def test_typo_measure_confirms(monkeypatch):
    """HUMAN-engineering_edge-002：「祖册数」无高置信映射 → 澄清（带候选
    「注册用户数」）而非瞎猜出数。"""
    out = _route_offline(monkeypatch, _fx_q("HUMAN-engineering_edge-002"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["注册用户数"]


# ------------------------------------------------------------------ ② 口径歧义


def test_ambiguous_caliber_new_customer_confirms(monkeypatch):
    """HUMAN-engineering_edge-005：「新客」≈注册但语境不完全等同 → 把理解翻译
    出来确认（按注册口径理解？），不直接返回数据。"""
    out = _route_offline(monkeypatch, _fx_q("HUMAN-engineering_edge-005"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["注册用户数"]


def test_ambiguous_caliber_new_add_confirms(monkeypatch):
    """GLM-caliber_trap-001：「新增用户」≈注册但需确认后出数。"""
    out = _route_offline(monkeypatch, _fx_q("GLM-caliber_trap-001"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["注册用户数"]


def test_unregistered_caliber_confirms_default(monkeypatch):
    """QW-caliber_trap-002：「激活口径」未注册 → 澄清引导（默认口径候选），
    不硬答也不死拒。"""
    out = _route_offline(monkeypatch, _fx_q("QW-caliber_trap-002"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["注册用户数（默认口径）"]


def test_cross_memory_caliber_honestly_clarifies(monkeypatch):
    """GLM-caliber_trap-006：「上次汇报的口径」是外部口头引用，系统无跨对话
    记忆 → 如实澄清是否按默认口径，不自行假设后硬出数。"""
    out = _route_offline(monkeypatch, _fx_q("GLM-caliber_trap-006"))
    clarify = out.get("filter_clarify")
    assert clarify is not None
    assert clarify["suggestions"] == ["注册用户数（默认口径）"]


def test_explicit_raw_caliber_rejects_not_confirms(monkeypatch):
    """QW-caliber_trap-001：显式索求未注册「原始口径」且预先否定默认口径
    （「别拿现在这个口径糊弄我」）→ REJECT，不得以默认口径反问或冒充出数。"""
    q = _fx_q("QW-caliber_trap-001")
    assert plain_keyword_route(q).rejected  # 规则层同判（离线/降级一致）
    out = _route_offline(monkeypatch, q)
    assert out["plan"].rejected
    assert out["plan"].hit and not any(ch.isdigit() for ch in out["plan"].hit)


def test_retention_caliber_rejects(monkeypatch):
    """GLM-caliber_trap-002：「留存率」未注册派生概念 → REJECT（对比期数据
    亦在样本外），不拿注册数冒充留存。"""
    out = _route_offline(monkeypatch, _fx_q("GLM-caliber_trap-002"))
    assert out["plan"].rejected


# ------------------------------------------------------------------ ③ 语流混乱复合问


def test_compound_question_confirms():
    """HUMAN-engineering_edge-009：连说无标点复合问（各渠道 × 哪些渠道双问）
    → 选主问确认，SHALL NOT 静默丢一半。"""
    hit = llm_route.confirm_clarify_hit(_fx_q("HUMAN-engineering_edge-009"))
    assert hit is not None and "clarify" in hit
    assert hit["clarify"]["filter_clarify"]["suggestions"] == ["各渠道注册数"]


# ------------------------------------------------------------------ ④ 域外零信息输入


@pytest.mark.parametrize(
    "case_id", ["GLM-engineering_edge-002", "GLM-engineering_edge-003"]
)
def test_zero_info_input_guides_clarify(monkeypatch, case_id):
    """GLM-engineering_edge-002/003：纯标点/孤立裸数字 → 体面澄清引导，
    SHALL NOT REJECT、报堆栈或凭空出数。"""
    out = _route_offline(monkeypatch, _fx_q(case_id))
    clarify = out.get("filter_clarify")
    assert clarify is not None  # CLARIFY 不 REJECT
    assert clarify["suggestions"] == []


def test_escape_bomb_guides_clarify(monkeypatch):
    """QW-engineering_edge-006：转义炸弹串（引号/反斜杠嵌套+超长尾巴）→
    不崩、不当语句执行，能澄清真实意图（CLARIFY 不 REJECT）。"""
    out = _route_offline(monkeypatch, _fx_q("QW-engineering_edge-006"))
    assert out.get("filter_clarify") is not None


# ------------------------------------------------------------------ ⑤ 口语时间 + 符号变体


def test_oral_month_parses_to_full_month():
    """HUMAN-engineering_edge-003：「八月份」口语时间由代码解析为当月整月
    （解析权在代码，LLM 直出日期有系统性偏差）。"""
    rng = extract_oral_month("就是八月份的那个注册的那个数", date(2026, 9, 15))
    assert rng == {"time_from": "2026-08-01", "time_to": "2026-08-31"}
    assert extract_oral_month("十二月", date(2026, 9, 15)) == {
        "time_from": "2026-12-01",
        "time_to": "2026-12-31",
    }
    assert (
        extract_oral_month("8月的注册数", date(2026, 9, 15)) is None
    )  # 数字月份走既有链路
    assert extract_oral_month("今年的注册情况", date(2026, 9, 15)) is None


def test_oral_month_routes_to_answer_with_window(monkeypatch):
    """HUMAN-engineering_edge-003 全路由：填充词语流句 + 八月份 → 按注册度量
    直答（want ANSWER），时间窗 2026-08，不反问。"""
    out = _route_offline(monkeypatch, _fx_q("HUMAN-engineering_edge-003"))
    assert "error" not in out
    assert out["plan"].measure == "reg_user_cnt"
    assert out["time_from"] == "2026-08-01" and out["time_to"] == "2026-08-31"
    assert not out["plan"].rejected and "filter_clarify" not in out


def test_symbol_variant_maps_to_member_directly(monkeypatch):
    """HUMAN-engineering_edge-006：「优享加线上」加↔+ 高置信符号变体 → 直接
    链接到维表成员（不澄清、不猜）。"""
    plan = keyword_route(_fx_q("HUMAN-engineering_edge-006"))
    assert plan.measure == "reg_user_cnt"
    assert "channel_l2=优享+线上" in plan.dimensions
    # 值链接防线同一变体归一：不过滤值澄清（名单固定快照，零镜像依赖）
    monkeypatch.setattr(
        llm_route, "_channel_members", lambda: ("优享+线上", "银行App", "麦当劳")
    )
    linked, clarify = llm_route._link_filter_values(
        RoutePlan(measure="reg_user_cnt", dimensions=("channel_l2=优享加线上",))
    )
    assert clarify is None
    assert linked.dimensions == ("channel_l2=优享+线上",)


def test_symbol_variant_full_route_answers(monkeypatch):
    """HUMAN-engineering_edge-006 全路由：确认式澄清规则不得误伤高置信变体；
    离线组合与 runner 同构（llm_route error → keyword_route 兜底出数）。"""
    out = _route_offline(monkeypatch, _fx_q("HUMAN-engineering_edge-006"))
    assert "filter_clarify" not in out  # 确认式澄清不误伤高置信变体
    assert "error" in out  # LLM 不可用 → 引擎/runner 以 keyword_route 兜底
    plan = keyword_route(_fx_q("HUMAN-engineering_edge-006"))
    assert plan.measure == "reg_user_cnt"
    assert "channel_l2=优享+线上" in plan.dimensions


# ------------------------------------------------------------------ ⑥ 确认承接


def test_affirmative_reply_resolves_measure_confirm():
    """澄清应答「对」→ 按候选口径（注册）出数，不再重复追问。"""
    hit = llm_route.confirm_clarify_hit(_fx_q("HUMAN-engineering_edge-005") + " 对")
    assert hit is not None and "resolve" in hit
    assert hit["resolve"]["plan"].measure == "reg_user_cnt"


def test_default_reply_resolves_caliber_confirm():
    """「那就默认口径吧」→ 接受默认口径，按注册度量出数（多轮 T2 承接）。"""
    hit = llm_route.confirm_clarify_hit("激活口径的8月注册 那就默认口径吧")
    assert hit is not None and "resolve" in hit
    assert hit["resolve"]["plan"].measure == "reg_user_cnt"


def test_member_value_reply_resolves_channel_confirm():
    """澄清应答补上成员值「银行App」→ 高置信解析，不再澄清。"""
    hit = llm_route.confirm_clarify_hit(
        _fx_q("HUMAN-engineering_edge-001") + " 银行App"
    )
    assert hit is not None and "resolve" in hit
    assert "channel_l2=银行App" in hit["resolve"]["plan"].dimensions


# ------------------------------------------------------------------ ⑦ 防误伤（零回退）


@pytest.mark.parametrize(
    "case_id",
    [
        "HUMAN-engineering_edge-004",
        "HUMAN-engineering_edge-007",
        "HUMAN-engineering_edge-008",
        "QW-engineering_edge-003",
    ],
)
def test_existing_answer_shapes_not_clarified(case_id):
    """engineering_edge 既有应答问句零回退：确认式澄清/零信息规则一律不触发。"""
    question = _fx_q(case_id)
    assert llm_route.confirm_clarify_hit(question) is None
    plan = keyword_route(question)
    assert plan.measure == "reg_user_cnt" and not plan.rejected


@pytest.mark.parametrize("question", ["9月", "附近有什么好吃的餐厅"])
def test_bare_month_and_domain_out_keep_old_path(monkeypatch, question):
    """纯月份短语（多轮承接信号）与域外有信息问句维持既有路径（unregistered
    拒答），零信息澄清 SHALL NOT 扩大化。"""
    out = _route_offline(monkeypatch, question)
    assert "filter_clarify" not in out  # 不触发零信息澄清


def test_safety_precedence_over_confirm(monkeypatch):
    """安全红线优先级最高：差分/再识别特征问句先于一切澄清判定照拒
    （QW-safety_pii-001 原文，含成员值「银行App」）。"""
    q = _fx_q("QW-safety_pii-001")
    assert plain_keyword_route(q).rejected  # 规则层不变
    out = _route_offline(monkeypatch, q)
    assert out["plan"].rejected
    assert "filter_clarify" not in out


def test_clarify_copy_red_lines():
    """产品红线：确认/零信息澄清文案零数字、零 SQL、零表名/层名；多候选既有
    文案保持不变（拼多多类未知渠道路径零回归）。"""
    confirm = channel_clarify_answer("赢行", ["银行App"])
    assert confirm == "您是指「银行App」吗？确认后我来查询。"
    zero = channel_clarify_answer("（未能识别）", [])
    assert "没有识别到" in zero and "例如" in zero
    multi = channel_clarify_answer("不存在的渠道", ["银行App", "麦当劳", "中信书院"])
    assert multi.startswith("未找到该渠道「不存在的渠道」")
    assert "我能答的渠道有" in multi
    for copy in (confirm, zero, multi):
        assert not any(ch.isdigit() for ch in copy)
        assert "SELECT" not in copy.upper() and "dwd" not in copy and "cdm" not in copy
