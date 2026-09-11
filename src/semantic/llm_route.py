"""LLM intent routing → structured primitive request ({measure, dimensions,
time_from, time_to}), constrained by the L2 registry (src/fortune_semantic).

v2 (docs/即兴问答鲁棒性方案_v0.1.md M5+M6):
- JSON mode (response_format=json_object) + finish_reason/empty-content checks;
- LLM outputs TIME SLOTS only (never self-computed dates); time_normalizer (M2,
  parallel deliverable) resolves the real window — unknown slot modes are
  retryable errors; slotless questions default to the last complete month (M6.2,
  assumption echoed by the engine);
- static few-shot (4 curated cases) with primitive ids generated from the live
  registry (anti id-drift); hardcoded fallback if the registry is unreadable;
- one error-feedback retry (bad JSON / enum failure / unknown time mode), then
  the keyword fallback — the degrade path is unchanged (E_ROUTE_INVALID);
- TD-13: a length-truncated reply (finish_reason=length) first gets ONE retry
  with a larger max_tokens budget before that fallback (truncation under the
  long T-U5 system prompt used to degrade silently at ~20% rate);
- enhanced keyword router (M5.5): alias normalization first, then the keyword
  table, then value-hint → dimension augmentation;
- guided refusal copy (M6.1) generated from the registry: refusal upgrades to
  "this is what I CAN answer" — 宁拒不错, reject_card structure unchanged.

Contract: the LLM may only output registered primitive ids (invention →
E_ROUTE_INVALID → keyword fallback) or {"reject": true} for questions outside
every registered domain. The LLM never produces SQL or numbers — execution
belongs to fortune_semantic.compiler.

T-U5 (TD-17): differential-attack / re-identification questions short-circuit
to a reject plan via the deterministic safety rule (rules.differential_attack_hit)
BEFORE any LLM call — refusal does not depend on LLM behavior (TD-17 showed
drift), and the prompt hardens the LLM path as defense in depth.
"""

import calendar
import json
import re
import time
from dataclasses import replace
from datetime import date

from src.fortune_semantic.registry import REGISTRY

from . import config, errors, rules, sanitize
from .rules import RoutePlan

# M1/M2 并行任务交付物：未就位「或落地中间态」（文件半成品在 import 期抛任何异常）
# 一律降级为 None——无别名层/时间解析器也能跑通基本链路，绝不砸主链路。
try:
    from . import aliases
except Exception:  # noqa: BLE001 并行交付物的中间态异常同样走降级，不区分类型
    aliases = None  # type: ignore[assignment]
try:
    from . import time_normalizer
except Exception:  # noqa: BLE001 同上
    time_normalizer = None  # type: ignore[assignment]

