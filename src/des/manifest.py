"""manifest.json 生成与表 SHA256 计算（设计 §5.3/§4 机验锚点）。

- config_sha256 = SHA256(canonical(配置) ∥ "::" ∥ seed)；
- table_sha256 = SHA256(按 MATNR 排序的该表全行 canonical dump)（erp.MARA/mes.MPLA/wms.WMMD 各一份）；
- manifest 记录 seed/行数/注入计数，由 C4 门禁与实测重算核对。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .config import canonical_dump, config_sha256


def read_table_rows(db_path: Path, table: str) -> list[dict[str, Any]]:
    """按 MATNR 升序读取表全行（dict 列表，SHA256 校验锚点的数据源）。"""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY MATNR")]
    finally:
        conn.close()


def table_sha256(rows: list[dict[str, Any]]) -> str:
    """table_sha256 = SHA256(按 MATNR 排序的全行 canonical dump)（设计 §4）。"""
    dump = "\n".join(canonical_dump(row) for row in rows)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()


def build_manifest(config: dict, seed: int, out_dir: Path, injected_count: int) -> dict:
    """构建并落盘 manifest.json（§5.3 结构），返回清单 dict。"""
    ent = config["enterprise"]
    systems = ent["systems"]
    tables: dict[str, dict[str, Any]] = {}
    for code in ("erp", "mes", "wms"):
        sys_cfg = systems[code]
        rows = read_table_rows(out_dir / sys_cfg["db"], sys_cfg["table"])
        entry: dict[str, Any] = {"rows": len(rows), "sha256": table_sha256(rows)}
        if code == "erp":
            entry["multi_code_count"] = sum(1 for r in rows if r.get("BISMT"))
        tables[f"{code}.{sys_cfg['table']}"] = entry
    manifest = {
        "enterprise": ent["code"],
        "seed": seed,
        "config_sha256": config_sha256(config, seed),
        "tables": tables,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
