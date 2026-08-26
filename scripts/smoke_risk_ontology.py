"""S3 M2 本体冒烟验证（脊柱 + M1b 全量扩展；独立脚本，不经 pytest，用 /opt/anaconda3/bin/python3 直跑）。

验证（对应任务交付物 5）：
1. 金控风控本体独立注册：新 Registry() + register_risk_objects(reg) → self_check 0 致命 issue；
2. 共享注册表 build_registry()（S1 零售 + DES，风险本体未并入——ActionEngine 要求每个
   动作有运行时 handler，风险写回实现属 M3）→ 原状不受影响，self_check 0 致命 issue；
3. 脊柱 12 核心 + 支撑 User + M1b 全量扩展 20 对象类型齐全，PK/Title/own 标注就位；
4. 对象 schema 可导出：12 核心 + User 的 JSON Schema 落盘 scripts/out/s3_risk_schema.json，
   动作参数 schema 一并导出；抽查枚举字段（signal_status / five_classification / warn_level）
   与脱敏标注。

运行：/opt/anaconda3/bin/python3 scripts/smoke_risk_ontology.py（在仓库根目录）。
"""

import json
import sys
from pathlib import Path

# 脚本从 scripts/ 直跑，把仓库根目录加入 sys.path 以导入 src 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ontology import build_registry
from src.ontology.registry import Registry
from src.ontology.risk_actions import RISK_ACTIONS
from src.ontology.risk_links import RISK_LINK_TYPES
from src.ontology.risk_objects import (
    RISK_OBJECT_TYPES,
    register_risk_objects,
)

EXT_NAMES = [
    "CustomerRelation", "CustomerRelationTree", "ImportantCustomerList",
    "Top500CustomerRisk", "CustomerAssets", "InvestDistribution",
    "SubsidiaryCreditDetail", "BankPledgeDetail", "SecuritiesPledgeDetail",
    "SubsidiaryMortgage", "WarningPush", "CoDebtScore",
    "ConcentrationLimitAdj", "ConcentrationWarnAdj", "WarningConcentration",
    "WarningDerive", "WarningDeviation", "DeviationScore",
    "ApproveTodo", "ApproveOperLog",
]
CORE_NAMES = [
    "RiskCustomer", "GroupCustomer", "WarningSignal", "Disposal", "Collateral",
    "ApproveOrder", "ApproveTask", "ConcentrationLimit", "CoDebtCustomer",
    "RiskProject", "Metric", "Organization",
]
FAILURES: list[str] = []


def check(cond: bool, msg: str) -> None:
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        FAILURES.append(msg)


