# P1a DES 配置与表结构设计 v0.1

> 编制：数据角色（DES 设计）｜ 日期：2026-08-21 ｜ 状态：已验收（2026-08-21 Jack）
> 关联：docs/DES-最小垂直切片规划_v0.1草案.md（§2/§6/§7）、research/DES-行业标准参考.md（SAP 命名锚）、data/seed_retail_source.py（S1 确定性手法）、docs/S2-开发计划_v0.3 阶段 P1a、docs/S2-P0-执行记录.md §五 P1a 门禁
> 产出：本文档（单文件 md）；按约束不另建 yaml / 代码文件，下述 YAML 与伪代码为设计规格，由 P1a 编码活落地
> 目标：把 P1a DES 垂直切片的 **配置、表结构、一物多码注入、确定性、可机验口径** 五大设计一次讲清，供 Jack 业务验收后即开工

---

## 0. 一句话设计

**1 个行业模板（YAML 默认层）+ 1 个企业覆盖（YAML 覆盖层）→ 确定性生成 1 个制造业样例企业 3 个源系统（ERP/MES/WMS）各 1 张物料主数据表 → 注入 15%（±2%）一物多码 → 同 seed 同配置 SHA256 可复现、全部门禁可机验。**

设计锚点（对齐规划 §2/§6/§7 与 P1a 门禁）：
- R1：1 企业 = 1 目录，N 系统 = N SQLite 文件（erp.db/mes.db/wms.db）；
- R2：配置先做 2 层（行业模板 + 企业覆盖），YAML anchor/alias，不造 DSL；
- 编码规则：`MAT-YYYY-NNNN-CCC`（100% 可机验）；
- 一物多码：MARA 15% 记录带 BISMT 旧码（注入率 ±2%）；
- 确定性：同 seed 同配置 → 表 dump SHA256 相同（沿用 S1：SEED 固定 + 确定性生成）。

---

## 1. YAML 2 层配置设计

### 1.1 分层与职责

| 层 | 文件 | 职责 | 变更频率 |
|---|---|---|---|
| L1 行业模板（默认层） | `data/des/des_industry_template.yaml` | 制造业通用默认：编码规则、注入策略（字段/率/容差/旧码格式）、存储布局、seed 政策、物料规模默认 | 行业级，一般不改 |
| L2 企业覆盖（覆盖层） | `data/des/enterprises/<enterprise_code>/des_enterprise.yaml` | 单个企业：企业名/编码前缀/seed、声明该系统有哪些系统（db/表/行数）、注入率覆盖 | 每建一家企业新建/改 |

### 1.2 继承机制：加载器深度合并（非 DSL）

- **层间继承** = 加载器 `deep_merge(template, enterprise)`：标量用企业值覆盖、映射递归合并、列表整体替换（默认）；企业未写项自动继承模板默认。
- **文件内复用** = YAML anchor/alias：`&anchor` 定义、`*anchor` 引用、`<<: *anchor` 合并键，避免复制粘贴。
- 技术说明（诚实口径）：YAML 的 anchor/alias 是**文件作用域**，跨文件"继承"由加载器的深度合并完成——这是 dbt / Helm / Spring profiles 同款的分层配置标准做法，**不是 DSL**。
- 禁做清单（防 DSL 漂移，对齐 R2 复核）：不引入 Jinja / 自定义 `$ref` / `${}` 插值 / 多级 L0–L3 继承；合并后做配置校验（rate ∈ [0,1]、tolerance>0、field 存在），失败即 fail-fast 报错，不静默。

### 1.3 制造业样例企业完整配置

**模板文件 `des_industry_template.yaml`**：

