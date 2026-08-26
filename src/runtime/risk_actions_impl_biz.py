"""S3 M3 金控风控「配套业务对象」3 个风险动作 handler（集中度限额 + 风险项目）。

与 src.runtime.risk_actions_impl（预警/处置流 6 动作）分工：本模块承载写回
ap_concentration_limit / ap_risk_project 的动作（adjust_concentration_limit /
register_risk_project / update_risk_project_progress），由
risk_actions_impl.HANDLERS 合并注册，register_risk_action_handlers 统一注入引擎。
"""

from __future__ import annotations

from typing import Any

from src.runtime.action_engine import (
    ActionHandler,
    Effect,
    Snapshot,
    Writeback,
    _now,
)
from src.runtime.risk_db import RISK_DEMO_YEAR, risk_seq_id


def _risk_project_effects(proj_id: str, params: Any) -> list[Effect]:
    """风险项目登记的 5 条状态效果（纯函数）。"""
    return [
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


def _risk_project_insert(
    proj_id: str, group_name: str, params: Any, now: str
) -> list[Writeback]:
    """风险项目登记 INSERT 写回（纯函数；补齐全部 NOT NULL 列）。"""
    seq = int(proj_id[-8:])  # 取流水号拼批次号
    return [
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
                group_name,
                f"BATCH-RISK-{RISK_DEMO_YEAR}-{seq:06d}",
                "风险监控部",
                "",
                "",
                "",
                params.project_name,
                "",
                "",
                params.business_type,
                group_name,
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
        proj_id = risk_seq_id(
            conn, "project.ap_risk_project", "risk_project_id", "PROJ"
        )
        effects = _risk_project_effects(proj_id, params)
        writebacks = _risk_project_insert(proj_id, snapshot["group_name"], params, now)
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


BIZ_HANDLERS: dict[str, type[ActionHandler]] = {
    "adjust_concentration_limit": AdjustConcentrationLimitHandler,
    "register_risk_project": RegisterRiskProjectHandler,
    "update_risk_project_progress": UpdateRiskProjectProgressHandler,
}
