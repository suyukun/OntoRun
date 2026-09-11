"""Primitive catalog + routing helpers, DERIVED from the L2 registry
(src/fortune_semantic/registry — single source of truth, no local copy).

The demo RULES dictionary (REG_TOTAL/REG_BY_CHANNEL/GENDER_RATIO/OUT_OF_SCOPE
with per-rule SQL) is retired: queries are now primitive combinations
{measure, dimensions} and SQL comes from fortune_semantic.compiler.

- RoutePlan / keyword_route: fallback router mapping keywords to equivalent
  primitive combinations (e.g. 渠道 → channel_l2); differential-attack /
  re-identification guards (T-U5, TD-17) fire before everything, then reject
  domains, so unsafe or out-of-scope questions never leak into data queries.
- differential_attack_hit: feature-combination guard (NOT case lookup) —
  unique-value probing × personal-info demand etc.; each pattern is an AND of
  two feature groups so single-edge questions (normal aggregations) pass.

- build_profile: appendix-C schema; viz_map/rule_hints derived from the
  registry (D7 field names unchanged — frontend untouched).
- build_reject_answer: refusal copy (variant rotation, seed=request_id;
  the "ready" list derives from the registry, never hardcoded).
"""

import hashlib
import re
from dataclasses import dataclass

from src.fortune_semantic.registry import REGISTRY


@dataclass(frozen=True)
class RoutePlan:
    """Routing result: a primitive combination, or a structured reject signal."""

    measure: str | None = None
    dimensions: tuple[str, ...] = ()
    reject_domain: str | None = None
    hit: str | None = None  # matched keyword, feeds the refusal copy

    @property
    def rejected(self) -> bool:
        return self.reject_domain is not None

    @property
    def shape(self) -> str:
        """Display/trace label of the primitive combination."""
        if self.measure is None:
            return self.reject_domain or "无"
        if not self.dimensions:
            return self.measure
        return self.measure + "+" + "+".join(self.dimensions)


# T-U5 差分攻击/再识别防护（TD-17 并入，Jack 2026-09-11 裁决）：聚合层不得成为
# 个人定位入口。特征规则（组合判定，非 case 查表）——每组模式都是
# 「定位/粒度特征 × 索求/字段特征」的 AND 组合，单边特征不拒，收窄防误伤：
# 正常聚合问句（「哪个渠道注册最多」「日均注册多少」「给个统计，不要名单」）不命中。
DIFF_REJECT_DOMAIN = "个人数据防护（差分/再识别）"

# 模式一（差分攻击核心，TD-17）：聚合结果被钉到唯一值/极小值 × 个人级信息索求
_DIFF_UNIQUE_RE = re.compile(r"(?:正好|恰好|刚好)(?:是|为|等于)?[0-9０-９]+")
_DIFF_UNIQUE_WORDS = ("唯一", "只有一", "就一", "仅有一", "单独一")
_DIFF_INFO_WORDS = ("个人信息", "人的信息", "人信息", "注册人", "那个人", "这个人",
                    "是谁", "手机号", "电话号", "身份证", "姓名", "邮箱", "微信号",
                    "联系方式", "时间戳", "注册时间")

# 模式二（记录级出口）：记录粒度/导出形态 × PII 字段（「小区/年龄段」这类聚合
# 统计维度不入字段清单——GLM-safety_pii-003 类统计问必须放行；「明细/导出」
# 不入粒度词——多轮承接会把历史问句拼进路由文本，宽词在合法链路上误伤
# （tests/semantic/test_clarify_continuation 链路级测试锁定既有校验路径））
_DIFF_RECORD_WORDS = ("每个人", "逐人", "个人级", "行级", "名单", "清单",
                      "排名", "排行", "CSV", "Excel")
_DIFF_RECORD_RE = re.compile(r"前\s*[0-9０-９]+\s*[个位人名条]")
_DIFF_FIELD_WORDS = ("手机号", "电话", "身份证", "姓名", "邮箱", "微信号", "微信",
                     "联系方式", "时间戳", "注册时间")

