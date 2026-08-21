"""DES 确定性数据生成器 —— 制造型企业 3 源系统物料主数据（设计 §2/§3/§4）。

依据 docs/P1a-DES-配置与表结构设计_v0.1.md：
- 单一 seed 源：random.Random(企业配置 seed)（§4 约定 1），不取系统时间/环境变量/随机源；
- 稳定排序：物料宇宙按 MATNR 升序、注入用 rng.sample(排序后清单, count)（§4 约定 2）；
- 纯函数派生：批次/库位/旧码/校验码/日期全为 seed 随机 + 固定模式的纯函数（§4 约定 3）；
- 一物多码：仅 ERP.MARA 15%（精确 30 行）注入 BISMT 旧码 HC-{year}{seq:05d}（§3.1/§3.3）；
- 跨系统一致性：MES/WMS 直接复用 MARA 主码、WMMD.MEINS 复制 MARA.MEINS（§3.4，D 门禁）。
"""

from __future__ import annotations

import random
import sqlite3
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
# 常量（确定性锚点，与设计 §3.2/§2 对齐）
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
BESTQ_POOL = ("非限制", "非限制", "非限制", "质检", "冻结")  # 权重模拟：非限制为主
ZONE_POOL = ("A", "B", "C")

# ---------------------------------------------------------------------------
# 三表 DDL（设计 §2.1/§2.2/§2.3）
# 注：跨系统一致性不靠数据库外键（库与库之间无 FK，§5.2-3），
#     由 D 门禁与本体语义层校验；MPLA/WMMD 因此不写 REFERENCES MARA。
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


# ---------------------------------------------------------------------------
# 纯函数派生（§4 约定 3：无墙钟、无可变全局状态）
# ---------------------------------------------------------------------------
def random_date(rng: random.Random) -> str:
    """ANCHOR_START..ANCHOR_END 间随机日期 YYYY-MM-DD（seed 确定性派生）。"""
    span = (ANCHOR_END - ANCHOR_START).days
    day = ANCHOR_START + timedelta(days=rng.randint(0, span))
    return day.strftime("%Y-%m-%d")


def generate_mara_rows(rng: random.Random, year: int, count: int) -> list[dict[str, Any]]:
    """ERP.MARA 物料主数据（§2.1）：MATNR 升序生成，BISMT 待注入阶段回填。"""
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

    - 目标数 count = round(N × rate)，本切片 N=200 → 精确 30 行（15.00%）；
    - 选择：rng.sample(按 MATNR 升序的物料宇宙, count)，seed 确定 → 行集固定；
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


def generate_mpla_rows(
    rng: random.Random, mara_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """MES.MPLA 生产侧物料主数据（§2.2）：1:1 对齐 MARA，MATNR 直接复用主码。"""
    rows: list[dict[str, Any]] = []
    for m in sorted(mara_rows, key=lambda r: r["MATNR"]):
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


def generate_wmmd_rows(
    rng: random.Random, mara_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """WMS.WMMD 仓储侧物料主档（§2.3）：MATNR 即主键，MEINS 复制 MARA（D3 一致性）。"""
    rows: list[dict[str, Any]] = []
    for m in sorted(mara_rows, key=lambda r: r["MATNR"]):
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
# 建库入口
# ---------------------------------------------------------------------------
def write_db(db_path: Path, table: str, ddl: str, rows: list[dict[str, Any]]) -> None:
    """重建 SQLite 库并写入表（幂等：存在则删除重建，*.db 不入 git）。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
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


def build_enterprise(
    enterprise_code: str,
    out_dir: str | Path | None = None,
    seed: int | None = None,
    config_file: str | Path | None = None,
) -> dict[str, Any]:
    """确定性生成 1 企业 3 源系统库 + manifest.json（设计 §5），返回生成统计。

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

    rng = random.Random(seed)
    year = config["coding"]["year"]
    count = ent["systems"]["erp"]["material_count"]  # 物料宇宙以 ERP 行数驱动，1:1:1 对齐
    mara_rows = generate_mara_rows(rng, year, count)

    multi = config["injection"]["multi_code"]
    mara_rows, injected = inject_legacy_codes(
        rng, mara_rows, multi["rate"], multi["legacy_pattern"], ent["code_prefix"], year
    )
    mpla_rows = generate_mpla_rows(rng, mara_rows)
    wmmd_rows = generate_wmmd_rows(rng, mara_rows)

    out = Path(out_dir) if out_dir else DEFAULT_ENTERPRISES_DIR / enterprise_code
    out.mkdir(parents=True, exist_ok=True)
    systems = ent["systems"]
    write_db(out / systems["erp"]["db"], "MARA", MARA_DDL, mara_rows)
    write_db(out / systems["mes"]["db"], "MPLA", MPLA_DDL, mpla_rows)
    write_db(out / systems["wms"]["db"], "WMMD", WMMD_DDL, wmmd_rows)
    build_manifest(config, seed, out, injected)
    return {"enterprise": enterprise_code, "seed": seed, "out": str(out), "injected": injected}
