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
    Violation,  # noqa: F401 —— approve/close 的 validate_semantics 使用（后续批次）
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


def _risk_seq_id(conn: Any, table: str, pk_field: str, prefix: str, width: int = 8) -> str:
    """取源表主键末 width 位流水 max+1，拼 {PREFIX}-{year}-{8位}（编码规则 4）。"""
    row = conn.execute(
        f"SELECT MAX(CAST(SUBSTR({pk_field}, -{width}) AS INTEGER)) AS m FROM {table}"
    ).fetchone()
    seq = (row[0] or 0) + 1
    return f"{prefix}-{RISK_DEMO_YEAR:04d}-{seq:0{width}d}"


def _find_signal_by_remark(conn: Any, remark: str | None) -> dict | None:
    """从审批单 remark 解析信号号 → 查 ap_warning_signal（解析失败返回 None）。"""
    if not remark:
        return None
    m = _SIGNAL_ID_RE.search(remark)
    if m is None:
        return None
    cur = conn.execute(
        "SELECT * FROM ap_warning_signal WHERE signal_id=?", (m.group(0),)
    )
    cols = [c[0] for c in cur.description]
    row = cur.fetchone()
    return dict(zip(cols, row)) if row else None


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
            ok = warning is not None and warning["signal_status"] == _signal_cn("GENERATED")
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
            ok = warning is not None and warning["signal_status"] == _signal_cn("CONFIRMED")
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
            ok = disposal is not None and disposal["disposal_status"] == _disposal_cn("DRAFT")
            return ok, {"disposal_status": disposal["disposal_status"]} if disposal else None
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


HANDLERS: dict[str, type[ActionHandler]] = {
    "confirm_warning": ConfirmWarningHandler,
    "adjust_warning_level": AdjustWarningLevelHandler,
    "submit_disposal": SubmitDisposalHandler,
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
