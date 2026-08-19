"""E7 宽表拆分（蓝图 v0.3 §7 / 补丁 B3 最小实现 + E2 字段推断）。

一实体一表拆分：本模块把一张宽表按"列名前缀语义"拆为多张表，每张表一个
主键 + FK 链。增量更新三层（同步/处理/索引）按补丁 B3 降 TODO 注释，不实现。

宽表规则（与 data/builder_samples/wide_table_purchases.csv 对照）：
  - 头表：po_id/po_date/po_status/po_total_amount/buyer/warehouse_code 等
    无重复前缀的列。PK = po_id。
  - supplier_info（冗余列去重）：supplier_* 前缀列；按 supplier_id 去重。
    PK = supplier_id。
  - purchase_order_lines（行项目明细）：product_*/po_line_no/qty/... ，
    与 po_id 一起下推。PK = (po_id, po_line_no)。

TDD 对照 expected/wide_split.json：14 头 + 14 supplier + 25 明细 + 2 FK 链。

实现策略：列名前缀分类（按 P3 fixture 设计，未来可升级为 LLM 辅助）。
  - 列名以 po_ 开头且行内唯一（如 po_id/po_date/po_status/po_total_amount）
    -> 头表
  - 列名以 supplier_ 开头 -> supplier_info（按 supplier_id 去重）
  - 列名以 product_ 开头 / po_line_no / unit / unit_price / qty / line_amount /
    line_eta_date / line_received_qty -> purchase_order_lines

P3 简化：不写回数据库，导出为 in-memory 字典 + 写出 CSV 字符串（供测试断言）。
发布期：可对接 curated_datasets 写表（与 md_to_struct 一致）。
"""

from __future__ import annotations

import csv
from collections import OrderedDict
from dataclasses import dataclass

# 头表识别（不以 supplier_/product_ 开头 + 不在明细列表）
# 注：fixture 列名是 purchase_order_id 而非 po_id（README 描述用 po_id 是简称）
_HEAD_KEYS: frozenset[str] = frozenset({
    "purchase_order_id", "po_id", "po_date", "po_status",
    "po_total_amount", "buyer", "warehouse_code",
})
# 明细识别（行项目）
_LINE_KEYS: frozenset[str] = frozenset({
    "po_line_no", "product_id", "product_name", "product_category",
    "unit", "unit_price", "qty", "line_amount", "line_eta_date",
    "line_received_qty",
})
# supplier_info PK 列：单独识别（supplier_id 是 supplier_info 的 PK）
_SUPPLIER_PK_KEYS: frozenset[str] = frozenset({"supplier_id"})


@dataclass(frozen=True)
class SplitTable:
    name: str
    columns: tuple[str, ...]
    primary_key: tuple[str, ...] = ()
    foreign_keys: tuple[dict, ...] = ()
    rows: tuple[dict, ...] = ()


@dataclass(frozen=True)
class WideSplitResult:
    tables: tuple[SplitTable, ...]
    fk_links: tuple[dict, ...] = ()

    def as_dict(self) -> dict:
        return {
            "target_tables": [
                {
                    "table_name": t.name,
                    "row_count": len(t.rows),
                    "primary_key": list(t.primary_key),
                    "columns": list(t.columns),
                    **({"foreign_keys": list(t.foreign_keys)} if t.foreign_keys else {}),
                }
                for t in self.tables
            ],
            "fk_links_after_split": list(self.fk_links),
        }


def _classify_column(col: str) -> str:
    """把列名分到头/supplier_info/lines/ignore。

    优先级：lines > supplier_info > head。
    特殊：supplier_id 既属于 head（PO 表 FK 锚点）也属于 supplier_info（PK），
    分到 head 后由 supplier_info 强制注入 supplier_id 列。
    """
    if col in _LINE_KEYS:
        return "lines"
    if col == "supplier_id":
        return "head"
    if col.startswith("supplier_"):
        return "supplier_info"
    if col.startswith("product_"):
        return "lines"
    if col in _HEAD_KEYS:
        return "head"
    if col.startswith("po_"):
        return "lines"
    return "head"


def _read_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return [], []
        cols = list(reader.fieldnames)
        rows = list(reader)
    return cols, rows


