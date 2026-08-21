"""DES 配置加载与校验 —— YAML 2 层（行业模板 + 企业覆盖）深度合并 + fail-fast 校验 + canonical 序列化。

依据 docs/P1b-DES-横向铺开设计_v0.1.md（§5.1 约定 4 / §7.2 生成器扩展点）与 P1a 基线设计：
- 层间继承 = 加载器 deep_merge(template, enterprise)：标量企业覆盖、映射递归合并、列表整体替换（§1.2）；
- 表注册表：systems[code].tables[]（每表 kind/row_count/pk/depends_on/fk/injection），
  行数与表规格默认放模板层，企业层可覆盖（§7.2）；
- 合并后做配置校验（fail-fast）：row_count 正整数、depends_on/fk 引用存在、kind 枚举、pk 非空、
  rate∈[0,1]、tolerance>0、field 存在等，失败即抛 DesConfigError，不静默；
- Σ row_count == total_target 校验留待 Phase B（事务表未实现，本阶段只记录口径，见 sum_row_counts）；
- 配置规范化：key 排序 canonical JSON 序列化（含全部表规格 + data_version），供 config_sha256（约定 4）。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# 常量（确定性锚点：目录布局 / 表规格合法值 / MARA 字段契约，见设计 §2.1/§5）
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DES_DATA_DIR = PROJECT_ROOT / "data" / "des"
DEFAULT_TEMPLATE_FILE = DES_DATA_DIR / "des_industry_template.yaml"
DEFAULT_ENTERPRISES_DIR = DES_DATA_DIR / "enterprises"

# MARA 字段集（设计 §2.1）：注入字段 field 必须存在于此列中（配置校验用）
MARA_COLUMNS = ("MATNR", "MAKTX", "MTART", "BISMT", "MEINS", "MATKL", "ERDAT")

# 表类别（§3.1）：主数据 / 事务流水（事务表 Phase B 实现）
TABLE_KINDS = ("master", "transaction")


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
    scale: float | None = None,
) -> dict:
    """加载并规范化企业生效配置（模板层 + 企业覆盖层 deep_merge + 校验）。

    参数：
        enterprise_code：企业编码（目录名，如 hc_precision），用于解析默认企业配置路径；
        config_file：企业覆盖层 YAML（默认 <enterprises_dir>/<code>/des_enterprise.yaml）；
        template_file：行业模板层 YAML（默认 data/des/des_industry_template.yaml）；
        scale：行数缩放系数（None 默认 = 全量，行为与既往完全一致）。传数值时对每表
            row_count 乘 scale：row_count' = max(1, round(row_count × scale))，total_target
            重算为 Σ row_count'（见 _apply_scale）；scale 写入配置顶层参与 canonical 序列化
            → config_sha256（同 scale 同 seed → 同 sha；scale 不同 → sha 不同）。
            用于常规测试小规模快速跑（如 scale=0.003 → 总行数 ~3000），1M 演示/量级门禁保留 None。
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
    if scale is not None:
        if not isinstance(scale, (int, float)) or isinstance(scale, bool) or scale <= 0:
            raise DesConfigError(f"scale 必须为正数: {scale!r}")
        normalized = _apply_scale(normalized, float(scale))
        validate(normalized)
    return normalized


def _normalize(merged: dict, enterprise_code: str) -> dict:
    """把 deep_merge 后的两层配置规范化为生成器消费的生效配置。

    - 表注册表：enterprise.systems[code].tables[name] 每表一份规格
      （kind/row_count/pk/depends_on/fk/injection），企业覆盖层经 deep_merge 继承模板默认；
    - 注入配置：企业 enterprise.injection 与模板顶层 injection 深度合并为生效注入配置（企业项优先）。
    """
    ent = merged.get("enterprise", {})
    systems_raw = ent.get("systems", {})
    systems: dict[str, dict[str, Any]] = {}
    for code, raw in systems_raw.items():
        if not raw:
            continue
        tables: dict[str, dict[str, Any]] = {}
        for name, spec in (raw.get("tables") or {}).items():
            tables[name] = {
                "kind": spec.get("kind", "master"),
                "row_count": spec.get("row_count", 0),
                "pk": list(spec.get("pk") or []),
                "depends_on": list(spec.get("depends_on") or []),
                "fk": dict(spec.get("fk") or {}),
                "injection": spec.get("injection"),
            }
        systems[code] = {
            "db": raw.get("db", f"{code}.db"),
            "tables": tables,
        }
    injection = deep_merge(merged.get("injection", {}), ent.get("injection", {}))
    return {
        "industry": merged.get("industry", "manufacturing"),
        "template_version": str(merged.get("template_version", "")),
        "data_version": str(merged.get("data_version", "")),
        "total_target": merged.get("total_target"),
        "coding": {
            "master_pattern": merged.get("coding", {}).get("master_pattern", ""),
            "year": merged.get("coding", {}).get("year"),
        },
        "injection": injection,
        "storage": merged.get("storage", {"layout": "one_enterprise_one_dir"}),
        "seed_policy": merged.get("seed_policy", "fixed"),
        "enterprise": {
            "code": enterprise_code,
            "name": ent.get("name", ""),
            "code_prefix": ent.get("code_prefix", ""),
            "seed": ent.get("seed"),
            "systems": systems,
        },
    }


