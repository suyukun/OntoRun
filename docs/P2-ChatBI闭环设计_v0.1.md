# P2 ChatBI 闭环设计 v0.1（上篇：指标模型 + DuckDB 物化）

> 编制：架构角色（本体论方向）｜ 日期：2026-08-21 ｜ 状态：设计稿（本轮仅上篇）
> 关联：docs/S2-议题清单_v0.1.md（§3.5.5 议题1 形态 v2 / §3.18 C4 双引擎一致性 / §3.5 量级真相）、
> docs/S2-开发计划_v0.1草案.md（阶段 P2 门禁）、docs/P1b-DES-横向铺开设计_v0.1.md（18 表字段 / §6.2 Q2 基线）、
> docs/S2-P1b-横向铺开完成记录.md（Q2 实测 98ms / 基线需重定义）、docs/P1a-本体映射与查询契约设计_v0.1.md（契约 v0.1 / reconcile 范式）、
> src/des/materialize.py + src/des/contract.py（现有物化/契约接口）
> 产出：本文档（单文件 md，设计规格）；实现由 P2 编码活落地
> 范围（重要）：**本次只覆盖「本体读侧指标模型 + DuckDB 物化」**；「契约 v0.2 + head-to-head 实验设计」在下一版（下篇）补充，本篇不展开。

---

## 0. 前言（范围声明 + 一句话设计）

### 0.1 本轮范围声明（先对齐边界，防目标漂移）

P2（ChatBI 最小闭环，S2 开发计划阶段 P2）包含四件事：
**① 本体读侧指标模型 → ② DuckDB 物化 → ③ 受限结构化查询（契约 v0.2）→ ④ head-to-head 实验**。

本设计**上篇只做 ①+②**（指标模型 + 物化），③④ 在**下篇**补充，理由：
- ③ 契约 v0.2 依赖 D3 head-to-head 实验结果（受限结构化查询 vs NL2SQL+守卫，30 问，S2 垂直切片内跑）才能定终版——**实验未跑，契约不可先定**；
- ④ head-to-head 实验设计需要 ① 的指标语义面作实验集底座，先定指标面、后定实验面，顺序自洽；
- ①② 是 ③④ 的语义与数据前提：**对象→指标→物化结果**这条读侧链路先落定，契约 v0.2 的聚合执行才有落点（命中物化表而非裸表现场算）。

下篇待补内容（本篇不展开，仅登记）：契约 v0.2 schema 演进（含 count_distinct、时间范围过滤、物化表命中路由）、head-to-head 实验设计（30 问 / 指标 / 成功率 / P95 / 成本 / 拒答率）、终版决策与 Plan B。

### 0.2 一句话设计

**指标 = 挂在本体对象上的可预聚合度量（metric 注册表：对象 → 指标定义 → 物化结果）；LLM/Agent 在本体上选对象 → 指标，落到 DuckDB 预聚合表执行（每指标 1 张物化表），源 SQLite 与物化 DuckDB 之间用 C4 流转契约（全量重建 + 版本标识 + reconcile diff=0）保证一致性；对象级读侧（<~1 万对象）动态派生，指标级读侧一律预聚合——把 DES 100 万行数据的分析延迟从动态直算压到 ≤100ms 且相对加速 ≥10×（P2 对标基线，诚实口径见 §2.5）。**

设计锚点（对齐已拍板结论）：

| 锚点 | 依据 |
|---|---|
| 预聚合优先 / 本体读侧=物化指标语义入口 | 议题清单 §3.5.5-1/2（2026-08-21 Jack 拍板 v2） |
| 不造轮子：物化用 DuckDB 成熟能力，OntoRun 只做本体↔物化指标映射 | 议题清单 §3.5.5-3 / §0.5 不造轮子铁律 |
| 分析引擎 = DuckDB；SQLite 保留作源系统/写回层 | 议题清单 §3.5.5-5 |
| C4 双引擎一致性：流转契约 + reconcile 测试 + 单用户前提 | 议题清单 §3.18 C4 |
| 量级 = 100 万行级（1 企业 5 系统 18 表，本机可演示） | 议题清单 §3.19 C1 拍板 / P1b 完成记录 |
| P2 基线：无预聚合大聚合 ~2s → 预聚合 ≤100ms | 议题清单 §3.5-5（2.3s 实测）/ P1b 设计 §6.2（≤2000ms），**P1b 实测后重定义见 §2.5** |

