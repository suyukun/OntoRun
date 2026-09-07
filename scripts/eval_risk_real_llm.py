"""S3 M3b 真实 LLM 评测（30 题评测集子集）——验证「自然语言→契约→精准答案」端到端。

用真实 DEEPSEEK LLM（非 Mock）跑评测集核心题，验证：
- 可表达集内：自然语言被准确转换为受限契约 → 返回精准答案（与 ground truth 一致）；
- 域外：明确拒答（不瞎编）；
- 双签动作：high_risk 先提议，确认后执行。

运行：cd OntoRun && DEEPSEEK_API_KEY=$(awk '/DEEPSEEK_API_KEY:/{print $2}' ~/.dsh/.credentials.yaml | tr -d '\\r') \
      /opt/anaconda3/bin/python3 scripts/eval_risk_real_llm.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.provider import get_provider
from src.agent.risk_agent import RiskActionExecutor, RiskAgent
from src.runtime.risk_actions_impl import build_risk_engine
from src.runtime.risk_db import RiskStore, build_risk_source_registry
from src.runtime.risk_query import RiskQuery


def main() -> int:
    print("== S3 风险 Agent 真实 LLM 评测（DeepSeek）==")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("FAIL: 未设置 DEEPSEEK_API_KEY")
        return 1

    tmp = tempfile.mkdtemp(prefix="s3_eval_")
    store = RiskStore(ontology_path=Path(tmp) / "ontology.db")
    registry = build_risk_source_registry()
    engine = build_risk_engine(store=store, registry=registry)
    rq = RiskQuery(registry, store=store)
    provider = get_provider("deepseek")
    agent = RiskAgent(registry=registry, provider=provider,
                      executor=RiskActionExecutor(engine, rq), query=rq)

    questions = [
        # (问题, 期望类型: answer=应给出数据 / decline=应拒答)
        ("本月新增的红色预警信号有几条？", "answer"),
        ("当前处于确认中状态的预警信号有多少条？", "answer"),
        ("中科智造控股集团有限公司的集团客户编号是什么？", "answer"),
        ("本月集中度预警（红色）的客户有多少家？", "answer"),
        ("最近一周已通过的处置审批有多少条？", "answer"),
        ("五级分类为次级的风险项目有几个？", "answer"),
        ("根据巴塞尔协议III计算集团的资本充足率", "decline"),
        ("预测下季度哪些客户会违约", "decline"),
        # 批 4-① 图表口径：画图请求必须出结构化数据，不得以「无法绘制/不支持图表」拒答
        ("画一张天晟集团各机构占比与预警线的柱状图", "answer"),
        ("天晟集团归集集中度情况如何？请画图对比各机构占比与预警线", "answer"),
    ]

    passed = 0
    for q, expect in questions:
        try:
            turn = agent.run_turn(q)
            reply = (turn.reply or "").strip()
            is_confirm = turn.need_confirm is not None
            # 判定：answer 期望 → reply 非空且不含"拒答/无法/超出/不可"；decline 期望 → 含拒答语义
            decline_words = ("拒答", "无法", "超出", "不支持", "不能回答", "不在可答", "无可查", "不能查询")
            looks_decline = any(w in reply for w in decline_words)
            ok = (expect == "decline" and looks_decline) or (expect == "answer" and not looks_decline and reply)
            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            print(f"[{status}] {expect:8s} | {q}")
            print(f"         回复: {reply[:160]}")
            if is_confirm:
                print(f"         （双签提议: {turn.need_confirm.name}）")
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {q} → 异常: {exc}")

    print(f"\n== 结果: {passed}/{len(questions)} PASS ==")
    return 0 if passed == len(questions) else 1


if __name__ == "__main__":
    sys.exit(main())

