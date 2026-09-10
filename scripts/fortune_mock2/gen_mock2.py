#!/usr/bin/env python
"""Fortune Plaza mock phase 2: real-name / channel-auth / conversion chain.

Extends scripts/fortune_mock/gen_mock.py (phase 1, core 6 tables). Same method:
run the ORIGINAL warehouse ETL SQL verbatim per day (2026-07-01..2026-08-31),
substituting ONLY the ${data_ds} schedule placeholder.

New upstream mock tables (invented distributions, labelled):
  ods.ods_usms_lm_user_t_df           user agreement-sign snapshot, 2000 users x 62 days
  ods.ods_usms_lm_channel_user_t_df   channel-user relation + grant snapshot, ~2500 rels x 62 days
  cdm.dwd_lm_pv_df                    $pageview events (~2600 rows), ds = event day

Phase-1 table touched (declared exception; registration columns + all other
columns untouched except the six real-name columns and usr_sex below):
  cdm.dim_cu_usr_info_df  real_fg / real_dt / real_tm / real_way / real_type /
  real_chnl_id filled per user, snapshot-aware (real_fg=1 only on/after real_dt);
  usr_sex filled M/F/NULL ~ 48/47/5 for realism (gender dimension was registered
  with no data). Phase-1 had real_fg='1' for everyone with real_dt NULL (dead
  placeholder at the time); the real-name chain needs it. Users / registration
  values unchanged.

5 target tables replayed from the real scripts:
  cdm.dwd_cu_real_df, cdm.dwd_ch_usr_rltv_df,
  rec.ads_chnl_real_user_df, rec.ads_chnl_auth_qty_df, rec.ads_chnl_rltv_chnl_df,
  rec.ads_chnl_rgst_to_real_auth_dau_df
  Engine adaptations on the conversion script (business semantics unchanged,
  declared): GaussDB storage clauses "WITH (...) DISTRIBUTE BY HASH (usr_id)"
  of its LOCAL TEMPORARY mid table are stripped, and two TIMESTAMP-vs-VARCHAR
  comparisons get explicit CASTs (GaussDB casts implicitly, DuckDB refuses).

Mock assumptions (made up, plausible):
  real-name rate by channel group: F01 bank 70% / F02 securities 68% /
    F03 youxiang 62% / F04 mall 40% / F05 content 45%, bad-code users 1/3
    -> overall ~59% (~60%)
  grant rate per relation: bank 55% / securities 50% / youxiang 45% /
    mall 25% / content 30%; cross-channel 2nd relation fixed 30% -> overall ~40%
  usr_sex: M 48% / F 47% / NULL 5%
  $pageview: 80% finance-group / 70% mall-book users, 1-3 distinct days after
    registration

DuckDB is single-writer: readers may hold the file, so connect and every write
retry on a lock error (sleep 5s, max 5 tries). Phase-1 chain data untouched.

cdm.dim_ch_chl_df receives APPENDED rows only (13 CITIC relay channels x 62
snapshots, ids CH9001..CH9013, required by the relay ETL's hard-coded name
list); phase-1 rows are never modified, and acceptance proves the phase-1 ADS
rec.ads_rgst_chnl_cnt_df recomputes bit-identical from the untouched detail.

Rerunnable: wipes the 3 new upstream tables + 5 target tables first.
Usage: .venv/bin/python scripts/fortune_mock2/gen_mock2.py
"""

from __future__ import annotations

import random
import re
import time
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[2]
ETL_DIR = REPO / "materials" / "fortune-warehouse-input" / "2026-09-10-数仓ddl及脚本" / "01_财富管理脚本"
ETL = {
    "dwd_cu_real_df": ETL_DIR / "CDM层" / "用户域CU" / "脚本dwd_cu_real_df.sql",
    "dwd_ch_usr_rltv_df": ETL_DIR / "CDM层" / "渠道域CH" / "dwd_ch_usr_rltv_df.sql",
    "ads_chnl_real_user_df": ETL_DIR / "ADS层" / "核心指标" / "注册" / "脚本ads_chnl_real_user_df.sql",
    "ads_chnl_auth_qty_df": ETL_DIR / "ADS层" / "核心指标" / "授权" / "脚本ads_chnl_auth_qty_df.sql",
    "ads_chnl_rltv_chnl_df": ETL_DIR / "ADS层" / "核心指标" / "授权" / "脚本ads_chnl_rltv_chnl_df.sql",
    "ads_chnl_rgst_to_real_auth_dau_df": ETL_DIR / "ADS层" / "核心指标" / "综合" / "脚本ads_chnl_rgst_to_real_auth_dau_df.sql",
}
DB_PATH = REPO / "data" / "fortune_mirror.duckdb"

