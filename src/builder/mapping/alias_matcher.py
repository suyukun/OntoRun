"""E2 备用键匹配（蓝图 v0.3 §7）：文档中提及的自然语言公司名 → 实体。

策略：name_token_overlap + alias_dictionary + 上下文消歧。
P3 实现目标：对照 data/builder_samples/expected/alias_matching.json：
  - 22 个 alias 命中 10 个 supplier_id
  - 6 个 no_match 全部正确归入待补录
  - 2 处歧义（金辉 / 长江冷链）按"文档作者消歧声明 + 上下文同段指代"消歧
  - 命中率 22/28 = 78.6%

实现（不烧 token，可选 LLM 辅助，MockProvider 即可）：
  1. 主索引：master_supplier_names 全称集合 + 简称词典（行业/区域后缀剥离）。
  2. 候选 alias 抽取（双轨）：
     a) 短称：2-6 字中文 n-gram（华联/金辉/长江冷链等）
     b) 全称：以"公司/股份/厂/集团/有限公司/有限责任公司/股份有限公司"结尾的连续
        中文 token（深圳市华联电子科技有限公司）
     标点（（）【】、，。；：）内部分作为 alias 边界（与 fixture 表述一致：
     `（系统编号 SUP-001；简称华联电子）`）。
  3. 匹配：
     - exact_full_name：与全称完全一致 -> 1.0
     - abbreviation_stripped：去掉 区域/行业 后缀（电子/物流/纺织/包装/化工/食品
       /光电/塑胶/货运/贸易/冷链/照明/科技/股份/有限公司 等）后命中 -> 0.95
     - abbreviation_with_industry：含行业后缀的简称命中 -> 0.92
     - short_alias：>=2 字的简写与全称的"实体核心 token"（去掉上述后缀后）完全
       相同 -> 0.85~0.90
     - ambiguous_short_alias_resolved：简写存在多歧义候选，依赖同段前文已有全称
       消歧 -> 0.75~0.85
  4. 消歧：扫"同段上文最近出现的全称"作为指代；如无，则降级 no_match。
  5. no_match：候选打分全部 < 0.5 或行业后缀属地点（科技园/物流园 等）。
  6. 多候选冲突：保留同段前文消歧的；若仍冲突则置 ambiguous（不决断）。

TDD 简化原则：算法不追求语言学完备，对照 fixture 22/6/2 的命中/未命中/消歧三档
实现；同段消歧按"段落（空行分界）"边界。
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

# 行业/区域后缀（剥离后用于简称匹配）
_INDUSTRY_SUFFIXES: tuple[str, ...] = (
    "电子", "物流", "纺织", "包装", "化工", "食品", "光电", "塑胶",
    "货运", "贸易", "冷链", "照明", "科技", "股份", "国际",
)
_REGION_PREFIXES: tuple[str, ...] = (
    "深圳市", "广州市", "北京", "上海", "天津", "重庆", "成都", "武汉", "杭州",
    "苏州", "宁波", "青岛", "长沙", "合肥", "西安", "兰州", "昆明", "东莞",
    "佛山", "中山",
)
_CORP_SUFFIXES: tuple[str, ...] = (
    "有限公司", "股份有限公司", "有限责任公司", "公司", "集团", "厂", "制品厂",
)
# 地点名后缀（命中即归 no_match，不参与消歧）
_PLACE_SUFFIXES: tuple[str, ...] = (
    "科技园", "物流园", "工业园", "产业园", "开发区",
)

# 全称触发：以这些后缀结尾的连续中文 token 视为全称候选
_FULLNAME_TRIGGERS: tuple[str, ...] = (
    "有限公司", "股份有限公司", "有限责任公司", "集团", "制品厂",
    "厂", "公司",
)
# alias 边界标点
_BOUNDARY_PUNCT = "（()【】、，。；： \"“”‘’\n\t"


def _strip_corp(name: str) -> str:
    """去 公司/股份/有限公司 等公司后缀。"""
    s = name
    for suf in sorted(_CORP_SUFFIXES, key=len, reverse=True):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s


def _strip_region(name: str) -> str:
    """去 区域前缀（深圳/广州/北京 等）。"""
    for reg in sorted(_REGION_PREFIXES, key=len, reverse=True):
        if name.startswith(reg):
            return name[len(reg):]
    return name


def core_name(full_name: str) -> str:
    """从全称提取"核心 token"：去公司后缀 + 去区域前缀 + 多次去行业后缀。

    深圳市华联电子科技有限公司 -> 华联
    杭州华诺纺织有限公司 -> 华诺
    武汉长江冷链设备有限公司 -> 长江
    """
    s = _strip_corp(full_name)
    s = _strip_region(s)
    # 多次剥 INDUSTRY_SUFFIXES（如"华联电子科技" -> "华联"）
    changed = True
    while changed:
        changed = False
        for suf in sorted(_INDUSTRY_SUFFIXES, key=len, reverse=True):
            if s.endswith(suf) and len(s) > len(suf):
                s = s[: -len(suf)]
                changed = True
                break
    return s.strip()


def _is_place_name(name: str) -> bool:
    return any(name.endswith(p) for p in _PLACE_SUFFIXES)


def _is_full_name(s: str) -> bool:
    """以全称触发后缀结尾且 >= 4 字。"""
    if len(s) < 4:
        return False
    return any(s.endswith(t) for t in _FULLNAME_TRIGGERS)


def _extract_aliases(text: str) -> list[tuple[str, int]]:
    """从文档原文抽 alias 候选（双轨：短称 + 全称）。

    返回 [(alias, paragraph_index), ...]。段落以空行分界。
    短称：CJK run 内 2-4 字子串（华联/金辉/华联电子）。
    全称：以公司后缀结尾的连续中文 token（深圳市华联电子科技有限公司）。

    设计权衡：fixture 22 命中是按"全称 + 2-4 字简写"记，"长江冷链科技园"
    6 字靠 place_name 启发落 no_match（不强求完整 6 字被识别）。
    """
    paragraphs = re.split(r"\n\s*\n", text)
    out: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()
    full_re = re.compile(r"[\u4e00-\u9fff]{4,20}")
    short_re = re.compile(r"[\u4e00-\u9fff]{2,4}")
    for pi, para in enumerate(paragraphs):
        # 全称：先扫
        for m in full_re.finditer(para):
            tok = m.group(0)
            if _is_full_name(tok):
                key = (tok, pi)
                if key not in seen:
                    seen.add(key)
                    out.append(key)
        # 短称：2-4 字 finditer（贪婪 4 字）
        for m in short_re.finditer(para):
            tok = m.group(0)
            if all(ord(c) < 128 for c in tok):
                continue
            key = (tok, pi)
            if key not in seen:
                seen.add(key)
                out.append(key)
    return out


@dataclass(frozen=True)
class AliasMatch:
    """一个 alias 命中结果。"""

    alias: str
    matched_supplier_id: str | None
    match_type: str  # exact_full_name / abbreviation_stripped / short_alias / ambiguous_short_alias_resolved / abbreviation_with_industry / no_match_*
    confidence: float
    paragraph_index: int
    context: str = ""
    disambiguation_note: str = ""


@dataclass(frozen=True)
class AliasMatchResult:
    matches: tuple[AliasMatch, ...]
    no_match: tuple[AliasMatch, ...]
    matched_supplier_ids: tuple[str, ...]
    ambiguous_resolved: tuple[str, ...] = field(default_factory=tuple)
    total_alias_mentions: int = 0

    def as_dict(self) -> dict:
        return {
            "alias_to_entity_map": [
                {
                    "alias": m.alias,
                    "matched_supplier_id": m.matched_supplier_id,
                    "match_type": m.match_type,
                    "confidence": m.confidence,
                    "context": m.context,
                    **({"disambiguation_note": m.disambiguation_note} if m.disambiguation_note else {}),
                }
                for m in self.matches
            ],
            "no_match_entities": [
                {
                    "alias": m.alias,
                    "matched_supplier_id": None,
                    "reason": m.match_type,
                    "context": m.context,
                }
                for m in self.no_match
            ],
            "summary_counts": {
                "total_alias_mentions": self.total_alias_mentions,
                "matched_to_existing_supplier": len(self.matches),
                "no_match": len(self.no_match),
                "matched_supplier_ids_count": len(set(self.matched_supplier_ids)),
                "ambiguous_resolved_via_context": len(self.ambiguous_resolved),
            },
        }


def match_aliases(
    text: str,
    *,
    master_suppliers: list[dict],
) -> AliasMatchResult:
    """把文档中提及的公司名匹配到 master_suppliers 列表。

    master_suppliers 形如：[{"supplier_id": "SUP-001", "supplier_name": "深圳市华联电子科技有限公司", ...}, ...]
    """
    # 1) 构建主索引
    core_to_ids: dict[str, list[str]] = defaultdict(list)
    full_to_ids: dict[str, list[str]] = defaultdict(list)
    for s in master_suppliers:
        full = s.get("supplier_name", "")
        sid = s.get("supplier_id", "")
        if not full or not sid:
            continue
        full_to_ids[full].append(sid)
        core = core_name(full)
        if core:
            core_to_ids[core].append(sid)
    # 2) 抽 alias 候选
    aliases = _extract_aliases(text)
    # 3) 段落最近全称缓存（用于歧义消歧）
    paragraphs = re.split(r"\n\s*\n", text)
    last_full_in_para: dict[int, str] = {}
    # 4) 匹配
    matches: list[AliasMatch] = []
    no_match: list[AliasMatch] = []
    ambiguous_resolved: list[str] = []
    matched_ids: list[str] = []
    seen: set[tuple[str, int]] = set()
    for alias, pi in aliases:
        key = (alias, pi)
        if key in seen:
            continue
        seen.add(key)
        ctx = paragraphs[pi][:80] if pi < len(paragraphs) else ""
        # 地点名：no_match
        if _is_place_name(alias):
            no_match.append(
                AliasMatch(
                    alias=alias,
                    matched_supplier_id=None,
                    match_type="no_match_place_name_not_company",
                    confidence=0.0,
                    paragraph_index=pi,
                    context=ctx,
                )
            )
            continue
        # exact 全称
        if alias in full_to_ids:
            sid = full_to_ids[alias][0]
            matches.append(
                AliasMatch(
                    alias=alias,
                    matched_supplier_id=sid,
                    match_type="exact_full_name",
                    confidence=1.0,
                    paragraph_index=pi,
                    context=ctx,
                )
            )
            matched_ids.append(sid)
            last_full_in_para[pi] = alias
            continue
        # 含行业后缀的简称（abbreviation_with_industry）也是上下文指代锚点
        # 例如 "中山金辉照明" -> 命中 SUP-005 后，"金辉"可被同段消歧
        stripped_pre = None
        for suf in sorted(_INDUSTRY_SUFFIXES, key=len, reverse=True):
            if alias.endswith(suf) and len(alias) > len(suf):
                stripped_pre = alias[: -len(suf)]
                break
        if stripped_pre and stripped_pre in core_to_ids:
            ids = list(dict.fromkeys(core_to_ids[stripped_pre]))
            if len(ids) == 1:
                matches.append(
                    AliasMatch(
                        alias=alias,
                        matched_supplier_id=ids[0],
                        match_type="abbreviation_with_industry",
                        confidence=0.92,
                        paragraph_index=pi,
                        context=ctx,
                    )
                )
                matched_ids.append(ids[0])
                # 更新最近全称（与 industry 后缀别名互为消歧锚）
                for full_name, sids in full_to_ids.items():
                    if sids and sids[0] == ids[0]:
                        last_full_in_para[pi] = full_name
                        break
                continue
        # 简写 = core 名（精确）
        if alias in core_to_ids:
            ids = core_to_ids[alias]
            unique_ids = list(dict.fromkeys(ids))  # 保序去重
            if len(unique_ids) == 1:
                matches.append(
                    AliasMatch(
                        alias=alias,
                        matched_supplier_id=unique_ids[0],
                        match_type="short_alias",
                        confidence=0.85,
                        paragraph_index=pi,
                        context=ctx,
                    )
                )
                matched_ids.append(unique_ids[0])
            else:
                # 歧义：尝试用同段最近全称消歧
                recent_full = last_full_in_para.get(pi)
                resolved_id = None
                if recent_full and recent_full in full_to_ids:
                    rid = full_to_ids[recent_full][0]
                    if rid in unique_ids:
                        resolved_id = rid
                if resolved_id is None:
                    no_match.append(
                        AliasMatch(
                            alias=alias,
                            matched_supplier_id=None,
                            match_type="no_match_ambiguous_short_alias",
                            confidence=0.0,
                            paragraph_index=pi,
                            context=ctx,
                            disambiguation_note=f"歧义候选 ids={unique_ids}",
                        )
                    )
                else:
                    matches.append(
                        AliasMatch(
                            alias=alias,
                            matched_supplier_id=resolved_id,
                            match_type="ambiguous_short_alias_resolved",
                            confidence=0.75,
                            paragraph_index=pi,
                            context=ctx,
                            disambiguation_note=f"同段上文 {recent_full} 消歧",
                        )
                    )
                    matched_ids.append(resolved_id)
                    ambiguous_resolved.append(alias)
            continue
        # 含行业后缀的简称：尝试剥行业后缀
        stripped = None
        for suf in sorted(_INDUSTRY_SUFFIXES, key=len, reverse=True):
            if alias.endswith(suf) and len(alias) > len(suf):
                stripped = alias[: -len(suf)]
                break
        if stripped and stripped in core_to_ids:
            ids = list(dict.fromkeys(core_to_ids[stripped]))
            if len(ids) == 1:
                matches.append(
                    AliasMatch(
                        alias=alias,
                        matched_supplier_id=ids[0],
                        match_type="abbreviation_with_industry",
                        confidence=0.92,
                        paragraph_index=pi,
                        context=ctx,
                    )
                )
                matched_ids.append(ids[0])
                continue
        # abbreviation_stripped：去行业/区域/公司后缀后等于 core 名
        stripped2 = core_name(alias)
        if stripped2 and stripped2 in core_to_ids and stripped2 != alias:
            ids = core_to_ids[stripped2]
            if len(ids) == 1:
                matches.append(
                    AliasMatch(
                        alias=alias,
                        matched_supplier_id=ids[0],
                        match_type="abbreviation_stripped",
                        confidence=0.95,
                        paragraph_index=pi,
                        context=ctx,
                    )
                )
                matched_ids.append(ids[0])
                continue
        # 兜底：no_match
        no_match.append(
            AliasMatch(
                alias=alias,
                matched_supplier_id=None,
                match_type="no_match_company_not_in_supplier_master",
                confidence=0.0,
                paragraph_index=pi,
                context=ctx,
            )
        )
    return AliasMatchResult(
        matches=tuple(matches),
        no_match=tuple(no_match),
        matched_supplier_ids=tuple(matched_ids),
        ambiguous_resolved=tuple(ambiguous_resolved),
        total_alias_mentions=len(seen),
    )


__all__ = [
    "AliasMatch",
    "AliasMatchResult",
    "core_name",
    "match_aliases",
]
