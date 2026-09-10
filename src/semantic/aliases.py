"""M1 别名层：口语问法 → 注册表原语 id / 渠道成员值的确定性候选展开。

归属说明：别名属"问法理解层"，按六层架构放 src/semantic/（不改
src/fortune_semantic/，该包只做原语注册与编译）。

契约（并行 llm_route 改造任务依赖，勿改名）：
- ALIAS_TABLE: dict，按类别查询 {"measure" | "dimension" | "value":
  {别名关键词: (目标, ...)}}；关键词均已 normalize_text 归一；
  value 类目标为维表成员原值（大小写保持原样，匹配时才归一）。
- normalize_text(q: str) -> str：NFKC 全半角归一 + 去全部空白 + ASCII 小写。
- expand_candidates(q: str) -> {"measure_hints": [...], "dimension_hints": [...],
  "value_hints": [...]}：问题中命中的别名 → 候选 id/成员值。
  只产候选不做裁决（0 候选拒答 / 多候选澄清属 M4/M6）。

匹配规则：全部关键词按长度降序扫描，命中即消费字符区间（长词优先，
"一级渠道"不会被裸"渠道"重复命中）；同类内去重保序。

T2 依赖：real_name_user_cnt / auth_user_cnt 与两条比率在注册表已注册即自动
生效（T2 完整版已落地，见 src/fortune_semantic/registry.py）；若未来回退未
注册，expand_candidates 过滤失效目标而 ALIAS_TABLE 数据保留。

渠道值来源：运行时懒加载镜像库 cdm.dim_ch_chl_df 最新分区（fst/sec 名单，
快照策略同 registry.SNAPSHOT_LATEST）；库不可达时降级 BUILTIN_CHANNEL_VALUES
（2026-08-31 分区实证快照）。加载结果 lru_cache 进程内缓存。
"""

import unicodedata
from functools import lru_cache

from src.fortune_semantic.registry import REGISTRY

from . import config

# ----------------------------------------------------------------------
# 度量口语别名：问题关键词 → 原语 id（可多候选，裁决在下游）
# ----------------------------------------------------------------------
MEASURE_ALIASES: dict[str, tuple[str, ...]] = {
    # 注册用户数（KPI 增量口径）
    "注册了多少": ("reg_user_cnt",),
    "来了多少人": ("reg_user_cnt",),
    "新增用户": ("reg_user_cnt",),
    "新增注册": ("reg_user_cnt",),
    "注册用户数": ("reg_user_cnt",),
    "注册用户": ("reg_user_cnt",),
    "注册人数": ("reg_user_cnt",),
    "注册数": ("reg_user_cnt",),
    "注册量": ("reg_user_cnt",),
    # 裸"注册"兜底口语（"注册的男女比例"）——仅产候选，超纲句由路由/拒答层裁决
    "注册": ("reg_user_cnt",),
    # 实名用户数（T2 完整版已注册 → 自动生效；未注册则 _active 过滤，映射保留）
    "实名了多少": ("real_name_user_cnt",),
    "实名用户数": ("real_name_user_cnt",),
    "实名用户": ("real_name_user_cnt",),
    "实名人数": ("real_name_user_cnt",),
    "实名": ("real_name_user_cnt",),
    # 授权用户数（T2）
    "授权了多少": ("auth_user_cnt",),
    "授权用户数": ("auth_user_cnt",),
    "授权用户": ("auth_user_cnt",),
    "授权": ("auth_user_cnt",),
    # 转化率（复合度量）；裸"转化率"双候选 → 下游澄清
    "注册到实名的转化率": ("reg_to_real_rate",),
    "注册实名转化率": ("reg_to_real_rate",),
    "实名转化率": ("reg_to_real_rate",),
    "注册到授权的转化率": ("reg_to_auth_rate",),
    "注册授权转化率": ("reg_to_auth_rate",),
    "授权转化率": ("reg_to_auth_rate",),
    "转化率": ("reg_to_real_rate", "reg_to_auth_rate"),
}

# ----------------------------------------------------------------------
# 维度口语别名："time_grain=<grain>" 参数化写法同 llm_route.validate_plan
# ----------------------------------------------------------------------
DIMENSION_ALIASES: dict[str, tuple[str, ...]] = {
    "男女比例": ("gender",),
    "性别分布": ("gender",),
    "男的和女的": ("gender",),
    "男女": ("gender",),
    "性别": ("gender",),
    "一级渠道": ("channel_l1",),
    "二级渠道": ("channel_l2",),
    "三级渠道": ("channel_l3",),
    "渠道分布": ("channel_l2",),
    "各渠道": ("channel_l2",),
    "分渠道": ("channel_l2",),
    "渠道": ("channel_l2",),
    "走势": ("time_grain=day",),
    "趋势": ("time_grain=day",),
    "按天": ("time_grain=day",),
    "每天": ("time_grain=day",),
    "每日": ("time_grain=day",),
    "按周": ("time_grain=week",),
    "周度": ("time_grain=week",),
    "按月": ("time_grain=month",),
    "月度": ("time_grain=month",),
}

