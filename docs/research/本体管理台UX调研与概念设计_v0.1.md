# 本体管理台 UX 调研与概念设计 v0.1

> 任务：本体管理台（后台）的 UX 调研与概念设计——重点是"用户友好的呈现与交互"，不回答"造不造轮子"（上游已论证）。
> 上游文档：docs/research/本体管理台对标调研_v0.1.md（结论：治理底座复用 git + 界面自建薄壳）。本文回答"薄壳长什么样、用什么画图谱、和 chatbi 什么关系"。
> 调研人：Rose（子代理）；日期：2026-09-10；检索：web_search 5 次共 14 query（协议上限 30）+ 官方文档深读 + GitHub/npm API 一手实查。
> 来源标注：[T1]=官方文档/API 一手实查；[T4]=媒体评测；检索不到的如实标"未找到"。GitHub stars/pushed 与 npm 下载数据均为 2026-09-10 API 实查。
> 用户锚点：数仓工程师/分析师（专业但不写代码、不看 git），三件事 = 看懂 / 确认 / 追溯。本体规模 ≈ 28 张表、几十个对象/事件、中文标签、需点击看详情。

---

## 0. 从三件事推出的设计原则

| 用户要做的事 | 设计推论 |
|---|---|
| 看懂 | ① **业务名词即导航**：一级导航用"对象/规则/图谱"（业务语言），不用"表/字段/schema"（技术语言）；表名字段只在"绑定"里作为属性值出现。② **状态双编码**：未确认=橙色+文字徽章、已确认=绿色+徽章，绝不只用颜色。③ **每页都给"这是干嘛的"一句话**（对象有业务定义，规则有人话标题）。 |
| 确认 | ④ **口径规则是一等公民**：管理台的核心可操作对象不是"表"，是"口径规则"——它有自己的列表页、队列页、详情卡。⑤ **确认 = 是非题，且永远带上下文**：勾选框旁边必须同时可见：规则人话正文、出处（哪个脚本哪段）、影响哪个度量、上次确认人与时间。 |
| 追溯 | ⑥ **出处永远可展开、默认折叠**：默认展示"etl/reg_activation.sql L42-58"这样的定位摘要，点击展开脚本片段（用户不读代码，但要能指给开发看）。⑦ **确认必须冻结版本**：点确认那一刻的注册表版本（git commit hash）、确认人、时间一起落库——"确认的是哪个版本"说不清，确认就无效。 |

Palantir 的形态佐证这个切法：Ontology Manager（OMA）面向建设者做维护，Object Explorer 面向用户做探索——**同一个本体，两种界面人格**；我们对应为：管理台（数仓同学）≠ ChatBI（业务提问）。[T1] https://palantir.com/docs/foundry/ontology-manager/overview/ （官方定义 "enables you to build and maintain your organization's Ontology"）｜ https://palantir.com/docs/foundry/object-explorer/getting-started/ （官方定义 Explorer 首页为 "an orientation hub where one can start exploring objects"）

---

## 1. 调研发现

### 1.1 Palantir Ontology 管理侧的界面形态

**诚实声明：Palantir 文档站为客户端渲染，本文多次尝试（SSR HTML 抽取、Jina 阅读器代理）均无法取回完整正文；以下基于官方页面的 meta 摘要、文档目录树与上游调研已核实的一手引文。截图未找到（learn.palantir.com 课程页 403，上游调研已实证）。**

可确认的界面事实：

