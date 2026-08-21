"""DES 确定性数据生成器 —— 制造型企业 5 源系统 18 张表（9 主数据 + 9 事务，合计 1,000,000 行）。

依据 docs/P1b-DES-横向铺开设计_v0.1.md（§2/§3/§4/§5）：
- 表注册表驱动：TABLE_SPECS（表 → DDL + 行生成器）；build_enterprise 按 config 表规格的
  depends_on 拓扑序执行（约定 5：生成顺序固定；阶段 1 主数据 → 阶段 2 事务，§5.2）；
- 每表独立 RNG 流：random.Random(f"{seed}:{table_id}")，table_id 固定（约定 1 扩展）；
- 稳定排序：所有集合按各自主键升序生成/落库（约定 2）；
- 纯函数派生：批次/库位/旧码/校验码/日期/数量全为 seed 随机 + 固定模式（约定 3）；
- 一物多码：仅 ERP.MARA 15%（精确 1,200 行）注入 BISMT 旧码 HC-{year}{seq:05d}（§2.1/§5.2）；
- 跨系统一致性：MPLA/WMMD 1:1 对齐 MARA 主码、WMMD.MEINS 复制 MARA.MEINS（D1-D3/D9）；
- 事务表（§2.4-2.6）：EKKO/EKPO、VBAK/VBAP、AUFK/AFPO/COFV、MSEG、ACDOCA，合计 861,000 行，
  跨系统 FK 无孤儿（D4-D8）；MSEG 生成器先定 MARD 账面、再生成流水使净变 = LABST（D10 对账 diff=0）；
- ACDOCA REF_DOC 确定性抽样映射 VBELN/EBELN/MBLNR（D8，REF 无孤儿，§2.5 R4 推荐）。
"""

from __future__ import annotations

import random
import sqlite3
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .config import (
    DEFAULT_ENTERPRISES_DIR,
    DesConfigError,
    load_config,
)
from .manifest import build_manifest

# ---------------------------------------------------------------------------
# 常量（确定性锚点，与设计 §2/§3.2 对齐）
# ---------------------------------------------------------------------------
CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32 字符，剔除易混 0/O/1/I（§3.2）
ANCHOR_START = date(2025, 1, 1)
ANCHOR_END = date(2026, 12, 31)

MATERIAL_TYPES = ("FERT", "HALB", "ROH", "VERP", "HAWA")  # 枚举：成品/半成品/原材料/包装/贸易商品
UNITS = ("PC", "EA", "KG", "M", "箱", "SET")
MATERIAL_NAMES = (
    "铝合金外壳", "不锈钢紧固件", "伺服电机", "精密齿轮", "滚珠轴承",
    "PCB 主板", "散热模组", "注塑壳体", "线束总成", "气动元件",
    "减速器箱体", "密封圈", "传感器模组", "钣金支架", "数控刀具",
    "驱动控制板", "橡胶衬套", "冲压件", "联轴器", "紧固标准件",
)
NAME_VARIANTS = ("A 型", "B 型", "C 型", "标准型", "加强型", "轻量型")
WERKS_POOL = ("PL01", "PL02")
ARBPL_POOL = ("WC-ASSY-01", "WC-CNC-01", "WC-MOLD-02", "WC-TEST-01", "WC-PACK-01")
VERID_POOL = ("01", "02", "03")
DISPO_POOL = ("MRP-01", "MRP-02", "MRP-03")
LGORT_POOL = ("W01", "W02", "W03")
LGORT_PLANT = {"W01": "PL01", "W02": "PL02", "W03": "PL01"}  # 库存地点 → 所属工厂（MARD）
BESTQ_POOL = ("非限制", "非限制", "非限制", "质检", "冻结")  # 权重模拟：非限制为主
ZONE_POOL = ("A", "B", "C")
MAABC_POOL = ("A", "B", "C")  # ABC 分类（MARC）
EKGRP_POOL = ("E01", "E02", "E03")  # 采购组（MARC）
VENDOR_CODE_PREFIX = "SU"  # 供应商号前缀（§2.4 编码规则）
CUSTOMER_CODE_PREFIX = "CU"  # 客户号前缀（§2.1 编码规则）
CODE_WIDTH = 8  # 供应商/客户定宽序号位数（SU-00000001）
LAND1 = "CN"
KTOKD_POOL = ("0001", "0002", "0003")  # 客户账户组：零售/中小企业/集团
CITY_POOL = ("深圳", "上海", "苏州", "东莞", "杭州", "宁波", "青岛", "天津", "成都", "武汉", "佛山", "合肥")
VENDOR_NAMES = (
    "东成金属材料", "南方精密零件", "恒力标准件", "瑞鑫塑胶制品", "长城模具钢",
    "华东电子元件", "精工轴承", "天工传动件", "顺达包装材料", "晶圆半导体材料",
    "华泰紧固件", "立讯传感器", "中兴线缆", "山河液压件", "博世电机配件",
)
CUSTOMER_NAMES = (
    "华北智能装备", "联盛机电", "拓维自动化", "凯捷电子", "中科智能",
    "精诚数控", "蓝海机器人", "瑞驰汽车零部件", "恒泰家电", "广达工控",
    "远望通讯", "江川泵业", "长虹智能家居", "力神电池", "欧姆电子",
)
NAME_SUFFIXES = ("有限公司", "集团", "股份公司", "有限责任公司")
BOM_PARENT_TYPES = ("FERT", "HALB")  # BOM 所属成品/半成品（MAST）
BOM_STLAN = "1"  # BOM 用途（1=生产）
BOM_ITEM_STEP = 10  # STPO.STLKN 步长（00010 起，SAP 习惯）
STPO_ITEMS_PER_BOM = 5  # BOM 平均组件数（10,000 × 5 = 50,000，§3.3 比率 1:5）

