"""Decision-chain engine over the L2 semantic layer (primitive combinations).

Routing (LLM, registry-constrained) → structured plan {measure, dimensions};
the keyword router falls back to equivalent primitive combinations. Execution
delegates to fortune_semantic.compiler: deterministic SQL bound to the
registry, executed with time parameters against the DuckDB mirror.

- answers render through D6 templates; every printed number must trace to
  rows/params (hard gate, §5-D9);
- SemanticError(UNREGISTERED_*) from the compiler and reject plans from the
  routers both end in the structured refusal card (reject_scope flow);
- a registered dimension whose mirror column is unfilled (usr_sex all NULL)
  degrades with honest copy instead of inventing a distribution;
- every result carries data_profile="mock" (answers come from the 仿真镜像);
- continuous step numbering, idempotent traces, cancel-on-disconnect preserved.
"""

import calendar
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

import duckdb

from src.fortune_semantic.compiler import QueryRequest, compile_query
from src.fortune_semantic.registry import REGISTRY, SemanticError

from . import config, errors, sanitize, storage, templates
from .llm_route import guided_reject_answer, keyword_route, llm_route
from .rules import (
    SENSITIVE_FIELDS,
    RoutePlan,
    viz_for,
)
from .templates import NumberValidationError, validate_numbers

MONTH_RE = re.compile(r"(?:(20\d{2})\s*[-年/])?\s*(\d{1,2})\s*月")
TOKEN_CHUNK = 3
TOKEN_SLEEP_S = 0.01
SUCCESS_PATHS = {"semantic_pushdown"}
EMPTY_ANSWER = "该范围内无数据，请调整时间范围后重试。"
DIMENSION_UNFILLED_ANSWER = (
    "该维度已在语义层建模，但仿真镜像数据未填充对应字段，无法给出真实分布——"
    "维度已建模、仿真数据未填充，如实告知，不猜测。"
)


def new_request_id() -> str:
    return f"REQ-{date.today().isoformat()}-{uuid.uuid4().hex[:6].upper()}"  # noqa: DTZ011 本地日


def resolve_state(path: str, block_reason: str | None = None,
                  empty: bool = False, degraded: bool = False) -> str:
    """path(+block_reason) → one of the eight states (product doc §4.2, 1:1 mapping)."""
    if path in SUCCESS_PATHS:
        if empty:
            return "empty"
        return "success_warning" if degraded else "success"
    if path == "blocked_param":
        return "ask_param" if block_reason == "missing_param" else "reject_range"
    return {
        "unregistered": "reject_unregistered",
        "rejected": "reject_scope",
        "validation_failed": "validation_failed",
        "error": "error",
        "canceled": "canceled",
    }.get(path, "error")


def extract_params(question: str) -> dict | None:
    """Generic 「(YYYY)M月」 parsing → compiler time bounds; out-of-calendar
    months flow into the range check."""
    match = MONTH_RE.search(question)
    if not match:
        return None
    year = int(match.group(1) or 2026)
    month = int(match.group(2))
    last = calendar.monthrange(year, month)[1] if 1 <= month <= 12 else 31
    return {"time_from": f"{year:04d}-{month:02d}-01", "time_to": f"{year:04d}-{month:02d}-{last:02d}"}


@dataclass
class Ctx:
    """Shared per-query context: one result dict, auto-numbered steps."""

    question: str
    request_id: str
    result: dict
    steps: list = field(default_factory=list)
    _n: int = 0
    t0: float = 0.0  # 查询起点（iter_query 注入），final 帧计算 total_ms

    def __post_init__(self):
        self.result["steps"] = self.steps  # live reference: final payload carries steps

    def emit(self, title: str, status: str, detail: str, **extra) -> dict:
        self._n += 1
        step = {"n": self._n, "title": title, "status": status, "detail": detail}
        step.update(extra)
        self.steps.append(step)
        return {"kind": "step", "step": step}

    def final_frame(self) -> dict:
        self.result["state"] = resolve_state(
            self.result["path"], self.result.get("block_reason"),
            empty=self.result.get("empty", False), degraded=self.result.get("degraded", False),
        )
        if self.t0:
            self.result["total_ms"] = round((time.time() - self.t0) * 1000)
        storage.persist_trace(self.result)  # discipline: every path persists + terminates
        return {"kind": "final", "result": self.result}


