"""S3 M3b 风险 Agent 对话 冒烟验证（独立脚本，不经 pytest，/opt/anaconda3/bin/python3 直跑）。

覆盖（对应交付物 4）：
A. 读引擎精准问答：评测集 R01/R05/R11/R14/R19（用真实 ap_anping 数据 + 直接 SQL 对答案），
   D01 域外拒答（fail-closed DECLINE）；
B. 写引擎经 Agent 层：high_risk 动作（adjust_warning_level）→ need_confirm → 确认 →
   真实写回 + 审计；拒绝 → 不执行；双签强制（确认前绝不执行）；
C. 端点冒烟：/agent/risk/chat + /agent/risk/confirm（TestClient）。
可选 D：真实 LLM 实测（RISK_CHAT_REAL=1 且 DEEPSEEK_API_KEY 就绪时，信息性不参与 PASS/FAIL）。

【评测集适配说明】docs/S3-M3-评测集30题-v1.md 的实体名（华夏新能源集团/华辰制造）来自设计
文档占位，DES 生成的真实 ap_anping 数据用另一批虚构企业名；冒烟按题目模式适配到真实企业
（如 中科智造控股集团有限公司）并以直接 SQL 交叉验证答案正确性。

运行：/opt/anaconda3/bin/python3 scripts/smoke_risk_chat.py（仓库根目录）。
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.provider import ChatResponse, MockProvider, ToolCall
from src.agent.risk_agent import RiskActionExecutor, RiskAgent
from src.runtime.audit import AuditLog
from src.runtime.risk_actions_impl import build_risk_engine
from src.runtime.risk_db import RiskStore, build_risk_source_registry
from src.runtime.risk_query import RiskQuery, RiskQueryError

_FAILURES: list[str] = []
_MONTH = ("2026-12-01", "2026-12-31")  # 演示数据"本月"（数据截至 2026-12-31）
_GROUP = ""  # 评测 R01/R19 的真实集团（名称带唯一序号后缀，test_read_engine 开头动态解析）


def check(cond: bool, msg: str) -> bool:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        _FAILURES.append(msg)
    return cond


def _q(store: RiskStore, sql: str, args: tuple = ()) -> list[dict]:
    conn = store.source_conn()
    try:
        cur = conn.execute(sql, args)
        return [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    finally:
        conn.close()


def _q1(store: RiskStore, sql: str, args: tuple = ()):
    rows = _q(store, sql, args)
    return rows[0] if rows else None


def _run(rq: RiskQuery, contract: dict) -> dict:
    """执行契约；抛 RiskQueryError 时返回拒答信封（供断言语义）。"""
    try:
        return rq.execute(contract)
    except RiskQueryError as exc:
        return {"__declined__": exc.code, "__msg__": str(exc)}


def _is_declined(res: dict) -> bool:
    return "__declined__" in res


# ======================================================================
# A. 读引擎：R01/R05/R11/R14/R19 + D01
# ======================================================================


def test_read_engine(rq: RiskQuery, store: RiskStore) -> None:
    print("\n[A] 读引擎精准问答（真实 ap_anping 数据，直接 SQL 对答案）")
    global _GROUP
    _GROUP = _q1(store, "SELECT group_customer_name FROM customer.ap_group_customer ORDER BY group_customer_no LIMIT 1")["group_customer_name"]
    print(f"    演示集团（动态解析）: {_GROUP}")

    # ---- R01 集团客户编号 + 成员企业数 ----
    print("\n[R01] 集团客户编号和成员企业数")
    res = _run(rq, {
        "object_type": "group_customer",
        "filters": [{"field": "group_customer_name", "op": "eq", "value": _GROUP}],
        "limit": 1,
    })
    check(not _is_declined(res) and res.get("count") == 1, "R01 查询成功且命中 1 个集团")
    gt = _q1(store, "SELECT group_customer_no FROM customer.ap_group_customer "
                    "WHERE group_customer_name=? ORDER BY group_customer_no LIMIT 1", (_GROUP,))
    if gt:
        prop = res["items"][0]["properties"]
        mc_gt = _q1(store, "SELECT COUNT(*) n FROM customer.ap_customer WHERE group_customer_no=?",
                    (gt["group_customer_no"],))["n"]
        check(
            prop["group_customer_no"] == gt["group_customer_no"]
            and prop["member_count"] == mc_gt,
            f"R01 集团编号 {prop['group_customer_no']} / 成员数 {prop['member_count']}（GT={mc_gt}）",
        )

    # ---- R05 本月新增红色预警数 ----
    print("\n[R05] 本月新增的红色预警信号有几条")
    res = _run(rq, {
        "object_type": "warning_signal",
        "filters": [
            {"field": "warn_level", "op": "eq", "value": "红"},
            {"field": "signal_generate_date", "op": "ge", "value": _MONTH[0]},
            {"field": "signal_generate_date", "op": "le", "value": _MONTH[1]},
        ],
        "aggregations": [{"function": "count", "field": "*"}],
    })
    n = res["aggregations"][0]["value"] if not _is_declined(res) else None
    n_gt = _q1(store, "SELECT COUNT(*) n FROM ap_warning_signal WHERE warn_level='红' "
                      "AND signal_generate_date BETWEEN ? AND ?", _MONTH)["n"]
    check(n == n_gt, f"R05 红色预警 {n} 条（GT={n_gt}）")

    # ---- R11 集中度超限客户数 ----
    print("\n[R11] 哪些客户集中度超过集团资本净额 15%（= current_status RED_ALERT）")
    res = _run(rq, {
        "object_type": "concentration_limit",
        "filters": [{"field": "current_status", "op": "eq", "value": "RED_ALERT"}],
        "aggregations": [{"function": "count", "field": "*"}],
    })
    n = res["aggregations"][0]["value"] if not _is_declined(res) else None
    n_gt = _q1(store, "SELECT COUNT(*) n FROM concentration.ap_concentration_limit "
                      "WHERE current_status='RED_ALERT'")["n"]
    check(n == n_gt, f"R11 集中度超限客户 {n} 家（GT={n_gt}）；另取 Top5 名单抽查")
    res_top = _run(rq, {
        "object_type": "concentration_limit",
        "filters": [{"field": "current_status", "op": "eq", "value": "RED_ALERT"}],
        "order_by": [{"field": "concentration_limit", "direction": "desc"}],
        "limit": 5,
    })
    check(not _is_declined(res_top) and len(res_top["items"]) == 5, "R11 Top5 名单可查")

    # ---- R14 处置方案审批到哪个岗位 ----
    print("\n[R14] 集团预警的处置方案当前审批到哪个岗位")
    chain = _q(store, "SELECT DISTINCT g.group_customer_name FROM ap_warning_signal w "
                      "JOIN customer.ap_group_customer g ON w.group_customer_no=g.group_customer_no "
                      "JOIN ap_warning_disposal wd ON w.warning_id=wd.warning_id "
                      "JOIN approval.ap_approve_order o ON o.remark LIKE '%'||w.signal_id||'%' "
                      "JOIN approval.ap_approve_task t ON t.approve_order_id=o.approve_order_id "
                      "AND t.approve_task_status='PENDING' "
                      "WHERE o.approve_order_status='PROCESS' LIMIT 1")
    if not chain:
        check(False, "R14 未发现含审批链的集团（数据依赖）")
        return
    gname = chain[0]["group_customer_name"]
    res = _run(rq, {"analytic": "warning_approval_step", "params": {"group_customer_name": gname}})
    check(not _is_declined(res) and res.get("rows"), f"R14 analytic 命中（集团 {gname}）")
    if res.get("rows"):
        gt_step = _q1(store, "SELECT n.approve_node_name, t.post_id FROM ap_warning_signal w "
                      "JOIN customer.ap_group_customer g ON w.group_customer_no=g.group_customer_no "
                      "JOIN ap_warning_disposal wd ON w.warning_id=wd.warning_id "
                      "JOIN approval.ap_approve_order o ON o.remark LIKE '%'||w.signal_id||'%' "
                      "JOIN approval.ap_approve_task t ON t.approve_order_id=o.approve_order_id "
                      "AND t.approve_task_status='PENDING' "
                      "JOIN approval.ap_approve_node n ON t.approve_node_id=n.approve_node_id "
                      "WHERE g.group_customer_name=? AND o.approve_order_status='PROCESS' "
                      "ORDER BY n.approve_node_seq LIMIT 1", (gname,))
        check(
            gt_step and res["rows"][0]["approve_node_name"] == gt_step["approve_node_name"],
            f"R14 当前审批岗位 = {res['rows'][0]['approve_node_name']}（GT={gt_step['approve_node_name'] if gt_step else None}）",
        )

    # ---- R19 风险项目业务余额 + 已计提减值 ----
    print("\n[R19] 集团风险项目业务余额和已计提减值")
    res = _run(rq, {
        "object_type": "risk_project",
        "filters": [{"field": "group_customer_name", "op": "eq", "value": _GROUP}],
        "aggregations": [
            {"function": "sum", "field": "business_balance"},
            {"function": "sum", "field": "impairment_provision"},
        ],
    })
    gt = _q1(store, "SELECT COALESCE(SUM(business_balance),0) bb, "
                    "COALESCE(SUM(impairment_provision),0) ip FROM project.ap_risk_project "
                    "WHERE group_customer_name=?", (_GROUP,))
    if not _is_declined(res):
        bb = res["aggregations"][0]["value"]
        ip = res["aggregations"][1]["value"]
        check(
            abs(bb - gt["bb"]) < 1e-6 and abs(ip - gt["ip"]) < 1e-6,
            f"R19 业务余额 {bb:.2f} / 减值 {ip:.2f}（GT={gt['bb']:.2f}/{gt['ip']:.2f}）",
        )

    # ---- 抽查（信息性 PASS） ----
    print("\n[R17] 已销号预警数（抽查）")
    res = _run(rq, {
        "object_type": "warning_signal",
        "filters": [{"field": "signal_status", "op": "eq", "value": "CLOSED"}],
        "aggregations": [{"function": "count", "field": "*"}],
    })
    n = res["aggregations"][0]["value"] if not _is_declined(res) else None
    n_gt = _q1(store, "SELECT COUNT(*) n FROM ap_warning_signal WHERE signal_status='已关闭'")["n"]
    check(n == n_gt, f"R17 已销号 {n} 条（GT={n_gt}）")

    print("\n[R18] 五级分类=次级 风险项目数（抽查）")
    res = _run(rq, {
        "object_type": "risk_project",
        "filters": [{"field": "five_classification", "op": "eq", "value": "SECONDARY"}],
        "aggregations": [{"function": "count", "field": "*"}],
    })
    n = res["aggregations"][0]["value"] if not _is_declined(res) else None
    n_gt = _q1(store, "SELECT COUNT(*) n FROM project.ap_risk_project WHERE five_classification='SECONDARY'")["n"]
    check(n == n_gt, f"R18 次级项目 {n} 个（GT={n_gt}）")

    print("\n[R23] 最近 6 个月预警数量月度趋势（抽查，group_by 月粒度）")
    res = _run(rq, {
        "object_type": "warning_signal",
        "filters": [
            {"field": "signal_generate_date", "op": "ge", "value": "2026-07-01"},
            {"field": "signal_generate_date", "op": "le", "value": "2026-12-31"},
        ],
        "group_by": [{"field": "signal_generate_date", "granularity": "month"}],
        "aggregations": [{"function": "count", "field": "*"}],
    })
    check(not _is_declined(res) and res.get("row_count", 0) == 6, "R23 月度趋势 6 个月分组可查")

    # ---- D01 域外拒答（fail-closed） ----
    print("\n[D01] 域外拒答（fail-closed，不瞎编）")
    res = _run(rq, {"object_type": "organization", "filters": []})
    check(_is_declined(res) and res["__declined__"] == "OBJECT_NOT_QUERYABLE",
          f"D01 无源表对象拒答（{res.get('__declined__')}）")
    res = _run(rq, {"object_type": "warning_signal",
                    "filters": [{"field": "total_exposure", "op": "eq", "value": 1}]})
    check(_is_declined(res) and res["__declined__"] == "UNKNOWN_FILTER_FIELD",
          f"D01 不可达字段拒答（{res.get('__declined__')}）")
    res = _run(rq, {"object_type": "metric",
                    "filters": [{"field": "index_name", "op": "eq", "value": "资本充足率"}],
                    "aggregations": [{"function": "sum", "field": "index_value"}]})
    check(not _is_declined(res) and res["aggregations"][0]["value"] is None,
          "D01 资本充足率指标查无数据（空结果，交由 Agent 层按域外拒答）")


# ======================================================================
# B. 写引擎经 Agent 层（双签 + 真实写回 + 审计）
# ======================================================================


def test_write_via_agent(store: RiskStore, engine, rq: RiskQuery) -> None:
    print("\n[B] 写引擎经 Agent 层：high_risk 双签 → 确认 → 真实写回 + 审计")
    executor = RiskActionExecutor(engine, rq)

    w = _q1(store, "SELECT warning_id, warn_level FROM ap_warning_signal WHERE signal_status='确认中' LIMIT 1")
    check(w is not None, "找到确认中(CONFIRMED)预警供调级")
    if not w:
        return
    new_level = "红" if w["warn_level"] != "红" else "橙"

    prov = MockProvider(responses=[
        ChatResponse(tool_calls=[ToolCall(
            id="t1",
            name="adjust_warning_level",
            arguments={"warning_id": w["warning_id"], "new_level": new_level, "reason": "模型评分上调，升级预警"},
        )]),
    ])
    agent = RiskAgent(registry=build_risk_source_registry(), provider=prov,
                      executor=executor, query=rq)
    turn = agent.run_turn("把这条预警等级调整到更高等级")
    check(
        turn.need_confirm is not None and turn.need_confirm.name == "adjust_warning_level",
        "B1 high_risk 动作必须先 need_confirm（未执行）",
    )
    check(
        len(turn.tool_results) == 0,
        "B2 确认前零执行（tool_results 为空，双签强制）",
    )

    prov2 = MockProvider(responses=[ChatResponse(content="已按确认执行。")])
    agent2 = RiskAgent(registry=build_risk_source_registry(), provider=prov2,
                       executor=executor, query=rq)
    agent2.set_pending(turn.need_confirm)
    turn2 = agent2.confirm_pending(True, confirmant="human", confirmant_detail="风控主管-张")
    last = json.loads(turn2.tool_results[-1].content)
    check(last["outcome"] == "applied", f"B3 确认后 applied（outcome={last['outcome']}）")
    row = _q1(store, "SELECT warn_level, signal_status FROM ap_warning_signal WHERE warning_id=?",
              (w["warning_id"],))
    check(
        row["warn_level"] == new_level and row["signal_status"] == "已确认",
        f"B4 真实写回：warn_level {w['warn_level']}→{row['warn_level']}，信号状态→已确认(GRADED)",
    )
    audit = AuditLog(store)
    n = audit.query(action="adjust_warning_level", outcome="applied")[1]
    check(n == 1, f"B5 审计 applied 记录 = {n}")

    prov3 = MockProvider(responses=[
        ChatResponse(tool_calls=[ToolCall(
            id="t3", name="adjust_warning_level",
            arguments={"warning_id": w["warning_id"], "new_level": "紫", "reason": "x"},
        )]),
    ])
    agent3 = RiskAgent(registry=build_risk_source_registry(), provider=prov3,
                       executor=executor, query=rq)
    turn3 = agent3.run_turn("再调一次")
    prov4 = MockProvider(responses=[ChatResponse(content="已取消。")])
    agent4 = RiskAgent(registry=build_risk_source_registry(), provider=prov4,
                       executor=executor, query=rq)
    agent4.set_pending(turn3.need_confirm)
    turn4 = agent4.confirm_pending(False)
    last4 = json.loads(turn4.tool_results[-1].content)
    check(last4["outcome"] == "cancelled_by_user", "B6 拒绝 → cancelled_by_user（未执行）")

    cw = _q1(store, "SELECT warning_id FROM ap_warning_signal WHERE signal_status='待确认' LIMIT 1")
    if cw:
        prov5 = MockProvider(responses=[
            ChatResponse(tool_calls=[ToolCall(id="t5", name="confirm_warning",
                                              arguments={"warning_id": cw["warning_id"]})]),
            ChatResponse(content="已确认该预警信号。"),
        ])
        agent5 = RiskAgent(registry=build_risk_source_registry(), provider=prov5,
                           executor=executor, query=rq)
        turn5 = agent5.run_turn("把这条预警确认一下")
        check(turn5.need_confirm is None, "B7 非高风险 confirm_warning 无需双签（直接执行）")
        check(any(json.loads(r.content)["outcome"] == "applied" for r in turn5.tool_results),
              "B8 confirm_warning 执行 applied")


# ======================================================================
# C. 端点冒烟（TestClient）
# ======================================================================


def test_endpoints() -> None:
    print("\n[C] /agent/risk 端点冒烟（TestClient）")
    try:
        from fastapi.testclient import TestClient

        from src.app.main import create_risk_agent_app
    except Exception as exc:  # noqa: BLE001
        check(False, f"端点评测依赖不可用: {exc}")
        return
    os.environ["LLM_PROVIDER"] = "mock"  # 端点默认 provider 走 mock，不依赖 API key
    app = create_risk_agent_app()
    client = TestClient(app)
    r = client.post("/agent/risk/chat", json={"message": "本月红色预警几条？"})
    body = r.json()
    check(r.status_code == 200 and body.get("session_id"), "C1 /agent/risk/chat 200 + session")
    r2 = client.post("/agent/risk/confirm", json={"session_id": body["session_id"],
                                                  "call_id": "nope", "confirmed": True})
    check(r2.status_code == 400, "C2 无待确认提议 → 400")
    r3 = client.post("/agent/risk/chat", json={"message": "hi"}, headers={"X-Actor": "robot"})
    check(r3.status_code == 400, "C3 非法 actor → 400")


# ======================================================================
# D. 真实 LLM 实测（可选：RISK_CHAT_REAL=1 且 DEEPSEEK_API_KEY 就绪）
# ======================================================================


def test_real_llm(store: RiskStore, engine, rq: RiskQuery) -> None:
    if os.environ.get("RISK_CHAT_REAL") != "1":
        return
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("\n[D] 未设置 DEEPSEEK_API_KEY，跳过真实 LLM 实测（可设 RISK_CHAT_REAL=1 启用）")
        return
    print("\n[D] 真实 LLM 实测（RISK_CHAT_REAL=1，信息性）")
    from src.agent.provider import get_provider
    executor = RiskActionExecutor(engine, rq)
    provider = get_provider("deepseek")
    agent = RiskAgent(registry=build_risk_source_registry(), provider=provider,
                      executor=executor, query=rq)
    for question in ("本月新增的红色预警信号有几条？", "华夏新能源集团的资本充足率是多少？（域外，应拒答）"):
        try:
            turn = agent.run_turn(question)
            print(f"  Q: {question}\n  A: {turn.reply}\n  need_confirm: {turn.need_confirm is not None}")
        except Exception as exc:  # noqa: BLE001
            print(f"  真实 LLM 调用失败（信息性，不判失败）: {exc}")


def main() -> int:
    print("== S3 M3b 风险 Agent 对话 冒烟验证 ==")

    tmp = tempfile.mkdtemp(prefix="s3_risk_chat_smoke_")
    store = RiskStore(ontology_path=Path(tmp) / "ontology.db")
    registry = build_risk_source_registry()
    engine = build_risk_engine(store=store, registry=registry)
    rq = RiskQuery(registry, store=store)
    print(f"数据截至：{rq.as_of_date()}；可查对象：{', '.join(rq.queryable_objects())}")

    test_read_engine(rq, store)
    test_write_via_agent(store, engine, rq)
    test_endpoints()
    test_real_llm(store, engine, rq)

    print()
    if _FAILURES:
        print(f"FAILED {len(_FAILURES)} 项：")
        for f in _FAILURES:
            print(f"  - {f}")
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
