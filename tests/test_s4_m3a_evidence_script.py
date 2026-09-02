"""S4 M3a 增量测试：证据链载荷结构 + 第 1/2/4 幕端到端（真实库断言 10.8%/12.8%）。

只跑本文件（增量，禁全量 pytest）：
    /opt/anaconda3/bin/python3 -m pytest tests/test_s4_m3a_evidence_script.py -q

覆盖（口径包 v0.3 §六/§七）：
- 证据链载荷统一结构 {结论/依据表名/命中规则+条款/分母说明/明细行引用}（禁 mock）；
- 第 1 幕：天晟逐家 8.0%/5.5%/8.2% 单看都安全 → 归集 86.4/800 = 10.8% 橙（M2 引擎实算，非查表回显）；
- 第 2 幕：恒昌三线索（股权代持/交叉担保/资金往来）+ R2 重算 102.4/800 = 12.8% 红；
- 第 4 幕：approve_disposal REJECTED（2023 关联交易办法第二十三条）→ 处置退回重新起草（未处置）；
- 对话证据链：/agent/risk/chat 答案携带 evidence（剧本工具 / risk_query 内嵌）。

数据源 = ap_anping 真实库（只读）；第 4 幕写路径在 ap_anping 副本上执行（不污染演示数据）。
"""

from __future__ import annotations

import re
import shutil

import pytest
from fastapi.testclient import TestClient

from src.runtime.risk_db import AP_ANPING_DIR, RiskStore

TIANSHENG = "天晟集团有限公司"
TIANSHENG_NO = "GRP-2026-900001"  # 根因一串号修复：证据链一律按 group_customer_no 定位
HUAXIN_SW_NO = "GRP-2026-000098"  # 华信建设西南集团（首组，同名唯一化后保留原名）
GROUP_CAPITAL_YI = 800.0

# 证据链载荷统一键（口径包§六：结论/依据表名/命中规则+条款/分母说明/明细行引用）
EVIDENCE_KEYS = (
    "intent",
    "conclusion",
    "basis_tables",
    "rules_hits",
    "denominator",
    "detail_rows",
)


# ---------------------------------------------------------------------------
# 共享只读端点（真实 ap_anping，禁 mock）
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        yield c


def _reveal(client: TestClient) -> dict:
    res = client.get(
        "/risk/evidence/group-reveal", params={"group_customer_no": TIANSHENG_NO}
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["outcome"] == "ok"
    return body["data"]


def _upgrade(client: TestClient) -> dict:
    res = client.get(
        "/risk/evidence/related-upgrade", params={"group_customer_no": TIANSHENG_NO}
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]


# ---------------------------------------------------------------------------
# 证据链载荷结构（统一五要素）
# ---------------------------------------------------------------------------


def test_evidence_payload_structure(client: TestClient) -> None:
    """三个剧本查询的证据链载荷均为统一五要素结构（口径包§六，禁 mock）。"""
    for payload in (_reveal(client), _upgrade(client)):
        for key in EVIDENCE_KEYS:
            assert key in payload, f"证据链载荷缺 {key}: {payload.get('intent')}"
        assert isinstance(payload["basis_tables"], list) and payload["basis_tables"]
        assert isinstance(payload["rules_hits"], list)
        assert isinstance(payload["detail_rows"], list)
    # 第 4 幕审批链同样五要素（denominator 为 None，分母不适用）
    ac = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-00010309"}
    ).json()["data"]
    for key in EVIDENCE_KEYS:
        assert key in ac, f"审批链证据载荷缺 {key}"


def test_evidence_denominator_has_source(client: TestClient) -> None:
    """分母说明带真实来源（base.ap_sys_param，非硬编码）。"""
    denom = _reveal(client)["denominator"]
    assert denom["value_yi"] == GROUP_CAPITAL_YI
    assert denom["source"] == "base.ap_sys_param.CAP_GROUP_CONSOLIDATED"


