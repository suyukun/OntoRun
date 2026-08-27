"""S3 M4 回归：GET /des/enterprises/{name}/overview —— DES 可视化入口端点。

验证（对账纪律 = 单一事实来源）：
- 响应结构字段齐全；表数与 manifest/直查一致（54 表规格锁定）；
- 已知表行数 = 直接打开 SQLite COUNT(*)（端点不编数）；
- yaml 无 domains 时如实缺省 None（不编造业务域数据）；
- 未知企业 404 结构化错误。
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_REPO_ROOT = Path(__file__).resolve().parents[1]
_AP_DIR = _REPO_ROOT / "data" / "des" / "enterprises" / "ap_anping"


@pytest.fixture(scope="module")
def client():
    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        yield c


def test_enterprise_list_scans_directory(client: TestClient):
    """目录扫描：不写死单企业，ap_anping 在清单中且带 manifest 的企业可见。"""
    res = client.get("/des/enterprises")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    names = [i["name"] for i in body["data"]["items"]]
    assert "ap_anping" in names


def test_overview_structure_and_registry(client: TestClient):
    """概览结构：字段存在、表数=54（任务规格）、元信息来自真实 manifest/yaml。"""
    res = client.get("/des/enterprises/ap_anping/overview")
    assert res.status_code == 200, res.text
    data = res.json()["data"]

    ent = data["enterprise"]
    assert set(ent) == {
        "directory",
        "display_name",
        "code_prefix",
        "seed",
        "data_version",
        "config_sha256",
        "manifest_total_rows",
        "generated_at",
    }
    assert ent["directory"] == "ap_anping"
    # display_name/code_prefix 来自 des_enterprise.yaml 真实内容
    assert ent["display_name"] == "安平金融控股集团（Anping Financial Holding Group）"
    assert ent["code_prefix"] == "AP"
    # seed 来自 manifest.json
    manifest = json.loads((_AP_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert ent["seed"] == manifest["seed"]
    assert isinstance(ent["seed"], int)
    assert ent["generated_at"] is None  # 无时间戳字段 -> 如实缺省

    totals = data["totals"]
    assert set(totals) == {"databases", "tables", "live_rows"}
    # 规格：54 张表（生成注册表全量）
    assert totals["tables"] == 54
    assert totals["databases"] == 6  # 六库：customer/risk/concentration/approval/project/base
    # 每库表数合计 = 总表数
    assert sum(len(db["tables"]) for db in data["databases"]) == totals["tables"]
    # 每库行数合计 = 总行数
    assert sum(db["live_total_rows"] for db in data["databases"]) == totals["live_rows"]


def test_known_table_count_equals_direct_sqlite(client: TestClient):
    """单一事实来源对账：端点行数 == 直查 approval.db 实时 COUNT(*)。"""
    res = client.get("/des/enterprises/ap_anping/overview")
    data = res.json()["data"]
    approval = next(db for db in data["databases"] if db["file"] == "approval.db")
    tables = {t["table"]: t for t in approval["tables"]}
    for t in ("ap_approve_order", "ap_approve_task"):
        assert t in tables
        direct = sqlite3.connect(f"file:{_AP_DIR / 'approval.db'}?mode=ro", uri=True)
        try:
            expected = direct.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        finally:
            direct.close()
        assert tables[t]["rows"] == expected
        assert tables[t]["manifest_rows"] is not None


def test_total_live_rows_matches_sqlite_sum(client: TestClient):
    """总实时行数 == 全部库逐表 COUNT 求和（实查为准，不取自 manifest）。"""
    res = client.get("/des/enterprises/ap_anping/overview")
    data = res.json()["data"]
    expected = 0
    for db_path in sorted(_AP_DIR.glob("*.db")):
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            names = [
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            expected += sum(conn.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0] for n in names)
        finally:
            conn.close()
    assert data["totals"]["live_rows"] == expected


def test_domains_missing_is_null_not_fabricated(client: TestClient):
    """yaml 当前无顶层 domains 键（STEP2 产物未落盘）：domains 必须为 null，
    且表条目不得伪造『业务域归属』字段（解析不到就缺省，铁律③）。"""
    res = client.get("/des/enterprises/ap_anping/overview")
    data = res.json()["data"]
    assert data["domains"] is None
    sample = data["databases"][0]["tables"][0]
    assert set(sample) == {"table", "rows", "manifest_rows"}


def test_unknown_enterprise_returns_404(client: TestClient):
    """未知企业：结构化 404（不抛 500、不给邻近企业的数据）。"""
    res = client.get("/des/enterprises/no_such_ent/overview")
    assert res.status_code == 404
    body = res.json()
    assert body["outcome"] == "error"
    assert body["error"]["code"] == "DES_ENTERPRISE_NOT_FOUND"


def test_invalid_name_rejected(client: TestClient):
    """非法企业名（含大写与特殊字符）：不返回正常数据。"""
    res = client.get("/des/enterprises/BadName!/")
    assert res.status_code in (400, 404)
