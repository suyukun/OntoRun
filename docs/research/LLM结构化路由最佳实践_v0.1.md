# LLM 结构化路由最佳实践调研 v0.1（ChatBI llm_route 工程视角）

> 任务：OntoRun 编译器已确定性（{measure, dimensions[], time_from, time_to} → SQL），LLM 唯一职责=中文问题→该 JSON。调研五点工程最佳实践（每条带来源）：①结构化输出可靠性与失败重试 ②原语目录喂法（全量 vs 检索式）③实体链接 ④few-shot 选取 ⑤澄清循环。
> 调研人：Rose（子代理）；日期：2026-09-10；检索成本：web_search 6 次（预算 ≤30）+ 一手原文深读约 12 篇（arXiv 摘要/官方文档直读）。
> 来源分级：T1=原始文献/官方文档；T3=大厂工程博客/顶会；T4=产品文档；T5=社区（仅线索）。找不到/没核到的明确标注（见文末清单）。
> 现状锚点：`src/semantic/llm_route.py` —— 单发 chat.completions（temperature=0, max_tokens=200）+ 正则抽 JSON + `validate_plan` 对注册表枚举硬校验 + 任何失败降级关键词路由；目录全量进 system prompt（当前 7 度量 + 6 维度，其中 1 个带 grains）；无 JSON mode、无重试、无 few-shot、无维度值（filter）通道、无澄清通道。

---

## 结论先行（BLUF）

1. **结构化输出**：DeepSeek 云 API 场景 = JSON Output（`response_format=json_object`）+ 枚举硬校验保留为最终防线 + 校验失败做 ≤1 次"错误回喂重试"再降级；约束解码只有自托管才可用，且格式约束过强会伤推理（本文 schema 仅 4 字段，影响可控）。
2. **目录喂法**：13 个原语全量进 system prompt 是当前正确做法，**不要提前上 RAG**；设阈值（经验值 >50~100 原语）再切"检索 top-k"，且检索本身是难题（ToolRet），要配同义词+金标评测。
3. **实体链接**：分两层——维度 id（schema 层）LLM 直选+枚举校验（现状正确）；**维度值绝不让 LLM 直出终值**：LLM 只抽表面串，代码查维表候选（0 拒/1 用/多澄清），这是防幻觉参数的核心。
4. **few-shot**：补 3~5 个静态精选示例覆盖问法变体（含 reject 反例）；日志池积累后换"相似度检索 top-k"动态选例；示例必须与注册表同源生成，防改名漂移。
5. **澄清循环**：不指望 LLM 自觉问（两篇实证：模型认得歧义但压倒性直答）——用**确定性规则**判定必问/可默认（注册表元数据 + 候选数量），澄清走结构化通道 `{"clarify": {...}}`（与 reject 同级），问题与选项由代码生成。

---

## 块1：结构化输出可靠性（JSON mode / function calling / 约束解码 / 失败重试）

### 结论
- 三个层级是**递进的保证强度**：JSON mode 只保证"合法 JSON"不保证符合 schema（Azure OpenAI 官方对旧 JSON mode 的原话："guaranteed valid JSON but couldn't ensure strict adherence to the supplied schema"[T1]）；structured outputs / function calling（strict）保证 schema 合法（OpenAI 生态，需 `additionalProperties:false` 等 schema 限制[T1]）；约束解码（grammar-constrained decoding，Outlines/XGrammar/vLLM guided_json）在 token 级用上下文无关文法保证合法[T1]。
- 代价：格式约束越强，推理能力掉得越多（"Let Me Speak Freely"实证：结构化格式显著降低 LLM 推理表现，且约束越严退化越大[T1]）。**对策不是拒绝结构化，而是 schema 保持极小**——我们的路由输出只有 4 个字段，属于影响可控的轻约束。
- 自修复模式（业界标准做法，Instructor 库将其产品化）：校验失败 → 捕获校验错误 → 格式化为反馈 → 放回 prompt 上下文 → 让 LLM 重试，构成闭环[T3 官方文档]。
- DeepSeek 云 API 的现实（官方 JSON Output 文档）：`response_format={'type':'json_object'}`；prompt 必须含 "json" 字样并**给出输出样例**；`max_tokens` 要防截断；**该模式有概率返回空 content**（官方明示）[T1]。

