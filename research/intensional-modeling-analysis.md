# 内涵建模（Intensional Modeling）— 提案分析

> 日期：2026-08-18 ｜ 编制：Rose（基于 Jack 提供的《内涵建模·第三数据建模范式提案·征求意见稿》）
> 性质：研究档案，**不是** OntoRun 战略文件。判断给 Jack 拍板，结论落到 v0.3 战略 + AGENTS.md 时另走变更流程。
> 上游：提案原文 `/Users/suyukun/Downloads/内涵建模-第三数据建模范式提案.docx`
> 下游：方向与战略 v0.2 §3「脊柱之问」待用此分析；未拍板前不写回 v0.2 / AGENTS.md

---

## 0. BLUF

提案的内涵建模 = **OntoRun 一直缺的上位理论**。我们战略里「为 Agent 而建（可理解、可操作、可治理写回）」只是一句方向口号；提案把它升格为有数学根基（类型论 + 范畴论 + 效果系统 + 血缘半环 + 安全格）、有机检良构（1INF–6INF）、有可重复设计程序的完整方法论。

**OntoRun 不重写一份方法论**，但要把提案的核心原语（粒度 / 可加性 / 基数 / 时态 / 血缘 / 效果 / 意图）作为 MVP 之后的 schema 演进方向。MVP 第一里程碑的「三问测试」先不动，**但 schema 层要预留类型字段**，别等闭环跑通再回炉改 Pydantic 模型。

**两个不照搬**：
1. **不背书"第三范式"命名**——提案作者自承 5–10 年 50% 概率。OntoRun 的白皮书标题用「面向 AI 消费者的数据建模方法」更稳。
2. **不引入 Lean 4 / 范畴论库 / RDFlib**——学术发力点由 Jack 作"白皮书作者"另起炉灶，OntoRun 工程 repo 只承载"第一刀 = 零售供应链最小闭环"。

---

## 1. 提案核心结构（一段话 + 一张表）

**一句话**：把"外延（表与行）"降为可替换投影，把"内涵（带类型的、可组合的、有效性有界的业务定义）"立为第一建模产物。物理表（3NF / Data Vault / 湖仓）藏在内涵契约之后，agent 通过类型化 API/语义契约消费。

**八元组 I-Term**：

| 字段 | 提案名 | 业务含义 | OntoRun 现状 |
|---|---|---|---|
| C | Concept | 概念类（订单、客户…） | Object（已有） |
| G | Grain | 粒度 | ❌ 缺 |
| A | Additivity | 可加性 | ❌ 缺 |
| τ | Temporal | 时态类型 | ❌ 缺 |
| Σ | Scope | 范围/作用域（含基数） | ⚠️ 基数隐式，无显式字段 |
| Π | Provenance | 血缘/置信度 | ⚠️ 审计日志有，半环化无 |
| E | Effect | 效果/安全 | ⚠️ RBAC 临时方案，格模型无 |
| ι | Intent | 意图/目标 | ❌ 缺（**最值钱的创新**） |

**6 级机检良构 1INF–6INF**：
- 1–2INF 管"是什么"（对象/字段定义、概念包含）
- 3–4INF 管"组合得对不对"（粒度对齐、基数安全、可加性、时态 as-of）
- 5–6INF 管"能不能信、能不能动手"（血缘传播、效果授权、意图绑定）

**类型化组合演算 7 条规则**（合并 T₁、T₂ → T′ 时全部成立才合法）：
- 粒度规则：结果粒度只能上卷，混合不显式聚合 = ill-typed
- 基数/fan 规则：1:N 连接里"1"侧度量获得扇出多重性，禁止直接求和；强制 fan-safe drill-across（**按构造杜绝 chasm/fan trap**）
- 可加性规则：ratio 禁 SUM；semi-additive 禁沿时间求和
- 时态规则：连接须 as-of 对齐
- 血缘规则：Π(T′)=Π(T₁)⊗Π(T₂)，半环同态
- 效果/安全规则：动作型组合要求 ι 目标绑定+授权；安全标签按格最小上界
- 范围/作用域规则（Σ）：multiplicity-safe、scope-unifiable

---

## 2. 提案 vs OntoRun 现状——逐项映射

