"""逻辑规则与动作类型子包（重写蓝图 v0.3 §3 / §4 logic_rules+action_types+action_runs）。

职责（P4 已实现）：
- 逻辑规则真实推导（discovery.py，不硬塞固定模板，§10 决策 1.1.3）：从
  已发布 object_types 的 property_schema 实际推导（required/enum/数值边界/
  状态流转链），expression 为结构化可机器执行 JSON；
- 规则状态机（rules_repo.py）：draft->reviewed->published，复用
  src.builder.status_machine（E4，补丁 B4：P4 只做逻辑/动作状态机）；
- 动作类型对接（action_types.py）：runtime 内置动作 upsert 成 action_types
  元数据（单一事实来源 = 运行时引擎，builder 不复制逻辑）；submission_criteria
  可引用 published 逻辑规则（数据结构打通）；
- E6 快照审计（action_runs.py）：动作执行（真实 run 与 dry_run）写
  before/after 快照 + audit_ref（引用 audit_log.audit_id 对账，不复制真相）。

注意补丁 A2：动态对象类型的写回列发布期 TODO；本子包只登记动作元数据 +
E6 审计，不执行动态写回。
"""
