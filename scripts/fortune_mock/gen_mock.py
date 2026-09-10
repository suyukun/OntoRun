#!/usr/bin/env python
"""Generate mock data for the Fortune Plaza core 6-table chain (plan v0.1).

Pipeline (strictly follows docs/财富广场-mock数据方案_v0.1.md):
  1. cdm.dim_ch_chl_df      channel dim: 5 first / 10 second / 15 leaf channels,
                            daily full snapshots, fin_chnl_flg on every leaf
  2. cdm.dim_pb_date_yf     date dim: 62 days 2026-07-01..2026-08-31
  3. cdm.dim_cu_usr_info_df user dim: 2000 users, daily full snapshots
  4. cdm.dwd_cu_actv_df     activation detail: actv_tag 1/2, duplicate activations
  5. cdm.dwd_cu_rgst_fin_di built by running the REAL warehouse SQL verbatim
                            (脚本dwd_cu_rgst_fin_di.sql, only data_ds substituted)
  6. rec.ads_rgst_chnl_cnt_df built by running the REAL warehouse SQL verbatim
                            (脚本ads_rgst_chnl_cnt_df.sql, only data_ds substituted)

Corner cases baked in (plan section 二):
  a) 3 rows whose channel code is absent from the channel dim
     -> ADS left-join falls into a NULL channel group (expected anomaly)
  b) 2 one-person-multi-account examples (same phone, 2 usr_id each)
  c) 5 same-day register+activate users (segment A/B boundary)
  plus duplicate activations exercising the row_number dedup in the real ETL.

Rerunnable: wipes the 6 target tables, then regenerates everything.
Usage: .venv/bin/python scripts/fortune_mock/gen_mock.py
"""

from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[2]
ETL_DIR = REPO / "materials" / "fortune-warehouse-input" / "2026-09-10-数仓ddl及脚本" / "01_财富管理脚本"
ETL_FIN_SQL = ETL_DIR / "CDM层" / "用户域CU" / "脚本dwd_cu_rgst_fin_di.sql"
ETL_ADS_SQL = ETL_DIR / "ADS层" / "核心指标" / "注册" / "脚本ads_rgst_chnl_cnt_df.sql"
DB_PATH = REPO / "data" / "fortune_mirror.duckdb"

SEED = 20260911
START = date(2026, 7, 1)
N_DAYS = 62
END = START + timedelta(days=N_DAYS - 1)  # 2026-08-31
N_USERS = 2000
N_COHORT_B = 600   # 麦当劳·中信书院注册 (~30%)
N_ACTIVATED = 360  # 其中 ~60% 窗口内激活 -> 段B
DATA_DS = "${data_ds}"  # placeholder token in the original warehouse SQL

# ---------------------------------------------------------------------------
# Channel tree: 5 first-level / 10 second-level / 15 leaf channels.
# fin_chnl_flg / chnl_type / chnl_sub_nm are invented (plan §五: 分布是拍的).
# sec_nm for S0401/S0501 MUST be exactly 麦当劳 / 中信书院 (ETL 字面过滤依赖).
# (fst_id, fst_nm, sec_id, sec_nm, chnl_id, chnl_nm, fin, chnl_type, chnl_sub_nm)
# ---------------------------------------------------------------------------
CHANNELS = [
    ("F01", "中信银行", "S0101", "银行App", "CH0101", "中信银行App直注", "1", "APP", "中信银行"),
    ("F01", "中信银行", "S0101", "银行App", "CH0103", "银行出账单页嵌入口", "1", "APP", "中信银行"),
    ("F01", "中信银行", "S0102", "信用卡中心", "CH0102", "信用卡中心公众号", "1", "公众号", "中信银行"),
    ("F02", "中信证券", "S0201", "证券App", "CH0201", "中信证券App直注", "1", "APP", "中信证券"),
    ("F02", "中信证券", "S0202", "证券营业部", "CH0202", "营业部扫码开户", "1", "门店", "中信证券"),
    ("F03", "中信优享+", "S0301", "优享+线上", "CH0301", "中信优享+公众号", "1", "公众号", "中信优享+"),
    ("F03", "中信优享+", "S0301", "优享+线上", "CH0303", "中信优享+小程序", "1", "小程序", "中信优享+"),
    ("F03", "中信优享+", "S0301", "优享+线上", "CH0304", "优享+短信直达", "1", "短信", "中信优享+"),
    ("F03", "中信优享+", "S0302", "优享+企微", "CH0302", "中信优享+企微", "1", "企微", "中信优享+"),
    ("F04", "合作商圈", "S0401", "麦当劳", "CH0401", "麦当劳门店码", "0", "门店码", "麦当劳"),
    ("F04", "合作商圈", "S0401", "麦当劳", "CH0402", "麦当劳App联登", "0", "APP", "麦当劳"),
    ("F04", "合作商圈", "S0402", "商圈其他", "CH0403", "商圈异业联登", "0", "联登", "合作商圈"),
    ("F05", "内容生态", "S0501", "中信书院", "CH0501", "中信书院公众号", "0", "公众号", "中信书院"),
    ("F05", "内容生态", "S0501", "中信书院", "CH0502", "中信书院App", "0", "APP", "中信书院"),
    ("F05", "内容生态", "S0502", "书店门店", "CH0503", "书店门店码", "0", "门店码", "中信书院"),
]
BY_CHNL = {c[4]: c for c in CHANNELS}
FIN_LEAF_IDS = [c[4] for c in CHANNELS if c[6] == "1"]
MCD_LEAF_IDS = ["CH0401", "CH0402"]
BOOK_LEAF_IDS = ["CH0501", "CH0502"]

