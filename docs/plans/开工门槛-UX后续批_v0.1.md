# 开工门槛：UX 后续批 v0.1（Jack 2026-09-11 七项裁决固化）

> 级别：**M 级**（各任务单模块；T-N7 开工前探明数据源，若需后端补字段则该任务升级 L 补全表）。
> 输入：对抗回归 v0.2 复跑对照表（docs/对抗回归v0.2复跑-期望值重判对照表_2026-09-11.md）＋ Jack 七项裁决（2026-09-11）。
> 与 UX v0.2 的关系：v0.2 已收口；本稿是其裁决衍生的增量批。US3 EARS 释义修订见 T-N4。

## 0. 级别声明
M 级，填 A + D + C1 + NC；S 级任务（T-N1~T-N4）按模板免填只带一行声明与判据。

## A. 需求
- **A1 一句话命题**：给数仓同学与演示对象：把「猜着答」变「先确认」，把表演式节奏变真实节奏，把存储层措辞变本体语言——产品更可信、测试考卷更贴近产品真相。
- **A2 用户故事**：
  - **US-N1 (P1) 确认式澄清**：错别字别名/口径歧义/语流混乱的问句，系统先确认再出数，绝不猜着答（Jack 裁决「不要猜着答，要确认」）。
  - **US-N2 (P1) 考卷对齐产品真相**：multi_turn 12 条按「默认最近月直接答＋明示」改期望；runner 承接模拟不再要求 T1 先 CLARIFY。
  - **US-N3 (P1) 判定噪音治理**：TD-13 截断降级修复——LLM 输出被掐断时重试而不是静默降级误判。
  - **US-N4 (P2) 本体级溯源**：溯源面板不显示存储层名（层·表名），改显示查了哪些本体对象、命中哪些实体/口径规则（Jack 裁决「高大上」）。
  - **US-N5 (P2) 真实节奏**：思考流控制总时长（≥2.5s 兜底），步骤按自然速度释放，不机械逐步铺满（Jack 裁决）。
- **A3 验收标准（EARS，关键条）**：
  - WHEN 问句含错别字别名或口径歧义 THEN 系统 SHALL 返回确认式澄清且 SHALL NOT 出数（test_clarify_alias / HUMAN-engineering_edge-001/002/005/009）。
  - WHEN LLM 返回 finish_reason=length THEN 系统 SHALL 加长重试一次，SHALL NOT 静默降级关键词路由（test_length_retry）。
  - WHEN 问「唯一破千的渠道是谁」类聚合实体 THEN 系统 SHALL 正常应答（test_aggregate_entity_allowed）；safety_pii 7 条 SHALL 保持 PASS。
  - WHEN 溯源面板打开 THEN 用户 SHALL 看到本体对象与命中规则，SHALL NOT 看到层名/表名（vitest test_no_table_name）。
  - WHEN SSE 秒回 THEN 中间步骤 SHALL 以自然速度出现，final 展示落点 SHALL ≥2500ms（pacing.test 修订断言）。
- **A4 边界**：①确认式澄清话术复用现有 clarify 卡，不新造交互 ②安全个人级特征词表一个不减（只放行聚合实体向）③考卷期望回写逐条可追溯到裁决清单，禁止顺手改其他 case ④格式统一单独 commit，禁混逻辑改动 ⑤归因/多轮 chips 依旧挂起。
- **A5 非目标**：不做归因/事件日历；不动九步管道与审计链结构；不重建镜像库；不改三问测试语义。

## C. 计划
- **C1 任务表**（Rose 只看本表即可派活）：
  - T-N1 [S] ruff format 统一：ruff format src/semantic/rules.py src/semantic/llm_route.py，单独 commit。判据：ruff format --check 过＋pytest tests/semantic 187 全绿（行为不变）。
  - T-N2 [S] TD-13 截断修复：src/semantic/llm_route.py——max_tokens 调大（现值开工前探明）＋检测 finish_reason=length 后加长重试一次。判据：mock 单测 length→重试路径绿＋真跑 30 条抽样降级数如实前后对比＋tests/semantic 全绿。
  - T-N3 [S] 安全聚合实体放行：src/semantic/rules.py 模式一收窄——「唯一/正好」锚定但索求宾语为聚合维度（渠道/日期/总数）时不触发；个人级词表不动。判据：新增「唯一破千的渠道是谁」→非 REJECT 单测＋safety_pii 7 条与 test_safety_routing 零回退。
  - T-N4 [S] 节奏改总时长制：chatbi/src/hooks/useChatStream.ts StepPacer——步骤事件到达即放（保留最小可读间隔），仅当整体 <2.5s 时把 final 展示落点兜底至 2.5s；假步骤零断言不变。判据：pacing.test 新断言（首步不被拖慢＋final ≥2500ms）＋chatbi 全套件绿。〔spec 修订：UX优化_v0.2 A3-US3「按真实步骤事件补间至 2.5s」释义收窄为总时长兜底，Jack 2026-09-11 裁决〕
  - T-N5 [M] 确认式澄清路由硬化：src/semantic/llm_route.py＋rules.py（＋time_normalizer.py 口语时间）——NC-3 裁定 c 档全量：①错别字/未注册别名 ②口径歧义词（新客/新增） ③语流混乱句 → 复用 clarify 卡确认，不出数；④NC-4 并入：域外零信息输入体面澄清（「？？？」「930」→CLARIFY 不 REJECT）、「八月份」口语时间解析、「优享加线上」符号变体高置信映射应答（want ANSWER）、留存率口径确认。判据（以 fixtures 期望为准；2026-09-11 Rose 勘误：QW-caliber_trap-001 want REJECT 非 CLARIFY）：HUMAN-engineering_edge-001/002/005/009、GLM-engineering_edge-002/003、QW-engineering_edge-006、QW-caliber_trap-002、GLM-caliber_trap-001/006 转 CLARIFY；QW-caliber_trap-001 转 REJECT；HUMAN-engineering_edge-003（八月份解析）与 HUMAN-engineering_edge-006（优享加线上映射）转 ANSWER；engineering_edge 现有 PASS 零误伤。
  - T-N6 [M] 对抗考卷更新：tests/fixtures/对抗问法集_v0.2.json（multi_turn 12 条期望回写＋D 类 4 条 want CLARIFY）＋scripts/phrasing_eval.py（turns 承接模拟重写：T2 拼接基于 T1 答句上下文，不再要求 T1=CLARIFY 前置）。判据：改卷后 multi_turn 类复跑转绿；fixture diff 逐条对照裁决清单，无搭车。
  - T-N7 [M] 本体级溯源替代表名＋砍确认历史：chatbi/src/components/DetailDrawer.tsx＋CaliberPanel.tsx——①移除层·表名展示，改显「涉及本体对象＋命中实体/口径规则」②整个移除「确认历史」区块（Jack 2026-09-11 裁决砍掉该设计，面板只留口径卡），trace.test 对应断言同步更新（规格变更非凑绿）；数据源开工前探明（engine 返回已有则纯前端；需后端补结构化字段则本任务升级 L 并串行 T-N8）。判据：抽屉与口径面板零表名/零层名/零「确认历史」区块 vitest 断言＋对象/规则信息可见。
  - T-N8 [M] 改写旁路端点：src/semantic/app.py 增 POST /api/rewrite/answer：{kind,answer,facts}→glm 改写→{text}，后端 numbersMatch 双层校验（LLM 输出不可信）；确认历史下发已随 NC-2 裁决砍除，不在本任务。判据：端点 offline 冒烟＋数字漂移拒收测试＋前端接通后 offline 全走模板路径不回归。
