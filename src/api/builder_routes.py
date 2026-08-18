"""Builder API 路由（P0 骨架，重写蓝图 v0.3 §3 / 补丁 v0.3.1）。

P0 阶段仅暴露 /api/v1/builder/health 健康检查端点，回报：
- status（子系统就绪状态）
- schema_version（BUILDER_SCHEMA_VERSION）
- store_path（本体库路径）

业务端点（datasets/pipelines/curated/mappings/extractions 等）按 P2-P4 推进。
统一信封复用 src.api.schemas.Envelope / ErrorInfo。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.api.schemas import Envelope, ErrorInfo
from src.builder import BUILDER_SCHEMA_VERSION
from src.runtime.store import BUILDER_TABLES

builder_router = APIRouter(prefix="/api/v1/builder", tags=["builder"])


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _envelope(
    request_id: str, outcome: str, data: Any = None, error: ErrorInfo | None = None
) -> dict:
    return Envelope(
        request_id=request_id, outcome=outcome, data=data, error=error
    ).model_dump()


@builder_router.get("/health")
def builder_health(request: Request) -> JSONResponse:
    """Builder 子系统健康检查：回报 schema 版本与已建表清单。"""
    request_id = _new_request_id()
    rt = request.app.state.runtime
    store = rt.store
    # 已建表清单（来自本体库 schema）；用于运维核对 P0 10 张表是否齐全
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