def main() -> int:
    print("== S3 M2 金控风控本体 冒烟验证 ==")

    # 1) 风险本体独立注册（fresh Registry，不并入共享注册表）
    print("\n[1] register_risk_objects(fresh Registry) + self_check")
    reg = Registry()
    register_risk_objects(reg)
    issues = reg.self_check()
    errs = [i for i in issues if i.severity == "error"]
    check(len(errs) == 0, f"独立注册 self_check 无致命 issue（errors={len(errs)}, total={len(issues)}）")
    for i in errs:
        print(f"       ERR {i.code}: {i.message}")

    # 2) 共享注册表（build_registry：零售 + DES）不受影响
    print("\n[2] build_registry()（共享注册表，风险本体未并入） + self_check")
    shared = build_registry()
    issues2 = shared.self_check()
    errs2 = [i for i in issues2 if i.severity == "error"]
    check(len(errs2) == 0, f"共享注册表 self_check 无致命 issue（errors={len(errs2)}, total={len(issues2)}）")
    print(f"       objects={len(shared.object_types())} links={len(shared.link_types())} actions={len(shared.actions())}")
    print("       （风险本体暂不并入：ActionEngine 要求每个注册动作有运行时写回 handler，属 M3 范围）")

    # 3) 12 核心对象 + 支撑 User
    print("\n[3] 脊柱 12 核心 + User + M1b 全量扩展 20 对象")
    model_names = {o.model.__name__ for o in reg.object_types()}
    for n in CORE_NAMES:
        check(n in model_names, f"核心对象 {n} 已注册")
    check("User" in model_names, "支撑对象 User 已注册（org.has_users 可解析）")
    for n in EXT_NAMES:
        check(n in model_names, f"全量扩展对象 {n} 已注册")
    check(len(RISK_OBJECT_TYPES) == 33, f"RISK_OBJECT_TYPES = 33（脊柱 12 核心 + User + 全量扩展 20，实际 {len(RISK_OBJECT_TYPES)}）")
    check(len(RISK_LINK_TYPES) == 37, f"RISK_LINK_TYPES = 37（M2 14 + M1b 扩展 23，实际 {len(RISK_LINK_TYPES)}）")
    check(len(RISK_ACTIONS) == 9, f"RISK_ACTIONS = 9（实际 {len(RISK_ACTIONS)}）")

    # 4) schema 导出（对象 + 动作参数） + 枚举/脱敏抽查
    print("\n[4] schema 导出（对象 JSON Schema + 动作参数 JSON Schema）")
    out_dir = Path("scripts/out")
    out_dir.mkdir(exist_ok=True)
    payload: dict = {
        "objects": {},
        "actions": {},
        "meta": {"core_object_classes": CORE_NAMES, "ext_object_classes": EXT_NAMES, "registered_customer_type": "RiskCustomer"},
    }
    for o in RISK_OBJECT_TYPES:
        payload["objects"][o.name] = {
            "api_name": o.api_name,
            "source_table": o.source_table,
            "pk_field": o.pk_field,
            "title_field": o.title_field,
            "schema": o.model.model_json_schema(),
        }
    for a in RISK_ACTIONS:
        payload["actions"][a.name] = {
            "params_schema": a.params_model.model_json_schema(),
            "high_risk": a.high_risk,
        }
    out_file = out_dir / "s3_risk_schema.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    check(out_file.exists(), f"schema 落盘 {out_file}（{out_file.stat().st_size} bytes）")

    ws = payload["objects"]["WarningSignal"]["schema"]["properties"]
    check(
        ws["signal_status"]["enum"] == ["GENERATED", "CONFIRMED", "GRADED", "IN_DISPOSAL", "CLOSED"],
        "WarningSignal.signal_status 枚举 = GENERATED/CONFIRMED/GRADED/IN_DISPOSAL/CLOSED",
    )
    check(
        ws["warn_level"]["enum"] == ["RED", "YELLOW", "BLUE"],
        "WarningSignal.warn_level 枚举 = RED/YELLOW/BLUE",
    )
    rp = payload["objects"]["RiskProject"]["schema"]["properties"]
    check(
        rp["five_classification"]["enum"] == ["NORMAL", "ATTENTION", "SECONDARY", "DOUBTFUL", "LOSS"],
        "RiskProject.five_classification 枚举 = NORMAL/ATTENTION/SECONDARY/DOUBTFUL/LOSS",
    )
    cust = payload["objects"]["RiskCustomer"]["schema"]["properties"]
    gc = payload["objects"]["GroupCustomer"]["schema"]["properties"]
    check("（脱敏）" in cust["cert_no"].get("description", ""), "RiskCustomer.cert_no 注释标注（脱敏）")
    check("（脱敏）" in gc["group_customer_no"].get("description", ""), "GroupCustomer.group_customer_no 注释标注（脱敏）")
    cr = payload["objects"]["CustomerRelation"]["schema"]["properties"]
    check(
        cr["customer_relation_id"]["description"] == "主键ID（PK/Title）",
        "CustomerRelation.customer_relation_id 主键标注（PK/Title）",
    )
    check("（脱敏）" in cr["internal_customer_no"].get("description", ""), "CustomerRelation.internal_customer_no 注释标注（脱敏）")
    wc = payload["objects"]["WarningConcentration"]["schema"]["properties"]
    check(
        wc["warn_level"]["enum"] == ["RED", "YELLOW"],
        "WarningConcentration.warn_level 枚举 = RED/YELLOW",
    )
    at = payload["objects"]["ApproveTodo"]["schema"]["properties"]
    check(
        at["approve_todo_status"]["enum"] == ["UNHANDLED", "HANDLED", "INVALID"],
        "ApproveTodo.approve_todo_status 枚举 = UNHANDLED/HANDLED/INVALID",
    )
    sd = payload["objects"]["SubsidiaryCreditDetail"]["schema"]["properties"]
    check(
        sd["project_id"]["description"] == "主键ID（PK/Title）",
        "SubsidiaryCreditDetail.project_id 主键标注（PK/Title，源表无独立主键列）",
    )

    for name in ("confirm_warning", "adjust_warning_level", "submit_disposal"):
        check(
            name in payload["actions"] and payload["actions"][name]["params_schema"],
            f"核心动作 {name} 参数 schema 可导出",
        )

    print(f"\n== 结果：{'全部通过' if not FAILURES else f'{len(FAILURES)} 项失败'} ==")
    for f in FAILURES:
        print(f"  FAILED: {f}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())