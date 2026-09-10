"""T2 扩展验收：实名/授权原子度量 + 比率复合度量 + gender 维度（扩展不破坏）。

跑法（禁跑全量）：
    .venv/bin/python -m pytest tests/test_fortune_semantic_ext.py -q

对账锚（materials 真实脚本 + 镜像 ADS 表）：
- 实名 ads_chnl_real_user_df：real_curmth/real_all 累计列逐格相等（含 null 组）；
  real_today 当日变式为镜像 timestamp 伪像，不作对账基准（registry R6）
- 授权 ads_chnl_auth_qty_df：镜像为账户口径（行计数，R8），用户口径按同源参照；
  渠道归属经用户维注册渠道名（R9，与注册明细全等）
- 比率 ads_chnl_rgst_to_real_auth_dau_df @2026-08-15：reg_to_real_rate 的
  real_cnt_m/rgst_cnt_m 变式逐格相等（KPI 六渠道；ADS 整体行未剔除直注段不用）
"""

import json
from pathlib import Path

import duckdb
import pytest

from src.fortune_semantic.compiler import QueryRequest, run_query
from src.fortune_semantic.query import main as cli_main
from src.fortune_semantic.registry import REGISTRY, SemanticError

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "fortune_mirror.duckdb"

FULL_RANGE = {"time_from": "2026-07-01", "time_to": "2026-08-31"}
AUG_1_TO_15 = {"time_from": "2026-08-01", "time_to": "2026-08-15"}

# 镜像库实证基准（防漂移，2026-09-11）
REAL_TOTAL_FULL = 1178  # 实名去重用户总数（= max(ds) 快照全量）
AUTH_TOTAL_FULL = 944  # 授权去重用户总数（grant_fg=1，max(ds) 快照）

USR_LATEST = (
    "(SELECT * FROM cdm.dim_cu_usr_info_df "
    "WHERE ds = (SELECT max(ds) FROM cdm.dim_cu_usr_info_df))"
)
CHN_LATEST = (
    "(SELECT * FROM cdm.dim_ch_chl_df "
    "WHERE ds = (SELECT max(ds) FROM cdm.dim_ch_chl_df))"
)
REAL_LATEST = (
    "(SELECT * FROM cdm.dwd_cu_real_df "
    "WHERE ds = (SELECT max(ds) FROM cdm.dwd_cu_real_df))"
)
AUTH_LATEST = (
    "(SELECT * FROM cdm.dwd_ch_usr_rltv_df "
    "WHERE ds = (SELECT max(ds) FROM cdm.dwd_ch_usr_rltv_df) AND grant_fg = '1')"
)


@pytest.fixture()
def conn():
    connection = duckdb.connect(str(DB_PATH), read_only=True)
    yield connection
    connection.close()


def _run(conn, **kwargs):
    return run_query(QueryRequest(**kwargs), conn=conn)


def _single_dim_map(result):
    """单维度结果 -> {维度值: 度量值}（含 None 组）。"""
    assert len(result["columns"]) == 2
    return {row[0]: row[1] for row in result["rows"]}


# ==================================================================
# 注册表挂载：新度量/复合度量/口径规则 + 出处脚本真实存在
# ==================================================================


def test_ext_registry_mounted_and_scripts_exist():
    real = REGISTRY.measures["real_name_user_cnt"]
    assert real.source_table == "cdm.dwd_cu_real_df"
    assert real.time_field == "real_dt"
    auth = REGISTRY.measures["auth_user_cnt"]
    assert auth.source_table == "cdm.dwd_ch_usr_rltv_df"
    assert auth.time_field == "grant_dt"
    assert set(auth.dimension_overrides) == {
        "channel_l1",
        "channel_l2",
        "channel_l3",
    }

    ratio = REGISTRY.ratios["reg_to_real_rate"]
    assert (ratio.numerator, ratio.denominator) == (
        "real_name_user_cnt",
        "reg_user_cnt",
    )
    assert REGISTRY.ratios["reg_to_auth_rate"].denominator == "reg_user_cnt"

    # R5-R10 挂载、unverified、出处脚本真实存在（可机器追溯）；
    # R1 已由管理台确认流置 confirmed（老测试锁定），新规则保持 unverified
    assert {"R5", "R6", "R7", "R8", "R9", "R10"} <= set(REGISTRY.rules)
    assert REGISTRY.rules["R1"].status == "confirmed"
    assert all(
        REGISTRY.rules[rid].status == "unverified"
        for rid in ("R5", "R6", "R7", "R8", "R9", "R10")
    )
    for rule_id in ("R5", "R6", "R7", "R8", "R9", "R10"):
        script = Path(REGISTRY.rules[rule_id].source_script)
        assert script.is_file(), (rule_id, script)