# ------------------------------------------------------------------- templates

def answer_assemble(measure_col: str, dims, rows: list, params: dict) -> str:
    """Semantic-layer template assembly — the LLM never produces numbers (D6).
    Shapes without a template fall back to a number-free sentence (table renders)."""
    return templates.render(measure_col, dims, rows, params) or "查询完成，结果见下表。"


def traceable_numbers(measure_col: str, dims, rows: list, params: dict | None) -> set:
    """Every number the templates may print, derived from rows/params only.
    Invariant (D6 / test): numbers(answer) ⊆ traceable_numbers(...)."""
    allowed: set = set()

    def add(value):
        allowed.add(str(value))
        if isinstance(value, int) or (isinstance(value, float) and float(value).is_integer()):
            allowed.add(f"{int(value):,}")

    for row in rows:
        for value in row.values():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                add(value)
    if dims and rows:
        add(sum(r[measure_col] for r in rows))
    dim_ids = {d.split("=")[0] for d in dims}
    if "gender" in dim_ids and rows:
        total = sum(r[measure_col] for r in rows)
        for r in rows:
            allowed.add(f"{100 * r[measure_col] / total:.1f}")
    for bound in (params or {}).values():
        for part in re.split(r"\D", str(bound)):
            if part:
                allowed.add(part)
                allowed.add(str(int(part)))
    return allowed


# ----------------------------------------------------------------- chain steps

def _route(ctx: Ctx):
    """LLM routing (registry-constrained) with keyword fallback.
    Returns (plan, llm, route_code, why)."""
    llm = llm_route(ctx.question)
    if "error" not in llm:
        return llm["plan"], llm, None, f"DeepSeek 路由 {llm['ms']}ms · 原始输出: {llm['raw']}"
    plan = keyword_route(ctx.question)  # M5.5 增强版：别名归一 + value_hints 维度补带
    hit = plan.hit or plan.reject_domain or "无命中"
    why = f"LLM 路由不可用（{llm['error']}），退回关键词匹配 → {hit}"
    return plan, None, llm.get("error_code", errors.E_ROUTE_FALLBACK), why


def _check_params(params: dict | None):
    """Returns (block_reason, answer, detail) when the query must stop, else None."""
    rng = config.data_range()
    if params and (params["time_from"] < rng["min"] or params["time_to"] > rng["max"]):
        return ("out_of_range",
                f"当前数据仅覆盖 {rng['min']} ~ {rng['max']}，该时间段无数据。",
                f"时间范围超出数据边界 {rng} → 如实说明，不硬答")
    if params is None:
        return ("missing_param", errors.user_message(errors.E_PARAM_MISSING),
                "时间范围缺失 → 追问用户，不猜测")
    return None


def _tables_for(measure_id: str, dimensions) -> list:
    """Queried tables with their warehouse layer, derived from the registry."""
    def layer_of(table: str) -> str:
        return table.split(".")[-1].split("_")[0].upper()

    reg = REGISTRY
    out = [{"name": reg.measures[measure_id].source_table,
            "layer": layer_of(reg.measures[measure_id].source_table)}]
    seen = {reg.measures[measure_id].source_table}
    for entry in dimensions:
        dim = reg.dimensions.get(entry.split("=")[0])
        if dim is None or dim.join is None or dim.join.table in seen:
            continue
        seen.add(dim.join.table)
        out.append({"name": dim.join.table, "layer": layer_of(dim.join.table)})
    return out


