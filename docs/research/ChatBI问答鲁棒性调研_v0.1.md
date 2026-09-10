# ChatBI 问答鲁棒性调研 v0.1

> 任务来源：Jack「先想清楚再做」——演示要经得起即兴提问，检索业界对六个难点的解法。
> 调研日期：2026-09-10 · 调研方式：web 检索 + 原文深读（来源分级 T1-T6，见文末清单）
> 检索预算报告：web_search 调用 8 次（27 条 query），web_fetch 16 次（成功 13）；未超单代理 ≤30 上限。
> 适用对象：OntoRun 语义层（确定性编译器：度量×维度×时间→SQL；LLM 只负责把自然语言映射到原语组合，结构化输出）。

---

## 0. 一页结论（TL;DR）

1. **我们「原语固定、LLM 只选」的架构不是孤例，是业界收敛的主流路线**：衡石 NL2Metrics（NL→指标→HQL→SQL）、Aloudata NL2MQL2SQL（NL→指标查询语言 MQL→确定性感义引擎→SQL）、腾讯云 ChatBI（意图路由→澄清→DSL 生成，规则+大模型融合）全部同构。**差别不在编译器，在编译器前面那层「问法理解」的工程**——这正是六个难点的位置。
2. 业界把问法理解拆成固定流水线：**意图路由 → 槽位填充（度量/维度/时间）→ 实体链接（字符串→维度成员）→（缺槽时）澄清反问 → 生成 DSL/MQL**。LLM 在每个环节只做一次、只做一件事（腾讯云：每模块最低仅一次模型交互，首 token <2s）。
3. 相对时间业界答案是**混合式：模型只做「抽取+标准化」，真实日期区间由确定性代码算**（阿里 XiYan-DateResolver 两步法：微调模型抽表达式 → 脚本 date_convert.py 算日期，覆盖范围内 >95% 准确率）。LLM 直出日期区间被证明不可靠（DateLogicQA 显示 LLM 存在系统性时序偏差）。
4. 多轮的业界共识：**维护结构化「对话状态/查询计划」，每轮做差量更新（新增/修改/纯追问），不是把聊天记录丢给 LLM 重答**。衡石明确拆出三种跨轮依赖：指代消解、增量修改、上下文继承。
5. 模糊问法与拒答是同一机制的两面：**置信度不足→反问补槽；超纲→体面拒绝+引导到最近合法问法**（Power BI Copilot 用 AI Instructions 实现「不猜、必反问」；蚂蚁用「智能澄清-知识沉淀-动态召回」闭环，一次澄清长期复用）。
6. 衡石「68%→89%」考据：**原始出处是独立对话框 vs 嵌入式上下文模式的 A/B 对比**——问题描述准确率 23%→68%，首次回答满意度 41%→89%，日均频次 1.2→6.7 次。它不是「评测集分数」，而是「引导式输入 vs 空白框」的交互实验；方向性结论（引导大幅提升问法质量）可信，数字是厂商单方实验（T3）。
7. 评测集业界构成 = **分层指标 + 回归坏例集**：各链路模块命中率（意图/实体/时间/生成）+ 端到端数值正确率 + 澄清效率（追问次数）；学术参照系 BIRD（12,751 对问答-SQL、95 库、37 领域，强调外部知识与脏值）与 Spider 2.0（真实企业工作流，成功率骤降）。我们已有 S3 评测集 30 题先例，建议按六难点扩成分层问法集。

---

## 1. 业界通用架构：问法理解流水线与叫法（检索问题 2）

业界没有统一名词，落地模式高度一致：

| 学界/业界叫法 | 在 ChatBI 里的实体 | 典型实现 |
|---|---|---|
| 意图分类 / 意图路由 | 判断查数、要解释、要归因还是闲聊 | 腾讯云「意图路由」独立模块；衡石「意图分类→路由到 NL2Metrics」 |
| 槽位填充（Slot Filling） | 抽出度量、维度、过滤、时间、排序、topN | 衡石「指标检索→时间修饰词注入指标定义」；FreeWheel 分层解析器（BERT+CRF 识别时间/指标/维度实体 + 规则引擎处理行业语法） |
| 实体链接 / 实体召回 / 维度成员检索 | 把「麦当劳」「优享+线上」链到维度真实值 | 衡石指标库向量检索；FreeWheel 混合检索（向量+TF-IDF+图）→业务约束过滤→LLM 决策，选表准确率 95%+ |
| 对话状态管理 / 会话状态机 | 跨轮保持查询计划 | 衡石对话状态引擎；FreeWheel 会话状态机持久化关键实体 |
| 语义层中转（NL2Metrics / NL2MQL2SQL / NL2DSL） | NL 不直译 SQL，先译受控中间语言 | 衡石 HQL；Aloudata MQL；腾讯 DSL |

