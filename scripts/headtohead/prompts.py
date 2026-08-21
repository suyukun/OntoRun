"""A/B 两形态的 LLM 提示词构建（schema 提示 + 契约 schema 提示）。"""
from __future__ import annotations

from src.des.metrics import MetricRegistry

# 18 表 schema 一览（A 形态 NL2SQL 提示用）
TABLE_SCHEMA = {
    "erp.db": {
        "KNA1": ["KUNNR", "NAME1", "KTOKD", "ORT01"],
        "MARA": ["MATNR", "MAKTX", "MTART", "BISMT", "MEINS", "MATKL", "ERDAT"],
        "MARC": ["MATNR", "WERKS", "MAABC", "DISPO", "EKGRP"],
        "MARD": ["MATNR", "WERKS", "LGORT", "LABST", "INSME", "SPEME"],
        "MAST": ["MATNR", "WERKS", "STLNR", "STLAN"],
        "STPO": ["STLNR", "STLKN", "IDNRK", "MENGE", "MEINS"],
        "VBAK": ["VBELN", "KUNNR", "AUDAT", "NETWR", "VKORG"],
        "VBAP": ["VBELN", "POSNR", "MATNR", "KWMENG", "MEINS", "NETWR"],
    },
    "mes.db": {
        "MPLA": ["MPLA_ID", "MATNR", "CHARG", "WERKS", "ARBPL", "VERID", "DISPO"],
        "AUFK": ["AUFNR", "MATNR", "AUART", "WERKS", "FTRMS", "STATUS"],
        "AFPO": ["AUFNR", "POSNR", "MATNR", "GAMNG", "MEINS"],
        "COFV": ["CONFNR", "AUFNR", "MATNR", "WERKS", "ARBPL", "DATUM", "ISM01", "ISMN1"],
    },
    "wms.db": {
        "WMMD": ["MATNR", "LGORT", "LGPBE", "MEINS", "BESTQ", "ERDAT"],
        "MSEG": ["MBLNR", "ZEILE", "MATNR", "WERKS", "LGORT", "BWART", "MENGE", "MEINS", "BUDAT", "EBELN", "AUFNR"],
    },
    "scm.db": {
        "LFA1": ["LIFNR", "NAME1", "ORT01", "LAND1"],
        "EKKO": ["EBELN", "LIFNR", "BSART", "AEDAT"],
        "EKPO": ["EBELN", "EBELP", "MATNR", "MENGE", "MEINS", "NETWR"],
    },
    "fin.db": {
        "ACDOCA": ["BELNR", "POSNR", "RACCT", "KOSTL", "WSL", "BUDAT", "REF_DOC", "REF_TYPE"],
    },
}

COL_HINTS = {
    "KNA1.KTOKD": "客户账户组：0001 零售 / 0002 中小企业 / 0003 集团（corporate=0003）",
    "MARA.BISMT": "旧码，仅一物多码物料非空",
    "MARA.MTART": "物料类型：FERT成品/HALB半成品/ROH原材料/VERP包装/HAWA贸易商品",
    "MARA.MATKL": "物料组（品类），形如 Z-<TYPE>-NN",
    "MARD.LABST": "库存账面（非限制库存量）",
    "MARD.WERKS": "工厂：PL01/PL02", "MARD.LGORT": "仓库：W01/W02/W03",
    "MSEG.BWART": "移动类型：101采购收货(+)/301移库(±)/201发料(-)/261生产发料(-)",
    "MSEG.MENGE": "带符号数量：收货正、发料负",
    "ACDOCA.REF_TYPE": "参考单据类型：SO销售订单/PO采购订单/MV库存移动",
    "ACDOCA.WSL": "金额，借正贷负（SO+WSL<0 视为退款）",
    "AUFK.STATUS": "工单状态：REL下达/PCNF部分确认/DLV交付/CLSD关闭",
    "AUFK.FTRMS": "工单计划完成日期", "COFV.DATUM": "报工日期", "COFV.ISM01": "报工数量", "COFV.ISMN1": "报工工时",
    "VBAK.AUDAT": "销售订单日期", "VBAK.NETWR": "订单净额", "VBAP.NETWR": "项目净额", "VBAP.KWMENG": "项目数量",
    "EKKO.AEDAT": "采购订单日期", "EKPO.NETWR": "采购项目金额", "EKPO.MENGE": "采购项目数量",
}

BUSINESS_NOTE = (
    "业务语义：客户=customer(KNA1)，销售订单=orders(VBAK 抬头 + VBAP 项目，按 VBELN 关联)，"
    "库存账面=inventory(MARD)，库存流水=wms.MSEG，采购=purchase(EKKO 抬头 + EKPO 项目)，"
    "财务=finance(ACDOCA)，供应商=vendor(LFA1)，生产工单=production(AUFK/COFV)，物料=material(MARA)。\n"
    "日期字段：AUDAT(销售)/AEDAT(采购)/BUDAT(财务、库存流水)/DATUM(报工)，全表覆盖 2025-01-01 至 2026-12-31。\n"
    "「月」= substr(日期,1,7)（YYYY-MM）；「季度」= 年||'Q'||(FLOOR((月-1)/3)+1)。"
)


def build_a_schema() -> str:
    lines = ["## 可用数据表（DuckDB sqlite_scan 跨库，库文件名即第一个参数）", ""]
    for db, tables in TABLE_SCHEMA.items():
        lines.append(f"### {db}")
        for t, cols in tables.items():
            hint = "".join(f"\n    - {c}: {COL_HINTS.get(t + '.' + c, '')}" for c in cols if COL_HINTS.get(t + '.' + c))
            lines.append(f"- {t}({', '.join(cols)}){hint}")
    lines.append("")
    lines.append(BUSINESS_NOTE)
    return "\n".join(lines)


