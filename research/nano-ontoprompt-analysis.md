# nano-ontoprompt 代码研究报告

> 调研日期：2026-08-18 ｜ 调研方式：GitHub API 全量文件树 + 关键源码精读（git clone 协议网络不稳，未走本地克隆）
> 研究对象：https://github.com/jingw2/nano-ontoprompt（已 fork 到 suyukun/nano-ontoprompt，master）
> 结论先行：**这是"本体构建/管理平台"，不是"语义接口运行时"**——它把原始数据经管道变成本体+知识图谱并做质量审查；动作执行只作用于平台内部的本体图数据，**"写回外部系统"停留在设计文档与动作模板，引擎无实现**。与 OntoRun 研究对象（LLM 经语义接口写回真实源系统）不撞车，反而互补，且有多处可直接借鉴的工程手法。

---

## 1. 项目画像

| 维度 | 事实 |
|---|---|
| 定位 | 轻量级、借鉴 Palantir Foundry 设计的**领域本体构建平台**（Ontology-as-a-Service 单项目多租户形态） |
| 作者 | B站 UP主「零点未来」（jingw2）——见 research/palantir-bilibili-notes.md |
| 活跃度 | 2026-05-17 创建，2026-08-18 仍在推送；**405 stars / 143 forks** |
| 语言 | 全栈：FastAPI (Python) + React/TS 前端 |
| 测试 | 300+ pytest（含 v2 供应链 golden 测试、E2E 增量流程测试） |
| 许可证 | MIT |

## 2. 技术栈（backend/requirements.txt + frontend/package.json 实测）

- 后端：FastAPI 0.115 / SQLAlchemy 2.0 / Alembic / pydantic 2.9 / Celery+Redis / slowapi（限流）
- 存储：元库 SQLite(dev)/PostgreSQL(prod)；**Neo4j(图) / ChromaDB(向量) / MinIO(对象) / Redis 全部可选，缺失时优雅回退**（SQLite 图谱 / 本地文件 / 同步执行）
- LLM：openai / anthropic SDK + **LiteLLM 代理（统一多 provider key 与用量）**；markitdown(文档转MD)、rdflib(导出RDF)、duckdb(本地分析)
- 前端：React ^19.2.6（README 写 18，package.json 实测 19）/ Vite / Tailwind / Cytoscape.js(知识图谱) / @xyflow/react(管道画布) / zustand / react-query / i18next(中英)

## 3. 架构与功能（两条构建路径）

### 3.1 路径 A：Pipeline Mapping（v2，主推）
完整数据集成链路：**数据接入 → 原始存储 → 转换 → Curated 数据集 → 本体映射**
- 连接器：文件上传 / MySQL、PostgreSQL / MongoDB / REST API（支持增量同步）
- 三条转换路径：A 结构化(CSV/Excel schema推断+清洗)、B 半结构化(JSON拍平/XML解析)、C 非结构化(文档→Markdown→LLM或规则结构化)
- Curated 数据集：质量评分、人工审核（仅管理员审批）、版本管理
- 自动映射：数据集→实体类型、列→属性、外键→关系、自动推断基数
- 跨数据集关系推断：精确外键匹配 + **值格式容错**(SUP-001↔SUP001) + 备用键匹配(文档公司名→Supplier) + 可选 LLM 语义链接
- Logic & Actions 自动发现：从映射/schema约束/状态字段/关系生成，**草稿→审核→发布**流程上线

### 3.2 路径 B：简易 LLM 提取（v1）
上传文档 → 选提示词+模型 → 一键提取知识图谱（实体/关系/逻辑规则/动作），输出经 PostHarnessValidator 多层校验后落库。

### 3.3 平台功能
- 知识图谱：Cytoscape.js 交互式网状视图，一键隐藏孤立节点；Neo4j 或 SQLite 回退
- 搜索：关键词(SQL) / 语义搜索(ChromaDB)，均带回退
- **LLM 驱动质量审查（ReAct Agent）**：8 个内置检查工具（摘要/覆盖率/引用校验/模式推断）链式调用，产出分级审查报告，持久化为审计任务
- 导出：JSON / YAML / CSV / **Turtle (RDF)** / HTML
- 用户管理：JWT，admin/editor 角色；Curated 审批仅限管理员
- 多语言界面（中英）

## 4. 关键机制深挖（源码精读）