# —— 事务表常量（§2 编码规则总表 / §2.1-2.5 业务枚举，常量化禁硬编码）——
DOC_CODE_WIDTH = 6  # 单据码序号位数（PO/SO/WO/CF/MV/FI，NNNNNN 6 位，单年 99.9 万行上限）
VKORG = "1000"  # 销售组织（VBAK）
BSART = "NB"  # 采购订单类型：标准（EKKO）
AUART = "PPSM"  # 生产工单类型：生产（AUFK）
STATUS_POOL = ("REL", "PCNF", "DLV", "CLSD")  # 工单状态：下达/部分确认/交付/关闭（过滤查询载体）
RECEIPT_BWART = ("101", "301")  # 收货移动类型：101 采购收货 / 301 移库入库（§2.3）
ISSUE_BWART = ("201", "261", "301")  # 发料移动类型：201 发料 / 261 生产发料 / 301 移库出库
RACCT_POOL = ("100101", "100201", "112201", "140501", "140502", "140503",
              "220201", "500101", "600101")  # 会计科目池（ACDOCA）
KOSTL_POOL = ("CC-PROD-01", "CC-PROD-02", "CC-ASSY-01", "CC-ADMIN-01", "CC-SALES-01")
ACDOCA_REF_SPLIT = (0.4, 0.3, 0.3)  # ACDOCA 参考单据抽样比例 SO/PO/MV（§2.5 R4，Σ=41,000）
VBAK_ITEMS_LO, VBAK_ITEMS_HI = 1, 4  # 每销售订单项目数范围（均值 2.5 → 40k:100k，§3.3）
EKPO_ITEMS_LO, EKPO_ITEMS_HI = 1, 4  # 每采购订单项目数范围（均值 2.67 → 30k:80k，§3.3）
AFPO_ITEMS_LO, AFPO_ITEMS_HI = 1, 2  # 每工单项目数范围（均值 1.33 → 90k:120k，§3.3）
COFV_ITEMS_LO, COFV_ITEMS_HI = 1, 3  # 每工单报工次数范围（均值 2 → 90k:180k，§3.3）
MSEG_COUNT_LO, MSEG_COUNT_HI = 5, 9  # 每 (MATNR,LGORT) 账面行移动笔数（奇；收发对 + 锚点，D10）

# ---------------------------------------------------------------------------
# 九张主数据表 DDL（设计 §2.1/§2.2/§2.3/§2.4；MARA/MPLA/WMMD 字段不变 = 兼容红线）
# 注：跨系统一致性不靠数据库外键（库与库之间无 FK，§5.2-3），由 D 门禁与本体语义层校验。
# ---------------------------------------------------------------------------
MARA_DDL = """
CREATE TABLE MARA (
  MATNR TEXT PRIMARY KEY,
  MAKTX TEXT NOT NULL,
  MTART TEXT NOT NULL CHECK (MTART IN ('FERT','HALB','ROH','VERP','HAWA')),
  BISMT TEXT,
  MEINS TEXT NOT NULL,
  MATKL TEXT NOT NULL,
  ERDAT TEXT NOT NULL
);
"""
LFA1_DDL = """
CREATE TABLE LFA1 (
  LIFNR TEXT PRIMARY KEY,
  NAME1 TEXT NOT NULL,
  ORT01 TEXT NOT NULL,
  LAND1 TEXT NOT NULL
);
"""
KNA1_DDL = """
CREATE TABLE KNA1 (
  KUNNR TEXT PRIMARY KEY,
  NAME1 TEXT NOT NULL,
  KTOKD TEXT NOT NULL,
  ORT01 TEXT NOT NULL
);
"""
MARC_DDL = """
CREATE TABLE MARC (
  MATNR TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  MAABC TEXT NOT NULL CHECK (MAABC IN ('A','B','C')),
  DISPO TEXT NOT NULL,
  EKGRP TEXT NOT NULL,
  PRIMARY KEY (MATNR, WERKS)
);
"""
MARD_DDL = """
CREATE TABLE MARD (
  MATNR TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  LGORT TEXT NOT NULL,
  LABST REAL NOT NULL,
  INSME REAL NOT NULL,
  SPEME REAL NOT NULL,
  PRIMARY KEY (MATNR, WERKS, LGORT)
);
"""
MAST_DDL = """
CREATE TABLE MAST (
  MATNR TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  STLNR TEXT NOT NULL,
  STLAN TEXT NOT NULL,
  PRIMARY KEY (MATNR, WERKS, STLNR)
);
"""
STPO_DDL = """
CREATE TABLE STPO (
  STLNR TEXT NOT NULL,
  STLKN TEXT NOT NULL,
  IDNRK TEXT NOT NULL,
  MENGE REAL NOT NULL,
  MEINS TEXT NOT NULL,
  PRIMARY KEY (STLNR, STLKN)
);
"""
MPLA_DDL = """
CREATE TABLE MPLA (
  MPLA_ID TEXT PRIMARY KEY,
  MATNR TEXT NOT NULL UNIQUE,
  CHARG TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  ARBPL TEXT NOT NULL,
  VERID TEXT NOT NULL,
  DISPO TEXT NOT NULL
);
"""
WMMD_DDL = """
CREATE TABLE WMMD (
  MATNR TEXT PRIMARY KEY,
  LGORT TEXT NOT NULL,
  LGPBE TEXT NOT NULL,
  MEINS TEXT NOT NULL,
  BESTQ TEXT NOT NULL CHECK (BESTQ IN ('非限制','质检','冻结')),
  ERDAT TEXT NOT NULL
);
"""
VBAK_DDL = """
CREATE TABLE VBAK (
  VBELN TEXT PRIMARY KEY,
  KUNNR TEXT NOT NULL,
  AUDAT TEXT NOT NULL,
  NETWR REAL NOT NULL,
  VKORG TEXT NOT NULL
);
"""
VBAP_DDL = """
CREATE TABLE VBAP (
  VBELN TEXT NOT NULL,
  POSNR TEXT NOT NULL,
  MATNR TEXT NOT NULL,
  KWMENG REAL NOT NULL,
  MEINS TEXT NOT NULL,
  NETWR REAL NOT NULL,
  PRIMARY KEY (VBELN, POSNR)
);
"""
EKKO_DDL = """
CREATE TABLE EKKO (
  EBELN TEXT PRIMARY KEY,
  LIFNR TEXT NOT NULL,
  BSART TEXT NOT NULL,
  AEDAT TEXT NOT NULL
);
"""
EKPO_DDL = """
CREATE TABLE EKPO (
  EBELN TEXT NOT NULL,
  EBELP TEXT NOT NULL,
  MATNR TEXT NOT NULL,
  MENGE REAL NOT NULL,
  MEINS TEXT NOT NULL,
  NETWR REAL NOT NULL,
  PRIMARY KEY (EBELN, EBELP)
);
"""
AUFK_DDL = """
CREATE TABLE AUFK (
  AUFNR TEXT PRIMARY KEY,
  MATNR TEXT NOT NULL,
  AUART TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  FTRMS TEXT NOT NULL,
  STATUS TEXT NOT NULL
);
"""
AFPO_DDL = """
CREATE TABLE AFPO (
  AUFNR TEXT NOT NULL,
  POSNR TEXT NOT NULL,
  MATNR TEXT NOT NULL,
  GAMNG REAL NOT NULL,
  MEINS TEXT NOT NULL,
  PRIMARY KEY (AUFNR, POSNR)
);
"""
COFV_DDL = """
CREATE TABLE COFV (
  CONFNR TEXT PRIMARY KEY,
  AUFNR TEXT NOT NULL,
  MATNR TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  ARBPL TEXT NOT NULL,
  DATUM TEXT NOT NULL,
  ISM01 REAL NOT NULL,
  ISMN1 REAL NOT NULL
);
"""
MSEG_DDL = """
CREATE TABLE MSEG (
  MBLNR TEXT NOT NULL,
  ZEILE TEXT NOT NULL,
  MATNR TEXT NOT NULL,
  WERKS TEXT NOT NULL,
  LGORT TEXT NOT NULL,
  BWART TEXT NOT NULL,
  MENGE REAL NOT NULL,
  MEINS TEXT NOT NULL,
  BUDAT TEXT NOT NULL,
  EBELN TEXT,
  AUFNR TEXT,
  PRIMARY KEY (MBLNR, ZEILE)
);
"""
ACDOCA_DDL = """
CREATE TABLE ACDOCA (
  BELNR TEXT NOT NULL,
  POSNR TEXT NOT NULL,
  RACCT TEXT NOT NULL,
  KOSTL TEXT NOT NULL,
  WSL REAL NOT NULL,
  BUDAT TEXT NOT NULL,
  REF_DOC TEXT NOT NULL,
  REF_TYPE TEXT NOT NULL CHECK (REF_TYPE IN ('SO','PO','MV')),
  PRIMARY KEY (BELNR, POSNR)
);
"""


