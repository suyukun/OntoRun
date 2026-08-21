# P1b DES 横向铺开设计 v0.1

> 编制：数据角色（DES 设计）｜ 日期：2026-08-21 ｜ 状态：设计稿（待 Jack 验收）
> 关联：docs/S2-开发计划_v0.1草案.md（阶段 P1b 门禁）、docs/S2-议题清单_v0.1.md（§3.5 SQLite 实测）、docs/P1a-DES-配置与表结构设计_v0.1.md（P1a 基线）、docs/P1a-本体映射与查询契约设计_v0.1.md（Material/Code 契约）、research/DES-行业标准参考.md（SAP 命名锚）
> 产出：本文档（单文件 md，设计规格）；实现由 P1b 编码活落地，与 P1a 同一次验收范式
> 目标：把 P1b DES 横向铺开的 **表清单、行数分布、跨系统关系、确定性扩展、量级达标测试规格、对 P1a 兼容** 六大设计一次讲清，供 Jack 验收后即开工

---

## 0. 一句话设计

**在 P1a「1 企业 3 系统 3 表 200 行」骨架上横向铺开为「1 企业 5 系统 18 表 100 万行」：ERP/MES/WMS 保留并扩容，新增 SCM（采购）与 FIN（财务）两个源系统；物料主数据保持 P1a 编码格式扩容到 8,000 行，事务/流水表承载约 86% 的行数；同 seed 同配置 SHA256 全表可复现；5 个代表性查询（跨库 join/聚合/过滤/链路/对账）本机 P95+内存达标，为 P2 ChatBI 提供足够数据量并反哺预聚合设计。**

设计锚点（对齐 P1a 与 S2 计划 §P1b）：
- 量级口径：**总行数 = 1,000,000（精确 Σ配置值；±2% 为门禁容差上界）**，主数据 139,000 / 事务 861,000；
- 编码格式**不变**：物料主码 `MAT-YYYY-NNNN-CCC`（NNNN 4 位 → 物料宇宙上限 9,999，P1b 取 8,000，在界内）；
- 一物多码注入**保留**：仅 ERP.MARA 15%（8,000×15% = 精确 1,200 行，B2 精确命中）；
- 跨系统无孤儿口径**保留并扩展**：全 18 表所有外键 LEFT JOIN 空侧 = 0；并新增「库存账面=流水净变」自洽对账；
- 存储布局不变：1 企业 = 1 目录，N 系统 = N SQLite 文件（erp.db/mes.db/wms.db/scm.db/fin.db）；
- 确定性沿用 P1a 四约定并新增**约定 5（生成顺序固定）**，manifest.json 记录每表 SHA256 与 total_rows。

---

## 1. 范围与量级口径

### 1.1 系统与表规模

| 维度 | P1a | P1b | 说明 |
|---|---|---|---|
| 源系统 | ERP/MES/WMS（3 个） | **ERP/MES/WMS/SCM/FIN（5 个）** | 新增采购系统（scm.db，对齐「供应链/进销存」现实）与财务系统（fin.db，对齐「用友类财务 vs 生产 ERP」现实，见行业参考「财务系统可用用友类」） |
| 表数 | 3 | **18** | 范围 10-20 内 |
| 总行数 | 600 | **1,000,000** | 量级门禁目标 |

### 1.2 量级口径（可机验，三段式）

| 口径 | 目标 | 判定 |
|---|---|---|
| **总行数目标** | **1,000,000** | `Σ(每表 row_count) == 1,000,000`（配置校验 + 生成后实测比对，入 manifest.total_rows） |
| **主事务表行数** | **861,000（86.1%）** | 9 张事务/流水表合计（订单、工单、报工、库存流水、财务凭证） |
| **主数据表行数** | **139,000（13.9%）** | 9 张主数据表合计（物料、工厂、库存地点、BOM、客户、供应商） |

分布原则：**主数据小、事务数据大**（真实企业主数据通常占总量 5-20%，事务/流水占 80-95%）；单据比率（销售订单→项目 1:2.5、采购订单→项目 1:2.67、工单→报工 1:2、BOM→组件 1:5）符合制造企业业务比例。

> 量级与 §3.5 实测对齐：议题清单 §3.5（2026-08-21）实测「100 万行 + 5 万客户 = 123MB、插入 9.3s、等值 3ms、join 30ms、SUM 67ms、TOP10 聚合 2.3s」——P1b 的 100 万行正好落在该实测量级上（4 倍于 DES 目标 25 万行/季度），本机可跑、GitHub 下载生成可跑。

---

## 2. 表清单（18 表 · 5 系统）

命名对齐 SAP 锚（research/DES-行业标准参考.md §一）；COFV、ACDOCA 的少量自定义字段为「切片简化」处理（同 P1a 把 MAKT 并入 MARA 的处理，登记技术债）。字段取「最小但真实」——只保留叙事所需 + 主外键 + 聚合/过滤所需。

> 编码规则总表（前缀互斥、可机验，机器可区分单据类型，延续 P1a「新旧码格式互斥」原则）：

