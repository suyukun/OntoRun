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
- P0-文案（根因二）：「数据异常异常」拼接 bug；ap_sys_param 内部记号 → in-universe 文案。

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
    finally:
        conn.close()
    print("===== 补丁完成 =====")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
