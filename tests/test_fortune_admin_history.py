"""T102 增量测试：history ?rule_id/?object 过滤三态 + 无匹配空列表。

SPEC docs/plans/开工门槛-管理台重构_v0.2.md §C1-T102：
- rule_id 命中：只返回该规则的确认/裁决 commit（含 escalate 变体）；
- 组合过滤：rule_id + object AND 交集；object 语义 = /api/ontology payload
  的 related_tables（表 id）；
- 无参全量回归：不带参数时形状/顺序/数量与既有行为完全不变；
- 无匹配：返回空列表、正常返回不报错。

覆盖两层：函数层直调 history_payload；HTTP 层走 router /api/history
query param 透传（TestClient 实测 200 与过滤生效），"无匹配返回空列表
200 不报错"两层各自验证。

隔离：history 读取的 git 仓与 registry 全部落 tmp 沙盒（monkeypatch
REPO_ROOT/路径），零污染本仓工作区与 git 历史。
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.fortune_admin import history, ontology

REGISTRY_REL = Path("src/fortune_semantic/registry.py")
CONFIRMATIONS_REL = Path("data/fortune_admin/confirmations.json")

# registry payload 语义：source_script 提取表 id（R8/R5 各挂不同 ADS 表）
R8_TABLE = "ads_chnl_auth_qty_df"
R5_TABLE = "ads_chnl_real_user_df"

R8_CONFIRM = "chore(fortune-admin): rule R8 confirmed by 王工 [code:aaa111]"
R8_ESCALATE = (
    "chore(fortune-admin): rule R8 ESCALATED (undecided) by 王工 [code:bbb222]"
)
R5_CONFIRM = "chore(fortune-admin): rule R5 confirmed by 李四 [code:ccc333]"
# 诱饵：正文提到 rule R8 但不是确认记录，不得被 rule_id=R8 命中
R8_MENTION = "docs: explain rule R8 semantics in passing"

# git log 最新在前（沙盒内按最老优先创建，共 4 条）
ALL_SUBJECTS = [R8_CONFIRM, R8_ESCALATE, R5_CONFIRM, R8_MENTION]
R8_SUBJECTS = [R8_CONFIRM, R8_ESCALATE]


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30, check=False
    )


@pytest.fixture(scope="module")
def client():
    from src.fortune_admin.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """tmp git 仓：4 条已知 subject 的空 commit；registry 拷自本仓。"""
    (tmp_path / REGISTRY_REL.parent).mkdir(parents=True)
    shutil.copyfile(ontology.REGISTRY_PATH, tmp_path / REGISTRY_REL)
    (tmp_path / CONFIRMATIONS_REL.parent).mkdir(parents=True)
    (tmp_path / CONFIRMATIONS_REL).write_text("[]\n", encoding="utf-8")
    assert _git(tmp_path, "init", "-q").returncode == 0
    assert _git(tmp_path, "config", "user.email", "t102@test.local").returncode == 0
    assert _git(tmp_path, "config", "user.name", "T102 Test").returncode == 0
    for subject in reversed(ALL_SUBJECTS):
        proc = _git(tmp_path, "commit", "--allow-empty", "-m", subject)
        assert proc.returncode == 0, proc.stderr
    monkeypatch.setattr(history, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(ontology, "REGISTRY_PATH", tmp_path / REGISTRY_REL)
    monkeypatch.setattr(ontology, "CONFIRMATIONS_PATH", tmp_path / CONFIRMATIONS_REL)
    monkeypatch.setattr(ontology, "REPO_ROOT", tmp_path)
    return tmp_path


def test_no_params_behavior_unchanged(sandbox: Path, client: TestClient):
    """无参全量回归：数量/顺序/条目形状与既有行为完全不变 + HTTP 冒烟 200。"""
    full = history.history_payload()
    assert [c["subject"] for c in full["commits"]] == ALL_SUBJECTS
    assert full["count"] == len(ALL_SUBJECTS)
    # 既有条目形状不减不增（无参不新增字段）
    assert set(full["commits"][0]) == {"short", "author", "time", "human", "subject"}
    assert history.history_payload(20) == full

    res = client.get("/api/history")
    assert res.status_code == 200, res.text
    assert res.json() == full  # 端点透传 payload，行为不变


def test_rule_id_filter_keeps_only_that_rule(sandbox: Path):
    """rule_id 命中：R8 的确认+裁决记录全留；诱饵（正文提到 R8）不误挂。"""
    data = history.history_payload(rule_id="R8")
    assert [c["subject"] for c in data["commits"]] == R8_SUBJECTS
    assert data["count"] == len(R8_SUBJECTS)

    other = history.history_payload(rule_id="R5")
    assert [c["subject"] for c in other["commits"]] == [R5_CONFIRM]


def test_combined_filters_and(sandbox: Path):
    """组合过滤 = AND：两参同满足才留；任一不满足即空。"""
    hit = history.history_payload(rule_id="R8", object=R8_TABLE)
    assert [c["subject"] for c in hit["commits"]] == R8_SUBJECTS

    miss = history.history_payload(rule_id="R8", object=R5_TABLE)
    assert miss == {"commits": [], "count": 0}


def test_object_filter_semantics_matches_payload(sandbox: Path):
    """object 过滤：related_tables 语义与 /api/ontology payload 同源同义。"""
    payload_rules = {
        r["id"]: r["related_tables"] for r in ontology.ontology_payload()["rules"]
    }
    assert payload_rules["R8"] == [R8_TABLE]  # 沙盒 registry 的表 id 与常量一致

    by_object = history.history_payload(object=R8_TABLE)
    assert [c["subject"] for c in by_object["commits"]] == R8_SUBJECTS
    r5_only = history.history_payload(object=R5_TABLE)
    assert [c["subject"] for c in r5_only["commits"]] == [R5_CONFIRM]


def test_no_match_returns_empty_list(sandbox: Path):
    """无匹配：空列表 + count 0，正常返回不报错（规则不存在/表不存在）。"""
    assert history.history_payload(rule_id="NOPE") == {"commits": [], "count": 0}
    assert history.history_payload(object="no_such_table") == {
        "commits": [],
        "count": 0,
    }


def test_http_filters_via_query_params(sandbox: Path, client: TestClient):
    """HTTP 层（T102 接线）：query param 透传过滤生效——rule_id/object/组合/无匹配。"""
    r8 = client.get("/api/history", params={"rule_id": "R8"})
    assert r8.status_code == 200, r8.text
    assert [c["subject"] for c in r8.json()["commits"]] == R8_SUBJECTS

    by_object = client.get("/api/history", params={"object": R8_TABLE})
    assert by_object.status_code == 200, by_object.text
    assert [c["subject"] for c in by_object.json()["commits"]] == R8_SUBJECTS

    combo_hit = client.get("/api/history", params={"rule_id": "R8", "object": R8_TABLE})
    assert combo_hit.status_code == 200, combo_hit.text
    assert [c["subject"] for c in combo_hit.json()["commits"]] == R8_SUBJECTS

    combo_miss = client.get(
        "/api/history", params={"rule_id": "R8", "object": R5_TABLE}
    )
    assert combo_miss.status_code == 200, combo_miss.text
    assert combo_miss.json() == {"commits": [], "count": 0}

    nope = client.get("/api/history", params={"rule_id": "NOPE"})
    assert nope.status_code == 200, nope.text
    assert nope.json() == {"commits": [], "count": 0}