| 码 | 前缀 | 格式 | 承载表 |
|---|---|---|---|
| 物料主码 | MAT | `MAT-YYYY-NNNN-CCC`（NNNN 4 位） | 全部物料相关表 |
| 旧码 | HC | `HC-{year}{seq:05d}` | 仅 MARA.BISMT |
| BOM 号 | BO | `BO-YYYY-NNNNNN` | MAST/STPO |
| 采购订单 | PO | `PO-YYYY-NNNNNN` | EKKO/EKPO |
| 销售订单 | SO | `SO-YYYY-NNNNNN` | VBAK/VBAP |
| 生产工单 | WO | `WO-YYYY-NNNNNN` | AUFK/AFPO/COFV |
| 报工确认 | CF | `CF-YYYY-NNNNNN` | COFV |
| 物料凭证 | MV | `MV-YYYY-NNNNNN` | MSEG |
| 会计凭证 | FI | `FI-YYYY-NNNNNN` | ACDOCA |
| 客户号 | CU | `CU-00000001`（8 位） | KNA1 |
| 供应商号 | SU | `SU-00000001`（8 位） | LFA1 |

> YYYY = 配置 `coding.year`（2026）；NNNNNN 6 位支持单年 99.9 万行上限，覆盖本设计最大表（180,000 行）。多年度数据扩位留技术债。

### 2.1 ERP 系统（erp.db）—— 物料/工程/库存地点/销售（8 表）

**MARA 物料主数据** — 8,000 行 ｜ PK `MATNR`（延续 P1a，字段不变）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MATNR | TEXT | 物料号（主码 MAT-YYYY-NNNN-CCC） | PK |
| MAKTX | TEXT | 物料描述（中文名） | |
| MTART | TEXT | 物料类型（FERT/HALB/ROH/VERP/HAWA） | |
| BISMT | TEXT NULL | 行业物料号（旧码 HC-{year}{seq:05d}，一物多码注入 1,200 行） | |
| MEINS | TEXT | 基本计量单位 | 与 WMS/事务表一致 |
| MATKL | TEXT | 物料组 | |
| ERDAT | TEXT | 创建日期 | |

**MARC 物料工厂数据** — 16,000 行 ｜ PK `(MATNR, WERKS)`（8,000 物料 × 2 工厂）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MATNR | TEXT | 物料号 | PK / FK→MARA.MATNR |
| WERKS | TEXT | 工厂（PL01/PL02） | PK |
| MAABC | TEXT | ABC 分类（A/B/C） | |
| DISPO | TEXT | MRP 控制者 | |
| EKGRP | TEXT | 采购组 | |

**MARD 库存地点库存** — 24,000 行 ｜ PK `(MATNR, WERKS, LGORT)`（8,000 物料 × 3 地点）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MATNR | TEXT | 物料号 | PK / FK→MARA.MATNR |
| WERKS | TEXT | 工厂 | PK |
| LGORT | TEXT | 库存地点（W01/W02/W03） | PK |
| LABST | REAL | 不限制使用库存（账面值） | 与流水对账（§6 Q5） |
| INSME | REAL | 质检库存 | |
| SPEME | REAL | 冻结库存 | |

**MAST BOM 链接表** — 10,000 行 ｜ PK `(MATNR, WERKS, STLNR)`（部分成品/半成品有 BOM，可多版本）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MATNR | TEXT | 物料号（BOM 所属成品/半成品） | PK / FK→MARA.MATNR |
| WERKS | TEXT | 工厂 | PK |
| STLNR | TEXT | BOM 号（BO-2026-NNNNNN） | PK / FK→STPO.STLNR |
| STLAN | TEXT | BOM 用途（1=生产） | |

**STPO BOM 项目** — 50,000 行 ｜ PK `(STLNR, STLKN)`（10,000 BOM × 平均 5 组件）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| STLNR | TEXT | BOM 号 | PK / FK→MAST.STLNR |
| STLKN | TEXT | 项目号（00010 起 5 位） | PK |
| IDNRK | TEXT | 组件物料号 | FK→MARA.MATNR |
| MENGE | REAL | 组件数量 | |
| MEINS | TEXT | 组件单位 | |

**VBAK 销售订单抬头** — 40,000 行 ｜ PK `VBELN`

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| VBELN | TEXT | 销售订单号（SO-2026-NNNNNN） | PK |
| KUNNR | TEXT | 客户号 | FK→KNA1.KUNNR |
| AUDAT | TEXT | 单据日期 | |
| NETWR | REAL | 订单净额 | |
| VKORG | TEXT | 销售组织（1000） | |

**VBAP 销售订单项目** — 100,000 行 ｜ PK `(VBELN, POSNR)`（40,000 单 × 平均 2.5 项目）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| VBELN | TEXT | 销售订单号 | PK / FK→VBAK.VBELN |
| POSNR | TEXT | 项目号（000010 5 位） | PK |
| MATNR | TEXT | 物料号 | FK→MARA.MATNR |
| KWMENG | REAL | 订单数量 | |
| MEINS | TEXT | 单位 | |
| NETWR | REAL | 项目净额 | |

**KNA1 客户主数据** — 10,000 行 ｜ PK `KUNNR`

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| KUNNR | TEXT | 客户号（CU-00000001） | PK |
| NAME1 | TEXT | 客户名称 | |
| KTOKD | TEXT | 账户组 | |
| ORT01 | TEXT | 城市 | |

