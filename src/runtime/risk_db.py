"""S3 M3 金控风控（ap_anping）数据源适配层。

职责（写引擎的「数据源」交付物）：
1. 六库一体连接：ap_anping 数据分散在 6 个 SQLite 库（customer/risk/concentration/
   approval/project/base），动作写回常跨库（如审批单在 approval.db、信号在 risk.db）。
   RiskStore 以 risk.db 为主库、其余 5 库 ATTACH，同连接事务 = 跨库原子（§2.3 写引擎）。
2. 状态机值适配：源系统用中文状态（待确认/确认中/已确认/已关闭/已撤销；未处置/处置中/
   已处置/暂缓处置），本体用规范英文状态机（GENERATED/CONFIRMED/GRADED/IN_DISPOSAL/
   CLOSED；DRAFT/SUBMITTED/APPROVING/APPROVED/REJECTED/EXECUTING/DONE）。动作 handler
   在本体域做状态机校验（读中文→译英文→判迁移），写回时把目标英文态译回中文落源库。
   本体为执行真相源（docs/S3-安平金控-业务流程建模-v1.md「执行真相源在本体，本稿仅供参考」），
   本映射即「源系统词汇 ↔ 规范词汇」的适配层（语义接口研究点：适配而非改写源系统）。
3. 源系统表适配：本体对象 source_table 是逻辑表名（o_a_erms_*，M1a 脱敏映射），实际落
   ap_anping 各库真实表名。build_risk_source_registry() 把 source_table 改写到真实表
   （含库别名限定），供 ObjectIndex / 读引擎（ContractExecutor 走同一数据源）消费。

信号状态映射说明（适配决策，见 docs/S3-M1a-字段脱敏映射-脊柱12表.json 值域）：
源 ap_warning_signal.signal_status 7 值 ↔ 本体 7 态，取单调递进：
  待确认=GENERATED（生成待确认）→ 确认中=CONFIRMED（人工认领/进入确认流程）
  → 已确认=GRADED（定级完成）→ 处置中=IN_DISPOSAL（处置流转）→ 已关闭=CLOSED；
  已撤销=REJECTED_AS_FALSE（误报撤销）、已排除=EXCLUDED（非实质风险排除）。
  处置方案提交把 signal_status 置「处置中」，销号再由「处置中」→「已关闭」，
  与业务流程建模的状态机一致。

处置身份适配：本体 Disposal.disposal_id 在源系统落 ap_warning_disposal（WD- 前缀，
处置状态载体表，1 处置↔1 预警，含 disposal_status）；ap_disposal（DSP- 前缀）是处置
批次主单（batch，无独立状态列，不承载状态机）。ap_warning_disposal 无 deal_type/comment
列，submit_disposal 的处置内容参数仅落审计 params（见 risk_actions_impl 文档）。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.ontology.registry import Registry
from src.ontology.risk_objects import register_risk_objects
from src.runtime.store import Store

# ap_anping 数据根目录（6 库 12 表，308k 行，des 生成物）
AP_ANPING_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "des" / "enterprises" / "ap_anping"
)
# S3 风险本体库（审计/ontology_state 落库），与零售本体库分离
DEFAULT_RISK_ONTOLOGY_DB = (
    Path(__file__).resolve().parents[2] / "data" / "ontology" / "s3_risk_ontology.db"
)

# 演示业务年度（ap_anping 编码规则：{PREFIX}-{YYYY}-{8位流水}，data 均按 2026）
RISK_DEMO_YEAR = 2026

# ---- 信号状态：本体规范态 ↔ 源系统中文值（适配层，1:1；口径包§四 七态） ----
SIGNAL_STATUS_TO_CN: dict[str, str] = {
    "GENERATED": "待确认",
    "CONFIRMED": "确认中",
    "GRADED": "已确认",
    "IN_DISPOSAL": "处置中",
    "CLOSED": "已关闭",
    "REJECTED_AS_FALSE": "已撤销",
    "EXCLUDED": "已排除",
}
SIGNAL_STATUS_FROM_CN: dict[str, str] = {v: k for k, v in SIGNAL_STATUS_TO_CN.items()}

# ---- 处置状态：本体 7 态 ↔ 源 ap_warning_disposal.disposal_status 4 值（多对一） ----
DISPOSAL_STATUS_TO_CN: dict[str, str] = {
    "DRAFT": "未处置",
    "SUBMITTED": "处置中",
    "APPROVING": "处置中",
    "APPROVED": "处置中",
    "REJECTED": "暂缓处置",
    "EXECUTING": "处置中",
    "DONE": "已处置",
}
# 反向（源中文 → 本体态）：处置中取 EXECUTING 为规范代表态（其余态由动作迁移决定）
DISPOSAL_STATUS_FROM_CN: dict[str, str] = {
    "未处置": "DRAFT",
    "处置中": "EXECUTING",
    "已处置": "DONE",
    "暂缓处置": "REJECTED",
}

# ---- 对象类型 → ap_anping 实际表（含库别名限定；主库 risk.db 表不带别名） ----
# 全量 33 对象均已映射真实表（M2 起补全脊柱四表 ap_collateral/ap_codebt_customer/
# ap_org/ap_user；新增无源对象时须同步登记 NOT_QUERYABLE_OBJECTS 拒答）。
SOURCE_TABLE_MAP: dict[str, str] = {
    # 脊柱 13 对象
    "RiskCustomer": "customer.ap_customer",
    "GroupCustomer": "customer.ap_group_customer",
    "WarningSignal": "ap_warning_signal",
    "Metric": "base.ap_dim_metric",
    "Disposal": "ap_warning_disposal",
    "ApproveOrder": "approval.ap_approve_order",
    "ApproveTask": "approval.ap_approve_task",
    "ConcentrationLimit": "concentration.ap_concentration_limit",
    "RiskProject": "project.ap_risk_project",
    "Collateral": "customer.ap_collateral",
    "CoDebtCustomer": "concentration.ap_codebt_customer",
    "Organization": "base.ap_org",
    "User": "base.ap_user",
    # 全量扩展对象（33 对象全量，真实表名 = 脱敏名 ap_*）
    "CustomerRelation": "customer.ap_customer_relation",
    "CustomerRelationTree": "customer.ap_customer_relation_tree",
    "ImportantCustomerList": "customer.ap_important_customer_list",
    "Top500CustomerRisk": "customer.ap_top500_customer_risk",
    "CustomerAssets": "customer.ap_customer_assets",
    "InvestDistribution": "customer.ap_customer_invest_dist",
    "SubsidiaryCreditDetail": "customer.ap_subsidiary_credit_detail",
    "BankPledgeDetail": "customer.ap_bank_pledge_detail",
    "SecuritiesPledgeDetail": "customer.ap_securities_pledge_detail",
    "SubsidiaryMortgage": "customer.ap_subsidiary_mortgage",
    "WarningPush": "ap_warning_push",  # risk.db 主库无别名
    "CoDebtScore": "concentration.ap_codebt_warn_score",
    "ConcentrationLimitAdj": "concentration.ap_concentration_limit_adj",
    "ConcentrationWarnAdj": "concentration.ap_concentration_warn_adj",
    "WarningConcentration": "ap_warn_signal_concentration",
    "WarningDerive": "ap_warn_signal_derive",
    "WarningDeviation": "ap_warn_signal_deviation",
    "DeviationScore": "ap_deviation_warn_score",
    "ApproveTodo": "approval.ap_approve_todo",
    "ApproveOperLog": "approval.ap_approve_oper_log",
}


def risk_db(name: str) -> sqlite3.Connection:
    """打开 ap_anping 单个库（name ∈ customer/risk/concentration/approval/project/base）。"""
    conn = sqlite3.connect(str(AP_ANPING_DIR / f"{name}.db"))
    conn.row_factory = sqlite3.Row
    return conn


class RiskStore(Store):
    """ap_anping 六库一体源连接：主库 risk.db，其余 5 库 ATTACH，跨库事务原子。

    动作写回常跨库（approval/concentration/project/customer/base），同连接 BEGIN
    IMMEDIATE → COMMIT 覆盖全部附库（SQLite 单连接跨库事务原子）；沿用 Store 单写
    连接串行语义（§3.4）。
    """

    ATTACH_DBS: tuple[str, ...] = (
        "approval",
        "concentration",
        "project",
        "customer",
        "base",
    )

    def __init__(
        self,
        ontology_path: str | Path | None = None,
        ap_dir: str | Path | None = None,
    ) -> None:
        d = Path(ap_dir) if ap_dir else AP_ANPING_DIR
        super().__init__(
            source_path=d / "risk.db",
            ontology_path=ontology_path or DEFAULT_RISK_ONTOLOGY_DB,
        )

    def source_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._source_path))
        conn.row_factory = sqlite3.Row
        for alias in self.ATTACH_DBS:
            conn.execute(
                f"ATTACH DATABASE ? AS {alias}",
                (str(self._source_path.parent / f"{alias}.db"),),
            )
        return conn


def risk_seq_id(
    conn: sqlite3.Connection, table: str, pk_field: str, prefix: str, width: int = 8
) -> str:
    """取源表主键末 width 位流水 max+1，拼 {PREFIX}-{year}-{8位}（编码规则 4）。

    源主键形如 PROJ-2026-00001234，末 8 位即流水号（SUBSTR 负偏移）。
    """
    row = conn.execute(
        f"SELECT MAX(CAST(SUBSTR({pk_field}, -{width}) AS INTEGER)) AS m FROM {table}"
    ).fetchone()
    seq = (row[0] or 0) + 1
    return f"{prefix}-{RISK_DEMO_YEAR:04d}-{seq:0{width}d}"


def build_risk_source_registry() -> Registry:
    """风险本体独立注册 + 源表名适配（逻辑表名 → ap_anping 真实表）。

    供 ActionEngine / ObjectIndex 消费：self_check 在独立注册表上全绿（对象/链接/
    动作语义不变），source_table 改写到真实表后 refresh/load 可读真实数据。
    ObjectTypeDef 用 model_copy 避免污染共享 RISK_OBJECT_TYPES（单一真相）。
    """
    reg = Registry()
    register_risk_objects(reg)
    for obj in list(reg.object_types()):
        real = SOURCE_TABLE_MAP.get(obj.name)
        if real and obj.source_table != real:
            reg._objects[obj.name] = obj.model_copy(update={"source_table": real})
    return reg