```yaml
# des_industry_template.yaml —— 制造业行业模板（默认层，行业级共用，一般不改）
industry: manufacturing
template_version: "0.1"

# —— 默认锚：企业文件经加载器深度合并继承；本文件内 anchor/alias 消重 ——
coding: &coding
  master_pattern: "MAT-{YYYY}-{NNNN}-{CCC}"    # 新主码（ERP MATNR 格式），机验锚点
  year: 2026

injection: &injection
  multi_code:
    field: BISMT            # 旧码承载字段（ERP MARA.BISMT）
    rate: 0.15              # 一物多码注入率目标（默认 15%）
    tolerance: 0.02         # 注入率机验容差（±2%）
    legacy_pattern: "{prefix}-{year}{seq:05d}"   # 旧码格式，如 HC-202600007

storage:
  layout: "one_enterprise_one_dir"   # 1 企业=1 目录，N 系统=N SQLite 文件（见 §5）

seed_policy: fixed                   # 确定性锚：固定 seed（沿用 S1：SEED 固定 + 确定性生成）
material_count_default: 200
```

**企业覆盖文件 `des_enterprise.yaml`**（华成精密制造样例，完整）：

```yaml
# data/des/enterprises/hc_precision/des_enterprise.yaml —— 制造业样例企业覆盖层
# 继承：加载器 deep_merge(des_industry_template.yaml, 本文件)；
#       本文件只写"要声明/要改"的，coding/injection 默认/storage/seed_policy 自动继承模板。
# 本文件内用 YAML anchor/alias（& 定义、* 引用、<<: 合并）复用三系统共享结构，不复制粘贴。
inherit: des_industry_template.yaml

# —— 三系统共享覆盖：定义一次，三处 <<: 继承（anchor/alias 消重）——
system_common: &system_common
  material_count: 200       # 同一物料宇宙（由 MARA 行数驱动），三系统 1:1:1 对齐
  row_count: 200

enterprise:
  name: "华成精密制造（HuaCheng Precision Manufacturing）"
  code_prefix: "HC"         # 企业编码前缀 → 目录名 hc_precision、旧码前缀 HC-
  seed: 20260821            # 生成 seed（确定性锚：同 seed 同配置 → SHA256 相同，见 §4）

  systems:
    erp:                    # ERP 源系统，1 张物料主数据表（对齐 SAP MARA）
      <<: *system_common
      db: erp.db
      table: MARA
    mes:                    # MES 源系统，1 张生产侧物料主数据表（含批次/工艺）
      <<: *system_common
      db: mes.db
      table: MPLA
    wms:                    # WMS 源系统，1 张仓储侧物料主档（含库位/计量单位）
      <<: *system_common
      db: wms.db
      table: WMMD

  injection:
    multi_code:
      rate: 0.15            # 覆盖/确认模板默认：一物多码注入率 15%
      legacy_prefix: "HC"   # 旧码前缀（合并后旧码格式 = "HC-{year}{seq:05d}"）
```

**合并后生效值（给 Jack 看的等价视图）**：

| 项 | 生效值 |
|---|---|
| 企业 | 华成精密制造（HC）｜ seed=20260821 |
| 编码规则 | `MAT-2026-NNNN-CCC`（新主码） |
| 一物多码 | field=BISMT，率 15%（±2%），旧码 `HC-{year}{seq:05d}` |
| 系统 | ERP→`erp.db`/MARA(200) ｜ MES→`mes.db`/MPLA(200) ｜ WMS→`wms.db`/WMMD(200) |
| 存储 | one_enterprise_one_dir → `data/des/hc_precision/` |

---

## 2. 三张表结构（每系统 1 张物料主数据表）

命名对齐 SAP 锚（research/DES-行业标准参考.md：MARA 物料主数据等公开数据字典）；切片每系统只取与"一物多码/跨系统映射"叙事相关的最小字段集，横向铺开（P1b）再扩工厂/库存/批次明细等表。

### 2.1 ERP：`MARA` 物料主数据（对齐 SAP MARA）

