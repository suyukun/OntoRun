"""P2 head-to-head 实验主 runner（任务 2/3）。

A=LLM 生成 SQL → 多层守卫（只读白名单视图/单语句/禁注入/结果护栏/超时）→ DuckDB 本地执行；
B=LLM 生成契约 JSON → validate_contract + ContractExecutor 执行（PermissionContext.allow_all 内部口径）。
逐问记录：成功(答案 vs GT)/拒答(fail-closed)/错误，LLM 延迟、执行延迟、token 分项、成本估算。
增量写 scripts/headtohead/results.json（每问完成即落盘，可断点续跑）。
"""
from __future__ import annotations

import json
import random
import re
import sys
import threading
import time
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.headtohead.compare import (
    extract_codes,
    extract_rows,
    extract_scalar,
    match_table,
)
from scripts.headtohead.prompts import (
    build_a_prompt,
    build_b_prompt,
    build_b_surface,
)
from scripts.headtohead.questions import BY_ID, QUESTIONS
from src.agent.provider import (
    ChatMessage,
    ChatResponse,
    DeepSeekProvider,
    _to_openai_message,
)
from src.des.contract import ContractError, ContractExecutor, PermissionContext
from src.des.materialize import materialize_des
from src.des.metrics import load_metrics
from src.ontology import build_registry

ENTERPRISE = "hc_precision"
D = ROOT / "data" / "des" / "enterprises" / ENTERPRISE
RESULTS_FILE = HERE / "results.json"

# 18 表白名单（A 形态守卫：FROM/JOIN 标识符必须 ∈ 此集 ∪ CTE 名）
WHITELIST_TABLES = {
    "KNA1", "MARA", "MARC", "MARD", "MAST", "STPO", "VBAK", "VBAP",
    "MPLA", "AUFK", "AFPO", "COFV", "WMMD", "MSEG", "LFA1", "EKKO", "EKPO", "ACDOCA",
}
FORBIDDEN = [
    ";", "--", "/*", "*/", "insert", "update", "delete", "drop", "alter", "create",
    "attach", "pragma", "load", "copy ", "call ", "read_csv", "read_parquet",
    "read_json", "glob(", "secret", "system", "from all_files", "import", "export",
]
RESULT_ROW_CAP = 200_000   # A 形态结果护栏（行数，analytics 口径）
RESULT_COL_CAP = 20        # A 形态结果护栏（列数）
EXEC_TIMEOUT_S = 60        # 单查询执行超时


# ---------------- 用量捕获 provider（走现有 DeepSeek provider 同款 SDK/key/model） ----------------
class MeasuredDeepSeek(DeepSeekProvider):
    def __init__(self):
        super().__init__()
        self.calls: list[dict] = []

    def chat(self, messages, tools=None):
        msgs = [m if isinstance(m, ChatMessage) else ChatMessage(role=m["role"], content=m.get("content"))
                for m in messages]
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[_to_openai_message(m) for m in msgs],
            tools=tools,
        )
        u = resp.usage
        self.calls.append({
            "prompt": int(u.prompt_tokens or 0),
            "completion": int(u.completion_tokens or 0),
        })
        choice = resp.choices[0].message
        tool_calls = []
        for tc in choice.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}
            tool_calls.append(type("TC", (), {"id": tc.id, "name": tc.function.name, "arguments": args})())
        return ChatResponse(content=choice.content, tool_calls=tool_calls)


def llm_call(provider, messages, attempts=3) -> tuple[str | None, float, dict]:
    """调用 LLM（重试 3 次，退避）。返回 (content, 耗时 ms, usage dict)。"""
    last_err = None
    for i in range(attempts):
        t0 = time.time()
        try:
            resp = provider.chat(messages)
            dt = (time.time() - t0) * 1000
            usage = provider.calls[-1] if provider.calls else {}
            return resp.content, dt, usage
        except Exception as e:  # noqa: BLE001 — 网络/限流失败如实记录
            last_err = repr(e)
            time.sleep(2 * (i + 1))
    return None, (time.time() - t0) * 1000, {"error": last_err}


