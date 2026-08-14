"""语义接口 API 路由（B3，技术方案 §4.1 端点清单）。

API 层 = 薄壳（§4.4）：请求反序列化 → 调 runtime（query/action_engine/audit/registry）
→ 组装统一信封；禁止在 API 层写业务规则（业务规则只在动作前置规则里）。
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.api.schemas import ERROR_CODE_HTTP_STATUS, ERROR_MESSAGES, Envelope, ErrorInfo
from src.runtime.action_engine import ActionResult
from src.runtime.query import (
    InvalidDirection,
    LinkNotFound,
    ObjectNotFound,
    QueryError,
    UnknownFilterField,
    UnknownObjectType,
)

meta_router = APIRouter(prefix="/meta", tags=["meta"])
objects_router = APIRouter(prefix="/objects", tags=["objects"])
actions_router = APIRouter(prefix="/actions", tags=["actions"])
audit_router = APIRouter(prefix="/audit", tags=["audit"])


def _runtime(request: Request) -> Any:
    return request.app.state.runtime


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _envelope(request_id: str, outcome: str, data: Any = None,
              error: ErrorInfo | None = None) -> dict:
    return Envelope(request_id=request_id, outcome=outcome, data=data, error=error).model_dump()


def _error_response(request_id: str, code: str, detail: Any = None,
                    extra_outcome: str = "error") -> JSONResponse:
    status = ERROR_CODE_HTTP_STATUS.get(code, 400)
    return JSONResponse(status_code=status, content=_envelope(
        request_id, extra_outcome, None, ErrorInfo(code=code,
                                                   message=ERROR_MESSAGES.get(code, code),
                                                   detail=detail)))


# ======================================================================
# /meta —— schema 元数据（驱动前端 UI / Agent 工具生成，§3.2 一处定义四处消费）
# ======================================================================

@meta_router.get("/schema")
def get_schema(request: Request) -> dict:
    rt = _runtime(request)
    reg = rt.registry
    return _envelope(_new_request_id(), "ok", data={
        "objects": [_object_meta(o) for o in reg.object_types()],
        "links": [l.model_dump() for l in reg.link_types()],
        "actions": [_action_meta(a) for a in reg.actions()],
    })


@meta_router.get("/objects")
def get_objects(request: Request) -> dict:
    rt = _runtime(request)
    return _envelope(_new_request_id(), "ok",
                     data=[_object_meta(o) for o in rt.registry.object_types()])


@meta_router.get("/actions")
def get_actions(request: Request) -> dict:
    rt = _runtime(request)
    return _envelope(_new_request_id(), "ok",
                     data=[_action_meta(a) for a in rt.registry.actions()])


def _object_meta(obj: Any) -> dict:
    return {
        "name": obj.name, "api_name": obj.api_name, "description": obj.description,
        "pk_field": obj.pk_field, "title_field": obj.title_field or obj.pk_field,
        "source_table": obj.source_table,
        "properties": obj.model.model_json_schema()["properties"],
    }


def _action_meta(action: Any) -> dict:
    return {
        "name": action.name, "description": action.description,
        "high_risk": action.high_risk,
        "params_schema": action.params_model.model_json_schema(),
        "preconditions": [p.model_dump() for p in action.preconditions],
        "error_codes": action.error_codes,
        "state_effects": action.state_effects.model_dump(),
    }


# ======================================================================
# /objects —— 对象列表 / 详情 / 链接遍历
# ======================================================================

@objects_router.get("/{type}")
def list_objects(type: str, request: Request, page: int = 1,
                 page_size: int = 20) -> JSONResponse:
    """对象列表：非 page/page_size 的 query 参数视为等值过滤（§3.2 等值与枚举）。"""
    rt = _runtime(request)
    request_id = _new_request_id()
    filters = {k: v for k, v in request.query_params.items()
               if k not in ("page", "page_size")}
    try:
        items, total = rt.query.list_objects(type, filters=filters,
                                             page=page, page_size=page_size)
    except (UnknownObjectType, UnknownFilterField) as exc:
        return _error_response(request_id, "OBJECT_TYPE_NOT_FOUND" if isinstance(exc, UnknownObjectType)
                               else "UNKNOWN_FILTER_FIELD", {"field": getattr(exc, "field", None)})
    return JSONResponse(content=_envelope(request_id, "ok", {
        "type": type, "page": page, "page_size": page_size, "total": total,
        "items": items,
    }))


@objects_router.get("/{type}/{pk}")
def object_detail(type: str, pk: str, request: Request) -> JSONResponse:
    rt = _runtime(request)
    request_id = _new_request_id()
    try:
        detail = rt.query.get_detail(type, pk)
    except UnknownObjectType as exc:
        return _error_response(request_id, "OBJECT_TYPE_NOT_FOUND", {"type": exc.type_name})
    except ObjectNotFound as exc:
        return _error_response(request_id, "OBJECT_NOT_FOUND", {"type": exc.type_name, "pk": exc.pk})
    return JSONResponse(content=_envelope(request_id, "ok", detail))


@objects_router.get("/{type}/{pk}/links/{link_name}")
def link_traversal(type: str, pk: str, link_name: str, request: Request,
                   direction: str = "out") -> JSONResponse:
    rt = _runtime(request)
    request_id = _new_request_id()
    try:
        objects = rt.query.get_links(type, pk, link_name, direction)
    except UnknownObjectType as exc:
        return _error_response(request_id, "OBJECT_TYPE_NOT_FOUND", {"type": exc.type_name})
    except ObjectNotFound as exc:
        return _error_response(request_id, "OBJECT_NOT_FOUND", {"type": exc.type_name, "pk": exc.pk})
    except LinkNotFound as exc:
        return _error_response(request_id, "LINK_NOT_FOUND",
                               {"type": exc.type_name, "link_name": exc.link_name})
    except InvalidDirection as exc:
        return _error_response(request_id, "INVALID_DIRECTION", {"direction": exc.direction})
    return JSONResponse(content=_envelope(request_id, "ok", {
        "link_name": link_name, "direction": direction, "objects": objects,
    }))


# ======================================================================
# /actions —— 唯一写入口（D-T3：无泛化 update，§1.1/§5.2）
# ======================================================================

@actions_router.post("/{action_name}")
async def submit_action(action_name: str, request: Request) -> JSONResponse:
    """提交动作：唯一写入口。业务拒绝 = 200 + outcome=rejected（§4.2）。"""
    rt = _runtime(request)
    request_id = request.headers.get("X-Request-ID", _new_request_id())
    actor = request.headers.get("X-Actor", "api")
    actor_detail = request.headers.get("X-Actor-Detail", "")
    try:
        raw = await request.body()
        params = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return _error_response(request_id, "INVALID_REQUEST")
    if not isinstance(params, dict):
        return _error_response(request_id, "INVALID_REQUEST", {"expect": "JSON object"})

    result: ActionResult = rt.engine.execute(action_name, params, actor=actor,
                                             actor_detail=actor_detail, request_id=request_id)
    if result.outcome == "applied":
        return JSONResponse(content=_envelope(request_id, "applied", data={
            "audit_id": result.audit_id, "action_name": result.action_name,
            "effects": [e.model_dump() for e in result.effects],
            "request_id": request_id,
        }))
    return JSONResponse(content=_envelope(
        request_id, result.outcome, None,
        ErrorInfo(code=result.error_code or "FAILED", message=result.message or "",
                  detail=result.detail)))


@actions_router.get("/{audit_id}")
def action_replay(audit_id: str, request: Request) -> JSONResponse:
    """动作结果/审计回查（幂等重放，§4.1）。"""
    rt = _runtime(request)
    request_id = _new_request_id()
    record = rt.audit.get(audit_id)
    if record is None:
        return _error_response(request_id, "OBJECT_NOT_FOUND", {"audit_id": audit_id})
    return JSONResponse(content=_envelope(request_id, "ok", record))


# ======================================================================
# /audit —— 审计查询（演示用，§3.5）
# ======================================================================

@audit_router.get("")
def audit_query(request: Request, action: str | None = None,
                outcome: str | None = None, page: int = 1,
                page_size: int = 20) -> dict:
    rt = _runtime(request)
    items, total = rt.audit.query(action=action, outcome=outcome, page=page, page_size=page_size)
    return _envelope(_new_request_id(), "ok", {"items": items, "total": total})


@audit_router.get("/{audit_id}")
def audit_get(audit_id: str, request: Request) -> JSONResponse:
    rt = _runtime(request)
    record = rt.audit.get(audit_id)
    if record is None:
        return _error_response(_new_request_id(), "OBJECT_NOT_FOUND", {"audit_id": audit_id})
    return JSONResponse(content=_envelope(_new_request_id(), "ok", record))
