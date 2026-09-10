"""语义层不变量套件 I1-I5（governance 测试，锁死安全边界）。

跑法（禁跑全量）：
    .venv/bin/python -m pytest tests/test_fortune_invariants.py -q

不变量归属：
- I1 同源一致 / I2 身份粒度 / I3 时间显式 / I5 拒答完整 -> 本文件；
- I4 组合保真 -> 已由 tests/test_fortune_semantic.py 的 T2（channel_l2 对账
  ADS 标准答案 + null 组如实存在不计入比对）与 T3（channel_l1 ×
  time_grain=week 双向组合对参照实现）覆盖，此处不重复实现。
"""

import json
from pathlib import Path

import duckdb
import pytest

from src.fortune_semantic.compiler import QueryRequest, compile_query, run_query
from src.fortune_semantic.registry import REGISTRY, SemanticError

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "fortune_mirror.duckdb"

AUG_FROM, AUG_TO = "2026-08-01", "2026-08-31"

# 2026-09-10 镜像库实证基准（防漂移）：8 月编译器总数 = 分组求和（含 null 组）
# = ADS 三级按二级聚合总和（含 null sec 组，ADS 也如实带这 1 条无维表匹配组）
AUG_TOTAL = 930
AUG_NULL_GROUP = 1

# 用户维当期末快照（ds = 2026-08-31）：usr_id 粒度 2000，手机号粒度 1998，
# 差值即一人多账号现象（phone 无缺失，方向 phone <= usr_id 恒成立）
USR_SNAPSHOT_ROWS = 2000
USR_SNAPSHOT_PHONES = 1998

# 结构化错误输出中禁止出现的堆栈/内部路径泄漏标记
LEAK_MARKERS = ("Traceback", "site-packages", "/Users", ".py")


@pytest.fixture()
def conn():
    connection = duckdb.connect(str(DB_PATH), read_only=True)
    yield connection
    connection.close()


# ======================================================================
# I1 同源一致：同一答案三条独立推导路径必须相等
# ======================================================================

def test_i1_three_way_consistency_august(conn):
    """分渠道Σ(含 null 组) == 无维度总数 == 镜像库 ADS 二级聚合总和。"""
    by_channel = run_query(
        QueryRequest(
            measure="reg_user_cnt",
            dimensions=("channel_l2",),
            time_from=AUG_FROM,
            time_to=AUG_TO,
        ),
        conn=conn,
    )
    total = run_query(
        QueryRequest(
            measure="reg_user_cnt",
            dimensions=(),
            time_from=AUG_FROM,
            time_to=AUG_TO,
        ),
        conn=conn,
    )

    assert by_channel["columns"] == ["channel_l2", "reg_user_cnt"]
    got = {row[0]: row[1] for row in by_channel["rows"]}
    # null 组（明细 rgst_chnl_id 无维表匹配）如实存在，单列、计入求和
    assert got.get(None) == AUG_NULL_GROUP

    channel_sum = sum(got.values())
    assert channel_sum == total["rows"][0][0] == AUG_TOTAL

    # 镜像库 ADS 标准答案：三级按二级聚合（8 月末截面）
    ads_rows = conn.execute(
        """
        SELECT sec_chnl_nm, sum(new_rgst_cnt_m) AS cnt
        FROM rec.ads_rgst_chnl_cnt_df
        WHERE CAST(data_dt AS DATE) = DATE '2026-08-31'
        GROUP BY 1
        """
    ).fetchall()
    ads = {name: int(cnt) for name, cnt in ads_rows}
    assert ads.get(None) == AUG_NULL_GROUP
    assert sum(ads.values()) == AUG_TOTAL

    # 非 null 组逐一相等：编译器维表口径 == ADS 发布口径
    assert {k: v for k, v in got.items() if k is not None} == {
        k: v for k, v in ads.items() if k is not None
    }


# ======================================================================
# I2 身份粒度：去重语义是度量定义的一部分，不是执行期可选项
# ======================================================================

DEDUP_MARK = "COUNT(DISTINCT"


