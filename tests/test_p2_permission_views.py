"""P4 数据权限下沉测试（docs/P4-权限会话审计设计_v0.1.md §2）：metrics.db 对象级权限视图。

覆盖（对齐 §2.1/§2.2 + 任务口径）：
- create_permission_views：allow 对象建 perm_<object_type>（内容 = 物化表全列 +
  metric_id 判别列）、deny 对象不建且旧视图清除、幂等重跑、metrics.db 缺失 fail-fast；
- 视图内容：per-metric 行 = 物化表直查（对象级过滤正确）；属性级 deny 不投影到视图
  （视图全列透传，属性级裁剪仍由语义层 visible_attributes 处理）；
- 执行器 metric 路径：allow 对象走视图查询结果 = 直查物化表；对象级 deny → 拒答
  （PERMISSION_DENIED）；decide 放行但视图缺失/为空 → fail-closed 拒答（防视图旁路）；
- 兼容：allow_all 上下文（内部工具/对账）无视图也可直查物化表（行为不变）。

约束：物化用真实企业库（data/des/enterprises/hc_precision/，已生成）；权限用临时
Store（tmp_path 双库，不污染真实 ontology.db）；视图写入 metrics.db 临时副本
（每测试独立，不污染真实 metrics.db），副本 + manifest 符号链接保证 T3 守卫通过。
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import duckdb
import pytest

from src.des.config import load_config
from src.des.contract import (
    ContractExecutor,
    PermissionContext,
    PermissionDeniedError,
)
from src.des.materialize import DesMaterialization, materialize_des
from src.des.metrics import METRICS_DB, MetricRegistry, load_metrics, metric_table_name
from src.des.metrics_materialize import (
    MetricsMaterializationResult,
    materialize_metrics,
)
from src.des.permission_views import (
    PermissionViewError,
    create_permission_views,
    permission_view_name,
)
from src.ontology import build_registry
from src.ontology.registry import Registry
from src.runtime.permissions import (
    PermissionPolicy,
    PermissionService,
    PermissionSubject,
)
from src.runtime.store import Store

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "hc_precision"
ENTERPRISE_DIR = ROOT / "data" / "des" / "enterprises" / ENTERPRISE_CODE
METRICS_DB_PATH = ENTERPRISE_DIR / METRICS_DB

_CONFIG = load_config(ENTERPRISE_CODE)
_METRIC_REGISTRY = load_metrics(config=_CONFIG)


# ---------------------------------------------------------------------------
# fixtures（沿用 test_p2_chatbi.py 模式：会话级物化 + 每测试独立权限 Store / metrics 副本）
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def registry() -> Registry:
    return build_registry()


@pytest.fixture(scope="session")
def metrics() -> MetricRegistry:
    return _METRIC_REGISTRY


@pytest.fixture(scope="session")
def mz(registry: Registry) -> DesMaterialization:
    """DES 物化（DuckDB 跨库）+ 会话级 Registry；退出时关闭 DuckDB 连接。"""
    mat = materialize_des(ENTERPRISE_CODE, out_dir=ENTERPRISE_DIR, registry=registry)
    yield mat
    mat.duckdb.close()


@pytest.fixture(scope="session")
def mat_result() -> MetricsMaterializationResult:
    """物化管道跑一次（全量重建 + reconcile 全检 + 版本戳提交；幂等，~4s）。"""
    return materialize_metrics(ENTERPRISE_CODE)


@pytest.fixture
def metrics_db(tmp_path: Path, mat_result: MetricsMaterializationResult) -> Path:
    """每测试独立 metrics.db 副本（真实库同版本，T3 守卫通过；视图写副本不碰真库）。"""
    work = tmp_path / "metrics_copy"
    work.mkdir()
    shutil.copy(METRICS_DB_PATH, work / METRICS_DB)
    os.symlink(ENTERPRISE_DIR / "manifest.json", work / "manifest.json")
    return work / METRICS_DB


@pytest.fixture
def perm_service(tmp_path: Path, registry: Registry) -> PermissionService:
    """每个权限测试独立临时双库（source + ontology），绝不碰真实 data/。"""
    store = Store(tmp_path / "source.db", tmp_path / "ontology.db")
    store.migrate()
    return PermissionService(store, registry)


def _agent() -> PermissionSubject:
    return PermissionSubject(kind="agent", id="procurement_agent")


def _policy(**kw) -> PermissionPolicy:
    defaults = {
        "policy_id": "p1",
        "object_type": "Material",
        "operation": "read",
        "effect": "allow",
        "subject": _agent(),
    }
    return PermissionPolicy(**{**defaults, **kw})


def _ctx(perm_service: PermissionService) -> PermissionContext:
    return PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)


def _build_views(
    db: Path, metrics: MetricRegistry, ctx: PermissionContext
) -> dict[str, list[str]]:
    return create_permission_views(db, metrics, ctx.permission_registry, ctx.subject)


def _executor(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    db: Path,
    ctx: PermissionContext | None,
) -> ContractExecutor:
    return ContractExecutor(
        mz, registry, metrics=metrics, metrics_db=db, permission_ctx=ctx
    )


def _view_exists(db: Path, view: str) -> bool:
    conn = duckdb.connect(str(db), read_only=True)
    try:
        return (
            conn.execute(
                "SELECT 1 FROM information_schema.views "
                "WHERE table_schema='main' AND table_name=?",
                (view,),
            ).fetchone()
            is not None
        )
    finally:
        conn.close()


def _view_rows(db: Path, view: str, cols: str = "*") -> list[tuple]:
    conn = duckdb.connect(str(db), read_only=True)
    try:
        return conn.execute(f"SELECT {cols} FROM {view}").fetchall()
    finally:
        conn.close()


# ===========================================================================
# ① create_permission_views：allow 建视图 / deny 不建 / 幂等 / fail-fast
# ===========================================================================
def test_create_views_allow_object(
    metrics_db: Path, metrics: MetricRegistry, perm_service: PermissionService
) -> None:
    """allow 对象：建 perm_<object_type>，内容 = 该对象全部物化表 UNION + metric_id 判别列。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(_policy(policy_id="allow-vendor", object_type="Vendor"))
    ctx = _ctx(perm_service)
    created = _build_views(metrics_db, metrics, ctx)
    assert set(created) == {"Material", "Vendor"}
    assert set(created["Material"]) == {
        m.metric_id for m in metrics.metrics_by_object("Material")
    }
    conn = duckdb.connect(str(metrics_db), read_only=True)
    try:
        cols = [
            r[0]
            for r in conn.execute(f"DESCRIBE {permission_view_name('Material')}").fetchall()
        ]
        assert cols[0] == "metric_id"  # 判别列（查询侧过滤用，返回列显式选择不含它）
        # 视图列 = 该对象全部物化表的维度+度量列并集（全列透传，属性级归语义层）
        mat_cols: set[str] = set()
        for m in metrics.metrics_by_object("Material"):
            mat_cols.update(d.name for d in m.dimension_fields)
            mat_cols.add(m.measure.name)
        assert mat_cols <= set(cols[1:])
    finally:
        conn.close()


