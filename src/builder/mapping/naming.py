"""E2 字段命名与 is_technical 标记（蓝图 v0.3 §7 / 补丁 v0.3.1）。

字段推断：列名 snake_case -> PascalCase 属性名（本体 property_schema.properties 的 key）。
is_technical 标记：纯 ID/时间戳列隐藏，不进入 property_schema properties。

TDD 对照 data/builder_samples/expected/schema_inferred.json：
- supplier_id -> SupplierId
- etl_loaded_at / source_system -> is_technical=true（不进入 properties）
- contact_phone -> ContactPhone（非空率 < 1.0 仍保留；非空率过滤非 P3 范围）

设计：P3 只做"列名 -> 属性名 + is_technical 标记 + 类型映射"，不做
非空率阈值过滤（会丢可观测的脏数据列）。该决策写在本模块顶部，发布期可重审。
"""

from __future__ import annotations

# is_technical 后缀/前缀启发（与 schema_infer._TECHNICAL_SUFFIXES 对齐，
# 此处独立维护以保证 mapping 模块不依赖 pipeline）
_TECHNICAL_SUFFIXES: tuple[str, ...] = (
    "_at", "_ts", "_loaded_at", "etl_", "source_", "load_",
)
_TECHNICAL_EXACT: frozenset[str] = frozenset({
    "source_system",
    "etl_loaded_at",
    "load_batch_id",
    "row_hash",
})

# 列类型 -> 属性 JSON Schema type
_TYPE_MAP: dict[str, str] = {
    "string": "string",
    "integer": "integer",
    "float": "number",
    "datetime": "string",  # JSON Schema 无 datetime；存 ISO 8601 字符串
    "enum": "string",
}


def to_pascal_case(snake: str) -> str:
    """snake_case -> PascalCase。supplier_id -> SupplierId。

    处理：单下划线 / 连续下划线 / 纯小写 / 含数字。数字段保留。
    失败兜底：非空即可。
    """
    if not snake:
        return ""
    parts = [p for p in snake.split("_") if p]
    if not parts:
        return ""
    out_parts: list[str] = []
    for p in parts:
        if not p:
            continue
        if p[0].isdigit():
            out_parts.append(p)
        else:
            out_parts.append(p[0].upper() + p[1:])
    return "".join(out_parts)


def is_technical_column(column: str) -> bool:
    """is_technical 启发：列名以后缀/前缀匹配 + 精确集合。"""
    if column in _TECHNICAL_EXACT:
        return True
    n = column.lower()
    return any(n.startswith(p) or n.endswith(p) for p in _TECHNICAL_SUFFIXES)


def is_id_only_column(column: str) -> bool:
    """纯 ID 列：列名以 _id 结尾。

    注：纯 ID 列业务上重要（FK 主键），is_technical=False；property_schema
    生成时仍会保留它（PK 在 required），只是 mapping 派生 link 时把它当作
    link anchor，不暴露给 LLM 作为 attribute 描述。
    """
    return column.lower().endswith("_id") or column.lower() == "id"


def map_type(inferred_type: str) -> str:
    """schema_infer.inferred_type -> property_schema JSON Schema type。"""
    return _TYPE_MAP.get(inferred_type, "string")


def derive_property_schema(
    columns: list[dict],
    *,
    pk_column: str | None = None,
) -> dict:
    """从 columns 列表派生 property_schema 草稿。

    columns 形如：
      [{"column": "supplier_id", "inferred_type": "string", "is_technical": False,
        "role": "primary_key", "non_null_ratio": 1.0}, ...]

    返回 JSON Schema 草稿：
      {
        "type": "object",
        "properties": {PascalName: {type, description, [enum]}},
        "required": [PascalName, ...],
        "hidden_columns": [原始列名, ...]   # is_technical=True 的原列名
      }
    """
    properties: dict = {}
    required: list[str] = []
    hidden: list[str] = []
    pk = pk_column
    for c in columns:
        col = c.get("column", "")
        if not col:
            continue
        if c.get("is_technical"):
            hidden.append(col)
            continue
        pascal = to_pascal_case(col)
        if not pascal:
            continue
        prop: dict = {
            "type": map_type(c.get("inferred_type", "string")),
            "description": (c.get("role", "attribute") + "（自动从 " + col + " 派生）"),
        }
        if c.get("distinct_values"):
            prop["enum"] = list(c["distinct_values"])
        properties[pascal] = prop
        if col == pk:
            required.insert(0, pascal)
        elif c.get("non_null_ratio", 0.0) >= 1.0 and c.get("role") != "attribute":
            required.append(pascal)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "hidden_columns": hidden,
    }


__all__ = [
    "derive_property_schema",
    "is_id_only_column",
    "is_technical_column",
    "map_type",
    "to_pascal_case",
]
