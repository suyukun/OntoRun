"""S3 金控风控场景本体 —— 动作模板（M2 设计 §3，映射业务流程 STEP 3 动作清单）。

3 个核心动作做全（confirm_warning / adjust_warning_level / submit_disposal），
含参数模型 + Precondition（错误码）+ StateEffects（状态归属效果，§2.7）；
其余 6 个动作先注册占位（参数模型 + 前置/效果骨架，语义由 M3 动作执行器细化）。

错误码全集 = S1 §4.3 CANONICAL_ERROR_CODES（src/ontology/actions.py 已并入
RISK_ERROR_CODES）；Registry.self_check 对每个动作校验参数 schema、错误码、
前置声明、效果字段归属。参数模型导出 JSON Schema 供前端表单/LLM 工具生成。
"""

from typing import Literal

from pydantic import BaseModel, Field

from src.ontology.actions import ActionDef, Precondition, StateEffects

# 参数约束（对齐 S1：ID 类 64、自由文本 500）
_STR_MAX = 64
_TEXT_MAX = 500


# ---- 参数模型（LLM 输出视为不可信输入：类型/枚举/长度上限经 Pydantic 校验，§5.4） ----
class ConfirmWarningParams(BaseModel):
    warning_id: str = Field(max_length=_STR_MAX, description="预警信号 ID")


class AdjustWarningLevelParams(BaseModel):
    warning_id: str = Field(max_length=_STR_MAX, description="预警信号 ID")
    new_level: Literal["RED", "YELLOW", "BLUE"] = Field(description="调整后的预警等级")
    reason: str = Field(min_length=1, max_length=_TEXT_MAX, description="调整原因")


class SubmitDisposalParams(BaseModel):
    disposal_id: str = Field(max_length=_STR_MAX, description="处置记录 ID")
    deal_type: str = Field(
        min_length=1, max_length=_STR_MAX, description="处置类型（字典项P066，M3 补全枚举）"
    )
    comment: str = Field(min_length=1, max_length=_TEXT_MAX, description="处置事由")


class ApproveDisposalParams(BaseModel):
    approve_order_id: str = Field(max_length=_STR_MAX, description="审批单 ID")
    decision: Literal["APPROVED", "REJECTED"] = Field(description="审批结论")
    opinion: str = Field(min_length=1, max_length=_TEXT_MAX, description="审批意见")


class PushWarningParams(BaseModel):
    warning_id: str = Field(max_length=_STR_MAX, description="预警信号 ID")
    to_user: str = Field(min_length=1, max_length=_STR_MAX, description="推送对象（用户/机构）")


class CloseWarningParams(BaseModel):
    warning_id: str = Field(max_length=_STR_MAX, description="预警信号 ID")
    close_reason: str = Field(min_length=1, max_length=_TEXT_MAX, description="销号原因")


class AdjustConcentrationLimitParams(BaseModel):
    concentration_limit_id: str = Field(max_length=_STR_MAX, description="集中度限额记录 ID")
    new_limit: float = Field(ge=0, description="新集中度限额（万元）")
    reason: str = Field(min_length=1, max_length=_TEXT_MAX, description="调整原因")


class RegisterRiskProjectParams(BaseModel):
    group_customer_no: str = Field(max_length=_STR_MAX, description="所属集团编号")
    project_name: str = Field(min_length=1, max_length=_STR_MAX, description="项目名称")
    business_type: str = Field(min_length=1, max_length=_STR_MAX, description="业务类型")
    five_classification: Literal[
        "NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"
    ] = Field(description="五级分类")


class UpdateRiskProjectProgressParams(BaseModel):
    risk_project_id: str = Field(max_length=_STR_MAX, description="风险项目 ID")
    project_progress: str = Field(min_length=1, max_length=_TEXT_MAX, description="项目进展")
    new_five_classification: Literal[
        "NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"
    ] = Field(description="最新五级分类")