SEED = 20260912
START = date(2026, 7, 1)
N_DAYS = 62
END = START + timedelta(days=N_DAYS - 1)  # 2026-08-31
DAY_DS = "${data_ds}"
MID_TBL = "ads_chnl_rgst_to_real_auth_dau_df_mid_01"

# channel-group -> (real-name rate, grant rate); keyed by first-level channel id
RATE = {"F01": 0.70, "F02": 0.68, "F03": 0.62, "F04": 0.40, "F05": 0.45}
GRANT = {"F01": 0.55, "F02": 0.50, "F03": 0.45, "F04": 0.25, "F05": 0.30}
CROSS_GRANT = 0.30          # 2nd (cross-channel) relation grant rate
P_SECOND_REL = 0.25         # share of users having a 2nd relation
REAL_WAY = [("1", 0.60), ("2", 0.30), ("3", 0.10)]  # 1 face / 2 card-4 / 3 counter
BAD_REAL = 1 / 3            # 3 phase-1 bad-code users: ~1 of them real-named
PV_P = {"fin": 0.80, "seg_b": 0.70}
PV_DAYS = [(1, 0.5), (2, 0.3), (3, 0.2)]  # distinct active days per active user
USR_STATUS = [("0", 0.96), ("1", 0.03), ("2", 0.01)]
SEX = [("M", 0.48), ("F", 0.47), (None, 0.05)]  # NULL kept for realism

# 13 CITIC-group relay channels: ads_chnl_rltv_chnl_df hard-codes these sec
# names, and dwd_ch_usr_rltv_df joins dim_ch_chl_df on Chnl_Id, so the channel
# dim MUST contain them for the relay metrics to be non-empty. Phase 1 built
# only the 15 acquisition leaves (sec names are media forms, not CITIC names).
# We APPEND these (never touching phase-1 rows) and prove the phase-1 ADS is
# bit-identical afterwards. (chnl_id, sec_chnl_nm = CITIC entity, grant rate)
RELAY_CHNLS = [
    ("CH9001", "中信银行信用卡", 0.52), ("CH9002", "中信银行", 0.55),
    ("CH9003", "中信建投证券", 0.48), ("CH9004", "中信证券", 0.50),
    ("CH9005", "中信消费金融", 0.45), ("CH9006", "百信银行", 0.42),
    ("CH9007", "中信保诚人寿", 0.38), ("CH9008", "华夏基金", 0.35),
    ("CH9009", "中信建投期货", 0.33), ("CH9010", "中信期货", 0.35),
    ("CH9011", "中信信托", 0.30), ("CH9012", "信银理财", 0.40),
    ("CH9013", "中信优享+公众号", 0.25),
]
P_RELAY_MAIN = 0.70  # main relation lands on a CITIC relay channel (real-world shape)


def ts(d, hms="00:00:00"):
    return datetime.combine(d, dtime.fromisoformat(hms))


def _lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    if isinstance(v, datetime):
        return "'" + v.strftime("%Y-%m-%d %H:%M:%S") + "'"
    if isinstance(v, date):
        return "'" + v.isoformat() + "'"
    return str(v)


def bulk_insert(exec_fn, prefix_sql, rows, chunk=1000):
    prefix = prefix_sql.rstrip()
    if prefix.endswith("("):
        prefix = prefix[:-1].rstrip()  # 'VALUES (' -> 'VALUES'; rows carry their own parens
    for i in range(0, len(rows), chunk):
        stmt = prefix + " " + ",".join(
            "(" + ",".join(_lit(v) for v in r) + ")" for r in rows[i:i + chunk])
        exec_fn(stmt)


