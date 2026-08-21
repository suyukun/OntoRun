"""DES（真实企业生成工具）—— S2 P1a 垂直切片数据侧模块。

对外 CLI：python -m src.des --enterprise hc_precision --seed 20260821 --out <dir>
公开 API：load_config / build_enterprise / build_manifest / config_sha256 / table_sha256
"""

from .config import (
    DesConfigError,
    canonical_dump,
    config_sha256,
    deep_merge,
    load_config,
)
from .generate import build_enterprise, check_code, master_code
from .manifest import build_manifest, table_sha256

__all__ = [
    "DesConfigError",
    "build_enterprise",
    "build_manifest",
    "canonical_dump",
    "check_code",
    "config_sha256",
    "deep_merge",
    "load_config",
    "master_code",
    "table_sha256",
]
