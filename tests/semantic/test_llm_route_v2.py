"""llm_route v2 (M5+M6) — 全 mock，不打真 API；不改旧测试文件。

覆盖（docs/即兴问答鲁棒性方案_v0.1.md）：
- M5.1 JSON mode 契约：response_format=json_object、finish_reason=length、空 content；
- M5.2 时间槽四形态解析（prev_month / last_n_days / absolute / month_of，
  mock time_normalizer）；未知时间模式 → 可重试错误；
- M5.3 few-shot 进提示词（原语 id 来自注册表现值）；
- M5.4 JSON 坏/枚举失败 → 错误回喂重试 ≤1 次 → 降级 keyword_route 全链路；
- M5.5 增强版 keyword_route（别名归一 + value_hints 维度补带；无别名层可跑）；
- M6.1 {"reject": true} / 枚举彻底失败 → 引导式拒答文案（含度量人话，无数字）；
- M6.2 时间缺失默认最近完整月 +「按 YYYY-MM 统计」回显。
"""

import calendar
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

_TMP = Path(tempfile.mkdtemp(prefix="llm-route-v2-"))
os.environ.setdefault("SEMANTIC_APP_DB", str(_TMP / "app.db"))
os.environ.setdefault("SEMANTIC_TRACE_LOG", str(_TMP / "trace.jsonl"))

from src.fortune_semantic.registry import REGISTRY
from src.semantic import config, engine, errors, llm_route, storage

storage.migrate()  # 全链路测试要落 trace（幂等迁移）


# ------------------------------------------------------------------ test doubles

def _resp(content, finish_reason="stop"):
    """OpenAI chat.completions 响应替身。"""
    return SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content), finish_reason=finish_reason)])


