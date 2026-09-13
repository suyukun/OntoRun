#!/usr/bin/env python3
"""合成注册域样本数据（按 DWD/DIM 字典简化）。纪律：汇总表由明细聚合生成，不手写假数字；PII 只造加密假态。"""
import sqlite3, random, os
from datetime import date, timedelta

random.seed(42)
DB = "/Users/suyukun/Projects/OntoRun/data/fortune/fortune.db"
os.makedirs(os.path.dirname(DB), exist_ok=True)

CHANNELS = [  # (chnl_id, nm, fst_chnl_nm, fin_flg)
    ("CH001", "中信证券app",   "中信证券", 1),
    ("CH002", "中信建投app",   "中信建投", 1),
    ("CH003", "信享app",      "中信金控", 1),
    ("CH004", "微广场",       "微信生态", 0),
    ("CH005", "负一屏",       "终端合作", 0),
    ("CH006", "小米合作",     "外部投放", 0),
    ("CH007", "搜索投放",     "外部投放", 0),
]
D0, D1 = date(2026, 7, 1), date(2026, 8, 31)
DAYS = [(D0 + timedelta(days=i)).isoformat() for i in range((D1 - D0).days + 1)]

conn = sqlite3.connect(DB)
c = conn.cursor()
for t in ["dim_ch_chl_df", "dim_cu_usr_info_df", "dwd_tr_rgst_df", "dwd_cu_actv_df", "dwd_ch_usr_rltv_df", "dws_reg_daily_df"]:
    c.execute(f"DROP TABLE IF EXISTS {t}")

c.execute("CREATE TABLE dim_ch_chl_df (chnl_id TEXT, chnl_nm TEXT, fst_chnl_nm TEXT, fin_chnl_flg INT)")
c.executemany("INSERT INTO dim_ch_chl_df VALUES (?,?,?,?)", CHANNELS)

# 用户与注册：7 月 2900 人、8 月 2100 人（环比 -27.6%，贴日活下滑叙事）；渠道权重贴近"自营占比低"
weights = [0.14, 0.11, 0.09, 0.24, 0.20, 0.14, 0.08]
def pick_chnl(): return random.choices(CHANNELS, weights)[0]
def fake_aes(tag):  # 加密假态：固定前缀+随机十六进制，演示"语义层只暴露加密态"
    return f"enc(aes)::{tag}:" + "".join(random.choices("0123456789abcdef", k=32))

c.execute("""CREATE TABLE dim_cu_usr_info_df (
    usr_id TEXT PRIMARY KEY, rgst_dt TEXT, rgst_chnl_id TEXT, usr_stat_fg INT,
    real_fg INT, real_dt TEXT, real_way TEXT, usr_sex INT,
    usr_phone_erpt TEXT, usr_idcardno_erpt TEXT)""")
c.execute("""CREATE TABLE dwd_tr_rgst_df (
    data_dt TEXT, usr_id TEXT, rgst_chnl_id TEXT, rgst INT, if_act INT, is_real INT, activity_type TEXT)""")

users, rgsts = [], []
uid_seq = 0
for d in DAYS:
    m8 = d.startswith("2026-08")
    n = random.randint(55, 80) if not m8 else random.randint(45, 72)  # 8 月略降
    for _ in range(n):
        uid_seq += 1
        uid = f"U{uid_seq:06d}"
        ch = pick_chnl()
        real = 1 if random.random() < 0.42 else 0
        act = 1 if random.random() < 0.55 else 0
        acty = random.choice(["", "ACT-MGM", "ACT-XIAOMI", "ACT-JUN"]) if random.random() < 0.3 else ""
        users.append((uid, d, ch[0], 1, real, d if real else None, random.choice(["0", "1"]) if real else None,
                      random.choice([1, 2]), fake_aes("phone"), fake_aes("idcard")))
        rgsts.append((d, uid, ch[0], 1, act, real, acty))

c.executemany("INSERT INTO dim_cu_usr_info_df VALUES (?,?,?,?,?,?,?,?,?,?)", users)
c.executemany("INSERT INTO dwd_tr_rgst_df VALUES (?,?,?,?,?,?,?)", rgsts)

# 授权：实名用户 85% 有关联授权，未实名 30%
rltv = []
for u in users:
    if random.random() < (0.85 if u[4] else 0.30):
        r = random.randint(1, 30)
        rltv.append((u[1], u[0], u[2], (date.fromisoformat(u[1]) + timedelta(days=r)).isoformat()))
c.execute("CREATE TABLE dwd_ch_usr_rltv_df (rgst_dt TEXT, usr_id TEXT, chnl_id TEXT, auth_dt TEXT)")
c.executemany("INSERT INTO dwd_ch_usr_rltv_df VALUES (?,?,?,?)", rltv)

# 激活：非金融渠道(CH004-007)注册的激活事实
actv = [(u[1], u[0]) for u in users if u[2] in ("CH004", "CH005", "CH006", "CH007")]
c.execute("CREATE TABLE dwd_cu_actv_df (rgst_dt TEXT, usr_id TEXT)")
c.executemany("INSERT INTO dwd_cu_actv_df VALUES (?,?)", actv)

# 汇总表（热路径）：由明细聚合生成 —— 同源计算，不手写
c.execute("""CREATE TABLE dws_reg_daily_df AS
    SELECT data_dt, rgst_chnl_id AS chnl_id, COUNT(DISTINCT usr_id) AS cnt
    FROM dwd_tr_rgst_df GROUP BY data_dt, rgst_chnl_id""")

conn.commit()
n_reg = c.execute("SELECT COUNT(*), SUM(rgst) FROM dwd_tr_rgst_df").fetchone()
n_aug = c.execute("SELECT COALESCE(SUM(cnt),0) FROM dws_reg_daily_df WHERE data_dt LIKE '2026-08%'").fetchone()[0]
n_jul = c.execute("SELECT COALESCE(SUM(cnt),0) FROM dws_reg_daily_df WHERE data_dt LIKE '2026-07%'").fetchone()[0]
print(f"DB: {DB}")
print(f"users={len(users)} rgst_rows={n_reg[0]} rgst_sum={n_reg[1]} | 7月={n_jul} 8月={n_aug} 环比={100*(n_aug-n_jul)/n_jul:+.1f}%")
print(f"auth_rows={len(rltv)} actv_rows={len(actv)}")
conn.close()
