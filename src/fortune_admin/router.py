"""本体管理台 API router：/api/ontology /api/lineage /api/history + 确认写端点。"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.fortune_admin import (
    confirm_store,
    history,
    lineage,
    object_detail,
    ontology,
    trial,
)

router = APIRouter(prefix="/api")
router.include_router(trial.router)  # T204 试算只读端点（独立装配 trial.py）

VALID_VERDICTS = ("confirmed", "rejected")
VALID_KINDS = ("measure", "dimension", "table")


# T0a 契约镜像：ontology-admin/src/api.ts 的 DecisionOptionKey。
# account/user/both = 三选一裁决（落 confirmed）；escalate = 只留痕不翻转（A4-7）。
DecisionOptionKey = Literal["account", "user", "both", "escalate"]


class DecisionSpec(BaseModel):
    """R8 裁决请求体（T0a 契约：decision?: {option_key}）。"""

    option_key: DecisionOptionKey = Field(
        description="account | user | both = 三选一裁决；escalate = 只留痕不翻转"
    )


class ConfirmBody(BaseModel):
    verdict: str = Field(description="confirmed | rejected")
    confirmeer: str = Field(min_length=1, description="确认人（落 commit message）")
    decision: DecisionSpec | None = Field(
        default=None, description="可选裁决；缺省 = 既有普通确认行为不变"
    )


@router.get("/ontology")
def get_ontology() -> dict:
    return ontology.ontology_payload()


@router.get("/lineage")
def get_lineage() -> dict:
    payload = ontology.ontology_payload()
    unconfirmed_tables = [
        t
        for r in payload["rules"]
        if r["status"] != "confirmed"
        for t in r["related_tables"]
    ]
    return lineage.lineage_payload(unconfirmed_tables)


@router.get("/objects/{kind}/{object_id}")
def get_object(kind: str, object_id: str) -> dict:
    if kind not in VALID_KINDS:
        raise HTTPException(404, f"kind 必须是 {VALID_KINDS} 之一，收到: {kind}")
    payload = object_detail.object_payload(kind, object_id)
    if payload is None:
        raise HTTPException(404, f"对象不存在: {kind}/{object_id}")
    return payload


@router.get("/history")
def get_history(
    limit: int = 20, rule_id: str | None = None, object: str | None = None
) -> dict:
    # T102：rule_id/object 过滤透传（语义见 history.history_payload）
    return history.history_payload(
        min(max(limit, 1), 50), rule_id=rule_id, object=object
    )


@router.post("/rules/{rule_id}/confirm")
def post_confirm(rule_id: str, body: ConfirmBody) -> dict:
    if body.verdict not in VALID_VERDICTS:
        raise HTTPException(
            422, f"verdict 必须是 {VALID_VERDICTS} 之一，收到: {body.verdict}"
        )
    option_key = body.decision.option_key if body.decision else None
    registry = ontology.load_registry()
    if rule_id not in registry.rules:
        raise HTTPException(404, f"规则不存在: {rule_id}")
    record = confirm_store.confirm_rule(
        rule_id, body.verdict, body.confirmeer, option_key
    )
    escalated = option_key == "escalate"
    if escalated:
        new_status = registry.rules[rule_id].status  # A4-7 留痕不翻转，读当前值
    else:
        new_status = "confirmed" if body.verdict == "confirmed" else "unverified"
    response = {
        "record": record,
        "rule": {"id": rule_id, "status": new_status},
        "message": (
            f"已记录：{body.confirmeer} "
            f"{'确认' if body.verdict == 'confirmed' else '驳回'} {rule_id}"
            f"（版本 {record['commit']}）"
            if record["commit"]
            else f"已记录（JSON 降级，未产生 commit）：{body.confirmeer} {rule_id}"
        ),
        # R8 裁决可判别字段（escalate 的 toast 文案归 T203 前端）
        "decision": record.get("decision"),
        "escalated": escalated,
    }
    if escalated:
        response["message"] = (
            f"已留痕：{body.confirmeer} 将 {rule_id} 升级裁决"
            f"（线下处理，规则保持待确认）（版本 {record['commit']}）"
            if record["commit"]
            else f"已留痕（JSON 降级，未产生 commit）：{body.confirmeer} {rule_id} 升级裁决"
        )
    return response