# ---------------------------------------------------------------------------
# 主编码规则 MAT-YYYY-NNNN-CCC（§3.2，确定性、跨语言可重算）
# ---------------------------------------------------------------------------
def check_code(year: int, seq: int) -> str:
    """计算 MAT-YYYY-NNNN-CCC 的 3 位校验码 CCC（32 位乘法散列，§3.2）。"""
    n = year * 10000 + seq
    r0 = (n * 2654435761) & 0xFFFFFFFF
    return CHARS[r0 % 32] + CHARS[(r0 >> 5) % 32] + CHARS[(r0 >> 10) % 32]


def master_code(year: int, seq: int) -> str:
    """主码 MAT-YYYY-NNNN-CCC：seq 从 1 起的 4 位顺序号（企业物料宇宙内唯一）。"""
    return f"MAT-{year:04d}-{seq:04d}-{check_code(year, seq)}"


def sequence_code(prefix: str, seq: int, width: int = CODE_WIDTH) -> str:
    """定宽顺序码 SU-00000001 / CU-00000001（§2.4/§2.1 编码规则，8 位序号）。"""
    return f"{prefix}-{seq:0{width}d}"


def document_code(prefix: str, year: int, seq: int) -> str:
    """单据码 {prefix}-{year:04d}-{seq:06d}（§2 编码规则总表，NNNNNN 6 位）。

    承载 PO/SO/WO/CF/MV/FI 六类单据；单年 6 位序号上限 999,999，覆盖最大表（COFV/MSEG 180,000）。
    """
    return f"{prefix}-{year:04d}-{seq:0{DOC_CODE_WIDTH}d}"


# ---------------------------------------------------------------------------
# 纯函数派生（§4 约定 3：无墙钟、无可变全局状态）
# ---------------------------------------------------------------------------
def random_date(rng: random.Random) -> str:
    """ANCHOR_START..ANCHOR_END 间随机日期 YYYY-MM-DD（seed 确定性派生）。"""
    span = (ANCHOR_END - ANCHOR_START).days
    day = ANCHOR_START + timedelta(days=rng.randint(0, span))
    return day.strftime("%Y-%m-%d")


def generate_mara_rows(rng: random.Random, year: int, count: int) -> list[dict[str, Any]]:
    """ERP.MARA 物料主数据（§2.1）：MATNR 升序生成，BISMT 待注入阶段回填（字段不变）。"""
    rows: list[dict[str, Any]] = []
    for seq in range(1, count + 1):
        mtype = rng.choice(MATERIAL_TYPES)
        rows.append(
            {
                "MATNR": master_code(year, seq),
                "MAKTX": f"{rng.choice(MATERIAL_NAMES)}{rng.choice(NAME_VARIANTS)}",
                "MTART": mtype,
                "BISMT": None,
                "MEINS": rng.choice(UNITS),
                "MATKL": f"Z-{mtype}-{seq % 50 + 1:02d}",
                "ERDAT": random_date(rng),
            }
        )
    return rows


def inject_legacy_codes(
    rng: random.Random,
    mara_rows: list[dict[str, Any]],
    rate: float,
    legacy_pattern: str,
    prefix: str,
    year: int,
) -> tuple[list[dict[str, Any]], int]:
    """一物多码注入（§3.3）：返回 (新行列表, 注入行数)。

    - 目标数 count = round(N × rate)，N=8,000 → 精确 1,200 行（15.00%）；
    - 选择：rng.sample(按 MATNR 升序的物料宇宙, count)，seed 确定 → 行集固定（约定 2/3）；
    - 旧码：按 MATNR 升序赋予 seq=1..count，格式 legacy_pattern（HC-{year}{seq:05d}），互异。
    """
    count = round(len(mara_rows) * rate)
    sorted_matnrs = sorted(r["MATNR"] for r in mara_rows)
    selected = set(rng.sample(sorted_matnrs, count))
    legacy_by_matnr: dict[str, str] = {}
    for idx, matnr in enumerate(sorted(selected), start=1):
        legacy_by_matnr[matnr] = legacy_pattern.format(prefix=prefix, year=year, seq=idx)
    rows = []
    for row in sorted(mara_rows, key=lambda r: r["MATNR"]):
        rows.append({**row, "BISMT": legacy_by_matnr.get(row["MATNR"])})
    return rows, count


