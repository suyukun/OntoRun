"""A1 单向流入 Registry。

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
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from src.builder.link_types import list_published as list_published_lt
from src.builder.object_types import list_published as list_published_ot
from src.ontology.links import LinkTypeDef
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


def _build_dynamic_model(
    schema: dict, name: str, extra_fields: dict[str, Any] | None = None
) -> type[BaseModel]:
    """property_schema (JSON Schema 子集) + 额外字段 -> Pydantic 类。

    extra_fields 形如 {field_name: python_type}，用于注入 fk 字段（与 self_check 对齐）。
    """
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
    # 注入额外字段（fk 字段默认 Optional[str]，原 property_schema 已有则不覆盖）
    if extra_fields:
        for fname, ftype in extra_fields.items():
            if fname in fields:
                continue
            fields[fname] = (ftype, Field(default=None))
    suffix = abs(hash((name, tuple(sorted((extra_fields or {}).keys()))))) & 0xFFFF
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
    *,
    reload: bool = False,
) -> dict[str, Any]:
    """把本体库 published 行注册进内存 registry。

    P2 范围：
    - object_types 仍按 property_schema 生成 Pydantic 类（必要字段 + 必含 fk 字段）；
    - link_types 真正注册到 Registry（fk_field 必填，self_check 通过则注册成功）；
    - 失败仅记 issue（severity=warning），不阻断启动（与 _reload_runtime_registry 一致）。

    reload=True：跳过"已注册 ot/lt"的重新注册（用于 publish 后的内存同步）。
    此时不重 build model（保留首次启动建出的 class），仅注册数据库新增的 ot/lt。

    返回：{"issues": list[dict], "loaded_ot": int, "loaded_lt": int, "lt_scanned": int, "skipped": int}
    """
    conn = sqlite3.connect(ontology_db_path)
    conn.row_factory = sqlite3.Row
    issues: list[LoadIssue] = []
    loaded_ot = 0
    loaded_lt = 0
    lt_scanned = 0
    skipped = 0

    # 先建立 name -> api_name 索引（用于 inverse_name 推导）
    api_name_by_ot: dict[str, str] = {o.name: o.api_name for o in registry.object_types()}
    ot_names: set[str] = set(api_name_by_ot)

    # P2 预扫 link_types：收集 ot 必含的 fk 字段集合（cardinality 决定方向）
    # 同时建立 id <-> name 双向索引（link_types.source_type_id/target_type_id 用 id，
    # 但 ot 端按 name 注册到 Registry，比对需同时支持 id 和 name）。
    lt_rows = list(list_published_lt(conn))
    published_ot_rows = list(list_published_ot(conn))
    # id -> name
    id_to_name: dict[str, str] = {r.id: r.name for r in published_ot_rows}
    # 端点 set（id 和 name 都收）
    endpoint_keys: set[str] = set(id_to_name.keys()) | set(id_to_name.values())
    fk_by_ot: dict[str, dict[str, Any]] = defaultdict(dict)  # ot_name -> {fk_field: str}
    for lt in lt_rows:
        if not lt.fk_field:
            issues.append(
                LoadIssue(
                    code="BUILDER_LINK_FK_MISSING",
                    severity="warning",
                    message=f"link_type {lt.name!r} 缺 fk_field，跳过 link 注册",
                )
            )
            continue
        # 端点为 name 优先（id -> name 映射），下面 fk_by_ot 用 name 作 key
        src_name = id_to_name.get(lt.source_type_id, lt.source_type_id)
        tgt_name = id_to_name.get(lt.target_type_id, lt.target_type_id)
        if lt.cardinality in ("N:1", "1:1"):
            fk_by_ot[src_name][lt.fk_field] = str
        elif lt.cardinality == "1:N":
            fk_by_ot[tgt_name][lt.fk_field] = str

    # reload 模式：清空 builder 加载的 ot 与其相关 lt（首次启动 reload=False 不动）
    if reload:
        for ot_name in list(ot_names):
            if ot_name in api_name_by_ot and ot_name not in {o.name for o in registry.object_types() if False}:
                pass
        # 只清空"曾经是 builder 加载的"ot：扫数据库拿本次扫描涉及的 ot 集合，
        # 不在内置集合里的全部反注册。
        builtin_ot_names = {
            o.name
            for o in registry.object_types()
            if not o.model.__name__.startswith("DynModel_")
        }
        to_unregister = [n for n in ot_names if n not in builtin_ot_names]
        for n in to_unregister:
            registry.unregister_object_type(n)
            registry.unregister_link_types_by_endpoint(n)
        # 重置 ot_names（仅保留内置）
        ot_names = set(builtin_ot_names)
        api_name_by_ot = {
            o.name: o.api_name for o in registry.object_types()
        }

    try:
        for row in list_published_ot(conn):
            extra = fk_by_ot.get(row.name) or None
            if row.name in ot_names:
                if reload:
                    # 上面已清空 + 重置 ot_names，到这里不应再命中；兜底 skip
                    continue
                issues.append(
                    LoadIssue(
                        code="BUILDER_NAME_CONFLICT",
                        severity="error",
                        message=f"object_type {row.name!r} 与内置类型同名，拒绝注册（补丁 A1）",
                    )
                )
                skipped += 1
                continue
            model_cls = _build_dynamic_model(row.property_schema, row.name, extra)
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

        # P2：link_types 真入 Registry
        # 已存在的 link 名字（reload 模式去重）
        existing_link_names: set[str] = {l.name for l in registry.link_types()}
        registered_link_names: set[str] = set()
        for row in lt_rows:
            lt_scanned += 1
            if not row.fk_field:
                continue  # 上面已记 issue
            # source/target 端点：id 和 name 都支持（API 端允许两种引用）
            src_name = id_to_name.get(row.source_type_id, row.source_type_id)
            tgt_name = id_to_name.get(row.target_type_id, row.target_type_id)
            if (
                row.source_type_id not in endpoint_keys
                or row.target_type_id not in endpoint_keys
            ):
                issues.append(
                    LoadIssue(
                        code="BUILDER_LINK_ENDPOINT_UNRESOLVED",
                        severity="warning",
                        message=(
                            f"link_type {row.name!r} 两端类型未注册 "
                            f"({row.source_type_id} -> {row.target_type_id})"
                        ),
                    )
                )
                continue
            if row.name in registered_link_names or (
                reload and row.name in existing_link_names
            ):
                if reload and row.name in existing_link_names:
                    # 增量：已存在则跳过
                    continue
                issues.append(
                    LoadIssue(
                        code="BUILDER_LINK_NAME_DUPLICATE",
                        severity="warning",
                        message=f"link_type {row.name!r} 重复，跳过",
                    )
                )
                continue
            target_api = api_name_by_ot.get(tgt_name, tgt_name)
            inverse = _derive_inverse_name(row.name, target_api)
            cardinality = row.cardinality
            if cardinality not in ("N:1", "1:N"):
                issues.append(
                    LoadIssue(
                        code="BUILDER_LINK_CARDINALITY_UNSUPPORTED",
                        severity="warning",
                        message=(
                            f"link_type {row.name!r} 基数 {cardinality} 在 MVP 范围外 "
                            "（N:1 / 1:N），跳过注册；保留审计/查询可用"
                        ),
                    )
                )
                continue
            # link 用 name 注册（与 ontology/links.py 内置约定一致 + registry self_check 按 name 找 object_type）
            link_defn = LinkTypeDef(
                name=row.name,
                source_type=src_name,
                target_type=tgt_name,
                cardinality=cardinality,
                fk_field=row.fk_field,
                inverse_name=inverse,
                description=row.semantic_name or row.name,
            )
            try:
                registry.register_link_type(link_defn)
            except Exception as exc:  # noqa: BLE001
                issues.append(
                    LoadIssue(
                        code="BUILDER_LINK_REGISTER_FAILED",
                        severity="warning",
                        message=f"link_type {row.name!r} 注册失败: {exc}",
                    )
                )
                continue
            registered_link_names.add(row.name)
            loaded_lt += 1
            issues.append(
                LoadIssue(
                    code="BUILDER_LOADED",
                    severity="info",
                    message=f"link_type {row.name!r} 已动态注册 (fk={row.fk_field})",
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
        "loaded_lt": loaded_lt,
        "lt_scanned": lt_scanned,
        "skipped": skipped,
    }
