# Palantir Ontology 调研报告：从概念到工程落地

> 调研日期：2026-08-14 ｜ 性质：面向"企业数据本体/语义层如何落地"项目的一手事实核查
> 方法：以 Palantir 官方文档（palantir.com/docs）为主，辅以 SEC S-1 招股书原文、Palantir 官方博客、以及第三方工程/财经分析（含中文批判视角）。所有关键论断均附来源 URL。
> 关键结论先行：**Palantir 的 Ontology 不是"设计期的静态数据模型"，而是一整套运行期系统**——它把"模型"做成了索引、查询、写回、安全、版本演进的运行时基础设施，并把"写回与行动治理"作为与传统数据建模/语义层最本质的分水岭。

---

## 0. 五个问题的 TL;DR

1. **Ontology 是什么**：Foundry 中位于数据资产（datasets / virtual tables / models）之上、连接"真实世界实体"的**运行期语义层**。核心构件：Object types、Properties、Link types、Action types、Functions、Interfaces、Object Views；背后是一组微服务（OMS、Object databases、OSS、Actions、Funnel、Functions on Objects）。
2. **与传统数据建模的本质区别**：Ontology 是"运行期语义层 + 行动执行层"，不是"设计期蓝图"。官方原话：Ontology 是 *operational layer*、*digital twin*，"不只是数据的模型，而是企业决策的模型"；它直接驱动应用、支持 Actions 写回真实系统、带运行期安全与版本演进（branching）。传统 LDM/语义层（含 Teradata FS-LDM、指标层）是**只读、设计期、无写回回路**的产物。
3. **数据打通**：pipeline → Foundry dataset/streaming datasource → Ontology Manager 中为 Object type 配置 **backing datasource** 并做列→Property 映射 → **Funnel** 服务增量索引进 Object Storage v2 → 用户通过 **Actions** 编辑（写回），编辑先落索引、再周期性持久化到 Funnel 管理的 dataset；还支持 materializations 把"含用户编辑的最新对象状态"导出回数据层。
4. **FDE（Forward Deployed Engineer）**：Palantir 派驻客户现场的工程师，是 Ontology 的实际构建者/落地者（与客户工程师一起，花数周至数月建模、写 ETL、做映射、调动作），并把现场经验回流到平台产品。官方将其定位为"部署+反哺"的工程方法论，而非咨询顾问。2025 年起又推出了把这一角色产品化的 **AI FDE**（对话式智能体）。
5. **方法论**：官方有非常具体、可执行的文档：*Ontology design: Best practices / Structural guidance / Anti-patterns*（四原则 + 八大反模式 + 命名规范 + 安全设计 + 性能取舍），以及 *Create an object type* 分步教程、*Delivering a use case* 交付方法论。第三方还有可运行的最小参考实现（GitHub: operational-ontology）。同时存在明显的营销话术层（"数字孪生/决策本体"叙事）与批判视角（"Ontology 就是表+存储过程换了个名字"）。

---

## 1. Palantir Foundry 里的 Ontology 到底是什么？核心构件与运行时作用

### 1.1 官方定义（一手）

**Ontology Overview（官方文档）**：

> "Ontology is an **operational layer** for the organization. The Ontology sits on top of the digital assets integrated into the Palantir platform (datasets, virtual tables, and models) and connects them to their real-world counterparts, ranging from physical assets like plants, equipment, and products to concepts like customer orders or financial transactions. In many settings, the Ontology serves as a **digital twin** of the organization, containing both the **semantic elements** (objects, properties, links) and **kinetic elements** (actions, functions, dynamic security) needed to enable use cases of all types."

来源：https://www.palantir.com/docs/foundry/ontology/overview/

同一页的关键论断：

> "Far beyond data cataloging or schema design solutions, the Ontology allows you to define a robust foundation for end-user workflows, including rich metadata for all fields and complete with granular security and governance for all changes."
> "Action types and functions：The kinetics of the organization—enabling change while complying with organizational controls and governance—are defined in the Ontology using action types and functions."

**Core concepts（官方文档）**给出构件级定义，并给出"数据集 ↔ Ontology"类比表：

> "An Ontology is a categorization of the world. In Foundry, the Ontology is the digital twin of an organization..."
> - **Object type**：the schema definition of a real-world entity or event.（类比：Dataset ↔ Object type；Row ↔ Object；Column ↔ Property；Field ↔ Property value；Join ↔ Link type）
> - **Property**：the schema definition of a characteristic of a real-world entity or event.
> - **Shared property**：可在多个 object types 上复用的 property，实现跨类型一致性建模与元数据集中管理。
> - **Link type**：the schema definition of a relationship between two object types；link 是关系的一个实例。
> - **Action type**：the schema definition of a set of changes or edits to objects, property values, and links that a user can take at once. It also includes the side effect behaviors that occur with action submission.
> - 另有 **Roles**（本体层权限模型）、**Functions**（可接收 object/object set 作为入参的代码逻辑）、**Interfaces**（对象类型多态）、**Object Views**（单个对象的统一信息中枢）。

来源：https://www.palantir.com/docs/foundry/ontology/core-concepts/

### 1.2 核心构件清单与运行时作用