# ---------------------------------------------------------------------------
# 生成上下文工具
# ---------------------------------------------------------------------------
def _row_count(ctx: dict[str, Any], table_id: str) -> int:
    """从配置表注册表读某表 row_count（配置为单一事实来源）。"""
    code, name = table_id.split(".", 1)
    return ctx["config"]["enterprise"]["systems"][code]["tables"][name]["row_count"]


def _sort_rows(rows: list[dict[str, Any]], pk: list[str]) -> list[dict[str, Any]]:
    """按主键列升序稳定排序（约定 2：按自然键排序落库）。"""
    return sorted(rows, key=lambda r: tuple(r[c] for c in pk))


def _distribute_counts(
    rng: random.Random,
    n: int,
    total: int,
    lo: int,
    hi: int,
    step: int = 1,
) -> list[int]:
    """把 total 行数分配到 n 个父单据（每份 ∈ [lo,hi] 且步长 step），确定性收敛。

    父子单据比率（§3.3）落地：先按 seed 随机给初值，再单向微调索引使 Σ = total 精确；
    要求 lo*n ≤ total ≤ hi*n 且 total 与初值之和同余（step），否则进入无限循环（fail-fast 由调用方保证）。
    """
    counts = [rng.randrange(lo, hi + 1, step) for _ in range(n)]
    diff = total - sum(counts)
    while diff > 0:
        i = rng.randrange(n)
        if counts[i] + step <= hi:
            counts[i] += step
            diff -= step
    while diff < 0:
        i = rng.randrange(n)
        if counts[i] - step >= lo:
            counts[i] -= step
            diff += step
    return counts


# ---------------------------------------------------------------------------
# 九张主数据表行生成器（每表独立 RNG 流，约定 1 扩展）
# ---------------------------------------------------------------------------
def generate_lfa1_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """SCM.LFA1 供应商主数据（§2.4）：SU-00000001 起 8 位定宽码，5,000 行。"""
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "scm.LFA1") + 1):
        rows.append(
            {
                "LIFNR": sequence_code(VENDOR_CODE_PREFIX, seq),
                "NAME1": f"{rng.choice(VENDOR_NAMES)}{rng.choice(NAME_SUFFIXES)}",
                "ORT01": rng.choice(CITY_POOL),
                "LAND1": LAND1,
            }
        )
    return rows


def generate_kna1_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.KNA1 客户主数据（§2.1）：CU-00000001 起 8 位定宽码，10,000 行。"""
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "erp.KNA1") + 1):
        rows.append(
            {
                "KUNNR": sequence_code(CUSTOMER_CODE_PREFIX, seq),
                "NAME1": f"{rng.choice(CUSTOMER_NAMES)}{rng.choice(NAME_SUFFIXES)}",
                "KTOKD": rng.choice(KTOKD_POOL),
                "ORT01": rng.choice(CITY_POOL),
            }
        )
    return rows


def generate_erp_mara(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.MARA 物料主数据（§2.1，字段不变）：MATNR 升序 + 15% 一物多码注入 BISMT。"""
    year = ctx["year"]
    rows = generate_mara_rows(rng, year, _row_count(ctx, "erp.MARA"))
    multi = ctx["config"]["injection"]["multi_code"]
    rows, _ = inject_legacy_codes(
        rng, rows, multi["rate"], multi["legacy_pattern"], ctx["code_prefix"], year
    )
    return rows


def generate_marc_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.MARC 物料工厂数据（§2.1）：8,000 物料 × 2 工厂 PL01/PL02 = 16,000 行。"""
    rows: list[dict[str, Any]] = []
    for m in ctx["erp.MARA"]:
        for werks in WERKS_POOL:
            rows.append(
                {
                    "MATNR": m["MATNR"],
                    "WERKS": werks,
                    "MAABC": rng.choice(MAABC_POOL),
                    "DISPO": rng.choice(DISPO_POOL),
                    "EKGRP": rng.choice(EKGRP_POOL),
                }
            )
    return rows


def generate_mard_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.MARD 库存地点库存（§2.1）：8,000 物料 × 3 地点 = 24,000 行，LABST 账面库存。"""
    rows: list[dict[str, Any]] = []
    for m in ctx["erp.MARA"]:
        for lgort in LGORT_POOL:
            rows.append(
                {
                    "MATNR": m["MATNR"],
                    "WERKS": LGORT_PLANT[lgort],
                    "LGORT": lgort,
                    "LABST": round(rng.uniform(100, 5000), 2),
                    "INSME": round(rng.uniform(0, 300), 2),
                    "SPEME": round(rng.uniform(0, 100), 2),
                }
            )
    return rows


def generate_mast_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.MAST BOM 链接表（§2.1）：10,000 BOM 头 BO-YYYY-NNNNNN，父物料取 FERT/HALB。"""
    year = ctx["year"]
    parents = [m["MATNR"] for m in ctx["erp.MARA"] if m["MTART"] in BOM_PARENT_TYPES]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "erp.MAST") + 1):
        rows.append(
            {
                "MATNR": rng.choice(parents),
                "WERKS": rng.choice(WERKS_POOL),
                "STLNR": f"BO-{year:04d}-{seq:06d}",
                "STLAN": BOM_STLAN,
            }
        )
    return rows


def generate_stpo_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.STPO BOM 项目（§2.1）：10,000 BOM × 5 组件 = 50,000 行，IDNRK FK→MARA。"""
    mara = ctx["erp.MARA"]
    all_matnrs = [m["MATNR"] for m in mara]
    parent_idx = {matnr: i for i, matnr in enumerate(all_matnrs)}
    meins_by_matnr = {m["MATNR"]: m["MEINS"] for m in mara}
    n = len(all_matnrs)
    rows: list[dict[str, Any]] = []
    for mast in ctx["erp.MAST"]:
        pidx = parent_idx[mast["MATNR"]]
        # 排除父物料自身：从 n-1 个候选索引采样，>= pidx 顺移 1 位（O(1) 排除，确定性）
        comps = [
            all_matnrs[i if i < pidx else i + 1]
            for i in rng.sample(range(n - 1), STPO_ITEMS_PER_BOM)
        ]
        for idx, matnr in enumerate(comps, start=1):
            rows.append(
                {
                    "STLNR": mast["STLNR"],
                    "STLKN": f"{idx * BOM_ITEM_STEP:05d}",
                    "IDNRK": matnr,
                    "MENGE": round(rng.uniform(0.5, 20), 2),
                    "MEINS": meins_by_matnr[matnr],
                }
            )
    return rows


