"""Builder 映射/提取 API 路由（蓝图 v0.3 §9-P3 / 补丁 A1）。

端点：
- POST /api/v1/builder/mappings/auto         从 curated/dataset 推断映射
- GET  /api/v1/builder/mappings             列表
- GET  /api/v1/builder/mappings/{name}       单个（按 entity_class 找最近一条）
- POST /api/v1/builder/mappings/{name}/apply 映射结果生成 draft object_types/link_types
- POST /api/v1/builder/extractions/run      跑 LLM 提取（mock/deepseek）
- GET  /api/v1/builder/extractions          列表（含 validation_report）
- GET  /api/v1/builder/extractions/{name}   单个

X-Actor 校验复用 ALLOWED_ACTORS；统一信封。
apply 流程：A1 单向流入 + 补丁 A1（与内置同名拒绝 publish；publish 后 reload Registry）
"""

from __future__ import annotations

import asyncio
import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from src.api.schemas import (
    ERROR_CODE_HTTP_STATUS,
    ERROR_MESSAGES,
    Envelope,
    ErrorInfo,
)
from src.builder import (
    conflict as conflict_mod,
)
from src.builder import (
    link_types as lt_repo,
)
from src.builder import (
    object_types as ot_repo,
)
from src.builder.extraction import (
    ExtractionResult,
    extract_from_text,
)
from src.builder.extraction import (
    repo as extraction_repo,
)
from src.builder.mapping import auto_map_from_inference
from src.builder.mapping import repo as mapping_repo
from src.builder.pipeline import schema_infer
from src.builder.pipeline.schema_infer import infer_from_csv_path
from src.builder.status_machine import (
    DRAFT,
    PUBLISHED,
    REVIEWED,
    IllegalTransitionError,
)
from src.runtime.action_engine import ALLOWED_ACTORS

builder_mapping_extraction_router = APIRouter(
    prefix="/api/v1/builder", tags=["builder-mapping-extraction"]
)


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _envelope(request_id, outcome, data=None, error=None):
    return Envelope(
        request_id=request_id, outcome=outcome, data=data, error=error
    ).model_dump()


def _error(request_id, code, detail=None, outcome="error"):
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


def _ok(request_id, data):
    return _envelope(request_id, "ok", data)


def _check_actor(request, request_id):
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


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------------
# Pydantic models
# ----------------------------------------------------------------------


class MappingAutoRequest(BaseModel):
    """POST /mappings/auto 入参。"""

    source_table: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    target_table: str | None = None
    target_path: str | None = None
    target_pk: str | None = None
    alias_doc_path: str | None = None
    alias_doc_text: str | None = None
    master_suppliers_path: str | None = None


class ExtractionRunRequest(BaseModel):
    source_path: str = Field(min_length=1)
    provider: str = Field(default="mock", pattern=r"^(mock|deepseek)$")
    source_text: str | None = None
    extraction_schema: dict | None = None


# ----------------------------------------------------------------------
# /mappings/auto
# ----------------------------------------------------------------------