RISK_ACTIONS: list[ActionDef] = [
    # ---- 核心动作 1：预警信号确认（GENERATED → CONFIRMED） ----
    ActionDef(
        name="confirm_warning",
        description=(
            "确认预警信号：仅 GENERATED（生成）状态的信号可确认，确认后 signal_status → "
            "CONFIRMED；确认代表人工认领该预警进入人工定级流程。"
        ),
        params_model=ConfirmWarningParams,
        preconditions=[
            Precondition(error_code="WARNING_NOT_FOUND", summary="预警信号存在"),
            Precondition(
                error_code="WARNING_NOT_CONFIRMABLE",
                summary="signal_status 必须为 GENERATED（已确认/已关闭不可重复确认）",
            ),
        ],
        state_effects=StateEffects(source_backed=["WarningSignal.signal_status"]),
        error_codes=["INVALID_PARAMS", "WARNING_NOT_FOUND", "WARNING_NOT_CONFIRMABLE"],
    ),
    # ---- 核心动作 2：预警等级调整（CONFIRMED 下 RED/YELLOW/BLUE 调整） ----
    ActionDef(
        name="adjust_warning_level",
        description=(
            "调整预警等级：仅 CONFIRMED 状态可调；等级调整必须给出 reason；"
            "升级至更高预警等级（如 YELLOW→RED）为高风险调整，需人机双签/审批。"
        ),
        params_model=AdjustWarningLevelParams,
        preconditions=[
            Precondition(error_code="WARNING_NOT_FOUND", summary="预警信号存在"),
            Precondition(
                error_code="WARNING_NOT_ADJUSTABLE",
                summary="signal_status 必须为 CONFIRMED（GRADED 后由定级流程管理）",
            ),
            Precondition(
                error_code="WARNING_LEVEL_INVALID",
                summary="new_level ∈ {RED,YELLOW,BLUE} 且升级需审批（风险动作）",
            ),
        ],
        state_effects=StateEffects(
            source_backed=["WarningSignal.warn_level"],
            ontology_owned=["WarningSignal.warn_adjust_reason"],
        ),
        error_codes=[
            "INVALID_PARAMS",
            "WARNING_NOT_FOUND",
            "WARNING_NOT_ADJUSTABLE",
            "WARNING_LEVEL_INVALID",
        ],
        high_risk=True,
    ),
    # ---- 核心动作 3：处置方案提交（DRAFT → SUBMITTED，信号进入 IN_DISPOSAL） ----
    ActionDef(
        name="submit_disposal",
        description=(
            "提交处置方案：仅 DRAFT 状态的处置可提交，提交后 disposal_status → SUBMITTED，"
            "对应预警信号 signal_status → IN_DISPOSAL（进入处置流转）。"
        ),
        params_model=SubmitDisposalParams,
        preconditions=[
            Precondition(error_code="DISPOSAL_NOT_FOUND", summary="处置记录存在"),
            Precondition(
                error_code="DISPOSAL_NOT_SUBMITTABLE",
                summary="disposal_status 必须为 DRAFT（已提交不可重复提交）",
            ),
        ],
        state_effects=StateEffects(
            source_backed=[
                "Disposal.disposal_status",
                "WarningSignal.signal_status",
            ]
        ),
        error_codes=[
            "INVALID_PARAMS",
            "DISPOSAL_NOT_FOUND",
            "DISPOSAL_NOT_SUBMITTABLE",
        ],
    ),
    # ---- 占位动作（参数/前置/效果骨架，M3 动作执行器细化） ----
    ActionDef(
        name="approve_disposal",
        description=(
            "处置审批（占位）：对处置/风险项目审批单给出 APPROVED/REJECTED 结论，"
            "同步推进 Disposal 状态；高风险动作需双签。"
        ),
        params_model=ApproveDisposalParams,
        preconditions=[
            Precondition(error_code="APPROVE_ORDER_NOT_FOUND", summary="审批单存在")
        ],
        state_effects=StateEffects(
            source_backed=[
                "ApproveOrder.approve_order_status",
                "Disposal.disposal_status",
            ]
        ),
        error_codes=["INVALID_PARAMS", "APPROVE_ORDER_NOT_FOUND"],
        high_risk=True,
    ),
    ActionDef(
        name="push_warning",
        description="预警推送（占位）：将预警信号推送给处置/管理人员，记录推送时间。",
        params_model=PushWarningParams,
        preconditions=[
            Precondition(error_code="WARNING_NOT_FOUND", summary="预警信号存在")
        ],
        state_effects=StateEffects(ontology_owned=["WarningSignal.push_at"]),
        error_codes=["INVALID_PARAMS", "WARNING_NOT_FOUND"],
    ),
    ActionDef(
        name="close_warning",
        description=(
            "预警销号（占位）：处置完成后将信号状态置 CLOSED；销号属收尾动作需审批。"
        ),
        params_model=CloseWarningParams,
        preconditions=[
            Precondition(error_code="WARNING_NOT_FOUND", summary="预警信号存在")
        ],
        state_effects=StateEffects(source_backed=["WarningSignal.signal_status"]),
        error_codes=["INVALID_PARAMS", "WARNING_NOT_FOUND"],
        high_risk=True,
    ),
    ActionDef(
        name="adjust_concentration_limit",
        description=(
            "集中度限额调整（占位）：调整集中度限额并保留更新前值（concentration_limit_old），"
            "记录审批意见；高风险动作需双签。"
        ),
        params_model=AdjustConcentrationLimitParams,
        preconditions=[
            Precondition(
                error_code="CONCENTRATION_LIMIT_NOT_FOUND", summary="集中度限额记录存在"
            )
        ],
        state_effects=StateEffects(
            source_backed=[
                "ConcentrationLimit.concentration_limit",
                "ConcentrationLimit.concentration_limit_old",
            ],
            ontology_owned=["ConcentrationLimit.approve_comment"],
        ),
        error_codes=["INVALID_PARAMS", "CONCENTRATION_LIMIT_NOT_FOUND"],
        high_risk=True,
    ),
    ActionDef(
        name="register_risk_project",
        description=(
            "风险项目登记（占位）：登记风险项目（按集团编号+项目名+五级分类），"
            "重复登记拦截；属风险暴露新增需审批。"
        ),
        params_model=RegisterRiskProjectParams,
        preconditions=[
            Precondition(
                error_code="RISK_PROJECT_ALREADY_EXISTS",
                summary="同集团同项目名未登记（防重复登记）",
            )
        ],
        state_effects=StateEffects(
            source_backed=[
                "RiskProject.risk_project_id",
                "RiskProject.group_customer_no",
                "RiskProject.project_name",
            ]
        ),
        error_codes=["INVALID_PARAMS", "RISK_PROJECT_ALREADY_EXISTS"],
        high_risk=True,
    ),
    ActionDef(
        name="update_risk_project_progress",
        description="风险项目进展更新（占位）：更新项目进展文本与最新五级分类。",
        params_model=UpdateRiskProjectProgressParams,
        preconditions=[
            Precondition(error_code="RISK_PROJECT_NOT_FOUND", summary="风险项目存在")
        ],
        state_effects=StateEffects(
            source_backed=[
                "RiskProject.project_progress",
                "RiskProject.five_classification",
            ]
        ),
        error_codes=["INVALID_PARAMS", "RISK_PROJECT_NOT_FOUND"],
    ),
]