1. **双应用分工**：Ontology Manager（建设者：建/改对象类型、属性、链接类型）与 Object Explorer（消费者：探索对象与关系）。Explorer 首页定位是 "orientation hub"——即**工作台/入口枢纽**，从具体对象或自由探索两个方向进入。[T1] meta 摘要，URL 同上
2. **文档目录树透露的功能面**（palantir.com/docs Ontology building 节，[T1] 侧边栏实抓）：Ontologies → Branching → Review ontology proposals（提案评审）；Object types → Create/Edit；Properties；Link types；Object Explorer（独立应用节）。——**"浏览"与"变更治理"在 IA 上是分开的两块**，不是混在一个列表里。
3. **变更治理 = 提案-评审-合并**：官方原话 "An ontology proposal is analogous to a Pull Request in a version control system. Proposals serve as a mechanism for reviewing and approving changes"。[T1] https://palantir.com/docs/foundry/ontologies/review-ontology-proposals/ （meta 摘要实抓；全文核实记录见上游对标调研 v0.1）
4. **对我们的映射**：Palantir 的 proposal 流重（分支→修改→提案→评审→合并），我们的最小同构是**状态翻转即 commit**（unverified→confirmed 一次点击生成一条带身份的 git commit）——上游对标调研 v0.1 已定此路线，本文的确认 UX 都建立在其上。

### 1.2 对象详情页参照：OpenMetadata / DataHub 术语详情页

两者虽是"描述型"目录（管术语不管口径确认），但**详情页的字段组织与左右结构**是数仓同学熟悉的行业普通话，直接借鉴：

- **OpenMetadata Glossary Term 字段清单**（[T1] 实抓 https://docs.open-metadata.org/v1.13.x/how-to-guides/data-governance/glossary/create-terms ）：Name / DisplayName / **Description（必填，官方要求 "a unique and clear definition to establish consistent usage and understanding"——强制业务定义，正是对象详情页头部的做法）** / Tags / Synonyms / Related Terms / Mutually Exclusive / References（外链出处）/ **Owner / Reviewers（负责人制）**。子术语构成概念层级。
- **DataHub Business Glossary 页面结构**（[T1] 实抓 https://docs.datahub.com/docs/glossary/business-glossary ）：
  - 入口在顶部 "Govern → Glossary"，**左侧层级导航树 + 右侧详情**的经典目录布局；
  - Term 页内用 **Tab 分区：Related Terms（Contains/Inherits 关系）/ Related Entities（被哪些资产引用）**——"定义、关系、被引用"三分法，可平移为我们的"概览 / 口径规则 / 关系 / 变更历史"Tab；
  - 编辑=行内编辑（点名称旁铅笔），删除=二次确认弹层；
  - 官方定位原话：术语间关系把 Glossary 变成 "a connected, machine-readable model of your business that can be **visualized, traversed, and queried**"——与我们"列表+图谱双视图"一致。
- **差异提醒（不照抄的部分）**：目录类详情页是"静态描述"，我们的口径规则 Tab 每张卡带**可操作的是非题按钮**——详情页不是纯阅读页，这是与 OpenMetadata/DataHub 的本质区别。

### 1.3 确认/审批流的 UX 模式（业界做法）

| 模式 | 出处 | 对我们的取舍 |
|---|---|---|
| 提案-评审-合并（proposal ≈ PR） | Palantir [T1]（见 1.1-3） | 太重。MVP 只取"每次变更留痕可评审"的内核：状态翻转=commit |
| Owner/Reviewer + 认证状态徽章 | OpenMetadata Glossary [T1]（见 1.2；certification 机制见上游调研 v0.1） | 取"负责人+状态徽章常驻卡片"的呈现；MVP 不做多角色（开放问题 3） |
| 审批工单 + 版本字段级 diff（变更标红+旧值删除线）+ 双负责人（业务/技术口径分设） | 网易有数指标字典、腾讯 WeData [T1]，详见上游对标调研 v0.1 块3 | diff 呈现方式照抄：**语义 diff（"哪个口径描述从 X 变成 Y"）默认展示，原始 git diff 折叠为"查看原始变更"**。双负责人制进开放问题 3 |
| 二次确认弹层（删除等不可逆动作） | DataHub 删除流程 [T1]（见 1.2） | 确认口径是可逆动作（再点一次翻转状态，产生新 commit），**不做二次弹层**，但 toast 里明示"已记录：王工 2026-09-10 确认" |

