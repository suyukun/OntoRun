#!/usr/bin/env python3
"""S3 M1b 脚手架：由 docs/S3-M1a-字段脱敏映射-全量42表.json 生成 42 张新表 DDL 源码。

产出（字面 CREATE TABLE 字符串，与脊柱 risk_ddl.py 同风格）：
    src/des/generators/risk_ddl_ext.py   —— customer(11) + risk(11) = 22 表
    src/des/generators/risk_ddl_ext2.py  —— concentration(4) + approval(3) + project(2) + base(11) = 20 表
字段类型推断规则（infer_type）+ 手工覆盖 TYPE_OVERRIDES（单一事实来源）；PK 列置首；
列注释取 field_comments；clear_remark_* 可空，其余 NOT NULL。dict key = {system}.{table}（与 RISK_DDL 一致）。
表名 = 脱敏名（JSON key）；source_table（原型 o_a_erms_*/p_erms_*）只进模块注释溯源，不进表名/字段名。

用法：/opt/anaconda3/bin/python3 scripts/s3_m1b_scaffold_risk_ext.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "S3-M1a-字段脱敏映射-全量42表.json"
OUT_EXT = ROOT / "src" / "des" / "generators" / "risk_ddl_ext.py"
OUT_EXT2 = ROOT / "src" / "des" / "generators" / "risk_ddl_ext2.py"

# 系统 → 表清单（(system, table, pk)；顺序即 DDL 文件内顺序；与 des_risk_industry_template.yaml 注册表一致）
CUSTOMER_TABLES = [
    ("customer", "ap_customer_relation", "customer_relation_id"),
    ("customer", "ap_customer_relation_tree", "customer_relation_tree_id"),
    ("customer", "ap_important_customer_list", "important_customer_id"),
    ("customer", "ap_top500_customer_risk", "top500_customer_id"),
    ("customer", "ap_customer_assets", "customer_assets_id"),
    ("customer", "ap_customer_invest_dist", "customer_invest_dist_id"),
    ("customer", "ap_subsidiary_credit_detail", "project_id"),
    ("customer", "ap_collateral", "collateral_id"),
    ("customer", "ap_subsidiary_mortgage", "subsidiary_mortgage_id"),
    ("customer", "ap_bank_pledge_detail", "bank_pledge_id"),
    ("customer", "ap_securities_pledge_detail", "securities_pledge_id"),
]
RISK_TABLES = [
    ("risk", "ap_warning_push", "warning_push_id"),
    ("risk", "ap_audit_detail", "audit_id"),
    ("risk", "ap_compliance_risk_ledger", "compliance_risk_id"),
    ("risk", "ap_compliance_risk_ledger_tmp", "compliance_risk_tmp_id"),
    ("risk", "ap_regulatory_penalty", "penalty_id"),
    ("risk", "ap_warn_signal_concentration", "concentration_signal_id"),
    ("risk", "ap_warn_signal_derive", "derive_warning_id"),
    ("risk", "ap_warn_derive_deal_detail", "derive_deal_detail_id"),
    ("risk", "ap_warn_derive_sub_push", "derive_sub_push_id"),
    ("risk", "ap_warn_signal_deviation", "deviation_signal_id"),
    ("risk", "ap_deviation_warn_score", "deviation_warn_score_id"),
]
CONCENTRATION_TABLES = [
    ("concentration", "ap_concentration_limit_adj", "concentration_limit_adj_id"),
    ("concentration", "ap_concentration_warn_adj", "concentration_warn_adj_id"),
    ("concentration", "ap_codebt_customer", "codebt_customer_id"),
    ("concentration", "ap_codebt_warn_score", "codebt_warn_score_id"),
]
APPROVAL_TABLES = [
    ("approval", "ap_approve_oper_log", "approve_log_id"),
    ("approval", "ap_approve_warn_rel", "approve_warn_rel_id"),
    ("approval", "ap_approve_todo", "approve_todo_id"),
]
PROJECT_TABLES = [
    ("project", "ap_cust_query_log", "cust_query_log_id"),
    ("project", "ap_serial_counter", "serial_counter_id"),
]
BASE_TABLES = [
    ("base", "ap_metric_std", "index_id"),
    ("base", "ap_dim_rank", "dim_rank_id"),
    ("base", "ap_custom_param", "custom_param_id"),
    ("base", "ap_preference_file", "preference_file_id"),
    ("base", "ap_supervise_opinion", "supervise_opinion_id"),
    ("base", "ap_top_query_log", "top_query_log_id"),
    ("base", "ap_data_dict", "dict_id"),
    ("base", "ap_sys_param", "sys_param_id"),
    ("base", "ap_org", "org_id"),
    ("base", "ap_user", "user_id"),
    ("base", "ap_biz_dict", "biz_dict_id"),
]

# 字段类型覆盖（推断规则的例外，单一事实来源）
TYPE_OVERRIDES: dict[str, dict[str, str]] = {
    "ap_serial_counter": {"current_counter": "INTEGER", "date_str": "TEXT"},
    "ap_cust_query_log": {"data_flag": "INTEGER"},
    "ap_user": {"user_num": "TEXT", "sex_code": "TEXT", "pass_error_count": "INTEGER", "login_succ_count": "INTEGER"},
    "ap_org": {"sort_no": "INTEGER", "parent_org_code": "TEXT"},
    "ap_biz_dict": {"dict_value": "TEXT", "sort_no": "INTEGER", "is_sealed": "INTEGER", "is_deleted": "INTEGER"},
    "ap_data_dict": {"dict_value": "TEXT", "dict_seq": "INTEGER", "status_code": "INTEGER", "del_ind": "INTEGER"},
    "ap_sys_param": {"param_value": "TEXT", "whether_cache": "INTEGER", "del_ind": "INTEGER"},
    "ap_supervise_opinion": {"year_time": "TEXT"},
    "ap_metric_std": {"index_value": "REAL"},
    "ap_dim_rank": {"index_value": "REAL"},
    "ap_custom_param": {"index_value": "REAL", "del_ind": "INTEGER"},
    "ap_important_customer_list": {
        "important_customer_flag": "INTEGER", "risk_customer_flag": "INTEGER",
        "custom_customer_flag": "INTEGER", "is_real_estate": "INTEGER", "is_high_leverage": "INTEGER",
    },
    "ap_top500_customer_risk": {
        "group_member_count": "INTEGER", "concentration_degree": "REAL",
        "invest_balance": "REAL", "risk_exposure": "REAL", "risk_asset_balance": "REAL",
        "invest_balance_new": "REAL", "warn_flag": "INTEGER",
    },
    "ap_customer_assets": {
        "invest_balance": "REAL", "risk_exposure": "REAL", "risk_asset_balance": "REAL", "invest_balance_new": "REAL",
    },
    "ap_customer_invest_dist": {
        "invest_balance": "REAL", "risk_exposure": "REAL", "risk_asset_balance": "REAL",
        "risk_bad_balance": "REAL", "invest_balance_new": "REAL",
    },
    "ap_subsidiary_credit_detail": {
        "group_peer_flag": "INTEGER", "related_party_ind": "INTEGER", "peer_flag": "INTEGER",
        "registered_capital": "REAL", "business_balance": "REAL", "risk_exposure": "REAL",
        "pledge_value": "REAL", "guarantee_value": "REAL", "impairment_provision": "REAL",
        "limit_value": "REAL", "principal_overdue_days": "INTEGER", "interest_overdue_days": "INTEGER",
        "shareholder_ratio_1": "REAL", "shareholder_ratio_2": "REAL", "shareholder_ratio_3": "REAL",
        "invest_amount_1": "REAL", "invest_ratio_1": "REAL", "invest_amount_2": "REAL",
        "invest_ratio_2": "REAL", "invest_amount_3": "REAL", "invest_ratio_3": "REAL",
        "final_score": "REAL", "industry_commerce_index": "REAL", "trading_index": "REAL",
        "credit_index": "REAL", "credit_reference_index": "REAL", "financial_index": "REAL",
    },
    "ap_collateral": {
        "guarantee_contract_amount": "REAL", "guarantee_repay_order": "INTEGER",
        "mortgage_ind": "INTEGER", "is_have_external_estimate_org": "INTEGER",
        "estimate_value": "REAL", "corp_identify_value": "REAL", "mortgaged_value": "REAL",
        "mortgage_rate": "REAL", "maintenance_rate": "REAL",
        "is_mortgage_registered": "INTEGER", "is_major_guarantee_collateral": "INTEGER",
    },
    "ap_subsidiary_mortgage": {
        "mortgage_ind": "INTEGER", "total_count": "INTEGER", "estimate_value": "REAL",
        "corp_identify_value": "REAL", "mortgaged_value": "REAL", "estimate_quantity": "INTEGER",
        "percent_value": "REAL",
    },
    "ap_bank_pledge_detail": {
        "guarantee_contract_amount": "REAL", "guarantee_contract_balance": "REAL",
        "guarantee_repay_order": "INTEGER", "mortgage_ind": "INTEGER",
        "is_have_external_estimate_org": "INTEGER", "initial_estimate_value": "REAL",
        "latest_estimate_value": "REAL", "disposal_value": "REAL", "mortgaged_value": "REAL",
        "mortgage_rate": "REAL", "maintenance_rate": "REAL",
        "is_mortgage_registered": "INTEGER",
    },
    "ap_securities_pledge_detail": {
        "invest_value": "REAL", "pledge_subject_value": "REAL", "bonus_amount": "REAL", "maintenance_rate": "REAL",
    },
    "ap_compliance_risk_ledger": {"penalty_percent": "REAL", "expect_penalty_amount": "REAL"},
    "ap_compliance_risk_ledger_tmp": {"penalty_percent": "REAL", "expect_penalty_amount": "REAL"},
    "ap_regulatory_penalty": {
        "penalty_amount": "REAL", "confiscation_amount": "REAL", "rectification_complete_flag": "INTEGER",
    },
    "ap_codebt_customer": {
        "group_member_count": "INTEGER", "subsidiary_count": "INTEGER",
        "invest_balance": "REAL", "risk_exposure": "REAL", "is_deleted": "INTEGER",
    },
    "ap_codebt_warn_score": {
        "risk_exposure": "REAL", "invest_balance": "REAL", "signal_count": "INTEGER",
        "red_signal_count": "INTEGER", "blue_signal_count": "INTEGER", "yellow_signal_count": "INTEGER",
        "subsidiary_count": "INTEGER", "top10_risk_exposure_avg": "REAL", "score": "REAL",
    },
    "ap_warn_signal_concentration": {
        "group_member_count": "INTEGER", "invest_balance": "REAL", "risk_exposure": "REAL",
        "concentration_degree": "REAL", "concentration_limit": "REAL", "risk_warning_threshold": "REAL",
        "is_deleted": "INTEGER",
    },
    "ap_warn_signal_derive": {"is_deleted": "INTEGER", "is_holding_add": "INTEGER"},
    "ap_warn_derive_deal_detail": {"is_deleted": "INTEGER"},
    "ap_warn_derive_sub_push": {"is_deleted": "INTEGER", "etl_job_flag": "INTEGER"},
    "ap_warn_signal_deviation": {
        "group_member_count": "INTEGER", "invest_balance": "REAL", "risk_exposure": "REAL",
        "mom": "REAL", "mgr": "REAL", "ytd": "REAL", "is_deleted": "INTEGER",
    },
    "ap_deviation_warn_score": {
        "risk_exposure": "REAL", "invest_balance": "REAL", "mom": "REAL", "ytd": "REAL", "mgr": "REAL",
        "score": "REAL", "exposure_change": "REAL", "signal_strength": "REAL",
        "is_disposal_needed": "INTEGER", "variation": "REAL",
    },
    "ap_approve_oper_log": {"ext": "TEXT"},
    "ap_approve_warn_rel": {"is_deleted": "INTEGER"},
    "ap_approve_todo": {"is_deleted": "INTEGER"},
}


def infer_type(field: str) -> str:
    """默认类型推断（被 TYPE_OVERRIDES 覆盖）。"""
    f = field.lower()
    if f.startswith("is_") or f.endswith(("_flag", "_ind", "_mark", "_count", "_num")):
        return "INTEGER"
    if f in ("del_ind", "is_deleted", "del_flag", "whether_cache", "data_flag", "rectification_complete_flag"):
        return "INTEGER"
    if f.endswith("_quantity") or f.endswith("_sort_no"):
        return "INTEGER"
    if f.endswith((
        "_amount", "_balance", "_value", "_exposure", "_limit", "_score", "_ratio",
        "_rate", "_percent", "_degree", "_provision", "_variation", "_strength", "_change",
    )) or f in ("mom", "mgr", "ytd", "index_value", "score", "penalty_percent",
                "concentration_degree", "exposure_change", "signal_strength", "top10_risk_exposure_avg"):
        return "REAL"
    if "_date" in f or "_time" in f or "_day" in f or f.endswith("_year"):
        return "TEXT"
    return "TEXT"


def build_ddl(table: str, pk: str, fields: list[tuple[str, str, str]]) -> str:
    """由字段列表生成 CREATE TABLE（PK 列置首，其余按 JSON 顺序；clear_remark_* 可空）。
    列注释取 field_comments（字段元组第 2 项）；逗号置于列定义后、注释前（SQLite 无尾逗号）。"""
    overrides = TYPE_OVERRIDES.get(table, {})
    comments = {n: c for n, c, _ in fields}
    names = [n for n, _, _ in fields]
    ordered = [pk] + [n for n in names if n != pk]
    col_lines: list[str] = []
    for i, name in enumerate(ordered):
        ftype = overrides.get(name, infer_type(name))
        nullable = "" if name.startswith("clear_remark_") else " NOT NULL"
        comma = "," if i < len(ordered) - 1 else ""
        col_lines.append(f"  {name} {ftype}{nullable}{comma}  -- {comments.get(name, '')}")
    body = "\n".join(col_lines)
    return f"CREATE TABLE {table} (\n{body}\n);"


def emit(header: str, tables: list[tuple[str, str, str]], data: dict, sys_prefix: str) -> str:
    out = [header, ""]
    ddls: list[str] = []
    for system, table, pk in tables:
        v = data[table]
        fields = [(new, v["field_comments"].get(new, ""), v["source_table"]) for orig, new in v["renamed"].items()]
        head = f"# {system}.{table} —— {v['source_comment']}（原型 {v['source_table']}，{len(v['renamed'])} 字段）"
        const = table.upper() + "_DDL"
        ddl = build_ddl(table, pk, fields)
        ddls.append(f'{head}\n{const} = """\n{ddl}\n"""')
    out.append("\n\n".join(ddls))
    out.append("")
    out.append(f"RISK_EXT_DDL_{sys_prefix}: dict[str, str] = {{")
    for system, table, _ in tables:
        out.append(f'    "{system}.{table}": {table.upper()}_DDL,')
    out.append("}")
    return "\n".join(out) + "\n"


def main() -> None:
    data = json.loads(DOC.read_text(encoding="utf-8"))
    header = (
        '"""S3 M1b 全量补全：42 张新表 DDL（脱敏后字段，数据字典 = docs/S3-M1a-字段脱敏映射-全量42表.json）。\n'
        "本文件由 scripts/s3_m1b_scaffold_risk_ext.py 生成（类型推断 + 覆盖）；改动请改脚手架后重新生成。\n"
        "字段名 = renamed（ap_ 脱敏名），注释 = field_comments；表名 = 脱敏名，原型表名只作溯源注释。\n"
        '"""\n'
    )
    ext = emit(header, CUSTOMER_TABLES + RISK_TABLES, data, "1")
    ext2 = emit(header, CONCENTRATION_TABLES + APPROVAL_TABLES + PROJECT_TABLES + BASE_TABLES, data, "2")
    OUT_EXT.write_text(ext, encoding="utf-8")
    OUT_EXT2.write_text(ext2, encoding="utf-8")
    print(f"written {OUT_EXT} ({len(CUSTOMER_TABLES) + len(RISK_TABLES)} tables)")
    print(f"written {OUT_EXT2} ({len(CONCENTRATION_TABLES) + len(APPROVAL_TABLES) + len(PROJECT_TABLES) + len(BASE_TABLES)} tables)")


if __name__ == "__main__":
    main()