| 构件 | 是什么（schema 定义） | 运行时作用 |
|---|---|---|
| **Object type** | 真实世界实体/事件的 schema | 每行数据成为一个"对象"；对象被索引进 object database，可被搜索、查询、聚合、被应用和 Agent 直接引用；有 **primary key**（唯一标识，编辑永久挂在主键上）与 **title key**（显示名） |
| **Property** | 实体的特征定义（有 base type：String/Integer/Date/Timestamp/Array/Struct/Geopoint/Media Reference/Time Series/Marking/Cipher 等） | 属性值来自 backing datasource 列映射；支持 derived property（查询期实时计算）与 edit-only property（只允许用户编辑） |
| **Link type** | 两个 object type 之间的关系定义 | 双向可遍历（两个 side，各有 API name）；支持 1:1/1:N/M:N（M:N 需要 join table）；支持 **object-backed link**（关系本身携带元数据）；链接关系驱动对象导航（如从"订单"直达"客户/产品"） |
| **Action type** | "一次可同时施加的一组对象/属性/链接变更"的定义 | 用户/Agent 提交 Action → Actions 服务校验（rules、parameters、submission criteria）→ 应用编辑到对象数据库索引 → 触发 side effects（通知、webhook、调度 pipeline build）→ 写入审计（action log） |
| **Function-backed action** | 当简单 rules 不足以描述变更时，Action 调用一个函数定义编辑逻辑 | 支持任意复杂度：跨多个链接对象批量改状态、按业务逻辑计算后写入、一次性创建多种对象并建链；受 action/function 执行上限约束 |
| **Functions** | 以对象/对象集为输入的代码逻辑（TypeScript/Python） | 在运行期被 Workshop、Actions、应用、Agent 调用；是"逻辑资产"接入 Ontology 的入口（含 model-backed functions 把 ML 模型接入） |
| **Interface** | 描述对象类型的"形状+能力"（属性/链接/动作集合） | 提供对象类型多态：工作流可以面向 interface 而非具体类型（如 Inspectable 被 Vehicle/Equipment/Facility 共同实现） |
| **Object Views / Object Explorer / Workshop** | 消费 Ontology 的用户侧应用 | 搜索对象、对象详情页、低代码应用构建——全部直接读 Ontology 运行时 |

来源：
- Object types：https://www.palantir.com/docs/foundry/object-link-types/object-types-overview/ ；创建/映射细节：https://www.palantir.com/docs/foundry/object-link-types/create-object-type/
- Properties：https://www.palantir.com/docs/foundry/object-link-types/properties-overview/
- Link types：https://www.palantir.com/docs/foundry/object-link-types/link-types-overview/
- Action types：https://www.palantir.com/docs/foundry/action-types/overview/
- Function-backed actions：https://www.palantir.com/docs/foundry/action-types/function-actions-overview/

### 1.3 背后的运行期服务（"模型是怎么跑起来的"）

官方 *Ontology architecture* 页明确：Ontology 后端由多个服务组成，承担三大功能——**datasource 管理与 schema 定义、对象的查询/搜索/聚合、写入编排（索引 + 用户编辑）**：

- **Ontology Metadata Service (OMS)**：定义"存在哪些本体实体"（object types、link types、action types 等的元数据）。
- **Object databases**：存储索引后的对象数据，提供快速查询；即 **Object Storage v1 (Phonograph，已计划废弃，2026-06-30 后不可用) / Object Storage v2（新一代规范存储）**。OSv2 特性：默认增量索引、单类型可支撑数百亿对象、单 Action 可编辑 10,000 对象、单类型最多 2000 个属性、支持 streaming datasource。
- **Object Set Service (OSS)**：读取入口，支撑搜索/过滤/聚合/加载；object set 分 static/dynamic、temporary/permanent。
- **Actions**：应用用户编辑的服务，提供结构化变更、权限与条件校验、历史 action log。
- **Object Data Funnel（"Funnel"）**：OSv2 中负责把 datasource 数据与 Actions 用户编辑编排写入 object databases 的微服务。
- **Functions on Objects**：在操作型场景中快速执行的代码逻辑。

来源：https://www.palantir.com/docs/foundry/object-backend/overview/
对象存储：https://www.palantir.com/docs/foundry/object-databases/object-storage-v1/ ；索引：https://www.palantir.com/docs/foundry/object-indexing/overview/

补充（IPO 招股书原话，2020 S-1）：Palantir 自述 ontology management 是"Create a data model that reflects the real world… objects, properties, and relationships that tie objects together"，并且**"the ontology is also translated into a programmatic model… used to generate a comprehensive domain-specific software development kit ('DS-SDK')"**——即本体直接生成 SDK，供客户开发 ontology-aware 应用。来源：https://www.sec.gov/Archives/edgar/data/1321655/000119312520230013/d904406ds1.htm

---

## 2. 与传统数据建模（Teradata FS-LDM / 逻辑数据模型 / 统一语义层）的本质区别

**结论先行：Palantir 的 Ontology 是"运行期语义层 + 行动执行层"；传统 LDM/语义层是"设计期蓝图 + 只读访问层"。** 差的不在"建模符号"，而在"模型有没有运行时、能不能写回、谁来治理决策"。

### 2.1 官方自己的论证：决策中心 vs 数据中心

*Why create an Ontology?*（官方）直接给出与"传统数据架构"的对比：