def _reject_card(domain: str | None, hit: str | None, code: str = "UNREGISTERED_MEASURE",
                 message: str | None = None, **extra_details) -> dict:
    """Structured refusal card: machine-readable reason + what IS answerable."""
    return {
        "code": code,
        "message": message or f"未注册域「{domain}」：当前语义层无可回答的注册口径",
        "details": {"hit": hit, "domain": domain,
                    "available_measures": sorted(REGISTRY.measures), **extra_details},
    }


def _finish_refused(ctx: Ctx, card: dict, keyword: str | None):
    """OUT_OF_SCOPE flow: structured refusal card + variant copy — never numbers."""
    answer = guided_reject_answer(keyword)  # M6.1 拒答文案升级为引导式（注册表现生成）
    ctx.result["path"] = "rejected"
    ctx.result["error_code"] = errors.E_SCOPE
    ctx.result["reject_card"] = card
    ctx.result["answer"] = answer
    yield ctx.emit("口径拦截", "blocked", f"结构化拒答 [{card['code']}] {card['message']}")
    yield ctx.emit("回答", "blocked", answer)
    yield ctx.final_frame()


def _finish_error(ctx: Ctx, code: str, message: str) -> dict:
    """Service-exception terminal frame (appendix A: error frame replaces final)."""
    ctx.result["path"] = "error"
    ctx.result["error_code"] = code
    ctx.result["answer"] = message
    ctx.result["state"] = resolve_state("error")
    if ctx.t0:
        ctx.result["total_ms"] = round((time.time() - ctx.t0) * 1000)
    storage.persist_trace(ctx.result)
    return {"kind": "error", "code": code, "message": message}


# ------------------------------------------------------------------- main flow

def _run_gates(ctx: Ctx):
    """Route → reject/param gates. Yields gate frames; returns (plan, llm, params),
    or (None, None, None) when the chain already terminated."""
    plan, llm, route_code, why = _route(ctx)
    ctx.result["measure"] = plan.measure
    ctx.result["dimensions"] = list(plan.dimensions)
    ctx.result["rule"] = plan.shape if plan.measure else None
    if route_code:
        ctx.result["degraded"] = True
        ctx.result["route_code"] = route_code
    yield ctx.emit("意图路由", "ok" if (plan.measure or plan.rejected) else "fail",
                   f"选定查询 = {plan.shape}（{why}）")

    if plan.rejected:  # unregistered business domain → structured refusal card
        yield from _finish_refused(ctx, _reject_card(plan.reject_domain, plan.hit), plan.hit)
        return None, None, None

    if plan.measure is None:  # no routing hit at all
        ctx.result["path"] = "unregistered"
        ctx.result["error_code"] = errors.E_SCOPE
        ctx.result["reject_card"] = _reject_card(
            None, None, message="问题未映射到任何已注册原语组合")
        ctx.result["answer"] = guided_reject_answer(None)  # M6.1：无命中同样给引导式拒答
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return None, None, None

    measure = REGISTRY.measures[plan.measure]
    status = ", ".join(f"{rid}({rule.status})" for rid, rule in sorted(REGISTRY.rules.items()))
    yield ctx.emit("口径声明", "ok",
                   f"{measure.description}；口径规则 {status or '无'}")

    params = None
    if llm and llm.get("time_from") and llm.get("time_to"):
        params = {"time_from": llm["time_from"], "time_to": llm["time_to"]}
    if params is None:
        params = extract_params(ctx.question)
    blocked = _check_params(params)
    if blocked:
        yield from _finish_blocked_param(ctx, blocked)
        return None, None, None
    if llm and llm.get("time_from"):
        src_note = "DeepSeek 抽取"
        if llm.get("time_defaulted"):  # M6.2：时间缺失默认最近完整月，假设显式化
            src_note += f"（默认最近完整月，按 {params['time_from'][:7]} 统计）"
    else:
        src_note = "关键词回退抽取"
    yield ctx.emit("参数抽取+校验", "ok", f"{params} ✓（{src_note}）")
    ctx.result["path"] = "semantic_pushdown"
    return plan, llm, params


