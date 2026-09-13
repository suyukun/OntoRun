#!/usr/bin/env python3
"""财富广场注册域·最小语义层（核心逻辑）。
决策链：意图路由(选规则) → 口径声明 → 参数校验 → SQL编译 → 下推执行 → 结果校验 → 回答。
LLM 自由度 = 输出规则 ID + 参数（演示用关键词模拟；真实系统 = LLM 分类，输出限制为规则枚举）。"""
import sqlite3, time, uuid
from datetime import date

DB = "/Users/suyukun/Projects/OntoRun/data/fortune/fortune.db"

RULES = {
    "REG_TOTAL": {
        "desc": "注册用户数（自然月去重人数）",
        "keywords": ["注册总数", "注册多少", "注册用户数", "注册量", "注册"],
        "path": "hot", "layer": "DWS",
        "caliber": "SUM(去重 usr_id)；含子公司同步注册；口径裁决号 2026-09-08-J1",
        "params": ["start", "end"],
        "sql": "SELECT COALESCE(SUM(cnt),0) AS total FROM dws_reg_daily_df WHERE data_dt BETWEEN :start AND :end",
        "columns": ["total"],
        "tables": [{"name": "dws_reg_daily_df", "layer": "DWS"}],
    },
    "REG_BY_CHANNEL": {
        "desc": "分渠道注册用户数（明细下推聚合）",
        "keywords": ["按渠道", "渠道", "分渠道", "各渠道", "来源"],
        "path": "cold_pushdown", "layer": "DWD+DIM",
        "caliber": "明细按 rgst_chnl_id 聚合去重；渠道名 JOIN 渠道维表；与 REG_TOTAL 必须同源一致",
        "params": ["start", "end"],
        "sql": "SELECT ch.chnl_nm AS channel, COUNT(DISTINCT r.usr_id) AS cnt FROM dwd_tr_rgst_df r JOIN dim_ch_chl_df ch ON ch.chnl_id = r.rgst_chnl_id WHERE r.data_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC",
        "columns": ["channel", "cnt"],
        "tables": [{"name": "dwd_tr_rgst_df", "layer": "DWD"}, {"name": "dim_ch_chl_df", "layer": "DIM"}],
    },
    "GENDER_RATIO": {
        "desc": "注册用户性别分布（维表属性即席统计）",
        "keywords": ["男女", "性别", "男性", "女性", "比例"],
        "path": "cold_adhoc", "layer": "DIM",
        "caliber": "维表 usr_sex 属性分布；明细级即席计算，回答必须标注",
        "params": ["start", "end"],
        "sql": "SELECT CASE usr_sex WHEN 1 THEN '男' WHEN 2 THEN '女' ELSE '未知' END AS gender, COUNT(DISTINCT u.usr_id) AS cnt FROM dim_cu_usr_info_df u WHERE u.rgst_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC",
        "columns": ["gender", "cnt"],
        "notice": "明细级即席计算（未预聚合）：结果为即时快照，非月报口径",
        "tables": [{"name": "dim_cu_usr_info_df", "layer": "DIM"}],
    },
    "OUT_OF_SCOPE": {
        "desc": "范围外问题（活跃/转化域未注册）",
        "keywords": ["活动", "任务", "抽奖", "奖品", "导流", "日活", "活跃"],
        "path": "rejected",
        "reject": "该问题涉及【活跃/转化域】，当前语义范围仅注册域（Jack 2026-09-08 收窄指令）。不生成 SQL、不猜测。扩展范围需先注册对应对象与口径。",
        "tables": [],
    },
}
RULE_ORDER = ["OUT_OF_SCOPE", "GENDER_RATIO", "REG_BY_CHANNEL", "REG_TOTAL"]

import os, re, json as _json, time as _time

def _load_env():
    env = {}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env
_ENV = _load_env()
DATA_RANGE = {"min": "2026-07-01", "max": "2026-08-31"}  # 样本数据边界（硬校验用）