# 模式三（再识别核验）：个人标识号（含打码形态）× 存在性/日期反查
_DIFF_ID_RE = re.compile(r"[0-9０-９]{3}[*＊]{2,}[0-9０-９]{4}")
_DIFF_ID_WORDS = ("手机号", "电话号", "这个号", "该号码", "该号", "身份证")
_DIFF_PROBE_WORDS = ("是不是", "是否", "有没有", "注册日期", "哪天注册",
                     "什么时候注册")


def _any_word_in(text: str, words: tuple[str, ...]) -> bool:
    return any(w in text for w in words)


def differential_attack_hit(question: str) -> str | None:
    """差分攻击/再识别特征判定（T-U5）：命中 → 返回可读命中理由（人话、不含
    数字，可安全拼进拒答文案——文案无数字红线）；未命中 → None。
    三组模式均为 AND 组合（见上方块注释），规则可解释、特征收窄防误伤。"""
    if ((_DIFF_UNIQUE_RE.search(question) or _any_word_in(question, _DIFF_UNIQUE_WORDS))
            and _any_word_in(question, _DIFF_INFO_WORDS)):
        return "聚合唯一值反推定位个人（差分攻击特征）"
    if ((_any_word_in(question, _DIFF_RECORD_WORDS) or _DIFF_RECORD_RE.search(question))
            and _any_word_in(question, _DIFF_FIELD_WORDS)):
        return "记录级个人信息名单/明细索求（再识别特征）"
    if ((_DIFF_ID_RE.search(question) or _any_word_in(question, _DIFF_ID_WORDS))
            and _any_word_in(question, _DIFF_PROBE_WORDS)):
        return "以个人标识号反查注册状态（再识别核验特征）"
    return None


# Reject-first: unregistered business domains refuse before any data primitive.
_REJECT_DOMAINS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("活跃/转化域", ("活动", "任务", "抽奖", "奖品", "导流", "日活", "活跃", "转化")),
    ("资产/持仓域", ("资产", "持仓", "理财", "收益", "余额", "AUM", "aum")),
)

# Keyword → primitive fragment (dimension entries may carry a grain argument).
_DIMENSION_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("channel_l2", ("分渠道", "按渠道", "各渠道", "渠道", "来源")),
    ("gender", ("男女", "性别", "男性", "女性")),
    ("time_grain=day", ("按日", "每天", "每日", "逐日")),
    ("time_grain=week", ("按周", "每周", "逐周")),
    ("time_grain=month", ("按月", "每月", "逐月", "月度")),
)

_MEASURE_KEYWORDS = ("注册", "用户数")  # any hit selects the registration measure
_REGISTRATION_MEASURE = "reg_user_cnt"  # 「注册」关键词的等价原语（未注册则退回首个度量）


def keyword_route(question: str) -> RoutePlan:
    """Fallback router when LLM routing is unavailable: keywords → equivalent
    primitive combination; unregistered domains → structured reject plan."""
    # T-U5 安全特征最优先（TD-17）：差分/再识别问句先于域外判定拒绝。
    diff_hit = differential_attack_hit(question)
    if diff_hit:
        return RoutePlan(reject_domain=DIFF_REJECT_DOMAIN, hit=diff_hit)
    for domain, keywords in _REJECT_DOMAINS:
        for kw in keywords:
            if kw in question:
                return RoutePlan(reject_domain=domain, hit=kw)
    dimensions: list[str] = []
    hit = None
    for entry, keywords in _DIMENSION_KEYWORDS:
        for kw in keywords:
            if kw in question:
                dimensions.append(entry)
                hit = hit or kw
                break
    if any(kw in question for kw in _MEASURE_KEYWORDS):
        measure = _REGISTRATION_MEASURE if _REGISTRATION_MEASURE in REGISTRY.measures \
            else next(iter(REGISTRY.measures), None)
        if measure:
            return RoutePlan(measure=measure, dimensions=tuple(dimensions),
                             hit=hit or next(kw for kw in _MEASURE_KEYWORDS if kw in question))
    return RoutePlan()  # no confident mapping → unregistered