def _finish_blocked_param(ctx: Ctx, blocked):
    block_reason, answer, detail = blocked
    ctx.result["path"] = "blocked_param"
    ctx.result["block_reason"] = block_reason
    ctx.result["error_code"] = (errors.E_PARAM_MISSING if block_reason == "missing_param"
                                else errors.E_PARAM_RANGE)
    ctx.result["answer"] = answer
    yield ctx.emit("参数校验", "fail", detail)
    yield ctx.emit("回答", "blocked", answer)
    yield ctx.final_frame()


def _presentation_order(plan: RoutePlan, rows: list) -> list:
    """Leaderboard shapes (single non-time dimension) sort by measure DESC for
    the TOP-N answer; the compiler itself only orders by dimension columns."""
    if len(plan.dimensions) == 1 and not plan.dimensions[0].startswith("time_grain"):
        return sorted(rows, key=lambda r: r[plan.measure], reverse=True)
    return rows


def _execute(conn, compiled, plan: RoutePlan) -> tuple:
    """Pushdown execution + same-source cross check inside one read-only
    mirror connection. Returns (rows-as-dicts, columns, checks, ms)."""
    t0 = time.time()
    cursor = conn.execute(compiled.sql, list(compiled.params))
    columns = [d[0] for d in cursor.description]
    rows = _presentation_order(plan, [dict(zip(columns, row)) for row in cursor.fetchall()])
    ms = round((time.time() - t0) * 1000, 1)
    checks = [(f"列结构与编译产物一致 {list(compiled.columns)}", columns == list(compiled.columns))]
    if plan.dimensions:  # cross-source invariant: grouped sum == dimensionless total
        total_req = QueryRequest(measure=plan.measure, dimensions=(),
                                 time_from=compiled.params[0], time_to=compiled.params[1])
        total_sql = compile_query(total_req)
        total = conn.execute(total_sql.sql, list(total_sql.params)).fetchone()[0]
        subtotal = sum(r[plan.measure] for r in rows)
        checks.append((f"同源交叉：分组合计 {subtotal} = 无维度总数 {total}", subtotal == total))
    return rows, columns, checks, ms


def _stream_answer(ctx: Ctx):
    yield ctx.emit("回答", "ok", ctx.result["answer"])
    answer = ctx.result["answer"]
    for i in range(0, len(answer), TOKEN_CHUNK):
        yield {"kind": "token", "text": answer[i:i + TOKEN_CHUNK]}
        time.sleep(TOKEN_SLEEP_S)


