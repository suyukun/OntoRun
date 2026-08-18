# 内涵建模 linter 30 天可落地规格

> 日期：2026-08-18 ｜ 角色：研究/AI subagent（Rose 指派）｜ 性质：研究档案（提案分析 §8 待补项 C），只写设计、不写代码、不改项目文件
> 上游：`research/intensional-modeling-analysis.md` ｜ 下游：编码 subagent（命名/选库/选框架/实现）
> 范围：1INF–3INF（粒度/基数/可加性）schema 静态机检；5–6INF 后置

## 1. BLUF

**linter = 把提案"类型化组合演算 7 条规则"的 1–3INF 子集做成只读 schema 静态检查器**：输入 `src/ontology/` 的 Pydantic 注册表（含提案 §3 的 4 类字段），输出与现有 `registry.self_check` 同构的 Issue 报告，挂测试/CI 门禁，作为第一里程碑"LLM 消费前先机检"的 schema 质量层。30 天只做**声明一致性**：不做运行期查询校验、不做类型推断。节奏：W1 落 4 类字段+规则骨架，W2–W3 九条规则，W4 CLI+门禁+文档。

## 2. Linter 原型规格

**输入**（字段=提案 §3 四类字段，先走变更流程落 schema 再上 linter）：
- ObjectTypeDef：主键 + grain 声明；Measure：additivity、temporal_type
- LinkTypeDef：cardinality（含 N:M 扩展）、aggregation_hint
- ActionDef：intent_ids、effect_type（仅登记，不判语义——5–6INF 后置）

**输出**：Issue 列表（severity error/warning + 位置 + 规则码 + 说明），机器可读；退出码 0=通过/1=有 error/2=用法错误；`--explain <码>` 打印规则依据。CLI 为单入口命令，命名与框架由编码角色定。

**检查规则 9 条**（依据=提案 §1 组合演算 + 三外部材料）：

| 码 | 规则 | 严重度 | 依据 |
|---|---|---|---|
| INF2-DEF-001 | 对象有唯一主键；Measure/Link 引用对象存在 | E | self_check 既有 |
| INF1-ADD-001 | additivity 值合法；ratio 须声明分子分母，禁裸 SUM | E | 提案/MetricFlow |
| INF3-GRA-001 | 对象与 additive Measure 须显式声明 grain | E | 论文 CalcG |
| INF3-GRA-002 | 聚合目标粒度须为源粒度上卷（沿主键/FK 链） | E | 论文同态/上卷 |
| INF3-CARD-001 | N:1"1"侧 additive 沿"N"聚合须有 aggregation_hint | W | 论文 fan trap |
| INF3-ADD-002 | semi-additive 须声明 temporal_type；沿时间 SUM 报警 | E | MetricFlow non_additive |
| INF3-CARD-002 | N:M 禁直接 sum（须 hint 非 sum 或经事实对象） | E | 提案 fan-safe |
| INF3-CARD-003 | 两路 many-to-one 汇聚+双侧 additive 须显式聚合策略 | W | Snowflake chasm |
| INF3-TEMP-001 | temporal_type 声明完整（bitemporal 两时间字段存在） | E | 提案 τ |

**错误码**：`INF{n}-{类别}-{NNN}`，类别 DEF/GRA/CARD/ADD/TEMP；码表进注册表，与 `actions.py` 的 CANONICAL_ERROR_CODES 并列不冲突。

**集成点**：只读 `objects/links/actions/registry`，输出复用 `registry.Issue` 形态；运行时加载 schema 前先过 linter；self_check 已查主键唯一/链接命名，linter 不重复，只管 1INF–3INF 语义。

## 3. 外部三材料要点（重点=已可机检）

**arXiv:2601.00995（⚠️ v2 已改名"Grain Theory: Type-Level Granularity Correctness in Data Pipelines"）**：把粒度升为任意代数类型的可组合类型级性质（grain/entity key/behavioral class + 格 + Armstrong 公理）；变换有 grain lift，同态定理保证组合；CalcG 仅凭 schema 元数据 O(|V|k|F|) 在 DAG 上传播粒度——fan trap 成 schema 可检违反；chasm trap 只定位序链结构模式（数据实例级不可判）；行为类错配=编译期类型错误；Lean4 全证（34 模块零 sorry）。**未形式化**：一般 grain 蕴含（sum/递归）、域规则、操作契约、自动修复。可机检：粒度传播、fan trap、行为类。

**MetricFlow（2025-12-18 开源，Apache 2.0，对齐 OSI）**：语义模型=语义图节点，以 entity（primary/foreign/unique/natural）为 join 键显式相连（YAML）；agg 枚举 sum/min/max/avg/median/count_distinct/percentile/sum_boolean；semi-additive 用 non_additive_dimension 声明；metric 类型 simple/ratio（分子分母）/cumulative/derived。可机检：agg 合法性、ratio 依赖、semi-additive 维度约束、join 路径无隐式连接。

**Snowflake Cortex Analyst（2025-02-20）**：schema 表达为粒度图（节点=粒度，边=many-to-one，自环=1:1）；按 GROUP BY/DISTINCT 沿图上卷定位查询粒度（含 derived granularity）；逐 CTE 递归建图，join 必须在图中存在否则判幻觉→纠错模块回喂 LLM 重试；additive 聚合只许在最细节点，fan trap=additive 在根上、chasm=两路汇聚双侧聚合→拒绝。可机检：粒度定位、join 路径、additive 位置、chasm 模式。

## 4. 与提案已有判断的对应

- ✅ §4"先做验证器、限 1INF–3INF"→ 本规格即其 30 天实例；§3 四类字段 = linter 输入前提
- ✅ §1 组合演算中"粒度/基数/可加性"子集 → R3–R8；"按构造杜绝 fan/chasm"→ R7/R8（schema 层近似）
- ✅ D-T2 不引 RDFlib → linter 只读 Pydantic 注册表
- ⚠️ **提案已说但 linter 做不了**：①类型可推断默认值（§4）——只查显式声明，推断后置；②5–6INF（血缘半环/效果格/意图绑定）——只登记不判语义；③"连接须 as-of 对齐"需运行期查询分析——linter 只查 temporal_type 声明完整（R9）；④chasm trap 数据实例级判定（论文明示不可类型级）——只报结构 warning；⑤血缘 Π 半环传播——数据量上来后做

## 5. MVP 阶段不要做（防目标漂移）

- ❌ 运行期/生成 SQL 的查询级校验（Snowflake 粒度图那套，属 LLM 查询层）
- ❌ 类型推断、自动修复（pipeline synthesis）、一般 grain 蕴含、Lean/范畴论形式化（归白皮书通道）
- ❌ 5–6INF 语义检查、时态 as-of 连接验证
- ❌ 引 RDFlib/新 schema 格式/新依赖（AGENTS.md D-T2）
- ❌ 工具命名/选库/选框架、写任何代码（留给编码 subagent）
- ❌ 改 `src/ontology/` 现有文件（字段变更走独立流程，不分散打补丁）

---
*本档案由研究/AI subagent 编制，供 Rose 验收后转编码 subagent。不修改任何项目文件。*
