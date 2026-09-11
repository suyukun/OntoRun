"""TD-13 截断修复（UX 后续批 T-N2）——finish_reason=length 加长重试，全 mock。

背景：max_tokens 硬编码 200，T-U5 加长系统提示词后输出截断率约 20%
（route_error=length 实证）；旧路径截断后以同预算重试（必然再截断）→
静默降级关键词路由造成误判。

契约（门槛稿 A3 test_length_retry）：
- WHEN LLM 返回 finish_reason=length THEN 加长重试一次（更大 max_tokens）；
- 重试成功 → 正常 plan；重试仍失败 → 才走既有降级路径（E_ROUTE_INVALID）。
LLM client 经 keyword-only 参数 client= 注入（测试 seam，生产路径不变）。
"""

import json
from types import SimpleNamespace

from src.semantic import errors, llm_route


def _resp(content, finish_reason="stop"):
    """OpenAI chat.completions 响应替身（同 test_llm_route_v2 模式）。"""
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content), finish_reason=finish_reason
            )
        ]
    )


class ScriptedClient:
    """按脚本逐次返回并记录每次 create kwargs 的 client 替身（注入用）。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self._i = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses[min(self._i, len(self.responses) - 1)]
        self._i += 1
        return response


def _plan_payload() -> str:
    return json.dumps({"measure": "reg_user_cnt", "dimensions": []}, ensure_ascii=False)


def test_length_retry_uses_larger_max_tokens():
    """① 首发截断（length）→ 重试被触发，且重试 max_tokens 严格更大。"""
    client = ScriptedClient(
        [
            _resp('{"measure": "reg_user_cnt", "dim', finish_reason="length"),
            _resp(_plan_payload()),
        ]
    )
    llm_route.llm_route("上个月注册了多少人", client=client)
    assert len(client.calls) == 2  # 截断 → 恰好重试一次
    first, retry = client.calls
    assert first["max_tokens"] == llm_route.LLM_MAX_TOKENS
    assert retry["max_tokens"] == llm_route.LLM_LENGTH_RETRY_MAX_TOKENS
    assert retry["max_tokens"] > first["max_tokens"]


def test_length_retry_success_returns_plan():
    """② 重试后成功 → 正常 plan 返回，不走降级（无 error）。"""
    client = ScriptedClient(
        [
            _resp('{"measure": "reg_user_cnt", "dim', finish_reason="length"),
            _resp(_plan_payload()),
        ]
    )
    out = llm_route.llm_route("上个月注册了多少人", client=client)
    assert "error" not in out
    assert out["plan"].measure == "reg_user_cnt"
    assert not out["plan"].rejected


def test_length_retry_still_truncated_degrades():
    """③ 重试仍截断 → 走既有降级路径（E_ROUTE_INVALID → keyword 兜底）。"""
    client = ScriptedClient(
        [
            _resp('{"measure"', finish_reason="length"),
            _resp('{"measure"', finish_reason="length"),
        ]
    )
    out = llm_route.llm_route("上个月注册了多少人", client=client)
    assert out["error_code"] == errors.E_ROUTE_INVALID
    assert "error" in out and "plan" not in out
    assert len(client.calls) == 2  # 只加长重试一次，不追加第三次调用
    assert client.calls[1]["max_tokens"] > client.calls[0]["max_tokens"]
    assert "raw" in out  # 截断原始输出留痕（脱敏后）