---

## 1. 本体读侧指标模型

### 1.1 定位：本体读侧 = 物化指标的语义入口

延续议题清单 §3.5.5-2 的形态结论：**本体对象可「指向」预聚合指标（对象 → 指标定义 → 物化结果），Agent 在本体上选择，落到预聚合层执行**。本次把这条链路在指标模型层面做死：

1. **指标是一等公民**（不是新对象类型）：指标 = 对象上「可聚合属性」的语义化扩展。对象负责语义锚定（"这是销售金额的挂靠主体"），指标负责口径（"按什么维度、聚什么、怎么算"）；
2. **对象可指向多个指标**（1:N）：如 Material 对象可指向物料组计数、按物料×月的销售金额、按物料×地点的库存账面、按物料×月的采购数量等多个指标；一个指标只挂一个主体对象（粒度由 dimension_fields 表达，见 §1.2）；
3. **不造轮子**：指标定义（维度/度量/聚合）是成熟数仓范式（dbt Semantic Layer / LookML 同构），OntoRun 只做「**本体↔物化指标**」的映射层（对象/字段语义 ↔ 源表列 ↔ 物化表），度量定义本身不复刻任何新范式。

### 1.2 metric 定义（schema）

指标注册表每条记录形如（核心 7 字段 = 任务规格字段，一字不差）：

~~~json
{
  "metric_id": "sales_amount_by_mat_month",
  "object_type": "Material",
  "dimension_fields": [
    { "name": "matnr",    "source": "VBAP.MATNR",                     "transform": null },
    { "name": "month",    "source": "VBAK.AUDAT",                     "transform": "substr(1,7)" }
  ],
  "measure": { "name": "sales_amount", "source": "VBAP.NETWR" },
  "agg_function": "sum",
  "definition": "按物料×月的销售金额 = Σ VBAP.NETWR（月 = VBAK.AUDAT 前 7 位，口径单点）",
  "source_tables": ["erp.VBAK", "erp.VBAP"]
}
~~~

字段语义（均为机器校验输入，见 §1.3）：

| 字段 | 类型 | 语义 | 说明 |
|---|---|---|---|
| metric_id | string | 指标全局唯一标识 | snake_case，禁硬编码，注册表单一事实来源；物化表名由此派生（§2.1） |
| object_type | string | 指标主体对象 | 须解析到已注册对象类型（M1）；对象可指向多个指标（§1.4） |
| dimension_fields[] | array | 粒度维度 = 物化分组键 | 每项 {name（本体字段名）, source（源列，含表限定）, transform（可选派生，如 substr→月）}；非空（M6） |
| measure | object | 度量 | {name, source}；数值型用于 sum/avg/min/max，任意型用于 count/count_distinct（M5） |
| agg_function | enum | 聚合函数 | sum / count / count_distinct / avg / min / max（M4） |
| definition | string | 口径定义（人读 + 口径单点） | 物化 SQL 与 reconcile SQL **同源于此**（§2.3），禁双处维护 |
| source_tables[] | array | 来源表 | 形如 "erp.VBAK"，须 ∈ DES 表注册表（M2）；跨库由 DuckDB sqlite_scan 打通（竖井在语义层打通，延续 P1a） |

> 可选扩展字段（本期启用但非校验必需，登记不展开）：unit（度量单位，如 CNY/PC）、data_version（指标定义版本，参与物化版本戳，见 §2.2）。

### 1.3 指标校验规则（可机验，兑现铁律②）

指标注册表加载即校验，任一违规 fail-fast（对齐 contract.py V1-V5 与 config.py 的 fail-fast 纪律）：

