"""T-N8 改写旁路端点（POST /api/rewrite/answer）— 全 mock，不打真 API。

覆盖（docs/plans/开工门槛-UX后续批_v0.1.md C1 T-N8）：
- ① 正常改写 → 200 {"text": 改写文, "rewritten": true}（契约冻结）；
- ② 数字漂移 → 200 rewritten:false 且 text=原文案（后端硬判据：NFKC+千分位
  归一后数字序列逐一相等，LLM 输出不可信）；
- ③ mock 超时（>2s 硬判据，测试内收紧到 0.05s）→ 200 静默兜底，不 500；
- ④ offline（SEMANTIC_DISABLE_LLM=1）→ rewritten:false 且零 LLM 触达；
- 归一层单测（全角/千分位）＋ answer≤500 字符防注入面硬上限。
"""

import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

_TMP = Path(tempfile.mkdtemp(prefix="rewrite-endpoint-"))
os.environ.setdefault("SEMANTIC_APP_DB", str(_TMP / "app.db"))
os.environ.setdefault("SEMANTIC_TRACE_LOG", str(_TMP / "trace.jsonl"))

from fastapi.testclient import TestClient  # noqa: E402

from src.semantic import app as app_module  # noqa: E402
from src.semantic import storage  # noqa: E402
from src.semantic.app import _number_seq, app  # noqa: E402

storage.migrate()  # 与其他端点测试同款：幂等迁移；本端点自身只读、不落库
client = TestClient(app)

ANSWER = "抱歉，这个问题我答不了。我能答：注册用户数 × 各渠道、性别、任意时间窗。"


def _resp(content):
    """OpenAI chat.completions 响应替身（test_llm_route_v2 同款）。"""
    return SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content), finish_reason="stop")])


def _install_llm(monkeypatch, content=None, delay=0.0):
    """注入假 OpenAI client（openai.OpenAI 在端点内延迟 import，attr 补丁即生效）；
    返回调用记录，供断言 prompt 形态与是否触达。"""
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if delay:
            time.sleep(delay)
        return _resp(content)

    monkeypatch.setattr(
        "openai.OpenAI",
        lambda **_kw: SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        ),
    )
    return calls


@pytest.fixture(autouse=True)
def _llm_env(monkeypatch):
    """默认 LLM 链路开启（假 key，零网络）；offline 用例自行 setenv 关闭。"""
    monkeypatch.delenv("SEMANTIC_DISABLE_LLM", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key-mock")


def _post(answer=ANSWER, kind="reject"):
    return client.post(
        "/api/rewrite/answer",
        json={"kind": kind, "answer": answer, "facts": {}},
    )


def test_rewrite_success_contract(monkeypatch):
    """① 正常改写：200 + {"text", "rewritten": true}，prompt 精简两段式。"""
    rewritten = "好的，这个问题我暂时答不上来。我可以答：注册用户数相关的查询。"
    calls = _install_llm(monkeypatch, content=rewritten)
    r = _post()
    assert r.status_code == 200
    assert r.json() == {"text": rewritten, "rewritten": True}
    assert len(calls) == 1
    messages = calls[0]["messages"]
    assert [m["role"] for m in messages] == ["system", "user"]  # 精简两段式，防截断
    assert "数字" in messages[0]["content"]  # 一句话任务锁点：数字一字不动
    assert messages[1]["content"] == ANSWER


def test_number_drift_falls_back_to_original(monkeypatch):
    """② 数字漂移：凭空引入/改动数字 → rewritten:false 且 text=原文案。"""
    _install_llm(monkeypatch, content="其实 2026 年 9 月注册了 12345 人。")  # 凭空引入
    r = _post()
    assert r.status_code == 200
    assert r.json() == {"text": ANSWER, "rewritten": False}

    numbered = "2026年8月共注册 1,234 人。"
    _install_llm(monkeypatch, content="2026年8月共注册 1235 人。")  # 改动数字
    r2 = _post(answer=numbered, kind="clarify")
    assert r2.status_code == 200
    assert r2.json() == {"text": numbered, "rewritten": False}


def test_llm_timeout_falls_back(monkeypatch):
    """③ 超时（2s 硬判据，测试内收紧为 0.05s）：200 静默兜底原文案，不 500。"""
    monkeypatch.setattr(app_module, "REWRITE_TIMEOUT_S", 0.05)
    _install_llm(monkeypatch, content="迟到的改写", delay=0.5)
    r = _post()
    assert r.status_code == 200
    assert r.json() == {"text": ANSWER, "rewritten": False}


def test_offline_falls_back_without_llm_call(monkeypatch):
    """④ offline（SEMANTIC_DISABLE_LLM=1）：rewritten:false 且零 LLM 触达。"""
    monkeypatch.setenv("SEMANTIC_DISABLE_LLM", "1")
    calls = _install_llm(monkeypatch, content="不应触达")
    r = _post()
    assert r.status_code == 200
    assert r.json() == {"text": ANSWER, "rewritten": False}
    assert calls == []  # offline 不构造 client、不发请求


def test_number_seq_nfkc_and_thousands_normalization():
    """硬判据归一层：NFKC 全角→半角、千分位剔除、小数/日期分段。"""
    assert _number_seq("共 1,234 人") == ["1234"]
    assert _number_seq("共１，２３４人") == ["1234"]  # NFKC + 全角千分位
    assert _number_seq("环比增长5.5%") == ["5.5"]
    assert _number_seq("2026-08") == ["2026", "08"]
    assert _number_seq("无任何数字的拒答文案") == []


def test_answer_length_hard_cap(monkeypatch):
    """防注入面：answer>500 字符 → 422 校验拒绝，不进 prompt。"""
    _install_llm(monkeypatch, content="x")
    r = _post(answer="长" * 501)
    assert r.status_code == 422
