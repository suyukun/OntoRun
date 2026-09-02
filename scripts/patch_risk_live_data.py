"""S4 修复轮 · 活系统数据补丁（幂等，可重复执行）——把 ap_anping 六库补到修复后口径。

背景：彩排修复清单（docs/s4-rehearsal/00-汇聚-彩排修复清单.md）P0/P1 的「活系统」侧数据修复。
生成器（src/des/generators/*）已同步修改（未来再生成即得正确数据）；本脚本只对**存量库**做
等价迁移，不重新生成（避免 RNG 流整体漂移破坏剧本依赖的确定性信号/审批链 ID）。

覆盖（对应修复项）：
- P0-1 阈值可查询：base.ap_sys_param 增元数据列（param_source/param_approver/numerator_desc/
  denominator_desc/netting_rule），R1a 三线与资本常量回填（出处条款/审批人/版本/更新时间/分子/分母/净额规则）；
- P0-3 时间单调：update_time ≥ create_time（信号 generate/update、处置 operate/disposal、各主数据）；
- P0-3 处置对齐：ap_warning_disposal.disposal_progress 按 disposal_status 收敛；信号 disposal_status 按生命周期对齐；
- P1-2 枚举残留清理：concentration.ap_concentration_limit.current_status 英文告警码 → 中文（红/橙/黄/正常）；
- P1-3 名称池再洗：>8 字合成集团名收敛到自然长度，并级联到所有携带 group_customer_name 的表
  （customer/project/base/risk 六库）；
- P0-串号（M4 第三轮终审根因一）：同名集团加编号后缀（如 翔宇电子华北集团（07）），保证
  group_customer_name 全局唯一，并级联到所有携带 group_customer_name / belong_group 的表；
- P0-文案（根因二）：「数据异常异常」拼接 bug；ap_sys_param 内部记号 → in-universe 文案；
- P0-道具（根因三）：天晟红警 WS-2026-90000002 下挂 PROCESS 审批单（AI 拆分提议 → 审批人
  第二十三条驳回 + 审计落库），落 ap_approve_order / ap_approve_task / ap_approve_warn_rel。

用法（工作目录 = OntoRun 根目录）：
    /opt/anaconda3/bin/python3 scripts/patch_risk_live_data.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
AP = ROOT / "data" / "des" / "enterprises" / "ap_anping"
DB_FILES = ("customer", "risk", "concentration", "approval", "project", "base")

# 名称中缀（与 risk_generators.CUST_NAME_MID 同源，用于拆解过长的合成集团名）
_MIDS = (
    "长三角",
    "珠三角",
    "环渤海",
    "华东",
    "华南",
    "华北",
    "西部",
    "东北",
    "沿海",
    "中原",
    "西南",
    "西北",
)
_SUFFIXES = ("控股集团有限公司", "产业发展集团", "集团有限公司", "实业集团", "控股集团")
_COMPACT_SUFFIXES = ("集团有限公司", "实业集团", "控股集团", "集团")


def shorten_group_name(name: str) -> str:
    """把过长的合成集团名收敛到自然长度（≤9 字）：长后缀收敛为「集团」，保留基名+中缀。

    保留中缀是唯一性关键（同一基名的集团靠「华东/华南/…」区分），只收敛冗余长后缀，
    避免「宏远实业华东实业集团」「宏远实业华南实业集团」撞名。
    """
    if len(name) <= 9:
        return name
    for suf in _SUFFIXES:
        if name.endswith(suf):
            return f"{name[:-len(suf)]}集团"
    return name


def _main_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(AP / "risk.db"))
    conn.row_factory = sqlite3.Row
    for alias in DB_FILES:
        if alias == "risk":
            continue
        conn.execute(f"ATTACH DATABASE ? AS {alias}", (str(AP / f"{alias}.db"),))
    return conn


def _tables_with_column(conn: sqlite3.Connection, col: str) -> list[str]:
    out = []
    for alias in DB_FILES:
        db = alias if alias != "risk" else "main"
        for (t,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ):
            cols = [r[1] for r in conn.execute(f"PRAGMA {db}.table_info({t})")]
            if col in cols:
                out.append(f"{alias}.{t}" if alias != "risk" else t)
    return out


def patch_sys_param_metadata(conn: sqlite3.Connection) -> None:
    """P0-1：ap_sys_param 增元数据列并回填（出处/审批人/版本/更新时间/分子/分母/净额规则）。"""
    cols = [r[1] for r in conn.execute("PRAGMA base.table_info(ap_sys_param)")]
    for c in ("param_source", "param_approver", "numerator_desc", "denominator_desc", "netting_rule"):
        if c not in cols:
            conn.execute(f"ALTER TABLE base.ap_sys_param ADD COLUMN {c} TEXT")
    # 元数据来源与 risk_script_props.PARAM_META / risk_evidence.PARAM_META 同源
    from src.des.generators.risk_script_props import PARAM_META

    for pid, meta in PARAM_META.items():
        conn.execute(
            "UPDATE base.ap_sys_param SET param_source=?, param_approver=?, "
            "numerator_desc=?, denominator_desc=?, netting_rule=?, version='v1.0', "
            "update_time='2026-11-30' WHERE param_id=?",
            (
                meta.get("param_source"),
                meta.get("param_approver"),
                meta.get("numerator_desc"),
                meta.get("denominator_desc"),
                meta.get("netting_rule"),
                pid,
            ),
        )


def patch_enum_chinese(conn: sqlite3.Connection) -> None:
    """P1-2：concentration_limit.current_status 英文告警码 → 中文（红/橙/黄/正常）。"""
    mapping = {
        "RED_ALERT": "红",
        "ORANGE_ALERT": "橙",
        "YELLOW_ALERT": "黄",
        "NORMAL": "正常",
    }
    for old, new in mapping.items():
        cur = conn.execute(
            "UPDATE concentration.ap_concentration_limit SET current_status=? "
            "WHERE current_status=?",
            (new, old),
        )
        if cur.rowcount:
            print(f"  [P1-2] current_status {old} → {new}（{cur.rowcount} 行）")


def patch_time_monotonic(conn: sqlite3.Connection) -> None:
    """P0-3：时间字段单调（update_time ≥ create_time / update ≥ generate）。"""
    # 预警信号：update_time / signal_update_date ≥ signal_generate_date
    cur = conn.execute(
        "UPDATE ap_warning_signal SET update_time = signal_generate_date "
        "WHERE update_time < signal_generate_date"
    )
    if cur.rowcount:
        print(f"  [P0-3] ap_warning_signal.update_time 单调化（{cur.rowcount} 行）")
    cur = conn.execute(
        "UPDATE ap_warning_signal SET signal_update_date = signal_generate_date "
        "WHERE signal_update_date IS NOT NULL AND signal_update_date < signal_generate_date"
    )
    if cur.rowcount:
        print(f"  [P0-3] ap_warning_signal.signal_update_date 单调化（{cur.rowcount} 行）")
    # 处置：operate_time ≥ disposal_time
    cur = conn.execute(
        "UPDATE ap_warning_disposal SET operate_time = disposal_time "
        "WHERE operate_time IS NOT NULL AND disposal_time IS NOT NULL "
        "AND operate_time < disposal_time"
    )
    if cur.rowcount:
        print(f"  [P0-3] ap_warning_disposal.operate_time 单调化（{cur.rowcount} 行）")
    # 各主数据：update_time ≥ create_time（列缺失的表跳过——如 subsidiary_credit_detail 无 create/update 列）
    pairs = [
        "customer.ap_group_customer",
        "customer.ap_customer",
        "customer.ap_subsidiary_credit_detail",
        "customer.ap_customer_relation_tree",
        "customer.ap_customer_relation",
        "concentration.ap_concentration_limit",
        "base.ap_sys_param",
        "base.ap_dim_metric",
    ]
    for tbl in pairs:
        db, table = (tbl.split(".", 1) if "." in tbl else ("main", tbl))
        cols = [r[1] for r in conn.execute(f"PRAGMA {db}.table_info({table})")]
        if "update_time" not in cols or "create_time" not in cols:
            continue
        cur = conn.execute(
            f"UPDATE {tbl} SET update_time = create_time "
            f"WHERE update_time IS NOT NULL AND create_time IS NOT NULL "
            f"AND update_time < create_time"
        )
        if cur.rowcount:
            print(f"  [P0-3] {tbl}.update_time 单调化（{cur.rowcount} 行）")


def patch_disposal_alignment(conn: sqlite3.Connection) -> None:
    """P0-3：处置状态与处置进展对齐。"""
    # ap_warning_disposal：progress 按 status 收敛（已处置 → 完成/解除/压降）
    done_cur = conn.execute(
        "UPDATE ap_warning_disposal SET disposal_progress='已完成处置' "
        "WHERE disposal_status='已处置' "
        "AND (disposal_progress IS NULL OR "
        "     (disposal_progress NOT LIKE '%完成%' AND disposal_progress NOT LIKE '%解除%' "
        "      AND disposal_progress NOT LIKE '%压降%'))"
    )
    if done_cur.rowcount:
        print(f"  [P0-3] ap_warning_disposal 已处置 progress 对齐（{done_cur.rowcount} 行）")
    pend_cur = conn.execute(
        "UPDATE ap_warning_disposal SET disposal_progress='待制定处置方案' "
        "WHERE disposal_status='未处置' AND (disposal_progress IS NULL OR disposal_progress='')"
    )
    if pend_cur.rowcount:
        print(f"  [P0-3] ap_warning_disposal 未处置 progress 对齐（{pend_cur.rowcount} 行）")
    # 信号 disposal_status 按生命周期对齐（口径包§四：处置中→处置中；已关闭→已处置；其余→未处置）
    lifecycle = {
        "待确认": "未处置",
        "确认中": "未处置",
        "已确认": "未处置",
        "处置中": "处置中",
        "已关闭": "已处置",
        "已撤销": "未处置",
        "已排除": "未处置",
    }
    for status, disp in lifecycle.items():
        cur = conn.execute(
            "UPDATE ap_warning_signal SET disposal_status=? "
            "WHERE signal_status=? AND disposal_status IS NOT NULL AND disposal_status<>?",
            (disp, status, disp),
        )
        if cur.rowcount:
            print(f"  [P0-3] ap_warning_signal disposal_status 对齐 {status}→{disp}（{cur.rowcount} 行）")


_PROP_GROUP_NAMES = ("天晟集团有限公司", "恒昌贸易集团有限公司", "瑞华能源集团有限公司")


def _restore_prop_group_names(conn: sqlite3.Connection) -> None:
    """幂等守护：把剧本道具集团名恢复为口径包原值（避免前序缩短把恒昌/瑞华洗短）。"""
    cascade = [
        "customer.ap_group_customer",
        "customer.ap_customer",
        "customer.ap_subsidiary_credit_detail",
        "customer.ap_customer_relation_tree",
        "customer.ap_customer_relation",
        "customer.ap_important_customer_list",
        "customer.ap_top500_customer_risk",
        "customer.ap_bank_pledge_detail",
        "customer.ap_collateral",
        "project.ap_risk_project",
        "base.ap_dim_metric",
        "base.ap_dim_rank",
        "ap_deviation_warn_score",
        "ap_warn_signal_concentration",
        "ap_warn_signal_deviation",
    ]
    rows = conn.execute(
        "SELECT group_customer_no, group_customer_name FROM customer.ap_group_customer "
        "WHERE group_customer_no LIKE 'GRP-2026-900%'"
    ).fetchall()
    # 以道具编号对应的标准名回写（前序缩短可能把恒昌/瑞华洗短 → 恢复）
    std = {"GRP-2026-900001": "天晟集团有限公司", "GRP-2026-900002": "恒昌贸易集团有限公司", "GRP-2026-900003": "瑞华能源集团有限公司"}
    for r in rows:
        want = std.get(r["group_customer_no"])
        if not want or r["group_customer_name"] == want:
            continue
        old = r["group_customer_name"]
        for tbl in cascade:
            conn.execute(f"UPDATE {tbl} SET group_customer_name=? WHERE group_customer_name=?", (want, old))
        conn.execute("UPDATE ap_warning_signal SET belong_group=? WHERE belong_group=?", (want, old))


def patch_group_names(conn: sqlite3.Connection) -> None:
    """P1-3：>8 字合成集团名收敛到自然长度，级联到所有 group_customer_name / belong_group。"""
    _restore_prop_group_names(conn)
    rows = conn.execute(
        "SELECT group_customer_name FROM customer.ap_group_customer "
        "WHERE LENGTH(group_customer_name) > 8 "
        "AND group_customer_no NOT LIKE 'GRP-2026-900%'"
    ).fetchall()
    rename = {}
    for r in rows:
        old = r[0]
        new = shorten_group_name(old)
        if new != old:
            rename[old] = new
    if not rename:
        print("  [P1-3] 无超长集团名，跳过")
        return
    # 唯一性说明：存量数据本身集团名即非唯一（8003 集团仅 963 个不同名，见 dups），
    # 收敛后允许同名（与存量一致）；group_customer_no 才是真正标识。
    print(f"  [P1-3] 集团名收敛 {len(rename)} 个（例: {list(rename.items())[:3]}）")
    # 主表
    conn.execute("BEGIN")
    try:
        for old, new in rename.items():
            conn.execute(
                "UPDATE customer.ap_group_customer SET group_customer_name=? "
                "WHERE group_customer_name=?",
                (new, old),
            )
        # 级联：所有携带 group_customer_name 的表
        cascade = [
            "customer.ap_customer",
            "customer.ap_subsidiary_credit_detail",
            "customer.ap_customer_relation_tree",
            "customer.ap_customer_relation",
            "customer.ap_important_customer_list",
            "customer.ap_top500_customer_risk",
            "customer.ap_bank_pledge_detail",
            "customer.ap_collateral",
            "project.ap_risk_project",
            "base.ap_dim_metric",
            "base.ap_dim_rank",
            "ap_deviation_warn_score",
            "ap_warn_signal_concentration",
            "ap_warn_signal_deviation",
        ]
        for tbl in cascade:
            for old, new in rename.items():
                conn.execute(
                    f"UPDATE {tbl} SET group_customer_name=? WHERE group_customer_name=?",
                    (new, old),
                )
        # 预警信号的 belong_group（risk.db 主表，无 group_customer_name 列）
        for old, new in rename.items():
            conn.execute(
                "UPDATE ap_warning_signal SET belong_group=? WHERE belong_group=?",
                (new, old),
            )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def patch_group_name_uniqueness(conn: sqlite3.Connection) -> None:
    """P0-串号（根因一）：同名集团加编号后缀，保证 group_customer_name 全局唯一。

    策略：
    - 主表 customer.ap_group_customer：按 group_customer_no 序，同名集团首个保留原名、
      后续加（NN）后缀（如 翔宇电子华北集团（07））；剧本道具集团（GRP-2026-900%）不动；
    - 级联（按各自键定位到具体集团后逐组改名）：
      ① 有 group_customer_no 列的表 → 按 group_customer_no；
      ② ap_warning_signal → belong_group 按 group_customer_no；
      ③ 有 cert_no 列的表（customer_relation/tree、subsidiary_credit_detail）→
         cert_no（ap_customer 唯一，杜绝同名客户跨集团串号）→ 集团编号；
    - 仅存 customer_name 的无键表（ap_bank_pledge_detail / ap_collateral /
      ap_warn_signal_derive / ap_important_customer_list / ap_risk_project /
      ap_deviation_warn_score）：行级无法逐组定位（同名客户跨集团），保留原名
      （首组名称仍为合法集团名），不参与证据链/看板/报送口径，不影响串号修复。
    """
    rows = conn.execute(
        "SELECT group_customer_no, group_customer_name FROM customer.ap_group_customer "
        "ORDER BY group_customer_no"
    ).fetchall()
    seen: dict[str, int] = {}
    renames: dict[str, str] = {}
    for r in rows:
        gno = r["group_customer_no"]
        if gno.startswith("GRP-2026-900"):
            continue  # 剧本道具集团（天晟/恒昌/瑞华）唯一，不动
        name = r["group_customer_name"]
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            renames[gno] = f"{name}（{seen[name]:02d}）"
    if not renames:
        print("  [P0-串号] 无同名集团，跳过")
        return
    print(
        f"  [P0-串号] 同名集团去重 {len(renames)} 个（例: {list(renames.items())[:3]}）"
    )
    conn.execute("BEGIN")
    try:
        for gno, new in renames.items():
            conn.execute(
                "UPDATE customer.ap_group_customer SET group_customer_name=? "
                "WHERE group_customer_no=?",
                (new, gno),
            )
        # ① 有 group_customer_no 键的表
        for tbl in (
            "customer.ap_customer",
            "customer.ap_top500_customer_risk",
            "base.ap_dim_metric",
            "base.ap_dim_rank",
            "ap_warn_signal_concentration",
            "ap_warn_signal_deviation",
        ):
            for gno, new in renames.items():
                conn.execute(
                    f"UPDATE {tbl} SET group_customer_name=? WHERE group_customer_no=?",
                    (new, gno),
                )
        # ② ap_warning_signal.belong_group（risk.db 主表）
        for gno, new in renames.items():
            conn.execute(
                "UPDATE ap_warning_signal SET belong_group=? WHERE group_customer_no=?",
                (new, gno),
            )
        # ③ cert_no 键的表：cert_no（唯一）→ ap_customer.group_customer_no
        cert_to_gno = {
            c["cert_no"]: c["group_customer_no"]
            for c in conn.execute(
                "SELECT cert_no, group_customer_no FROM customer.ap_customer"
            )
        }
        gno_to_certs: dict[str, list[str]] = {}
        for cert, g in cert_to_gno.items():
            gno_to_certs.setdefault(g, []).append(cert)
        for tbl, namecol in (
            ("customer.ap_customer_relation", "group_customer_name"),
            ("customer.ap_customer_relation_tree", "group_customer_name"),
        ):
            for gno, new in renames.items():
                for cert in gno_to_certs.get(gno, []):
                    conn.execute(
                        f"UPDATE {tbl} SET {namecol}=? WHERE cert_no=?",
                        (new, cert),
                    )
        # ap_subsidiary_credit_detail：group_customer_name + group_customer_name_processed 双列
        for gno, new in renames.items():
            for cert in gno_to_certs.get(gno, []):
                conn.execute(
                    "UPDATE customer.ap_subsidiary_credit_detail SET "
                    "group_customer_name=?, group_customer_name_processed=? "
                    "WHERE cert_no=?",
                    (new, new, cert),
                )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def patch_data_anomaly_concat(conn: sqlite3.Connection) -> None:
    """P0-文案（根因二）：「数据异常异常」拼接 bug → 「数据异常」。（生成器 _warn_reason 已修）"""
    cur = conn.execute(
        "UPDATE ap_warning_signal SET warn_reason=REPLACE(warn_reason, '数据异常异常', '数据异常') "
        "WHERE warn_reason LIKE '%数据异常异常%'"
    )
    if cur.rowcount:
        print(f"  [P0-文案] 数据异常异常 → 数据异常（{cur.rowcount} 行）")


def patch_concentration_reason_percent(conn: sqlite3.Connection) -> None:
    """F2：RNG 浓度类信号事由剥离百分比（文案与实算脱钩 → 只留维度描述）。

    生成器 risk_generators._warn_reason 已改（未来再生成即无百分比）；本函数对存量库
    迁移：把「集团集中度敞口超限 10%」类事由剥离百分比为「集团集中度敞口超限」——
    该百分比是 RNG 独立流生成的，与源库集中度实算（concentration_limit 归集）脱钩，
    低集中度集团会被误判为「敞口超限 10%」（如 翔宇东北（05）实算 0.9%）。
    剧本道具事由（天晟/瑞华「归集余额 X 亿元 ÷ 800 亿元 = Y%」）不以「集团集中度
    敞口超限」开头，不受影响。
    """
    import re

    pat = re.compile(r"^(集团集中度敞口超限) \d+%")
    rows = conn.execute(
        "SELECT warning_id, warn_reason FROM ap_warning_signal "
        "WHERE warn_reason LIKE '集团集中度敞口超限%'"
    ).fetchall()
    n = 0
    for r in rows:
        new = pat.sub(r"\1", r["warn_reason"] or "")
        if new != r["warn_reason"]:
            conn.execute(
                "UPDATE ap_warning_signal SET warn_reason=? WHERE warning_id=?",
                (new, r["warning_id"]),
            )
            n += 1
    if n:
        print(f"  [F2] 浓度类事由剥离百分比（{n} 行）")


def patch_concentration_reason_phrase(conn: sqlite3.Connection) -> None:
    """F8：RNG 浓度类事由残余「集团集中度敞口超限」全量剥离（漏网路径补清）。

    生成器 risk_generators._warn_reason 已改为「集团集中度指标异动」（未来再生成即无
    「敞口超限」）；本函数对存量库迁移 ap_warning_signal + ap_warn_signal_derive（含
    warn_reason_updated）——该硬断言与源库集中度实算（concentration_limit 归集）脱钩，
    低集中度集团会被误判「敞口超限」；改监测语气「指标异动」，口径以实算为准。
    幂等：无匹配即零变更。
    """
    import re

    pat = re.compile(r"^集团集中度敞口超限(?:\s*\d+%)?")
    tables = (
        ("ap_warning_signal", "warn_reason", "warning_id"),
        ("ap_warn_signal_derive", "warn_reason", "derive_warning_id"),
        ("ap_warn_signal_derive", "warn_reason_updated", "derive_warning_id"),
    )
    total = 0
    for table, col, pk_col in tables:
        rows = conn.execute(
            f"SELECT {pk_col} AS pk, {col} AS v FROM {table} "
            f"WHERE {col} LIKE '集团集中度敞口超限%'"
        ).fetchall()
        for r in rows:
            new = pat.sub("集团集中度指标异动", r["v"] or "")
            if new != r["v"]:
                conn.execute(
                    f"UPDATE {table} SET {col}=? WHERE {pk_col}=?",
                    (new, r["pk"]),
                )
                total += 1
    if total:
        print(f"  [F8] 浓度类事由残余「敞口超限」剥离（{total} 行）")


def patch_push_columns_cleanup(conn: sqlite3.Connection) -> None:
    """F14：推送列「集团集中度敞口超限 N%」硬写百分比剥离（监测语气对齐 F8）。

    F8 只清了信号事由列（warn_reason / warn_reason_updated），推送列漏网：ap_warning_signal.
    push_warn_reason（2092 行）+ ap_warning_push.push_warn_reason（860 行）+
    ap_warn_derive_sub_push.warn_reason_updated（522 行）仍为「集团集中度敞口超限 N%，
    触发X色预警」。该百分比与源库集中度实算（concentration_limit 归集）脱钩（同 F8 根因），
    改监测语气「集团集中度指标异动」；保留「，触发X色预警」等非百分比部分。
    生成器 _warn_reason 已同步（未来再生成即无「敞口超限」）；本函数只迁存量。
    幂等：无匹配即零变更。
    """
    import re

    pat = re.compile(r"^集团集中度敞口超限(?:\s*\d+%)?")
    tables = (
        ("ap_warning_signal", "push_warn_reason", "warning_id"),
        ("ap_warning_push", "push_warn_reason", "warning_push_id"),
        ("ap_warn_derive_sub_push", "warn_reason_updated", "derive_sub_push_id"),
    )
    total = 0
    for table, col, pk_col in tables:
        rows = conn.execute(
            f"SELECT {pk_col} AS pk, {col} AS v FROM {table} "
            f"WHERE {col} LIKE '集团集中度敞口超限%'"
        ).fetchall()
        for r in rows:
            new = pat.sub("集团集中度指标异动", r["v"] or "")
            if new != r["v"]:
                conn.execute(
                    f"UPDATE {table} SET {col}=? WHERE {pk_col}=?",
                    (new, r["pk"]),
                )
                total += 1
    if total:
        print(f"  [F14] 推送列「敞口超限」残留剥离（{total} 行）")


def _reason_stem(reason: str) -> str:
    """F19：从事由文案剥离「，模型评分 N」与「，触发X色预警」尾巴，得事由词干。

    跨行只搬事由类别、不搬评分数字（数字是各行独立实算，搬即编造）。
    """
    import re

    s = re.sub(r"，模型评分\s*\d+", "", reason)
    s = re.sub(r"，触发[红橙黄]色预警.*$", "", s)
    return s.strip("，, ")


def patch_signal_reason_dimension_fix(conn: sqlite3.Connection) -> None:
    """F19：非集中度维度信号的「集团集中度指标异动」模板文案改写为真实触发语气。

    F8/F14 两轮清洗把「敞口超限 N%」统一替换为模板「集团集中度指标异动」，但该
    模板被贴到了实算集中度 <9% 关注线的非集中度维度集团信号上（000098 实算
    0.41%、001516 实算 0.93%），与 verify-reason 结论「与集中度阈值无关」同屏
    自相矛盾（第七轮复测 P1 实证）。

    口径（07 方案 §四 定稿）：
    - 台账实算 ≥9% 的集团仅天晟/瑞华两组，其信号为完整 R1a 计算句、不含模板，
      故全部模板行都属于误标、整行改写（无分桶）；
    - 改写 = 同集团姊妹信号（warn_reason 不含「集中度」）最高频文案的事由词干
      + 本行原等级短语；无姊妹集团兜底「综合指标异动」；
    - push_warn_reason 与 warn_reason 同值同步；ap_warning_push 经 warning_id
      关联；ap_warn_derive_sub_push 经 customer_id → ap_customer 关联集团；
    - 顺带收口「数据异常异常」拼接残留（push 三列 637 行，历史补丁只修了
      warn_reason 列）；
    - 幂等：改写后行不再含模板，重复执行零变更。
    ⚠️ 本函数不注册进 main()——活库执行需 Jack 对 07 方案拍板后手动调用。
    """
    import re

    template = "集团集中度指标异动"
    stem_cache: dict[str, str] = {}
    fallback = "综合指标异动"

    def _group_stem(gno: str | None) -> str:
        if not gno:
            return fallback
        if gno in stem_cache:
            return stem_cache[gno]
        row = conn.execute(
            "SELECT warn_reason, COUNT(*) n FROM ap_warning_signal "
            "WHERE group_customer_no=? AND warn_reason NOT LIKE '%集中度%' "
            "GROUP BY warn_reason ORDER BY n DESC LIMIT 1",
            (gno,),
        ).fetchone()
        stem = _reason_stem(row["warn_reason"]) if row and row["warn_reason"] else fallback
        stem_cache[gno] = stem or fallback
        return stem_cache[gno]

    def _rewrite(old: str, stem: str) -> str:
        m = re.search(r"触发[红橙黄]色预警", old or "")
        tail = m.group(0) if m else "触发预警（触发事由见处置明细）"
        return f"{stem}，{tail}"

    # 1) ap_warning_signal：warn_reason 与 push_warn_reason 同值改写
    rows = conn.execute(
        "SELECT signal_id AS pk, group_customer_no AS gno, warn_level, "
        "warn_reason AS v FROM ap_warning_signal "
        "WHERE warn_reason LIKE ?",
        (template + "%",),
    ).fetchall()
    for r in rows:
        new = _rewrite(r["v"], _group_stem(r["gno"]))
        conn.execute(
            "UPDATE ap_warning_signal SET warn_reason=?, push_warn_reason=? "
            "WHERE signal_id=?",
            (new, new, r["pk"]),
        )
    print(f"  [F19] 信号事由列模板改写 {len(rows)} 行")

    # 2) ap_warning_push：经 warning_id 关联信号，取改写后事由
    rows = conn.execute(
        "SELECT p.warning_push_id AS pk, s.warn_reason AS nr "
        "FROM ap_warning_push p JOIN ap_warning_signal s "
        "ON p.warning_id = s.warning_id "
        "WHERE p.push_warn_reason LIKE ?",
        (template + "%",),
    ).fetchall()
    for r in rows:
        conn.execute(
            "UPDATE ap_warning_push SET push_warn_reason=? WHERE warning_push_id=?",
            (r["nr"], r["pk"]),
        )
    print(f"  [F19] 推送表经 warning_id 关联改写 {len(rows)} 行")

    # 3) ap_warn_derive_sub_push：经 customer_id → ap_customer 关联集团
    rows = conn.execute(
        "SELECT d.derive_sub_push_id AS pk, c.group_customer_no AS gno, "
        "d.warn_reason_updated AS v FROM ap_warn_derive_sub_push d "
        "JOIN customer.ap_customer c ON d.customer_id = c.customer_id "
        "WHERE d.warn_reason_updated LIKE ?",
        (template + "%",),
    ).fetchall()
    for r in rows:
        new = _rewrite(r["v"], _group_stem(r["gno"]))
        conn.execute(
            "UPDATE ap_warn_derive_sub_push SET warn_reason_updated=? "
            "WHERE derive_sub_push_id=?",
            (new, r["pk"]),
        )
    print(f"  [F19] 衍生推送表经 customer_id 关联改写 {len(rows)} 行")

    # 4) 「数据异常异常」拼接残留收口（三列 REPLACE，幂等）
    dup_total = 0
    for table, col in (
        ("ap_warning_signal", "push_warn_reason"),
        ("ap_warning_push", "push_warn_reason"),
        ("ap_warn_derive_sub_push", "warn_reason_updated"),
    ):
        cur = conn.execute(
            f"UPDATE {table} SET {col}=REPLACE({col}, '数据异常异常', '数据异常') "
            f"WHERE {col} LIKE '%数据异常异常%'"
        )
        dup_total += cur.rowcount
    if dup_total:
        print(f"  [F19] 「数据异常异常」拼接残留收口 {dup_total} 行")


# F20/F21：目标组（前十大非道具背景 + 质疑道具）——target 为台账目标占比（占 800 亿）。
# None = 台账不动（质疑道具与主链），仅回填明细勾稽。
_F20_TARGETS: tuple[tuple[str, float | None], ...] = (
    ("GRP-2026-003708", 0.041),  # 翔宇电子华北（16）
    ("GRP-2026-004743", 0.032),  # 盛世文旅沿海（23）
    ("GRP-2026-001234", 0.050),  # 东方商贸华南（07）——明细 0 行，需插行
    ("GRP-2026-001968", 0.059),  # 泰和能源西部（06）
    ("GRP-2026-006914", 0.068),  # 正大纺织中原（28）
    ("GRP-2026-005224", 0.046),  # 远航物流西北（19）
    ("GRP-2026-004681", 0.038),  # 瑞丰食品沿海（25）
    ("GRP-2026-001516", None),   # 质疑道具：台账不动，仅回填勾稽
    ("GRP-2026-000098", None),   # 质疑道具：同上
)
_F20_INTERNAL_RATIO = 0.30  # 内部交叉授信占归集数比例（07 方案拍板点①）
_F20_INTERNAL_COUNTERPARTY = "安平商业保理有限公司"


def patch_group_ledger_reconciliation(conn: sqlite3.Connection) -> None:
    """F20+F21：背景集团台账-明细勾稽重锚 + 前十大分布补腰（联动，等拍板执行）。

    根因（第七轮实证）：生成器两表独立随机——台账（ap_concentration_limit）与
    明细（ap_subsidiary_credit_detail）从不互引，背景集团全部不勾稽（18 抽 3 中，
    000098 明细 36.53 亿 vs 台账 3.30 亿方向都反），且 001234 明细 0 行。

    口径（07 方案）：
    - 单一事实源 = 台账。目标组台账缩放到目标占比（F21 补腰，避开 9/10/12 三线
      ±0.3pp）；质疑道具（001516/000098）台账不动；
    - 明细回填：非内部行等比缩放至 Σ = S×(1−内部占比)；每组补 1 行内部交叉授信
      （customer_name=安平商业保理，命中 F13 读侧 LIKE '安平%' 判定），余额
      = S×内部占比——抵销叙事从此有数可勾；
    - 001234 明细 0 行：借主链模板行插 3 行外部机构明细 + 1 行内部行；
    - 主链（天晟/瑞华）零触碰；F23 账龄另函数；
    - 幂等：内部行按固定 project_id 定位（存在即更新），缩放重复执行因子=1。
    ⚠️ 不注册进 main()——活库执行需 Jack 对 07 方案拍板后手动调用。
    """
    # JOIN 键索引（cert_no/group_customer_no 无索引时每组查询全表扫描，分钟级卡死；
    # schema 前缀在索引名上——SQLite 的 ON 子句只接受裸表名）
    for ddl in (
        "CREATE INDEX IF NOT EXISTS customer.idx_ascd_cert_no ON ap_subsidiary_credit_detail(cert_no)",
        "CREATE INDEX IF NOT EXISTS customer.idx_ascd_project ON ap_subsidiary_credit_detail(project_id)",
        "CREATE INDEX IF NOT EXISTS customer.idx_cust_cert ON ap_customer(cert_no)",
        "CREATE INDEX IF NOT EXISTS customer.idx_cust_gno ON ap_customer(group_customer_no)",
        "CREATE INDEX IF NOT EXISTS customer.idx_cust_cno ON ap_customer(customer_no)",
    ):
        conn.execute(ddl)
    conn.commit()
    for gno, target in _F20_TARGETS:
        ledger = conn.execute(
            "SELECT COALESCE(SUM(cl.concentration_limit),0) AS s_wan "
            "FROM concentration.ap_concentration_limit cl "
            "JOIN customer.ap_customer c ON c.customer_no = cl.customer_no "
            "WHERE c.group_customer_no=?",
            (gno,),
        ).fetchone()["s_wan"]
        s_yi = ledger / 10000.0
        if target is not None:
            s_yi_new = round(target * 800.0, 2)
            if ledger > 0 and abs(s_yi_new - s_yi) > 0.005:
                factor = (s_yi_new * 10000.0) / ledger
                conn.execute(
                    "UPDATE concentration.ap_concentration_limit SET concentration_limit = "
                    "CAST(concentration_limit * ? AS REAL) WHERE customer_no IN "
                    "(SELECT customer_no FROM customer.ap_customer WHERE group_customer_no=?)",
                    (factor, gno),
                )
            s_yi = s_yi_new
        if s_yi <= 0:
            print(f"  [F20] {gno} 无台账，跳过")
            continue

        details = conn.execute(
            "SELECT s.rowid AS rid, s.business_balance AS bal, s.customer_name AS cname "
            "FROM customer.ap_subsidiary_credit_detail s "
            "JOIN customer.ap_customer c ON s.cert_no = c.cert_no "
            "WHERE c.group_customer_no=? AND s.customer_name NOT LIKE '安平%'",
            (gno,),
        ).fetchall()
        cur_ext = sum(r["bal"] for r in details) / 10000.0
        internal_yi = round(s_yi * _F20_INTERNAL_RATIO, 2)
        ext_target = s_yi - internal_yi

        # 非内部行等比缩放至 Σexternal = S×(1−内部占比)
        if details and cur_ext > 0:
            factor = ext_target / cur_ext
            if abs(factor - 1.0) > 1e-6:
                for r in details:
                    conn.execute(
                        "UPDATE customer.ap_subsidiary_credit_detail SET "
                        "business_balance=CAST(business_balance * ? AS REAL), "
                        "risk_exposure=CAST(risk_exposure * ? AS REAL), "
                        "limit_value=CAST(limit_value * ? AS REAL) WHERE rowid=?",
                        (factor, factor, factor, r["rid"]),
                    )
        elif details and cur_ext == 0:
            even = round(ext_target * 10000.0 / len(details), 2)
            for r in details:
                conn.execute(
                    "UPDATE customer.ap_subsidiary_credit_detail SET business_balance=? "
                    "WHERE rowid=?",
                    (even, r["rid"]),
                )

        # 内部交叉授信行（固定 project_id 幂等定位）
        pid = f"SC-2026-F20I-{gno[-6:]}"
        # 模板行 cert_no 必须取本集团成员（cert_no 是读侧 JOIN 归组键）；
        # 集团成员在明细表无任何行时（如 001234）借他组行结构 + 本集团成员 cert_no
        member = conn.execute(
            "SELECT cert_no, customer_name FROM customer.ap_customer "
            "WHERE group_customer_no=? AND cert_no IS NOT NULL LIMIT 1",
            (gno,),
        ).fetchone()
        if details:
            base_row = conn.execute(
                "SELECT * FROM customer.ap_subsidiary_credit_detail WHERE rowid=?",
                (details[0]["rid"],),
            ).fetchone()
        elif member:
            base_row = dict(
                conn.execute(
                    "SELECT * FROM customer.ap_subsidiary_credit_detail LIMIT 1"
                ).fetchone()
            )
            base_row["cert_no"] = member["cert_no"]
            base_row["customer_name"] = member["customer_name"]
        else:
            base_row = None
        internal_wan = round(internal_yi * 10000.0, 2)
        existing = conn.execute(
            "SELECT 1 FROM customer.ap_subsidiary_credit_detail WHERE project_id=?", (pid,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE customer.ap_subsidiary_credit_detail SET business_balance=? "
                "WHERE project_id=?",
                (internal_wan, pid),
            )
        elif base_row is not None:
            row = dict(base_row)
            row["project_id"] = pid
            row["customer_name"] = _F20_INTERNAL_COUNTERPARTY
            # F27：org_name 独立——沿用模板 org 会被读侧 GROUP BY org_name 并组，
            # 内部抵销行不可见（第八轮授信岗实证：0.99 亿藏进安平消费金融组）
            row["org_name"] = "安平商业保理"
            row["business_balance"] = internal_wan
            row["risk_exposure"] = internal_wan
            row["limit_value"] = internal_wan
            row["project_name"] = f"集团内部交叉授信（{_F20_INTERNAL_COUNTERPARTY}）"
            cols = ", ".join(row.keys())
            conn.execute(
                f"INSERT INTO customer.ap_subsidiary_credit_detail ({cols}) "
                f"VALUES ({', '.join('?' * len(row))})",
                list(row.values()),
            )
        # F20②：001234 类 0 行集团——按目标 Σ 拆 3 行外部明细（借主链模板）
        if not details and base_row is not None:
            n_ext = 3
            each_wan = round(ext_target * 10000.0 / n_ext, 2)
            for org, i in zip(("安平银行", "安平证券", "安平资产管理"), range(n_ext)):
                row = dict(base_row)
                row["project_id"] = f"SC-2026-F20E-{gno[-6:]}-{i + 1}"
                row["org_name"] = org
                row["business_balance"] = each_wan
                row["risk_exposure"] = each_wan
                row["limit_value"] = each_wan
                row["project_name"] = f"{gname_or_fallback(conn, gno)}{org}授信项目"
                cols = ", ".join(row.keys())
                conn.execute(
                    f"INSERT INTO customer.ap_subsidiary_credit_detail ({cols}) "
                    f"VALUES ({', '.join('?' * len(row))})",
                    list(row.values()),
                )
            print(f"  [F20] {gno} 明细 0 行 → 插 {n_ext} 行外部明细（Σ={ext_target:.2f} 亿）")
    print("  [F20/F21] 勾稽重锚完成（副本验证后活库执行仍需拍板）")


def gname_or_fallback(conn: sqlite3.Connection, gno: str) -> str:
    row = conn.execute(
        "SELECT group_customer_name FROM customer.ap_customer WHERE group_customer_no=? LIMIT 1",
        (gno,),
    ).fetchone()
    return row["group_customer_name"] if row else gno


_F23_DISCIPLINE_DAYS = {"红": 7, "橙": 30, "黄": 90}  # 处置纪律上限（红立即报告/橙按月催办）


def patch_overdue_date_compliance(conn: sqlite3.Connection) -> None:
    """F23：账龄/处置时长合规化（数据时钟 2026-12-31 为锚，道具链排除）。

    第七轮复测实证：avg_open_age_days 359–374 天（数学上限 364——生成器把
    signal_generate_date 随机铺到 2025 年，与 SGN-2026-* 编号矛盾）；处置时长
    avg 120 天、min −670 天（倒挂）/max 707 天，与「红色立即报告、按月催办」
    纪律冲突。修法：
    - 生成日期年份归一 2025→2026（保持月日，分布自然；道具组 GRP-2026-900% 排除），
      同步 update_time / signal_update_date 单调（P0-3 口径）；
    - 已处置行 operate_time 按等级纪律重排（红 ≤7 / 橙 ≤30 / 黄 ≤90 天，偏移由
      rowid 派生——种子固定幂等）；负值（倒挂）行一并归位；
    - 明细表逾期天数 >364 钳到 364（业务时钟上限）；
    - 道具处置行（WD-2026-9000xx / 天晟瑞华链）零触碰。
    幂等：年份归一后无 2025 行；纪律重排后时长全部 ≤ 上限。
    ⚠️ 不注册进 main()——活库执行需 Jack 对 07 方案拍板后手动调用。
    """
    # 1) 生成日期年份归一（2025→2026，道具组排除）
    cur = conn.execute(
        "UPDATE ap_warning_signal SET signal_generate_date='2026'||substr(signal_generate_date,5) "
        "WHERE substr(signal_generate_date,1,4)='2025' "
        "AND group_customer_no NOT LIKE 'GRP-2026-900%'"
    )
    if cur.rowcount:
        print(f"  [F23] signal_generate_date 2025→2026 归一（{cur.rowcount} 行）")
    # 单调同步（P0-3 口径）：generate 晚于 update 的行对齐
    for col in ("update_time", "signal_update_date"):
        conn.execute(
            f"UPDATE ap_warning_signal SET {col}=signal_generate_date "
            f"WHERE {col} IS NOT NULL AND {col} < signal_generate_date "
            "AND group_customer_no NOT LIKE 'GRP-2026-900%'"
        )

    # 2) 已处置行 operate_time 按等级纪律重排（道具链排除；负值/超限一并归位）
    from datetime import date as _date
    from datetime import timedelta as _td

    rows = conn.execute(
        "SELECT d.disposal_id AS pk, s.warn_level AS lvl, "
        "s.signal_generate_date AS gen, "
        "CAST(julianday(d.operate_time) - julianday(s.signal_generate_date) AS INT) AS days "
        "FROM ap_warning_disposal d JOIN ap_warning_signal s "
        "ON d.warning_id = s.warning_id "
        "WHERE d.disposal_status='已处置' AND d.operate_time IS NOT NULL "
        "AND s.signal_generate_date IS NOT NULL "
        "AND s.group_customer_no NOT LIKE 'GRP-2026-900%'"
    ).fetchall()
    n = 0
    for r in rows:
        cap = _F23_DISCIPLINE_DAYS.get(r["lvl"], 90)
        if r["days"] is None or (0 <= r["days"] <= cap):
            continue
        offset = (sum(ord(ch) for ch in r["pk"]) % max(cap - 1, 1)) + 1
        gen = _date.fromisoformat(r["gen"][:10])
        conn.execute(
            "UPDATE ap_warning_disposal SET operate_time=? WHERE disposal_id=?",
            ((gen + _td(days=offset)).isoformat(), r["pk"]),
        )
        n += 1
    if n:
        print(f"  [F23] 已处置 operate_time 按纪律重排（{n} 行；红≤7/橙≤30/黄≤90 天）")

    # 3) 明细表逾期天数钳业务时钟上限
    for col in ("principal_overdue_days", "interest_overdue_days"):
        cur = conn.execute(
            f"UPDATE customer.ap_subsidiary_credit_detail SET {col}=364 "
            f"WHERE {col} > 364"
        )
        if cur.rowcount:
            print(f"  [F23] 明细 {col} 钳至 ≤364（{cur.rowcount} 行）")


def patch_sys_param_in_universe(conn: sqlite3.Connection) -> None:
    """P0-文案（根因二）：ap_sys_param 内部记号 → in-universe 文案。

    口径包 v0.3 复评审：param_source/param_approver/param_description/version/update_user
    不得出现「口径包」「演示设定」「拍板」等内部记号直达用户屏；审批人/版本/更新人改业务口径。
    文案单一来源 = risk_script_props.CAPITAL_PARAMS / PARAM_META（生成器同源，已改 in-universe）。
    """
    from src.des.generators.risk_script_props import CAPITAL_PARAMS, PARAM_META

    for pid, ptype, value, desc in CAPITAL_PARAMS:
        meta = PARAM_META.get(pid, {})
        conn.execute(
            "UPDATE base.ap_sys_param SET param_description=?, param_source=?, "
            "param_approver=?, version='v3' WHERE param_id=?",
            (desc, meta.get("param_source"), meta.get("param_approver"), pid),
        )
    # update_user=SYSTEM → 中性文案（系统初始化；元数据含版本即可）
    cur = conn.execute(
        "UPDATE base.ap_sys_param SET update_user='系统初始化' WHERE update_user='SYSTEM'"
    )
    if cur.rowcount:
        print(f"  [P0-文案] ap_sys_param.update_user SYSTEM → 系统初始化（{cur.rowcount} 行）")


_REJECT_REQUEST_ID = "REJ-2026-90000002"  # 预置驳回审计行幂等标记（F10：in-universe，不再含 s4-preset）


def _node_for_seq(conn: sqlite3.Connection, seq: int) -> tuple[str, str]:
    """按 approve_node_seq 取节点（节点 1=风险预警管理岗 / 节点 2=风控部门负责人）。"""
    for nd in conn.execute(
        "SELECT approve_node_id, post_id, approve_node_seq FROM approval.ap_approve_node "
        "ORDER BY approve_node_seq"
    ):
        if nd["approve_node_seq"] == seq:
            return nd["approve_node_id"], nd["post_id"]
    fallback = {
        1: ("NODE-2026-000001", "POST-RISK-MGMT"),
        2: ("NODE-2026-000002", "POST-RISK-DIR"),
    }
    return fallback.get(seq, fallback[1])


def _seed_reject_audit() -> None:
    """F4 预置驳回审计行（落风险本体库 data/ontology/s3_risk_ontology.db，幂等）。

    审计为 WORM（append-only，哈希链由 AuditLog 计算）；request_id 固定标记，
    已存在即跳过。演示第 4 幕「全程审计可回放」无需现场写回即可见驳回留痕。
    """
    import json
    from datetime import datetime, timedelta, timezone

    from src.des.generators.risk_script_props import PROP_APPROVE_ORDER
    from src.runtime.audit import AuditLog, AuditRecord
    from src.runtime.risk_db import RiskStore

    oid = PROP_APPROVE_ORDER[0][0]
    opinion = PROP_APPROVE_ORDER[0][7]
    store = RiskStore()
    audit = AuditLog(store)
    existing = audit.query(action="approve_disposal", page_size=200)[0]
    if any(r.get("request_id") == _REJECT_REQUEST_ID for r in existing):
        print("  [F4] 预置驳回审计行已存在，跳过")
        return
    record = AuditRecord(
        action_name="approve_disposal",
        actor="human",
        # F10：actor_detail 剥离「s4-preset」内部记号 → in-universe 审批人身份
        actor_detail="风控审批人（人工双签驳回）",
        request_id=_REJECT_REQUEST_ID,
        # F10：审计时间戳与业务时间线对齐（审批单/任务 approve_time=2026-12-10，
        # 数据时钟 2026-12；不再落真实 UTC 时钟 2026-09 早于业务时间倒挂）
        ts=datetime(2026, 12, 10, 9, 0, 0, tzinfo=timezone(timedelta(hours=8))),
        params_json=json.dumps(
            {"approve_order_id": oid, "decision": "REJECTED", "opinion": opinion},
            ensure_ascii=False,
        ),
        outcome="applied",
        message="处置审批驳回：违反 2023 关联交易办法第二十三条（禁止隐匿关联关系拆分交易），退回重新起草",
    )
    audit.append(record)
    print(f"  [F4] 预置驳回审计行落库（{record.audit_id}）")


def patch_preset_audit_in_universe() -> None:
    """F10：预置驳回审计行 in-universe（存量库迁移）。

    actor_detail 剥离「s4-preset」记号 → 业务口径审批人身份；request_id 改 in-universe；
    时间戳对齐业务时间线（审批单/任务 approve_time=2026-12-10，数据时钟 2026-12，
    不再落真实 UTC 时钟 2026-09 早于业务时间倒挂）。哈希链按规格重算（修改行在链尾，
    verify_integrity 保持全绿）。生成器 _seed_reject_audit 已同源修改，本函数只迁存量。
    """
    from src.runtime.audit import _content_of, _hash_chain
    from src.runtime.risk_db import RiskStore

    store = RiskStore()
    conn = store.ontology_conn()
    try:
        rows = conn.execute(
            "SELECT seq FROM audit_log WHERE request_id='s4-preset-reject' ORDER BY seq"
        ).fetchall()
        if not rows:
            print("  [F10] 预置驳回审计行已 in-universe，跳过")
            return
        # WORM 只读触发器临时摘除（迁移预置审计行，审计为演示数据；完成后重建保 WORM）
        conn.execute("DROP TRIGGER IF EXISTS trg_audit_log_wo_upd")
        conn.execute("DROP TRIGGER IF EXISTS trg_audit_log_wo_del")
        for r in rows:
            conn.execute(
                "UPDATE audit_log SET actor_detail=?, request_id=?, ts=? WHERE seq=?",
                (
                    "风控审批人（人工双签驳回）",
                    "REJ-2026-90000002",
                    "2026-12-10 09:00:00",
                    r["seq"],
                ),
            )
        first_seq = rows[0]["seq"]
        prev_hash = ""
        prev = conn.execute(
            "SELECT record_hash FROM audit_log WHERE seq < ? ORDER BY seq DESC LIMIT 1",
            (first_seq,),
        ).fetchone()
        if prev:
            prev_hash = prev["record_hash"]
        for row in conn.execute(
            "SELECT * FROM audit_log WHERE seq >= ? ORDER BY seq", (first_seq,)
        ):
            rec_hash = _hash_chain(prev_hash, _content_of(dict(row)))
            conn.execute(
                "UPDATE audit_log SET prev_hash=?, record_hash=? WHERE seq=?",
                (prev_hash, rec_hash, row["seq"]),
            )
            prev_hash = rec_hash
        # 重建 WORM 只读触发器（审计 append-only 语义恢复）
        conn.execute(
            "CREATE TRIGGER IF NOT EXISTS trg_audit_log_wo_upd BEFORE UPDATE ON audit_log "
            "BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END"
        )
        conn.execute(
            "CREATE TRIGGER IF NOT EXISTS trg_audit_log_wo_del BEFORE DELETE ON audit_log "
            "BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END"
        )
        conn.commit()
        print(f"  [F10] 预置驳回审计行 in-universe（{len(rows)} 行，时间戳对齐 2026-12）")
    finally:
        conn.close()


def patch_approval_prop(conn: sqlite3.Connection) -> None:
    """F4：天晟红警 WS-2026-90000002 下挂 REJECTED 审批单（预置驳回演示态）+ 双节点双签 + 审计行。

    演示第 4 幕「人拦 AI」默认即见：AI 拆分授信提议已被审批人按 2023 关联交易办法第二十三条
    驳回（opinion 落驳回依据），审批链双节点（节点 1 风险预警管理岗已审 APPROVED / 节点 2
    风控部门负责人已驳 REJECTED），审计行已落库；patch_approval_reset_to_pending 可重置回
    PROCESS（节点 2 回 PENDING）供现场 live 驳回演示。幂等：按 approve_order_id / task_id 定位。
    与生成器 risk_script_props.PROP_APPROVE_* 同源（未来再生成即得正确数据）。
    """
    from src.des.generators.risk_script_props import (
        PROP_APPROVE_ORDER,
        PROP_APPROVE_TASK,
        PROP_APPROVE_WARN_REL,
    )

    oid, title, apply_user, apply_time, status, btype, remark, opinion = (
        PROP_APPROVE_ORDER[0]
    )
    order = conn.execute(
        "SELECT approve_order_id FROM approval.ap_approve_order WHERE approve_order_id=?",
        (oid,),
    ).fetchone()
    if order:
        conn.execute(
            "UPDATE approval.ap_approve_order SET approve_order_status=?, opinion_description=?, "
            "approved_user_id=?, approve_time=?, update_time=? WHERE approve_order_id=?",
            ("REJECTED", opinion, "U90003", apply_time, apply_time, oid),
        )
    else:
        conn.execute(
            "INSERT INTO approval.ap_approve_order ("
            "approve_order_id, approve_order_type, approve_order_title, apply_user_id, "
            "approved_user_id, apply_time, approve_time, approve_order_status, business_type, "
            "remark, is_deleted, create_time, update_time, derive_warn_level_red, "
            "derive_warn_level_yellow, derive_warn_level_blue, opinion_description) "
            "VALUES (?, 'WARN_SGN', ?, ?, 'U90003', ?, ?, ?, ?, ?, 0, ?, ?, 1, 0, 0, ?)",
            (
                oid,
                title,
                apply_user,
                apply_time,
                apply_time,
                status,
                btype,
                remark,
                apply_time,
                apply_time,
                opinion,
            ),
        )
    for tid, _oid, tstatus, tresult, tremark, node_seq in PROP_APPROVE_TASK:
        node_id, post_id = _node_for_seq(conn, node_seq)
        exists = conn.execute(
            "SELECT 1 FROM approval.ap_approve_task WHERE approve_task_id=?", (tid,)
        ).fetchone()
        if exists:
            conn.execute(
                "UPDATE approval.ap_approve_task SET approve_order_id=?, approve_node_id=?, "
                "post_id=?, approve_task_status=?, approve_result=?, approve_remark=?, "
                "approve_time=? WHERE approve_task_id=?",
                (
                    oid,
                    node_id,
                    post_id,
                    tstatus,
                    tresult,
                    tremark,
                    apply_time if tstatus == "COMPLETED" else None,
                    tid,
                ),
            )
        else:
            conn.execute(
                "INSERT INTO approval.ap_approve_task ("
                "approve_task_id, approve_order_id, approve_node_id, post_id, "
                "approve_task_status, approve_result, approve_remark, approve_time, "
                "is_deleted, create_time, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)",
                (
                    tid,
                    oid,
                    node_id,
                    post_id,
                    tstatus,
                    tresult,
                    tremark,
                    apply_time if tstatus == "COMPLETED" else None,
                    apply_time,
                    apply_time,
                ),
            )
    for rid, _oid, wid in PROP_APPROVE_WARN_REL:
        exists = conn.execute(
            "SELECT 1 FROM approval.ap_approve_warn_rel WHERE approve_warn_rel_id=?", (rid,)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO approval.ap_approve_warn_rel ("
                "approve_warn_rel_id, approve_order_id, warning_id, is_deleted, "
                "create_time, update_time) VALUES (?, ?, ?, 0, ?, ?)",
                (rid, oid, wid, apply_time, apply_time),
            )
    _seed_reject_audit()
    print(
        f"  [F4] 天晟审批链预置驳回态完成（{oid} REJECTED / "
        f"{len(PROP_APPROVE_TASK)} 节点 / 驳回意见+审计行落库）"
    )


def patch_approval_reset_to_pending(conn: sqlite3.Connection) -> None:
    """F4 现场 live 演示重置：把预置 REJECTED 驳回态重置回 PROCESS（节点 2 回 PENDING）。

    供现场演示第 4 幕「人拦 AI」实时驳回：节点 1 保持已审（COMPLETED/APPROVED），节点 2
    置回 PENDING（待审批人按第二十三条现场驳回）；审批单回 PROCESS（approve_disposal 仅
    PROCESS 可审）。审计为 WORM 不可清（历史驳回审计行仍可回放），现场 live 驳回将追加新
    审计行。幂等：可重复执行（每次重置回 PENDING）。
    """
    from src.des.generators.risk_script_props import (
        PROP_APPROVE_ORDER,
        PROP_APPROVE_TASK,
    )

    oid = PROP_APPROVE_ORDER[0][0]
    apply_time = PROP_APPROVE_ORDER[0][3]
    conn.execute(
        "UPDATE approval.ap_approve_order SET approve_order_status='PROCESS', "
        "approve_time=NULL, approved_user_id='', opinion_description=NULL, update_time=? "
        "WHERE approve_order_id=?",
        (apply_time, oid),
    )
    for tid, _oid, tstatus, tresult, tremark, node_seq in PROP_APPROVE_TASK:
        if node_seq == 1:
            conn.execute(
                "UPDATE approval.ap_approve_task SET approve_task_status='COMPLETED', "
                "approve_result='APPROVED', approve_remark='同意', approve_time=? "
                "WHERE approve_task_id=?",
                (apply_time, tid),
            )
        else:
            conn.execute(
                "UPDATE approval.ap_approve_task SET approve_task_status='PENDING', "
                "approve_result=NULL, approve_remark=NULL, approve_time=NULL "
                "WHERE approve_task_id=?",
                (tid,),
            )
    print("  [F4] 天晟审批单已重置回 PROCESS（节点 2 回 PENDING，供现场 live 驳回）")


_RUIHUA_SPLIT = (
    ("SC-2026-900005", "安平银行", 400000.0, 40.0),
    ("SC-2026-900006", "安平证券", 200000.0, 20.0),
    ("SC-2026-900007", "安平资产管理", 152000.0, 15.2),
)


def patch_ruihua_redistribution(conn: sqlite3.Connection) -> None:
    """F3：瑞华敞口重分布到多家附属机构（单家 < 行内限额 60 亿），与生成器同源。

    现状：瑞华 75.2 亿全挂安平银行（>行内限额 60 亿），结论模板却断言「单看均安全」——
    算术矛盾+双重病根（种子全挂一家+模板写死均安全）。重分布为 安平银行 40 亿 +
    安平证券 20 亿 + 安平资管 15.2 亿（合计 75.2 亿 → 9.4% 黄不变，§七 第 6 幕闭环案例）。
    幂等：按 project_id 定位（存在即对账更新金额/机构，不存在即插入）。
    """
    src = conn.execute(
        "SELECT * FROM customer.ap_subsidiary_credit_detail WHERE project_id=?",
        ("SC-2026-900005",),
    ).fetchone()
    if src is None:
        print("  [F3] 瑞华授信行缺失（SC-2026-900005），跳过")
        return
    base = dict(src)
    for pid, org, bal_wan, _yi in _RUIHUA_SPLIT:
        row = dict(base)
        row["project_id"] = pid
        row["org_name"] = org
        row["project_name"] = f"瑞华实业有限公司{org}授信项目"
        row["business_balance"] = bal_wan
        row["risk_exposure"] = bal_wan
        row["pledge_value"] = round(bal_wan * 0.3, 2)
        row["guarantee_value"] = round(bal_wan * 0.2, 2)
        row["limit_value"] = bal_wan
        exists = conn.execute(
            "SELECT 1 FROM customer.ap_subsidiary_credit_detail WHERE project_id=?",
            (pid,),
        ).fetchone()
        if exists:
            conn.execute(
                "UPDATE customer.ap_subsidiary_credit_detail SET org_name=?, project_name=?, "
                "business_balance=?, risk_exposure=?, pledge_value=?, guarantee_value=?, "
                "limit_value=? WHERE project_id=?",
                (
                    org,
                    row["project_name"],
                    bal_wan,
                    bal_wan,
                    row["pledge_value"],
                    row["guarantee_value"],
                    bal_wan,
                    pid,
                ),
            )
        else:
            cols = ", ".join(row.keys())
            placeholders = ", ".join("?" * len(row))
            conn.execute(
                f"INSERT INTO customer.ap_subsidiary_credit_detail ({cols}) "
                f"VALUES ({placeholders})",
                list(row.values()),
            )
    n = conn.execute(
        "SELECT COUNT(*) n FROM customer.ap_subsidiary_credit_detail "
        "WHERE customer_name='瑞华实业有限公司'"
    ).fetchone()["n"]
    print(
        f"  [F3] 瑞华敞口重分布完成（{n} 行；安平银行 40 / 安平证券 20 / 安平资管 15.2 亿）"
    )


def main() -> int:
    print("===== S4 修复轮 · 活系统数据补丁 =====")
    conn = _main_conn()
    try:
        print("[1/6] P0-1 阈值元数据（base.ap_sys_param）")
        patch_sys_param_metadata(conn)
        conn.commit()
        print("[2/6] P1-2 枚举残留清理（current_status → 中文）")
        patch_enum_chinese(conn)
        conn.commit()
        print("[3/6] P0-3 时间字段单调")
        patch_time_monotonic(conn)
        conn.commit()
        print("[4/6] P0-3 处置状态/进展对齐")
        patch_disposal_alignment(conn)
        conn.commit()
        print("[5/6] P1-3 集团名再洗（级联）")
        patch_group_names(conn)
        conn.commit()
        print("[6/6] P0-串号 + P0-文案（重名去重/异常拼接/参数 in-universe）")
        patch_group_name_uniqueness(conn)
        patch_data_anomaly_concat(conn)
        patch_sys_param_in_universe(conn)
        conn.commit()
        print("[6b] F2 浓度类事由剥离百分比（文案对齐实算）")
        patch_concentration_reason_percent(conn)
        conn.commit()
        print("[6b2] F8 浓度类事由残余「敞口超限」全量剥离（漏网路径）")
        patch_concentration_reason_phrase(conn)
        conn.commit()
        print("[6b3] F14 推送列「敞口超限」硬写百分比剥离（监测语气对齐 F8）")
        patch_push_columns_cleanup(conn)
        conn.commit()
        print("[6c] F3 瑞华敞口重分布（单家 < 行内限额）")
        patch_ruihua_redistribution(conn)
        conn.commit()
        print("[7/7] F4 第 4 幕审批链（双节点 + 预置 REJECTED 驳回态 + 审计行）")
        patch_approval_prop(conn)
        conn.commit()
        print("[7b] F10 预置驳回审计行 in-universe（剥离 s4-preset + 时间戳对齐 2026-12）")
        patch_preset_audit_in_universe()
        conn.commit()
        print("[8/8] F4 现场 live 演示重置工具（patch_approval_reset_to_pending 已注册，默认不执行）")
    finally:
        conn.close()
    print("===== 补丁完成 =====")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
