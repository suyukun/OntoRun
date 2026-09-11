"""GET /api/ontology 数据装配：原语 + 口径规则 + 确认状态。

registry.py 会被确认写路径在运行期改写（git commit），
因此这里每次请求用 importlib 现场加载，绝不复用进程内旧注册表。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "src/fortune_semantic/registry.py"
CONFIRMATIONS_PATH = REPO_ROOT / "data/fortune_admin/confirmations.json"


class DivergenceOption(BaseModel):
    """口径分歧候选：同一口径的另一种合法解释及其证据。"""

    key: str = Field(description="选项键，与 Decision.option_key 对应")
    label: str = Field(description="选项显示名（如“计法人账/计个人账”）")
    value_evidence: str = Field(description="该解释下的指标值及出处脚本证据")
    applies_to: str = Field(description="适用范围：该解释对哪类口径/场景成立")


class Decision(BaseModel):
    """裁决记录：人对分歧的裁决结果（落 git commit，不可回退）。"""

    option_key: str = Field(description="所选选项键；escalate 表示已升级留痕（线下处理，状态不翻转）")
    decided_by: str = Field(description="裁决人（落 commit message）")
    time: datetime = Field(description="裁决时间")
    commit: str = Field(description="承载该裁决的 git commit 短哈希")


class TrialResult(BaseModel):
    """试算行：规则在指定月份的数值（只读试算，与图表同源，禁手填假数字）。"""

    rule_id: str = Field(description="口径规则 id")
    month: str = Field(description="统计月份，YYYY-MM")
    value: float = Field(description="试算数值")
    unit: str = Field(description="数值单位（如 万元 / 户）")
    generated_at: datetime = Field(description="数值生成时间")
    source: Literal["semantic_query", "cache"] = Field(description="来源：语义查询实时计算或当日缓存")


class CaliberRule(BaseModel):
    """管理台侧口径规则 payload 模型：镜像 ontology_payload 的 rules 项。"""

    id: str = Field(description="口径规则 id")
    description: str = Field(description="人话描述")
    source_script: str = Field(description="出处脚本（数仓证据文件）")
    status: str = Field(default="unverified", description="确认状态：unverified | confirmed")
    related_tables: list[str] = Field(
        default_factory=list,
        description="关联表名（从出处脚本提取）",
    )
    last_record: dict | None = Field(
        default=None,
        description="最近一次确认记录（含关联 commit）",
    )
    divergence: list[DivergenceOption] | None = Field(
        default=None,
        description="分歧候选列表，仅当该规则存在多种合法解释时给出",
    )
    decision: Decision | None = Field(
        default=None,
        description="裁决记录，仅当分歧已被裁决后给出",
    )


# code -> commit 短哈希缓存（commit message 含 [code:xxxxxx]，用 grep 反查）。
_commit_cache: dict[str, str | None] = {}


def load_registry():
    """现场加载 registry.py（确认写路径会改它，不能吃进程内旧缓存）。"""
    spec = importlib.util.spec_from_file_location(
        "fortune_semantic_registry_live", REGISTRY_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.REGISTRY


def _tables_from_script(source_script: str) -> list[str]:
    """从出处脚本名提取关联表名：脚本dwd_cu_rgst_fin_di.sql -> dwd_cu_rgst_fin_di。"""
    name = Path(source_script).stem
    if name.startswith("脚本"):
        return [name[len("脚本"):]]
    return []


def load_confirmations() -> list[dict]:
    if not CONFIRMATIONS_PATH.exists():
        return []
    return json.loads(CONFIRMATIONS_PATH.read_text(encoding="utf-8"))


def _commit_for_code(code: str) -> str | None:
    """按确认短码反查 commit 短哈希（确认记录与 commit 自引用，靠 message 联结）。"""
    if code in _commit_cache:
        return _commit_cache[code]
    proc = subprocess.run(
        # -F：方括号按字面匹配（否则 [code:x] 会被当正则字符类，错联 commit）
        ["git", "log", "-F", "--grep", f"[code:{code}]", "--format=%h", "-1"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    commit = proc.stdout.strip() or None if proc.returncode == 0 else None
    _commit_cache[code] = commit
    return commit


# ---- 分歧对照装配数据（T201；R8 证据刷新 2026-09-11，与试算端点对源）----
# registry.py 规则块中 R8 的双口径实证只有描述文本、无结构化数据可读
# （语义层只读不改），故在管理台装配层落结构。数字原则=可追溯+来源日期
# 透明：user 口径 607 为 2026-09-11 试算端点实跑真值（GET /api/trial/R8
# ?month=2026-08 与图表同链路真实算出，镜像库 2026-08 再生后数据）；
# account 595 / 丢 55 为 2026-08 镜像历史实证（registry R8 描述原文；
# 语义层暂无账户口径度量，无法同链路刷新，故保留并显式标注数据日期）。
_DIVERGENCES: dict[str, list[DivergenceOption]] = {
    "R8": [
        DivergenceOption(
            key="account",
            label="按账户计数（授权账户数）",
            value_evidence=(
                "595（2026-08 历史实证：ADS 脚本按行计数=授权账户数，一人多渠道"
                "授权重复计入；语义层暂无该口径度量，未随镜像库再生刷新）"
            ),
            applies_to="与 ADS 报表/脚本逐格对账场景：逐格相等仅在账户口径下成立",
        ),
        DivergenceOption(
            key="user",
            label="按用户去重（授权用户数）",
            value_evidence=(
                "607（2026-09-11 试算端点实跑：语义层 auth_user_cnt 按用户去重，"
                "与 GET /api/trial/R8?month=2026-08 图表同源；2026-08 镜像历史"
                "实证另有 55 名无金融注册授权用户被内联注册表丢弃）"
            ),
            applies_to="业务统计授权用户数场景：一人多渠道授权不重复计",
        ),
    ],
}


def _decision_from_record(rec: dict | None) -> dict | None:
    """T202：确认记录内嵌的 decision（含 escalate 留痕）回流 payload。

    记录落 confirmations.json 时 commit 尚未产生（追加式，靠短码反查联结），
    故 decision.commit 缺失时用记录上已反查的 commit 补全；json 降级保持 None。
    """
    if rec is None or rec.get("decision") is None:
        return None
    decision = {**rec["decision"]}
    if not decision.get("commit"):
        decision["commit"] = rec.get("commit")
    return decision


def ontology_payload() -> dict:
    registry = load_registry()
    confirmations = load_confirmations()

    measures = [
        {
            "id": m.id,
            "description": m.description,
            "expression": m.expression,
            "source_table": m.source_table,
            "source_alias": m.source_alias,
            "time_field": m.time_field,
            "filters": list(m.filters),
        }
        for m in registry.measures.values()
    ]
    dimensions = [
        {
            "id": d.id,
            "description": d.description,
            "expression": d.expression,
            "join": (
                {
                    "table": d.join.table,
                    "alias": d.join.alias,
                    "on": d.join.on,
                    "select_columns": list(d.join.select_columns),
                    "snapshot_policy": d.join.snapshot_policy,
                    "snapshot_column": d.join.snapshot_column,
                }
                if d.join
                else None
            ),
            "grains": dict(d.grains) if d.grains else None,
        }
        for d in registry.dimensions.values()
    ]

    last_by_rule: dict[str, dict] = {}
    for rec in confirmations:
        enriched = {
            **rec,
            "commit": rec.get("commit") or (
                _commit_for_code(rec["code"]) if rec.get("code") else None
            ),
        }
        last_by_rule[rec["rule_id"]] = enriched  # 追加式记录，后者覆盖 = 最新一次

    rules = []
    for r in registry.rules.values():
        divergence = _DIVERGENCES.get(r.id)
        rules.append(
            {
                "id": r.id,
                "description": r.description,
                "source_script": r.source_script,
                "status": r.status,
                "related_tables": _tables_from_script(r.source_script),
                "last_record": last_by_rule.get(r.id),
                # T201：R8 双口径对照（无分歧规则为 None）；T202：decision 由最新确认记录回流。
                "divergence": (
                    [opt.model_dump(mode="json") for opt in divergence]
                    if divergence
                    else None
                ),
                "decision": _decision_from_record(last_by_rule.get(r.id)),
            }
        )

    pending = sum(1 for r in rules if r["status"] != "confirmed")
    return {
        "measures": measures,
        "dimensions": dimensions,
        "rules": rules,
        "summary": {
            "measures": len(measures),
            "dimensions": len(dimensions),
            "rules": len(rules),
            "pending": pending,
            "confirmed": len(rules) - pending,
        },
    }