| 字段 | 类型 | 中文释义 | 主/外键 | 编码规则 / 取值 |
|---|---|---|---|---|
| MATNR | TEXT | 物料号（新主码） | PK | `MAT-YYYY-NNNN-CCC`，100% 机验（§3.2/§6-A） |
| MAKTX | TEXT | 物料描述（中文名） | | 自由文本非空；示例「铝合金外壳 A 型」 |
| MTART | TEXT | 物料类型 | | 枚举（SAP 标准）：FERT 成品 / HALB 半成品 / ROH 原材料 / VERP 包装 / HAWA 贸易商品 |
| BISMT | TEXT NULL | 行业物料号（旧码） | | 仅注入行非空，格式 `HC-{year}{seq:05d}`；**必不等于 MATNR**（多码冲突点） |
| MEINS | TEXT | 基本计量单位 | | PC / EA / KG / M / 箱…；与 WMS.MEINS 一致性校验（§6-D3） |
| MATKL | TEXT | 物料组 | | 可按类型派生，如 `Z-FERT-01` |
| ERDAT | TEXT | 创建日期 | | YYYY-MM-DD，seed 确定性生成 |

> 注：SAP 真实 MARA 有数百字段；切片刻意只取 7 个与叙事相关的字段（MAKTX 在真实 SAP 属 MAKT 表，切片简化并表，P1b 拆表时还原——已在技术债登记）。

### 2.2 MES：`MPLA` 生产侧物料主数据（切片命名）

| 字段 | 类型 | 中文释义 | 主/外键 | 编码规则 / 取值 |
|---|---|---|---|---|
| MPLA_ID | TEXT | 生产物料主数据 ID | PK | `MP-<MATNR>`（直接编码关联 ERP 主码，跨系统口径自证） |
| MATNR | TEXT | 物料号 | FK → MARA.MATNR | = 同一物料在 ERP 的主码 |
| CHARG | TEXT | 生产批次号 | | `L+YYYYMMDD+NNN`，seed 确定性生成 |
| WERKS | TEXT | 工厂 | | 示例 `PL01` |
| ARBPL | TEXT | 工作中心 | | 示例 `WC-ASSY-01` |
| VERID | TEXT | 生产版本 | | 示例 `01` |
| DISPO | TEXT | MRP 控制者 | | 示例 `MRP-01` |

### 2.3 WMS：`WMMD` 仓储侧物料主档（切片命名）

| 字段 | 类型 | 中文释义 | 主/外键 | 编码规则 / 取值 |
|---|---|---|---|---|
| MATNR | TEXT | 物料号 | PK 且 FK → MARA.MATNR | **仓储侧不发明自己的编码，直接以 ERP 主码为主键**（真实 WMS 消费 ERP 物料主档的集成口径） |
| LGORT | TEXT | 库存地点 | | 示例 `W01` |
| LGPBE | TEXT | 库位（存储仓格） | | `库区-排-列-层`，示例 `A-01-03-12` |
| MEINS | TEXT | 计量单位 | | 与 MARA.MEINS 一致（§6-D3） |
| BESTQ | TEXT | 库存类别 | | 枚举：非限制 / 质检 / 冻结 |
| ERDAT | TEXT | 建立日期 | | YYYY-MM-DD，seed 确定性生成 |

---

## 3. 一物多码注入设计

### 3.1 语义（数据侧口径）

- **一物多码** = 同一物理物料在旧系统（历史遗留）用**旧码 BISMT** 称呼、在新系统（ERP/MES/WMS）用**新主码 MATNR** 称呼，两个编码并存于企业数据中——需求说明书首个问题 DQ-01 的数据载体。
- 注入位置：仅 **ERP.MARA** 的 15% 记录带 BISMT 旧码；MES/WMS 表不带旧码（它们按新码作业）。
- 本体侧（架构子代理文档 P1a-本体映射与查询契约）把 MATNR、BISMT 映射到**同一物料实体**（hasCode 多值）；本文档只保证数据侧两种码都落库、口径一致、可被机器枚举。