### 4.1 动作执行（routers/v2/logic_actions.py，最相关）
POST /{ontology_id}/actions/{action_id}/run 完整链路：
1. **前置门控**：action 必须 enabled + status==published 才能运行期执行
2. **提交校验** _validate_action_submission：missing_parameter / required_target / entity_exists / field_equals / required_param 五类 criteria
3. **审计执行记录** OntologyActionRun：status(running→completed/failed)、**before_snapshot / after_snapshot**、side_effect_results、executed_by、error
4. **effects 引擎**：仅支持四类图内变更——set_property(实体属性)、create_object、merge_relationship、delete_relationship
5. 失败回滚 + 错误入审计

> 核心发现：effects 全部作用于**平台内部 Entity/Relation 图数据**。"Writeback: 外部写回"在 discover_actions 里只是**声明式动作模板**（confidence 0.7），run 引擎里没有对应实现分支（else 分支直接 skipped）。

### 4.2 写回能力核验（设计 vs 实现）
- 设计文档 ONTOLOGY.md（2728 行）**确有写回架构**：§17 S4 病历草稿工作流写了 encounter.archiveDraft() 的 **HIS 写回路径**、§6 有 Function 完整写路径、§7 Governance ConfirmLevel/执行流/Validate 分层。
- 但代码搜索证实：archiveDraft **仅存在于 ONTOLOGY.md**；writeback 命中 4 处 = 动作模板(logic_actions.py) + 映射服务 + 前端向导标签 + 测试文件，**无外部系统写回的引擎实现**。
- **判断**：它的写回是"设计蓝图 + 声明模板"，未成为可验证的运行闭环。这正是 OntoRun 的差异化核心。

### 4.3 PostHarnessValidator（engine/post_harness/validator.py）——LLM 输出质量校验
- 四级严重度（fatal/error/warning/info）+ 分类报告（by_severity/has_fatal/has_errors）
- 七道检查：结构 / 必填字段 / **引用完整性**(source/target 指向存在的实体) / **去重**(按 (name_cn,type) 与 (source,type,target) 就地去重) / **类型白名单**(DEFAULT_ALLOWED_TYPES 覆盖供应链+医疗+财务+法律+教育域，>50% 自定义类型告警) / **Python 语法校验**(ast.parse function_code) / 语义引用校验(linked_entities/linked_logic_names)
- 意义：这是"LLM 输出视为不可信输入、入库前多重闸门"的工程化范本，与我们的安全纪律同构。

### 4.4 自动映射与关系推断（services/v2/mapping/，mapping_service.py 79KB 核心）
- 外键检测 / 值格式容错 / 备用键匹配（alt-key links）/ 可选 LLM 语义链接（ENABLE_LLM_FK_DETECTION）
- **宽表拆分**（wide_table_split.py）：与 B 站笔记 EP04"一个 Object Type 只对应一张表"一致，Palantir 硬规则落地
- 增量更新：orchestrator + 同步→处理→索引三层配合（与笔记 EP04 完全对应）

### 4.5 优雅降级（平台级设计哲学）
Neo4j / MinIO / ChromaDB / Redis / Celery 全可选，缺失自动回退 SQLite + 本地存储 + 同步执行。与我们"本地可跑可演示"的约束完全同向。

### 4.6 ONTOLOGY.md 设计文档（2728 行）值得读的章节
- §6 Function/Action 系统：定义与实现分离、命名规范、**Composite Function（合并意图）**、**Observation Function（对话提取型）**
- §7 Governance：ConfirmLevel 枚举、执行流、Validate 分层、BuildSummary
- §9 Event Bus：事件设计、订阅者职责
- §12 测试策略：**用内存 Fake 替代 DB**、必测场景清单
- §13 六个常见陷阱：Object Store 当权威源用 / Function 粒度太细 / 事件订阅者里写图边 / FunctionResult 返回裸 ID 等
- §15-18 扩展场景：临床筛查（双图 patient_graph vs clinical_kb）、S1 多模态采集状态机、S4 病历草稿（含 HIS 写回设计）、Actor 体系与租户隔离（7 类角色+authorizeFunction）

## 5. 与 OntoRun 对比