# Corner-case fixed user ids
BAD_USERS = ["U1398", "U1399", "U1400"]                       # a) 渠道码不在维表 (cohort A)
PERSON_ACCOUNTS = {  # b) 一人多账号 (cohort B): 同手机号, 同日注册
    "P001": {"accs": ["U1401", "U1402"], "brand": "麦当劳", "phone": "13700000001"},
    "P002": {"accs": ["U1403", "U1404"], "brand": "中信书院", "phone": "13700000002"},
}
SAME_DAY_USERS = ["U1405", "U1406", "U1407", "U1408", "U1409"]  # c) 同日注册+激活
DUP_ACT_USERS = [f"U{i}" for i in range(1410, 1420)]          # 重复激活 10 例
SAME_DT_TAG_USERS = DUP_ACT_USERS[:2]  # 额外激活行同日、tag 相反 -> 验 row_number 决胜


def ts(d: date) -> datetime:
    return datetime.combine(d, time(0, 0))


def _lit(v) -> str:
    """Render a python value as a safe SQL literal (internal mock data only)."""
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    if isinstance(v, datetime):
        return "'" + v.strftime("%Y-%m-%d %H:%M:%S") + "'"
    if isinstance(v, date):
        return "'" + v.isoformat() + "'"
    return str(v)


def bulk_insert(con: duckdb.DuckDBPyConnection, insert_sql: str, rows: list, chunk: int = 1000) -> None:
    """Chunked multi-row VALUES insert. (duckdb executemany is ~5ms/row on wide
    tables -> 62k rows would take ~5min; inlined literals run the same data in ~2s.)"""
    prefix = insert_sql.rstrip()
    if prefix.endswith("VALUES ("):
        prefix = prefix[:-1].rstrip()
    if not prefix.endswith("VALUES"):
        raise ValueError("insert_sql must end with 'VALUES ('")
    for i in range(0, len(rows), chunk):
        part = rows[i:i + chunk]
        stmt = prefix + ",".join("(" + ",".join(_lit(v) for v in r) + ")" for r in part)
        con.execute(stmt)


