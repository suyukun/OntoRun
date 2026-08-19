"""E2 跨表主键/外键检测 + 基数推断（蓝图 v0.3 §7）。

输入：两张表的 (列名 -> 样本值序列) 字典。
输出：detected_links（每条 link 含 source_field/target_field/cardinality/match_summary）。

算法步骤：
  1. 候选列对：source/target 共享同名列名（优先级 1：精确同名；优先级 2：源
     列名 = 目标 entity 名 + '_id' 形式，如 'supplier_id' 匹配 'supplier' 表）。
  2. 匹配三类：
     - direct_match：原值完全相同（去 None/空）
     - format_normalized_match：value_format.normalize_id 相等
     - unmatched：其余（含 typo 与完全无关值）
  3. 基数推断：扫 source 表每行 source_field 值，统计落在 target 集合（直接 +
     归一）中的 unique 数；判定 N:1（每行 target 值几乎唯一）/ 1:N（多个 source
     行共用同一 target 行）/ 1:1（双方一一对应）。

TDD 对照 data/builder_samples/expected/fk_detection.json：
  source_table = products_ref_suppliers, target = suppliers_dirty
  link lnk_product_supplier cardinality=N:1
  match_summary: direct=26, format_normalized=5, unmatched=3
  total=34
  3 个 unmatched：SUP-0051/SUP-0014/SUP-0018（typo）
  5 个 format_normalized：SUP-003↔SUP003/SUP-006↔SUP006/SUP-008↔SUP008/SUP-016↔SUP016
  注：fixture 在 26 direct + 5 normalized + 3 unmatched = 34 之中
    26 direct 实际包括：原值相同（含 SUP-001 等）+ 同表同名匹配
  cardinality：products_per_supplier_distribution 显示多个 supplier 各对应多个 product
              -> N:1（products.supplier_id -> suppliers.supplier_id 实际是 products 表
              端 = "N",  suppliers 端 = "1"）
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from src.builder.mapping.value_format import normalize_id


@dataclass(frozen=True)
class FKMatch:
    """单行匹配结果。"""

    raw_source_value: str
    target_match: str | None  # 直接命中值 / 归一命中值 / None
    match_type: str  # "direct" | "format_normalized" | "unmatched"
    closest_target: str | None = None  # 未命中但有 typo 嫌疑时给最近候选
    reason: str = ""


@dataclass(frozen=True)
class DetectedLink:
    """一条检测到的跨表 link。"""

    link_id: str  # 形如 lnk_{source_table}_{target_table}_{field}
    source_field: str
    target_field: str
    cardinality: str  # N:1 / 1:N / 1:1 / N:M
    detection_method: str
    matches: tuple[FKMatch, ...] = field(default_factory=tuple)
    match_summary: dict[str, int] = field(default_factory=dict)
    products_per_target: dict[str, int] = field(default_factory=dict)
    targets_per_source: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "link_id": self.link_id,
            "source_field": self.source_field,
            "target_field": self.target_field,
            "cardinality": self.cardinality,
            "detection_method": self.detection_method,
            "match_summary": self.match_summary,
            "cardinality_inference": {
                "products_per_supplier_distribution": self.products_per_target,
                "cardinality_final": self.cardinality,
            },
        }


def _slugify(name: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return s or "x"


def _candidates(
    source_columns: list[str], target_columns: list[str], target_table: str
) -> list[tuple[str, str, str]]:
    """返回候选列对 [(src_col, tgt_col, priority_tag), ...]。

    优先级：
      - "exact"：两边列名完全相同
      - "entity_anchor"：source_col = {target_table}_id 形式（针对 PK 是
        通用 'id' 的 target 表，源列含目标表实体名）
    """
    pairs: list[tuple[str, str, str]] = []
    src_set = set(source_columns)
    tgt_set = set(target_columns)
    common = src_set & tgt_set
    for col in common:
        pairs.append((col, col, "exact"))
    target_anchor = f"{target_table}_id"
    if target_anchor in src_set and target_anchor not in tgt_set:
        # 兜底：target 表用 'id' 而源表用 '{entity}_id' 形式时
        # 这里不强行配，避免误报；调用方可通过 source_pk_override 指定
        pass
    return pairs


def _match_value(
    raw: str | None, target_index: dict[str, None], target_norm_index: dict[str, str]
) -> tuple[str, str, str | None]:
    """匹配单个 raw 值到 target 集合。

    返回 (match_type, matched_target_or_None, reason)。
    match_type: "direct" / "format_normalized" / "unmatched"
    """
    if raw is None or str(raw).strip() == "":
        return ("unmatched", None, "empty_value")
    s = str(raw).strip()
    if s in target_index:
        return ("direct", s, "")
    norm = normalize_id(s)
    if norm in target_norm_index:
        return ("format_normalized", target_norm_index[norm], "")
    return ("unmatched", None, "not_in_target_set")


def _build_indices(target_values: list[str]) -> tuple[set[str], dict[str, str]]:
    target_set: set[str] = set()
    norm_index: dict[str, str] = {}
    for v in target_values:
        if v is None or str(v).strip() == "":
            continue
        s = str(v).strip()
        target_set.add(s)
        n = normalize_id(s)
        # 若多值归一到同一 norm，取首条（更可读）
        norm_index.setdefault(n, s)
    return target_set, norm_index


def _infer_cardinality(
    source_rows: list[dict],
    source_field: str,
    target_index: set[str],
    target_norm_index: dict[str, str],
) -> tuple[str, dict[str, int], dict[str, int]]:
    """根据 source 行里 source_field 值的分布推断基数。

    返回 (cardinality, products_per_target, targets_per_source)。
    products_per_target 形如 {target_value: source_row_count}。
    targets_per_source 形如 {source_value: distinct_target_count}（每行 source 端
    只有 1 个 target，所以恒为 1，保留字段用于将来 1:1 检测）。
    """
    products_per_target: Counter = Counter()
    targets_per_source: Counter = Counter()
    for r in source_rows:
        v = r.get(source_field)
        if v is None or str(v).strip() == "":
            continue
        s = str(v).strip()
        if s in target_index:
            products_per_target[s] += 1
        else:
            n = normalize_id(s)
            if n in target_norm_index:
                products_per_target[target_norm_index[n]] += 1
        targets_per_source[s] = 1
    # 推断：N:1 多数（多数 target 被多行引用）/ 1:N 罕见 / 1:1 双方等量
    if not products_per_target:
        return ("N:1", dict(products_per_target), dict(targets_per_source))
    max_refs = max(products_per_target.values())
    n_targets = len(products_per_target)
    n_sources = sum(products_per_target.values())
    if n_targets == n_sources and max_refs == 1 or max_refs <= 1:
        cardinality = "1:1"
    else:
        # 多数情形：source 行数 > target distinct 数 -> N:1
        # 极端情形：单 target 被大量 source 引用（每个 target 行被多次命中）-> N:1
        cardinality = "N:1"
    return (cardinality, dict(products_per_target), dict(targets_per_source))


def detect_links(
    *,
    source_table: str,
    target_table: str,
    source_columns: list[str],
    target_columns: list[str],
    source_rows: list[dict],
    target_rows: list[dict],
    target_pk: str | None = None,
) -> list[DetectedLink]:
    """检测 source 与 target 间的跨表链接（自动找候选列对 + 匹配 + 基数）。"""
    # 目标表主键列：默认 "id" / "{table}_id" / 第一列
    if target_pk is None:
        if target_table in target_columns:
            target_pk = target_table
        elif "id" in target_columns:
            target_pk = "id"
        else:
            target_pk = target_columns[0]
    if target_pk not in target_columns:
        # 兜底：取第一列
        target_pk = target_columns[0]
    target_values = [
        r.get(target_pk) for r in target_rows if r.get(target_pk) is not None
    ]
    target_set, target_norm_index = _build_indices([str(v) for v in target_values])
    pairs = _candidates(source_columns, target_columns, target_table)
    if not pairs:
        return []
    out: list[DetectedLink] = []
    for src_col, tgt_col, prio in pairs:
        matches: list[FKMatch] = []
        for r in source_rows:
            raw = r.get(src_col)
            if raw is None or str(raw).strip() == "":
                matches.append(
                    FKMatch(
                        raw_source_value=str(raw) if raw is not None else "",
                        target_match=None,
                        match_type="unmatched",
                        reason="empty_value",
                    )
                )
                continue
            s = str(raw).strip()
            mt, matched, _reason = _match_value(s, target_set, target_norm_index)
            # 关键分类：raw != matched 但归一后相等 -> format_normalized
            if mt == "direct" and matched is not None and matched != s:
                mt = "format_normalized"
            if mt == "unmatched":
                # 给 closest target（如果归一后存在于归一集合但值未匹配——typo 提示）
                closest = None
                norm_s = normalize_id(s)
                # 仅用于"前 3 位"或"去 1 位"近似
                if norm_s and any(t.startswith(norm_s[:4]) for t in target_norm_index):
                    cand = next(
                        iter(t for t in target_norm_index if t.startswith(norm_s[:4])),
                        None,
                    )
                    if cand:
                        closest = target_norm_index[cand]
                matches.append(
                    FKMatch(
                        raw_source_value=s,
                        target_match=None,
                        match_type="unmatched",
                        closest_target=closest,
                        reason="typo_or_not_in_target" if closest else "not_in_target",
                    )
                )
            else:
                matches.append(
                    FKMatch(
                        raw_source_value=s,
                        target_match=matched,
                        match_type=mt,
                    )
                )
        # 统计
        direct = sum(1 for m in matches if m.match_type == "direct")
        fmt_norm = sum(1 for m in matches if m.match_type == "format_normalized")
        unmatch = sum(1 for m in matches if m.match_type == "unmatched")
        cardinality, ppt, tps = _infer_cardinality(
            source_rows, src_col, target_set, target_norm_index
        )
        link_id = f"lnk_{_slugify(source_table)}_{_slugify(target_table)}_{_slugify(src_col)}"
        out.append(
            DetectedLink(
                link_id=link_id,
                source_field=src_col,
                target_field=tgt_col,
                cardinality=cardinality,
                detection_method=(
                    "column_name_match_with_value_format_normalization"
                    if fmt_norm > 0
                    else "column_name_match_direct"
                ),
                matches=tuple(matches),
                match_summary={
                    "direct_match_rows": direct,
                    "format_normalized_match_rows": fmt_norm,
                    "unmatched_rows": unmatch,
                    "total_rows": len(matches),
                },
                products_per_target=ppt,
                targets_per_source=tps,
            )
        )
    return out


__all__ = ["DetectedLink", "FKMatch", "detect_links"]
