"""P2 ChatBI 指标注册表加载 + 校验（M1-M8）。

依据 docs/P2-ChatBI闭环设计_v0.1.md §1（指标模型 7 字段 / 校验 M1-M8 / 5 组 15 指标清单 §1.5）：
- 指标 = 挂在本体对象上的可预聚合度量（对象 → 指标定义 → 物化结果），本注册表 = 单一事实来源；
- 加载即校验，任一违规 fail-fast（对齐 contract.py V1-V5 与 config.py 的 fail-fast 纪律）；
- M1-M8 机器校验（对象白名单 / 来源表白名单 / 字段存在 / 聚合合法 / 类型兼容 / 粒度唯一 /
  id 唯一 / 命名与 transform 白名单——M8 防未来注册表成为半可信输入时的物化 SQL 注入面）；
- 5 个指标主体对象（Material + Customer/Vendor/InventoryLocation/FinanceEntry）均已注册
  （2026-08-21 Jack 拍板解除 planned 标记），M1 一律要求 object_type 可解析到已注册对象。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from src.des.config import DES_DATA_DIR

if TYPE_CHECKING:  # Registry 仅类型提示（可选注入），运行期不依赖 ontology
    from src.ontology.registry import Registry

# ---------------------------------------------------------------------------
# 常量（M1-M8 校验白名单 / 18 表列契约，设计 §1.2/§1.3 + P1b §2/§3.1）
# ---------------------------------------------------------------------------
DEFAULT_METRICS_FILE = DES_DATA_DIR / "des_metrics.yaml"

# M4 聚合函数白名单（§1.3）
AGG_FUNCTIONS = ("sum", "count", "count_distinct", "avg", "min", "max")
# M5：sum/avg/min/max 要求数值度量列（REAL）；count/count_distinct 允许任意列或 '*'
NUMERIC_AGGS = ("sum", "avg", "min", "max")
ANY_COLUMN_AGGS = ("count", "count_distinct")

# M1 已注册 DES 主体对象（P1a 注册 Material/Code；P2 注册 Customer/Vendor/InventoryLocation/
# FinanceEntry——2026-08-21 Jack 拍板解除 planned 标记；Customer 复用 S1 零售 Customer）
REGISTERED_OBJECT_TYPES = (
    "Material",
    "Customer",
    "Vendor",
    "InventoryLocation",
    "FinanceEntry",
)

# M2 来源表白名单 = DES 18 表（P1b §3.1；可选从生效配置 systems[].tables[] 派生，见 _source_table_whitelist）
DES_SOURCE_TABLES = frozenset(
    {
        "erp.MARA",
        "erp.MARC",
        "erp.MARD",
        "erp.MAST",
        "erp.STPO",
        "erp.VBAK",
        "erp.VBAP",
        "erp.KNA1",
        "mes.MPLA",
        "mes.AUFK",
        "mes.AFPO",
        "mes.COFV",
        "wms.WMMD",
        "wms.MSEG",
        "scm.LFA1",
        "scm.EKKO",
        "scm.EKPO",
        "fin.ACDOCA",
    }
)

# M3/M5 源表列契约（P1b §2 表字段，与生成实测表结构一致；供字段存在/类型兼容 + 后续物化 SQL 同源使用）
SOURCE_COLUMNS: dict[str, dict[str, str]] = {
    "erp.MARA": {
        "MATNR": "TEXT",
        "MAKTX": "TEXT",
        "MTART": "TEXT",
        "BISMT": "TEXT",
        "MEINS": "TEXT",
        "MATKL": "TEXT",
        "ERDAT": "TEXT",
    },
    "erp.MARC": {
        "MATNR": "TEXT",
        "WERKS": "TEXT",
        "MAABC": "TEXT",
        "DISPO": "TEXT",
        "EKGRP": "TEXT",
    },
    "erp.MARD": {
        "MATNR": "TEXT",
        "WERKS": "TEXT",
        "LGORT": "TEXT",
        "LABST": "REAL",
        "INSME": "REAL",
        "SPEME": "REAL",
    },
    "erp.MAST": {"MATNR": "TEXT", "WERKS": "TEXT", "STLNR": "TEXT", "STLAN": "TEXT"},
    "erp.STPO": {
        "STLNR": "TEXT",
        "STLKN": "TEXT",
        "IDNRK": "TEXT",
        "MENGE": "REAL",
        "MEINS": "TEXT",
    },
    "erp.VBAK": {
        "VBELN": "TEXT",
        "KUNNR": "TEXT",
        "AUDAT": "TEXT",
        "NETWR": "REAL",
        "VKORG": "TEXT",
    },
    "erp.VBAP": {
        "VBELN": "TEXT",
        "POSNR": "TEXT",
        "MATNR": "TEXT",
        "KWMENG": "REAL",
        "MEINS": "TEXT",
        "NETWR": "REAL",
    },
    "erp.KNA1": {"KUNNR": "TEXT", "NAME1": "TEXT", "KTOKD": "TEXT", "ORT01": "TEXT"},
    "mes.MPLA": {
        "MPLA_ID": "TEXT",
        "MATNR": "TEXT",
        "CHARG": "TEXT",
        "WERKS": "TEXT",
        "ARBPL": "TEXT",
        "VERID": "TEXT",
        "DISPO": "TEXT",
    },
    "mes.AUFK": {
        "AUFNR": "TEXT",
        "MATNR": "TEXT",
        "AUART": "TEXT",
        "WERKS": "TEXT",
        "FTRMS": "TEXT",
        "STATUS": "TEXT",
    },
    "mes.AFPO": {
        "AUFNR": "TEXT",
        "POSNR": "TEXT",
        "MATNR": "TEXT",
        "GAMNG": "REAL",
        "MEINS": "TEXT",
    },
    "mes.COFV": {
        "CONFNR": "TEXT",
        "AUFNR": "TEXT",
        "MATNR": "TEXT",
        "WERKS": "TEXT",
        "ARBPL": "TEXT",
        "DATUM": "TEXT",
        "ISM01": "REAL",
        "ISMN1": "REAL",
    },
    "wms.WMMD": {
        "MATNR": "TEXT",
        "LGORT": "TEXT",
        "LGPBE": "TEXT",
        "MEINS": "TEXT",
        "BESTQ": "TEXT",
        "ERDAT": "TEXT",
    },
    "wms.MSEG": {
        "MBLNR": "TEXT",
        "ZEILE": "TEXT",
        "MATNR": "TEXT",
        "WERKS": "TEXT",
        "LGORT": "TEXT",
        "BWART": "TEXT",
        "MENGE": "REAL",
        "MEINS": "TEXT",
        "BUDAT": "TEXT",
        "EBELN": "TEXT",
        "AUFNR": "TEXT",
    },
    "scm.LFA1": {"LIFNR": "TEXT", "NAME1": "TEXT", "ORT01": "TEXT", "LAND1": "TEXT"},
    "scm.EKKO": {"EBELN": "TEXT", "LIFNR": "TEXT", "BSART": "TEXT", "AEDAT": "TEXT"},
    "scm.EKPO": {
        "EBELN": "TEXT",
        "EBELP": "TEXT",
        "MATNR": "TEXT",
        "MENGE": "REAL",
        "MEINS": "TEXT",
        "NETWR": "REAL",
    },
    "fin.ACDOCA": {
        "BELNR": "TEXT",
        "POSNR": "TEXT",
        "RACCT": "TEXT",
        "KOSTL": "TEXT",
        "WSL": "REAL",
        "BUDAT": "TEXT",
        "REF_DOC": "TEXT",
        "REF_TYPE": "TEXT",
    },
}

# metric_id / dimension / measure 命名契约（snake_case，§1.2 + M8）
_METRIC_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# ---------------------------------------------------------------------------
# 物化存储/命名 + 时间维度识别（读侧契约共用，禁双处硬编码；metrics_materialize 同源）
# ---------------------------------------------------------------------------
METRICS_DB = "metrics.db"  # 指标物化库文件名（§2.1，企业目录下与 5 源库并列）
METRIC_TABLE_PREFIX = "metric_"  # 物化表名前缀（§2.1，metric_<id> 由注册表派生）
METRIC_META_TABLE = "metric_meta"  # 物化元表（§2.1，版本/口径锚，读侧 T3 守卫同源引用）
DATE_TRANSFORM_FUNCS = ("substr",)  # 时间派生 transform（substr(1,7) → YYYY-MM 月粒度）
_SUBSTR_LEN_RE = re.compile(r"^substr\(\s*1\s*,\s*(\d+)\s*\)$")


# M8 transform 白名单正则（函数名 ∈ DATE_TRANSFORM_FUNCS + 参数为数字/纯逗号分隔，防注入面）
_TRANSFORM_FUNC_ALT = "|".join(re.escape(f) for f in DATE_TRANSFORM_FUNCS)
_TRANSFORM_RE = re.compile(rf"^({_TRANSFORM_FUNC_ALT})\(\s*\d+\s*(?:,\s*\d+\s*)*\)$")


def _check_transform_m8(transform: str) -> str | None:
    """M8 transform 校验：函数名 ∈ DATE_TRANSFORM_FUNCS 白名单 + 参数为数字/纯逗号分隔。"""
    if _TRANSFORM_RE.match(transform.strip()) is None:
        return (
            f"transform 非法（M8）：函数名须 ∈ {list(DATE_TRANSFORM_FUNCS)}"
            f" 且参数为数字/逗号分隔: {transform!r}"
        )
    return None


def metric_table_name(metric_id: str) -> str:
    """物化表名：metric_<metric_id>（§2.1，由注册表派生，禁硬编码）。"""
    return METRIC_TABLE_PREFIX + metric_id


def is_date_dimension(dim: DimensionField) -> bool:
    """维度是否为日期维度（带时间派生 transform；v0.2 time_range 的绑定点）。"""
    if dim.transform is None:
        return False
    return dim.transform.split("(", 1)[0].strip() in DATE_TRANSFORM_FUNCS


def date_dimension_grain(dim: DimensionField) -> int | None:
    """日期维度输出粒度（字符数）：substr(1,7) → 7（YYYY-MM）、substr(1,10) → 10（YYYY-MM-DD）。

    返回 None 表示非 substr 派生（time_range 按整串比较，不截断）。
    """
    if dim.transform is None:
        return 10
    m = _SUBSTR_LEN_RE.match(dim.transform)
    return int(m.group(1)) if m else None


class MetricError(Exception):
    """指标注册表加载/校验失败（fail-fast，不静默）。"""


# ---------------------------------------------------------------------------
# 数据模型（校验通过后不可变）
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DimensionField:
    """粒度维度（物化分组键）：本体语义名 → 源列 + 可选派生 transform。"""

    name: str
    source: str  # 'TABLE.COLUMN'（表名省略系统前缀，如 'VBAP.MATNR'）
    transform: str | None = None  # 可选派生（如 'substr(1,7)' → 月）


@dataclass(frozen=True)
class Measure:
    """度量：{name（本体字段名）, source（源列 'TABLE.COLUMN' 或 '*'）}。"""

    name: str
    source: str


@dataclass(frozen=True)
class MetricDef:
    """单条指标定义（核心 7 字段，§1.2）。"""

    metric_id: str
    object_type: str
    dimension_fields: tuple[DimensionField, ...]
    measure: Measure
    agg_function: str
    definition: str
    source_tables: tuple[str, ...]


@dataclass(frozen=True)
class MetricRegistry:
    """校验通过后的指标注册表（不可变；含按对象索引）。"""

    metrics: tuple[MetricDef, ...]

    def by_id(self) -> dict[str, MetricDef]:
        return {m.metric_id: m for m in self.metrics}

    def metrics_by_object(self, object_type: str) -> tuple[MetricDef, ...]:
        """给定对象返回其全部指标（§1.4：对象可指向多个指标，供 Agent 选对象→选指标）。"""
        return tuple(m for m in self.metrics if m.object_type == object_type)


# ---------------------------------------------------------------------------
# 加载
# ---------------------------------------------------------------------------
def _load_yaml(path: Path) -> dict:
    """读取注册表 YAML，非法结构即 fail-fast。"""
    if not path.is_file():
        raise MetricError(f"指标注册表不存在: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MetricError(f"指标注册表必须为映射: {path}")
    return data


def _registered_object_types(registry: Registry | None) -> set[str]:
    """M1 已注册对象集：优先取注入 Registry，兜底 REGISTERED_OBJECT_TYPES 常量（5 主体对象）。"""
    reg = {o.name for o in registry.object_types()} if registry is not None else set()
    return reg | set(REGISTERED_OBJECT_TYPES)


def _source_table_whitelist(config: dict | None) -> set[str]:
    """M2 来源表白名单：优先从生效配置 systems[].tables[] 派生，兜底 DES_SOURCE_TABLES 常量（18 表）。"""
    if config is None:
        return set(DES_SOURCE_TABLES)
    return {
        f"{code}.{name}"
        for code, sys_cfg in config["enterprise"]["systems"].items()
        for name in sys_cfg["tables"]
    }


# ---------------------------------------------------------------------------
# 校验 M1-M8（fail-fast）
# ---------------------------------------------------------------------------
def _resolve_source(
    source: str, source_tables: tuple[str, ...]
) -> tuple[str, str] | None:
    """解析 'TABLE.COLUMN' → (表 id, 列名)；表名须唯一命中 source_tables 之一（VBAP→erp.VBAP）。"""
    parts = source.split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    matches = [t for t in source_tables if t.split(".")[-1] == parts[0]]
    if len(matches) != 1:
        return None
    return matches[0], parts[1]


def _structure_violations(raw: Any, idx: int) -> tuple[list[str], dict | None]:
    """字段级结构校验（7 字段齐全 + 类型正确）；返回 (违规, 裸指标 dict or None)。"""
    if not isinstance(raw, dict):
        return [f"指标 #{idx} 必须为映射"], None
    required = (
        "metric_id",
        "object_type",
        "dimension_fields",
        "measure",
        "agg_function",
        "definition",
        "source_tables",
    )
    missing = [k for k in required if k not in raw]
    if missing:
        return [f"指标 #{idx} 缺少字段 {missing}"], None
    v: list[str] = []
    mid = raw["metric_id"]
    if not isinstance(mid, str) or not mid:
        v.append(f"指标 #{idx}: metric_id 必须为非空字符串")
    elif not _METRIC_ID_RE.match(mid):
        v.append(f"指标 #{idx}: metric_id 命名须为 snake_case: {mid!r}")
    if not isinstance(raw["object_type"], str) or not raw["object_type"]:
        v.append(f"指标 #{idx}: object_type 必须为非空字符串")
    if not isinstance(raw["definition"], str) or not raw["definition"]:
        v.append(f"指标 #{idx}: definition 必须为非空字符串")
    if not isinstance(raw["agg_function"], str) or not raw["agg_function"]:
        v.append(f"指标 #{idx}: agg_function 必须为非空字符串")
    dims = raw["dimension_fields"]
    if not isinstance(dims, list) or not dims:
        v.append(f"指标 #{idx}: dimension_fields 必须为非空数组（M6）")
    else:
        for pos, d in enumerate(dims):
            if (
                not isinstance(d, dict)
                or not isinstance(d.get("name"), str)
                or not d.get("name")
                or not isinstance(d.get("source"), str)
                or not d.get("source")
            ):
                v.append(f"指标 #{idx}: dimension_fields[{pos}] 必须含非空 name/source")
                continue
            tr = d.get("transform")
            if tr is not None and not isinstance(tr, str):
                v.append(
                    f"指标 #{idx}: dimension_fields[{pos}].transform 必须为字符串或 null"
                )
    m = raw["measure"]
    if (
        not isinstance(m, dict)
        or not isinstance(m.get("name"), str)
        or not m.get("name")
        or not isinstance(m.get("source"), str)
        or not m.get("source")
    ):
        v.append(f"指标 #{idx}: measure 必须为 {{name, source}} 且非空")
    st = raw["source_tables"]
    if (
        not isinstance(st, list)
        or not st
        or not all(isinstance(t, str) and t for t in st)
    ):
        v.append(f"指标 #{idx}: source_tables 必须为非空字符串数组")
    return (v, raw if not v else None)


def _check_m1_m2_m4(
    raw: dict, idx: int, registered: set[str], whitelist: set[str]
) -> list[str]:
    """M1 对象白名单 / M2 来源表白名单 / M4 聚合函数合法。"""
    v: list[str] = []
    ot = raw["object_type"]
    if ot not in registered:
        v.append(
            f"指标 #{idx}: object_type 未注册（M1）: {ot!r}（已注册={sorted(registered)}）"
        )
    for t in raw["source_tables"]:
        if t not in whitelist:
            v.append(f"指标 #{idx}: source_tables 不在 18 表白名单（M2）: {t!r}")
    if raw["agg_function"] not in AGG_FUNCTIONS:
        v.append(
            f"指标 #{idx}: agg_function 非法（M4）: {raw['agg_function']!r}"
            f"（应为 {list(AGG_FUNCTIONS)}）"
        )
    return v


def _check_m3_m5(raw: dict, idx: int) -> list[str]:
    """M3 字段存在（维度/度量列 ∈ 源表列契约）+ M5 度量类型兼容 + 维度名唯一（M6 单条）。"""
    v: list[str] = []
    st = tuple(raw["source_tables"])
    agg = raw["agg_function"]
    dim_names: list[str] = []
    for pos, d in enumerate(raw["dimension_fields"]):
        resolved = _resolve_source(d["source"], st)
        if resolved is None:
            v.append(
                f"指标 #{idx}: 维度 source 无法解析到来源表（M3）: {d['source']!r}"
            )
        else:
            table_id, column = resolved
            if column not in SOURCE_COLUMNS.get(table_id, {}):
                v.append(f"指标 #{idx}: 维度列不存在（M3）: {table_id}.{column}")
        if d["name"] in dim_names:
            v.append(f"指标 #{idx}: 维度名重复（M6）: {d['name']!r}")
        dim_names.append(d["name"])
    src = raw["measure"]["source"]
    if src == "*":
        if agg not in ANY_COLUMN_AGGS:
            v.append(
                f"指标 #{idx}: measure.source='*' 仅 count/count_distinct 允许（M5）: {agg}"
            )
        return v
    resolved = _resolve_source(src, st)
    if resolved is None:
        v.append(f"指标 #{idx}: measure source 无法解析到来源表（M3）: {src!r}")
        return v
    table_id, column = resolved
    col_type = SOURCE_COLUMNS.get(table_id, {}).get(column)
    if col_type is None:
        v.append(f"指标 #{idx}: 度量列不存在（M3）: {table_id}.{column}")
        return v
    if agg in NUMERIC_AGGS and col_type != "REAL":
        v.append(
            f"指标 #{idx}: {agg} 要求数值度量列（M5）: {table_id}.{column} 类型 {col_type!r}"
        )
    return v


def _check_m6_grain_m7(
    raw: dict, idx: int, seen_grains: dict[tuple, int], seen_ids: dict[str, int]
) -> list[str]:
    """M6 粒度唯一（同 对象×维度×度量×聚合 不得重复）+ M7 metric_id 唯一。"""
    v: list[str] = []
    mid = raw["metric_id"]
    if mid in seen_ids:
        v.append(
            f"指标 #{idx}: metric_id 重复（M7）: {mid!r}（首次出现于 #{seen_ids[mid]}）"
        )
    else:
        seen_ids[mid] = idx
    dims = tuple(sorted(d["name"] for d in raw["dimension_fields"]))
    grain = (raw["object_type"], dims, raw["measure"]["name"], raw["agg_function"])
    prev = seen_grains.get(grain)
    if prev is not None:
        v.append(f"指标 #{idx}: 粒度重复（M6，物化行歧义）: {grain!r} 与 #{prev} 相同")
    else:
        seen_grains[grain] = idx
    return v


def _check_m8_naming_transform(raw: dict, idx: int) -> list[str]:
    """M8 命名 + transform 白名单（red-team P2-8 纵深防御）：dimension/measure name 须
    snake_case（^[a-z][a-z0-9_]*$，复用 metric_id 正则）；transform 函数名 ∈ 白名单且
    参数为数字/纯逗号分隔——防未来注册表成为半可信输入时的物化 SQL 注入面。"""
    v: list[str] = []
    for pos, d in enumerate(raw["dimension_fields"]):
        name = d.get("name")
        if isinstance(name, str) and not _METRIC_ID_RE.match(name):
            v.append(f"指标 #{idx}: dimension name 命名须为 snake_case（M8）: {name!r}")
        tr = d.get("transform")
        if isinstance(tr, str):
            err = _check_transform_m8(tr)
            if err:
                v.append(f"指标 #{idx}: dimension_fields[{pos}] {err}")
    m = raw["measure"]
    mname = m.get("name") if isinstance(m, dict) else None
    if isinstance(mname, str) and not _METRIC_ID_RE.match(mname):
        v.append(f"指标 #{idx}: measure name 命名须为 snake_case（M8）: {mname!r}")
    return v


def _to_metric(raw: dict) -> MetricDef:
    """把通过校验的裸 dict 转成不可变 MetricDef。"""
    dims = tuple(
        DimensionField(name=d["name"], source=d["source"], transform=d.get("transform"))
        for d in raw["dimension_fields"]
    )
    return MetricDef(
        metric_id=raw["metric_id"],
        object_type=raw["object_type"],
        dimension_fields=dims,
        measure=Measure(name=raw["measure"]["name"], source=raw["measure"]["source"]),
        agg_function=raw["agg_function"],
        definition=raw["definition"],
        source_tables=tuple(raw["source_tables"]),
    )


# ---------------------------------------------------------------------------
# 公开入口
# ---------------------------------------------------------------------------
def load_metrics(
    path: str | Path | None = None,
    *,
    registry: Registry | None = None,
    config: dict | None = None,
) -> MetricRegistry:
    """加载指标注册表 YAML 并执行 M1-M8 校验（fail-fast，任一违规抛 MetricError）。

    参数：
        path：注册表 YAML 路径（默认 data/des/des_metrics.yaml）；
        registry：可选本体 Registry（M1 已注册对象集；不传时用内置 5 主体对象集）；
        config：可选生效配置（M2 来源表白名单派生；不传时用 18 表常量）。
    返回：MetricRegistry（metrics / by_id / metrics_by_object）。
    """
    yaml_path = Path(path) if path is not None else DEFAULT_METRICS_FILE
    data = _load_yaml(yaml_path)
    raw_metrics = data.get("metrics")
    if not isinstance(raw_metrics, list) or not raw_metrics:
        raise MetricError(f"注册表 metrics 必须为非空数组: {yaml_path}")
    registered = _registered_object_types(registry)
    whitelist = _source_table_whitelist(config)
    metrics: list[MetricDef] = []
    seen_ids: dict[str, int] = {}
    seen_grains: dict[tuple, int] = {}
    for idx, raw in enumerate(raw_metrics):
        struct_v, valid = _structure_violations(raw, idx)
        violations = list(struct_v)
        if valid is not None:
            violations.extend(_check_m1_m2_m4(valid, idx, registered, whitelist))
            violations.extend(_check_m3_m5(valid, idx))
            violations.extend(_check_m6_grain_m7(valid, idx, seen_grains, seen_ids))
            violations.extend(_check_m8_naming_transform(valid, idx))
        if violations:
            raise MetricError(
                f"{yaml_path}: 指标 #{idx} 校验失败: " + "; ".join(violations)
            )
        metric = _to_metric(valid)
        metrics.append(metric)
    return MetricRegistry(metrics=tuple(metrics))
