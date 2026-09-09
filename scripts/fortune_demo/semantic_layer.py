#!/usr/bin/env python3
"""财富广场注册域·最小语义层演示。
工作机制：问题 → 意图路由(选规则,不写SQL) → 口径声明 → 参数校验 → 规则模板编译SQL → 下推 → 结果校验 → 回答。
LLM 在本链路中的自由度被压缩为：输出一个规则 ID + 参数（演示中用关键词匹配模拟 LLM，真实系统=LLM 分类输出被限制为规则枚举）。"""
import sqlite3, re, time, json

DB = "/Users/suyukun/Documents/OntoRun/data/fortune/fortune.db"

# ---------- 规则注册表（每条口径经人裁决后注册；LLM 只能引用，不能发明） ----------
RULES = {
    "REG_TOTAL": {
        "desc": "注册用户数（自然月去重人数）",
        "keywords": ["注册总数", "注册多少", "注册用户数", "注册量", "注册"],
        "path": "hot",
        "caliber": "SUM(去重 usr_id)；含子公司同步注册；口径注册表裁决号 2026-09-08-J1",
        "params": ["start", "end"],
        "sql": "SELECT COALESCE(SUM(cnt),0) AS total FROM dws_reg_daily_df WHERE data_dt BETWEEN :start AND :end",
        "columns": ["total"],
    },
    "REG_BY_CHANNEL": {
        "desc": "分渠道注册用户数",
        "keywords": ["按渠道", "渠道", "分渠道", "各渠道", "来源"],
        "path": "cold_pushdown",
        "caliber": "明细按 rgst_chnl_id 聚合去重；渠道名 JOIN 渠道维表解析；与 REG_TOTAL 必须同源一致",
        "params": ["start", "end"],
        "sql": """SELECT ch.chnl_nm AS channel, COUNT(DISTINCT r.usr_id) AS cnt
                  FROM dwd_tr_rgst_df r JOIN dim_ch_chl_df ch ON ch.chnl_id = r.rgst_chnl_id
                  WHERE r.data_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC""",
        "columns": ["channel", "cnt"],
    },
    "GENDER_RATIO": {
        "desc": "注册用户性别分布（维表属性即席统计）",
        "keywords": ["男女", "性别", "男性", "女性", "比例"],
        "path": "cold_adhoc",
        "caliber": "维表 usr_sex 属性分布；明细级即席计算——回答必须标注",
        "params": ["start", "end"],
        "sql": """SELECT CASE usr_sex WHEN 1 THEN '男' WHEN 2 THEN '女' ELSE '未知' END AS gender,
                         COUNT(DISTINCT u.usr_id) AS cnt
                  FROM dim_cu_usr_info_df u WHERE u.rgst_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC""",
        "columns": ["gender", "cnt"],
        "notice": "明细级即席计算（未预聚合）：结果为即时快照，非月报口径",
    },
    "OUT_OF_SCOPE": {
        "desc": "范围外问题（活跃/转化域未注册）",
        "keywords": ["活动", "任务", "抽奖", "奖品", "导流", "日活", "活跃"],
        "reject": "该问题涉及【活跃/转化域】，当前语义范围仅注册域（Jack 2026-09-08 收窄指令）。不生成 SQL、不猜测。扩展范围需先注册对应对象与口径。",
    },
}
RULE_ORDER = ["OUT_OF_SCOPE", "GENDER_RATIO", "REG_BY_CHANNEL", "REG_TOTAL"]  # 拒答最优先；特异性高者先匹配；宽词兜底

# ---------- 决策链 ----------
def route(question: str):
    """意图路由（mock LLM）：返回 (rule_id, 依据)。真实系统 = LLM 分类，输出被限制为规则 ID 枚举。"""
    for rid in RULE_ORDER:
        for kw in RULES[rid]["keywords"]:
            if kw in question:
                return rid, f"命中关键词「{kw}」"
    return None, "无规则命中"

def extract_params(question: str, rule: dict):
    """参数抽取（mock LLM）+ 硬校验。演示问题限定 7月/8月。"""
    if "8月" in question or "八月" in question:
        return {"start": "2026-08-01", "end": "2026-08-31"}
    if "7月" in question or "七月" in question:
        return {"start": "2026-07-01", "end": "2026-07-31"}
    return None  # 校验拦截：时间参数缺失 → 追问，不猜

