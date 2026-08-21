"""DES（真实企业生成工具）—— S2 P1a 垂直切片（数据侧 + 本体侧）。

对外 CLI：python -m src.des --enterprise hc_precision --seed 20260821 --out <dir>
数据侧公开 API：load_config / build_enterprise / build_manifest / config_sha256 / table_sha256
本体侧公开 API：materialize_des（DuckDB 跨 3 库物化）/ validate_contract / ContractExecutor
                / run_dq01 / reconcile_dq01（契约 v0.1 + DQ-01 一物多码 + 对账）
"""

from .config import (
    DesConfigError,
    canonical_dump,
    config_sha256,
    deep_merge,
    load_config,
)
from .contract import (
    DQ01_CONTRACT,
    ContractError,
    ContractExecutor,
    ReconcileResult,
    reconcile_dq01,
    run_dq01,
    validate_contract,
)
from .generate import build_enterprise, check_code, master_code
from .manifest import build_manifest, table_sha256
from .materialize import (
    DesMaterialization,
    MaterializeError,
    derive_legacy_regex,
    materialize_des,
)

__all__ = [
    "DQ01_CONTRACT",
    "ContractError",
    "ContractExecutor",
    "DesConfigError",
    "DesMaterialization",
    "MaterializeError",
    "ReconcileResult",
    "build_enterprise",
    "build_manifest",
    "canonical_dump",
    "check_code",
    "config_sha256",
    "deep_merge",
    "derive_legacy_regex",
    "load_config",
    "master_code",
    "materialize_des",
    "reconcile_dq01",
    "run_dq01",
    "table_sha256",
    "validate_contract",
]
