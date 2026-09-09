"""Decision-chain engine: iter_query event stream migrated from
scripts/fortune_demo/semantic_layer.py (logic preserved).

Engineering upgrades:
- continuous per-query step numbering (product doc §7 #3, no skipped numbers);
- structured eight-state mapping + block_reason (missing_param / out_of_range);
- generic month parameter parsing (out_of_range reachable without the LLM);
- data boundary from semantic-layer metadata (config.data_range), not hardcoded;
- SQL executed with bound parameters (templates stay :named for display);
- PII guard on rows, sanitized LLM raw output, E_SQL error frames;
- D6 hard gate: template answers validated against the traceable number set
  (untraceable number -> validation_failed, product doc §5-D6/§5-D9);
- cancel support: client disconnect persists the trace marked canceled.
"""

import calendar
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from . import config, errors, sanitize, storage, templates
from .llm_route import llm_route
from .rules import RULES, SENSITIVE_FIELDS, keyword_route
from .templates import NumberValidationError, validate_numbers

MONTH_RE = re.compile(r"(?:(20\d{2})\s*[-年/])?\s*(\d{1,2})\s*月")
TOKEN_CHUNK = 3
TOKEN_SLEEP_S = 0.01
SUCCESS_PATHS = {"hot", "cold_pushdown", "cold_adhoc"}
EMPTY_ANSWER = "该范围内无数据，请调整时间范围后重试。"


def new_request_id() -> str:
    return f"REQ-{date.today().isoformat()}-{uuid.uuid4().hex[:6].upper()}"


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
    """Generic 「(YYYY)M月」 parsing; out-of-calendar months flow into the range check."""
    match = MONTH_RE.search(question)
    if not match:
        return None
    year = int(match.group(1) or 2026)
    month = int(match.group(2))
    last = calendar.monthrange(year, month)[1] if 1 <= month <= 12 else 31
    return {"start": f"{year:04d}-{month:02d}-01", "end": f"{year:04d}-{month:02d}-{last:02d}"}


def compile_sql(template: str, params: dict) -> str:
    """Human-readable SQL for display/trace. Execution itself uses bound parameters."""
    sql = template
    for key, val in params.items():
        sql = sql.replace(":" + key, f"'{val}'")
    return sql


@dataclass
class Ctx:
    """Shared per-query context: one result dict, auto-numbered steps."""

    question: str
    request_id: str
    result: dict
    steps: list = field(default_factory=list)
    _n: int = 0

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
        storage.persist_trace(self.result)  # discipline: every path persists + terminates
        return {"kind": "final", "result": self.result}


# ------------------------------------------------------------------- templates

def answer_assemble(rule_id: str, rows: list, params: dict) -> str:
    """Semantic-layer template assembly — the LLM never produces numbers (D6).
    Sentence patterns + slot builders live in templates.py (per-rule registry)."""
    return templates.render(rule_id, rows, params)


def traceable_numbers(rule_id: str, rows: list, params: dict | None) -> set:
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
    for col in ("cnt", "total"):
        vals = [r[col] for r in rows if col in r]
        if vals:
            add(sum(vals))
    if rule_id == "GENDER_RATIO" and rows:
        total = sum(r["cnt"] for r in rows)
        for r in rows:
            allowed.add(f"{100 * r['cnt'] / total:.1f}")
    for bound in (params or {}).values():
        for part in re.split(r"\D", str(bound)):
            if part:
                allowed.add(part)
                allowed.add(str(int(part)))
    return allowed


# ----------------------------------------------------------------- chain steps

def _route(ctx: Ctx):
    """LLM routing (enum-restricted) with keyword fallback. Returns (rule_id, llm, route_code, why)."""
    llm = llm_route(ctx.question)
    if "error" not in llm:
        return llm["rule_id"], llm, None, f"DeepSeek 路由 {llm['ms']}ms · 原始输出: {llm['raw']}"
    rule_id, kw = keyword_route(ctx.question)
    why = f"LLM 路由不可用（{llm['error']}），退回关键词匹配 → 命中「{kw}」"
    return rule_id, None, llm.get("error_code", errors.E_ROUTE_FALLBACK), why


