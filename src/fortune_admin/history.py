"""GET /api/history：git log 最近 20 条人话化（时间 / 作者 / 改了什么）。"""

from __future__ import annotations

import subprocess
from pathlib import Path

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


def history_payload(limit: int = 20) -> dict:
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
    return {"commits": commits, "count": len(commits)}
