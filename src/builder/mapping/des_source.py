"""P3 DES 数据源装载（设计 §1.1 阶段 0）→ SourceDescriptor（四适配器输入）。

对 1 企业 DES 配置 + 生成库（erp/mes/wms/scm/fin *.db）装载 SourceDescriptor：
- columns：真实表 schema（PRAGMA table_info 列名 + SQLite 类型映射），is_technical=False
  （DES 列无 _at/_ts/etl_ 等技术列启发匹配，见 naming.is_technical_column）；
- detected_links：config 表规格 fk 关系驱动的 fk_detection（跨表 FK，去重值集比对，
  秒级，不整表扫描；fk 关系单一事实来源 = des_industry_template.yaml 表规格 fk）；
- des_mappings：DES 语义声明（demo 口径 = 从 GT 文件派生，见 semantics_from_gt；
  设计 §1.2「DES 管道按 §3.7-1 声明对象级/属性级已知映射」，score=1.0 高置信自动过）；
- alias_result：None（DES 无备用键匹配场景）。

输出喂给 run_mapping_pipeline / annotate_mapping_candidates（阶段 1 四适配器）。
与外部导入通道（auto_map）同构：阶段 2-4 完全共用，仅阶段 0/1 的装载与候选来源不同。
表/列名来自 config 与 PRAGMA（可信常量），拼接 SQL 前做标识符校验防注入（纵深防御）。
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.builder.mapping.fk_detection import DetectedLink, detect_links

# DISTINCT 值集上限（FK 去重值集远小于此；安全兜底防异常表拖慢）
_FAST_CAP = 50000
# SQLite 类型 → 适配器 inferred_type（供 naming 类型映射；DES 候选以语义声明为准）
_TYPE_MAP = {
    "TEXT": "string",
    "VARCHAR": "string",
    "CHAR": "string",
    "REAL": "float",
    "FLOAT": "float",
    "NUMERIC": "float",
    "DOUBLE": "float",
    "INTEGER": "integer",
    "INT": "integer",
    "BIGINT": "integer",
}
# 标识符白名单（表/列名拼接 SQL 前校验，防注入纵深防御）
_IDENT_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _check_ident(name: str) -> str:
    """表/列名必须是标识符（防 SQL 注入；config/PRAGMA 输入也强制校验）。"""
    if not _IDENT_RE.match(name):
        raise ValueError(f"非法表/列标识符: {name!r}")
    return name


def table_schema(db_path: Path, table: str) -> list[dict]:
    """真实表 schema：PRAGMA table_info → [{column, type, is_technical}]（单一事实来源 = 生成库）。"""
    _check_ident(table)
    conn = sqlite3.connect(str(db_path))
    try:
        raw = conn.execute(f"PRAGMA table_info({table})").fetchall()
    finally:
        conn.close()
    out: list[dict] = []
    for r in raw:
        col = r[1]
        _check_ident(col)
        out.append(
            {
                "column": col,
                "inferred_type": _TYPE_MAP.get(
                    str(r[2]).upper().split("(")[0], "string"
                ),
                "is_technical": False,  # DES 列无技术后缀；如将来有 ETL 列在此标 True 隐藏
            }
        )
    return out


def _distinct_values(db_path: Path, table: str, col: str) -> list[dict[str, Any]]:
    """某列 DISTINCT 值集（去重后很小；供 fk_detection 匹配与基数，不整表扫描）。"""
    _check_ident(table)
    _check_ident(col)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            f"SELECT DISTINCT {col} FROM {table} LIMIT ?", (_FAST_CAP,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _db_path(config: dict, out_dir: Path, code: str) -> Path:
    return out_dir / config["enterprise"]["systems"][code]["db"]


def detect_fk_links(config: dict, out_dir: Path, table_id: str) -> list[DetectedLink]:
    """config 表规格 fk 关系驱动的跨表链接检测（设计 §1.2：跨表 FK 用 config fk 关系驱动）。

    对每 (fk_col → target_table) 关系跑 fk_detection.detect_links：source 用 fk 列去重值集、
    target 用主键去重值集，秒级完成（不整表扫描）。fk 关系 = 模板层表规格 fk（单一事实来源）。
    """
    code, name = table_id.split(".", 1)
    spec = config["enterprise"]["systems"][code]["tables"][name]
    fk = spec.get("fk") or {}
    src_db = _db_path(config, out_dir, code)
    src_cols = [c["column"] for c in table_schema(src_db, name)]
    out: list[DetectedLink] = []
    for fk_col, target_tid in fk.items():
        t_code, t_name = target_tid.split(".", 1)
        t_spec = config["enterprise"]["systems"][t_code]["tables"][t_name]
        t_db = _db_path(config, out_dir, t_code)
        t_cols = [c["column"] for c in table_schema(t_db, t_name)]
        t_pk = t_spec["pk"][0]
        out.extend(
            detect_links(
                source_table=table_id,
                target_table=target_tid,
                source_columns=src_cols,
                target_columns=t_cols,
                source_rows=_distinct_values(src_db, name, fk_col),
                target_rows=_distinct_values(t_db, t_name, t_pk),
                target_pk=t_pk,
            )
        )
    return out


def semantics_from_gt(entries: list[dict]) -> dict[str, dict]:
    """GT 条目 → 每表语义声明（demo 口径：GT = DES 声明语义，单一事实来源）。

    返回 {source_table: {"object": str?, "attributes": [(col, field), ...],
                          "links": [(col, link), ...]}}。
    object 条目的 source_field 取表主键列（对象锚定身份列，见 GT 文件标注）。
    """
    out: dict[str, dict] = {}
    for e in entries:
        tid = e["source_table"]
        sem = out.setdefault(tid, {"attributes": [], "links": []})
        if e["kind"] == "object":
            sem["object"] = e["gt_target"]
            sem["object_field"] = e["source_field"]
        elif e["kind"] == "attribute":
            sem["attributes"].append((e["source_field"], e["gt_target"]))
        elif e["kind"] == "link":
            sem["links"].append((e["source_field"], e["gt_target"]))
        else:  # pragma: no cover - load_ground_truth 已 fail-fast
            raise ValueError(f"非法 GT kind: {e['kind']}")
    return out


def build_des_source(
    config: dict, out_dir: Path, table_id: str, semantic: dict
) -> dict:
    """单表 SourceDescriptor（设计 §1.1 阶段 0 输出）：真实 schema 列 + fk 链接 + 语义声明。

    semantic = semantics_from_gt 输出的单表声明（含 object/attributes/links）。
    返回 source dict（喂 run_mapping_pipeline）。
    """
    code, name = table_id.split(".", 1)
    spec = config["enterprise"]["systems"][code]["tables"][name]
    pk = spec["pk"][0]
    src_db = _db_path(config, out_dir, code)
    columns = table_schema(src_db, name)
    des_mappings: list[dict] = []
    if "object" in semantic:
        des_mappings.append(
            {"kind": "object", "target": semantic["object"], "source_field": pk}
        )
    for col, target in semantic.get("attributes", []):
        des_mappings.append(
            {"kind": "attribute", "target": target, "source_field": col}
        )
    for col, target in semantic.get("links", []):
        des_mappings.append({"kind": "link", "target": target, "source_field": col})
    return {
        "source_table": table_id,
        "columns": columns,
        "detected_links": detect_fk_links(config, out_dir, table_id),
        "alias_result": None,
        "des_mappings": des_mappings,
    }


def build_des_sources(
    config: dict, out_dir: Path, semantics: dict[str, dict]
) -> list[dict]:
    """18 表 SourceDescriptor 列表（按表名拓扑序稳定排序，输出确定）。"""
    return [
        build_des_source(config, out_dir, tid, semantics[tid])
        for tid in sorted(semantics)
    ]


__all__ = [
    "build_des_source",
    "build_des_sources",
    "detect_fk_links",
    "semantics_from_gt",
    "table_schema",
]