# ==================================================================
# real_name_user_cnt：对 ADS ads_chnl_real_user_df 标准答案逐格相等
# ==================================================================


def test_real_name_cnt_total_full_range(conn):
    result = _run(conn, measure="real_name_user_cnt", dimensions=(), **FULL_RANGE)
    assert result["columns"] == ["real_name_user_cnt"]
    assert result["rows"] == [(REAL_TOTAL_FULL,)]
    # 编译器卫生：去重 + 最新分区快照过滤进 SQL，日期走绑定参数
    assert "COUNT(DISTINCT" in result["sql"]
    assert "max(ds)" in result["sql"]
    assert result["params"] == ["2026-07-01", "2026-08-31"]


def test_real_name_cnt_channel_l2_matches_ads(conn):
    """T2 方法：三级按二级聚合后逐格相等（null 组如实存在一并比对）。"""
    got_month = _single_dim_map(
        _run(
            conn,
            measure="real_name_user_cnt",
            dimensions=("channel_l2",),
            time_from="2026-08-01",
            time_to="2026-08-31",
        )
    )
    got_full = _single_dim_map(
        _run(
            conn, measure="real_name_user_cnt", dimensions=("channel_l2",), **FULL_RANGE
        )
    )

    ads_rows = conn.execute(
        """
        SELECT sec_chnl_nm, sum(real_curmth), sum(real_all)
        FROM rec.ads_chnl_real_user_df
        WHERE CAST(data_dt AS DATE) = DATE '2026-08-31'
        GROUP BY 1
        """
    ).fetchall()
    ads_month = {name: int(m) for name, m, _ in ads_rows}
    ads_all = {name: int(a) for name, _, a in ads_rows}
    assert sum(ads_all.values()) == REAL_TOTAL_FULL
    assert sum(ads_month.values()) == 842  # 8 月当月实名（7 月增量 336）

    # 当月累计窗口 == ADS real_curmth；全量窗口 == ADS real_all（均含 null 组）
    assert got_month == ads_month
    assert got_full == ads_all


# ==================================================================
# auth_user_cnt：用户口径同源参照逐格相等；ADS 账户口径方向对账（R8）
# ==================================================================