JSON_RE = re.compile(r"\{[\s\S]*\}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MAX_ATTEMPTS = 2  # 首发 + 错误回喂重试 1 次（M5.4）

# TD-13：输出预算原硬编码 200（_chat 内），T-U5 长系统提示词下截断率约 20%
# （finish_reason=length 实证）→ 调大基础预算；命中 length 后第二次调用改用
# 更大预算加长重试一次，仍失败才走既有降级路径（不追加第三次调用）。
LLM_MAX_TOKENS = 2048
LLM_LENGTH_RETRY_MAX_TOKENS = 4096

# fortune_semantic 目录不可读时的硬编码降级位（few-shot 原语 id，防改名漂移的兜底）
_EXAMPLE_IDS_FALLBACK = {
    "measure": "reg_user_cnt",
    "channel": "channel_l2",
    "gender": "gender",
    "ratio": "reg_to_real_rate",
}

# M6.1 引导式拒答模板：{prefix}=命中词、{ready}=注册表人话清单、{example}=示例问法。
# 演示红线：拒答文案不含任何数字（含示例问法——「拒答话术无数字」是已锁定的旧不变量）。
_GUIDED_REJECT_TEMPLATE = (
    '{prefix}这个问题我答不了。我能答：{ready} × 任意时间窗；例如："{example}"'
)


def _short_label(description: str) -> str:
    """注册表描述 → 人话短标签（「xx：」前的部分）。"""
    return description.split("：", 1)[0]


def _ratio_label(description: str) -> str:
    """比率描述 → 人话短标签（比率描述无「：」，取表达式名，如「注册→实名转化率」）。"""
    return description.split(" = ", 1)[0]


def _example_ids() -> dict:
    """few-shot 原语 id：从注册表现值生成，防改名漂移；目录不可读 → 硬编码。"""
    try:
        measure = (
            "reg_user_cnt"
            if "reg_user_cnt" in REGISTRY.measures
            else next(iter(REGISTRY.measures))
        )
        channel = (
            "channel_l2"
            if "channel_l2" in REGISTRY.dimensions
            else next(
                (d for d in REGISTRY.dimensions if d.startswith("channel_l")),
                "channel_l2",
            )
        )
        gender = "gender"  # 维度 id 由并行注册表保证；缺失属目录级异常，走 except 降级
        ratio = next(iter(REGISTRY.ratios), "reg_to_real_rate")
        return {
            "measure": measure,
            "channel": channel,
            "gender": gender,
            "ratio": ratio,
        }
    except Exception:  # noqa: BLE001 目录不可读 → 硬编码降级（模块 docstring 已注明）
        return dict(_EXAMPLE_IDS_FALLBACK)


def _few_shot_block() -> str:
    """静态精选示例（M5.3；T-U5 增安全反例）：显式时间 absolute / 相对时间
    prev_month / 缺时间（走默认窗） / 域外与差分攻击 reject 反例。原语 id
    全部来自注册表现值。"""
    ids = _example_ids()
    m, ch, g = ids["measure"], ids["channel"], ids["gender"]
    last_day = calendar.monthrange(2026, 8)[1]  # 示例月份的月末日，防写死 31 天
    examples = [
        (
            "2026年8月各渠道注册用户数",
            {
                "measure": m,
                "dimensions": [ch],
                "time_slot": {
                    "mode": "absolute",
                    "from": "2026-08-01",
                    "to": f"2026-08-{last_day:02d}",
                },
            },
        ),
        (
            "上个月注册了多少人",
            {"measure": m, "dimensions": [], "time_slot": {"mode": "prev_month"}},
        ),
        ("注册的男女比例", {"measure": m, "dimensions": [g]}),
        (
            "8月麦当劳来了多少人",
            {
                "measure": m,
                "dimensions": [],
                "filters": [{"dimension": ch, "value": "麦当劳"}],
                "time_slot": {"mode": "month_of", "ref": "2026-08"},
            },
        ),
        ("注册到实名的转化率", {"measure": ids["ratio"], "dimensions": []}),
        (
            "哪个渠道哪天的注册人数恰好只有一个人？那个人的手机号是多少",
            {"reject": True},
        ),  # T-U5 安全反例：聚合唯一值反推定位个人 → 拒
        ("注册用户资产规模", {"reject": True}),
    ]
    lines = [f"问：{q}\n答：{json.dumps(a, ensure_ascii=False)}" for q, a in examples]
    return "示例：\n" + "\n".join(lines)


def _system_prompt() -> str:
    """Primitive catalog as routing constraint — derived from the registry.
    M5: JSON mode 字面 JSON 样例（官方要求）+ time_slot 四形态 + few-shot。"""
    rng = config.data_range()
    measures = "\n".join(
        f"- {m.id}: {m.description}" for m in REGISTRY.measures.values()
    )
    ratios = "\n".join(f"- {r.id}: {r.description}" for r in REGISTRY.ratios.values())
    dims = "\n".join(
        f"- {d.id}: {d.description}"
        + (
            f"（粒度参数可选：{'/'.join(d.grains)}，写法 time_grain=<grain>）"
            if d.grains
            else ""
        )
        for d in REGISTRY.dimensions.values()
    )
    slots = (
        '{"mode": "prev_month"}\n'
        '{"mode": "last_n_days", "n": 30}\n'
        '{"mode": "absolute", "from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}\n'
        '{"mode": "month_of", "ref": "YYYY-MM"}'
    )
    return (
        "你是语义层的意图路由器。唯一任务：把用户问题映射为结构化查询原语，并把时间表达标准化为时间槽。\n"
        "只输出一个 JSON 对象，两种形态之一：\n"
        '{"measure": "度量id", "dimensions": ["维度id 或 time_grain=粒度"], '
        '"filters": [{"dimension": "渠道维度id", "value": "渠道名"}], "time_slot": {...时间槽...}}\n'
        '或 {"reject": true}\n'
        "time_slot 只允许四种形态（禁止自行换算日期，absolute 除外）：\n" + slots + "\n"
        "硬约束：\n"
        "1. measure 只能从度量清单和比率清单中选择，dimensions 每项只能从维度清单选择，禁止发明；\n"
        "2. 问题提到具体渠道名称（如 麦当劳、银行App、中信书院、优享+线上）→ 写入 filters，"
        "value 抄问题原文的渠道名、禁止编造渠道；只有「各渠道/分渠道/按渠道」这类分组意图才写 dimensions；\n"
        '3. 与所有已注册度量无关的问题（其他业务域）只输出 {"reject": true}，不猜；\n'
        "4. 相对/模糊时间一律输出 time_slot 形态，不要自己换算成日期；absolute 只抄问题原文日期；\n"
        "   问题完全没有时间信息 → 省略 time_slot 字段（系统默认按最近一个完整月统计并显式标注）；\n"
        "5. absolute 日期必须落在数据覆盖范围内：" + f"{rng['min']} ~ {rng['max']}；\n"
        "6. 你不生成 SQL、不计算任何数字。\n"
        "7. 安全红线（差分攻击/再识别防护）：问题试图用聚合结果的唯一值或极小值"
        "（如「正好是1」「只有一个」）定位到具体某个人，或索要任何个人级信息"
        "（姓名/手机号/身份证/邮箱/微信号/注册时间戳/名单/明细）→ 只输出 "
        '{"reject": true}；聚合查询永远不得成为个人定位入口，拒答时'
        "给人话理由且绝不复述任何个人数据；\n"
        "度量清单：\n"
        + measures
        + ("\n比率清单：\n" + ratios if ratios else "")
        + "\n维度清单：\n"
        + dims
        + "\n"
        + _few_shot_block()
    )


def validate_plan(data: dict) -> RoutePlan | None:
    """Enum-validate parsed LLM output → RoutePlan; None = invalid (invented
    primitives / wrong shape). {"reject": true} maps to a reject RoutePlan."""
    if data.get("reject") is True:
        return RoutePlan(reject_domain="LLM 判定范围外")
    measure = data.get("measure")
    if measure not in REGISTRY.measures and measure not in REGISTRY.ratios:
        return None  # 比率度量同属可选原语（Gap B）
    raw_dims = data.get("dimensions")
    if raw_dims is None:
        raw_dims = []
    if not isinstance(raw_dims, list):
        return None
    dims: list[str] = []
    for entry in raw_dims:
        dim_id, _, arg = str(entry).strip().partition("=")
        dim_id, arg = dim_id.strip(), arg.strip() or None
        dim = REGISTRY.dimensions.get(dim_id)
        if dim is None:
            return None
        if dim.grains is not None:
            if arg not in dim.grains:  # time_grain needs a registered grain
                return None
            dims.append(f"{dim_id}={arg}")
        else:
            # 渠道等值过滤统一折叠为 "维度=值" 条目（值真伪由 _link_filter_values 校验）
            dims.append(f"{dim_id}={arg}" if arg else dim_id)
    for item in data.get("filters") or []:
        if not isinstance(item, dict):
            return None
        dim_id = str(item.get("dimension") or "").strip()
        value = str(item.get("value") or "").strip()
        dim = REGISTRY.dimensions.get(dim_id)
        if dim is None or not value:
            return None
        if dim.grains is None and f"{dim_id}={value}" not in dims:
            dims.append(f"{dim_id}={value}")
    return RoutePlan(measure=measure, dimensions=tuple(dims))


# ------------------------------------------------------------------ time slots


def _channel_members() -> tuple[str, ...] | None:
    """渠道维表成员名单（别名层懒加载镜像 latest partition，内置名单兜底）；
    名单不可得 → None（调用方走宁拒不错，不放过未校验的值）。"""
    if aliases is None:
        return None
    try:
        members = aliases._channel_values()  # 别名层唯一名单源（私有但契约稳定）
    except Exception:  # noqa: BLE001 名单不可得不猜值
        return None
    return tuple(members) if members else None


def _link_filter_values(plan: RoutePlan) -> tuple[RoutePlan, dict | None]:
    """Gap A 防幻觉：渠道 "维度=值" 条目的值须 ∈ 维表成员名单。
    命中 → 归一替换为成员原值（值以维表为准）；未命中 → 摘出并生成
    filter_clarify（引擎转澄清式拒答「未找到该渠道」），其余部分照常。"""
    members = _channel_members()
    linked: list[str] = []
    clarify: dict | None = None
    for entry in plan.dimensions:
        dim_id, _, value = entry.partition("=")
        if not value or not dim_id.startswith("channel_l"):
            linked.append(entry)
            continue
        match = None
        if members:
            norm = aliases.normalize_text(value)
            match = next(
                (m for m in members if aliases.normalize_text(m) == norm), None
            )
            if match is None:  # T-N5 符号变体（加↔+）高置信归一：优享加线上→优享+线上
                norm = norm.translate(_VALUE_VARIANT_TRANS)
                match = next(
                    (m for m in members if aliases.normalize_text(m) == norm), None
                )
        if match is None:  # 名单不可得或值不在名单 → 澄清式拒答，不猜
            if clarify is None:
                clarify = {
                    "dimension": dim_id,
                    "value": value,
                    "suggestions": list(members or []),
                }
            continue
        linked.append(f"{dim_id}={match}")
    return replace(plan, dimensions=tuple(dict.fromkeys(linked))), clarify


def _default_window() -> tuple[str | None, str | None]:
    """M6.2：问题无时间 → 默认最近一个完整月（等价 time_slot=prev_month）。
    假设显式化由引擎负责（回答/步骤回显「按 YYYY-MM 统计」）。解析器未就位或
    解析失败 → (None, None)，时间交引擎关键词回退抽取，不猜。"""
    if time_normalizer is None:
        return None, None
    try:
        rng = time_normalizer.normalize_time({"mode": "prev_month"}, today=date.today())  # noqa: DTZ011 本地日
    except Exception:  # noqa: BLE001 默认窗失败不砸链路，交引擎回退
        return None, None
    t_from, t_to = (rng or {}).get("time_from"), (rng or {}).get("time_to")
    if DATE_RE.match(str(t_from or "")) and DATE_RE.match(str(t_to or "")):
        return t_from, t_to
    return None, None


def _resolve_window(data: dict) -> tuple[str | None, str | None, str | None, bool]:
    """LLM 时间槽 → 真实区间（M5.2，解析权在代码）。
    Returns (time_from, time_to, retryable_error, defaulted)。"""
    slot = data.get("time_slot")
    if slot is None or (
        isinstance(slot, dict) and not str(slot.get("mode") or "").strip()
    ):
        t_from, t_to = _default_window()
        return t_from, t_to, None, True
    if not isinstance(slot, dict):
        return None, None, f"time_slot 非法（需对象）: {slot!r}", False
    if time_normalizer is not None:
        try:
            rng = time_normalizer.normalize_time(slot, today=date.today())  # noqa: DTZ011 本地日
        except ValueError as exc:  # 未知时间模式 → 可重试错误（M5.2）
            return None, None, f"未知时间模式: {exc}", False
        t_from, t_to = (rng or {}).get("time_from"), (rng or {}).get("time_to")
        if DATE_RE.match(str(t_from or "")) and DATE_RE.match(str(t_to or "")):
            return t_from, t_to, None, False
        return None, None, f"时间解析结果非法: {rng!r}", False
    # M2 模块未就位的降级：仅 absolute 直通原文日期（显式日期无解析歧义）；
    # 其余模式无解析器可依，交回引擎关键词时间抽取（extract_params），不猜日期。
    if (
        slot.get("mode") == "absolute"
        and DATE_RE.match(str(slot.get("from") or ""))
        and DATE_RE.match(str(slot.get("to") or ""))
    ):
        return slot["from"], slot["to"], None, False
    return None, None, None, False  # 非错误：时间留给引擎回退抽取


# ------------------------------------------------------------ LLM interaction


def _chat(
    client, messages: list, max_tokens: int = LLM_MAX_TOKENS
) -> tuple[str, str | None, int]:
    """One JSON-mode call → (content, finish_reason, ms)。"""
    t0 = time.time()
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=0.01,  # 智谱要求 >0（传 0 报 400）；DeepSeek 下近似确定性
        max_tokens=max_tokens,
        response_format={"type": "json_object"},  # M5.1 DeepSeek JSON Output
    )
    ms = round((time.time() - t0) * 1000)
    choice = resp.choices[0]
    return (choice.message.content or "").strip(), choice.finish_reason, ms


