"""API 层响应模型与错误码映射（B3，技术方案 §4）。

- 统一响应信封 {request_id, outcome, data|error}（§4.1）；
- §4.3 错误码全集 → 中文消息 + HTTP 状态（业务码一律 200，语义在信封内，§4.2）；
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

# Builder 子系统错误码（蓝图 v0.3 §9-P1 / 补丁 A1）：4xx 表达违规语义
BUILDER_ERROR_MESSAGES: dict[str, str] = {
    "BUILDER_OBJECT_TYPE_NOT_FOUND": "对象类型不存在",
    "BUILDER_LINK_TYPE_NOT_FOUND": "链接类型不存在",
    "BUILDER_INVALID_PROPERTY_SCHEMA": "property_schema 不合法（缺 PK / 非 JSON Schema / 缺 required）",
    "BUILDER_INVALID_STATUS_TRANSITION": "非法状态流转（仅 draft→reviewed→published 合法）",
    "BUILDER_DELETE_NOT_ALLOWED": "仅 draft 可删除",
    "BUILDER_NAME_CONFLICT": "与内置类型同名（补丁 A1：拒绝 publish / 拒绝注册）",
    "BUILDER_UNKNOWN_SOURCE_TYPE": "link.source_type_id 不在已发布 object_types 中",
    "BUILDER_UNKNOWN_TARGET_TYPE": "link.target_type_id 不在已发布 object_types 中",
    "BUILDER_LINK_ENDPOINT_UNRESOLVED": "link 两端类型未注册",
    "BUILDER_INVALID_REQUEST": "请求参数不合法（category/cardinality 等枚举越界）",
    # P2 新增
    "BUILDER_DATASET_NOT_FOUND": "数据集不存在",
    "BUILDER_DATASET_FILE_MISSING": "数据集源文件丢失",
    "BUILDER_PIPELINE_NOT_FOUND": "管道不存在",
    "BUILDER_INVALID_DAG": "DAG 校验失败（环/重复 id/未知节点/自环）",
    "BUILDER_CURATED_NOT_FOUND": "curated 数据集不存在",
    # P3 新增
    "BUILDER_MAPPING_NOT_FOUND": "映射记录不存在",
    "BUILDER_EXTRACTION_NOT_FOUND": "提取任务不存在",
    # P4 新增（逻辑规则 / 动作类型 / E6 动作执行）
    "BUILDER_LOGIC_RULE_NOT_FOUND": "逻辑规则不存在",
    "BUILDER_OBJECT_TYPE_NOT_PUBLISHED": "对象类型未发布（逻辑推导只接受已发布 object_types）",
    "BUILDER_LOGIC_EXPRESSION_INVALID": "逻辑规则表达式不合法（结构化可机器执行的 JSON）",
    "BUILDER_LOGIC_RULE_NOT_PUBLISHED": "submission_criteria 引用的逻辑规则不存在或未发布",
    "BUILDER_ACTION_TYPE_NOT_FOUND": "动作类型不存在",
    "BUILDER_ACTION_NOT_PUBLISHED": "动作类型未发布，不可执行",
    "BUILDER_ACTION_NOT_EXECUTABLE": "动态对象类型动作的写回执行列发布期 TODO（补丁 A2）",
}
ERROR_MESSAGES.update(BUILDER_ERROR_MESSAGES)

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
        # Builder 错误码 HTTP 状态映射（业务类非法流转/校验失败 → 4xx）
        "BUILDER_OBJECT_TYPE_NOT_FOUND": 404,
        "BUILDER_LINK_TYPE_NOT_FOUND": 404,
        "BUILDER_INVALID_PROPERTY_SCHEMA": 400,
        "BUILDER_INVALID_STATUS_TRANSITION": 400,
        "BUILDER_DELETE_NOT_ALLOWED": 400,
        "BUILDER_NAME_CONFLICT": 400,
        "BUILDER_UNKNOWN_SOURCE_TYPE": 400,
        "BUILDER_UNKNOWN_TARGET_TYPE": 400,
        "BUILDER_LINK_ENDPOINT_UNRESOLVED": 400,
        "BUILDER_INVALID_REQUEST": 400,
        # P2
        "BUILDER_DATASET_NOT_FOUND": 404,
        "BUILDER_DATASET_FILE_MISSING": 410,
        "BUILDER_PIPELINE_NOT_FOUND": 404,
        "BUILDER_INVALID_DAG": 400,
        "BUILDER_CURATED_NOT_FOUND": 404,
        # P3
        "BUILDER_MAPPING_NOT_FOUND": 404,
        "BUILDER_EXTRACTION_NOT_FOUND": 404,
        # P4
        "BUILDER_LOGIC_RULE_NOT_FOUND": 404,
        "BUILDER_OBJECT_TYPE_NOT_PUBLISHED": 400,
        "BUILDER_LOGIC_EXPRESSION_INVALID": 400,
        "BUILDER_LOGIC_RULE_NOT_PUBLISHED": 400,
        "BUILDER_ACTION_TYPE_NOT_FOUND": 404,
        "BUILDER_ACTION_NOT_PUBLISHED": 400,
        "BUILDER_ACTION_NOT_EXECUTABLE": 400,
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