> "The Ontology represents **the decisions in an enterprise, not simply the data**. … Traditional data architectures do not capture the reasoning that goes into decision-making or the actions that follow, and therefore limit learning and the incorporation of AI. Conventional analytics architectures do not contextualize computation in lived reality, and remain disconnected from operations."
> "Closing the action loop as decisions are made in real-time is **what distinguishes an operational system from an analytical system**."
> 并把本体构件比作"名词与动词"："If the data elements in the Ontology are 'the nouns' of the enterprise (the semantic, real-world objects and links), then the actions can be considered 'the verbs' (the kinetic, real-world execution)."

来源：https://www.palantir.com/docs/foundry/ontology/why-ontology/

官方把"一次操作决策"拆成四要素：**Data / Logic / Action / Security**，Ontology 把它们整合进同一套可运行资源——这是传统建模工具完全没有的第四、第五维度（Action 与运行时 Security）。

来源：同上（why-ontology）。

### 2.2 数据层 vs 对象层（官方二分）

官方 *Introductory concepts* 明确定义平台内数据分两层：

> "…data in the platform living in two places: the **data layer** and the **object layer**."
> "In the data layer, data is stored inside **datasets**… Every dataset maintains a record of how it was produced… **data lineage**."
> "In the object layer, or Ontology, data is stored in **objects and links**… The object layer takes the data stored in tabular datasets—rows and columns of data—and converts it into a series of concise, representative objects…"

来源：https://www.palantir.com/docs/foundry/getting-started/introductory-concepts/

### 2.3 与"传统数据建模/语义层"的对比表（本报告整理）

| 维度 | 传统企业 LDM / Teradata FS-LDM | 传统"统一语义层/指标层"（LookML、dbt Semantic Layer、Cognos/MicroStrategy 语义层） | Palantir Foundry Ontology |
|---|---|---|---|
| 形态 | 设计期文档/模型（ER 图、3NF/维度模型）；FS-LDM 是金融业企业级逻辑模型蓝图（数千实体，Party/Agreement/Account/Product/Location/Event/Asset 等主题域），通过 CASE 工具/文档交付 | 设计期"度量/维度"定义 + 查询时翻译成 SQL；本质是**只读**的报表层 | **运行期系统**：对象被索引、可查询、可编辑、可被应用与 Agent 消费 |
| 是否有运行时 | 无——模型本身不执行 | 有部分运行时（查询翻译/缓存），但不持有状态 | 有完整运行时：对象数据库 + 查询服务 + 写回服务 + 版本管理 |
| 数据流向 | 单向：源 → 数仓 → 报表 | 单向：数仓 → 指标 → 报表/BI | **双向**：源 → 本体（读），本体 → 源系统（Actions writeback 写回） |
| 决策/行动 | 不建模决策，不产生"行动" | 不建模决策，只读 | 显式建模"行动"（Action types），带规则、审批、审计、side effects |
| 治理/安全 | 靠元数据/权限系统外围控制 | 行/列级权限，报表层 | 本体层原生的 marking/行级/列级/动态安全，随对象/链接/动作流转 |
| 演进 | 重设计、长周期、易腐化（业界共识：LDM 交付即过时） | 增量演进相对容易，但无版本化协作 | **Global Branching**：类 Git 的分支→提案→评审→合并，零停机演进；**Scenarios**：沙箱式"what-if"不污染生产 |
| 与 AI 的关系 | 无 | 可作为 RAG 上下文 | 对象/链接/动作直接作为 Agent 工具（tool）与上下文，受同一安全模型约束 |

### 2.4 第三方视角：把话说明白的两面

**支持面（第三方工程解释）**：Sherwood News 引用 Goldman 研报，把"Ontology vs 传统表/外键"讲得很直白：

> Goldman：Ontology 是 Palantir 的"core technical differentiation"，"bridges the gap between the raw data across an organization (structured, unstructured, siloed, etc.) and operational decision-making"。并举例：传统做法是 suppliers/shipments/warehouses/products 各自建表靠外键关联；ontology 则建模真实对象与关系——"if a shipment is delayed, all affected products, warehouses, and suppliers are automatically updated in the ontology"。

来源：https://sherwood.news/markets/what-the-heck-is-palantirs-ontology/

**批判面（中文工程博客 vonng）**——这个视角对你的项目最有"对抗性检验"价值：

> "Palantir's Ontology has four core concepts: Object Type, Property, Link, and Action… Look at this table: Category ↔ Table ↔ Class ↔ Object Type；Property ↔ Column ↔ Field ↔ Property；Relation ↔ Foreign Key ↔ Association ↔ Link；— ↔ Stored Procedure ↔ Method ↔ Action。**The same structure in different vocabularies. Highly overlapping and close to isomorphic in practical modeling terms.**"
> "Palantir's value isn't in the Ontology concept—it's in everything outside of it. It's in building GUIs for non-technical users. In spending months on-site understanding business processes…"
> 结论："Palantir invented nothing new"——但作者同时承认：*"Sure, a few lines of SQL can design a schema, but can it deliver an end-to-end platform that a supply chain manager can actually use? Of course not."*

来源：https://blog.vonng.com/en/db/ontology-bullshit/

