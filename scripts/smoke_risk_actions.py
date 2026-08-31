"""S3 M3 风险动作写引擎冒烟验证（独立脚本，不经 pytest，/opt/anaconda3/bin/python3 直跑）。

对 9 个风险动作逐一验证（对应交付物 4）：
1. 合法参数 → 执行 → 数据库真实变更（如 adjust_warning_level 后 warn_level 真变）
   + 状态机正确迁移 + 审计记录生成（含哈希链完整）；
2. 非法参数/非法状态 → 返回正确错误码（如对已关闭信号调 confirm_warning → 报错）；
3. 每个动作输出 PASS/FAIL，全部通过退出码 0。

注意：本脚本真实写回 ap_anping 数据（六库），审计落独立临时本体库；每次运行按起始状态
现取数据行，可重复运行。运行：/opt/anaconda3/bin/python3 scripts/smoke_risk_actions.py
"""

from __future__ import annotations

import re
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.runtime.audit import AuditLog
from src.runtime.risk_actions_impl import build_risk_engine
from src.runtime.risk_db import RiskStore

_FAILURES: list[str] = []


def check(cond: bool, msg: str) -> bool:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        _FAILURES.append(msg)
    return cond


def _pick(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> sqlite3.Row | None:
    return conn.execute(sql, args).fetchone()


def _ontology_value(engine, object_type: str, pk: str, prop: str) -> str | None:
    """本体自有状态（ontology_state 表在独立本体库，非源库）。"""
    con = engine.store.ontology_conn()
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            "SELECT value FROM ontology_state WHERE object_type=? AND pk=? AND prop=?",
            (object_type, pk, prop),
        ).fetchone()
        return row["value"] if row else None
    finally:
        con.close()


def applied_count(audit: AuditLog, action: str) -> int:
    _, total = audit.query(action=action, outcome="applied")
    return total


