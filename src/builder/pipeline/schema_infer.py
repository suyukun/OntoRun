"""A 路径 · 结构化：schema 推断 + 数据清洗（蓝图 v0.3 §6 / 补丁 C4）。

输入：CSV 文件路径或已解析的 list[dict]（connector 拉取的 rows）。
输出：
  - inferred_schema: list[ColumnSpec]（列名 / 类型 / 非空率 / 角色 / 脏数据样本）
  - cleansed_rows  : 去重 + 类型清洗后的行（in-place 修改，副本返回）

类型规则（轻量版，TDD 对照 data/builder_samples/expected/schema_inferred.json）：
  - 全部为数值字符或可被 strip_unit_chars 解析为 float → float
  - 全部为 ISO 8601 datetime → datetime
  - 全部为预定义 enum（候选值 < 行数 * 0.3）→ enum
  - 其余 → string

脏数据规则（per-column，config 支持 custom）：
  - "N/A" / "n/a" / "" / "null" → None
  - 数值列的 "4.5分" / "4.5 元" → 4.5（strip_unit_chars_then_to_float）
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------
# 数据类
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class ColumnSpec:
    """单列 schema 推断结果。"""

    column: str
    inferred_type: str  # string / integer / float / datetime / enum
    non_null_ratio: float
    distinct_count: int
    is_technical: bool = False  # 默认 False（启发式：列名以 etl_/source_/load_/_at 结尾→True）
    distinct_values: list[str] = field(default_factory=list)
    dirty_samples: list[dict[str, Any]] = field(default_factory=list)
    role: str = "attribute"  # primary_key / display_name / attribute / metric / classifier / technical


@dataclass(frozen=True)
class SchemaInferenceResult:
    dataset_id: str
    source_path: str
    kind: str
    row_count_raw: int
    row_count_after_dedup: int
    duplicate_rows: list[dict[str, Any]] = field(default_factory=list)
    inferred_schema: list[ColumnSpec] = field(default_factory=list)


# ----------------------------------------------------------------------
# 启发式
# ----------------------------------------------------------------------

_TECHNICAL_SUFFIXES: tuple[str, ...] = ("_at", "_ts", "etl_", "source_", "load_", "_loaded_at")
_NA_TOKENS: frozenset[str] = frozenset({"n/a", "na", "null", "none", ""})
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
_ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
)
_UNIT_TAIL_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*\D+$")
# PK 启发式：非空率=1.0 且 distinct_count == row_count
# Display name 启发式：含 'name' / '名称' / 'title' 关键字（按业务习惯）


# ----------------------------------------------------------------------
# 推断 + 清洗
# ----------------------------------------------------------------------


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    """读 CSV 全部行为 list[dict]（保留原始字符串）。"""
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _is_technical_column(name: str) -> bool:
    n = name.lower()
    return any(n.startswith(p) or n.endswith(p) for p in _TECHNICAL_SUFFIXES)


def _infer_column_type(
    values: list[str | None], row_count: int
) -> tuple[str, list[str]]:
    """推断列类型 + distinct values（仅 enum 类型返回）。"""
    non_null: list[str] = [v for v in values if v.lower() not in _NA_TOKENS]
    if not non_null:
        return "string", []
    # int
    if all(_INT_RE.match(v) for v in non_null):
        return "integer", []
    # float（含单位后缀的也能 strip 后转 float）
    if all(_FLOAT_RE.match(v) or _UNIT_TAIL_RE.match(v) for v in non_null):
        return "float", []
    # ISO datetime
    if all(_ISO_RE.match(v) for v in non_null):
        return "datetime", []
    # enum 启发：distinct 数 < 30% 且 <= 50
    distinct = sorted(set(non_null))
    if distinct and len(distinct) <= max(8, int(row_count * 0.3)):
        return "enum", distinct
    return "string", []


def _role_of(column: str, types: dict[str, str]) -> str:
    """根据列名 + 类型给 role 启发式（PK 由 caller 根据 distinct==row_count 决定）。"""
    if _is_technical_column(column):
        return "technical"
    n = column.lower()
    t = types[column]
    if "name" in n or "名称" in column or "title" in n:
        return "display_name"
    if t in {"integer", "float"}:
        return "metric"
    if t == "enum":
        return "classifier"
    return "attribute"


def _cleanse_value(value: str | None, target_type: str) -> tuple[Any, bool]:
    """单值清洗：(cleaned, is_dirty)。is_dirty=True 表示原值需要修整后才合规。"""
    if value is None or value.lower() in _NA_TOKENS:
        return None, False
    if target_type == "float":
        if _FLOAT_RE.match(value):
            return float(value), False
        m = _UNIT_TAIL_RE.match(value)
        if m:
            return float(m.group(1)), True
        return value, False  # 留作异常，不强行转
    if target_type == "integer":
        if _INT_RE.match(value):
            return int(value), False
        return value, True
    return value, False


def _collect_dirty_samples(
    values: list[str | None], target_type: str, column: str
) -> list[dict[str, Any]]:
    """收集脏数据样本（行 1-based 含表头、原始值、规则描述）。"""
    samples: list[dict[str, Any]] = []
    for i, v in enumerate(values, start=2):  # 1-based，含表头行
        if v is None or v.lower() in _NA_TOKENS:
            if target_type in {"integer", "float", "datetime"}:
                samples.append(
                    {
                        "row": i - 1,  # 数据行号（不含表头），与 expected 保持一致
                        "raw": v if v is not None else "",
                        "expected_type": target_type,
                        "cleanse_rule": "treat_as_null",
                    }
                )
            continue
        if target_type in {"float", "integer"}:
            m = _UNIT_TAIL_RE.match(v)
            if m:
                samples.append(
                    {
                        "row": i - 1,
                        "raw": v,
                        "expected_type": target_type,
                        "cleanse_rule": "strip_unit_chars_then_to_float",
                    }
                )
                continue
            if target_type == "float" and not _FLOAT_RE.match(v):
                samples.append(
                    {
                        "row": i - 1,
                        "raw": v,
                        "expected_type": target_type,
                        "cleanse_rule": "strip_unit_chars_then_to_float",
                    }
                )
    return samples


def _dedup_rows(rows: list[dict[str, str]], key_col: str | None) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """按 key_col 去重；返回 (rows_kept, duplicate_rows)。

    duplicate_rows 形如 {"row_index": 1-based-data-row, "duplicate_of_row": ..., "key": "..."}。
    key_col=None 时不做去重。
    """
    if not key_col:
        return list(rows), []
    seen: dict[str, int] = {}
    keep: list[dict[str, str]] = []
    dups: list[dict[str, Any]] = []
    for i, row in enumerate(rows, start=1):  # data row 1-based
        k = row.get(key_col, "")
        if k in seen:
            dups.append(
                {
                    "row_index": i,
                    "duplicate_of_row": seen[k],
                    "key": k,
                }
            )
        else:
            seen[k] = i
            keep.append(row)
    return keep, dups


def infer_schema(
    rows: list[dict[str, str]],
    *,
    dataset_id: str,
    source_path: str,
    kind: str = "csv",
    pk_column: str | None = "supplier_id",
) -> SchemaInferenceResult:
    """对 rows 推断 schema（含去重 + 脏数据样本）。"""
    if not rows:
        return SchemaInferenceResult(
            dataset_id=dataset_id,
            source_path=source_path,
            kind=kind,
            row_count_raw=0,
            row_count_after_dedup=0,
        )
    columns: list[str] = list(rows[0].keys())
    row_count_raw = len(rows)
    pk_col: str | None = pk_column if pk_column in columns else None
    rows_kept, duplicates = _dedup_rows(rows, pk_col)
    row_count_after = len(rows_kept)
    types: dict[str, str] = {}
    specs: list[ColumnSpec] = []
    for col in columns:
        col_values: list[str | None] = [r.get(col) for r in rows_kept]
        non_null = [v for v in col_values if v is not None and v.lower() not in _NA_TOKENS]
        non_null_count = len(non_null)
        non_null_ratio = (non_null_count / row_count_after) if row_count_after else 0.0
        distinct = sorted(set(non_null))
        t, enums = _infer_column_type(col_values, row_count_after)
        types[col] = t
        # 角色：PK 优先（distinct == row_count 且非空率 1.0）
        role: str
        if (
            pk_col is not None
            and col == pk_col
            and non_null_count == row_count_after
            and len(distinct) == row_count_after
        ):
            role = "primary_key"
        elif _is_technical_column(col):
            role = "technical"
        elif "name" in col.lower() or "名称" in col:
            role = "display_name"
        elif t in {"integer", "float"}:
            role = "metric"
        elif t == "enum":
            role = "classifier"
        else:
            role = "attribute"
        dirty = _collect_dirty_samples(col_values, t, col)
        spec = ColumnSpec(
            column=col,
            inferred_type=t,
            non_null_ratio=non_null_ratio,
            distinct_count=len(distinct),
            is_technical=(role == "technical"),
            distinct_values=enums,
            dirty_samples=dirty,
            role=role,
        )
        specs.append(spec)
    return SchemaInferenceResult(
        dataset_id=dataset_id,
        source_path=source_path,
        kind=kind,
        row_count_raw=row_count_raw,
        row_count_after_dedup=row_count_after,
        duplicate_rows=duplicates,
        inferred_schema=specs,
    )


def cleanse_rows(
    rows: list[dict[str, str]], specs: list[ColumnSpec]
) -> list[dict[str, Any]]:
    """按 spec 对每行做类型清洗；返回新 list（不改入参）。"""
    type_by_col: dict[str, str] = {s.column: s.inferred_type for s in specs}
    out: list[dict[str, Any]] = []
    for r in rows:
        cleaned: dict[str, Any] = {}
        for col, raw in r.items():
            t = type_by_col.get(col, "string")
            v, _ = _cleanse_value(raw, t)
            cleaned[col] = v
        out.append(cleaned)
    return out


# ----------------------------------------------------------------------
# 入口：从文件路径 + 期望 dataset_id / pk_column
# ----------------------------------------------------------------------


def infer_from_csv_path(
    path: str | Path,
    *,
    dataset_id: str | None = None,
    pk_column: str | None = "supplier_id",
) -> SchemaInferenceResult:
    """便捷入口：读 CSV + 推断。dataset_id 默认用 path.stem。"""
    p = Path(path)
    rows = _read_csv(p)
    return infer_schema(
        rows,
        dataset_id=dataset_id or p.stem,
        source_path=p.name,
        kind="csv",
        pk_column=pk_column,
    )


def is_iterable_of_dict(obj: Any) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, dict))
