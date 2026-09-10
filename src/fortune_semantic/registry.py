"""财富广场语义原语注册表（Pydantic 显式注册表，不引 RDF）。

三个口径陷阱的注册表表达（2026-09-10 镜像库实证）：
1. 粒度对齐：ADS 按三级渠道分组，二级答案 = 三级聚合后才可对账；
2. 字段来源：渠道维度一律 JOIN cdm.dim_ch_chl_df 取维表列，
   禁止用明细自带 rgst_sec_chnl_nm 分组；
3. 维表快照：dim_ch_chl_df / dim_cu_usr_info_df 均为 ds 日分区快照，
   不选分区会 join 扇出（实证 1760 行 -> 108937 行），
   快照策略绑定 latest_partition（当前镜像 max(ds) = '2026-08-31'）。

口径规则 R1-R10 全部标 unverified（未经数仓确认，管理台确认后置 confirmed）；
字段结构（id/人话描述/出处脚本/确认状态）为管理台预留。

T2 扩展（2026-09-11，扩展不破坏）：原子度量新增 real_name_user_cnt /
auth_user_cnt（口径锚 ADS层/核心指标 真实脚本，R5-R9）；复合度量第一次
落地为 RatioMeasure（分子/分母度量 id，编译器分别聚合后外层相除，R10）。
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RuleStatus = Literal["unverified", "confirmed"]

SNAPSHOT_LATEST = "latest_partition"

WAREHOUSE_SCRIPT_DIR = (
    "materials/fortune-warehouse-input/2026-09-10-数仓ddl及脚本/01_财富管理脚本"
)


class CaliberRule(BaseModel):
    """口径规则：语义层显式化的业务口径，供管理台确认/治理。"""

    model_config = ConfigDict(frozen=True)

    id: str
    description: str = Field(description="人话描述")
    source_script: str = Field(description="出处脚本（数仓证据文件）")
    status: RuleStatus = "unverified"


class JoinSpec(BaseModel):
    """维表关联：JOIN 目标 + 快照策略（防分区扇出）。"""

    model_config = ConfigDict(frozen=True)

    table: str
    alias: str
    on: str = Field(description="JOIN 条件模板，{src}/{j} 占位")
    select_columns: tuple[str, ...]
    snapshot_policy: str = SNAPSHOT_LATEST
    snapshot_column: str = "ds"


class DimensionOverride(BaseModel):
    """度量级维度覆写：同一维度 id 在特定度量下的 join 与取值表达式。"""

    model_config = ConfigDict(frozen=True)

    join: JoinSpec
    expression: str = Field(description="维度取值表达式模板，{j} 占位")


class RatioMeasure(BaseModel):
    """复合度量（OneData"复合指标"）：分子/分母为原子度量 id。

    编译器在同维度同时间窗下对分子分母按各自绑定分别聚合，
    再外层相除；分母为 0 或缺失输出 NULL（R10）。
    """

    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    numerator: str = Field(description="分子原子度量 id")
    denominator: str = Field(description="分母原子度量 id")


class Measure(BaseModel):
    """度量：绑定源表 + 表达式模板（{src} = source_alias）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    expression: str = Field(description="聚合表达式模板，{src} 占位")
    source_table: str
    source_alias: str
    time_field: str = Field(description="时间字段（列名），显式声明")
    filters: tuple[str, ...] = Field(
        default=(), description="WHERE 条件模板，{src}/{tbl} 占位"
    )
    dimension_overrides: dict[str, DimensionOverride] = Field(
        default={},
        description="维度 id -> 度量级覆写（该度量下此维度改用此 join/表达式）",
    )


class Dimension(BaseModel):
    """维度：渠道/属性维走 JOIN 维表列，time_grain 基于度量时间字段。"""

    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    expression: str = Field(
        default="", description="表达式模板，{j} 占位；time_grain 维度为空"
    )
    join: JoinSpec | None = None
    grains: dict[str, str] | None = Field(
        default=None,
        description="time_grain 专用：grain -> 表达式模板（{t} = 度量时间字段）",
    )