**追溯的三件套（每条规则卡必须能展开）**：① 出处：ETL 脚本路径+行段锚点，点击展开片段；② 确认记录：谁、何时、确认时的注册表版本（commit hash 短码展示）；③ 变更时间线：该规则的 git log 翻译成人话列表（例："2026-09-01 李工 把生效日期从 07-01 改为 07-09"）。git 本身已内置全部数据（上游调研 v0.1：git log --follow + diff 渲染，约 0.5 天），管理台只做**翻译层**。

---

## 2. 概念设计

### 2.1 信息架构（页面清单）

单应用、左侧一级导航，六个页面：

| # | 页面 | 一句定位 | 对应"三件事" |
|---|---|---|---|
| 1 | **工作台**（首页候选） | 今天必须处理的事：待确认规则数（大数字+直通按钮）+ 最近 7 天变更摘要 + 本体规模卡（N 对象/N 事件/N 规则/N% 已确认） | 确认（入口） |
| 2 | **对象列表页** | 本体目录：对象+事件统一列表（类型/业务域筛选，每行显示"规则数+未确认数"徽章），行点击进详情 | 看懂 |
| 3 | **对象详情页** | 单个对象的全部真相：定义、属性+绑定、口径规则卡（含确认状态与出处）、关系、变更历史（Tab 组织，见 wireframe ①） | 看懂+确认+追溯 |
| 4 | **口径规则页**（规则中心） | 全部口径规则的横切面：按确认状态/所属对象/出处脚本过滤的列表，每行一条是非题——**确认动线的主体页** | 确认 |
| 5 | **全局图谱页** | 对象+链接的一张图：看结构、找孤立对象、点节点侧滑出摘要卡进详情（见 wireframe ③） | 看懂 |
| 6 | **变更历史页** | git 历史的人话翻译：全局时间线 + 按对象/规则/操作人过滤，每条可展开语义 diff | 追溯 |

顶栏：全局搜索（对象名/规则关键词/表名）+ 待确认角标（任何页可达确认队列）+ 用户身份（确认动作的身份来源）。

> IA 上刻意不做的：多级权限管理页、批量导入页、通知中心——发布期再说（与上游调研 v0.1 的 MVP 裁剪一致）。

### 2.2 Wireframe ①：对象详情页（核心页）

信息层级：**头部身份卡 → Tab 概览（属性+绑定并排）→ 口径规则 Tab（确认动线所在）→ 关系 Tab**。线框为示意，宽度不代表最终像素。

~~~
┌──────────────────────────────────────────────────────────────────────────────┐
│ 顶栏 [OntoRun 管理台]  [🔍 搜对象/规则/表名…]              [待确认 12] [王工 ▾] │
├─────────┬────────────────────────────────────────────────────────────────────┤
│ ▣ 工作台 │  ← 返回对象列表                                                     │
│ ○ 对象   │ ┌──────────────────────────────────────────────────────────────┐  │
│ ○ 规则   │ │ 👤 User 用户                    [对象] [业务域·客户]           │  │
│ ○ 图谱   │ │ "在 APP 或渠道完成注册的自然人"          负责人: 李工           │  │
│ ○ 变更   │ │ 口径规则 5 条：✅ 3 已确认 · ⚠️ 2 待确认                       │  │
│         │ │ [概览] [口径规则 5•] [关系] [变更历史]      ← Tab（•=待确认）    │  │
│         │ └──────────────────────────────────────────────────────────────┘  │
│         │ ▼ Tab「概览」                                                      │
│         │ ┌─ 属性 ────────────────────────┐ ┌─ 绑定（数仓定位）────────────┐  │
│         │ │ 属性     业务含义     类型     │ │ 属性     → 表.字段            │  │
│         │ │ gender   性别        枚举     │ │ gender   dw.dwd_user.gender  │  │
│         │ │ reg_type 注册类型     枚举     │ │ reg_type dw.dwd_user.reg_type│  │
│         │ └───────────────────────────────┘ └──────────────────────────────┘  │
│         │ ▼ Tab「口径规则」——规则卡列表（待确认置顶）                          │
│         │ ┌──────────────────────────────────────────────────────────────┐  │
│         │ │ ⚠️ R-012 注册 KPI 激活边界                        [未确认]     │  │
│         │ │ "麦当劳/中信渠道用户需完成激活，才算注册 KPI"                   │  │
│         │ │ 生效：2024-07-09 起    影响：Registration.注册用户数           │  │
│         │ │ 📎 出处：etl/reg_activation.sql L42-58        [展开脚本片段▾]  │  │
│         │ │ 上次确认：无                                                  │  │
│         │ │                      [ ✓ 对，仍生效 ]  [ ✗ 不再生效 ]          │  │
│         │ └──────────────────────────────────────────────────────────────┘  │
│         │ ┌ ✅ R-009 注册渠道归属首次触点 —— 王工 2026-08-30 确认（点开详情）┐ │
│         │ ▼ Tab「关系」：以 User 为中心的小图谱（或简化列表，见开放问题5）     │  │
└─────────┴────────────────────────────────────────────────────────────────────┘
~~~

