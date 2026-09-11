# AI 工程管理开工前方法调研 v0.1

> 命题：多模块一轮轮交付一轮轮返工 = 没想清楚就开工。本文回答「开工前必须完成什么」。
> 调研人：Rose（调研子代理）· 日期 2026-09-11 · 时间盒 60 分钟内完成。
> 来源分级：T1 官方规范/T2 研究机构/T3 大厂工程博客·官方文档/T4 编辑审校媒体/T5 高质量社区（仅作线索）。关键结论尽量 ≥2 独立来源；未核验处显式标注（见 §5）。

---

## 1. 各家方法一览表

| 方法 | 核心机制 | 适用场景 | 来源 |
|---|---|---|---|
| GitHub Spec Kit（v1.0.0，2026-08） | 6 步：/speckit.constitution（项目原则，一次）→ specify → plan → tasks → implement → converge（实现对照 spec 收口，重复直到 Converged）。口号 "Define what to build before building it"；spec 成为可执行上游，不再是用完即弃的脚手架 | 中大型功能、多轮交付、防目标漂移 | [github/spec-kit README](https://github.com/github/spec-kit)（T3）；[Microsoft Learn 配套课](https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-enterprise-developers/4-establish-project-principles-constitution-file)（T3） |
| AWS Kiro（specs 三件套） | requirements.md（用户故事 + EARS 验收标准：WHEN…THE SYSTEM SHALL…）+ design.md（架构/时序图/实现考量）+ tasks.md（离散可勾选任务，每任务有预期产出）。四阶段：需求→设计→实施计划→执行跟踪 | 复杂特性，需要需求可逐条验证 | [kiro.dev/docs/specs](https://kiro.dev/docs/specs/)（T3，官方页 JS 渲染未能取正文）；结构转述见 [promptz kiro-specs](https://github.com/cremich/promptz.lib/blob/main/steering/kiro-specs.md)（T5） |
| Claude Code 官方最佳实践（Anthropic） | 四阶段 Explore → Plan → Implement → Commit，plan mode 强制"先探索后动手"；"给 Claude 一个能跑的检查（测试/构建/lint/截图对比），否则你自己就是验证回路"；CLAUDE.md 只留"删掉会出错"的条目；上下文窗口是第一约束（满了就忘事、出错） | 所有 agent 编码的默认纪律 | [code.claude.com best practices](https://code.claude.com/docs/en/best-practices)（T3，2026-09-11 抓取） |
| OpenAI Codex + AGENTS.md | Codex 生态用项目级 AGENTS.md（构建/测试命令、代码风格、约定）给 agent 稳定上下文；开放格式，60k+ 项目采用，Codex/Jules/Zed 等通吃 | 跨 agent 的项目规则标准化 | [agents.md](https://agents.md/)（T1）；Codex 官方指南 [developers.openai.com/codex](https://developers.openai.com/codex/guides/best-practices)（本机 403 未核验，见 §5） |
| Cursor Rules | 项目级系统指令（.cursor/rules 等 4 种类型），把提示词/脚本/流程固化成团队可共享的规则，agent 每轮自动加载 | 团队级风格与流程固化 | [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)（T3） |
| METR RCT 实证 | 随机对照试验测 AI 提效：早期 2025 工具让资深开源开发者慢 19%（而自认为快 20%）；2026-02 更新：新实验有选择偏差，回访开发者估快 18%（CI −38%~+9%）——感知与实测长期背离，速度主张必须实测 | 评估 AI 团队效率、防止"感觉很快"自欺 | [METR 2025-07](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)（T2）；[METR 2026-02 更新](https://metr.org/blog/2026-02-24-uplift-update/)（T2） |
| 实践者复盘（NearForm，2026-04） | "Context collapse"：约 20 个 prompt 后模型开始自相矛盾、反复重解释，微修正累积成小时级返工（"hidden tax"）；改用 SDD 后"用一份聚焦、自包含的任务替代嘈杂对话"，不一致与返工下降 | 单人/小队 vibe coding 之痛的对照证据 | [NearForm 文章](https://nearform.com/digital-community/why-ill-never-go-back-to-vibe-coding-a-developers-case-for-spec-driven-development/)（T4） |

**防 AI 跑偏的机制（各家交叉验证后的共性，≥2 来源）**：
1. 原则门禁前置：宪法/AGENTS.md/CLAUDE.md/规则——开工前把"不许做什么"写成 agent 每轮必读的文件（Spec Kit constitution check、Anthropic CLAUDE.md、agents.md、Cursor Rules 四源一致）。
2. 验收标准先于代码：EARS / Given-When-Then 写进 spec，逐条可验证（Kiro + Spec Kit 模板）。
3. 未定项显式阻断：Spec Kit 模板用 NEEDS CLARIFICATION 标记，不清零不许 implement。
4. 可跑的 pass/fail 检查：没有机器检查，"看起来完了"是唯一信号，人成了验证回路（Anthropic 原文）。
5. 收口对照（converge）：实现完成后对照 spec/plan/tasks 收口，而不是靠人盯（Spec Kit v1.0 新增步骤）。

---

## 2. 开工前必要工作清单（OntoRun 定制版）

> 原则：最小必要件，不是企业流程。单人+AI 团队砍掉评审会/多人签核，保留可机器验证的骨架。Anthropic 自己说"一句话能说清的 diff 就跳过计划"——所以先分级：
> - S 级（一句话改动）：直接做，不填清单。
> - M 级（单模块功能）：填 A + D。
> - L 级（跨模块/新方向）：填 A + B + C + D 全表。
> 本清单针对 L 级；M 级按需裁剪。每条给"完成的标志"，全勾才许派编码子代理。

### A. 需求分析（Problem Statement）
- [ ] A1 一句话命题：给谁、解决什么问题、成功后世界有何不同。
  完成标志：Jack 用一句话复述后 Rose 无需追问。
- [ ] A2 用户故事 ≤5 条，P1/P2/P3 排序，每条独立可测、独立可交付（Spec Kit：单做 P1 也是一个能用的 MVP 切片）。
  完成标志：砍掉 P2/P3 后 P1 仍自成闭环。
- [ ] A3 验收标准（EARS 或 Given/When/Then），每条挂在一个用户故事下，格式 WHEN <条件> THE SYSTEM SHALL <可观察行为>。
  完成标志：每条验收标准能想出对应的一条测试/命令（名字先写上）。
- [ ] A4 边界条件 ≥3 条：空输入、失败路径、权限外、并发/重复提交类（对标 Spec Kit Edge Cases 节）。
  完成标志：每条边界有一个"系统应当怎样"的明确答案，不是"再说"。
- [ ] A5 非目标（本轮不做什么）显式列出。
  完成标志：Jack 拍板确认；子代理交付物里出现非目标内容 = 退回。

### B. 设计（只定会返工的部分）
- [ ] B1 技术上下文定案：动哪些文件/模块、依赖与版本不变量、数据存哪、怎么测（对标 Spec Kit plan-template 的 Technical Context）。
  完成标志：能画出改动影响面，git diff --stat 的预期范围可预估。
- [ ] B2 关键决策 ≤5 条 + 理由（含备选为什么不用），记入 docs/adr/ 雏形。
  完成标志：每条决策一句话能说清"为什么不是另一个方案"。
- [ ] B3 接口/数据契约：schema、API 形状、表结构——契约先定，实现后动。
  完成标志：契约以代码形式存在（Pydantic/TS 类型/DDL），可 import。
- [ ] B4 宪法门禁检查：对照三条铁律 + 最小实现 + 边界三档（AGENTS.md）逐条过。
  完成标志：检查结果写进 spec 文档，NEEDS CLARIFICATION 清零（Spec Kit 机制）。

### C. 计划（tasks.md 级）
- [ ] C1 任务按用户故事分组，每任务有确切文件路径 + 完成判据（Spec Kit tasks 模板硬性要求带路径）。
  完成标志：Rose 只看 tasks.md 就能派活，无需追问。
- [ ] C2 阻断性前置任务（foundational：如路由壳、注册表骨架）单独成组，未完成不许开故事任务。
  完成标志：前置组有明确"完成即解锁"的判据。
- [ ] C3 并行标记与依赖：可并行的任务标 [P]，串行依赖写明。
  完成标志：并发派活数 ≤4 限额内排得开。
- [ ] C4 时间盒与止损线：预估轮次；同一任务返工 ≥2 轮 → 停，回 B 修 spec，不许第 3 次 patch（自定约定，依据见 §5.3）。
  完成标志：止损线写在任务派发单里，子代理可见。

### D. 验收（开工前就要能跑）
- [ ] D1 可执行验收命令集合：如 pytest tests/test_builder_pX.py -q、cd web && npx tsc --noEmit、三问测试 E2E。注意项目纪律：子代理只跑增量测试，不跑全量 pytest。
  完成标志：开工前先跑一遍这些命令并记录输出（预期红/基线绿），而不是交付后第一次跑。
- [ ] D2 验收看 diff：改动行可追溯到 A 的条目；搭车改动退回。
  完成标志：验收单有"diff ↔ 条目"对照栏。
- [ ] D3 演示路径：Jack 5 分钟能亲手走一遍的验收脚本（点哪里、看什么、应是什么）。
  完成标志：写在 spec 末尾，不靠子代理口述。
- [ ] D4 DoD 一句话声明：什么叫绿、什么不算完（对标 AGENTS.md 验收标准节）。
  完成标志：与 A3 逐条对得上，无新增判据。

**防跑偏运行时条款（开工后）**
- 收口用 converge 思路：交付对照 spec 逐条打勾，不靠"我觉得完了"。
- 返工第 2 轮起，新开会话只带 spec + 失败清单，不带上一轮修补历史（Anthropic：上下文塞满性能劣化，模型会忘掉早期指令——修补循环越长越错）。

---

## 3. 应用示例：管理台重构（L 级）

> 假设声明：三方向目前只有名称，无需求输入；以下按 OntoRun 已知架构（web/ React+AntD 本体驱动 UI、语义接口 API、AGENTS.md 三铁律）演示填法。真实开工前由 Rose 与 Jack 补全真实输入并拍板。

- A1 管理台的代码跟不上本体 schema 演进，每次改 schema 都要手改管理台页面——目标是让管理台完全由 schema 元数据驱动，改 schema 零页面改动。
- A2（示例裁到 2 条）US1 (P1)：管理员打开对象管理页，看到注册表中全部对象及其链接/动作定义，与 src/ontology 注册表一一对应。US2 (P2)：管理员在页面上编辑动作参数约束并保存，刷新后仍生效（写回注册表定义而非页面硬编码）。
- A3（EARS 示例）WHEN 管理员打开 /admin/objects THEN 界面 SHALL 列出对象注册表中的全部对象键（断言：列表项 = 注册表 keys，无硬编码条目）；WHEN 注册表新增一个对象并刷新 THEN 管理台 SHALL 无需代码改动即显示该对象。
- A4 边界：注册表为空 → 显示空态而非报错；schema 加载失败 → 显式错误卡片；未授权角色 → 403 页而非空白。
- A5 非目标：不改语义接口 API（src/api）、不改本体 schema 定义本身、不引入新 UI 框架/组件库、不做权限矩阵（发布期）。
- B1 动 web/src 管理台路由与组件；接口契约沿用语义 API 的 schema 元数据端点；测试 vitest + tsc --noEmit。决策示例：列表数据运行时从元数据端点取，而非构建期导入注册表（理由：改 schema 免重建前端；备选"构建期导入"因需重新构建被否）。
- B4 宪法检查：本体驱动 UI（关键设计决策 2）✅；不动 schema ✅；最小实现（不先做权限矩阵）✅。
- C1 示例：T001 [US1] web/src/admin/ObjectList.tsx——渲染注册表对象列表，vitest 断言列表=注册表 keys；T002 [P][US1] web/src/admin/…。前置组：管理台路由壳 + schema 元数据 mock。
- C4 止损：US1 返工 ≥2 轮 → 停，回 B1 重查契约；预期 1 轮过。
- D1 开工前先跑：cd web && npx tsc --noEmit（基线绿）+ npm run test -- ObjectList（预期红：组件不存在）+ npm run lint。记录基线输出。
- D2 验收 diff 对照 A2/A3 条目；A5 内容出现即退回。
- D3 Jack 演示路径：npm run dev → 开 /admin/objects → 对照注册表键 → 在注册表临时加一个测试对象 → 刷新页面看到它出现 → 撤销。
- D4 绿 = D1 全绿 + D3 走通 + 无搭车 diff；不算完 = 页面有任一硬编码对象名。

---

## 4. 直接回答本次五问（结论版）

1. Spec 要素：用户故事（排序+独立可测）、EARS/GWT 验收标准、边界条件、功能需求（FR-x MUST 句式）、非目标/约束（NEEDS CLARIFICATION 清零才开工）；防跑偏靠宪法门禁 + converge 对照收口。
2. 官方纪律：Anthropic explore→plan→implement→commit，plan mode 先行，"一句话 diff 免计划"；给 agent 可跑的 pass/fail 检查；CLAUDE.md/AGENTS.md/Cursor Rules = 项目规则固化为 agent 必读文件。
3. 验收前置：验收标准写进 spec 且每条映射一条可执行检查（测试/构建/lint/截图对比），开工前命令先跑出基线；Anthropic 原话——没有可跑检查，"你自己就是验证回路"。
4. 防返工：唯一 RCT（METR）证明感知与实测背离且效应随情境反转——必须实测不猜；实践者证据指向 context collapse 是多轮修补越修越坏的机理（Claude 文档同源：上下文满→忘指令→出错）；量化"一次说清 vs 多轮修补"的公开研究未找到（见 §5）。
5. 轻量适配：分级触发（一句话改动免流程）；最小必要件 = 一句话命题 + 非目标 + 可跑验收命令 + 任务带文件路径；砍掉评审会/签核，用"Jack 复述确认 + 机器门禁"替代。

## 5. 诚实标注：未找到 / 存疑 / 未核验

1. OpenAI Codex 官方 best practices 逐字未核验：developers.openai.com 本机抓取 403。Codex 部分仅能确认 AGENTS.md 生态事实（agents.md 已核验）；指南具体条目是转述，未采信为结论依据。
2. GitClear《AI 代码质量 2025》未核验：官网 403（Cloudflare）。"AI 生成代码重复率上升/重构率下降"仅为线索（T5 级），未进结论；LeadDev 同题材文章只取得标题与 URL，正文未取到。
3. "一次说清楚 vs 多轮修补"无权威量化研究：检索到的最接近证据是 METR RCT（但结论是"效应依赖情境+感知偏差"）与 NearForm 实践复盘（定性）。§2-C4 的"返工 ≥2 轮停"阈值是我们自定的工程约定，不是文献结论。
4. "何时重写 spec 而非继续 patch"无权威文献：仅能从两条已核验事实推出可操作规则——(a) 上下文劣化机理（Anthropic 文档），(b) 返工多源于 spec 缺陷而非实现缺陷（Spec Kit 的 converge 设计意图，转述）。推导部分已按推导标注。
5. Kiro 官方文档正文未取到（JS 渲染）：三件套结构引自 T5 社区文件 + 官方页标题佐证；EARS 原始论文未检索（时间盒）。
6. 时效：任务描述中的 Spec Kit "四阶段" 已过时——2026-08 v1.0.0 起 constitution 与 converge 并入成六步。本文以抓取日（2026-09-11）所见为准。
7. 经典 TDD/BDD 谱系未单独溯源：本报告以三家 AI 原生方法中的机制承接"测试即规格"，未引用 Kent Beck/Gojko Adzic 原文。

## 6. 来源清单（全部 URL）

| # | 来源 | 级别 | 状态 |
|---|---|---|---|
| 1 | https://github.com/github/spec-kit | T3 | ✅ 已核验（README v1.0.0） |
| 2 | https://github.com/github/spec-kit/blob/main/templates/spec-template.md | T3 | ✅ 已核验 |
| 3 | https://github.com/github/spec-kit/blob/main/templates/plan-template.md 、 tasks-template.md | T3 | ✅ 已核验 |
| 4 | https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-enterprise-developers/4-establish-project-principles-constitution-file | T3 | ◐ 仅搜索摘要 |
| 5 | https://kiro.dev/docs/specs/ | T3 | ◐ 页面存在，正文 JS 渲染未取到 |
| 6 | https://github.com/cremich/promptz.lib/blob/main/steering/kiro-specs.md | T5 | ✅ 已核验（转述 Kiro 结构） |
| 7 | https://code.claude.com/docs/en/best-practices | T3 | ✅ 已核验（2026-09-11） |
| 8 | https://agents.md/ | T1 | ✅ 已核验 |
| 9 | https://developers.openai.com/codex/guides/best-practices | T3 | ❌ 403 未核验 |
| 10 | https://cursor.com/docs/context/rules | T3 | ✅ 已核验（规则类型/存放位置） |
| 11 | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ | T2 | ✅ 已核验 |
| 12 | https://metr.org/blog/2026-02-24-uplift-update/ | T2 | ✅ 已核验 |
| 13 | https://nearform.com/digital-community/why-ill-never-go-back-to-vibe-coding-a-developers-case-for-spec-driven-development/ | T4 | ✅ 已核验（2026-04-29） |
| 14 | https://www.gitclear.com/ai_assistant_code_quality_2025_research | T3 | ❌ 403 未核验 |
| 15 | https://leaddev.com/technical-direction/how-ai-generated-code-accelerates-technical-debt | T4 | ❌ 正文未取到 |