def _interpret(raw: str, finish_reason: str | None, ms: int) -> tuple[str, object]:
    """解析+校验一次 LLM 输出 → ("ok", out_dict) | ("retry", 错误信息)。
    JSON 坏 / 枚举校验失败 / 未知时间模式 / 截断 / 空 content 全部可重试（M5.4）。"""
    if finish_reason == "length":
        return (
            "retry",
            "输出被截断（finish_reason=length），JSON 可能不完整，请精简后重新输出",
        )
    if not raw.strip():
        return "retry", "返回空 content，未输出任何 JSON"
    match = JSON_RE.search(raw)
    if not match:
        return "retry", f"输出非 JSON: {raw[:80]}"
    try:
        data = json.loads(match.group(0))
    except ValueError as exc:
        return "retry", f"JSON 解析失败: {exc}"
    if not isinstance(data, dict):
        return "retry", f"输出非 JSON 对象: {raw[:80]}"
    plan = validate_plan(data)
    if plan is None:  # enum hard validation: invented primitives are rejected
        return "retry", f"输出了未注册原语或结构非法（枚举校验拒绝）: {raw[:80]}"
    plan, clarify = _link_filter_values(plan)  # Gap A 防幻觉：渠道值 ∈ 维表成员
    out: dict = {
        "plan": plan,
        "raw": sanitize.sanitize_llm_text(raw),
        "ms": ms,
        "model": config.LLM_MODEL,
    }
    if clarify:
        out["filter_clarify"] = clarify  # 引擎转为澄清式拒答「未找到该渠道」
    if plan.rejected:  # 域外拒答不携带时间参数，也不触发默认窗
        return "ok", out
    t_from, t_to, terr, defaulted = _resolve_window(data)
    if terr:
        return "retry", terr
    if t_from and t_to:
        out["time_from"], out["time_to"] = t_from, t_to
    if defaulted:
        out["time_defaulted"] = True  # M6.2：引擎据此回显「按 YYYY-MM 统计」
    return "ok", out