| # | 规则 | 实现 | 失败处理 |
|---|---|---|---|
| M1 | 主体对象白名单 | object_type 解析到 Registry 已注册对象（复用 _resolve_type） | 抛 MetricError（拒加载） |
| M2 | 来源表白名单 | source_tables 全 ∈ DES 生效配置表注册表（systems[].tables[]，含 erp.VBAK 等 18 表） | 同上 |
| M3 | 字段存在 | dimension/measure 的 source 列须存在于对应源表列（读生效配置表规格/实测表结构） | 同上 |
| M4 | 聚合函数合法 | agg_function ∈ {sum, count, count_distinct, avg, min, max} | 同上 |
| M5 | 度量类型 | sum/avg/min/max 要求数值列（REAL）；count/count_distinct 允许任意列或 * | 同上 |
| M6 | 粒度确定性 | dimension_fields 非空且可作物化行唯一键（粒度重复 → 物化行歧义） | 同上 |
| M7 | metric_id 唯一 | 注册表内不重名（加载期去重） | 同上 |

### 1.4 对象 → 指标（对象可指向多个指标）

- 注册表维护 metrics_by_object(object_type) 索引：给定对象返回其全部指标（供 Agent 在本体上「选对象 → 看指标列表 → 选指标 → 落物化结果」）；
- 当前 15 个指标挂载分布（见 §1.5）：Material 对象指向最多（物料组 3 + 销售按物料 2 + 库存按物料 1 + 采购按物料 1 = **7 个**），Customer/Vendor/InventoryLocation/FinanceEntry 各 1-2 个——**一个对象指向多个指标、一个指标只挂一个主体对象**；
- **P2 实现第一步 = 注册主体对象**：现有 Registry 仅注册 Material/Code（P1a）；本设计 15 指标所需的 4 个新主体对象（Customer/Vendor/InventoryLocation/FinanceEntry）须按 P1a 范式（ObjectTypeDef + Pydantic + 物化 SQL + 注册）补注册，其源表/主键见 §1.5 表。对象 schema 细化（字段级映射/归属标注）属 P2 本体映射实现工作，本篇只声明指标挂载所需的对象锚点（M1 校验依赖）。

### 1.5 5 组 15 指标清单（从 18 表挑选）

按任务要求从 18 表挑 **5 组各 3 个**（物料/销售/库存/采购/财务），共 15 个指标。每组明确：**维度字段（语义→源列）/ 度量字段（源列）/ 聚合函数 / 来源表**；「月」维度统一 = 日期列 substr(col,1,7)（TEXT 'YYYY-MM-DD' → 'YYYY-MM'，口径单点，见 §2.3）。

**组 A · 物料（主体对象 Material，源表 erp.MARA / erp.MARC）**

| metric_id | 维度字段（源列） | 度量（源列） | 聚合 | 来源表 |
|---|---|---|---|---|
| mat_count_by_type_factory | material_type(MARA.MTART), factory(MARC.WERKS) | *（行计数） | count | erp.MARA, erp.MARC |
| mat_count_by_abc_factory | abc_class(MARC.MAABC), factory(MARC.WERKS) | * | count | erp.MARC |
| mat_count_by_group | material_group(MARA.MATKL) | * | count | erp.MARA |

**组 B · 销售（主体对象 Material / Customer，源表 erp.VBAK + erp.VBAP）**

| metric_id | 维度字段（源列） | 度量（源列） | 聚合 | 来源表 |
|---|---|---|---|---|
| sales_amount_by_mat_month | matnr(VBAP.MATNR), month(VBAK.AUDAT→substr) | sales_amount(VBAP.NETWR) | sum | erp.VBAK, erp.VBAP |
| sales_amount_by_customer_month | customer(VBAK.KUNNR), month(VBAK.AUDAT→substr) | sales_amount(VBAP.NETWR) | sum | erp.VBAK, erp.VBAP |
| sales_qty_by_mat_month | matnr(VBAP.MATNR), month(VBAK.AUDAT→substr) | sales_qty(VBAP.KWMENG) | sum | erp.VBAK, erp.VBAP |

