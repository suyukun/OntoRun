"""Error code system (product doc appendix B) + sanitized user-copy mapping."""

E_NET = "E_NET"
E_ROUTE_FALLBACK = "E_ROUTE_FALLBACK"
E_ROUTE_INVALID = "E_ROUTE_INVALID"
E_SQL = "E_SQL"
E_VALIDATION = "E_VALIDATION"
E_PARAM_MISSING = "E_PARAM_MISSING"
E_PARAM_RANGE = "E_PARAM_RANGE"
E_SCOPE = "E_SCOPE"

# User-facing copy per appendix B. Fallback codes are silent to the user (degraded
# success with a warning badge), so their copy is for trace/logs only.
USER_COPY = {
    E_NET: "查询失败：服务未响应",
    E_ROUTE_FALLBACK: "（无感降级：LLM 路由不可用，已用关键词路由回答）",
    E_ROUTE_INVALID: "（无感降级：LLM 输出非法，已用关键词路由回答）",
    E_SQL: "查询执行出错，已记录（{request_id}）",
    E_VALIDATION: "校验未通过，拒绝返回",
    E_PARAM_MISSING: "请问您要查询哪个月份？",
    E_PARAM_RANGE: "当前查询时间超出数据覆盖范围",
    E_SCOPE: "该问题不在当前语义范围内",
}


def user_message(code: str, **fmt) -> str:
    """Map an error code to user copy — never leak internal stacks/details."""
    return USER_COPY.get(code, "查询失败，请稍后重试").format(**fmt)
