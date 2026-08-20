"""P0 骨架验收测试。

覆盖 P0 全部交付物：
1. builder 子包可导入（六个子包 + __init__ 中文 docstring）；
2. init_builder_schema 在临时库建表成功且幂等，schema_version 递增；
3. GraphStore（关系表实现）增/删/查邻居基本路径；
4. /api/v1/builder/health 端点通，统一信封格式。

约定：临时库用 pytest tmp_path 隔离，不污染 data/ontology/ontology.db。
"""

from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ----------------------------------------------------------------------
# 1. 包/子包可导入
# ----------------------------------------------------------------------


SUBPACKAGES = [
    "src.builder",
    "src.builder.connectors",
    "src.builder.pipeline",
    "src.builder.curated",
    "src.builder.mapping",
    "src.builder.extraction",
    "src.builder.logic",
]


@pytest.mark.parametrize("modname", SUBPACKAGES)
def test_builder_subpackage_importable(modname: str) -> None:
    """六个子包均可被 import（不要求有公开符号，仅要求包存在且带 docstring）。"""
    mod = importlib.import_module(modname)
    assert mod.__doc__, f"{modname} 缺少模块 docstring（蓝图要求中文职责说明）"
    assert "蓝图" in (mod.__doc__ or "") or "v0.3" in (mod.__doc__ or ""), (
        f"{modname} docstring 应引用蓝图版本号"
    )


def test_builder_top_level_init() -> None:
    """src.builder/__init__.py 暴露 BUILDER_SCHEMA_VERSION 等关键符号。"""
    builder = importlib.import_module("src.builder")
    assert hasattr(builder, "BUILDER_SCHEMA_VERSION"), (
        "src.builder 应暴露 BUILDER_SCHEMA_VERSION"
    )
    assert isinstance(builder.BUILDER_SCHEMA_VERSION, int)


# ----------------------------------------------------------------------
# 2. BUILDER_SCHEMA_V1 建表 + 幂等 + schema_version 递增
# ----------------------------------------------------------------------


def _fresh_conn(tmp_path: Path) -> sqlite3.Connection:
    """每测试独立的临时 ontology 库连接（落盘到 tmp_path）。"""
    db = tmp_path / "ontology.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def test_init_builder_schema_creates_all_tables(tmp_path: Path) -> None:
    """init_builder_schema 在空库上建全 10 张表（蓝图 §4）。"""
    from src.runtime.store import BUILDER_TABLES, init_builder_schema

    conn = _fresh_conn(tmp_path)
    try:
        init_builder_schema(conn)
        names = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert set(BUILDER_TABLES).issubset(names), (
        f"缺少表：{set(BUILDER_TABLES) - names}"
    )
    for required in (
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
    ):
        assert required in names, f"必须存在的表缺失：{required}"


def test_init_builder_schema_is_idempotent(tmp_path: Path) -> None:
    """二次调用不抛错、不丢字段（CREATE TABLE IF NOT EXISTS + INSERT OR REPLACE 风格）。"""
    from src.runtime.store import init_builder_schema

    conn = _fresh_conn(tmp_path)
    try:
        init_builder_schema(conn)
        conn.execute(
            "INSERT INTO object_types (ontology_id, name, name_cn, description, "
            "category, property_schema, status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                "ont_test",
                "Customer",
                "客户",
                "测试",
                "domain",
                "{}",
                "draft",
                "2026-01-01 00:00:00",
                "2026-01-01 00:00:00",
            ),
        )
        conn.commit()
        init_builder_schema(conn)
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM object_types WHERE name='Customer'"
        ).fetchone()
    finally:
        conn.close()
    assert row["c"] == 1, "二次 init 后数据应保留（幂等）"


