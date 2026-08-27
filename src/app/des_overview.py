"""S3 M4：DES 企业模拟可视化入口 —— GET /des/enterprises/{name}/overview。

目的：让「DES 升级」看得见（此前全部是后端能力，无任何界面）。

数据纪律（单一事实来源）：
- 行数 = 打开企业目录下各 SQLite 库实时 COUNT(*)，绝不硬编码；
- 元信息（seed/data_version/config_sha256/manifest 行数）来自 manifest.json
  与 des_enterprise.yaml 本体，缺什么如实缺省（None），不编造；
- 当前 ap_anping 的 yaml 只有企业身份（name/code_prefix/seed），无顶层
  domains 键（STEP2 业务域机器产物 domains.json 设计上应落盘而尚未落盘，
  见 docs/S3-M1b-DES金融化设计-v1.md §目录结构），故 domains 返回 None。

结构上不写死单企业：扫描 data/des/enterprises/ 目录，凡含 manifest.json
的子目录即一家企业（现 AP安平金控 / HC华成精密 / NH宁海重工 三家）。
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# 仓根定位：src/app/des_overview.py -> parents[0]=src/app, [1]=src, [2]=仓根
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = _REPO_ROOT / "data" / "des" / "enterprises"

_ENTERPRISE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")  # 防路径穿越


def _err(status_code: int, code: str, message: str) -> JSONResponse:
    """错误结构与本项目其他端点口径一致（request_id/outcome/error）。"""
    return JSONResponse(
        status_code=status_code,
        content={
            "request_id": "",
            "outcome": "error",
            "error": {"code": code, "message": message},
        },
    )


def _enterprise_dirs() -> list[Path]:
    """扫描数据根下含 manifest.json 的企业目录（目录名即企业名）。"""
    if not _DATA_ROOT.is_dir():
        return []
    return sorted(p for p in _DATA_ROOT.iterdir() if (p / "manifest.json").is_file())


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml_identity(path: Path) -> dict[str, Any]:
    """解析 des_enterprise.yaml；只取能确证的字段，缺省即缺，不造数。

    注意：企业覆盖层继承行业模板（deep_merge），但本端点不做跨文件合并——
    只解析企业文件本体声明的身份与顶层 domains，避免把模板猜测当事实。
    """
    try:
        import yaml
    except ImportError:  # pragma: no cover - PyYAML 为 requirements 固定依赖
        return {}
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(doc, dict):
        return {}
    ent = doc.get("enterprise") if isinstance(doc.get("enterprise"), dict) else {}
    domains = doc.get("domains")
    out: dict[str, Any] = {
        "display_name": ent.get("name"),
        "code_prefix": ent.get("code_prefix"),
        # domains：只有 yaml 真有该键才透出（类型不对也如实标 null——不修数据）
        "domains": domains if isinstance(domains, list) else None,
    }
    return out


def _count_db_tables(db_path: Path) -> dict[str, Any]:
    """实时打开单个 SQLite 库：逐表 COUNT(*)（只读连接，表名出自系统表）。"""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return {"file": db_path.name, "live_total_rows": None, "tables": [], "error": f"open failed: {exc}"}
    try:
        names = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        tables = []
        for t in names:
            try:
                n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            except sqlite3.Error as exc:
                tables.append({"table": t, "rows": None, "manifest_rows": None, "error": str(exc)})
                continue
            tables.append({"table": t, "rows": n, "manifest_rows": None})
        return {"file": db_path.name, "live_total_rows": sum(t["rows"] or 0 for t in tables), "tables": tables}
    finally:
        conn.close()


def _build_overview(directory: Path) -> dict[str, Any]:
    """组装 overview data：manifest 元信息 + yaml 身份 + 实时行数统计。"""
    manifest = _read_json(directory / "manifest.json")
    identity = _read_yaml_identity(directory / "des_enterprise.yaml")

    manifest_tables: dict[str, int] = {}
    for fq, info in (manifest.get("tables") or {}).items():
        if isinstance(info, dict):
            manifest_tables[fq] = info.get("rows")

    # manifest 形如 "<library>.<table>" -> 按 file 名对回各库的清单行数参照
    by_lib_rows: dict[str, dict[str, int]] = {}
    for fq, rows in manifest_tables.items():
        lib, _, tbl = fq.partition(".")
        by_lib_rows.setdefault(lib, {})[tbl] = rows

    databases = []
    for db_path in sorted(directory.glob("*.db")):
        stat = _count_db_tables(db_path)
        ref = by_lib_rows.get(db_path.stem, {})
        for t in stat["tables"]:
            m = ref.get(t["table"])
            t["manifest_rows"] = m  # 清单无此表时如实 None
        databases.append(stat)

    live_tables = sum(len(d["tables"]) for d in databases)
    live_rows = sum(d["live_total_rows"] or 0 for d in databases)

    return {
        "enterprise": {
            "directory": directory.name,
            "display_name": identity.get("display_name"),
            "code_prefix": identity.get("code_prefix"),
            "seed": manifest.get("seed"),
            "data_version": manifest.get("data_version"),
            "config_sha256": manifest.get("config_sha256"),
            "manifest_total_rows": manifest.get("total_rows"),
            "generated_at": None,  # manifest 无时间戳字段：如实缺省，不以文件 mtime 充数
        },
        "databases": databases,
        "totals": {"databases": len(databases), "tables": live_tables, "live_rows": live_rows},
        "domains": identity.get("domains"),
    }


def register_des_routes(app: FastAPI) -> None:
    """挂载 DES 概览端点（可在任意 FastAPI 实例复用；最小侵入 create_*_app 均可见）。"""

    @app.get("/des/enterprises")
    def des_enterprise_list():
        """可用企业清单（扫描目录；yaml 身份缺失时 display_name 如实 null）。"""
        items = []
        for d in _enterprise_dirs():
            ident = _read_yaml_identity(d / "des_enterprise.yaml")
            items.append({"name": d.name, "display_name": ident.get("display_name")})
        return {"request_id": "", "outcome": "ok", "data": {"items": items}}

    @app.get("/des/enterprises/{name}/overview")
    def des_enterprise_overview(name: str):
        """单企业概览：元信息 + 每库每表实时行数 + 业务域（缺则 null）。"""
        if not _ENTERPRISE_NAME_RE.match(name):
            return _err(400, "INVALID_ENTERPRISE_NAME", f"非法企业名: {name}")
        matches = [p for p in _enterprise_dirs() if p.name == name]
        if not matches:
            return _err(
                404,
                "DES_ENTERPRISE_NOT_FOUND",
                f"企业不存在或缺少 manifest.json: {name}（可用见 GET /des/enterprises）",
            )
        data = _build_overview(matches[0])
        return {"request_id": "", "outcome": "ok", "data": data}