### 2.2 MES 系统（mes.db）—— 生产执行（4 表）

**MPLA 生产物料主数据** — 8,000 行 ｜ PK `MPLA_ID`（延续 P1a，字段不变，1:1 对齐 MARA）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MPLA_ID | TEXT | 生产物料主数据 ID（MP-<MATNR>） | PK |
| MATNR | TEXT | 物料号 | FK→MARA.MATNR |
| CHARG | TEXT | 生产批次号（L+YYYYMMDD+NNN） | |
| WERKS | TEXT | 工厂 | |
| ARBPL | TEXT | 工作中心 | |
| VERID | TEXT | 生产版本 | |
| DISPO | TEXT | MRP 控制者 | |

**AUFK 生产工单抬头** — 90,000 行 ｜ PK `AUFNR`

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| AUFNR | TEXT | 生产工单号（WO-2026-NNNNNN） | PK |
| MATNR | TEXT | 主产出物料 | FK→MARA.MATNR（简化并表，真实在 AFPO，同 P1a 并表处理） |
| AUART | TEXT | 工单类型（PPSM 生产） | |
| WERKS | TEXT | 工厂 | |
| FTRMS | TEXT | 计划开始日期 | |
| STATUS | TEXT | 工单状态（REL 下达/PCNF 部分确认/DLV 交付/CLSD 关闭） | 过滤查询载体 |

**AFPO 生产工单项目** — 120,000 行 ｜ PK `(AUFNR, POSNR)`（90,000 工单 × 平均 1.33 项目）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| AUFNR | TEXT | 生产工单号 | PK / FK→AUFK.AUFNR |
| POSNR | TEXT | 项目号 | PK |
| MATNR | TEXT | 物料（组件/产出） | FK→MARA.MATNR |
| GAMNG | REAL | 订单数量 | |
| MEINS | TEXT | 单位 | |

**COFV 报工确认流水** — 180,000 行 ｜ PK `CONFNR`（90,000 工单 × 平均 2 次报工；切片命名，合并 SAP COFV/AFVV 确认字段）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| CONFNR | TEXT | 报工确认号（CF-2026-NNNNNN） | PK |
| AUFNR | TEXT | 生产工单号 | FK→AUFK.AUFNR |
| MATNR | TEXT | 报工物料 | FK→MARA.MATNR |
| WERKS | TEXT | 工厂 | |
| ARBPL | TEXT | 工作中心 | |
| DATUM | TEXT | 报工日期 | |
| ISM01 | REAL | 报工产出数量 | 聚合载体 |
| ISMN1 | REAL | 实际工时（小时） | 聚合载体 |

### 2.3 WMS 系统（wms.db）—— 仓储（2 表）

**WMMD 仓储物料主档** — 8,000 行 ｜ PK `MATNR`（延续 P1a，字段不变，1:1 对齐 MARA）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MATNR | TEXT | 物料号 | PK / FK→MARA.MATNR |
| LGORT | TEXT | 库存地点 | |
| LGPBE | TEXT | 库位 | |
| MEINS | TEXT | 计量单位（=MARA.MEINS） | 一致性校验 |
| BESTQ | TEXT | 库存类别（非限制/质检/冻结） | |
| ERDAT | TEXT | 建立日期 | |

**MSEG 库存流水（物料凭证行项目）** — 180,000 行 ｜ PK `(MBLNR, ZEILE)`（最大流水表）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| MBLNR | TEXT | 物料凭证号（MV-2026-NNNNNN） | PK |
| ZEILE | TEXT | 行项目号（01..99） | PK |
| MATNR | TEXT | 物料号 | FK→MARA.MATNR |
| WERKS | TEXT | 工厂 | |
| LGORT | TEXT | 库存地点 | |
| BWART | TEXT | 移动类型（101 收货/201 发料/261 生产发料/301 移库） | |
| MENGE | REAL | 数量（带符号：入正/出负） | 与 MARD 对账 |
| MEINS | TEXT | 单位 | |
| BUDAT | TEXT | 过账日期 | |
| EBELN | TEXT NULL | 参考采购订单 | 可空 FK→EKKO.EBELN |
| AUFNR | TEXT NULL | 参考生产工单 | 可空 FK→AUFK.AUFNR |

### 2.4 SCM 系统（scm.db）—— 采购（3 表）

**LFA1 供应商主数据** — 5,000 行 ｜ PK `LIFNR`

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| LIFNR | TEXT | 供应商号（SU-00000001） | PK |
| NAME1 | TEXT | 供应商名称 | |
| ORT01 | TEXT | 城市 | |
| LAND1 | TEXT | 国家 | |

**EKKO 采购订单抬头** — 30,000 行 ｜ PK `EBELN`

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| EBELN | TEXT | 采购订单号（PO-2026-NNNNNN） | PK |
| LIFNR | TEXT | 供应商号 | FK→LFA1.LIFNR |
| BSART | TEXT | 采购订单类型（NB 标准） | |
| AEDAT | TEXT | 创建日期 | |

**EKPO 采购订单项目** — 80,000 行 ｜ PK `(EBELN, EBELP)`（30,000 单 × 平均 2.67 项目）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| EBELN | TEXT | 采购订单号 | PK / FK→EKKO.EBELN |
| EBELP | TEXT | 项目号（00010 5 位） | PK |
| MATNR | TEXT | 物料号 | FK→MARA.MATNR |
| MENGE | REAL | 采购数量 | |
| MEINS | TEXT | 单位 | |
| NETWR | REAL | 净价 | |

