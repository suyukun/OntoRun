"""S3：风险本体 → builder 存储层 幂等 seed 脚本。

背景（Jack 验收口径）：/builder/object-types、/builder/link-types、/builder/actions
三个 builder 页面空表（total=0）。S3 风险本体在独立注册表
（build_risk_source_registry：33 对象 / 37 链接 / 9 动作），从未写入过演示后端
（uvicorn src.app.main:app 默认库 data/ontology/ontology.db）的构建段三张表。

方案（最小侵入、可重跑）：
- 单一事实来源 = 风险本体注册代码（src/ontology/risk_objects*/risk_links/
  risk_actions，经 build_risk_source_registry() 装配）。本脚本只做程序化映射，
  不手抄清单值。
- object_types / link_types 以 draft 态落库：符合 E4 状态机 draft->reviewed->
  published 设计。published 会经 registry_loader 流入运行时 Registry 并挂上
  源表加载路径——发布是页面上的显式动作，seed 不越权代做。
- action_types 复用 src.builder.logic.action_types.upsert_runtime_action
  （P4-T2 既有幂等 upsert），与 S1 内置动作行同形态；登记即 published 与既有约定一致。

冲突策略：
- 对象/链接用确定性 id（ot_s3_<api_name> / lt_s3_<link 名点号转下划线>）判定幂等；
- 确定性 id 已存在（前次 seed）→ 跳过；
- 同名行已存在但 id 不同（S1/S2 或人工建行）→ 跳过不覆盖；链接端点解析到旧行 id；
- 动作按 name upsert：存在则刷新元数据列并保留原 id/status。

用法：
    python3 scripts/seed_builder_from_risk_ontology.py [--ontology-db PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import BaseModel

from src.builder.logic.action_types import (
    build_submission_criteria,
    get_by_name,
    upsert_runtime_action,
)
from src.runtime.risk_db import build_risk_source_registry
from src.runtime.store import DEFAULT_ONTOLOGY_DB

# 确定性 id 前缀（区别于 API 生成的 ot_/lt_ + uuid；重跑幂等靠它判定）
OT_ID_PREFIX = "ot_s3_"
LT_ID_PREFIX = "lt_s3_"

# 风险对象全部为业务域实体 -> category=domain；
# 链接全部带 fk_field -> category=fk_inferred（由外键关系推导得名）
OBJECT_CATEGORY = "domain"
LINK_CATEGORY_FK = "fk_inferred"

# 与 builder/publish_validator._VALID_TYPES 保持同一套 JSON 类型名
_JSON_TYPE_MAP: dict[Any, tuple[str, str | None]] = {
    str: ("string", None),
    bool: ("boolean", None),
    int: ("integer", None),
    float: ("number", None),
    datetime: ("string", "date-time"),
    date: ("string", "date"),
}


def _json_type_of(annotation: Any) -> tuple[str, str | None, list | None]:
    """python 注解 -> (json_type, format, enum)；Optional[X]/Literal[...] 就地解包。"""
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        rest = [a for a in get_args(annotation) if a is not type(None)]
        if len(rest) == 1:
            return _json_type_of(rest[0])
        return "object", None, None
    if origin is Literal:
        values = list(get_args(annotation))
        base, fmt, _ = _json_type_of(type(values[0]) if values else str)
        return base, fmt, values
    hit = _JSON_TYPE_MAP.get(annotation)
    if hit is not None:
        return hit[0], hit[1], None
    if origin is list:
        return "array", None, None
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return "object", None, None
    return "string", None, None


def _model_property_schema(model: type[BaseModel]) -> dict:
    """pydantic 模型 -> builder property_schema（字段描述/归属照抄本体定义）。"""
    properties: dict[str, dict] = {}
    required: list[str] = []
    for fname, finfo in model.model_fields.items():
        jtype, fmt, enum = _json_type_of(finfo.annotation)
        prop: dict[str, Any] = {"type": jtype}
        if fmt:
            prop["format"] = fmt
        if finfo.description:
            prop["description"] = finfo.description
        if enum:
            prop["enum"] = enum
        extra = finfo.json_schema_extra
        ownership = extra.get("ownership") if isinstance(extra, dict) else None
        if ownership:
            prop["x-ownership"] = ownership
        properties[fname] = prop
        if finfo.is_required():
            required.append(fname)
    schema: dict[str, Any] = {
        "type": "object",
        "title": model.__name__,
        "properties": properties,
        "required": required,
    }
    doc = model.__doc__
    if doc:
        head = doc.strip().splitlines()[0].strip()
        if head:
            schema["description"] = head
    return schema


def _name_cn_from(text: str) -> str:
    """从中文描述截首个句读前短语作 name_cn 展示位（程序化提取，非手写）。"""
    head = text.split("。")[0].split("，")[0].strip()
    return head[:64]


def _lt_row_id(link_name: str) -> str:
    return LT_ID_PREFIX + link_name.replace(".", "_")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _load_existing(conn: sqlite3.Connection, table: str) -> tuple[set, dict]:
    ids: set[str] = set()
    names: dict[str, str] = {}
    for row in conn.execute(f"SELECT id, name FROM {table}"):
        ids.add(row["id"])
        names.setdefault(row["name"], row["id"])
    return ids, names


def _insert_object_rows(
    conn: sqlite3.Connection, object_defs: list[Any]
) -> tuple[dict[str, int], dict[str, str]]:
    """插 object_types draft 行；返回 (统计, 本体类型名 -> 行 id 映射)。"""
    stats = {"inserted": 0, "skipped": 0}
    existing_ids, existing_names = _load_existing(conn, "object_types")
    name_to_id = dict(existing_names)
    now = _utc_now()
    for defn in object_defs:
        # 行名 = 本体显式 api_name（业务准确的展示标识，如 codebt_customer；
        # CamelCase 类名保留在 property_schema.title，信息不丢）。
        # 链接端点解析仍按 LinkTypeDef.source_type/target_type 的 CamelCase 名
        # 经 name_to_id 映射到行 id。
        row_name = defn.api_name
        row_id = OT_ID_PREFIX + defn.api_name
        known_id = existing_names.get(defn.api_name)
        if known_id is None:
            known_id = existing_names.get(defn.name)  # 兼容旧式/手工 CamelCase 行
        if known_id is None and row_id in existing_ids:
            known_id = row_id  # 前次 seed 的确定性 id 命中
        if known_id is not None:
            name_to_id.setdefault(defn.name, known_id)
            stats["skipped"] += 1
            continue
        conn.execute(
            "INSERT INTO object_types (id, ontology_id, name, name_cn, description, "
            "category, property_schema, status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                row_id,
                "default",
                row_name,
                _name_cn_from(defn.description),
                defn.description,
                OBJECT_CATEGORY,
                json.dumps(_model_property_schema(defn.model), ensure_ascii=False),
                "draft",
                now,
                now,
            ),
        )
        existing_ids.add(row_id)
        existing_names[defn.name] = row_id
        name_to_id[defn.name] = row_id
        stats["inserted"] += 1
    return stats, name_to_id


def _insert_link_rows(
    conn: sqlite3.Connection,
    link_defs: list[Any],
    *,
    ot_name_to_id: dict[str, str],
) -> dict[str, int]:
    """插 link_types draft 行；端点解析不到已注册对象时回退存 CamelCase 名。

    回退依据：publish 校验（validate_link_type）按"已发布行的 id 或 name"匹配端点，
    存名合法且后续 publish 时会被兜住；正常路径（33 对象齐全）不会触发回退。
    """
    stats = {"inserted": 0, "skipped": 0, "endpoint_fallback": 0}
    existing_ids, existing_names = _load_existing(conn, "link_types")
    now = _utc_now()
    for link in link_defs:
        row_id = _lt_row_id(link.name)
        known_id = existing_names.get(link.name)
        if known_id is None and row_id in existing_ids:
            known_id = row_id
        if known_id is not None:
            stats["skipped"] += 1
            continue
        source_ref = ot_name_to_id.get(link.source_type, link.source_type)
        target_ref = ot_name_to_id.get(link.target_type, link.target_type)
        if source_ref == link.source_type:
            stats["endpoint_fallback"] += 1
        if target_ref == link.target_type:
            stats["endpoint_fallback"] += 1
        conn.execute(
            "INSERT INTO link_types (id, ontology_id, name, semantic_name, category, "
            "source_type_id, target_type_id, cardinality, fk_field, status, "
            "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                row_id,
                "default",
                link.name,
                link.inverse_name,
                LINK_CATEGORY_FK,
                source_ref,
                target_ref,
                link.cardinality,
                link.fk_field,
                "draft",
                now,
                now,
            ),
        )
        existing_ids.add(row_id)
        existing_names[link.name] = row_id
        stats["inserted"] += 1
    return stats


def _action_meta(action: Any) -> dict:
    """ActionDef -> upsert_runtime_action 三元组（元数据结构对齐 P4-T2 同步路径）。"""
    return {
        "parameters": action.params_model.model_json_schema(),
        "submission_criteria": {
            "preconditions": [
                {"error_code": pc.error_code, "summary": pc.summary}
                for pc in action.preconditions
            ],
        },
        "effects": action.state_effects.model_dump(),
    }


def _upsert_action_rows(conn: sqlite3.Connection, actions: list[Any]) -> dict[str, int]:
    """真实写入路径：走既有幂等 upsert（登记即 published，保留既有 id/status）。"""
    created = updated = 0
    for action in actions:
        meta = _action_meta(action)
        _, was_created = upsert_runtime_action(
            conn,
            ontology_id="default",
            name=action.name,
            parameters=meta["parameters"],
            submission_criteria=build_submission_criteria(conn, action),
            effects=meta["effects"],
        )
        created += int(was_created)
        updated += int(not was_created)
    return {"created": created, "updated": updated}


def _project_action_changes(
    conn: sqlite3.Connection, actions: list[Any]
) -> dict[str, int]:
    """dry-run 投影：按 name 判定每个动作将 created 还是 updated（不写库）。"""
    created = sum(1 for a in actions if get_by_name(conn, a.name) is None)
    return {"created": created, "updated": len(actions) - created}


def seed(ontology_path: str | Path, *, dry_run: bool = False) -> dict:
    """执行 seed 并返回摘要（供 CLI 打印与测试断言）。

    对象/链接在一个事务内写入（dry_run 则整体回滚）；动作走 upsert 自提交，
    故 dry_run 只投影不触碰。返回 {"db","counts","issues"} 形态的字典。
    """
    path = Path(ontology_path)
    if not path.exists():
        raise SystemExit(
            f"[seed-builder] 本体库不存在: {path} —— 先启动一次演示服务"
            f"（uvicorn src.app.main:app）或 Store.migrate() 建表后再 seed"
        )
    registry = build_risk_source_registry()
    objs = list(registry.object_types())
    links = list(registry.link_types())
    acts = list(registry.actions())

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None  # 手动事务：BEGIN/COMMIT 全程自控
    try:
        conn.execute("BEGIN")
        obj_stats, ot_name_to_id = _insert_object_rows(conn, objs)
        link_stats = _insert_link_rows(conn, links, ot_name_to_id=ot_name_to_id)
        if dry_run:
            conn.execute("ROLLBACK")
            action_stats = _project_action_changes(conn, acts)
        else:
            conn.execute("COMMIT")
            action_stats = _upsert_action_rows(conn, acts)
    finally:
        conn.close()

    return {
        "db": str(path),
        "dry_run": dry_run,
        "source": {
            "objects": len(objs),
            "links": len(links),
            "actions": len(acts),
        },
        "object_types": obj_stats,
        "link_types": link_stats,
        "action_types": action_stats,
        "status_note": "对象/链接以 draft 入库（E4 状态机）；动作登记即 published（P4-T2 约定）",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ontology-db",
        default=str(DEFAULT_ONTOLOGY_DB),
        help=f"目标本体库（默认演示库 {DEFAULT_ONTOLOGY_DB}）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只投影将要写入的行数，不落库",
    )
    args = parser.parse_args(argv)
    summary = seed(args.ontology_db, dry_run=args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