**模式判断**：业界从「NL2SQL 直译」普遍转向「NL → 受控中间表示 → 确定性引擎」，动机是 NL2SQL 准确率天花板（衡石引述业界普遍 70%-85%）与口径漂移。中间表示越受限，LLM 自由度越小，鲁棒性越高——**我们「LLM 只选原语」是该路线的极致形态，方向正确、业界证据充分**。

来源：衡石 NL2Metrics（T3）https://www.hengshi.com/blog/nl2metrics-accuracy-breakthrough.html ；衡石 NL2DSL（T3）https://www.hengshi.com/blog/1148.html ；Aloudata NL2MQL2SQL（T4）https://developer.cloud.tencent.cn/article/2613621 ；FreeWheel ChatBI 架构解析（InfoQ，经百度开发者转载读取，T4）https://www.infoq.cn/article/zn5fv8qxoncytiaumglo ；腾讯云 ChatBI（T3）https://cloud.tencent.cn/developer/article/2543992

---

## 2. 五家厂商问法理解与交互形态速查（检索问题 1）

| 厂商 | 问法理解策略 | 澄清/多轮/拒答的交互形态 | 来源层级 |
|---|---|---|---|
| **衡石 HENGSHI** | 意图分类→指标向量检索→NL2Metrics；对话状态引擎（指代消解/增量修改/上下文继承） | 「认知脚手架」：BI 页内嵌问数入口+视觉锚点（自动推荐专业问题）+语义关联（点击图表后「经销商」自动绑定区域指代），代替空白对话框；空白框模式 87% 用户首问模糊、62% 需 3 次以上追问 | T3 |
| **观远 Guandata** | 问数 Agent：中文 NL→意图理解→图表；「企业知识」绑定指标口径（提「销售额」用企业口径算） | 多轮追问（「这个月销售额怎么样」→「华东区域呢」）；行列级权限兜底；澄清反问细节未公开（营销文为主） | T4（交互形态可信，机制未公开） |
| **网易有数** | 有数 BI 内置 ChatBI/智能问数，已适配 DeepSeek；杭研玉言 NL2SQL 领域大模型（AiDD 分享） | 产品页未公开澄清/拒答细节——**未找到，标注未验证** | T2 产品页 + T4 媒体 |
| **阿里 Quick BI 智能小Q** | 5 个 Agent（问数/解读/报告/搭建/洞察）；问数 Agent：自然语言即问即答、预览选择数据集、快捷提问、多轮对话；官方称 100 万+专项训练语料、20+ 种调优手段 | 多轮对话深入分析、快捷提问（预设问法引导）；模糊问法另见蚂蚁 DeepInsight 澄清闭环（§3.3）；澄清 UI 官方细节未检索到——标注未验证 | T2 官方文档 |
| **腾讯云 ChatBI** | 模块化链路：意图路由→智能选表/多表关联→意图澄清→DSL 生成；每模块最低一次模型交互；流式输出；「大模型+传统规则融合机制」增强鲁棒性 | 意图澄清是独立链路环节；知识库可配置生效范围（人工录入业务叫法映射）；「提问建议」引导式推荐问法；波动归因支持自定义维度和时间 | T3 + T2 文档 |

来源：衡石 https://www.hengshi.com/blog/1166.html 、https://www.hengshi.com/blog/chatbi-multi-turn-context-management.html ；观远 https://www.guandata.com/gy/post/roEwRyJN.html ；网易数帆 https://163yun.com/product/bi 及 DeepSeek 适配报道（T4）http://ex.chinadaily.com.cn/exchange/partners/82/rss/channel/cn/columns/sz8srm/stories/WS67ad8621a310be53ce3f5350.html ；Quick BI https://help.aliyun.com/zh/quick-bi/user-guide/smartq ；腾讯云 https://cloud.tencent.cn/developer/article/2543992 、https://cloud.tencent.com/document/product/590/116807

---

## 3. 六难点逐项：业界做法 → 来源 → 对我们的适配建议

### 3.1 难点① 口语化问法（「上个月麦当劳来了多少人」）

