"""C 路径 · 非结构化：MD 文本 → 结构化行（蓝图 v0.3 §6 / 补丁 C4）。

md_to_struct:
  段落策略：
    - 标题（# ## ###） -> 切分块的边界；保留为 section 字段。
    - Markdown 表格（| ... |） -> 多行；列名解析首行；每行带 source_ref = {section, line}。
    - 列表（- *） -> 多行；每项一行。
    - 普通段落 -> 单行 + 整段文本。
  每行附带 source_ref（section 标题 + 行号），便于溯源。

PDF / DOCX 降级：
  不可解析的 kind（pdf/docx）-> 返回 {"status": "unsupported_kind_no_markitdown",
  "rows": [], "reason": "..."}，不抛错。markitdown 装上后此分支可升级。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MDSection:
    heading: str
    level: int  # 1 / 2 / 3
    rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class MDStructResult:
    source_path: str
    sections: tuple[MDSection, ...]
    rows: tuple[dict[str, Any], ...]
    degraded: dict[str, str] | None = None  # 非 MD 路径时填充


def _is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 3


def _is_separator(line: str) -> bool:
    s = line.strip()
    return bool(re.fullmatch(r"\|?[\s\-:|]+\|?", s)) and "---" in s


def _split_table_row(line: str) -> list[str]:
    s = line.strip()
    s = s.removeprefix("|")
    s = s.removesuffix("|")
    return [c.strip() for c in s.split("|")]


def _is_list_item(line: str) -> bool:
    s = line.lstrip()
    return s.startswith(("- ", "* ", "+ ")) or re.match(r"^d+\.", s) is not None


def _strip_list_marker(line: str) -> str:
    s = line.lstrip()
    for prefix in ("- ", "* ", "+ "):
        if s.startswith(prefix):
            return s[len(prefix):].strip()
    m = re.match(r"^\d+\.\s*", s)
    if m:
        return s[m.end():].strip()
    return s


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def md_to_struct(
    text: str,
    *,
    source_path: str = "",
) -> MDStructResult:
    """Markdown 文本 -> 结构化行（带 source_ref）。"""
    sections: list[MDSection] = []
    all_rows: list[dict[str, Any]] = []
    current_heading = "(preamble)"
    current_level = 1
    current_section_rows: list[dict[str, Any]] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # 标题
        m = _HEADING_RE.match(line)
        if m:
            # 归档当前 section
            if current_section_rows:
                sections.append(
                    MDSection(
                        heading=current_heading,
                        level=current_level,
                        rows=tuple(current_section_rows),
                    )
                )
            current_heading = m.group(2).strip()
            current_level = len(m.group(1))
            current_section_rows = []
            i += 1
            continue
        # 表格
        if _is_table_line(line):
            header = _split_table_row(line)
            # 下一行通常是 separator
            j = i + 1
            if j < n and _is_separator(lines[j]):
                j += 1
            else:
                # 非法表，不当作表
                current_section_rows.append(
                    {
                        "type": "paragraph",
                        "text": stripped,
                        "source_ref": {"section": current_heading, "line": i + 1},
                    }
                )
                i += 1
                continue
            # 数据行直到非表格行
            while j < n and _is_table_line(lines[j]):
                cells = _split_table_row(lines[j])
                # 补齐/截齐到 header 长度
                if len(cells) < len(header):
                    cells = cells + [""] * (len(header) - len(cells))
                elif len(cells) > len(header):
                    cells = cells[: len(header)]
                row = {
                    "type": "table_row",
                    "section": current_heading,
                    **{h: c for h, c in zip(header, cells)},
                    "source_ref": {"section": current_heading, "line": j + 1},
                }
                current_section_rows.append(row)
                all_rows.append(row)
                j += 1
            i = j
            continue
        # 列表
        if _is_list_item(line):
            row = {
                "type": "list_item",
                "section": current_heading,
                "text": _strip_list_marker(line),
                "source_ref": {"section": current_heading, "line": i + 1},
            }
            current_section_rows.append(row)
            all_rows.append(row)
            i += 1
            continue
        # 普通段落
        para_lines = [stripped]
        j = i + 1
        while j < n and lines[j].strip() and not _HEADING_RE.match(lines[j]) and not _is_table_line(lines[j]) and not _is_list_item(lines[j]):
            para_lines.append(lines[j].strip())
            j += 1
        row = {
            "type": "paragraph",
            "section": current_heading,
            "text": " ".join(para_lines),
            "source_ref": {"section": current_heading, "line": i + 1},
        }
        current_section_rows.append(row)
        all_rows.append(row)
        i = j
    # 收尾
    if current_section_rows:
        sections.append(
            MDSection(
                heading=current_heading,
                level=current_level,
                rows=tuple(current_section_rows),
            )
        )
    return MDStructResult(
        source_path=source_path,
        sections=tuple(sections),
        rows=tuple(all_rows),
    )


# ----------------------------------------------------------------------
# PDF / DOCX 降级
# ----------------------------------------------------------------------


def extract_text(
    path: str | Path,
) -> MDStructResult:
    """统一入口：按扩展名分发；PDF/DOCX 无 markitdown 时降级。"""
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".md", ".markdown", ""):
        return md_to_struct(p.read_text(encoding="utf-8"), source_path=p.name)
    if ext == ".pdf":
        return MDStructResult(
            source_path=p.name,
            sections=(),
            rows=(),
            degraded={
                "status": "unsupported_kind_no_markitdown",
                "reason": "PDF 需要 markitdown；MVP 不装新依赖，发布期集成",
            },
        )
    if ext == ".docx":
        return MDStructResult(
            source_path=p.name,
            sections=(),
            rows=(),
            degraded={
                "status": "unsupported_kind_no_markitdown",
                "reason": "DOCX 需要 markitdown；MVP 不装新依赖，发布期集成",
            },
        )
    # 未知扩展：降级报 unsupported_kind
    return MDStructResult(
        source_path=p.name,
        sections=(),
        rows=(),
        degraded={
            "status": "unsupported_kind_no_markitdown",
            "reason": f"未知扩展 {ext!r}：MVP 仅支持 .md",
        },
    )