def test_create_views_deny_object_not_created(
    metrics_db: Path, metrics: MetricRegistry, perm_service: PermissionService
) -> None:
    """deny 对象（无 read 策略）：不建视图；撤销策略重跑后旧视图被清除（deny 不出现在视图）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(_policy(policy_id="allow-vendor", object_type="Vendor"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    assert _view_exists(metrics_db, permission_view_name("Material"))
    assert _view_exists(metrics_db, permission_view_name("Vendor"))
    # 撤销 Material 策略（对象级 deny）→ 重建 → perm_Material 被清除，perm_Vendor 保留
    perm_service.delete("allow-mat")
    created = _build_views(metrics_db, metrics, ctx)
    assert set(created) == {"Vendor"}
    assert not _view_exists(metrics_db, permission_view_name("Material"))
    assert _view_exists(metrics_db, permission_view_name("Vendor"))


def test_create_views_idempotent(
    metrics_db: Path, metrics: MetricRegistry, perm_service: PermissionService
) -> None:
    """CREATE OR REPLACE 幂等：同策略重跑不报错，视图内容逐行不变。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    before = sorted(
        _view_rows(metrics_db, permission_view_name("Material")),
        key=lambda r: tuple(str(x) for x in r),
    )
    _build_views(metrics_db, metrics, ctx)
    after = sorted(
        _view_rows(metrics_db, permission_view_name("Material")),
        key=lambda r: tuple(str(x) for x in r),
    )
    assert before == after


