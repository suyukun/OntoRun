"""P6 全链路 E2E 验收测试（蓝图 v0.3 §9-P6 / §12-2/3/4/6 + 补丁 v0.3.1 A1/A2）。

一条命令端到端（§12-2）：一条 pytest 函数（test_full_chain_*）走通
  CSV 上传 → 管道 run（A 路径 schema_infer）→ Curated 审核 → 自动映射 apply
  → 对象/链接类型 review + publish → Registry 可见（/meta/schema，A1 单向流入）
  → LLM 动作（MockProvider，无 key 全绿 —— 蓝图 §11 / 补丁 C5）→ 写回源系统
  → 源库真变断言 → 审计含 E6 before/after 快照（audit_ref 对账 action_runs）。

同时承载 §12 验收证据：
  §12-2  端到端演示链路一条命令可自动运行（pytest 本文件即全链）；
  §12-3  三问回归：LLM 段含 cancel_order 成功（Q1/Q2）+ 已发货拒绝（Q3）；
  §12-4  审计含 before/after 快照（action_runs 快照 + audit_log 对账 + /audit 可见）；
  §12-6  SQLite-only 无外部服务（双库 SQLite 文件 + GraphStore 走 SQLite 实现
         + 无 DEEPSEEK_API_KEY 可建 app 出 schema，LLM 降级 mock）。

约定（与 P0-P4 一致）：fixtures 走 data/builder_samples/；临时库隔离；管道
in-memory runs 每测试清空；上传目录改到 tmp_path 不污染 data/。
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from data import seed_retail_source as seed
from src.agent.agent import Agent
from src.agent.provider import ChatResponse, MockProvider, ToolCall

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "builder_samples"

# seed 中的确定性样本（data/seed_retail_source.py 顶部注释，与 P4 一致）
ORDER_CONFIRMED = "ORD-1001"  # confirmed（可取消演示样本）
ORDER_SHIPPED = "ORD-2007"  # shipped（已发货拦截样本）


class P6Executor:
    """LLM 动作执行器：走 builder 动作端点 /api/v1/builder/actions/{name}/run。

    与 test_agent_e2e.RecordingExecutor 同形（记录每次调用 + 统一执行入口），
    但端点返回 E6 before/after 快照 + audit_ref（action_runs 证据面），
    让"LLM 动作 → 写回 → E6 快照审计"落在同一条链路。
    """

    def __init__(self, client: TestClient) -> None:
        self._client = client
        self.calls: list[tuple[str, dict]] = []

    def execute(
        self,
        action_name: str,
        params: dict,
        *,
        actor: str = "llm",
        actor_detail: str = "",
        request_id: str = "",
    ) -> dict:
        self.calls.append((action_name, params))
        resp = self._client.post(
            f"/api/v1/builder/actions/{action_name}/run",
            json={"params": params},
            headers={
                "X-Actor": actor,
                "X-Actor-Detail": actor_detail,
                "X-Request-ID": request_id,
            },
        )
        return resp.json()

    def search(
        self,
        object_type: str,
        filter: dict | None = None,
        page_size: int = 10,
    ) -> dict:
        query = {"page_size": page_size}
        if filter:
            query.update({k: v for k, v in filter.items()})
        resp = self._client.get(f"/objects/{object_type}", params=query)
        return resp.json()


# ----------------------------------------------------------------------
# fixtures：真实双库 + 进程内 app
# ----------------------------------------------------------------------


@pytest.fixture(scope="module")
def p6_seed_db(tmp_path_factory):
    """一次性 seed 源库（每测试拷一份，防并行竞态）。"""
    path = tmp_path_factory.mktemp("p6_seed") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def p6_env(tmp_path, p6_seed_db, monkeypatch):
    """真实 FastAPI 应用 + 独立双库（每测试一份拷贝）+ 隔离上传目录。"""
    from src.api.main import create_app
    from src.builder import datasets_repo, pipelines_repo

    source = tmp_path / "source.db"
    shutil.copy(p6_seed_db, source)
    ontology = tmp_path / "ontology.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(exist_ok=True)
    monkeypatch.setattr(datasets_repo, "DEFAULT_UPLOAD_DIR", upload_dir)
    pipelines_repo.clear_runs()  # 进程内管道 runs 隔离
    app = create_app(source_db=source, ontology_db=ontology)
    client = TestClient(app)
    with client:
        yield SimpleNamespace(client=client, source=source, ontology=ontology, app=app)


# ----------------------------------------------------------------------
# 1. §12-2 全链路 E2E（一条测试函数）
# ----------------------------------------------------------------------


class TestP6FullLinkE2E:
    """构建段 + 运行段拼接（补丁 A2）：一条测试走通 §12-2 全链。"""

    def test_full_chain_csv_to_writeback_with_snapshot_audit(self, p6_env) -> None:
        client = p6_env.client

        # ================= 构建段 =================
        # 1) CSV 上传（builder_samples 真实样本）
        csv_text = (SAMPLES / "suppliers_dirty.csv").read_text(encoding="utf-8")
        r = client.post(
            "/api/v1/builder/datasets/upload",
            files={"file": ("suppliers_dirty.csv", csv_text.encode("utf-8"), "text/csv")},
            data={"name": "p6_suppliers"},
        )
        assert r.status_code == 200, r.text
        upload = r.json()["data"]
        assert upload["kind"] == "csv" and upload["status"] == "uploaded"
        src_path = upload["source_path"]

        # 2) 管道 create -> run（A 路径：connector -> schema_infer -> output curated）
        dag = {
            "nodes": [
                {
                    "id": "read",
                    "kind": "connector",
                    "config": {"kind": "csv", "path": src_path},
                    "next": ["infer"],
                },
                {
                    "id": "infer",
                    "kind": "transform",
                    "config": {
                        "op": "schema_infer",
                        "dataset_id": "p6_suppliers",
                        "kind": "csv",
                        "source_path": src_path,
                        "pk_column": "auto",
                    },
                    "next": ["out"],
                },
                {
                    "id": "out",
                    "kind": "output",
                    "config": {"target": "curated", "dataset_id": "p6_suppliers"},
                },
            ]
        }
        r = client.post(
            "/api/v1/builder/pipelines",
            json={"name": "p6_suppliers_pl", "dag_json": dag},
        )
        assert r.status_code == 200, r.text
        r = client.post("/api/v1/builder/pipelines/p6_suppliers_pl/run")
        body = r.json()
        assert body["outcome"] == "ok", body
        assert body["data"]["final_status"] == "succeeded"
        assert body["data"]["curated_dataset_id"], "curated 未生成"

        # 3) Curated 审核：draft -> reviewed -> approved
        cur = client.get("/api/v1/builder/curated/p6_suppliers").json()["data"]
        assert cur["status"] == "draft" and cur["row_count"] == 20  # 去重后
        r = client.post("/api/v1/builder/curated/p6_suppliers/review")
        assert r.json()["data"]["status"] == "reviewed"
        r = client.post("/api/v1/builder/curated/p6_suppliers/review")
        assert r.json()["data"]["status"] == "approved"

        # 4) 自动映射 -> apply -> publish：供应商对象类型（实体一等公民）
        r = client.post(
            "/api/v1/builder/mappings/auto",
            headers={"X-Actor": "api"},
            json={
                "source_table": "suppliers_dirty",
                "source_path": str(SAMPLES / "suppliers_dirty.csv"),
            },
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["entity_class"] == "SuppliersDirty"
        assert r.json()["data"]["status"] == "draft"
        r = client.post(
            "/api/v1/builder/mappings/SuppliersDirty/apply", headers={"X-Actor": "api"}
        )
        assert r.status_code == 200, r.text
        ot_suppliers = r.json()["data"]["object_type_id"]
        r = client.post(
            f"/api/v1/builder/object-types/{ot_suppliers}/review",
            headers={"X-Actor": "api"},
        )
        assert r.status_code == 200, r.text
        r = client.post(
            f"/api/v1/builder/object-types/{ot_suppliers}/publish",
            headers={"X-Actor": "api"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["status"] == "published"

        # 5) 商品映射（FK 指向已发布的 SuppliersDirty）-> apply -> publish ot + link
        r = client.post(
            "/api/v1/builder/mappings/auto",
            headers={"X-Actor": "api"},
            json={
                "source_table": "products_ref_suppliers",
                "source_path": str(SAMPLES / "products_ref_suppliers.csv"),
                "target_table": "SuppliersDirty",  # 与已发布 object_type 名一致（apply 按名查）
                "target_path": str(SAMPLES / "suppliers_dirty.csv"),
                "target_pk": "supplier_id",
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["entity_class"] == "ProductsRefSuppliers"
        assert len(data["fk_mappings"]) >= 1  # E2 FK 检测产链
        r = client.post(
            "/api/v1/builder/mappings/ProductsRefSuppliers/apply",
            headers={"X-Actor": "api"},
        )
        assert r.status_code == 200, r.text
        apply = r.json()["data"]
        ot_products = apply["object_type_id"]
        assert apply["created_links"], f"apply 未生成 link_type: {apply}"
        # publish 商品对象类型
        r = client.post(
            f"/api/v1/builder/object-types/{ot_products}/review",
            headers={"X-Actor": "api"},
        )
        assert r.status_code == 200, r.text
        r = client.post(
            f"/api/v1/builder/object-types/{ot_products}/publish",
            headers={"X-Actor": "api"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["status"] == "published"
        # publish 全部 link_type（E4 状态机：draft -> reviewed -> published）
        published_links: set[str] = set()
        for link in apply["created_links"]:
            lt_id = link["id"]
            r = client.post(
                f"/api/v1/builder/link-types/{lt_id}/review",
                headers={"X-Actor": "api"},
            )
            assert r.status_code == 200, r.text
            r = client.post(
                f"/api/v1/builder/link-types/{lt_id}/publish",
                headers={"X-Actor": "api"},
            )
            assert r.status_code == 200, r.text
            assert r.json()["data"]["status"] == "published"
            published_links.add(r.json()["data"]["name"])

        # 6) 本体进 Registry（A1 单向流入：/meta/schema 立即可见）
        r = client.get("/meta/schema")
        assert r.status_code == 200, r.text
        schema = r.json()["data"]
        ot_names = {o["name"] for o in schema["objects"]}
        assert {"SuppliersDirty", "ProductsRefSuppliers"} <= ot_names
        lt_names = {l["name"] for l in schema["links"]}
        assert published_links <= lt_names

        # ================= 运行段（LLM 动作 -> 写回 -> 审计 E6） =================
        # LLM 用合并后的 Registry（单一事实来源 = 启动时合并，补丁 A1）
        registry = client.app.state.runtime.registry
        executor = P6Executor(client)

        # 三问 1/2：mock LLM 提议 cancel_order -> 真执行 -> 源库真变 -> 审计
        conn = sqlite3.connect(p6_env.source)
        conn.row_factory = sqlite3.Row
        before_reserved = {
            row["product_id"]: row["reserved_qty"]
            for row in conn.execute(
                "SELECT product_id, reserved_qty FROM inventory WHERE warehouse_id=?",
                (seed.MAIN_WAREHOUSE_ID,),
            )
        }
        conn.close()

        provider = MockProvider(
            responses=[
                ChatResponse(
                    tool_calls=[
                        ToolCall(
                            id="p6_c1",
                            name="cancel_order",
                            arguments={
                                "order_id": ORDER_CONFIRMED,
                                "reason": "P6 全链路验收",
                            },
                        )
                    ]
                ),
                ChatResponse(content="好的，订单 ORD-1001 已取消。"),
            ]
        )
        agent = Agent(registry=registry, provider=provider, executor=executor)
        turn = agent.run_turn("把 ORD-1001 取消，理由：P6 全链路验收")
        assert turn.reply == "好的，订单 ORD-1001 已取消。"
        assert executor.calls == [
            ("cancel_order", {"order_id": ORDER_CONFIRMED, "reason": "P6 全链路验收"})
        ]

        # 源库真变（三问 2：直查源库）+ 库存释放
        conn = sqlite3.connect(p6_env.source)
        conn.row_factory = sqlite3.Row
        assert (
            conn.execute(
                "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
            ).fetchone()["status"]
            == "cancelled"
        )
        for pid, qty in (("SKU-003", 3), ("SKU-004", 2)):
            row = conn.execute(
                "SELECT reserved_qty FROM inventory WHERE product_id=? AND warehouse_id=?",
                (pid, seed.MAIN_WAREHOUSE_ID),
            ).fetchone()
            assert row["reserved_qty"] == before_reserved[pid] - qty, f"{pid} 未释放"
        conn.close()

        # 审计（§12-4 E6）：audit_log 对账 action_runs before/after 快照 + /audit 可见
        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            audit = conn.execute(
                "SELECT * FROM audit_log WHERE action_name='cancel_order' "
                "AND outcome='applied' AND actor='llm' ORDER BY ts DESC LIMIT 1"
            ).fetchone()
            assert audit is not None, "LLM 动作必须留审计（写必有痕）"
            wb = json.loads(audit["writeback_json"])
            assert any("UPDATE orders" in w["sql"] for w in wb)
            assert all(w["rows"] >= 1 for w in wb)
            run_row = conn.execute(
                "SELECT * FROM action_runs WHERE audit_ref=?", (audit["audit_id"],)
            ).fetchone()
            assert run_row is not None, "audit_ref 必须对账到 action_runs（E6 证据面）"
            before = json.loads(run_row["before_snapshot_json"])
            after = json.loads(run_row["after_snapshot_json"])
            assert before["objects"]["order"]["status"] == "confirmed"
            assert after["records"]["Order"][ORDER_CONFIRMED]["status"] == "cancelled"
            assert (
                after["records"]["Order"][ORDER_CONFIRMED]["status"]
                != before["objects"]["order"]["status"]
            )
            assert run_row["status"] == "applied" and run_row["executed_by"] == "llm"
            audit_id = audit["audit_id"]
        r = client.get("/audit", params={"action": "cancel_order"})
        assert r.status_code == 200
        assert any(item["audit_id"] == audit_id for item in r.json()["data"]["items"])

        # 三问 3：已发货订单被拦（LLM 从错误码学习）+ 拒绝路径仍审计
        provider2 = MockProvider(
            responses=[
                ChatResponse(
                    tool_calls=[
                        ToolCall(
                            id="p6_c2",
                            name="cancel_order",
                            arguments={"order_id": ORDER_SHIPPED},
                        )
                    ]
                ),
                ChatResponse(content="ORD-2007 已发货，不能取消，建议走退款流程。"),
            ]
        )
        agent2 = Agent(registry=registry, provider=provider2, executor=executor)
        turn2 = agent2.run_turn("把 ORD-2007 取消")
        assert turn2.reply == "ORD-2007 已发货，不能取消，建议走退款流程。"
        assert executor.calls[-1] == ("cancel_order", {"order_id": ORDER_SHIPPED})
        conn = sqlite3.connect(p6_env.source)
        conn.row_factory = sqlite3.Row
        assert (
            conn.execute(
                "SELECT status FROM orders WHERE order_id=?", (ORDER_SHIPPED,)
            ).fetchone()["status"]
            == "shipped"
        )
        conn.close()
        with store.ontology_conn() as conn:
            rejected = conn.execute(
                "SELECT * FROM audit_log WHERE action_name='cancel_order' "
                "AND outcome='rejected' AND actor='llm' ORDER BY ts DESC LIMIT 1"
            ).fetchone()
            assert rejected is not None
            assert (
                rejected["error_code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
            )


# ----------------------------------------------------------------------
# 2. §12 证据补强（独立小测试）
# ----------------------------------------------------------------------


class TestSection12Evidence:
    """§12-4/6 的独立证据 + 蓝图 §11 无 key 降级（补丁 C5）。"""

    def test_sqlite_only_no_external_dependencies(self, p6_env) -> None:
        """§12-6：全链 SQLite-only、无外部服务依赖。"""
        # 1) 双库都是 SQLite 文件（magic bytes：SQLite format 3）
        for db in (p6_env.source, p6_env.ontology):
            with open(db, "rb") as f:
                assert f.read(16) == b"SQLite format 3\x00", f"{db} 不是 SQLite 文件"
        # 2) 存储适配层 GraphStore = SQLite 关系表实现（补丁 B2：Vector/Cache 已删除）
        from src.storage.graph_store import GraphStore
        from src.storage.sqlite_graph_store import SQLiteGraphStore

        assert issubclass(SQLiteGraphStore, GraphStore)
        # 3) builder 元数据 10 张表全部落本体库（A3：构建产物零污染源库）
        store = p6_env.client.app.state.runtime.store
        with store.ontology_conn() as conn:
            tables = {
                row["name"]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        assert {
            "object_types",
            "link_types",
            "datasets",
            "pipelines",
            "curated_datasets",
            "mappings",
            "extraction_tasks",
            "logic_rules",
            "action_types",
            "action_runs",
        } <= tables

    def test_app_builds_and_schema_without_llm_key(self, tmp_path, p6_seed_db, monkeypatch) -> None:
        """蓝图 §11 / 补丁 C5：无 DEEPSEEK_API_KEY 时应用构建 + 元数据全可用（LLM 降级 mock）。"""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.setenv("LLM_PROVIDER", "mock")
        from src.api.main import create_app
        from src.builder import datasets_repo

        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir(exist_ok=True)
        monkeypatch.setattr(datasets_repo, "DEFAULT_UPLOAD_DIR", upload_dir)
        source = tmp_path / "source.db"
        shutil.copy(p6_seed_db, source)
        app = create_app(source_db=source, ontology_db=tmp_path / "ontology.db")
        with TestClient(app) as client:
            r = client.get("/meta/schema")
            assert r.status_code == 200
            assert len(r.json()["data"]["objects"]) >= 8  # 内置 8 对象
            r = client.get("/api/v1/builder/health")
            assert r.json()["data"]["status"] == "ready"
        # 无 key 时 DeepSeekProvider 构造必须拒绝（证明没偷偷 fallback 真 key）
        from src.agent.provider import DeepSeekProvider

        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekProvider()


# ----------------------------------------------------------------------
# 3. E3 提取可选段（补丁 C5：MockProvider 全绿，无 key 可跑）
# ----------------------------------------------------------------------


class TestExtractionOptionalSegment:
    """extractions/run 成功路径（P3 只覆盖失败路径）：MockProvider 脚本化全绿。"""

    def test_extraction_run_succeeds_with_mock(
        self, p6_env, monkeypatch, make_mock_provider
    ) -> None:
        from src.api import builder_mapping_extraction_routes as mapping_routes

        mock = make_mock_provider("clean_two_entities")
        monkeypatch.setattr(mapping_routes, "_build_provider", lambda name: mock)
        r = p6_env.client.post(
            "/api/v1/builder/extractions/run",
            headers={"X-Actor": "api"},
            json={
                "source_path": str(SAMPLES / "supplier_memo.md"),
                "provider": "mock",
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()["data"]
        assert body["status"] == "succeeded"
        assert body["provider"] == "mock"
        assert body["result_summary"]["entity_count"] == 2
        assert body["result_summary"]["relation_count"] == 1
        assert body["validation_report"]["counts_by_severity"].get("fatal", 0) == 0
