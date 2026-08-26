"""S3 M3 金控风控 9 个风险动作的真实写回 handler（写引擎，§2.3）。

每个动作 = 事务内快照读取（显式 SQL 直查 ap_anping 真实表，跨库经 RiskStore
ATTACH 连接）→ 状态机前置校验（本体英文态判迁移，错误码取自
src/ontology/risk_error_codes.py）→ 写回真实源库（写中文值，本体态译为源值）
→ effects（本体域 diff，审计/索引来源）。

处置身份适配：submit/approve 用 ap_warning_disposal（WD-...，处置状态载体表），
见 src.runtime.risk_db 模块文档。审批单↔预警信号经 ap_approve_order.remark 内嵌
信号号（"对预警信号 SGN-YYYY-XXXXXXXX 申请处置审批"）解析。

与零售 handler（src/runtime/actions_impl.py）完全独立：本模块只增不改，注册走
register_risk_action_handlers(engine) 挂到动作名→handler 映射，不触碰既有注册。
"""

from __future__ import annotations

import re
from typing import Any

from src.runtime.action_engine import (
    ActionEngine,
    ActionHandler,
    Effect,
    Snapshot,
    Violation,
    Writeback,
    _now,
)
from src.runtime.audit import AuditLog
from src.runtime.index import ObjectIndex
from src.runtime.risk_db import (
    DISPOSAL_STATUS_FROM_CN,
    DISPOSAL_STATUS_TO_CN,
    RISK_DEMO_YEAR,
    SIGNAL_STATUS_FROM_CN,
    SIGNAL_STATUS_TO_CN,
    build_risk_source_registry,
)
from src.runtime.store import Store

# 审批单 remark 内嵌信号号（生成器格式：对预警信号 SGN-2026-00041235 申请处置审批）
_SIGNAL_ID_RE = re.compile(r"SGN-\d{4}-\d{8}")


def _signal_cn(status: str) -> str:
    """本体英文信号态 → 源系统中文值（未知值原样透传，防御）。"""
    return SIGNAL_STATUS_TO_CN.get(status, status)


def _disposal_cn(status: str) -> str:
    """本体英文处置态 → 源系统中文值。"""
    return DISPOSAL_STATUS_TO_CN.get(status, status)


def _signal_en(status: str) -> str:
    """源系统中文信号态 → 本体英文态（未知值原样透传）。"""
    return SIGNAL_STATUS_FROM_CN.get(status, status)


def _disposal_en(status: str) -> str:
    """源系统中文处置态 → 本体英文态。"""
    return DISPOSAL_STATUS_FROM_CN.get(status, status)


def _risk_seq_id(
    conn: Any, table: str, pk_field: str, prefix: str, width: int = 8
) -> str:
    """取源表主键末 width 位流水 max+1，拼 {PREFIX}-{year}-{8位}（编码规则 4）。"""
    row = conn.execute(
        f"SELECT MAX(CAST(SUBSTR({pk_field}, -{width}) AS INTEGER)) AS m FROM {table}"
    ).fetchone()
    seq = (row[0] or 0) + 1
    return f"{prefix}-{RISK_DEMO_YEAR:04d}-{seq:0{width}d}"


def _resolve_warning_from_order(snapshot: Snapshot, order: dict) -> dict | None:
    """从审批单 remark 内嵌信号号（SGN-YYYY-XXXXXXXX）解析预警信号；失败返回 None。"""
    m = _SIGNAL_ID_RE.search(order.get("remark") or "")
    if m is None:
        return None
    return snapshot.one(
        "SELECT * FROM ap_warning_signal WHERE signal_id=?", (m.group(0),)
    )


# ======================================================================
# 动作 1：confirm_warning 预警信号确认（GENERATED → CONFIRMED）
# ======================================================================


