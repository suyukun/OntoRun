
# P1a 本体映射与查询契约设计 v0.1

> 编制：架构角色（本体论方向）｜ 日期：2026-08-21 ｜ 状态：已验收（2026-08-21 Jack）
> 关联：docs/P1a-DES-配置与表结构设计_v0.1.md（数据角色，本设计的字段落点与门禁锚）、docs/DES-最小垂直切片规划_v0.1草案.md（§2/§8）、research/s2-review-decision-pack.md（D3）、docs/S2-P0-执行记录.md §五 P1a 门禁、docs/S2-议题清单_v0.1.md §3.7（议题 2）
> 风格对齐：src/ontology/objects.py（Pydantic + own() 状态归属）、src/ontology/links.py（LinkTypeDef 双向链接）、src/ontology/registry.py（注册表 + self_check）；**不引入 RDFlib**
> 产出：本文档（单文件 md，设计规格）；实现由 P1a 编码活落地，与数据角色文档同一次验收（P1a 门禁 3/4/5）

---

## 0. 一句话设计

**1 个物料概念对象（Material）+ 1 个编码对象（Code）→ 用 hasCode 链接把 3 个源系统（erp/mes/wms）的编码映射成 1 个概念（join key = MATNR）；一物多码（DQ-01）= 同一概念同时有主码族（MATNR）与旧码族（BISMT，15% 注入），用一条可机验谓词判定；结构化查询契约 v0.1 用一条 JSON 表达「哪些物料一物多码？」并给 ground truth 标答与门禁。**

设计锚点（对齐数据角色 P1a 文档 §3/§6 与规划 §8）：
- **join key = MATNR**：erp.db(MARA) / mes.db(MPLA) / wms.db(WMMD) 三库按 MATNR 关联成 1 实体（MES/WMS 无孤儿，门禁 D1/D2）；
- **一物多码判定口径与 BISMT 字段口径一致**：BISMT 非空 ∧ ≠ MATNR ∧ 匹配旧码正则（门禁 A4/B 同源）；
- **契约 v0.1**：object_type / filters / aggregations / group_by / link_traversal（≤1 跳），LLM 产出、白名单校验 fail-closed、值参数化不拼 SQL；
- **D3 背景**：契约 v0.1 是 S2 垂直切片内 head-to-head 实验（受限结构化查询 vs NL2SQL+守卫，30 问）的输入，实验后再定终版。

---

## 1. 物料实体本体定义

### 1.1 设计总览：概念对象 + 编码对象 + hasCode 链接

一物多码问题（DQ-01）的本质是「**竖井系统里同一概念以不同编码出现**」：3 个独立源系统库（System Silos，数据角色文档 §5.2）各用自己的标识称呼同一物料。本体层的答案 = 建一个**概念对象 Material**（跨系统物化，join key = MATNR），把 3 个系统的编码作为其「多码」承载，再用 **hasCode 链接**显式声明「哪些编码 → 哪个物料概念」。

| 构件 | 表达 | 职责 |
|---|---|---|
| `Material`（物料概念） | Pydantic 对象，字段内嵌 4 个码位（plm_code / matnr / mes_code / old_code） | 查询与 join 的直接入口（去规范化，方便过滤/聚合） |
| `Code`（编码对象） | Pydantic 对象，code_space + value | 码空间的图表达：一码一对象，可扩展新码空间不动 schema |
| `material.codes`（hasCode 链接） | LinkTypeDef 风格，Material 1:N Code | 3 系统编码 → 1 物料概念的可遍历边（本体图） |
| 跨系统 join key | `MATNR`（三表同值） | 数据侧把 erp/mes/wms 三行组装成 1 个 Material 实体的锚 |

> 冗余是刻意的：Material 内嵌码位 = 查询便利（filters/聚合直接命中，不必每次遍历链接）；Code + hasCode = 本体图语义（编码归属可遍历、可审计、可扩码空间）。这正是 Palantir「对象属性（property）与关系（relation）并存」的做法——属性承载查询，关系承载语义。