def generate_mpla_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """MES.MPLA 生产物料主数据（§2.2，字段不变）：1:1 对齐 MARA，MPLA_ID = MP-<MATNR>。"""
    rows: list[dict[str, Any]] = []
    for m in ctx["erp.MARA"]:
        day = random_date(rng).replace("-", "")
        rows.append(
            {
                "MPLA_ID": f"MP-{m['MATNR']}",
                "MATNR": m["MATNR"],
                "CHARG": f"L{day}{rng.randint(1, 999):03d}",
                "WERKS": rng.choice(WERKS_POOL),
                "ARBPL": rng.choice(ARBPL_POOL),
                "VERID": rng.choice(VERID_POOL),
                "DISPO": rng.choice(DISPO_POOL),
            }
        )
    return rows


def generate_wmmd_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """WMS.WMMD 仓储侧物料主档（§2.3，字段不变）：MATNR 即主键，MEINS 复制 MARA（D3 一致性）。"""
    rows: list[dict[str, Any]] = []
    for m in ctx["erp.MARA"]:
        rows.append(
            {
                "MATNR": m["MATNR"],
                "LGORT": rng.choice(LGORT_POOL),
                "LGPBE": (
                    f"{rng.choice(ZONE_POOL)}-{rng.randint(1, 9):02d}"
                    f"-{rng.randint(1, 9):02d}-{rng.randint(1, 5):02d}"
                ),
                "MEINS": m["MEINS"],
                "BESTQ": rng.choice(BESTQ_POOL),
                "ERDAT": random_date(rng),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# 九张事务/流水表行生成器（§2.4-2.6；每表独立 RNG 流，引用主数据/上级单据确定性输出）
# ---------------------------------------------------------------------------
def generate_ekko_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """SCM.EKKO 采购订单抬头（§2.4）：PO-YYYY-NNNNNN，30,000 单，LIFNR FK→LFA1。"""
    year = ctx["year"]
    lfa1_keys = [l["LIFNR"] for l in ctx["scm.LFA1"]]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "scm.EKKO") + 1):
        rows.append(
            {
                "EBELN": document_code("PO", year, seq),
                "LIFNR": rng.choice(lfa1_keys),
                "BSART": BSART,
                "AEDAT": random_date(rng),
            }
        )
    return rows


def generate_ekpo_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """SCM.EKPO 采购订单项目（§2.4）：30,000 单 × 平均 2.67 项目 = 80,000 行。

    MENGE/MEINS 随物料确定性派生（MEINS 复制 MARA，跨表单位一致）。
    """
    mara = ctx["erp.MARA"]
    matnrs = [m["MATNR"] for m in mara]
    meins_by = {m["MATNR"]: m["MEINS"] for m in mara}
    counts = _distribute_counts(
        rng, _row_count(ctx, "scm.EKKO"), _row_count(ctx, "scm.EKPO"),
        EKPO_ITEMS_LO, EKPO_ITEMS_HI,
    )
    rows: list[dict[str, Any]] = []
    for ekko, c in zip(ctx["scm.EKKO"], counts):
        for pos in range(1, c + 1):
            matnr = rng.choice(matnrs)
            rows.append(
                {
                    "EBELN": ekko["EBELN"],
                    "EBELP": f"{pos:05d}",
                    "MATNR": matnr,
                    "MENGE": round(rng.uniform(1, 1000), 2),
                    "MEINS": meins_by[matnr],
                    "NETWR": round(rng.uniform(5, 10000), 2),
                }
            )
    return rows