class ConfirmWarningHandler(ActionHandler):
    """确认预警信号：仅待确认（GENERATED）可确认，确认后 signal_status → 确认中（CONFIRMED）。"""

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "warning": snapshot.one(
                "SELECT * FROM ap_warning_signal WHERE warning_id=?",
                (params.warning_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        warning = snapshot["warning"]
        if code == "WARNING_NOT_FOUND":
            return warning is not None, None
        if code == "WARNING_NOT_CONFIRMABLE":
            ok = warning is not None and warning["signal_status"] == _signal_cn(
                "GENERATED"
            )
            return ok, {"signal_status": warning["signal_status"]} if warning else None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        warning = snapshot["warning"]
        now = _now()
        effects = [
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="signal_status",
                old=_signal_en(warning["signal_status"]),
                new="CONFIRMED",
                note="预警信号人工确认",
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE ap_warning_signal SET signal_status=?, update_time=? WHERE warning_id=?",
                params=[_signal_cn("CONFIRMED"), now, warning["warning_id"]],
                table="ap_warning_signal",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 2：adjust_warning_level 预警等级调整（CONFIRMED → GRADED，高风险双签）
# ======================================================================


class AdjustWarningLevelHandler(ActionHandler):
    """调整预警等级：仅确认中（CONFIRMED）可调；等级变更 → 已确认（GRADED，定级完成）。

    warn_level 写源库，reason 落本体自有 warn_adjust_reason；升级至更高等级属高风险
    由 high_risk 双签承担（WARNING_LEVEL_INVALID 的枚举部分由 Pydantic Literal 强校验）。
    """

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "warning": snapshot.one(
                "SELECT * FROM ap_warning_signal WHERE warning_id=?",
                (params.warning_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        warning = snapshot["warning"]
        if code == "WARNING_NOT_FOUND":
            return warning is not None, None
        if code == "WARNING_NOT_ADJUSTABLE":
            ok = warning is not None and warning["signal_status"] == _signal_cn(
                "CONFIRMED"
            )
            return ok, {"signal_status": warning["signal_status"]} if warning else None
        if code == "WARNING_LEVEL_INVALID":
            # new_level ∈ {RED,YELLOW,BLUE} 由参数模型 Literal 强校验；升级审批走双签
            return True, {"note": "枚举由参数模型校验，升级审批由双签承担"}
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        warning = snapshot["warning"]
        now = _now()
        effects = [
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="warn_level",
                old=warning["warn_level"],
                new=params.new_level,
                note="预警等级调整",
            ),
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="signal_status",
                old=_signal_en(warning["signal_status"]),
                new="GRADED",
                note="等级定级完成",
            ),
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="warn_adjust_reason",
                old=None,
                new=params.reason,
                note="本体自有状态",
            ),
        ]
        writebacks = [
            Writeback(
                sql="UPDATE ap_warning_signal SET warn_level=?, signal_status=?, update_time=? "
                "WHERE warning_id=?",
                params=[
                    params.new_level,
                    _signal_cn("GRADED"),
                    now,
                    warning["warning_id"],
                ],
                table="ap_warning_signal",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 3：submit_disposal 处置方案提交（DRAFT → SUBMITTED，信号 → IN_DISPOSAL）
# ======================================================================


class SubmitDisposalHandler(ActionHandler):
    """提交处置方案：仅未处置（DRAFT）可提交；处置 → 处置中（SUBMITTED），
    对应预警信号 signal_status → 处置中（IN_DISPOSAL）、disposal_status → 处置中。
    deal_type/comment 为处置内容，源 ap_warning_disposal 无对应列 → 落审计 params。
    """

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        disposal = snapshot.one(
            "SELECT * FROM ap_warning_disposal WHERE disposal_id=?",
            (params.disposal_id,),
        )
        warning = None
        if disposal:
            warning = snapshot.one(
                "SELECT * FROM ap_warning_signal WHERE warning_id=?",
                (disposal["warning_id"],),
            )
        return {"disposal": disposal, "warning": warning}

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        disposal = snapshot["disposal"]
        if code == "DISPOSAL_NOT_FOUND":
            return disposal is not None, None
        if code == "DISPOSAL_NOT_SUBMITTABLE":
            ok = disposal is not None and disposal["disposal_status"] == _disposal_cn(
                "DRAFT"
            )
            return ok, {
                "disposal_status": disposal["disposal_status"]
            } if disposal else None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        disposal, warning = snapshot["disposal"], snapshot["warning"]
        now = _now()
        effects = [
            Effect(
                object_type="Disposal",
                pk=disposal["disposal_id"],
                prop="disposal_status",
                old=_disposal_en(disposal["disposal_status"]),
                new="SUBMITTED",
                note="处置方案提交",
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE ap_warning_disposal SET disposal_status=?, disposal_progress=?, "
                "operate_time=?, operator_user=? WHERE disposal_id=?",
                params=[
                    _disposal_cn("SUBMITTED"),
                    "已制定处置方案",
                    now,
                    "系统",
                    disposal["disposal_id"],
                ],
                table="ap_warning_disposal",
            )
        ]
        if warning is not None:
            effects.append(
                Effect(
                    object_type="WarningSignal",
                    pk=warning["warning_id"],
                    prop="signal_status",
                    old=_signal_en(warning["signal_status"]),
                    new="IN_DISPOSAL",
                    note="信号进入处置流转",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE ap_warning_signal SET signal_status=?, disposal_status=?, "
                    "update_time=? WHERE warning_id=?",
                    params=[
                        _signal_cn("IN_DISPOSAL"),
                        "处置中",
                        now,
                        warning["warning_id"],
                    ],
                    table="ap_warning_signal",
                )
            )
        return effects, writebacks


# ======================================================================
# 动作 4：approve_disposal 处置审批（PROCESS → APPROVED/REJECTED，高风险双签）
# ======================================================================


class ApproveDisposalHandler(ActionHandler):
    """处置审批：审批单仅 PROCESS 可审（语义校验 APPROVE_ORDER_NOT_PROCESSING）；
    结论 APPROVED/REJECTED 写 ap_approve_order + 未决审批任务，并同步关联处置与
    预警信号（经 remark 内嵌信号号解析）。高风险双签由 Agent 层承担。
    """

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        order = snapshot.one(
            "SELECT * FROM approval.ap_approve_order WHERE approve_order_id=?",
            (params.approve_order_id,),
        )
        warning = None
        if order:
            warning = _resolve_warning_from_order(snapshot, order)
        disposal = None
        if warning is not None:
            disposal = snapshot.one(
                "SELECT * FROM ap_warning_disposal WHERE warning_id=?",
                (warning["warning_id"],),
            )
        pending_tasks = (
            snapshot.query(
                "SELECT * FROM approval.ap_approve_task WHERE approve_order_id=? "
                "AND approve_task_status='PENDING'",
                (params.approve_order_id,),
            )
            if order
            else []
        )
        return {
            "order": order,
            "warning": warning,
            "disposal": disposal,
            "pending_tasks": pending_tasks,
        }

    def validate_semantics(self, snapshot: dict, params: Any) -> Violation | None:
        order = snapshot["order"]
        if order is not None and order["approve_order_status"] != "PROCESS":
            return Violation(
                error_code="APPROVE_ORDER_NOT_PROCESSING",
                message="审批单状态非 PROCESS，不可审批",
                detail={"approve_order_status": order["approve_order_status"]},
            )
        return None

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "APPROVE_ORDER_NOT_FOUND":
            return snapshot["order"] is not None, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        order = snapshot["order"]
        now = _now()
        decision = params.decision
        effects = [
            Effect(
                object_type="ApproveOrder",
                pk=order["approve_order_id"],
                prop="approve_order_status",
                old=order["approve_order_status"],
                new=decision,
                note="处置审批结论",
            ),
            Effect(
                object_type="ApproveOrder",
                pk=order["approve_order_id"],
                prop="opinion_description",
                old=order.get("opinion_description"),
                new=params.opinion,
                note="审批意见",
            ),
        ]
        writebacks = [
            Writeback(
                sql="UPDATE approval.ap_approve_order SET approve_order_status=?, "
                "approve_time=?, opinion_description=?, update_time=? WHERE approve_order_id=?",
                params=[
                    decision,
                    now,
                    params.opinion,
                    now,
                    order["approve_order_id"],
                ],
                table="ap_approve_order",
            )
        ]
        for task in snapshot["pending_tasks"]:
            effects.append(
                Effect(
                    object_type="ApproveTask",
                    pk=task["approve_task_id"],
                    prop="approve_task_status",
                    old=task["approve_task_status"],
                    new="COMPLETED",
                    note="审批任务办结",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE approval.ap_approve_task SET approve_task_status='COMPLETED', "
                    "approve_result=?, approve_remark=?, approve_time=?, update_time=? "
                    "WHERE approve_task_id=?",
                    params=[
                        decision,
                        params.opinion,
                        now,
                        now,
                        task["approve_task_id"],
                    ],
                    table="ap_approve_task",
                )
            )
        disposal = snapshot["disposal"]
        if disposal is not None:
            new_status = "APPROVED" if decision == "APPROVED" else "REJECTED"
            effects.append(
                Effect(
                    object_type="Disposal",
                    pk=disposal["disposal_id"],
                    prop="disposal_status",
                    old=_disposal_en(disposal["disposal_status"]),
                    new=new_status,
                    note="处置审批结果同步",
                )
            )
            writebacks.append(
                Writeback(
                    sql="UPDATE ap_warning_disposal SET disposal_status=?, operate_time=?, "
                    "operator_user=? WHERE disposal_id=?",
                    params=[
                        _disposal_cn(new_status),
                        now,
                        "系统",
                        disposal["disposal_id"],
                    ],
                    table="ap_warning_disposal",
                )
            )
        if snapshot["warning"] is not None:
            signal_status = "处置中" if decision == "APPROVED" else "暂缓处置"
            writebacks.append(
                Writeback(
                    sql="UPDATE ap_warning_signal SET disposal_status=?, update_time=? "
                    "WHERE warning_id=?",
                    params=[
                        signal_status,
                        now,
                        snapshot["warning"]["warning_id"],
                    ],
                    table="ap_warning_signal",
                )
            )
        return effects, writebacks


# ======================================================================
# 动作 5：push_warning 预警推送（写 ap_warning_signal.to_user + push_at 本体态）
# ======================================================================


class PushWarningHandler(ActionHandler):
    """推送预警：把信号推给指定对象（to_user 写源库），推送时间落本体自有 push_at。"""

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "warning": snapshot.one(
                "SELECT * FROM ap_warning_signal WHERE warning_id=?",
                (params.warning_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "WARNING_NOT_FOUND":
            return snapshot["warning"] is not None, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        warning = snapshot["warning"]
        now = _now()
        effects = [
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="push_at",
                old=None,
                new=now,
                note="推送时间（本体自有）",
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE ap_warning_signal SET to_user=?, push_warn_reason=?, update_time=? "
                "WHERE warning_id=?",
                params=[
                    params.to_user,
                    warning.get("warn_reason") or "",
                    now,
                    warning["warning_id"],
                ],
                table="ap_warning_signal",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 6：close_warning 预警销号（IN_DISPOSAL → CLOSED，高风险双签）
# ======================================================================


class CloseWarningHandler(ActionHandler):
    """预警销号：仅处置中（IN_DISPOSAL）信号可销号（语义校验 WARNING_NOT_CLOSABLE）；
    销号后 signal_status → 已关闭（CLOSED）、disposal_status → 已处置。
    """

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "warning": snapshot.one(
                "SELECT * FROM ap_warning_signal WHERE warning_id=?",
                (params.warning_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "WARNING_NOT_FOUND":
            return snapshot["warning"] is not None, None
        return True, None

    def validate_semantics(self, snapshot: dict, params: Any) -> Violation | None:
        warning = snapshot["warning"]
        if warning is not None and warning["signal_status"] != _signal_cn(
            "IN_DISPOSAL"
        ):
            return Violation(
                error_code="WARNING_NOT_CLOSABLE",
                message="仅处置中（IN_DISPOSAL）的预警信号可销号",
                detail={"signal_status": warning["signal_status"]},
            )
        return None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        warning = snapshot["warning"]
        now = _now()
        effects = [
            Effect(
                object_type="WarningSignal",
                pk=warning["warning_id"],
                prop="signal_status",
                old=_signal_en(warning["signal_status"]),
                new="CLOSED",
                note="预警销号",
            )
        ]
        writebacks = [
            Writeback(
                sql="UPDATE ap_warning_signal SET signal_status=?, disposal_status='已处置', "
                "update_time=? WHERE warning_id=?",
                params=[_signal_cn("CLOSED"), now, warning["warning_id"]],
                table="ap_warning_signal",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 7：adjust_concentration_limit 集中度限额调整（保留旧值审计，高风险双签）
# ======================================================================


class AdjustConcentrationLimitHandler(ActionHandler):
    """集中度限额调整：concentration_limit_old 先留调整前值（保留旧值审计），
    concentration_limit 写新限额；审批意见落本体自有 approve_comment。"""

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "limit": snapshot.one(
                "SELECT * FROM concentration.ap_concentration_limit "
                "WHERE concentration_limit_id=?",
                (params.concentration_limit_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "CONCENTRATION_LIMIT_NOT_FOUND":
            return snapshot["limit"] is not None, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        limit = snapshot["limit"]
        now = _now()
        old_value = limit["concentration_limit"]
        effects = [
            Effect(
                object_type="ConcentrationLimit",
                pk=limit["concentration_limit_id"],
                prop="concentration_limit",
                old=old_value,
                new=params.new_limit,
                note="集中度限额调整",
            ),
            Effect(
                object_type="ConcentrationLimit",
                pk=limit["concentration_limit_id"],
                prop="concentration_limit_old",
                old=limit["concentration_limit_old"],
                new=old_value,
                note="保留调整前值",
            ),
            Effect(
                object_type="ConcentrationLimit",
                pk=limit["concentration_limit_id"],
                prop="approve_comment",
                old=None,
                new=params.reason,
                note="本体自有审批意见",
            ),
        ]
        writebacks = [
            Writeback(
                sql="UPDATE concentration.ap_concentration_limit SET "
                "concentration_limit_old=concentration_limit, concentration_limit=?, "
                "update_time=? WHERE concentration_limit_id=?",
                params=[params.new_limit, now, limit["concentration_limit_id"]],
                table="ap_concentration_limit",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 8：register_risk_project 风险项目登记（防重复，高风险双签）
# ======================================================================


class RegisterRiskProjectHandler(ActionHandler):
    """风险项目登记：同集团同项目名未登记（RISK_PROJECT_ALREADY_EXISTS 防重复）；
    新项目 INSERT ap_risk_project（主键流水 PROJ-{year}-{8位}，编码规则 4）。"""

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        group = snapshot.one(
            "SELECT * FROM customer.ap_group_customer WHERE group_customer_no=?",
            (params.group_customer_no,),
        )
        group_name = group["group_customer_name"] if group else params.group_customer_no
        existing = snapshot.one(
            "SELECT * FROM project.ap_risk_project WHERE group_customer_name=? "
            "AND project_name=?",
            (group_name, params.project_name),
        )
        return {"group": group, "group_name": group_name, "existing": existing}

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "RISK_PROJECT_ALREADY_EXISTS":
            existing = snapshot["existing"]
            ok = existing is None
            return (
                ok,
                {"duplicate_project": existing["risk_project_id"]}
                if existing
                else None,
            )
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        now = _now()
        proj_id = _risk_seq_id(
            conn, "project.ap_risk_project", "risk_project_id", "PROJ"
        )
        effects = [
            Effect(
                object_type="RiskProject",
                pk=proj_id,
                prop="risk_project_id",
                old=None,
                new=proj_id,
                note="风险项目登记",
            ),
            Effect(
                object_type="RiskProject",
                pk=proj_id,
                prop="group_customer_no",
                old=None,
                new=params.group_customer_no,
            ),
            Effect(
                object_type="RiskProject",
                pk=proj_id,
                prop="project_name",
                old=None,
                new=params.project_name,
            ),
            Effect(
                object_type="RiskProject",
                pk=proj_id,
                prop="business_type",
                old=None,
                new=params.business_type,
            ),
            Effect(
                object_type="RiskProject",
                pk=proj_id,
                prop="five_classification",
                old=None,
                new=params.five_classification,
            ),
        ]
        seq = int(proj_id[-8:])  # 取流水号拼批次号
        writebacks = [
            Writeback(
                sql="INSERT INTO project.ap_risk_project (risk_project_id, sort_no, "
                "group_customer_name, batch_id, division, enterprise_overview, org_id_1, "
                "org_name_1, project_name, org_id_2, org_name_2, business_type, "
                "credit_subject, business_balance, risk_exposure_balance, impairment_provision, "
                "five_classification, guarantee_method, project_progress, is_deleted, "
                "create_user, create_time, update_time, update_user) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                params=[
                    proj_id,
                    0,
                    snapshot["group_name"],
                    f"BATCH-RISK-{RISK_DEMO_YEAR}-{seq:06d}",
                    "风险监控部",
                    "",
                    "",
                    "",
                    params.project_name,
                    "",
                    "",
                    params.business_type,
                    snapshot["group_name"],
                    0.0,
                    0.0,
                    0.0,
                    params.five_classification,
                    "信用",
                    "登记待评估",
                    0,
                    "系统",
                    now,
                    now,
                    "系统",
                ],
                table="ap_risk_project",
            )
        ]
        return effects, writebacks


# ======================================================================
# 动作 9：update_risk_project_progress 项目进展更新
# ======================================================================


class UpdateRiskProjectProgressHandler(ActionHandler):
    """风险项目进展更新：更新 project_progress 文本与最新五级分类。"""

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        return {
            "project": snapshot.one(
                "SELECT * FROM project.ap_risk_project WHERE risk_project_id=?",
                (params.risk_project_id,),
            )
        }

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        if code == "RISK_PROJECT_NOT_FOUND":
            return snapshot["project"] is not None, None
        return True, None

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        project = snapshot["project"]
        now = _now()
        effects = [
            Effect(
                object_type="RiskProject",
                pk=project["risk_project_id"],
                prop="project_progress",
                old=project["project_progress"],
                new=params.project_progress,
                note="项目进展更新",
            ),
            Effect(
                object_type="RiskProject",
                pk=project["risk_project_id"],
                prop="five_classification",
                old=project["five_classification"],
                new=params.new_five_classification,
            ),
        ]
        writebacks = [
            Writeback(
                sql="UPDATE project.ap_risk_project SET project_progress=?, "
                "five_classification=?, update_time=? WHERE risk_project_id=?",
                params=[
                    params.project_progress,
                    params.new_five_classification,
                    now,
                    project["risk_project_id"],
                ],
                table="ap_risk_project",
            )
        ]
        return effects, writebacks


HANDLERS: dict[str, type[ActionHandler]] = {
    "confirm_warning": ConfirmWarningHandler,
    "adjust_warning_level": AdjustWarningLevelHandler,
    "submit_disposal": SubmitDisposalHandler,
    "approve_disposal": ApproveDisposalHandler,
    "push_warning": PushWarningHandler,
    "close_warning": CloseWarningHandler,
    "adjust_concentration_limit": AdjustConcentrationLimitHandler,
    "register_risk_project": RegisterRiskProjectHandler,
    "update_risk_project_progress": UpdateRiskProjectProgressHandler,
}


def register_risk_action_handlers(engine: ActionEngine) -> None:
    """把风险动作 handler 挂到 ActionEngine（动作名→handler 实例）。

    与零售 handler 完全独立（不动 actions_impl.HANDLERS）：本函数把 HANDLERS 里已
    注册的 9 个风险 handler 注入 engine._handlers，供 execute 管道统一执行。
    """
    for name, factory in HANDLERS.items():
        engine._handlers[name] = factory(engine)


def build_risk_engine(
    store: Store | None = None,
    registry=None,
    index: ObjectIndex | None = None,
    audit: AuditLog | None = None,
) -> ActionEngine:
    """一键构建 S3 风险写引擎（数据源 = ap_anping 六库一体，审计落独立本体库）。

    冒烟脚本 / Agent 对话窗口接线入口：默认建 RiskStore（独立 S3 本体库）、
    风险源适配注册表、ObjectIndex、AuditLog，构造 ActionEngine 后注入风险 handler。
    """
    from src.runtime.risk_db import RiskStore

    store = store or RiskStore()
    store.migrate()
    registry = registry or build_risk_source_registry()
    index = index or ObjectIndex(registry)
    audit = audit or AuditLog(store)
    engine = ActionEngine(registry, store, index, audit)
    register_risk_action_handlers(engine)
    return engine