def test_evidence_fail_closed_unknown_group(client: TestClient) -> None:
    """不存在的集团编号 → 400 GROUP_NOT_FOUND（fail-closed，绝不回显 0% 玩具结果）。"""
    res = client.get(
        "/risk/evidence/group-reveal", params={"group_customer_no": "GRP-2026-999999"}
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "GROUP_NOT_FOUND"
    res2 = client.get(
        "/risk/evidence/related-upgrade", params={"group_customer_no": "GRP-2026-999999"}
    )
    assert res2.status_code == 400
    assert res2.json()["error"]["code"] == "GROUP_NOT_FOUND"


# ---------------------------------------------------------------------------
# 第 1 幕：揭示（逐家单看都安全 → 归集 10.8% 橙）
# ---------------------------------------------------------------------------


def test_act1_per_institution_safe(client: TestClient) -> None:
    """逐家附属机构单看都安全（口径包§七 第 1 幕：48/8.0%、22/5.5%、16.4/8.2%）。"""
    detail = {d["org_name"]: d for d in _reveal(client)["detail_rows"]}
    assert detail["安平银行"]["balance_yi"] == pytest.approx(48.0, abs=1e-3)
    assert detail["安平银行"]["ratio_display"] == "8.0%"
    assert detail["安平银行"]["reference_denom_yi"] == 600.0
    assert detail["安平证券"]["ratio_display"] == "5.5%"
    assert detail["安平证券"]["reference_denom_yi"] == 400.0
    assert detail["安平资产管理"]["ratio_display"] == "8.2%"
    assert detail["安平资产管理"]["reference_denom_yi"] == 200.0


def test_act1_aggregation_108_orange(client: TestClient) -> None:
    """归集实算 86.4/800 = 10.8% 橙（M2 引擎 risk_rules 实算，口径包§七 第 1 幕）。"""
    data = _reveal(client)
    comp = data["rules_hits"][0]["computed"]
    assert data["rules_hits"][0]["rule"] == "R1a"
    assert comp["numerator_yi"] == pytest.approx(86.4, abs=1e-3)
    assert comp["denominator_yi"] == GROUP_CAPITAL_YI
    assert comp["ratio"] == pytest.approx(0.108, abs=1e-3)
    assert comp["ratio_display"] == "10.8%"
    assert comp["level"] == "橙"
    # R1a 条款引用（金控办法第三十二/三十三条）+ 橙色预警信号已生成
    assert "第三十二/三十三条" in data["rules_hits"][0]["clause"]
    assert any(s["warn_level"] == "橙" for s in data["signals"])


def test_act1_not_table_echo_computed(client: TestClient) -> None:
    """数据经 M2 引擎实算（红队玩具分水岭）：结论含「归集实算」，且与库内信号原因可互证。"""
    data = _reveal(client)
    assert "实算" in data["conclusion"]
    assert data["conclusion"].startswith(TIANSHENG)


# ---------------------------------------------------------------------------
# 第 2 幕：升级识别（恒昌三线索 + R2 纳入重算 12.8% 红）
# ---------------------------------------------------------------------------


def test_act2_hengchang_three_clues(client: TestClient) -> None:
    """恒昌贸易三线索可回溯（股权代持/交叉担保/资金往来，customer_relation_tree 明细行）。"""
    data = _upgrade(client)
    party = next(d for d in data["detail_rows"] if "恒昌" in d["customer_name"])
    assert party["balance_yi"] == pytest.approx(16.0, abs=1e-3)
    assert set(party["clue_names"]) == {"股权代持", "交叉担保", "资金往来"}
    clue_names = {c["clue"] for c in party["relation_clues"]}
    assert clue_names == {"股权代持", "交叉担保", "资金往来"}
    # 每条线索带真实明细行引用（关系树 PK）
    assert all(
        c["row_ref"].startswith("customer.ap_customer_relation_tree#")
        for c in party["relation_clues"]
    )


def test_act2_r2_recompute_128_red(client: TestClient) -> None:
    """R2 纳入归集重算 102.4/800 = 12.8% 红（口径包§七 第 2 幕）。"""
    data = _upgrade(client)
    rules = {h["rule"]: h for h in data["rules_hits"]}
    assert "R2" in rules and "R1a" in rules
    comp = rules["R1a"]["computed"]
    assert comp["numerator_yi"] == pytest.approx(102.4, abs=1e-3)
    assert comp["ratio"] == pytest.approx(0.128, abs=1e-3)
    assert comp["ratio_display"] == "12.8%"
    assert comp["level"] == "红"
    assert rules["R2"]["computed"]["related_balance_yi"] == pytest.approx(
        16.0, abs=1e-3
    )
    assert "2018" in rules["R2"]["clause"]
    assert any(s["warn_level"] == "红" for s in data["signals"])


# ---------------------------------------------------------------------------
# F7（P0）：两套分子源统一 —— 证据链与看板同源（ap_concentration_limit 台账聚合 + R2）
# ---------------------------------------------------------------------------

RANK5_NO = "GRP-2026-001234"  # rank5：台账 8.16 亿（修复前 group-reveal 误报 400）


def _dash_ranking(client: TestClient) -> list[dict]:
    return client.get("/risk/dashboard").json()["data"]["group_concentration_ranking"]


def test_f7_rank5_group_reveal_same_source(client: TestClient) -> None:
    """F7：rank5（GRP-2026-001234，台账 8.16 亿）group-reveal 200，数字与看板 1.02% 同源。"""
    res = client.get(
        "/risk/evidence/group-reveal", params={"group_customer_no": RANK5_NO}
    )
    assert res.status_code == 200, res.text
    comp = res.json()["data"]["rules_hits"][0]["computed"]
    # F20/F21：001234 台账重锚至 5.0%（40 亿，腰部分布带）
    assert comp["numerator_yi"] == pytest.approx(40.0, abs=1e-2)
    assert comp["ratio_display"] == "5.0%"
    assert comp["level"] == "无"
    # 与看板同源：看板排名含该集团，ratio 一致
    entry = next(
        (g for g in _dash_ranking(client) if g["group_customer_no"] == RANK5_NO), None
    )
    assert entry is not None
    assert entry["concentration_ratio"] == pytest.approx(comp["ratio"], abs=1e-4)


def test_f7_evidence_matches_dashboard_same_source(client: TestClient) -> None:
    """F7 同源：group-reveal/related-upgrade/verify-reason 与看板排名数字完全一致（两套分子源统一）。"""
    for g in _dash_ranking(client)[:10]:
        gno = g["group_customer_no"]
        reveal = client.get(
            "/risk/evidence/group-reveal", params={"group_customer_no": gno}
        ).json()["data"]
        upgrade = client.get(
            "/risk/evidence/related-upgrade", params={"group_customer_no": gno}
        ).json()["data"]
        verify = client.get(
            "/risk/evidence/verify-reason", params={"group_customer_no": gno}
        ).json()["data"]
        # post_R2（R2 纳入后口径）与看板一致
        assert upgrade["r2_levels"]["post_r2"]["ratio"] == pytest.approx(
            g["concentration_ratio"], abs=1e-4
        )
        assert upgrade["r2_levels"]["post_r2"]["level"] == g["concentration_level"]
        # reveal 同构含 post_R2；verify-reason 集中度实算一致
        assert reveal["r2_levels"]["post_r2"]["ratio"] == pytest.approx(
            g["concentration_ratio"], abs=1e-4
        )
        assert verify["rules_hits"][0]["computed"]["ratio"] == pytest.approx(
            g["concentration_ratio"], abs=1e-4
        )


def test_f7_tiansheng_two_level_pre_post(client: TestClient) -> None:
    """F7b：天晟两级口径显式给出 pre_R2（10.8% 橙）与 post_R2（12.8% 红）+「纳入隐性关联前后」文案。"""
    reveal = _reveal(client)
    rl = reveal["r2_levels"]
    assert rl["pre_r2"]["ratio_display"] == "10.8%"
    assert rl["pre_r2"]["level"] == "橙"
    assert rl["post_r2"]["ratio_display"] == "12.8%"
    assert rl["post_r2"]["level"] == "红"
    assert "纳入隐性关联" in rl["note"]
    assert "纳入隐性关联前" in reveal["conclusion"]
    up = _upgrade(client)
    assert up["r2_levels"]["pre_r2"]["ratio_display"] == "10.8%"
    assert up["r2_levels"]["post_r2"]["ratio_display"] == "12.8%"


# ---------------------------------------------------------------------------
# F13：明细行 is_internal 标记 + 结论抵销勾稽说明（口径包§一 内部抵销注记）
# ---------------------------------------------------------------------------


def test_f13_detail_is_internal_marker(client: TestClient) -> None:
    """F13：detail_rows 加 is_internal 标记——区分「集团内部成员间交叉授信」与「外部融资敞口」。

    天晟为外部集团客户（融资对手方均为非安平成员），故逐家明细均 is_internal=False
    （外部融资敞口，internal_balance_yi=0）；勾稽说明出现在结论与 r2 note。
    """
    reveal = _reveal(client)
    assert reveal["detail_rows"], "天晟应含逐家明细"
    for d in reveal["detail_rows"]:
        assert "is_internal" in d, f"明细行缺 is_internal 标记: {d['org_name']}"
        assert d["is_internal"] is False
        assert d["internal_balance_yi"] == 0.0
        assert d["external_balance_yi"] == d["balance_yi"]
    # F27：勾稽对账数字化——外部 + 内部抵销 = 明细合计 = 台账归集
    assert "勾稽对账" in reveal["conclusion"], "结论应带三数对账"
    assert "三数对账" in reveal["r2_levels"]["note"]

    up = _upgrade(client)
    assert up["detail_rows"], "天晟应含隐性关联方明细"
    for d in up["detail_rows"]:
        assert d["is_internal"] is False, "恒昌等隐性关联方为外部一致行动人（外部敞口）"
    assert "抵销后外部净敞口" in up["conclusion"]

    draft = client.get(
        "/risk/reporting/draft", params={"group_customer_no": TIANSHENG_NO}
    ).json()["data"]
    for b in draft["breakdown"]:
        assert "is_internal" in b, f"报送 breakdown 缺 is_internal: {b['org_name']}"
    assert "抵销后外部净敞口" in draft["consolidated_exposure"]["caliber_note"]


def test_f15_audit_in_universe(client: TestClient) -> None:
    """F15：/risk/audit 展示层 in-universe——无 llm:/call_ 机码，actor_detail 空值补齐。

    WORM 审计原行不改，仅展示层映射：actor=llm → AI 智能体（风险预警助手）；
    actor_detail 含 DeepSeekProvider/confirmed_call → 归一业务文案；空 → 按 action 回填岗位。
    """
    data = client.get("/risk/audit").json()["data"]
    items = data["items"]
    assert items, "审计应非空"
    # F18：默认 business 视图——55 条中 50 条开发冒烟痕折叠为 migrated_records，
    # 业务行 5 条（req_* 4 条 + REJ-2026-90000002 预置驳回）
    assert data["total"] == 5
    assert data["migrated_records"] == 50
    all_view = client.get("/risk/audit", params={"view": "all"}).json()["data"]
    assert all_view["total"] == 55, "view=all 应全量透明保留（WORM 不动）"
    machine = [
        it
        for it in items
        if "llm:" in (it.get("actor") or "")
        or "call_" in (it.get("actor_detail") or "")
        or "DeepSeekProvider" in (it.get("actor_detail") or "")
        or it.get("actor") in ("llm", "human")
    ]
    assert not machine, f"审计展示泄漏机码: {machine}"
    assert all((it.get("actor_detail") or "").strip() for it in items), (
        "首页 actor_detail 空值应补齐"
    )
    # approval_chain 审计回放同样 in-universe
    ac = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-90000002"}
    ).json()["data"]
    for a in ac["detail_rows"][0].get("audit_trail") or []:
        assert "call_" not in (a.get("actor_detail") or ""), f"审计回放泄漏机码: {a}"