设计要点：① 待确认规则卡**置顶且高亮**，已确认折叠为摘要行（进度感，不被淹没）；② 确认按钮措辞是规则本身的是非题变体（"对，仍生效"），不是抽象的"通过/驳回"；③ 出处锚点默认折叠（原则⑥）；④ 头部状态汇总条让"这个对象可不可信"一眼可见。

### 2.3 Wireframe ②：待确认队列页（口径规则页的确认视图）

~~~
┌ 口径规则 · 待确认 (12) ────────────────────────────────────────────────┐
│ 筛选: [所属对象▾] [出处脚本▾] [进入队列时间▾]        已确认 today: 3 条 │
├───────────────────────────────────────────────────────────────────────┤
│ ⚠️ "激活边界 2024-07-09 仍生效？"                  R-012 · 排队 3 天    │
│    User 用户 › 注册 KPI      📎 etl/reg_activation.sql L42-58          │
│    影响: Registration.注册用户数            上次确认: 无（新规则）       │
│    [ ✓ 对 ]  [ ✗ 不对 ]  [ 先看完整卡片 → ]                            │
├───────────────────────────────────────────────────────────────────────┤
│ ⚠️ "渠道归属以首次触点为准？"                      R-015 · 排队 1 天    │
│    Channel 渠道 › 首触归因   📎 etl/attrib_v2.sql L10-40               │
│    [ ✓ 对 ]  [ ✗ 不对 ]  [ 先看完整卡片 → ]                            │
└───────────────────────────────────────────────────────────────────────┘
   点 [✓] → 不弹层，直接落库 → 行变绿收起 → toast「已记录：王工 2026-09-10 确认
   （版本 a1b2c3d）· 可在变更历史中查看」→ 计数 12→11
~~~

设计要点：① 每行是一个**完整的是非题**（不含上下文也能答），上下文用"先看完整卡片"承接——兼顾效率与严肃；② 确认即时反馈+可回溯（不设撤销弹窗，纠错=再点一次产生新记录，历史不删除）；③ 排队时长让积压可见（管理台自己也被"管理"）。

### 2.4 Wireframe ③：全局图谱页