def split_wide_table(
    rows: list[dict[str, str]],
    columns: list[str] | None = None,
    *,
    head_table: str = "purchase_orders",
    supplier_table: str = "supplier_info",
    lines_table: str = "purchase_order_lines",
    pk_field: str = "purchase_order_id",
    supplier_pk: str = "supplier_id",
    line_pk_pair: tuple[str, str] = ("purchase_order_id", "po_line_no"),
) -> WideSplitResult:
    """把宽表行拆为头/supplier_info/lines 三张表。

    rows：宽表行（list[dict]，每行同 schema）
    columns：列名（缺省取 rows[0].keys()）。
    """
    if not rows:
        return WideSplitResult(tables=(), fk_links=())
    if columns is None:
        columns = list(rows[0].keys())
    # 1) 分类列
    head_cols: list[str] = []
    supplier_cols: list[str] = []
    line_cols: list[str] = []
    for col in columns:
        cls = _classify_column(col)
        if cls == "head":
            head_cols.append(col)
        elif cls == "supplier_info":
            supplier_cols.append(col)
        elif cls == "lines":
            line_cols.append(col)
    # 保序：原列序
    head_cols_set = set(head_cols)
    supplier_cols_set = set(supplier_cols)
    line_cols_set = set(line_cols)
    head_cols = [c for c in columns if c in head_cols_set]
    supplier_cols = [c for c in columns if c in supplier_cols_set]
    # 强制 supplier_info 包含 supplier_id（PK）
    if supplier_pk not in supplier_cols_set and supplier_pk in columns:
        supplier_cols.insert(0, supplier_pk)
    line_cols = [c for c in columns if c in line_cols_set]
    # 2) 头表：每 po 取首行（按 pk_field 去重）
    head_seen: OrderedDict[str, dict[str, str]] = OrderedDict()
    for r in rows:
        pk = r.get(pk_field, "")
        if not pk:
            continue
        if pk in head_seen:
            continue
        head_seen[pk] = {c: r.get(c, "") for c in head_cols}
    # 3) supplier_info：按 supplier_pk 去重，保留首行非空字段
    supp_seen: OrderedDict[str, dict[str, str]] = OrderedDict()
    for r in rows:
        sid = r.get(supplier_pk, "")
        if not sid:
            continue
        if sid in supp_seen:
            existing = supp_seen[sid]
            for c in supplier_cols:
                if not existing.get(c) and r.get(c):
                    existing[c] = r[c]
            continue
        supp_seen[sid] = {c: r.get(c, "") for c in supplier_cols}
    # 4) lines：每行 = 一行明细
    line_rows: list[dict[str, str]] = []
    for r in rows:
        line_rows.append({c: r.get(c, "") for c in line_cols})
    # 5) 构造表
    head_table_obj = SplitTable(
        name=head_table,
        columns=tuple(head_cols),
        primary_key=(pk_field,),
        rows=tuple(head_seen.values()),
    )
    supplier_table_obj = SplitTable(
        name=supplier_table,
        columns=tuple(supplier_cols),
        primary_key=(supplier_pk,),
        rows=tuple(supp_seen.values()),
    )
    line_pk1, line_pk2 = line_pk_pair
    lines_table_obj = SplitTable(
        name=lines_table,
        columns=tuple(line_cols),
        primary_key=(line_pk1, line_pk2),
        foreign_keys=(
            {
                "column": line_pk1,
                "references": f"{head_table}.{line_pk1}",
                "cardinality": "N:1",
            },
        ),
        rows=tuple(line_rows),
    )
    fk_links = [
        {
            "from": f"{head_table}.{supplier_pk}",
            "to": f"{supplier_table}.{supplier_pk}",
            "cardinality": "N:1",
        },
        {
            "from": f"{head_table}.{pk_field}",
            "to": f"{lines_table}.{line_pk1}",
            "cardinality": "1:N",
        },
    ]
    return WideSplitResult(
        tables=(head_table_obj, supplier_table_obj, lines_table_obj),
        fk_links=tuple(fk_links),
    )


def split_wide_table_from_path(path: str) -> WideSplitResult:
    cols, rows = _read_csv(path)
    return split_wide_table(rows, columns=cols)


# TODO 补丁 B3：增量更新三层（同步/处理/索引）本窗口不实现；
#      发布期由 P5/P6 增量同步子系统负责（见 docs/重写蓝图_v0.3 §7 / 补丁 B3）。


__all__ = ["SplitTable", "WideSplitResult", "split_wide_table", "split_wide_table_from_path"]