def _extract_balanced_json(text: str) -> str | None:
    """从文本提取第一个配平花括号 JSON 对象（跳过前后文字，处理嵌套与字符串内花括号）。"""
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def parse_json_obj(text: str | None) -> dict | None:
    """解析 LLM 输出 JSON：容忍 markdown 围栏 / 前后多余文字 / 围栏内嵌。"""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        frag = _extract_balanced_json(text)
        if frag:
            try:
                return json.loads(frag)
            except json.JSONDecodeError:
                return None
        return None


# ---------------- A 形态：SQL 守卫 + 执行 ----------------
def guard_sql(sql: str) -> list[str]:
    """多层守卫（设计 §5）：单语句 / 禁注入 / 白名单表 / 结果护栏在 exec 层。返回违规列表。"""
    v: list[str] = []
    s = sql.strip()
    if not re.match(r"^(SELECT|WITH)\b", s, re.IGNORECASE):
        v.append("非 SELECT/WITH 单语句")
        return v
    low = " " + s.lower() + " "
    for f in FORBIDDEN:
        if f in low:
            v.append(f"含禁用片段: {f!r}")
    # 提取 FROM/JOIN 表标识符（允许 db.table 限定名，限定名取表名部分校验）
    refs = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)", s, re.IGNORECASE)
    cte_names = set(re.findall(r"\bWITH\s+([A-Za-z_][A-Za-z0-9_]*)\s+AS\b", s, re.IGNORECASE))
    cte_up = {c.upper() for c in cte_names}
    bad = []
    for r in refs:
        tbl = r.split(".")[-1]
        q = r.split(".")[0] if "." in r else None
        ok = tbl.upper() in WHITELIST_TABLES or tbl.upper() in cte_up
        if not ok:
            bad.append(r)
        elif q is not None and q.lower() not in ("erp", "mes", "wms", "scm", "fin"):
            bad.append(r)  # 限定名必须是 5 源库名
    if bad:
        v.append(f"引用非白名单表: {sorted(set(bad))}")
    # 结果/列数护栏在 execute 后校验
    return v


def exec_a(sql: str) -> tuple[list[list], list[str], float]:
    """执行 LLM 生成的 SQL（视图 + 只读），返回 (行, 违规列表, 耗时 ms)。"""
    con = duckdb.connect()
    try:
        con.execute("LOAD sqlite")
        for db, tables in _VIEWS.items():
            for t in tables:
                con.execute(
                    f"CREATE VIEW {t} AS SELECT * FROM sqlite_scan('{D}/{db}','{t}')"
                )
        result: dict = {"rows": None}
        err: list[str] = []
        # 剥掉库名限定前缀（fin.ACDOCA -> ACDOCA），视图为裸表名
        sql_exec = re.sub(r"\b(erp|mes|wms|scm|fin)\.([A-Za-z_][A-Za-z0-9_]*)\b", r"\2", sql)

        def run():
            try:
                cur = con.execute(sql_exec)
                cols = [d[0] for d in cur.description]
                if len(cols) > RESULT_COL_CAP:
                    err.append(f"列数 {len(cols)} 超过护栏 {RESULT_COL_CAP}")
                    return
                rows = cur.fetchall()
                if len(rows) > RESULT_ROW_CAP:
                    err.append(f"行数 {len(rows)} 超过护栏 {RESULT_ROW_CAP}")
                    return
                result["rows"] = [list(r) for r in rows]
            except Exception as e:  # noqa: BLE001 — SQL 执行失败如实记录
                err.append(f"执行错误: {e}")

        t0 = time.time()
        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(timeout=EXEC_TIMEOUT_S)
        dt = (time.time() - t0) * 1000
        if th.is_alive():
            err.append(f"执行超时 >{EXEC_TIMEOUT_S}s")
        return result["rows"], err, dt
    finally:
        con.close()


_VIEWS = {
    "erp.db": ["KNA1", "MARA", "MARC", "MARD", "MAST", "STPO", "VBAK", "VBAP"],
    "mes.db": ["MPLA", "AUFK", "AFPO", "COFV"],
    "wms.db": ["WMMD", "MSEG"],
    "scm.db": ["LFA1", "EKKO", "EKPO"],
    "fin.db": ["ACDOCA"],
}


