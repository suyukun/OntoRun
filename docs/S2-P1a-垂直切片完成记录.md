# S2 P1a 垂直切片完成记录（2026-08-21）

> 编制：Rose ｜ 状态：P1a 数据侧 + 本体映射侧已穿通，阶段末全量验证中
> 依据：S2 开发计划 v0.3（P1a 门禁）+ DES 切片规划 v0.2 + 两份 P1a 设计稿（Jack 已验收）

## 一、P1a 目标与门禁
P1a = 3 系统（ERP/MES/WMS）×1 表（物料主数据）+ 一物多码注入 + 本体映射（3 编码→1 物料）+ 查询契约 v0.1 穿通。
门禁：MARA 确定性（SHA256 同）· 注入率 ±2% · 编码 100% · 跨系统映射可查 · Jack 业务验收。

## 二、交付物（git 链）
| commit | 内容 |
|---|---|
| 5a0359f | 两份 P1a 设计稿（数据侧 + 架构侧） |
| f08b786 | Jack 验收落盘（5 项拍板全过） |
| c46eb1b | DES 数据生成器（src/des/）+ 数据侧门禁 16 条 |
| b922baa | 本体映射（Material/Code 进 Registry）+ 物化器 + 契约执行器 + 映射侧门禁 15 条 |

## 三、验证结果（全绿）
1. **数据侧门禁** tests/test_des_p1a_data.py：16 绿（A 编码100%+CCC重算 / B 注入率15.00% / C 确定性SHA256 / D 跨系统无孤儿）
2. **映射侧门禁** tests/test_des_p1a_mapping.py：15 绿（物化锚点 200/830 / V1-V5 拒答 9 条 / DQ-01+Q2+Q3 执行 / reconcile）
3. **DQ-01 端到端**：物化 200 Material + 830 Code → 契约查询「哪些物料一物多码？」返回 30 条（含 5 码 codes 数组）→ 与数据侧注入集对账 ok=True（30=30, ratio=0.15, 0 差异）
4. **既有回归**：增量 94 passed；全量 pytest 阶段末验证中
5. **ruff**：src/ tests/ 全绿
6. **golden 快照**：随 Registry 新增 Material/Code 重新生成（tools 查询工具枚举含 material/code，只读不写回，符合设计）

## 四、顺带修复（P1a 阶段末）
- golden 快照：schema 变更需同步（测试契约明示），已重生成
- 3 个既有 builder 子包 docstring 缺「蓝图 v0.3」引用（S1 基线即红，非 P1a 回归）：mapping/extraction/logic 已补

## 五、待确认 / 后续
- 契约聚合标量返回字段名（row_count vs count）留契约 v0.2（D3 head-to-head 30 问后定）
- P1b：10-20 表 100 万行级 + 量级测试（5 个代表性查询 P95+内存达标）
- 第二企业样例验证「同模板不同企业」复用性 → P1b