DIM_CH = JoinSpec(
    table="cdm.dim_ch_chl_df",
    alias="chn",
    on="{src}.rgst_chnl_id = {j}.chnl_id",
    select_columns=("chnl_id", "fst_chnl_nm", "sec_chnl_nm", "thd_chnl_nm", "ds"),
)

DIM_USR = JoinSpec(
    table="cdm.dim_cu_usr_info_df",
    alias="usr",
    on="{src}.usr_id = {j}.usr_id",
    select_columns=("usr_id", "usr_sex", "ds"),
)

# 授权度量专用：授权明细无注册渠道列，经用户维注册渠道名归组（R9，
# 镜像实证与注册明细 rgst_sec_chnl_nm 全等）。与 DIM_USR 同表同别名，
# 编译器按 (table, alias) 合并 select_columns，gender+渠道组合时自动并列。
DIM_USR_RGST = JoinSpec(
    table="cdm.dim_cu_usr_info_df",
    alias="usr",
    on="{src}.usr_id = {j}.usr_id",
    select_columns=(
        "usr_id",
        "rgst_fst_chnl_nm",
        "rgst_sec_chnl_nm",
        "rgst_thd_chnl_nm",
        "ds",
    ),
)


MEASURES = {
    "reg_user_cnt": Measure(
        id="reg_user_cnt",
        description="注册用户数：注册 KPI 明细去重用户数（增量表每行一人，rgst_num=1 为表语义）",
        expression="COUNT(DISTINCT {src}.usr_id)",
        source_table="cdm.dwd_cu_rgst_fin_di",
        source_alias="dwd",
        time_field="rgst_dt",
        filters=("{src}.rgst_num = 1",),
    ),
    # 明细快照过滤模板：{tbl} 由编译器以度量 source_table 代入，表名单一来源
    "real_name_user_cnt": Measure(
        id="real_name_user_cnt",
        description=(
            "实名用户数：窗口内完成实名（real_dt 落窗）的去重用户数；明细为逐日累积快照，"
            "恒取 max(ds) 最新分区（R5/R6，口径锚 ads_chnl_real_user_df 脚本）"
        ),
        expression="COUNT(DISTINCT {src}.usr_id)",
        source_table="cdm.dwd_cu_real_df",
        source_alias="rl",
        time_field="real_dt",
        filters=("{src}.ds = (SELECT max(ds) FROM {tbl})",),
    ),
    "auth_user_cnt": Measure(
        id="auth_user_cnt",
        description=(
            "授权用户数：窗口内完成授权（grant_fg=1 且 grant_dt 落窗）的去重用户数；"
            "恒取 max(ds) 最新分区；渠道经用户维注册渠道名归组（R7-R9，口径锚 ads_chnl_auth_qty_df 脚本）"
        ),
        expression="COUNT(DISTINCT {src}.usr_id)",
        source_table="cdm.dwd_ch_usr_rltv_df",
        source_alias="rv",
        time_field="grant_dt",
        filters=(
            "{src}.grant_fg = '1'",
            "{src}.ds = (SELECT max(ds) FROM {tbl})",
            "CAST({src}.grant_dt AS DATE) >= DATE '2022-12-26'",
        ),
        dimension_overrides={
            "channel_l1": DimensionOverride(
                join=DIM_USR_RGST, expression="{j}.rgst_fst_chnl_nm"
            ),
            "channel_l2": DimensionOverride(
                join=DIM_USR_RGST, expression="{j}.rgst_sec_chnl_nm"
            ),
            "channel_l3": DimensionOverride(
                join=DIM_USR_RGST, expression="{j}.rgst_thd_chnl_nm"
            ),
        },
    ),
}

