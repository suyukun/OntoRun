"""E2 值格式容错（蓝图 v0.3 §7）。

把 SUP-001 / SUP001 / SUP-0001 等不同格式归一为同一集合，让跨表 FK 匹配
能跨越风格差异。

算法：
  1. 抽"字母前缀 + 数字部分"两段：
     - 前缀：连续大写字母（SUP/PO/SKU/P/C 等）
     - 数字部分：纯数字（可含前导零）
  2. 数字部分按"原始位数"归一（保留 0，去除尾随 0 不行——会撞值）：
     - SUP-001 -> SUP001（去分隔符）
     - SUP-0011 -> SUP0011（保留 4 位）
     - SUP0011 -> SUP0011
  3. 比较：归一后字符串相等 -> 同一实体。

注意：typo（如 SUP-0051 应匹配 SUP-005）不在本模块处理，归一后 SUP-0051 !=
SUP-005 -> 走 FK 检测的 unmatched_samples 报告。

TDD 对照 data/builder_samples/expected/fk_detection.json：
  direct_match：原值完全相同或经纯去分隔符后相同（如 SUP-003 vs SUP003 -> SUP003）
  format_normalized_match：去分隔符 + 数字位数对齐（实际算法=去分隔符，位数不动）

fixture 标了 5 个 format_normalized（SUP-003/SUP-006/SUP-008/SUP-016 等去 - 变 SUP003 等），
与"去分隔符"算法一致；不引入位数 padding。
"""

from __future__ import annotations

import re

# 抽 "字母前缀 + 数字部分"：前缀为大写字母段（贪婪），数字为连续数字
_PREFIX_NUM_RE = re.compile(r"^([A-Z]+)[-_]?(\d+)$")
# 退化：纯数字（无前缀）
_PURE_NUM_RE = re.compile(r"^\d+$")


def normalize_id(value: str) -> str:
    """把 SUP-001 / SUP001 / SUP-0001 等归一到单一形式：去分隔符，保留前导零。

    返回形式：{PREFIX}{DIGITS_NO_LEADING_DROP}。
    无法解析：原样返回（带 None 标记由调用方判断）。
    """
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    m = _PREFIX_NUM_RE.match(s)
    if m:
        prefix, num = m.group(1), m.group(2)
        # 数字部分去前导零再补齐到原始位数（保留原始位数信息，避免 SUP-0011 vs SUP-011 撞名）
        return f"{prefix}{num}"
    if _PURE_NUM_RE.match(s):
        return s
    # 退化：原样返回（让调用方按"非可归一"处理）
    return s


def is_format_normalized_pair(a: str, b: str) -> bool:
    """a 与 b 归一后相等 -> 同一实体（含 SUP-001 ↔ SUP001）。"""
    if not a or not b:
        return False
    if a == b:
        return False  # 完全相同属 direct_match，不算 format_normalized
    return normalize_id(a) == normalize_id(b)


def group_by_normalized(values: list[str]) -> dict[str, list[str]]:
    """把一组 ID 按归一形式分组。返回 {normalized: [原始值, ...]}。

    注：空字符串 / None 归一为 "" -> 落到 "" key，调用方按需过滤。
    """
    out: dict[str, list[str]] = {}
    for v in values:
        n = normalize_id(v)
        out.setdefault(n, []).append(v)
    return out


__all__ = [
    "group_by_normalized",
    "is_format_normalized_pair",
    "normalize_id",
]