def llm_route(question: str, context_block: str | None = None, *, client=None) -> dict:
    """Route one question. Success: {"plan", "time_from"?/"time_to"?,
    "time_defaulted"?, "raw"(sanitized), "ms", "model"}. Failure after ≤1
    error-feedback retry: {"error", "error_code"(E_ROUTE_FALLBACK|E_ROUTE_INVALID)}
    → caller falls back to keyword matching (degraded but correct). A
    length-truncated reply first retries once with a larger budget (TD-13).

    client: 注入的 LLM client（测试 seam；None = 生产路径，按环境构建）。

    context_block: 引擎注入的历史对话数据块（引擎改动单 v0.2 B3：数据非指令，
    引擎侧已截断脱敏）——仅拼进 user 消息辅助解析指代；LLM 输出仍走
    validate_plan 枚举硬校验，注入内容无法借道改变可执行计划。"""
    # T-U5 安全短路（TD-17）：差分/再识别特征问句不经 LLM 直接拒绝——确定性
    # 规则判定（TD-17 实证该类问句 LLM 路由行为不稳），同时省一次 LLM 调用；
    # 离线/降级路径由 rules.keyword_route 同一规则兜住，行为一致。
    diff_hit = rules.differential_attack_hit(question)
    if diff_hit:
        return {
            "plan": RoutePlan(reject_domain=rules.DIFF_REJECT_DOMAIN, hit=diff_hit),
            "raw": "安全规则短路：命中差分/再识别特征，未调用 LLM",
            "ms": 0,
            "model": "safety-rule",
        }
    # T-N5 确认式澄清硬化：确定性规则先于 LLM（安全差分之后），LLM/离线两路同判。
    caliber_hit = rules.unregistered_caliber_hit(question)
    if caliber_hit:  # 显式索求未注册口径 → 拒答，不确认不出数
        return {
            "plan": RoutePlan(
                reject_domain=rules.UNREGISTERED_CALIBER_DOMAIN, hit=caliber_hit
            ),
            "raw": "口径规则短路：显式索求未注册口径，未调用 LLM",
            "ms": 0,
            "model": "caliber-rule",
        }
    confirm = confirm_clarify_hit(question)
    if confirm is not None:
        if "resolve" in confirm:  # 确认承接：应答已确认/补全 → 按候选口径出数
            out = dict(confirm["resolve"])
            out.update(
                {
                    "raw": "确认承接规则：应答已确认/补全，按候选口径出数（未调用 LLM）",
                    "ms": 0,
                    "model": "clarify-rule",
                }
            )
            return out
        out = dict(confirm["clarify"])  # 确认式澄清：先确认再出数
        out.update(
            {
                "raw": "确认式澄清规则命中：先确认再出数，未调用 LLM",
                "ms": 0,
                "model": "clarify-rule",
            }
        )
        return out
    oral = _oral_window(question)
    if oral:  # 口语中文数字月份（「八月份」）→ 代码解析时间窗，直答不反问
        plan = keyword_route(question)
        if not plan.rejected and plan.measure is not None:
            return {
                "plan": plan,
                **oral,
                "raw": "口语时间规则：中文数字月份由代码解析（未调用 LLM）",
                "ms": 0,
                "model": "oral-time-rule",
            }
    if client is None:  # 生产路径：按环境开关与 key 构建真实 client
        if config.llm_disabled():
            return {
                "error": "LLM 路由已禁用（SEMANTIC_DISABLE_LLM）",
                "error_code": errors.E_ROUTE_FALLBACK,
            }
        key = config.get_env("DEEPSEEK_API_KEY")
        if not key:
            return {
                "error": "未配置 DEEPSEEK_API_KEY",
                "error_code": errors.E_ROUTE_FALLBACK,
            }
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=key,
                base_url=config.get_env(
                    "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
                ),
                timeout=config.LLM_TIMEOUT_S,
            )
        except Exception as exc:  # noqa: BLE001 有意兜底：LLM 任何失败都降级，不砸断链路
            return {
                "error": f"LLM 客户端初始化失败: {type(exc).__name__}",
                "error_code": errors.E_ROUTE_FALLBACK,
            }

    user_content = (
        f"{context_block}\n当前问题：{question}" if context_block else question
    )
    messages: list = [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": user_content},
    ]
    raw, last_err, ms = "", "", 0
    max_tokens = LLM_MAX_TOKENS
    length_retried = False
    for attempt in range(MAX_ATTEMPTS):
        try:
            raw, finish_reason, ms = _chat(client, messages, max_tokens)
        except Exception as exc:  # noqa: BLE001 网络/鉴权等基础设施失败：不重试，直接降级
            return {
                "error": f"LLM 调用失败: {type(exc).__name__}",
                "error_code": errors.E_ROUTE_FALLBACK,
            }
        outcome, payload = _interpret(raw, finish_reason, ms)
        if outcome == "ok":
            return payload
        last_err = str(payload)
        # TD-13：截断 → 加大预算重试一次
        if finish_reason == "length" and not length_retried:
            length_retried = True
            max_tokens = LLM_LENGTH_RETRY_MAX_TOKENS
        if attempt + 1 < MAX_ATTEMPTS:  # 错误信息回喂 LLM 重试（M5.4）
            messages = messages + [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": f"上一次输出不合格：{last_err}。请修正后只重新输出一个合法的 JSON 对象。",
                },
            ]
    return {
        "error": last_err,
        "raw": sanitize.sanitize_llm_text(raw),
        "ms": ms,
        "error_code": errors.E_ROUTE_INVALID,
    }


