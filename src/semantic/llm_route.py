"""LLM intent routing (DeepSeek via OpenAI-compatible SDK), migrated from demo.

Contract: the LLM may only output a rule ID from the registry (invention → reject)
plus date parameters. Any failure returns {"error": ..., "error_code": ...} and the
caller falls back to keyword matching (degraded but correct).
"""

import json
import re
import time

from . import config, errors, sanitize
from .rules import RULES

JSON_RE = re.compile(r"\{[\s\S]*\}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _system_prompt() -> str:
    catalog = "\n".join(f"- {k}: {v.get('desc', '')}" for k, v in RULES.items())
    rng = config.data_range()
    return (
        "你是语义层的意图路由器。唯一任务：把用户问题映射到唯一规则 ID，并抽取时间参数。"
        '只输出一个 JSON 对象：{"rule_id": "...", "params": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}，'
        "rule_id 必须从清单中选择，禁止发明；时间缺失时 params 传空对象；"
        f"时间参数必须落在样本数据可用范围内：{rng['min']} ~ {rng['max']}。\n"
        "与注册规则无关的问题一律 rule_id=OUT_OF_SCOPE。\n规则清单：\n" + catalog
    )


def llm_route(question: str) -> dict:
    """Route one question. Success: {"rule_id", "params", "raw"(sanitized), "ms", "model"}.
    Failure: {"error", "error_code"(E_ROUTE_FALLBACK|E_ROUTE_INVALID), ...}."""
    if config.llm_disabled():
        return {"error": "LLM 路由已禁用（SEMANTIC_DISABLE_LLM）", "error_code": errors.E_ROUTE_FALLBACK}
    key = config.get_env("DEEPSEEK_API_KEY")
    if not key:
        return {"error": "未配置 DEEPSEEK_API_KEY", "error_code": errors.E_ROUTE_FALLBACK}
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=key,
            base_url=config.get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            timeout=config.LLM_TIMEOUT_S,
        )
        t0 = time.time()
        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "system", "content": _system_prompt()}, {"role": "user", "content": question}],
            temperature=0,
            max_tokens=200,
        )
        ms = round((time.time() - t0) * 1000)
        raw = sanitize.sanitize_llm_text(resp.choices[0].message.content.strip())
    except Exception as exc:  # network/model errors → degrade, never crash the chain
        return {"error": f"LLM 调用失败: {type(exc).__name__}", "error_code": errors.E_ROUTE_FALLBACK}

    match = JSON_RE.search(raw)
    if not match:
        return {"error": f"LLM 输出非 JSON: {raw[:80]}", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    try:
        data = json.loads(match.group(0))
    except ValueError as exc:
        return {"error": f"JSON 解析失败: {exc}", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    rule_id = data.get("rule_id")
    if rule_id not in RULES:  # enum hard validation: invented rules are rejected
        return {"error": f"LLM 发明了未注册规则「{rule_id}」→ 拒绝", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    params = {k: v for k, v in (data.get("params") or {}).items() if DATE_RE.match(str(v))}
    return {"rule_id": rule_id, "params": params, "raw": raw, "ms": ms, "model": config.LLM_MODEL}