~~~
┌ 全局图谱 ───────────────────────────────────────────────────────────────┐
│ ┌ 过滤 ─────┐ ┌ 画布 ────────────────────────────────┐ ┌ 详情抽屉 ──┐ │
│ │ 类型      │ │     [Channel 渠道]───[User 用户]      │ │ (点击节点   │ │
│ │ ☑ 对象    │ │    /          \      |  \            │ │  后滑出)    │ │
│ │ ☑ 事件    │ │ [Campaign]    [Registration]         │ │ 👤 User 用户 │ │
│ │ 业务域    │ │               /      \               │ │ 规则 5 ⚠️2  │ │
│ │ ☑ 客户    │ │        [Order]      [Activation]     │ │ 属性 8 · 绑定│ │
│ │ ☐ 交易    │ │                                      │ │ dw.dwd_user │ │
│ │ 高亮      │ │  节点=对象/事件（角标=待确认数）        │ │ [进入详情→] │ │
│ │ ☑ 未确认  │ │  边=链接（虚线红=关联未确认规则）       │ │            │ │
│ │ 着色:业务域│ │  [🔍定位] [⊕] [⊖] [⤢适应] [小地图]    │ │            │ │
│ └───────────┘ └──────────────────────────────────────┘ └────────────┘ │
│  布局: 力导向（d3-force）· 节点几十个量级，单击选中、抽屉里进详情        │
└─────────────────────────────────────────────────────────────────────────┘
~~~

设计要点：① 图谱的价值不是"好看"是"**找异常**"——默认高亮未确认规则关联的节点/边，让"哪里口径还没钉死"在图上一眼可见；② 点击节点=侧滑抽屉摘要（不打断），抽屉里"进入详情"才跳页；③ 搜索定位对象（图 + 列表双入口找同一批东西）。

### 2.5 追溯与 diff 呈现守则（全站一致）

1. **语义 diff 默认，原始 diff 折叠**：变更历史每条默认渲染为人话（"生效日期：2024-07-01 → 2024-07-09"），底部"查看原始变更"折叠 git diff——参考网易有数"变更标红+旧值删除线"的字段级呈现 [T1，上游调研 v0.1 块3]。
2. **确认记录不可变**：确认写 append-only 的确认记录（人/时间/commit），状态可再翻转但历史不覆盖——"谁在哪个版本上点了头"永远可查。
3. **每处状态徽章可点击**=跳到该规则的变更历史过滤视图（追溯不用找入口）。

---

## 3. 图谱组件选型

### 3.1 对比（一手数据 2026-09-10 GitHub/npm API 实查）

| 维度 | **React Flow** (@xyflow/react) | Cytoscape.js | AntV G6 | d3-force |
|---|---|---|---|---|
| 定位 | React 节点式 UI 库（节点=React 组件）| 图论分析 canvas 库 | 图可视化框架（AntV 系）| 力导向布局算法（单模块，非产品）|
| stars | **38,319** | 11,202 | 12,289 | 2,001 |
| 最近 push | 2026-09-09（最活跃）| 2026-09-09 | **2026-07-15（放缓）** | 2023-12-30（稳定冻结）|
| npm 周下载 | 7,945,941 | 14,670,550 | 228,047 | — |
| License | MIT | MIT | MIT | ISC |
| 自定义节点（中文标签/徽章/按钮）| **直接写 JSX，AntD 组件可嵌入节点** | canvas 绘制，自定义成本高 | 自定义 shape，v5 API 全新、资料尚少 | 全手写 |
| 点击节点出详情抽屉 | onNodeClick 原生支持，与 React 状态天然打通 | 支持，命令式事件需桥接 React | 支持 | 全手写 |
| 渲染 | SVG/HTML（几十节点无压力；千级以上弱于 canvas 系）| Canvas（大图强）| Canvas（大图强）| — |
| React 团队上手 | 约半天（官方 React 原生）| 2–3 天 + 命令式桥接层 | 2–3 天（中文文档最好）| 布局 1 天，交互/渲染全自研 |
| 主要风险 | 超大图性能（我们无此场景）| React 集成要写桥接层 | v5 迁移期、近期推进放缓（push 停在 2026-07-15，open issues 333）| 不是库是算法，等于自研画布 |

数据源：[T1] GitHub REST API（github.com/xyflow/xyflow、cytoscape/cytoscape.js、antvis/G6、d3/d3-force）与 npm downloads API（api.npmjs.org，区间 2026-08-31~09-06）实查；定性判断依据官方文档：reactflow.dev（custom nodes = React components）、docs.cytoscape.org、g6.antv.antgroup.com（中文官方站）。

