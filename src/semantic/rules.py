"""Rule registry (config-driven), migrated 1:1 from demo RULES.

Engineering upgrades: viz field per rule (product doc D7), PII sensitive-field
list, and build_profile() for the appendix-C profile schema. Adding a business
domain = register rules here + a profile; the shell stays untouched (§7 #11).
"""

RULES = {
    "REG_TOTAL": {
        "desc": "注册用户数（自然月去重人数）",
        "keywords": ["注册总数", "注册多少", "注册用户数", "注册量", "注册"],
        "path": "hot",
        "layer": "DWS",
        "viz": "kpi",
        "caliber": "SUM(去重 usr_id)；含子公司同步注册；口径裁决号 2026-09-08-J1",
        "params": ["start", "end"],
        "sql": "SELECT COALESCE(SUM(cnt),0) AS total FROM dws_reg_daily_df WHERE data_dt BETWEEN :start AND :end",
        "columns": ["total"],
        "tables": [{"name": "dws_reg_daily_df", "layer": "DWS"}],
    },
    "REG_BY_CHANNEL": {
        "desc": "分渠道注册用户数（明细下推聚合）",
        "keywords": ["按渠道", "渠道", "分渠道", "各渠道", "来源"],
        "path": "cold_pushdown",
        "layer": "DWD+DIM",
        "viz": "bar",
        "caliber": "明细按 rgst_chnl_id 聚合去重；渠道名 JOIN 渠道维表；与 REG_TOTAL 必须同源一致",
        "params": ["start", "end"],
        "sql": ("SELECT ch.chnl_nm AS channel, COUNT(DISTINCT r.usr_id) AS cnt "
                "FROM dwd_tr_rgst_df r JOIN dim_ch_chl_df ch ON ch.chnl_id = r.rgst_chnl_id "
                "WHERE r.data_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC"),
        "columns": ["channel", "cnt"],
        "tables": [{"name": "dwd_tr_rgst_df", "layer": "DWD"}, {"name": "dim_ch_chl_df", "layer": "DIM"}],
    },
    "GENDER_RATIO": {
        "desc": "注册用户性别分布（维表属性即席统计）",
        "keywords": ["男女", "性别", "男性", "女性", "比例"],
        "path": "cold_adhoc",
        "layer": "DIM",
        "viz": "pie",
        "caliber": "维表 usr_sex 属性分布；明细级即席计算，回答必须标注",
        "params": ["start", "end"],
        "sql": ("SELECT CASE usr_sex WHEN 1 THEN '男' WHEN 2 THEN '女' ELSE '未知' END AS gender, "
                "COUNT(DISTINCT u.usr_id) AS cnt FROM dim_cu_usr_info_df u "
                "WHERE u.rgst_dt BETWEEN :start AND :end GROUP BY 1 ORDER BY 2 DESC"),
        "columns": ["gender", "cnt"],
        "notice": "明细级即席计算（未预聚合）：结果为即时快照，非月报口径",
        "tables": [{"name": "dim_cu_usr_info_df", "layer": "DIM"}],
    },
    "OUT_OF_SCOPE": {
        "desc": "范围外问题（活跃/转化域未注册）",
        "keywords": ["活动", "任务", "抽奖", "奖品", "导流", "日活", "活跃"],
        "path": "rejected",
        "reject": ("该问题涉及【活跃/转化域】，当前语义范围仅注册域（Jack 2026-09-08 收窄指令）。"
                  "不生成 SQL、不猜测。扩展范围需先注册对应对象与口径。"),
        "tables": [],
    },
}

# Keyword scan order: reject-first so scope questions never leak into data rules.
RULE_ORDER = ["OUT_OF_SCOPE", "GENDER_RATIO", "REG_BY_CHANNEL", "REG_TOTAL"]

# PII fields (appendix C sensitive_fields): only encrypted state may leave the layer.
SENSITIVE_FIELDS = ["usr_phone_erpt", "usr_idcardno_erpt"]


def keyword_route(question: str):
    """Fallback router when LLM routing is unavailable. Returns (rule_id|None, why)."""
    for rid in RULE_ORDER:
        for kw in RULES[rid]["keywords"]:
            if kw in question:
                return rid, f"命中关键词「{kw}」"
    return None, "无规则命中"


def build_profile() -> dict:
    """Appendix-C profile schema. viz_map/rule_hints generated from RULES (single source)."""
    return {
        "name": "fortune-registration",
        "display": "财富广场 · 注册域",
        "endpoint": "/api/chat",
        "theme": "fortune",
        "panels": ["decision_pipeline", "path_badge", "conclusion_basis", "history"],
        "examples": [
            "2026年8月注册用户数是多少？",
            "8月分渠道注册情况",
            "8月注册用户男女比例",
            "7月注册用户数是多少？",
        ],
        "path_labels": {
            "hot": "🔥 热路径·月报口径",
            "cold_pushdown": "❄ 冷路径·明细下推",
            "cold_adhoc": "🧊 冷路径·即席计算",
            "blocked_param": "⛔ 参数待补/超边界",
            "unregistered": "🚫 未注册口径",
            "rejected": "🚫 范围外",
            "validation_failed": "⚠️ 校验未通过",
        },
        "rule_hints": {
            rid: {"caliber": rule["caliber"]}
            for rid, rule in RULES.items()
            if "caliber" in rule
        },
        "viz_map": {rid: rule["viz"] for rid, rule in RULES.items() if "viz" in rule},
        "sensitive_fields": list(SENSITIVE_FIELDS),
        "role_visibility": {"analyst": ["L1", "L2", "L3", "timing"], "viewer": ["L1"]},
    }