def test_f14_push_columns_cleanup() -> None:
    """F14：推送列「集团集中度敞口超限」残留 = 0（同 F8 监测语气，活库补丁幂等双落）。

    三处漏网写入点：ap_warning_signal.push_warn_reason（2092 行）、ap_warning_push.
    push_warn_reason（860 行）、ap_warn_derive_sub_push.warn_reason_updated（522 行）
    仍硬写「集团集中度敞口超限 N%」→ patch_risk_live_data.patch_push_columns_cleanup
    迁移为「集团集中度指标异动」；生成器 _warn_reason 已同源。
    """
    import sqlite3

    conn = sqlite3.connect(str(AP_ANPING_DIR / "risk.db"))
    try:
        for alias in ("approval", "concentration", "project", "customer", "base"):
            conn.execute(
                f"ATTACH DATABASE ? AS {alias}",
                (str(AP_ANPING_DIR / f"{alias}.db"),),
            )
        for table, col in (
            ("ap_warning_signal", "push_warn_reason"),
            ("ap_warning_push", "push_warn_reason"),
            ("ap_warn_derive_sub_push", "warn_reason_updated"),
        ):
            n = conn.execute(
                f"SELECT COUNT(*) n FROM {table} WHERE {col} LIKE '%敞口超限%'"
            ).fetchone()[0]
            assert n == 0, f"F14 残留未清: {table}.{col} 仍有 {n} 行「敞口超限」"
        # F19：F14 的中间态模板「集团集中度指标异动」已被维度改写取代——
        # 非集中度维度集团换真实触发语气，模板残留必须为 0
        n = conn.execute(
            "SELECT COUNT(*) FROM ap_warning_signal "
            "WHERE push_warn_reason LIKE '集团集中度指标异动%'"
        ).fetchone()[0]
        assert n == 0, f"F19 后模板残留 {n} 行"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 第 4 幕：双签驳回（2023 办法第二十三条 → 处置退回重新起草）
# ---------------------------------------------------------------------------


