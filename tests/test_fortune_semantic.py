"""T2 验收测试：最小语义层（原语注册表 + 确定性编译器）—— I4 组合保真第一版。

跑法（禁跑全量）：
    .venv/bin/python -m pytest tests/test_fortune_semantic.py -q
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

# 2026-09-10 已人工验数的 ADS 修正答案（二级 = 三级 M 口径聚合，8 月末截面）
DOCUMENTED_ADS_L2_AUGUST = {
    "中信书院": 120,
    "优享+企微": 85,
    "优享+线上": 232,
    "信用卡中心": 77,
    "证券App": 76,
    "证券营业部": 78,
    "银行App": 143,
    "麦当劳": 118,
}


@pytest.fixture()
def conn():
    connection = duckdb.connect(str(DB_PATH), read_only=True)
    yield connection
    connection.close()


def _run(conn, **kwargs):
    return run_query(QueryRequest(**kwargs), conn=conn)


def _to_dict_single_dim(result):
    assert result["columns"][:2] and result["columns"][-1] == "reg_user_cnt"
    return {row[0]: row[-1] for row in result["rows"]}


def test_registry_rules_mounted_and_unverified():
    """口径规则管理台预留字段挂载：R1-R4 在册、状态合法；未确认项保持 unverified。

    2026-09-11 更新：R1 已由管理台确认流置 confirmed（commit 4e77cc4，Rose 自动验收），
    断言从"全部 unverified"收敛为"未确认的 R2-R4 保持 unverified"。
    """
    assert {"R1", "R2", "R3", "R4"} <= set(REGISTRY.rules)
    assert all(rule.status in ("unverified", "confirmed") for rule in REGISTRY.rules.values())
    assert REGISTRY.rules["R1"].status == "confirmed"
    assert all(REGISTRY.rules[rid].status == "unverified" for rid in ("R2", "R3", "R4"))
    assert all(rule.source_script for rule in REGISTRY.rules.values())


def test_t1_total_count_no_dimensions(conn):
    result = _run(conn, measure="reg_user_cnt", dimensions=(), **FULL_RANGE)
    assert result["columns"] == ["reg_user_cnt"]
    assert result["rows"] == [(1760,)]
    assert "COUNT(DISTINCT" in result["sql"]


def test_t2_channel_l2_august_matches_ads(conn):
    result = _run(
        conn,
        measure="reg_user_cnt",
        dimensions=("channel_l2",),
        time_from="2026-08-01",
        time_to="2026-08-31",
    )
    got = _to_dict_single_dim(result)

    # ADS 修正答案：三级渠道按二级聚合（sec_chnl_nm 非空），M 口径 8 月末截面
    ads_rows = conn.execute(
        """
        SELECT sec_chnl_nm, sum(new_rgst_cnt_m) AS cnt
        FROM rec.ads_rgst_chnl_cnt_df
        WHERE CAST(data_dt AS DATE) = DATE '2026-08-31'
          AND sec_chnl_nm IS NOT NULL
        GROUP BY 1
        """
    ).fetchall()
    expected = {name: int(cnt) for name, cnt in ads_rows}
    assert expected == DOCUMENTED_ADS_L2_AUGUST  # 对账基准锁定（防 ADS 漂移）

    non_null = {key: value for key, value in got.items() if key is not None}
    assert non_null == expected

    # null 组如实存在不计入比对：明细 rgst_chnl_id 无维表匹配
    # （全量表 3 条 CHN_BAD_01/02/03，8 月窗口内为 1 条）
    assert got.get(None) == 1
    assert sum(got.values()) == 930

    # 编译器卫生：SQL 无业务字面量（渠道名/日期不进 SQL 文本，走注册表与绑定参数）
    assert "中信书院" not in result["sql"]
    assert "2026-08" not in result["sql"]


def test_t3_channel_l1_week_combination_both_ways(conn):
    """组合证明（非菜单）：渠道 JOIN 维 + 时间粒度两种异质维度自由组合。"""
    result = _run(
        conn,
        measure="reg_user_cnt",
        dimensions=("channel_l1", "time_grain=week"),
        **FULL_RANGE,
    )
    assert result["columns"] == ["channel_l1", "time_grain_week", "reg_user_cnt"]
    got = {(row[0], row[1]): row[2] for row in result["rows"]}

    # 参照实现：同一字段来源（明细 JOIN 渠道维当期末快照），自算双向对
    ref_rows = conn.execute(
        """
        SELECT chn.fst_chnl_nm, strftime(dwd.rgst_dt, '%W') AS wk,
               COUNT(DISTINCT dwd.usr_id) AS cnt
        FROM cdm.dwd_cu_rgst_fin_di AS dwd
        LEFT JOIN (
            SELECT chnl_id, fst_chnl_nm, ds FROM cdm.dim_ch_chl_df
            WHERE ds = (SELECT max(ds) FROM cdm.dim_ch_chl_df)
        ) AS chn
          ON dwd.rgst_chnl_id = chn.chnl_id
        WHERE dwd.rgst_num = 1
          AND CAST(dwd.rgst_dt AS DATE) BETWEEN DATE '2026-07-01' AND DATE '2026-08-31'
        GROUP BY 1, 2
        """
    ).fetchall()
    expected = {(name, wk): cnt for name, wk, cnt in ref_rows}
    assert got == expected  # 双向：多组/少组/数值不符任一即失败

    # 每行一人 -> 分组求和 = 总数（无 join 扇出不变量）
    assert sum(got.values()) == 1760
    assert len({wk for _, wk in got}) >= 8  # 周粒度真正展开
    assert "中信优享+" not in result["sql"]  # 业务字面量不进 SQL


def test_t4_unregistered_dimension_structured_error(conn):
    with pytest.raises(SemanticError) as excinfo:
        _run(conn, measure="reg_user_cnt", dimensions=("region",), **FULL_RANGE)
    assert excinfo.value.code == "UNREGISTERED_DIMENSION"
    assert excinfo.value.details["dimension"] == "region"
    assert "channel_l2" in excinfo.value.details["available"]


def test_t4_cli_rejects_without_silent_fallback(capsys):
    payload = json.dumps(
        {
            "measure": "reg_user_cnt",
            "dimensions": ["region"],
            "time_from": "2026-07-01",
            "time_to": "2026-08-31",
        }
    )
    exit_code = cli_main([payload])
    assert exit_code == 2
    error = json.loads(capsys.readouterr().err)["error"]
    assert error["code"] == "UNREGISTERED_DIMENSION"
    assert error["details"]["dimension"] == "region"