### 2.5 FIN 系统（fin.db）—— 财务（1 表）

**ACDOCA 财务日记账** — 41,000 行 ｜ PK `(BELNR, POSNR)`（S/4HANA 万能日记账的切片简化）

| 字段 | 类型 | 中文释义 | 主/外键 |
|---|---|---|---|
| BELNR | TEXT | 会计凭证号（FI-2026-NNNNNN） | PK |
| POSNR | TEXT | 行项目号 | PK |
| RACCT | TEXT | 科目 | |
| KOSTL | TEXT | 成本中心 | 聚合载体 |
| WSL | REAL | 金额（借正/贷负） | 聚合载体 |
| BUDAT | TEXT | 过账日期 | |
| REF_DOC | TEXT | 参考业务单据号 | FK→（VBELN/EBELN/MBLNR 之一） |
| REF_TYPE | TEXT | 参考单据类型（SO/PO/MV） | 决定 REF_DOC 归属 |

> ACDOCA 生成规则（确定性）：从 VBAP(100k)/EKPO(80k)/MSEG(180k) 按固定比例确定性抽样过账，每条抽样单据生成 1 行 ACDOCA；`REF_DOC` 必能 join 回对应源表主键（无孤儿）。41,000 = 抽样映射后的财务凭证量（财务凭证是「已过账子集」，小于业务单据总量，口径合理）。

---

## 3. 行数分布

### 3.1 分表行数（配置驱动，入 manifest）

| 系统 | 表 | 行数 | 类别 |
|---|---|---|---|
| ERP | MARA | 8,000 | 主数据 |
| ERP | MARC | 16,000 | 主数据 |
| ERP | MARD | 24,000 | 主数据 |
| ERP | MAST | 10,000 | 主数据 |
| ERP | STPO | 50,000 | 主数据 |
| ERP | VBAK | 40,000 | 事务 |
| ERP | VBAP | 100,000 | 事务 |
| ERP | KNA1 | 10,000 | 主数据 |
| MES | MPLA | 8,000 | 主数据 |
| MES | AUFK | 90,000 | 事务 |
| MES | AFPO | 120,000 | 事务 |
| MES | COFV | 180,000 | 事务 |
| WMS | WMMD | 8,000 | 主数据 |
| WMS | MSEG | 180,000 | 事务 |
| SCM | LFA1 | 5,000 | 主数据 |
| SCM | EKKO | 30,000 | 事务 |
| SCM | EKPO | 80,000 | 事务 |
| FIN | ACDOCA | 41,000 | 事务 |
| **合计** | **18 表** | **1,000,000** | — |

### 3.2 口径汇总

| 口径 | 值 | 占比 |
|---|---|---|
| 主数据表合计（9 表） | 139,000 | 13.9% |
| 主事务表合计（9 表） | 861,000 | 86.1% |
| **总行数** | **1,000,000** | 100% |

### 3.3 业务比率（分布符合真实企业比例）

| 比率 | P1b 值 | 真实企业量级参考 |
|---|---|---|
| 销售订单：项目 | 1 : 2.5（40k : 100k） | 1 : 2-4 |
| 采购订单：项目 | 1 : 2.67（30k : 80k） | 1 : 2-4 |
| 生产工单：报工 | 1 : 2（90k : 180k） | 1 : 2-5 |
| BOM：组件 | 1 : 5（10k : 50k） | 1 : 3-10 |
| 物料：工厂/地点 | 1 : 2 / 1 : 3（8k : 16k/24k） | 多工厂多地点 |
| 客户：订单 | 1 : 4（10k : 40k） | 年 3-6 单/客户 |
| 供应商：采购单 | 1 : 6（5k : 30k） | 年 5-10 单/供应商 |

---

## 4. 跨系统关系（join key 设计 + 无孤儿口径）

### 4.1 join key 层次

延续 P1a「**MATNR 主键 + 跨系统 join key = MATNR**」，扩展到新表关联键：

```
第 0 层（主键/编码）   MATNR  → 全部物料相关表（MARA/MARC/MARD/MAST/MPLA/WMMD/EKPO/VBAP/AUFK/AFPO/COFV/MSEG）
                       LIFNR  → LFA1（供应商主数据）
                       KUNNR  → KNA1（客户主数据）
第 1 层（单据内部）     EKKO.EBELN → EKPO.EBELN；VBAK.VBELN → VBAP.VBELN；AUFK.AUFNR → AFPO/COFV.AUFNR
第 2 层（跨系统引用）   MSEG.EBELN → EKKO.EBELN（采购收货）；MSEG.AUFNR → AUFK.AUFNR（生产发料）
                       ACDOCA.REF_DOC → VBELN/EBELN/MBLNR（财务过账追溯）
第 3 层（BOM）          MAST.STLNR → STPO.STLNR；STPO.IDNRK → MARA.MATNR
```

竖井打通仍发生在**语义层而非数据层**：库与库之间无外键（延续 P1a §5.2-3），join 由本体映射 + DuckDB `sqlite_scan` 完成——P1b 只是把「3 库」扩展为「5 库」。