**业界做法**
- 不指望 LLM 天生懂口语，靠**「检索增强的语义元数据」+口语映射资产**：衡石把指标定义/描述向量化进检索库，提问先检索最匹配的指标定义（口语「来了多少人」→指标「到场人数」靠相似度召回）；观远「学习企业元数据和知识」，提「销售额」就用企业口径；腾讯云靠知识库（可配生效范围）注入业务黑话。
- 表名/字段名缩写拼音（xsdd=销售订单明细）靠**别名层**解决——语义层为每个原语挂载口语别名、同义词、业务黑话（衡石 NL2Metrics 明列为挑战 1.1）。

**关键来源**：衡石 NL2Metrics（T3）；观远（T4）；腾讯云知识库（T3）。

**对 OntoRun 的适配建议**
1. 口语归一化是**语义层配置资产，不是 prompt 技巧**：给每个度量/维度在注册表里加 aliases 字段（含「来了多少人→到场人数」这类口语映射），编译 prompt 时按检索相关性注入候选原语及其别名——LLM 结构化输出仍只能选注册过的原语，口语在「选择」之前被消化。
2. 演示防线：把 demo 可预期的口语问法预先埋进别名表（数据工作而非模型工作），并计入评测集。

### 3.2 难点② 相对时间（最近一周/今年/三季度/上个月）

**业界做法**
- **成熟答案是混合式，不是规则库 vs LLM 二选一**。代表：阿里 XiYan 团队 XiYan-DateResolver 两步流水线：①微调小模型（Qwen2-7B）从文本抽取时间表达式并标准化（「上周周三」→标准格式），②确定性脚本 date_convert.py 按当前日期算真实区间；覆盖 100+ 种中文时间表达，覆盖范围内准确率 >95%。**模糊理解交给模型，日期算术交给代码**。
- 传统规则库路线：Facebook Duckling（Haskell，Time 维度 + ZH 中文规则模块，规则+统计排序）、Stanford SUTime、HeidelTime——可解释、零推理成本，但中文口语覆盖需自补规则。
- 厂商落地：FreeWheel 用规则引擎处理「对比上周」类时间偏移，把解析出的区间（2023-10-02~10-08）持久化进会话状态复用；衡石把「上个月」时间修饰词**注入指标定义**生成查询，并把「上个月是自然月还是滚动 30 天」明列为语义歧义挑战。
- 反面证据：LLM 直出日期区间不可靠——DateLogicQA 基准显示 LLM 存在系统性时序偏差；Power BI Copilot 场景下「recently」也必须反问澄清。

**关键来源**：XiYan-DateResolver（开源一手，T2）https://github.com/XGenerationLab/XiYan-DateResolver ；Duckling（T2/T4）https://github.com/facebook/duckling ；FreeWheel（T4）；衡石 NL2Metrics（T3）；DateLogicQA（T1）https://ar5iv.labs.arxiv.org/html/2412.13377

**对 OntoRun 的适配建议**
1. 时间是编译器一等原语，**禁止 LLM 直出日期区间**——LLM 结构化输出只产出标准化时间槽（模式：自然月/滚动窗口/季度/最近N天 + 偏移 + 粒度），由确定性 time-normalizer 代码算区间。DateResolver 两步法可直接借鉴（其 100+ 中文表达清单可当规则库需求清单，date_convert.py 逻辑可参考实现）。
2. 「自然月 vs 滚动30天」这类歧义**不进模型，进口径包**：语义层为每个时间敏感度量声明默认时间语义，歧义时进澄清（§3.3）。

### 3.3 难点③ 模糊问法（「注册情况怎么样」——缺维度缺度量）

**业界做法**
- **澄清循环（反问补全）是标准交互**：蚂蚁 DeepInsight x ChatBI「**智能澄清-知识沉淀-动态召回**」闭环——精准识别歧义、**最少提问**（一次澄清只问最关键槽位）、澄清结果结构化留存，**一次澄清、长期复用**（下次同问直接命中历史澄清）。
- **控制模糊容忍度**而非全有或全无：Power BI Copilot 的 AI Instructions 可调歧义容忍级别，极端规则「用户未明确提到度量名/度量名有歧义→不返回结果，反问指哪个度量」——实证有效（对「recently」「nicest」类问法稳定反问）。
- **引导式输入从源头减少模糊**：衡石数据——独立对话框 87% 用户首问模糊、62% 需 3 次以上追问；嵌入式上下文+推荐问法后问题描述准确率 23%→68%、首次回答满意度 41%→89%。**最好的澄清是让用户不用澄清**。
- 兜底形态：腾讯云「提问建议」预设问法；追问超限后展示推荐问法列表而非硬失败。