# ----------------------------------------------------------------------
# 渠道值口语变体：关键词 → 维表成员原值（规范值本身由 _channel_values 动态匹配）
# ----------------------------------------------------------------------
VALUE_ALIASES: dict[str, tuple[str, ...]] = {
    "优享plus": ("优享+线上",),
    "优享线上": ("优享+线上",),
    # 裸"优享+"歧义（线上/企微双渠道）→ 双候选，裁决在下游
    "优享+": ("优享+线上", "优享+企微"),
    "金拱门": ("麦当劳",),
}

# 类别键即契约：按类别查询别名资产
ALIAS_TABLE: dict[str, dict[str, tuple[str, ...]]] = {
    "measure": MEASURE_ALIASES,
    "dimension": DIMENSION_ALIASES,
    "value": VALUE_ALIASES,
}

# cdm.dim_ch_chl_df latest_partition（ds=2026-08-31）fst/sec 实证快照（2026-09-10）。
# 仅当镜像库不可达时兜底；库可达时以 _channel_values 实查为准（刷新=重跑镜像）。
BUILTIN_CHANNEL_VALUES: tuple[str, ...] = (
    "中信优享+",
    "中信证券",
    "中信银行",
    "中信集团",
    "内容生态",
    "合作商圈",
    "优享+企微",
    "优享+线上",
    "证券App",
    "证券营业部",
    "信用卡中心",
    "银行App",
    "中信优享+公众号",
    "中信保诚人寿",
    "中信信托",
    "中信建投期货",
    "中信建投证券",
    "中信期货",
    "中信消费金融",
    "中信银行信用卡",
    "信银理财",
    "华夏基金",
    "百信银行",
    "中信书院",
    "书店门店",
    "商圈其他",
    "麦当劳",
)

_REGISTERED_MEASURES = frozenset(REGISTRY.measures) | frozenset(REGISTRY.ratios)


def _active(targets: tuple[str, ...]) -> tuple[str, ...]:
    """度量目标未注册自动失效（T2 回退安全），注册即自动生效。"""
    return tuple(t for t in targets if t in _REGISTERED_MEASURES)


# 静态别名编译产物：长度降序，同类并列时保持声明序（sorted 稳定）
_COMPILED: list[tuple[str, str, tuple[str, ...]]] = sorted(
    [
        *((kw, "measure_hints", _active(ts)) for kw, ts in MEASURE_ALIASES.items()),
        *((kw, "dimension_hints", ts) for kw, ts in DIMENSION_ALIASES.items()),
        *((kw, "value_hints", ts) for kw, ts in VALUE_ALIASES.items()),
    ],
    key=lambda entry: len(entry[0]),
    reverse=True,
)


@lru_cache(maxsize=1)
def _channel_values() -> tuple[str, ...]:
    """最新分区渠道成员（fst+sec 去重）；镜像不可达降级内置名单（结果缓存）。"""
    try:
        import duckdb

        conn = duckdb.connect(str(config.MIRROR_DB), read_only=True)
        try:
            rows = conn.execute(
                "SELECT fst_chnl_nm, sec_chnl_nm FROM cdm.dim_ch_chl_df "
                "WHERE ds = (SELECT max(ds) FROM cdm.dim_ch_chl_df)"
            ).fetchall()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001 有意兜底：镜像不可达不砸断别名层
        return BUILTIN_CHANNEL_VALUES
    values = {
        str(name).strip() for row in rows for name in row if name and str(name).strip()
    }
    return tuple(sorted(values)) if values else BUILTIN_CHANNEL_VALUES


def normalize_text(q: str) -> str:
    """NFKC 全半角归一 + 去全部空白 + ASCII 小写（仅用于匹配，不改写目标值）。"""
    text = unicodedata.normalize("NFKC", str(q))
    return "".join(text.split()).lower()


def expand_candidates(q: str) -> dict:
    """问题（归一后）中命中的别名 → 候选；长词优先消费区间，同类去重保序。"""
    text = normalize_text(q)
    hints: dict[str, list[str]] = {
        "measure_hints": [],
        "dimension_hints": [],
        "value_hints": [],
    }
    if not text:
        return hints
    # 渠道成员原值直接命中也算 value 候选（"麦当劳"本身即规范值）
    dynamic = [
        (normalize_text(value), "value_hints", (value,)) for value in _channel_values()
    ]
    consumed = [False] * len(text)
    for keyword, kind, targets in sorted(
        [*_COMPILED, *dynamic], key=lambda entry: len(entry[0]), reverse=True
    ):
        _consume(text, keyword, kind, targets, hints, consumed)
    return hints


def _consume(
    text: str,
    keyword: str,
    kind: str,
    targets: tuple[str, ...],
    hints: dict[str, list[str]],
    consumed: list[bool],
) -> None:
    """非重叠消费扫描：命中区间已被更长关键词占用则跳过。"""
    start = 0
    while (hit := text.find(keyword, start)) != -1:
        end = hit + len(keyword)
        if not any(consumed[hit:end]):
            for index in range(hit, end):
                consumed[index] = True
            bucket = hints[kind]
            for target in targets:
                if target not in bucket:
                    bucket.append(target)
        start = hit + 1