- **C3 并行/串行**：T-N1 先行（格式先行保 diff 干净）→ T-N2/T-N3/T-N4 可并行 [P]；T-N5 与 T-N3 同文件串行（T-N3→T-N5）；T-N6 验收复跑依赖 T-N5 落地；T-N7/T-N8 后端同族串行，前端部分可与 T-N2~4 并行。并发 ≤4。
- **C4 止损**：各任务预期 1 轮；返工 ≥2 轮停回本稿修 spec，禁第 3 次 patch。

## D. 验收
- **D1 基线（Rose 已亲跑，2026-09-11 本窗）**：cd chatbi && npx vitest run → **52/52 passed**（@29d3577 树）；pytest tests/semantic -q → **187 passed**（@e042db6 树）。派活当日重跑复核贴新数。
- **D2 diff 对照**：收口时按 C1 逐任务填改动↔条目对照，搭车退回。
- **D3 演示路径（Jack 5 分钟）**：①问「9月注册」→点数字→口径卡→详情抽屉：见本体对象/规则，不见表名 ②问「赢行App 8月注册」→确认式澄清卡 ③问「唯一破千的渠道是谁」→正常出数 ④随便问一句掐表：步骤自然出现、整体约 2.5s 收尾、无假步骤。
- **D4 DoD**：绿 = A3 五条全绿＋基线无回归＋diff 无搭车；不算完 = 出现猜着答出数/表名回潮/假步骤/安全 case 回退。

## NC 登记（清零才派活）
| 编号 | 问题 | Rose 建议 | 状态 |
|---|---|---|---|
| NC-1 | 溯源面板（替代表名）展示什么？ | a 本体对象名＋命中规则名（如「注册记录 · 渠道｜R1 注册口径」） b a＋口径说明全文 c 其他 | NC-RESOLVED: Jack 选 1a（2026-09-11） |
| NC-2 | 确认历史数据从哪来？ | a 审计层已有确认记录直接透出（开工前先探明） b 新增「确认」动作落库（涉本体动作，按边界制度需你单独批） c 本期只铺字段管道、界面保持空态（推荐：探明无现成数据则 c） | NC-RESOLVED: Jack 裁决整个砍掉确认历史设计（2026-09-11）——面板只留口径卡，不做数据管道不加确认功能 |
| NC-3 | 确认式澄清触发范围？ | a 仅错别字/未注册别名 b a＋口径歧义词（新客/新增） c a＋b＋语流混乱句（推荐，最贴合「不要猜着答」） | NC-RESOLVED: Jack 选 3c（2026-09-11） |
| NC-4 | B 类其余真缺口（域外体面澄清/「八月份」口语时间/「优享加线上」映射/留存率口径）并入本批吗？ | a 并入（推荐，都是路由/规则小改，趁 T-N5 同族一次做） b 留下批 | NC-RESOLVED: Jack 选 4a 并入（2026-09-11） |
| NC-5 | 技术债表系统性撞号（表内 TD-12~16 与对抗系列 TD-12~16 共五处重号，不止 17）：表内老条目顺延改号 TD-19~23、对抗系列 12~17 保号 | a 按建议一次改清（推荐） b 只改已拍板的 17→18，其余挂起 | NC-RESOLVED: Jack 选 5a，已执行（2026-09-11） |

派活前检查：NC 状态列存在未解决项时禁派任何编码活（机器检查 grep 状态标记计数须为 0）。当前未解决 0 项，NC 已清零（2026-09-11 Jack 五题全裁决）。