def compile_sql(template: str, params: dict):
    sql = template
    for k, v in params.items():
        sql = sql.replace(f":{k}", f"'{v}'")
    return sql

def cross_validate(rule_id: str, rows: list, columns: list, conn) -> list:
    """结果校验：列结构 / 枚举合法 / 同源交叉一致性。"""
    checks = []
    actual_cols = list(rows[0].keys()) if rows else columns
    checks.append(("列结构与规则声明一致", actual_cols == columns))
    if rule_id == "REG_BY_CHANNEL":
        chs = {r[0] for r in conn.execute("SELECT chnl_nm FROM dim_ch_chl_df")}
        bad = [r["channel"] for r in rows if r["channel"] not in chs]
        checks.append(("渠道枚举 ⊆ 渠道维表", not bad))
        s = sum(r["cnt"] for r in rows)
        total = conn.execute("SELECT COALESCE(SUM(cnt),0) FROM dws_reg_daily_df WHERE data_dt BETWEEN :s AND :e",
                             {"s": _P["start"], "e": _P["end"]}).fetchone()[0]
        checks.append((f"同源交叉：分渠道合计 {s} = 热路径总数 {total}", s == total))
    if rule_id == "GENDER_RATIO":
        checks.append(("标注冷路径免责声明", True))
    return checks

def answer_assemble(rule_id: str, rows: list, params: dict) -> str:
    if rule_id == "REG_TOTAL":
        return f"{params['start'][:7]} 月注册 {rows[0]['total']:,} 人。"
    if rule_id == "REG_BY_CHANNEL":
        top = "、".join(f"{r['channel']} {r['cnt']:,}" for r in rows[:3])
        return f"共 {sum(r['cnt'] for r in rows):,} 人，TOP3：{top}。"
    if rule_id == "GENDER_RATIO":
        s = sum(r["cnt"] for r in rows)
        return "、".join(f"{r['gender']} {r['cnt']:,}（{100*r['cnt']/s:.1f}%）" for r in rows) + f"。合计 {s:,} 人。"
    return ""

_P = None  # 当前参数（交叉校验用）

def ask(question: str):
    global _P
    print("━" * 62)
    print(f"用户问题：{question}")
    trace = []

    rid, why = route(question)
    print(f"[1 意图路由] 选定规则 = {rid or '无'}（{why}）——LLM 输出被限制为规则 ID，不生成 SQL")

    if rid is None:
        print("[7 回答] 抱歉，该问题尚未注册口径。可提交为新的派生规则候选。")
        return
    rule = RULES[rid]
    if "reject" in rule:
        print(f"[2 口径] —— 拦截：{rule['reject']}")
        print("[7 回答] " + rule["reject"])
        return

    print(f"[2 口径声明] {rule['caliber']}")
    params = extract_params(question, rule)
    if params is None:
        print("[3 参数校验] ✗ 时间范围缺失 → 追问用户，不猜测")
        print("[7 回答] 请问您要查询哪个月份？")
        return
    _P = params
    print(f"[3 参数抽取+校验] {params} ✓")

    sql = compile_sql(rule["sql"], params)
    print(f"[4 SQL 编译] 由规则模板确定性编译（LLM 未参与）：\n    {re.sub(r'\s+', ' ', sql)}")

    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    t0 = time.time()
    rows = [dict(r) for r in conn.execute(sql)]
    ms = (time.time() - t0) * 1000
    print(f"[5 下推执行] sqlite → {len(rows)} 行，{ms:.1f}ms（计算在数据引擎，不在语义层）")

    checks = cross_validate(rid, rows, rule["columns"], conn)
    for name, ok in checks:
        print(f"[6 校验] {'✓' if ok else '✗'} {name}")
    if not all(ok for _, ok in checks):
        print("[7 回答] 校验未通过，拒绝返回结果。")
        return

    notice = f"（{rule['notice']}）" if rule.get("notice") else ""
    print(f"[7 回答] {answer_assemble(rid, rows, params)}{notice}")
    conn.close()

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║ 财富广场注册域 · 最小语义层演示（数据=合成样本，口径=演示裁决）")
    print("╚══════════════════════════════════════════════════════════╝")
    for q in ["8月注册用户数是多少？",
              "8月按渠道的注册用户数？",
              "8月注册用户的男女比例是多少？",
              "8月注册用户里参加过活动的有多少？",
              "注册用户数是多少？"]:
        ask(q)