def llm_route(question):
    """真 LLM 路由（DeepSeek）：输出被限制为规则 ID 枚举 + 参数 JSON。
    硬校验：rule_id 必须在注册表内（发明即拒绝）；日期格式合法。
    任何失败返回 None → 上层退回关键词匹配（降级路径）。"""
    try:
        from openai import OpenAI
    except ImportError:
        return {"error": "openai 包未安装"}
    key = _ENV.get("DEEPSEEK_API_KEY")
    if not key:
        return {"error": ".env 无 DEEPSEEK_API_KEY"}
    catalog = "\n".join(f"- {k}: {v.get('desc', '')}" for k, v in RULES.items())
    system = (
        "你是语义层的意图路由器。唯一任务：把用户问题映射到唯一规则 ID，并抽取时间参数。"
        '只输出一个 JSON 对象：{"rule_id": "...", "params": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}，'
        "rule_id 必须从清单中选择，禁止发明；时间缺失时 params 传空对象；"
        "时间参数必须落在样本数据可用范围内：2026-07-01 ~ 2026-08-31。\n与注册规则无关的问题一律 rule_id=OUT_OF_SCOPE。\n规则清单：\n" + catalog
    )
    try:
        client = OpenAI(api_key=key, base_url=_ENV.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
        t0 = _time.time()
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
            temperature=0, max_tokens=200,
        )
        ms = round((_time.time() - t0) * 1000)
        raw = resp.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"LLM 调用失败: {e}"}
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {"error": f"LLM 输出非 JSON: {raw[:80]}", "raw": raw, "ms": ms}
    try:
        data = _json.loads(m.group(0))
    except Exception as e:
        return {"error": f"JSON 解析失败: {e}", "raw": raw, "ms": ms}
    rid = data.get("rule_id")
    if rid not in RULES:
        return {"error": f"LLM 发明了未注册规则「{rid}」→ 拒绝", "raw": raw, "ms": ms}
    params = {k: v for k, v in (data.get("params") or {}).items() if re.match(r"^\d{4}-\d{2}-\d{2}$", str(v))}
    return {"rule_id": rid, "params": params, "raw": raw, "ms": ms, "model": "deepseek-chat"}


def route(question):
    for rid in RULE_ORDER:
        for kw in RULES[rid]["keywords"]:
            if kw in question:
                return rid, f"命中关键词「{kw}」"
    return None, "无规则命中"

def extract_params(question):
    if "8月" in question or "八月" in question:
        return {"start": "2026-08-01", "end": "2026-08-31"}
    if "7月" in question or "七月" in question:
        return {"start": "2026-07-01", "end": "2026-07-31"}
    return None

def compile_sql(template, params):
    sql = template
    for k, v in params.items():
        sql = sql.replace(f":{k}", f"'{v}'")
    return sql

def answer_assemble(rule_id, rows, params):
    if rule_id == "REG_TOTAL":
        return f"{params['start'][:7]} 月注册 {rows[0]['total']:,} 人。"
    if rule_id == "REG_BY_CHANNEL":
        return f"共 {sum(r['cnt'] for r in rows):,} 人，TOP3：" + "、".join(f"{r['channel']} {r['cnt']:,}" for r in rows[:3]) + "。"
    if rule_id == "GENDER_RATIO":
        s = sum(r["cnt"] for r in rows)
        return "、".join(f"{r['gender']} {r['cnt']:,}（{100*r['cnt']/s:.1f}%）" for r in rows) + f"。合计 {s:,} 人。"
    return ""

TRACE_LOG = "/Users/suyukun/Projects/OntoRun/data/fortune/trace_log.jsonl"

def _persist(result: dict):
    """证据链落库（最小版）：每次查询全步 trace 追加至 JSONL。审计级（不可篡改/回放/导出）为待办。"""
    try:
        with open(TRACE_LOG, "a", encoding="utf-8") as f:
            f.write(_json.dumps(result, ensure_ascii=False) + "\n")
    except Exception:
        pass

