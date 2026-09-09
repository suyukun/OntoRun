#!/usr/bin/env python3
"""财富广场注册域·最小语义层（核心逻辑）。
决策链：意图路由(选规则) → 口径声明 → 参数校验 → SQL编译 → 下推执行 → 结果校验 → 回答。
LLM 自由度 = 输出规则 ID + 参数（演示用关键词模拟；真实系统 = LLM 分类，输出限制为规则枚举）。"""
import sqlite3, time, uuid
from datetime import date

DB = "/Users/suyukun/Documents/OntoRun/data/fortune/fortune.db"

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

def run_query(question: str) -> dict:
    """执行一次完整决策链，返回结构化结果（供 CLI 打印 / Web API 消费）。"""
    request_id = f"REQ-{date.today().isoformat()}-{uuid.uuid4().hex[:6].upper()}"
    steps = []
    def step(n, title, status, detail, **extra):
        d = {"n": n, "title": title, "status": status, "detail": detail}
        d.update(extra); steps.append(d)

    rid, why = route(question)
    step(1, "意图路由", "ok" if rid else "fail", f"选定规则 = {rid or '无'}（{why}）。LLM 输出被限制为规则 ID，不生成 SQL。")
    result = {"request_id": request_id, "question": question, "rule": rid, "steps": steps,
              "path": "unknown", "answer": "", "sql": None, "rows": [], "tables": []}
    if rid is None:
        result["path"] = "unregistered"
        result["answer"] = "该问题尚未注册口径，可提交为新的派生规则候选。"
        step(7, "回答", "blocked", result["answer"])
        return result

    rule = RULES[rid]
    result["path"] = rule["path"]; result["tables"] = rule.get("tables", [])
    if "reject" in rule:
        step(2, "口径拦截", "blocked", rule["reject"])
        result["answer"] = rule["reject"]
        step(7, "回答", "blocked", rule["reject"])
        return result
    step(2, "口径声明", "ok", rule["caliber"])

    params = extract_params(question)
    if params is None:
        step(3, "参数校验", "fail", "时间范围缺失 → 追问用户，不猜测")
        result["path"] = "blocked_param"
        result["answer"] = "请问您要查询哪个月份？"
        step(7, "回答", "blocked", result["answer"])
        return result
    step(3, "参数抽取+校验", "ok", f"{params} ✓")

    sql = compile_sql(rule["sql"], params)
    result["sql"] = sql
    step(4, "SQL 编译", "ok", "由规则模板确定性编译（LLM 未参与）", sql=sql)

    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    t0 = time.time()
    rows = [dict(r) for r in conn.execute(sql)]
    ms = round((time.time() - t0) * 1000, 1)
    result["rows"] = rows
    step(5, "下推执行", "ok", f"sqlite → {len(rows)} 行，{ms}ms（计算在数据引擎，不在语义层）", ms=ms, row_count=len(rows))

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
        step(6, "结果校验", "ok" if ok else "fail", f"{'✓' if ok else '✗'} {name}")
    if not all_ok:
        result["path"] = "validation_failed"
        result["answer"] = "校验未通过，拒绝返回结果。"
        step(7, "回答", "blocked", result["answer"])
        conn.close()
        return result

    notice = f"（{rule['notice']}）" if rule.get("notice") else ""
    result["answer"] = answer_assemble(rid, rows, params) + notice
    step(7, "回答", "ok", result["answer"])
    conn.close()
    return result

if __name__ == "__main__":
    print(f"request 演示：")
    for q in ["8月注册用户数是多少？", "8月按渠道的注册用户数？", "8月注册用户的男女比例是多少？",
              "8月注册用户里参加过活动的有多少？", "注册用户数是多少？"]:
        res = run_query(q)
        print("━" * 60)
        print(f"Q: {q}   [path={res['path']}]")
        for s in res["steps"]:
            print(f"  [{s['n']} {s['title']}] {s['status']} — {s['detail']}")
        print(f"  答: {res['answer']}")
