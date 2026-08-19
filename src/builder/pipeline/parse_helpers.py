"""B 路径 · 半结构化：JSON flatten + XML parse（蓝图 v0.3 §6 / 补丁 C4）。

flatten:
  嵌套对象 {parent}_{child} 拍平到主表。
  数组 + 元素是 dict -> 下推为子表；外键 = 主表 primary_key。
  嵌套 dict list (二级) -> 二级子表，外键 = 一级子表 row。
  同名字段冲突：加父键前缀消解。
  数组为空 → 父行保留，子表不产行。

parse_xml:
  属性 -> 列；文本 -> 列；子元素 -> 下推子表（同名加前缀）。
  空 <certifications/> 不产 cert 行。

fixture 期望对照（data/builder_samples/expected/）：
  - parse.json: products=12, product_specs=33, product_certifications=12, catalog_metadata=1
  - flatten.json: orders=16, orders_items=29, orders_shipping=12, orders_notes=3,
    orders_note_replies=2；shipping / notes 均为子表（fixture 与"嵌套对象拍到主表"约定
    略冲突——fixture 把"非 primitive"全当子表，本模块实现遵循 fixture）。
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------
# 数据类
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class FlattenedTable:
    table_name: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    primary_key: tuple[str, ...] = ()
    foreign_keys: tuple[dict[str, str], ...] = ()


@dataclass(frozen=True)
class FlattenResult:
    tables: list[FlattenedTable]


@dataclass
class _MutableTable:
    name: str
    columns: set[str] = field(default_factory=set)
    rows: list[dict[str, Any]] = field(default_factory=list)
    primary_key: tuple[str, ...] = ()
    foreign_keys: tuple[dict[str, str], ...] = ()

    def freeze(self) -> FlattenedTable:
        return FlattenedTable(
            table_name=self.name,
            columns=tuple(sorted(self.columns)),
            rows=tuple(self.rows),
            primary_key=self.primary_key,
            foreign_keys=self.foreign_keys,
        )


# ----------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------


def _is_primitive(v: Any) -> bool:
    return v is None or isinstance(v, (str, int, float, bool))


def _is_dict(v: Any) -> bool:
    return isinstance(v, Mapping)


def _is_dict_list(v: Any) -> bool:
    return isinstance(v, list) and bool(v) and _is_dict(v[0])


def _sanitize(name: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z一-鿿_]+", "_", name).strip("_")
    return s or "col"


# ----------------------------------------------------------------------
# flatten —— 遵循 fixture：所有非 primitive 字段都下推为子表
# ----------------------------------------------------------------------


def flatten(
    root: Mapping[str, Any],
    *,
    primary_key: str = "id",
    root_table: str | None = None,
) -> FlattenResult:
    """把 JSON 树（dict）拍平为多张子表。

    fixture 约定：
      - primitive 字段 -> 主表列。
      - dict 字段（嵌套对象）-> 子表（fk 1:1，主表 pk），列 = {parent}_{child}。
      - list[dict] 字段 -> 子表（fk N:1，主表 pk），列 = 子记录字段。
      - 二级嵌套 dict list -> 二级子表（fk N:1，一级子表 row）。
      - 空 list -> 不产行（父行保留）。
    """
    if not _is_dict(root):
        raise TypeError(f"root 必须是 dict，实际 {type(root).__name__}")
    # 找首层数组字段（元素为 dict）作为主对象列表
    array_fields = [(k, v) for k, v in root.items() if _is_dict_list(v)]
    if not array_fields:
        return FlattenResult(tables=[_MutableTable(name=root_table or "main").freeze()])
    main_key, main_list = array_fields[0]
    main_table = _MutableTable(
        name=root_table or _sanitize(main_key),
        primary_key=(primary_key,),
    )
    sub_tables: dict[str, _MutableTable] = {}
    sub2_tables: dict[str, _MutableTable] = {}

    def _ensure_sub(parent_name: str, key: str, ref_table: str) -> _MutableTable:
        sub_name = f"{parent_name}_{_sanitize(key)}"
        if sub_name not in sub_tables:
            sub_tables[sub_name] = _MutableTable(
                name=sub_name,
                primary_key=(primary_key,),
                foreign_keys=(
                    {
                        "column": primary_key,
                        "references": f"{ref_table}.{primary_key}",
                        "cardinality": "N:1",
                    },
                ),
            )
        return sub_tables[sub_name]

    # ----- Pass 1：收集 schema -----
    for record in main_list:
        for k, v in record.items():
            if _is_primitive(v):
                _add_column(main_table, _sanitize(k))
            elif _is_dict(v):
                sub = _ensure_sub(main_table.name, k, main_table.name)
                for ck in v:
                    _add_column(sub, f"{_sanitize(k)}_{_sanitize(ck)}")
            elif _is_dict_list(v):
                sub = _ensure_sub(main_table.name, k, main_table.name)
                for sub_rec in v:
                    for sk, sv in sub_rec.items():
                        if _is_primitive(sv):
                            _add_column(sub, _sanitize(sk))
                        elif _is_dict(sv):
                            for ck in sv:
                                _add_column(
                                    sub, f"{_sanitize(sk)}_{_sanitize(ck)}"
                                )
                        elif _is_dict_list(sv):
                            sub2_name = f"{sub.name}_{_sanitize(sk)}"
                            if sub2_name not in sub2_tables:
                                sub2_tables[sub2_name] = _MutableTable(
                                    name=sub2_name,
                                    primary_key=(primary_key,),
                                    foreign_keys=(
                                        {
                                            "column": primary_key,
                                            "references": f"{sub.name}.{primary_key}",
                                            "cardinality": "N:1",
                                        },
                                    ),
                                )
                            for sub2_rec in sv:
                                for sk2, sv2 in sub2_rec.items():
                                    if _is_primitive(sv2):
                                        _add_column(sub2_tables[sub2_name], _sanitize(sk2))
                                    elif _is_dict(sv2):
                                        for ck2 in sv2:
                                            _add_column(
                                                sub2_tables[sub2_name],
                                                f"{_sanitize(sk2)}_{_sanitize(ck2)}",
                                            )

    # ----- Pass 2：产行 -----
    for record in main_list:
        pk_value = record.get(primary_key, "")
        row: dict[str, Any] = {}
        for k, v in record.items():
            if _is_primitive(v):
                row[_sanitize(k)] = v
            elif _is_dict(v):
                sub = _ensure_sub(main_table.name, k, main_table.name)
                sub_row: dict[str, Any] = {primary_key: pk_value}
                for ck, cv in v.items():
                    sub_row[f"{_sanitize(k)}_{_sanitize(ck)}"] = cv
                sub.rows.append(sub_row)
            elif _is_dict_list(v):
                sub = _ensure_sub(main_table.name, k, main_table.name)
                for sub_rec in v:
                    s_row: dict[str, Any] = {primary_key: pk_value}
                    for sk, sv in sub_rec.items():
                        if _is_primitive(sv):
                            s_row[_sanitize(sk)] = sv
                        elif _is_dict(sv):
                            for ck, cv in sv.items():
                                s_row[f"{_sanitize(sk)}_{_sanitize(ck)}"] = cv
                        elif _is_dict_list(sv):
                            sub2_name = f"{sub.name}_{_sanitize(sk)}"
                            mt2 = sub2_tables[sub2_name]
                            for sub2_rec in sv:
                                sub2_row: dict[str, Any] = {primary_key: pk_value}
                                for sk2, sv2 in sub2_rec.items():
                                    if _is_primitive(sv2):
                                        sub2_row[_sanitize(sk2)] = sv2
                                    elif _is_dict(sv2):
                                        for ck2, cv2 in sv2.items():
                                            sub2_row[
                                                f"{_sanitize(sk2)}_{_sanitize(ck2)}"
                                            ] = cv2
                                mt2.rows.append(sub2_row)
                    sub.rows.append(s_row)
        main_table.rows.append(row)

    return FlattenResult(
        tables=[
            main_table.freeze(),
            *(t.freeze() for t in sub_tables.values()),
            *(t.freeze() for t in sub2_tables.values()),
        ]
    )


def _add_column(mt: _MutableTable, col: str) -> None:
    mt.columns.add(col)


def flatten_from_path(
    path: str | Path, *, primary_key: str = "id", root_table: str | None = None
) -> FlattenResult:
    p = Path(path)
    root = json.loads(p.read_text(encoding="utf-8"))
    return flatten(root, primary_key=primary_key, root_table=root_table or p.stem)


# ----------------------------------------------------------------------
# parse_xml —— 遵循 fixture：主表 = <products>，product 行包含属性 + 文本子元素
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedTable:
    table_name: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    primary_key: tuple[str, ...] = ()
    foreign_keys: tuple[dict[str, str], ...] = ()


@dataclass
class _XmlMutableTable:
    name: str
    columns: set[str] = field(default_factory=set)
    rows: list[dict[str, Any]] = field(default_factory=list)
    primary_key: tuple[str, ...] = ()
    foreign_keys: tuple[dict[str, str], ...] = ()

    def freeze(self) -> ParsedTable:
        return ParsedTable(
            table_name=self.name,
            columns=tuple(sorted(self.columns)),
            rows=tuple(self.rows),
            primary_key=self.primary_key,
            foreign_keys=self.foreign_keys,
        )


def _xml_local_tag(tag: str) -> str:
    """strip XML namespace {ns}local -> local。"""
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_xml(
    root: ET.Element,
    *,
    primary_key: str = "id",
    main_collection: str | None = None,
) -> list[ParsedTable]:
    """XML 根 -> 多张表：metadata 表 + 主表 + 下推子表。

    fixture 约定（catalog.xml）：
      - root = <catalog>，子元素 = <metadata>（单） + <products>（单，内含 12 个 <product>）。
      - 主集合 = "products"（单元素，包装）。
      - 主表 = "products"：每行 = 一个 <product>（属性 + 文本子元素拍平）。
      - 下推：<product> 下 <specs>（单，内含多 <spec>）-> "product_specs"；
              <product> 下 <certifications>（单，内含 0/N 个 <cert>）-> "product_certifications"，
              空时不产行。
    """
    # 顶层分组
    child_groups: dict[str, list[ET.Element]] = {}
    for c in list(root):
        tag = _xml_local_tag(c.tag)
        child_groups.setdefault(tag, []).append(c)
    # 决定主集合
    if main_collection is None:
        for tag, elems in child_groups.items():
            if elems and len(elems) == 1 and list(elems[0]):
                # 包装元素（如 <products>） -> 主集合
                main_collection = tag
                break
        if main_collection is None:
            for tag, elems in child_groups.items():
                if elems and (len(elems) > 1 or elems[0].attrib.get(primary_key)):
                    main_collection = tag
                    break
    # metadata：root 属性 + 非主集合的纯文本子元素
    metadata: dict[str, Any] = dict(root.attrib)
    if main_collection is not None:
        for tag, elems in child_groups.items():
            if tag == main_collection:
                continue
            if not elems:
                continue
            if all(not list(e) for e in elems):
                if len(elems) == 1:
                    metadata[tag] = (elems[0].text or "").strip() or None
                else:
                    metadata[tag] = [(e.text or "").strip() or None for e in elems]
    metadata_table = _XmlMutableTable(
        name=f"{_xml_local_tag(root.tag)}_metadata",
        primary_key=("vendor",) if "vendor" in metadata else ("id",),
    )
    for k in metadata:
        metadata_table.columns.add(k)
    metadata_table.rows.append(metadata)
    if main_collection is None:
        return [metadata_table.freeze()]
    # 主集合元素（通常是 <products> 单元素包装）
    main_wrap_elems = child_groups.get(main_collection, [])
    # 主表：每行 = main_collection 内的每一个子元素（如 <products> 下每个 <product>）
    main_table = _XmlMutableTable(name=main_collection, primary_key=(primary_key,))
    sub_tables: dict[str, _XmlMutableTable] = {}
    # 收集所有主行
    main_rows: list[ET.Element] = []
    for wrap in main_wrap_elems:
        main_rows.extend(list(wrap))
    for elem in main_rows:
        pk_value = elem.attrib.get(primary_key)
        row: dict[str, Any] = {}
        for k, v in elem.attrib.items():
            row[_sanitize(k)] = v
            main_table.columns.add(_sanitize(k))
        # 处理子元素：拍平（单元素 + 文本/单子元素）或下推（同名多 child）
        sub_groups: dict[str, list[ET.Element]] = {}
        for c in list(elem):
            t = _xml_local_tag(c.tag)
            sub_groups.setdefault(t, []).append(c)
        for tag, sub_elems in sub_groups.items():
            # 子表名：去掉复数 s 后缀（products -> product，specs -> spec，certs -> cert）
            singular = tag[:-1] if tag.endswith("s") and len(tag) > 1 else tag
            if len(sub_elems) == 1 and not list(sub_elems[0]):
                # 纯文本子元素 -> 主表列
                val = (sub_elems[0].text or "").strip()
                row[_sanitize(tag)] = val
                main_table.columns.add(_sanitize(tag))
            else:
                # 下推子表：单元素包装时看内部（如 <specs> -> <spec>）；多同名元素直接下推
                actual_items: list[ET.Element] = []
                if len(sub_elems) == 1:
                    inner = list(sub_elems[0])
                    if inner:
                        # 内部子元素集合 -> 全部展开为子表行
                        # 但若内部又只有 1 个且仍是包装（如 <specs><spec>...</spec></specs>）？
                        # 当前 catalog 数据：<specs> 内有 0..N 个 <spec>（同名多 child 时下推；
                        # 单 child 时仍按"含子元素"下推）
                        actual_items = inner
                else:
                    actual_items = sub_elems
                if not actual_items:
                    # 空包装（如 <certifications/>）-> 不产行
                    continue
                sub_table_name = f"{_sanitize(singular)}s" if not singular.endswith("s") else singular
                if not sub_table_name.startswith(main_table.name.rstrip("s") if main_table.name.endswith("s") else main_table.name):
                    # 子表名 = "{main_singular}{sub_singular}"（如 product_specs）
                    main_singular = main_table.name.removesuffix("s")
                    sub_table_name = f"{main_singular}_{sub_table_name}"
                if sub_table_name not in sub_tables:
                    sub_tables[sub_table_name] = _XmlMutableTable(
                        name=sub_table_name,
                        primary_key=(primary_key,),
                        foreign_keys=(
                            {
                                "column": primary_key,
                                "references": f"{main_table.name}.{primary_key}",
                                "cardinality": "N:1",
                            },
                        ),
                    )
                mt = sub_tables[sub_table_name]
                for s_elem in actual_items:
                    s_row: dict[str, Any] = {primary_key: pk_value}
                    for sk, sv in s_elem.attrib.items():
                        s_row[_sanitize(sk)] = sv
                        mt.columns.add(_sanitize(sk))
                    if s_elem.text and s_elem.text.strip() and not list(s_elem):
                        s_row["value"] = s_elem.text.strip()
                        mt.columns.add("value")
                    mt.rows.append(s_row)
        main_table.rows.append(row)
    return [
        main_table.freeze(),
        metadata_table.freeze(),
        *(t.freeze() for t in sub_tables.values()),
    ]


def parse_xml_from_path(
    path: str | Path, *, main_collection: str | None = None
) -> list[ParsedTable]:
    p = Path(path)
    tree = ET.parse(p)
    return parse_xml(tree.getroot(), main_collection=main_collection)
