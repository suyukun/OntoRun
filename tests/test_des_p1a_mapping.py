"""S2 P1a DES 垂直切片 —— 本体映射侧门禁（设计文档 §1.4/§3/§4 可机验断言）。

对照 docs/P1a-本体映射与查询契约设计_v0.1.md：
- 物化锚点（§1.4/§1.5）：Material=200、Code=830（跨 3 源系统物化，可机验）；
- 契约校验 V1-V5（§3.3）：字段白名单 / 类型 / ≤1 跳 / 防注入 / 护栏，违规一律 fail-closed 拒答；
- ground truth（§4.1-§4.3）：DQ-01（Q1）/ Q2 / Q3 执行断言 + reconcile_dq01 三方对账（§2.3）。
旧码正则禁硬编码：一律从配置派生（mz.legacy_re，设计 §2.2）。
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from src.des.contract import (
    DQ01_CONTRACT,
    ContractError,
    ContractExecutor,
    reconcile_dq01,
    validate_contract,
)
from src.des.generate import build_enterprise
from src.des.materialize import DesMaterialization, materialize_des, rows_as_dicts
from src.ontology import build_registry
from src.ontology.registry import Registry

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "hc_precision"
ENTERPRISE_DIR = ROOT / "data" / "des" / "enterprises" / ENTERPRISE_CODE
EXPECTED_MATERIAL = 200  # 设计 §1.4/§1.5：MARA 行数 = 物料概念数
EXPECTED_CODE = 830  # 设计 §1.4：200×3 主码族 + 200 mes + 30 legacy
EXPECTED_MULTI = 30  # 设计 §4.1：round(N × rate) = round(200×0.15)
EXPECTED_RATE = 0.15  # 设计 §4.3：占比 = 30/200 = 15.00%


# 契约校验 V1-V5 拒答集：（违规契约, 预期违规说明片段, 对应规则）
INVALID_CONTRACTS: list[tuple[dict, str, str]] = [
    ({"object_type": "Material", "bogus": 1}, "未知顶层键", "V4 additionalProperties:false"),
    (
        {"object_type": "Material", "filters": {"no_such_field": {"op": "is_not_null"}}},
        "不在 Material 白名单",
        "V1 字段白名单",
    ),
    (
        {"object_type": "Material", "filters": {"old_code": {"op": "like", "value": "x"}}},
        "过滤操作符非法",
        "V2 操作符",
    ),
    (
        {"object_type": "Material", "filters": {"old_code": {"op": "is_not_null", "value": "x"}}},
        "不得携带 value",
        "V2 操作符约束",
    ),
    (
        {"object_type": "Material", "link_traversal": {"link": "material.codes", "hops": 2}},
        "hops 必须为 1",
        "V3 ≤1 跳",
    ),
    (
        {"object_type": "Material", "link_traversal": {"link": "material.bogus", "hops": 1}},
        "链接未注册",
        "V1 链接白名单",
    ),
    (
        {"object_type": "Material", "aggregations": [{"function": "sum", "field": "*"}]},
        "仅 count 允许",
        "V2 聚合约束",
    ),
    (
        {
            "object_type": "Material",
            "filters": {"old_code": {"op": "eq", "value": "x'; DROP TABLE material; --"}},
        },
        "疑似 SQL 片段",
        "V4 防注入",
    ),
    ({"object_type": "NoSuchType"}, "object_type 未注册", "V1 对象白名单"),
]


# ---------------------------------------------------------------------------
# fixtures / 工具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def mz() -> Iterator[tuple[DesMaterialization, Registry]]:
    """DES 物化（DuckDB 跨 3 库）+ 会话级 Registry；退出时关闭 DuckDB 连接。"""
    build_enterprise(ENTERPRISE_CODE, out_dir=str(ENTERPRISE_DIR))
    reg = build_registry()
    mat = materialize_des(ENTERPRISE_CODE, out_dir=ENTERPRISE_DIR, registry=reg)
    yield mat, reg
    mat.duckdb.close()


def _executor(mz: tuple[DesMaterialization, Registry]) -> ContractExecutor:
    """从会话物化构造执行器（校验 + 参数化执行）。"""
    mat, reg = mz
    return ContractExecutor(mat, reg)


# ===========================================================================
# 物化锚点（设计 §1.4/§1.5）
# ===========================================================================
def test_materialization_anchors(mz: tuple[DesMaterialization, Registry]) -> None:
    """物化锚点：Material=200、Code=830、跨库一致性 0 差异、self_check 零问题。"""
    mat, _ = mz
    assert mat.material_count == EXPECTED_MATERIAL
    assert mat.code_count == EXPECTED_CODE
    cross = mat.validation["cross_db"]
    assert cross["orphan_mpla"] == 0  # 设计 §1.5：MES/WMS 无孤儿
    assert cross["orphan_wmmd"] == 0
    assert cross["d3_mismatch"] == 0  # WMMD.MEINS = MARA.MEINS（门禁 D3 对齐）
    assert mat.validation["self_check_issues"] == []  # CODE_SPACE_ENUM / MULTI_CODE 一致


# ===========================================================================
# 契约校验 V1-V5（设计 §3.3，fail-closed 拒答）
# ===========================================================================
@pytest.mark.parametrize(
    "contract, expect, rule",
    INVALID_CONTRACTS,
    ids=[case[2] for case in INVALID_CONTRACTS],
)
def test_invalid_contract_fail_closed(
    mz: tuple[DesMaterialization, Registry], contract: dict, expect: str, rule: str
) -> None:
    """V1-V5 违规契约：校验器报违规 ∧ 执行器抛 ContractError（拒答，不降级为裸执行）。"""
    violations = validate_contract(contract, mz[1])
    assert violations, f"（{rule}）契约应被拒答: {contract}"
    assert any(expect in v for v in violations), f"（{rule}）缺预期违规说明 {expect!r}: {violations}"
    with pytest.raises(ContractError):
        _executor(mz).execute(contract)


def test_dq01_contract_validates_clean(mz: tuple[DesMaterialization, Registry]) -> None:
    """DQ-01 契约（设计 §3.2）通过 V1-V5 校验：零违规。"""
    assert validate_contract(DQ01_CONTRACT, mz[1]) == []


# ===========================================================================
# ground truth 执行（设计 §4.3 Q1/Q2/Q3）
# ===========================================================================
def test_dq01_execution(mz: tuple[DesMaterialization, Registry]) -> None:
    """DQ-01（Q1）：30 条 Material，每条满足一物多码全谓词，codes 含 legacy 行。"""
    result = _executor(mz).execute(DQ01_CONTRACT)
    assert result["object_type"] == "Material"
    assert result["count"] == EXPECTED_MULTI
    pks = [i["pk"] for i in result["items"]]
    assert pks == sorted(pks), "items 应按 matnr 升序（设计 §4.3 Q1）"
    legacy_re = mz[0].legacy_re  # 由配置派生（设计 §2.2，禁硬编码）
    for item in result["items"]:
        props = item["properties"]
        old = props["old_code"]
        assert old is not None
        assert old != props["matnr"]
        assert legacy_re.match(old), f"旧码不匹配派生正则: {old}"
        legacy = [c for c in item["codes"] if c["code_space"] == "legacy"]
        assert len(legacy) == 1 and legacy[0]["value"] == old


def test_q2_single_material_codes(mz: tuple[DesMaterialization, Registry]) -> None:
    """Q2：单物料编码查询 —— filters matnr eq + hasCode 遍历带回编码数组。"""
    matnr = rows_as_dicts(
        mz[0].duckdb,
        "SELECT matnr FROM material WHERE old_code IS NOT NULL ORDER BY matnr LIMIT 1",
    )[0]["matnr"]
    contract = {
        "object_type": "Material",
        "filters": {"matnr": {"op": "eq", "value": matnr}},
        "link_traversal": {"link": "material.codes", "hops": 1},
    }
    result = _executor(mz).execute(contract)
    assert result["count"] == 1
    item = result["items"][0]
    props = item["properties"]
    assert props["matnr"] == matnr
    by_space = {c["code_space"]: c["value"] for c in item["codes"]}
    assert by_space["erp"] == by_space["plm"] == by_space["wms"] == matnr  # 主码族同值（§1.3）
    assert by_space["mes"] == "MP-" + matnr  # MES 派生码（§1.3）
    old = props["old_code"]
    # 有旧码 ⟺ codes 含 legacy 行且 value == old_code（双向，§2.3）
    assert by_space.get("legacy") == old
    expected_codes = 4 + (1 if old is not None else 0)  # 主码族 3 + mes + legacy(若有)
    assert len(item["codes"]) == expected_codes


def test_q3_aggregation(mz: tuple[DesMaterialization, Registry]) -> None:
    """Q3：一物多码计数与占比（聚合）—— count=30、ratio=15.00%。"""
    contract = {
        "object_type": "Material",
        "filters": {"old_code": {"op": "is_not_null"}},
        "aggregations": [{"function": "count", "field": "*"}],
    }
    result = _executor(mz).execute(contract)
    assert result["object_type"] == "Material"
    assert result["row_count"] == EXPECTED_MULTI
    agg = result["aggregations"][0]
    assert (agg["function"], agg["field"], agg["value"]) == ("count", "*", EXPECTED_MULTI)
    assert agg["value"] / mz[0].material_count == pytest.approx(EXPECTED_RATE)


def test_reconcile_dq01(mz: tuple[DesMaterialization, Registry]) -> None:
    """DQ-01 三方对账（设计 §2.3）：ok=True、expected=actual=30、differences 空。"""
    result = _executor(mz).execute(DQ01_CONTRACT)
    rec = reconcile_dq01(result, out_dir=ENTERPRISE_DIR)
    assert rec.ok is True
    assert rec.expected_count == EXPECTED_MULTI
    assert rec.actual_count == EXPECTED_MULTI
    assert rec.differences == []