### 4.2 跨系统无孤儿口径（D 门禁扩展：D1-Dn 全外键）

| # | FK | 断言（LEFT JOIN 空侧） |
|---|---|---|
| D1 | MPLA/WMMD.MATNR → MARA.MATNR | = 0（P1a 保留） |
| D2 | MARC/MARD/MAST.MATNR → MARA.MATNR | = 0 |
| D3 | STPO.IDNRK → MARA.MATNR；STPO.STLNR → MAST.STLNR | = 0 |
| D4 | EKKO.LIFNR → LFA1.LIFNR；EKPO.EBELN → EKKO.EBELN；EKPO.MATNR → MARA.MATNR | = 0 |
| D5 | VBAK.KUNNR → KNA1.KUNNR；VBAP.VBELN → VBAK.VBELN；VBAP.MATNR → MARA.MATNR | = 0 |
| D6 | AUFK.MATNR → MARA.MATNR；AFPO.AUFNR → AUFK.AUFNR；AFPO.MATNR → MARA.MATNR；COFV.AUFNR → AUFK.AUFNR | = 0 |
| D7 | MSEG.MATNR → MARA.MATNR；MSEG.EBELN 非空 → EKKO.EBELN；MSEG.AUFNR 非空 → AUFK.AUFNR | = 0（可空字段非空时成立） |
| D8 | ACDOCA.REF_DOC → 对应 REF_TYPE（SO/PO/MV）源表主键 | = 0 |
| D9 | WMMD.MEINS = MARA.MEINS（计量单位一致，P1a D3 保留） | 0 差异 |
| D10 | **对账自洽**：`Σ MSEG.MENGE（按 MATNR+LGORT）= MARD.LABST` | 0 差异（生成器保证，§6 Q5） |

> **无孤儿是 P1b 门禁而非默认**：真实企业有孤儿/断链，但那是「问题注入」的事（留后续问题阶段）；P1b 先保证 join 干净、确定性可验证，语义层才能可靠映射。D10 对账自洽 = 生成器先定 MARD 账面、再生成 MSEG 流水使得按地点净变 = 账面——「账面 = 流水」在数据里自洽，对账 diff=0 全量可断言（真实感 + 可机验双赢；「账面≠流水」的差异场景留问题注入）。

---

## 5. 确定性扩展（P1a 4 约定 → P1b 5 约定）

沿用 P1a §4 四约定，**原样保留并扩展**，新增约定 5：

| # | 约定 | P1a 规则 | P1b 扩展 |
|---|---|---|---|
| 1 | 单一 seed 源 | `random.Random(企业 seed)` 三系统共用 | **每表独立 RNG 流**：`random.Random(f"{seed}:{table_id}")`，table_id 固定（如 `erp.MARA`）；事务表行生成引用主数据表确定性输出（读内存/临时库），不重抽 |
| 2 | 稳定排序 | 物料宇宙按 MATNR 升序 | 泛化：所有集合按各自自然键排序（MATNR/EBELN/VBELN/AUFNR/MBLNR…）；事务表按主键升序落库 |
| 3 | 纯函数派生 | 批次/库位/旧码/校验码/日期纯函数 | 不变；数量/金额用 REAL（IEEE-754 双精度，固定 RNG + 固定运算 → 跨平台逐位确定） |
| 4 | 配置规范化 | canonical JSON ∥ seed → config_sha256 | 不变；**canonical 配置扩展为含全部表规格**（每表 row_count/kind/pk/depends_on/注入率），并新增 `data_version` 字段参与 hash |
| **5** | **生成顺序固定**（新增） | — | 生成器按表依赖拓扑序执行（§5.2），顺序固定保证跨系统引用确定、无不可复现的中间态 |

### 5.1 SHA256 泛化（manifest.json 扩展）

- `config_sha256 = SHA256(canonical(含全部表配置 + data_version) ∥ "::" ∥ seed)`（公式不变，输入扩展）；
- `table_sha256` = 每表**按主键排序**的全行 canonical dump 的 SHA256（P1a 按 MATNR，P1b 泛化为各表主键，如 MARC=(MATNR,WERKS)、EKPO=(EBELN,EBELP)）；
- manifest.json 扩展：

```json
{
  "enterprise": "hc_precision",
  "seed": 20260821,
  "data_version": "P1b-1",
  "config_sha256": "...",
  "total_rows": 1000000,
  "tables": {
    "erp.MARA":  { "rows": 8000,  "sha256": "...", "multi_code_count": 1200 },
    "erp.MARC":  { "rows": 16000, "sha256": "..." },
    "...":        { "...": "..." },
    "fin.ACDOCA": { "rows": 41000, "sha256": "..." }
  }
}
```

### 5.2 生成拓扑（约定 5 落地）

```
阶段 1 主数据（6 步，可并行表内确定性）：
  LFA1, KNA1 → MARA（含 15% 注入 1,200 行） → MARC, MARD → MAST → STPO → MPLA, WMMD
阶段 2 事务（依赖主数据与上级单据）：
  EKKO(依赖 LFA1) → EKPO(依赖 EKKO+MARA)
  VBAK(依赖 KNA1) → VBAP(依赖 VBAK+MARA)
  AUFK(依赖 MARA) → AFPO(依赖 AUFK+MARA) → COFV(依赖 AUFK+MARA)
  MSEG(依赖 MARA+EKKO+AUFK，且满足 D10 对账自洽)
  ACDOCA(依赖 VBAP/EKPO/MSEG 抽样映射)
```