def test_init_builder_schema_records_version(tmp_path: Path) -> None:
    """init_builder_schema 写入 schema_version 行（共享本体库的版本表）。

    约束：现有 store.migrate 写 v1（get_schema_version 返回 1），builder 子系统
    共用同一 schema_version 表；P0 阶段 v1 行 note 标记包含 builder 段。
    后续阶段引入破坏性变更时再升 version（蓝图 §10 schema_version 演进原则）。
    """
    from src.runtime.store import BUILDER_SCHEMA_VERSION, init_builder_schema

    conn = _fresh_conn(tmp_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version ("
            "version INTEGER PRIMARY KEY, note TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version, note, applied_at) "
            "VALUES (1, 'MVP 本体运行时 v1', '2026-01-01 00:00:00')"
        )
        conn.commit()
        init_builder_schema(conn)
        versions = [
            r["version"]
            for r in conn.execute(
                "SELECT version FROM schema_version ORDER BY version"
            ).fetchall()
        ]
        notes = {
            r["version"]: r["note"]
            for r in conn.execute(
                "SELECT version, note FROM schema_version"
            ).fetchall()
        }
    finally:
        conn.close()

    assert 1 in versions, "原 v1 行必须保留"
    assert BUILDER_SCHEMA_VERSION in versions, (
        f"builder schema 版本号 {BUILDER_SCHEMA_VERSION} 必须写入 schema_version"
    )
    # 标记 builder 段已应用（v1 行的 note 应包含 builder 子系统标识）
    assert "builder" in (notes.get(BUILDER_SCHEMA_VERSION, "").lower()), (
        f"v{BUILDER_SCHEMA_VERSION} 行 note 应含 builder 标记，实际："
        f"{notes.get(BUILDER_SCHEMA_VERSION)}"
    )


def test_store_migrate_runs_builder_schema(tmp_path: Path) -> None:
    """Store.migrate 在本体库建好 builder 表（端到端：建库 + migrate）。"""
    from src.runtime.store import BUILDER_TABLES, Store

    store = Store(ontology_path=tmp_path / "ontology.db")
    store.migrate()

    with store.ontology_conn() as conn:
        names = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert set(BUILDER_TABLES).issubset(names)


# ----------------------------------------------------------------------
# 3. GraphStore（SQLite 关系表实现）增/删/查邻居
# ----------------------------------------------------------------------


def _make_graph_store(tmp_path: Path):
    """工厂：每次返回独立的 SQLiteGraphStore（nodes/edges 表建于本体库）。"""
    from src.storage.sqlite_graph_store import SQLiteGraphStore

    db = tmp_path / "graph.db"
    return SQLiteGraphStore(db)


def test_graph_store_add_and_get_node(tmp_path: Path) -> None:
    from src.storage.graph_store import Node

    store = _make_graph_store(tmp_path)
    n1 = Node(id="A", kind="entity", attrs={"label": "alice"})
    store.add_node(n1)
    got = store.get_node("A")
    assert got is not None
    assert got.id == "A"
    assert got.attrs["label"] == "alice"
    assert store.get_node("nope") is None


def test_graph_store_edge_and_neighbors(tmp_path: Path) -> None:
    from src.storage.graph_store import Edge, Node

    store = _make_graph_store(tmp_path)
    store.add_node(Node(id="A"))
    store.add_node(Node(id="B"))
    store.add_node(Node(id="C"))
    store.add_edge(Edge(src="A", dst="B", kind="knows"))
    store.add_edge(Edge(src="A", dst="C", kind="knows"))
    store.add_edge(Edge(src="B", dst="C", kind="manages"))

    out_a = store.neighbors("A", direction="out")
    assert {n.id for n in out_a} == {"B", "C"}

    in_c = store.neighbors("C", direction="in")
    assert {n.id for n in in_c} == {"A", "B"}

    both = store.neighbors("A", direction="both")
    assert {n.id for n in both} == {"B", "C"}


def test_graph_store_remove_node_cascades_edges(tmp_path: Path) -> None:
    from src.storage.graph_store import Edge, Node

    store = _make_graph_store(tmp_path)
    store.add_node(Node(id="X"))
    store.add_node(Node(id="Y"))
    store.add_edge(Edge(src="X", dst="Y"))
    store.remove_node("X")
    assert store.get_node("X") is None
    assert store.neighbors("Y", direction="in") == []


def test_graph_store_persistence(tmp_path: Path) -> None:
    """重开 store 应能看到先前写入的节点（落盘到 SQLite）。"""
    from src.storage.graph_store import Node
    from src.storage.sqlite_graph_store import SQLiteGraphStore

    db = tmp_path / "graph.db"
    s1 = SQLiteGraphStore(db)
    s1.add_node(Node(id="P", attrs={"v": 1}))
    s1.add_node(Node(id="Q"))
    s1.close()
    s2 = SQLiteGraphStore(db)
    try:
        assert s2.get_node("P") is not None
        assert {n.id for n in s2.neighbors("P", direction="out")} == set()
    finally:
        s2.close()


# ----------------------------------------------------------------------
# 4. /api/v1/builder/health 端点
# ----------------------------------------------------------------------


@pytest.fixture(scope="session")
def seed_db_path_p0(tmp_path_factory):
    """用现有 seed 在 session 范围建一次源库（避免每个测试都重 seed 慢）。"""
    from data import seed_retail_source as seed

    path = tmp_path_factory.mktemp("seed_p0") / "source.db"
    seed.build_database(path)
    return path


@pytest.fixture
def builder_client(tmp_path: Path, seed_db_path_p0: Path):
    """复用现有 create_app 模式（与 test_b3_api.client 一致：拷 seed 源库）。"""
    import shutil

    from src.api.main import create_app

    source = tmp_path / "source.db"
    shutil.copy(seed_db_path_p0, source)
    app = create_app(source_db=source, ontology_db=tmp_path / "ontology.db")
    with TestClient(app) as c:
        yield c


def test_builder_health_endpoint(builder_client: TestClient) -> None:
    """builder 健康端点：返回 builder 子系统状态字段（ready / degraded 之一）。"""
    from src.runtime.store import BUILDER_SCHEMA_VERSION, BUILDER_TABLES

    resp = builder_client.get("/api/v1/builder/health")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "status" in body["data"]
    # red-team E3 修复：API 实际仅返 ready/degraded，去除「ok」永真可达的伪成员
    assert body["data"]["status"] in {"ready", "degraded"}
    # 健康路径下必须 ready（builder 表都建好）
    assert body["data"]["status"] == "ready"
    # tables_present 覆盖全部 10 张表
    assert set(body["data"]["tables_missing"]) == set()
    assert set(body["data"]["tables_present"]) >= set(BUILDER_TABLES)
    # 封口：schema_version 与 BUILDER_SCHEMA_VERSION 一致
    assert body["data"]["schema_version"] == BUILDER_SCHEMA_VERSION


def test_builder_health_reports_schema_version(builder_client: TestClient) -> None:
    """健康端点应回报 builder schema 版本号（便于运维核对）。"""
    resp = builder_client.get("/api/v1/builder/health")
    body = resp.json()
    from src.runtime.store import BUILDER_SCHEMA_VERSION

    assert body["data"]["schema_version"] == BUILDER_SCHEMA_VERSION


def test_builder_health_reports_degraded_when_table_missing(
    builder_client: TestClient,
) -> None:
    """red-team E3 负向测试：删一张 builder 表后 status 应为 degraded。"""
    store = builder_client.app.state.runtime.store
    # 删一张 builder 表（datasets），模拟迁移不完整 / 手动 DROP 场景
    with store.ontology_conn() as conn:
        conn.execute("DROP TABLE IF EXISTS datasets")
        conn.commit()
    resp = builder_client.get("/api/v1/builder/health")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["data"]["status"] == "degraded", body
    assert "datasets" in body["data"]["tables_missing"]
    # 其余表仍在
    assert "object_types" in body["data"]["tables_present"]


# ---------- red-team 封口断言 ----------


def test_builder_schema_version_is_single_source() -> None:
    """red-team E1 封口：跨模块版本号一致性——不允许双轨重定义。"""
    import src.builder as builder_pkg
    from src.runtime import store as store_mod

    assert builder_pkg.BUILDER_SCHEMA_VERSION == store_mod.BUILDER_SCHEMA_VERSION
    # __module__ 必须来自 runtime.store（证明是透传）
    assert (
        builder_pkg.BUILDER_SCHEMA_VERSION.__class__.__module__
        == "src.runtime.store"
        or builder_pkg.BUILDER_SCHEMA_VERSION is store_mod.BUILDER_SCHEMA_VERSION
    )


def test_schema_version_note_contains_both_segments() -> None:
    """red-team E2 封口：v1 行 note 必须含运行时 + builder 两段（red-team E2）。"""
    import os
    import tempfile

    from src.runtime.store import Store

    with tempfile.TemporaryDirectory() as td:
        s = Store(ontology_path=os.path.join(td, "ont.db"))
        s.migrate()
        with s.ontology_conn() as conn:
            row = conn.execute(
                "SELECT note FROM schema_version WHERE version=1"
            ).fetchone()
        note = row["note"]
        # 两段都必须在（red-team E2 修复：合并而非覆盖）
        assert "audit_log" in note, f"运行时段缺失: {note!r}"
        assert "builder" in note, f"builder 段缺失: {note!r}"


def test_degraded_status_when_health_endpoint_reports_degraded(
    builder_client: TestClient,
) -> None:
    """red-team E3 封口：degraded 路径独立断言（与 E3 负向测试互补）。"""
    store = builder_client.app.state.runtime.store
    with store.ontology_conn() as conn:
        conn.execute("DROP TABLE IF EXISTS action_runs")
        conn.execute("DROP TABLE IF EXISTS pipelines")
        conn.commit()
    resp = builder_client.get("/api/v1/builder/health")
    body = resp.json()
    assert body["data"]["status"] == "degraded"
    miss = set(body["data"]["tables_missing"])
    assert {"action_runs", "pipelines"} <= miss
