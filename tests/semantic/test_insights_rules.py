"""T-U2 主动洞察规则测试（UX v0.2 US2，B3 契约冻结）。

三态：命中 / 不命中 / 兜底。规则=纯统计（非 LLM），阈值常量见
src/semantic/insights.py；fixture 镜像与注册表原语同构（同 test_d6 模式）。
契约（勿改字段名）：
  命中   → {"insights": [{type, channel, metric, current, baseline,
                           delta_pct, drilldown:{measure,dimensions,time}}]}
  无命中 → {"insights": [], "fallback": "common_queries"}
"""

import json
from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient

from src.semantic import config
from src.semantic.app import app


def _build_mirror(path: Path, daily: dict[str, list[tuple[str, int]]]) -> Path:
    """最小同构镜像：注册明细（渠道 id）+ 渠道维（二级渠道名）。

    daily: 渠道名 -> [(日期 'YYYY-MM-DD', 注册数), ...]；每人一行（rgst_num=1 表语义）。
    """
    conn = duckdb.connect(str(path))
    conn.execute("CREATE SCHEMA cdm")
    conn.execute(
        "CREATE TABLE cdm.dwd_cu_rgst_fin_di "
        "(usr_id VARCHAR, rgst_chnl_id VARCHAR, rgst_dt TIMESTAMP, rgst_num INTEGER)"
    )
    conn.execute(
        "CREATE TABLE cdm.dim_ch_chl_df "
        "(chnl_id VARCHAR, fst_chnl_nm VARCHAR, sec_chnl_nm VARCHAR, "
        "thd_chnl_nm VARCHAR, ds TIMESTAMP)"
    )
    chn_rows, usr_rows = [], []
    for i, (name, entries) in enumerate(daily.items(), start=1):
        chn_rows.append((f"CHN{i:02d}", f"一级{i}", name, name))
        uid = 0
        for day, count in entries:
            for _ in range(count):
                uid += 1
                usr_rows.append(
                    (f"u{i:02d}-{uid:04d}", f"CHN{i:02d}", f"{day} 10:{uid % 60:02d}:00")
                )
    conn.executemany(
        "INSERT INTO cdm.dim_ch_chl_df VALUES (?, ?, ?, ?, TIMESTAMP '2026-09-07')", chn_rows
    )
    conn.executemany(
        "INSERT INTO cdm.dwd_cu_rgst_fin_di VALUES (?, ?, ?, 1)", usr_rows
    )
    conn.close()
    return path


@pytest.fixture()
def install_mirror(monkeypatch, tmp_path):
    """fixture 镜像注入：config.MIRROR_DB 调用时读取，monkeypatch 生效。"""

    def _install(daily: dict[str, list[tuple[str, int]]]) -> Path:
        path = tmp_path / "fixture_mirror.duckdb"
        path.unlink(missing_ok=True)
        built = _build_mirror(path, daily)
        monkeypatch.setattr(config, "MIRROR_DB", built)
        return built

    return _install


def _get_body(install_mirror, daily: dict) -> dict:
    install_mirror(daily)
    with TestClient(app) as client:  # lifespan 迁移会话库（conftest 已 pin）
        resp = client.get("/api/insights")
    assert resp.status_code == 200
    return resp.json()


# ------------------------------------------------------------- 规则三态