RATIOS = {
    "reg_to_real_rate": RatioMeasure(
        id="reg_to_real_rate",
        description=(
            "注册→实名转化率 = real_name_user_cnt / reg_user_cnt，"
            "同维度同时间窗分别聚合后相除；分母 0/缺失输出 NULL（R10）"
        ),
        numerator="real_name_user_cnt",
        denominator="reg_user_cnt",
    ),
    "reg_to_auth_rate": RatioMeasure(
        id="reg_to_auth_rate",
        description=(
            "注册→授权转化率 = auth_user_cnt / reg_user_cnt，"
            "同维度同时间窗分别聚合后相除；分母 0/缺失输出 NULL（R10）"
        ),
        numerator="auth_user_cnt",
        denominator="reg_user_cnt",
    ),
}

DIMENSIONS = {
    "channel_l1": Dimension(
        id="channel_l1",
        description="一级渠道：JOIN 渠道维 fst_chnl_nm（维表列为准，禁止明细自带名分组）",
        expression="{j}.fst_chnl_nm",
        join=DIM_CH,
    ),
    "channel_l2": Dimension(
        id="channel_l2",
        description="二级渠道：JOIN 渠道维 sec_chnl_nm（对账时由三级 ADS 聚合对齐）",
        expression="{j}.sec_chnl_nm",
        join=DIM_CH,
    ),
    "channel_l3": Dimension(
        id="channel_l3",
        description="三级渠道：JOIN 渠道维 thd_chnl_nm（ADS 原生分组粒度）",
        expression="{j}.thd_chnl_nm",
        join=DIM_CH,
    ),
    "gender": Dimension(
        id="gender",
        description="性别：JOIN 用户维 usr_sex（usr_id 粒度，快照取当期末分区 max(ds)='2026-08-31'）",
        expression="{j}.usr_sex",
        join=DIM_USR,
    ),
    "time_grain": Dimension(
        id="time_grain",
        description="时间粒度：基于度量时间字段 rgst_dt；week 用 strftime %W（周一起算，零填充周号）",
        grains={
            "day": "strftime({t}, '%Y-%m-%d')",
            "week": "strftime({t}, '%W')",
            "month": "strftime({t}, '%Y-%m')",
        },
    ),
}

