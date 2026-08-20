# GLM5.3 长程 Coding 方法论拆解 —— 质量优先的 Harness 最佳实践

> 日期 2026-08-20 ｜ 来源：OntoRun P4 子代理完整会话日志（11167 行/6MB，GLM5.3 on 火山 Coding Plan）+ Jack 观察 ｜ 状态：v1，待深入
> 出发点（Jack 定调）：**最最重要的是输出质量**——模型层可换、质量难提升；GLM5.3「笨笨的、一板一眼」的长程 coding 思路才是研究对象；成本控制只是次要维度。

## 〇、一句话结论
GLM5.3 在长程任务里表现出的不是"笨"，而是**可复制的工程化推进纪律**——把它拆成 8 条显式方法论，写进 harness 派活模板，任何模型都能获得类似的质量下限。

## 一、实证：它实际怎么干（日志原文采样，逐条对应）

| # | 行为（日志原文） | 方法论本质 |
|---|---|---|
| 1 | "Let me start by reading the required documents... focus on §4 data model, §5 API, §9 P4 row, §10 design decisions" | **先读规则禁动手**：按优先级清单系统性读规格，不是漫游 |
| 2 | 25 段设计推理后才写第一行代码（turn1=40 步纯侦查+设计，173K thinking） | **先画全图再动手**：设计期拒绝早产，宁慢勿错 |
| 3 | "Now I have the full picture. Time to plan... Files to create: 1. rules_repo.py 2. ..." | **动笔前输出实施计划**：文件级清单，让设计可审 |
| 4 | "store.py done. Now action_engine.py: add dry_run + snapshot_observer. Need to re-read the relevant section first (edit requires recent read)" | **小批量推进 + 遵守工具纪律**：一次一个模块，edit 前必 read |
| 5 | "Wait - there's an issue in my discovery.py: the template literal double-backslash is wrong, Python regex needs single backslash" | **写后立即自查**：当场抓转义 bug，不等测试暴露 |
| 6 | "I used rt.registry_has_action(name) - that doesn't exist... I need to add a helper or check differently" | **发现假设 API 不存在立即修正**：不自欺、不糊弄 |
| 7 | "I'm resuming from a breakpoint. Note: I already read test_agent_provider_deepseek.py earlier (the stub client pattern)" | **恢复时先回忆既有上下文**：不重复读、不重推设计 |
| 8 | "7 errors: 1. SIM118... wait, but sqlite3.Row is not a dict! does `in` work on Row?" | **修 lint 也带质疑**：不盲从工具，对抗性验证 |

## 二、8 条可迁移方法论（harness 派活模板直接可写）

1. **规格优先清单**：派活时给"必读文件+重点段落"清单，要求读完才能动手（P4 已做，效果显著：turn1 全部精力花在理解上）
2. **设计先行、禁止早产**：复杂任务要求先输出「实施计划」（文件级），Rose 可审可拦，之后才准写码
3. **小批量提交节奏**：一次一个模块，改完即自查；禁止一次写 5 个文件再统一看
4. **工具纪律显式化**：edit 前必须 read 最新内容、grep 定位不漫游、bash 带 timeoutMs
5. **写后自检清单**：转义/引号/API 签名/导入路径——写码步骤后固定插一个自检步
6. **假设即验证**：用到 API 先确认存在与签名；发现假设错误立即修正并记录，不静默绕过
7. **断点恢复协议**：中断/唤醒时先 3 行注记（已做到哪/下一步/关键上下文在哪），恢复时先回忆再动手
8. **对工具输出保持质疑**：lint/编译/测试报错要判断"是否真问题"，不无脑修（P4 的 sqlite3.Row 案例）

## 三、成本控制（次要维度，简表）

| 手段 | 机制 | 备注 |
|---|---|---|
| 切便宜模型 | 直接降单价 | 质量可能降，只用于简单任务 |
| 任务拆分（>60 步必拆） | 上下文小→折算少 | 质量也受益（聚焦） |
| 上下文注入控制 | 只读必要段落 | 防膨胀 |
| 额度预算/窗口<30% 暂停 | 防窗口烧穿 | 运营层 |

> 成本优化原则：**永远不牺牲质量换省钱**；省钱只在"质量不敏感"的任务上做。

## 四、后续深入方向（点子 2026-08-20 ②）
- [ ] 把 8 条方法论落成 `agent-coding-methodology` skill（跨项目复用）
- [ ] 对比实验：同一任务用方法论 prompt vs 无约束 prompt，量化质量差异（测试通过率/返工率）
- [ ] 探针：方法论对"非推理模型"（如 DeepSeek-V3 快模型）的迁移增益——若有效，harness 可低配高质量
- [ ] 火山双层计费公众号选题（点子 2026-08-20 ①，独立线）