def test_hit_channel_total_contribution(install_mirror):
    """命中：渠道 A 末日翻倍 → 渠道/总量/贡献度三类洞察；契约字段精确冻结。"""
    days = [(f"2026-09-0{d}", 10) for d in range(1, 7)]  # 9-01..9-06 平稳
    body = _get_body(install_mirror, {
        "渠道A": days + [("2026-09-07", 20)],  # 末日 10→20：+100%
        "渠道B": days + [("2026-09-07", 10)],  # 平稳（占比被动下降仍算贡献度突变）
    })
    assert "fallback" not in body  # 命中态无兜底键（B3）
    items = body["insights"]
    assert items, "规则应命中"

    # 契约冻结：字段集合精确（多字段/少字段都算违约）
    for item in items:
        assert set(item) == {"type", "channel", "metric", "current", "baseline",
                             "delta_pct", "drilldown"}
        assert set(item["drilldown"]) == {"measure", "dimensions", "time"}
        assert set(item["drilldown"]["time"]) == {"from", "to"}

    channel_hit = next(i for i in items if i["type"] == "channel_day_over_day")
    assert channel_hit["channel"] == "渠道A"
    assert channel_hit["metric"] == "注册用户数"  # 来自注册表 description（单一来源）
    assert channel_hit["current"] == 20 and channel_hit["baseline"] == 10
    assert channel_hit["delta_pct"] == pytest.approx(100.0)
    assert channel_hit["drilldown"]["measure"] == "reg_user_cnt"
    assert channel_hit["drilldown"]["dimensions"] == ["channel_l2"]

    total_hit = next(i for i in items if i["type"] == "total_day_over_day")
    assert total_hit["channel"] is None  # 总量无渠道归属
    assert total_hit["current"] == 30 and total_hit["baseline"] == 20
    assert total_hit["delta_pct"] == pytest.approx(50.0)

    contrib = [i for i in items if i["type"] == "contribution_day_over_day"]
    contrib_a = next(i for i in contrib if i["channel"] == "渠道A")
    # 占比 50% → 66.7%：相对变化 +33.3%
    assert contrib_a["current"] == pytest.approx(66.7, abs=0.1)
    assert contrib_a["baseline"] == pytest.approx(50.0, abs=0.1)
    assert contrib_a["delta_pct"] == pytest.approx(33.3, abs=0.1)

    # 按 |delta_pct| 降序（最大的突变最靠前），且不超过常量上限
    from src.semantic import insights as insights_mod

    assert items == sorted(items, key=lambda i: abs(i["delta_pct"]), reverse=True)
    assert len(items) <= insights_mod.MAX_INSIGHTS


def test_no_hit_returns_fallback(install_mirror):
    """不命中：全程平稳 → 无凑数洞察卡，返回常用查询兜底（宁缺毋滥）。"""
    days = [(f"2026-09-0{d}", 10) for d in range(1, 8)]  # 7 日全平稳
    body = _get_body(install_mirror, {"渠道A": days, "渠道B": days})
    assert body == {"insights": [], "fallback": "common_queries"}


def test_fallback_when_sample_below_minimum(install_mirror):
    """兜底：仅 3 日样本（< 最小样本 5 日）→ 即使有突变也不出卡。"""
    body = _get_body(install_mirror, {
        "渠道A": [("2026-09-05", 10), ("2026-09-06", 10), ("2026-09-07", 40)],
    })
    assert body == {"insights": [], "fallback": "common_queries"}


def test_fallback_when_mirror_unreadable(monkeypatch):
    """兜底：镜像库不可读（缺失/损坏）→ 诚实降级到常用查询，不 500、不编造。"""
    monkeypatch.setattr(config, "MIRROR_DB", Path("/nonexistent/mirror.duckdb"))
    with TestClient(app) as client:
        resp = client.get("/api/insights")
    assert resp.status_code == 200
    assert resp.json() == {"insights": [], "fallback": "common_queries"}


# ------------------------------------------------- 安全红线：零 SQL / 零表结构


def test_response_leaks_no_sql_or_schema(install_mirror):
    """产品红线：响应零 SQL、零表结构（用户可见层；命中态同样不得泄漏）。"""
    days = [(f"2026-09-0{d}", 10) for d in range(1, 7)]
    body = _get_body(install_mirror, {"渠道A": days + [("2026-09-07", 20)]})
    lowered = json.dumps(body, ensure_ascii=False).lower()
    for banned in ("select", "from cdm", "dwd_", "dim_ch", "where ", "duckdb"):
        assert banned not in lowered, banned