def _check_params(params: dict | None):
    """Returns (block_reason, answer, detail) when the query must stop, else None."""
    rng = config.data_range()
    if params and (params["start"] < rng["min"] or params["end"] > rng["max"]):
        return ("out_of_range",
                f"当前数据仅覆盖 {rng['min']} ~ {rng['max']}，该时间段无数据。",
                f"时间范围超出数据边界 {rng} → 如实说明，不硬答")
    if params is None:
        return ("missing_param", errors.user_message(errors.E_PARAM_MISSING),
                "时间范围缺失 → 追问用户，不猜测")
    return None


def _checks(conn: sqlite3.Connection, rule_id: str, rows: list, params: dict) -> list:
    """Result validation (demo logic): column shape + cross-source consistency."""
    rule = RULES[rule_id]
    checks = []
    actual_cols = list(rows[0].keys()) if rows else rule["columns"]
    checks.append(("列结构与规则声明一致", actual_cols == rule["columns"]))
    if rule_id == "REG_BY_CHANNEL":
        channels = {r[0] for r in conn.execute("SELECT chnl_nm FROM dim_ch_chl_df")}
        checks.append(("渠道枚举 ⊆ 渠道维表", all(r["channel"] in channels for r in rows)))
        subtotal = sum(r["cnt"] for r in rows)
        total = conn.execute(
            "SELECT COALESCE(SUM(cnt),0) FROM dws_reg_daily_df WHERE data_dt BETWEEN ? AND ?",
            (params["start"], params["end"]),
        ).fetchone()[0]
        checks.append((f"同源交叉：分渠道合计 {subtotal} = 热路径总数 {total}", subtotal == total))
    if rule_id == "GENDER_RATIO":
        checks.append(("冷路径免责声明已附加", True))
    return checks


def _execute(rule: dict, rule_id: str, params: dict):
    """Pushdown execution + checks inside one connection (single executor step)."""
    conn = sqlite3.connect(config.FORTUNE_DB)
    conn.row_factory = sqlite3.Row
    try:
        t0 = time.time()
        rows = [dict(r) for r in conn.execute(rule["sql"], params)]
        ms = round((time.time() - t0) * 1000, 1)
        checks = _checks(conn, rule_id, rows, params)
        return rows, checks, ms
    finally:
        conn.close()


# ------------------------------------------------------------------ end states

def _stream_answer(ctx: Ctx):
    yield ctx.emit("回答", "ok", ctx.result["answer"])
    answer = ctx.result["answer"]
    for i in range(0, len(answer), TOKEN_CHUNK):
        yield {"kind": "token", "text": answer[i:i + TOKEN_CHUNK]}
        time.sleep(TOKEN_SLEEP_S)


def _finish_error(ctx: Ctx, code: str, message: str) -> dict:
    """Service-exception terminal frame (appendix A: error frame replaces final)."""
    ctx.result["path"] = "error"
    ctx.result["error_code"] = code
    ctx.result["answer"] = message
    ctx.result["state"] = resolve_state("error")
    storage.persist_trace(ctx.result)
    return {"kind": "error", "code": code, "message": message}


# ------------------------------------------------------------------- main flow

