"""DES 配置加载与校验 —— YAML 2 层（行业模板 + 企业覆盖）深度合并 + fail-fast 校验 + canonical 序列化。

依据 docs/P1a-DES-配置与表结构设计_v0.1.md：
- 层间继承 = 加载器 deep_merge(template, enterprise)：标量企业覆盖、映射递归合并、列表整体替换（§1.2）；
- 合并后做配置校验（rate∈[0,1]、tolerance>0、field 存在等），失败即 fail-fast 报错，不静默（§1.2）；
- 配置规范化：key 排序 canonical JSON 序列化，供 config_sha256（§4 约定 4）。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# 常量（确定性锚点：目录布局与 MARA 字段契约，见设计 §2.1/§5）
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DES_DATA_DIR = PROJECT_ROOT / "data" / "des"
DEFAULT_TEMPLATE_FILE = DES_DATA_DIR / "des_industry_template.yaml"
DEFAULT_ENTERPRISES_DIR = DES_DATA_DIR / "enterprises"

# MARA 字段集（设计 §2.1）：注入字段 field 必须存在于此列中（配置校验用）
MARA_COLUMNS = ("MATNR", "MAKTX", "MTART", "BISMT", "MEINS", "MATKL", "ERDAT")


class DesConfigError(Exception):
    """配置加载/校验失败（fail-fast，不静默）。"""


# ---------------------------------------------------------------------------
# 层间继承：深度合并（§1.2）
# ---------------------------------------------------------------------------
def deep_merge(base: dict, override: dict) -> dict:
    """深度合并两层配置：映射递归合并，标量/列表用 override 整体替换（§1.2）。

    - 标量：企业值覆盖模板值；
    - 映射：递归合并（企业未写项自动继承模板）；
    - 列表：整体替换（默认）。
    """
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


# ---------------------------------------------------------------------------
# 加载 + 规范化（合并后生效配置）
# ---------------------------------------------------------------------------
def _load_yaml(path: Path) -> dict:
    """读取 YAML 文件，非法结构即 fail-fast。"""
    if not path.is_file():
        raise DesConfigError(f"配置文件不存在: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DesConfigError(f"配置必须为映射: {path}")
    return data


def load_config(
    enterprise_code: str,
    config_file: str | Path | None = None,
    template_file: str | Path | None = None,
) -> dict:
    """加载并规范化企业生效配置（模板层 + 企业覆盖层 deep_merge + 校验）。

    参数：
        enterprise_code：企业编码（目录名，如 hc_precision），用于解析默认企业配置路径；
        config_file：企业覆盖层 YAML（默认 <enterprises_dir>/<code>/des_enterprise.yaml）；
        template_file：行业模板层 YAML（默认 data/des/des_industry_template.yaml）。
    """
    ent_path = (
        Path(config_file)
        if config_file
        else DEFAULT_ENTERPRISES_DIR / enterprise_code / "des_enterprise.yaml"
    )
    enterprise = _load_yaml(ent_path)

    # 模板解析：显式传入优先，否则取企业文件声明的 inherit（相对 data/des/ 解析）
    if template_file is None:
        inherit = enterprise.get("inherit")
        if isinstance(inherit, str):
            template_file = DES_DATA_DIR / inherit
    template = _load_yaml(Path(template_file) if template_file else DEFAULT_TEMPLATE_FILE)

    merged = deep_merge(template, enterprise)
    normalized = _normalize(merged, enterprise_code)
    validate(normalized)
    return normalized


def _normalize(merged: dict, enterprise_code: str) -> dict:
    """把 deep_merge 后的两层配置规范化为生成器消费的生效配置。

    企业覆盖层把注入覆盖放在 enterprise.injection（设计 §1.3 企业文件），
    与模板顶层 injection 深度合并为生效注入配置（企业项优先）。
    """
    ent = merged.get("enterprise", {})
    systems_raw = ent.get("systems", {})
    default_count = merged.get("material_count_default", 200)
    systems: dict[str, dict[str, Any]] = {}
    for code in ("erp", "mes", "wms"):
        raw = systems_raw.get(code, {})
        if not raw:
            continue
        count = raw.get("material_count", default_count)
        systems[code] = {
            "db": raw.get("db", f"{code}.db"),
            "table": raw.get("table", ""),
            "material_count": count,
            "row_count": raw.get("row_count", count),
        }
    injection = deep_merge(merged.get("injection", {}), ent.get("injection", {}))
    return {
        "industry": merged.get("industry", "manufacturing"),
        "template_version": str(merged.get("template_version", "")),
        "coding": {
            "master_pattern": merged.get("coding", {}).get("master_pattern", ""),
            "year": merged.get("coding", {}).get("year"),
        },
        "injection": injection,
        "storage": merged.get("storage", {"layout": "one_enterprise_one_dir"}),
        "seed_policy": merged.get("seed_policy", "fixed"),
        "material_count_default": default_count,
        "enterprise": {
            "code": enterprise_code,
            "name": ent.get("name", ""),
            "code_prefix": ent.get("code_prefix", ""),
            "seed": ent.get("seed"),
            "systems": systems,
        },
    }


# ---------------------------------------------------------------------------
# fail-fast 配置校验（§1.2 禁做清单 / §6 机验口径）
# ---------------------------------------------------------------------------
def validate(config: dict) -> None:
    """校验生效配置，任一不合法即抛 DesConfigError（fail-fast，不静默）。"""
    ent = config.get("enterprise", {})
    if not ent.get("name"):
        raise DesConfigError("enterprise.name 缺失")
    if not ent.get("code_prefix"):
        raise DesConfigError("enterprise.code_prefix 缺失")
    seed = ent.get("seed")
    if not isinstance(seed, int) or seed < 0:
        raise DesConfigError(f"enterprise.seed 必须为非负整数: {seed!r}")
    systems = ent.get("systems", {})
    if not systems:
        raise DesConfigError("enterprise.systems 缺失（至少一个源系统）")
    for code, sys_cfg in systems.items():
        if not sys_cfg.get("db") or not sys_cfg.get("table"):
            raise DesConfigError(f"系统 {code} 缺少 db/table")
        count = sys_cfg.get("material_count", 0)
        if not isinstance(count, int) or count < 1:
            raise DesConfigError(f"系统 {code} material_count 必须为正整数: {count!r}")

    year = config.get("coding", {}).get("year")
    if not isinstance(year, int) or not 1000 <= year <= 9999:
        raise DesConfigError(f"coding.year 必须为 4 位年份: {year!r}")
    pattern = config.get("coding", {}).get("master_pattern", "")
    if "{YYYY}" not in pattern or "{NNNN}" not in pattern or "{CCC}" not in pattern:
        raise DesConfigError(f"coding.master_pattern 缺少占位符: {pattern!r}")

    multi = config.get("injection", {}).get("multi_code", {})
    rate = multi.get("rate")
    if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
        raise DesConfigError(f"注入率 multi_code.rate 必须 ∈ [0,1]: {rate!r}")
    tolerance = multi.get("tolerance")
    if not isinstance(tolerance, (int, float)) or tolerance <= 0:
        raise DesConfigError(f"注入容差 multi_code.tolerance 必须 >0: {tolerance!r}")
    field = multi.get("field")
    if field not in MARA_COLUMNS:
        raise DesConfigError(f"注入字段 multi_code.field 不在 MARA 列中: {field!r}")
    if not multi.get("legacy_pattern") or not multi.get("legacy_prefix"):
        raise DesConfigError("multi_code 缺少 legacy_pattern/legacy_prefix")


# ---------------------------------------------------------------------------
# canonical 序列化 + config_sha256（§4 约定 4）
# ---------------------------------------------------------------------------
def canonical_dump(obj: Any) -> str:
    """canonical JSON：dict 按 key 排序、紧凑分隔符、UTF-8 保中文（§4 约定 4）。"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def config_sha256(config: dict, seed: int) -> str:
    """config_sha256 = SHA256(canonical(配置) ∥ "::" ∥ seed)（§4 机验锚点）。"""
    payload = f"{canonical_dump(config)}::{seed}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