**关键来源**：蚂蚁 DeepInsight（阿里云开发者社区，蚂蚁数据智能技术署名，T4）https://developer.aliyun.com/article/1693372 ；Chris Webb 微软 MVP 博客（T3）https://blog.crossjoin.co.uk/2025/07/13/power-bi-copilot-ai-instructions-and-dealing-with-ambiguity/ ；衡石 1166（T3）；腾讯云提问建议（T2）。

**对 OntoRun 的适配建议**
1. LLM 结构化输出增加 clarification_required + 缺槽枚举 + 候选列表：缺度量→反问「看哪个指标？」（候选=注册表里的合法度量，**候选由编译器生成，不让 LLM 编**）；缺维度→给默认维度+可切换建议。
2. **澄清成本指标化**：「澄清次数/轮次」进评测集（对齐业界最少提问原则）。
3. 演示文案兜底：模糊问法按「反问一次+给候选」编排，体现掌控感而非失败。

### 3.4 难点④ 多轮上下文（「那分渠道呢？」承接上题）

**业界做法**
- 衡石对话状态管理（公开拆解最完整）：每轮维护**对话状态 = 当前查询计划（指标/维度/过滤/排序/时间窗）+ 已确认口径与消歧结果 + 增量意图 + 权限上下文 + 会话摘要**；新问话执行「**状态差量更新**」，先判本句属「新增条件/修改条件/纯追问」三类之一再合并；三种跨轮依赖：**指代消解**（「那」→上一轮分析对象）、**增量修改**（「改成按销售额排」=覆盖排序、其余保留）、**上下文继承**（「只看数码品类」隐含继承上月+华东约束）。
- FreeWheel 会话状态机：前序问答关键实体（时间区间、指标别名）持久化复用。
- 腾讯云：链路模块化+流式输出降低多轮等待感。

**关键来源**：衡石多轮博客（T3）https://www.hengshi.com/blog/chatbi-multi-turn-context-management.html ；FreeWheel（T4）；腾讯云（T3）。

**对 OntoRun 的适配建议**
1. **我们的结构化原语组合天然就是「对话状态」**——架构红利：多轮 = 每轮让 LLM 输出对上一组合的**结构化 patch**（op: add / replace / clear，作用槽位，新值仍只能选合法原语），编译器每轮拿完整组合编译，无感多轮。不要把聊天记录裸喂 LLM 重答。
2. 「纯追问」（解释结果、不改查询）单独分类路由到解读分支，不进编译器。
3. patch 失败（指代无法消解）→ 回落 §3.3 澄清。

### 3.5 难点⑤ 超纲问题的体面拒答

**业界做法**
- **「不猜、必问/必拒」可配置**：Power BI Copilot 实证——AI Instructions 写死规则后即对模糊问法稳定反问；代价是体验变硬，所以要**容忍度可调**。
- **引导式拒答**：拒答时给最近似可答问题——腾讯云「提问建议」、衡石「视觉锚点推荐问题」都是「拒答+引导」形态；衡石哲学：不做搜索引擎式万能框，**缩圈到语义层覆盖范围内作答**。
- 兜底分层：能答（原语组合）→ 部分可答（近似组合+说明差异）→ 不可答（体面拒绝+推荐问法/转人工/转明细查询）。

**关键来源**：Chris Webb（T3）；腾讯云提问建议（T2）https://cloud.tencent.com/document/product/590/116807 ；衡石 1166（T3）。

**对 OntoRun 的适配建议**
1. 拒答判据**用映射置信度而非模型自觉**：LLM 结构化输出带 confidence + 未识别片段；低于阈值或存在无法绑定任何原语的片段→进拒答分支。拒答消息模板化：「当前数据范围覆盖 X/Y/Z，您可以问：…」（推荐问法从注册表按相似度生成）。
2. 演示红线：**宁拒不错**——编造数字是演示事故，体面拒答是设计能力。评测集放超纲题，验收「拒答正确率」。

### 3.6 难点⑥ 实体匹配（「优享+线上」特殊字符、问法→维度值）

