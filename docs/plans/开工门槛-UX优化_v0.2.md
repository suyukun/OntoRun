# 开工门槛：UX 优化 v0.2（aha 两腿：主动洞察＋可感知信任）

> 级别：**L 级**（跨模块：chatbi 前端＋语义服务新模块＋新端点；按开工门槛-模板全表填写）。
> 输入：Jack 定位级反馈「整个系统不 aha」＋调研 docs/research/ChatBI体验设计调研_v0.1.md（Tableau Pulse 样板：主动洞察检测层=统计规则非 LLM）＋ Jack 三点裁决（SQL 不暴露／P1 挂起／洞察宁缺毋滥）。
> 与 UX v0.1 的关系：**本稿取代 v0.1**——v0.1 的 10 项 U 卡修订项（侧栏折叠等）转 BACKLOG，aha 主线落地后按需重开。
> 状态：初稿，NC 清零＋Jack 过目后才派编码活。派活时机：**引擎改动单收口后**（app.py 不双飞）。

## 0. 级别声明
L 级，填全表。不做降级。

## A. 需求
- **A1 一句话命题**：给数仓同学与演示对象：打开产品，值得看的自己先开口（洞察卡），每个数字点得穿、敢相信（溯源穿透）——从问答计算器变成先开口、可信任的数据分析师。
- **A2 用户故事**：
  - **US1 (P1) 溯源穿透**：点答案里任一数字 → 口径卡（这句数怎么算的，人话＋规则状态）→ 来源明细行样例 → 确认历史（谁何时确认）。**SQL 与表结构不出用户层**（Jack 裁决：对客户无意义＋攻击面）。
  - **US2 (P1) 主动洞察**：打开产品，规则命中才出洞察卡（渠道日环比突变/总量突变/贡献度突变），卡带「看分解」走现有语义接口；**没有发现不出卡**，退化为常用查询入口（Jack 裁决：宁缺毋滥不强行加戏）。
  - **US3 (P2) 思考节奏与话术**：最短 2.5s 真实时钟补间（演示模式可配，节拍器由真实 SSE 步骤事件驱动）＋思考流话术模板池随机化；**假步骤零容忍**。
  - **US4 (P2) 拒答话术改写**：REJECT/CLARIFY 文案 flash 模型并行改写＋模板兜底；数字与事实永远由结构化字段回填，LLM 只改措辞。
- **A3 验收标准（EARS）**：
  - WHEN 用户点击答案中任一数字 THEN 系统 SHALL 展示口径卡＋来源明细样例＋确认历史，SHALL NOT 展示 SQL/表结构（vitest test_trace_penetration）。
  - WHEN 洞察规则命中（|日环比|≥30% 且近 7 日样本≥5 日）THEN 打开页 SHALL 置顶洞察卡并带「看分解」动作；WHEN 无命中 THEN SHALL 显示常用查询入口，SHALL NOT 出现凑数洞察卡（pytest test_insights_rules + vitest）。
  - WHEN SSE 全程 <2.5s 且演示模式开 THEN 前端 SHALL 按真实步骤事件补间至 2.5s，SHALL NOT 插入不存在步骤（vitest test_pacing_fake_step_zero）。
  - WHEN REJECT/CLARIFY 产生 THEN 改写并行发起（超时 2s 回退模板），文案中数字 SHALL 与结构化字段逐一相等（test_rewrite_fallback + 数字相等断言）。
- **A4 边界**：①洞察只报事实**不归因**（无事件日历，因果沉默=诚实铁律；归因二期走事件标注积累）②阈值 30%/7 日/最小样本 5 日为常量可配 ③审计层内部保留 SQL，用户可见层零 SQL ④改写失败/超时/限流→模板静默回退 ⑤多轮 chips、首页聚合位（原 P1）**挂起**等引擎 v0.2 落地后评估 ⑥路由提速（TD-13）另单不在本稿。
- **A5 非目标（出现即退回）**：不做归因/事件日历；不做多轮 chips；不暴露 SQL/表结构；不改九步管道与审计链结构；不动语义接口既有契约（仅新增 GET /api/insights）。

