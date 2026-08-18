"""本体构建子系统（重写蓝图 v0.3 §3 / 补丁 v0.3.1）。

职责：把异构数据（CSV/Excel/JSON/MD/PDF/DOCX）经「连接器 → 管道 → Curated →
自动映射 → LLM 提取 → 逻辑规则 → 动作」流水线，变成可被运行时（§4）消费的
对象类型 / 链接类型 / 动作类型（草稿→审核→发布状态机 E4），最终在应用启动时
**动态合并进现有 ontology/ Registry**（补丁 A1：本体单一事实来源 = 启动合并后
的 Registry；构建产物在运行时只读，参见 A2）。

子包分工（蓝图 §3）：
- connectors：数据接入（文件上传、SQL/REST 发布期）
- pipeline   ：DAG 执行 + E1 三路径（schema_infer/cleanse/flatten/parse_xml/
              doc_to_md/md_to_struct）
- curated    ：质量评分 + 审核（draft→reviewed→approved，补丁 B4）
- mapping    ：E2 自动映射（FK/容错/备用键/基数 + E7 宽表拆分最小实现）
- extraction ：E3 LLM 提取 + 七道校验器
- logic      ：逻辑规则真实推导 + 状态机 + 动作类型对接 + E6 快照审计

P0 交付：仅子包骨架与表结构（BUILDER_SCHEMA_V1 见 runtime.store），
各子包业务实现按 P1-P4 推进。
"""

from src.builder import connectors, curated, extraction, logic, mapping, pipeline

BUILDER_SCHEMA_VERSION: int = 2
"""本体构建 schema 版本号（写入本体库 schema_version 表）。

当前 v2 = 蓝图 §4 全 10 张表 + 补丁修正（extraction_tasks 删 progress、
datasets.kind 扩展 pdf/docx、link_types 加 semantic_name 等）。
"""

__all__ = [
    "BUILDER_SCHEMA_VERSION",
    "connectors",
    "curated",
    "extraction",
    "logic",
    "mapping",
    "pipeline",
]
