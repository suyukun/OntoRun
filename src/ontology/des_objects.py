"""DES 垂直切片本体对象 —— Material（物料概念）+ Code（编码对象）+ hasCode 链接，
+ P2 ChatBI 主体对象（Vendor / InventoryLocation / FinanceEntry，2026-08-21 Jack 拍板注册）。
+（Customer 主体对象复用 S1 零售 Customer，同一注册表，见 src/ontology/objects.py。）

source_table 语义（P2 接线，报告 §5 缺口修复）：一律指向本体物化器落盘的表名
（material/codes/vendor/inventory_location/finance_entry，见 src/des/materialize.py），
与 Material/Code 同范式；权威源表（scm.LFA1 / erp.MARD / fin.ACDOCA）语义由指标注册表
source_tables 与物化 SQL 承载——注册对象即可查询对象，不再出现「已注册但源表未接线」。

依据 docs/P1a-本体映射与查询契约设计_v0.1.md §1.2/§1.4：
- Material = 跨 3 源系统（ERP/MES/WMS）物化的物料概念，join key = MATNR，字段内嵌 4 码位
  （属性承载查询：filters/聚合直接命中，不必每次遍历链接，设计 §1.1）；
- Code = 码空间的图表达（一码一对象），经 hasCode（material.codes）归属到 Material
  （关系承载语义：编码归属可遍历、可审计、可扩码空间，设计 §1.1）；
- 冗余是刻意的：属性承载查询、关系承载语义（Palantir「对象属性与关系并存」做法）。

self_check 两条检查（设计 §1.4 表，经 Registry 扩展点 des_self_checks 挂载）：
- CODE_SPACE_ENUM_VALID：Code.code_space 必须 ∈ {plm, erp, mes, wms, legacy}；
- MULTI_CODE_FIELD_CONSISTENT：Material.old_code 非空 ⟺ 该物料存在 code_space="legacy"
  的 Code 行（双向一致，防字段/图层双轨漂移）。
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel

from src.ontology.links import LinkTypeDef
from src.ontology.objects import OWN_DERIVED, OWN_SOURCE, ObjectTypeDef, own
from src.ontology.registry import Issue

MaterialType = Literal["FERT", "HALB", "ROH", "VERP", "HAWA"]  # 对齐 SAP MTART

# 码空间全集（设计 §1.3：plm/erp/mes = 三编码，wms = 采用主码，legacy = 旧码 BISMT）
CODE_SPACES: tuple[str, ...] = ("plm", "erp", "mes", "wms", "legacy")


class Material(BaseModel):
    """物料概念。PK/Title = matnr（ERP 主码，跨系统 join key）。"""

    matnr: str = own(
        OWN_SOURCE, "物料号（ERP 主码，PK/Title；跨系统 join key，erp/mes/wms 三表同值）"
    )
    name: str = own(OWN_SOURCE, "物料描述（权威列 ERP.MARA.MAKTX）")
    material_type: MaterialType = own(OWN_SOURCE, "物料类型（权威列 ERP.MARA.MTART）")
    plm_code: str = own(
        OWN_DERIVED, "PLM 编码（工程主数据签发的主码视角；本切片与 matnr 同值，见设计 §1.3）"
    )
    mes_code: str = own(
        OWN_DERIVED, "MES 编码 = MPLA_ID = 'MP-' + matnr（物化自 MES.MPLA，计算态）"
    )
    old_code: str | None = own(
        OWN_SOURCE,
        "旧码 BISMT（权威列 ERP.MARA.BISMT，仅一物多码行非空；多码冲突点，见设计 §2）",
        default=None,
    )
    base_unit: str = own(OWN_SOURCE, "基本计量单位（权威列 ERP.MARA.MEINS，与 WMS 一致，门禁 D3）")
    material_group: str = own(OWN_SOURCE, "物料组（权威列 ERP.MARA.MATKL）")
    created_date: date = own(OWN_SOURCE, "创建日期（权威列 ERP.MARA.ERDAT，seed 确定性）")


class Code(BaseModel):
    """系统编码对象。PK = code_id（"{code_space}:{value}"）。一码一对象，归属一个物料概念。"""

    code_id: str = own(OWN_SOURCE, "编码记录号（PK，派生自 code_space + value）")
    code_space: Literal["plm", "erp", "mes", "wms", "legacy"] = own(
        OWN_SOURCE, "码空间：plm/erp/mes = 设计 §1.3 三编码，wms = 采用主码，legacy = 旧码 BISMT"
    )
    value: str = own(OWN_SOURCE, "编码值（权威列：MATNR / MPLA_ID / BISMT）")
    material_matnr: str = own(OWN_SOURCE, "归属物料（FK -> Material.matnr，hasCode 链接承载）")


class Vendor(BaseModel):
    """供应商（DES：采购主体，权威表 SCM.LFA1）。PK/Title = vendor_id。"""

    vendor_id: str = own(OWN_SOURCE, "供应商号（PK/Title，权威列 SCM.LFA1.LIFNR）")
    name: str = own(OWN_SOURCE, "供应商名称（权威列 SCM.LFA1.NAME1）")
    city: str = own(OWN_SOURCE, "所在城市（权威列 SCM.LFA1.ORT01）")
    country: str = own(OWN_SOURCE, "国家/地区（权威列 SCM.LFA1.LAND1）")


class InventoryLocation(BaseModel):
    """库存地点（DES：ERP.MARD 地点粒度 WERKS+LGORT）。PK = location_id 派生。"""

    location_id: str = own(
        OWN_SOURCE, "库存地点号（PK，派生自 factory + location，'{WERKS}|{LGORT}'）"
    )
    factory: str = own(OWN_SOURCE, "工厂（权威列 ERP.MARD.WERKS，指标维度 factory）")
    location: str = own(
        OWN_SOURCE, "库存地点（权威列 ERP.MARD.LGORT / WMS.MSEG.LGORT，指标维度 location）"
    )


class FinanceEntry(BaseModel):
    """财务凭证行（DES：权威表 FIN.ACDOCA）。PK = entry_id 派生自 BELNR+POSNR。"""

    entry_id: str = own(
        OWN_SOURCE, "财务凭证行号（PK，派生自 belnr + posnr，'{BELNR}|{POSNR}'）"
    )
    belnr: str = own(OWN_SOURCE, "会计凭证号（权威列 FIN.ACDOCA.BELNR）")
    posnr: str = own(OWN_SOURCE, "凭证行项目（权威列 FIN.ACDOCA.POSNR）")
    account: str = own(OWN_SOURCE, "会计科目（权威列 FIN.ACDOCA.RACCT，指标维度 account）")
    cost_center: str = own(OWN_SOURCE, "成本中心（权威列 FIN.ACDOCA.KOSTL，指标维度 cost_center）")
    amount: float = own(OWN_SOURCE, "金额（借正/贷负，权威列 FIN.ACDOCA.WSL，指标度量 amount）")
    post_date: str = own(OWN_SOURCE, "过账日期 YYYY-MM-DD（权威列 FIN.ACDOCA.BUDAT，指标月维度源）")
    ref_type: str = own(OWN_SOURCE, "参考单据类型 SO/PO/MV（权威列 FIN.ACDOCA.REF_TYPE，指标维度 ref_type）")
    ref_doc: str = own(OWN_SOURCE, "参考单据号（权威列 FIN.ACDOCA.REF_DOC；SO=订单号，退款链路查询用）")


# hasCode 链接：Material 1:N Code（1 概念多编码），FK 在 Code（target 侧）——
# 对齐 S1「1:N → 外键在 target」约定（src/ontology/links.py 头注释）
HAS_CODE_LINK = LinkTypeDef(
    name="material.codes",
    source_type="Material",
    target_type="Code",
    cardinality="1:N",
    fk_field="material_matnr",
    inverse_name="code.material",
    description="编码归属：一个物料概念有多个系统编码（hasCode 多值，3 系统编码 → 1 概念）",
)

# 物化表名（与 src/des/materialize.py 落盘的 SQLite 物化库表名对齐）
DES_OBJECT_TYPES: list[ObjectTypeDef] = [
    ObjectTypeDef(
        name="Material",
        api_name="material",
        description="物料概念（DES：1 概念跨 3 源系统，join key = MATNR）",
        model=Material,
        pk_field="matnr",
        title_field="matnr",
        source_table="material",
    ),
    ObjectTypeDef(
        name="Code",
        api_name="code",
        description="系统编码（DES：一码一对象，hasCode 归属物料）",
        model=Code,
        pk_field="code_id",
        title_field="code_id",
        source_table="codes",
    ),
    ObjectTypeDef(
        name="Vendor",
        api_name="vendor",
        description="供应商（DES：采购主体，权威表 scm.LFA1，PK = LIFNR）",
        model=Vendor,
        pk_field="vendor_id",
        title_field="vendor_id",
        source_table="vendor",
    ),
    ObjectTypeDef(
        name="InventoryLocation",
        api_name="inventory_location",
        description="库存地点（DES：ERP.MARD 地点粒度 WERKS+LGORT）",
        model=InventoryLocation,
        pk_field="location_id",
        title_field="location_id",
        source_table="inventory_location",
    ),
    ObjectTypeDef(
        name="FinanceEntry",
        api_name="finance_entry",
        description="财务凭证行（DES：权威表 fin.ACDOCA，PK = BELNR+POSNR）",
        model=FinanceEntry,
        pk_field="entry_id",
        title_field="entry_id",
        source_table="finance_entry",
    ),
]

DES_LINK_TYPES: list[LinkTypeDef] = [HAS_CODE_LINK]


# ---------------------------------------------------------------------------
# self_check 扩展点：CODE_SPACE_ENUM_VALID / MULTI_CODE_FIELD_CONSISTENT（设计 §1.4 表）
# ---------------------------------------------------------------------------
def des_self_checks(
    registry: Any, instance_data: dict[str, list[dict[str, Any]]] | None = None
) -> list[Issue]:
    """DES 对象 self_check（经 Registry.add_self_check 挂载）。

    instance_data 形如 {对象类型名: [行 dict, ...]}（如 {"Material": [...], "Code": [...]}），
    由本体物化器在物化后提供；无数据时只跑 schema 层检查（CODE_SPACE_ENUM_VALID 模型枚举）。
    """
    issues: list[Issue] = []
    if not (registry.has_object_type("Code") and registry.has_object_type("Material")):
        return issues  # 通用 registry 无 DES 对象时跳过（不误报）
    issues.extend(_check_code_space_enum_schema(registry))
    if instance_data:
        issues.extend(_check_code_space_enum_data(instance_data))
        issues.extend(_check_multi_code_consistency(instance_data))
    return issues


def _check_code_space_enum_schema(registry: Any) -> list[Issue]:
    """CODE_SPACE_ENUM_VALID（schema 层）：Code.code_space 的 Literal 枚举 == 码空间全集。"""
    annotation = registry.object_type("Code").model.model_fields["code_space"].annotation
    if get_origin(annotation) is not Literal:
        return [
            Issue(
                severity="error",
                code="CODE_SPACE_ENUM_VALID",
                message="Code.code_space 必须为 Literal 码空间枚举",
            )
        ]
    declared = set(get_args(annotation))
    if declared != set(CODE_SPACES):
        return [
            Issue(
                severity="error",
                code="CODE_SPACE_ENUM_VALID",
                message=f"Code.code_space 枚举 {sorted(declared)} ≠ 码空间全集 {list(CODE_SPACES)}",
            )
        ]
    return []


def _check_code_space_enum_data(instance_data: dict[str, list[dict[str, Any]]]) -> list[Issue]:
    """CODE_SPACE_ENUM_VALID（实例层）：Code 行 code_space 必须落在全集内。"""
    codes = instance_data.get("Code", [])
    bad = sorted({c["code_space"] for c in codes if c.get("code_space") not in CODE_SPACES})
    if bad:
        return [
            Issue(
                severity="error",
                code="CODE_SPACE_ENUM_VALID",
                message=f"Code 行存在非法码空间: {bad}",
            )
        ]
    return []


def _check_multi_code_consistency(instance_data: dict[str, list[dict[str, Any]]]) -> list[Issue]:
    """MULTI_CODE_FIELD_CONSISTENT：old_code 非空 ⟺ 存在 legacy Code 行（双向一致）。"""
    materials = instance_data.get("Material", [])
    codes = instance_data.get("Code", [])
    with_old = {m["matnr"] for m in materials if m.get("old_code") is not None}
    with_legacy = {c["material_matnr"] for c in codes if c.get("code_space") == "legacy"}
    drift = sorted(with_old.symmetric_difference(with_legacy))
    if drift:
        return [
            Issue(
                severity="error",
                code="MULTI_CODE_FIELD_CONSISTENT",
                message=f"old_code 非空物料与 legacy Code 行不一致（双轨漂移）: {drift}",
            )
        ]
    return []
