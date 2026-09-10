"""本体管理台 API router：/api/ontology /api/lineage /api/history + 确认写端点。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.fortune_admin import confirm_store, history, lineage, ontology

router = APIRouter(prefix="/api")

VALID_VERDICTS = ("confirmed", "rejected")


class ConfirmBody(BaseModel):
    verdict: str = Field(description="confirmed | rejected")
    confirmeer: str = Field(min_length=1, description="确认人（落 commit message）")


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


@router.get("/history")
def get_history(limit: int = 20) -> dict:
    return history.history_payload(min(max(limit, 1), 50))


@router.post("/rules/{rule_id}/confirm")
def post_confirm(rule_id: str, body: ConfirmBody) -> dict:
    if body.verdict not in VALID_VERDICTS:
        raise HTTPException(
            422, f"verdict 必须是 {VALID_VERDICTS} 之一，收到: {body.verdict}"
        )
    registry = ontology.load_registry()
    if rule_id not in registry.rules:
        raise HTTPException(404, f"规则不存在: {rule_id}")
    record = confirm_store.confirm_rule(rule_id, body.verdict, body.confirmeer)
    new_status = "confirmed" if body.verdict == "confirmed" else "unverified"
    return {
        "record": record,
        "rule": {"id": rule_id, "status": new_status},
        "message": (
            f"已记录：{body.confirmeer} "
            f"{'确认' if body.verdict == 'confirmed' else '驳回'} {rule_id}"
            f"（版本 {record['commit']}）"
            if record["commit"]
            else f"已记录（JSON 降级，未产生 commit）：{body.confirmeer} {rule_id}"
        ),
    }