def _apply_scale(config: dict, scale: float) -> dict:
    """按 scale 缩放每表 row_count（round + 下限 max(1,·)），并重算 total_target = Σ。

    - 每表 row_count' = max(1, round(row_count × scale))：下限 1 保证最小行数（表仍可生成）；
    - total_target' = Σ row_count'（保持 validate 的 Σ == total_target 机验口径）；
    - 把 scale 写入返回配置顶层（key "scale"）：参与 canonical 序列化 → config_sha256，
      同 scale 同 seed → 同 sha；scale 不同（即使行数偶然相同）→ sha 不同（§5.1 约定 4）。
      scale=None 时不含该键，全量配置与既往完全一致（canonical/SHA 不变）。
    注：派生表（如 MARC=2×MARA、STPO=5×MAST）实际行数随父表比例走，小 scale 下可能
    与独立 round 出的 row_count' 有 ±1 级取整差，属生成器自洽口径（见 generate.py）。
    """
    systems: dict[str, dict[str, Any]] = {}
    for code, sys_cfg in config["enterprise"]["systems"].items():
        tables = {
            name: {**spec, "row_count": max(1, round(spec["row_count"] * scale))}
            for name, spec in sys_cfg["tables"].items()
        }
        systems[code] = {**sys_cfg, "tables": tables}
    scaled = {
        **config,
        "scale": scale,
        "enterprise": {**config["enterprise"], "systems": systems},
    }
    scaled["total_target"] = sum(
        spec["row_count"]
        for sys_cfg in systems.values()
        for spec in sys_cfg["tables"].values()
    )
    return scaled


# ---------------------------------------------------------------------------
# fail-fast 配置校验（§1.2 禁做清单 / §6 机验口径 / §7.2 扩展校验）
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

    # 表注册表引用集合（depends_on / fk 引用存在性校验）
    table_ids = {
        f"{code}.{name}"
        for code, sys_cfg in systems.items()
        for name in sys_cfg.get("tables", {})
    }
    for code, sys_cfg in systems.items():
        if not sys_cfg.get("db"):
            raise DesConfigError(f"系统 {code} 缺少 db")
        tables = sys_cfg.get("tables", {})
        if not tables:
            raise DesConfigError(f"系统 {code} 缺少表注册（tables 至少一张）")
        for name, spec in tables.items():
            table_id = f"{code}.{name}"
            kind = spec.get("kind")
            if kind not in TABLE_KINDS:
                raise DesConfigError(f"表 {table_id} kind 非法: {kind!r}（应为 {list(TABLE_KINDS)}）")
            row_count = spec.get("row_count", 0)
            if not isinstance(row_count, int) or row_count < 1:
                raise DesConfigError(f"表 {table_id} row_count 必须为正整数: {row_count!r}")
            pk = spec.get("pk")
            if not pk or not all(isinstance(c, str) and c for c in pk):
                raise DesConfigError(f"表 {table_id} pk 必须为非空字符串数组: {pk!r}")
            for dep in spec.get("depends_on", []):
                if dep not in table_ids:
                    raise DesConfigError(f"表 {table_id} depends_on 引用不存在: {dep!r}")
            for field, ref in (spec.get("fk") or {}).items():
                if ref not in table_ids:
                    raise DesConfigError(f"表 {table_id} fk {field} 引用不存在: {ref!r}")
            injection = spec.get("injection")
            if injection is not None and not isinstance(injection, (str, dict)):
                raise DesConfigError(f"表 {table_id} injection 必须为字符串或映射: {injection!r}")

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

    if not config.get("data_version"):
        raise DesConfigError("data_version 缺失（参与 config_sha256，约定 4）")
    total = config.get("total_target")
    if not isinstance(total, int) or total < 1:
        raise DesConfigError(f"total_target 必须为正整数: {total!r}")
    # Σ row_count == total_target 机验（Phase B 事务表已实现，启用：量级口径 §1.2/§3.1）
    if sum_row_counts(config) != total:
        raise DesConfigError(
            f"Σ row_count ({sum_row_counts(config)}) != total_target ({total})，"
            "表规格行数合计须精确等于总行数门禁"
        )


def sum_row_counts(config: dict) -> int:
    """Σ 全部表 row_count（§1.2 量级口径；Phase B 门禁：== total_target）。"""
    return sum(
        spec["row_count"]
        for sys_cfg in config["enterprise"]["systems"].values()
        for spec in sys_cfg["tables"].values()
    )


# ---------------------------------------------------------------------------
# canonical 序列化 + config_sha256（§4 约定 4）
# ---------------------------------------------------------------------------
def canonical_dump(obj: Any) -> str:
    """canonical JSON：dict 按 key 排序、紧凑分隔符、UTF-8 保中文（§4 约定 4）。"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def config_sha256(config: dict, seed: int) -> str:
    """config_sha256 = SHA256(canonical(配置) ∥ "::" ∥ seed)（§4 机验锚点，含全部表规格 + data_version）。"""
    payload = f"{canonical_dump(config)}::{seed}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
