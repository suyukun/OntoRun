"""Builder 管道 / 数据集 / Curated API（蓝图 v0.3 §9-P2）。

端点（全部统一信封 + X-Actor 校验）：
- POST /api/v1/builder/datasets/upload         上传文件 → datasets 行
- GET  /api/v1/builder/datasets                 列表（kind/status/page）
- GET  /api/v1/builder/datasets/{name}/preview  preview 头 N 行
- POST /api/v1/builder/pipelines                建管道（name + dag_json）
- GET  /api/v1/builder/pipelines/{name}         取单个
- POST /api/v1/builder/pipelines/{name}/run     同步执行
- GET  /api/v1/builder/pipelines/{name}/runs    列 in-memory runs
- GET  /api/v1/builder/curated                  列表
- GET  /api/v1/builder/curated/{name}           取单个（按 name 找最近一条）
- POST /api/v1/builder/curated/{name}/review    draft->reviewed;再 review -> approved

统一信封 + X-Actor 校验复用 src.api.schemas / src.runtime.action_engine.ALLOWED_ACTORS。
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from src.api.schemas import (
    ERROR_CODE_HTTP_STATUS,
    ERROR_MESSAGES,
    Envelope,
    ErrorInfo,
)
from src.builder import datasets_repo, pipelines_repo
from src.builder.connectors.file_readers import read as file_read
from src.builder.curated import repo as curated_repo
from src.builder.pipeline.dag import (
    DAGValidationError,
    NodeStatus,
    parse_dag,
    run_pipeline,
)
from src.builder.pipeline.runners import (
    make_connector_handler,
    make_output_handler,
    make_storage_handler,
    make_transform_handler,
)
from src.runtime.action_engine import ALLOWED_ACTORS

builder_pipeline_router = APIRouter(
    prefix="/api/v1/builder", tags=["builder-pipeline"]
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


def _check_actor(request: Request, request_id: str) -> JSONResponse | None:
    """X-Actor 校验；非白名单返回 4xx 错误响应，否则返回 None。"""
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


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------------
# Pydantic models
# ----------------------------------------------------------------------


class PipelineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    dag_json: dict
    status: str = Field(default="draft", pattern=r"^(draft|active|archived)$")


# ----------------------------------------------------------------------
# /datasets
# ----------------------------------------------------------------------


@builder_pipeline_router.post("/datasets/upload")
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),  # noqa: B008  FastAPI 官方要求 File(...) 形式
    name: str | None = Form(default=None),
    upload_dir: str | None = Form(default=None),
) -> JSONResponse:
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    store = request.app.state.runtime.store
    # name 缺省用 filename stem
    orig = file.filename or "uploaded"
    base = Path(orig).stem or "uploaded"
    suffix = Path(orig).suffix or ""
    ds_name = name or base
    # 写文件（测试可通过 upload_dir form 字段覆盖默认 data/builder_uploads/）
    target_dir = (
        Path(upload_dir) if upload_dir else datasets_repo.DEFAULT_UPLOAD_DIR
    )
    if name:
        path = datasets_repo.upload_path(target_dir, name, suffix)
    else:
        path = datasets_repo.upload_path(target_dir, base, suffix)
    content = await file.read()
    path.write_bytes(content)
    # kind = suffix 推断
    kind = suffix.lstrip(".").lower() or "unknown"
    if kind not in datasets_repo.ALLOWED_KINDS:
        kind = "csv"  # 退化：未识别扩展名记 csv，preview 仍可工作
    # 简单行数：CSV 统计行数；其他 0
    row_count = 0
    if kind == "csv":
        try:
            text = content.decode("utf-8", errors="replace")
            row_count = max(0, text.count("\n") - (1 if text.startswith("supplier_id,") else 0))
        except Exception:  # noqa: BLE001
            row_count = 0
    with store.ontology_conn() as conn:
        ds = datasets_repo.create(
            conn,
            ontology_id="default",
            name=ds_name,
            kind=kind,
            source_path=str(path),
            status="uploaded",
            row_count=row_count,
        )
    return JSONResponse(content=_ok(request_id, datasets_repo.row_to_dict(ds)))


@builder_pipeline_router.get("/datasets")
def list_datasets(
    request: Request,
    kind: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = datasets_repo.list_all(
            conn, kind=kind, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [datasets_repo.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_pipeline_router.get("/datasets/{name}/preview")
def preview_dataset(
    name: str, request: Request, limit: int = Query(default=10, ge=1, le=200)
) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        ds = datasets_repo.get_by_name(conn, name)
    if ds is None:
        return _error(request_id, "BUILDER_DATASET_NOT_FOUND", {"name": name})
    if not ds.source_path or not Path(ds.source_path).exists():
        return _error(
            request_id,
            "BUILDER_DATASET_FILE_MISSING",
            {"name": name, "source_path": ds.source_path},
        )
    cr = file_read(ds.source_path)
    if cr.degraded:
        return JSONResponse(
            content=_ok(
                request_id,
                {
                    "name": name,
                    "kind": ds.kind,
                    "degraded": cr.degraded,
                    "preview": [],
                },
            )
        )
    rows = list(cr.rows)[:limit]
    return JSONResponse(
        content=_ok(
            request_id,
            {
                "name": name,
                "kind": ds.kind,
                "row_count": len(cr.rows),
                "preview": rows,
            },
        )
    )


# ----------------------------------------------------------------------
# /pipelines
# ----------------------------------------------------------------------


@builder_pipeline_router.post("/pipelines")
async def create_pipeline(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    body = await _safe_json(request_id, request)
    if not isinstance(body, dict):
        return body
    try:
        payload = PipelineCreate(**body)
    except (ValidationError, ValueError) as exc:
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)})
    # dag_json 顶层校验（节点结构），不强制传入 nodes（API 接收两种形态）
    if "nodes" in payload.dag_json:
        try:
            parse_dag(payload.dag_json)
        except DAGValidationError as exc:
            return _error(request_id, "BUILDER_INVALID_DAG", {"detail": str(exc)})
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        pl = pipelines_repo.create(
            conn,
            ontology_id="default",
            name=payload.name,
            dag_json=payload.dag_json,
            status=payload.status,
        )
    return JSONResponse(content=_ok(request_id, pipelines_repo.row_to_dict(pl)))


@builder_pipeline_router.get("/pipelines/{name}")
def get_pipeline(name: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        pl = pipelines_repo.get_by_name(conn, name)
    if pl is None:
        return _error(request_id, "BUILDER_PIPELINE_NOT_FOUND", {"name": name})
    return JSONResponse(content=_ok(request_id, pipelines_repo.row_to_dict(pl)))


@builder_pipeline_router.post("/pipelines/{name}/run")
def run_pipeline_endpoint(name: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        pl = pipelines_repo.get_by_name(conn, name)
    if pl is None:
        return _error(request_id, "BUILDER_PIPELINE_NOT_FOUND", {"name": name})
    try:
        nodes = parse_dag(pl.dag_json)
    except DAGValidationError as exc:
        return _error(request_id, "BUILDER_INVALID_DAG", {"detail": str(exc)})
    # 派发 handlers（按节点 kind）
    handlers: dict[str, Any] = {}
    with store.ontology_conn() as conn:
        for n in nodes:
            if n.kind == "connector":
                handlers[n.id] = make_connector_handler()
            elif n.kind == "transform":
                handlers[n.id] = make_transform_handler()
            elif n.kind == "storage":
                handlers[n.id] = make_storage_handler(conn)
            elif n.kind == "output":
                handlers[n.id] = make_output_handler(conn)
            else:
                handlers[n.id] = None
        run = run_pipeline(nodes, handlers)
    # 记录 in-memory run
    rec = pipelines_repo.PipelineRunRecord(
        run_id=f"run_{uuid.uuid4().hex[:12]}",
        pipeline_id=pl.id,
        pipeline_name=pl.name,
        started_at=_now(),
        finished_at=_now(),
        final_status=run.final_status.value,
        node_results=[
            {
                "node_id": r.node_id,
                "status": r.status.value,
                "error": r.error,
            }
            for r in run.nodes.values()
        ],
        curated_dataset_id=_curated_id_from_output(run.nodes),
        error=None if run.final_status == NodeStatus.SUCCEEDED else "pipeline_failed",
    )
    pipelines_repo.record_run(rec)
    return JSONResponse(
        content=_ok(
            request_id,
            {
                "run_id": rec.run_id,
                "pipeline_name": pl.name,
                "final_status": rec.final_status,
                "nodes": rec.node_results,
                "curated_dataset_id": rec.curated_dataset_id,
            },
        )
    )


def _curated_id_from_output(nodes_results: dict) -> str | None:
    """从 output 节点 output 中提 curated_id。"""
    for r in nodes_results.values():
        out = r.output
        if isinstance(out, dict) and "curated_id" in out:
            return out["curated_id"]
    return None


@builder_pipeline_router.get("/pipelines/{name}/runs")
def list_pipeline_runs(name: str, request: Request) -> dict:
    request_id = _new_request_id()
    runs = pipelines_repo.list_runs(name)
    items = [
        {
            "run_id": r.run_id,
            "pipeline_name": r.pipeline_name,
            "final_status": r.final_status,
            "started_at": r.started_at,
            "finished_at": r.finished_at,
            "node_count": len(r.node_results),
            "curated_dataset_id": r.curated_dataset_id,
            "error": r.error,
        }
        for r in runs
    ]
    return _ok(request_id, {"pipeline_name": name, "runs": items, "total": len(items)})


# ----------------------------------------------------------------------
# /curated
# ----------------------------------------------------------------------


@builder_pipeline_router.get("/curated")
def list_curated(
    request: Request,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = curated_repo.list_all(
            conn, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [curated_repo.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_pipeline_router.get("/curated/{name}")
def get_curated(name: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = curated_repo.get_by_dataset_id(conn, name)
    if row is None:
        return _error(request_id, "BUILDER_CURATED_NOT_FOUND", {"name": name})
    return JSONResponse(content=_ok(request_id, curated_repo.row_to_dict(row)))


@builder_pipeline_router.post("/curated/{name}/review")
def review_curated(name: str, request: Request) -> JSONResponse:
    """curated 状态机：draft -> reviewed（首次调）；reviewed -> approved（再调）。

    一次 review 推进一步；目标状态 = 当前状态 + 1。
    """
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = curated_repo.get_by_dataset_id(conn, name)
        if row is None:
            return _error(request_id, "BUILDER_CURATED_NOT_FOUND", {"name": name})
        next_status = {
            "draft": "reviewed",
            "reviewed": "approved",
        }.get(row.status)
        if next_status is None:
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": row.status, "target": "next", "reason": "已 approved，不可再推进"},
            )
        try:
            updated = curated_repo.transition_status(conn, row.id, next_status)
        except Exception as exc:  # noqa: BLE001
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": row.status, "target": next_status, "detail": str(exc)},
            )
    return JSONResponse(content=_ok(request_id, curated_repo.row_to_dict(updated)))


# ----------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------


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
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"expect": "JSON object"}
        )
    return obj