def test_act4_approval_chain_article23(client: TestClient) -> None:
    """审批链证据含 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）。"""
    data = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-00010309"}
    ).json()["data"]
    hit = data["rules_hits"][0]
    assert hit["rule"] == "2023 关联交易办法第二十三条"
    assert "拆分交易" in hit["text"]
    # 明细行：信号 + 处置 + 审批单/任务
    row = data["detail_rows"][0]
    assert row["signal"]["signal_id"] == "SGN-2026-00010309"
    assert row["approve_orders"], "应解析出审批单"
    assert row["approve_orders"][0]["order"]["approve_order_status"] == "PROCESS"


PROP_APPROVE_ORDER_ID = "APP-2026-90000002"  # 天晟红警下挂审批单（根因三道具）


def test_act4_prop_chain_under_tiansheng_red(client: TestClient) -> None:
    """天晟红警 WS-2026-90000002 下挂 REJECTED 审批单（F4 预置驳回演示态）：
    AI 拆分提议已被审批人按 2023 办法第二十三条驳回——双节点双签（节点1 已审 / 节点2 已驳）、
    opinion 落第二十三条依据、审计行已预置；approval-chain 可一键调档回放。"""
    data = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-90000002"}
    ).json()["data"]
    row = data["detail_rows"][0]
    assert row["signal"]["signal_id"] == "SGN-2026-90000002"
    orders = {o["order"]["approve_order_id"]: o for o in row["approve_orders"]}
    assert PROP_APPROVE_ORDER_ID in orders, "天晟红警必须下挂审批单（不再「暂无待审批单」）"
    o = orders[PROP_APPROVE_ORDER_ID]["order"]
    # F4：预置驳回态（REJECTED + opinion 第二十三条），双节点双签
    assert o["approve_order_status"] == "REJECTED"
    assert "第二十三条" in (o["opinion_description"] or "")
    assert "拆分" in (o["remark"] or "")
    assert "SGN-2026-90000002" in (o["remark"] or "")
    tasks = orders[PROP_APPROVE_ORDER_ID]["tasks"]
    assert len(tasks) == 2, f"审批链应为双节点双签（实得 {len(tasks)} 条任务）"
    by_result = {t["approve_result"] for t in tasks}
    assert by_result == {"APPROVED", "REJECTED"}, f"双签应为 一签通过一签驳回（实得 {by_result}）"
    assert all(t["approve_task_status"] == "COMPLETED" for t in tasks)
    # F4/F6：审计行已预置（驳回留痕可回放，非依赖现场 live 写回）
    assert row.get("audit_trail"), "审批链证据应带预置驳回审计行（不再审计空账）"
    assert any("REJECTED" in (a.get("params_json") or "") for a in row["audit_trail"])
    hit = data["rules_hits"][0]
    assert hit["rule"] == "2023 关联交易办法第二十三条"
    assert "拆分交易" in hit["text"]


def test_f10_preset_audit_in_universe(client: TestClient) -> None:
    """F10：预置驳回审计行 in-universe——actor_detail 无「s4-preset」、时间戳对齐 2026-12 业务线。"""
    data = client.get(
        "/risk/evidence/approval-chain", params={"warning_id": "WS-2026-90000002"}
    ).json()["data"]
    trail = data["detail_rows"][0].get("audit_trail") or []
    assert trail, "应有预置驳回审计行"
    for a in trail:
        assert "s4-preset" not in (a.get("actor_detail") or ""), (
            f"actor_detail 泄漏内部记号: {a['actor_detail']}"
        )
        # 审计时间戳不得早于业务时间线（数据时钟 2026-12，审批链 approve_time=2026-12-10）
        assert a["ts"] >= "2026-12-01", f"审计时间戳早于业务线倒挂: {a['ts']}"
    assert any("REJECTED" in (a.get("params_json") or "") for a in trail)


def test_f10_reset_route_registered(client: TestClient) -> None:
    """F10：演示重置功能以正式路由暴露（OpenAPI 可见），供演示前重置用。"""
    paths = client.get("/openapi.json").json()["paths"]
    assert "/risk/demo/reset-approval" in paths
    assert "post" in paths["/risk/demo/reset-approval"]
    assert "重置" in (
        paths["/risk/demo/reset-approval"]["post"].get("description") or ""
    )


def test_f11_risk_audit_aggregation(client: TestClient) -> None:
    """F11：/audit 一键调档改指风险审计库 s3_risk_ontology.db（不再 total=0 空账）。

    检查组「一键调档」：/risk/audit 聚合风险动作全程审计，含预置驳回（approve_disposal，
    in-universe actor_detail + 2026-12 业务时间戳），与 approval-chain 的 audit_trail 同源。
    """
    data = client.get("/risk/audit").json()["data"]
    assert data["total"] > 0, "风险审计应非空账（读 s3_risk_ontology.db）"
    # 含预置驳回审计行（approve_disposal + in-universe）
    appr = client.get("/risk/audit", params={"action": "approve_disposal"}).json()[
        "data"
    ]
    assert appr["total"] >= 1
    hits = [
        it
        for it in appr["items"]
        if "REJ-2026-90000002" in (it.get("request_id") or "")
    ]
    assert hits, "风险审计应含预置驳回审计行（request_id=REJ-2026-90000002）"
    row = hits[0]
    assert "s4-preset" not in (row.get("actor_detail") or "")
    assert row["ts"] >= "2026-12-01"