**组 C · 库存（主体对象 InventoryLocation / Material，源表 erp.MARD + wms.MSEG）**

| metric_id | 维度字段（源列） | 度量（源列） | 聚合 | 来源表 |
|---|---|---|---|---|
| stock_balance_by_location | factory(MARD.WERKS), location(MARD.LGORT) | stock_balance(MARD.LABST) | sum | erp.MARD |
| stock_balance_by_mat_location | matnr(MARD.MATNR), factory(MARD.WERKS), location(MARD.LGORT) | stock_balance(MARD.LABST) | sum | erp.MARD |
| stock_flow_by_location | factory(MSEG.WERKS), location(MSEG.LGORT) | flow_qty(MSEG.MENGE) | sum | wms.MSEG |

> C3（流水净变）与 C1（账面）按地点 **diff=0 自洽**（复用 D10 对账口径，§2.3 R2）——这是「物化层对账」的天然锚。

**组 D · 采购（主体对象 Vendor / Material，源表 scm.EKKO + scm.EKPO）**

| metric_id | 维度字段（源列） | 度量（源列） | 聚合 | 来源表 |
|---|---|---|---|---|
| purchase_amount_by_vendor_month | vendor(EKKO.LIFNR), month(EKKO.AEDAT→substr) | purchase_amount(EKPO.NETWR) | sum | scm.EKKO, scm.EKPO |
| purchase_qty_by_mat_month | matnr(EKPO.MATNR), month(EKKO.AEDAT→substr) | purchase_qty(EKPO.MENGE) | sum | scm.EKKO, scm.EKPO |
| purchase_order_count_by_vendor_month | vendor(EKKO.LIFNR), month(EKKO.AEDAT→substr) | purchase_orders(EKKO.EBELN) | count_distinct | scm.EKKO |

**组 E · 财务（主体对象 FinanceEntry，源表 fin.ACDOCA）**

| metric_id | 维度字段（源列） | 度量（源列） | 聚合 | 来源表 |
|---|---|---|---|---|
| finance_amount_by_account_month | account(ACDOCA.RACCT), month(ACDOCA.BUDAT→substr) | amount(ACDOCA.WSL) | sum | fin.ACDOCA |
| finance_amount_by_costcenter_month | cost_center(ACDOCA.KOSTL), month(ACDOCA.BUDAT→substr) | amount(ACDOCA.WSL) | sum | fin.ACDOCA |
| finance_amount_by_reftype | ref_type(ACDOCA.REF_TYPE) | amount(ACDOCA.WSL) | sum | fin.ACDOCA |

**主体对象注册需求汇总**（供 P2 实现排期）：

| 对象 | 源表（PK） | 状态 |
|---|---|---|
| Material | erp.MARA（MATNR） | ✅ 已注册（P1a） |
| Customer | erp.KNA1（KUNNR） | 待注册（P2 实现） |
| Vendor | scm.LFA1（LIFNR） | 待注册 |
| InventoryLocation | erp.MARD 地点粒度（WERKS+LGORT） | 待注册 |
| FinanceEntry | fin.ACDOCA（BELNR+POSNR） | 待注册 |

### 1.6 示例指标（完整定义）

**例 1 ·「按物料+月的销售金额」**（组 B1，对应任务示例）：

~~~json
{
  "metric_id": "sales_amount_by_mat_month",
  "object_type": "Material",
  "dimension_fields": [
    { "name": "matnr", "source": "VBAP.MATNR" },
    { "name": "month", "source": "VBAK.AUDAT", "transform": "substr(1,7)" }
  ],
  "measure": { "name": "sales_amount", "source": "VBAP.NETWR" },
  "agg_function": "sum",
  "definition": "按物料×月的销售金额 = Σ VBAP.NETWR（月 = VBAK.AUDAT 前 7 位；VBAK↔VBAP 以 VBELN 关联，无孤儿门禁 D5）",
  "source_tables": ["erp.VBAK", "erp.VBAP"]
}
~~~

