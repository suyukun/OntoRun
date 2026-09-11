"""确认写路径：改 registry 确认状态 -> git commit（subprocess 直调 git）。

写路径 spike 结论（见仓库 git log 首条 fortune-admin 验证 commit）：
主路径 = registry.py 状态翻转 + confirmations.json 追加 + 一次 commit；
git 不可用时降级 = 仅写 confirmations.json（技术债：状态翻转延迟到人工 commit）。
"""

from __future__ import annotations

import json
import re
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_REL = Path("src/fortune_semantic/registry.py")
CONFIRMATIONS_REL = Path("data/fortune_admin/confirmations.json")

RULE_BLOCK_RE = re.compile(r'^\s*"(?P<rid>[A-Za-z0-9_-]+)": CaliberRule\($')


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def set_rule_status(source: str, rule_id: str, status: str) -> str:
    """把 RULES 里指定规则块的 status 置为给定值，返回新文件全文。

    规则块 = 形如 4 空格缩进的 '"R1": CaliberRule(' 行，到其 4 空格缩进的 '),'
    收尾行。块内已有 status= 行则原位替换，否则在收尾行前插入。
    """
    lines = source.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        m = RULE_BLOCK_RE.match(line.rstrip("\n"))
        if m and m.group("rid") == rule_id:
            start = i
            break
    if start is None:
        raise ValueError(f"registry.py 中找不到规则块: {rule_id}")

    end = None
    for j in range(start + 1, len(lines)):
        if lines[j].rstrip("\n") == "    ),":
            end = j
            break
    if end is None:
        raise ValueError(f"规则块未闭合: {rule_id}")

    new_line = f'        status="{status}",\n'
    for k in range(start + 1, end):
        if re.match(r"^\s*status=", lines[k]):
            lines[k] = new_line
            return "".join(lines)
    lines.insert(end, new_line)
    return "".join(lines)


def _append_confirmation(record: dict) -> None:
    path = REPO_ROOT / CONFIRMATIONS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if path.exists():
        records = json.loads(path.read_text(encoding="utf-8"))
    records.append(record)
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def confirm_rule(
    rule_id: str, verdict: str, confirmer: str, option_key: str | None = None
) -> dict:
    """确认/驳回一条口径规则，返回含 {mode, code, commit} 的确认记录。

    mode=git：registry 状态翻转 + confirmations.json 追加 + git commit；
    mode=json：git 不可用，仅追加 confirmations.json（降级，登记技术债）。
    code = 本次确认短码（进 commit message）；commit = git 短哈希（json 模式为 null）。
    option_key（T202 R8 裁决）：account/user/both = 正常确认路径，记录内嵌
    decision、commit message 附裁决结论；escalate = 只追加 escalated 留痕
    （状态不翻转，可再次裁决），见 _escalate_rule；None = 既有普通确认，行为不变。
    """
    code = secrets.token_hex(3)  # 6 位短码
    now = datetime.now(timezone.utc).astimezone()
    record = {
        "rule_id": rule_id,
        "verdict": verdict,
        "confirmer": confirmer,
        "code": code,
        "time": now.isoformat(timespec="seconds"),
    }

    if option_key == "escalate":
        return _escalate_rule(record)
    if option_key is not None:
        record["decision"] = {
            "option_key": option_key,
            "decided_by": confirmer,
            "time": record["time"],
            "commit": None,  # commit 成功后回填
        }

    registry_path = REPO_ROOT / REGISTRY_REL
    new_status = "confirmed" if verdict == "confirmed" else "unverified"
    new_source = set_rule_status(
        registry_path.read_text(encoding="utf-8"), rule_id, new_status
    )
    registry_path.write_text(new_source, encoding="utf-8")
    _append_confirmation(record)

    staged = [str(REGISTRY_REL), str(CONFIRMATIONS_REL)]
    verb = "confirmed" if verdict == "confirmed" else "REJECTED(back to unverified)"
    message = (
        f"chore(fortune-admin): rule {rule_id} {verb} by {confirmer} [code:{code}]"
    )
    if option_key is not None:
        message += f" | {rule_id} verdict: {option_key} (decided by {confirmer})"
    try:
        add = _git("add", *staged)
        if add.returncode != 0:
            raise RuntimeError(add.stderr.strip())
        commit = _git("commit", "-m", message)
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr.strip())
        short = _git("rev-parse", "--short", "HEAD")
        if short.returncode != 0:
            raise RuntimeError(short.stderr.strip())
        record["commit"] = short.stdout.strip()
        if option_key is not None:
            record["decision"]["commit"] = record["commit"]
        return {**record, "mode": "git"}
    except (RuntimeError, subprocess.SubprocessError, FileNotFoundError):
        # 降级：git 写路径失败，registry 翻转留在工作区，记录已入 JSON。
        return {**record, "commit": None, "mode": "json"}


def _escalate_rule(record: dict) -> dict:
    """escalate 留痕（T202 R8 逃生口）：只追加 escalated 记录 + git commit 留痕。

    registry 状态不翻转（保持待确认，可再次裁决）；git 不可用时走既有
    JSON 降级（记录已入 confirmations.json，留痕仍有效）。
    """
    record["verdict"] = "escalated"
    record["decision"] = {
        "option_key": "escalate",
        "decided_by": record["confirmer"],
        "time": record["time"],
        "commit": None,  # commit 成功后回填
    }
    _append_confirmation(record)
    message = (
        f"chore(fortune-admin): rule {record['rule_id']} ESCALATED (undecided) "
        f"by {record['confirmer']} [code:{record['code']}]"
    )
    try:
        add = _git("add", str(CONFIRMATIONS_REL))
        if add.returncode != 0:
            raise RuntimeError(add.stderr.strip())
        commit = _git("commit", "-m", message)
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr.strip())
        short = _git("rev-parse", "--short", "HEAD")
        if short.returncode != 0:
            raise RuntimeError(short.stderr.strip())
        record["commit"] = short.stdout.strip()
        record["decision"]["commit"] = record["commit"]
        return {**record, "mode": "git"}
    except (RuntimeError, subprocess.SubprocessError, FileNotFoundError):
        # 降级：git 写路径失败，留痕记录已入 JSON，规则状态未动。
        return {**record, "commit": None, "mode": "json"}