def test_act4_prop_reset_to_pending_then_live_reject(act4_env) -> None:
    """F4：预置 REJECTED 道具链可重置回 PENDING（供现场 live 驳回演示）→ 现场驳回生效。

    道具链 APP-2026-90000002 默认 REJECTED（预置驳回态）；patch_approval_reset_to_pending
    把审批单重置回 PROCESS、节点 2 回 PENDING（节点 1 保持已审）；审批人现场按第二十三条
    approve_disposal decision=REJECTED → 状态再回 REJECTED + opinion + 双节点 COMPLETED。
    """
    store, engine = act4_env
    conn = store.source_conn()
    try:
        # 重置回 PENDING（模拟 patch_approval_reset_to_pending）
        conn.execute(
            "UPDATE approval.ap_approve_order SET approve_order_status='PROCESS', "
            "approve_time=NULL, approved_user_id='', opinion_description=NULL "
            "WHERE approve_order_id=?", (PROP_APPROVE_ORDER_ID,)
        )
        conn.execute(
            "UPDATE approval.ap_approve_task SET approve_task_status='PENDING', "
            "approve_result=NULL, approve_remark=NULL, approve_time=NULL "
            "WHERE approve_task_id=?", ("AT-2026-90000003",)
        )
        conn.commit()
        # 现场驳回（第二十三条）
        res = engine.execute(
            "approve_disposal",
            {
                "approve_order_id": PROP_APPROVE_ORDER_ID,
                "decision": "REJECTED",
                "opinion": (
                    "驳回：AI 提议将天晟部分授信拆分至非关联第三方通道主体降低名义"
                    "归集集中度，违反 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）。"
                ),
            },
            actor="human",
            actor_detail="human:风控审批人; confirmed_call:s4m3a-f4-live",
            request_id="s4m3a-f4-live",
        )
        assert res.outcome == "applied", f"现场驳回应生效: {res.error_code} {res.message}"
        order = conn.execute(
            "SELECT approve_order_status, opinion_description FROM approval.ap_approve_order "
            "WHERE approve_order_id=?", (PROP_APPROVE_ORDER_ID,)
        ).fetchone()
        tasks = conn.execute(
            "SELECT approve_task_id, approve_task_status, approve_result "
            "FROM approval.ap_approve_task WHERE approve_order_id=? ORDER BY approve_task_id",
            (PROP_APPROVE_ORDER_ID,),
        ).fetchall()
    finally:
        conn.close()
    assert order["approve_order_status"] == "REJECTED"
    assert "第二十三条" in (order["opinion_description"] or "")
    assert len(tasks) == 2
    by_result = {t["approve_result"] for t in tasks}
    assert by_result == {"APPROVED", "REJECTED"}, f"现场驳回后双节点应 APPROVED+REJECTED（实得 {by_result}）"
    assert all(t["approve_task_status"] == "COMPLETED" for t in tasks)


def _pick_process_order(store: RiskStore) -> dict:
    """从 ap_anping（或其副本）挑一个与处置关联的 PROCESS 审批单。

    F4：道具链（APP-2026-90000002）默认已是 REJECTED 预置驳回态（不可再审），
    故仅筛选 approve_order_status='PROCESS' 的审批单（含现场重置回 PENDING 的道具链）。
    """
    conn = store.source_conn()
    try:
        # 道具链：仅在其为 PROCESS（现场 reset 后）时优先
        prop = conn.execute(
            "SELECT approve_order_id, remark FROM approval.ap_approve_order "
            "WHERE approve_order_id=? AND approve_order_status='PROCESS'",
            (PROP_APPROVE_ORDER_ID,),
        ).fetchone()
        if prop and re.search(r"SGN-\d{4}-\d{8}", prop["remark"] or ""):
            m = re.search(r"SGN-\d{4}-\d{8}", prop["remark"])
            w = conn.execute(
                "SELECT warning_id FROM ap_warning_signal WHERE signal_id=?",
                (m.group(0),),
            ).fetchone()
            d = conn.execute(
                "SELECT disposal_id FROM ap_warning_disposal WHERE warning_id=?",
                (w["warning_id"],),
            ).fetchone()
            if w and d:
                return {
                    "order": prop["approve_order_id"],
                    "signal": m.group(0),
                    "warning": w["warning_id"],
                    "disposal": d["disposal_id"],
                }
        for o in conn.execute(
            "SELECT approve_order_id, remark FROM approval.ap_approve_order "
            "WHERE approve_order_status='PROCESS' LIMIT 300"
        ):
            m = re.search(r"SGN-\d{4}-\d{8}", o["remark"] or "")
            if not m:
                continue
            w = conn.execute(
                "SELECT warning_id FROM ap_warning_signal WHERE signal_id=?",
                (m.group(0),),
            ).fetchone()
            if not w:
                continue
            d = conn.execute(
                "SELECT disposal_id FROM ap_warning_disposal WHERE warning_id=?",
                (w["warning_id"],),
            ).fetchone()
            if d:
                return {
                    "order": o["approve_order_id"],
                    "signal": m.group(0),
                    "warning": w["warning_id"],
                    "disposal": d["disposal_id"],
                }
    finally:
        conn.close()
    raise AssertionError("ap_anping 未找到与处置关联的 PROCESS 审批单")


@pytest.fixture()
def act4_env(tmp_path_factory):
    """在 ap_anping 副本上建写引擎（第 4 幕写路径不污染演示数据）。"""
    dst = tmp_path_factory.mktemp("s4m3a_act4")
    for f in AP_ANPING_DIR.glob("*.db"):
        shutil.copy2(f, dst / f.name)
    store = RiskStore(ap_dir=dst, ontology_path=dst / "ontology.db")
    from src.runtime.risk_actions_impl import build_risk_engine

    engine = build_risk_engine(store=store)
    return store, engine