def generate_vbak_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.VBAK 销售订单抬头（§2.1）：SO-YYYY-NNNNNN，40,000 单，KUNNR FK→KNA1。"""
    year = ctx["year"]
    kna1_keys = [k["KUNNR"] for k in ctx["erp.KNA1"]]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "erp.VBAK") + 1):
        rows.append(
            {
                "VBELN": document_code("SO", year, seq),
                "KUNNR": rng.choice(kna1_keys),
                "AUDAT": random_date(rng),
                "NETWR": round(rng.uniform(100, 100000), 2),
                "VKORG": VKORG,
            }
        )
    return rows


def generate_vbap_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """ERP.VBAP 销售订单项目（§2.1）：40,000 单 × 平均 2.5 项目 = 100,000 行。"""
    mara = ctx["erp.MARA"]
    matnrs = [m["MATNR"] for m in mara]
    meins_by = {m["MATNR"]: m["MEINS"] for m in mara}
    counts = _distribute_counts(
        rng, _row_count(ctx, "erp.VBAK"), _row_count(ctx, "erp.VBAP"),
        VBAK_ITEMS_LO, VBAK_ITEMS_HI,
    )
    rows: list[dict[str, Any]] = []
    for vbak, c in zip(ctx["erp.VBAK"], counts):
        for pos in range(1, c + 1):
            matnr = rng.choice(matnrs)
            rows.append(
                {
                    "VBELN": vbak["VBELN"],
                    "POSNR": f"{pos:05d}",
                    "MATNR": matnr,
                    "KWMENG": round(rng.uniform(1, 500), 2),
                    "MEINS": meins_by[matnr],
                    "NETWR": round(rng.uniform(10, 20000), 2),
                }
            )
    return rows


def generate_aufk_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """MES.AUFK 生产工单抬头（§2.2）：WO-YYYY-NNNNNN，90,000 工单，MATNR FK→MARA。"""
    year = ctx["year"]
    matnrs = [m["MATNR"] for m in ctx["erp.MARA"]]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "mes.AUFK") + 1):
        rows.append(
            {
                "AUFNR": document_code("WO", year, seq),
                "MATNR": rng.choice(matnrs),
                "AUART": AUART,
                "WERKS": rng.choice(WERKS_POOL),
                "FTRMS": random_date(rng),
                "STATUS": rng.choice(STATUS_POOL),
            }
        )
    return rows


def generate_afpo_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """MES.AFPO 生产工单项目（§2.2）：90,000 工单 × 平均 1.33 项目 = 120,000 行。"""
    mara = ctx["erp.MARA"]
    matnrs = [m["MATNR"] for m in mara]
    meins_by = {m["MATNR"]: m["MEINS"] for m in mara}
    counts = _distribute_counts(
        rng, _row_count(ctx, "mes.AUFK"), _row_count(ctx, "mes.AFPO"),
        AFPO_ITEMS_LO, AFPO_ITEMS_HI,
    )
    rows: list[dict[str, Any]] = []
    for aufk, c in zip(ctx["mes.AUFK"], counts):
        for pos in range(1, c + 1):
            matnr = rng.choice(matnrs)
            rows.append(
                {
                    "AUFNR": aufk["AUFNR"],
                    "POSNR": f"{pos:05d}",
                    "MATNR": matnr,
                    "GAMNG": round(rng.uniform(1, 200), 2),
                    "MEINS": meins_by[matnr],
                }
            )
    return rows


def generate_cofv_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """MES.COFV 报工确认流水（§2.2）：90,000 工单 × 平均 2 次 = 180,000 行，CONFNR=CF-…。"""
    year = ctx["year"]
    matnrs = [m["MATNR"] for m in ctx["erp.MARA"]]
    counts = _distribute_counts(
        rng, _row_count(ctx, "mes.AUFK"), _row_count(ctx, "mes.COFV"),
        COFV_ITEMS_LO, COFV_ITEMS_HI,
    )
    rows: list[dict[str, Any]] = []
    seq = 0
    for aufk, c in zip(ctx["mes.AUFK"], counts):
        for _ in range(c):
            seq += 1
            rows.append(
                {
                    "CONFNR": document_code("CF", year, seq),
                    "AUFNR": aufk["AUFNR"],
                    "MATNR": rng.choice(matnrs),
                    "WERKS": aufk["WERKS"],
                    "ARBPL": rng.choice(ARBPL_POOL),
                    "DATUM": random_date(rng),
                    "ISM01": round(rng.uniform(1, 100), 2),
                    "ISMN1": round(rng.uniform(0.5, 20), 2),
                }
            )
    return rows


def _mseg_pair_rows(
    rng: random.Random,
    mrow: dict[str, Any],
    pairs: int,
    meins_by: dict[str, str],
    ekko_keys: list[str],
    aufk_keys: list[str],
) -> list[dict[str, Any]]:
    """生成一对收发移动（+X 收货 / -X 发料，净 0.0），返回该账面行的全部收发对。

    101 收货引 EBELN、261 生产发料引 AUFNR（可空 FK，D7）；301 移库收发均不引单。
    """
    matnr, werks, lgort = mrow["MATNR"], mrow["WERKS"], mrow["LGORT"]
    meins = meins_by[matnr]
    rows: list[dict[str, Any]] = []
    for _ in range(pairs):
        qty = round(rng.uniform(1, 300), 2)
        r_bwart = rng.choice(RECEIPT_BWART)
        rows.append(
            {
                "MATNR": matnr, "WERKS": werks, "LGORT": lgort, "BWART": r_bwart,
                "MENGE": qty, "MEINS": meins, "BUDAT": random_date(rng),
                "EBELN": rng.choice(ekko_keys) if r_bwart == "101" else None, "AUFNR": None,
            }
        )
        i_bwart = rng.choice(ISSUE_BWART)
        rows.append(
            {
                "MATNR": matnr, "WERKS": werks, "LGORT": lgort, "BWART": i_bwart,
                "MENGE": -qty, "MEINS": meins, "BUDAT": random_date(rng),
                "EBELN": None, "AUFNR": rng.choice(aufk_keys) if i_bwart == "261" else None,
            }
        )
    return rows


def _mseg_anchor_row(
    rng: random.Random,
    mrow: dict[str, Any],
    meins_by: dict[str, str],
    ekko_keys: list[str],
) -> dict[str, Any]:
    """锚点 101 收货行：MENGE = MARD.LABST（D10 账面=净变），引 EKKO。"""
    matnr, werks, lgort = mrow["MATNR"], mrow["WERKS"], mrow["LGORT"]
    return {
        "MATNR": matnr, "WERKS": werks, "LGORT": lgort, "BWART": "101",
        "MENGE": mrow["LABST"], "MEINS": meins_by[matnr], "BUDAT": random_date(rng),
        "EBELN": rng.choice(ekko_keys), "AUFNR": None,
    }


def generate_mseg_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """WMS.MSEG 库存流水（§2.3）：180,000 行，满足 D10 对账自洽（净变 = MARD.LABST，diff=0）。

    生成器先定 MARD 账面、再生成 MSEG 使按 (MATNR,LGORT) 净变 = MARD.LABST：
    - 每账面行生成 k 笔移动（k∈{5,7,9} 奇、Σ=180,000）：收发对（+X,-X，IEEE 相邻净 0.0）
      + 锚点 101 收货（= LABST，引 EKKO）；
    - 落库按 LGORT 分段（W01→W02→W03）：段内先全部收发对（每对相邻净 0.0）、后全部锚点
      （按 MATNR 升序，与 MARD 按地点 SUM(LABST) 同序累加）→ 按物料×地点 与 按地点 双口径 diff 精确 0。
    """
    year = ctx["year"]
    meins_by = {m["MATNR"]: m["MEINS"] for m in ctx["erp.MARA"]}
    ekko_keys = [e["EBELN"] for e in ctx["scm.EKKO"]]
    aufk_keys = [a["AUFNR"] for a in ctx["mes.AUFK"]]
    mard = ctx["erp.MARD"]
    counts = _distribute_counts(
        rng, len(mard), _row_count(ctx, "wms.MSEG"), MSEG_COUNT_LO, MSEG_COUNT_HI, step=2,
    )
    pairs_by_lgort: dict[str, list[dict[str, Any]]] = {lg: [] for lg in LGORT_POOL}
    anchors_by_lgort: dict[str, list[dict[str, Any]]] = {lg: [] for lg in LGORT_POOL}
    for mrow, k in zip(mard, counts):
        lgort = mrow["LGORT"]
        pairs_by_lgort[lgort].extend(
            _mseg_pair_rows(rng, mrow, (k - 1) // 2, meins_by, ekko_keys, aufk_keys)
        )
        anchors_by_lgort[lgort].append(_mseg_anchor_row(rng, mrow, meins_by, ekko_keys))
    rows: list[dict[str, Any]] = []
    seq = 0
    for lgort in LGORT_POOL:
        for r in pairs_by_lgort[lgort]:
            seq += 1
            rows.append({"MBLNR": document_code("MV", year, seq), "ZEILE": "01", **r})
        for r in anchors_by_lgort[lgort]:
            seq += 1
            rows.append({"MBLNR": document_code("MV", year, seq), "ZEILE": "01", **r})
    return rows


def generate_acdoca_rows(rng: random.Random, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """FIN.ACDOCA 财务日记账（§2.5）：41,000 行，REF_DOC 确定性抽样映射 VBELN/EBELN/MBLNR。

    从 VBAK/EKKO/MSEG 主键按固定比例（SO/PO/MV = 40/30/30%）rng.sample 确定性抽样，
    每条抽样单据生成 1 行 ACDOCA → REF_DOC 必能 join 回源表主键（D8 无孤儿）。
    """
    year = ctx["year"]
    total = _row_count(ctx, "fin.ACDOCA")
    so_n = round(total * ACDOCA_REF_SPLIT[0])
    po_n = round(total * ACDOCA_REF_SPLIT[1])
    mv_n = total - so_n - po_n
    so_refs = rng.sample(sorted(v["VBELN"] for v in ctx["erp.VBAK"]), so_n)
    po_refs = rng.sample(sorted(e["EBELN"] for e in ctx["scm.EKKO"]), po_n)
    mv_refs = rng.sample(sorted(m["MBLNR"] for m in ctx["wms.MSEG"]), mv_n)
    refs = (
        [("SO", d) for d in so_refs]
        + [("PO", d) for d in po_refs]
        + [("MV", d) for d in mv_refs]
    )
    rows: list[dict[str, Any]] = []
    for seq, (ref_type, ref_doc) in enumerate(refs, start=1):
        rows.append(
            {
                "BELNR": document_code("FI", year, seq),
                "POSNR": "01",
                "RACCT": rng.choice(RACCT_POOL),
                "KOSTL": rng.choice(KOSTL_POOL),
                "WSL": round(rng.uniform(-100000, 100000), 2),
                "BUDAT": random_date(rng),
                "REF_DOC": ref_doc,
                "REF_TYPE": ref_type,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# 表注册表（表 → DDL + 行生成器 + 主键 + 依赖；§7.2 生成器扩展点）
# ---------------------------------------------------------------------------
TABLE_SPECS: dict[str, dict[str, Any]] = {
    "scm.LFA1": {"ddl": LFA1_DDL, "gen": generate_lfa1_rows, "pk": ["LIFNR"], "depends_on": []},
    "erp.KNA1": {"ddl": KNA1_DDL, "gen": generate_kna1_rows, "pk": ["KUNNR"], "depends_on": []},
    "erp.MARA": {"ddl": MARA_DDL, "gen": generate_erp_mara, "pk": ["MATNR"], "depends_on": []},
    "erp.MARC": {"ddl": MARC_DDL, "gen": generate_marc_rows, "pk": ["MATNR", "WERKS"], "depends_on": ["erp.MARA"]},
    "erp.MARD": {"ddl": MARD_DDL, "gen": generate_mard_rows, "pk": ["MATNR", "WERKS", "LGORT"], "depends_on": ["erp.MARA"]},
    "erp.MAST": {"ddl": MAST_DDL, "gen": generate_mast_rows, "pk": ["MATNR", "WERKS", "STLNR"], "depends_on": ["erp.MARA"]},
    "erp.STPO": {"ddl": STPO_DDL, "gen": generate_stpo_rows, "pk": ["STLNR", "STLKN"], "depends_on": ["erp.MARA", "erp.MAST"]},
    "mes.MPLA": {"ddl": MPLA_DDL, "gen": generate_mpla_rows, "pk": ["MPLA_ID"], "depends_on": ["erp.MARA"]},
    "wms.WMMD": {"ddl": WMMD_DDL, "gen": generate_wmmd_rows, "pk": ["MATNR"], "depends_on": ["erp.MARA"]},
    # —— 事务/流水表（Phase B，§2.4-2.6；依赖主数据与上级单据，拓扑序固定）——
    "erp.VBAK": {"ddl": VBAK_DDL, "gen": generate_vbak_rows, "pk": ["VBELN"], "depends_on": ["erp.KNA1"]},
    "erp.VBAP": {"ddl": VBAP_DDL, "gen": generate_vbap_rows, "pk": ["VBELN", "POSNR"], "depends_on": ["erp.VBAK", "erp.MARA"]},
    "mes.AUFK": {"ddl": AUFK_DDL, "gen": generate_aufk_rows, "pk": ["AUFNR"], "depends_on": ["erp.MARA"]},
    "mes.AFPO": {"ddl": AFPO_DDL, "gen": generate_afpo_rows, "pk": ["AUFNR", "POSNR"], "depends_on": ["mes.AUFK", "erp.MARA"]},
    "mes.COFV": {"ddl": COFV_DDL, "gen": generate_cofv_rows, "pk": ["CONFNR"], "depends_on": ["mes.AUFK", "erp.MARA"]},
    "wms.MSEG": {"ddl": MSEG_DDL, "gen": generate_mseg_rows, "pk": ["MBLNR", "ZEILE"], "depends_on": ["erp.MARA", "scm.EKKO", "mes.AUFK"]},
    "scm.EKKO": {"ddl": EKKO_DDL, "gen": generate_ekko_rows, "pk": ["EBELN"], "depends_on": ["scm.LFA1"]},
    "scm.EKPO": {"ddl": EKPO_DDL, "gen": generate_ekpo_rows, "pk": ["EBELN", "EBELP"], "depends_on": ["scm.EKKO", "erp.MARA"]},
    "fin.ACDOCA": {"ddl": ACDOCA_DDL, "gen": generate_acdoca_rows, "pk": ["BELNR", "POSNR"], "depends_on": ["erp.VBAP", "scm.EKPO", "wms.MSEG"]},
}

GenFn = Callable[[random.Random, dict[str, Any]], list[dict[str, Any]]]


def _check_spec_vs_config(config: dict, table_id: str, spec: dict[str, Any]) -> None:
    """校验注册表 pk/depends_on 与配置表规格一致（单一事实来源，fail-fast）。"""
    code, name = table_id.split(".", 1)
    cfg = config["enterprise"]["systems"][code]["tables"][name]
    if spec["pk"] != cfg["pk"]:
        raise DesConfigError(f"表 {table_id} 主键注册表与配置不一致: {spec['pk']} != {cfg['pk']}")
    if spec["depends_on"] != cfg["depends_on"]:
        raise DesConfigError(f"表 {table_id} 依赖注册表与配置不一致: {spec['depends_on']} != {cfg['depends_on']}")


def _generation_order(config: dict) -> list[str]:
    """按配置表规格（master+transaction）+ depends_on 拓扑排序，得到固定生成顺序（约定 5）。

    依赖约束全部表集合内部：阶段 1 主数据（LFA1/KNA1→MARA→MARC/MARD→MAST→STPO→MPLA/WMMD）
    → 阶段 2 事务（EKKO→EKPO、VBAK→VBAP、AUFK→AFPO/COFV、MSEG、ACDOCA，§5.2）。
    """
    specs: dict[str, list[str]] = {}
    for code, sys_cfg in config["enterprise"]["systems"].items():
        for name, spec in sys_cfg["tables"].items():
            specs[f"{code}.{name}"] = spec["depends_on"]
    order: list[str] = []
    done: set[str] = set()
    while len(done) < len(specs):
        progress = False
        for table_id, deps in sorted(specs.items()):
            if table_id in done:
                continue
            if all(d in done for d in deps):
                order.append(table_id)
                done.add(table_id)
                progress = True
        if not progress:
            raise DesConfigError(f"表依赖成环或缺失: {sorted(set(specs) - done)}")
    return order


# ---------------------------------------------------------------------------
# 建库入口
# ---------------------------------------------------------------------------
def write_db(db_path: Path, tables: list[tuple[str, str, list[dict[str, Any]]]]) -> None:
    """重建 SQLite 库并写入多张表（幂等：存在则删除重建，*.db 不入 git）。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
        for table, ddl, rows in tables:
            conn.executescript(ddl)
            columns = list(rows[0].keys())
            placeholders = ",".join("?" * len(columns))
            conn.executemany(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                [tuple(r[c] for c in columns) for r in rows],
            )
        conn.commit()
    finally:
        conn.close()


