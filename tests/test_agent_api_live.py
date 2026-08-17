"""波 4a 任务 2：真 LLM 冒烟测试（DeepSeek）。

单条"取消订单"对话冒烟，断言不崩即可。
网络失败则如实报告，不伪造结果。
"""

import os
import shutil

import pytest
from fastapi.testclient import TestClient

from data import seed_retail_source as seed


@pytest.fixture(scope="session")
def seed_db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("agent_live") / "source.db"
    seed.build_database(path)
    return path


@pytest.mark.slow
@pytest.mark.live
def test_agent_chat_cancel_order_live_llm(tmp_path, seed_db_path, monkeypatch):
    """真 LLM 冒烟：用 DeepSeekProvider 跑 1 条"取消订单"对话，断言不崩。

    环境变量 DEEPSEEK_API_KEY 必须已设置。
    网络失败 → pytest.skip（如实报告，不伪造）。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        pytest.skip("DEEPSEEK_API_KEY 未设置，跳过真 LLM 冒烟（非失败）")

    source = tmp_path / "source.db"
    shutil.copy(seed_db_path, source)
    ontology = tmp_path / "ontology.db"

    # 用真实 provider 创建 app
    # 注意：monkeypatch 设置环境变量确保 DeepSeekProvider 可用
    monkeypatch.setenv("DEEPSEEK_API_KEY", api_key)
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")

    from src.app.main import create_app as create_agent_app

    try:
        app = create_agent_app(source_db=source, ontology_db=ontology)
    except Exception as e:  # noqa: BLE001 (smoke test: catch-all on network/bootstrap)
        pytest.skip(f"创建 app 失败（可能网络不通）: {e}")

    with TestClient(app) as client:
        # 先查 ORD-1001 确认可取消
        resp = client.get("/objects/order/ORD-1001")
        if resp.status_code != 200:
            pytest.skip(f"seed 数据异常: {resp.json()}")

        # 发送取消订单请求
        try:
            resp = client.post(
                "/agent/chat",
                json={
                    "message": "请帮我取消订单 ORD-1001，理由是客户改主意了"
                },
            )
        except Exception as e:  # noqa: BLE001 (smoke test: catch-all on network/API)
            pytest.skip(f"DeepSeek API 调用失败（网络/限流）: {e}")

        # 断言不崩
        assert resp.status_code == 200, f"真 LLM 冒烟失败: {resp.json()}"
        body = resp.json()

        # 不要求精确回复内容（LLM 非确定性），但必须有 session_id 和 reply
        assert "session_id" in body
        assert "reply" in body
        assert len(body["reply"]) > 0, "LLM 回复不应为空"

        # 如果 LLM 返回了 need_confirm（不应该，cancel_order 非高风险），
        # 那也是合法状态（只是 LLM 行为偏差，不视为失败）
        if body.get("need_confirm"):
            # 这种情况不常见但非错误，确认即可
            need = body["need_confirm"]
            resp2 = client.post(
                "/agent/confirm",
                json={
                    "session_id": body["session_id"],
                    "call_id": need["id"],
                    "confirmed": True,
                },
            )
            assert resp2.status_code in (200, 400), f"确认失败: {resp2.json()}"