def test_act4_reject_returns_to_redraft(act4_env) -> None:
    """审批人依 2023 办法第二十三条驳回 → 处置退回重新起草（未处置），全程留痕。

    （口径包§七 第 4 幕：approve_disposal decision=REJECTED → 处置退回重新起草；
    驳回依据文案 = 第二十三条「禁止隐匿关联关系拆分交易」。）
    """
    store, engine = act4_env
    target = _pick_process_order(store)

    from src.runtime.risk_evidence import ARTICLE_2023_23

    opinion = (
        "驳回：AI 提议将天晟部分授信拆分至非关联第三方通道主体降低名义归集集中度，"
        "违反 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易）。"
        + ARTICLE_2023_23
    )
    res = engine.execute(
        "approve_disposal",
        {
            "approve_order_id": target["order"],
            "decision": "REJECTED",
            "opinion": opinion,
        },
        actor="human",
        actor_detail="human:风控审批人; confirmed_call:s4m3a",
        request_id="s4m3a-reject-test",
    )
    assert res.outcome == "applied", f"驳回应生效: {res.error_code} {res.message}"

    conn = store.source_conn()
    try:
        order = conn.execute(
            "SELECT approve_order_status, opinion_description "
            "FROM approval.ap_approve_order WHERE approve_order_id=?",
            (target["order"],),
        ).fetchone()
        disposal = conn.execute(
            "SELECT disposal_status FROM ap_warning_disposal WHERE disposal_id=?",
            (target["disposal"],),
        ).fetchone()
        signal = conn.execute(
            "SELECT disposal_status FROM ap_warning_signal WHERE warning_id=?",
            (target["warning"],),
        ).fetchone()
        tasks = conn.execute(
            "SELECT approve_task_status, approve_result FROM approval.ap_approve_task "
            "WHERE approve_order_id=?",
            (target["order"],),
        ).fetchall()
    finally:
        conn.close()
    assert order["approve_order_status"] == "REJECTED"
    assert "第二十三条" in (order["opinion_description"] or "")
    # 状态退回重新起草：处置回到 DRAFT（未处置），信号处置状态=暂缓处置
    assert disposal["disposal_status"] == "未处置", (
        f"处置应退回未处置重新起草（实得 {disposal['disposal_status']}）"
    )
    assert signal["disposal_status"] == "暂缓处置"
    assert tasks and all(t["approve_task_status"] == "COMPLETED" for t in tasks)
    assert all(t["approve_result"] == "REJECTED" for t in tasks)
    # 审计留痕
    n = engine.audit.query(action="approve_disposal", outcome="applied")[1]
    assert n >= 1


# ---------------------------------------------------------------------------
# 对话证据链：/agent/risk/chat 答案携带 evidence（剧本工具）
# ---------------------------------------------------------------------------


def test_agent_chat_evidence_attached(tmp_path, monkeypatch) -> None:
    """「天晟集团风险有多大」→ 答案携带第 1 幕证据链载荷（对话为演示一级入口）。"""
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t1",
                        name="risk_group_reveal",
                        arguments={"group_customer_no": TIANSHENG_NO},
                    )
                ]
            ),
            ChatResponse(
                content="天晟集团归集 86.4 亿元 ÷ 800 亿元 = 10.8%，触发橙色预警。"
            ),
        ]
    )
    # 路由内 from src.agent.provider import get_provider 在 app 创建时绑定 → 先打补丁再建 app
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "天晟集团风险有多大？"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["evidence"], "每个答案统一附证据链载荷"
        ev = body["evidence"][0]
        assert ev["intent"] == "act1_group_reveal"
        assert ev["rules_hits"][0]["rule"] == "R1a"
        assert ev["rules_hits"][0]["computed"]["ratio_display"] == "10.8%"
        assert ev["denominator"]["value_yi"] == GROUP_CAPITAL_YI


def test_two_consecutive_questions_evidence_backfilled(
    tmp_path, monkeypatch
) -> None:
    """两连问（附带 P2）：第二轮未命中工具（evidence=null）→ 用会话最近一次载荷补位。

    修复前第二轮 evidence=None，答案证据链断链；修复后回填上一轮证据链载荷。
    """
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t1",
                        name="risk_group_reveal",
                        arguments={"group_customer_no": TIANSHENG_NO},
                    )
                ]
            ),
            ChatResponse(content="天晟归集 86.4 亿元 ÷ 800 亿元 = 10.8%，橙色预警。"),
            # 第二轮：纯文本回答（无工具调用 → 无新证据）
            ChatResponse(content="分母是集团并表资本 800 亿元。"),
        ]
    )
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        r1 = c.post(
            "/agent/risk/chat",
            json={"message": "天晟集团风险有多大？", "session_id": "s-ev-backfill"},
        )
        assert r1.status_code == 200, r1.text
        assert r1.json()["evidence"]
        sid = r1.json()["session_id"]  # 会话由路由生成，取返回值续问
        r2 = c.post(
            "/agent/risk/chat",
            json={"message": "分母是什么？", "session_id": sid},
        )
        assert r2.status_code == 200, r2.text
        body = r2.json()
        assert body["evidence"], "两连问第二轮 evidence 应补位（不再 null）"
        assert body["evidence"][0]["intent"] == "act1_group_reveal"


def test_agent_chat_risk_query_evidence(tmp_path, monkeypatch) -> None:
    """普通 risk_query 答案也带最小证据链载荷（依据表名/明细行引用）。"""
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t2",
                        name="risk_query",
                        arguments={
                            "object_type": "warning_signal",
                            "filters": [
                                {"field": "warn_level", "op": "eq", "value": "红"}
                            ],
                            "aggregations": [{"function": "count", "field": "*"}],
                        },
                    )
                ]
            ),
            ChatResponse(content="红色预警若干条。"),
        ]
    )
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "红色预警几条？"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["evidence"]
        ev = body["evidence"][0]
        assert ev["intent"] == "risk_query:warning_signal"
        assert "ap_warning_signal" in ev["basis_tables"]

# ---------------------------------------------------------------------------
# R2-P0-A / R2-P1-B：质疑实查路径 + 思维链剥离（反编造防线）
# ---------------------------------------------------------------------------


def test_verify_reason_non_concentration_dimension(client: TestClient) -> None:
    """质疑实查：低集中度却标红的行 → warning_dimension=non_concentration（R2-P0-A/R2-P1-A）。

    华信建设西南集团集中度实算 0.41%（< 关注线 9%，R1a 定级「无」）却挂红——
    真实原因 = 非集中度维度（资质缺失异常/模型评分 88），不得套集中度逻辑错答。
    （F26 勘误：早期材料误写 6.2%，实算以 0.41% 为准——单一事实来源。）
    """
    data = client.get(
        "/risk/evidence/verify-reason",
        params={"group_customer_no": HUAXIN_SW_NO},
    ).json()["data"]
    assert data["intent"] == "risk_verify_reason"
    assert data["warning_dimension"] == "non_concentration"
    for key in EVIDENCE_KEYS:
        assert key in data, f"质疑实查载荷缺 {key}"
    comp = data["rules_hits"][0]["computed"]
    assert comp["ratio"] < 0.09 and comp["level"] == "无"
    assert "非集中度维度" in data["conclusion"]
    sig = data["detail_rows"][0]["signals"][0]
    assert sig["warn_level"] == "红"
    assert "模型评分" in (sig["warn_reason"] or "")
    assert data["denominator"]["value_yi"] == GROUP_CAPITAL_YI