def test_auth_user_cnt_channel_l2_user_vs_account(conn):
    got = _single_dim_map(
        _run(conn, measure="auth_user_cnt", dimensions=("channel_l2",), **FULL_RANGE)
    )

    # 同源参照一：用户维注册渠道名（语义层绑定的同源实现，含 null 组）
    ref_usr = dict(
        conn.execute(
            f"""
            SELECT u.rgst_sec_chnl_nm, COUNT(DISTINCT rv.usr_id)
            FROM {AUTH_LATEST} rv LEFT JOIN {USR_LATEST} u ON rv.usr_id = u.usr_id
            WHERE CAST(rv.grant_dt AS DATE) BETWEEN DATE '2026-07-01'
                  AND DATE '2026-08-31'
            GROUP BY 1
            """
        ).fetchall()
    )
    assert got == ref_usr
    assert sum(got.values()) == AUTH_TOTAL_FULL

    # R9 等价性（机器锁定）：同时在用户维与注册明细中的授权用户，渠道名全等
    name_mismatch = conn.execute(
        f"""
        SELECT COUNT(DISTINCT rv.usr_id)
        FROM {AUTH_LATEST} rv
        JOIN {USR_LATEST} u ON rv.usr_id = u.usr_id
        JOIN cdm.dwd_cu_rgst_fin_di f ON rv.usr_id = f.usr_id
        WHERE COALESCE(u.rgst_sec_chnl_nm, '')
              <> COALESCE(f.rgst_sec_chnl_nm, '')
        """
    ).fetchone()[0]
    assert name_mismatch == 0

    ref_fin = dict(
        conn.execute(
            f"""
            SELECT f.rgst_sec_chnl_nm, COUNT(DISTINCT rv.usr_id)
            FROM {AUTH_LATEST} rv
            LEFT JOIN cdm.dwd_cu_rgst_fin_di f ON rv.usr_id = f.usr_id
            WHERE CAST(rv.grant_dt AS DATE) BETWEEN DATE '2026-07-01'
                  AND DATE '2026-08-31'
            GROUP BY 1
            """
        ).fetchall()
    )
    non_null_fin = {k: v for k, v in ref_fin.items() if k is not None}
    # 成员差实锤（R8 记载的 ADS 丢弃面）：有授权但无金融注册记录的用户
    # 用户维仍给渠道名（语义层计入），ADS 内联注册表整行丢弃。镜像实证 86 人
    fin_absent = conn.execute(
        f"""
        SELECT COUNT(DISTINCT rv.usr_id) FROM {AUTH_LATEST} rv
        WHERE NOT EXISTS (
            SELECT 1 FROM cdm.dwd_cu_rgst_fin_di f WHERE f.usr_id = rv.usr_id
        )
        """
    ).fetchone()[0]
    assert fin_absent == 86

    # ADS 账户口径（行计数）复现 ADS 发布值，两个窗口各自逐格：
    # 当月窗口 == auth_user_mon_cnt（8/31 截面），全史窗口 == auth_user_all_cnt
    ads_rows = conn.execute(
        """
        SELECT rgst_sec_chnl_nm, sum(auth_user_mon_cnt), sum(auth_user_all_cnt)
        FROM rec.ads_chnl_auth_qty_df
        WHERE CAST(data_dt AS DATE) = DATE '2026-08-31'
        GROUP BY 1
        """
    ).fetchall()
    ads_accounts_mon = {sec: int(mon) for sec, mon, _ in ads_rows}
    ads_accounts_all = {sec: int(all_) for sec, _, all_ in ads_rows}

    def _account_rows(time_from):
        rows = conn.execute(
            f"""
            SELECT f.rgst_sec_chnl_nm, COUNT(*)
            FROM {AUTH_LATEST} rv
            JOIN cdm.dwd_cu_rgst_fin_di f ON rv.usr_id = f.usr_id
            WHERE CAST(rv.grant_dt AS DATE) BETWEEN DATE '{time_from}'
                  AND DATE '2026-08-31'
            GROUP BY 1
            """
        ).fetchall()
        return dict(rows)

    assert _account_rows("2026-08-01") == ads_accounts_mon
    assert _account_rows("2026-07-01") == ads_accounts_all
    # 方向不变量（同一 fin 映射下）：授权账户数 >= 授权用户数
    # （跨映射不比：ADS 丢弃 86 个无金融注册授权用户，见上 fin_absent）
    assert all(ads_accounts_all[sec] >= non_null_fin[sec] for sec in ads_accounts_all)
    # 分歧实锤（同窗口同映射，8 月）：ADS 账户数 595 > 去重用户数 552
    aug_users = dict(
        conn.execute(
            f"""
            SELECT f.rgst_sec_chnl_nm, COUNT(DISTINCT rv.usr_id)
            FROM {AUTH_LATEST} rv
            JOIN cdm.dwd_cu_rgst_fin_di f ON rv.usr_id = f.usr_id
            WHERE CAST(rv.grant_dt AS DATE) BETWEEN DATE '2026-08-01'
                  AND DATE '2026-08-31'
            GROUP BY 1
            """
        ).fetchall()
    )
    assert sum(ads_accounts_mon.values()) > sum(aug_users.values())


# ==================================================================
# 比率复合度量：@2026-08-15 对 ads_chnl_rgst_to_real_auth_dau_df
# ==================================================================


