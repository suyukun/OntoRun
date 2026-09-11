"""GET /api/history：git log 最近 20 条人话化（时间 / 作者 / 改了什么）。

可选过滤（T102）：rule_id= 只留该规则的确认/裁决记录；object= 只留关联表
含该表的规则记录（表 id 语义与 /api/ontology payload 的 related_tables 一致）；
两参 AND 组合；均不传则行为不变。过滤作用于最近 limit 条窗口内。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.fortune_admin import ontology

REPO_ROOT = Path(__file__).resolve().parents[2]

TYPE_CN = {
    "feat": "新增",
    "fix": "修复",
    "docs": "文档",
    "refactor": "重构",
    "test": "测试",
    "chore": "配置/杂项",
    "perf": "性能",
    "ci": "CI",
    "style": "格式",
}

LOG_FORMAT = "%h%x09%an%x09%aI%x09%s"

# 确认/裁决 commit（confirm_store 产出）subject 恒为 `type(scope): rule <id> ...`；
# 锚定 what 首词，`docs: 提到 rule R8` 之类不误挂。
RULE_SUBJECT_RE = re.compile(r"^rule (?P<rid>[A-Za-z0-9_-]+)\b")


def _git_log(limit: int) -> str:
    proc = subprocess.run(
        ["git", "log", f"-{limit}", f"--pretty=format:{LOG_FORMAT}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout


def humanize(subject: str) -> dict:
    """conventional commit subject -> {kind, scope, what}；解析不出就原样保留。"""
    kind, scope, what = "其他", "", subject
    if ":" in subject:
        head, rest = subject.split(":", 1)
        parts = head.split("(", 1)
        kind_raw = parts[0].strip().lower()
        kind = TYPE_CN.get(kind_raw, kind_raw or "其他")
        scope = parts[1].rstrip(")").strip() if len(parts) > 1 else ""
        what = rest.strip()
    return {"kind": kind, "scope": scope, "what": what}


def _rule_id_of_subject(subject: str) -> str | None:
    """commit 关联的规则 id（T102）；非确认/裁决类 commit 无主，返回 None。"""
    m = RULE_SUBJECT_RE.match(humanize(subject)["what"])
    return m.group("rid") if m else None


def _related_tables_map() -> dict[str, list[str]]:
    """rule id -> related_tables（T102，与 GET /api/ontology payload 同源同义）。"""
    return {r["id"]: r["related_tables"] for r in ontology.ontology_payload()["rules"]}


def history_payload(
    limit: int = 20, rule_id: str | None = None, object: str | None = None
) -> dict:
    commits = []
    for line in _git_log(limit).splitlines():
        if not line.strip():
            continue
        short, author, time_iso, subject = (line.split("\t", 3) + [""])[:4]
        parsed = humanize(subject)
        scope = f"（{parsed['scope']}）" if parsed["scope"] else ""
        commits.append(
            {
                "short": short,
                "author": author,
                "time": time_iso,
                "human": f"{parsed['kind']}{scope}：{parsed['what']}",
                "subject": subject,
            }
        )
    if rule_id is None and object is None:
        return {"commits": commits, "count": len(commits)}  # 无参行为完全不变

    tables_by_rule = _related_tables_map()
    filtered = []
    for c in commits:
        rid = _rule_id_of_subject(c["subject"])
        if rule_id is not None and rid != rule_id:
            continue
        if object is not None and object not in tables_by_rule.get(rid, []):
            continue
        filtered.append(c)
    return {"commits": filtered, "count": len(filtered)}
