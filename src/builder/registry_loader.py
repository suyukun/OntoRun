"""A1 单向流入 Registry（重写蓝图 v0.3 §10 决策 1 / 补丁 v0.3.1 A1）。

启动时：
- 读本体库 published 状态的 object_types / link_types 行；
- property_schema 用 pydantic.create_model 动态生成 Pydantic 类（不是 stub）；
- 与内置 OBJECT_TYPES / LINK_TYPES 名称 set 比对：冲突 -> 不注册 + issue；
- 返回 issue 列表（dict: code/severity/message），由 main.py 聚合到启动日志/错误。

约定：不动 src/ontology/registry.py（任务边界限定 src/builder/、src/api/、tests/）。
本模块在 register 之前主动校验 self_check 等价的硬约束，违规则跳过 + 记 error issue，
确保启动不因 builder 脏数据炸（self_check 留给现有路径处理，但 loader 已先挡一道）。
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from src.builder.link_types import list_published as list_published_lt
from src.builder.object_types import list_published as list_published_ot
from src.ontology.objects import ObjectTypeDef
from src.ontology.registry import Registry


@dataclass(frozen=True)
class LoadIssue:
    """loader 输出的问题条目（与 registry.Issue 同构但独立类型，避免跨模块耦合）。"""

    code: str
    severity: str  # "error" | "warning" | "info"
    message: str


# ----------------------------------------------------------------------
# property_schema -> Pydantic 动态类
# ----------------------------------------------------------------------


_JSON_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _enum_literal(values: list) -> Any:
    """把 enum 列表包装为 typing.Literal[...]（Pydantic v2 兼容）。"""
    if not values:
        return str
    types = sorted({type(v).__name__ for v in values})
    if types == ["str"]:
        return Literal[tuple(values)]  # type: ignore[valid-type]
    if types == ["int"]:
        return Literal[tuple(values)]  # type: ignore[valid-type]
    return str


def _build_dynamic_model(schema: dict, name: str) -> type[BaseModel]:
    """property_schema (JSON Schema 子集) -> Pydantic 类。"""
    properties: dict = schema.get("properties") or {}
    required: set[str] = set(schema.get("required") or [])
    fields: dict[str, tuple[Any, Any]] = {}
    for fname, fdef in properties.items():
        fdef = fdef or {}
        ftype = fdef.get("type", "string")
        if fdef.get("enum"):
            py_type: Any = _enum_literal(fdef["enum"])
        else:
            py_type = _JSON_TYPE_MAP.get(ftype, str)
        if fname in required:
            fields[fname] = (py_type, Field(...))
        else:
            fields[fname] = (py_type, Field(default=None))
    # create_model 需要类名合法（不以数字开头、不能重复）。hash 避免冲突。
    suffix = abs(hash(name)) & 0xFFFF
    unique_name = f"DynModel_{name[:20]}_{suffix:x}"
    return create_model(unique_name, **fields)  # type: ignore[call-overload]


# ----------------------------------------------------------------------
# link 双向命名（与 ontology/links.py 内置约定一致）
# ----------------------------------------------------------------------


def _derive_inverse_name(
    link_name: str, target_api_name: str
) -> str:
    """按内置约定：inverse_name 必须以 <target_api_name>. 开头。

    简化策略：link_name 形如 '<source>.<verb>'，inverse = '<target>.source_<verb>'。
    若 link_name 已是 '<target>.<x>' 形式，取其反向。MVP 不细化复数，发布期再升级。
    """
    if "." in link_name:
        _left, _, verb = link_name.partition(".")
        if verb:
            return f"{target_api_name}.{verb}_rev"
    return f"{target_api_name}.rev_{abs(hash(link_name)) & 0xFFFF:x}"


# ----------------------------------------------------------------------
# 主入口
# ----------------------------------------------------------------------


def load_published_into_registry(
    ontology_db_path: str | Path,
    registry: Registry,
) -> dict[str, Any]:
    """把本体库 published 行注册进内存 registry。

    P1 范围：仅注册 object_types。link_types 仅做冲突扫描 + 端点解析（不入 Registry
    实际内存表——动态 link 在 self_check 阶段会要求 fk_field 在 model 字段里，
    动态 property_schema 不强制 fk 字段，强行注册会触发 LINK_FK_MISSING。
    留 P2/P3 与映射 apply 阶段一起做；本阶段 link_types 表为审计与查询所用）。

    返回：{"issues": list[dict], "loaded_ot": int, "lt_scanned": int, "skipped": int}
    """
    conn = sqlite3.connect(ontology_db_path)
    conn.row_factory = sqlite3.Row
    issues: list[LoadIssue] = []
    loaded_ot = 0
    lt_scanned = 0
    skipped = 0

    # 先建立 name -> api_name 索引（用于 inverse_name 推导）
    api_name_by_ot: dict[str, str] = {o.name: o.api_name for o in registry.object_types()}
    ot_names: set[str] = set(api_name_by_ot)

    try:
        for row in list_published_ot(conn):
            if row.name in ot_names:
                issues.append(
                    LoadIssue(
                        code="BUILDER_NAME_CONFLICT",
                        severity="error",
                        message=f"object_type {row.name!r} 与内置类型同名，拒绝注册（补丁 A1）",
                    )
                )
                skipped += 1
                continue
            model_cls = _build_dynamic_model(row.property_schema, row.name)
            defn = ObjectTypeDef(
                name=row.name,
                api_name=row.api_name,
                description=row.description or row.name_cn or row.name,
                model=model_cls,
                pk_field=row.pk_field,
                title_field=row.title_field,
                source_table=row.source_table,
            )
            try:
                registry.register_object_type(defn)
            except ValueError as exc:
                issues.append(
                    LoadIssue(
                        code="BUILDER_NAME_CONFLICT",
                        severity="error",
                        message=f"object_type {row.name!r} 注册失败: {exc}",
                    )
                )
                skipped += 1
                continue
            api_name_by_ot[row.name] = row.api_name
            ot_names.add(row.name)
            loaded_ot += 1
            issues.append(
                LoadIssue(
                    code="BUILDER_LOADED",
                    severity="info",
                    message=f"object_type {row.name!r} 已动态注册",
                )
            )

        # link_types 扫描：仅记 issue，不入 Registry（理由见 docstring）
        for row in list_published_lt(conn):
            lt_scanned += 1
            if (
                row.source_type_id not in ot_names
                or row.target_type_id not in ot_names
            ):
                issues.append(
                    LoadIssue(
                        code="BUILDER_LINK_ENDPOINT_UNRESOLVED",
                        severity="warning",
                        message=(
                            f"link_type {row.name!r} 两端类型未注册 "
                            f"({row.source_type_id} -> {row.target_type_id})，"
                            f"P1 不入 Registry；P2 修复端点后再启用"
                        ),
                    )
                )
    finally:
        conn.close()

    return {
        "issues": [
            {"code": i.code, "severity": i.severity, "message": i.message}
            for i in issues
        ],
        "loaded_ot": loaded_ot,
        "lt_scanned": lt_scanned,
        "skipped": skipped,
    }
