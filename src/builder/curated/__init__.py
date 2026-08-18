"""Curated 数据集子包（重写蓝图 v0.3 §3 / §4 curated_datasets 表）。

职责：把管道产物（curated_datasets 表）从 draft 推到 reviewed / approved；
质量评分 quality_score JSON（含完整性/一致性/重复率等维度，P2 详细定义）。

审核状态机（补丁 B4：E4 仅 P1 object_types/link_types 走发布；P0 阶段 Curated
仍走 draft→reviewed→approved，状态字段与蓝图 §4 一致）。

P0 仅子包骨架；P2 实现审核动作。
"""