def run_a(provider, q, gt_rows, gt_meta) -> dict:
    """A 形态单问：LLM 生成 SQL → 守卫 → 执行 → 比较。"""
    rec = {"form": "A", "qid": q["id"], "ask": q["ask"]}
    messages = build_a_prompt(q["ask"], ", ".join(q["gt_cols"]), q.get("adapted_note", ""))
    content, llm_ms, usage = llm_call(provider, messages)
    rec["llm_ms"] = round(llm_ms, 1)
    rec["usage"] = usage
    rec["llm_err"] = usage.get("error")
    if content is None:
        rec["outcome"] = "error"; rec["detail"] = f"LLM 调用失败: {usage.get('error')}"
        return rec
    obj = parse_json_obj(content)
    if obj is None or not isinstance(obj.get("sql"), str):
        rec["outcome"] = "error"; rec["detail"] = f"LLM 输出非 JSON/sql: {content[:200]}"
        return rec
    sql = obj["sql"]
    rec["sql"] = sql
    violations = guard_sql(sql)
    if violations:
        rec["outcome"] = "refusal"; rec["detail"] = "守卫拒答: " + "; ".join(violations)
        return rec
    rows, errs, ex_ms = exec_a(sql)
    rec["exec_ms"] = round(ex_ms, 1)
    if errs:
        rec["outcome"] = "error" if "执行错误" in errs[0] else "refusal"
        rec["detail"] = "; ".join(errs)
        return rec
    ok, reason = compare_answer(q, rows)
    rec["outcome"] = "correct" if ok else "wrong"
    rec["detail"] = "" if ok else reason
    rec["ans_row_count"] = len(rows) if rows else 0
    return rec


# ---------------- B 形态：契约校验 + 执行（allow_all） ----------------
def run_b(provider, q, gt_rows, gt_meta, executor, surface) -> dict:
    rec = {"form": "B", "qid": q["id"], "ask": q["ask"]}
    messages = build_b_prompt(q["ask"], surface)
    content, llm_ms, usage = llm_call(provider, messages)
    rec["llm_ms"] = round(llm_ms, 1)
    rec["usage"] = usage
    rec["llm_err"] = usage.get("error")
    if content is None:
        rec["outcome"] = "error"; rec["detail"] = f"LLM 调用失败: {usage.get('error')}"
        return rec
    obj = parse_json_obj(content)
    if obj is None:
        rec["outcome"] = "error"; rec["detail"] = f"LLM 输出非 JSON: {content[:200]}"
        return rec
    if obj.get("refused") is True:
        rec["outcome"] = "refusal"; rec["detail"] = "LLM 拒答(受限面不可表达): " + str(obj.get("reason", ""))[:200]
        return rec
    # 接受 {"contract": {...}} 或裸契约对象（带 contract_version/metric/object_type 之一）
    contract = obj.get("contract")
    if not isinstance(contract, dict) and any(k in obj for k in ("contract_version", "metric", "object_type")):
        contract = obj
    if not isinstance(contract, dict):
        rec["outcome"] = "error"; rec["detail"] = f"输出缺 contract: {content[:200]}"
        return rec
    rec["contract"] = contract
    t0 = time.time()
    try:
        result = executor.execute(contract)
    except ContractError as e:
        rec["exec_ms"] = round((time.time() - t0) * 1000, 1)
        rec["outcome"] = "refusal"; rec["detail"] = f"校验/执行拒答(fail-closed): {str(e)[:200]}"
        return rec
    except Exception as e:  # noqa: BLE001 — 契约执行异常如实记录
        rec["exec_ms"] = round((time.time() - t0) * 1000, 1)
        rec["outcome"] = "error"; rec["detail"] = f"执行异常: {repr(e)[:200]}"
        return rec
    rec["exec_ms"] = round((time.time() - t0) * 1000, 1)
    ok, reason = compare_answer(q, result, form="B")
    rec["outcome"] = "correct" if ok else "wrong"
    rec["detail"] = "" if ok else reason
    return rec