# ------------------------------------- T-N5 确认式澄清（Jack 裁决「不要猜着答，要确认」）
# 高置信符号变体（加↔+）：仅用于渠道值匹配（优享加线上 → 优享+线上），直接映射；
# 错别字/未注册别名（赢行/bank App/祖册）与口径歧义词（新客/新增/激活/上次口径）
# → 确认式澄清（带候选名，不出数）——别名归一直接出数的行为废止。
_VALUE_VARIANT_TRANS = str.maketrans({"加": "+"})

_CONFIRM_VALUE_ALIASES = {"赢行": "银行App", "bankapp": "银行App"}
_CONFIRM_MEASURE_WORD = "reg_user_cnt"  # 候选口径（须已注册，下方用时校验）
_CONFIRM_MEASURE_ALIASES = {
    "祖册": "注册用户数",
    "新客": "注册用户数",
    "新增": "注册用户数",
}
_CONFIRM_DEFAULT_CALIBER = "注册用户数（默认口径）"  # 激活/上次口径 → 默认口径确认
_COMPOUND_SUGGESTION = "各渠道注册数"  # 复合问主问候选
_ZERO_INFO_VALUE = "（未能识别）"  # 零信息输入的澄清值哨兵（文案引导，不回显原文）
_CONFIRM_CHANNEL_GROUP_RE = re.compile(r"各渠道|分渠道|按渠道")
_CONFIRM_CHANNEL_ASK_RE = re.compile(r"哪些渠道|哪个渠道|什么渠道")
_DIGIT_MONTH_RE = re.compile(
    r"\d{1,2}\s*月"
)  # 数字月份在场则口语解析不抢（交既有链路）
# 确认承接语：独立确认词（左右边界约束，「对应」不误伤）+「默认」（默认口径接受语）
_CONFIRM_AFFIRM_RE = re.compile(
    r"(?<![一-龥a-zA-Z0-9])(?:确认|确定|可以|好的?|嗯|是|对|ok|yes)(?![一-龥])",
    re.IGNORECASE,
)