### 3.2 主编码规则 `MAT-YYYY-NNNN-CCC`（100% 可机验）

- 结构：`MAT-`（固定前缀）｜ `YYYY`（生成年份，配置 `coding.year`）｜ `NNNN`（企业物料宇宙内 0001 起 4 位顺序号，唯一）｜ `CCC`（3 位校验码）。
- 校验码算法（确定性、跨语言可重算，已用 JS/Python 双端验证一致）：

```
字符表 CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"   # 32 字符，剔除易混 0/O/1/I
n    = YYYY * 10000 + NNNN
r0   = (n * 2654435761) & 0xFFFFFFFF                 # 32 位乘法散列（Knuth 乘法）
CCC  = CHARS[r0 % 32] + CHARS[(r0 >> 5) % 32] + CHARS[(r0 >> 10) % 32]
```

- 真实示例（seed 无关，纯规则）：`MAT-2026-0001-K4V`、`MAT-2026-0002-4JT`、`MAT-2026-0003-MXR`、`MAT-2026-0004-6DQ`、`MAT-2026-0005-PSN`。
- 机验方式：读 MATNR 解析出 YYYY/NNNN → 重算 CCC → 相等（§6-A2）。

### 3.3 注入率 ±2% 的确定性保证

| 环节 | 规则 |
|---|---|
| 目标数量 | `count = round(material_count × rate)` → 200 × 15% = **精确 30 行**，注入率 = 30/200 = **15.00%**（容差内精确命中） |
| 选择方式 | 物料宇宙按 MATNR 升序稳定排序后，用单 seed 的 `rng.sample(排序后清单, count)` 选出注入行集 |
| 容差语义 | 门禁断言 `|实际注入率 − 配置率| ≤ tolerance(0.02)`；当 count 非整数时才落到容差边缘（N=200 不触发） |
| 确定性 | 同 seed → 注入行集固定（可精确枚举），两次生成逐一相等（§6-B3） |

### 3.4 同一物料在 3 系统间编码一致的关联口径

1. **唯一主码 = MATNR**：MES.MPLA.MATNR 与 WMS.WMMD.MATNR 全部 = 对应 MARA.MATNR（FK / 同值），保证跨系统 join 干净；WMMD 直接以 MATNR 为主键（§2.3）。
2. **格式互斥**：旧码 `HC-{year}{seq:05d}` 与主码 `MAT-YYYY-NNNN-CCC` 正则不重叠 → 机器可区分"这条是旧码"，多码冲突可断言（§6-A4）。
3. **冲突语义留待本体层**：数据侧保证 30 个被注入物料"既有 MATNR 又有 BISMT"，3 码（PLM/ERP/MES 视角）→ 1 概念的本体映射由架构子代理文档承接，本表结构提供字段落点。
4. **机验锚点**：MES/WMS 无孤儿 MATNR；WMMD.MEINS=MARA.MEINS；三表行数 1:1:1（§6-D）。

---

## 4. 确定性约定（同 seed 同配置 → SHA256 相同）

沿用 S1 手法（`seed_retail_source.py`：SEED 固定 + 确定性生成），约定四条：

| # | 约定 | 落地规则 |
|---|---|---|
| 1 | 单一 seed 源 | 生成器入口 = `random.Random(企业配置 seed)`（本例 20260821），三系统共用；**不取** 系统时间 / 环境变量 / 操作系统随机源 / UUID |
| 2 | 稳定排序 | 所有集合迭代先排序：物料宇宙按 MATNR 升序、描述词库按字典序、注入用 `rng.sample(稳定排序清单, count)`；**不依赖 dict 无序**（即使 Python 3.7+ dict 保序也显式排序，跨版本稳定） |
| 3 | 纯函数派生 | 批次号 / 库位 / 旧码 / 校验码 / 日期全部为（seed 随机 + 固定模式）的纯函数，无累积可变全局状态 |
| 4 | 配置规范化 | SHA256 的输入 = 规范化配置 + seed：配置先按 key 排序序列化为 canonical JSON/YAML 再拼 seed，避免 dict 顺序影响 hash |