物化 SQL 形态（口径单点，物化/reconcile 同源；表/字段全部来自注册表常量，无用户输入）：
SELECT VBAP.MATNR AS matnr, substr(VBAK.AUDAT,1,7) AS month, SUM(VBAP.NETWR) AS sales_amount
 FROM sqlite_scan('erp.db','VBAP') VBAP JOIN sqlite_scan('erp.db','VBAK') VBAK ON VBAP.VBELN=VBAK.VBELN
 GROUP BY 1,2

**例 2 ·「按地点的库存账面」**（组 C1，对应任务示例）：

~~~json
{
  "metric_id": "stock_balance_by_location",
  "object_type": "InventoryLocation",
  "dimension_fields": [
    { "name": "factory",  "source": "MARD.WERKS" },
    { "name": "location", "source": "MARD.LGORT" }
  ],
  "measure": { "name": "stock_balance", "source": "MARD.LABST" },
  "agg_function": "sum",
  "definition": "按库存地点的库存账面 = Σ MARD.LABST（W01/W02/W03 三地点；与 C3 流水净变对账 diff=0，D10）",
  "source_tables": ["erp.MARD"]
}
~~~

> 示例锚定：这两例正好覆盖「按物料×月」（跨 VBAK+VBAP 双表、含派生月维度）与「按地点」（单表、纯维度）两类典型指标形态，验证 schema 表达能力足够。

---

## 2. DuckDB 物化设计

### 2.1 物化表清单（每指标 1 张预聚合表）

**命名**：metric_{metric_id}（如 metric_sales_amount_by_mat_month），由注册表派生（禁硬编码）。

**表结构**：dimension_fields 全列（按注册表顺序）+ measure 1 列；主键 = 维度组合（M6 保证行唯一）。

~~~
metric_sales_amount_by_mat_month (
  matnr TEXT, month TEXT,        -- dimension_fields
  sales_amount DOUBLE,           -- measure
  PRIMARY KEY (matnr, month)     -- 粒度键
)
~~~

**存储**：持久化 DuckDB 文件 **metrics.db**（企业目录 data/des/enterprises/<code>/metrics.db，与 5 源 SQLite 库 + materialized.db 并列）。用 DuckDB 持久化文件 = 成熟能力（列存/向量化/单文件），不引新引擎；读侧查询直连 metrics.db 即可命中预聚合。

**体积预估（上界 = 维度基数积，实际 ≤ 上界）**：

| 组 | 物化表 | 维度基数上界 | 上界行数 |
|---|---|---|---|
| A | mat_count_by_* ×3 | MTART(5)×WERKS(2) 等小基数 | ≤100 |
| B | sales_* ×3 | matnr(8,000)×month(≤12) / customer(10,000)×month(≤12) | ≤96k / 120k / 96k |
| C | stock_* ×3 | location ≤6；matnr(8,000)×werks(2)×lgort(3) | ≤48k |
| D | purchase_* ×3 | vendor(5,000)×month(≤12) | ≤60k×2 + ≤60k |
| E | finance_* ×3 | account/cost_center 小基数 | ≤100 |
| **合计** | 15 表 | — | **≤ ~50 万行（量级远小于源表 100 万行，磁盘 < 50 MB）** |

> 「空间换时间」成本量化：预聚合后全量数据 ≈ 源表的一半行数级（且列数更少），磁盘增量 < 50 MB，换取分析延迟两个数量级下降（§2.5）——继承 Jack 数仓经验，对齐议题清单 §3.5.5-1。

**物化元表** metric_meta（版本/口径锚，§2.2 详述）：
metric_id, data_version, config_sha256, refresh_mode, refresh_ts, row_count, source_total_rows。

### 2.2 SQLite→DuckDB 刷新机制（C4 流转契约）