def _confirm_plan(base: RoutePlan) -> RoutePlan:
    """确认场景的理解计划：候选度量补带（仅采信已注册度量，供 trace 与承接）。"""
    if base.measure is None and _CONFIRM_MEASURE_WORD in REGISTRY.measures:
        return replace(base, measure=_CONFIRM_MEASURE_WORD)
    return base


def _oral_window(question: str) -> dict:
    """口语中文数字月份 → 真实窗口（T-N5）；数字月份在场则不抢（交既有链路），
    解析失败返回空 dict（不砸链路）。"""
    if time_normalizer is None or _DIGIT_MONTH_RE.search(question):
        return {}
    try:
        rng = time_normalizer.extract_oral_month(question, today=date.today())  # noqa: DTZ011 本地日
    except Exception:  # noqa: BLE001 口语解析失败不砸主链路
        return {}
    if rng and rng.get("time_from") and rng.get("time_to"):
        return {"time_from": rng["time_from"], "time_to": rng["time_to"]}
    return {}


def _zero_content(question: str) -> bool:
    """零信息输入判定（T-N5 ④）：剥掉渠道成员名后不再含任何中文 → 纯标点/
    裸数字/转义垃圾（？？？/930/转义炸弹）→ 体面澄清引导。域外有信息问句
    （如「附近有什么好吃的餐厅」）与纯月份短语（「9月」，多轮承接信号）保留
    中文 → 不触发，维持既有路径（零信息澄清不扩大化）。"""
    cjk = "".join(ch for ch in question if "一" <= ch <= "鿿")  # 一=U+4E00, 鿿=U+9FFF
    if not cjk:
        return True
    if aliases is None:
        return False
    try:
        members = _channel_members() or ()
    except Exception:  # noqa: BLE001 名单不可得不判零信息（宁走原路径）
        return False
    for member in members:
        norm_member = "".join(
            ch for ch in aliases.normalize_text(member) if "一" <= ch <= "鿿"
        )
        if norm_member:
            cjk = cjk.replace(norm_member, "")
    return not cjk