**SHA256 校验对象（机验锚点，落 manifest.json）**：
- `config_sha256 = SHA256(canonical(配置) ∥ "::" ∥ seed)`
- `table_sha256 = SHA256(按 MATNR 排序的该表全行 dump)`（erp.MARA / mes.MPLA / wms.WMMD 各一份）

---

## 5. 目录 / 存储（1 企业 = 1 目录，N 系统 = N SQLite 文件）

### 5.1 目录布局（设计）

```
data/des/
├── des_industry_template.yaml              # L1 行业模板（行业级共用）
└── enterprises/
    └── hc_precision/                       # L2 企业覆盖（1 企业 = 1 目录）
        ├── des_enterprise.yaml
        ├── erp.db                          # ERP 源系统库（表 MARA）
        ├── mes.db                          # MES 源系统库（表 MPLA）
        ├── wms.db                          # WMS 源系统库（表 WMMD）
        └── manifest.json                   # 生成清单：config_sha/seed/每表 sha/行数/注入率
```

### 5.2 理由（对齐 R1 复核 + System Silos 反模式）

1. **真实企业就是"系统竖井"**：ERP/MES/WMS 是独立系统，独立 schema、独立权限、独立运维、独立生命周期。把 N 个系统塞进 1 个库 = 抹掉真实的竖井边界 = **System Silos 反模式**；按系统分文件才保留"真实感"（规划 §7 R1 四模型共识，P0）。
2. **独立文件 = 独立事务/权限/加密/备份粒度**：erp.db 坏了只重建 ERP；各系统可单独加密、单独授予读权限，不互相牵连。
3. **语义层在"库之上"**：跨系统一致性**不靠**数据库外键（库与库之间本来没有 FK），靠本体映射 + 查询契约（DuckDB `sqlite_scan` 跨 3 库物化，已验证，规划 §6-3）——这正是"本体 = 语义层"主张的落点：**竖井的打通发生在语义层，而非数据层**。
4. **与 S1 先例一致**：`data/sources/retail_source.db` 已是单源库先例，切片只是"双库 → N 库"的扩展。
5. **可扩展**：加第 4 个系统 = 企业目录下加 1 个 `.db`，不动既有库。

### 5.3 manifest.json（可机验锚点）

```json
{
  "enterprise": "hc_precision",
  "seed": 20260821,
  "config_sha256": "...",
  "tables": {
    "erp.MARA": { "rows": 200, "sha256": "...", "multi_code_count": 30 },
    "mes.MPLA": { "rows": 200, "sha256": "..." },
    "wms.WMMD": { "rows": 200, "sha256": "..." }
  }
}
```

> 延续 S1 约定：`*.db` 不入 git（.gitignore），`des_enterprise.yaml` 与 `manifest.json` 入库（单一事实来源 = git + 文件）。

---

## 6. 可机验口径清单（门禁 → 检查项 → 断言 → 测试锚点）

把 P1a 门禁翻译成可断言的检查项；每条对应 S2 `tests/test_des_p1a_*.py` 的一个 pytest 用例（数据角色实现），兑现铁律②"规则必须能机器验证"。

### 门禁 A：编码 100% 合规

| # | 检查项（断言） |
|---|---|
| A1 | 全部 MATNR 匹配 `^MAT-\d{4}-\d{4}-[A-Z0-9]{3}$` |
| A2 | 逐行重算 CCC 与存储值相等（100%） |
| A3 | NNNN 在企业物料宇宙内无重复；YYYY = 配置 `coding.year` |
| A4 | 全部 BISMT 非空行：BISMT 不匹配主码正则（新旧码格式互斥）且 BISMT 互异；BISMT 非空行数 = 30 |

### 门禁 B：注入率 ±2%

