"""数据接入（蓝图 v0.3 §3 connectors / 补丁 C4）。

读取样本数据文件，按扩展名分发，返回 list[dict]（CSV/JSON）或 {tables: ...}（XML/MD）。

不直接做类型推断 / 清洗；类型推断交给 transform，connector 只负责"打开文件"。
"""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConnectorResult:
    """connector 输出：raw rows 或结构化子表。"""

    source_path: str
    kind: str  # csv / json / xml / md / pdf / docx / unknown
    rows: tuple[dict[str, Any], ...] = ()
    tables: tuple[Mapping[str, Any], ...] = ()  # 复杂格式（xml/md）用
    degraded: dict[str, str] | None = None


def read_csv(path: str | Path) -> ConnectorResult:
    p = Path(path)
    with open(p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return ConnectorResult(source_path=p.name, kind="csv", rows=tuple(rows))


def read_json(path: str | Path) -> ConnectorResult:
    p = Path(path)
    root = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(root, list):
        return ConnectorResult(
            source_path=p.name, kind="json", rows=tuple(root if all(isinstance(x, Mapping) for x in root) else [])
        )
    if isinstance(root, Mapping):
        # 找顶层数组字段
        for v in root.values():
            if isinstance(v, list) and v and isinstance(v[0], Mapping):
                return ConnectorResult(source_path=p.name, kind="json", rows=tuple(v))
        # 否则整树视为单行
        return ConnectorResult(source_path=p.name, kind="json", rows=(dict(root),))
    return ConnectorResult(
        source_path=p.name,
        kind="json",
        rows=(),
        degraded={"status": "unsupported_shape", "reason": f"json root type {type(root).__name__}"},
    )


def read_xml(path: str | Path) -> ConnectorResult:
    p = Path(path)
    tree = ET.parse(p)
    root = tree.getroot()
    # 找首个有 id 属性 / 多个同名子元素的组
    for c in list(root):
        if c.attrib.get("id") or c.attrib.get("pk"):
            return ConnectorResult(
                source_path=p.name,
                kind="xml",
                rows=(),
                tables=({"main_collection": c.tag},),
            )
    return ConnectorResult(source_path=p.name, kind="xml", rows=(), tables=(), degraded=None)


def read_md(path: str | Path) -> ConnectorResult:
    p = Path(path)
    return ConnectorResult(
        source_path=p.name,
        kind="md",
        rows=(),
        tables=(),
        degraded=None,
    )


def read(path: str | Path) -> ConnectorResult:
    """按扩展名分发。PDF/DOCX 不可读 -> degraded 状态。"""
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".csv":
        return read_csv(p)
    if ext == ".json":
        return read_json(p)
    if ext in (".xml",):
        return read_xml(p)
    if ext in (".md", ".markdown"):
        return read_md(p)
    if ext in (".pdf", ".docx"):
        return ConnectorResult(
            source_path=p.name,
            kind=ext.lstrip("."),
            rows=(),
            tables=(),
            degraded={
                "status": "unsupported_kind_no_markitdown",
                "reason": f"{ext} 需要 markitdown；MVP 不装新依赖",
            },
        )
    return ConnectorResult(
        source_path=p.name,
        kind="unknown",
        rows=(),
        tables=(),
        degraded={"status": "unsupported_kind", "reason": f"未知扩展 {ext!r}"},
    )
