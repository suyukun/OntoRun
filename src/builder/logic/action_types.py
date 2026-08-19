"""action_types 表仓储 + runtime 引擎对接（蓝图 v0.3 §4/§5 / P4-T2）。

单一事实来源 = 运行时引擎（src/ontology/actions.py 的 ActionDef 声明，
Registry 注册）：builder 侧只登记元数据，不复制执行逻辑（补丁 A1 单向流入）。

- sync_action_types_from_registry：把 Registry 中的内置动作 upsert 成
  action_types 行（parameters = params_model JSON Schema、
  submission_criteria = 前置规则 + 引用的 published 逻辑规则、
  effects = state_effects 标注）。内置动作已在引擎上线，登记即 published；
  E3 提取的动态动作（若未来落表）走 draft->reviewed->published，
  其写回执行列发布期 TODO（补丁 A2）。
- submission_criteria.logic_rules：published 逻辑规则引用（数据结构上打通，
  P4-T1 规则可被动作引用；运行时强制执行属现有引擎职责，这里只解析引用）。
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.builder.status_machine import DRAFT, PUBLISHED

# 动作效果字段引用形态 "Order.status" 的对象类型提取
_EFFECT_FIELD_RE = re.compile(r"^([A-Za-z_][\w]*)\.[A-Za-z_][\w]*$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return f"at_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class ActionTypeRow:
    """action_types 表行（frozen；更新返回新对象）。"""

    id: str
    ontology_id: str
    name: str
    parameters: dict
    submission_criteria: dict
    effects: dict
    status: str
    created_at: str
    updated_at: str


def _load_json(raw, default):
    if raw is None:
        return default
    if isinstance(raw, (str, bytes, bytearray)):
        return json.loads(raw) if raw else default
    if isinstance(raw, dict):
        return raw
    return default


def _row_factory(row: sqlite3.Row) -> ActionTypeRow:
    return ActionTypeRow(
        id=row["id"],
        ontology_id=row["ontology_id"],
        name=row["name"],
        parameters=_load_json(row["parameters_json"], {}),
        submission_criteria=_load_json(row["submission_criteria_json"], {}),
        effects=_load_json(row["effects_json"], {}),
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ----------------------------------------------------------------------
# CRUD
# ----------------------------------------------------------------------


def get(conn: sqlite3.Connection, at_id: str) -> ActionTypeRow | None:
    row = conn.execute("SELECT * FROM action_types WHERE id = ?", (at_id,)).fetchone()
    return _row_factory(row) if row else None


def get_by_name(conn: sqlite3.Connection, name: str) -> ActionTypeRow | None:
    row = conn.execute(
        "SELECT * FROM action_types WHERE name = ? ORDER BY created_at DESC LIMIT 1",
        (name,),
    ).fetchone()
    return _row_factory(row) if row else None


def resolve(conn: sqlite3.Connection, ref: str) -> ActionTypeRow | None:
    """id 优先、name 兜底。"""
    row = get(conn, ref)
    if row is not None:
        return row
    return get_by_name(conn, ref)


def list_all(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ActionTypeRow], int]:
    where: list[str] = []
    params: list = []
    if status:
        where.append("status = ?")
        params.append(status)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM action_types {where_sql}", params
    ).fetchone()["c"]
    offset = max(0, (page - 1) * page_size)
    rows = conn.execute(
        f"SELECT * FROM action_types {where_sql} ORDER BY name LIMIT ? OFFSET ?",
        (*params, page_size, offset),
    ).fetchall()
    return [_row_factory(r) for r in rows], total


def create(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    parameters: dict,
    submission_criteria: dict,
    effects: dict,
    status: str = DRAFT,
) -> ActionTypeRow:
    """建一行（E3 提取的动态动作走此入口，status=draft；执行列发布期 TODO）。"""
    new_id = _new_id()
    now = _now()
    conn.execute(
        "INSERT INTO action_types (id, ontology_id, name, parameters_json, "
        "submission_criteria_json, effects_json, status, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_id,
            ontology_id,
            name,
            json.dumps(parameters, ensure_ascii=False),
            json.dumps(submission_criteria, ensure_ascii=False),
            json.dumps(effects, ensure_ascii=False),
            status,
            now,
            now,
        ),
    )
    conn.commit()
    return get(conn, new_id)  # type: ignore[return-value]


def upsert_runtime_action(
    conn: sqlite3.Connection,
    *,
    ontology_id: str,
    name: str,
    parameters: dict,
    submission_criteria: dict,
    effects: dict,
) -> tuple[ActionTypeRow, bool]:
    """upsert 一条 runtime 内置动作元数据；返回 (row, created)。

    已存在（按 name）：更新三个元数据字段、保留既有 id 与 status（内置动作
    首次登记即为 published；后续 sync 幂等）。
    """
    existing = get_by_name(conn, name)
    if existing is None:
        row = create(
            conn,
            ontology_id=ontology_id,
            name=name,
            parameters=parameters,
            submission_criteria=submission_criteria,
            effects=effects,
            status=PUBLISHED,  # 内置动作已在引擎上线，登记即 published
        )
        return row, True
    conn.execute(
        "UPDATE action_types SET parameters_json = ?, submission_criteria_json = ?, "
        "effects_json = ?, updated_at = ? WHERE id = ?",
        (
            json.dumps(parameters, ensure_ascii=False),
            json.dumps(submission_criteria, ensure_ascii=False),
            json.dumps(effects, ensure_ascii=False),
            _now(),
            existing.id,
        ),
    )
    conn.commit()
    return get(conn, existing.id), False  # type: ignore[return-value]


def update_submission_criteria(
    conn: sqlite3.Connection, at_id: str, logic_rules: list[str]
) -> ActionTypeRow | None:
    """替换 submission_criteria.logic_rules 引用（人工/上游 linking 用）。"""
    row = get(conn, at_id)
    if row is None:
        return None
    criteria = dict(row.submission_criteria)
    criteria["logic_rules"] = list(logic_rules)
    conn.execute(
        "UPDATE action_types SET submission_criteria_json = ?, updated_at = ? "
        "WHERE id = ?",
        (json.dumps(criteria, ensure_ascii=False), _now(), at_id),
    )
    conn.commit()
    return get(conn, at_id)


def row_to_dict(row: ActionTypeRow) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "parameters": row.parameters,
        "submission_criteria": row.submission_criteria,
        "effects": row.effects,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


# ----------------------------------------------------------------------
# Registry -> action_types 同步（单一事实来源 = runtime 引擎）
# ----------------------------------------------------------------------


def _effect_object_types(action) -> list[str]:
    """从 StateEffects 的 <Type>.<field> 引用提对象类型名。"""
    fields = list(action.state_effects.source_backed or [])
    fields += list(action.state_effects.ontology_owned or [])
    fields += list(action.state_effects.derived or [])
    out: list[str] = []
    for ref in fields:
        m = _EFFECT_FIELD_RE.match(str(ref))
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def build_submission_criteria(conn: sqlite3.Connection, action) -> dict:
    """submission_criteria = 引擎前置规则声明 + 引用的 published 逻辑规则。

    logic_rules 引用按"规则 expression.object_type ∈ 动作效果对象类型"连接
    （真实数据 join，不凭空造；内置动作效果对象是内置类型，与 builder 侧
    规则（builder 对象类型）天然不相交时为空列表--结构打通即可）。
    """
    from src.builder.logic import rules_repo

    effect_types = set(_effect_object_types(action))
    refs: list[str] = []
    for rule in rules_repo.list_published(conn):
        obj_type = rule.expression.get("object_type")
        if isinstance(obj_type, str) and obj_type in effect_types:
            refs.append(rule.name)
    return {
        "preconditions": [
            {"error_code": pc.error_code, "summary": pc.summary}
            for pc in action.preconditions
        ],
        "logic_rules": refs,
    }


def sync_action_types_from_registry(conn: sqlite3.Connection, registry) -> dict:
    """把 Registry 全部动作 upsert 进 action_types（幂等，可重复调用）。

    返回 {"synced", "created", "updated", "issues"}；issues 仅在异常时出现
    （正常内置动作不应失败）。
    """
    created = 0
    updated = 0
    issues: list[dict] = []
    for action in registry.actions():
        try:
            _, was_created = upsert_runtime_action(
                conn,
                ontology_id="default",
                name=action.name,
                parameters=action.params_model.model_json_schema(),
                submission_criteria=build_submission_criteria(conn, action),
                effects=action.state_effects.model_dump(),
            )
            created += int(was_created)
            updated += int(not was_created)
        except Exception as exc:  # noqa: BLE001 -- 单动作失败不阻断其余
            issues.append(
                {"code": "ACTION_SYNC_FAILED", "message": f"{action.name}: {exc}"}
            )
    return {
        "synced": created + updated,
        "created": created,
        "updated": updated,
        "issues": issues,
    }


# ----------------------------------------------------------------------
# submission_criteria 解析（引用完整性）
# ----------------------------------------------------------------------


def resolve_submission_criteria(conn: sqlite3.Connection, criteria: dict) -> dict:
    """解析 submission_criteria：preconditions 原样 + logic_rules 解析为规则行。

    返回 {"preconditions": [...], "logic_rules": [LogicRuleRow], "error": str|None}。
    error 非空 = 存在悬空引用（引用的规则不存在）或引用未 published 规则。
    """
    from src.builder.logic import rules_repo

    preconditions = criteria.get("preconditions") or []
    resolved: list = []
    errors: list[str] = []
    for ref in criteria.get("logic_rules") or []:
        rule = rules_repo.resolve(conn, str(ref))
        if rule is None:
            errors.append(f"引用的逻辑规则不存在: {ref}")
        elif rule.status != PUBLISHED:
            errors.append(f"引用的逻辑规则未发布: {ref}（当前 {rule.status}）")
        else:
            resolved.append(rule)
    return {
        "preconditions": preconditions,
        "logic_rules": resolved,
        "error": "; ".join(errors) if errors else None,
    }


__all__ = [
    "ActionTypeRow",
    "build_submission_criteria",
    "create",
    "get",
    "get_by_name",
    "list_all",
    "resolve",
    "resolve_submission_criteria",
    "row_to_dict",
    "sync_action_types_from_registry",
    "update_submission_criteria",
    "upsert_runtime_action",
]
