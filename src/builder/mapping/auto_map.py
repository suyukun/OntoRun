"""E2 自动映射编排（蓝图 v0.3 §7）。

编排四技法：字段推断 + FK 检测 + 值格式容错 + 备用键匹配，输出一份
MappingRow 内容（field_mapping / fk_mappings / cardinalities），落到 mappings
表（status=draft）。

输入：
  - source_schema_inference: SchemaInferenceResult（来自 schema_infer.infer_schema）
  - source_rows / target_rows：原始 list[dict]（target 必有，备用键可选）
  - target_table / target_pk：跨表匹配目标

输出：dict 形态的 mapping payload（与 mappings 表 JSON 列同构）+ 派生 object_type
property_schema 草稿 + 派生 link_type 元数据（fk_field/cardinality）。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.builder.mapping import alias_matcher, fk_detection, naming
from src.builder.pipeline.schema_infer import SchemaInferenceResult


@dataclass(frozen=True)
class AutoMapResult:
    entity_class: str
    source_table: str
    field_mapping: list[dict]  # 每项 {column, property_name, is_technical, inferred_type, is_pk}
    property_schema: dict  # 派生的 object_type property_schema
    fk_mappings: list[dict]  # 每项 {link_id, source_field, target_field, target_table, cardinality, detection_method}
    cardinalities: dict
    alias_matches: dict | None = None  # 仅当有 target master 时填

    def as_dict(self) -> dict:
        return {
            "entity_class": self.entity_class,
            "source_table": self.source_table,
            "field_mapping": self.field_mapping,
            "property_schema": self.property_schema,
            "fk_mappings": self.fk_mappings,
            "cardinalities": self.cardinalities,
            **({"alias_matches": self.alias_matches} if self.alias_matches is not None else {}),
        }


def _entity_class_from_source(source_table: str) -> str:
    """从 source_table 派生 entity_class 名（PascalCase 形式）。"""
    base = source_table.replace(".csv", "").replace(".json", "").replace(".md", "")
    return naming.to_pascal_case(base) or "Entity"


def auto_map_from_inference(
    inference: SchemaInferenceResult,
    *,
    source_rows: list[dict[str, str]] | None = None,
    target_table: str | None = None,
    target_rows: list[dict[str, str]] | None = None,
    target_pk: str | None = None,
    target_columns: list[str] | None = None,
    alias_doc_text: str | None = None,
    master_suppliers: list[dict] | None = None,
) -> AutoMapResult:
    """从 schema 推断结果出发做自动映射。"""
    source_table = inference.source_path or "source"
    entity_class = _entity_class_from_source(source_table)
    # 1) 字段推断
    cols_payload = [
        {
            "column": s.column,
            "inferred_type": s.inferred_type,
            "is_technical": s.is_technical,
            "role": s.role,
            "non_null_ratio": s.non_null_ratio,
            "distinct_values": s.distinct_values,
        }
        for s in inference.inferred_schema
    ]
    pk = next((c.column for c in inference.inferred_schema if c.role == "primary_key"), None)
    property_schema = naming.derive_property_schema(cols_payload, pk_column=pk)
    field_mapping: list[dict] = []
    for c in cols_payload:
        field_mapping.append(
            {
                "column": c["column"],
                "property_name": naming.to_pascal_case(c["column"]),
                "inferred_type": c["inferred_type"],
                "is_technical": c["is_technical"],
                "is_pk": c["column"] == pk,
            }
        )
    # 2) FK 检测
    fk_mappings: list[dict] = []
    cardinalities: dict[str, str] = {}
    if target_table is not None and target_rows is not None and source_rows is not None:
        if target_columns is None:
            target_columns = list(target_rows[0].keys()) if target_rows else []
        source_columns = [s.column for s in inference.inferred_schema]
        detected = fk_detection.detect_links(
            source_table=source_table,
            target_table=target_table,
            source_columns=source_columns,
            target_columns=target_columns,
            source_rows=source_rows,
            target_rows=target_rows,
            target_pk=target_pk,
        )
        for d in detected:
            fk_mappings.append(
                {
                    "link_id": d.link_id,
                    "source_field": d.source_field,
                    "target_field": d.target_field,
                    "target_table": target_table,
                    "cardinality": d.cardinality,
                    "detection_method": d.detection_method,
                    "match_summary": d.match_summary,
                    "unmatched_samples": [
                        {
                            "raw": m.raw_source_value,
                            "closest": m.closest_target,
                            "reason": m.reason,
                        }
                        for m in d.matches
                        if m.match_type == "unmatched"
                    ][:5],
                }
            )
            cardinalities[d.link_id] = d.cardinality
    # 3) 备用键匹配（可选）
    alias_payload: dict | None = None
    if alias_doc_text and master_suppliers:
        am = alias_matcher.match_aliases(alias_doc_text, master_suppliers=master_suppliers)
        alias_payload = am.as_dict()
    return AutoMapResult(
        entity_class=entity_class,
        source_table=source_table,
        field_mapping=field_mapping,
        property_schema=property_schema,
        fk_mappings=fk_mappings,
        cardinalities=cardinalities,
        alias_matches=alias_payload,
    )


__all__ = ["AutoMapResult", "auto_map_from_inference"]
