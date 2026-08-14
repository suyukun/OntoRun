"""审计日志读写（B2，技术方案 §3.5）。

audit_log 是"运行语义层"区别于"只读语义层"的证据面：writeback_json 含写回 SQL 与影响行数，
三问测试 2 除直查源库断言外，审计亦可自证（§3.5 注）。
audit_id 用 ULID（时间有序 + 随机，标准库实现，不引依赖）。
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from src.runtime.store import Store

# Crockford Base32（ULID 字母表，不含 I/L/O/U）
_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """生成 ULID：48 位毫秒时间戳 + 80 位随机（标准库，无第三方依赖）。"""
    ts = int(time.time() * 1000) & ((1 << 48) - 1)
    rand = int.from_bytes(os.urandom(10), "big")

    def _encode(value: int, length: int) -> str:
        chars = [_ULID_ALPHABET[(value >> (5 * i)) & 31] for i in range(length)]
        return "".join(reversed(chars))

    return _encode(ts, 10) + _encode(rand, 16)


class AuditRecord(BaseModel):
    """审计记录（§3.5 schema，逐字段对齐）。"""

    audit_id: str = Field(default_factory=new_ulid)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action_name: str
    actor: str = "api"
    actor_detail: str = ""
    request_id: str = ""
    params_json: str = "{}"
    preconditions_json: str = "[]"
    effects_json: str = "[]"
    writeback_json: str = "[]"
    outcome: str
    error_code: str | None = None
    message: str | None = None
    detail_json: str | None = None
    duration_ms: int = 0


def _j(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


class AuditLog:
    """审计日志：追加（append）/ 查询（query）/ 单条（get）。"""

    def __init__(self, store: Store) -> None:
        self._store = store

    def append(self, record: AuditRecord) -> str:
        conn = self._store.ontology_conn()
        try:
            conn.execute(
                "INSERT INTO audit_log (audit_id, ts, action_name, actor, actor_detail, request_id, "
                "params_json, preconditions_json, effects_json, writeback_json, outcome, error_code, "
                "message, detail_json, duration_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    record.audit_id,
                    record.ts.strftime("%Y-%m-%d %H:%M:%S"),
                    record.action_name,
                    record.actor,
                    record.actor_detail,
                    record.request_id,
                    record.params_json,
                    record.preconditions_json,
                    record.effects_json,
                    record.writeback_json,
                    record.outcome,
                    record.error_code,
                    record.message,
                    record.detail_json,
                    record.duration_ms,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return record.audit_id

    def get(self, audit_id: str) -> dict | None:
        conn = self._store.ontology_conn()
        try:
            row = conn.execute(
                "SELECT * FROM audit_log WHERE audit_id=?", (audit_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def query(
        self,
        action: str | None = None,
        outcome: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """审计查询（演示用）：按 action/outcome 过滤 + 分页，按时间倒序。"""
        where, params = [], []
        if action:
            where.append("action_name=?")
            params.append(action)
        if outcome:
            where.append("outcome=?")
            params.append(outcome)
        sql_where = ("WHERE " + " AND ".join(where)) if where else ""
        conn = self._store.ontology_conn()
        try:
            total = conn.execute(
                f"SELECT COUNT(*) AS n FROM audit_log {sql_where}", params
            ).fetchone()["n"]
            rows = conn.execute(
                f"SELECT * FROM audit_log {sql_where} ORDER BY ts DESC, audit_id DESC "
                "LIMIT ? OFFSET ?",
                params + [page_size, max(page - 1, 0) * page_size],
            ).fetchall()
            return [dict(r) for r in rows], total
        finally:
            conn.close()
