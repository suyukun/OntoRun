"""GET /api/ontology 数据装配：原语 + 口径规则 + 确认状态。

registry.py 会被确认写路径在运行期改写（git commit），
因此这里每次请求用 importlib 现场加载，绝不复用进程内旧注册表。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "src/fortune_semantic/registry.py"
CONFIRMATIONS_PATH = REPO_ROOT / "data/fortune_admin/confirmations.json"

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
        rules.append(
            {
                "id": r.id,
                "description": r.description,
                "source_script": r.source_script,
                "status": r.status,
                "related_tables": _tables_from_script(r.source_script),
                "last_record": last_by_rule.get(r.id),
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
