"""Builder API 路由（P0 骨架 + P1 建模：蓝图 v0.3 §3 / §5 / 补丁 v0.3.1）。

端点：
- GET  /api/v1/builder/health（已在 P0 实现）
- GET  /api/v1/builder/object-types?category=&status=&page=&page_size=
- POST /api/v1/builder/object-types
- GET  /api/v1/builder/object-types/{id}
- PUT  /api/v1/builder/object-types/{id}
- DELETE /api/v1/builder/object-types/{id}（仅 draft）
- POST /api/v1/builder/object-types/{id}/review
- POST /api/v1/builder/object-types/{id}/publish
- GET  /api/v1/builder/link-types?...（同形态）
- POST /api/v1/builder/link-types
- GET  /api/v1/builder/link-types/{id}
- PUT  /api/v1/builder/link-types/{id}
- DELETE /api/v1/builder/link-types/{id}
- POST /api/v1/builder/link-types/{id}/review
- POST /api/v1/builder/link-types/{id}/publish

统一信封复用 src.api.schemas.Envelope / ErrorInfo。
所有 BUILDER_* 错误码 → 4xx（在 src.api.schemas 注册）。
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from src.api.schemas import (
    ERROR_CODE_HTTP_STATUS,
    ERROR_MESSAGES,
    Envelope,
    ErrorInfo,
)
from src.builder import conflict as conflict_mod
from src.builder import link_types as lt_repo
from src.builder import object_types as ot_repo
from src.builder.publish_validator import (
    validate_link_type,
    validate_object_type,
)
from src.builder.status_machine import (
    PUBLISHED,
    REVIEWED,
    IllegalTransitionError,
)
from src.runtime.store import BUILDER_SCHEMA_VERSION, BUILDER_TABLES

builder_router = APIRouter(prefix="/api/v1/builder", tags=["builder"])


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _envelope(
    request_id: str, outcome: str, data: Any = None, error: ErrorInfo | None = None
) -> dict:
    return Envelope(
        request_id=request_id, outcome=outcome, data=data, error=error
    ).model_dump()


def _error(
    request_id: str,
    code: str,
    detail: Any = None,
    outcome: str = "error",
) -> JSONResponse:
    status = ERROR_CODE_HTTP_STATUS.get(code, 400)
    return JSONResponse(
        status_code=status,
        content=_envelope(
            request_id,
            outcome,
            None,
            ErrorInfo(code=code, message=ERROR_MESSAGES.get(code, code), detail=detail),
        ),
    )


def _ok(request_id: str, data: Any) -> dict:
    return _envelope(request_id, "ok", data)


def _row_to_dict(row: Any) -> dict:
    """frozen dataclass -> dict（含 JSON Schema 字段回填）。"""
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "name_cn": row.name_cn,
        "description": row.description,
        "category": row.category,
        "property_schema": row.property_schema,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
        **({"pk_field": row.pk_field, "title_field": row.title_field,
            "source_table": row.source_table, "api_name": row.api_name}
           if hasattr(row, "pk_field") else {}),
    }


def _lt_row_to_dict(row: Any) -> dict:
    return {
        "id": row.id,
        "ontology_id": row.ontology_id,
        "name": row.name,
        "semantic_name": row.semantic_name,
        "category": row.category,
        "source_type_id": row.source_type_id,
        "target_type_id": row.target_type_id,
        "cardinality": row.cardinality,
        "fk_field": row.fk_field,
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


# ======================================================================
# Pydantic 入参模型
# ======================================================================


class ObjectTypeCreate(BaseModel):
    ontology_id: str = "default"
    name: str = Field(min_length=1, max_length=128)
    name_cn: str = ""
    description: str = ""
    category: str = Field(pattern=r"^(domain|artifact|conceptual)$")
    property_schema: dict
    pk_field: str = "id"
    title_field: str | None = None
    source_table: str = ""


class ObjectTypeUpdate(BaseModel):
    name: str | None = None
    name_cn: str | None = None
    description: str | None = None
    category: str | None = None
    property_schema: dict | None = None
    pk_field: str | None = None
    title_field: str | None = None
    source_table: str | None = None


class LinkTypeCreate(BaseModel):
    ontology_id: str = "default"
    name: str = Field(min_length=1, max_length=128)
    semantic_name: str = ""
    category: str = Field(pattern=r"^(semantic|fk_inferred|structural)$")
    source_type_id: str
    target_type_id: str
    cardinality: str = Field(pattern=r"^(1:1|1:N|N:1|N:M)$")
    fk_field: str = ""


class LinkTypeUpdate(BaseModel):
    name: str | None = None
    semantic_name: str | None = None
    category: str | None = None
    source_type_id: str | None = None
    target_type_id: str | None = None
    cardinality: str | None = None
    fk_field: str | None = None


def _coerce_json(value: Any) -> dict:
    """property_schema 允许 dict；如为 str 自动解析。"""
    if isinstance(value, dict):
        return value
    if isinstance(value, (str, bytes, bytearray)):
        obj = json.loads(value)
        if not isinstance(obj, dict):
            raise TypeError("property_schema 顶层必须为 JSON object")
        return obj
    raise TypeError(f"property_schema 类型非法: {type(value).__name__}")


# ======================================================================
# /health (P0)
# ======================================================================


@builder_router.get("/health")
def builder_health(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        existing = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    ready = set(BUILDER_TABLES).issubset(existing)
    return JSONResponse(
        content=_envelope(
            request_id,
            "ok",
            {
                "status": "ready" if ready else "degraded",
                "schema_version": BUILDER_SCHEMA_VERSION,
                "tables_present": sorted(existing & set(BUILDER_TABLES)),
                "tables_missing": sorted(set(BUILDER_TABLES) - existing),
                "store_path": str(store.ontology_path),
            },
        )
    )


# ======================================================================
# /object-types
# ======================================================================


@builder_router.get("/object-types")
def list_object_types(
    request: Request,
    category: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = ot_repo.list_all(
            conn, category=category, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [_row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_router.post("/object-types")
async def create_object_type(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body  # _safe_json 已返回错误响应
    try:
        payload = ObjectTypeCreate(**body)
    except (ValidationError, ValueError) as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)}
        )
    try:
        property_schema = _coerce_json(payload.property_schema)
    except ValueError as exc:
        return _error(
            request_id, "BUILDER_INVALID_PROPERTY_SCHEMA", {"detail": str(exc)}
        )
    store = request.app.state.runtime.store
    # 粗校验：property_schema.type 必须为 object（POST 即拦；publish 再做严格校验）
    if property_schema.get("type") != "object":
        return _error(
            request_id,
            "BUILDER_INVALID_PROPERTY_SCHEMA",
            {"detail": "property_schema.type 必须为 object"},
        )
    with store.ontology_conn() as conn:
        # POST 阶段做粗校验：name 与内置冲突即拒
        if conflict_mod.check_object_type_name_conflict(conn, payload.name):
            return _error(
                request_id,
                "BUILDER_NAME_CONFLICT",
                {"name": payload.name, "reason": "与内置类型同名"},
            )
        row = ot_repo.create(
            conn,
            ontology_id=payload.ontology_id,
            name=payload.name,
            name_cn=payload.name_cn,
            description=payload.description,
            category=payload.category,
            property_schema=property_schema,
        )
    return JSONResponse(content=_ok(request_id, _row_to_dict(row)))


@builder_router.get("/object-types/{ot_id}")
def get_object_type(ot_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = ot_repo.get(conn, ot_id)
    if row is None:
        return _error(request_id, "BUILDER_OBJECT_TYPE_NOT_FOUND", {"id": ot_id})
    return JSONResponse(content=_ok(request_id, _row_to_dict(row)))


@builder_router.put("/object-types/{ot_id}")
async def update_object_type(ot_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = ObjectTypeUpdate(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    patch = payload.model_dump(exclude_unset=True)
    if "property_schema" in patch:
        try:
            patch["property_schema"] = _coerce_json(patch["property_schema"])
        except ValueError as exc:
            return _error(
                request_id, "BUILDER_INVALID_PROPERTY_SCHEMA", {"detail": str(exc)}
            )
    store = request.app.state.runtime.store
    try:
        with store.ontology_conn() as conn:
            row = ot_repo.update(conn, ot_id, patch)
    except PermissionError as exc:
        return _error(
            request_id, "BUILDER_INVALID_STATUS_TRANSITION", {"detail": str(exc)}
        )
    if row is None:
        return _error(request_id, "BUILDER_OBJECT_TYPE_NOT_FOUND", {"id": ot_id})
    return JSONResponse(content=_ok(request_id, _row_to_dict(row)))


@builder_router.delete("/object-types/{ot_id}")
def delete_object_type(ot_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    try:
        with store.ontology_conn() as conn:
            ok = ot_repo.delete(conn, ot_id)
    except PermissionError as exc:
        return _error(request_id, "BUILDER_DELETE_NOT_ALLOWED", {"detail": str(exc)})
    if not ok:
        return _error(request_id, "BUILDER_OBJECT_TYPE_NOT_FOUND", {"id": ot_id})
    return JSONResponse(content=_ok(request_id, {"id": ot_id, "deleted": True}))


@builder_router.post("/object-types/{ot_id}/review")
def review_object_type(ot_id: str, request: Request) -> JSONResponse:
    return _transition_object_type(
        ot_id, request, target=REVIEWED, next_label="reviewed"
    )


@builder_router.post("/object-types/{ot_id}/publish")
def publish_object_type(ot_id: str, request: Request) -> JSONResponse:
    """publish 校验：property_schema + 与内置同名冲突 + （间接）link 端点（按需）。

    publish 成功后同步 reload 内存 Registry：让 /meta/schema 立即可见新类型
    （A1 单向流入的实际期望——补丁 A1）。reload 失败不影响 publish 状态（已落库），
    仅记 error issue，运营可通过重启恢复。
    """
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = ot_repo.get(conn, ot_id)
        if row is None:
            return _error(request_id, "BUILDER_OBJECT_TYPE_NOT_FOUND", {"id": ot_id})
        # 1) 与内置同名冲突
        conflict = conflict_mod.check_object_type_name_conflict(conn, row.name)
        if conflict:
            return _error(
                request_id, "BUILDER_NAME_CONFLICT", conflict
            )
        # 2) property_schema 合法
        err = validate_object_type(row)
        if err:
            return _error(
                request_id, "BUILDER_INVALID_PROPERTY_SCHEMA", {"detail": err}
            )
        # 3) 状态流转
        try:
            row = ot_repo.transition_status(conn, ot_id, PUBLISHED)
        except IllegalTransitionError as exc:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": exc.current, "target": exc.target},
            )
    # 4) publish 成功后立即 reload 内存 Registry
    reload_err = _reload_runtime_registry(request)
    if reload_err:
        return JSONResponse(
            content=_ok(
                request_id,
                {
                    **_row_to_dict(row),
                    "_warning": f"已落库但 Registry 同步失败: {reload_err}",
                },
            )
        )
    return JSONResponse(content=_ok(request_id, _row_to_dict(row)))


def _reload_runtime_registry(request: Request) -> str | None:
    """重新跑一遍 loader 同步刷内存 Registry（reload=True 幂等）。

    返回 error message 或 None。
    """
    from src.builder.registry_loader import load_published_into_registry

    rt = request.app.state.runtime
    try:
        result = load_published_into_registry(
            rt.store.ontology_path, rt.registry, reload=True
        )
    except Exception as exc:  # noqa: BLE001 —— loader 失败仅警告，不阻断 publish
        return f"loader exception: {exc}"
    errs = [i for i in result["issues"] if i["severity"] == "error"]
    if errs:
        return "; ".join(i["message"] for i in errs)
    return None


def _transition_object_type(
    ot_id: str, request: Request, *, target: str, next_label: str
) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        try:
            row = ot_repo.transition_status(conn, ot_id, target)
        except IllegalTransitionError as exc:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": exc.current, "target": exc.target},
            )
    if row is None:
        return _error(request_id, "BUILDER_OBJECT_TYPE_NOT_FOUND", {"id": ot_id})
    return JSONResponse(content=_ok(request_id, _row_to_dict(row)))


# ======================================================================
# /link-types
# ======================================================================


@builder_router.get("/link-types")
def list_link_types(
    request: Request,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = lt_repo.list_all(
            conn, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [_lt_row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_router.post("/link-types")
async def create_link_type(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = LinkTypeCreate(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        # 两端类型必须存在（任意 status 都允许；publish 阶段再校验 published）
        if ot_repo.get(conn, payload.source_type_id) is None:
            return _error(
                request_id,
                "BUILDER_UNKNOWN_SOURCE_TYPE",
                {"source_type_id": payload.source_type_id},
            )
        if ot_repo.get(conn, payload.target_type_id) is None:
            return _error(
                request_id,
                "BUILDER_UNKNOWN_TARGET_TYPE",
                {"target_type_id": payload.target_type_id},
            )
        if conflict_mod.check_link_type_name_conflict(conn, payload.name):
            return _error(
                request_id, "BUILDER_NAME_CONFLICT", {"name": payload.name}
            )
        row = lt_repo.create(
            conn,
            ontology_id=payload.ontology_id,
            name=payload.name,
            semantic_name=payload.semantic_name,
            category=payload.category,
            source_type_id=payload.source_type_id,
            target_type_id=payload.target_type_id,
            cardinality=payload.cardinality,
            fk_field=payload.fk_field,
        )
    return JSONResponse(content=_ok(request_id, _lt_row_to_dict(row)))


@builder_router.get("/link-types/{lt_id}")
def get_link_type(lt_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = lt_repo.get(conn, lt_id)
    if row is None:
        return _error(request_id, "BUILDER_LINK_TYPE_NOT_FOUND", {"id": lt_id})
    return JSONResponse(content=_ok(request_id, _lt_row_to_dict(row)))


@builder_router.put("/link-types/{lt_id}")
async def update_link_type(lt_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = LinkTypeUpdate(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    patch = payload.model_dump(exclude_unset=True)
    store = request.app.state.runtime.store
    try:
        with store.ontology_conn() as conn:
            row = lt_repo.update(conn, lt_id, patch)
    except PermissionError as exc:
        return _error(
            request_id, "BUILDER_INVALID_STATUS_TRANSITION", {"detail": str(exc)}
        )
    if row is None:
        return _error(request_id, "BUILDER_LINK_TYPE_NOT_FOUND", {"id": lt_id})
    return JSONResponse(content=_ok(request_id, _lt_row_to_dict(row)))


@builder_router.delete("/link-types/{lt_id}")
def delete_link_type(lt_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    try:
        with store.ontology_conn() as conn:
            ok = lt_repo.delete(conn, lt_id)
    except PermissionError as exc:
        return _error(request_id, "BUILDER_DELETE_NOT_ALLOWED", {"detail": str(exc)})
    if not ok:
        return _error(request_id, "BUILDER_LINK_TYPE_NOT_FOUND", {"id": lt_id})
    return JSONResponse(content=_ok(request_id, {"id": lt_id, "deleted": True}))


@builder_router.post("/link-types/{lt_id}/review")
def review_link_type(lt_id: str, request: Request) -> JSONResponse:
    return _transition_link_type(
        lt_id, request, target=REVIEWED
    )


@builder_router.post("/link-types/{lt_id}/publish")
def publish_link_type(lt_id: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = lt_repo.get(conn, lt_id)
        if row is None:
            return _error(request_id, "BUILDER_LINK_TYPE_NOT_FOUND", {"id": lt_id})
        # publish 时校验：两端 published + name 不冲突
        # known_ot_ids 包含 id 和 name（兼容 id 与 name 两种引用）
        published_ot_rows = ot_repo.list_published(conn)
        known_ot_ids: set[str] = set()
        for o in published_ot_rows:
            known_ot_ids.add(o.id)
            known_ot_ids.add(o.name)
        err = validate_link_type(row, known_ot_ids)
        if err:
            return _error(
                request_id, "BUILDER_INVALID_PROPERTY_SCHEMA", {"detail": err}
            )
        if conflict_mod.check_link_type_name_conflict(conn, row.name):
            return _error(request_id, "BUILDER_NAME_CONFLICT", {"name": row.name})
        try:
            row = lt_repo.transition_status(conn, lt_id, PUBLISHED)
        except IllegalTransitionError as exc:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": exc.current, "target": exc.target},
            )
    # P2 同步 reload 内存 Registry（与 publish_object_type 一致：让 /meta/schema 立即可见）
    reload_err = _reload_runtime_registry(request)
    if reload_err:
        return JSONResponse(
            content=_ok(
                request_id,
                {
                    **_lt_row_to_dict(row),
                    "_warning": f"已落库但 Registry 同步失败: {reload_err}",
                },
            )
        )
    return JSONResponse(content=_ok(request_id, _lt_row_to_dict(row)))


def _transition_link_type(
    lt_id: str, request: Request, *, target: str
) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        try:
            row = lt_repo.transition_status(conn, lt_id, target)
        except IllegalTransitionError as exc:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": exc.current, "target": exc.target},
            )
    if row is None:
        return _error(request_id, "BUILDER_LINK_TYPE_NOT_FOUND", {"id": lt_id})
    return JSONResponse(content=_ok(request_id, _lt_row_to_dict(row)))


# ======================================================================
# 工具
# ======================================================================


async def _safe_json(request_id: str, request: Request) -> dict | JSONResponse:
    """读 JSON body；错误时返回 JSONResponse，否则返回 dict。"""
    try:
        raw = await request.body()
    except Exception as exc:  # noqa: BLE001
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": f"body 读取失败: {exc}"}
        )
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": f"JSON 解析失败: {exc}"}
        )
    if not isinstance(obj, dict):
        return _error(
            request_id,
            "BUILDER_INVALID_REQUEST",
            {"expect": "JSON object"},
        )
    return obj
