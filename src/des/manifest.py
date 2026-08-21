"""manifest.json 生成与表 SHA256 计算（设计 §5.1/§4 机验锚点，按各表主键泛化）。

- config_sha256 = SHA256(canonical(含全部表规格 + data_version 的配置) ∥ "::" ∥ seed)；
- table_sha256 = 每表**按主键排序**的全行 canonical dump 的 SHA256（主键从配置表规格读取）；
- manifest 记录 data_version / total_rows / 每表 rows + sha256（erp.MARA 另记 multi_code_count），
  由 C4 门禁与实测重算核对。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .config import canonical_dump, config_sha256


def read_table_rows(db_path: Path, table: str, pk: list[str]) -> list[dict[str, Any]]:
    """按主键列升序读取表全行（dict 列表，SHA256 校验锚点的数据源）。"""
    order = ", ".join(pk)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY {order}")]
    finally:
        conn.close()


def table_sha256(rows: list[dict[str, Any]]) -> str:
    """table_sha256 = SHA256(按主键排序的全行 canonical dump)（设计 §4 约定 2/4）。"""
    dump = "\n".join(canonical_dump(row) for row in rows)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()


def build_manifest(
    config: dict,
    seed: int,
    out_dir: Path,
    generated_table_ids: list[str],
) -> dict:
    """构建并落盘 manifest.json（§5.1 结构），返回清单 dict。

    generated_table_ids：本阶段实际生成的表 id 列表（Phase A 为主数据表；事务表 Phase B 追加）。
    """
    systems = config["enterprise"]["systems"]
    tables: dict[str, dict[str, Any]] = {}
    for table_id in sorted(generated_table_ids):
        code, name = table_id.split(".", 1)
        sys_cfg = systems[code]
        pk = sys_cfg["tables"][name]["pk"]
        rows = read_table_rows(out_dir / sys_cfg["db"], name, pk)
        entry: dict[str, Any] = {"rows": len(rows), "sha256": table_sha256(rows)}
        if table_id == "erp.MARA":
            entry["multi_code_count"] = sum(1 for r in rows if r.get("BISMT"))
        tables[table_id] = entry
    manifest = {
        "enterprise": config["enterprise"]["code"],
        "seed": seed,
        "data_version": config.get("data_version", ""),
        "config_sha256": config_sha256(config, seed),
        "total_rows": sum(e["rows"] for e in tables.values()),
        "tables": tables,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