def test_ratio_reg_to_real_rate_matches_ads_dau_0815(conn):
    result = _run(
        conn,
        measure="reg_to_real_rate",
        dimensions=("channel_l2",),
        **AUG_1_TO_15,
    )
    assert result["columns"] == [
        "channel_l2",
        "real_name_user_cnt",
        "reg_user_cnt",
        "reg_to_real_rate",
    ]
    # 分子分母子查询各带独立时间边界：参数为 (from, to, from, to)
    assert result["params"] == [
        "2026-08-01",
        "2026-08-15",
        "2026-08-01",
        "2026-08-15",
    ]
    assert "2026-08" not in result["sql"]  # 日期字面量不进 SQL 文本

    got = {row[0]: row[1:] for row in result["rows"]}
    # ADS 标准答案（KPI 渠道行；整体行未剔除直注段不用，见综合脚本 t1/t2 不对称）
    ads_rows = conn.execute(
        """
        SELECT rgst_sec_chnl_nm, real_cnt_m, rgst_cnt_m
        FROM rec.ads_chnl_rgst_to_real_auth_dau_df
        WHERE CAST(data_dt AS DATE) = DATE '2026-08-15'
          AND rgst_sec_chnl_nm <> '整体'
        """
    ).fetchall()
    assert len(ads_rows) == 6
    for sec, real_m, rgst_m in ads_rows:
        num, den, rate = got[sec]
        assert num == real_m, sec
        assert den == rgst_m, sec
        assert rate == pytest.approx(real_m / rgst_m), sec
    assert "整体" not in got


def test_ratio_auth_rate_same_source_and_invariants_full_range(conn):
    """reg_to_auth_rate：分子/分母与各自原子度量同源一致（I1 式）。"""
    result = _run(
        conn,
        measure="reg_to_auth_rate",
        dimensions=("channel_l2",),
        **FULL_RANGE,
    )
    got = {row[0]: row[1:] for row in result["rows"]}
    atomic_auth = _single_dim_map(
        _run(conn, measure="auth_user_cnt", dimensions=("channel_l2",), **FULL_RANGE)
    )
    atomic_reg = _single_dim_map(
        _run(conn, measure="reg_user_cnt", dimensions=("channel_l2",), **FULL_RANGE)
    )
    # 对侧缺失的组按 0 计（编译器 COALESCE 语义）
    assert {k: v[0] for k, v in got.items()} == {k: atomic_auth.get(k, 0) for k in got}
    assert {k: v[1] for k, v in got.items()} == {k: atomic_reg.get(k, 0) for k in got}
    for sec, (num, den, rate) in got.items():
        expected = num / den if den else None
        if expected is None:
            assert rate is None, sec
        else:
            assert rate == pytest.approx(expected), sec


def test_ratio_zero_denominator_outputs_null(conn):
    """分母 0/缺失输出 NULL 不报错；镜像实证：7/4 中信书院授权 3 人、注册 0。"""
    result = _run(
        conn,
        measure="reg_to_auth_rate",
        dimensions=("channel_l2",),
        time_from="2026-07-04",
        time_to="2026-07-04",
    )
    got = {row[0]: row[1:] for row in result["rows"]}
    num, den, rate = got["中信书院"]
    assert num == 3 and den == 0 and rate is None  # 结构化 NULL，非异常

    # 空窗口无维度：单行 (0, 0, NULL)，COUNT 空集语义
    empty = _run(
        conn,
        measure="reg_to_real_rate",
        dimensions=(),
        time_from="2026-09-01",
        time_to="2026-09-30",
    )
    assert empty["rows"] == [(0, 0, None)]

    # 结构化报错路径在复合度量上保持
    with pytest.raises(SemanticError) as excinfo:
        _run(conn, measure="reg_to_real_rate", dimensions=("region",), **FULL_RANGE)
    assert excinfo.value.code == "UNREGISTERED_DIMENSION"


# ==================================================================
# gender 维度：M/F/NULL 三组都有值，NULL 如实输出不过滤
# ==================================================================