**业界做法**
- 业界叫法：**实体链接（Entity Linking）/ 实体召回 / 维度成员检索（Dimension Member Retrieval）**——把问题表面字符串链到语义层维度的真实成员值。
- 成熟做法是**召回-排序-确认三级**：FreeWheel 混合检索（向量 Sentence-BERT+FAISS、TF-IDF 精确、图检索）→ 业务约束过滤（权限/血缘）→ LLM 决策，选表准确率 95%+；同构方法用于维度成员：向量召回 + 精确/规范化匹配兜底，置信度不足即澄清，**绝不静默选近似值**。
- 特殊字符/别名：业界惯例是**别名词典 + 字符串规范化**（全半角、大小写、空格、加号/与符号变体）作确定性预处理，向量检索只兜长尾口语；腾讯云知识库支持人工录入「业务叫法↔字段」映射，本质是别名运营。

**关键来源**：FreeWheel（T4）；衡石指标检索（T3）；腾讯云知识库（T3）；Xpert Dimension Member Retrieval（同类概念旁证，页面 JS 渲染未深读，仅题录，T5）。

**对 OntoRun 的适配建议**
1. 维度成员**别名表 + 规范化函数**进语义层（canonical_value + aliases + normalize()），「优享+」类值预埋变体；排查加号在 query string / URL 编码里变空格的前后端隐患。
2. 匹配流程：规范化精确匹配 → 别名精确匹配 → 向量/模糊召回 top-k → **top-1 置信度不足或多候选时反问（候选=真实维度值）**，绝不把未确认字符串编进 SQL 参数。这条同时是注入防御边界：进编译器的维度值必须来自注册表成员集。

---

## 4. 评测：业界问法测试集怎么建（检索问题 4）

**学术基准（参照系）**
- **BIRD-SQL**：12,751 对问题-SQL、95 个大库（33.4GB）、37+ 领域；三大主张——需引入外部知识、需推理「脏值」、需考虑执行效率；定义了「真实库内容影响解析」的评测观。T2：https://bird-bench.github.io/
- **Spider 2.0**：真实企业级 text-to-SQL 工作流（多表、多方言、BI 工具链），模型成功率相比学术基准大幅下降（定位已确认；最新分数未深读 leaderboard，不引具体数字）。T2：https://github.com/xlang-ai/Spider2
- **DateLogicQA**：专测 LLM 时间表达偏差，支持「时间要单独测」。T1。

**业界实践构成**
- **分层指标**：FreeWheel（召回/选表层 95%+ 单列）与腾讯云（各模块准确率分开报告）——**按链路模块分层数指标**，不做单一总分。
- **交互质量指标**：衡石 A/B 用「问题描述准确率、首次回答满意度、日均使用频次」衡量问法引导；蚂蚁闭环隐含「澄清次数最少化」。**评测不止测「答对没」，还测「问了几轮才答对」**。
- **回归坏例集**：《智能问数 Skill 维护手册》提出把「感觉不准」翻译成「改哪个文件」的回归法——坏例沉淀为用例、改动后重跑（题录级线索，T5，未深读）；IEEE 有垂直领域 ChatBI 自动生成测试样本论文（题录，T1，未深读）。
- **衡石 68%→89% 考据（重点澄清）**：原始出处=衡石博客《为什么不做 BI 版搜索引擎》实验对比表——独立对话框 vs 嵌入式上下文：问题描述准确率 **23%→68%**、首次回答满意度 **41%→89%**、日均频次 1.2→6.7。「68%→89%」系两行数字的流传合并，**衡量的是引导式交互的价值，不是某评测集的准确率分数**；同文 87%/62%/8.2min 来自「某第三方机构对 200 家企业用户测试」（机构名未给出，按 T3 厂商引述对待）。结论可用（引导式输入显著改善问法质量），引用数字需注明口径。

**对 OntoRun 的适配建议**
1. 把 S3 的 30 题评测集扩成**六难点分层问法集**：每层独立指标（口语映射命中率 / 时间区间正确率 / 模糊题澄清正确率 / 多轮 patch 正确率 / 超纲拒答正确率 / 实体链接正确率）+ 少量端到端数值对拍题（编译器产物 vs 手工 SQL）。
2. 建立**坏例回归制**：彩排与真实试用中每个翻车问法 → 进评测集 → 修复后重跑（对齐「不手写假数字」纪律）。
3. 加**澄清效率指标**（澄清轮次中位数），防「全都反问」的偷懒解法拿高分。

---

## 5. 未找到 / 未验证清单（诚实标注）

