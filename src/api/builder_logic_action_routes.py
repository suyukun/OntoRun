"""Builder 逻辑规则 / 动作类型 / E6 动作执行 API（蓝图 v0.3 §9-P4 / §5）。

端点（统一信封 + X-Actor 校验，对齐 builder_*_routes.py 风格）：
- POST /api/v1/builder/logic/discover      从已发布 object_types 推导逻辑规则
- GET  /api/v1/builder/logic               列表（logic_type/severity/status 筛选）
- GET  /api/v1/builder/logic/{ref}         单条（id 或 name）
- POST /api/v1/builder/logic/{ref}/review  draft -> reviewed（E4 状态机）
- POST /api/v1/builder/logic/{ref}/publish reviewed -> published（表达式校验）
- GET  /api/v1/builder/actions             动作类型列表（含 runtime 同步元数据）
- GET  /api/v1/builder/actions/{name}      单条（含 submission_criteria 解析）
- POST /api/v1/builder/actions/{name}/run  对接 runtime 引擎执行（支持 dry_run，
                                           落 action_runs E6 before/after 快照）
- GET  /api/v1/builder/actions/{name}/runs 执行历史（含快照与 audit_ref）

业务拒绝/失败 = 200 + outcome=rejected/failed（与运行时 /actions 约定一致，§4.2）；
未知动作 404、非法流转 4xx、A2 边界（动态动作执行）400。
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from src.api.schemas import (
    ERROR_CODE_HTTP_STATUS,
    ERROR_MESSAGES,
    Envelope,
    ErrorInfo,
)
from src.builder.logic import action_runs, action_types, discovery, rules_repo
from src.builder.status_machine import (
    PUBLISHED,
    REVIEWED,
    IllegalTransitionError,
)
from src.runtime.action_engine import ALLOWED_ACTORS

builder_logic_action_router = APIRouter(
    prefix="/api/v1/builder", tags=["builder-logic-action"]
)


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _envelope(
    request_id: str, outcome: str, data: Any = None, error: ErrorInfo | None = None
) -> dict:
    return Envelope(
        request_id=request_id, outcome=outcome, data=data, error=error
    ).model_dump()


def _error(
    request_id: str, code: str, detail: Any = None, outcome: str = "error"
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


def _check_actor(request: Request, request_id: str) -> JSONResponse | None:
    """X-Actor 校验；非白名单返回 400 错误响应，否则返回 None。"""
    actor = request.headers.get("X-Actor", "api")
    if actor not in ALLOWED_ACTORS:
        return JSONResponse(
            status_code=400,
            content=_envelope(
                request_id,
                "error",
                None,
                ErrorInfo(
                    code="INVALID_ACTOR",
                    message=ERROR_MESSAGES["INVALID_ACTOR"],
                    detail={"actor": actor},
                ),
            ),
        )
    return None


async def _safe_json(request_id: str, request: Request) -> dict | JSONResponse:
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
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"expect": "JSON object"})
    return obj


# ----------------------------------------------------------------------
# Pydantic 入参模型
# ----------------------------------------------------------------------


class LogicDiscoverRequest(BaseModel):
    """POST /logic/discover 入参：object_type 缺省 = 全部已发布。"""

    object_type: str | None = Field(default=None, max_length=128)
    ontology_id: str = Field(default="default", max_length=64)


class ActionRunRequest(BaseModel):
    """POST /actions/{name}/run 入参。

    params 必经引擎 Pydantic 校验（LLM 输出视为不可信输入，不可绕开）。
    """

    params: dict = Field(default_factory=dict)
    dry_run: bool = False


def _registry_has_action(registry, name: str) -> bool:
    """runtime Registry 是否有该动作实现（内置动作唯一事实来源）。"""
    try:
        registry.action(name)
        return True
    except KeyError:
        return False


# ----------------------------------------------------------------------
# /logic
# ----------------------------------------------------------------------


@builder_logic_action_router.post("/logic/discover")
async def logic_discover(request: Request) -> JSONResponse:
    """从已发布 object_types 的 property_schema 实际推导逻辑规则（禁模板化）。"""
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = LogicDiscoverRequest(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        result = discovery.discover_rules(
            conn,
            object_type_ref=payload.object_type,
            ontology_id=payload.ontology_id,
        )
        if result.get("error") == "not_found_or_not_published":
            return _error(
                request_id,
                "BUILDER_OBJECT_TYPE_NOT_PUBLISHED",
                {"object_type": payload.object_type},
            )
    return JSONResponse(content=_ok(request_id, result))


@builder_logic_action_router.get("/logic")
def list_logic_rules(
    request: Request,
    logic_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = rules_repo.list_all(
            conn,
            logic_type=logic_type,
            severity=severity,
            status=status,
            page=page,
            page_size=page_size,
        )
    return _ok(
        request_id,
        {
            "items": [rules_repo.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_logic_action_router.get("/logic/{ref}")
def get_logic_rule(ref: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = rules_repo.resolve(conn, ref)
    if row is None:
        return _error(request_id, "BUILDER_LOGIC_RULE_NOT_FOUND", {"ref": ref})
    return JSONResponse(content=_ok(request_id, rules_repo.row_to_dict(row)))


def _transition_logic_rule(ref: str, request: Request, *, target: str) -> JSONResponse:
    """review/publish 共用流转（E4 状态机；publish 加表达式结构校验）。"""
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = rules_repo.resolve(conn, ref)
        if row is None:
            return _error(request_id, "BUILDER_LOGIC_RULE_NOT_FOUND", {"ref": ref})
        if target == PUBLISHED:
            err = discovery.validate_expression(row.expression)
            if err:
                return _error(
                    request_id,
                    "BUILDER_LOGIC_EXPRESSION_INVALID",
                    {"rule": row.name, "detail": err},
                )
        try:
            row = rules_repo.transition_status(conn, row.id, target)
        except IllegalTransitionError as exc:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": exc.current, "target": exc.target},
            )
    return JSONResponse(content=_ok(request_id, rules_repo.row_to_dict(row)))


@builder_logic_action_router.post("/logic/{ref}/review")
def review_logic_rule(ref: str, request: Request) -> JSONResponse:
    return _transition_logic_rule(ref, request, target=REVIEWED)


@builder_logic_action_router.post("/logic/{ref}/publish")
def publish_logic_rule(ref: str, request: Request) -> JSONResponse:
    return _transition_logic_rule(ref, request, target=PUBLISHED)


# ----------------------------------------------------------------------
# /actions（动作类型元数据 + 引擎执行 + E6 runs）
# ----------------------------------------------------------------------


@builder_logic_action_router.get("/actions")
def list_action_types(
    request: Request,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = action_types.list_all(
            conn, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [action_types.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_logic_action_router.get("/actions/{name}")
def get_action_type(name: str, request: Request) -> JSONResponse:
    """详情：含 submission_criteria 解析（published 逻辑规则引用校验）。"""
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = action_types.resolve(conn, name)
        if row is None:
            return _error(request_id, "BUILDER_ACTION_TYPE_NOT_FOUND", {"name": name})
        criteria = action_types.resolve_submission_criteria(
            conn, row.submission_criteria
        )
    data = action_types.row_to_dict(row)
    data["resolved_criteria"] = {
        "preconditions": criteria["preconditions"],
        "logic_rules": [rules_repo.row_to_dict(r) for r in criteria["logic_rules"]],
        "error": criteria["error"],
    }
    return JSONResponse(content=_ok(request_id, data))


@builder_logic_action_router.post("/actions/{name}/run")
async def run_action_endpoint(name: str, request: Request) -> JSONResponse:
    """对接 runtime 引擎真实执行（支持 dry_run）；每 run 落 action_runs（E6）。"""
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = ActionRunRequest(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    actor = request.headers.get("X-Actor", "api")
    rt = request.app.state.runtime
    store = rt.store
    with store.ontology_conn() as conn:
        at_row = action_types.resolve(conn, name)
        if at_row is None:
            return _error(request_id, "BUILDER_ACTION_TYPE_NOT_FOUND", {"name": name})
        if at_row.status != PUBLISHED:
            return _error(
                request_id,
                "BUILDER_ACTION_NOT_PUBLISHED",
                {"name": name, "status": at_row.status},
            )
        # submission_criteria 引用完整性（悬空/未发布引用 -> 4xx 拒执行）
        criteria = action_types.resolve_submission_criteria(
            conn, at_row.submission_criteria
        )
        if criteria["error"]:
            return _error(
                request_id,
                "BUILDER_LOGIC_RULE_NOT_PUBLISHED",
                {"name": name, "detail": criteria["error"]},
            )
        if not _registry_has_action(rt.registry, name):
            # 补丁 A2：动态对象类型的写回执行列发布期 TODO，只登记元数据不执行
            return _error(
                request_id,
                "BUILDER_ACTION_NOT_EXECUTABLE",
                {"name": name, "reason": "runtime 引擎无此动作实现（补丁 A2 TODO）"},
            )
        result, run_row = action_runs.run_action(
            store,
            rt.registry,
            rt.engine,
            conn,
            action_type_id=at_row.id,
            action_name=name,
            params=payload.params,
            actor=actor,
            dry_run=payload.dry_run,
            request_id=request_id,
        )
    return JSONResponse(
        content=_envelope(
            request_id,
            result.outcome,
            data={
                "run_id": run_row.id,
                "action_name": name,
                "status": run_row.status,
                "dry_run": payload.dry_run,
                "error": run_row.error,
                "error_code": result.error_code,
                "executed_by": run_row.executed_by,
                "audit_ref": run_row.audit_ref,
                "duration_ms": result.duration_ms,
                "effects": [e.model_dump() for e in result.effects],
                "before_snapshot": run_row.before_snapshot,
                "after_snapshot": run_row.after_snapshot,
                "logic_rules": [r.name for r in criteria["logic_rules"]],
            },
        )
    )


@builder_logic_action_router.get("/actions/{name}/runs")
def list_action_runs(
    name: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> JSONResponse:
    """执行历史（含 before/after 快照与 audit_ref 对账锚点）。"""
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        at_row = action_types.resolve(conn, name)
        if at_row is None:
            return _error(request_id, "BUILDER_ACTION_TYPE_NOT_FOUND", {"name": name})
        runs, total = action_runs.list_by_action(
            conn, at_row.id, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "action_name": name,
            "items": [action_runs.row_to_dict(r) for r in runs],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


__all__ = ["builder_logic_action_router"]