### 1.2 Material 对象定义（Pydantic 规格）

风格对齐 `src/ontology/objects.py`：`BaseModel` + `own(ownership, description)` 状态归属标注（source-backed / ontology-owned / derived）。

~~~python
"""物料概念对象 —— DES 垂直切片：1 概念跨 3 源系统（ERP/MES/WMS），join key = MATNR。

状态归属三分类沿用 S1（src/ontology/objects.py）：
- source-backed：源系统权威（动作写回目标明确）；Material 是"跨系统物化"对象，
  其 source-backed 字段的权威列注明在 description（如 BISMT 权威在 ERP.MARA）。
- derived：由源列经 join/派生得到（计算态，永不写回）——Material 是物化快照，
  derived 字段 = 物化结果，不是源系统某列的直接搬运。
- ontology-owned：本体自有状态（本切片暂不引入，P1b 状态类字段再扩）。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from src.ontology.objects import own  # 复用 S1 的 own() 归属标注

MaterialType = Literal["FERT", "HALB", "ROH", "VERP", "HAWA"]  # 对齐 SAP MTART


class Material(BaseModel):
    """物料概念。PK/Title = matnr（ERP 编码，跨系统 join key）。"""

    matnr: str = own(
        OWN_SOURCE, "物料号（ERP 主码，PK/Title；跨系统 join key，erp/mes/wms 三表同值）"
    )
    name: str = own(OWN_SOURCE, "物料描述（权威列 ERP.MARA.MAKTX）")
    material_type: MaterialType = own(OWN_SOURCE, "物料类型（权威列 ERP.MARA.MTART）")
    plm_code: str = own(
        OWN_DERIVED, "PLM 编码（工程主数据签发的主码视角；本切片与 matnr 同值，见 §1.3）"
    )
    mes_code: str = own(
        OWN_DERIVED, "MES 编码 = MPLA_ID = 'MP-' + matnr（物化自 MES.MPLA，计算态）"
    )
    old_code: str | None = own(
        OWN_SOURCE,
        "旧码 BISMT（权威列 ERP.MARA.BISMT，仅一物多码行非空；多码冲突点，见 §2）",
        default=None,
    )
    base_unit: str = own(OWN_SOURCE, "基本计量单位（权威列 ERP.MARA.MEINS，与 WMS 一致，门禁 D3）")
    material_group: str = own(OWN_SOURCE, "物料组（权威列 ERP.MARA.MATKL）")
    created_date: date = own(OWN_SOURCE, "创建日期（权威列 ERP.MARA.ERDAT，seed 确定性）")
~~~

字段↔数据侧映射（与数据角色文档 §2 严格对齐）：

| Material 字段 | 权威源 | 数据侧列 | 物化方式 |
|---|---|---|---|
| matnr | ERP.MARA | MATNR | 主键直接搬 |
| name | ERP.MARA | MAKTX | 直接搬 |
| material_type | ERP.MARA | MTART | 直接搬（枚举 5 值） |
| plm_code | 无独立表（PLM 签发视角） | — | 派生：= matnr（§1.3 说明） |
| mes_code | MES.MPLA | MPLA_ID（="MP-<MATNR>"） | 经 join key 组装 |
| old_code | ERP.MARA | BISMT（仅 15% 行非空） | 直接搬 |
| base_unit | ERP.MARA / WMS.WMMD | MEINS（两表一致） | 直接搬 + D3 校验 |
| material_group | ERP.MARA | MATKL | 直接搬 |
| created_date | ERP.MARA | ERDAT | 直接搬 |

### 1.3 三个编码 + 旧码的承载与取值口径

本切片有 5 个码空间（4 个落在 Material 字段，1 个 WMS 走主码）——明确各自的「值怎么来、和谁同值」：

| 码 | 码空间 | Material 字段 | 取值口径 | 与主码关系 |
|---|---|---|---|---|
| 主码族 | `erp` | matnr | = ERP.MARA.MATNR | 主码（join key） |
| | `plm` | plm_code | = matnr（PLM 签发主码 → ERP 采纳，同值） | 与主码同值（签发视角） |
| | `wms` | —（不设字段） | = matnr（WMS 不发明编码，直接采用 ERP 主码，门禁 D1） | 与主码同值（消费视角） |
| MES 码 | `mes` | mes_code | = MES.MPLA.MPLA_ID = "MP-" + matnr | 派生编码（独立字符串，可机验） |
| 旧码族 | `legacy` | old_code | = ERP.MARA.BISMT，仅注入行非空（15%） | **必不等于主码**（多码冲突点，门禁 A4） |

> 语义要点：**「3 编码 → 1 概念」指的是 plm/erp/mes 三个码空间映射同一物料概念**（规划 §2）；其中 plm/erp/wms 三视角共用同一字符串 MATNR（主码一次签发、三系统采纳——这正是「跨系统 join key = MATNR」的本体图表达），mes 是独立派生编码。而**一物多码**（DQ-01）的冲突不是「PLM 码≠ERP 码」（那类工程码与物料码的冲突留 P1b 引入独立 PDM 表再演），而是**主码族 vs 旧码族**两代编码并存（§2）。数据侧保证（门禁 A4）旧码格式与主码正则互斥，机器可区分。

### 1.4 Code 对象 + hasCode 链接（LinkTypeDef 风格）

`Code` 编码对象把码空间显式化：一码一对象，值来自源系统列，归属到 Material（hasCode 多值）。

~~~python
from pydantic import BaseModel
from src.ontology.objects import own
from src.ontology.links import LinkTypeDef


class Code(BaseModel):
    """系统编码对象。PK = code_id（"{code_space}:{value}"）。一码一对象，归属一个物料概念。"""

    code_id: str = own(OWN_SOURCE, "编码记录号（PK，派生自 code_space + value）")
    code_space: Literal["plm", "erp", "mes", "wms", "legacy"] = own(
        OWN_SOURCE, "码空间：plm/erp/mes = 规划 §2 三编码，wms = 采用主码，legacy = 旧码 BISMT"
    )
    value: str = own(OWN_SOURCE, "编码值（权威列：MATNR / MPLA_ID / BISMT）")
    material_matnr: str = own(OWN_SOURCE, "归属物料（FK -> Material.matnr，hasCode 链接承载）")


# hasCode 链接：Material 1:N Code（1 概念多编码），FK 在 Code（target 侧）——对齐 S1
# 「1:N → 外键在 target」约定（src/ontology/links.py 头注释）
HAS_CODE_LINK = LinkTypeDef(
    name="material.codes",
    source_type="Material",
    target_type="Code",
    cardinality="1:N",
    fk_field="material_matnr",
    inverse_name="code.material",
    description="编码归属：一个物料概念有多个系统编码（hasCode 多值，3 系统编码 → 1 概念）",
)
~~~

**Code 对象的确定性物化**（本体加载器从三源表派生，同 seed 同配置可复现）：

| 码空间 | 每条 Material 生成的 Code 行 | 行数 |
|---|---|---|
| plm / erp / wms | 各 1 行，value = matnr | 200 × 3 |
| mes | 1 行，value = "MP-" + matnr | 200 |
| legacy | 仅 old_code 非空者 1 行，value = BISMT | 30 |
| **合计** | — | **830** |

> code_id 约定 `"{code_space}:{value}"`（如 `erp:MAT-2026-0001-K4V`、`legacy:HC-202600007`），确定性、无歧义、可机验。

**注册与自检**：Material / Code 追加注册进 `Registry`（与 S1 8 对象同一注册表，`/meta/schema` 与本体驱动 UI 自动暴露新对象）；`self_check` 新增两条检查项（设计规格，实现落地）：

| 检查 | severity | 断言 |
|---|---|---|
| CODE_SPACE_ENUM_VALID | error | Code.code_space ∈ {plm, erp, mes, wms, legacy} |
| MULTI_CODE_FIELD_CONSISTENT | error | Material.old_code 非空 ⟺ 该物料存在 code_space="legacy" 的 Code 行（双向一致，防双轨漂移） |

### 1.5 跨系统 join key 契约（表级）

**同一物料在 erp.db/mes.db/wms.db 关联成 1 实体的 key = MATNR**，契约如下（与数据角色文档 §3.4/§6-D 同源）：

~~~
ERP.MARA.MATNR = MES.MPLA.MATNR = WMS.WMMD.MATNR   （三表 1:1:1，200 物料宇宙对齐）
约束：MES/WMS 无孤儿（LEFT JOIN 空侧 = 0，门禁 D1/D2）
      WMMD.MEINS = MARA.MEINS（计量单位一致，门禁 D3）
~~~

- 本体加载器以 **ERP.MARA 为概念主承载**（200 行驱动），MES/WMS 按 MATNR join 补入 mes_code / 校验 base_unit；
- 竖井打通发生在**语义层而非数据层**：三库之间无外键，join 由本体映射 + 查询契约完成（DuckDB `sqlite_scan` 跨 3 库物化，规划 §6-3 已验证）——这是「本体 = 语义层」主张的直接落点；
- 可机验锚点：Material 实例数 = MARA 行数 = 200；Code 行数 = 830（确定性，见 §1.4）。

---

## 2. 一物多码的本体表达与判定口径

### 2.1 本体表达

一物多码在本体中 = **同一 Material 概念同时拥有主码族与旧码族**，两层表达互相印证：
1. **字段层**：Material.old_code 非空（30/200 = 15%，数据侧注入）；
2. **图层**：该 Material 经 hasCode 同时挂 code_space="erp/plm/wms"（主码族，值 = matnr）与 code_space="legacy"（旧码族，值 = BISMT）的 Code 行。

> 「一物多码」不是「一个物料有两行」，而是**一个概念、两个编码代际**——本体用「1 概念 N 编码」表达，正是语义层相对关系型数据的价值点。

### 2.2 判定口径（可机验谓词）

给定 Material 的某条数据（来自 ERP.MARA），**一物多码 ⟺ 以下三条同时成立**：

~~~
is_multi_code(row) :=  row.BISMT IS NOT NULL
                   AND row.BISMT != row.MATNR                 # 旧码不等于主码（多码冲突点）
                   AND re.match(LEGACY_RE, row.BISMT)         # 匹配旧码正则（格式互斥于主码）
~~~

其中旧码正则**由配置派生**（数据角色文档 §1.3/§3.4，禁硬编码）：

~~~
LEGACY_RE = f"^{legacy_prefix}-\d{{4}}\d{{5}}$"     # 通用形：<prefix>-<YYYY><seq:05d>
             ->  ^HC-\d{9}$                            # 本切片生效值（prefix=HC, year=2026, seq 5 位）
主码正则（对立面）: ^MAT-\d{4}-\d{4}-[A-Z0-9]{3}$     # 新旧格式互斥（门禁 A4）
~~~

**语义（与数据角色口径逐条对齐）**：
- **BISMT 非空** ⟺ 注入行（30 行）——数据角色门禁 B2 精确命中 `round(N×rate) = round(200×0.15) = 30`；
- **≠ MATNR**：数据侧保证注入行「必不等于 MATNR」（表结构文档 §2.1），谓词再加一道防御（即使未来有脏数据也不误判）；
- **匹配旧码正则**：把「这是旧码」从「看起来像旧码」变成机器可断言；格式互斥保证不会与主码正则重叠。

**「哪些物料一物多码」的机器判定集**：

~~~
multi_code_set = { matnr | is_multi_code(row) }，期望基数 = 30，占比 = 15.00%（N=200）
~~~

### 2.3 机器验证（与数据侧 reconcile）

一物多码判定不是「人工口径」，而是**三方一致、双端对账**：

| 端 | 枚举来源 | 期望值 |
|---|---|---|
| 数据侧 | 数据生成器按注入行集枚举（确定性，同 seed 同配置） | 30 个 MATNR |
| 本体侧 | 契约查询「old_code is_not_null」（§3） | 30 个 MATNR |
| 对账 | 两侧按 matnr 升序逐一相等；计数 = manifest.multi_code_count（门禁 C4） | 0 差异 |

> 这同时兑现测试角色门禁：本体查询结果 ≠ 数据侧注入集 = 本体映射或数据注入出了问题，**任一侧错都暴露**。

### 2.4 边界与例外（门禁 B4 衔接）

| 情形 | 判定 | 处理 |
|---|---|---|
| BISMT 非空 且 ≠ MATNR 且 匹配旧码正则 | **一物多码**（入 multi_code_set） | 正常计入 |
| BISMT 非空 但 = MATNR | 畸形（违反注入约定） | 数据门禁 B4 拦截；本体侧对账报差异 |
| BISMT 非空 但不匹配旧码正则 | 畸形/脏数据 | 同左；不静默吞掉 |
| BISMT 为空 | 单码物料 | 不入 multi_code_set |

---

## 3. 结构化查询契约 v0.1 细化

### 3.1 契约 JSON Schema（完整）

对齐规划 §8 雏形（object_type / filters / aggregations / group_by / link_traversal），把「≤1 跳链接」与字段白名单显式化。v0.1 的 filter 在 §8 等值基础上扩展了 `is_not_null`（DQ-01 必需的最小操作符集），其余（range/like 等）留 v0.2 由实验决定。

~~~json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OntoRun 结构化查询契约 v0.1",
  "type": "object",
  "required": ["object_type"],
  "properties": {
    "object_type": {
      "type": "string",
      "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
      "description": "对象类型名或 api_name，须在注册表中可解析（白名单，见 §3.3）"
    },
    "filters": {
      "type": "object",
      "additionalProperties": { "$ref": "#/definitions/filterExpr" },
      "description": "字段白名单：key 必须属于 object_type 的 model_fields"
    },
    "aggregations": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["function", "field"],
        "properties": {
          "function": { "enum": ["count", "sum", "avg", "min", "max"] },
          "field": { "type": "string" }
        }
      },
      "description": "field='*' 仅 count 允许；sum/avg/min/max 要求数值字段"
    },
    "group_by": {
      "type": "array",
      "maxItems": 4,
      "items": { "type": "string" },
      "description": "字段白名单同 filters；有 aggregations 而无 group_by → 标量结果"
    },
    "link_traversal": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["link"],
          "properties": {
            "link": { "type": "string", "description": "已注册链接名，须从 object_type 可达" },
            "hops": { "const": 1, "description": "v0.1 单跳封顶，≤1 跳链接" }
          },
          "additionalProperties": false
        }
      ]
    }
  },
  "additionalProperties": false,
  "definitions": {
    "filterExpr": {
      "oneOf": [
        { "type": ["string", "number", "boolean"], "description": "简写 = 等值 {op:eq}" },
        {
          "type": "object",
          "required": ["op"],
          "properties": {
            "op": { "enum": ["eq", "ne", "is_null", "is_not_null", "in"] },
            "value": { "description": "op∈{eq,ne,in} 必填；is_null/is_not_null 忽略" }
          },
          "additionalProperties": false
        }
      ]
    }
  }
}
~~~

### 3.2 「哪些物料一物多码？」完整契约实例

~~~json
{
  "contract_version": "0.1",
  "object_type": "Material",
  "filters": {
    "old_code": { "op": "is_not_null" }
  },
  "aggregations": [],
  "group_by": [],
  "link_traversal": { "link": "material.codes", "hops": 1 }
}
~~~

- **过滤器只写一条**：`old_code is_not_null`（等价于 §2.2 谓词第一条；谓词的 ≠ 与正则两道防御由契约执行器统一套用——执行器对「old_code 非空」的结果集强制再过 §2.2 全谓词，保证口径单点）；
- **link_traversal**：`material.codes, hops=1` 把每条物料的全部编码带回（主码族 + legacy），返回结构见 §4.3 Q1；
- 期望结果：**30 条 Material**，按 matnr 升序，与数据侧注入行集逐一相等（§2.3 对账）。

### 3.3 契约校验规则（可机验，兑现铁律②）

| # | 规则 | 实现 | 失败处理 |
|---|---|---|---|
| V1 字段白名单 | object_type 必须解析到已注册对象类型；filters / group_by 字段必须 ∈ 该类型 model_fields；link 必须 ∈ 已注册链接且从该类型可达 | 校验器查 Registry | 契约校验失败 → 拒答（fail-closed） |
| V2 类型约束 | filter 值类型必须匹配字段 schema（string/integer/枚举值）；sum/avg/min/max 仅数值字段；count 允许 "*"；is_null/is_not_null 不得带 value | Pydantic `model_validate` + 注册表类型元数据 | 同上 |
| V3 ≤1 跳链接 | link_traversal.hops ∈ {1}；单跳封顶，禁止对遍历目标再链接（无链式多跳、无环） | 契约 schema `const:1` | 同上 |
| V4 防注入 | 契约值一律参数化绑定（placeholder），**永不拼 SQL**；拒绝一切未知键/未知字段/未知链接（additionalProperties:false）；值内禁 SQL 片段/注释/引号逃逸 | 白名单 fail-closed + 参数化执行 | 同上（拒答，不降级为裸执行） |
| V5 结果护栏 | 结果行数上限（默认 ≤1000）、aggregations ≤5、group_by ≤4 | 执行器 | 超限拒答/提示加过滤 |

> **衔接 S1 动作参数校验纪律**：S1 动作执行管道① = `action.params_model.model_validate(params)`，类型/枚举/边界失败 → `INVALID_PARAMS`（src/runtime/action_engine.py，AGENTS.md 安全要求：LLM 输出不可信 → 参数必须校验、防注入）。契约校验同纪律、同机制：LLM 产出的是受限 JSON（不是 SQL），校验器按注册表白名单 fail-closed，失败即拒答（拒答率成为 D3 可测指标之一）。

### 3.4 D3 背景：head-to-head 实验与终版决策

本契约是 **S2 垂直切片内 head-to-head 实验的输入**（research/s2-review-decision-pack.md 决策 4，P0 已拍板）：

| 维度 | 内容 |
|---|---|
| 对照 | **受限结构化查询**（LLM 产出契约 JSON，本地校验执行）vs **NL2SQL + 守卫**（LLM 写 SQL，多层安全校验） |
| 实验集 | **30 个分析问题**（含 §4.3 的 3 个 ground truth 问题作为对标锚），同问法双形态跑 |
| 指标 | 成功率 / P95 延迟 / 单次成本 / 可控性（是否可审计可回滚）/ 拒答率 |
| 终版决策 | 实验后定契约 v0.2 终版；若受限 IR 表达力不足，20% 冷问题允许 LLM 生成经安全校验的 SQL（兜底，Plan B） |
| 本切片范围 | P1a 只交付契约 v0.1 + 校验器规格 + 标答（§4），实验执行在 P2 阶段，不在本切片实现 |

---

## 4. ground truth 标答集草案

### 4.1 DQ-01 标答口径（供测试角色写门禁）

**一物多码标答 = 数据侧注入行集（确定性枚举），本体查询必须与之逐一相等**——标答不靠人工拍脑袋，而是「数据侧注入 ∧ 本体判定 ∧ 双端对账」三方一致（§2.3）：

~~~
DQ-01 标答：
  multi_code_set（30 个 MATNR，按 matnr 升序，同 seed=20260821 同配置确定性枚举）
  每个成员满足：old_code 非空 ∧ old_code ≠ matnr ∧ old_code 匹配 ^HC-\d{9}$ ∧ old_code 互异
  计数 = round(N × rate) = 30；占比 = 15.00%（±0，N=200 精确命中）
~~~

### 4.2 标答记录结构（结构化，供测试写成 pytest 门禁）

~~~json
{
  "gt_id": "DQ-01",
  "question": "哪些物料一物多码？",
  "contract": { "object_type": "Material", "filters": { "old_code": { "op": "is_not_null" } }, "link_traversal": { "link": "material.codes", "hops": 1 } },
  "expected": {
    "object_type": "Material",
    "count": 30,
    "ratio": 0.15,
    "matnr_set_source": "data-side injection set (seed=20260821, deterministic)",
    "per_item": ["old_code not null", "old_code != matnr", "old_code matches ^HC-\d{9}$"]
  }
}
~~~

### 4.3 三个验证问题（问法 / 契约 / 期望返回结构）

**Q1 · 主问题 DQ-01「哪些物料一物多码？」**

| 项 | 内容 |
|---|---|
| 问法 | 「哪些物料一物多码？」/「哪些物料同时有新主码和旧码？」 |
| 契约 | 见 §3.2（filters + link_traversal 带回编码） |
| 期望返回 | 30 条 Material，按 matnr 升序，每条含属性 + codes 数组 |
| 门禁断言 | ① count == 30；② 每条 old_code 非空 ∧ ≠ matnr ∧ 匹配 `^HC-\d{9}$`；③ matnr 集合 == 数据侧注入集（同 seed 枚举比对）；④ 有 legacy 的 Code 行且 value == old_code |

~~~json
{
  "object_type": "Material",
  "count": 30,
  "items": [
    { "pk": "MAT-2026-0001-K4V",
      "properties": { "matnr": "MAT-2026-0001-K4V", "name": "铝合金外壳 A 型", "material_type": "FERT",
                      "plm_code": "MAT-2026-0001-K4V", "mes_code": "MP-MAT-2026-0001-K4V",
                      "old_code": "HC-202600007", "base_unit": "PC" },
      "codes": [
        { "code_space": "erp", "value": "MAT-2026-0001-K4V" },
        { "code_space": "plm", "value": "MAT-2026-0001-K4V" },
        { "code_space": "wms", "value": "MAT-2026-0001-K4V" },
        { "code_space": "mes", "value": "MP-MAT-2026-0001-K4V" },
        { "code_space": "legacy", "value": "HC-202600007" }
      ] }
  ]
}
~~~

**Q2 · 单物料编码查询（hasCode 遍历）**

| 项 | 内容 |
|---|---|
| 问法 | 「物料 MAT-2026-0001-K4V 有哪些编码？」（单实体，可换任一 MATNR） |
| 契约 | `{"object_type": "Material", "filters": {"matnr": {"op": "eq", "value": "MAT-2026-0001-K4V"}}, "link_traversal": {"link": "material.codes", "hops": 1}}` |
| 期望返回 | 1 条 Material + codes 数组 |
| 门禁断言 | ① 命中 1 条；② 主码族（plm/erp/wms）value == matnr；③ mes value == "MP-" + matnr；④ 该物料有旧码 ⟺ codes 含 legacy 行且 value == old_code |

**Q3 · 一物多码计数与占比（聚合）**

| 项 | 内容 |
|---|---|
| 问法 | 「一共有多少物料一物多码？占比多少？」 |
| 契约 | `{"object_type": "Material", "filters": {"old_code": {"op": "is_not_null"}}, "aggregations": [{"function": "count", "field": "*"}]}` |
| 期望返回 | 标量 count（占比由调用方按 count/N 算） |
| 门禁断言 | ① count == round(N × rate) == 30；② count == manifest.multi_code_count（门禁 C4 对齐）；③ ratio == 30/200 == 15.00% |

> 三个问题覆盖契约三大能力面：过滤 + 链接遍历（Q1/Q2）、纯过滤 + 聚合（Q3）；同时作为 D3 head-to-head 的 3 个对标锚问。

---

## 5. S1 映射能力复用点清单

议题 2 映射管线（docs/S2-议题清单_v0.1.md §3.7）形态 = 「DES 语义已知半自动映射 + 分级置信度 + 轻人工审核」；S1 `src/builder/mapping/` 的三块能力按「借接口、借算法、借形态」三档复用，简述如下。

### 5.1 fk_detection.py —— 借算法（跨库链接自动复核）

- **复用点**：自动发现/复核 DES 三表间的跨系统链接 → 产出候选 LinkTypeDef。对 (source=mes.MPLA, target=erp.MARA)、(wms.WMMD, erp.MARA)，`detect_links` 从样本自动验证 `MATNR` 同名链接 + 基数推断（应为 N:1，`match_summary.direct_match_rows` = 200/200 = 100%）。
- **接口形态**：`detect_links(*, source_table, target_table, source_columns, target_columns, source_rows, target_rows, target_pk) -> list[DetectedLink]`，`DetectedLink.link_id / source_field / target_field / cardinality / match_summary` 直接映射为 `LinkTypeDef(fk_field, cardinality)` + 置信度（direct 占比）。
- **议题 2 落地**：DES 语义已知 → detect_links 作**自动复核**（非从零发现）；direct=100% 高置信度自动过，否则进人工审核队列。

### 5.2 naming.py —— 借接口（列清单 → 属性 schema 草稿）

- **复用点**：从三张源表列清单派生 Material / Code 的 property schema 草稿（PascalCase 属性名、is_technical 隐藏列、required）。DES YAML 自带中文释义与表/字段语义 → **DES 语义优先作 description，naming 兜底**（高置信度映射自动过，议题 2 §3.7-2）。
- **接口形态**：`derive_property_schema(columns, pk_column) -> {type, properties, required, hidden_columns}`，辅助 `to_pascal_case / is_technical_column / is_id_only_column / map_type`。
- **边界（诚实口径）**：naming 不产生业务语义（「MATNR 是物料号」来自 DES 配置），只做命名规范化与技术列隐藏——因此 DES 场景它是「骨架生成器」，不是「语义理解器」。

### 5.3 alias_matcher.py —— 借形态（不借算法）

- **复用点**：`match_aliases` 的**输出形态**（`AliasMatchResult.matches / no_match / ambiguous_resolved / confidence` 三档 + 置信度）是「别名/码 → 实体」映射建议的通用骨架，可直接用作**旧码 BISMT / 编码 → Material** 的映射建议结构，对接 P1.5 映射置信度打标骨架与审核队列（议题 2 §3.7-3 的映射建议队列）。
- **接口形态**：`match_aliases(text, master_suppliers) -> AliasMatchResult`，`AliasMatch(match_type, confidence, disambiguation_note)`。
- **边界（诚实口径）**：算法本体（中文公司名 2-4 字 n-gram 剥离）**不适用于 DES 编码**——编码匹配用 `value_format.normalize_id`（SUP-001↔SUP001 归一，fk_detection 同源依赖）与旧码/主码正则更贴切。即：**借形态（置信度三档），不借算法（中文 n-gram）**。

### 5.4 议题 2 管线衔接小结

| S1 能力 | 复用档 | 在「DES 数据 → 本体」中的角色 |
|---|---|---|
| fk_detection.detect_links | 借算法 | 跨系统链接自动复核 → 候选 LinkTypeDef + 置信度 |
| naming.derive_property_schema | 借接口 | 源表列清单 → 对象 property schema 草稿（DES 语义覆盖 description） |
| alias_matcher.match_aliases | 借形态 | 「码 → 实体」映射建议的三档/置信度输出结构（审核队列） |
| （相邻）value_format.normalize_id | 借算法 | 编码值归一（直接适用于主码/旧码匹配，fk_detection 同源） |

---

## 附：本设计对「研究对象锚定」的回答

这份本体映射与契约设计不为建本体而建本体：它服务「LLM 经语义接口操作真实系统」的叙事——**一物多码（DQ-01）是真实企业里语义冲突的源头**，Material + hasCode + 契约正是「把竖井系统（3 个独立库）的同一概念（物料）对齐」的语义层机制；契约 v0.1 是 ChatBI 读侧与本体对象/指标对接的正式接口，也是 D3 head-to-head 实验的对标基线。

