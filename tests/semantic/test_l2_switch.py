"""L2 语义层切换验收（任务验收 a①②③，TestClient 级，不起长驻服务）。

①问"2026年8月分渠道注册用户数"→思考流→SQL 来自 compiler→数字与镜像库直查一致
  →消息含 data_profile=mock；
②问"注册用户资产规模"→结构化拒答卡；
③会话存储/SSE 冒烟不回归（帧形状 + profile 契约派生自注册表）。

Env: keyword routing (SEMANTIC_DISABLE_LLM=1) — LLM 不可用时的兜底路径必须可测。
"""

import json
import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="semantic-l2-"))
os.environ.setdefault("SEMANTIC_APP_DB", str(_TMP / "app.db"))
os.environ.setdefault("SEMANTIC_TRACE_LOG", str(_TMP / "trace.jsonl"))
os.environ.setdefault("SEMANTIC_DISABLE_LLM", "1")

import duckdb
from fastapi.testclient import TestClient

from src.fortune_semantic.compiler import QueryRequest, compile_query
from src.semantic import storage
from src.semantic.app import app

storage.migrate()
client = TestClient(app)
MIRROR = Path(__file__).resolve().parents[2] / "data" / "fortune_mirror.duckdb"
CHANNEL_QUESTION = "2026年8月分渠道注册用户数"
ASSET_QUESTION = "注册用户资产规模"


def _frames(question, **payload):
    with client.stream("POST", "/api/chat", json={"question": question, **payload}) as resp:
        assert resp.status_code == 200
        return [json.loads(line[len("data: "):])
                for line in resp.iter_lines() if line.startswith("data: ")]


def _final(frames) -> dict:
    finals = [f for f in frames if f["kind"] == "final"]
    assert len(finals) == 1
    return finals[0]["result"]


def _direct_mirror_channel_l2() -> list:
    """镜像库直查（独立 SQL，不经语义层）作为对账基准。"""
    conn = duckdb.connect(str(MIRROR), read_only=True)
    try:
        return conn.execute(
            """
            SELECT chn.sec_chnl_nm, COUNT(DISTINCT dwd.usr_id) AS cnt
            FROM cdm.dwd_cu_rgst_fin_di AS dwd
            LEFT JOIN (
                SELECT * FROM cdm.dim_ch_chl_df
                WHERE ds = (SELECT max(ds) FROM cdm.dim_ch_chl_df)
            ) AS chn ON dwd.rgst_chnl_id = chn.chnl_id
            WHERE dwd.rgst_num = 1
              AND CAST(dwd.rgst_dt AS DATE) BETWEEN DATE '2026-08-01' AND DATE '2026-08-31'
            GROUP BY 1 ORDER BY 2 DESC
            """
        ).fetchall()
    finally:
        conn.close()


def test_channel_question_l2_end_to_end():
    """①思考流 → SQL 来自 compiler → 数字与镜像库直查一致 → data_profile=mock。"""
    frames = _frames(CHANNEL_QUESTION)
    steps = [f["step"] for f in frames if f["kind"] == "step"]
    assert [s["n"] for s in steps] == list(range(1, len(steps) + 1))  # 思考流连续编号
    assert any(s["title"] == "意图路由" for s in steps)

    final = _final(frames)
    assert final["path"] == "semantic_pushdown"
    assert final["measure"] == "reg_user_cnt" and final["dimensions"] == ["channel_l2"]

    # SQL 来自 compiler（与同请求直接编译产物逐字一致）
    expected = compile_query(QueryRequest(
        measure="reg_user_cnt", dimensions=("channel_l2",),
        time_from="2026-08-01", time_to="2026-08-31"))
    assert final["sql"] == expected.sql
    assert any(s["title"] == "SQL 编译" and s.get("sql") == expected.sql for s in steps)

    # 数字与镜像库直查一致（含直查独立 SQL 的总计与 TOP3）
    direct = _direct_mirror_channel_l2()
    got = {r["channel_l2"]: r["reg_user_cnt"] for r in final["rows"]}
    assert got == {name: cnt for name, cnt in direct}
    assert f"共 {sum(cnt for _, cnt in direct):,} 人" in final["answer"]
    for name, cnt in direct[:3]:
        assert f"{name} {cnt:,}" in final["answer"]

    assert final["viz"] == "bar"
    assert final["data_profile"] == "mock"  # 结果元数据徽标（API 先行）
    # 会话存储中的结果消息同样带 data_profile
    messages = client.get("/api/sessions/" + final["conversation_id"]).json()["messages"]
    assert messages[1]["role"] == "assistant"
    assert messages[1]["result"]["data_profile"] == "mock"


def test_unregistered_measure_structured_reject():
    """②未注册度量（资产规模）→ 结构化拒答卡，复用 OUT_OF_SCOPE 流，无数字。"""
    final = _final(_frames(ASSET_QUESTION))
    assert final["path"] == "rejected"
    assert final["state"] == "reject_scope"
    card = final["reject_card"]
    assert card["code"] == "UNREGISTERED_MEASURE"
    assert "资产" in json.dumps(card["details"], ensure_ascii=False)
    assert "reg_user_cnt" in card["details"]["available_measures"]  # 告知能答什么
    assert not any(ch.isdigit() for ch in final["answer"])  # 拒答话术无数字
    assert "已就绪" in final["answer"] or "能答" in final["answer"]
    assert final["data_profile"] == "mock"


def test_profile_contract_derived_from_registry():
    """D7 契约字段名不变，值派生自 fortune_semantic.registry（前端零感知）。"""
    profile = client.get("/api/profile").json()
    assert {"rule_hints", "viz_map", "path_labels", "sensitive_fields"} <= set(profile)
    assert set(profile["rule_hints"]) >= {"reg_user_cnt", "channel_l2", "gender"}
    assert profile["viz_map"]["reg_user_cnt"] == "kpi"
    assert profile["viz_map"]["reg_user_cnt+channel_l2"] == "bar"
    assert profile["viz_map"]["reg_user_cnt+gender"] == "pie"
    assert profile["path_labels"]["semantic_pushdown"]


def test_sse_smoke_frames_shape():
    """③SSE 冒烟：step→token→final 帧形状不回归，final 带结构化 L2 元数据。"""
    frames = _frames("2026年8月注册用户数是多少？", client_request_id="CRID-L2-SMOKE")
    kinds = [f["kind"] for f in frames]
    assert kinds[0] == "step" and kinds[-1] == "final"
    assert "token" in kinds
    final = _final(frames)
    assert final["measure"] == "reg_user_cnt" and final["dimensions"] == []
    assert final["params"] == {"time_from": "2026-08-01", "time_to": "2026-08-31"}
    assert final["data_profile"] == "mock"
