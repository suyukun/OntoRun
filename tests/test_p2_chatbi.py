"""P2 ChatBI 门禁测试（docs/P2-ChatBI闭环设计_v0.1.md §6 五门禁 + §1-3 可机验断言）。

覆盖（对齐 P2 五门禁 + 上篇 §1/§2/§3 断言清单）：
- 指标注册表（§1.2/§1.3）：load_metrics 26 条 + M1-M9 校验 fail-fast（未知对象/未知来源表/
  未知列/非法聚合/类型不兼容/粒度重复/重复 metric_id/命名与 transform/M9 可选扩展字段拒绝）；
- 物化 + C4 reconcile（§2.1-§2.3）：materialize_metrics 跑通（26 表行数>0 + 逐指标 reconcile
  全绿 + 版本戳提交）、reconcile_metrics 全 diff=0（R1）、check_metrics_version 漂移检出（R3/T3）；
- 契约 v0.2 metric 执行（§3.1/§3.2）：sales_amount_by_mat_month + 维度过滤返回行数与值
  与源库直算一致；非法 metric_id/未知维度键 fail-closed；T3 版本守卫漂移拒答；V5 结果护栏；
- v0.1 兼容（§6 补充断言）：DQ-01（round(N×rate) 条）、Q2/Q3 原样可执行且结果一致；
- 读侧权限（§3.3）：无 ctx 兼容 / 无策略 fail-closed / allow 通过 / 属性级 deny fail-closed；
- 性能冒烟（§4.3 P95≤500ms，宽松判据避免 CI 抖动，标记 slow）。

约束：物化/查询用真实企业库（data/des/enterprises/hc_precision/，已生成），权限用临时
Store（tmp_path 双库，不污染真实 ontology.db）；物化在会话级跑一次（全量重建幂等，实测 ~4s，
与设计 §2.5 量级一致）。
"""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

import duckdb
import pytest