def test_create_views_missing_db_fails(tmp_path: Path) -> None:
    """metrics.db 缺失 → PermissionViewError（fail-fast，提示先物化）。"""
    ctx = PermissionContext.allow_all()
    with pytest.raises(PermissionViewError) as exc:
        create_permission_views(
            tmp_path / "nope.db", _METRIC_REGISTRY, ctx.permission_registry, ctx.subject
        )
    assert "metrics.db 缺失" in str(exc.value)


# ===========================================================================
# ② 视图内容 = 物化表（对象级过滤正确；属性级仍由语义层处理）
# ===========================================================================
def test_view_rows_equal_materialized(
    metrics_db: Path, metrics: MetricRegistry, perm_service: PermissionService
) -> None:
    """per-metric 视图行 = 物化表直查（列值逐行一致）；视图总行数 = 各表行数之和。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    view = permission_view_name("Material")
    conn = duckdb.connect(str(metrics_db), read_only=True)
    try:
        total = 0
        for m in metrics.metrics_by_object("Material"):
            cols = ", ".join(d.name for d in m.dimension_fields) + ", " + m.measure.name
            view_rows = conn.execute(
                f"SELECT {cols} FROM {view} WHERE metric_id='{m.metric_id}'"
            ).fetchall()
            direct = conn.execute(f"SELECT {cols} FROM {metric_table_name(m.metric_id)}").fetchall()
            assert len(view_rows) == len(direct) > 0
            assert view_rows == direct, f"视图行 ≠ 物化表直查: {m.metric_id}"
            total += len(direct)
        view_total = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
        assert view_total == total  # UNION 无重复（UNION ALL，不吞行）
    finally:
        conn.close()


def test_attribute_deny_semantic_layer_not_view(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """属性级 deny：视图全列透传（含 matnr），语义层 visible_attributes 裁剪/fail-closed。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(
        _policy(
            policy_id="deny-matnr",
            effect="deny",
            scope="attribute",
            attributes=["matnr"],
        )
    )
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    # 视图仍含 matnr 列（对象级下沉不投影属性级；属性级归语义层标注）
    conn = duckdb.connect(str(metrics_db), read_only=True)
    try:
        cols = [
            r[0]
            for r in conn.execute(f"DESCRIBE {permission_view_name('Material')}").fetchall()
        ]
        assert "matnr" in cols
    finally:
        conn.close()
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    # 语义层：请求不可见列 → fail-closed 拒答
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(
            {
                "contract_version": "0.2",
                "metric": {
                    "metric_id": "sales_amount_by_mat_month",
                    "dimension_filters": {
                        "matnr": {"op": "eq", "value": "MAT-2026-2979-MC4"}
                    },
                },
            }
        )
    assert "matnr" in str(exc.value)
    # 语义层：不引用 matnr 的指标查询 → 通过，结果列不含 matnr
    result = ex.execute(
        {"contract_version": "0.2", "metric": {"metric_id": "mat_count_by_type_factory"}}
    )
    assert result["count"] > 0
    assert all("matnr" not in row for row in result["rows"])


# ===========================================================================
# ③ 执行器 metric 路径：视图查询 = 直查 / deny 拒答 / 视图缺失·为空 fail-closed
# ===========================================================================
def _sales_contract(matnr: str) -> dict:
    return {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "sales_amount_by_mat_month",
            "dimension_filters": {"matnr": {"op": "eq", "value": matnr}},
        },
    }