**本报告对这场争论的裁决（供你项目使用）**：
- 建模符号层面（ER/LDM vs Object types/Properties/Links）确实高度同构——vonng 说对了一半；
- 但"同构"只覆盖**静态 schema**。Palantir 真正的新东西是：①把模型变成运行期可索引/可查询的服务；②Actions 提供了**受治理的写回回路**（write-back loop），这是传统 LDM/语义层完全没有的；③Funnel/OSS/OMS 一套后端把"模型"变成平台级运行时；④branching/scenarios 让本体像代码一样演进。**因此"设计期的静态模型 vs 运行期的语义层"这个二分是成立的，且是全部差异的根源**。
- 反方提醒同样成立：这些机制本身（索引、写回、权限）每个都不是新发明，Ontology 的价值在于**把它们与"模型"一体化**，而不是模型符号本身。你的项目如果只讲建模，会被一句"这不就是 CREATE TABLE"击穿；必须讲运行时与写回。

Teradata FS-LDM 官方材料（供对照）：http://www.teradata.com/t/assets/0/206/280/848ddfc1-fb1e-4484-80c0-5eb050724bb0.pdf （FS-LDM 是 3NF 风格的企业级金融逻辑数据模型，属设计期蓝图，无运行时/写回能力——此为业界共识性背景，报告中以 Palantir 官方对"传统数据架构"的批评作为对照依据。）

---

## 3. Ontology 与真实数据怎么打通？

### 3.1 读路径：pipeline → dataset → backing datasource → Funnel 索引 → Object Storage

官方流程（*Object indexing* / *Funnel batch pipelines*）：

1. 数据经 Code Repositories / Pipeline Builder / 连接器等产出 **Foundry datasets**（或 streaming datasource、restricted view、virtual table）。
2. 在 **Ontology Manager** 里创建 Object type，选择一个 **backing datasource**，把 datasource 的列逐个映射为 Property（官方警告：**"a single datasource can only be used to back one object type"**）；配置 **primary key**（必须唯一、必须确定性，否则编辑会丢失、链接会消失）与 **title key**。
3. **Funnel** 服务通过 **Funnel batch pipelines** 把数据索引进 Object Storage v2。管线四步：**Changelog**（计算增量 diff）→ **Merge changes**（把 datasource 变更与 Actions 用户编辑按主键合并）→ **Indexing**（转成对象数据库的索引文件）→ **Hydration**（把索引文件加载进查询节点，之后可被搜索/查询）。
4. 默认**增量索引**（只索引变更行）；当单次事务改动 >80% 行、或 schema 变更触发 replacement pipeline 时，才做全量重建。schema 变更时，live pipeline 继续服务，后台并行跑 replacement pipeline，完成后再切换——**零停机演进**。

来源：
- 创建与映射：https://www.palantir.com/docs/foundry/object-link-types/create-object-type/
- 索引总览：https://www.palantir.com/docs/foundry/object-indexing/overview/
- Funnel 批管线：https://www.palantir.com/docs/foundry/object-indexing/funnel-batch-pipelines/
- 低延迟写/编辑可用 direct datasources（官方一句定位："For low-latency writes and edits into the Ontology, you can also use direct datasources."）——同上索引总览页。

### 3.2 写路径：Actions → 索引即时生效 → 周期性持久化 → 冲突消解

官方 *How user edits are applied*（写回机制最细的一手材料）：

> "When an Action is applied to an object, link, or object set, the data-modification logic is **immediately applied to the index in the object databases** and periodically flushed into a persistent store in the form of Foundry datasets owned and managed by Funnel."

- 即时性：Actions 服务把修改指令发到 Funnel 管理的队列（带 offset 跟踪），**立即应用到对象数据库的 live 索引**——编辑之后发生的查询保证读到编辑结果。
- 持久化：Funnel 的 merged dataset 会**每 6 小时**（或每次 datasource 有新事务时）自动构建，把用户编辑从队列落盘成 Foundry dataset，防止队列膨胀。
- **冲突消解**（datasource 更新 vs 用户编辑）：对象类型级可配两种策略——**Strategy 1: Apply user edits（默认，用户编辑永远赢）**；**Strategy 2: Apply most recent value（按时间戳比较，编辑时间新于 datasource 时间戳才生效）**。官方给出逐时间步的完整示例表（T0–T10），包括"行删除后重现，之前的编辑仍保留"等边界行为。
- **edit-only property**：只允许用户编辑、datasource 永远覆盖不了的属性。
- 删除不是"编辑"：删除后对象从本体消失；同主键行重新出现时，若用户编辑过则编辑仍然生效（策略 1 下）。
- **版本一致性**：Actions 执行期间做对象版本检查（OSv1 全量检查，OSv2 只检查直接参与编辑生成的对象），避免把 Action 作用到过期版本。

来源：https://www.palantir.com/docs/foundry/object-edits/how-edits-applied/

### 3.3 写回闭环的另一半：writeback / materialized datasets

- OSv1（Phonograph）时代：用户编辑需要 **writeback dataset** 承载；官方定义："The most up-to-date version of object data with user edits incorporated will be captured in an object type's **writeback dataset**."（https://www.palantir.com/docs/foundry/action-types/overview/ ）
- OSv2 时代：**materializations** 取代 writeback dataset——把"对象的最新状态（含用户编辑）"物化回 dataset，供下游 pipeline 与批量下载使用；支持"用户编辑自动传播（几分钟延迟）"或"周期性构建（6 小时）"两种模式；物化数据集 schema 取自 Ontology 定义的 API names（而非原 datasource schema）；含 __is_deleted、__patch_offset 等 Funnel 元数据列（仅供去重，不可用于生产逻辑）。
- 跨系统写回：Actions 的 side effect 可触发 **webhook / API 调用 / 调度 pipeline build**，把变更推到外部系统（ERP/WMS 等）。官方 why-ontology 的 Onyx 案例里明确演示：同一决策同时走"WMS 收 API 更新、三个 ERP 收原生连接器更新、生产计划系统收扁平文件"。

