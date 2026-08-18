"""LLM 提取子包（重写蓝图 v0.3 §3 / §8 / 补丁 C3）。

E3 文档 → 实体/关系/动作；入库前七道校验器（fatal/error/warning/info）：
1. 结构（合法 JSON、必含 entities 数组）
2. 必填字段（实体 name/type、关系 source/target/type、动作 name）
3. 引用完整性（关系两端必须指向存在的实体）
4. 去重（按 (name,type) 与 (source,type,target) 去重）
5. 类型白名单（实体类型在预设域集合内，>50% 自定义则告警）
6. 语法校验（动作 function_code 用 ast.parse）
7. 语义引用（linked_entities/linked_logic 指向真实存在项）

extraction_tasks 表**无 progress 字段**（同步执行无进度语义，补丁 C3）。

P0 仅子包骨架；P3 实现提取器 + 七道校验器。
"""