def _direct_sales_rows(db: Path, matnr: str) -> list[dict]:
    """物化表直查（同 _query_metric 口径：维度全列 + 度量列，ORDER BY 维度键）。"""
    conn = duckdb.connect(str(db), read_only=True)
    try:
        rows = conn.execute(
            "SELECT matnr, month, sales_amount FROM metric_sales_amount_by_mat_month "
            "WHERE matnr=? ORDER BY matnr, month",
            [matnr],
        ).fetchall()
    finally:
        conn.close()
    return [dict(zip(("matnr", "month", "sales_amount"), row)) for row in rows]


def test_executor_allow_object_queries_view(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """allow 对象走视图查询：结果 = 直查物化表（行为一致），判别列不外泄。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    conn = duckdb.connect(str(metrics_db), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    result = ex.execute(_sales_contract(matnr))
    expected = _direct_sales_rows(metrics_db, matnr)
    assert result["count"] == len(expected) > 0
    assert result["rows"] == expected  # 视图查询与直查逐行精确相等
    assert set(result["rows"][0]) == {"matnr", "month", "sales_amount"}


def test_executor_group_by_through_view(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """有 group_by 走视图：物化表子集重聚合结果 = 直查（metric_id 过滤不串表）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    result = ex.execute(
        {
            "contract_version": "0.2",
            "metric": {"metric_id": "sales_amount_by_mat_month", "group_by": ["month"]},
        }
    )
    conn = duckdb.connect(str(metrics_db), read_only=True)
    try:
        direct = [
            dict(zip(("month", "sales_amount"), row))
            for row in conn.execute(
                "SELECT month, SUM(sales_amount) AS sales_amount "
                "FROM metric_sales_amount_by_mat_month GROUP BY month ORDER BY month"
            ).fetchall()
        ]
    finally:
        conn.close()
    assert result["count"] == len(direct) > 0
    assert result["rows"] == direct


def test_executor_deny_object_fail_closed(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """对象级 deny（无 read 策略）：metric 查询 → PermissionDeniedError（PERMISSION_DENIED）。"""
    perm_service.create(_policy(policy_id="allow-vendor", object_type="Vendor"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(
            {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month"}}
        )
    assert exc.value.code == "PERMISSION_DENIED"


def test_executor_view_missing_fail_closed(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """decide 放行但视图缺失（策略变更后未重建）→ fail-closed 拒答（防视图旁路直查）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    # 故意不建视图（模拟调用方未重建）——对象级强制不允许回落直查物化表
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(
            {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month"}}
        )
    assert exc.value.code == "PERMISSION_DENIED"
    assert "视图缺失" in str(exc.value)


def test_executor_view_empty_fail_closed(
    metrics_db: Path,
    metrics: MetricRegistry,
    perm_service: PermissionService,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """视图存在但为空（异常态）→ fail-closed 拒答（对象级 deny 语义不放过空视图）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = _ctx(perm_service)
    _build_views(metrics_db, metrics, ctx)
    # 人为把视图置空（WHERE FALSE），模拟对象无数据/异常态
    conn = duckdb.connect(str(metrics_db))
    try:
        conn.execute(
            f"CREATE OR REPLACE VIEW {permission_view_name('Material')} "
            "AS SELECT 'x' AS metric_id, 1 AS c WHERE FALSE"
        )
    finally:
        conn.close()
    ex = _executor(mz, registry, metrics, metrics_db, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(
            {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month"}}
        )
    assert exc.value.code == "PERMISSION_DENIED"
    assert "视图为空" in str(exc.value)


def test_executor_allow_all_direct_no_views_needed(
    metrics_db: Path,
    metrics: MetricRegistry,
    mz: DesMaterialization,
    registry: Registry,
) -> None:
    """兼容：allow_all 上下文（内部工具/对账）无视图也可直查物化表（行为不变）。"""
    ex = _executor(mz, registry, metrics, metrics_db, PermissionContext.allow_all())
    result = ex.execute(
        {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_mat_month", "topN": 3}}
    )
    assert 0 < result["count"] <= 3
    assert not _view_exists(metrics_db, permission_view_name("Material"))
