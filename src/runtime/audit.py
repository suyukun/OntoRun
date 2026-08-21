"""审计日志读写（B2，技术方案 §3.5）。

audit_log 是"运行语义层"区别于"只读语义层"的证据面：writeback_json 含写回 SQL 与影响行数，
三问测试 2 除直查源库断言外，审计亦可自证（§3.5 注）。
audit_id 用 ULID（时间有序 + 随机，标准库实现，不引依赖）。
链序 = seq 自增列（追加序，与 audit_id 字典序解耦；red-team P2-1：同毫秒乱序 audit_id
不断链——append 取 max(seq) 作 prev，verify 按 seq 升序重算）。

修正策略（P1.5 R3，Jack 已批准）：审计为 WORM（append-only），原记录绝不 UPDATE——
发现原记录有误时经 append_correction 追加一条 source='correction' 的修正记录（关联原
audit_id + 原因 + 修正字段），保留"原值 + 修正"两段证据链，哈希链随之扩展不重算。
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any, Protocol

from pydantic import BaseModel, Field

from src.runtime.store import AUDIT_SOURCES, RETENTION_CLASSES, Store

# Crockford Base32（ULID 字母表，不含 I/L/O/U）
_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# P1.5 R3 审计修正策略（append correction）：审计为 WORM（append-only），原记录一经落库
# 绝不 UPDATE——发现原记录有误时追加一条 source='correction' 的修正记录，保留"原值 + 修正"
# 两段证据链。修正记录的 action_name 固定常量，与业务动作区分（source 单一来源 = store.AUDIT_SOURCES）。
CORRECTION_ACTION_NAME = "audit_correction"


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
    # P1.5 治理段：TTL 分级 + 来源分类（默认 sensitive/action，枚举单一来源 = store 顶部常量）
    retention_class: str = "sensitive"
    source: str = "action"


def _j(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


# ----------------------------------------------------------------------
# P1.5 哈希链（设计 2.3，零依赖 stdlib hashlib）
# ----------------------------------------------------------------------
# 链序 = ORDER BY audit_id（ULID 时间有序，天然给链定序）。
# record_hash = SHA256(prev_hash + "|" + canonical_json(record 内容))；首条 prev_hash = ""。
# canonical = json.dumps(sort_keys, separators=(',',':'), ensure_ascii=False)（确定性、跨版本稳定）。


class FieldEffect(Protocol):
    """字段级镜像输入协议：与 action_engine.Effect 结构兼容（object_type/pk/prop/old/new）。

    不直接 import action_engine.Effect 以避开 action_engine -> audit 的循环依赖；
    运行时按协议 duck-typing，Engine 的 Effect 对象直接可用。
    """

    object_type: str
    pk: str
    prop: str
    old: Any
    new: Any


def _canonical_json(value: Any) -> str:
    """canonical 序列化（设计 2.3）：sort_keys + 紧凑分隔符 + 非 ASCII 原样。"""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_chain(prev_hash: str, content: dict) -> str:
    """record_hash = SHA256(prev_hash + "|" + canonical_json(content))（genesis prev_hash=""）。"""
    payload = (prev_hash or "") + "|" + _canonical_json(content)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# 哈希忽略字段：prev_hash / record_hash / seq 是链元数据（seq = 链序，非记录内容），
# 不能自引用入内容——回填/追加 seq 不影响既有 record_hash（既有表兼容，red-team P2-1）。
_HASH_IGNORE_FIELDS = frozenset({"prev_hash", "record_hash", "seq"})


def _content_of(row: dict) -> dict:
    """参与哈希的记录内容 = 全字段去掉 prev_hash/record_hash。"""
    return {k: v for k, v in row.items() if k not in _HASH_IGNORE_FIELDS}


def _retention_source_validate(record: AuditRecord) -> None:
    """retention_class/source 枚举合法（机验 ⑤）：单一来源 = store 顶部常量。"""
    if record.retention_class not in RETENTION_CLASSES:
        raise ValueError(f"非法 retention_class: {record.retention_class}")
    if record.source not in AUDIT_SOURCES:
        raise ValueError(f"非法 source: {record.source}")


def _audit_row(record: AuditRecord) -> dict:
    """AuditRecord → 审计行 dict（哈希内容来源，链元数据列 seq/prev_hash/record_hash 由追加方补）。"""
    return {
        "audit_id": record.audit_id,
        "ts": record.ts.strftime("%Y-%m-%d %H:%M:%S"),
        "action_name": record.action_name,
        "actor": record.actor,
        "actor_detail": record.actor_detail,
        "request_id": record.request_id,
        "params_json": record.params_json,
        "preconditions_json": record.preconditions_json,
        "effects_json": record.effects_json,
        "writeback_json": record.writeback_json,
        "outcome": record.outcome,
        "error_code": record.error_code,
        "message": record.message,
        "detail_json": record.detail_json,
        "duration_ms": record.duration_ms,
        "retention_class": record.retention_class,
        "source": record.source,
    }


def _append_mirrors(conn, record: AuditRecord, row: dict, effects) -> None:
    """字段级镜像（同一事务，记录 + 镜像原子；镜像行不入链，跟随母记录）。"""
    for e in effects or []:
        conn.execute(
            "INSERT INTO audit_field_mirror (mirror_id, audit_id, object_type, pk, "
            "prop, old_value, new_value, ts) VALUES (?,?,?,?,?,?,?,?)",
            (
                new_ulid(),
                record.audit_id,
                e.object_type,
                e.pk,
                e.prop,
                None if e.old is None else str(e.old),
                None if e.new is None else str(e.new),
                row["ts"],
            ),
        )


class AuditLog:
    """审计日志：追加（append）/ 查询（query）/ 单条（get）。"""

    def __init__(self, store: Store) -> None:
        self._store = store

    def append(
        self, record: AuditRecord, effects: list[FieldEffect] | None = None
    ) -> str:
        """原语义 + 计算 prev_hash/record_hash（哈希链）+ 同步落字段级镜像（同一事务）。

        - 链序 = seq 自增列（追加序；首条 prev_hash = "" genesis；red-team P2-1：与
          audit_id 字典序解耦，同毫秒乱序 audit_id 不断链）；
        - record_hash = SHA256(prev_hash + "|" + canonical_json(内容))（设计 2.3）；
        - effects 按 FieldEffect 协议 duck-typing（action_engine.Effect 直接可用），
          同一事务内落 audit_field_mirror（记录 + 镜像原子，设计 2.4）；
        - retention_class/source 默认 sensitive/action，枚举非法即拒绝（机验 ⑤）。
        """
        conn = self._store.ontology_conn()
        try:
            self.append_on(conn, record, effects)
            conn.commit()
        finally:
            conn.close()
        return record.audit_id

    def append_on(
        self, conn: sqlite3.Connection, record: AuditRecord, effects: list[FieldEffect] | None = None
    ) -> str:
        """追加核心（接受外部连接，供 P2-6 审核导入单连接单事务复用）。

        与 append 同一实现（链序/哈希/镜像原子），但不负责 commit——由调用方在同一事务内
        组合「改 target + 流转 + history + audit」并一次性提交（red-team P2-6）。
        """
        _retention_source_validate(record)
        row = _audit_row(record)
        seq = self._next_seq(conn)
        prev_hash = self._prev_hash(conn)
        record_hash = _hash_chain(prev_hash, _content_of(row))
        conn.execute(
            "INSERT INTO audit_log (audit_id, seq, ts, action_name, actor, actor_detail, "
            "request_id, params_json, preconditions_json, effects_json, writeback_json, "
            "outcome, error_code, message, detail_json, duration_ms, prev_hash, record_hash, "
            "retention_class, source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                row["audit_id"],
                seq,
                row["ts"],
                row["action_name"],
                row["actor"],
                row["actor_detail"],
                row["request_id"],
                row["params_json"],
                row["preconditions_json"],
                row["effects_json"],
                row["writeback_json"],
                row["outcome"],
                row["error_code"],
                row["message"],
                row["detail_json"],
                row["duration_ms"],
                prev_hash,
                record_hash,
                row["retention_class"],
                row["source"],
            ),
        )
        _append_mirrors(conn, record, row, effects)
        return record.audit_id

    def _next_seq(self, conn) -> int:
        """链序列（追加序）：max(seq)+1。Store 单写连接串行（§3.4），同事务内安全。"""
        row = conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 AS n FROM audit_log").fetchone()
        return int(row["n"])

    def _prev_hash(self, conn) -> str:
        """链上前一记录的 record_hash（按 seq 降序 = 最近追加；空链 → genesis ""）。"""
        row = conn.execute(
            "SELECT record_hash FROM audit_log ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row["record_hash"] if row else ""

    def get(self, audit_id: str) -> dict | None:
        conn = self._store.ontology_conn()
        try:
            row = conn.execute(
                "SELECT * FROM audit_log WHERE audit_id=?", (audit_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def append_correction(
        self,
        original_audit_id: str,
        reason: str,
        corrected_fields: dict[str, Any],
        *,
        actor: str = "api",
        actor_detail: str = "",
    ) -> str:
        """追加一条修正审计记录（P1.5 R3：append correction，绝不 UPDATE 原记录）。

        修正策略：审计为 WORM（append-only，store 层 BEFORE UPDATE/DELETE 触发器强制），
        原记录一经落库不可改动。发现原记录内容有误时，不 UPDATE 原记录，而是追加一条
        source='correction' 的修正记录：关联原 audit_id、记录修正原因与修正字段，完整保留
        "原值 + 修正"两段证据链；修正记录同样入哈希链，verify_integrity 保持全绿。

        - original_audit_id：被修正的原审计记录（必须已存在，否则 ValueError，防悬空关联）；
        - reason：修正原因（落 message 供人工可读，同时入 detail_json 结构化）；
        - corrected_fields：被修正的审计字段 → 修正值 映射（落 detail_json，入哈希不可旁路篡改）；
        - 修正记录字段：action_name=audit_correction / outcome=applied / source=correction；
          detail_json = {original_audit_id, reason, corrected_fields}。
        返回新修正记录的 audit_id。
        """
        if self.get(original_audit_id) is None:
            raise ValueError(f"修正目标审计记录不存在: {original_audit_id}")
        detail = {
            "original_audit_id": original_audit_id,
            "reason": reason,
            "corrected_fields": corrected_fields,
        }
        record = AuditRecord(
            action_name=CORRECTION_ACTION_NAME,
            actor=actor,
            actor_detail=actor_detail,
            outcome="applied",
            source="correction",
            message=reason,
            detail_json=_j(detail),
        )
        return self.append(record)

    def find_corrections(self, original_audit_id: str) -> list[dict]:
        """查询某审计记录的全部修正记录（source='correction' 且 detail_json 关联 original_audit_id）。

        修正链路机器可查：给出原记录 audit_id，回溯其所有修正记录（按追加序）。
        """
        conn = self._store.ontology_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE source='correction' ORDER BY seq ASC"
            ).fetchall()
        finally:
            conn.close()
        return [
            dict(r)
            for r in rows
            if (json.loads(r["detail_json"] or "{}").get("original_audit_id"))
            == original_audit_id
        ]

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

    def verify_integrity(self) -> dict:
        """按 seq 升序（追加序）重算整条哈希链（设计 2.3/2.5 机验 ②③；red-team P2-1）。

        链序 = 追加序（seq），与 audit_id 字典序解耦——同毫秒乱序 audit_id 的追加不断链。
        返回 {ok, checked, broken, first_broken_index}：
        - ok = 链全部自洽；checked = 检查条数；
        - broken = 被篡改/删除/插入的记录 audit_id 列表；
        - first_broken_index = 链序上首个坏记录的下标（None = 全绿）。
        任一条的 prev/record_hash 与按规格重算不符（或前后衔接断裂）即 broken。
        """
        conn = self._store.ontology_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY seq ASC"
            ).fetchall()
        finally:
            conn.close()
        broken: list[str] = []
        first_broken_index: int | None = None
        prev_hash = ""
        for i, raw in enumerate(rows):
            row = dict(raw)
            expected = _hash_chain(prev_hash, _content_of(row))
            prev_ok = row["prev_hash"] == prev_hash
            rec_ok = row["record_hash"] == expected
            if not (prev_ok and rec_ok):
                broken.append(row["audit_id"])
                if first_broken_index is None:
                    first_broken_index = i
            prev_hash = row["record_hash"]
        return {
            "ok": not broken,
            "checked": len(rows),
            "broken": broken,
            "first_broken_index": first_broken_index,
        }