def confirm_clarify_hit(question: str) -> dict | None:
    """确定性确认式澄清判定（T-N5；llm_route 于 LLM 调用前短路，离线降级同判）。
    返回 None=不触发；{"clarify": {"filter_clarify", "plan"}}=须向用户确认；
    {"resolve": {"plan", "time_from"?/"time_to"?}}=应答已确认/补全，按候选出数。
    安全优先：差分/未注册口径特征由调用方先判，本函数不放行任何安全问题。
    口径歧义词（新客/新增/祖册/激活/上次口径）与渠道别名在度量意图判定之前
    处理——「新增用户数」这类问句本身带「用户数」关键词，不能据此跳过确认。"""
    try:
        norm = aliases.normalize_text(question) if aliases is not None else question
    except Exception:  # noqa: BLE001 别名层异常不砸澄清判定
        norm = question
    affirm = bool(_CONFIRM_AFFIRM_RE.search(question)) or "默认" in question

    # ① 渠道错别字/未注册别名（最高优先）：候选成员值已随应答回来 → 视为确认
    for keyword, member in _CONFIRM_VALUE_ALIASES.items():
        if keyword in norm:
            confirmed = affirm or (
                aliases is not None and aliases.normalize_text(member) in norm
            )
            plan = keyword_route(question)
            if confirmed:
                dims = list(plan.dimensions)
                entry = f"channel_l2={member}"
                if "channel_l2" in REGISTRY.dimensions and entry not in dims:
                    dims.append(entry)
                return {
                    "resolve": {
                        "plan": replace(plan, dimensions=tuple(dims)),
                        **_oral_window(question),
                    }
                }
            return {
                "clarify": {
                    "filter_clarify": {
                        "dimension": "channel_l2",
                        "value": keyword,
                        "suggestions": [member],
                    },
                    "plan": _confirm_plan(plan),
                }
            }

    # ② 口径歧义词：翻译出理解（按注册口径理解？）确认后再查，不直接出数
    caliber_labels = dict(_CONFIRM_MEASURE_ALIASES)
    if "激活" in norm:
        caliber_labels["激活"] = _CONFIRM_DEFAULT_CALIBER
    if "上次" in question and "口径" in question:
        caliber_labels.setdefault("上次", _CONFIRM_DEFAULT_CALIBER)
    for keyword, label in caliber_labels.items():
        if keyword in norm:
            plan = _confirm_plan(keyword_route(question))
            if affirm:  # 确认承接：应答「对/默认」→ 按候选口径出数
                return {"resolve": {"plan": plan, **_oral_window(question)}}
            return {
                "clarify": {
                    "filter_clarify": {
                        "dimension": "measure",
                        "value": keyword,
                        "suggestions": [label],
                    },
                    "plan": plan,
                }
            }

    # ③ 语流混乱复合问（各渠道分组 × 哪些渠道枚举双问并存）→ 选主问确认
    if _CONFIRM_CHANNEL_GROUP_RE.search(question) and _CONFIRM_CHANNEL_ASK_RE.search(
        question
    ):
        plan = keyword_route(question)
        if affirm:
            return {"resolve": {"plan": plan, **_oral_window(question)}}
        return {
            "clarify": {
                "filter_clarify": {
                    "dimension": "compound",
                    "value": "复合问题",
                    "suggestions": [_COMPOUND_SUGGESTION],
                },
                "plan": plan,
            }
        }

    # ④ 域外零信息输入：无任何度量/维度意图且剥成员后无中文 → 引导澄清
    base = keyword_route(question)
    if base.rejected or base.measure is not None or base.dimensions:
        return None  # 已有可执行意图（含「注册注册注册」类），走既有链路
    try:
        hints = aliases.expand_candidates(question) if aliases is not None else {}
    except Exception:  # noqa: BLE001
        hints = {}
    if hints.get("measure_hints") or hints.get("dimension_hints"):
        return None
    if not _zero_content(question):
        return None
    return {
        "clarify": {
            "filter_clarify": {
                "dimension": "input",
                "value": _ZERO_INFO_VALUE,
                "suggestions": [],
            },
            "plan": base,
        }
    }


# ------------------------------------------- enhanced keyword fallback (M5.5)