def viz_for(measure: str, dimensions) -> str | None:
    """D7 viz contract from query shape: no dimension → kpi; single channel →
    bar; gender → pie; time grain → line; composites → None (table fallback)."""
    if not dimensions:
        return "kpi"
    if len(dimensions) == 1:
        first = dimensions[0].split("=")[0]
        if first.startswith("channel_l"):
            return "bar"
        if first == "gender":
            return "pie"
        if first == "time_grain":
            return "line"
    return None


def _short_label(description: str) -> str:
    return description.split("：", 1)[0]


def _ready_labels() -> str:
    """Currently answerable primitives, generated from the registry alone."""
    reg = REGISTRY
    labels = [_short_label(m.description) for m in reg.measures.values()]
    labels += [_short_label(d.description) for d in reg.dimensions.values()]
    return "、".join(labels)


# 拒答句式池：{kw}=命中词，{ready}=当前已注册原语清单；同一问句重试稳定（seed=request_id）
_REJECT_VARIANTS = (
    "「{kw}」对应的口径还没有在语义层注册，我不猜数。现在能答：{ready}，换个问法试试？",
    "「{kw}」超出了当前已注册的语义范围。宁可不答，不出假数。已就绪的口径：{ready}。",
    "「{kw}」暂无可回答的注册口径，不生成 SQL、不猜测。已就绪：{ready}；扩展需先注册对应度量与维度。",
)


def build_reject_answer(keyword: str | None, seed: str) -> str:
    """按命中词 + 句式变体生成拒答（seed 决定变体序，同请求重试稳定）。"""
    kw = keyword or "这个问题"
    idx = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(_REJECT_VARIANTS)
    return _REJECT_VARIANTS[idx].format(kw=kw, ready=_ready_labels())


# PII fields (appendix C sensitive_fields): only encrypted state may leave the layer.
SENSITIVE_FIELDS = ["usr_phone_erpt", "usr_idcardno_erpt"]


def build_profile() -> dict:
    """Appendix-C profile schema; viz_map/rule_hints derived from the registry."""
    reg = REGISTRY
    status = ", ".join(f"{rid}({rule.status})" for rid, rule in sorted(reg.rules.items()))
    rule_hints: dict = {}
    for mid, m in reg.measures.items():
        rule_hints[mid] = {"caliber": f"{m.description}；口径规则 {status}" if status else m.description}
    for did, d in reg.dimensions.items():
        rule_hints[did] = {"caliber": d.description}
    viz_map: dict = {}
    for mid in reg.measures:
        viz_map[mid] = viz_for(mid, ())
        for did in reg.dimensions:
            viz_map[f"{mid}+{did}"] = viz_for(mid, (did,))
    return {
        "name": "fortune-registration",
        "display": "财富ThoughtSpot",
        "endpoint": "/api/chat",
        "theme": "fortune",
        "panels": ["decision_pipeline", "path_badge", "conclusion_basis", "history"],
        "examples": [
            "2026年8月注册用户数是多少？",
            "8月分渠道注册情况",
            "8月注册用户男女比例",
            "7月注册用户数是多少？",
        ],
        "path_labels": {
            "semantic_pushdown": "语义下推·镜像库",
            "blocked_param": "参数待补/超边界",
            "unregistered": "未注册口径",
            "rejected": "范围外",
            "validation_failed": "校验未通过",
        },
        "rule_hints": rule_hints,
        "viz_map": viz_map,
        "sensitive_fields": list(SENSITIVE_FIELDS),
        "role_visibility": {"analyst": ["L1", "L2", "L3", "timing"], "viewer": ["L1"]},
    }
