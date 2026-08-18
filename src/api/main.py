"""FastAPI 应用工厂（B3，技术方案 §4）。

create_app 组装：registry（self_check）→ Store（双库+migrate）→ ObjectIndex（全量加载）
→ AuditLog → ActionEngine → ObjectQuery；挂载 meta/objects/actions/audit 路由。
OpenAPI 自动生成（/openapi.json 与 /docs）。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from src.api import routes
from src.api.builder_routes import builder_router
from src.ontology import build_registry
from src.runtime.action_engine import ActionEngine
from src.runtime.audit import AuditLog
from src.runtime.index import ObjectIndex
from src.runtime.query import ObjectQuery
from src.runtime.store import Store


@dataclass
class RuntimeServices:
    """进程内服务聚合（API 薄壳的依赖注入）。"""

    registry: Any
    store: Store
    index: ObjectIndex
    query: ObjectQuery
    audit: AuditLog
    engine: ActionEngine


def create_app(
    source_db: str | Path | None = None,
    ontology_db: str | Path | None = None,
    rebuild_seed: bool = False,
) -> FastAPI:
    """创建语义接口应用。source_db/ontology_db 可注入（测试用临时库）。"""
    if rebuild_seed:
        from data import seed_retail_source

        seed_path = Path(source_db) if source_db else seed_retail_source.DEFAULT_DB_PATH
        seed_retail_source.build_database(seed_path)

    registry = build_registry()
    issues = registry.self_check()
    errors = [i.message for i in issues if i.severity == "error"]
    if errors:
        raise RuntimeError(f"本体 registry self_check 未通过: {errors}")

    store = Store(source_db, ontology_db)
    store.migrate()

    # A1 单向流入（蓝图 v0.3 §10 决策 1 / 补丁 A1）：把本体库 published 行合并进
    # 内存 Registry。冲突检测 / 动态类生成由 src.builder.registry_loader 完成。
    # 在 store.migrate 之后跑（要读本体库），在 self_check 之后再跑（让内置段先稳）。
    from src.builder.registry_loader import load_published_into_registry

    load_result = load_published_into_registry(store.ontology_path, registry)
    load_errors = [i for i in load_result["issues"] if i["severity"] == "error"]
    if load_errors:
        raise RuntimeError(
            "Builder loader 报 error 级 issue（冲突/未注册端点等）: "
            + "; ".join(i["message"] for i in load_errors)
        )

    index = ObjectIndex(registry)
    with store.source_conn() as conn:
        index.load_all(conn)
    with store.ontology_conn() as conn:
        index.load_ontology_state(conn)
    audit = AuditLog(store)
    engine = ActionEngine(registry, store, index, audit)
    query = ObjectQuery(index, registry)

    app = FastAPI(
        title="OntoRun 语义接口",
        description="零售供应链最小语义接口闭环（对象/链接/动作 + 本体运行时写回回路）",
        version="0.1.0",
    )
    app.state.runtime = RuntimeServices(
        registry=registry,
        store=store,
        index=index,
        query=query,
        audit=audit,
        engine=engine,
    )
    app.include_router(routes.meta_router)
    app.include_router(routes.objects_router)
    app.include_router(routes.actions_router)
    app.include_router(routes.audit_router)
    app.include_router(builder_router)
    _inject_schema_into_openapi(app, registry)
    return app


def _inject_schema_into_openapi(app: FastAPI, registry: Any) -> None:
    """把本体 schema（对象属性 + 动作参数模型）注入 OpenAPI components（§3.2 元数据驱动）。"""
    from fastapi.openapi.utils import get_openapi

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        schemas = schema.setdefault("components", {}).setdefault("schemas", {})
        for obj in registry.object_types():
            name = obj.model.__name__
            if name not in schemas:
                schemas[name] = obj.model.model_json_schema()
        for action in registry.actions():
            name = action.params_model.__name__
            if name not in schemas:
                schemas[name] = action.params_model.model_json_schema()
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi


app = create_app()
