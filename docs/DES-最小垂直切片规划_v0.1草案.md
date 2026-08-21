# DES 最小垂直切片规划（v0.2）

> 编制：Rose ｜ 日期：2026-08-21 ｜ 状态：并入 4 模型复核修正（C1-C6 共识 + D1-D3 待 Jack）
> 目标：证明 DES 全链路"穿得通"——1 张主数据表 + 1 个问题 + 1 条本体映射 → ChatBI 能问 1 个真问题 → 方法论 UI 能展示 1 步

## 1. 为什么先做垂直切片（对抗性论证）
- 风险：DES 全量 30-50 表 3-4 周，若"造到一半发现方向错" = 时间沉没；
- 垂直切片 = 最短路径验证"数据真实感 + 问题站得住 + 映射经得起挑刺"三要素；
- 切片跑通后，横向铺开是"复制模式"，风险大降。

## 2. 切片内容（最小集）

| 要素 | 选什么 | 为什么 |
|---|---|---|
| 主数据表 | **MARA 物料主数据**（~200 行） | 制造业核心、编码规则可验（MAT-YYYY-NNNN-CCC）、一物多码问题载体 |
| 问题 | **DQ-01 一物多码**（15% 记录带 BISMT 旧码） | 需求说明书首个问题、跨系统语义冲突的代表、本体映射直观 |
| 本体映射 | 物料实体 hasCode(PLM/ERP/MES) → 3 编码映射 1 概念 | 直接验证"本体=语义层"主张、对接议题 2 映射机制 |

## 3. 全链路验证（穿通判定）

```
YAML 配置 → DES 生成 MARA 表（SQLite）→ 注入一物多码 → 本体映射（物料实体+多码属性）
→ ChatBI 问"哪些物料一物多码？"→ 语义层查询 → 返回物化结果
→ 方法论 UI 展示"数据映射"这一步（输入/输出/为什么/实际跑）
```

**穿通判据（可机验）**：
1. MARA 表生成确定性（同 seed 同配置 → SHA256 相同）；
2. 一物多码注入率 = 配置值（±2%），编码规则 100% 符合；
3. 本体映射：3 个编码 → 1 个物料实体，可查询（DuckDB 物化结果）；
4. ChatBI：问"一物多码物料"→ 正确返回 + 拒答率可测；
5. 方法论 UI：展示映射步骤，绑定真实运行。

## 4. 工作量粗估
- DES 配置系统（YAML 4 层继承）：0.5 周
- MARA 生成 + 问题注入：1 周
- 本体映射 + DuckDB 物化：0.5 周
- ChatBI 最小查询：0.5 周
- 方法论 UI 1 步：0.5 周
- **合计约 3 周**（1 人）



## 6. 关键技术验证（2026-08-21，验证先行）

1. **workflow 模型覆盖生效**：agent(..., { provider:"volc-coding-plan", model:"minimax-m3" }) 确实派出 MiniMax-M3（冒烟测试返回 "MiniMax-M3"），非继承 flash——多模型复核机制可行；
2. **DuckDB 1.5.5 已装**（清华源）；**DuckDB 可直接读 SQLite**（sqlite_scan，无需转换）——双引擎方案成立；
3. **DuckDB 物化聚合验证通过**：从 SQLite 源表 CREATE TABLE AS SELECT ... GROUP BY → 物化聚合表 + 导出 parquet 持久化——ChatBI"预聚合优先"落地路径成立。

## 7. 4 模型复核对本切片的修正（2026-08-21，并入）

| 修正 | 原设计 | 复核后（4 模型共识） | 影响 |
|---|---|---|---|
| R1 系统边界 | 1 企业=1 库 | **1 企业=1 目录，N 系统=N SQLite 文件**（erp.db/crm.db/wms.db）——真实企业系统是独立 schema/独立权限，1 库塞所有系统是 System Silos 反模式 | 切片从 1 表改为 1 企业 3 系统 各 1 表验证跨系统映射（P0，DES 未开工，零返工） |
| R2 配置层 | 4 层 YAML 继承（L0-L3） | **先 2 层**（行业模板 + 企业覆盖），用 YAML anchor/alias，不造配置 DSL（P1） | 配置系统简化 |
| R3 量级 | 25 万行/季度 覆盖 4 倍 | **诚实降级 S2 目标为 100GB-1TB 级**（DuckDB 胜任），设量级 gate（100 万/1 亿行），DES 不宣称验证 PB（P0） | ChatBI 叙事修正 |
| R4 映射验证 | 映射做实 无验收口径 | **定义 50 问题×3 域的 ground truth 标答集，映射 top-5 recall 不小于 80%** 才够 S2 入场券（P0） | 切片加映射验证 |
| R5 流程驱动 | 砍 SimPy/NetworkX | **D1 待 Jack**：复用 SimPy/状态机库 vs 降级 规则+分布采样（P0） | 技术栈待定 |

**切片调整**：垂直切片从 1 表+1 问题+1 映射 升级为 **3 系统×1 表 + 1 跨系统问题（一物多码）+ 本体映射 + 结构化查询契约（含 ground truth 验证）**——既验证真实感，又验证跨系统映射与查询契约，对冲 C1/C2 两个最大风险。

## 8. ChatBI 结构化查询契约 v0.1（pro F4 / m3 F1-1 要求先定契约）

契约 JSON 示例（object_type / filters / aggregations / group_by / link_traversal 字段，≤1 跳链接遍历）：
- object_type: Order
- filters: status=shipped
- aggregations: count(order_id)
- group_by: customer_id
- link_traversal: placed_by, hops=1

这就是 本体到分析引擎 映射的契约；D3（受限结构化查询 vs LLM 写 SQL+守卫）待 Jack 拍板后再定是否保留。


- 议题 1（ChatBI 形态）、议题 2（映射机制）、议题 9（DES 形态）——均已定
- 复用：builder/mapping（fk_detection/naming/alias_matcher）、agent/provider、前端 builder 页