def connect_retry(path, tries=5):
    for i in range(tries):
        try:
            return duckdb.connect(str(path))
        except duckdb.IOException as e:
            if "lock" not in str(e).lower() or i == tries - 1:
                raise
            print(f"[lock] connect blocked by another process, retry {i + 1}/{tries} in 5s")
            time.sleep(5)
    raise RuntimeError("unreachable")


def exec_retry(con, sql, tries=5):
    for i in range(tries):
        try:
            return con.execute(sql)
        except duckdb.IOException as e:
            if "lock" not in str(e).lower() or i == tries - 1:
                raise
            print(f"[lock] write blocked by another process, retry {i + 1}/{tries} in 5s")
            time.sleep(5)
    raise RuntimeError("unreachable")


# GaussDB -> DuckDB engine adaptations on the conversion script (business
# semantics unchanged; all three declared):
#   1. strip the physical storage clauses "WITH (...) DISTRIBUTE BY HASH (usr_id)"
#   2. 't1.rgst_dt <= t2.evt_trig_dt': GaussDB compares TIMESTAMP with VARCHAR
#      implicitly; DuckDB needs an explicit CAST.
#   3. 'rgst_dt >= cur_mth_begin' (mid col rgst_dt DATE vs cur_mth_begin
#      VARCHAR(128)): same implicit cast, made explicit.
GAUSS_TAIL = re.compile(
    r"\s*WITH\s*\([^)]*\)\s*DISTRIBUTE BY HASH\s*\([^)]*\)", re.I | re.S)


def gauss_to_duckdb(tpl: str) -> str:
    sql = GAUSS_TAIL.sub("", tpl)
    assert "t1.rgst_dt <= t2.evt_trig_dt" in sql and sql.count("rgst_dt >= cur_mth_begin") == 2
    sql = sql.replace("t1.rgst_dt <= t2.evt_trig_dt",
                      "t1.rgst_dt <= CAST(t2.evt_trig_dt AS TIMESTAMP)")
    sql = sql.replace("rgst_dt >= cur_mth_begin",
                      "rgst_dt >= CAST(cur_mth_begin AS DATE)")
    return sql


def weighted(rng, pairs):
    x, acc = rng.random(), 0.0
    for v, p in pairs:
        acc += p
        if x < acc:
            return v
    return pairs[-1][0]