| 事项 | 状态 |
|---|---|
| 网易有数 ChatBI 澄清/拒答交互具体形态 | 未找到公开技术细节（产品页与媒体稿均未披露）——未验证 |
| Quick BI 智能小Q 澄清反问官方 UI 细节 | 帮助文档确认多轮/快捷提问存在，澄清 UI 细节未检索到——未验证 |
| 观远澄清反问机制 | 营销内容确认多轮追问，机制细节未公开——未验证 |
| 衡石引述「第三方机构 200 家企业测试」（87%/62%/8.2min） | 原始报告不可考，按厂商引述对待（T3 单源） |
| Spider 2.0 最新成功率数字 | 未深读 leaderboard，文中不引具体分数 |
| 王鑫芸《企业级智能问数场景完美评测集构建方法与实践》 | PDF 付费墙，仅题录未深读 |
| Xpert「Dimension Member Retrieval」正文 | JS 渲染抓取失败，仅题录作概念旁证 |
| 蚂蚁 DeepInsight 长文正文 | 抓取被截断，核心闭环来自官方简介段，细节机制未全文核读 |

---

## 6. 来源清单（分级）

**T1 学术一手**
- DateLogicQA: Temporal Biases in LLMs — https://ar5iv.labs.arxiv.org/html/2412.13377
- Enhancing ChatBI System Performance…Automated Sample Generation Pipeline（IEEE，题录）— https://ieeexplore.ieee.org/document/11189210

**T2 官方文档 / 官方基准 / 开源一手**
- Quick BI 智能小Q 帮助文档 — https://help.aliyun.com/zh/quick-bi/user-guide/smartq
- 腾讯云 BI 提问建议 — https://cloud.tencent.com/document/product/590/116807
- BIRD-SQL 官网 — https://bird-bench.github.io/
- Spider 2.0 — https://github.com/xlang-ai/Spider2
- XiYan-DateResolver（阿里 XiYan 团队开源）— https://github.com/XGenerationLab/XiYan-DateResolver
- facebook/duckling（含 ZH Time 规则模块）— https://github.com/facebook/duckling
- 网易数帆有数 BI 产品页 — https://163yun.com/product/bi

**T3 厂商技术博客（具名工程团队）**
- 衡石 NL2Metrics 深度解析 — https://www.hengshi.com/blog/nl2metrics-accuracy-breakthrough.html
- 衡石 ChatBI 多轮对话与上下文管理 — https://www.hengshi.com/blog/chatbi-multi-turn-context-management.html
- 衡石 为什么不做 BI 版搜索引擎（68%/89% 原始出处）— https://www.hengshi.com/blog/1166.html
- 衡石 NL2DSL — https://www.hengshi.com/blog/1148.html
- 衡石 RAG × ChatBI — https://www.hengshi.com/blog/rag-chatbi-grounded-answers.html
- 腾讯云大数据：ChatBI 多表关联与四大能力升级 — https://cloud.tencent.cn/developer/article/2543992

**T4 主流技术媒体 / 实名社区**
- FreeWheel ChatBI 架构深度解析（InfoQ；经 developer.baidu.com 转载读取）— https://www.infoq.cn/article/zn5fv8qxoncytiaumglo
- 蚂蚁 DeepInsight x ChatBI：智能歧义识别+知识沉淀 — https://developer.aliyun.com/article/1693372
- Aloudata：ChatBI 走向落地（NL2MQL2SQL）— https://developer.cloud.tencent.cn/article/2613621
- 观远问数 Agent 实践（内容营销向，交互形态参考）— https://www.guandata.com/gy/post/roEwRyJN.html
- Chris Webb（微软 MVP）：Power BI Copilot, AI Instructions And Dealing With Ambiguity — https://blog.crossjoin.co.uk/2025/07/13/power-bi-copilot-ai-instructions-and-dealing-with-ambiguity/

**T5 线索（不作结论依据）**
- 亿问 Data Agent 语义收敛（oschina，抓取无正文）— https://my.oschina.net/u/9708825/blog/19719683
- 智能问数 Skill 维护手册·回归（CSDN，题录）— https://aicoding.csdn.net/6a679e1610ee7a33f292fee8.html
- 王鑫芸·企业级智能问数评测集构建（付费墙，题录）— https://www.sgpjbg.com/baogao/1258712.html

---

## 修订日志
- v0.1（2026-09-10）：首版。六难点+通用架构+厂商速查+评测+未验证清单；检索预算：web_search×8 / web_fetch×16。