def _run_gates(ctx: Ctx):
    """Route → scope/param gates. Yields gate frames; returns (rule, params), or
    (None, None) when the chain already terminated (unregistered/rejected/blocked)."""
    rule_id, llm, route_code, why = _route(ctx)
    ctx.result["rule"] = rule_id
    if route_code:
        ctx.result["degraded"] = True
        ctx.result["route_code"] = route_code
    yield ctx.emit("意图路由", "ok" if rule_id else "fail",
                   f"选定规则 = {rule_id or '无'}（{why}）。LLM 只能输出规则 ID 枚举，不生成 SQL；发明即拒绝。")

    if rule_id is None:
        ctx.result["path"] = "unregistered"
        ctx.result["error_code"] = errors.E_SCOPE
        ctx.result["answer"] = "该问题尚未注册口径，可提交为新的派生规则候选。"
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return None, None

    rule = RULES[rule_id]
    ctx.result["path"] = rule["path"]
    ctx.result["tables"] = rule.get("tables", [])

    if "reject" in rule:  # out-of registered scope → refuse, never guess
        ctx.result["error_code"] = errors.E_SCOPE
        ctx.result["answer"] = rule["reject"]
        yield ctx.emit("口径拦截", "blocked", rule["reject"])
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return None, None

    yield ctx.emit("口径声明", "ok", rule["caliber"])

    params = (llm.get("params") if llm else None) or extract_params(ctx.question)
    blocked = _check_params(params)
    if blocked:
        yield from _finish_blocked_param(ctx, blocked)
        return None, None
    src_note = "DeepSeek 抽取" if (llm and llm.get("params")) else "关键词回退抽取"
    yield ctx.emit("参数抽取+校验", "ok", f"{params} ✓（{src_note}）")
    return rule, params


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


def _run_data_path(ctx: Ctx, rule: dict, params: dict):
    """SQL compile → pushdown → validation → template answer (numbers from rows only)."""
    rule_id = ctx.result["rule"]
    ctx.result["params"] = params
    ctx.result["viz"] = rule.get("viz")  # D7: visualization contract from rule registry (None → table fallback)
    ctx.result["sql"] = compile_sql(rule["sql"], params)
    yield ctx.emit("SQL 编译", "ok", "由规则模板确定性编译（LLM 未参与）", sql=ctx.result["sql"])

    try:
        rows, checks, ms = _execute(rule, rule_id, params)
    except sqlite3.Error:
        yield _finish_error(ctx, errors.E_SQL,
                            errors.user_message(errors.E_SQL, request_id=ctx.request_id))
        return

    ctx.result["rows"] = sanitize.apply_pii_policy(rows, SENSITIVE_FIELDS)
    yield ctx.emit("下推执行", "ok", f"sqlite → {len(rows)} 行，{ms}ms（计算在数据引擎，不在语义层）",
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

    if not rows:
        ctx.result["empty"] = True
        ctx.result["answer"] = EMPTY_ANSWER
    else:
        notice = f"（{rule['notice']}）" if rule.get("notice") else ""
        ctx.result["answer"] = answer_assemble(rule_id, rows, params) + notice
    try:  # D6 hard gate: every printed number must be traceable (§5-D9)
        found = validate_numbers(ctx.result["answer"],
                                 traceable_numbers(rule_id, rows, params))
    except NumberValidationError as exc:
        ctx.result["path"] = "validation_failed"
        ctx.result["error_code"] = errors.E_VALIDATION
        ctx.result["answer"] = errors.user_message(errors.E_VALIDATION)
        yield ctx.emit("数字校验", "fail", str(exc))  # 数值对照只进 trace，不进用户文案
        yield ctx.emit("回答", "blocked", ctx.result["answer"])
        yield ctx.final_frame()
        return
    yield ctx.emit("数字校验", "ok",
                   f"回答 {len(found)} 个数字全部 ∈ 语义层可溯源集合（D6）")
    yield from _stream_answer(ctx)
    yield ctx.final_frame()


def _run(ctx: Ctx):
    rule, params = yield from _run_gates(ctx)
    if rule is None:
        return
    yield from _run_data_path(ctx, rule, params)


def iter_query(question: str, request_id: str | None = None):
    """Execute the full decision chain, yielding step/token/final(/error) events.
    Frames: {"kind": "step", "step": {...}} | {"kind": "token", "text"} |
    {"kind": "final", "result": {...}} | {"kind": "error", "code", "message"}."""
    rid = request_id or new_request_id()
    ctx = Ctx(question=question, request_id=rid, result={
        "request_id": rid,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "rule": None,
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