### 证据与来源
- DeepSeek 官方《JSON Output》：三条注意事项 + 空 content 概率。[T1] https://api-docs.deepseek.com/zh-cn/guides/json_mode
- Azure OpenAI 官方（Microsoft Learn）Structured Outputs：与 JSON mode 的对比原话、schema 约束（additionalProperties:false、嵌套/属性数上限）。[T1] https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/structured-outputs
- Let Me Speak Freely?（arXiv 2408.02442）：格式限制显著损害推理，越严越差。[T1] https://arxiv.org/abs/2408.02442
- XGrammar（arXiv 2411.15100）：CFG 约束解码引擎，vLLM 集成；结构化生成保证合法性的机制层证据。[T1] https://arxiv.org/abs/2411.15100 （vLLM 功能页：https://docs.vllm.ai/en/latest/features/structured_outputs.html）
- Instructor 官方《Retry Mechanisms》：重试四步（捕获错误→格式化反馈→入上下文→重问）。[T3] https://python.useinstructor.com/learning/validation/retry_mechanisms/

### 对 llm_route.py 的落地建议
1. `llm_route()` 的 `create()` 加 `response_format={"type": "json_object"}`；`_system_prompt()` 末尾补一个**字面 JSON 样例**（DeepSeek 官方要求给样例；现 prompt 只有文字描述）。现有"JSON"字样已满足"含 json 字样"要求。
2. 响应后检查 `finish_reason == "length"` 与空 content（官方明示有空 content 概率）：这两类按**可重试失败**处理（归 `E_ROUTE_FALLBACK` 语义：重试一次→降级关键词），不要算 `E_ROUTE_INVALID`。
3. 失败重试：`validate_plan` 失败（非 JSON / 未注册原语）时，做 **≤1 次**错误回喂重试——把校验错误原文 + 上次原始输出拼进 follow-up 消息重问（Instructor 模式）；仍失败才走关键词降级。重试计入 `ms` 与审计字段。
4. 不引入约束解码：DeepSeek 云 API 未提供该参数（其官方文档未见，标注：未逐项核验全部 API 参数）；若未来自托管 vLLM，可用 guided_json 兜底格式层，`validate_plan` 枚举校验仍保留为最终防线（两层）。
5. schema 保持 4 字段极小形态；不要为"更结构化"把推理过程塞进 JSON 字段（2408.02442 的教训方向）。

---

## 块2：原语目录怎么喂——全量进 prompt vs 检索式（RAG）

### 结论
- **目录小就全量喂，这是对的，不要提前优化**。当前 13 原语全量进 system prompt 完全正确。
- 目录到几百个原语时的实证路线是**检索式**：RAG-MCP 在 MCP 工具压力测试中，检索后只喂相关工具描述，prompt token 降 50%+，工具选择准确率 **43.13% vs 13.62%**（全量喂，约 3 倍提升）[T1]。
- 但检索不是免费午餐：ToolRet（7.6k 查询 × 43k 工具）显示**强 IR 模型在工具检索上表现差**，低检索质量直接拖垮下游工具使用通过率[T1/T3]——检索质量决定上限，需要注册表别名/同义词、混合检索、金标评测兜底。
- 比喂法更根本的是**条目描述质量**：Snowflake Cortex Analyst 官方立场——只给 DB schema 不够，语义模型承载业务定义与口径处理才是高精度关键[T1]；Anthropic 写工具指南同样把描述质量 + held-out 评测列为第一杠杆[T3]。

### 证据与来源
- RAG-MCP（arXiv 2505.03275）：prompt bloat 量化 + 检索式工具选择准确率 3 倍。[T1] https://arxiv.org/abs/2505.03275
- ToolRet / "Retrieval Models Aren't Tool-Savvy"（ACL 2025 Findings）。[T1] https://aclanthology.org/2025.findings-acl.1258/
- Anthropic Engineering《Writing effective tools for AI agents》：描述质量、工具合并（consolidation）、held-out 评测驱动迭代。[T3] https://www.anthropic.com/engineering/writing-tools-for-agents
- Snowflake《Best Practices for Creating Semantic Views for Cortex Analyst》/ Cortex Analyst 文档：语义模型弥补 schema 缺业务知识。[T1] https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst

### 对 llm_route.py 的落地建议
1. **短期不动**（13 原语）；把精力花在注册表描述质量上：每个 measure/dimension 的 description 补**中文同义词/别名**（喂法不变，LLM 路由与未来检索同时受益）。
2. 预埋切换开关：`config` 加目录规模阈值（经验值 **>50~100 原语**或 system prompt 超千 token 级——经验线，非文献结论，标注）：超过则 `_system_prompt()` 改走"检索 top-k（k≈15）+ reject 兜底"。检索失败/低分时**必须保留 reject 通道**，防漏召回硬塞错误域。
3. 检索式实现最小形态：原语 id+description+别名 建索引（先字符/词面，后 embedding）；更保守的零向量库方案=两级路由：先按业务域分组选域、再在域内全量选原语。
4. 建立 question→plan 金标集（哪怕 30~50 条），任何喂法/模型改动跑同一评测再上线。

---

## 块3：实体链接（"麦当劳"→渠道维度值）

### 结论
- **分两层**：维度 id 是闭枚举（schema 层），LLM 直选 + 枚举校验即可（现状正确）；**维度值（filter value）是开放集，绝不让 LLM 直出终值**——LLM 只抽取问题里的表面串（mention），由确定性代码查维表/词典候选：精确/别名 → 模糊 → embedding；0 候选=拒或如实说无、1 候选=直用、多候选=带选项澄清。
- 这是 text-to-SQL 领域验证过的"value linking/值锚定"路线：CodeS 明确"从数据库检索与问题对齐的值可提升 schema linking"[T1]；SEA-SQL 用语义增强 schema + 执行校验动态修正，在 GPT-3.5 场景以 9%~58% 成本做到 SOTA 级[T1]。产品侧，维度成员检索已是语义模型标准能力（Xpert 文档有专页[T4]）。

### 证据与来源
- CodeS（arXiv 2402.16347）：值检索帮助 schema linking。[T1] https://arxiv.org/abs/2402.16347
- SEA-SQL（arXiv 2408.04919）：语义增强 schema + 自适应修正 + 执行校验。[T1] https://arxiv.org/abs/2408.04919
- Xpert AI《Dimension Member Retrieval》：语义模型把"维度成员检索"作为独立能力（存在性证据，算法细节未核）。[T4] https://docs.xpertai.cn/en/data/analytics/semantic-model/dimension-member-retrieval
- Snowflake Cortex Analyst：语义模型桥接业务用户与数据库。[T1] https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst

### 对 llm_route.py 的落地建议
1. 扩展请求 schema：路由输出加 `entities: [{"mention": "...", "dimension_hint": "维度id|"}]`（LLM 只抄表面串、可给维度提示），**不给 value_code**；新增确定性 `linker` 模块把 mention 解析为注册值（`dimension_id=value_code`），compiler 只认 value_code。
2. 维度值来源进注册表：Dimension 增加 values 提供方式（维表查询或快照 + 别名表）；匹配顺序：精确 → 归一化（大小写/空格）→ 别名 → 模糊（编辑距离；embedding 兜底 MVP 可后置）。
3. 0 候选 → 澄清或"无此维度值"如实回答，**禁止 LLM 补一个值**；多候选 → 进块5澄清通道并附选项。
4. linker 全程确定性、可审计、可缓存（mention→code 结果缓存），这正是"LLM 输出视为不可信输入"安全纪律在参数层的落实。

---

## 块4：few-shot 示例的选取策略

### 结论
- 当前 prompt **零示例**，应补 3~5 个静态精选，覆盖问法变体的正例 + reject 反例。
- 规模化后（有 verified 日志）换**动态选例**：按问题相似度检索 top-k。Text-to-SQL 的系统评测（DAIL-SQL，Spider 86.2%，约 1600 token/题）支持：相似度选例 + "问题→SQL"成对展示 + 骨架（掩码问法）表示是其消融中的有效组合[T1]。
- 示例可以自动化运维：DSPy 的 BootstrapFewShot 家族把"采样 traces → 按指标筛选 → 择优塞入 demos"做成标准机制（含 KNN 检索式选例）[T3 官方文档]——对应我们的路线：人工 verified 示例为种子，日志池为增量。

### 证据与来源
- DAIL-SQL（arXiv 2308.15363 / 官方 README）：选例与组织策略系统评测；86.2% Spider。[T1] https://arxiv.org/abs/2308.15363 ｜ https://github.com/BeachWang/DAIL-SQL
- DSPy BootstrapFewShot family 官方文档：demos 的采样-筛选-KNN 检索机制。[T3] https://dspy.ai/diving-deeper/bootstrap-fewshot-family/

