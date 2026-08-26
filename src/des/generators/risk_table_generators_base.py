"""金融风控 M1b 全量补全 —— base 系统 11 张新表行生成器（脱敏后 ap_* 表）。

依赖 risk_generators（编码/DMN 规则/共享业务池）与 risk_ddl_ext2（DDL）。
覆盖标准指标/维度排名/自定义参数/附件/监管意见/查询日志/数据字典/系统参数/机构/用户/业务字典。
FK 引用真实：customer_no/group_customer_no → ap_customer/ap_group_customer；其余独立支撑表。
原型表名（o_base_*/o_sys_*/o_a_erms_*/erms_*）只在 docstring 溯源。
"""

from __future__ import annotations

import random
from typing import Any

from .risk_ddl_ext2 import RISK_EXT_DDL_2
from .risk_generators import (
    DICT_TYPE_DEFS,
    EXT_JSON_KEYS,
    METRIC_STD_DEFS,
    ORG_LEVEL_POOL,
    ORG_POOL,
    PRODUCT_CODE_POOL,
    _email,
    _idcard,
    _landline,
    _mobile,
    _person_name,
    _row_count,
    random_date,
)


def generate_ap_metric_std_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_metric_std 标准化指标信息（原型 o_a_erms_index_list_std）：指标标准字典，index_id 唯一。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_metric_std") + 1):
        _mid, mname, munit = rng.choice(METRIC_STD_DEFS)
        rows.append(
            {
                "data_date": random_date(rng),
                "upstream_update_time": random_date(rng),
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "org_name": rng.choice(ORG_POOL),
                "index_level_id": f"LV{rng.randint(1, 4)}",
                "index_level_name": rng.choice(("指标", "二级指标", "三级指标")),
                "index_type_id": f"TY{rng.randint(1, 6)}",
                "index_type_name": rng.choice(
                    ("规模类", "风险类", "质量类", "资本类", "效益类")
                ),
                "original_index_id": f"ORI-{year:04d}-{seq:08d}",
                "original_index_name": f"原始指标{seq}",
                "index_id": f"IDX-{year:04d}-{seq:06d}",
                "index_name": mname,
                "index_value": round(rng.uniform(1, 1000), 2),
                "index_unit": munit,
                "currency_id": "CNY",
                "currency_name": "人民币",
                "index_frequency": rng.choice(("日", "月", "季", "年")),
                "index_type_code": rng.choice(("REPORT", "MONITOR", "RISK")),
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
                "clear_remark_4": None,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "create_org_no": f"ORG{rng.randint(1, 99):03d}",
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def generate_ap_dim_rank_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_dim_rank 分维度排名信息（原型 o_a_erms_dim_rank）：
    FK customer_no/group_customer_no → ap_customer/ap_group_customer。"""
    year = ctx["year"]
    customers = ctx["customer.ap_customer"]
    groups = ctx["customer.ap_group_customer"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_dim_rank") + 1):
        if rng.random() < 0.5:
            grp = rng.choice(groups)
            # 集团维度行：customer_no 填集团代表性成员（保证 FK customer_no 无孤儿）
            members = [
                c
                for c in customers
                if c["group_customer_no"] == grp["group_customer_no"]
            ] or customers
            rep = rng.choice(members)
            cust_no, cust_nm, grp_no, grp_nm = (
                rep["customer_no"],
                rep["customer_name"],
                grp["group_customer_no"],
                grp["group_customer_name"],
            )
            dim_code, dim_name = "DIM_GROUP", "集团客户"
        else:
            cust = rng.choice(customers)
            cust_no, cust_nm, grp_no, grp_nm = (
                cust["customer_no"],
                cust["customer_name"],
                cust["group_customer_no"],
                cust["group_customer_name"],
            )
            dim_code, dim_name = "DIM_CUST", "单一客户"
        rows.append(
            {
                "dim_rank_id": f"DR-{year:04d}-{seq:08d}",
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "dim_type_code": dim_code,
                "dim_type_name": dim_name,
                "customer_no": cust_no,
                "customer_name": cust_nm,
                "group_customer_no": grp_no,
                "group_customer_name": grp_nm,
                "business_type_code": rng.choice([p[0] for p in PRODUCT_CODE_POOL]),
                "index_value": round(rng.uniform(1, 1000), 2),
                "index_unit": rng.choice(("亿元", "%", "个")),
                "currency_id": "CNY",
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "create_org_no": f"ORG{rng.randint(1, 99):03d}",
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
                "data_date": random_date(rng),
            }
        )
    return rows


def generate_ap_custom_param_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_custom_param 自定义参数表（原型 o_a_erms_custom_param）：参数指标快照。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_custom_param") + 1):
        rows.append(
            {
                "custom_param_id": f"CP-{year:04d}-{seq:08d}",
                "data_date": random_date(rng),
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "index_id": f"CPIDX-{seq:03d}",
                "index_value": round(rng.uniform(0, 1000), 2),
                "index_description": rng.choice(
                    ("自定义预警阈值", "区域调整系数", "条线权重", "专项监测参数")
                ),
                "del_ind": 0,
                "clear_remark_1": None,
                "clear_remark_2": None,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "create_org_no": f"ORG{rng.randint(1, 99):03d}",
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_org_no": f"ORG{rng.randint(1, 99):03d}",
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def generate_ap_preference_file_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_preference_file 偏好陈述信息附件表（原型 o_a_erms_pref_info_file_tab）：附件元数据。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_preference_file") + 1):
        rows.append(
            {
                "preference_file_id": f"PF-{year:04d}-{seq:08d}",
                "business_type": rng.choice(
                    ("客户准入", "授信审批", "预警处置", "风险项目")
                ),
                "business_id": f"BIZ-{year:04d}-{seq:08d}",
                "file_id": f"F-{year:04d}-{seq:08d}",
                "file_name": f"{rng.choice(('客户尽调', '授信方案', '处置方案', '押品评估'))}_附件_{seq}",
                "file_suffix": rng.choice((".pdf", ".docx", ".xlsx", ".jpg")),
                "file_type": rng.choice(("PDF", "WORD", "EXCEL", "IMAGE")),
                "file_path": f"/app/storage/attachment/{year}/{seq}.pdf",
                "operator_user": _person_name(rng),
                "operate_time": random_date(rng),
                "attachment_belong": "AP001",
                "belong_dept": rng.choice(("风险管理部", "授信管理部", "合规部")),
                "clear_remark_1": None,
                "clear_remark_2": None,
                "clear_remark_3": None,
            }
        )
    return rows


def generate_ap_supervise_opinion_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_supervise_opinion 监管意见分类展示（原型 o_a_erms_supervise_opinion_classify）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_supervise_opinion") + 1):
        rows.append(
            {
                "supervise_opinion_id": f"SO-{year:04d}-{seq:08d}",
                "org_id": f"ORG{rng.randint(1, 99):03d}",
                "org_name": rng.choice(ORG_POOL),
                "year_time": str(year),
                "first_directory": rng.choice(
                    ("公司治理", "风险管理", "合规经营", "数据治理")
                ),
                "second_directory": rng.choice(
                    ("授信管理", "流动性管理", "反洗钱", "信息披露")
                ),
                "problem_areas": rng.choice(
                    (
                        "房地产贷款集中度偏高",
                        "同业依赖度上升",
                        "不良贷款反弹",
                        "关联交易管理薄弱",
                    )
                ),
                "basic_matter": rng.choice(
                    ("要求按季度报送整改情况", "要求完善内控制度", "要求加强风险监测")
                ),
                "industry_self": rng.choice(("行业共性", "自身问题")),
                "update_time": random_date(rng),
                "remark": rng.choice(("持续跟踪", "已完成整改", "")),
            }
        )
    return rows


def generate_ap_top_query_log_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_top_query_log 客户查询历史记录（原型 o_a_erms_top_query_log）：4 字段精简日志。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_top_query_log") + 1):
        rows.append(
            {
                "top_query_log_id": f"TQ-{year:04d}-{seq:08d}",
                "query_keyword": rng.choice(
                    (
                        "宏远",
                        "泰和",
                        "恒达",
                        "华夏新能源",
                        "集中度",
                        "不良贷款",
                        "风险项目",
                    )
                ),
                "create_user": f"U{rng.randint(1, 5000):05d}",
                "create_time": random_date(rng),
            }
        )
    return rows


def generate_ap_data_dict_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_data_dict 数据字典（原型 o_base_ddct）：按 DICT_TYPE_DEFS 展开字典项。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    pool = [
        v
        for t in DICT_TYPE_DEFS
        for v in (f"{t[0]}-01", f"{t[0]}-02", f"{t[0]}-03", f"{t[0]}-04")
    ]
    for seq in range(1, _row_count(ctx, "base.ap_data_dict") + 1):
        tcode, tname = rng.choice(DICT_TYPE_DEFS)
        rows.append(
            {
                "dict_id": f"D-{year:04d}-{seq:06d}",
                "dict_key": rng.choice(pool),
                "dict_type_code": tcode,
                "dict_type_name": tname,
                "dict_value": f"{seq:02d}",
                "dict_value_name": rng.choice(
                    (
                        "正常",
                        "关注",
                        "预警",
                        "高风险",
                        "有效",
                        "无效",
                        "未推送",
                        "已推送",
                    )
                ),
                "dict_group": "AP",
                "dict_description": f"{tname}字典项{seq}",
                "dict_seq": seq,
                "status_code": 1,
                "create_time": random_date(rng),
                "create_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
                "extended_id": None,
                "del_ind": 0,
                "version": "1.0",
                "tenant_id": "AP001",
                "system_id": "SYS-RISK",
            }
        )
    return rows


def generate_ap_sys_param_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_sys_param 系统参数（原型 o_base_stm_parm）：系统运行参数。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_sys_param") + 1):
        rows.append(
            {
                "sys_param_id": f"SP-{year:04d}-{seq:05d}",
                "param_type_code": rng.choice(("SYSTEM", "REPORT", "MONITOR")),
                "param_type_name": rng.choice(("系统级", "报送级", "监测级")),
                "param_id": f"PARAM-{seq:03d}",
                "param_value": rng.choice(
                    (
                        "ON",
                        "OFF",
                        str(rng.randint(1, 999)),
                        "https://api.anping.local/v1",
                    )
                ),
                "param_description": rng.choice(
                    ("风险预警开关", "报送接口地址", "监测频率", "登录超时时长")
                ),
                "whether_cache": rng.randint(0, 1),
                "create_time": random_date(rng),
                "create_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
                "extended_id": None,
                "del_ind": 0,
                "version": "1.0",
                "tenant_id": "AP001",
            }
        )
    return rows


def generate_ap_org_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_org 系统机构表（原型 o_sys_organization）：安平体系机构层级，parent_org_code 自引用。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_org") + 1):
        code = f"ORG{seq:03d}"
        parent = "" if seq == 1 else f"ORG{rng.randint(1, max(1, seq - 1)):03d}"
        rows.append(
            {
                "org_id": f"ORGID-{year:04d}-{seq:04d}",
                "org_code": code,
                "org_name": rng.choice(ORG_POOL),
                "parent_org_code": parent,
                "org_level_code": rng.choice(ORG_LEVEL_POOL),
                "sort_no": seq,
                "ext_json_data": None
                if rng.random() < 0.5
                else f'{{"{rng.choice(EXT_JSON_KEYS)}": "{rng.randint(1, 9)}"}}',
                "status_code": 1,
                "remark": rng.choice(("安平集团机构", "子公司机构", "")),
                "del_ind": 0,
                "create_user": "SYSTEM",
                "create_time": random_date(rng),
                "update_user": "SYSTEM",
                "update_time": random_date(rng),
                "extended_id": None,
                "version": "1.0",
                "tenant_id": "AP001",
                "client_id": "AP-WEB",
            }
        )
    return rows


def generate_ap_user_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_user 系统用户信息表（原型 o_sys_user，37 字段）：人员主数据，脱敏（非真实身份）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_user") + 1):
        name = _person_name(rng)
        cert_type_code = rng.choice(("0", "1", "2", "5"))
        rows.append(
            {
                "user_id": f"U{seq:08d}",
                "user_num": f"U{year:04d}{seq:05d}",
                "real_name": name,
                "login_name": f"user{seq:04d}",
                "password": _idcard(rng),
                "salt": _idcard(rng)[:8],
                "status_code": 1,
                "sex_code": rng.choice(("1", "2")),
                "cert_type_code": cert_type_code,
                "cert_no": _idcard(rng),
                "qq": f"{rng.randint(10000, 999999999)}",
                "wechat": f"wx_{name}{rng.randint(100, 999)}",
                "telephone": _landline(rng),
                "mobile": _mobile(rng),
                "email": _email(rng),
                "fax": _landline(rng),
                "pass_error_count": rng.randint(0, 5),
                "login_succ_count": rng.randint(0, 5000),
                "lock_time": random_date(rng),
                "remark": rng.choice(("风控用户", "审批用户", "管理员", "")),
                "province": rng.choice(
                    ("上海市", "浙江省", "广东省", "北京市", "四川省")
                ),
                "city": rng.choice(("上海", "杭州", "深圳", "北京", "成都")),
                "district": rng.choice(
                    ("浦东新区", "西湖区", "南山区", "朝阳区", "高新区")
                ),
                "address": f"{rng.choice(('金融', '科技', '中心', '国际'))}{rng.choice(('大道', '路', '街'))}{rng.randint(1, 999)}号",
                "client_id": "AP-WEB",
                "client_name": "安平金控统一门户",
                "create_time": random_date(rng),
                "create_user": "SYSTEM",
                "update_time": random_date(rng),
                "update_user": "SYSTEM",
                "extended_id": None,
                "del_ind": 0,
                "version": "1.0",
                "tenant_id": "AP001",
                "last_login_time": random_date(rng),
                "grayscale_version": "v1",
                "cipher": _idcard(rng),
            }
        )
    return rows


def generate_ap_biz_dict_rows(
    rng: random.Random, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """base.ap_biz_dict 业务字典表（原型 erms_dict_biz）：业务字典码值（parent_id 自引用分层）。"""
    year = ctx["year"]
    rows: list[dict[str, Any]] = []
    for seq in range(1, _row_count(ctx, "base.ap_biz_dict") + 1):
        tcode, tname = rng.choice(DICT_TYPE_DEFS)
        parent = (
            ""
            if seq % 5 == 1
            else f"BD-{year:04d}-{max(1, seq - rng.randint(1, 4)):05d}"
        )
        rows.append(
            {
                "biz_dict_id": f"BD-{year:04d}-{seq:05d}",
                "tenant_id": "AP001",
                "parent_id": parent,
                "code": f"{tcode}-{seq:02d}",
                "dict_key": tcode,
                "dict_value": rng.choice(
                    ("正常", "关注", "预警", "高风险", "有效", "无效")
                ),
                "sort_no": seq,
                "remark": f"{tname}业务字典",
                "is_sealed": rng.randint(0, 1),
                "is_deleted": 0,
                "system_code": "SYS-RISK",
                "extension_1": None,
                "extension_2": None,
                "extension_3": None,
                "extension_4": None,
                "extension_5": None,
                "dictionary_type": tname,
                "data_source_id": "AP-CORE",
                "sql_sentence": None,
            }
        )
    return rows


# 本模块 11 表 DDL 注册（供 RISK_TABLE_SPECS 复用，字典 key = {system}.{table}）
BASE_EXT_DDL: dict[str, str] = {
    "base.ap_metric_std": RISK_EXT_DDL_2["base.ap_metric_std"],
    "base.ap_dim_rank": RISK_EXT_DDL_2["base.ap_dim_rank"],
    "base.ap_custom_param": RISK_EXT_DDL_2["base.ap_custom_param"],
    "base.ap_preference_file": RISK_EXT_DDL_2["base.ap_preference_file"],
    "base.ap_supervise_opinion": RISK_EXT_DDL_2["base.ap_supervise_opinion"],
    "base.ap_top_query_log": RISK_EXT_DDL_2["base.ap_top_query_log"],
    "base.ap_data_dict": RISK_EXT_DDL_2["base.ap_data_dict"],
    "base.ap_sys_param": RISK_EXT_DDL_2["base.ap_sys_param"],
    "base.ap_org": RISK_EXT_DDL_2["base.ap_org"],
    "base.ap_user": RISK_EXT_DDL_2["base.ap_user"],
    "base.ap_biz_dict": RISK_EXT_DDL_2["base.ap_biz_dict"],
}