class FakeClient:
    """按脚本逐次返回；脚本耗尽后重复最后一个（ degrade 测试用）。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self._i = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses[min(self._i, len(self.responses) - 1)]
        self._i += 1
        return response


class FakeNormalizer:
    """time_normalizer.normalize_time 契约的最小替身：记录调用、四形态确定性返回。"""

    def __init__(self, fail_modes=()):
        self.fail_modes = set(fail_modes)
        self.calls = []

    def normalize_time(self, slot, today):
        self.calls.append(dict(slot))
        mode = slot.get("mode")
        if mode in self.fail_modes:
            raise ValueError(f"未知时间模式: {mode!r}")
        if mode == "absolute":  # 真实契约：from/to 键
            return {"time_from": slot["from"], "time_to": slot["to"]}
        if mode == "month_of":  # 真实契约：ref=YYYY-MM
            year, month = int(str(slot["ref"]).split("-")[0]), int(str(slot["ref"]).split("-")[1])
            last = calendar.monthrange(year, month)[1]
            return {"time_from": f"{year:04d}-{month:02d}-01",
                    "time_to": f"{year:04d}-{month:02d}-{last:02d}"}
        if mode == "last_n_days":
            return {"time_from": "2026-08-01", "time_to": "2026-08-30"}  # 滚动窗确定性替身
        if mode == "prev_month":
            return {"time_from": "2026-08-01", "time_to": "2026-08-31"}
        raise AssertionError(f"替身未覆盖的时间形态: {mode!r}")


def _plan_payload(**overrides) -> str:
    base = {"measure": "reg_user_cnt", "dimensions": ["channel_l2"]}
    base.update(overrides)
    return json.dumps(base, ensure_ascii=False)


def _no_slot_payload() -> str:
    return json.dumps({"measure": "reg_user_cnt", "dimensions": []}, ensure_ascii=False)


@pytest.fixture(autouse=True)
def _llm_env(monkeypatch):
    """本文件需要 LLM 链路开启；monkeypatch 逐用例还原，不污染其他测试文件。"""
    monkeypatch.delenv("SEMANTIC_DISABLE_LLM", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key-mock")  # mock 网关用假 key


@pytest.fixture
def normalizer(monkeypatch):
    fake = FakeNormalizer()
    monkeypatch.setattr(llm_route, "time_normalizer", fake)
    return fake


def _route(monkeypatch, responses, question="2026年8月各渠道注册用户数"):
    client = FakeClient(responses)
    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: client)
    return client, llm_route.llm_route(question)


def _final(frames):
    finals = [f for f in frames if f["kind"] == "final"]
    assert len(finals) == 1
    return finals[0]["result"]


# --------------------------------------------------------- M5.1/M5.2/M5.3 基线

def test_json_mode_contract_and_success_path(monkeypatch, normalizer):
    """M5.1：JSON mode 参数必须带上；成功路径抽出 plan + 时间区间。"""
    client, out = _route(monkeypatch, [_resp(_plan_payload(time_slot={"mode": "prev_month"}))])
    assert out["plan"].measure == "reg_user_cnt"
    assert out["time_from"] == "2026-08-01" and out["time_to"] == "2026-08-31"
    assert "time_defaulted" not in out
    assert client.calls[0]["response_format"] == {"type": "json_object"}
    assert client.calls[0]["model"] == config.LLM_MODEL
    assert normalizer.calls == [{"mode": "prev_month"}]
    assert len(client.calls) == 1  # 首发即成功，不重试


@pytest.mark.parametrize("slot,expect_from,expect_to", [
    ({"mode": "prev_month"}, "2026-08-01", "2026-08-31"),
    ({"mode": "last_n_days", "n": 30}, "2026-08-01", "2026-08-30"),
    ({"mode": "absolute", "from": "2026-08-01", "to": "2026-08-31"},
     "2026-08-01", "2026-08-31"),
    ({"mode": "month_of", "ref": "2026-08"}, "2026-08-01", "2026-08-31"),
])
def test_time_slot_four_forms(monkeypatch, normalizer, slot, expect_from, expect_to):
    """M5.2：四种时间槽形态全部解析为真实区间，槽原样进解析器。"""
    _client, out = _route(monkeypatch, [_resp(_plan_payload(time_slot=slot))])
    assert out["time_from"] == expect_from and out["time_to"] == expect_to
    assert normalizer.calls == [slot]


def test_prompt_contains_contract_and_registry_ids():
    """M5.3：提示词含四种时间槽形态、字面 JSON 样例、域外反例；
    few-shot 原语 id 与注册表现值一致（防改名漂移）。"""
    prompt = llm_route._system_prompt()
    for token in ("prev_month", "last_n_days", "absolute", "month_of",
                  '{"reject": true}', "time_slot", "示例", "filters",
                  "reg_to_real_rate", "麦当劳"):
        assert token in prompt, token
    ids = llm_route._example_ids()
    assert ids["measure"] in REGISTRY.measures
    assert ids["channel"] in REGISTRY.dimensions
    assert ids["gender"] in REGISTRY.dimensions
    assert ids["ratio"] in REGISTRY.ratios
    assert f'"dimensions": ["{ids["channel"]}"]' in prompt
    assert config.data_range()["min"] in prompt  # absolute 边界随数据覆盖走


def test_validate_plan_still_rejects_invented_primitives():
    """枚举硬校验：未注册原语/维度拒绝；渠道值条目、filters 数组与比率放行。"""
    assert llm_route.validate_plan({"measure": "aum_total"}) is None
    assert llm_route.validate_plan({"measure": "reg_user_cnt", "dimensions": ["nope"]}) is None
    assert llm_route.validate_plan({"reject": True}).rejected
    plan = llm_route.validate_plan({"measure": "reg_user_cnt", "dimensions": ["time_grain=day"]})
    assert plan.dimensions == ("time_grain=day",)
    # Gap A：非粒度维度 dim=value 与 filters 数组统一折叠为 "维度=值" 条目
    arg_plan = llm_route.validate_plan(
        {"measure": "reg_user_cnt", "dimensions": ["channel_l2=麦当劳"]})
    assert arg_plan.dimensions == ("channel_l2=麦当劳",)
    f_plan = llm_route.validate_plan(
        {"measure": "reg_user_cnt",
         "filters": [{"dimension": "channel_l2", "value": "麦当劳"}]})
    assert f_plan.dimensions == ("channel_l2=麦当劳",)
    assert llm_route.validate_plan(
        {"measure": "reg_user_cnt", "filters": [{"dimension": "nope", "value": "x"}]}) is None
    assert llm_route.validate_plan(
        {"measure": "reg_user_cnt", "filters": [{"dimension": "channel_l2", "value": ""}]}) is None
    assert llm_route.validate_plan(
        {"measure": "reg_user_cnt", "filters": [{"dimension": "time_grain", "value": "day"}]}
    ).dimensions == ()  # 粒度维度不接受值过滤
    # Gap B：比率度量进枚举
    ratio_plan = llm_route.validate_plan({"measure": "reg_to_real_rate"})
    assert ratio_plan.measure == "reg_to_real_rate"


# ------------------------------------------------------- M5.2 未知模式 / M5.4 重试

def test_unknown_time_mode_retries_with_feedback_then_degrades(monkeypatch, normalizer):
    """未知时间模式 → ValueError 归可重试 → 回喂后仍败 → 降级错误。"""
    normalizer.fail_modes.add("quantum")
    bad = _resp(_plan_payload(time_slot={"mode": "quantum"}))
    client, out = _route(monkeypatch, [bad])
    assert out["error_code"] == errors.E_ROUTE_INVALID and "plan" not in out
    assert len(client.calls) == 2  # 首发 + 1 次错误回喂
    assert len(normalizer.calls) == 2
    feedback = client.calls[1]["messages"][-1]["content"]
    assert "上一次输出不合格" in feedback and "未知时间模式" in feedback


def test_unknown_time_mode_recovers_on_retry(monkeypatch, normalizer):
    """首发未知模式，回喂重试改输出 prev_month → 成功。"""
    normalizer.fail_modes.add("quantum")
    client, out = _route(monkeypatch, [
        _resp(_plan_payload(time_slot={"mode": "quantum"})),
        _resp(_plan_payload(time_slot={"mode": "prev_month"})),
    ])
    assert out["plan"].measure == "reg_user_cnt"
    assert out["time_from"] == "2026-08-01"
    assert len(client.calls) == 2


def test_bad_json_retries_with_error_feedback_then_succeeds(monkeypatch, normalizer):
    """JSON 坏 → 错误信息回喂（assistant+user 追加）→ 重试成功。"""
    client, out = _route(monkeypatch, [
        _resp("抱歉，这个问题我无法用 JSON 回答。"),
        _resp(_plan_payload(time_slot={"mode": "prev_month"})),
    ])
    assert out["plan"].measure == "reg_user_cnt"
    assert len(client.calls) == 2
    roles = [m["role"] for m in client.calls[1]["messages"]]
    assert roles == ["system", "user", "assistant", "user"]
    feedback = client.calls[1]["messages"][-1]["content"]
    assert "上一次输出不合格" in feedback and "JSON" in feedback


def test_bad_json_twice_degrades_to_invalid_error(monkeypatch, normalizer):
    """两次 JSON 坏 → E_ROUTE_INVALID → 引擎走关键词降级（现有路径）。"""
    _client, out = _route(monkeypatch, [_resp("还是不是 JSON"), _resp("[1, 2, 3]")])
    assert out["error_code"] == errors.E_ROUTE_INVALID
    assert "error" in out and "plan" not in out
    assert "raw" in out  # 原始输出留痕（已脱敏）


def test_finish_reason_length_and_empty_content_are_retryable(monkeypatch, normalizer):
    """M5.1：length 截断与空 content 都归可重试；重试仍坏 → 降级。"""
    client, out = _route(monkeypatch, [
        _resp('{"measure": "reg_user_cnt", "dim', finish_reason="length"),
        _resp("   ", finish_reason="stop"),
    ])
    assert out["error_code"] == errors.E_ROUTE_INVALID
    assert len(client.calls) == 2
    assert normalizer.calls == []  # 两次都没到时间解析
    _client, out2 = _route(monkeypatch, [
        _resp('{"measure"', finish_reason="length"),
        _resp(_plan_payload(time_slot={"mode": "prev_month"})),
    ])
    assert out2["plan"].measure == "reg_user_cnt"  # 截断后重试可恢复


# ------------------------------------------------------------- M6.2 默认时间窗

def test_no_time_slot_defaults_to_last_complete_month(monkeypatch, normalizer):
    """M6.2：LLM 未给时间槽 → 默认最近一个完整月（prev_month 等价）+ 显式标记。"""
    _client, out = _route(monkeypatch, [_resp(_no_slot_payload())])
    assert out["time_defaulted"] is True
    assert out["time_from"] == "2026-08-01" and out["time_to"] == "2026-08-31"
    assert normalizer.calls == [{"mode": "prev_month"}]


def test_default_window_full_chain_echoes_month(monkeypatch, normalizer):
    """M6.2 全链路：默认窗生效、回答回显「按 2026-08 统计」、状态 success。"""
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp(_no_slot_payload())]))
    frames = list(engine.iter_query("注册用户数是多少"))
    result = _final(frames)
    assert result["params"] == {"time_from": "2026-08-01", "time_to": "2026-08-31"}
    assert result["state"] == "success"
    assert "2026-08" in result["answer"]  # 模板 month 槽回显统计月份
    param_steps = [s for s in result["steps"] if s["title"] == "参数抽取+校验"]
    assert param_steps and "按 2026-08 统计" in param_steps[-1]["detail"]


# --------------------------------------------------------------- M6.1 拒答引导

def test_reject_full_chain_guided_copy(monkeypatch, normalizer):
    """LLM 输出 {"reject": true} → 引导式拒答：度量/维度人话 + 示例，无数字；
    reject_card 结构不变（code/message/details）。"""
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp('{"reject": true}')]))
    result = _final(list(engine.iter_query("注册用户资产规模")))
    assert result["path"] == "rejected"
    card = result["reject_card"]
    assert set(card) == {"code", "message", "details"}
    assert "reg_user_cnt" in card["details"]["available_measures"]
    answer = result["answer"]
    assert "这个问题我答不了" in answer
    assert "注册用户数" in answer  # 度量人话清单（注册表现生成）
    assert "渠道" in answer  # 维度人话清单
    assert "例如" in answer
    assert not any(ch.isdigit() for ch in answer)  # 演示红线：拒答文案无数字


def test_enum_failure_degrades_via_keyword_to_guided_reject(monkeypatch, normalizer):
    """M6.1：LLM 枚举校验彻底失败 → 关键词降级命中拒答域 → 同样引导式文案。"""
    bad = _resp(_plan_payload(measure="aum_total", dimensions=[]))
    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient([bad]))
    result = _final(list(engine.iter_query("注册用户资产规模")))
    assert result["path"] == "rejected"
    assert "我能答" in result["answer"]
    assert "渠道" in result["answer"]


def test_total_miss_degrades_to_unregistered_guided(monkeypatch, normalizer):
    """LLM 失败且关键词零命中 → unregistered 路径也升级为引导式拒答。"""
    bad = _resp(_plan_payload(measure="aum_total", dimensions=[]))
    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient([bad]))
    result = _final(list(engine.iter_query("附近有什么好吃的餐厅")))
    assert result["path"] == "unregistered"
    assert "我能答" in result["answer"]
    assert not any(ch.isdigit() for ch in result["answer"])


# ------------------------------------------------- M5.5 增强版 keyword_route

def test_enhanced_keyword_route_with_value_hints(monkeypatch):
    """别名归一 + value_hints 命中 → 对应维度补带。
    现契约（aliases.py）：value_hints 为问题命中的渠道成员值字符串（已按问题
    匹配）；渠道值族挂 channel_l2（M3 实体链接器再做层级细分+值下推）。"""
    fake_aliases = SimpleNamespace(
        normalize_text=lambda q: q.replace("来了多少人", "注册用户数"),
        expand_candidates=lambda q: {"measure_hints": ["reg_user_cnt"],
                                     "dimension_hints": [],
                                     "value_hints": ["优享+线上", "优享+企微"]},
    )
    monkeypatch.setattr(llm_route, "aliases", fake_aliases)
    plan = llm_route.keyword_route("优享+来了多少人")
    assert plan.measure == "reg_user_cnt"
    assert "channel_l2" in plan.dimensions
    # 无 value_hints → 不额外带维度
    plain = SimpleNamespace(
        normalize_text=lambda q: q.replace("来了多少人", "注册用户数"),
        expand_candidates=lambda q: {"measure_hints": ["reg_user_cnt"],
                                     "dimension_hints": [], "value_hints": []},
    )
    monkeypatch.setattr(llm_route, "aliases", plain)
    plan2 = llm_route.keyword_route("来了多少人")
    assert plan2.measure == "reg_user_cnt"
    assert "channel_l2" not in plan2.dimensions


def test_enhanced_keyword_route_value_hints_forward_compat_dict(monkeypatch):
    """前向兼容：value_hints 若升级为带维度对象则直接采用其维度。"""
    fake_aliases = SimpleNamespace(
        normalize_text=lambda q: q,
        expand_candidates=lambda q: {"measure_hints": [], "dimension_hints": [],
                                     "value_hints": [{"dimension": "channel_l3", "value": "X"}]},
    )
    monkeypatch.setattr(llm_route, "aliases", fake_aliases)
    plan = llm_route.keyword_route("X渠道注册了多少人")
    assert plan.measure == "reg_user_cnt"
    assert "channel_l3=X" in plan.dimensions


def test_enhanced_keyword_route_survives_alias_errors(monkeypatch):
    """别名层抛异常 → 兜底链路不受影响。"""
    def _boom(*args):
        raise RuntimeError("alias layer down")
    monkeypatch.setattr(llm_route, "aliases",
                        SimpleNamespace(normalize_text=_boom, expand_candidates=_boom))
    plan = llm_route.keyword_route("2026年8月各渠道注册用户数")
    assert plan.measure == "reg_user_cnt" and "channel_l2" in plan.dimensions


def test_enhanced_keyword_route_without_aliases(monkeypatch):
    """无别名层（并行任务未就位/降级为 None）→ 现有关键词表照常工作。"""
    monkeypatch.setattr(llm_route, "aliases", None)
    plan = llm_route.keyword_route("2026年8月各渠道注册用户数")
    assert plan.measure == "reg_user_cnt" and plan.dimensions == ("channel_l2",)
    assert llm_route.keyword_route("抽奖活动效果怎么样").rejected


def test_keyword_route_adopts_measure_hints():
    """真实别名层：关键词表缺口语（"来了多少人"）→ measure_hints 兜底命中。"""
    plan = llm_route.keyword_route("来了多少人")
    assert plan.measure == "reg_user_cnt"


def test_keyword_route_measure_hints_other_measure():
    """"实名了多少人" → real_name_user_cnt（已注册度量直接采信）。"""
    plan = llm_route.keyword_route("实名了多少人")
    assert plan.measure == "real_name_user_cnt"


def test_keyword_route_adopts_dimension_hints():
    """dimension_hints 同理补维度："男的和女的来了多少人" → reg_user_cnt + gender。"""
    plan = llm_route.keyword_route("男的和女的来了多少人")
    assert plan.measure == "reg_user_cnt"
    assert "gender" in plan.dimensions


# -------------------------------------------------- Gap A 值过滤端到端 / Gap B 比率

def test_keyword_route_single_value_hint_becomes_filter(monkeypatch):
    """单一渠道值候选 → "channel_l2=值" 过滤条目（不再是全量细分）。"""
    fake_aliases = SimpleNamespace(
        normalize_text=lambda q: q.replace("来了多少人", "注册用户数"),
        expand_candidates=lambda q: {"measure_hints": ["reg_user_cnt"],
                                     "dimension_hints": [],
                                     "value_hints": ["优享+线上"]},
    )
    monkeypatch.setattr(llm_route, "aliases", fake_aliases)
    plan = llm_route.keyword_route("优享+线上来了多少人")
    assert plan.measure == "reg_user_cnt"
    assert plan.dimensions == ("channel_l2=优享+线上",)


def test_llm_filter_full_chain_sql_and_answer(monkeypatch, normalizer):
    """验收①：8月麦当劳来了多少人 → 编译 SQL 含 sec_chnl_nm = ? 且参数为麦当劳，
    交叉校验两侧同滤，state=success（数字全部可溯源）。"""
    payload = json.dumps({"measure": "reg_user_cnt", "dimensions": [],
                          "filters": [{"dimension": "channel_l2", "value": "麦当劳"}],
                          "time_slot": {"mode": "month_of", "ref": "2026-08"}},
                         ensure_ascii=False)
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp(payload)]))
    result = _final(list(engine.iter_query("8月麦当劳来了多少人")))
    assert result["path"] == "semantic_pushdown"
    assert result["state"] == "success"
    assert "sec_chnl_nm = ?" in result["sql"]
    assert "麦当劳" in result["sql_params"]  # 值走绑定参数，永不拼 SQL
    assert result["filters"] == [{"dimension": "channel_l2", "value": "麦当劳"}]
    assert result["answer"]  # 有真实数字且通过 D6 溯源门禁


def test_llm_filter_with_group_dimension(monkeypatch, normalizer):
    """验收②：银行App/中信书院类问法 → 维度分组正确（filter 不混入 dimensions）。"""
    payload = json.dumps({"measure": "reg_user_cnt", "dimensions": ["channel_l1"],
                          "filters": [{"dimension": "channel_l2", "value": "银行App"}],
                          "time_slot": {"mode": "month_of", "ref": "2026-08"}},
                         ensure_ascii=False)
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp(payload)]))
    result = _final(list(engine.iter_query("银行App上个月注册了多少")))
    assert result["path"] == "semantic_pushdown"
    assert result["state"] == "success"
    # dimensions 留痕含过滤条目（路由决策）；SQL 分组仅 channel_l1，过滤走 WHERE
    assert result["dimensions"] == ["channel_l1", "channel_l2=银行App"]
    assert "银行App" in result["sql_params"]


def test_llm_unknown_channel_clarify_reject(monkeypatch, normalizer):
    """验收①反向：编造渠道值 → 澄清式拒答「未找到该渠道」（宁拒不错）。"""
    payload = json.dumps({"measure": "reg_user_cnt",
                          "filters": [{"dimension": "channel_l2", "value": "不存在的渠道"}]},
                         ensure_ascii=False)
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp(payload)]))
    result = _final(list(engine.iter_query("8月不存在的渠道来了多少人")))
    assert result["path"] == "rejected"
    card = result["reject_card"]
    assert card["code"] == "UNKNOWN_DIMENSION_VALUE"
    assert "未找到该渠道" in card["message"]
    assert "不存在的渠道" in result["answer"]
    assert not any(ch.isdigit() for ch in result["answer"])


def test_ratio_measure_routes_and_executes(monkeypatch, normalizer):
    """验收③：转化率条目路由到 reg_to_real_rate 并全链路执行（表格呈现）。"""
    payload = json.dumps({"measure": "reg_to_real_rate", "dimensions": []},
                         ensure_ascii=False)
    monkeypatch.setattr("openai.OpenAI",
                        lambda **kwargs: FakeClient([_resp(payload)]))
    result = _final(list(engine.iter_query("注册到实名的转化率")))
    assert result["measure"] == "reg_to_real_rate"
    assert result["path"] == "semantic_pushdown"
    assert result["state"] == "success"
    assert "转化率" in result["answer"]