# ---------------- 比较 ----------------
def compare_answer(q, answer, form="A") -> tuple[bool, str]:
    kind = q["kind"]
    key_idx, val_idx = q.get("key_idx", []), q.get("val_idx", [])
    gt = q["_gt_rows"]
    if kind == "scalar":
        a = extract_scalar(answer)
        g = extract_scalar(gt)
        if a is None or g is None:
            return False, f"标量提取失败: answer={a!r} gt={g!r}"
        from scripts.headtohead.compare import close
        ok = close(g, a)
        return (ok, "" if ok else f"标量不匹配: GT {g} vs answer {a}")
    if kind == "codes":
        g = extract_codes([{"codes": [{"code_space": r[1], "value": r[2]}], "pk": r[0]} for r in gt])
        if form == "B":
            a = extract_codes(answer)
        else:
            a = extract_codes([{"codes": [{"code_space": r[1], "value": r[2]}], "pk": r[0]} for r in answer]) if answer else []
        r = match_table(sorted(g), sorted(a), [0, 1, 2], [], rel=1e-4)
        return (r["ok"], r["reason"])
    # table 形态：A=SQL 行；B=ContractExecutor 结果（rows/items/aggregations）
    if form == "B":
        a = extract_b_rows(q, answer)
    else:
        a = answer or []
    # 列数一致性：GT 列数 = 比较所需列数（key+val 的最大位置+1）
    need = max((key_idx + val_idx) or [0]) + 1
    if a and any(len(r) < need for r in a):
        return False, f"answer 列数不足 (need {need})"
    r = match_table([list(r) for r in gt], [list(r) for r in a], key_idx, val_idx)
    return (r["ok"], r["reason"])



def extract_b_rows(q, result) -> list[list]:
    """把 ContractExecutor 结果提取为 GT 列序的行。"""
    kind = q["kind"]
    qid = q["id"]
    if kind == "scalar":
        return extract_rows(result)
    if "rows" in result and isinstance(result["rows"], list):
        return [list(r.values()) for r in result["rows"]]
    if "items" in result and isinstance(result["items"], list):
        if qid == "F6":
            out = []
            for it in result["items"]:
                p = it.get("properties", {})
                out.append([p.get("matnr"), p.get("name"), p.get("material_type"), p.get("old_code")])
            return out
        if qid == "L3":
            return extract_codes(result)
    if "aggregations" in result and isinstance(result["aggregations"], list):
        return [[a["value"]] for a in result["aggregations"]]
    return []


# ---------------- 主流程 ----------------
def load_or_init_results() -> dict:
    if RESULTS_FILE.is_file():
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    return {"runs": [], "negative": [], "meta": {}}


def main() -> None:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20260821
    rng = random.Random(seed)

    # 载入 GT
    gt = json.loads((HERE / "gt_results.json").read_text(encoding="utf-8"))
    for q in QUESTIONS:
        q["_gt_rows"] = [[_clean(v) for v in r] for r in gt[q["id"]]["rows"]]
        q["gt_cols"] = gt[q["id"]]["cols"]

    # 本体执行器（B 形态，allow_all 内部口径）
    reg = build_registry()
    mz = materialize_des(ENTERPRISE, registry=reg)
    metrics = load_metrics(config=mz.config)
    executor = ContractExecutor(mz, reg, metrics=metrics,
                                permission_ctx=PermissionContext.allow_all())
    surface = build_b_surface(metrics)

    provider = MeasuredDeepSeek()
    state = load_or_init_results()
    done = {r["qid"] for r in state["runs"]}

    order = [q["id"] for q in QUESTIONS]
    rng.shuffle(order)

    for qid in order:
        if qid in done:
            continue
        q = BY_ID[qid]
        ra = run_a(provider, q, None, None)
        rb = run_b(provider, q, None, None, executor, surface)
        state["runs"].append(ra)
        state["runs"].append(rb)
        state["meta"] = {"seed": seed, "n": len(QUESTIONS)}
        RESULTS_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{len(state['runs'])//2}/30] {qid}: A={ra['outcome']} B={rb['outcome']} "
              f"({ra.get('detail','')[:40]} | {rb.get('detail','')[:40]})", flush=True)

    mz.duckdb.close()
    total_llm = sum(1 for r in state["runs"])
    print(f"\n完成 30 问 × 2 形态 = {total_llm} 次 LLM 调用。结果 -> {RESULTS_FILE}", flush=True)


def _clean(v):
    if isinstance(v, float):
        return round(v, 6)
    return v


if __name__ == "__main__":
    main()