| 维度 | nano-ontoprompt | OntoRun（我们的研究对象） |
|---|---|---|
| 本质 | **本体构建/管理平台**（data→ontology→KG） | **语义接口运行时**（LLM→语义接口→动作→写回源系统） |
| 数据 | 自带元库+图谱，本体数据活在平台内 | 独立"源系统"库 + 写回库（双库补偿式） |
| 动作 | 图内 CRUD/状态流转/链接维护，提交校验+快照审计 | 动作门控写回**源系统**，源记录真变、规则拦截、全链路审计（三问测试） |
| LLM 角色 | ①提取本体 ②质量审查 Agent | 意图理解→决策→调动作（写回回路） |
| 本体来源 | **自动映射/LLM 发现**（从数据长出来） | MVP 手写 Pydantic + 显式注册表 |
| 写回外部系统 | 设计文档有蓝图，**引擎未实现** | **核心交付物**，E2E 验证通过 |
| 治理 | 角色权限 + action 发布状态机 + 快照审计 | 审计 + 规则前置校验 + 权限边界（发布期） |
| 部署 | Docker Compose 全栈（可降级） | 本地 FastAPI+SQLite 双库（发布期 Docker） |
| 测试 | 300+ pytest | 187 后端 + 23 前端（三问/E2E 全绿） |

**一句话差异**：它回答"本体怎么从数据里长出来并管起来"，我们回答"LLM 怎么在一个受治理的语义接口里操作真实业务系统并真写回"。二者是**本体全生命周期的前半段 vs 后半段**，可互补不冲突。

## 6. 可借鉴清单（按优先级）

1. **submission_criteria 五类门控 + action 发布状态机**（draft→review→published 才能执行）——我们的动作门控可对齐这套词汇与流程
2. **before/after snapshot 审计**——我们的审计是否含变更前后快照？建议补（当前审计是写回 SQL+影响行数，可升级为快照对比）
3. **优雅降级哲学**——可选服务全回退，本地零依赖可跑；强化我们"本地可演示"卖点
4. **PostHarnessValidator 七道检查**——若未来我们让 LLM 生成/扩展本体 schema，直接套用这套校验层（含 ast.parse 语法校验、类型白名单）
5. **自动映射 + 关系推断四技法**（外键/格式容错/备用键/LLM语义链接）——补上我们"本体从哪来"的研究空白（白皮书扩展章节素材）
6. **LLM 质量审查 ReAct Agent（8 工具链式）**——本体质量自动体检，可作发布期功能或白皮书方法论案例
7. **ConfirmLevel 分层 / Event Bus 模式 / Function 定义与实现分离**——设计层思想，写进白皮书"发布期演进"参考
8. **测试策略：内存 Fake 替代 DB**——我们的运行时测试可借鉴（已有此风格可强化）

## 7. 竞争/定位含义（喂给 D 讨论 + 发布物料）

- **不撞车**：它是"构建器"，我们是"运行时"。它的存在恰恰**验证了 Palantir 式轻量落地有受众**（405 stars），且**缺了我们的写回闭环**。
- **发布定位可选一句**：本体生命周期分两段——构建（nano-ontoprompt 这类开源已做）与**运行/写回（OntoRun 研究面）**；我们补上"LLM 真操作真实系统"的后半段。可做差异对照表的一行，不点名互踩。
- **合作/引用可能性**：MIT 开源、作者活跃、同为中文语境——白皮书可把它列为"本体构建"环节的成熟开源参考（传输层/操作层用现成方案的精神一致）。
- **注意**：它也用了供应链 test_data 与 RDF 导出（rdflib）——我们"不引入 RDFlib MVP"的决策不受影响，但发布期若做 RDF 导出可直接借鉴其实现。

## 8. 附录：关键文件索引（GitHub API 路径）

- 动作执行：backend/app/routers/v2/logic_actions.py（629 行，run + submission criteria + 逻辑规则求值）
- 动作模型/审计表：backend/app/models/v2/action.py（OntologyActionType / OntologyActionRun 含 before/after 快照）
- 校验器：backend/app/engine/post_harness/validator.py
- 自动映射：backend/app/services/v2/mapping/mapping_service.py（79KB）/ auto_mapper.py / 备用键测试 backend/tests/v2/mapping/test_alt_key_links.py
- 管道步骤：backend/app/services/v2/pipeline/steps/（document_to_md / md_to_structured / wide_table_split / json_flatten / schema_inference / xml_parse）
- 图/向量/增量：services/v2/graph/（neo4j/nl2cypher/cypher_builder）、vector/chroma_service、incremental/orchestrator
- 设计文档：ONTOLOGY.md（2728 行，Object/Link/Function/Governance/EventBus + 临床/多模态/病历写回扩展场景）
- 审计服务：backend/app/services/audit_service.py（21KB，v1 审计）
- 供应链数据与 golden 测试：scripts/data/run_full_supply_chain.py、run_supply_chain_pipeline.py、backend/tests/v2/mapping/test_supply_chain_golden.py、test_data/供应链

---

*fork 在 suyukun/nano-ontoprompt；如需本地精读可稍后从 fork 拉取（git 网络不稳时走 API 亦可）。*