来源：
- 物化：https://www.palantir.com/docs/foundry/object-edits/materializations/
- 编辑总览：https://www.palantir.com/docs/foundry/object-edits/overview/
- 对象存储 v1（Phonograph，计划废弃）：https://www.palantir.com/docs/foundry/object-databases/object-storage-v1/

### 3.4 状态归属（第三方参考实现的精炼模型）

GitHub 上 *operational-ontology*（Foundry Ontology 模式的最小可运行参考实现）把"状态所有权"分成三类，非常利于落地讲解：

- **source-backed**：状态由上游系统主控（如订单状态归 ERP）；本体内变更需受治理地写回源系统，源系统保持权威。
- **ontology-owned**：源系统里根本没有的列（如"指派给谁""处置备注"），本体自己的存储就是系统记录。
- **derived**：计算态（聚合/计数），永不写。

来源：https://github.com/gura105/operational-ontology （配套文章：https://dev.to/gura105/operational-ontology-the-pattern-behind-palantir-foundrys-ontology-44m8 ）

### 3.5 沙箱与演进：Scenarios / Global Branching

- **Ontology scenarios**（Beta）："a sandbox to apply edits on top of the data in your Ontology, generated by applying one or more actions"——用于 what-if 分析、业务逻辑模拟、Agent 评估；默认 30 天 TTL，每 10 分钟自动 rebase 到主分支。来源：https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario/
- **Branching the ontology**：与 Global Branching 集成，支持在分支上开发本体资源（object/action/link/interface/shared property 类型），受保护资源必须走"分支→提案→评审→合并"；支持 rebase 与冲突解决。来源：https://www.palantir.com/docs/foundry/ontologies/branching-ontology/

---

## 4. Forward Deployed Engineer（FDE）是什么？与 Ontology 什么关系？

### 4.1 官方定义（一手）

**S-1 招股书（2020）**：

> "Our forward deployed engineers ("FDEs") have travelled to bases in Afghanistan and factories in the industrial Midwest to deploy our platforms. **Time in the field adds to the continuous improvement of our platforms. As FDEs help customers make the most of our software, they observe users' challenges firsthand.**"

来源：https://www.sec.gov/Archives/edgar/data/1321655/000119312520230013/d904406ds1.htm

官方博客（Palantir 内部对工程角色的权威分层）：
- **"Dev versus Delta: Demystifying engineering roles at Palantir"**（blog.palantir.com）——Palantir 把工程角色分为 **Dev（核心平台工程师）** 与 **Delta（派驻现场的 FDE）** 两条线；Delta 的使命是"把平台部署到客户的真实问题上"。https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87
- **"A day in the life of a Palantir Forward Deployed Software Engineer"**——现场工作日常：理解业务、写 ETL/模型、与客户一起构建。https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1
- 官方社区讨论（FDE 是谁、做什么）：https://community.palantir.com/t/who-are-palantir-fdes/6847

> 注：上述两篇 Medium 博客正文因 Cloudflare 拦截无法全文抓取，此处引用其标题与官方定位；内容要点由第三方转述交叉验证（见 4.2/4.3）。

### 4.2 FDE 到底做什么（第三方工程解读）

- **"Delta + Echo" 双人小组**：Delta（FDE，写代码：Python ETL、ontology 模型等）+ Echo（deployment strategist，管客户关系与工作流落地）。
- **FDE 写生产级代码，但在客户现场工作**："FDEs write production-grade code but work inside a customer instead of a corporate lab"；2016 年前后 Palantir 的 FDE 数量已超过"普通产品工程师"。
- **"Field-Driven Productization"**：FDE 在现场实验、把共性反馈回核心工程团队，平台据此迭代——这是 FDE 模式与普通咨询的本质区别（不是交付一单就走，而是长期驻场并反哺产品）。

来源：https://cloud-authority.com/the-rise-of-the-forward-deployed-engineer-history-myths-and-why-it-s-back.md

- 财经媒体 Sherwood News 明确把 **FDE 与 Ontology 的构建绑定**：

> "…it can take a significant investment of a company's time to create that foundation [the ontology], **which is typically done by engineers employed by both Palantir — what they call 'forward deployed engineers,' or FDEs — and the corporation itself. It can take weeks and even months.**"

来源：https://sherwood.news/markets/what-the-heck-is-palantirs-ontology/

### 4.3 批判视角（对你有用）

- vonng：FDE 的现场工作本质是"数据集成 + 胶水代码"（把 SAP 数据搬进 Foundry、调 Kafka connector、处理 Oracle/Snowflake schema 不兼容、给业务解释 Link 为什么改）——"the most labor-intensive, context-dependent part of enterprise software engineering"。并指出 Palantir 把 FDE 人力成本计入 R&D/S&M 而非 COGS（Michael Burry 做空报告也抓这一点），商业模式是"重服务层"。
- 也就是说：**Ontology 的构建本身就是 FDE 的核心交付物**；ontology 建模的复杂度和专有 GUI 抬高了客户的切换成本，也抬高了 FDE 的不可替代性——"越难用，客户越离不开 FDE"。