def test_i2_compiled_sql_always_dedups():
    """编译器生成的 SQL 恒含 COUNT(DISTINCT ...)（文本级，覆盖全部维度组合）。"""
    combos = (
        (),
        ("channel_l1",),
        ("channel_l2",),
        ("channel_l3",),
        ("gender",),
        ("time_grain=day",),
        ("time_grain=week",),
        ("time_grain=month",),
        ("channel_l1", "time_grain=month"),
    )
    for dimensions in combos:
        compiled = compile_query(
            QueryRequest(
                measure="reg_user_cnt",
                dimensions=dimensions,
                time_from=AUG_FROM,
                time_to=AUG_TO,
            )
        )
        assert DEDUP_MARK in compiled.sql, dimensions


def test_i2_increment_table_one_row_per_person(conn):
    """镜像库实证：增量表 COUNT(DISTINCT usr_id)==COUNT(*)（每行一人）。"""
    overall = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT usr_id) FROM cdm.dwd_cu_rgst_fin_di"
    ).fetchone()
    assert overall[0] == overall[1] == 1760

    # 度量口径（rgst_num=1）不丢行且同样每行一人
    scoped = conn.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT usr_id)
        FROM cdm.dwd_cu_rgst_fin_di
        WHERE rgst_num = 1
        """
    ).fetchone()
    assert scoped[0] == scoped[1] == overall[0]


def test_i2_user_dim_phone_granularity(conn):
    """用户维手机号粒度：DISTINCT phone 1998 < usr_id 2000，一人多账号如实存在。

    只锁方向合法性（phone 数 <= usr_id 数、无 NULL 缺失、多账号实锤），
    不判业务对错——粒度语义由调用方按问题选择。
    """
    snapshot = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT usr_id), COUNT(DISTINCT usr_phone_erpt) "
        "FROM cdm.dim_cu_usr_info_df WHERE ds = "
        "(SELECT max(ds) FROM cdm.dim_cu_usr_info_df)"
    ).fetchone()
    assert snapshot[0] == snapshot[1] == USR_SNAPSHOT_ROWS
    assert snapshot[2] == USR_SNAPSHOT_PHONES

    null_phone = conn.execute(
        "SELECT COUNT(*) FROM cdm.dim_cu_usr_info_df WHERE ds = "
        "(SELECT max(ds) FROM cdm.dim_cu_usr_info_df) "
        "AND usr_phone_erpt IS NULL"
    ).fetchone()[0]
    assert null_phone == 0  # 差值不是 NULL 造成的假象

    multi_account_phones = conn.execute(
        "SELECT COUNT(*) FROM ("
        "SELECT usr_phone_erpt FROM cdm.dim_cu_usr_info_df WHERE ds = "
        "(SELECT max(ds) FROM cdm.dim_cu_usr_info_df) "
        "GROUP BY 1 HAVING COUNT(DISTINCT usr_id) > 1)"
    ).fetchone()[0]
    assert multi_account_phones >= 1  # 一人多账号现象实锤


# ======================================================================
# I3 时间显式：无时间边界的全表查询在编译期就不该存在
# ======================================================================

def test_i3_every_measure_binds_time_field():
    """registry 每个度量的 time_field 显式声明且非空。"""
    assert REGISTRY.measures, "注册表至少要有一个度量"
    for measure_id, measure in REGISTRY.measures.items():
        assert measure.time_field, f"度量 {measure_id} 缺少 time_field"


def test_i3_sql_carries_explicit_time_cast_and_bounds():
    """编译 SQL 必含度量时间字段的显式 CAST + 上下界比较，边界走绑定参数。"""
    measure = REGISTRY.get_measure("reg_user_cnt")
    time_col = f"{measure.source_alias}.{measure.time_field}"
    lower = f"CAST({time_col} AS DATE) >= ?"
    upper = f"CAST({time_col} AS DATE) <= ?"
    for dimensions in ((), ("channel_l2",)):
        compiled = compile_query(
            QueryRequest(
                measure="reg_user_cnt",
                dimensions=dimensions,
                time_from=AUG_FROM,
                time_to=AUG_TO,
            )
        )
        assert lower in compiled.sql, dimensions
        assert upper in compiled.sql, dimensions
        assert compiled.params == (AUG_FROM, AUG_TO)
        assert AUG_FROM not in compiled.sql  # 日期字面量不进 SQL 文本
        assert AUG_TO not in compiled.sql


def test_i3_inverted_time_window_structured_error():
    """from > to -> 结构化 INVALID_TIME_RANGE；from == to 边界合法。"""
    with pytest.raises(SemanticError) as excinfo:
        compile_query(
            QueryRequest(
                measure="reg_user_cnt",
                dimensions=(),
                time_from=AUG_TO,
                time_to=AUG_FROM,
            )
        )
    err = excinfo.value
    assert err.code == "INVALID_TIME_RANGE"
    assert AUG_TO in err.message and AUG_FROM in err.message
    assert err.details["time_from"] == AUG_TO
    assert err.details["time_to"] == AUG_FROM

    same_day = compile_query(
        QueryRequest(
            measure="reg_user_cnt",
            dimensions=(),
            time_from=AUG_FROM,
            time_to=AUG_FROM,
        )
    )
    assert same_day.params == (AUG_FROM, AUG_FROM)


# ======================================================================
# I5 拒答完整：三类拒绝 + 三字段齐全 + 零泄漏
# ======================================================================

def test_i5_unregistered_measure():
    with pytest.raises(SemanticError) as excinfo:
        compile_query(
            QueryRequest(
                measure="total_profit",
                dimensions=(),
                time_from=AUG_FROM,
                time_to=AUG_TO,
            )
        )
    err = excinfo.value
    assert err.code == "UNREGISTERED_MEASURE"
    assert "total_profit" in err.message
    assert err.details["measure"] == "total_profit"
    assert err.details["available"] == sorted(REGISTRY.measures)
    assert "reg_user_cnt" in err.details["available"]


def test_i5_unregistered_dimension():
    with pytest.raises(SemanticError) as excinfo:
        compile_query(
            QueryRequest(
                measure="reg_user_cnt",
                dimensions=("region",),
                time_from=AUG_FROM,
                time_to=AUG_TO,
            )
        )
    err = excinfo.value
    assert err.code == "UNREGISTERED_DIMENSION"
    assert "region" in err.message
    assert err.details["dimension"] == "region"
    assert err.details["available"] == sorted(REGISTRY.dimensions)
    assert {"channel_l1", "channel_l2", "channel_l3"} <= set(
        err.details["available"]
    )


def test_i5_invalid_time_grain():
    """无效粒度与缺失粒度都归 INVALID_TIME_GRAIN，且给出合法粒度清单。"""
    cases = (("time_grain=quarter", "quarter"), ("time_grain", ""))
    for entry, grain in cases:
        with pytest.raises(SemanticError) as excinfo:
            compile_query(
                QueryRequest(
                    measure="reg_user_cnt",
                    dimensions=(entry,),
                    time_from=AUG_FROM,
                    time_to=AUG_TO,
                )
            )
        err = excinfo.value
        assert err.code == "INVALID_TIME_GRAIN", entry
        if grain:
            assert grain in err.message
            assert err.details["grain"] == grain
        assert err.details["dimension"] == "time_grain"
        assert err.details["available"] == sorted(
            REGISTRY.dimensions["time_grain"].grains
        )
        assert set(err.details["available"]) == {"day", "week", "month"}


def _collect_refusals() -> list[SemanticError]:
    """现场触发全部拒答类错误（含 INVALID_TIME_RANGE），供零泄漏断言。"""
    refusals = []
    cases = (
        ("total_profit", ()),
        ("reg_user_cnt", ("region",)),
        ("reg_user_cnt", ("time_grain=quarter",)),
        ("reg_user_cnt", ("time_grain",)),
    )
    for measure_id, dimensions in cases:
        with pytest.raises(SemanticError) as excinfo:
            compile_query(
                QueryRequest(
                    measure=measure_id,
                    dimensions=dimensions,
                    time_from=AUG_FROM,
                    time_to=AUG_TO,
                )
            )
        refusals.append(excinfo.value)
    with pytest.raises(SemanticError) as excinfo:
        compile_query(
            QueryRequest(
                measure="reg_user_cnt",
                dimensions=(),
                time_from=AUG_TO,
                time_to=AUG_FROM,
            )
        )
    refusals.append(excinfo.value)
    return refusals


def test_i5_errors_leak_no_stack_or_paths():
    """任何 SemanticError 的 str/to_dict 均不含堆栈或内部路径（LLM 可见面收敛）。"""
    for err in _collect_refusals():
        serialized = json.dumps(err.to_dict(), ensure_ascii=False)
        for text in (str(err), serialized):
            for marker in LEAK_MARKERS:
                assert marker not in text, (err.code, marker, text)
