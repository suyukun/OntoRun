"""自动映射子包（蓝图 v0.3）。

E2 自动映射四技法（核心算法，测透）：
- 字段推断（列名→属性，snake_case→PascalCase，is_technical 标记）
- FK 检测（跨表主键/外键同名 + 基数推断 1:1/1:N/M:N）
- 值格式容错（SUP-001 ↔ SUP001 归一）
- 备用键匹配（自然语言名 → 实体；可选 LLM 辅助）

E7 宽表拆分：保留最小实现（一实体一表拆分），增量更新三层（同步/处理/索引）
降 TODO 注释（补丁 B3）。

P0 仅子包骨架；P3 实现具体算法。
"""

from src.builder.mapping import (
    alias_matcher,
    annotate,
    fk_detection,
    naming,
    repo,
    value_format,
    wide_split,
)
from src.builder.mapping.annotate import (
    MappingCandidate,
    MappingCandidateService,
    classify,
)
from src.builder.mapping.auto_map import AutoMapResult, auto_map_from_inference

__all__ = [
    "AutoMapResult",
    "MappingCandidate",
    "MappingCandidateService",
    "alias_matcher",
    "annotate",
    "auto_map_from_inference",
    "classify",
    "fk_detection",
    "naming",
    "repo",
    "value_format",
    "wide_split",
]
