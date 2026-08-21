"""动作执行引擎（B2，技术方案 §3.3 核心管道）。

管道：① 参数校验(Pydantic) → ② 源库事务（BEGIN IMMEDIATE，单写连接=天然串行）
→ ③ 事务内重读快照（防读-改-写竞态）→ ④ 前置规则按声明顺序执行（submission criteria）
→ ⑤ 计算变更（纯函数）→ ⑥ 写回源库（source-backed，每条带 SQL 与影响行数）
→ ⑦ 源库提交后更新本体索引 + 本体自有状态（补偿式，§7.4）
→ ⑧ 审计落库（applied/rejected/failed 三态）。

设计要点（§3.3）：
- 拒绝路径早退：任何前置不满足 → rejected + 业务错误码 + 源库零变更（三问测试 3 的机制保证）；
- 写回与索引同事务语义：源库提交成功才更新索引；索引/本体库失败 → 审计记 failed + 告警（可对账）；
- 效果计算是纯函数（可单测、可重放，审计 diff 来源）；
- 一切写操作只能经 execute()（无泛化 update，D-T3）；
- 审计完整性：actor 白名单（human/llm/api）与 audit_log / action_runs 的 CHECK
  同源（src.runtime.store.ALLOWED_ACTORS 单一来源，TD-9），非法 actor 在写源库前
  拒绝（failed），保证"源库已写则必有审计"（补偿式承诺的底线）。
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from src.ontology.objects import OWN_ONTOLOGY, field_ownership
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord, _j
from src.runtime.index import ObjectIndex
from src.runtime.store import ALLOWED_ACTORS, Store

# §4.3 错误码 → 中文消息（API 层信封错误也复用）
ERROR_MESSAGES: dict[str, str] = {
    "INVALID_PARAMS": "参数不合法（类型/枚举/边界校验失败）",
    "UNKNOWN_ACTION": "动作不存在",
    "ORDER_NOT_FOUND": "订单不存在",
    "INVENTORY_NOT_FOUND": "库存记录不存在",
    "CUSTOMER_NOT_FOUND": "客户不存在",
    "PRODUCT_NOT_FOUND": "商品不存在",
    "PRODUCT_INACTIVE": "商品已下架，不可下单",
    "OUT_OF_STOCK": "可用库存不足",
    "ORDER_NOT_CONFIRMABLE": "仅 pending 状态的订单可确认",
    "ORDER_NOT_CANCELLABLE": "订单当前状态不允许取消",
    "SHIPPED_ORDER_CANNOT_BE_CANCELLED": "订单已发货，不能取消，请走退款流程",
    "ORDER_NOT_SHIPPABLE": "仅 confirmed 状态的订单可发货",
    "INSUFFICIENT_INVENTORY": "发货仓物理在库不足",
    "INSUFFICIENT_RESERVED": "新在库数量不能低于已锁库存",
    "REFUND_NOT_PENDING": "退款单不存在或已审核",
    "AMOUNT_EXCEEDS_PAID": "退款金额超过实付（含已批准退款）",
    "REFUND_NOT_ALLOWED": "订单状态不允许退款",
}

# failed 路径对外稳定错误码/文案（安全摘要，不含原始异常文本——AGENTS.md
# 「错误信息不泄漏敏感数据」：异常详情只记日志 logger，不进对外 message）
FAILED_CODE_EXECUTION = "EXECUTION_FAILED"
FAILED_MESSAGE_EXECUTION = "动作执行失败：内部错误"
FAILED_CODE_SYNC = "ONTOLOGY_SYNC_FAILED"
FAILED_MESSAGE_SYNC = "本体库同步失败（源库已变更，需对账）"

logger = logging.getLogger(__name__)

# 合法操作者：单一来源 = src.runtime.store.ALLOWED_ACTORS（TD-9 收口）。
# audit_log.actor / action_runs.executed_by 的 CHECK 与 API 层 X-Actor 白名单
# 均引用同一常量，防双轨漂移；此处仅导入不重定义。

_TIME_FMT = "%Y-%m-%d %H:%M:%S"


def _now() -> str:
    return datetime.now(timezone.utc).strftime(_TIME_FMT)


class Effect(BaseModel):
    """变更 diff（前后对比，审计 effects_json 来源，§3.5）。"""

    object_type: str
    pk: str
    prop: str
    old: Any = None
    new: Any = None
    note: str | None = None


class Writeback(BaseModel):
    """写回源库的一条 SQL（含影响行数，审计 writeback_json 来源——"源记录真变"铁证）。"""

    sql: str
    params: list[Any]
    table: str
    rows: int = 0


class Violation(BaseModel):
    """前置规则违反：错误码 + 消息 + 详情。"""

    error_code: str
    message: str
    detail: dict[str, Any] | None = None


class ActionResult(BaseModel):
    """动作执行结果（outcome ∈ applied/rejected/failed）。"""

    action_name: str
    outcome: str
    error_code: str | None = None
    message: str | None = None
    detail: Any = None
    effects: list[Effect] = Field(default_factory=list)
    writebacks: list[Writeback] = Field(default_factory=list)
    audit_id: str | None = None
    request_id: str = ""
    duration_ms: int = 0


class Snapshot:
    """事务内快照读取器（源库重读最新值，防读-改-写竞态，§3.3 ③）。"""

    def __init__(self, conn: Any, registry: Registry) -> None:
        self._conn = conn
        self._registry = registry

    def get(self, type_name: str, pk: str) -> dict | None:
        obj = self._registry.object_type(type_name)
        cur = self._conn.execute(
            f"SELECT * FROM {obj.source_table} WHERE {obj.pk_field}=?", (str(pk),)
        )
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None

    def list_where(self, type_name: str, field: str, value: Any) -> list[dict]:
        obj = self._registry.object_type(type_name)
        cur = self._conn.execute(
            f"SELECT * FROM {obj.source_table} WHERE {field}=?", (value,)
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def one(self, sql: str, params: tuple = ()) -> dict | None:
        cur = self._conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        cur = self._conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


class ActionHandler:
    """动作处理基类：每动作实现 快照/语义校验/前置规则/效果计算。"""

    def __init__(self, engine: ActionEngine) -> None:
        self.engine = engine

    def load_snapshot(self, snapshot: Snapshot, params: Any) -> dict:
        raise NotImplementedError

    def validate_semantics(self, snapshot: dict, params: Any) -> Violation | None:
        """语义级参数校验（如发货仓存在性，§2.4 A4 归入参数校验）。"""
        return None

    def check(self, code: str, snapshot: dict, params: Any) -> tuple[bool, dict | None]:
        raise NotImplementedError

    def compute_effects(
        self, conn: Any, snapshot: dict, params: Any
    ) -> tuple[list[Effect], list[Writeback]]:
        raise NotImplementedError


class ActionEngine:
    """动作执行管道（§3.3）。"""

    def __init__(
        self, registry: Registry, store: Store, index: ObjectIndex, audit: AuditLog
    ) -> None:
        # 冲突消解策略 1（user_edit_wins）由各 handler 的无条件写回隐式执行
        # （compute_effects 算新值 → writeback 覆盖源库当前值）；conflict.py 保留为
        # 策略 2（时间戳优先）的声明与测试锚点，未接线（技术方案 §3.4 发布期待定）。
        self.registry = registry
        self.store = store
        self.index = index
        self.audit = audit
        self._handlers: dict[str, ActionHandler] = {
            a.name: self._build_handler(a.name) for a in registry.actions()
        }

    def _build_handler(self, action_name: str) -> ActionHandler:
        from src.runtime import actions_impl  # 延迟导入避免循环

        factory = actions_impl.HANDLERS.get(action_name)
        if factory is None:
            raise ValueError(f"动作实现缺失: {action_name}")
        return factory(self)

    # ---- 主入口 ----

    def execute(
        self,
        action_name: str,
        params: dict[str, Any],
        actor: str = "api",
        actor_detail: str = "",
        request_id: str = "",
        *,
        dry_run: bool = False,
        snapshot_observer: Callable[[dict], None] | None = None,
    ) -> ActionResult:
        """执行动作管道（§3.3）。

        P4/E6 扩展（向后兼容，缺省关闭）：
        - dry_run=True：管道全走（参数校验/事务内快照/前置规则/效果计算），
          但写回不执行、事务回滚、索引不更新、不落 audit_log（audit CHECK
          无 dry_run 语义；构建侧 action_runs 是 dry_run 的证据面）；
          前置不满足时仍走 rejected（拒绝路径早退语义不变）。
        - snapshot_observer：load_snapshot 之后回调一次，接收 handler 快照
          （相关源记录执行前状态），供调用方记录 before_snapshot（E6）。
        """
        t0 = time.monotonic()
        # 审计完整性底线：非法 actor 无法落审计（audit_log CHECK），拒绝执行、源库零变更；
        # API 层另有 400 白名单校验（routes.py），此处为绕过 API 直调 runtime 的兜底。
        if actor not in ALLOWED_ACTORS:
            return ActionResult(
                action_name=action_name,
                outcome="failed",
                message=f"非法操作者: {actor}（仅允许 {ALLOWED_ACTORS}）",
                request_id=request_id,
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        try:
            action = self.registry.action(action_name)
        except KeyError:
            return self._reject(
                None,
                action_name,
                "UNKNOWN_ACTION",
                params,
                actor,
                actor_detail,
                request_id,
                t0,
                None,
                [],
            )
        handler = self._handlers[action_name]

        # ① 参数校验（LLM 输出视为不可信输入，Pydantic 强校验）
        try:
            validated = action.params_model.model_validate(params)
        except ValidationError as exc:
            detail = [
                {"loc": ".".join(str(x) for x in e["loc"]), "msg": e["msg"]}
                for e in exc.errors()
            ]
            return self._reject(
                action,
                action_name,
                "INVALID_PARAMS",
                params,
                actor,
                actor_detail,
                request_id,
                t0,
                detail,
                [],
            )

        conn = self.store.source_conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            snapshot_reader = Snapshot(conn, self.registry)
            snapshot = handler.load_snapshot(snapshot_reader, validated)
            # E6 before_snapshot 钩子：拒绝/失败路径也已拿到快照（早退前回调）
            if snapshot_observer is not None:
                snapshot_observer(snapshot)

            # 语义级参数校验（在事务内、前置规则之前）
            violation = handler.validate_semantics(snapshot, validated)
            if violation is not None:
                conn.rollback()
                return self._reject(
                    action,
                    action_name,
                    violation.error_code,
                    params,
                    actor,
                    actor_detail,
                    request_id,
                    t0,
                    violation.detail,
                    [],
                    violation.message,
                )

            # ④ 前置规则按声明顺序全部求值（审计全量留痕，§3.5 preconditions_json），
            #    拒绝时取第一个违反项（§3.3 violations[0]），源库零变更。
            checks: list[dict] = []
            first_violation: tuple[str, Any] | None = None
            for pc in action.preconditions:
                passed, detail = handler.check(pc.error_code, snapshot, validated)
                checks.append(
                    {"code": pc.error_code, "passed": bool(passed), "detail": detail}
                )
                if not passed and first_violation is None:
                    first_violation = (pc.error_code, detail)
            if first_violation is not None:
                conn.rollback()
                return self._reject(
                    action,
                    action_name,
                    first_violation[0],
                    params,
                    actor,
                    actor_detail,
                    request_id,
                    t0,
                    first_violation[1],
                    checks,
                )

            # ⑤ 计算变更（纯函数）+ ⑥ 写回源库
            effects, writebacks = handler.compute_effects(conn, snapshot, validated)
            if dry_run:
                # E6 dry_run：效果已算出（含将执行的 SQL），但零写回零提交。
                conn.rollback()
                return ActionResult(
                    action_name=action_name,
                    outcome="dry_run",
                    request_id=request_id,
                    duration_ms=int((time.monotonic() - t0) * 1000),
                    effects=effects,
                    writebacks=writebacks,
                )
            for wb in writebacks:
                cur = conn.execute(wb.sql, wb.params)
                wb.rows = cur.rowcount
            conn.commit()
        except Exception:  # 引擎兜底：回滚 + failed 审计
            try:
                conn.rollback()
            finally:
                conn.close()
            # 原始异常只进日志（含 traceback）；对外 message 用稳定安全摘要（F1 red-team）
            logger.exception(
                "动作执行异常（内部错误，不对调用方回显）: action=%s request_id=%s",
                action_name,
                request_id,
            )
            return self._failed(
                action_name,
                params,
                actor,
                actor_detail,
                request_id,
                t0,
                FAILED_MESSAGE_EXECUTION,
                error_code=FAILED_CODE_EXECUTION,
            )
        finally:
            # 拒绝路径（return 在 try 内）也会走到这里释放连接（关闭失败可忽略）
            if conn:
                with suppress(Exception):
                    conn.close()

        # ⑦ 源库已提交 → 同步索引 + 本体自有状态（补偿式：失败留审计可对账）
        sync_conn = self.store.source_conn()
        try:
            pairs = list({(e.object_type, e.pk) for e in effects})
            self.index.refresh_many(pairs, sync_conn)
            for eff in effects:
                obj_def = self.registry.object_type(eff.object_type)
                if field_ownership(obj_def.model, eff.prop) == OWN_ONTOLOGY:
                    self._persist_ontology_state(eff)
                    self.index.set_ontology_state(
                        eff.object_type, eff.pk, eff.prop, eff.new
                    )
        except Exception:  # 补偿式：审计记 failed + 告警
            # 原始异常只进日志；对外 message 用稳定安全摘要（F1 red-team）
            logger.exception(
                "本体库同步失败（源库已变更，需对账）: action=%s request_id=%s",
                action_name,
                request_id,
            )
            return self._failed(
                action_name,
                params,
                actor,
                actor_detail,
                request_id,
                t0,
                FAILED_MESSAGE_SYNC,
                error_code=FAILED_CODE_SYNC,
                effects=effects,
                writebacks=writebacks,
            )
        finally:
            sync_conn.close()

        # ⑧ 审计落库（applied）
        audit_id = self._append_audit(
            action_name,
            actor,
            actor_detail,
            request_id,
            params,
            checks,
            effects,
            writebacks,
            "applied",
            None,
            t0,
        )
        return ActionResult(
            action_name=action_name,
            outcome="applied",
            audit_id=audit_id,
            request_id=request_id,
            duration_ms=int((time.monotonic() - t0) * 1000),
            effects=effects,
            writebacks=writebacks,
        )

    # ---- 内部：审计组装 ----

    def _persist_ontology_state(self, eff: Effect) -> None:
        conn = self.store.ontology_conn()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO ontology_state (object_type, pk, prop, value, updated_at) "
                "VALUES (?,?,?,?,?)",
                (
                    eff.object_type,
                    eff.pk,
                    eff.prop,
                    None if eff.new is None else str(eff.new),
                    _now(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _append_audit(
        self,
        action_name: str,
        actor: str,
        actor_detail: str,
        request_id: str,
        params: dict,
        checks: list[dict],
        effects: list[Effect],
        writebacks: list[Writeback],
        outcome: str,
        error: tuple[str, dict | None, str | None] | None,
        t0: float,
    ) -> str:
        record = AuditRecord(
            action_name=action_name,
            actor=actor,
            actor_detail=actor_detail,
            request_id=request_id,
            params_json=_j(params),
            preconditions_json=_j(checks),
            effects_json=_j([e.model_dump() for e in effects]),
            writeback_json=_j([w.model_dump() for w in writebacks]),
            outcome=outcome,
            error_code=error[0] if error else None,
            message=error[2] if error else None,
            detail_json=_j(error[1]) if error and error[1] is not None else None,
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
        # P1.5：effects 传入 append 派生 audit_field_mirror（记录 + 镜像同事务原子）
        return self.audit.append(record, effects=effects)

    def _reject(
        self,
        action: Any,
        action_name: str,
        code: str,
        params: dict,
        actor: str,
        actor_detail: str,
        request_id: str,
        t0: float,
        detail: dict | None,
        checks: list[dict],
        message: str | None = None,
    ) -> ActionResult:
        msg = message or ERROR_MESSAGES.get(code, code)
        audit_id = self._append_audit(
            action_name,
            actor,
            actor_detail,
            request_id,
            params,
            checks,
            [],
            [],
            "rejected",
            (code, detail, msg),
            t0,
        )
        return ActionResult(
            action_name=action_name,
            outcome="rejected",
            error_code=code,
            message=msg,
            detail=detail,
            audit_id=audit_id,
            request_id=request_id,
            duration_ms=int((time.monotonic() - t0) * 1000),
        )

    def _failed(
        self,
        action_name: str,
        params: dict,
        actor: str,
        actor_detail: str,
        request_id: str,
        t0: float,
        message: str,
        error_code: str | None = None,
        effects: list[Effect] | None = None,
        writebacks: list[Writeback] | None = None,
    ) -> ActionResult:
        audit_id = self._append_audit(
            action_name,
            actor,
            actor_detail,
            request_id,
            params,
            [],
            effects or [],
            writebacks or [],
            "failed",
            (error_code, None, message),
            t0,
        )
        return ActionResult(
            action_name=action_name,
            outcome="failed",
            error_code=error_code,
            message=message,
            audit_id=audit_id,
            request_id=request_id,
            duration_ms=int((time.monotonic() - t0) * 1000),
            effects=effects or [],
            writebacks=writebacks or [],
        )

    # ---- 工具 ----

    def next_seq(self, conn: Any, table: str, pk_field: str, prefix: str) -> int:
        """取源表主键最大序号 +1（如 ORD-2200 → 2201）。"""
        row = conn.execute(
            f"SELECT MAX(CAST(SUBSTR({pk_field}, {len(prefix) + 1}) AS INTEGER)) AS m "
            f"FROM {table}"
        ).fetchone()
        return (row[0] or 0) + 1