**数据流向**（一句话）：5×SQLite（源系统/写回层）→ DuckDB sqlite_scan 跨库 join（语义层，延续 materialize.py 模式）→ 物化指标表 metrics.db（预聚合，读侧唯一数据源）→ 契约 v0.2 查询命中物化表。

**（1）刷新模式：全量重建（S2 默认，显式声明单用户前提，对齐 C4）**

- 依据：DES 数据**确定性静态**（同 seed 同配置全表 SHA256 可复现，P1b 约定 1-5）+ S2 单用户 + 写回搁置（议题 8 T5 显式记录）→ 事务数据无运行期追加 → **全量重建最简、最可验**（无增量状态机、无水位线、天然幂等）；
- 实现形态：refresh_metrics(enterprise_code) 物化管道 = ① 加载+校验指标注册表（M1-M7）→ ② 逐指标 CREATE OR REPLACE TABLE metric_<id> AS SELECT ... GROUP BY dims（sqlite_scan 直读源库，见 §1.6 SQL 形态）→ ③ 写 metric_meta（含 data_version/config_sha256/row_count）→ ④ reconcile 全检（§2.3）→ ⑤ 全绿才提交版本戳；
- **幂等**：CREATE OR REPLACE 天然幂等；同输入重跑产出逐位相同（确定性，对齐 manifest SHA256 语义）；任一指标失败 → 整批不提交新版本戳，查询侧仍读旧物化（fail-closed，不半新半旧）。

**（2）增量刷新：预留契约、S2 不实现**

- 触发条件 = 写回开放（S3）：MSEG/ACDOCA 等流水运行期追加后，全量重建成本随流水增长，需增量（按数据版本水位线 INSERT 增量 + 重算受影响维度组合）；
- 本期只定义契约不实现：refresh_mode ∈ {full, incremental}，S2 固定 full，S3 接写回时启用 incremental；
- **不造轮子声明**：增量刷新属成熟数仓范式，届时评估 dbt incremental / DuckDB 增量物化等成熟能力，不自研状态机（议题清单 §0.5 铁律）。

**（3）刷新触发时机（三档）**

| 档 | 触发 | 说明 |
|---|---|---|
| T1 构建管道 | DES generate → materialize → refresh_metrics 一条命令串行 | 保证「数据一变，物化必新」；CLI 形态 python -m src.des --enterprise <code> --refresh-metrics |
| T2 显式 CLI | 独立手动/定时触发 refresh | 运维/演示用 |
| T3 查询侧守卫 | 契约执行器每次读 metrics.db 前校验 metric_meta.data_version == manifest.data_version | **C4 一致性的机器断言点**：不一致 → 拒答并报「数据版本漂移，请刷新」/ 自动触发（默认自动，配置开关） |

**（4）物化版本标识**

- metric_meta 的 data_version/config_sha256 **同源于 manifest.json**（单一事实来源，P1b-1 / config_sha256 逐位一致）；源数据一变（重新生成 → manifest 变化）→ 物化版本戳即失效 → T3 守卫拦截；
- 双库（SQLite 源 / DuckDB 物化）漂移 = 机器可检（版本比对），不靠人工判断。

### 2.3 reconcile 测试口径（物化 vs 源库直算 diff=0）

**定义**：对每个指标，物化表 metric_<id> 与「直接对源 SQLite（经 sqlite_scan 或 sqlite3 直连）跑同一 GROUP BY 聚合」的结果，**按维度键排序逐行比对，维度值 + 度量值精确相等，行数一致 = diff=0**。物化 SQL 与 reconcile SQL **同源同一个 definition/transform**（口径单点，防双轨漂移）。

**输出**：ReconcileResult（对齐 contract.py reconcile_dq01 形态）：ok / expected_count / actual_count / differences[]。

**机器断言（门禁）**：