RULES = {
    "R1": CaliberRule(
        id="R1",
        description="直注段渠道排除：注册渠道为麦当劳/中信书院的用户不进直注段（光注册不算 KPI）",
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/CDM层/用户域CU/脚本dwd_cu_rgst_fin_di.sql",
        status="confirmed",
    ),
    "R2": CaliberRule(
        id="R2",
        description="激活段：仅麦当劳/中信书院渠道用户带 if_act=1 激活标记，经激活转化计入注册 KPI",
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/CDM层/用户域CU/脚本dwd_cu_rgst_fin_di.sql",
    ),
    "R3": CaliberRule(
        id="R3",
        description=(
            "激活日期边界：actv_tag='1' 自 2024-07-01 起算（2024-06-30 前公众号不算）；"
            "actv_tag='2'（企微+小程序关注）自 2024-07-09 上线起算"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/CDM层/用户域CU/脚本dwd_cu_actv_df.sql",
    ),
    "R4": CaliberRule(
        id="R4",
        description="多激活取最早：一人多条激活记录按用户取最早一条（row_number 去重）",
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/CDM层/用户域CU/脚本dwd_cu_actv_df.sql",
    ),
    # ---- T2 扩展：实名 / 授权 / 比率（出处均为 ADS层/核心指标 真实脚本）----
    "R5": CaliberRule(
        id="R5",
        description=(
            "实名明细快照：dwd_cu_real_df 为逐日累积快照（镜像实证 8/31 分区含全史"
            " 1178 用户），恒取 max(ds) 最新分区；对应脚本明细 t1 where ds='${data_ds}'"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/注册/脚本ads_chnl_real_user_df.sql",
    ),
    "R6": CaliberRule(
        id="R6",
        description=(
            "实名时间语义：real_dt 为实名完成时点（TIMESTAMP 带时分秒，镜像无零点值）；"
            "镜像 ADS real_today（当日变式）因 timestamp=日期逐格相等恒 0（伪像），"
            "日粒度对账用 real_curmth/real_all 累计列替代（窗口含首日即等价）"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/注册/脚本ads_chnl_real_user_df.sql",
    ),
    "R7": CaliberRule(
        id="R7",
        description=(
            "授权明细过滤：grant_fg='1' 且恒取 max(ds) 最新分区；grant_dt 为授权时点；"
            "脚本含 grant_dt>='2022-12-26' 上线下界（镜像 0 行命中，惰性保留）"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/授权/脚本ads_chnl_auth_qty_df.sql",
    ),
    "R8": CaliberRule(
        id="R8",
        description=(
            "授权计数口径分歧（未决）：ADS 脚本按行计数=授权账户数，一人多渠道授权重复计入"
            "（镜像 8 月实证 595 账户 vs 552 去重用户），且内联注册表丢失无金融注册的授权用户"
            "（镜像 8 月 55 人）；语义层 auth_user_cnt 按用户去重，逐格相等仅在账户口径下成立，"
            "账户数 >= 用户数方向恒成立"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/授权/脚本ads_chnl_auth_qty_df.sql",
    ),
    "R9": CaliberRule(
        id="R9",
        description=(
            "授权渠道归属：授权明细无注册渠道列，语义层经用户维 rgst_fst/sec/thd_chnl_nm 归组"
            "（镜像实证与注册明细 rgst_sec_chnl_nm 对授权用户全等，0 不一致）；"
            "ADS 脚本用 fin∪nonfin 注册表联合推导（fin 优先，row_number rn=1）"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/授权/脚本ads_chnl_auth_qty_df.sql",
    ),
    "R10": CaliberRule(
        id="R10",
        description=(
            "比率复合口径：同维度同时间窗下分子分母按各自源表/时间字段/过滤分别聚合，"
            "维度键 IS NOT DISTINCT FROM 全外对齐后外层相除；分母 0 或缺失输出 NULL 不报错；"
            "转化链口径锚 ads_chnl_rgst_to_real_auth_dau_df（注册→实名→授权）"
        ),
        source_script=f"{WAREHOUSE_SCRIPT_DIR}/ADS层/核心指标/综合/脚本ads_chnl_rgst_to_real_auth_dau_df.sql",
    ),
}


class SemanticError(Exception):
    """结构化语义层错误（禁止静默兜底）。"""

    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class SemanticRegistry(BaseModel):
    """原语注册表：度量 / 维度 / 口径规则的唯一事实来源。"""

    model_config = ConfigDict(frozen=True)

    measures: dict[str, Measure]
    dimensions: dict[str, Dimension]
    rules: dict[str, CaliberRule]
    ratios: dict[str, RatioMeasure] = Field(
        default={},
        description="复合度量（分子/分母指向 measures 中的原子度量）",
    )

    def get_measure(self, measure_id: str) -> Measure:
        try:
            return self.measures[measure_id]
        except KeyError:
            raise SemanticError(
                "UNREGISTERED_MEASURE",
                f"度量未注册: {measure_id}",
                measure=measure_id,
                available=sorted(self.measures),
            ) from None

    def get_dimension(self, dimension_id: str) -> Dimension:
        try:
            return self.dimensions[dimension_id]
        except KeyError:
            raise SemanticError(
                "UNREGISTERED_DIMENSION",
                f"维度未注册: {dimension_id}",
                dimension=dimension_id,
                available=sorted(self.dimensions),
            ) from None


REGISTRY = SemanticRegistry(
    measures=MEASURES, dimensions=DIMENSIONS, rules=RULES, ratios=RATIOS
)