MARA 注入：`round(8,000 × 0.15) = 1,200`（整数精确命中，B2 断言仍成立）；注入行集按 MATNR 升序 + `rng.sample`（约定 2/3）。

---

## 6. 量级达标测试规格（P1b 门禁）

门禁（S2 计划 §P1b）：「100 万行跑 5 个代表性查询（跨库 join/聚合/过滤/链路），P95+内存达标（本机可演示）」。以下为规格。

### 6.1 数据集口径

- 固定数据集 = 同 seed 同配置确定性生成的 **1,000,000 行**（18 表 5 库）；
- 测量方法：每查询**预热 1 次**后**重复 ≥10 次取 P95**（查询结果缓存无关——每次独立执行）；
- 硬件基线：**本机**（≥8 GB RAM，M 系或主流 x86 开发机）；内存以进程峰值 RSS 计（生成 + 查询全流程）；
- 实现：**DuckDB `sqlite_scan` 为主**（P1a materialize.py 已建立直读 5 库路径，不经 ETL；顺带作为 P2 物化基线）；对照/降级路径 = SQLite `ATTACH` 5 库（同一机 SQLite 可 ATTACH 多个 db 文件），供 DuckDB 不可得时兜底。

### 6.2 5 个代表性查询（SQL 形态 = 跨库视角，库路径参数化）

**Q1 · 跨库 join（采购链路明细）** —— 覆盖「跨库 join」

```sql
SELECT p.EBELN, p.EBELP, p.MATNR, m.MAKTX, l.NAME1 AS vendor_name, p.MENGE, p.NETWR
FROM   sqlite_scan('scm.db','EKPO') p
JOIN   sqlite_scan('scm.db','EKKO') h ON p.EBELN = h.EBELN
JOIN   sqlite_scan('erp.db','MARA') m ON p.MATNR = m.MATNR
JOIN   sqlite_scan('scm.db','LFA1') l ON h.LIFNR = l.LIFNR
WHERE  p.NETWR > 1000
ORDER BY p.NETWR DESC LIMIT 50;
```
数据集：80k EKPO × 30k EKKO × 8k MARA × 5k LFA1（跨 scm.db + erp.db）。**P95 ≤ 500 ms**。

**Q2 · 无预聚合大聚合（报工/库存/财务按月汇总）** —— 覆盖「聚合」（量级真相所在）

```sql
SELECT 'MES' AS sys, substr(DATUM,1,7) AS ym, SUM(ISM01) AS qty, SUM(ISMN1) AS hrs
FROM   sqlite_scan('mes.db','COFV') GROUP BY 1,2
UNION ALL
SELECT 'WMS', substr(BUDAT,1,7), SUM(MENGE), 0
FROM   sqlite_scan('wms.db','MSEG') GROUP BY 1,2
UNION ALL
SELECT 'FIN', substr(BUDAT,1,7), 0, SUM(WSL)
FROM   sqlite_scan('fin.db','ACDOCA') GROUP BY 1,2
ORDER BY sys, ym;
```
数据集：180k + 180k + 41k = **401k 行聚合**（本数据集无预聚合大聚合最坏情形，对齐 §3.5「TOP10 聚合 2.3s/100 万行」实测）。**P95 ≤ 2,000 ms**。

> 反哺 ChatBI 预聚合（议题 1）：Q2 的 2s 级 P95 即 P2 预聚合的**对标基线**——P2 用 DuckDB 物化月汇总后，同问题应 ≤100 ms（两个数量级差距），为「预聚合优先」提供量化证据。

**Q3 · 过滤 + TOP-N（成品销售 TOP20）** —— 覆盖「过滤」

```sql
SELECT m.MAKTX, v.MATNR, SUM(v.KWMENG) AS qty, SUM(v.NETWR) AS amount
FROM   sqlite_scan('erp.db','VBAP') v
JOIN   sqlite_scan('erp.db','MARA') m ON v.MATNR = m.MATNR
WHERE  m.MTART = 'FERT'
GROUP BY m.MAKTX, v.MATNR
ORDER BY amount DESC LIMIT 20;
```
数据集：100k VBAP × 8k MARA，过滤 FERT + 分组排序 TOP20。**P95 ≤ 800 ms**。

**Q4 · 链路追溯（物料 → BOM 组件 → 采购 → 收货 → 财务）** —— 覆盖「链路」（6 跳跨 4 库）