| # | 断言 | 判定 |
|---|---|---|
| R1 | 每指标 reconcile ok（15 条全绿） | 物化 vs 源库直算 diff=0 |
| R2 | 跨指标自洽：C3（流水净变） vs C1（账面）按地点 diff=0 | 复用 D10 对账口径，从「源库直算对账」升级为「物化层对账」 |
| R3 | 版本守卫：改 manifest.data_version（模拟源变更）→ T3 检测漂移 → 拒答/提示（fail-closed） | C4 一致性 |
| R4 | 幂等：连续两次 refresh，metrics.db 全表 SHA256 相同 | 全量重建幂等 |

**测试定位**：tests/test_des_p2_metrics.py（增量测试，秒级；遵守铁律①：子代理不跑全量 pytest，用小规模 scale=0.003 数据集验证确定性断言，量级门禁用全量只读）。

### 2.4 预聚合 vs 动态派生边界

延续议题清单 §3.5.5-1（Palantir 官方区分 pre-computed vs dynamically derived，<~1 万对象/查询才用动态派生），定三条**语义优先**决策规则（阈值仅作经验锚，不硬编码）：

| 规则 | 内容 | 判定（可机验） |
|---|---|---|
| ① 指标一律预聚合 | **凡 metric 注册表内定义的指标 → 命中物化表，绝不裸表现场算** | metric_id ∈ 注册表 → 预聚合 |
| ② 对象级读侧动态派生 | 实体查询/细粒度过滤/≤1 跳链接（现有 contract v0.1 执行器 + DuckDB 内存物化）保持动态；当前 Material 8,000 < ~1 万，在动态派生适用域内 | 无聚合/无指标引用 → 动态派生 |
| ③ 冷指标先查后物化 | 不在注册表、低频、临时维度组合 → 动态直算（DuckDB sqlite_scan）兜底；若 P95 超阈值或高频化 → 升级为注册指标（走预聚合） | 命中率/延迟触发升级 |

> 边界 = 「指标 vs 对象」的语义分界，不是纯行数阈值：**聚合型读侧归预聚合，实体型读侧归动态派生**；<~1 万对象只是 Palantir 同源的经验参考值。

### 2.5 P2 对标基线（预聚合价值量化，诚实口径）

**初始锚（设计输入）**：议题清单 §3.5-5 SQLite 实测「100 万行 TOP10 聚合 2.3s」→ P1b 设计 §6.2 Q2（无预聚合大聚合 401k 行）阈值 ≤2000ms → 原定基线「~2s → 预聚合 ≤100ms」。

**P1b 实测修正（2026-08-21，必须如实引用）**：P1b 完成记录 §三——DuckDB sqlite_scan 无预聚合 Q2 实测 **P95 = 98ms**（远快于 2s 预估），且完成记录 §六 明确「**P2 预聚合对标基线需重定义（建议加更重聚合形态，如多列 GROUP BY + 大 DISTINCT）**」。

**因此 P2 基线设计为「绝对 + 相对」双目标 + 更重聚合形态**：

| 目标 | 判定 | 适用 |
|---|---|---|
| 绝对：物化指标查询 P95 ≤ **100ms** | 任意维度过滤命中物化表 | 全部 15 指标 |
| 相对：物化 vs 动态直算加速比 ≥ **10×** | 同问题同数据集（预热 1 次 + 重复 ≥10 次取 P95，对齐 P1b §6.1 测量方法） | **4 个「更重聚合」指标：B1 / C2 / D2 / D3**（B1/D2 物料×月 ≈9.6 万分组键、C2 三列 GROUP BY、D3 count_distinct 大 DISTINCT，动态直算可达几百 ms~2s 级） |
| 诚实兜底 | 若某指标动态直算已 <50ms（如 A1/A3 小基数）→ **如实报告「差距小、非瓶颈」**，不夸大 | 其余 11 个只测 reconcile（R1）不测延迟 |

**可选项（风险对策，非主门禁）**：scale 放大档（如 10× → 1000 万行）验证预聚合优势随量级扩大；超量级不设为主门禁（对齐 C1「100 万行级」定论与 Jack「超量级反而不利演示/传播」拍板）。

