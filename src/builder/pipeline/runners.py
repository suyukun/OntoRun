"""管道执行 handler 工厂（蓝图 v0.3 §9-P2）。

把 connector / schema_infer / cleanse / flatten / parse_xml / md_to_struct / 
output 包装成 DAG handler。POST /pipelines/{name}/run 时按节点 kind + config
自动派发。

config 约定：
- connector: {"kind": "csv"|"json"|"xml"|"md", "path": "..."} → 读文件
- transform: {"op": "schema_infer"|"cleanse"|"flatten"|"parse_xml"|"md_to_struct",
              "pk_column": "..."(可选), "main_collection": "..."(XML 可选)}
- output  : {"target": "curated", "dataset_id": "..."(默认同 pipeline.name)}
- storage : 同 output（P2 范围归并到 output，storage 仅做占位）
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from src.builder.connectors.file_readers import read as file_read
from src.builder.pipeline.dag import Node
from src.builder.pipeline.md_to_struct import extract_text, md_to_struct
from src.builder.pipeline.parse_helpers import (
    flatten,
    parse_xml,
    parse_xml_from_path,
)
from src.builder.pipeline.schema_infer import (
    cleanse_rows,
    infer_schema,
)

# ----------------------------------------------------------------------
# handler 工厂：返回 (node, upstream_outputs) -> output
# ----------------------------------------------------------------------


def make_connector_handler() -> Any:
    def handler(node: Node, _up: dict[str, Any]) -> Any:
        cfg = node.config
        path = cfg.get("path")
        if not path:
            raise ValueError(f"connector {node.id} 缺 config.path")
        kind = cfg.get("kind")
        if kind is None:
            # 从扩展名自动判断
            ext = Path(path).suffix.lower().lstrip(".")
            kind = ext or "unknown"
        if kind == "md":
            # MD 用 md_to_struct 入口
            return extract_text(path)
        if kind in ("json", "xml"):
            # 给 transform 准备 ConnectorResult
            return file_read(path)
        if kind == "csv":
            return file_read(path)
        # pdf/docx 等降级路径：仍走 file_read，degraded 字段透传
        return file_read(path)

    return handler


def make_transform_handler() -> Any:
    def handler(node: Node, up: dict[str, Any]) -> Any:
        cfg = node.config
        op = cfg.get("op")
        # 默认从第一个上游输出读
        upstream_vals = [v for v in up.values() if v is not None]
        if not upstream_vals:
            raise ValueError(f"transform {node.id} 缺上游输出")
        prev = upstream_vals[0]

        if op == "schema_infer":
            # prev 可能是 ConnectorResult（含 rows）或 SchemaInferenceResult
            if hasattr(prev, "dataset_id") and hasattr(prev, "inferred_schema"):
                # 已是 schema_infer 结果（重用）
                return prev
            rows = _extract_rows(prev)
            pk = cfg.get("pk_column", "id")
            # 若 rows 是 dict 列表且含 supplier_id，自动用 supplier_id 作为 pk
            if pk == "auto" and rows and isinstance(rows[0], dict):
                if "supplier_id" in rows[0]:
                    pk = "supplier_id"
                else:
                    pk = next(iter(rows[0].keys()))
            return infer_schema(
                rows,
                dataset_id=cfg.get("dataset_id", node.id),
                source_path=cfg.get("source_path", ""),
                kind=cfg.get("kind", "csv"),
                pk_column=pk,
            )

        if op == "cleanse":
            if hasattr(prev, "inferred_schema"):
                specs = prev.inferred_schema
                rows = _extract_rows_from_inferred(prev)
            else:
                raise ValueError("cleanse 需上游是 schema_infer 结果")
            return cleanse_rows(rows, specs)

        if op == "flatten":
            if isinstance(prev, dict) and "rows" not in prev:
                # 直接是 JSON 树
                return flatten(
                    prev,
                    primary_key=cfg.get("primary_key", "id"),
                    root_table=cfg.get("root_table"),
                )
            # 是 ConnectorResult：先转 dict
            if hasattr(prev, "rows") and prev.rows and isinstance(prev.rows[0], dict):
                # rows 是 list[dict]，包成 {rows: [...]} 树
                return flatten(
                    {"rows": list(prev.rows)},
                    primary_key=cfg.get("primary_key", "id"),
                    root_table=cfg.get("root_table"),
                )
            raise ValueError("flatten 上游不是 dict 树或 list[dict]")

        if op == "parse_xml":
            from xml.etree import ElementTree as ET
            if isinstance(prev, ET.Element):
                return parse_xml(
                    prev,
                    primary_key=cfg.get("primary_key", "id"),
                    main_collection=cfg.get("main_collection"),
                )
            # ConnectorResult：需要重新读 XML（ConnectorResult 没存 Element）
            if hasattr(prev, "source_path") and prev.source_path:
                return parse_xml_from_path(
                    _resolve_path(prev.source_path),
                    main_collection=cfg.get("main_collection"),
                )
            raise ValueError("parse_xml 上游无 source_path")

        if op == "md_to_struct":
            if hasattr(prev, "sections"):  # MDStructResult
                return prev
            return md_to_struct(str(prev), source_path=cfg.get("source_path", ""))

        raise ValueError(f"transform op 未知: {op}")

    return handler


def make_output_handler(conn: sqlite3.Connection) -> Any:
    """output 节点：落 curated_datasets（按 dataset_id upsert）。"""
    from src.builder.curated import repo as curated_repo

    def handler(node: Node, up: dict[str, Any]) -> Any:
        cfg = node.config
        target = cfg.get("target", "curated")
        dataset_id = cfg.get("dataset_id") or node.id
        # 从上游收集质量分（schema_infer/cleanse 输出可直接产 quality）
        upstream_vals = [v for v in up.values() if v is not None]
        prev = upstream_vals[0] if upstream_vals else None
        quality = _build_quality(prev, dataset_id)
        row_count = _row_count_of(prev)
        if target == "curated":
            row = curated_repo.upsert_from_run(
                conn,
                dataset_id=dataset_id,
                quality=quality,
                row_count=row_count,
            )
            return {
                "target": "curated",
                "curated_id": row.id,
                "dataset_id": row.dataset_id,
                "row_count": row.row_count,
            }
        raise ValueError(f"output target 未知: {target}")

    return handler


def make_storage_handler(conn: sqlite3.Connection) -> Any:
    """storage 节点：P2 简化等同 output，路径存 datasets.source_path（如有）。"""
    from src.builder.curated import repo as curated_repo

    def handler(node: Node, up: dict[str, Any]) -> Any:
        cfg = node.config
        dataset_id = cfg.get("dataset_id") or node.id
        upstream_vals = [v for v in up.values() if v is not None]
        prev = upstream_vals[0] if upstream_vals else None
        quality = _build_quality(prev, dataset_id)
        row_count = _row_count_of(prev)
        row = curated_repo.upsert_from_run(
            conn, dataset_id=dataset_id, quality=quality, row_count=row_count
        )
        return {
            "target": "curated_via_storage",
            "curated_id": row.id,
            "dataset_id": row.dataset_id,
        }

    return handler


# ----------------------------------------------------------------------
# 内部辅助
# ----------------------------------------------------------------------


def _resolve_path(source_path: str) -> Path:
    p = Path(source_path)
    if p.is_absolute():
        return p
    # 相对路径相对 data/builder_samples/（fixture 兜底）
    samples = Path(__file__).resolve().parents[2] / "data" / "builder_samples"
    cand = samples / p
    if cand.exists():
        return cand
    return p


def _extract_rows(obj: Any) -> list[dict[str, str]]:
    """从 ConnectorResult 或 SchemaInferenceResult 取 list[dict]。"""
    if hasattr(obj, "rows"):
        return [dict(r) for r in obj.rows]
    if isinstance(obj, list):
        return [dict(r) for r in obj if isinstance(r, dict)]
    raise ValueError(f"无法从 {type(obj).__name__} 提取 rows")


def _extract_rows_from_inferred(obj: Any) -> list[dict[str, str]]:
    """从 SchemaInferenceResult 拿 dedup 后的 rows（粗近似：取 duplicate_rows 的补集）。

    MVP 简化：只重读 CSV 不可行，这里用 _extract_rows 兜底。
    """
    return _extract_rows(obj) if hasattr(obj, "rows") else []


def _build_quality(prev: Any, dataset_id: str) -> dict:
    """从前一节点结果产 quality_score dict。"""
    q: dict[str, Any] = {"dataset_id": dataset_id}
    if prev is None:
        return q
    if hasattr(prev, "row_count_raw"):
        q["row_count_raw"] = prev.row_count_raw
        q["row_count_after_dedup"] = prev.row_count_after_dedup
        q["duplicate_rate"] = (
            (prev.row_count_raw - prev.row_count_after_dedup) / prev.row_count_raw
            if prev.row_count_raw
            else 0.0
        )
        # 非空率均值
        specs = getattr(prev, "inferred_schema", []) or []
        if specs:
            avg = sum(s.non_null_ratio for s in specs) / len(specs)
            q["completeness"] = round(avg, 4)
        # 脏数据样本数
        dirty_total = sum(len(s.dirty_samples) for s in specs)
        q["dirty_sample_count"] = dirty_total
        q["source"] = "schema_infer"
    elif isinstance(prev, list) and prev and isinstance(prev[0], dict):
        q["row_count"] = len(prev)
        q["source"] = "cleanse"
    elif hasattr(prev, "tables"):  # FlattenResult
        q["tables"] = [
            {"name": t.table_name, "rows": len(t.rows), "columns": list(t.columns)}
            for t in prev.tables
        ]
        q["source"] = "flatten"
    elif isinstance(prev, list) and prev and hasattr(prev[0], "table_name"):
        q["tables"] = [
            {"name": t.table_name, "rows": len(t.rows)} for t in prev
        ]
        q["source"] = "parse_xml"
    elif hasattr(prev, "sections"):  # MDStructResult
        q["section_count"] = len(prev.sections)
        q["row_count"] = len(prev.rows)
        q["source"] = "md_to_struct"
    elif isinstance(prev, dict):
        q.update({"source": "output_dict", **(prev or {})})
    return q


def _row_count_of(prev: Any) -> int:
    if prev is None:
        return 0
    if hasattr(prev, "row_count_after_dedup"):
        return int(prev.row_count_after_dedup or 0)
    if isinstance(prev, list):
        return len(prev)
    if hasattr(prev, "rows"):
        return len(prev.rows)
    if hasattr(prev, "tables"):
        return sum(len(t.rows) for t in prev.tables)
    return 0