来源：https://blog.vonng.com/en/db/ontology-bullshit/

### 4.4 2025 新动向：AI FDE（把 FDE 产品化）

官方文档已上线 **AI FDE**：

> "**AI FDE**, the AI-powered forward deployed engineer, is an interactive agent that operates Foundry for you through conversational commands. AI FDE translates natural language requests into Foundry operations, allowing you to perform data transformations, manage code repositories, **build and maintain your ontology**, and more."

机制：分析意图 → 选定 Foundry 操作 → 用原生工具执行 → 返回解释；闭环运行（执行→观察→下一步）；推荐启用 Global Branching 以支持 AI FDE 编辑本体。**这说明"构建/维护 Ontology"已成为被 AI 自动化的工作**，对"本体论落地方法论"项目是极强的信号。

来源：https://www.palantir.com/docs/foundry/ai-fde/overview

---

## 5. 公开的 Ontology 构建方法论：哪些是干货，哪些是营销

### 5.1 实操干货（可执行、有具体规则）

**A. Ontology design: Best practices（官方，四原则，按优先级排序）**
1. **Domain-driven design**——"The Ontology models the real world, not the source data." 对象必须是领域概念（Patient/WorkOrder/Vessel），不是表/API/电子表格页；"resist the urge to map columns 1:1 to properties"；先识别实体再看源 schema；命名面向人（person.children 而非 person.linkedChildPersonObjects）。
2. **Don't repeat yourself（rule of three）**——同一个东西建了三次就重构；单一规范类型 + 单一规范工作流。
3. **Open for extension, closed for modification**——核心模型稳定，扩展走新链接类型/新 interface 实现/新属性命名空间（示例：Equipment 加认证信息时新建 Equipment Certification 链接类型，而不是往 Equipment 上堆 4 个可空属性）。
4. **Composition over deep hierarchies**——用 interface 做多继承（示例：Arena implements Building + SchedulableResource，而非 Asset→Building→SchedulableBuilding→Arena 深链）。
外加"**Pragmatism and tradeoffs**"：原则是指导不是法律；先可用后完美；**命名质量、语义清晰、安全设计是后期难修的，其他都可以先砍**。

来源：https://www.palantir.com/docs/foundry/ontology/ontology-best-practices/

**B. Ontology design: Structural guidance（官方，结构级细则）**
- 归一化与 derived properties："Store each fact once. Use derived properties for convenience."——区分"pre-computed（pipeline 里算）"与"dynamically derived（依赖链接/动作变化的查询期计算）"；给出性能阈值建议（每查询 <~10k 对象用 derived property 自由；更高要考虑有记录的 denormalization）。
- Structs：多字段概念（地址）用 struct 而非 10 个平铺属性；struct 可带元数据（置信度、来源、推理过程）——特别适合 AI 输出。
- Interfaces：能力型（Inspectable/Schedulable/Billable）与分类型（MilitaryAsset）接口；工作流面向接口；"Scaffold now, consolidate later"。
- Links vs object-backed links：关系本身带元数据（role/startDate/allocation）就用 object-backed link；"avoid links that exist only because two datasets share a foreign key"。
- 命名规范表：对象类型用单数具体名词；属性名自解释（lastInspectionDate 而非 dtLastInspMod）；链接双向命名（department / employees）。
- 安全设计："Design security semantically… principle of least privilege"；行级+列级组合出单元级（cell-level）权限；**禁止为做安全而拆对象类型**（PublicPatient/RestrictedPatient 是反例，应一个 Patient 类型 + 列级/行级策略）；"Start restrictive, open up deliberately"。

来源：https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance/

**C. Ontology design: Anti-patterns（官方，八大反模式，每个都带"症状→成因→危害→解决方案→示例"）**
1. **System Silos**：按源系统建对象类型（HR Employee / Badge Employee / PM Employee）→ 应合并成单一 Employee + pipeline 合并数据集，定义主键与冲突优先级。
2. **The Kitchen Sink**：把 ETL 技术列（_crm_extracted_at、last_etl_update_timestamp）当属性 → 只保留有业务含义的列，技术元数据留在 backing dataset 不进本体。
3. **Department Silos**：销售/客服/财务各建各的 Customer → 共享对象类型 + 部门专属属性/链接 + 受限视图。
4. **The God Object**：一个 Asset 装下设备/软件许可/房产/金融工具/员工（150+ 属性大量为 null）→ 拆成不同对象类型 + interface 表达共性。
5. **The Golden Hammer**：把本该 pipeline/automation/function 干的事全做成 Action（如"Calculate Regional Sales"手动触发）→ 给出"工具选择矩阵"：Action 用于人类决策，pipeline 用于批量变换，automation 用于事件驱动，function 用于实时复杂计算。
6. **Action Sprawl**：20 个单属性 Action（Update First Name / Update Last Name…）→ 按业务操作聚合（Transfer Employee / Onboard New Employee / Approve Purchase Order）。
7. **The Time Machine**：把历史版本建成多个对象/对象类型（Contract v1/v2/v3、Contract 2023/2024/2025）→ 一个对象 + 链接的历史/修订对象类型 + 时间序列属性。
8. **The Misnomer**：Item/value/type/date 这类模糊命名 → 具体命名 + 自解释链接名 + 全元素描述。