def _run_data_path(ctx: Ctx, plan: RoutePlan, params: dict):
    """Compiler SQL → pushdown → validation → template answer (numbers from rows only)."""
    mcol = plan.measure
    ctx.result["params"] = params
    ctx.result["viz"] = viz_for(plan.measure, plan.dimensions)  # D7: shape-derived viz (None → table)
    request = QueryRequest(measure=plan.measure, dimensions=plan.dimensions,
                           time_from=params["time_from"], time_to=params["time_to"])
    try:
        compiled = compile_query(request)
    except SemanticError as exc:  # defense in depth: router validated, compiler decides
        yield from _finish_refused(ctx, dict(exc.to_dict()["error"]),
                                   exc.details.get("measure") or exc.details.get("dimension"))
        return
    ctx.result["sql"] = compiled.sql
    ctx.result["tables"] = _tables_for(plan.measure, plan.dimensions)
    yield ctx.emit("SQL 编译", "ok", "语义层编译器按注册表确定性编译，时间走绑定参数",
                   sql=compiled.sql)

    try:
        conn = duckdb.connect(str(config.MIRROR_DB), read_only=True)
        try:
            rows, _columns, checks, ms = _execute(conn, compiled, plan)
        finally:
            conn.close()
    except SemanticError as exc:
        yield from _finish_refused(ctx, dict(exc.to_dict()["error"]), None)
        return
    except duckdb.Error:
        yield _finish_error(ctx, errors.E_SQL,
                            errors.user_message(errors.E_SQL, request_id=ctx.request_id))
        return

    ctx.result["rows"] = sanitize.apply_pii_policy(rows, SENSITIVE_FIELDS)
    yield ctx.emit("下推执行", "ok", f"duckdb 镜像 → {len(rows)} 行 · {ms}ms",
                   ms=ms, row_count=len(rows))
    for name, ok in checks:
        yield ctx.emit("结果校验", "ok" if ok else "fail", f"{'✓' if ok else '✗'} {name}")

    if not all(ok for _, ok in checks):
        ctx.result["path"] = "validation_failed"
        ctx.result["error_code"] = errors.E_VALIDATION
        ctx.result["answer"] = errors.user_message(errors.E_VALIDATION)
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return

    dim_ids = {d.split("=")[0] for d in plan.dimensions}
    if not rows:
        ctx.result["empty"] = True
        ctx.result["answer"] = EMPTY_ANSWER
    elif "gender" in dim_ids and all(r.get("gender") is None for r in rows):
        # Registered dimension, unfilled mirror column → honest degradation, no fake split.
        ctx.result["degraded"] = True
        ctx.result["degraded_reason"] = "dimension_unfilled"
        ctx.result["answer"] = DIMENSION_UNFILLED_ANSWER
        yield ctx.emit("降级说明", "warn",
                       "gender 已注册，但镜像 dim_cu_usr_info_df.usr_sex 全为 NULL")
    else:
        ctx.result["answer"] = answer_assemble(mcol, plan.dimensions, rows, params)
    try:  # D6 hard gate: every printed number must be traceable (§5-D9)
        found = validate_numbers(ctx.result["answer"],
                                 traceable_numbers(mcol, plan.dimensions, rows, params))
    except NumberValidationError as exc:
        ctx.result["path"] = "validation_failed"
        ctx.result["error_code"] = errors.E_VALIDATION
        ctx.result["answer"] = errors.user_message(errors.E_VALIDATION)
        yield ctx.emit("数字校验", "fail", str(exc))  # 数值对照只进 trace，不进用户文案
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return
    yield ctx.emit("数字校验", "ok", f"{len(found)} 个数字全部可溯源")
    yield from _stream_answer(ctx)
    yield ctx.final_frame()


def _run(ctx: Ctx):
    plan, _llm, params = yield from _run_gates(ctx)
    if plan is None:
        return
    yield from _run_data_path(ctx, plan, params)


def iter_query(question: str, request_id: str | None = None):
    """Execute the full decision chain, yielding step/token/final(/error) events.
    Frames: {"kind": "step", "step": {...}} | {"kind": "token", "text"} |
    {"kind": "final", "result": {...}} | {"kind": "error", "code", "message"}."""
    rid = request_id or new_request_id()
    ctx = Ctx(question=question, request_id=rid, t0=time.time(), result={
        "request_id": rid,
        "started_at": datetime.now().isoformat(timespec="seconds"),  # noqa: DTZ005 与 storage 同格式
        "question": question,
        "rule": None,
        "measure": None,
        "dimensions": [],
        "data_profile": "mock",  # 仿真镜像数据徽标元数据（D7 下一步前端消费）
        "path": "unknown",
        "state": None,
        "answer": "",
        "sql": None,
        "rows": [],
        "tables": [],
        "params": None,
    })
    try:
        yield from _run(ctx)
    except GeneratorExit:  # client disconnected → record the canceled trace (best effort)
        ctx.result["canceled"] = True
        ctx.result["state"] = resolve_state("canceled")
        storage.persist_trace(ctx.result)
        raise
