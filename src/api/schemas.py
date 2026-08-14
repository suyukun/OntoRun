"""API 层响应模型与错误码映射（B3，技术方案 §4）。

- 统一响应信封 {request_id, outcome, data|error}（§4.1）；
- §4.3 错误码全集 17 码 → 中文消息 + HTTP 状态（业务码一律 200，语义在信封内，§4.2）；
- 读侧错误码（OBJECT_TYPE_NOT_FOUND 等）属 HTTP 层，不在 §4.3 业务全集内。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.runtime.action_engine import ERROR_MESSAGES as RUNTIME_ERROR_MESSAGES

# §4.3 业务错误码 → 中文消息（与运行时 ERROR_MESSAGES 同源，防双轨）
ERROR_MESSAGES: dict[str, str] = dict(RUNTIME_ERROR_MESSAGES)

# 读侧/HTTP 层错误码
READ_ERROR_MESSAGES: dict[str, str] = {
    "OBJECT_TYPE_NOT_FOUND": "对象类型不存在",
    "OBJECT_NOT_FOUND": "对象不存在",
    "LINK_NOT_FOUND": "链接不存在或不可从该对象遍历",
    "INVALID_DIRECTION": "非法遍历方向（应为 out/in）",
    "UNKNOWN_FILTER_FIELD": "过滤字段不存在",
    "INVALID_REQUEST": "请求体不合法（JSON 解析失败）",
    "INVALID_ACTOR": "非法操作者（X-Actor 仅允许 human/llm/api）",
}
ERROR_MESSAGES.update(READ_ERROR_MESSAGES)

# 业务错误码（§4.3 全集）→ 200（信封内表达语义）；读侧错误 → 4xx
ERROR_CODE_HTTP_STATUS: dict[str, int] = {code: 200 for code in RUNTIME_ERROR_MESSAGES}
ERROR_CODE_HTTP_STATUS.update(
    {
        "OBJECT_TYPE_NOT_FOUND": 404,
        "OBJECT_NOT_FOUND": 404,
        "LINK_NOT_FOUND": 404,
        "INVALID_DIRECTION": 400,
        "UNKNOWN_FILTER_FIELD": 400,
        "INVALID_REQUEST": 400,
        "INVALID_ACTOR": 400,
    }
)


class ErrorInfo(BaseModel):
    """信封错误体。"""

    code: str
    message: str
    detail: Any = None


class Envelope(BaseModel):
    """统一响应信封：{request_id, outcome, data|error}（§4.1）。"""

    request_id: str
    outcome: str
    data: Any = None
    error: ErrorInfo | None = None