来源：https://www.palantir.com/docs/foundry/ontology/ontology-anti-patterns/

**D. 分步落地教程（官方）**
- *Create an object type*：引导式向导（选 backing datasource → 元数据 → 属性映射 → 主键/标题键 → 生成 actions → 保存位置 → Save）；含手动流程、API 命名规则、主键唯一性/确定性要求、常见报错（如 Phonograph2:DatasetAndBranchAlreadyRegistered，同一 datasource 不能背两个对象类型）。来源：https://www.palantir.com/docs/foundry/object-link-types/create-object-type/
- *Delivering a use case*：方法论定义——"A use case is a time-bound effort by a dedicated team to support a specific decision-making process"；先谈 outcome 再谈工具（"instead of starting with a need to build a sales dashboard, seek to understand what decisions and outcomes your work might enable"）。来源：https://www.palantir.com/docs/foundry/getting-started/delivering-a-use-case/
- 官方还提供 **seed ontologies**（S-1 原话："often starting from seed ontologies that we provide to give customers a running start"，如疫情疾病追踪本体）；以及 AIP Developer Tier / AIP Bootcamp 供动手试。来源：https://www.palantir.com/docs/foundry/getting-started/overview/

**E. 第三方可运行参考实现（最"可落地"的外部材料）**
- GitHub *operational-ontology*：用几十行 SQL + TypeScript 实现 Foundry Ontology 模式的最小参考实现，演示完整闭环——两个异构遗留订单系统的数据整合 → 建模 Customer/Order/Product（+源系统不存在的 Note 类型）→ 链接遍历 → assignOrder 写本体自有状态 → cancelOrder 拒绝已发货订单（返回 SHIPPED_ORDER_CANNOT_BE_CANCELLED）→ 成功取消且 ERP 行真的被改 → 重新索引后本体自有状态保留 → 全程审计日志。
- 该仓库给出**模式四属性**（判定标准）：①语义对象与链接；②**Action 门控写入**（"no generic update path"）；③业务规则放在 Action（前置条件拒绝违反域不变量的写入，且"不是访问控制、不是 UI 校验"）；④**写回系统记录**（每种状态声明归属：source-backed / ontology-owned / derived）。
- 还有一句被广泛引用的判断标准："**A semantic layer lets you read your business. An operational ontology lets you run it.**" 以及三问测试："Can you cancel an order from your semantic layer?"——答"不能"= 只读层；答"能但任何系统记录都没变"= 平行数据库；答"能且已发货订单也被取消"= 只是写 API（缺第 3 属性）。

来源：https://github.com/gura105/operational-ontology ；配套文章：https://dev.to/gura105/operational-ontology-the-pattern-behind-palantir-foundrys-ontology-44m8

### 5.2 营销概念层（要区分开）

- *Why create an Ontology?* 整页是**决策中心叙事**（"The Ontology represents the decisions in an enterprise, not simply the data"、Data/Logic/Action/Security 四要素、数字孪生、human-agent 协同）——方向正确但难以直接执行，属于"为什么"而非"怎么做"。
- "Ontology 是 2,300 年哲学词汇的认知税"（vonng）：对非技术决策者极有效，对工程师是信息不对称；你的项目如果沿用这套叙事而没有可复现机制，会被工程师群体质疑。
- 财经媒体的"核心差异化"表述（Goldman/Sankar"our advantage comes down to Ontology"）服务于估值叙事，具体机制需回到官方文档核实（本报告已核实）。

---

## 6. 对本项目最有价值的 3 个洞察（差异化建议）

**洞察 1：把"设计期模型 vs 运行期语义层"作为主线论题，但用"机制清单"而不是"口号"来论证。**
Palantir 与 Teradata FS-LDM / 企业 LDM / 指标层的最本质差异，不是建模符号（ER vs Object types 高度同构），而是 Ontology 有完整运行时：OMS（元数据服务）、Funnel（增量索引管线）、OSS（查询）、Object databases（OSv2 存储）、Actions（写回）、branching/scenarios（演进）。落地方法论应回答"模型交付后由哪些运行时组件承载、如何承载"，并给出每个机制的工程事实（如 Funnel 的 Changelog→Merge→Index→Hydration 四步、增量索引与 80% 全量重建阈值、6 小时持久化节奏）。这直接回应 vonng 式批判（"不就是 CREATE TABLE"）——**同构的是 schema，不同构的是运行时与写回回路**。

**洞察 2：把"行动门控的写回回路"（Action-gated write-back loop）做成方法论的核心差异点与验收标准。**
这是传统语义层（只读）与 Palantir 式本体（可运行）的分水岭，且有现成的可执行判据：operational-ontology 的"四属性 + 三问测试"（"能从语义层取消订单吗？源系统记录真的变了吗？已发货订单会被拦吗？"）。落地项目可以给出：状态所有权三分类（source-backed / ontology-owned / derived）、冲突消解策略（用户编辑优先 vs 时间戳优先，Palantir 两种都有）、审计与规则前置校验（submission criteria）。把"读语义层"升级为"运行语义层"，这是与所有语义层/指标层产品对话时的最强差异点。