```sql
SELECT m.MATNR, stp.IDNRK AS comp_matnr, e.EBELN, s.MBLNR, a.BELNR AS fi_doc
FROM   sqlite_scan('erp.db','MARA') m
LEFT JOIN sqlite_scan('erp.db','MAST') mast ON mast.MATNR = m.MATNR
LEFT JOIN sqlite_scan('erp.db','STPO') stp ON stp.STLNR = mast.STLNR
LEFT JOIN sqlite_scan('scm.db','EKPO') e ON e.MATNR = stp.IDNRK
LEFT JOIN sqlite_scan('wms.db','MSEG') s ON s.MATNR = e.MATNR AND s.EBELN = e.EBELN
LEFT JOIN sqlite_scan('fin.db','ACDOCA') a ON a.REF_DOC = s.MBLNR
WHERE  m.MATNR = 'MAT-2026-0001-K4V';
```
数据集：8k+10k+50k+80k+180k+41k ≈ **369k join 面，6 跳跨 erp/scm/wms/fin 4 库**（ChatBI 跨系统追问的典型慢路径）。**P95 ≤ 3,000 ms**。

**Q5 · 库存对账（账面 MARD vs 流水 MSEG）** —— 覆盖「一致性/对账」

```sql
SELECT COALESCE(sd.LGORT, mv.LGORT) AS lgort,
       COALESCE(sd.labst, 0)    AS book_stock,
       COALESCE(mv.flow_qty, 0) AS flow_stock,
       COALESCE(sd.labst, 0) - COALESCE(mv.flow_qty, 0) AS diff
FROM (SELECT LGORT, SUM(LABST) AS labst FROM sqlite_scan('erp.db','MARD') GROUP BY LGORT) sd
FULL OUTER JOIN (SELECT LGORT, SUM(MENGE) AS flow_qty FROM sqlite_scan('wms.db','MSEG') GROUP BY LGORT) mv
  ON sd.LGORT = mv.LGORT
ORDER BY lgort;
```
数据集：24k MARD × 180k MSEG 按地点汇总对账（D10 自洽 → **diff=0 全量断言**）。**P95 ≤ 2,000 ms**。

### 6.3 阈值汇总（本机可演示为界）

| 查询 | 类别 | 扫描面 | P95 阈值 | 内存贡献 |
|---|---|---|---|---|
| Q1 | 跨库 join | 80k×30k×8k×5k | ≤ 500 ms | 中 |
| Q2 | 聚合（无预聚合） | 401k 行 | ≤ 2,000 ms | 高（GROUP BY 中间态） |
| Q3 | 过滤 + TOP-N | 100k×8k | ≤ 800 ms | 低 |
| Q4 | 链路（6 跳跨 4 库） | 369k join 面 | ≤ 3,000 ms | 高（join fan-out） |
| Q5 | 对账（一致性） | 24k×180k | ≤ 2,000 ms | 中 |

**内存阈值**：全流程（生成 + 5 查询）**峰值 RSS ≤ 1.5 GB**，常规查询 ≤ 800 MB（本机 ≥8 GB 无压力）。依据：§3.5 实测 100 万行仅 123 MB 磁盘；DuckDB 列存 + `sqlite_scan` 流式扫描，中间结果远低于 1.5 GB。
**附加操作上界**：全量生成 ≤ 3 分钟（实测 100 万行插入 9.3s）；5 源库 + 物化库磁盘合计 ≤ 300 MB。

> 若 P95 超阈值：先查是否可优化查询形态（缩小 join 面/加过滤）→ 再降级为「抽样集」（如 50 万行）并如实报告量级缺口，不静默通过（兑现量级门禁诚实口径）。

---

## 7. 对 P1a 的兼容（现有 3 表如何扩 + 生成器扩展点）

### 7.1 三张现有表

| 项 | P1a | P1b | 兼容判定 |
|---|---|---|---|
| MARA 字段 | 7 字段（MATNR/MAKTX/MTART/BISMT/MEINS/MATKL/ERDAT） | **不变（不删不改）** | 字段兼容 |
| MARA 行数 | 200 | **8,000** | 行数变（配置驱动）；SHA256 变属预期（P1a C2「改配置→sha 变」语义，非回归） |
| MPLA/WMMD | 200，1:1:1 与 MARA | **8,000，1:1:1 保留** | D4 语义保留（8,000=8,000=8,000） |
| 编码格式 | `MAT-YYYY-NNNN-CCC` | **不变** | 4 位 NNNN 上限 9,999，8,000 在界内；示例码 `MAT-2026-0001-K4V` 仍有效 |
| 一物多码注入 | 仅 MARA 15%（精确 30 行） | **保留，仅 MARA 15%（精确 1,200 行）** | `round(8,000×0.15)=1,200` 整数，B2 精确命中；B1 率±2% 主判据不变 |
| 确定性 4 约定 | 原样 | **原样保留 + 新增约定 5** | 约定 1-4 不削弱 |
| D 门禁 | D1-D4 | **D1-Dn 全外键 + D10 对账** | 保留并扩展 |

> 关键约束（兼容红线）：① MARA/MPLA/WMMD 字段不删不改（可加列）；② 4 条确定性约定原样保留；③ 无孤儿口径保留；④ seed 固定 20260821，数据版本用新增 `data_version` 显式化；⑤ 编码格式不变（物料宇宙 ≤9,999 由 NNNN 4 位决定，升级 NNNN→NNNNN 为独立 ADR，P1b 不做）。

### 7.2 生成器扩展点（P1a 代码结构 → P1b）

