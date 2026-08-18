"""发布校验（蓝图 v0.3 §9-P1）。

publish 前必须通过的双重校验：
1. property_schema 是合法 JSON Schema（type=object + 含 PK 字段 + 字段定义完整）；
2. link_types 两端的 object_type 行存在且 status=published。

返回值约定：None = 通过；str = 失败原因（短中文，落到 envelope error.detail）。
"""

from __future__ import annotations

import json
from typing import Any

# JSON Schema 最小必备：type=object + properties 是 dict
_VALID_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


def validate_object_type(row: Any) -> str | None:
    """校验 object_types 行能否 publish。row 需有 name/property_schema/pk_field/category 属性。

    返回 None = 通过；返回 str = 失败原因。
    """
    if not getattr(row, "name", ""):
        return "name 不能为空"
    if not getattr(row, "pk_field", ""):
        return "pk_field 不能为空"
    schema, err = _parse_json_schema(getattr(row, "property_schema", None))
    if err:
        return f"property_schema 解析失败: {err}"
    if schema.get("type") != "object":
        return "property_schema.type 必须为 object"
    props = schema.get("properties")
    if not isinstance(props, dict) or not props:
        return "property_schema.properties 必须为非空 dict"
    pk = row.pk_field
    if pk not in props:
        return f"property_schema.properties 缺少主键字段 {pk}"
    pk_def = props[pk]
    if not isinstance(pk_def, dict):
        return f"property_schema.properties.{pk} 必须为 dict"
    if pk_def.get("type") not in _VALID_TYPES:
        return f"property_schema.properties.{pk}.type 非法: {pk_def.get('type')}"
    # 任意 required 字段必须定义在 properties 中
    required = schema.get("required", [])
    if not isinstance(required, list):
        return "property_schema.required 必须为 list"
    for f in required:
        if f not in props:
            return f"property_schema.required 字段 {f} 未在 properties 定义"
    return None


def validate_link_type(
    row: Any,
    known_object_type_names: set[str],
) -> str | None:
    """校验 link_types 行能否 publish。两端类型必须在 known_object_type_names 中。

    P1 范围：fk_field 暂不强制（任务边界：DDL 无该列，loader 不入 Registry）。
    P2 映射 apply 阶段会写入并要求 fk_field 必填。
    """
    if not getattr(row, "name", ""):
        return "name 不能为空"
    if row.source_type_id not in known_object_type_names:
        return f"source_type_id {row.source_type_id} 不在已发布 object_types 集合中"
    if row.target_type_id not in known_object_type_names:
        return f"target_type_id {row.target_type_id} 不在已发布 object_types 集合中"
    if row.source_type_id == row.target_type_id:
        return "不允许自环链接（source == target）"
    if row.cardinality not in {"1:1", "1:N", "N:1", "N:M"}:
        return f"cardinality 非法: {row.cardinality}"
    return None


def _parse_json_schema(raw: Any) -> tuple[dict, str | None]:
    """property_schema 可能是 dict 或 JSON 字符串；统一解析为 dict。"""
    if isinstance(raw, dict):
        return raw, None
    if isinstance(raw, (str, bytes)):
        try:
            obj = json.loads(raw)
        except (TypeError, ValueError) as exc:
            return {}, f"JSON 解析失败: {exc}"
        if not isinstance(obj, dict):
            return {}, "property_schema 顶层必须为 JSON object"
        return obj, None
    return {}, f"property_schema 类型非法: {type(raw).__name__}"