A_SYSTEM = (
    "你是制造业企业数据分析师，只输出 DuckDB 可执行的 SELECT 查询。\n"
    "规则：\n"
    "1. 所有数据表已注册为视图，直接写裸表名即可：FROM VBAK JOIN VBAP ON ...（不要写库名前缀如 erp.VBAK / fin.ACDOCA；"
    "表名必须来自给定 schema，禁任何其他数据源/函数，禁 read_csv/read_parquet/glob/系统表）。\n"
    "2. 单条 SELECT 语句（可含 WITH/UNION ALL），禁止 ; 多语句、禁止注释、禁止 DDL/DML（insert/update/delete/drop/alter/create）。\n"
    "3. 输出必须是合法 JSON：{\"sql\": \"...\"}，不要输出其他文字。\n"
    "4. 输出列的顺序必须与题目要求的输出列顺序完全一致，不得多列或少列。\n"
    "5. 金额/数量用 ROUND(x, 2) 保留两位小数。\n"
)



def build_a_prompt(ask: str, expected_cols: str, extra: str = "") -> list[dict]:
    return [
        {"role": "system", "content": A_SYSTEM + "\n\n" + build_a_schema()},
        {"role": "user", "content": (
            f"题目：{ask}\n"
            f"期望输出列（按此顺序）：{expected_cols}\n"
            f"{('补充口径：' + extra + chr(10)) if extra else ''}"
            "请生成 DuckDB SQL（JSON 格式 {\"sql\": \"...\"}）。"
        )},
    ]


# ---------------- B 形态：契约 surface ----------------
B_OBJECT_SURFACE = (
    "## 本体对象（v0.1 对象路径）\n"
    "- Material（material）：matnr, name, material_type(FERT/HALB/ROH/VERP/HAWA), plm_code, mes_code, "
    "old_code(仅一物多码非空), base_unit, material_group, created_date。链接 material.codes（1 跳）。\n"
    "- Code（code）：code_id, code_space(plm/erp/mes/wms/legacy), value, material_matnr。\n"
)

B_CONTRACT_SCHEMA = (
    "## 契约 schema（v0.1/v0.2）\n"
    "- v0.1 对象路径：{\"contract_version\": \"0.1\", \"object_type\": \"Material\", \"filters\": {...}, "
    "\"aggregations\": [{\"function\": ..., \"field\": ...}], \"group_by\": [...], \"link_traversal\": {...}|null}\n"
    "  - filters 操作符：eq/ne/is_null/is_not_null/in；如 {\"old_code\": {\"op\": \"is_not_null\"}}\n"
    "  - aggregations.function ∈ count/sum/avg/min/max/count_distinct；field 可为字段名或 \"*\"（仅 count）\n"
    "- v0.2 指标路径：{\"contract_version\": \"0.2\", \"metric\": {\"metric_id\": ..., "
    "\"dimension_filters\": {...}, \"time_range\": {\"from\": \"YYYY-MM-DD\", \"to\": \"YYYY-MM-DD\"}, "
    "\"group_by\": [...]}}\n"
    "  - metric 存在时不要求 object_type/aggregations；group_by 只能取该指标维度字段子集；\n"
    "  - 非 metric 契约（v0.1 对象路径）不支持 time_range（会 fail-closed 拒答）。\n"
)

B_METRIC_CATALOG = (
    "## 指标注册表（v0.2 指标路径，metric_id 必须精确命中；维度名须与列名一致）\n"
)


def build_b_surface(metrics: MetricRegistry) -> str:
    lines = [B_OBJECT_SURFACE, "", B_METRIC_CATALOG]
    for m in metrics.metrics:
        dims = ", ".join(f"{d.name}" for d in m.dimension_fields)
        lines.append(
            f"- {m.metric_id}: 主体 {m.object_type}，维度 [{dims}]，度量 {m.measure.name}，聚合 {m.agg_function}"
        )
    lines.append("")
    lines.append(
        "### 指标语义\n"
        "- sales_*: 销售金额/数量（VBAK 月 AUDAT）；stock_*: 库存账面(月/不按月)；purchase_*: 采购（EKKO 月 AEDAT）；"
        "finance_*: 财务（ACDOCA 月 BUDAT）；mat_count_*: 物料计数。\n"
        "- 物化指标表预聚合，维度过滤只能作用在维度列上，不能按度量值过滤。"
    )
    return "\n".join(lines)


B_SYSTEM = (
    "你是本体查询契约生成器：把用户的中文分析问题映射为本体受限结构化查询契约。\n"
    "规则：\n"
    "1. 若问题能用给定的对象路径（Material/Code + material.codes）或指标注册表表达，输出契约 JSON："
    "{\"contract\": {...}}。\n"
    "2. 若问题需要的语义（表/字段/聚合/链接）不在上述受限面内，禁止编造，输出 "
    "{\"refused\": true, \"reason\": \"...\"} 说明哪个语义受限。\n"
    "3. 契约字段必须精确使用给定的对象字段名/指标 metric_id/维度名。\n"
    "4. 只输出一个 JSON，不要输出其他文字。\n"
)


def build_b_prompt(ask: str, surface: str) -> list[dict]:
    return [
        {"role": "system", "content": B_SYSTEM + "\n\n" + surface + "\n" + B_CONTRACT_SCHEMA},
        {"role": "user", "content": f"题目：{ask}\n请生成契约 JSON 或 refusal。"},
    ]