def main() -> None:
    rng = random.Random(SEED)
    con = duckdb.connect(str(DB_PATH))
    days = [START + timedelta(days=i) for i in range(N_DAYS)]
    day_strs = [d.isoformat() for d in days]

    # ---------------- wipe (rerunnable) ----------------
    for t in ("cdm.dim_ch_chl_df", "cdm.dim_pb_date_yf", "cdm.dim_cu_usr_info_df",
              "cdm.dwd_cu_actv_df", "cdm.dwd_cu_rgst_fin_di", "rec.ads_rgst_chnl_cnt_df"):
        con.execute(f"DELETE FROM {t}")

    # ---------------- 1. channel dim (daily full snapshots) ----------------
    chnl_rows = [(c[4], c[5], "1", "mock", c[4], c[5], c[2], c[3], c[0], c[1], "L4",
                  c[6], day_strs[0], c[7], c[8], ts(d)) for d in days for c in CHANNELS]
    bulk_insert(
        con,
        "INSERT INTO cdm.dim_ch_chl_df (chnl_id, chnl_nm, chnl_stat, chnl_dc, "
        "thd_chnl_id, thd_chnl_nm, sec_chnl_id, sec_chnl_nm, fst_chnl_id, fst_chnl_nm, "
        "chnl_lvl, fin_chnl_flg, chnl_effect_dt, chnl_type, chnl_sub_nm, ds) VALUES (",
        chnl_rows,
    )
    print(f"dim_ch_chl_df: {len(chnl_rows)} rows (15 channels x {N_DAYS} snapshots)")

    # ---------------- 2. date dim ----------------
    date_rows = []
    for d in days:
        mth_begin = d.replace(day=1)
        nxt_mth = (mth_begin + timedelta(days=32)).replace(day=1)
        prv_mth_begin = (mth_begin - timedelta(days=1)).replace(day=1)
        quar_begin = date(d.year, ((d.month - 1) // 3) * 3 + 1, 1)
        date_rows.append((
            ts(d), d.strftime("%Y-%m"), str(d.year), f"{d.year}Q{(d.month - 1) // 3 + 1}",
            d.strftime("%m"), d.strftime("%m"), d.strftime("%b"), d.strftime("%d"),
            str((d.weekday() + 1) % 7 + 1), f"星期{'一二三四五六日'[d.weekday()]}", d.strftime("%A"),
            1 if d.weekday() < 5 else 0, 1 if d.weekday() >= 5 else 0, 0,
            d.isocalendar()[1], d.day, d.timetuple().tm_yday, (d - quar_begin).days + 1,
            None, None, ts(d - timedelta(days=1)), ts(d + timedelta(days=1)),
            ts(mth_begin), ts(nxt_mth - timedelta(days=1)),
            ts(prv_mth_begin), ts(mth_begin - timedelta(days=1)),
            ts(quar_begin), None, None, ts(date(d.year, 1, 1)), ts(date(d.year, 12, 31)),
            ts(d - timedelta(days=2)), ts(d - timedelta(days=6)), ts(d - timedelta(days=14)),
            ts(d - timedelta(days=29)), ts(d - timedelta(days=59)), None, datetime.now(),
        ))
    bulk_insert(
        con,
        "INSERT INTO cdm.dim_pb_date_yf (date_dt, cur_year_mth, cur_year, cur_quarter, cur_mth, "
        "cur_mth_cn, cur_mth_en, cur_dt, cur_week, cur_week_cn, cur_week_en, workday_ind, "
        "week_end_ind, holiday_ind, week_of_year, day_of_month, day_of_year, day_of_quarter, "
        "last_month_dt, last_year_dt, last_dt, next_dt, cur_mth_begin, cur_mth_end, "
        "last_mth_begin, last_mth_end, quar_begin, quar_end, half_year_begin, year_begin, "
        "year_end, last_3_dt, last_7_dt, last_15_dt, last_30_dt, last_60_dt, last_90_dt, etl_time) "
        "VALUES (",
        date_rows,
    )
    print(f"dim_pb_date_yf: {len(date_rows)} rows ({day_strs[0]}..{day_strs[-1]})")

    # ---------------- 3. users + daily snapshots ----------------
    fin_users = [f"U{i:04d}" for i in range(1, 1398)]    # 1397 金融直注
    bad_reg = {u: f"CHN_BAD_{i + 1:02d}" for i, u in enumerate(BAD_USERS)}
    cohort_b = [f"U{i:04d}" for i in range(1401, 2001)]  # 600 麦当劳/中信书院
    brand = {u: "麦当劳" if i % 2 == 0 else "中信书院" for i, u in enumerate(cohort_b)}
    for spec in PERSON_ACCOUNTS.values():
        for u in spec["accs"]:
            brand[u] = spec["brand"]

    reg_day, reg_tm, leaf, phone, enjy, rtype, act_id = {}, {}, {}, {}, {}, {}, {}
    for i, u in enumerate(fin_users + BAD_USERS):
        reg_day[u] = days[rng.randrange(N_DAYS)]
        reg_tm[u] = f"{rng.randrange(6, 23):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
        phone[u] = f"139{i + 1:08d}"
        if u in bad_reg:
            leaf[u], enjy[u], rtype[u] = bad_reg[u], "0", "1"
        else:
            leaf[u] = rng.choice(FIN_LEAF_IDS)
            enjy[u] = rng.choice(("0", "1", "1"))
            rtype[u] = rng.choice(("1", "1", "1", "0"))
        act_id[u] = f"ACT{i % 7:03d}" if rng.random() < 0.2 else ""
    for j, u in enumerate(cohort_b):
        reg_day[u] = days[rng.randrange(N_DAYS)]
        reg_tm[u] = f"{rng.randrange(6, 23):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
        leaf[u] = rng.choice(MCD_LEAF_IDS if brand[u] == "麦当劳" else BOOK_LEAF_IDS)
        phone[u] = f"138{j + 1:08d}"
        enjy[u] = rng.choice(("0", "1"))
        rtype[u] = "1"
        act_id[u] = ""
    # b) 一人多账号: 同手机号、同日注册
    for spec in PERSON_ACCOUNTS.values():
        shared_day = days[rng.randrange(N_DAYS - 7)]
        for u in spec["accs"]:
            reg_day[u] = shared_day
            phone[u] = spec["phone"]
            leaf[u] = rng.choice(MCD_LEAF_IDS if brand[u] == "麦当劳" else BOOK_LEAF_IDS)

    # activations: 60% of cohort B; forced roles first, rest random
    forced = [PERSON_ACCOUNTS["P001"]["accs"][0], PERSON_ACCOUNTS["P001"]["accs"][1],
              PERSON_ACCOUNTS["P002"]["accs"][0]]
    pool = [u for u in cohort_b
            if u not in forced and u not in SAME_DAY_USERS and u not in DUP_ACT_USERS]
    rest_n = N_ACTIVATED - len(forced) - len(SAME_DAY_USERS) - len(DUP_ACT_USERS)
    activated = set(forced + SAME_DAY_USERS + DUP_ACT_USERS + rng.sample(pool, rest_n))
    assert len(activated) == N_ACTIVATED, f"activated={len(activated)} != {N_ACTIVATED}"
    actv_rows = []
    actv_meta = {}
    for u in sorted(activated):
        a_day = reg_day[u] if u in SAME_DAY_USERS else min(reg_day[u] + timedelta(days=rng.randint(1, 20)), END)
        a_tm = f"{rng.randrange(7, 22):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
        tag = 2 if rng.random() < 0.25 else 1
        actv_meta[u] = (a_day, a_tm, tag)
        actv_rows.append((u, ts(a_day), ts(a_day) + timedelta(seconds=1), leaf[u],
                          BY_CHNL[leaf[u]][5], BY_CHNL[leaf[u]][2], brand[u], BY_CHNL[leaf[u]][8],
                          tag, ts(a_day) + timedelta(seconds=1), ts(reg_day[u]), brand[u], 1, ts(a_day)))
    for u in DUP_ACT_USERS:  # 重复激活 -> row_number 去重素材
        a_day, _a_tm, tag = actv_meta[u]
        if u in SAME_DT_TAG_USERS:
            extra_day, extra_tag = a_day, 2 if tag == 1 else 1  # 同日反向 tag, 验决胜
        else:
            extra_day, extra_tag = min(a_day + timedelta(days=rng.randint(1, 3)), END), tag
        actv_rows.append((u, ts(extra_day), ts(extra_day) + timedelta(seconds=2), leaf[u],
                          BY_CHNL[leaf[u]][5], BY_CHNL[leaf[u]][2], brand[u], BY_CHNL[leaf[u]][8],
                          extra_tag, ts(extra_day) + timedelta(seconds=2), ts(reg_day[u]), brand[u], 1, ts(extra_day)))
    bulk_insert(
        con,
        "INSERT INTO cdm.dwd_cu_actv_df (usr_id, actv_dt, actv_tm, actv_chnl_id, actv_chnl_nm, "
        "actv_sec_chnl_id, actv_sec_chnl_nm, actv_chnl_sub_nm, actv_tag, actv_date_src, "
        "rgst_dt, rgst_sec_chnl_nm, rgst_enjy_fg, ds) VALUES (",
        actv_rows,
    )
    print(f"dwd_cu_actv_df: {len(actv_rows)} rows ({len(activated)} activated users, "
          f"{len(DUP_ACT_USERS)} with a duplicate activation row)")

    snap = []
    for d in days:
        for u in (fin_users + BAD_USERS + cohort_b):
            if reg_day[u] > d:
                continue
            if u in bad_reg:
                fst_id, fst_nm, sec_id, sec_nm = "F_BAD", "幽灵渠道", "S_BAD", "幽灵渠道"
                ch_nm = "未知渠道"
            else:
                c = BY_CHNL[leaf[u]]
                fst_id, fst_nm, sec_id, sec_nm, ch_nm = c[0], c[1], c[2], c[3], c[5]
            snap.append((u, reg_day[u].isoformat(), f"{reg_day[u].isoformat()} {reg_tm[u]}",
                         "1", enjy[u], rtype[u], "1", fst_id, fst_nm, sec_id, sec_nm,
                         leaf[u], ch_nm, leaf[u], ch_nm, act_id[u], "1", phone[u], ts(d)))
    bulk_insert(
        con,
        "INSERT INTO cdm.dim_cu_usr_info_df (usr_id, rgst_dt, rgst_tm, usr_stat_fg, rgst_enjy_fg, "
        "rgst_type, rgst_fin_chnl_ind, rgst_fst_chnl_id, rgst_fst_chnl_nm, rgst_sec_chnl_id, "
        "rgst_sec_chnl_nm, rgst_thd_chnl_id, rgst_thd_chnl_nm, rgst_chnl_id, rgst_chnl_nm, "
        "rgst_act_id, real_fg, usr_phone_erpt, ds) VALUES (",
        snap,
    )
    print(f"dim_cu_usr_info_df: {len(snap)} rows ({N_USERS} users, daily full snapshots)")

    # ------------- 4+5. rgst_fin_di & ADS via the ORIGINAL warehouse SQL -------------
    fin_tpl = ETL_FIN_SQL.read_text(encoding="utf-8")
    ads_tpl = ETL_ADS_SQL.read_text(encoding="utf-8")
    for ds in day_strs:
        con.execute(fin_tpl.replace(DATA_DS, ds))
        con.execute(ads_tpl.replace(DATA_DS, ds))
    print(f"dwd_cu_rgst_fin_di + rec.ads_rgst_chnl_cnt_df: original warehouse SQL executed "
          f"per day for all {N_DAYS} days (only {DATA_DS} substituted)")

    # ================= acceptance evidence =================
    print("\n" + "=" * 28 + " 验收 1: 自洽对账 (明细重算 vs ADS) " + "=" * 28)
    sel = ads_tpl.split("insert into rec.ads_rgst_chnl_cnt_df", 1)[1].split(";", 1)[0].strip()
    con.execute("CREATE OR REPLACE TEMP TABLE ads_recalc AS "
                "SELECT * FROM rec.ads_rgst_chnl_cnt_df WHERE 1 = 0")
    for ds in day_strs:
        con.execute("INSERT INTO ads_recalc " + sel.replace(DATA_DS, ds))
    n_stored, n_recalc = con.execute(
        "SELECT (SELECT count(*) FROM rec.ads_rgst_chnl_cnt_df), (SELECT count(*) FROM ads_recalc)"
    ).fetchone()
    diff_both = con.execute(
        "SELECT count(*) FROM ((SELECT * FROM rec.ads_rgst_chnl_cnt_df EXCEPT SELECT * FROM ads_recalc) "
        "UNION ALL (SELECT * FROM ads_recalc EXCEPT SELECT * FROM rec.ads_rgst_chnl_cnt_df))"
    ).fetchone()[0]
    ok = diff_both == 0 and n_stored == n_recalc
    print(f"stored ADS rows = {n_stored}, recomputed-from-detail rows = {n_recalc}")
    print(f"双向 EXCEPT 差集 = {diff_both} 行 (期望 0) -> 逐格相等: {'PASS' if ok else 'FAIL'}")
    sums = con.execute(
        "SELECT sum(new_rgst_cnt_d), sum(new_rgst_cnt_7d), sum(new_rgst_cnt_m), "
        f"sum(new_rgst_cnt_y), sum(new_rgst_cnt_a) FROM rec.ads_rgst_chnl_cnt_df WHERE ds = '{day_strs[-1]}'"
    ).fetchone()
    print(f"末日分区 {day_strs[-1]} 五口径合计 D/7D/M/Y/A = {sums}")

    print("\n" + "=" * 28 + " 验收 2: corner case (null 渠道组) " + "=" * 28)
    null_rows, null_a, tot_a, chan_a = con.execute(
        "WITH f AS (SELECT * FROM rec.ads_rgst_chnl_cnt_df WHERE ds = ?) "
        "SELECT (SELECT count(*) FROM f WHERE fst_lvl_chnl_id IS NULL), "
        "(SELECT COALESCE(sum(new_rgst_cnt_a), 0) FROM f WHERE fst_lvl_chnl_id IS NULL), "
        "(SELECT COALESCE(sum(new_rgst_cnt_a), 0) FROM f), "
        "(SELECT COALESCE(sum(new_rgst_cnt_a), 0) FROM f WHERE fst_lvl_chnl_id IS NOT NULL)",
        [ts(END)],
    ).fetchone()
    bad_detail = con.execute(
        "SELECT count(*) FROM cdm.dwd_cu_rgst_fin_di WHERE rgst_chnl_id LIKE 'CHN_BAD%'"
    ).fetchone()[0]
    print(f"末日分区 null 渠道组: {null_rows} 行, 其历史累计 = {null_a} (坏码明细行 = {bad_detail})")
    print(f"Σ分渠道(非空) = {chan_a}  vs  Σ全部 = {tot_a}  ->  差值 = {tot_a - chan_a}")
    print("(预期异常: 3 条无维表渠道码 left join 落 null 组, 不可归因到 15 渠道; 若接 I1 拦截应报警)")

    print("\n" + "=" * 28 + " 验收 3: I2 去重键检查 " + "=" * 28)
    d_rows, d_usr = con.execute(
        "SELECT count(*), count(DISTINCT usr_id) FROM cdm.dwd_cu_rgst_fin_di"
    ).fetchone()
    print(f"dwd_cu_rgst_fin_di: COUNT(*) = {d_rows}, COUNT(DISTINCT usr_id) = {d_usr}, 差异 = {d_rows - d_usr}")
    print("  (同一 usr_id 至多一段A+一段B; 本 mock 按方案两群互斥: 金融直注不激活、麦当劳/中信注册者才激活, 故 usr_id 粒度无重叠)")
    u_rows, u_phone = con.execute(
        "SELECT count(*), count(DISTINCT usr_phone_erpt) FROM cdm.dim_cu_usr_info_df WHERE ds = ?",
        [ts(END)],
    ).fetchone()
    print(f"末日用户维快照: COUNT(*) = {u_rows}, COUNT(DISTINCT usr_phone_erpt) = {u_phone}, 差异 = {u_rows - u_phone}")
    print("  (一人多账号 2 例: P001=U1401/U1402 麦当劳, P002=U1403/U1404 中信书院, 各自同手机号)")
    a_rows, a_usr = con.execute(
        "SELECT count(*), count(DISTINCT usr_id) FROM cdm.dwd_cu_actv_df"
    ).fetchone()
    b_rows = con.execute("SELECT count(*) FROM cdm.dwd_cu_rgst_fin_di WHERE if_act = 1").fetchone()[0]
    print(f"激活明细: COUNT(*) = {a_rows}, DISTINCT usr_id = {a_usr}, 差异 = {a_rows - a_usr}")
    print(f"  (重复激活 {len(DUP_ACT_USERS)} 例被真实 ETL 的 row_number 去重 -> 段B行 = {b_rows} = 去重后激活用户数)")
    same_day = con.execute(
        "SELECT count(*) FROM cdm.dwd_cu_rgst_fin_di "
        "WHERE if_act = 1 AND CAST(nonfin_rgst_dt AS TIMESTAMP) = rgst_dt_src",
    ).fetchone()[0]
    print(f"同日注册+激活段B行 (原始注册日 nonfin_rgst_dt = 激活日 rgst_dt_src): {same_day} 例 "
          f"(埋点 {len(SAME_DAY_USERS)} + 激活偏移被窗口截断的自然边界值)")

    print("\n" + "=" * 28 + " 表行数清单 " + "=" * 28)
    for t in ("cdm.dim_ch_chl_df", "cdm.dim_pb_date_yf", "cdm.dim_cu_usr_info_df",
              "cdm.dwd_cu_actv_df", "cdm.dwd_cu_rgst_fin_di", "rec.ads_rgst_chnl_cnt_df"):
        (n,) = con.execute(f"SELECT count(*) FROM {t}").fetchone()
        print(f"{t:<28}{n:>9}")
    seg_a, seg_b = con.execute(
        "SELECT count(*) FILTER (WHERE if_act = 0), count(*) FILTER (WHERE if_act = 1) "
        "FROM cdm.dwd_cu_rgst_fin_di"
    ).fetchone()
    chnl_hits = con.execute(
        "SELECT count(DISTINCT rgst_chnl_id) FROM cdm.dwd_cu_rgst_fin_di "
        f"WHERE rgst_chnl_id IN {tuple(BY_CHNL)}"
    ).fetchone()[0]
    print(f"\n段A(金融直注) = {seg_a}, 段B(激活) = {seg_b}, 合计 = {seg_a + seg_b}; "
          f"命中维表 leaf 渠道数 = {chnl_hits}/15 (CH0403 商圈异业联登 / CH0503 书店门店码 "
          f"按设计未分配注册用户, 仍存在于渠道维)")
    con.close()
    print("\nDONE")


if __name__ == "__main__":
    main()