## B. 设计
- **B1 技术上下文**：动 chatbi/src/（穿透面板组件、洞察卡、节奏补间、话术池）、src/semantic/insights.py（新，规则引擎读镜像库）、src/semantic/app.py（+GET /api/insights，只读）、tests/。预期 diff：净增 600~900 行。
- **B2 关键决策**：①洞察=统计规则非 LLM（Tableau Pulse 模式；备选 LLM 生成洞察被否：幻觉＋费用＋不可审计）②用户可见层零 SQL（Jack 裁决；备选展示 SQL 被否：无意义＋攻击面）③改写并行＋模板兜底（月 0.4 元实证；备选同步改写被否：白加时延）④补间由真实 SSE 事件驱动（NN/g 三限值＋Devin/o1 反例；备选固定 sleep 被否：表演式进度）。
- **B3 契约（T-U1 前冻结）**：GET /api/insights → {"insights":[{type, channel, metric, current, baseline, delta_pct, drilldown:{measure,dimensions,time}}]} | {"insights":[], "fallback":"common_queries"}；穿透面板数据 = {caliber_card, sample_rows(≤5), confirm_history}（字段不含 SQL）。
- **B4 宪法门禁**：①MVP 三小件先跑通 ✅ ②规则与断言机器可验证 ✅ ③单一事实来源（本稿+调研文档）✅；安全：/api/insights 只读、无 SQL 回显、阈值常量防注入（数值白名单）。

## C. 计划
- **C1 任务**：
  - T-U1 [US1][P] chatbi 穿透面板（口径卡/来源行样例≤5/确认历史；数字可点击）。判据：vitest 穿透断言绿＋用户层零 SQL 断言绿。
  - T-U2 [US2] src/semantic/insights.py（三条规则＋常量）＋GET /api/insights＋洞察卡组件＋常用查询兜底。判据：pytest test_insights_rules 绿（命中/不命中/兜底三态）。
  - T-U3 [US3][P] 节奏补间＋话术模板池。判据：vitest 补间断言绿＋假步骤零（断言步骤集合⊆真实 SSE 事件）。
  - T-U4 [US4][P] 改写并行＋模板兜底＋数字相等断言。判据：vitest 绿＋offline 冒烟回退路径绿。
- **C2 前置**：无内部前置；**派活时机=引擎改动单收口后**（app.py 独占写）。
- **C3 并行**：T-U1 ∥ T-U3 ∥ T-U4（前端）＋T-U2（后端），并发 4 ≤4。
- **C4 止损**：各任务预期 1 轮；返工 ≥2 轮停回 B 修 spec。子代理派发单注明 bash timeoutMs ≥120000、禁全量 pytest。

## D. 验收
- **D1 基线（派活前 Rose 亲跑记录）**：cd chatbi && npx vitest run（记录基线）；pytest tests/semantic -q（当前 165 passed）；新增测试先行预期红（test_insights_rules/test_pacing_fake_step_zero）。
- **D2 diff 对照**：chatbi/src ↔ T-U1/U3/U4；insights.py+app.py ↔ T-U2；出现 SQL 回显或归因文案 = 退回。
- **D3 演示路径（Jack 5 分钟）**：①打开产品→看洞察卡或常用查询兜底 ②任问一句→点答案数字→口径卡→来源行→确认历史 ③问「9月注册」→看 REJECT 话术 ④关演示模式对比节奏。
- **D4 DoD**：绿 = A3 四条 EARS 全绿 + 用户层零 SQL 断言绿 + 基线无回归 + diff 无搭车；不算完 = 出现凑数洞察卡/假步骤/SQL 回显/归因文案。

## NC 登记（NEEDS CLARIFICATION；清零才派活）
| 编号 | 问题 | Rose 建议 | 状态 |
|---|---|---|---|
| NC-U1 | 来源明细行展示深度：样例 5 行还是可展开全量？ | 样例 5 行＋总数计数 | NC-OPEN |
| NC-U2 | 洞察阈值 30%/近 7 日均值/最小样本 5 日，默认合理？ | 按此默认，常量可配 | NC-OPEN |
| NC-U3 | 话术改写用哪个模型？ | zai glm-5.3-flash（套餐内免费，与路由同源但改写为旁路小调用） | NC-OPEN |
| NC-U4 | 2.5s 节奏开关默认值？ | 配置文件开关，演示默认开 | NC-OPEN |

派活前检查：grep -c 'NC-OPEN' 本文件 = 0。