@builder_mapping_extraction_router.post("/mappings/auto")
async def mappings_auto(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    body_raw = await request.body()
    try:
        body = json.loads(body_raw or b"{}")
    except json.JSONDecodeError as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": f"JSON 解析失败: {exc}"}
        )
    if not isinstance(body, dict):
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"expect": "object"})
    try:
        payload = MappingAutoRequest(**body)
    except (ValidationError, ValueError) as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)}
        )
    sp = Path(payload.source_path)
    if not sp.is_absolute():
        sp = (Path.cwd() / sp).resolve()
    if not sp.exists():
        return _error(
            request_id,
            "BUILDER_DATASET_FILE_MISSING",
            {"name": payload.source_table, "source_path": str(sp)},
        )
    try:
        inference = infer_from_csv_path(sp, dataset_id=payload.source_table, pk_column="auto")
    except Exception as exc:  # noqa: BLE001
        return _error(
            request_id,
            "BUILDER_INVALID_REQUEST",
            {"detail": f"schema_infer 失败: {exc}"},
        )
    # 读 source_rows（async 函数中避免阻塞 open：用 to_thread）
    def _read_csv_sync(p: Path) -> list[dict[str, str]]:
        with open(p, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    source_rows = await asyncio.to_thread(_read_csv_sync, sp)
    # target 可选
    target_rows: list[dict[str, str]] | None = None
    target_columns: list[str] | None = None
    if payload.target_path:
        tp = Path(payload.target_path)
        if not tp.is_absolute():
            tp = (Path.cwd() / tp).resolve()
        if not tp.exists():
            return _error(
                request_id,
                "BUILDER_DATASET_FILE_MISSING",
                {"name": payload.target_table, "source_path": str(tp)},
            )
        def _read_target(p: Path) -> tuple[list[dict], list[str]]:
            with open(p, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                return list(reader), list(reader.fieldnames or [])
        target_rows, target_columns = await asyncio.to_thread(_read_target, tp)
    # alias 可选
    alias_text: str | None = payload.alias_doc_text
    master: list[dict] | None = None
    if payload.master_suppliers_path:
        mp = Path(payload.master_suppliers_path)
        if not mp.is_absolute():
            mp = (Path.cwd() / mp).resolve()
        if mp.exists():
            def _read_master(p: Path) -> list[dict]:
                with open(p, encoding="utf-8", newline="") as f:
                    return list(csv.DictReader(f))
            master = await asyncio.to_thread(_read_master, mp)
    if alias_text is None and payload.alias_doc_path:
        dp = Path(payload.alias_doc_path)
        if not dp.is_absolute():
            dp = (Path.cwd() / dp).resolve()
        if dp.exists():
            alias_text = dp.read_text(encoding="utf-8")
    result = auto_map_from_inference(
        inference,
        source_rows=source_rows,
        target_table=payload.target_table,
        target_rows=target_rows,
        target_pk=payload.target_pk,
        target_columns=target_columns,
        alias_doc_text=alias_text,
        master_suppliers=master,
    )
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = mapping_repo.create(
            conn,
            ontology_id="default",
            entity_class=result.entity_class,
            source_table=result.source_table,
            field_mapping=result.field_mapping,
            fk_mappings=result.fk_mappings,
            cardinalities=result.cardinalities,
            status=DRAFT,
        )
    data = mapping_repo.row_to_dict(row)
    data["property_schema"] = result.property_schema
    if result.alias_matches is not None:
        data["alias_matches"] = result.alias_matches
    return JSONResponse(content=_ok(request_id, data))


@builder_mapping_extraction_router.get("/mappings")
def list_mappings(
    request: Request,
    entity_class: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = mapping_repo.list_all(
            conn,
            entity_class=entity_class,
            status=status,
            page=page,
            page_size=page_size,
        )
    return _ok(
        request_id,
        {
            "items": [mapping_repo.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_mapping_extraction_router.get("/mappings/{name}")
def get_mapping(name: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        # 简化：按 entity_class 找最近一条
        items, _ = mapping_repo.list_all(conn, entity_class=name, page=1, page_size=1)
    if not items:
        return _error(request_id, "BUILDER_MAPPING_NOT_FOUND", {"name": name})
    return JSONResponse(content=_ok(request_id, mapping_repo.row_to_dict(items[0])))


# ----------------------------------------------------------------------
# /mappings/{name}/apply
# ----------------------------------------------------------------------


@builder_mapping_extraction_router.post("/mappings/{name}/apply")
def mappings_apply(name: str, request: Request) -> JSONResponse:
    """把 mapping 结果生成 draft object_types + draft link_types。

    行为：
      - 找到 entity_class=name 的最新 draft mapping；
      - 创建 1 个 object_type（name = entity_class, property_schema = 派生）；
      - 对每条 fk_mapping，target_table 必须在已发布 object_types 中（按
        target_table 字符串等于 name 或 id）；存在则创建 link_type draft；
        否则 warning issue 记 result。
      - object_type 和 link_type 都保持 draft 状态（人工走 review -> publish）。
    """
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    store = request.app.state.runtime.store
    issues: list[dict] = []
    with store.ontology_conn() as conn:
        mp_items, _ = mapping_repo.list_all(conn, entity_class=name, page=1, page_size=1)
        if not mp_items:
            return _error(request_id, "BUILDER_MAPPING_NOT_FOUND", {"name": name})
        mp = mp_items[0]
        if mp.status not in (DRAFT, REVIEWED, PUBLISHED):
            return _error(
                request_id,
                "BUILDER_INVALID_STATUS_TRANSITION",
                {"current": mp.status, "target": "apply"},
            )
        # 1) 重建 property_schema（field_mapping -> JSON Schema）
        properties: dict = {}
        required: list[str] = []
        for f in mp.field_mapping:
            if f.get("is_technical"):
                continue
            pname = f.get("property_name") or f.get("column")
            _ = schema_infer.ColumnSpec.__class__  # 避免静态检查告警
            # 简单映射
            t = f.get("inferred_type", "string")
            json_type = {
                "string": "string",
                "integer": "integer",
                "float": "number",
                "datetime": "string",
                "enum": "string",
            }.get(t, "string")
            properties[pname] = {"type": json_type, "description": f"自动从 {f.get('column')} 派生"}
            if f.get("is_pk"):
                required.insert(0, pname)
        property_schema = {"type": "object", "properties": properties, "required": required}
        # 2) 冲突检测（与内置同名）
        if conflict_mod.check_object_type_name_conflict(conn, name):
            return _error(
                request_id,
                "BUILDER_NAME_CONFLICT",
                {"name": name, "reason": "与内置类型同名"},
            )
        # 3) 创建 object_type draft（按 entity_class；已存在则跳过 + 报 issue）
        existing_ot = ot_repo.get(conn, name) or _find_ot_by_name(conn, name)
        ot_id: str
        if existing_ot is None:
            ot_row = ot_repo.create(
                conn,
                ontology_id="default",
                name=name,
                name_cn=name,
                description=f"从 mapping {mp.id} 自动 apply 生成的 object_type",
                category="domain",
                property_schema=property_schema,
            )
            ot_id = ot_row.id
            issues.append({"code": "MAPPING_OT_CREATED", "severity": "info", "message": f"已创建 object_type {name!r}"})
        else:
            ot_id = existing_ot.id
            issues.append({
                "code": "MAPPING_OT_REUSED",
                "severity": "info",
                "message": f"object_type {name!r} 已存在，复用 id={ot_id}",
            })
        # 4) 为每条 fk 创建 link_type draft
        created_links: list[dict] = []
        skipped_links: list[dict] = []
        for fk in mp.fk_mappings or []:
            target_name = fk.get("target_table", "")
            target_ot = _find_ot_by_name(conn, target_name)
            if target_ot is None:
                # 没找到目标：把 fk_field 注入 source ot property_schema（不建 link）
                fk_field = fk.get("source_field", "")
                fk_pname = _snake_to_pascal(fk_field)
                if fk_field and fk_pname not in properties:
                    properties[fk_pname] = {
                        "type": "string",
                        "description": f"FK 锚点（apply 时未找到 target {target_name}）",
                    }
                issues.append({
                    "code": "MAPPING_FK_TARGET_MISSING",
                    "severity": "warning",
                    "message": f"fk {fk.get('link_id')!r} 目标 {target_name!r} 不在已发布 object_types，跳过 link 创建",
                })
                skipped_links.append(fk)
                continue
            link_id_name = fk.get("link_id", f"lnk_{name}_{target_name}")
            # 检查是否同名 link 已存在
            existing_lt = _find_lt_by_name(conn, link_id_name)
            if existing_lt is not None:
                created_links.append({"link_id": link_id_name, "status": "reused"})
                continue
            fk_field = fk.get("source_field", "")
            fk_pname = _snake_to_pascal(fk_field)
            if fk_field and fk_pname not in properties:
                properties[fk_pname] = {
                    "type": "string",
                    "description": "FK 锚点（apply 自动派生）",
                }
            cardinality = fk.get("cardinality", "N:1")
            try:
                lt_row = lt_repo.create(
                    conn,
                    ontology_id="default",
                    name=link_id_name,
                    semantic_name=fk.get("detection_method", ""),
                    category="fk_inferred",
                    source_type_id=ot_id,
                    target_type_id=target_ot.id,
                    cardinality=cardinality,
                    fk_field=fk_pname,
                )
                created_links.append({
                    "link_id": link_id_name,
                    "status": "created",
                    "id": lt_row.id,
                    "cardinality": cardinality,
                })
            except Exception as exc:  # noqa: BLE001
                issues.append({
                    "code": "MAPPING_FK_CREATE_FAILED",
                    "severity": "error",
                    "message": f"fk {link_id_name!r} 创建失败: {exc}",
                })
                skipped_links.append(fk)
        # 5) 推 mapping 状态到 reviewed（让人工审核 publish）
        try:
            mapping_repo.transition_status(conn, mp.id, REVIEWED)
        except IllegalTransitionError:
            pass  # 已经是 reviewed/published -> 忽略
    # 6) 同步 reload Registry（apply 完成让 A1 链路在下次 publish 前保留 draft；publish
    #    路径已由 /object-types/{id}/publish 处理 reload；这里不主动 reload）
    return JSONResponse(
        content=_ok(
            request_id,
            {
                "mapping_id": mp.id,
                "entity_class": name,
                "object_type_id": ot_id,
                "created_links": created_links,
                "skipped_links": skipped_links,
                "issues": issues,
            },
        )
    )


def _snake_to_pascal(s: str) -> str:
    if not s:
        return ""
    parts = [p for p in s.split("_") if p]
    return "".join((p[0].upper() + p[1:]) if p and not p[0].isdigit() else p for p in parts)


def _find_ot_by_name(conn, name: str):
    """在 object_types 表按 name 查（任意 status）。"""
    row = conn.execute(
        "SELECT * FROM object_types WHERE name = ?", (name,)
    ).fetchone()
    return ot_repo._row_factory(row) if row else None


def _find_lt_by_name(conn, name: str):
    row = conn.execute(
        "SELECT * FROM link_types WHERE name = ?", (name,)
    ).fetchone()
    return lt_repo._row_factory(row) if row else None


# ----------------------------------------------------------------------
# /extractions/run
# ----------------------------------------------------------------------


@builder_mapping_extraction_router.post("/extractions/run")
async def extractions_run(request: Request) -> JSONResponse:
    request_id = _new_request_id()
    actor_err = _check_actor(request, request_id)
    if actor_err is not None:
        return actor_err
    body_raw = await request.body()
    try:
        body = json.loads(body_raw or b"{}")
    except json.JSONDecodeError as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": f"JSON 解析失败: {exc}"}
        )
    if not isinstance(body, dict):
        return _error(request_id, "BUILDER_INVALID_REQUEST", {"expect": "object"})
    try:
        payload = ExtractionRunRequest(**body)
    except (ValidationError, ValueError) as exc:
        return _error(
            request_id, "BUILDER_INVALID_REQUEST", {"detail": str(exc)}
        )
    # 拿文本
    text = payload.source_text
    if text is None:
        sp = Path(payload.source_path)
        if not sp.is_absolute():
            sp = (Path.cwd() / sp).resolve()
        if not sp.exists():
            return _error(
                request_id,
                "BUILDER_DATASET_FILE_MISSING",
                {"name": payload.source_path, "source_path": str(sp)},
            )
        text = sp.read_text(encoding="utf-8")
    # provider
    provider = _build_provider(payload.provider)
    # schema 默认
    schema = payload.extraction_schema or {}
    if not schema:
        # 从 fixtures expected 读：调用方传 schema_json 即可；不传时为空集合
        schema = {
            "entity_types_whitelist": [],
            "relation_types_whitelist": [],
            "logic_rule_patterns": [],
            "action_types": [],
        }
    # 提取 + 校验
    result: ExtractionResult = extract_from_text(
        text,
        provider=provider,
        source_path=payload.source_path,
        schema=schema,
    )
    # 状态：有 fatal -> failed（参考补丁 C3 + 蓝图 §8：LLM 输出视为不可信，fatal 阻断）
    if result.validation_report.has_fatal:
        new_status = "failed"
    elif result.validation_report.has_error:
        new_status = "rejected"
    else:
        new_status = "succeeded"
    result_summary = {
        "entity_count": len(result.payload.entities),
        "relation_count": len(result.payload.relations),
        "logic_rule_count": len(result.payload.logic_rules),
        "action_count": len(result.payload.actions),
    }
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = extraction_repo.create(
            conn,
            ontology_id="default",
            status=new_status,
            result_summary=result_summary,
            validation_report=result.validation_report.as_dict(),
            source_path=payload.source_path,
            provider=result.provider,
        )
    data = extraction_repo.row_to_dict(row)
    data["payload"] = result.payload.as_dict()
    data["raw_response"] = result.raw_response
    return JSONResponse(content=_ok(request_id, data))


def _build_provider(name: str):
    if name == "mock":
        from src.agent.provider import MockProvider

        return MockProvider()
    if name == "deepseek":
        from src.agent.provider import DeepSeekProvider

        return DeepSeekProvider()  # 缺 key 时自己抛错
    raise ValueError(f"未知 provider: {name}")


# ----------------------------------------------------------------------
# /extractions + /extractions/{name}
# ----------------------------------------------------------------------


@builder_mapping_extraction_router.get("/extractions")
def list_extractions(
    request: Request,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        items, total = extraction_repo.list_all(
            conn, status=status, page=page, page_size=page_size
        )
    return _ok(
        request_id,
        {
            "items": [extraction_repo.row_to_dict(o) for o in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@builder_mapping_extraction_router.get("/extractions/{name}")
def get_extraction(name: str, request: Request) -> JSONResponse:
    request_id = _new_request_id()
    store = request.app.state.runtime.store
    with store.ontology_conn() as conn:
        # 优先按 id 查，再按 source_path（endswith 兜底）
        row = extraction_repo.get(conn, name)
        if row is None:
            items, _ = extraction_repo.list_all(conn, page=1, page_size=1000)
            cand = [
                i
                for i in items
                if i.source_path == name
                or i.source_path.endswith("/" + name)
                or i.source_path.endswith(name)
            ]
            row = cand[0] if cand else None
    if row is None:
        return _error(request_id, "BUILDER_EXTRACTION_NOT_FOUND", {"name": name})
    return JSONResponse(content=_ok(request_id, extraction_repo.row_to_dict(row)))


# ----------------------------------------------------------------------
# 错误码补登（统一信封需要）
# ----------------------------------------------------------------------

# 局部追加：避免编辑 src/api/schemas.py（P2 已定），通过 _error fallback code
# 处理：fallback 返回 code=...，HTTP 400；OK


__all__ = ["builder_mapping_extraction_router"]
