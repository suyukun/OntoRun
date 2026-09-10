"""财富广场语义原语注册表（Pydantic 显式注册表，不引 RDF）。

三个口径陷阱的注册表表达（2026-09-10 镜像库实证）：
1. 粒度对齐：ADS 按三级渠道分组，二级答案 = 三级聚合后才可对账；
2. 字段来源：渠道维度一律 JOIN cdm.dim_ch_chl_df 取维表列，
   禁止用明细自带 rgst_sec_chnl_nm 分组；
3. 维表快照：dim_ch_chl_df / dim_cu_usr_info_df 均为 ds 日分区快照，
   不选分区会 join 扇出（实证 1760 行 -> 108937 行），
   快照策略绑定 latest_partition（当前镜像 max(ds) = '2026-08-31'）。

口径规则 R1-R4 全部标 unverified（未经数仓确认，管理台确认后置 confirmed）；
字段结构（id/人话描述/出处脚本/确认状态）为管理台预留。
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
        default=(), description="WHERE 条件模板，{src} 占位"
    )


class JoinSpec(BaseModel):
    """维表关联：JOIN 目标 + 快照策略（防分区扇出）。"""

    model_config = ConfigDict(frozen=True)

    table: str
    alias: str
    on: str = Field(description="JOIN 条件模板，{src}/{j} 占位")
    select_columns: tuple[str, ...]
    snapshot_policy: str = SNAPSHOT_LATEST
    snapshot_column: str = "ds"


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


REGISTRY = SemanticRegistry(measures=MEASURES, dimensions=DIMENSIONS, rules=RULES)
