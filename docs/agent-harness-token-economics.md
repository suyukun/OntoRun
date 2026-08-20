# GLM5.3 长程 Coding 方法论拆解 —— 质量优先的 Harness 最佳实践（v2：业界对照版）

> 日期 2026-08-20 ｜ 来源：OntoRun P4 子代理会话日志实证（research/p4-session-archive/）+ 业界研究对照 + Jack 定调（质量优先）
> 状态：v2。v1 提炼 8 条方法论；v2 与业界研究对照、对抗性思考、收敛出 harness 机制优化建议。

## 〇、一句话结论
GLM5.3 的「笨」= 可复制的工程化推进纪律（8 条）；与业界研究对照后全部得到印证，但**真正的质量杠杆在验证层不在生成层**（业界共识：agent 自评/自测不可信）；方法论纪律的价值在于把模型自觉变成机制强制。

## 一、8 条方法论 vs 业界研究对照表

| # | 我的提炼（P4 实证） | 业界对应 | 印证/修正 |
|---|---|---|---|
| 1 | 规格优先清单 | SWE-agent 的 ACI（agent-computer interface，arxiv 2406.00515）；OpenAI Skills 原语；Anthropic 长任务工作流 | 印证：接口/上下文设计决定质量；修正：应系统化为「读什么、不读什么」的接口规范，非临时清单 |
| 2 | 设计先行禁止早产 | Plan-then-Execute 范式（arxiv 2605.14290）；L2MAC 结构化规划（arxiv 2310.02003） | 印证：规划先行是主流范式，非 GLM 独有 |
| 3 | 小批量推进 | 分解粒度优化（Microsoft Learn/AAAI 模块）；过细分解有 spawn overhead 与上下文重放成本 | 修正：粒度有最优区间，不是越细越好；需数据校准 |
| 4 | 工具纪律显式化 | SWE-agent ACI；CodeAct 行动空间设计（arxiv 2402.01030） | 印证：行动空间（工具用法的显式规范）是质量关键变量 |
| 5 | 写后自检 | Reflexion / ReflexiCoder（ACL 2026）/ Self-Refine；「让测试决定，别让模型自判」（腾讯云实践） | 印证：自检必须外接验证；纯模型自评不可信 |
| 6 | 假设即验证 | CodeAct 运行时反馈；「We Let an AI Agent Say I Passed」CircleCI | 印证：验证是硬问题——For Coding Agents, Verification Is Now the Harder Problem |
| 7 | 断点恢复协议 | OpenAI Compaction（server-side）；session persistence；L2MAC 状态管理 | 印证：上下文/状态管理是长任务核心原语（Skills+Shell+Compaction） |
| 8 | 对工具输出质疑 | Rethinking the Value of Agent-Generated Tests（arxiv 2602.07900）；PRoPE 属性测试验证（2506.18315） | 印证：agent 产物（含测试）不可信，需独立验证；质疑是美德 |

## 二、对抗性思考（我的 8 条哪里可能错）

1. **相关性 ≠ 因果性**：P4 全绿可能是模型能力+任务特性+运气，不是 8 条纪律的因果贡献。需要对照实验（有纪律 vs 无纪律 prompt，量化返工率）才能下结论。
2. **过度纪律的隐性成本**：小批量推进=更多工具往返=每步重放上下文更多（token 增长）；规格清单过严=探索不足、错过关键信息（GLM turn1 的 40 步侦查本身也是开销）。纪律要服务于质量，不是为纪律而纪律。
3. **overthinking 风险（顶会反方证据）**：Do NOT Think That Much（ICML 2025）、Don't Think Longer Think Wisely（NeurIPS 2025）、The Evolution of Thought（ACL 2026）、Think Deep Not Just Long（ICML 2026）——长思考≠聪明思考，GLM5.3 的 145x thinking 在简单任务上是纯浪费；强推 thinking 到非推理模型可能只增 token 不增质量。
4. **验证层才是真瓶颈**：业界共识=验证比生成难（agent 自生成测试不可信，2602.07900）。我的 8 条只有「写后自检」（生成侧），缺独立验证机制——P4 的 39 个测试是 agent 自写自跑，若没有测试角色 red-team + Rose 验收（我们的制度恰好有），质量就是自说自话。
5. **模型分层可能被高估**：trae 用户实测 GLM5.3 在 coding 任务性价比好；「简单任务用快模型」缺乏质量无损的证据——质量敏感项目也许应全程强模型，省钱只在质量不敏感任务做。

## 三、harness 机制优化建议（对抗性收敛）

| 优先级 | 机制 | 依据 | 落地 |
|---|---|---|---|
| P0 | **独立验证层强化**：测试角色 red-team + Rose 验收 + governance 机器检查 + 阶段末全量，从「流程存在」升级为「质量门禁」 | 验证是业界公认难点；agent 自测不可信 | 已有骨架（两档制），强化 red-team 深度 |
| P0 | **计划评审门**：复杂任务先交文件级实施计划，Rose 评审放行才准写码 | GLM 的「动笔前输出计划」+ Plan-then-Execute | 派活模板加一条硬规则 |
| P1 | **模块级测试门**：每完成一个模块必须跑对应增量测试（把「写后自检」机制化，不靠模型自觉） | Reflexion 外接验证；两档制已有 | 派活模板：模块完成=代码+测试+跑绿三件套 |
| P1 | **验证代理独立性**：写码子代理与验收子代理分离（同 agent 自评=无效，AGENTS.md 纪律 3 已有，扩大执行） | 2602.07900；AGENTS.md | 保持 |
| P2 | **effort 分级**：复杂任务高 effort（thinking），简单任务关 thinking/低 effort | overthinking 反方证据（ICML/NeurIPS/ICLR 2026） | 等模型切换时配 provider 能力表 |
| P2 | **分解粒度数据校准**：记录每任务步数/上下文/返工率，找最优区间（>60 步必拆是经验值，非定论） | 分解粒度研究（MS/AAAI） | 建轻量台账 |
| P2 | **上下文接口规范**：把「grep/offset 定位、只读必要段落、规格要点直写 prompt」从建议升级为派活模板配置 | OpenAI Skills/Compaction；SWE-agent ACI | 派活模板 |

## 四、待验证假设（不预设结论）
- [ ] H1：8 条方法论对非推理模型（快模型）有正迁移（对照实验）
- [ ] H2：计划评审门能拦截早期方向错误、降低返工率（对比有无评审门的任务）
- [ ] H3：独立验证层对最终质量的贡献 > 生成侧纪律（验证成本 vs 返工成本）
- [ ] H4：分解粒度存在最优区间，且与任务复杂度相关（台账数据积累后检验）
- [ ] 参考材料：SWE-agent(2406.00515)｜CodeAct(2402.01030)｜Plan-then-Execute(2605.14290)｜ReflexiCoder(ACL2026)｜agent tests(2602.07900)｜overthinking(ICML/NeurIPS/ACL 2025-26)｜OpenAI Agentic Primitives｜MS Learn 分解粒度

## 附：成本控制（次要维度，原则：不牺牲质量省钱）
- 切便宜模型只用于质量不敏感任务；任务拆分/上下文控制/额度预算为运营层，见 v1 报告