def main():
    rng = random.Random(SEED)
    con = connect_retry(DB_PATH)
    ex = lambda sql: exec_retry(con, sql)
    days = [START + timedelta(days=i) for i in range(N_DAYS)]
    day_strs = [d.isoformat() for d in days]

    # ---------- read phase-1 facts (users & channel dim are REUSED, not rebuilt) ----------
    users = ex(
        "SELECT usr_id, CAST(rgst_dt AS DATE), rgst_chnl_id, rgst_tm "
        "FROM cdm.dim_cu_usr_info_df WHERE ds = (SELECT max(ds) FROM cdm.dim_cu_usr_info_df)"
    ).fetchall()
    assert len(users) == 2000, f"expected 2000 phase-1 users, got {len(users)}"
    leaves = ex(
        "SELECT chnl_id, fst_chnl_id, fst_chnl_nm, sec_chnl_id, sec_chnl_nm, chnl_sub_nm "
        "FROM cdm.dim_ch_chl_df WHERE ds = (SELECT max(ds) FROM cdm.dim_ch_chl_df)"
    ).fetchall()
    leaf_by_id = {r[0]: r for r in leaves}
    fin_leaves = [r[0] for r in leaves if r[1] in ("F01", "F02", "F03")]

    # append 13 CITIC relay channels x 62 daily snapshots (phase-1 rows untouched)
    relay_rows = []
    for d in days:
        for cid, nm, _g in RELAY_CHNLS:
            relay_rows.append((cid, nm + "关联渠道", "1", "mock", cid, nm, cid, nm,
                               "FG9", "中信集团", "L4", "1", day_strs[0], "API", nm, ts(d)))
    bulk_insert(ex, "INSERT INTO cdm.dim_ch_chl_df (chnl_id, chnl_nm, chnl_stat, chnl_dc, "
                    "thd_chnl_id, thd_chnl_nm, sec_chnl_id, sec_chnl_nm, fst_chnl_id, fst_chnl_nm, "
                    "chnl_lvl, fin_chnl_flg, chnl_effect_dt, chnl_type, chnl_sub_nm, ds) VALUES (",
                relay_rows)
    for cid, nm, _g in RELAY_CHNLS:
        leaf_by_id[cid] = (cid, "FG9", "中信集团", cid, nm, nm)
    relay_ids = [c[0] for c in RELAY_CHNLS]
    relay_grant = {c[0]: c[2] for c in RELAY_CHNLS}

    # ---------- 0. wipe rerunnable scope (phase-1 tables NOT wiped) ----------
    for t in ("rec.ads_chnl_rgst_to_real_auth_dau_df", "rec.ads_chnl_rltv_chnl_df",
              "rec.ads_chnl_auth_qty_df", "rec.ads_chnl_real_user_df",
              "cdm.dwd_ch_usr_rltv_df", "cdm.dwd_cu_real_df",
              "cdm.dwd_lm_pv_df", "ods.ods_usms_lm_channel_user_t_df",
              "ods.ods_usms_lm_user_t_df"):
        ex(f"DELETE FROM {t}")

    # ---------- 1. real-name + sex attributes on dim_cu_usr_info_df (declared update) ----
    usr_real = {}  # usr_id -> (real_dt_str|None, real_tm, real_way, real_type, real_chnl_id, sex)
    for u, rgst_d, chnl, _tm in users:
        leaf = leaf_by_id.get(chnl)
        p = RATE[leaf[1]] if leaf else BAD_REAL
        if rng.random() >= p:
            real = (None, None, None, None, None)
        else:
            rday = min(rgst_d + timedelta(days=rng.randint(0, 30)), END)
            rtm = f"{rng.randrange(8, 22):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
            real_chnl = chnl if (leaf and rng.random() < 0.85) else rng.choice(fin_leaves)
            real = (f"{rday.isoformat()} {rtm}", f"{rday.isoformat()} {rtm}",
                    weighted(rng, REAL_WAY), "1", real_chnl)  # real_tm: full timestamp like rgst_tm
        usr_real[u] = real + (weighted(rng, SEX),)
    ex("CREATE OR REPLACE TEMP TABLE _usr_real (usr_id VARCHAR, real_dt VARCHAR, "
       "real_tm VARCHAR, real_way VARCHAR, real_type VARCHAR, real_chnl_id VARCHAR, "
       "sex VARCHAR)")
    bulk_insert(ex, "INSERT INTO _usr_real VALUES (",
                [(u,) + v for u, v in usr_real.items()])
    ex("UPDATE cdm.dim_cu_usr_info_df d SET "
       "real_fg = CASE WHEN r.real_dt IS NOT NULL "
       "           AND CAST(r.real_dt AS DATE) <= CAST(d.ds AS DATE) THEN '1' ELSE '0' END, "
       "real_dt = r.real_dt, real_tm = r.real_tm, real_way = r.real_way, "
       "real_type = r.real_type, real_chnl_id = r.real_chnl_id, usr_sex = r.sex "
       "FROM _usr_real r WHERE d.usr_id = r.usr_id")
    max_ds = ex("SELECT max(ds) FROM cdm.dim_cu_usr_info_df").fetchone()[0].date().isoformat()
    real_end, sex_m, sex_f, sex_n = ex(
        "SELECT count(*) FILTER (WHERE real_fg = '1'), count(*) FILTER (WHERE usr_sex = 'M'), "
        "count(*) FILTER (WHERE usr_sex = 'F'), count(*) FILTER (WHERE usr_sex IS NULL) "
        f"FROM cdm.dim_cu_usr_info_df WHERE ds = (SELECT max(ds) FROM cdm.dim_cu_usr_info_df)"
    ).fetchone()
    print(f"dim_cu_usr_info_df updated: real-named {real_end}/2000 at {max_ds} "
          f"({real_end / 20:.1f}%); usr_sex M/F/NULL = {sex_m}/{sex_f}/{sex_n}")

    # ---------- 2. ods.ods_usms_lm_user_t_df (62 daily snapshots) ----------
    rows = []
    for d in days:
        for u, rgst_d, chnl, rgst_tm in users:
            hms = (rgst_tm or "00:00:00").split(" ")[-1][:8]  # 'YYYY-MM-DD HH:MM:SS' -> 'HH:MM:SS'
            rows.append((u, ts(rgst_d, hms), ts(rgst_d, hms),
                         chnl if chnl in leaf_by_id else "CH0101", ts(d)))
    bulk_insert(ex, "INSERT INTO ods.ods_usms_lm_user_t_df "
                    "(uid, create_time, agreement_sign_time, agreement_sign_channel, ds) VALUES (",
                rows)
    print(f"ods_usms_lm_user_t_df: {len(rows)} rows (2000 users x {N_DAYS} snapshots)")

    # ---------- 3. ods.ods_usms_lm_channel_user_t_df (relation facts + 62 snapshots) ----
    rels, i = [], 0
    for u, rgst_d, chnl, _tm in users:
        n_rel = 2 if rng.random() < P_SECOND_REL else 1
        for k in range(n_rel):
            if k == 0:
                if rng.random() < P_RELAY_MAIN:
                    ch = rng.choice(relay_ids)
                    p_grant = relay_grant[ch]
                else:
                    ch = chnl if chnl in leaf_by_id else rng.choice(fin_leaves)
                    p_grant = GRANT[leaf_by_id[ch][1]] if ch in leaf_by_id else 0.5
            else:
                others = [c for c in leaf_by_id if c != chnl]
                ch = rng.choice(others) if others else chnl
                p_grant = CROSS_GRANT
            cday = min(rgst_d + timedelta(days=rng.randint(0, 5)), END)
            ctm = f"{rng.randrange(7, 23):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
            gday = gtm = None
            if rng.random() < p_grant:
                gday = min(cday + timedelta(days=rng.randint(0, 10)), END)
                gtm = f"{rng.randrange(7, 23):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
            rels.append(dict(cuid=f"C{i:07d}", u=u, ch=ch, cday=cday, ctm=ctm,
                             gday=gday, gtm=gtm, status=weighted(rng, USR_STATUS)))
            i += 1
    rows = []
    for d in days:
        for r in rels:
            granted = r["gday"] is not None and d >= r["gday"]
            upd = ts(r["gday"], r["gtm"]) if granted else ts(r["cday"], r["ctm"])
            rows.append((r["cuid"], r["u"], r["ch"], ts(r["cday"], r["ctm"]), upd,
                         ts(r["gday"], r["gtm"]) if granted else None,
                         r["status"], "1" if granted else "0", ts(d)))
    bulk_insert(ex, "INSERT INTO ods.ods_usms_lm_channel_user_t_df "
                    "(cuid, uid, channel_id, create_time, update_time, grant_time, "
                    "status, grant_status, ds) VALUES (", rows)
    gr_end = sum(1 for r in rels if r["gday"] is not None)
    print(f"ods_usms_lm_channel_user_t_df: {len(rows)} rows "
          f"({len(rels)} relations x {N_DAYS} snapshots); final grant rate = "
          f"{gr_end}/{len(rels)} = {gr_end / len(rels):.1%}")


    # ---------- 4. cdm.dwd_lm_pv_df ($pageview, ds = event day) ----------
    rows, j = [], 0
    for u, rgst_d, chnl, _tm in users:
        seg = "seg_b" if chnl in ("CH0401", "CH0402", "CH0501", "CH0502") else "fin"
        if rng.random() >= PV_P[seg]:
            continue
        span = (END - rgst_d).days
        if span < 0:
            continue
        n = min(weighted(rng, PV_DAYS), span + 1)
        for off in rng.sample(range(span + 1), n):
            dday = rgst_d + timedelta(days=off)
            t = f"{rng.randrange(7, 23):02d}:{rng.randrange(60):02d}:{rng.randrange(60):02d}"
            rows.append((f"E{j:08d}", u, "$pageview", f"{dday.isoformat()} {t}",
                         ts(dday, t), dday.isoformat(), ts(dday)))
            j += 1
    bulk_insert(ex, "INSERT INTO cdm.dwd_lm_pv_df (evt_id, login_id, event, evt_happ_tm, "
                    "evt_trig_tm, evt_trig_dt, ds) VALUES (", rows)
    print(f"dwd_lm_pv_df: {len(rows)} rows ($pageview events, ds = event day)")

    # ---------- 5. replay the real ETL scripts per day (verbatim, only ${data_ds}) ----
    tpl = {k: p.read_text(encoding="utf-8") for k, p in ETL.items()}
    tpl_conv = gauss_to_duckdb(tpl["ads_chnl_rgst_to_real_auth_dau_df"])
    assert "DISTRIBUTE" not in tpl_conv and "WITH (" not in tpl_conv
    for ds in day_strs:
        ex(tpl["dwd_cu_real_df"].replace(DAY_DS, ds))
        ex(tpl["dwd_ch_usr_rltv_df"].replace(DAY_DS, ds))
        ex(tpl["ads_chnl_real_user_df"].replace(DAY_DS, ds))
        ex(tpl["ads_chnl_auth_qty_df"].replace(DAY_DS, ds))
        ex(tpl["ads_chnl_rltv_chnl_df"].replace(DAY_DS, ds))
        ex(f"DROP TABLE IF EXISTS {MID_TBL}")  # temp-schema hit; warehouse: fresh session per day
        ex(tpl_conv.replace(DAY_DS, ds))
    print("5 ETL scripts replayed verbatim for all", N_DAYS, "days (only",
          DAY_DS, "substituted; conversion script: GaussDB storage clauses stripped)")

    # ================= acceptance evidence =================
    print("\n" + "=" * 28 + " 验收 1: 上游重算 vs 重放存储 (双向 EXCEPT) " + "=" * 28)
    names = ("ads_chnl_real_user_df", "ads_chnl_auth_qty_df", "ads_chnl_rltv_chnl_df",
             "ads_chnl_rgst_to_real_auth_dau_df")
    for name in names:
        body = tpl[name]
        mid_sel = None
        if name == "ads_chnl_rgst_to_real_auth_dau_df":
            body = gauss_to_duckdb(body)
            # acceptance loop runs fragments only: rebuild the mid temp table
            # whose CREATE lives outside the mid insert fragment
            ex("CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS " + MID_TBL + " "
               + body.split("CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS " + MID_TBL, 1)[1]
                      .split(";", 1)[0] + ";")
            mid_sel = body.split("insert into " + MID_TBL, 1)[1].split(";", 1)[0].strip()
            main_sel = body.split("insert into rec." + name, 1)[1].split(";", 1)[0].strip()
        else:
            main_sel = body.split("insert into rec." + name, 1)[1].split(";", 1)[0].strip()
        ex("CREATE OR REPLACE TEMP TABLE rc_" + name + " AS SELECT * FROM rec." + name + " WHERE 1 = 0")
        for ds in day_strs:
            if mid_sel is not None:
                ex(f"DELETE FROM {MID_TBL}")  # keep temp table, clear per day
                ex(("insert into " + MID_TBL + " " + mid_sel).replace(DAY_DS, ds))
            ex(("insert into rc_" + name + " " + main_sel).replace(DAY_DS, ds))
        n_stored = ex(f"SELECT count(*) FROM rec.{name}").fetchone()[0]
        n_rc = ex(f"SELECT count(*) FROM rc_{name}").fetchone()[0]
        diff = ex("SELECT count(*) FROM ((SELECT * FROM rec." + name + " EXCEPT SELECT * FROM rc_"
                  + name + ") UNION ALL (SELECT * FROM rc_" + name + " EXCEPT SELECT * FROM rec."
                  + name + "))").fetchone()[0]
        ok = diff == 0 and n_stored == n_rc
        print(f"{name:<38} stored={n_stored:>7} recalc={n_rc:>7} 双向EXCEPT差={diff}  "
              + ("PASS" if ok else "FAIL"))

    # phase-1 no-side-effect proof: dim_ch_chl_df got appended rows only; the
    # phase-1 ADS must recompute bit-identical from the untouched detail
    body = (ETL_DIR / "ADS层" / "核心指标" / "注册"
            / "脚本ads_rgst_chnl_cnt_df.sql").read_text(encoding="utf-8")
    sel = body.split("insert into rec.ads_rgst_chnl_cnt_df", 1)[1].split(";", 1)[0].strip()
    ex("CREATE OR REPLACE TEMP TABLE rc_phase1_ads AS SELECT * FROM rec.ads_rgst_chnl_cnt_df WHERE 1 = 0")
    for ds in day_strs:
        ex(("insert into rc_phase1_ads " + sel).replace(DAY_DS, ds))
    p1_stored = ex("SELECT count(*) FROM rec.ads_rgst_chnl_cnt_df").fetchone()[0]
    p1_rc = ex("SELECT count(*) FROM rc_phase1_ads").fetchone()[0]
    p1_diff = ex("SELECT count(*) FROM ((SELECT * FROM rec.ads_rgst_chnl_cnt_df EXCEPT SELECT * FROM rc_phase1_ads) "
                 "UNION ALL (SELECT * FROM rc_phase1_ads EXCEPT SELECT * FROM rec.ads_rgst_chnl_cnt_df))").fetchone()[0]
    print(f"{'ads_rgst_chnl_cnt_df(一期,无副作用)':<30} stored={p1_stored:>7} recalc={p1_rc:>7} "
          f"双向EXCEPT差={p1_diff}  {'PASS' if p1_diff == 0 and p1_stored == p1_rc else 'FAIL'}")

    print("\n" + "=" * 28 + " 验收 2: 转化率分子分母对账 (抽 2026-08-15) " + "=" * 28)
    vds = "2026-08-15"
    (rc_d, rc_m, rc_a, ac_d, ac_m, ac_a,
     rg_d, rg_m, rg_a, lg_d, lg_m, lg_a) = ex(
        "SELECT real_cnt_d, real_cnt_m, real_cnt_a, auth_cnt_d, auth_cnt_m, auth_cnt_a, "
        "rgst_cnt_d, rgst_cnt_m, rgst_cnt_a, rgst_log_cnt_d, rgst_log_cnt_m, rgst_log_cnt_a "
        "FROM rec.ads_chnl_rgst_to_real_auth_dau_df "
        f"WHERE ds = '{vds}' AND rgst_sec_chnl_nm = '整体'").fetchone()
    re_real = ex(f"SELECT sum(real_today), sum(real_curmth), sum(real_all) "
                 f"FROM rec.ads_chnl_real_user_df WHERE ds = '{vds}'").fetchone()
    re_auth = ex(f"SELECT sum(auth_user_cnt), sum(auth_user_mon_cnt), sum(auth_user_all_cnt) "
                 f"FROM rec.ads_chnl_auth_qty_df WHERE ds = '{vds}'").fetchone()
    re_rgst = ex(f"SELECT sum(new_rgst_cnt_d), sum(new_rgst_cnt_m), sum(new_rgst_cnt_a) "
                 f"FROM rec.ads_rgst_chnl_cnt_df WHERE ds = '{vds}' "
                 "AND sec_chnl_nm NOT IN ('麦当劳', '中信书院')").fetchone()
    re_log = ex(
        "WITH fin AS (SELECT usr_id, CAST(rgst_dt AS DATE) AS rgst_dt, rgst_sec_chnl_nm "
        "            FROM cdm.dwd_cu_rgst_fin_di WHERE ds <= '" + vds + "' GROUP BY 1, 2, 3), "
        "     pv  AS (SELECT CAST(evt_trig_dt AS DATE) AS e_dt, login_id FROM cdm.dwd_lm_pv_df "
        "            WHERE ds >= '2022-12-26' AND ds <= '" + vds + "' AND event = '$pageview' "
        "            GROUP BY 1, 2), "
        "     mid AS (SELECT f.usr_id, f.rgst_dt FROM fin f "
        "             JOIN pv p ON f.usr_id = p.login_id AND f.rgst_dt <= p.e_dt "
        "             WHERE f.rgst_dt <= DATE '" + vds + "' "
        "               AND f.rgst_sec_chnl_nm NOT IN ('麦当劳', '中信书院')) "
        "SELECT count(DISTINCT CASE WHEN rgst_dt = DATE '" + vds + "' THEN usr_id END), "
        "       count(DISTINCT CASE WHEN rgst_dt >= date_trunc('month', DATE '" + vds + "') "
        "                      THEN usr_id END), count(DISTINCT usr_id) FROM mid").fetchone()
    chk = [
        ("real_cnt_d  vs Σ real_today   ", rc_d, re_real[0]),
        ("real_cnt_m  vs Σ real_curmth  ", rc_m, re_real[1]),
        ("real_cnt_a  vs Σ real_all     ", rc_a, re_real[2]),
        ("auth_cnt_d  vs Σ auth_user_cnt", ac_d, re_auth[0]),
        ("auth_cnt_m  vs Σ auth_mon     ", ac_m, re_auth[1]),
        ("auth_cnt_a  vs Σ auth_all     ", ac_a, re_auth[2]),
        ("rgst_cnt_d  vs Σ rgst_d       ", rg_d, re_rgst[0]),
        ("rgst_cnt_m  vs Σ rgst_m       ", rg_m, re_rgst[1]),
        ("rgst_cnt_a  vs Σ rgst_a       ", rg_a, re_rgst[2]),
        ("rgst_log_cnt_d 重算            ", lg_d, re_log[0]),
        ("rgst_log_cnt_m 重算            ", lg_m, re_log[1]),
        ("rgst_log_cnt_a 重算            ", lg_a, re_log[2]),
    ]
    for label, got, want in chk:
        print(f"  {label}: 存储={got} 重算={want} " + ("PASS" if got == want else "FAIL"))

    print("\n" + "=" * 28 + " 验收 3: 行数清单 " + "=" * 28)
    for t in ("cdm.dwd_cu_real_df", "cdm.dwd_ch_usr_rltv_df",
              "rec.ads_chnl_real_user_df", "rec.ads_chnl_auth_qty_df",
              "rec.ads_chnl_rltv_chnl_df", "rec.ads_chnl_rgst_to_real_auth_dau_df",
              "ods.ods_usms_lm_user_t_df", "ods.ods_usms_lm_channel_user_t_df",
              "cdm.dwd_lm_pv_df", "cdm.dim_cu_usr_info_df"):
        (n,) = ex(f"SELECT count(*) FROM {t}").fetchone()
        print(f"{t:<42}{n:>9}")

    print("\n" + "=" * 28 + " 造数假设佐证 (末日快照) " + "=" * 28)
    rn_users = ex("SELECT count(*) FROM cdm.dim_cu_usr_info_df WHERE ds = "
                  "(SELECT max(ds) FROM cdm.dim_cu_usr_info_df) AND real_fg = '1'").fetchone()[0]
    real_detail, real_usr = ex("SELECT count(*), count(DISTINCT usr_id) FROM cdm.dwd_cu_real_df "
                               f"WHERE ds = '{day_strs[-1]}'").fetchone()
    rel_end, gr1 = ex("SELECT count(*), count(*) FILTER (WHERE grant_fg = '1') "
                      f"FROM cdm.dwd_ch_usr_rltv_df WHERE ds = '{day_strs[-1]}'").fetchone()
    whole = ex("SELECT rgst_cnt_d, real_cnt_d, auth_cnt_d, rgst_log_cnt_d "
               "FROM rec.ads_chnl_rgst_to_real_auth_dau_df "
               f"WHERE ds = '{day_strs[-1]}' AND rgst_sec_chnl_nm = '整体'").fetchone()
    top5 = ex("SELECT real_chnl_id, count(DISTINCT usr_id) FROM cdm.dwd_cu_real_df "
              f"WHERE ds = '{day_strs[-1]}' GROUP BY 1 ORDER BY 2 DESC LIMIT 5").fetchall()
    print(f"实名率(dim 用户维): {rn_users}/2000 = {rn_users / 20:.1f}%  -> "
          f"dwd_cu_real_df 明细行 {real_detail}, 实名用户 {real_usr}")
    print(f"授权率(dwd_ch_usr_rltv_df 末日): {gr1}/{rel_end} = {gr1 / rel_end:.1%}")
    print(f"实名渠道分布 top5: {top5}")
    print(f"转化率表末日整体行(注册D, 实名D, 授权D, 活跃注册D) = {tuple(whole)}")
    con.close()
    print("\nDONE")


if __name__ == "__main__":
    main()