**门禁判定**：物化 P95 ≤ 100ms ∧ 4 个重聚合指标（B1/C2/D2/D3）加速比 ≥ 10× → 通过；否则走降级路径（缩小聚合形态/如实报告量级缺口，兑现 P1b §6.3 诚实口径）。测试落 tests/test_des_p2_scale.py（对齐 P1b 量级门禁形态，硬件基线 = 本机 ≥8GB RAM）。

### 2.6 与现有物化/契约代码的衔接（复用点清单）

| 现有模块 | 复用点 | 本设计用法 |
|---|---|---|
| materialize.py | DuckDB sqlite_scan 跨 5 库直读 + 库路径参数化 + rows_as_dicts + MaterializeError fail-fast | 物化管道直接复用（§2.2 物化 SQL 的库路径/join 模式） |
| contract.py | AGG_FUNCS 枚举、validate_contract fail-closed 模式、reconcile_dq01 的 ReconcileResult 形态 | 指标校验（M1-M7）与 reconcile（R1）对齐同一纪律与形态 |
| config.py | 表注册表（systems[].tables[]）、data_version/config_sha256 | M2 来源表白名单 + §2.2 版本守卫的数据源 |
| manifest.json | tables.{system}.{table}.sha256 / total_rows / data_version | 版本标识 + 源数据变更检测（T3） |
| （新增）metrics.db | 持久化 DuckDB 文件（duckdb.connect(path)） | 指标物化层（不复用 SQLite materialized.db——那是对象物化，这是指标物化，语义分层） |

---

## 附：本轮风险与待确认项

| # | 项 | 类型 | 说明 / 建议 |
|---|---|---|---|
| R1 | P2 基线重定义 | 已处理 | P1b 实测 Q2=98ms 快于预估 → 已按「绝对 ≤100ms + 相对 ≥10×（更重聚合 4 指标）」重定义（§2.5），待 P2 实测校准 |
| R2 | 4 个新主体对象注册量 | 中 | Customer/Vendor/InventoryLocation/FinanceEntry 需按 P1a 范式补注册（对象 schema + 物化 SQL + Registry）；建议先注册 1 个（Customer）验证再批量，避免重复 P1b R2 教训 |
| R3 | 指标 definition 双源漂移 | 中 | 物化 SQL 与 reconcile SQL 必须同源同 definition/transform（§2.3），实现时用「注册表 → 派生 SQL」单点生成，禁两处手写 |
| R4 | 增量刷新 | 预留 | S2 全量重建 + 版本守卫已覆盖 C4；增量（写回后流水追加）留 S3，届时评估成熟增量物化，不造轮子 |
| R5 | 指标语义面 vs 30 问实验集 | 待下篇 | 15 指标的语义面是 head-to-head 30 问的候选底座，但 30 问问题集与契约 v0.2 形态留下篇定义，本篇指标清单可能按实验需要增补（新增指标=注册表加一条，成本低） |
| R6 | 月份基数 | 待实测 | 维度「月」上界按 ≤12 估（单年数据）；若 DES 生成年份分布更宽，物化行数上界随之放大，仍 < 50MB 量级，不构成风险 |

---

## 附：本设计对「研究对象锚定」的回答

这份指标模型 + 物化设计不为造指标而造指标：它把 ChatBI 读侧从「LLM 轮询 50 条数据」（ChatBI 方向文档，真实量级不可行）升级为「**对象→指标→物化结果**」的语义接口链路——本体对象是语义入口（选对象/选指标），DuckDB 预聚合是执行落点（空间换时间），C4 流转契约 + reconcile 是双引擎一致性的机器保证。这正是议题 1 形态 v2 的落地：**本体不取代数仓，是把数仓成果（物化指标）加语义外壳**；「对象<~1 万动态派生、指标走预聚合」的边界划分，对齐 Palantir pre-computed vs dynamically-derived 的成熟范式，OntoRun 只做差异化的「本体↔物化指标」映射层。契约 v0.2 与 head-to-head 实验设计在下一版（下篇）补充，本上篇为它们提供了已落定的指标语义面与物化数据面。
