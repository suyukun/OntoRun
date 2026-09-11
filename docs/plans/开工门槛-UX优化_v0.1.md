# 开工门槛 · 用户体验优化（前台 ChatBI）v0.1

> 任务来源：Jack 反馈（13 寸屏侧边栏累/澄清生硬/多轮缺失/模糊问法走默认或拒答）+ 实测失败案例（tests/fixtures/Jack实测失败案例_2026-09-10.md，8 例）+ Rose 六项假设（思考流可读性/澄清/多轮/拒答卡/图表自然性/等待与错误路径）。
> 方法：docs/research/AI工程管理开工前方法调研_v0.1.md §2 L 级 18 项清单（A+B+C+D+运行时条款）。
> 编制：Rose（试填初稿）· 2026-09-11 · 状态：**待 Jack 答疑附录 A 后才可派编码活**；[假设]=挖不到事实的推断，[NEEDS CLARIFICATION]=必须 Jack 拍板，两者不清零不开工。

## 0. 现状事实基线（2026-09-11 代码走查 + 复现实测，全部核验）

**前端 chatbi/**（React18+TS+Vite 零 UI 依赖，:5173 → proxy :8901）：
- 状态机 deriveStatus.ts：八状态+3 生命周期变体显式映射；思考流=直播「第 n 步」→首 token 自动折叠→「已思考 N 步 · X.Xs」可展开。
- 澄清现状：PARAM_CHIPS 硬编码 ['8月','7月']（MessageCard.tsx:26），点 chip=拼「8月+原问题」发新查询；**手输短答（如"9月"）原样独立发送，无人接住**。
- 图表：Chart.tsx 仅 bar/kpi 渲染器（Chart.tsx:10），**pie/line 声明了但一律表格兜底**；rules.py viz_for 已产出 pie（性别）/line（时间粒度）。
- 侧栏：SessionBar 230px 固定（index.css:68），无折叠、全部 css 无任何 @media 断点；错误/等待路径完备（停止/重试/30s 看门狗/彩蛋/呼吸态）。
- 测试：vitest 5 文件；messageCard.test.tsx:114 已锁「8月」chip 续查、:131 锁 out_of_range 文案（改文案须同步测试）。

**后端 src/semantic/**（FastAPI :8901；M1 别名/M2 时间解析/M5 few-shot/M6 引导拒答于 09-10 18:08-18:41 提交）：
- **版本差实锤**：Jack 实测在 09-10 白天，早于 M1-M6 提交——案例 1/2（时间已说还追问/口误重复）在当前 HEAD 关键词链路复测已能答（本稿实测"2026年8月的注册"→measure 命中+时间提取成功）。**但三个真缺口当前 HEAD 仍复现**：
  1. **澄清协议缺失**：iter_query(question) 无 pending 状态，"9月"独立路由→measure=None→「该问题尚未注册口径」（案例 3/4 根因，实测复现）；
  2. **双轨不一致**：无时间问题 LLM 路径=默认最近完整月（M6.2，回显只进折叠的思考流步骤 detail，engine.py:310-311，final 帧无 time_defaulted 字段），关键词降级路径=追问月份（实测"今年的注册情况"→missing_param）——「走默认/拒答」双轨即此（案例 5 根因）；
  3. **范围语义错误**：时间窗与数据窗部分重叠即整体拒答「该时间段无数据」——"今年(2026-01~12)"实际 7-8 月有数据却说无数据，**诚实性缺陷**（案例 6）。
- 同比/环比=未注册派生概念→引导拒答（案例 7/8）；拒答文案「可提交为新的派生规则候选」对非数仓用户不可懂（Jack 点名伤人）。
- 演示基线：./scripts/demo_fortune.sh start；演示卡第一幕「最近一周注册走势」线上现为表格（line 渲染器缺）。

---

## A. 需求分析

### A1 一句话命题
给数仓同学和 Jack 的演示/试用现场：问不明白时系统能接住追问、说错话系统能容错、该出图的数据出图、界面在 13 寸屏不挤——让「有过程、有依据、可溯源」从能用的壳变成拿得出手的门面，且**每个回答仍宁拒不猜**。
完成标志：Jack 复述确认（附录 A #0）。

### A2 用户故事（用户=数仓同学与 Jack；砍掉 P2 后 P1 仍自成闭环）
- **US1 (P1) 13 寸屏不挤**：数仓同学在 13 寸笔记本看演示，侧栏可一键折叠（首字圆标导航），消息列限宽居中，注意力在数字不在壳。
- **US2 (P1) 多轮澄清循环的完整对话**：数仓同学问「注册用户数是多少？」→ 系统追问月份（选项来自数据窗，不硬编码）→ **用户手输「9月」或点选项** → 系统接住为本轮澄清的应答、自动续查；9 月无数据则如实说「样本仅覆盖 7-8 月」——一问一答一澄清闭环，短答不再被当新问题（Jack 案例 1/3/4）。
- **US3 (P1) 图表自然性**：领导看演示，「男女比例」出饼图、走势出折线；图表与表格永远同源，声明与数据形态不符回落表格并留痕。
- **US4 (P1) 模糊问法默认呈现 + 边界诚实**：问「今年的注册情况」→ 默认呈现（已覆盖范围的结果+假设显式标注），不反问月份；时间窗部分覆盖时只答覆盖部分并明说「仅覆盖 7-8 月」，绝不说「无数据」（Jack 案例 5/6）。
- **US5 (P2) 说人话**：拒答/未注册/追问文案让非数仓用户看得懂（不再有「派生规则候选」式黑话），SQL/表名/证据编号原样保留供专业核对（Jack 反馈④+思考流可读性假设）。

### A3 验收标准（EARS；括号内=对应测试名）
**US1**
- WHEN 视口<1440px 或点击折叠钮 THEN 侧栏 SHALL 折叠至 ≤56px 并以首字圆标保留切换（sidebar.fold）
- WHEN Cmd/Ctrl+B THEN 折叠态 SHALL 切换且 localStorage 记忆（sidebar.shortcut）
- WHEN 折叠或宽屏 THEN 消息内容列 SHALL 限宽 ≤860px 居中（layout.maxwidth）
**US2**
- WHEN final 为参数追问且 result.clarify.options 非空 THEN 卡片 SHALL 渲染后端下发选项（弃前端硬编码月份）（clarify.options）
- WHEN 用户手输 ≤4 字短答且上一条 AI 卡为未解决追问 THEN 系统 SHALL 将短答与原问题合并续查，不独立路由（clarify.catch）
- WHEN 续查进行中 THEN 选项 SHALL 置灰防重，且澄清一轮为限不循环（clarify.once）
- WHEN 后端未下发 clarify（降级/旧会话恢复）THEN SHALL 回落纯文案追问不伪造选项（clarify.fallback）
**US3**
- WHEN viz='pie' 且 rows≤5 行 THEN SHALL 渲染饼图，>5 切片合并「其他」（chart.pie）
- WHEN viz='line' 且 rows 为时间序列 THEN SHALL 渲染折线（chart.line）
- WHEN viz 声明与 rows 形态不符或 rows 空 THEN SHALL 回落表格/空态并在 trace 留痕（chart.shapefence）
**US4**
- WHEN 时间窗与数据窗部分重叠 THEN 系统 SHALL 裁剪至重叠窗回答并在回答与步骤中显式说明覆盖边界，SHALL NOT 答「无数据」（range.partial）
- WHEN 时间窗完全出界 THEN SHALL 如实报数据边界与可问范围（range.out）
- WHEN LLM 与关键词降级两条路径遇无时间问题 THEN 行为 SHALL 一致（默认或追问二选一，附录 A #2）（time.consistent）
**US5**
- WHEN 渲染拒答/未注册/追问文案 THEN SHALL 通过「外行人能懂」清单（无派生规则候选/语义层元数据等术语），拒答无数字红线不破（copy.plain）
- WHEN 用户展开思考区 THEN 每步 SHALL 有业务化标题+人话说明，SQL/表名/证据编号原样保留（thinkflow.readable）

### A4 边界条件
1. 澄清续查后仍失败（如 9 月→out_of_range）→ 渲染对应状态卡+重试，追问不循环（一轮为限，M4 原则）。
2. 手输短答但上一条不是追问卡（用户已换话题输入完整问题）→ 不拼句正常路由；「短答」判定=≤4 字且命中澄清槽枚举（月份/渠道）[假设：判定规则见 B3]。
3. 刷新/切会话后 pending 澄清丢失 → 澄清卡随 result 快照仍在、点选项仍可续查；手输短答接住失效（可接受，记已知限制）[假设]。
4. mock 模式（后端未起）→ mock/stream.ts 同步补 pie/line/clarify/边界说明场景——mock 也是交付物。
5. 流式生成中折叠侧栏 → 纯布局操作，不得中断流/丢消息；busy 中重复点选项 → 现有 busy 置灰复用。
6. 关键词降级路径无 clarify 数据 → 回落纯文案追问（不伪造选项）。

### A5 非目标（出现即退回）
1. **自由上下文多轮**（「那 7 月呢」依赖上轮查询组合做 patch）——鲁棒性方案 v0.1 已排二期；本期只做**澄清循环内**的短应答接住（US2），两者边界=是否需要上一轮组合。
2. 同比/环比等派生概念的计算与注册（语义层活，另立任务；本期只把拒答文案改得诚实易懂）。
3. 375px 移动端精修（UX 审查 P2-2、BACKLOG A4 挂账不变）。
4. P2 清单未勾选项（原生 confirm 替换/会话搜索/焦点陷阱等）——除附录 A #8 点名捎带项。
5. 引入任何 UI 框架/图表库（保持零依赖）；ADR-0009 思考流交互范式不回退。

---

## B. 设计（只定会返工的部分）

### B1 技术上下文
- 动哪些文件：前端 chatbi/src/{index.css, App.tsx, components/{SessionBar,MessageCard,Chart,labels}, types.ts, mock/{stream,profile}}；后端 final 帧字段级扩展 src/semantic/{engine.py, llm_route.py, rules.py} + 范围裁剪语义 engine._check_params；测试 chatbi/src/__tests__/ 新增 3-4 文件 + tests/semantic/test_core.py 增量 + 压测集 fixtures 扩 Jack 8 例。
- 依赖与版本不变量：chatbi 仅 react/react-dom 不新增；Python 无新依赖；DuckDB 镜像/SQLite schema 不动。
- 数据存哪：折叠态 localStorage（对齐 S4 key：chat.sidebar.collapsed）；clarify options 随 final 快照自然持久化；pending 澄清仅内存（A4-3）。
- 怎么测：vitest（jsdom，mock 模式先行）+ pytest 增量 + phrasing_eval 压测 + curl final 帧冒烟。
- 影响面预估：前端 9 文件+后端 3-4 文件+测试，≈600-1000 行 [假设]。

### B2 关键决策（≤5，收口时提炼 ADR 雏形）
1. **澄清应答接住放前端**：App 层持 pendingClarify（内存），手输短答/点选项均「拼回完整问句」续查（"9月"+"注册用户数是多少？"）——备选「后端会话级 pending state」被否：服务端状态化破坏幂等回放与无状态 SSE，演示期单用户不值得；代价=刷新后短答接住失效（A4-3 已声明）。
2. **澄清选项契约进 final 帧**：result.clarify={question,options,kind}，options 由规则表/注册表生成（月份=数据覆盖窗枚举，渠道=维表成员），不让 LLM 编——D7 同构：控制权在语义层；顺带修「选项只有 8/7 暴露数据窗」→选项与边界说明同源生成（Jack 案例 1）。
3. **范围裁剪是语义不是展示**：部分重叠→裁剪回答属 engine._check_params 语义改动+文案诚实化，前端只渲染——备选「前端改写 out_of_range 文案」被否：数字必须同源，前端无权改语义结论。
4. **pie/line 纯 SVG 手写**延续 bar 先例（BACKLOG A4 分层原则：图型语义层定、样式展示层；ECharts 被否：零依赖+3 类图够演示）。
5. **默认窗策略统一**：M6.2「无时间→默认最近完整月+显式标注」扩展到关键词降级路径，标注从思考流提升到卡面（time_defaulted 进 final 帧）——双轨统一为「默认呈现」，是否保留追问路径待附录 A #2 裁决。

### B3 接口/数据契约（先定后写码）
    // chatbi/src/types.ts FinalResult 增（engine.py final 帧同步产出）：
    clarify?: { question: string; options: string[]; kind: 'missing_param' | 'dimension_value' }
    time_defaulted?: boolean   // M6.2 透出，卡面渲染假设标记
    range_note?: string        // 部分重叠时的覆盖边界说明（如「样本仅覆盖 2026-07-01~08-31」）
- 短答判定：≤4 字、正则 ^(\d{1,2}月|\d{4}年\d{1,2}月|去年|今年)$ 且值 ∈ 本轮 options/覆盖窗 [假设：实现时按枚举校验]。
- viz 契约不变（types.ts 已声明五类，只补渲染器）。完成标志：types.ts 可 import、pytest 断言 final 帧新字段。

### B4 宪法门禁检查
- 三铁律：①每 US 独立可交付、mock 先绿再联调 ✅ ②A3 每条挂具名测试 ✅ ③契约进 types.ts+engine 同步、决策记 B2 ✅
- 最小实现：无投机抽象；pending-state/ECharts 等更重方案均写明否决理由 ✅
- 安全：options/边界说明由注册表生成不让 LLM 编（注入面不扩大）；拒答无数字、仿真徽标、宁拒不猜三项演示红线不破 ✅
- 边界三档：不加依赖、不删文件、不改本体 schema → 无 🚫 项 ✅

---

## C. 计划（tasks 级）

### C1 任务清单（判据=可勾选）
- **T0 [前置·后端契约]**：final 帧补 clarify/time_defaulted/range_note + _check_params 部分重叠裁剪语义 + options 生成（rules.py）。判据：pytest tests/semantic/test_core.py 增量绿 + 压测集扩 Jack 8 例后 phrasing_eval 全绿。
- **T1 [US1]**：SessionBar/App/index.css 折叠+限宽。判据：A3-US1 三测试绿。
- **T2 [US2]**：MessageCard/App 澄清卡渲染+pendingClarify 短答接住+mock 场景同步。判据：A3-US2 四测试绿；更新既有 chip 断言。
- **T3 [US3]**：Chart.tsx 补 pie/line 渲染器+形态防御。判据：A3-US3 三测试绿；mock GENDER_RATIO 出饼图。
- **T4 [US4 前端半]**：卡面默认窗/覆盖边界标记渲染。判据：A3-US4 相关断言绿（后端半在 T0）。
- **T5 [US5]**：labels.ts 文案包（说人话）+思考流黑话降密按附录 A #6 裁决。判据：A3-US5 两测试绿+既有断言不破。

### C2 阻断性前置
T0 唯一前置，完成即解锁 T2/T4；T1/T3 无依赖可即开。

### C3 并行与依赖
- 波 1 并行 [P]：T0 ‖ T1 ‖ T3（三路，≤4 限额内）；波 2：T2+T4；波 3：T5+联调收口（demo_fortune.sh 起→curl 六问回归→压测集）。
- 串行约束：联调冒烟必须最后；mock 场景改动与 live 行为同一任务内交付。

### C4 时间盒与止损
- 单任务 1-2 轮子代理交付（AI 产能基准），整体 ≈2-3 个子代理日 [假设：无同类历史排期可参照]。
- 止损：同一任务返工 ≥2 轮 → 停，回本稿 B 修 spec，不许第 3 次 patch。
- 时间盒锚点 [NEEDS CLARIFICATION] #9：无明确演示日期则按「随下次口径确认会」倒排。

---

## D. 验收（开工前就能跑）

### D1 可执行验收命令（开工前先跑基线并记录）
    cd chatbi && npm run test                          # 基线已实跑（2026-09-11 10:17）：5 文件 31 passed 全绿
    cd chatbi && npm run test -- chart                 # T3 前预期红（无 pie/line 渲染器）
    cd chatbi && npx tsc --noEmit && npm run lint      # 基线零错
    pytest tests/semantic/test_core.py -q              # 增量；纪律：禁全量 pytest（仅 Rose 阶段末）
    pytest tests/semantic/test_llm_route_v2.py -q
    .venv/bin/python scripts/phrasing_eval.py          # 需 DEEPSEEK_API_KEY；基线 29/30，扩 Jack 8 例后不应降
    curl -s http://127.0.0.1:8901/api/profile | head -c 300      # 在线冒烟
    curl -sN -X POST http://127.0.0.1:8901/api/chat -H 'Content-Type: application/json' \
      -d '{"question":"注册用户数是多少？"}' | tail -3            # T0 后看 final 帧 clarify 字段

### D2 验收看 diff（改动行须可追溯，搭车即退回）
| diff 范围 | 条目 |
|---|---|
| SessionBar/App/index.css | US1/A3-US1 |
| MessageCard+App(pendingClarify)+types.ts | US2/A3-US2 |
| Chart.tsx | US3/A3-US3 |
| engine._check_params+卡面标记 | US4/A3-US4 |
| labels.ts | US5/A3-US5 |
| engine/llm_route/rules final 帧 | T0/B3 |
| 压测集 fixtures 扩 8 例 | §0 真缺口回归 |

### D3 Jack 5 分钟演示路径（亲手走，含一条被打断/说错的对话）
1. ./scripts/demo_fortune.sh start → 开 :5173，窗口缩到 ~1280 宽模拟 13 寸。
2. Cmd+B 折叠侧栏→消息列变宽→点首字圆标展开。（US1）
3. 问「注册用户数是多少？」→追问卡出可点月份→**故意说错：输入「去年」**→系统如实答数据边界与可问范围、不出假数→点「8月」选项→出数。（US2+被打断动线）
4. 问「9月注册用户数是多少？」→如实答「样本仅覆盖 7-8 月」——诚实边界是卖点不是翻车。（US4 回归）
5. 问「8月注册用户的男女比例」→饼图；问「最近一周注册走势」→折线 [若 #5 裁决进主线]。（US3）
6. 问「今年的注册情况」→默认呈现+「按 2026-08 统计（样本覆盖 7-8 月）」标记可见。（US4）
7. 回归重头戏：「注册用户资产规模」→拒答卡（新文案说人话）；流式中点「停止」→「已取消」→重试；刷新→会话恢复。
预期：全程无表格顶替图表、无短答被当新问题、无「无数据」假话、无需要重打完整问法的追问。

### D4 DoD 一句话
绿 = D1 全绿 + D3 七步走通 + A3 每条有同名测试 + diff 全部可追溯 + Jack 8 例逐条销号；不算完 = 任一 US 无测试、引入新依赖、A5 内容进 diff、或附录 A 未清零即开工。

---

## 运行时条款（开工后）
- 收口=converge：交付对照 §A3+Jack 8 例逐条打勾，不接受「我觉得完了」。
- 返工第 2 轮起：新开会话只带本稿+失败清单，不带修补历史（防上下文劣化）。
- 红线：宁拒不猜/拒答无数字/仿真徽标/图表表格同源——任何触碰即停。

## 附录 A：[NEEDS CLARIFICATION] 给 Jack 的问题清单（最高优先输出）
| # | 问题 | 默认建议（不答按此执行） |
|---|---|---|
| 0 | A1 命题与 US1-5 范围复述确认 | 确认后开工 |
| 1 | 侧栏「累」的解法：折叠（56px 圆标+Cmd+B）/窄化/默认收起？ | 折叠+S4 模式裁剪 |
| 2 | 无时间问题统一策略：一律默认呈现+显式标注（推荐，双轨合一），还是保留追问？哪些场景保留追问？ | 默认呈现+标注 |
| 3 | US2 短答接住仅限「上一条=未解决追问卡」，刷新后失效可接受？ | 可接受，记已知限制 |
| 4 | 「今年的注册情况」期望形态：总量+月度趋势同屏，还是先答总量给趋势入口？ | 先答已覆盖范围总量+趋势折线 |
| 5 | 走势/饼图进演示主线？（决定 T3 优先级；走势题线上现为表格） | 进主线 |
| 6 | 思考流黑话降密度：原语 id（REG_TOTAL）、耗时 ms、LLM 原始 JSON 哪些保留在卡面思考流？（现全在，抽屉另存审计视图） | 保留 SQL/表名/id，ms 与原始 JSON 只留抽屉 |
| 7 | 演示验收口径：live（真 DeepSeek 有路由方差）还是 mock？案例 1/2 建议先在当前版本 live 复测再定压测集 v2 范围 | live 演示、mock+压测集验收 |
| 8 | P2 捎带：切会话闪旧消息（P2-3，~10 行）做不做？ | 做 |
| 9 | 下次演示/试用日期？（定 C4 时间盒） | 随下次口径确认会 |

## 附录 B：[假设] 清单（可被事实推翻）
1. 13 寸屏≈1440×900 逻辑分辨率（UX 审查截图同款）；数仓同学跟随演示用笔记本。
2. 用户=数仓同学（口径确认场景）+Jack（演示者/试用者），非每日重度用户——高频使用行为不在本期输入内。
3. 折叠交互移植 S4 spec（docs/chat-ux-spec-v1.md §2.3-2.4，另一壳 web/src/chat）裁剪为自绘，仅作模式参照。
4. clarify options 生成：月份=数据覆盖窗逐月枚举（当前 2026-07/08），渠道=维表成员（复用 suggestions）；短答判定见 B3。
5. 时间盒≈2-3 子代理日为 AI 产能估算，非人天；无历史 UX 排期可参照。
6. localStorage key 沿用 S4 命名 chat.sidebar.collapsed（两壳并存不冲突）。
7. Jack 案例 1/2 在 live+当前 HEAD 的实际表现未复测（本稿仅复测关键词链路）——附录 A #7 裁决后补测。