def test_verify_reason_concentration_dimension(client: TestClient) -> None:
    """质疑实查：天晟 → warning_dimension=concentration，R1a computed 12.8% 红（口径包§七 第 2 幕）。"""
    data = client.get(
        "/risk/evidence/verify-reason", params={"group_customer_no": TIANSHENG_NO}
    ).json()["data"]
    assert data["warning_dimension"] == "concentration"
    comp = data["rules_hits"][0]["computed"]
    assert comp["ratio"] == pytest.approx(0.128, abs=1e-3)
    assert comp["ratio_display"] == "12.8%"
    assert comp["level"] == "红"


def test_agent_challenge_routes_to_verify_reason(tmp_path, monkeypatch) -> None:
    """质疑预设（凭什么挂红）→ 实查路径：调 risk_verify_reason 按实回答（R2-P0-A 防线）。

    挑战消息必须落到 risk_verify_reason 证据链（warning_dimension + R1a computed 比对），
    回答附证据链载荷，绝不凭空合成集中度明细。
    """
    from src.agent.provider import ChatResponse, MockProvider, ToolCall

    mock = MockProvider(
        responses=[
            ChatResponse(
                tool_calls=[
                    ToolCall(
                        id="t3",
                        name="risk_verify_reason",
                        arguments={"group_customer_no": HUAXIN_SW_NO},
                    )
                ]
            ),
            ChatResponse(
                content=(
                    "让我先理清用户的问题。该行标红原因是非集中度维度"
                    "（华信建设西南集团集中度实算 0.41%，R1a 定级「无」），"
                    "真实触发是资质缺失异常/模型评分 88，见证据链。"
                )
            ),
        ]
    )
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post(
            "/agent/risk/chat",
            json={"message": "华信建设西南集团才 0.41% 凭什么挂红？"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["evidence"], "质疑路径必须走实查证据链"
        ev = body["evidence"][0]
        assert ev["intent"] == "risk_verify_reason"
        assert ev["warning_dimension"] == "non_concentration"
        assert ev["rules_hits"][0]["computed"]["level"] == "无"
        # 思维链剥离：内心独白前缀不得上屏
        assert not body["reply"].startswith("让我先理清")
        assert "非集中度维度" in body["reply"]


def test_agent_chat_strips_chain_of_thought(tmp_path, monkeypatch) -> None:
    """思维链剥离：回复返回前剥离「让我先理清/我需要先」类内心独白前缀（R2-P1-B）。"""
    from src.agent.provider import ChatResponse, MockProvider

    mock = MockProvider(
        responses=[
            ChatResponse(
                content=(
                    "让我先理清用户的问题。天晟集团归集 86.4 亿元 ÷ 800 亿元 = "
                    "10.8%，触发橙色预警。"
                )
            )
        ]
    )
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "天晟集团风险有多大？"})
        assert res.status_code == 200, res.text
        reply = res.json()["reply"]
        assert not reply.startswith("让我先理清")
        assert reply.startswith("天晟集团")


# ---------------------------------------------------------------------------
# F16：相邻排名精度区分 + 等线判定措辞；F17：R2 note 按实际关联方条件输出
# （05 清单第六轮复测残留：rank9/10 同显 0.9%、等线称「内」与 ≥ 触发规则矛盾、
#   note 跨组硬编码泄漏恒昌文案）
# ---------------------------------------------------------------------------


def test_f16_ranking_adjacent_display_distinct(client: TestClient) -> None:
    """F16①：前十大排名展示值两两可区分，rank9/rank10 不再同显 0.9%。"""
    ranking = _dash_ranking(client)
    displays = [g["concentration_ratio_display"] for g in ranking]
    assert len(displays) == len(set(displays)), f"排名展示值有并列: {displays}"
    # F20/F21 补腰后：rank9 盛世 3.2%、rank10 翔宇东北 0.9332%（仍两两可区分）
    assert displays[8] == "3.2%" and displays[9] == "0.9332%"


def test_f16_equal_line_wording_touched(client: TestClient) -> None:
    """F16②：证券 5.5% / 资管 8.2% 恰等参考线 = 触达（达线即警），不得称「参考线内」。"""
    reveal = _reveal(client)
    assert "触达参考线 5.5%，达线即警" in reveal["conclusion"]
    assert "触达参考线 8.2%，达线即警" in reveal["conclusion"]
    assert "参考线 5.5% 内" not in reveal["conclusion"]
    assert "参考线 8.2% 内" not in reveal["conclusion"]
    assert "已触达参考线" in reveal["conclusion"]
    # F25：不得出现嵌套括号「（触达参考线 5.5%（达线即警））」
    assert "（触达参考线 5.5%（" not in reveal["conclusion"]


def test_f17_note_conditional_on_related_parties(client: TestClient) -> None:
    """F17：note 按实识别关联方输出——天晟带恒昌；无关联集团（翔宇东北 05）不泄漏恒昌文案。"""
    assert "恒昌贸易" in _reveal(client)["r2_levels"]["note"]
    assert "恒昌贸易" in _upgrade(client)["r2_levels"]["note"]
    res = client.get(
        "/risk/evidence/group-reveal",
        params={"group_customer_no": "GRP-2026-001516"},
    )
    assert res.status_code == 200, res.text
    rl = res.json()["data"]["r2_levels"]
    assert rl["pre_r2"]["ratio_display"] == "0.93%"
    assert rl["post_r2"]["ratio_display"] == "0.93%"
    assert "恒昌贸易" not in rl["note"]
    assert "无隐性关联纳入" in rl["note"]
    up = client.get(
        "/risk/evidence/related-upgrade",
        params={"group_customer_no": "GRP-2026-001516"},
    ).json()["data"]
    assert "恒昌贸易" not in up["r2_levels"]["note"]
    assert "无隐性关联纳入" in up["r2_levels"]["note"]


