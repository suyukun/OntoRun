"""DQ-01 跑通 + 对账（设计 §2.3/§3.2/§4.3）。

ReconcileResult：三方对账结果；reconcile_dq01：本体查询结果 vs 数据侧注入集 +
manifest.multi_code_count 对账；run_dq01：物化 + 执行 DQ-01。与 v0.1 单文件实现行为一致。
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.des.config import DEFAULT_ENTERPRISES_DIR
from src.des.contract.executor import ContractExecutor
from src.des.contract.permissions import PermissionContext
from src.des.contract.schema import DQ01_CONTRACT
from src.des.materialize import DesMaterialization, materialize_des
from src.ontology import build_registry
from src.ontology.registry import Registry


# ---------------------------------------------------------------------------
# DQ-01 跑通 + 对账（设计 §2.3/§3.2/§4.3）
# ---------------------------------------------------------------------------
@dataclass
class ReconcileResult:
    """DQ-01 三方对账结果：本体查询 vs 数据侧注入集 vs manifest。"""

    ok: bool
    expected_count: int
    actual_count: int
    ratio: float
    differences: list[str]


def reconcile_dq01(
    result: dict,
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    manifest: dict | None = None,
) -> ReconcileResult:
    """本体查询结果 vs 数据侧注入集 + manifest.multi_code_count 三方对账（设计 §2.3）。"""
    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    conn = sqlite3.connect(str(out / "erp.db"))
    try:
        data_side = [r[0] for r in conn.execute("SELECT MATNR FROM MARA WHERE BISMT IS NOT NULL ORDER BY MATNR")]
    finally:
        conn.close()
    if manifest is None:
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    erp_entry = manifest["tables"]["erp.MARA"]
    onto_side = [item["pk"] for item in result.get("items", [])]
    n = int(erp_entry["rows"])
    expected = int(erp_entry["multi_code_count"])
    differences = sorted(set(onto_side) ^ set(data_side))
    if len(onto_side) != len(data_side):
        differences.append(f"条数不一致: 本体 {len(onto_side)} ≠ 数据侧 {len(data_side)}")
    ok = not differences and len(onto_side) == expected
    return ReconcileResult(
        ok=ok,
        expected_count=expected,
        actual_count=len(onto_side),
        ratio=len(onto_side) / n if n else 0.0,
        differences=differences,
    )


def run_dq01(
    enterprise_code: str = "hc_precision",
    out_dir: str | Path | None = None,
    registry: Registry | None = None,
) -> tuple[dict, DesMaterialization]:
    """物化 + 执行 DQ-01，返回 (查询结果, 物化对象)。调用方负责 mz.duckdb.close()。"""
    reg = registry or build_registry()
    mz = materialize_des(enterprise_code, out_dir=out_dir, registry=reg)
    # 内部对账工具显式 allow-all 权限上下文（red-team P1-1：权限开关显式可见，不靠缺省放行）
    return (
        ContractExecutor(mz, reg, permission_ctx=PermissionContext.allow_all()).execute(DQ01_CONTRACT),
        mz,
    )