def main() -> int:
    print("== S3 M3 金控风控 9 风险动作 写引擎冒烟 ==")

    # 独立临时本体库（审计落库不污染演示库；源数据仍是 ap_anping 六库真写）
    tmp = tempfile.mkdtemp(prefix="s3_risk_smoke_")
    store = RiskStore(ontology_path=Path(tmp) / "ontology.db")
    engine = build_risk_engine(store=store)
    conn = engine.store.source_conn()
    conn.row_factory = sqlite3.Row
    audit = AuditLog(engine.store)
    n_actions = 9

    # ==================================================================
    # 1) confirm_warning 预警信号确认（GENERATED→CONFIRMED）
    # ==================================================================
    print("\n[1] confirm_warning")
    before = applied_count(audit, "confirm_warning")
    wid = _pick(
        conn,
        "SELECT warning_id FROM ap_warning_signal WHERE signal_status='待确认' LIMIT 1",
    )
    check(wid is not None, "找到待确认(GENERATED)信号")
    if wid:
        res = engine.execute(
            "confirm_warning",
            {"warning_id": wid["warning_id"]},
            actor="llm",
            request_id="smoke-m3",
        )
        row = _pick(
            conn,
            "SELECT signal_status FROM ap_warning_signal WHERE warning_id=?",
            (wid["warning_id"],),
        )
        check(res.outcome == "applied", f"确认 applied（error_code={res.error_code}）")
        check(
            row["signal_status"] == "确认中",
            f"信号状态迁移 待确认→确认中（实际 {row['signal_status']}）",
        )
        check(
            applied_count(audit, "confirm_warning") == before + 1,
            "审计 applied 记录 +1",
        )
        # 重复确认 → 拒绝
        res2 = engine.execute(
            "confirm_warning", {"warning_id": wid["warning_id"]}, actor="llm"
        )
        check(
            res2.outcome == "rejected" and res2.error_code == "WARNING_NOT_CONFIRMABLE",
            f"重复确认拒绝 WARNING_NOT_CONFIRMABLE（outcome={res2.outcome} code={res2.error_code}）",
        )
    # 不存在 → WARNING_NOT_FOUND
    res3 = engine.execute(
        "confirm_warning", {"warning_id": "WS-9999-99999999"}, actor="llm"
    )
    check(
        res3.error_code == "WARNING_NOT_FOUND",
        f"不存在信号 → WARNING_NOT_FOUND（{res3.error_code}）",
    )

    # ==================================================================
    # 2) adjust_warning_level 预警等级调整（CONFIRMED→GRADED）
    # ==================================================================
    print("\n[2] adjust_warning_level")
    before = applied_count(audit, "adjust_warning_level")
    w = _pick(
        conn,
        "SELECT warning_id, warn_level FROM ap_warning_signal WHERE signal_status='确认中' LIMIT 1",
    )
    check(w is not None, "找到确认中(CONFIRMED)信号")
    if w:
        new_level = "红" if w["warn_level"] != "红" else "橙"
        res = engine.execute(
            "adjust_warning_level",
            {
                "warning_id": w["warning_id"],
                "new_level": new_level,
                "reason": "模型评分上调，升级预警",
            },
            actor="human",
            request_id="smoke-m3",
        )
        row = _pick(
            conn,
            "SELECT warn_level, signal_status FROM ap_warning_signal WHERE warning_id=?",
            (w["warning_id"],),
        )
        check(res.outcome == "applied", f"调整 applied（error_code={res.error_code}）")
        check(
            row["warn_level"] == new_level,
            f"warn_level 真变：{w['warn_level']}→{row['warn_level']}（期望 {new_level}）",
        )
        check(
            row["signal_status"] == "已确认",
            f"状态机迁移 确认中→已确认(GRADED)（实际 {row['signal_status']}）",
        )
        check(
            applied_count(audit, "adjust_warning_level") == before + 1,
            "审计 applied 记录 +1",
        )
        # 本体自有 warn_adjust_reason 落库
        os_row = _ontology_value(
            engine, "WarningSignal", w["warning_id"], "warn_adjust_reason"
        )
        check(os_row == "模型评分上调，升级预警", "warn_adjust_reason 落本体自有状态")
    # 非法枚举 → INVALID_PARAMS
    res2 = engine.execute(
        "adjust_warning_level",
        {"warning_id": "WS-2026-00000001", "new_level": "紫", "reason": "x"},
        actor="human",
    )
    check(
        res2.error_code == "INVALID_PARAMS",
        f"非法等级枚举 → INVALID_PARAMS（{res2.error_code}）",
    )
    # 非法状态 → WARNING_NOT_ADJUSTABLE
    wc = _pick(
        conn,
        "SELECT warning_id FROM ap_warning_signal WHERE signal_status='已关闭' LIMIT 1",
    )
    if wc:
        res3 = engine.execute(
            "adjust_warning_level",
            {"warning_id": wc["warning_id"], "new_level": "红", "reason": "x"},
            actor="human",
        )
        check(
            res3.error_code == "WARNING_NOT_ADJUSTABLE",
            f"对已关闭信号调级 → WARNING_NOT_ADJUSTABLE（{res3.error_code}）",
        )

    # ==================================================================
    # 3) submit_disposal 处置方案提交（DRAFT→SUBMITTED，信号→IN_DISPOSAL）
    # ==================================================================
    print("\n[3] submit_disposal")
    before = applied_count(audit, "submit_disposal")
    d = _pick(
        conn,
        """SELECT wd.disposal_id, wd.warning_id FROM ap_warning_disposal wd
        JOIN ap_warning_signal w ON wd.warning_id=w.warning_id
        WHERE wd.disposal_status='未处置' AND w.signal_status='已确认' LIMIT 1""",
    )
    check(d is not None, "找到未处置(DRAFT)处置且信号已确认")
    if d:
        res = engine.execute(
            "submit_disposal",
            {
                "disposal_id": d["disposal_id"],
                "deal_type": "PUSH_SUBSIDIARY",
                "comment": "发送子公司执行处置",
            },
            actor="human",
            request_id="smoke-m3",
        )
        drow = _pick(
            conn,
            "SELECT disposal_status FROM ap_warning_disposal WHERE disposal_id=?",
            (d["disposal_id"],),
        )
        wrow = _pick(
            conn,
            "SELECT signal_status, disposal_status FROM ap_warning_signal WHERE warning_id=?",
            (d["warning_id"],),
        )
        check(res.outcome == "applied", f"提交 applied（error_code={res.error_code}）")
        check(
            drow["disposal_status"] == "处置中",
            f"处置状态 未处置→处置中（实际 {drow['disposal_status']}）",
        )
        check(
            wrow["signal_status"] == "处置中",
            f"信号状态 → 处置中(IN_DISPOSAL)（实际 {wrow['signal_status']}）",
        )
        check(
            wrow["disposal_status"] == "处置中",
            f"信号处置状态 → 处置中（实际 {wrow['disposal_status']}）",
        )
        check(
            applied_count(audit, "submit_disposal") == before + 1,
            "审计 applied 记录 +1",
        )
        res2 = engine.execute(
            "submit_disposal",
            {
                "disposal_id": d["disposal_id"],
                "deal_type": "PUSH_SUBSIDIARY",
                "comment": "again",
            },
            actor="human",
        )
        check(
            res2.error_code == "DISPOSAL_NOT_SUBMITTABLE",
            f"重复提交 → DISPOSAL_NOT_SUBMITTABLE（{res2.error_code}）",
        )
    res3 = engine.execute(
        "submit_disposal",
        {
            "disposal_id": "WD-9999-99999999",
            "deal_type": "PUSH_SUBSIDIARY",
            "comment": "x",
        },
        actor="human",
    )
    check(
        res3.error_code == "DISPOSAL_NOT_FOUND",
        f"不存在处置 → DISPOSAL_NOT_FOUND（{res3.error_code}）",
    )

    # ==================================================================
    # 4) approve_disposal 处置审批（PROCESS→APPROVED/REJECTED）
    # ==================================================================
    print("\n[4] approve_disposal")
    before = applied_count(audit, "approve_disposal")
    target = None
    for o in conn.execute(
        "SELECT approve_order_id, remark FROM approval.ap_approve_order WHERE approve_order_status='PROCESS' LIMIT 50"
    ).fetchall():
        m = re.search(r"SGN-\d{4}-\d{8}", o["remark"] or "")
        if not m:
            continue
        w = _pick(
            conn,
            "SELECT warning_id FROM ap_warning_signal WHERE signal_id=?",
            (m.group(0),),
        )
        if w and _pick(
            conn,
            "SELECT 1 AS x FROM ap_warning_disposal WHERE warning_id=?",
            (w["warning_id"],),
        ):
            target = o["approve_order_id"]
            break
    check(target is not None, "找到 PROCESS 审批单（含关联处置）")
    if target:
        res = engine.execute(
            "approve_disposal",
            {
                "approve_order_id": target,
                "decision": "APPROVED",
                "opinion": "同意，按处置方案执行",
            },
            actor="human",
            request_id="smoke-m3",
        )
        orow = _pick(
            conn,
            "SELECT approve_order_status, opinion_description FROM approval.ap_approve_order WHERE approve_order_id=?",
            (target,),
        )
        check(res.outcome == "applied", f"审批 applied（error_code={res.error_code}）")
        check(
            orow["approve_order_status"] == "APPROVED",
            f"审批单 PROCESS→APPROVED（实际 {orow['approve_order_status']}）",
        )
        check(
            orow["opinion_description"] == "同意，按处置方案执行",
            "审批意见写回 opinion_description",
        )
        check(
            applied_count(audit, "approve_disposal") == before + 1,
            "审计 applied 记录 +1",
        )
        res2 = engine.execute(
            "approve_disposal",
            {"approve_order_id": target, "decision": "APPROVED", "opinion": "again"},
            actor="human",
        )
        check(
            res2.error_code == "APPROVE_ORDER_NOT_PROCESSING",
            f"重复审批 → APPROVE_ORDER_NOT_PROCESSING（{res2.error_code}）",
        )
    res3 = engine.execute(
        "approve_disposal",
        {
            "approve_order_id": "APP-9999-99999999",
            "decision": "APPROVED",
            "opinion": "x",
        },
        actor="human",
    )
    check(
        res3.error_code == "APPROVE_ORDER_NOT_FOUND",
        f"不存在审批单 → APPROVE_ORDER_NOT_FOUND（{res3.error_code}）",
    )

    # ==================================================================
    # 5) push_warning 预警推送
    # ==================================================================
    print("\n[5] push_warning")
    before = applied_count(audit, "push_warning")
    p = _pick(conn, "SELECT warning_id, to_user FROM ap_warning_signal LIMIT 1")
    res = engine.execute(
        "push_warning",
        {"warning_id": p["warning_id"], "to_user": "U90000"},
        actor="llm",
        request_id="smoke-m3",
    )
    prow = _pick(
        conn,
        "SELECT to_user FROM ap_warning_signal WHERE warning_id=?",
        (p["warning_id"],),
    )
    check(res.outcome == "applied", f"推送 applied（error_code={res.error_code}）")
    check(
        prow["to_user"] == "U90000", f"to_user 真变（{p['to_user']}→{prow['to_user']}）"
    )
    check(applied_count(audit, "push_warning") == before + 1, "审计 applied 记录 +1")
    os_row = _ontology_value(engine, "WarningSignal", p["warning_id"], "push_at")
    check(os_row is not None, "push_at 落本体自有状态")
    res2 = engine.execute(
        "push_warning", {"warning_id": "WS-9999-99999999", "to_user": "U1"}, actor="llm"
    )
    check(
        res2.error_code == "WARNING_NOT_FOUND",
        f"不存在信号 → WARNING_NOT_FOUND（{res2.error_code}）",
    )

    # ==================================================================
    # 6) close_warning 预警销号（IN_DISPOSAL→CLOSED）
    # ==================================================================
    print("\n[6] close_warning")
    before = applied_count(audit, "close_warning")
    # 全流程：先提交一个新处置 → 信号进处置中 → 销号
    d2 = _pick(
        conn,
        """SELECT wd.disposal_id, wd.warning_id FROM ap_warning_disposal wd
        JOIN ap_warning_signal w ON wd.warning_id=w.warning_id
        WHERE wd.disposal_status='未处置' AND w.signal_status='已确认' LIMIT 1""",
    )
    check(d2 is not None, "找到新的未处置处置（用于销号全流程）")
    if d2:
        engine.execute(
            "submit_disposal",
            {
                "disposal_id": d2["disposal_id"],
                "deal_type": "MGMT_REVIEW",
                "comment": "进处置",
            },
            actor="human",
        )
        res = engine.execute(
            "close_warning",
            {"warning_id": d2["warning_id"], "close_reason": "处置完毕，风险解除"},
            actor="human",
            request_id="smoke-m3",
        )
        cw = _pick(
            conn,
            "SELECT signal_status, disposal_status FROM ap_warning_signal WHERE warning_id=?",
            (d2["warning_id"],),
        )
        check(res.outcome == "applied", f"销号 applied（error_code={res.error_code}）")
        check(
            cw["signal_status"] == "已关闭",
            f"信号状态 → 已关闭(CLOSED)（实际 {cw['signal_status']}）",
        )
        check(
            cw["disposal_status"] == "已处置",
            f"信号处置状态 → 已处置（实际 {cw['disposal_status']}）",
        )
        check(
            applied_count(audit, "close_warning") == before + 1, "审计 applied 记录 +1"
        )
    # 非法状态：对非处置中信号销号 → WARNING_NOT_CLOSABLE
    nc = _pick(
        conn,
        "SELECT warning_id FROM ap_warning_signal WHERE signal_status='待确认' LIMIT 1",
    )
    if nc:
        res2 = engine.execute(
            "close_warning",
            {"warning_id": nc["warning_id"], "close_reason": "x"},
            actor="human",
        )
        check(
            res2.error_code == "WARNING_NOT_CLOSABLE",
            f"对非处置中信号销号 → WARNING_NOT_CLOSABLE（{res2.error_code}）",
        )

    # ==================================================================
    # 7) adjust_concentration_limit 集中度限额调整（保留旧值）
    # ==================================================================
    print("\n[7] adjust_concentration_limit")
    before = applied_count(audit, "adjust_concentration_limit")
    cl = _pick(
        conn,
        "SELECT concentration_limit_id, concentration_limit, concentration_limit_old FROM ap_concentration_limit LIMIT 1",
    )
    new_limit = round(cl["concentration_limit"] + 1000, 2)
    res = engine.execute(
        "adjust_concentration_limit",
        {
            "concentration_limit_id": cl["concentration_limit_id"],
            "new_limit": new_limit,
            "reason": "集团整体授信上调",
        },
        actor="human",
        request_id="smoke-m3",
    )
    c2 = _pick(
        conn,
        "SELECT concentration_limit, concentration_limit_old FROM ap_concentration_limit WHERE concentration_limit_id=?",
        (cl["concentration_limit_id"],),
    )
    check(res.outcome == "applied", f"调整 applied（error_code={res.error_code}）")
    check(
        c2["concentration_limit"] == new_limit,
        f"限额真变：{cl['concentration_limit']}→{c2['concentration_limit']}",
    )
    check(
        c2["concentration_limit_old"] == cl["concentration_limit"],
        f"旧值保留：concentration_limit_old={c2['concentration_limit_old']}（=调整前 {cl['concentration_limit']}）",
    )
    check(
        applied_count(audit, "adjust_concentration_limit") == before + 1,
        "审计 applied 记录 +1",
    )
    os_row = _ontology_value(
        engine, "ConcentrationLimit", cl["concentration_limit_id"], "approve_comment"
    )
    check(os_row is not None, "approve_comment 落本体自有状态")
    res2 = engine.execute(
        "adjust_concentration_limit",
        {"concentration_limit_id": "CL-9999", "new_limit": 1, "reason": "x"},
        actor="human",
    )
    check(
        res2.error_code == "CONCENTRATION_LIMIT_NOT_FOUND",
        f"不存在限额 → CONCENTRATION_LIMIT_NOT_FOUND（{res2.error_code}）",
    )

    # ==================================================================
    # 8) register_risk_project 风险项目登记（防重复）
    # ==================================================================
    print("\n[8] register_risk_project")
    before = applied_count(audit, "register_risk_project")
    g = _pick(
        conn,
        "SELECT group_customer_no, group_customer_name FROM ap_group_customer LIMIT 1",
    )
    proj_name = f"冒烟登记项目-{abs(hash(Path(tmp).name)) % 100000}"
    res = engine.execute(
        "register_risk_project",
        {
            "group_customer_no": g["group_customer_no"],
            "project_name": proj_name,
            "business_type": "项目贷款",
            "five_classification": "NORMAL",
        },
        actor="human",
        request_id="smoke-m3",
    )
    new_row = _pick(
        conn,
        "SELECT risk_project_id, group_customer_name, five_classification FROM project.ap_risk_project WHERE group_customer_name=? AND project_name=?",
        (g["group_customer_name"], proj_name),
    )
    check(res.outcome == "applied", f"登记 applied（error_code={res.error_code}）")
    check(
        new_row is not None and new_row["risk_project_id"].startswith("PROJ-"),
        f"新项目真实插入（id={new_row['risk_project_id'] if new_row else None}）",
    )
    check(
        applied_count(audit, "register_risk_project") == before + 1,
        "审计 applied 记录 +1",
    )
    res2 = engine.execute(
        "register_risk_project",
        {
            "group_customer_no": g["group_customer_no"],
            "project_name": proj_name,
            "business_type": "项目贷款",
            "five_classification": "NORMAL",
        },
        actor="human",
    )
    check(
        res2.error_code == "RISK_PROJECT_ALREADY_EXISTS",
        f"重复登记 → RISK_PROJECT_ALREADY_EXISTS（{res2.error_code}）",
    )

    # ==================================================================
    # 9) update_risk_project_progress 项目进展更新
    # ==================================================================
    print("\n[9] update_risk_project_progress")
    before = applied_count(audit, "update_risk_project_progress")
    rp = _pick(
        conn,
        "SELECT risk_project_id, project_progress, five_classification FROM project.ap_risk_project LIMIT 1",
    )
    new_cls = "ATTENTION" if rp["five_classification"] != "ATTENTION" else "SECONDARY"
    res = engine.execute(
        "update_risk_project_progress",
        {
            "risk_project_id": rp["risk_project_id"],
            "project_progress": "完成现场尽调，风险缓释措施落实中",
            "new_five_classification": new_cls,
        },
        actor="human",
        request_id="smoke-m3",
    )
    r2 = _pick(
        conn,
        "SELECT project_progress, five_classification FROM project.ap_risk_project WHERE risk_project_id=?",
        (rp["risk_project_id"],),
    )
    check(res.outcome == "applied", f"进展更新 applied（error_code={res.error_code}）")
    check(
        r2["project_progress"] == "完成现场尽调，风险缓释措施落实中",
        "project_progress 真变",
    )
    check(
        r2["five_classification"] == new_cls,
        f"五级分类真变：{rp['five_classification']}→{r2['five_classification']}",
    )
    check(
        applied_count(audit, "update_risk_project_progress") == before + 1,
        "审计 applied 记录 +1",
    )
    res2 = engine.execute(
        "update_risk_project_progress",
        {
            "risk_project_id": "PROJ-9999-99999999",
            "project_progress": "x",
            "new_five_classification": "NORMAL",
        },
        actor="human",
    )
    check(
        res2.error_code == "RISK_PROJECT_NOT_FOUND",
        f"不存在项目 → RISK_PROJECT_NOT_FOUND（{res2.error_code}）",
    )

    # ==================================================================
    # 收尾：审计哈希链完整 + 汇总
    # ==================================================================
    integrity = audit.verify_integrity()
    check(integrity["ok"], f"审计哈希链完整（checked={integrity['checked']}）")
    total_applied = (
        applied_count(audit, "confirm_warning")
        + applied_count(audit, "adjust_warning_level")
        + applied_count(audit, "submit_disposal")
        + applied_count(audit, "approve_disposal")
        + applied_count(audit, "push_warning")
        + applied_count(audit, "close_warning")
        + applied_count(audit, "adjust_concentration_limit")
        + applied_count(audit, "register_risk_project")
        + applied_count(audit, "update_risk_project_progress")
    )
    ok_count = n_actions
    for a in (
        "confirm_warning",
        "adjust_warning_level",
        "submit_disposal",
        "approve_disposal",
        "push_warning",
        "close_warning",
        "adjust_concentration_limit",
        "register_risk_project",
        "update_risk_project_progress",
    ):
        if applied_count(audit, a) == 0:
            ok_count -= 1
    print(
        f"\n== 结果：{ok_count}/{n_actions} 动作有真实写回与审计；总 applied 审计 = {total_applied} =="
    )
    if _FAILURES:
        print("FAILED 项：")
        for f in _FAILURES:
            print(f"  - {f}")
        return 1
    print("全部通过。")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