**洞察 3：把"本体如何演进"（branching/scenarios/迁移）作为被所有人忽视的第二战场，并回应 AI 时代的自动化信号。**
传统 LDM 最大的失败模式是"模型交付即过时"（vonng 引用的 Donald Farmer 案例：本体没建完业务已经变了，且"错误的本体比没有本体更危险"）。Palantir 的应对是工程化的演进机制：Global Branching（分支→提案→评审→合并、资源保护、零停机 schema 变更）、Scenarios（30 天沙箱、自动 rebase）、主键确定性要求（防编辑丢失）、OSv1→OSv2 迁移框架。你的方法论若把"本体生命周期管理"（设计→运行→演进→治理）讲成主线，就避开了市面上所有"教你建模"内容的同质化；同时把 **AI FDE**（对话式构建/维护本体）作为"下一阶段本体由 Agent 构建"的前瞻信号写进路线图，形成"人机共建本体"的差异化叙事。

---

## 7. 来源清单

### 官方一手（文档/招股书）
1. Ontology Overview：https://www.palantir.com/docs/foundry/ontology/overview/
2. Why create an Ontology?：https://www.palantir.com/docs/foundry/ontology/why-ontology/
3. Ontology Core concepts：https://www.palantir.com/docs/foundry/ontology/core-concepts/
4. Ontology architecture（后端服务）：https://www.palantir.com/docs/foundry/object-backend/overview/
5. Create an object type（映射/主键/API 名）：https://www.palantir.com/docs/foundry/object-link-types/create-object-type/
6. Properties overview：https://www.palantir.com/docs/foundry/object-link-types/properties-overview/
7. Link types overview：https://www.palantir.com/docs/foundry/object-link-types/link-types-overview/
8. Action types overview：https://www.palantir.com/docs/foundry/action-types/overview/
9. Function-backed actions：https://www.palantir.com/docs/foundry/action-types/function-actions-overview/
10. Indexing overview：https://www.palantir.com/docs/foundry/object-indexing/overview/
11. Funnel batch pipelines：https://www.palantir.com/docs/foundry/object-indexing/funnel-batch-pipelines/
12. How user edits are applied（写回/冲突消解）：https://www.palantir.com/docs/foundry/object-edits/how-edits-applied/
13. Materializations（writeback→物化）：https://www.palantir.com/docs/foundry/object-edits/materializations/
14. Object edits overview：https://www.palantir.com/docs/foundry/object-edits/overview/
15. Object Storage v1 (Phonograph)：https://www.palantir.com/docs/foundry/object-databases/object-storage-v1/
16. Branching the ontology：https://www.palantir.com/docs/foundry/ontologies/branching-ontology/
17. Ontology scenarios：https://www.palantir.com/docs/foundry/ontology/overview-ontology-scenario/
18. Introductory concepts（数据层 vs 对象层）：https://www.palantir.com/docs/foundry/getting-started/introductory-concepts/
19. Delivering a use case（交付方法论）：https://www.palantir.com/docs/foundry/getting-started/delivering-a-use-case/
20. **Ontology design: Best practices**：https://www.palantir.com/docs/foundry/ontology/ontology-best-practices/
21. **Ontology design: Structural guidance**：https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance/
22. **Ontology design: Anti-patterns**：https://www.palantir.com/docs/foundry/ontology/ontology-anti-patterns/
23. AI FDE（官方文档）：https://www.palantir.com/docs/foundry/ai-fde/overview
24. Palantir S-1（2020-08-25，ontology management / DS-SDK / FDE 段落）：https://www.sec.gov/Archives/edgar/data/1321655/000119312520230013/d904406ds1.htm
25. 官方博客 Dev versus Delta（FDE vs Dev 角色）：https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87
26. 官方博客 A day in the life of a Palantir FDSE：https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1
27. Palantir 官方社区：FDE 是谁：https://community.palantir.com/t/who-are-palantir-fdes/6847

### 权威第三方
28. Sherwood News（含 Goldman 研报转述、Sankar 原话、FDE 与 ontology 绑定）：https://sherwood.news/markets/what-the-heck-is-palantirs-ontology/
29. vonng（中文批判视角"ontology-bullshit"）：https://blog.vonng.com/en/db/ontology-bullshit/
30. operational-ontology（可运行最小参考实现 + 四属性 + 三问测试）：https://github.com/gura105/operational-ontology ；配套文章：https://dev.to/gura105/operational-ontology-the-pattern-behind-palantir-foundrys-ontology-44m8
31. Cloud Authority（FDE 历史/Delta-Echo/Field-Driven Productization）：https://cloud-authority.com/the-rise-of-the-forward-deployed-engineer-history-myths-and-why-it-s-back.md
32. Teradata FS-LDM 官方 PDF（对照材料）：http://www.teradata.com/t/assets/0/206/280/848ddfc1-fb1e-4484-80c0-5eb050724bb0.pdf

### 调研方法备注
- 所有 Palantir 官方文档内容均为 2026-08-14 从 palantir.com/docs 直接抓取核对的正文（非转述）；官方博客（Medium 托管）正文被 Cloudflare 拦截，仅引用标题与官方定位，要点经第三方转述交叉验证。
- 本报告引用的 S-1 原文来自 SEC EDGAR 原始文件抓取。