def keyword_route(question: str) -> RoutePlan:
    """M5.5 增强版关键词路由（LLM 降级时的兜底，引擎同名调用）：
    ① 别名层归一后走现有关键词表；② 度量关键词未命中时采纳 measure_hints
    （已注册度量才采信）；③ dimension_hints 补维度；④ value_hints 补渠道维度。
    别名层未就位或异常 → 原样走旧表（无别名层也能跑通基本链路）。"""
    text = question
    hints: dict = {}
    if aliases is not None:
        try:
            text = aliases.normalize_text(question) or question
            hints = aliases.expand_candidates(question) or {}
            # T-N5 高置信符号变体（加↔+）：仅并值候选（优享加线上 → 优享+线上），
            # 直接映射应答；错别字/未注册别名不走此处（确认式澄清见上方短路）。
            variant = question.translate(_VALUE_VARIANT_TRANS)
            if variant != question:
                v_hints = aliases.expand_candidates(variant) or {}
                merged = list(hints.get("value_hints") or [])
                for value in v_hints.get("value_hints") or []:
                    if value not in merged:
                        merged.append(value)
                hints["value_hints"] = merged
        except Exception:  # noqa: BLE001 别名层任何异常不得砸断兜底链路
            text, hints = question, {}
    plan = rules.keyword_route(text)
    if plan.rejected:
        return plan
    if plan.measure is None:
        # 关键词表缺口语 → 别名度量候选兜底；仅采信已注册度量（比率度量
        # 不进 RoutePlan，引擎不认）。
        measure = next(
            (m for m in hints.get("measure_hints") or [] if m in REGISTRY.measures),
            None,
        )
        if measure is None:
            return plan  # 度量仍无命中：维度/值候选单独无意义，维持原判（宁拒不错）
        plan = replace(plan, measure=measure)
    dims = list(plan.dimensions)
    for dim_id in hints.get("dimension_hints") or []:
        if dim_id in REGISTRY.dimensions:
            dims.append(dim_id)
    # value_hints（Gap A）：单一候选 → 生成过滤条目；多候选歧义 → 只给全量细分
    # （宁拒不错：不替用户猜渠道）；dict 形态为前向兼容契约（自带维度）。
    candidates: list[str] = []
    for hint in hints.get("value_hints") or []:
        if isinstance(hint, dict):
            dim_id = str(hint.get("dimension") or hint.get("dim") or "").strip()
            value = str(hint.get("value") or "").strip()
            if (
                dim_id in REGISTRY.dimensions
                and value
                and f"{dim_id}={value}" not in dims
            ):
                dims.append(f"{dim_id}={value}")
        elif isinstance(hint, str) and hint:
            candidates.append(hint)
    if len(candidates) == 1 and "channel_l2" in REGISTRY.dimensions:
        entry = f"channel_l2={candidates[0]}"
        if entry not in dims:
            dims.append(entry)
    elif (
        len(candidates) > 1
        and "channel_l2" in REGISTRY.dimensions
        and "channel_l2" not in dims
    ):
        dims.append("channel_l2")
    if dims != list(plan.dimensions):
        return replace(plan, dimensions=tuple(dict.fromkeys(dims)))
    return plan


# ------------------------------------------------- guided refusal copy (M6.1)


def _example_question() -> str:
    """示例问法从注册表现值生成（人话标签），不引用可能漂移的原语 id。"""
    ids = _example_ids()
    m_label = _short_label(REGISTRY.measures[ids["measure"]].description)
    channel_ids = [d for d in REGISTRY.dimensions if d.startswith("channel_l")]
    d_label = (
        _short_label(REGISTRY.dimensions[channel_ids[0]].description)
        if channel_ids
        else "渠道"
    )
    base = "渠道" if "渠道" in d_label else d_label
    return f"上个月各{base}{m_label}"


def guided_reject_answer(keyword: str | None = None) -> str:
    """M6.1 引导式拒答：模板 + 注册表现生成（度量/维度人话清单 + 示例问法）。
    演示红线：宁拒不错，文案不含任何数字；reject_card 结构不变，仅文案升级。"""
    try:
        measures = "、".join(
            _short_label(m.description) for m in REGISTRY.measures.values()
        )
        ratios = "、".join(
            _ratio_label(r.description) for r in REGISTRY.ratios.values()
        )
        dims = "、".join(
            _short_label(d.description) for d in REGISTRY.dimensions.values()
        )
        example = _example_question()
        ready = f"{measures}、{ratios} × {dims}" if ratios else f"{measures} × {dims}"
    except Exception:  # noqa: BLE001 目录不可读 → 硬编码降级（与注册表现值同步维护）
        ready = "注册用户数 × 各渠道、性别、时间粒度"
        example = "上个月各渠道注册用户数"
    prefix = f"「{keyword}」" if keyword else ""
    return _GUIDED_REJECT_TEMPLATE.format(prefix=prefix, ready=ready, example=example)


def channel_clarify_answer(value: str, suggestions: list) -> str:
    """Gap A 澄清式拒答：渠道值不在维表成员名单（宁拒不错 + 引导改问）。
    T-N5 确认式澄清复用本出口：单候选 → 「您是指『候选』吗？」（Jack 裁决：
    别名命中带候选名确认，不出数）；零候选且值为零信息哨兵 → 输入引导。
    文案不含任何数字（演示红线与旧不变量一致）。"""
    if not suggestions:
        if str(value or "").strip() == _ZERO_INFO_VALUE:
            example = _example_question()
            return (
                "没有识别到您想查询的内容。请直接说明要查的指标和时间，"
                f"例如：「{example}」。"
            )
        return f"未找到该渠道「{value}」。也可以先问「各渠道分布」看看有哪些渠道。"
    if len(suggestions) == 1:  # 确认式澄清：带候选名（生产确认载荷恒单候选）
        return f"您是指「{suggestions[0]}」吗？确认后我来查询。"
    shown = "、".join(suggestions[:8])
    tail = "等" if len(suggestions) > 8 else ""
    known = f"我能答的渠道有：{shown}{tail}。"
    return f"未找到该渠道「{value}」。{known}也可以先问「各渠道分布」看看有哪些渠道。"