| # | 检查项（断言） |
|---|---|
| B1 | `|count(BISMT IS NOT NULL) / N − 0.15| ≤ 0.02` |
| B2 | （更紧）`count(BISMT IS NOT NULL) == round(N × 0.15)` |
| B3 | 同 seed 两次生成：BISMT 非空行集（按 MATNR 排序）逐一相等 |
| B4 | 注入行每行至多一个旧码；无同时缺 MATNR 或缺 BISMT 的畸形行 |

### 门禁 C：确定性 SHA256

| # | 检查项（断言） |
|---|---|
| C1 | 同 seed 同配置两次生成 → erp/mes/wms 三表 `table_sha256` 逐一相同 |
| C2 | 改 seed → 三表 sha 全变；改配置（如 rate）→ sha 变（配置参与 hash） |
| C3 | 生成不依赖墙钟：两次运行时间不同，sha 仍相同 |
| C4 | `manifest.json` 记录值与实测重算一致（config_sha/table_sha/行数/注入计数） |

### 门禁 D：跨系统一致性（关联口径）

| # | 检查项（断言） |
|---|---|
| D1 | `SELECT COUNT(*) FROM WMMD w LEFT JOIN MARA m ON w.MATNR=m.MATNR WHERE m.MATNR IS NULL` = 0（无孤儿） |
| D2 | 同上，MPLA.MATNR 相对 MARA.MATNR 孤儿 = 0 |
| D3 | 同物料 WMMD.MEINS = MARA.MEINS（计量单位一致） |
| D4 | MPLA / WMMD 行数 = MARA 行数 = 200（1:1:1 宇宙对齐） |

> 门禁总口径 = A∪B∪C∪D 全绿 = P1a 编码侧验收（P1a 门禁 1/2，见 S2-P0 执行记录 §五）；本体映射（3 编码→1 实体）、DuckDB 物化可查、Jack 业务验收为其余门禁。

---

## 7. 风险与待确认项

| # | 项 | 类型 | 说明 / 建议 |
|---|---|---|---|
| R1 | 校验码 CCC 算法 | 待确认 | 现为 32 位乘法散列（跨语言已验证）。若 Jack 想让 CCC 语义化（如成品 FERT→前缀字符），改动只影响 §3.2 规则，保持"可重算"即可——请拍板是否接受现算法 |
| R2 | YAML 跨文件 anchor 限制 | 已决策 | anchor/alias 为文件作用域，跨文件"继承"以加载器深度合并实现（业界标准，非 DSL）。不引入 Helm 式嵌套 values，防 DSL 漂移（对齐 R2） |
| R3 | 注入率容差语义 | 已决策 | 切片 N=200 精确命中 15.00%；±2% 为门禁上界。P1b 横向铺开（100 万行）时须重验 B1（round 可能偏离，以 B1 为准） |
| R4 | WMMD 主键即 MATNR | 待定 | 切片 1 行/物料成立；P1b 如需多库位/多批次须扩为 `(MATNR, LGORT)` 复合键，切片不阻塞 |
| R5 | 企业样例命名 | 待确认 | 「华成精密制造 / HC」为占位提案；是否需要一个第二企业样例验证"同模板不同企业"复用性（建议 P1b 再加） |
| R6 | `*.db` 入库策略 | 待确认 | 建议延续 S1：`*.db` 入 .gitignore、config+manifest 入库；若 Jack 想保留样例库供下载可改 |

---

## 附：本设计对"研究对象锚定"的回答

这份表结构/配置不是为造数据而造数据：它服务"LLM 经语义接口操作真实系统"的叙事——**一物多码（DQ-01）正是真实企业里语义冲突的源头，本体语义层存在的意义就是把竖井系统（3 个独立库）的同一概念（物料）对齐**。数据侧把"竖井 + 多码"如实造出来（§5.2-1、§3.1），语义层才有得映射、有得查。
