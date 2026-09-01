"""S4 M3a 证据链只读端点 —— 七幕剧本查询（第 1/2/4 幕）的「答案+证据」载荷。

与 Agent 剧本工具共用 src.runtime.risk_evidence.EvidenceService（真数据 + M2 规则引擎
实算，禁 mock / 禁查表回显）；供前端「证据链展开态」直接复用（不经 LLM 往返），以及
增量测试断言 10.8% / 12.8% 端到端验算。

端点（口径包 v0.3 §六/§七）：
- GET /risk/evidence/group-reveal?group_customer_name=…     第 1 幕揭示：逐家 → 归集 10.8% 橙
- GET /risk/evidence/related-upgrade?group_customer_name=…  第 2 幕升级识别：三线索 + R2 重算 12.8% 红
- GET /risk/evidence/approval-chain?…                       第 4 幕双签驳回：处置审批链 + 2023 办法第二十三条
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.runtime.risk_evidence import EvidenceError, EvidenceService


def _envelope(data: dict[str, Any]) -> JSONResponse:
    return JSONResponse(
        content={"request_id": "", "outcome": "ok", "data": data, "error": None}
    )


def _envelope_error(code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "request_id": "",
            "outcome": "error",
            "error": {"code": code, "message": message, "detail": None},
        },
    )


def register_risk_evidence_routes(app: FastAPI) -> None:
    """挂载证据链只读端点（可在任意 FastAPI 实例上复用）。"""
    service = EvidenceService()

    @app.get("/risk/evidence/group-reveal")
    def risk_evidence_group_reveal(request: Request):
        group = request.query_params.get("group_customer_name") or ""
        try:
            return _envelope(service.group_reveal(group))
        except EvidenceError as exc:
            return _envelope_error("GROUP_NOT_FOUND", str(exc))

    @app.get("/risk/evidence/related-upgrade")
    def risk_evidence_related_upgrade(request: Request):
        group = request.query_params.get("group_customer_name") or ""
        try:
            return _envelope(service.related_upgrade(group))
        except EvidenceError as exc:
            return _envelope_error("GROUP_NOT_FOUND", str(exc))

    @app.get("/risk/thresholds")
    def risk_thresholds():
        """R1a 三线阈值可查询（P0-1）：谁定的/怎么改（出处条款/版本/审批人/更新时间/分子构成/分母/净额规则）。"""
        return _envelope(service.thresholds())

    @app.get("/risk/evidence/verify-reason")
    def risk_evidence_verify_reason(request: Request):
        """质疑/复核实查（R2-P0-A）：按集团实查标红/橙行的真实原因维度（集中度/非集中度）+ R1a computed 比对。"""
        group = request.query_params.get("group_customer_name") or ""
        try:
            return _envelope(service.verify_red_reason(group))
        except EvidenceError as exc:
            return _envelope_error("GROUP_NOT_FOUND", str(exc))

    @app.get("/risk/evidence/approval-chain")
    def risk_evidence_approval_chain(request: Request):
        try:
            return _envelope(
                service.approval_chain(
                    group_customer_name=request.query_params.get("group_customer_name"),
                    signal_id=request.query_params.get("signal_id"),
                    warning_id=request.query_params.get("warning_id"),
                )
            )
        except EvidenceError as exc:
            return _envelope_error("SIGNAL_NOT_FOUND", str(exc))


__all__ = ["register_risk_evidence_routes"]