| 提案元素 | OntoRun 现状 | 差距 | 处置 |
|---|---|---|---|
| 内涵 = 第一产物，物理表降为可替换投影 | 已有"操作型本体 vs 描述型本体"立场（AGENTS.md §五个关键设计决策 D-T2：MVP 不用 RDFlib） | 我们已选 Pydantic + 注册表；未表态"物理层可换" | **白皮书写作时回扣**：MVP 不引入 RDFlib 不变；中长期可声明式映射（OBDA/R2RML） |
| Object + Link + Action | 本体核心三件 | ✅ 对齐 | 无 |
| 意图 ι 是一等建模维度 | 战略 §3 提"为 Agent 而建" | 战略口号，未落到 schema | **采纳**：Action 模型加 `intent_ids: list[str]` 字段 |
| 粒度 G / 可加性 A / 时态 τ 八元组 | 只有 Pydantic 字段 | 重大缺口 | **采纳**：MVP 后 Pydantic 模型加 4 个字段（见 §3） |
| 1INF–6INF 机检良构 | 无 | 缺口 | **不做 MVP 范围**；白皮书「理论章节」提及，工具留作 linter 阶段 |
| 基数 fan 规则按构造拒绝 chasm trap | 隐式无 | 缺口 | **采纳为 schema 字段**：Link 上加 `cardinality` + `aggregation_hint` |
| 血缘半环传播 | 审计日志 | 缺口 | **先记录"来源+置信度"结构化字段**；半环化等数据量上来 |
| 安全格 E（Denning 1976） | RBAC 临时 | 缺口 | **不阻塞 MVP**；标记为 R-2（中期演进） |
| 范畴论 schema 语义（Spivak） | 无 | 缺口 | **仅作白皮书理论背书**，代码不引入 |
| OBDA/R2RML 声明式映射 | 硬编码 SQL 写源系统 | 中期缺口 | **MVP 不做**；标注为发布期演进 |
| 设计程序 6 步（从决策/动作起步） | 我们"先想对象→再想动作" | **流程反了** | **采纳**：MVP 第一刀 = 枚举 LLM 要下的决策与动作，倒推对象 |
| 类型可推断默认值 | 靠人手 | 缺口 | **Linter 阶段做**，MVP 不引入 |
| 三个学术发力点（Lean / 1INF–6INF / 意图形式化） | 无 | 不在工程范围 | **Jack 个人写作通道**承担，不入 OntoRun repo |

---

## 3. 提案给 OntoRun 的「4 个 schema 字段」——最小落地建议

> 不重写 Pydantic 模型，只在现有 Object/Link/Action/Measure 上加 4 类字段，**字段加完就能跑 MVP**，机检 linter 留作后续。

```python
# 概念示意，最终落 src/ontology/ 后再定型

class Measure(BaseModel):
    name: str
    additivity: Literal["additive", "semi-additive", "ratio", "non-additive"]  # A
    temporal_type: Literal["point-in-time", "interval", "as-of-latest", "bitemporal"]  # τ
    # ... 现有字段保留

class Link(BaseModel):
    name: str
    cardinality: Literal["1:1", "1:N", "N:1", "N:M"]  # Σ 的一部分
    aggregation_hint: Literal["none", "sum", "avg", "max", "count-distinct"] | None
    # ... 现有字段保留

class Action(BaseModel):
    name: str
    intent_ids: list[str]                              # ι（最值钱）
    effect_type: Literal["read", "write", "external"]   # E 的最小化
    # ... 现有字段保留
```

> **为什么不现在就改**：Jack 已明令"团队在干活、不动 AGENTS.md / 战略文件"。schema 改动也属"团队上下文敏感面"——先立研究档案 + 等 linter 规格出来一起走变更流程，**不分散打补丁**。

---

## 4. 提案作者的自我质疑 + 我们的回应

