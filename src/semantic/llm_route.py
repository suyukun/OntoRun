"""LLM intent routing → structured primitive request ({measure, dimensions,
time_from, time_to}), constrained by the L2 registry (src/fortune_semantic).

Contract: the LLM may only output registered primitive ids (invention →
E_ROUTE_INVALID → keyword fallback) or {"reject": true} for questions outside
every registered domain. Any failure returns {"error", "error_code"} and the
caller falls back to keyword matching (degraded but correct). The LLM never
produces SQL or numbers — execution belongs to fortune_semantic.compiler.
"""

import json
import re
import time

from src.fortune_semantic.registry import REGISTRY

from . import config, errors, sanitize
from .rules import RoutePlan

JSON_RE = re.compile(r"\{[\s\S]*\}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _system_prompt() -> str:
    """Primitive catalog as routing constraint — derived from the registry."""
    rng = config.data_range()
    measures = "\n".join(f"- {m.id}: {m.description}" for m in REGISTRY.measures.values())
    dims = "\n".join(
        f"- {d.id}: {d.description}"
        + (f"（粒度参数可选：{'/'.join(d.grains)}，写法 time_grain=<grain>）" if d.grains else "")
        for d in REGISTRY.dimensions.values()
    )
    return (
        "你是语义层的意图路由器。唯一任务：把用户问题映射为结构化查询原语，并抽取时间参数。\n"
        '只输出一个 JSON 对象：{"measure": "度量id", "dimensions": ["维度id 或 维度id=参数"], '
        '"time_from": "YYYY-MM-DD", "time_to": "YYYY-MM-DD"}。\n'
        "硬约束：\n"
        "1. measure 只能从度量清单选择，dimensions 每项只能从维度清单选择，禁止发明；\n"
        "2. 与所有已注册度量无关的问题（其他业务域）只输出 {\"reject\": true}，不猜；\n"
        "3. 时间取问题中的明确表述，缺失时对应字段传 null；时间必须落在数据覆盖范围内："
        f"{rng['min']} ~ {rng['max']}；\n"
        "4. 你不生成 SQL、不计算任何数字。\n"
        "度量清单：\n" + measures + "\n维度清单：\n" + dims
    )


def validate_plan(data: dict) -> RoutePlan | None:
    """Enum-validate parsed LLM output → RoutePlan; None = invalid (invented
    primitives / wrong shape). {"reject": true} maps to a reject RoutePlan."""
    if data.get("reject") is True:
        return RoutePlan(reject_domain="LLM 判定范围外")
    measure = data.get("measure")
    if measure not in REGISTRY.measures:
        return None
    raw_dims = data.get("dimensions")
    if raw_dims is None:
        raw_dims = []
    if not isinstance(raw_dims, list):
        return None
    dims: list[str] = []
    for entry in raw_dims:
        dim_id, _, arg = str(entry).strip().partition("=")
        dim_id, arg = dim_id.strip(), arg.strip() or None
        dim = REGISTRY.dimensions.get(dim_id)
        if dim is None:
            return None
        if dim.grains is not None:
            if arg not in dim.grains:  # time_grain needs a registered grain
                return None
            dims.append(f"{dim_id}={arg}")
        elif arg is not None:
            return None
        else:
            dims.append(dim_id)
    return RoutePlan(measure=measure, dimensions=tuple(dims))


def llm_route(question: str) -> dict:
    """Route one question. Success: {"plan", "time_from"?/"time_to"?, "raw"(sanitized),
    "ms", "model"}. Failure: {"error", "error_code"(E_ROUTE_FALLBACK|E_ROUTE_INVALID)}."""
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
    except Exception as exc:  # noqa: BLE001 有意兜底：LLM 任何失败都降级，不砸断链路
        return {"error": f"LLM 调用失败: {type(exc).__name__}", "error_code": errors.E_ROUTE_FALLBACK}

    match = JSON_RE.search(raw)
    if not match:
        return {"error": f"LLM 输出非 JSON: {raw[:80]}", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    try:
        data = json.loads(match.group(0))
    except ValueError as exc:
        return {"error": f"JSON 解析失败: {exc}", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    if not isinstance(data, dict):
        return {"error": f"LLM 输出非对象: {raw[:80]}", "raw": raw, "ms": ms, "error_code": errors.E_ROUTE_INVALID}
    plan = validate_plan(data)
    if plan is None:  # enum hard validation: invented primitives are rejected
        return {"error": f"LLM 输出了未注册原语 → 拒绝: {raw[:80]}", "raw": raw, "ms": ms,
                "error_code": errors.E_ROUTE_INVALID}
    out: dict = {"plan": plan, "raw": raw, "ms": ms, "model": config.LLM_MODEL}
    for field in ("time_from", "time_to"):
        value = data.get(field)
        if isinstance(value, str) and DATE_RE.match(value):
            out[field] = value
    return out