### 3.2 结论：**React Flow（@xyflow/react）+ d3-force 布局，推荐**

理由（逐条对应我们的约束）：
1. **规模匹配**：几十个对象/事件远未到 canvas 系的性能主场，SVG 渲染 + 力导向完全够；28 张表、中文全称标签这种"节点内容重"的图，恰恰是 HTML/SVG 节点的强项。
2. **自定义节点=React 组件**：中文名称、业务域色块、待确认角标、点击选中态全是普通 JSX——这是"点击看详情"体验成本最低的路线；其余三家都要在非 React 的绘制层里复刻这套 UI。
3. **与现有栈同族**：chatbi 已是 React 18 + TS，图谱页不引入第二套心智；minimap/controls/background 开箱即用。
4. **维护最活跃**：38k stars、周下载 794 万、push 到 2026-09-09——四个候选中社区动能最强；MIT 无商用风险。
5. **退路清晰**：若发布期对象涨到几百+，图谱页做成独立模块（图谱组件+布局注入收敛在一处），届时换 Cytoscape/G6 只动一处——符合热插拔原则。

不推荐的首选理由一句话：Cytoscape（能力过剩、React 桥接成本）；G6（中文文档最好，但 v5 迁移期+推进放缓，作发布期备选）；d3-force（只是布局算法，配 React Flow 使用而非独立选型）。

---

## 4. 与 chatbi 前台的工程关系

**事实基线（一手实查 chatbi/package.json）**：React 18.3.1 + TypeScript 5.9 + Vite 7.1 + Vitest 4，src/ 下分 components/hooks/state/mock；**当前没有 AntD、没有路由库**——任务简报中"React+TS+Vite+AntD"的 AntD 与仓库实况不符（ADR-0009 的 ChatBI 壳可能未引入组件库），需 Jack 确认（开放问题 2）。

**建议：同仓不同入口（npm workspaces 单仓双应用），不建独立工程、不塞进 chatbi 单页。**

- 目录示意：chatbi/（现状不动）+ ontology-admin/（新增独立 Vite 入口、独立部署）+ packages/shared/（阶段二再抽：TS 类型 + API client + 主题 token）；后端同一 FastAPI 进程加 admin router。
- **为什么同仓**：同栈同团队；语义接口的 Pydantic schema 是唯一事实来源，管理台与 chatbi 的 TS 类型都应从它生成（openapi-typescript），分仓必漂移。
- **为什么不同页**：受众（数仓 vs 业务）、导航（管理台有侧栏结构 vs 问答流）、部署节奏（内部后台独立发版）都不同——塞进 chatbi 会互相拖累。
- **为什么管理台独立引 AntD 5**：表格（对象/规则列表）、表单（过滤/确认）、抽屉（图谱详情）是 AntD 主场；chatbi 不用组件库是它的选择，管理台不必跟随；两个应用各自打包互不影响。
- **后端关系**：同一 FastAPI 进程新增 admin router——只读端点读注册表 + 确认写端点走 git commit（上游调研 v0.1 已定）；不经过 chatbi 的任何链路。
- **若 Jack 不想动仓库结构**：最小方案 = 平级新目录 ontology-admin/ 独立 Vite 工程，阶段一不共享代码、仅靠 schema 生成类型对齐，发布期再收敛 monorepo（代价：短期类型/组件重复，可控）。

---

## 5. 给 Jack 拍板的开放问题（5 个）