def _persist_enterprise(
    out: Path,
    config: dict,
    seed: int,
    order: list[str],
    ctx: dict[str, Any],
    enterprise_code: str,
) -> dict[str, Any]:
    """按系统分组落库 + 写 manifest + 汇总结果（build_enterprise 的收尾阶段）。"""
    by_sys: dict[str, list[tuple[str, str, list[dict[str, Any]]]]] = {}
    for table_id in order:
        code, name = table_id.split(".", 1)
        by_sys.setdefault(code, []).append((name, TABLE_SPECS[table_id]["ddl"], ctx[table_id]))
    for code, tables in by_sys.items():
        write_db(out / config["enterprise"]["systems"][code]["db"], tables)

    build_manifest(config, seed, out, order)
    injected = sum(1 for r in ctx["erp.MARA"] if r.get("BISMT"))
    return {
        "enterprise": enterprise_code,
        "seed": seed,
        "out": str(out),
        "injected": injected,
        "total_rows": sum(len(ctx[tid]) for tid in order),
        "tables": {tid: len(ctx[tid]) for tid in order},
    }


def build_enterprise(
    enterprise_code: str,
    out_dir: str | Path | None = None,
    seed: int | None = None,
    config_file: str | Path | None = None,
) -> dict[str, Any]:
    """确定性生成 1 企业 5 源系统 18 张表（9 主数据 + 9 事务，合计 1,000,000 行）+ manifest.json。

    设计 §5 约定 1-5 全落地：每表独立 RNG 流、主键升序落库、纯函数派生、canonical 配置 hash、
    拓扑序固定（依赖 depends_on）。事务表引用主数据/上级单据的确定性内存输出，不重抽。

    参数：
        enterprise_code：企业编码（目录名）；
        out_dir：输出目录（默认 <data/des/enterprises>/<code>）；
        seed：覆盖企业配置中的 seed；
        config_file：覆盖企业配置 YAML（测试钩子，默认取企业目录内文件）。
    """
    config = load_config(enterprise_code, config_file=config_file)
    ent = config["enterprise"]
    if seed is None:
        seed = ent["seed"]
    if not isinstance(seed, int):
        raise DesConfigError(f"seed 必须为整数: {seed!r}")

    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    out.mkdir(parents=True, exist_ok=True)

    # 每表独立 RNG 流 + 拓扑序生成（约定 1/5），结果存 ctx 供下游表确定性引用
    ctx: dict[str, Any] = {
        "config": config,
        "year": config["coding"]["year"],
        "code_prefix": ent["code_prefix"],
    }
    order = _generation_order(config)
    for table_id in order:
        spec = TABLE_SPECS[table_id]
        _check_spec_vs_config(config, table_id, spec)
        rng = random.Random(f"{seed}:{table_id}")
        ctx[table_id] = _sort_rows(spec["gen"](rng, ctx), spec["pk"])
    return _persist_enterprise(out, config, seed, order, ctx, enterprise_code)