def test_f17_related_tail_note_conditional(client: TestClient) -> None:
    """F17：conclusion「纳入隐性关联前口径」尾注仅在确有纳入时追加。"""
    assert "本行为纳入隐性关联前的归集口径" in _reveal(client)["conclusion"]
    res = client.get(
        "/risk/evidence/group-reveal",
        params={"group_customer_no": "GRP-2026-001516"},
    ).json()["data"]
    assert "本行为纳入隐性关联前的归集口径" not in res["conclusion"]


def test_f24_thresholds_include_org_ref_lines(client: TestClient) -> None:
    """F24：机构级参考线（银行 60 亿/证券 5.5%/资管 8.2%）在 thresholds 可查证出处。"""
    data = client.get("/risk/thresholds").json()["data"]
    ids = {p["param_id"] for p in data["detail_rows"]}
    assert {
        "CAP_BANK_INTERNAL_LIMIT",
        "CAP_SECURITIES_REF_LINE",
        "CAP_AM_REF_LINE",
    } <= ids, f"thresholds 缺机构参考线参数行: {ids}"
    org_rows = {
        p["param_id"]: p for p in data["detail_rows"] if p["param_id"] in (
            "CAP_BANK_INTERNAL_LIMIT",
            "CAP_SECURITIES_REF_LINE",
            "CAP_AM_REF_LINE",
        )
    }
    for pid, row in org_rows.items():
        assert row["param_source"], f"{pid} 缺出处条款"
        assert row["param_approver"], f"{pid} 缺审批人"
    assert "机构级参考线" in data["conclusion"]


def test_f25_wording_polish(client: TestClient) -> None:
    """F25：文案细节包——「该集团」量词、verify-reason 比率不重复、审批链拼接无「。，」。"""
    vr = client.get(
        "/risk/evidence/verify-reason",
        params={"group_customer_no": "GRP-2026-001516"},
    ).json()["data"]
    assert "该集团标橙原因" in vr["conclusion"]
    assert "该行标" not in vr["conclusion"]
    assert "实算 0.93%（0.93%" not in vr["conclusion"], "比率不应重复出现"
    ac = client.get(
        "/risk/evidence/approval-chain",
        params={"warning_id": "WS-2026-90000002"},
    ).json()["data"]
    assert "。，" not in ac["conclusion"], f"审批链结论有拼接残渣: {ac['conclusion'][-120:]}"


# ---------------------------------------------------------------------------
# F18：审计演示视图（business 默认过滤开发痕，view=all 全量透明）
# F22：chat 出口兜底（独白全文剥离 + 新会话质疑反问定位）
# ---------------------------------------------------------------------------


def test_f18_audit_business_view_filters_smoke(client: TestClient) -> None:
    """F18：business 视图无 smoke-*/空 request_id 行；view=all 全量保留（WORM 不动）。"""
    biz = client.get("/risk/audit").json()["data"]
    assert biz["view"] == "business"
    for it in biz["items"]:
        rid = (it.get("request_id") or "").strip()
        assert rid and not rid.startswith("smoke-"), f"演示视图泄漏开发痕: {it}"
    allv = client.get("/risk/audit", params={"view": "all", "page_size": 100}).json()[
        "data"
    ]
    assert allv["total"] == 55 and allv["migrated_records"] == 0
    # action 过滤与视图叠加：approve_disposal 业务行仅预置驳回 1 条
    appr = client.get(
        "/risk/audit", params={"action": "approve_disposal"}
    ).json()["data"]
    assert appr["total"] == 1
    assert appr["items"][0]["request_id"] == "REJ-2026-90000002"


def test_f22_strip_chain_of_thought_fulltext() -> None:
    """F22①：独白剥离扩全文——中后部独白句删除，含「您/请」的对话句保留。"""
    from src.agent.risk_agent import strip_chain_of_thought

    reply = (
        "天晟集团归集 86.4 亿元 ÷ 800 亿元 = 10.8%，触发橙色预警。"
        "我应该查询该集团的信号明细。让我先理清用户的问题。"
        "经过分析，该集团标红原因见证据链。"
    )
    out = strip_chain_of_thought(reply)
    assert "我应该" not in out and "让我先理清" not in out
    assert "天晟集团归集" in out and "证据链" in out
    # 含「您」的句子是澄清正文，绝不误删
    keep = strip_chain_of_thought("我想先说明，您问的集团编号需要核对。天晟 10.8% 橙。")
    assert "您问的集团编号" in keep
    # 全部句子都是独白时保守返回，绝不让回复变空白
    assert strip_chain_of_thought("让我先理清。我想想。").strip()


def test_f22_challenge_without_object_asks_back(
    tmp_path, monkeypatch
) -> None:
    """F22②：新会话直接质疑且未定位对象 → 规则层反问定位（不经 LLM，零幻觉面）。"""
    from src.agent.provider import MockProvider

    mock = MockProvider(responses=[])  # 反问路径不应触达 LLM
    monkeypatch.setattr("src.agent.provider.get_provider", lambda name=None: mock)

    from src.app.main import create_risk_agent_app

    app = create_risk_agent_app()
    with TestClient(app) as c:
        res = c.post("/agent/risk/chat", json={"message": "凭什么把它标红？"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert "定位对象" in body["reply"], f"应反问定位: {body['reply'][:80]}"
        assert body["evidence"] is None
        # 已定位对象（带集团名）的正常提问不受影响——走 LLM 编排（此处 mock 无响应即报错，
        # 反问路径不触发即视为通过；编排链路已有独立测试覆盖）