from src.des.config import load_config
from src.des.contract import (
    DQ01_CONTRACT,
    MAX_TOP_N,
    ContractError,
    ContractExecutor,
    PermissionContext,
    PermissionDeniedError,
    validate_contract,
)
from src.des.materialize import DesMaterialization, materialize_des, rows_as_dicts
from src.des.metrics import METRICS_DB, MetricError, MetricRegistry, load_metrics
from src.des.metrics_materialize import (
    MetricMaterializeError,
    MetricsMaterializationResult,
    check_metrics_version,
    materialize_metrics,
    reconcile_inventory_r2,
    reconcile_metrics,
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

# 期望值全部从生效配置派生（单一事实来源 = 配置，禁硬编码）
_CONFIG = load_config(ENTERPRISE_CODE)
_MARA_ROWS = _CONFIG["enterprise"]["systems"]["erp"]["tables"]["MARA"]["row_count"]
_MULTI_RATE = _CONFIG["injection"]["multi_code"]["rate"]
EXPECTED_MULTI = round(_MARA_ROWS * _MULTI_RATE)  # DQ-01 = round(N×rate)（当前配置 = 1200）
# 指标集单一事实来源 = 注册表（当前 26 指标，禁硬编码 15）：计数与 id 集均从注册表派生，
# 后续增补指标免手改断言（对齐「期望值全部从生效配置派生」纪律）
_METRIC_REGISTRY = load_metrics(config=_CONFIG)
EXPECTED_METRIC_COUNT = len(_METRIC_REGISTRY.metrics)
_METRIC_IDS = {m.metric_id for m in _METRIC_REGISTRY.metrics}


# ---------------------------------------------------------------------------
# fixtures / 工具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def registry() -> Registry:
    return build_registry()


@pytest.fixture(scope="session")
def cfg() -> dict:
    return load_config(ENTERPRISE_CODE)


@pytest.fixture(scope="session")
def metrics(cfg: dict) -> MetricRegistry:
    return load_metrics(config=cfg)


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


@pytest.fixture(scope="session")
def executor(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    mat_result: MetricsMaterializationResult,
) -> ContractExecutor:
    """显式 allow-all 权限上下文执行器（功能路径共用；red-team P1-1：无 ctx = 默认 deny，
    功能测试必须显式放行；metrics_db 为 Path，勿传 str）。"""
    return ContractExecutor(
        mz,
        registry,
        metrics=metrics,
        metrics_db=METRICS_DB_PATH,
        permission_ctx=PermissionContext.allow_all(),
    )


@pytest.fixture
def perm_service(tmp_path, registry: Registry) -> PermissionService:
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


def _executor_with_perm(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    ctx: PermissionContext | None,
) -> ContractExecutor:
    """构造带读侧权限上下文的执行器（None = 默认 deny，fail-closed；red-team P1-1）。"""
    return ContractExecutor(
        mz, registry, metrics=metrics, metrics_db=METRICS_DB_PATH, permission_ctx=ctx
    )


def _source_direct_sales(matnr: str) -> list[dict]:
    """源库直算（同 definition 同 join）：VBAP↔VBAK 按 VBELN 关联 + substr 月（§2.3 R3 口径）。"""
    conn = duckdb.connect(str(ENTERPRISE_DIR / "erp.db"), read_only=True)
    try:
        rows = conn.execute(
            "SELECT vbap.MATNR AS matnr, substr(vbak.AUDAT, 1, 7) AS month, "
            "SUM(vbap.NETWR) AS sales_amount FROM VBAP vbap "
            "JOIN VBAK vbak ON vbap.VBELN = vbak.VBELN WHERE vbap.MATNR = ? "
            "GROUP BY 1, 2 ORDER BY 1, 2",
            [matnr],
        ).fetchall()
    finally:
        conn.close()
    return [dict(zip(("matnr", "month", "sales_amount"), row)) for row in rows]


# ===========================================================================
# ① 指标注册表（设计 §1.2/§1.3）
# ===========================================================================
def test_metric_registry_loads_expected() -> None:
    """load_metrics：默认注册表 YAML 加载全部指标（当前 26），metric_id 全局唯一（M7）。"""
    reg = load_metrics()
    ids = {m.metric_id for m in reg.metrics}
    assert len(reg.metrics) == EXPECTED_METRIC_COUNT
    assert ids == _METRIC_IDS


def test_metrics_by_object_index(metrics: MetricRegistry) -> None:
    """§1.4 对象 → 指标索引：Material 指向 7 个；4 个主体对象全部已注册（解除 planned，M1 前置）。"""
    assert len(metrics.metrics_by_object("Material")) == 11
    assert len(metrics.metrics_by_object("ErpCustomer")) == 5
    assert len(metrics.metrics_by_object("Vendor")) == 3
    assert len(metrics.metrics_by_object("InventoryLocation")) == 2
    assert len(metrics.metrics_by_object("FinanceEntry")) == 5
    # 26 指标全部挂载到 5 个已注册主体对象（Jack 2026-08-21 拍板，无 pending 待补录）
    subject = ("Material", "ErpCustomer", "Vendor", "InventoryLocation", "FinanceEntry")
    assert sum(len(metrics.metrics_by_object(o)) for o in subject) == EXPECTED_METRIC_COUNT
    assert not hasattr(metrics, "pending_registration")  # planned 概念已移除


def _base_metric() -> dict:
    return {
        "metric_id": "test_metric",
        "object_type": "Material",
        "dimension_fields": [{"name": "matnr", "source": "VBAP.MATNR"}],
        "measure": {"name": "amt", "source": "VBAP.NETWR"},
        "agg_function": "sum",
        "definition": "测试指标口径",
        "source_tables": ["erp.VBAP"],
    }


def _load_single(metric: dict) -> MetricRegistry:
    """写单条注册表 YAML 到临时文件并加载（M1-M7 fail-fast 探针）。"""
    import tempfile

    path = Path(tempfile.mktemp(suffix=".yaml"))
    try:
        path.write_text(
            __import__("yaml").safe_dump({"metrics": [metric]}), encoding="utf-8"
        )
        return load_metrics(path, config=load_config(ENTERPRISE_CODE))
    finally:
        path.unlink()


@pytest.mark.parametrize(
    "mutate, expect",
    [
        ({"object_type": "GhostObject"}, "M1"),  # M1 主体对象白名单
        ({"source_tables": ["erp.NOPE"]}, "M2"),  # M2 来源表白名单
        (
            {"dimension_fields": [{"name": "matnr", "source": "VBAP.NOPE"}]},
            "M3",  # M3 维度列存在
        ),
        ({"agg_function": "median"}, "M4"),  # M4 聚合函数合法
        (
            {
                "agg_function": "sum",
                "measure": {"name": "x", "source": "VBAP.MATNR"},
            },
            "M5",  # M5 sum 要求数值列
        ),
        (
            {"measure": {"name": "x", "source": "*"}, "agg_function": "sum"},
            "M5",  # M5 '*' 仅 count/count_distinct
        ),
        ({"dimension_fields": []}, "M6"),  # M6 粒度确定性：非空
        (
            {
                "dimension_fields": [
                    {"name": "matnr", "source": "VBAP.MATNR"},
                    {"name": "matnr", "source": "VBAK.AUDAT"},
                ],
                "source_tables": ["erp.VBAP", "erp.VBAK"],
            },
            "M6",  # M6 维度名重复
        ),
        (
            {"dimension_fields": [{"name": "matnr", "source": "VBAP.MATNR", "transform": "evil(1,2)"}]},
            "M8",  # M8 transform 函数名白名单（P2-8 防注入面）
        ),
        (
            {"dimension_fields": [{"name": "matnr", "source": "VBAP.MATNR", "transform": "substr(1;7)"}]},
            "M8",  # M8 transform 参数须数字/纯逗号分隔
        ),
        (
            {"dimension_fields": [{"name": "Bad-Name", "source": "VBAP.MATNR"}]},
            "M8",  # M8 dimension name 须 snake_case
        ),
        (
            {"measure": {"name": "Bad-Name", "source": "VBAP.NETWR"}},
            "M8",  # M8 measure name 须 snake_case
        ),
    ],
    ids=[
        "m1_unknown_object",
        "m2_unknown_table",
        "m3_unknown_column",
        "m4_unknown_agg",
        "m5_sum_on_text",
        "m5_star_non_count",
        "m6_empty_dims",
        "m6_dup_dim_name",
        "m8_bad_transform_func",
        "m8_bad_transform_args",
        "m8_bad_dim_name",
        "m8_bad_measure_name",
    ],
)
def test_metric_validation_rejects(mutate: dict, expect: str) -> None:
    """M1-M6 违规指标：load_metrics fail-fast 抛 MetricError 且消息含对应规则号。"""
    bad = _base_metric()
    bad.update(mutate)
    with pytest.raises(MetricError) as exc:
        _load_single(bad)
    assert expect in str(exc.value), f"缺预期规则 {expect}: {exc.value}"


def test_metric_validation_grain_duplicate() -> None:
    """M6 粒度重复（同 对象×维度×度量×聚合，不同 metric_id）→ 物化行歧义拒绝。"""
    second = _base_metric()
    second["metric_id"] = "test_metric_2"
    import tempfile

    path = Path(tempfile.mktemp(suffix=".yaml"))
    try:
        path.write_text(
            __import__("yaml").safe_dump(
                {"metrics": [_base_metric(), second]}
            ),
            encoding="utf-8",
        )
        with pytest.raises(MetricError) as exc:
            load_metrics(path, config=load_config(ENTERPRISE_CODE))
        assert "M6" in str(exc.value) or "粒度重复" in str(exc.value)
    finally:
        path.unlink()


def test_metric_validation_m7_duplicate_id() -> None:
    """M7 metric_id 重复（同 id 异粒度）→ 拒绝，消息含 M7。"""
    second = _base_metric()
    second["measure"] = {"name": "qty", "source": "VBAP.KWMENG"}  # 异粒度避免 M6 先发
    import tempfile

    path = Path(tempfile.mktemp(suffix=".yaml"))
    try:
        path.write_text(
            __import__("yaml").safe_dump(
                {"metrics": [_base_metric(), second]}
            ),
            encoding="utf-8",
        )
        with pytest.raises(MetricError) as exc:
            load_metrics(path, config=load_config(ENTERPRISE_CODE))
        assert "M7" in str(exc.value) and "重复" in str(exc.value)
    finally:
        path.unlink()


# ===========================================================================
# ② 物化 + C4 reconcile（设计 §2）
# ===========================================================================
def test_materialize_metrics_full(mat_result: MetricsMaterializationResult) -> None:
    """materialize_metrics 跑通：metrics.db 生成、26 表行数>0、逐指标 reconcile 全绿、版本戳提交。"""
    assert mat_result.metrics_db_path.is_file()
    assert set(mat_result.tables) == _METRIC_IDS
    assert all(rows > 0 for rows in mat_result.tables.values())
    assert len(mat_result.reconciles) == EXPECTED_METRIC_COUNT
    assert all(r.ok for r in mat_result.reconciles), [
        f"第 {i} 个指标 reconcile 未全绿: {r.differences}"
        for i, r in enumerate(mat_result.reconciles)
        if not r.ok
    ]
    man = json.loads((ENTERPRISE_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert mat_result.data_version == man["data_version"]
    assert mat_result.config_sha256 == man["config_sha256"]
    assert mat_result.refresh_mode == "full"


def test_reconcile_metrics_all_diff_zero(
    mat_result: MetricsMaterializationResult,
) -> None:
    """R1 reconcile 全检：每指标 物化 vs 源库直算 逐行 diff=0（ok + 行数一致 + 差异空）。"""
    results = reconcile_metrics(ENTERPRISE_CODE)
    assert len(results) == EXPECTED_METRIC_COUNT
    for r in results:
        assert r.ok is True, f"reconcile 未全绿: {r.differences}"
        assert r.expected_count == r.actual_count
        assert r.differences == []


def test_reconcile_inventory_r2_diff_zero(mat_result: MetricsMaterializationResult) -> None:
    """P2-3 R2 物化层跨指标自洽：C1 库存账面 vs C3 流水净变，按地点 diff=0（升级自 D10）。

    R1 同源 SQL 检不出系统性口径错误，R2 基于 metrics.db 物化表做第二道防线（red-team P2-3）。
    """
    r2 = reconcile_inventory_r2(ENTERPRISE_CODE)
    assert r2.ok is True, f"R2 未全绿: {r2.differences}"
    assert r2.differences == []
    assert r2.expected_count > 0 and r2.actual_count == r2.expected_count


def test_reconcile_detects_meta_row_count_mismatch(mat_result, tmp_path) -> None:
    """P2-3 ②：篡改 metric_meta.row_count → reconcile 检出「物化表行数 ≠ meta.row_count」。"""
    work = tmp_path / "meta_tamper"
    work.mkdir()
    shutil.copy(METRICS_DB_PATH, work / METRICS_DB)
    for name in ("erp.db", "mes.db", "wms.db", "scm.db", "fin.db", "manifest.json"):
        os.symlink(ENTERPRISE_DIR / name, work / name)
    con = duckdb.connect(str(work / METRICS_DB))
    try:
        con.execute(
            "UPDATE metric_meta SET row_count = 999 "
            "WHERE metric_id='sales_amount_by_mat_month'"
        )
    finally:
        con.close()
    results = reconcile_metrics(ENTERPRISE_CODE, out_dir=work)
    bad = [r for r in results if not r.ok]
    assert bad, "篡改 meta.row_count 后 reconcile 应检出（物化表行数 ≠ meta.row_count）"
    assert any("metric_meta.row_count" in d for d in bad[0].differences)


def test_check_metrics_version_ok(
    mat_result: MetricsMaterializationResult,
) -> None:
    """T3 版本守卫：全绿时返回全部指标摘要（当前 26），data_version/config_sha256 与 manifest 一致。"""
    summary = check_metrics_version(ENTERPRISE_CODE)
    man = json.loads((ENTERPRISE_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert len(summary["metrics"]) == EXPECTED_METRIC_COUNT
    assert summary["data_version"] == man["data_version"]
    assert summary["config_sha256"] == man["config_sha256"]
    assert all(m["row_count"] > 0 for m in summary["metrics"])


def test_check_metrics_version_drift(tmp_path) -> None:
    """R3 版本守卫漂移：改 manifest.data_version（模拟源变更未刷新）→ MetricMaterializeError（fail-closed）。"""
    drift_dir = tmp_path / "drift"
    drift_dir.mkdir()
    shutil.copy(METRICS_DB_PATH, drift_dir / METRICS_DB)
    man = json.loads((ENTERPRISE_DIR / "manifest.json").read_text(encoding="utf-8"))
    man["data_version"] = "DRIFT-999"
    with open(drift_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False)
    with pytest.raises(MetricMaterializeError) as exc:
        check_metrics_version(ENTERPRISE_CODE, out_dir=drift_dir)
    assert "漂移" in str(exc.value) and "T3" in str(exc.value)


def test_t3_guard_rejects_drift(
    mz: DesMaterialization, registry: Registry, metrics: MetricRegistry, tmp_path
) -> None:
    """T3 查询侧版本守卫：契约执行器读漂移 metrics.db → ContractError 拒答（fail-closed）。"""
    drift_dir = tmp_path / "drift_guard"
    drift_dir.mkdir()
    shutil.copy(METRICS_DB_PATH, drift_dir / METRICS_DB)
    man = json.loads((ENTERPRISE_DIR / "manifest.json").read_text(encoding="utf-8"))
    man["data_version"] = "DRIFT-999"
    with open(drift_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False)
    ex = ContractExecutor(
        mz,
        registry,
        metrics=metrics,
        metrics_db=drift_dir / METRICS_DB,
        permission_ctx=PermissionContext.allow_all(),
    )
    contract = {
        "contract_version": "0.2",
        "metric": {"metric_id": "sales_amount_by_mat_month"},
    }
    with pytest.raises(ContractError) as exc:
        ex.execute(contract)
    assert "漂移" in str(exc.value) and "T3" in str(exc.value)


# ===========================================================================
# ③ 契约 v0.2 metric 执行（设计 §3.1/§3.2）
# ===========================================================================
def _sales_contract(matnr: str, **metric_kw) -> dict:
    metric = {"metric_id": "sales_amount_by_mat_month", **metric_kw}
    if matnr:
        metric["dimension_filters"] = {"matnr": {"op": "eq", "value": matnr}}
    return {"contract_version": "0.2", "metric": metric}


def test_metric_query_correct_vs_source(
    executor: ContractExecutor, metrics: MetricRegistry
) -> None:
    """metric 契约（sales_amount_by_mat_month + 维度过滤）：行数与值 = 源库直算（口径一致）。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    result = executor.execute(_sales_contract(matnr))
    expected = _source_direct_sales(matnr)
    assert result["object_type"] == "Material"
    assert result["metric_id"] == "sales_amount_by_mat_month"
    assert result["count"] == len(expected) > 0
    assert result["rows"] == expected  # 维度值 + 度量值逐行精确相等


def test_metric_query_time_range_filter(executor: ContractExecutor) -> None:
    """time_range（{from,to}）绑定日期维度 month：只返回区间内月份（substr 截断口径）。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    result = executor.execute(
        _sales_contract(
            matnr, time_range={"from": "2026-01-01", "to": "2026-12-31"}
        )
    )
    months = {row["month"] for row in result["rows"]}
    assert months, "区间内应至少返回一个月"
    assert all(m >= "2026-01" and m <= "2026-12" for m in months)
    # 全月集合严格包含区间月份（过滤生效）
    all_months = {
        row["month"]
        for row in executor.execute(_sales_contract(matnr))["rows"]
    }
    assert months <= all_months and len(months) < len(all_months)


def test_metric_query_group_by_subset(executor: ContractExecutor) -> None:
    """metric.group_by 取物化表维度子集：物化表上重聚合（不现场算），行数 = 分组键数。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    result = executor.execute(
        _sales_contract(matnr, group_by=["month"])
    )
    assert result["count"] > 0
    for row in result["rows"]:
        assert set(row) == {"month", "sales_amount"}
    expected_months = {
        r["month"] for r in _source_direct_sales(matnr)
    }
    assert {row["month"] for row in result["rows"]} == expected_months


def test_metric_count_distinct_executes(
    executor: ContractExecutor, metrics: MetricRegistry
) -> None:
    """v0.2 扩展聚合 count_distinct（D3）：purchase_order_count_by_vendor_month 可执行。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        vendor = conn.execute(
            "SELECT vendor FROM metric_purchase_order_count_by_vendor_month "
            "ORDER BY purchase_orders DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    contract = {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "purchase_order_count_by_vendor_month",
            "dimension_filters": {"vendor": {"op": "eq", "value": vendor}},
        },
    }
    assert validate_contract(contract, build_registry(), metrics) == []
    result = executor.execute(contract)
    assert result["metric_id"] == "purchase_order_count_by_vendor_month"
    assert result["count"] > 0
    assert all(row["purchase_orders"] >= 1 for row in result["rows"])


def test_metric_invalid_id_fail_closed(
    executor: ContractExecutor, registry: Registry, metrics: MetricRegistry
) -> None:
    """非法 metric_id：校验器报违规 ∧ 执行器 ContractError（fail-closed 拒答）。"""
    contract = {
        "contract_version": "0.2",
        "metric": {"metric_id": "nope_metric"},
    }
    violations = validate_contract(contract, registry, metrics)
    assert any("metric_id 不在指标注册表" in v for v in violations)
    with pytest.raises(ContractError):
        executor.execute(contract)


def test_metric_unknown_dimension_key_fail_closed(
    executor: ContractExecutor, registry: Registry, metrics: MetricRegistry
) -> None:
    """未知维度键：dimension_filters 键不在物化维度白名单 → fail-closed 拒答。"""
    contract = {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "sales_amount_by_mat_month",
            "dimension_filters": {"bogus_dim": {"op": "eq", "value": "x"}},
        },
    }
    violations = validate_contract(contract, registry, metrics)
    assert any("维度白名单" in v for v in violations)
    with pytest.raises(ContractError):
        executor.execute(contract)


def test_metric_missing_registry_fail_closed(
    mz: DesMaterialization, registry: Registry
) -> None:
    """未注入指标注册表时含 metric 契约 → 校验违规 ∧ 执行器拒答（M 系列 fail-closed）。"""
    contract = {
        "contract_version": "0.2",
        "metric": {"metric_id": "sales_amount_by_mat_month"},
    }
    assert validate_contract(contract, registry)  # metrics=None → 非空违规
    ex = ContractExecutor(
        mz, registry, metrics_db=METRICS_DB_PATH, permission_ctx=PermissionContext.allow_all()
    )
    with pytest.raises(ContractError):
        ex.execute(contract)


def test_metric_v5_result_guard(executor: ContractExecutor) -> None:
    """V5 结果护栏（red-team P3-9 按规模派生）：合法全表分析（物化表全量行）按规模放行；
    结果超过规模派生上限（scale 被压低到远小于结果）仍 fail-closed 拒答——护栏接线未退化。"""
    contract = {
        "contract_version": "0.2",
        "metric": {"metric_id": "sales_amount_by_mat_month"},
    }
    assert validate_contract(contract, build_registry(), load_metrics(config=_CONFIG)) == []
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        scale = conn.execute(
            "SELECT row_count FROM metric_meta "
            "WHERE metric_id='sales_amount_by_mat_month'"
        ).fetchone()[0]
    finally:
        conn.close()
    # 按规模派生：护栏上限 = max(1000, 物化表行数) = 物化表行数 → 全表分析放行
    result = executor.execute(contract)
    assert result["count"] == scale > 0
    # 护栏仍有效：真实数据无法超出自身规模上限（rows ≤ 物化表行数），故用 scale 注入模拟
    # 元数据异常态（scale 远小于结果）→ 上限回落 1000 → 拒答，验证 _result_limit(scale) 接线
    original = executor._metric_scale
    executor._metric_scale = lambda conn, md: 10  # type: ignore[method-assign]
    try:
        with pytest.raises(ContractError) as exc:
            executor.execute(contract)
        assert "护栏" in str(exc.value)
    finally:
        executor._metric_scale = original


def test_metric_top_n_limits_rows(executor: ContractExecutor) -> None:
    """v0.2 表达力 Top-N（报告 §6 J4）：metric.topN 执行 LIMIT，返回 ≤N 行且按度量值降序；
    有 group_by 同样生效；非法 topN（0/超大/非整数）fail-closed 拒答。"""
    contract = {
        "contract_version": "0.2",
        "metric": {"metric_id": "sales_amount_by_mat_month", "topN": 5},
    }
    assert validate_contract(contract, build_registry(), load_metrics(config=_CONFIG)) == []
    result = executor.execute(contract)
    assert 0 < result["count"] <= 5
    vals = [row["sales_amount"] for row in result["rows"]]
    assert vals == sorted(vals, reverse=True)  # Top-N = 按度量值降序取前 N
    # 有 group_by 的 topN 同样生效（重聚合后按度量值降序截断）
    gb_contract = {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "sales_amount_by_mat_month",
            "topN": 3,
            "group_by": ["month"],
        },
    }
    gb_result = executor.execute(gb_contract)
    assert 0 < gb_result["count"] <= 3
    assert [r["sales_amount"] for r in gb_result["rows"]] == sorted(
        (r["sales_amount"] for r in gb_result["rows"]), reverse=True
    )
    # 非法 topN → 校验违规（fail-closed）
    for bad in (0, MAX_TOP_N + 1, "5", 3.5):
        bad_contract = {
            "contract_version": "0.2",
            "metric": {"metric_id": "sales_amount_by_mat_month", "topN": bad},
        }
        assert validate_contract(bad_contract, build_registry(), load_metrics(config=_CONFIG)), f"topN={bad!r} 应被拒"


def test_metric_measure_filter_executes(executor: ContractExecutor) -> None:
    """v0.2 表达力按度量过滤（报告 §6 F2/F4）：dimension_filters 支持度量列（如 sales_amount > 阈值）；
    非法度量过滤值（非数值）fail-closed 拒答（不静默忽略）。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        thr = conn.execute(
            "SELECT approx_quantile(sales_amount, 0.9) "
            "FROM metric_sales_amount_by_mat_month"
        ).fetchone()[0]
    finally:
        conn.close()
    contract = {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "sales_amount_by_mat_month",
            "dimension_filters": {"sales_amount": {"op": "gt", "value": float(thr)}},
        },
    }
    assert validate_contract(contract, build_registry(), load_metrics(config=_CONFIG)) == []
    result = executor.execute(contract)
    assert result["count"] > 0
    assert all(row["sales_amount"] > thr for row in result["rows"])
    # 非法度量过滤值（非数值）→ 校验违规 + 执行器拒答
    bad = {
        "contract_version": "0.2",
        "metric": {
            "metric_id": "sales_amount_by_mat_month",
            "dimension_filters": {"sales_amount": {"op": "gt", "value": "abc"}},
        },
    }
    violations = validate_contract(bad, build_registry(), load_metrics(config=_CONFIG))
    assert any("度量过滤值类型应为数值" in v for v in violations)
    with pytest.raises(ContractError):
        executor.execute(bad)


# ===========================================================================
# ④ v0.1 兼容（设计 §6 补充断言）
# ===========================================================================
def test_dq01_v01_compat(executor: ContractExecutor) -> None:
    """DQ-01 老 v0.1 契约：v0.2 执行器下原样通过，结果 = round(N×rate) 条（当前 = 1200）。"""
    assert validate_contract(DQ01_CONTRACT, build_registry()) == []
    result = executor.execute(DQ01_CONTRACT)
    assert result["object_type"] == "Material"
    assert result["count"] == EXPECTED_MULTI
    assert result["count"] == 1200  # 配置派生与任务口径交叉验证
    pks = [i["pk"] for i in result["items"]]
    assert pks == sorted(pks)


def test_q2_v01_compat(
    mz: DesMaterialization, executor: ContractExecutor
) -> None:
    """Q2 单物料编码查询：filters matnr eq + hasCode 遍历带回编码数组（结果与 v0.1 一致）。"""
    matnr = rows_as_dicts(
        mz.duckdb,
        "SELECT matnr FROM material WHERE old_code IS NOT NULL ORDER BY matnr LIMIT 1",
    )[0]["matnr"]
    contract = {
        "object_type": "Material",
        "filters": {"matnr": {"op": "eq", "value": matnr}},
        "link_traversal": {"link": "material.codes", "hops": 1},
    }
    result = executor.execute(contract)
    assert result["count"] == 1
    item = result["items"][0]
    assert item["properties"]["matnr"] == matnr
    by_space = {c["code_space"]: c["value"] for c in item["codes"]}
    assert by_space["erp"] == by_space["plm"] == by_space["wms"] == matnr
    assert by_space["mes"] == "MP-" + matnr
    assert by_space.get("legacy") == item["properties"]["old_code"]


def test_q3_v01_compat(executor: ContractExecutor) -> None:
    """Q3 一物多码计数聚合：count = round(N×rate)（与 v0.1 一致）。"""
    contract = {
        "object_type": "Material",
        "filters": {"old_code": {"op": "is_not_null"}},
        "aggregations": [{"function": "count", "field": "*"}],
    }
    result = executor.execute(contract)
    assert result["object_type"] == "Material"
    assert result["row_count"] == EXPECTED_MULTI
    agg = result["aggregations"][0]
    assert (agg["function"], agg["field"], agg["value"]) == (
        "count",
        "*",
        EXPECTED_MULTI,
    )


# ===========================================================================
# ⑤ 读侧权限（设计 §3.3，P1.5 decide(read) 接线）
# ===========================================================================
def test_permission_no_ctx_deny_fail_closed(
    mz: DesMaterialization, registry: Registry
) -> None:
    """red-team P1-1：无 permission_ctx → 执行器缺省默认 deny（fail-closed），读操作被拒。

    旧行为「无 ctx 照常执行」是 fail-open 缺陷，不再保留——内部工具需显式 allow_all 才放行。
    """
    ex = ContractExecutor(mz, registry)  # 不传 ctx = 默认 deny
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(DQ01_CONTRACT)
    assert exc.value.code == "PERMISSION_DENIED"


def test_permission_no_policy_fail_closed(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """无匹配策略 → decide(read) denied → PermissionDeniedError（fail-closed，不静默）。"""
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(DQ01_CONTRACT)
    assert exc.value.code == "PERMISSION_DENIED"


def test_permission_allow_passes(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """对象级 read allow → 通过；metric 结果列 = 维度 + 度量（对象字段受可见集约束）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    result = ex.execute(_sales_contract(matnr))
    assert result["count"] > 0
    assert set(result["rows"][0]) == {"matnr", "month", "sales_amount"}


def test_permission_attribute_deny_metric(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """属性级 deny（matnr）：metric 契约请求不可见维度列 → fail-closed 拒答（不静默裁剪）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(
        _policy(
            policy_id="deny-matnr",
            effect="deny",
            scope="attribute",
            attributes=["matnr"],
        )
    )
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(_sales_contract("MAT-2026-2979-MC4"))
    assert "matnr" in str(exc.value)


def test_permission_attribute_deny_v01_dq01(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """属性级 deny（old_code）：DQ-01 契约请求不可见列 → fail-closed 拒答（属性级读权限）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(
        _policy(
            policy_id="deny-old",
            effect="deny",
            scope="attribute",
            attributes=["old_code"],
        )
    )
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(DQ01_CONTRACT)
    assert "old_code" in str(exc.value)


def test_permission_link_target_denied_fail_closed(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """red-team P1-2：link_traversal 目标（Code）无 read 策略 + source（Material）allow → 拒答。

    目标对象权限必须纳入 decide(read)，否则 link_traversal 可系统性旁路被 deny 的敏感对象。
    """
    perm_service.create(_policy(policy_id="allow-mat"))  # 仅 Material allow，Code 无策略
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(DQ01_CONTRACT)
    assert exc.value.code == "PERMISSION_DENIED"
    assert "Code" in str(exc.value)


def test_permission_link_target_allow_passes(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """red-team P1-2：link 目标（Code）allow → DQ-01 返回且 codes 数组在（目标权限放行）。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(_policy(policy_id="allow-code", object_type="Code"))
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    result = ex.execute(DQ01_CONTRACT)
    assert result["count"] > 0
    assert any(item["codes"] for item in result["items"])


def test_permission_link_target_attribute_deny_fail_closed(
    mz: DesMaterialization,
    registry: Registry,
    metrics: MetricRegistry,
    perm_service: PermissionService,
) -> None:
    """red-team P1-2：link 目标（Code）属性级 deny（value）→ 返回列不可见 → fail-closed 拒答。"""
    perm_service.create(_policy(policy_id="allow-mat"))
    perm_service.create(_policy(policy_id="allow-code", object_type="Code"))
    perm_service.create(
        _policy(
            policy_id="deny-code-value",
            object_type="Code",
            effect="deny",
            scope="attribute",
            attributes=["value"],
        )
    )
    ctx = PermissionContext(subject=_agent(), permission_registry=perm_service.perm_registry)
    ex = _executor_with_perm(mz, registry, metrics, ctx)
    with pytest.raises(PermissionDeniedError) as exc:
        ex.execute(DQ01_CONTRACT)
    assert "value" in str(exc.value)


def test_v01_time_range_fail_closed(
    executor: ContractExecutor, registry: Registry
) -> None:
    """red-team P2-2：v0.1 非 metric 契约带 time_range → 校验违规 ∧ 执行器拒答（杜绝静默忽略）。"""
    contract = {
        "object_type": "Material",
        "filters": {"material_type": {"op": "eq", "value": "ROH"}},
        "time_range": {"from": "2026-01-01", "to": "2026-01-31"},
    }
    violations = validate_contract(contract, registry)
    assert any("不支持 time_range" in v for v in violations)
    with pytest.raises(ContractError) as exc:
        executor.execute(contract)
    assert "不支持 time_range" in str(exc.value)


# ===========================================================================
# ⑥ 性能冒烟（设计 §4.3 P95≤500ms，宽松判据，标记 slow）
# ===========================================================================
@pytest.mark.slow
def test_metric_query_p95_smoke(executor: ContractExecutor) -> None:
    """物化指标查询 P95 ≤ 500ms（§4.3 靶值；预热 1 次 + 重复 ≥10 次，宽松判据防 CI 抖动）。"""
    conn = duckdb.connect(str(METRICS_DB_PATH), read_only=True)
    try:
        matnr = conn.execute(
            "SELECT matnr FROM metric_sales_amount_by_mat_month "
            "ORDER BY sales_amount DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    contract = _sales_contract(matnr)
    executor.execute(contract)  # 预热 1 次（DuckDB 元数据/页缓存）
    lats_ms: list[float] = []
    for _ in range(12):
        start = time.perf_counter()
        result = executor.execute(contract)
        lats_ms.append((time.perf_counter() - start) * 1000)
        assert result["count"] > 0
    lats_ms.sort()
    p95 = lats_ms[int(len(lats_ms) * 0.95) - 1]
    assert p95 < 500.0, f"物化指标查询 P95={p95:.1f}ms 超过 §4.3 靶值 500ms"