| 提案 Q | 提案自答 | OntoRun 立场 |
|---|---|---|
| Q1 只是形式化已有东西？ | 工程特性分散≠理论存在 | **采纳作者立场**——「Codd 未发明集合论」类比强。**但**：OntoRun 不背书"范式之名"，做"语义接口可闭环"的事实 |
| Q2 八项类型太重？ | 多数可推断、人只裁例外 | **采纳**——MVP 加 4 字段，类型推断推给 linter 阶段 |
| Q3 LLM 更强后是否不需要？ | 类型是护栏不是束缚 | **采纳并写进白皮书**——这是 OntoRun vs "纯 LLM 即一切"的差异点 |
| Q4 学术画饼、落不了地？ | 验证器 + 查询编译器等价交付物明确 | **采纳"先做验证器"路径**——但范围限于 1INF–3INF（粒度/基数/可加性），5–6INF（效果/意图）后置 |

---

## 5. 风险与不照搬清单

**不照搬**（明牌反模式/目标漂移防护）：
1. 不引入 RDFlib（与 AGENTS.md D-T2 一致；提案 §十也排除 OBDA 走 OWL 路线）
2. 不引入 Lean 4 / Coq（学术发力点不在工程 repo）
3. 不引入范畴论库（Spivak 语义仅作白皮书引用）
4. 不背书"第三范式"命名（提案作者自承未共识）
5. 不重写方法论文档（**只引用提案**，OntoRun docs/ 只长我们自己的内容）
6. 不在 MVP 加 linter（**先跑通三问测试**，再补 linter）

**风险**：
- 提案"6 步设计程序"过重——MVP 阶段只做"决策清单 → 动作清单 → 对象/度量"，后三步（组合图、绑定外延、验证范式）发布期做
- 提案学术发力点（Lean 形式化）若由 Jack 写，**不要在 OntoRun repo**——另立"白皮书"项目，避免污染工程目录
- 类型化组合演算的"机检"门槛：MVP 不做机检，但 schema 字段预留好；否则后续 linter 阶段要回炉

---

## 6. 对 OntoRun 路线的具体建议（待 Jack 拍板，不直接改文件）

1. **MVP 启动顺序改**：先列"LLM 要下的决策与动作清单"，再倒推对象/字段；不要"先建 Customer/Order/Shipment 表"
2. **schema 加 4 类字段**（见 §3）——变更走单独流程，不在 B/C 完成前动
3. **战略 v0.2 §3"新范式之问"加一行**：「上位理论 = 内涵建模（I-Term 八元组 + 1INF–6INF + 类型化组合演算），OntoRun = 该理论的第一个零售供应链切片」
4. **白皮书章节改为"边长边写"**：先写 §「内涵建模是什么」（引用提案）+ §「我们怎么把第一刀切到零售供应链」+ §「闭环结果」；Lean 形式化 / R2RML 全文 / 格模型 留给"发布期"
5. **AGENTS.md §"五个关键设计决策"追加 D10**：「schema 字段遵循内涵类型（提案 §三），MVP 不实现 1INF–6INF 机检但字段预留」——与 D-T2（不引入 RDFlib）并列

---

## 7. 与现有研究材料的交叉

| 已有材料 | 关联 | 状态 |
|---|---|---|
| `research/palantir-ontology.md` | 提案 §十"工程先驱"直接点名 Palantir Object+Action | 已知，本档案不重复 |
| `research/palantir-foundry-docs-digest.md` | 同上 | 已知 |
| `research/nano-ontoprompt-analysis.md` | 与"LLM 消费语义层"主题相关 | 待 cross-ref |
| `research/palantir-bilibili-notes.md` | 概念入门 | 已知 |

---

## 8. 引用与待补

**已引**（提案原文段落号）：
- 摘要 P003；问题 §一 P004–P012；核心命题 §二 P014；I-Term §三 P016–P017；组合演算 §四 P020–P028；范式 §五 P031；设计程序 §六 P033–P038；数学 §七 P040–P051；金融实例 §八 P053–P056；对照 §九 P059；相关工作 §十 P060–P070；质疑 §十一 P072–P075；路线 §十二 P077–P082

**待补**（B+C 完成后追加）：
- 30 天可落地的 linter 原型规格（C 产出）
- Lean 4 论文 arXiv:2601.00995 摘要 + 与本档案的关联
- dbt MetricFlow 2025-12-18 公告中"已可机检的子集"与本档案映射

---

*本档案由 Rose 撰写，结论待 Jack 拍板后回写战略 v0.3 / AGENTS.md / 白皮书。本档案不修改任何项目文件。*