1. **首页是谁**：工作台（待确认驱动，推荐——管理台的价值首先是"把待办顶到脸上"）vs 对象列表（目录心智，Palantir Explorer 的 orientation hub 更接近这个）vs 全局图谱（演示效果最好但日用价值最低）？推荐**工作台**，图谱保持二级。
2. **组件库口径**：管理台引入 AntD 5？（chatbi 实况无组件库，简报却写 AntD——以哪个为准？）推荐**管理台独立引 AntD**，chatbi 保持现状，记一条 ADR。
3. **确认权限模型**：MVP 全员（数仓组）可确认+落身份，还是业务/技术口径双负责人分设（网易有数模式），还是指定每条规则的 owner？推荐 **MVP 全员+身份记录**，双负责人留给发布期。
4. **确认交互强度**：队列页一键 [对/错] 直接落库（快，推荐）vs 必须展开完整卡片二次确认（严肃但摩擦大）？以及变更历史的**字段级语义 diff 是否进 MVP**（git diff 翻译层约 +1 天）？
5. **图谱页进不进 MVP**：React Flow 路线约 1–2 天可跑通，但中文标签/布局调优有长尾；不进 MVP 则对象详情页"关系"Tab 先用结构化列表（DataHub Related Terms 式）顶替。推荐**进 MVP 但裁剪**：只做"力导向+点击抽屉+未确认高亮"，不做缩放/小地图调优。

---

## 附录 A：检索与未找到清单（诚实声明）

- 检索预算：web_search 5 次共 14 query（协议上限 30）；深读：Palantir 官方文档 3 页（meta 摘要+目录树）、OpenMetadata/DataHub 官方文档 2 页全文、GitHub API 5 仓库、npm API 3 包。
- **未找到（不编造）**：
  1. Palantir Ontology Manager / Object Explorer 的**完整正文与界面截图**——文档站客户端渲染，SSR 抽取与 Jina 阅读器代理（超时）均失败；learn.palantir.com ONTOLOGY 01 课程页 403（上游调研已实证）。本文 Palantir 结论基于官方 meta 摘要 [T1]、文档目录树 [T1] 与上游对标调研已核实引文。
  2. Palantir 图谱视图（Graph view）的独立文档页——未检索到；本文图谱设计不依赖它。
  3. React Flow 官方对"节点数上限"的量化口径——未检索到明确数字，本文以"几十节点量级"定性表述并给退路（3.2-5）。
- 与任务简报的一处事实出入：chatbi 当前 package.json 无 AntD（第 4 节已说明，开放问题 2）。

## 附录 B：来源清单

| 事实 | 等级 | URL |
|---|---|---|
| Ontology Manager 定义（建设者应用）| T1 | https://palantir.com/docs/foundry/ontology-manager/overview/ |
| Object Explorer 首页 = orientation hub | T1 | https://palantir.com/docs/foundry/object-explorer/getting-started/ |
| proposal ≈ Pull Request（评审流）| T1 | https://palantir.com/docs/foundry/ontologies/review-ontology-proposals/ |
| Ontology building 文档目录树（浏览/治理 IA 分离）| T1 | 上述三页侧边栏实抓 |
| learn 课程 ONTOLOGY 01 存在（403 无法深读）| T1 | https://learn.palantir.com/understanding-and-exploring-your-ontology |
| OpenMetadata 术语字段（Owner/Reviewers/References 等）| T1 | https://docs.open-metadata.org/v1.13.x/how-to-guides/data-governance/glossary/create-terms |
| DataHub Glossary 结构（左树+Tab+删除二次确认）| T1 | https://docs.datahub.com/docs/glossary/business-glossary |
| 四个图谱库 stars/pushed/license | T1(API) | github.com/xyflow/xyflow 等（2026-09-10 实查）|
| 三个包 npm 周下载量 | T1(API) | api.npmjs.org（2026-08-31~09-06 区间）|
| React Flow 自定义节点=React 组件 | T1 | https://reactflow.dev/learn/customization/custom-nodes |
| G6 中文官方文档 | T1 | https://g6.antv.antgroup.com/ |
| Cytoscape 官方文档 | T1 | https://docs.cytoscape.org/ |
| 网易有数/腾讯 WeData 审批+diff 形态 | T1 | 见上游对标调研 v0.1 块3（本文不重复核实）|
| chatbi 技术栈实况（无 AntD）| 一手实查 | chatbi/package.json（本仓库）|
