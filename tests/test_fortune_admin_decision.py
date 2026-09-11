"""T202 增量测试：R8 分歧裁决端到端（confirm + decision / escalate 逃生口）。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §A2-US2 / §A4-7 / §B3 / §C1-T202：
- [US2] 三选一裁决 → 落库 + 带身份 commit（含裁决结论）+ decision 回流 payload；
- [US2] escalate → 只留痕（谁/哪个版本未裁），规则状态不翻转，可再次裁决；
- 非法 option_key → 422；不带 decision 的普通确认行为完全不变（向后兼容）。

隔离：写路径全部落 tmp git 仓库副本（monkeypatch REPO_ROOT/路径），
零污染本仓工作区与 git 历史。
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.fortune_admin import confirm_store, ontology

CONFIRM_PATH = Path("data/fortune_admin/confirmations.json")
REGISTRY_PATH = Path("src/fortune_semantic/registry.py")


@pytest.fixture(scope="module")
def client():
    from src.fortune_admin.main import app

    with TestClient(app) as c:
        yield c


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30, check=False
    )


@pytest.fixture()
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """独立 tmp git 仓：registry.py 拷自本仓，confirmations.json 置空。"""
    (tmp_path / REGISTRY_PATH.parent).mkdir(parents=True)
    shutil.copyfile(Path(ontology.REGISTRY_PATH), tmp_path / REGISTRY_PATH)
    (tmp_path / CONFIRM_PATH.parent).mkdir(parents=True)
    (tmp_path / CONFIRM_PATH).write_text("[]\n", encoding="utf-8")
    assert _run_git(tmp_path, "init", "-q").returncode == 0
    assert _run_git(tmp_path, "config", "user.email", "t202@test.local").returncode == 0
    assert _run_git(tmp_path, "config", "user.name", "T202 Test").returncode == 0
    monkeypatch.setattr(confirm_store, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(ontology, "REGISTRY_PATH", tmp_path / REGISTRY_PATH)
    monkeypatch.setattr(ontology, "CONFIRMATIONS_PATH", tmp_path / CONFIRM_PATH)
    monkeypatch.setattr(ontology, "REPO_ROOT", tmp_path)
    return tmp_path


def _confirm(
    client: TestClient,
    rule_id: str = "R8",
    verdict: str = "confirmed",
    confirmer: str = "王工",
    option_key: str | None = None,
):
    body: dict = {"verdict": verdict, "confirmeer": confirmer}
    if option_key is not None:
        body["decision"] = {"option_key": option_key}
    return client.post(f"/api/rules/{rule_id}/confirm", json=body)


def _registry_text(sandbox: Path) -> str:
    return (sandbox / REGISTRY_PATH).read_text(encoding="utf-8")


def _r8_block(sandbox: Path) -> str:
    return _registry_text(sandbox).split('"R8": CaliberRule(')[1].split("\n    ),")[0]


def _confirmations(sandbox: Path) -> list:
    return json.loads((sandbox / CONFIRM_PATH).read_text(encoding="utf-8"))


def _last_commit_subject(sandbox: Path) -> str:
    proc = _run_git(sandbox, "log", "-1", "--format=%s")
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def test_decision_both_confirms_rule_with_commit_and_payload(
    client: TestClient, sandbox: Path
):
    """(a) 三选一裁决 both → 规则 confirmed + decision 记录正确 + git commit 产生。"""
    res = _confirm(client, option_key="both")
    assert res.status_code == 200, res.text
    data = res.json()

    # 规则翻转 confirmed（响应 + tmp registry 落盘真相源）
    assert data["rule"] == {"id": "R8", "status": "confirmed"}
    assert 'status="confirmed"' in _r8_block(sandbox)

    # git 可用：commit 短码产生，message 含裁决结论 + 身份 + 短码联结
    record = data["record"]
    assert record["mode"] == "git"
    assert record["commit"]
    subject = _last_commit_subject(sandbox)
    assert "verdict: both (decided by 王工)" in subject
    assert f"[code:{record['code']}]" in subject

    # decision 记录完整（option_key/decided_by/time/commit）
    assert data["decision"] == {
        "option_key": "both",
        "decided_by": "王工",
        "time": record["time"],
        "commit": record["commit"],
    }

    # decision 回流 payload（GET /api/ontology，T201 挂点）
    payload = client.get("/api/ontology").json()
    r8 = next(r for r in payload["rules"] if r["id"] == "R8")
    assert r8["status"] == "confirmed"
    assert r8["decision"]["option_key"] == "both"
    assert r8["decision"]["commit"] == record["commit"]


def test_escalate_leaves_trace_without_status_flip_then_can_decide(
    client: TestClient, sandbox: Path
):
    """(b) escalate → 留痕记录存在 + 状态仍待确认 + 可再次正常裁决成功。"""
    res = _confirm(client, option_key="escalate")
    assert res.status_code == 200, res.text
    data = res.json()

    # 可判别字段：escalated 标记 + decision.option_key=escalate
    assert data["escalated"] is True
    assert data["decision"]["option_key"] == "escalate"
    assert data["decision"]["decided_by"] == "王工"

    # 状态不翻转（响应读当前值 + registry 落盘无 status 翻转）
    assert data["rule"]["status"] == "unverified"
    assert "status=" not in _r8_block(sandbox)

    # 留痕记录存在：谁（confirmer）/哪个版本（rule_id+code）未裁
    records = _confirmations(sandbox)
    assert len(records) == 1
    trace = records[0]
    assert trace["verdict"] == "escalated"
    assert trace["confirmer"] == "王工"
    assert trace["rule_id"] == "R8"
    assert trace["code"]

    # escalate 同样 git commit 留痕（含短码联结，payload 反查依赖）
    assert data["record"]["commit"]
    assert f"[code:{trace['code']}]" in _last_commit_subject(sandbox)

    # 可再次正常裁决成功，最新裁决覆盖 escalate 留痕
    res2 = _confirm(client, option_key="both")
    assert res2.status_code == 200, res2.text
    assert res2.json()["rule"]["status"] == "confirmed"
    payload = client.get("/api/ontology").json()
    r8 = next(r for r in payload["rules"] if r["id"] == "R8")
    assert r8["status"] == "confirmed"
    assert r8["decision"]["option_key"] == "both"


def test_invalid_option_key_returns_422(client: TestClient, sandbox: Path):
    """(c) 非法 option_key（bogus）→ 422，不产生任何写副作用。"""
    res = _confirm(client, option_key="bogus")
    assert res.status_code == 422
    assert _confirmations(sandbox) == []
    proc = _run_git(sandbox, "log", "--oneline")
    assert proc.stdout.strip() == ""  # 零 commit，无半提交


def test_confirm_without_decision_unchanged(client: TestClient, sandbox: Path):
    """(d) 不带 decision 的普通确认回归不变：记录形状/commit message 无裁决后缀。"""
    res = _confirm(client)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["rule"] == {"id": "R8", "status": "confirmed"}
    assert data["escalated"] is False
    assert data["decision"] is None

    record = data["record"]
    assert "decision" not in record  # 记录形状向后兼容
    assert record["mode"] == "git"
    assert record["commit"]
    subject = _last_commit_subject(sandbox)
    assert "verdict:" not in subject  # 既有 message 格式，无裁决后缀
    assert f"[code:{record['code']}]" in subject


def test_escalate_degrades_to_json_when_git_unavailable(
    client: TestClient, sandbox: Path, monkeypatch: pytest.MonkeyPatch
):
    """escalate 走既有降级机制：git 不可用时留痕仍落 JSON，状态未动。"""

    def _broken_git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args, 1, "", "git unavailable")

    monkeypatch.setattr(confirm_store, "_git", _broken_git)
    res = _confirm(client, option_key="escalate")
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["record"]["mode"] == "json"
    assert data["record"]["commit"] is None
    assert data["decision"]["commit"] is None
    assert data["escalated"] is True
    assert data["rule"]["status"] == "unverified"  # 状态仍未翻转

    records = _confirmations(sandbox)
    assert len(records) == 1
    assert records[0]["verdict"] == "escalated"  # 留痕仍有效