@pytest.mark.parametrize(
    ("measure_id", "total"),
    [
        ("reg_user_cnt", 1760),
        ("real_name_user_cnt", REAL_TOTAL_FULL),
        ("auth_user_cnt", AUTH_TOTAL_FULL),
    ],
)
def test_gender_dimension_three_groups_all_measures(conn, measure_id, total):
    result = _run(conn, measure=measure_id, dimensions=("gender",), **FULL_RANGE)
    assert result["columns"] == ["gender", measure_id]
    got = _single_dim_map(result)
    assert {"M", "F", None} <= set(got)  # 三组都有值
    assert all(v > 0 for v in got.values())
    assert got[None] > 0  # NULL 性别如实输出，未被过滤
    assert sum(got.values()) == total  # 分组求和 = 总数（无 join 扇出）


# ==================================================================
# 组合证明：channel_l1 x gender（无 ADS 对照：同源参照 + Sigma 不变量）
# ==================================================================


def test_channel_l1_x_gender_combo_ratio(conn):
    result = _run(
        conn,
        measure="reg_to_real_rate",
        dimensions=("channel_l1", "gender"),
        **FULL_RANGE,
    )
    assert result["columns"] == [
        "channel_l1",
        "gender",
        "real_name_user_cnt",
        "reg_user_cnt",
        "reg_to_real_rate",
    ]
    got = {(row[0], row[1]): row[2:] for row in result["rows"]}

    num_rows = conn.execute(
        f"""
        SELECT chn.fst_chnl_nm, u.usr_sex, COUNT(DISTINCT r.usr_id)
        FROM {REAL_LATEST} r
        LEFT JOIN {CHN_LATEST} chn ON r.rgst_chnl_id = chn.chnl_id
        LEFT JOIN {USR_LATEST} u ON r.usr_id = u.usr_id
        GROUP BY 1, 2
        """
    ).fetchall()
    den_rows = conn.execute(
        f"""
        SELECT chn.fst_chnl_nm, u.usr_sex, COUNT(DISTINCT d.usr_id)
        FROM cdm.dwd_cu_rgst_fin_di d
        LEFT JOIN {CHN_LATEST} chn ON d.rgst_chnl_id = chn.chnl_id
        LEFT JOIN {USR_LATEST} u ON d.usr_id = u.usr_id
        WHERE d.rgst_num = 1
        GROUP BY 1, 2
        """
    ).fetchall()
    nums = {(a, b): c for a, b, c in num_rows}
    dens = {(a, b): c for a, b, c in den_rows}
    assert set(got) == set(nums) | set(dens)  # 组集合双向一致（多组/少组即失败）
    for key, (num, den, rate) in got.items():
        assert num == nums.get(key, 0), key
        assert den == dens.get(key, 0), key
        expected = num / den if den else None
        if expected is None:
            assert rate is None, key
        else:
            assert rate == pytest.approx(expected), key

    # Sigma 不变量：分子分母跨组求和 = 各自无维度总数
    assert sum(v[0] for v in got.values()) == REAL_TOTAL_FULL
    assert sum(v[1] for v in got.values()) == 1760


# ==================================================================
# CLI 不变即用：新度量/复合度量自动可用
# ==================================================================


def test_cli_ratio_and_real_measure_usable(capsys):
    payload = json.dumps(
        {
            "measure": "reg_to_real_rate",
            "dimensions": ["channel_l2"],
            "time_from": "2026-08-01",
            "time_to": "2026-08-15",
        }
    )
    assert cli_main([payload]) == 0
    out = capsys.readouterr().out
    rows_json = json.loads(out.split("=== ROWS ===\n")[1])
    assert rows_json["columns"][-1] == "reg_to_real_rate"
    assert len(rows_json["rows"]) >= 6

    payload2 = json.dumps(
        {
            "measure": "real_name_user_cnt",
            "dimensions": ["gender"],
            "time_from": "2026-07-01",
            "time_to": "2026-08-31",
        }
    )
    assert cli_main([payload2]) == 0
    rows_json2 = json.loads(capsys.readouterr().out.split("=== ROWS ===\n")[1])
    assert {r[0] for r in rows_json2["rows"]} >= {"M", "F", None}