| 模块 | P1a 现状 | P1b 扩展 | 扩展点 |
|---|---|---|---|
| `config.py` | `_normalize` 固定 erp/mes/wms 各 1 表 | 泛化为 `systems[code].tables[]`（每表 kind/row_count/pk/depends_on） | 行数默认放模板层，企业层可覆盖；校验扩展（row_count 正整数、depends_on 引用存在、FK 字段声明、`Σ row_count == total_target`） |
| `generate.py` | 3 个硬编码生成函数（mara/mpla/wmmd） | 引入**表注册表驱动**：`TABLE_SPECS`（表 → DDL + 行生成器 + 依赖）；`build_enterprise` 按拓扑序遍历；每表独立 RNG | 新增表 = 注册表加一条（复制模式）；事务表生成器读主数据确定性输出 |
| `manifest.py` | `read_table_rows` 按 MATNR 排序 | 泛化排序键（按各表主键）；`build_manifest` 遍历全部表 + total_rows | 主键作为表规格一部分 |
| `materialize.py` | 3 库 join（MARA/MPLA/WMMD） | N 库 join（join key 常量表 + 库路径参数化） | P2 物化基线直接复用 |

### 7.3 对 P1a 测试的影响

- `tests/test_des_p1a_data.py`（16 绿）：断言数值从硬编码（200/30）改为配置驱动（`expected_count` / `expected_injected = round(N×rate)`），**断言语义不变**（A 编码 100%、B 注入率±2%、C 确定性 SHA256、D 无孤儿）；
- `tests/test_des_p1a_mapping.py`（15 绿）：物化锚点从 200/830 改为配置驱动；Material/Code 契约不变（P1b 只扩数据面，不新增码空间）；
- 新增 `tests/test_des_p1b_data.py`：行数口径（Σ=1,000,000）、全外键无孤儿（D1-D8）、对账自洽（D10）、B2 精确 1,200；
- 新增 `tests/test_des_p1b_scale.py`：量级门禁（§6 五查询 P95 + 峰值内存 + 全量生成耗时）。

---

## 8. 风险与待确认项

| # | 项 | 类型 | 说明 / 建议 |
|---|---|---|---|
| R1 | 物料宇宙 ≤9,999 上限（NNNN 4 位） | 已决策 | P1b 取 8,000 在界内；若未来需 >9,999 物料，升级 NNNN→NNNNN（5 位），涉及 A1 正则与示例码，作为独立 ADR/技术债，**P1b 不做** |
| R2 | 18 表 5 系统实现量 | 中风险 | 横向铺开 = 复制模式（master/transaction 两类模板），建议实现时先做 1 张事务表（如 EKPO）验证注册表模式，再批量复制；另 2 个新源系统（scm/fin）即企业目录加 2 个 .db，无结构改动 |
| R3 | 量级 P95 阈值为预估 | 中风险 | 基于 §3.5 实测校准（本机 1M 行 TOP10 聚合 2.3s），阈值给余量；**以实测报告为准**，超阈值走 §6.3 降级路径并如实报告 |
| R4 | ACDOCA 抽样过账规则 | 待确认 | 需明确确定性抽样口径（REF_DOC 无孤儿、41,000 行来源）；备选 = 独立凭证流（不引用业务单据），但会削弱链路/对账叙事，建议保留 REF 引用 |
| R5 | 财务系统独立建模（FIN 库） | 待确认 | 采用「财务=FIN 独立库」（对齐用友类财务 vs 生产 ERP 现实，行业参考 §二）vs 并入 ERP——建议接受独立库（增强竖井叙事），请 Jack 拍板 |
| R6 | 一物多码在业务单据的体现 | 待确认 | P1b 单据统一用 MATNR（延续 P1a「MES/WMS 按新码作业」语义）；「业务单据用旧码下单」作为后续问题注入（P1c/问题阶段）第二注入点，不入 P1b |
| R7 | 第二企业样例（P1a R5） | 待确认 | 建议 P1b 收尾或 P2 前做小规模（2-3 万行）验证「同模板不同企业」复用性，**不参与 1M 门禁**（避免稀释量级） |
| R8 | GitHub 可跑口径 | 已决策 | `*.db` 不入 git（延续 R6）；GitHub 传播 = 生成器 + 配置，本地确定性生成 1M 行；量级门禁验证「本机生成 + 查询」可跑 |
| R9 | 数量/金额用 REAL 的确定性 | 已决策 | IEEE-754 双精度 + 固定 RNG + 固定运算 → 跨平台逐位确定；canonical dump 用 repr（Python 确定） |

---

## 附：本设计对「研究对象锚定」的回答

这份横向铺开设计不为造数据而造数据：它把「竖井系统 + 一物多码」从 P1a 的 3 表放大到 **18 表 5 系统 100 万行**——物料/工单/库存/BOM/订单/客户/供应商/财务，竖井边界（5 个独立库）与概念对齐（MATNR join key + 无孤儿 + 对账自洽）如实造出来，本体语义层（Material/Code + 查询契约 v0.1）才有足够大、足够真实的语义冲突面去映射、去治理、去查。量级测试的 5 个代表性查询（跨库 join/聚合/过滤/链路/对账）正是 ChatBI 在本体上会跑的查询形态；其中「无预聚合大聚合 2s 级」的实测基线，直接反哺 P2 的「预聚合优先」设计——本体不取代数仓，是把数仓成果（物化指标）加语义外壳，这条主线在 100 万行上第一次有了量化证据。