### 对 llm_route.py 的落地建议
1. `_system_prompt()` 附 3~5 例，每个一行问 + 一行 JSON，覆盖：直问；带明确时间；缺时间（null）；带 grain 参数（`维度id=参数` 写法）；**域外 reject 反例**（教会"不猜"）。
2. 示例**从注册表真实 id 生成**（模板化拼接），注册表改名/加项示例自动跟随，防示例漂移成幻觉源。
3. 建 `examples/verified_routes.jsonl`（人工确认的 问→plan），运行期按相似度选 top-3 替换静态示例；冷启动前纯静态。选例特征：问题相似度 + 骨架多样性（时间有无/维度个数/reject 混排），控制示例总 token（百级/个）。
4. 错误回喂重试轮：附上次错误输出作反例，不换 few-shot 集（保持变量单一，失败可归因）。

---

## 块5：澄清循环（缺参数时反问 vs 默认值兜底）

### 结论
- **不能指望 LLM 自觉澄清**，两篇独立实证：CLAMBER（12K 数据、taxonomy 驱动）——现役 LLM 识别与澄清歧义的能力有限，CoT/few-shot 只带来边际改善、反而可能加重过自信[T1]；"Knowing but Not Showing"（arXiv 2605.25284）——模型在显式判断时认得歧义，但行为上压倒性直答，检索上下文还会进一步降低提问率[T1]。
- 因此**判定权放代码里**：注册表元数据（哪些参数无默认值=必填）+ 确定性触发条件（候选 0/多、度量歧义）决定"必问 vs 可默认"；澄清走结构化通道 `{"clarify": {"question", "options"[...]}}`（与 reject 同级），**问题与选项由代码从候选生成**，不让 LLM 自由发挥措辞。
- 默认值兜底判据（工程建议，非文献结论，标注）：时间缺失 → 数据覆盖范围内默认区间并在回答**回显假设**；度量歧义（多原语同分）→ 必问；维度值 0 候选 → 如实说无（不问不猜）、多候选 → 必问；有注册默认值的参数 → 默认 + 回显。澄清一轮为限。

### 证据与来源
- CLAMBER（arXiv 2405.12063）。[T1] https://arxiv.org/abs/2405.12063
- Knowing but Not Showing（arXiv 2605.25284）。[T1] https://arxiv.org/abs/2605.25284
- （辅助）Do RAG LMs Know When They Don't Know?（AAAI）："知不知"校准仍是开放难题。[T1] https://ojs.aaai.org/index.php/AAAI/article/view/40822

### 对 llm_route.py 的落地建议
1. `RoutePlan` 增加 clarify 变体（`clarify_domain` + `question` + `options[]`）；`validate_plan` 返回三类结果：plan / reject / **clarify(原因)**——判定规则全在代码，LLM 只提供信号。
2. 触发条件与块1-4 联动：维度值多候选（块3）、度量检索/路由多解（块2）、注册表必填参数缺失 → clarify；时间缺省 → 默认区间 + 回显。
3. engine 侧透传 clarify 到前端（ChatBI 已有 Agent 式思考流交互，ADR-0009），澄清答案拼回问题再路由一次；**一轮为限**，防循环。
4. 记录 clarify 率与原因分布（沿用现有审计习惯）：澄清率高通常是目录/别名质量问题，反哺注册表而非加提示词。

---

## 未核/诚实标注清单
- OpenAI 官方博客（introducing structured outputs）与 platform 文档直读被拒（403/JS 渲染），"100% schema adherence"宣传语**未核到原文**；structured outputs vs JSON mode 的差异改以 Azure OpenAI 官方文档（Microsoft Learn）佐证。
- Snowflake Cortex Analyst "多匹配时主动澄清"的具体行为**未在官方文档核到**（目标页 JS 渲染/关键词未命中），本稿只采用其"语义模型必要性"表述。
- DeepSeek 云 API 是否存在 constrained-decoding 参数：其官方 JSON Output 文档未见该参数，标注"未逐项核验全部 API 参数"。
- SuperSonic（腾讯音乐 ChatBI OSS）README 未核到词典/实体细节，未采用。
- "目录 >50~100 原语切检索式"与各默认值策略为工程经验值，**非文献结论**。
- Let Me Speak Freely 的缓解策略细节（如 reason-then-format 顺序）只读摘要，未展开引用。