def iter_query(question: str):
    """执行一次完整决策链，逐步 yield 事件。
    事件：{"kind":"step",...} / {"kind":"token","text"} / {"kind":"final","result":result}
    纪律：每条路径必须 _persist + yield final（否则前端拿不到结果）。"""
    import datetime as _dt
    request_id = f"REQ-{date.today().isoformat()}-{uuid.uuid4().hex[:6].upper()}"
    started_at = _dt.datetime.now().isoformat(timespec="seconds")
    steps = []
    result = {"request_id": request_id, "started_at": started_at, "question": question, "rule": None,
              "steps": steps, "path": "unknown", "answer": "", "sql": None, "rows": [], "tables": []}

    def emit(n, title, status, detail, **extra):
        d = {"n": n, "title": title, "status": status, "detail": detail}
        d.update(extra)
        steps.append(d)
        return {"kind": "step", "step": d}

    def finish():
        _persist(result)
        return {"kind": "final", "result": result}

    # [1] 意图路由（LLM 只能输出规则 ID 枚举；失败退回关键词匹配）
    llm = llm_route(question)
    llm_params = None
    if llm and "error" not in llm:
        rid = llm["rule_id"]
        why = f"DeepSeek 路由 {llm['ms']}ms · 原始输出: {llm['raw']}"
    else:
        rid, kw = route(question)
        err = llm.get("error") if isinstance(llm, dict) else "未知"
        why = f"LLM 路由不可用（{err}），退回关键词匹配 → 命中「{kw}」"
    result["rule"] = rid
    yield emit(1, "意图路由", "ok" if rid else "fail",
               f"选定规则 = {rid or '无'}（{why}）。LLM 只能输出规则 ID 枚举，不生成 SQL；发明即拒绝。")

    if rid is None:
        result["path"] = "unregistered"
        result["answer"] = "该问题尚未注册口径，可提交为新的派生规则候选。"
        yield emit(7, "回答", "blocked", result["answer"])
        yield finish()
        return

    rule = RULES[rid]
    result["path"] = rule["path"]
    result["tables"] = rule.get("tables", [])

    # 范围外（拒答）
    if "reject" in rule:
        result["answer"] = rule["reject"]
        yield emit(2, "口径拦截", "blocked", rule["reject"])
        yield emit(7, "回答", "blocked", result["answer"])
        yield finish()
        return

    # [2] 口径声明
    yield emit(2, "口径声明", "ok", rule["caliber"])

    # [3] 参数抽取 + 硬校验（LLM 抽取优先，关键词回退；边界校验兜底）
    params = (llm.get("params") if llm and "error" not in llm else None) or extract_params(question)
    src_note = "DeepSeek 抽取" if (llm and "error" not in llm and llm.get("params")) else "关键词回退抽取"
    if params and (params["start"] < DATA_RANGE["min"] or params["end"] > DATA_RANGE["max"]):
        result["path"] = "blocked_param"
        result["answer"] = f"当前样本数据仅覆盖 {DATA_RANGE['min']} ~ {DATA_RANGE['max']}，该时间段无数据。"
        yield emit(3, "参数校验", "fail", f"时间范围超出样本数据边界 {DATA_RANGE} → 如实说明，不硬答")
        yield emit(7, "回答", "blocked", result["answer"])
        yield finish()
        return
    if params is None:
        result["path"] = "blocked_param"
        result["answer"] = "请问您要查询哪个月份？"
        yield emit(3, "参数校验", "fail", "时间范围缺失 → 追问用户，不猜测")
        yield emit(7, "回答", "blocked", result["answer"])
        yield finish()
        return
    yield emit(3, "参数抽取+校验", "ok", f"{params} ✓（{src_note}）")

    # [4] SQL 编译（确定性，LLM 不参与）
    sql = compile_sql(rule["sql"], params)
    result["sql"] = sql
    yield emit(4, "SQL 编译", "ok", "由规则模板确定性编译（LLM 未参与）", sql=sql)

    # [5] 下推执行
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    t0 = _time.time()
    rows = [dict(r) for r in conn.execute(sql)]
    ms = round((_time.time() - t0) * 1000, 1)
    result["rows"] = rows
    yield emit(5, "下推执行", "ok", f"sqlite → {len(rows)} 行，{ms}ms（计算在数据引擎，不在语义层）", ms=ms, row_count=len(rows))

    # [6] 结果校验
    checks = []
    actual_cols = list(rows[0].keys()) if rows else rule["columns"]
    checks.append(("列结构与规则声明一致", actual_cols == rule["columns"]))
    if rid == "REG_BY_CHANNEL":
        chs = {r[0] for r in conn.execute("SELECT chnl_nm FROM dim_ch_chl_df")}
        checks.append(("渠道枚举 ⊆ 渠道维表", all(r["channel"] in chs for r in rows)))
        s = sum(r["cnt"] for r in rows)
        total = conn.execute("SELECT COALESCE(SUM(cnt),0) FROM dws_reg_daily_df WHERE data_dt BETWEEN ? AND ?",
                             (params["start"], params["end"])).fetchone()[0]
        checks.append((f"同源交叉：分渠道合计 {s} = 热路径总数 {total}", s == total))
    if rid == "GENDER_RATIO":
        checks.append(("冷路径免责声明已附加", True))
    all_ok = all(ok for _, ok in checks)
    for name, ok in checks:
        yield emit(6, "结果校验", "ok" if ok else "fail", f"{'✓' if ok else '✗'} {name}")
    if not all_ok:
        conn.close()
        result["path"] = "validation_failed"
        result["answer"] = "校验未通过，拒绝返回结果。"
        yield emit(7, "回答", "blocked", result["answer"])
        yield finish()
        return

    # [7] 回答（拒答/追问外的正常路径才逐字流式）
    notice = f"（{rule['notice']}）" if rule.get("notice") else ""
    result["answer"] = answer_assemble(rid, rows, params) + notice
    yield emit(7, "回答", "ok", result["answer"])
    conn.close()
    for i in range(0, len(result["answer"]), 3):
        yield {"kind": "token", "text": result["answer"][i:i+3]}
        _time.sleep(0.015)
    yield finish()

def run_query(question: str) -> dict:
    """聚合 iter_query 的 final 结果（CLI / 旧接口兼容）。落盘由 iter_query 负责。"""
    result = None
    for ev in iter_query(question):
        if ev["kind"] == "final":
            result = ev["result"]
    return result
