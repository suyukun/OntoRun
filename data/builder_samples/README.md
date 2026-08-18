# data/builder_samples/ — 构建期测试数据集与预期 fixture

> 用途：P2（三路径管道 E1）/ P3（自动映射 E2 / LLM 提取 E3）/ E7 宽表拆分的 TDD 弹药。
> 范畴：仅供构建期 builder 子系统使用；不动 src/ tests/，不与 src/runtime/ 的源系统库（retail_source.db）混用。
> 单一事实来源：本目录下 CSV / JSON / MD / XML 全部人工落盘；expected/ 全部人工标注，禁止用脚本生成。
> 维护人：数据角色（Rose 派活，数据角色交付）。任何字段变更须更新 expected/ 对应 fixture 并写明原因。

---

## 文件清单与计数

| 路径 | 角色 | 行/条数 | 编码 | 大小（约） |
|---|---|---|---|---|
| `suppliers_dirty.csv` | A 路径·结构化·去重+类型脏数据+技术列 | 22 行（去重 20 行） | UTF-8 | 3.0 KB |
| `products_ref_suppliers.csv` | A 路径 + E2 FK 检测 | 34 行 | UTF-8 | 4.6 KB |
| `orders_nested.json` | B 路径·半结构化·双层嵌套 Explode | 16 订单 / 29 items / 12 shippings | UTF-8 | 11.0 KB |
| `catalog.xml` | B 路径·属性+子元素混合 | 12 products / 33 specs / 12 certs | UTF-8 | 6.5 KB |
| `supplier_memo.md` | C 路径·非结构化·LLM 提取 | 661 中文字 / 1261 总字符 | UTF-8 | 3.8 KB |
| `wide_table_purchases.csv` | E7 宽表拆分最小用例 | 25 行（14 头 + 14 supplier + 25 明细） | UTF-8 | 5.3 KB |
| `expected/schema_inferred.json` | A 路径 schema 推断预期 | — | UTF-8 | 4.5 KB |
| `expected/fk_detection.json` | E2 FK 检测 + 基数推断预期 | — | UTF-8 | 4.2 KB |
| `expected/flatten.json` | B 路径 JSON 拍平预期 | — | UTF-8 | 4.0 KB |
| `expected/parse.json` | B 路径 XML 解析预期 | — | UTF-8 | 4.8 KB |
| `expected/extraction_targets.json` | E3 LLM 提取黄金集 + 问题项 | — | UTF-8 | 8.5 KB |
| `expected/wide_split.json` | E7 宽表拆分预期 | — | UTF-8 | 3.0 KB |

---

## 蓝图规格对照表

| 样本 | 蓝图条目 | 验证点 | TDD 引用方式（仅说明，不写测试代码） |
|---|---|---|---|
| `suppliers_dirty.csv` | §6 A 路径 schema_infer / cleanse | 列推断 / 类型推断 / 非空率 / 技术列隐藏 / 去重 | TDD：读 schema_inferred.json 断言 schema；断言 etl_loaded_at is_technical=true；断言 22→20 去重；断言 rating 列清洗规则 |
| `suppliers_dirty.csv` | §7 E2 字段推断 + is_technical 标记 | 纯 ID/时间戳列隐藏 | TDD：断言 etl_loaded_at / source_system 在生成 ontology property_schema 时被排除 |
| `suppliers_dirty.csv` | §7 E2 值格式容错 | SUP-001 ↔ SUP003 同表并存 | TDD：assert schema_inferred.format_normalization_pairs 包含两个 pattern；下游 FK 跨表匹配时应能归一 |
| `products_ref_suppliers.csv` | §7 E2 FK 检测 + 基数推断 | 跨表主键同名 → 自动建链 | TDD：读 fk_detection.json 断言 lnk_product_supplier cardinality=N:1；断言 3 unmatched（typo）+ 5 format-normalized match |
| `orders_nested.json` | §6 B 路径 JSON 拍平 + Explode | items 数组 Explode；shipping 1:1 抽子表；notes 双层 Explode | TDD：读 flatten.json 断言 orders=16 / items=29 / shippings=12 / notes=3 / replies=2；断言 ORD-0007 取消订单 items=[] 不产行；断言 4 个无 shipping 不产 shipping 行 |
| `catalog.xml` | §6 B 路径 XML 解析 | 属性 → 列；子元素 → 子表；空 certifications 不产行 | TDD：读 parse.json 断言 products=12 / specs=33 / certs=12；断言 X-9003/X-9004/X-9006 certs=[] 不产行 |
| `supplier_memo.md` | §6 C 路径 MD→结构化 + §8 E3 七道校验 | 黄金集对照；故意问题项触发 V3/V4/V5 | TDD：跑 LLM 提取 → 对照 extraction_targets.golden_entities/relations/logic_rules/actions；断言 V3 捕到 LR-999 引用缺失（fatal）；断言 V4 捕到 "陈志强" 重复（error）；断言 V5 输出 marketing_artifact 警告 |
| `wide_table_purchases.csv` | §7 E7 宽表拆分（最小实现） | 一表三实体 → 三张表 + FK | TDD：读 wide_split.json 断言 purchase_orders=14 / supplier_info=14 / purchase_order_lines=25；断言 FK 链 purchase_orders→supplier_info (N:1) 与 purchase_orders→lines (1:N) |

---

## E3 黄金集设计说明（`expected/extraction_targets.json`）

### 干净实体（19 个，应全通过 V1-V5）
- 6 家公司（云汉零售、远洋冷链、云岭冷链、顺丰冷运、武汉长江冷链、中山金辉照明）
- 1 个内部品牌（鲜品汇）
- 6 个联系人（王晓燕、蔡晓东、周大鹏、陈志强、Jack、Rose）
- 1 个 SKU（SKU-LN2-TUN）、1 个产品名（液氮速冻隧道设备）
- 2 个审批角色（采购总监、CFO）
- 2 个金额分档（单笔大额合同 50 万 / 单笔中额合同 10-50 万）

### 故意埋设的问题项（3 个，触发 E3 不同校验器）

| # | 问题 | 触发校验器 | 期望严重度 | 期望消息 | 写在哪个块 |
|---|---|---|---|---|---|
| 1 | 实体 `远洋冷链2025Q3报价单` 的 `type=marketing_artifact` 不在 entity_types_whitelist | **V5 类型白名单** | warning | "实体类型 'marketing_artifact' 不在预设白名单中；自定义率 1/21 = 4.76%，<50% 阈值，输出 warning 不阻断" | `golden_entities[19]` |
| 2 | 实体 `陈志强 (subtype=supplier_contact)` 与 `陈志强 (subtype=internal_consultant)` 同 (name,type) | **V4 去重** | error | "实体 (陈志强, person) 出现 2 次，必须按 (name,type) 去重保留首条" | `golden_entities[20]` |
| 3 | 动作 `force_approve_for_demo.linked_logic=["LR-999"]` 引用不存在的规则 | **V3 引用完整性** | fatal | "linked_logic 引用了不存在的 LR-999；本数据集 LR 集合为 [LR-001..LR-005]" | `golden_actions[3]` |

### 校验预期摘要（写进 `expected_validator_summary` 块）
- V1 结构：pass
- V2 必填：pass
- V3 引用完整性：**fail**（1 处 fatal）
- V4 去重：**fail**（1 处 error）
- V5 类型白名单：**warning**（1 处，自定义率 < 50%）
- V6 语法校验：pass（动作无 function_code 字段）
- V7 语义引用：pass（除 V3 已捕的 LR-999）

### Logic Rules（5 个，含严重度差异，用于验证逻辑规则严重度字段）
- LR-001 大额合同双重审批（fatal）
- LR-002 中额合同单级审批（fatal）
- LR-003 温控失效 1.5 倍赔付（error）
- LR-004 远洋冷链混装范围（warning）
- LR-005 备份供应商启用条件（error）

### Actions（4 个，含 1 个故意问题项）
- approve_large_contract（链接 LR-001）
- activate_backup_supplier（链接 LR-005）
- file_compensation_claim（链接 LR-003）
- **force_approve_for_demo（链接 LR-999 → V3 捕获）**

---

## E7 宽表拆分设计说明（`expected/wide_split.json`）

原宽表 22 列混 3 实体（采购单头 / 供应商信息冗余 / 商品明细），拆分预期：

| 目标表 | 主键 | 期望行数 | 来源列 |
|---|---|---|---|
| `purchase_orders` | `purchase_order_id` | 14 | po_id, po_date, po_status, po_total_amount, supplier_id, buyer, warehouse_code |
| `supplier_info` | `supplier_id` | 14 | supplier_id, supplier_name, supplier_contact, supplier_phone, supplier_region, supplier_category（去重） |
| `purchase_order_lines` | `(purchase_order_id, po_line_no)` | 25 | po_id, po_line_no, product_id, product_name, product_category, unit, unit_price, qty, line_amount, line_eta_date, line_received_qty |

FK 链：
- `purchase_orders.supplier_id → supplier_info.supplier_id`（N:1）
- `purchase_orders.purchase_order_id → purchase_order_lines.purchase_order_id`（1:N）

---

## 蓝图数据规格缺口（执行时需补充决策）

1. **JSON 拍平命名冲突**：当 items 数组中的字段名与外层相同（如下单行 product_id 与订单 product_id），拍平后命名规则未规定（保留原名 / 加前缀 / 加后缀）。建议：保留原名，靠 schema 上下文区分。
2. **XML 属性 vs 子元素同名**：当 `<product name="X"><name>X</name></product>` 同时存在，期望行为未规定（属性优先 / 子元素优先 / 报错）。建议：子元素优先 + warn。
3. **E3 黄金集来源**：本目录 `extraction_targets.json` 是人工标注，但执行时 LLM 实际提取结果可能与黄金集不完全一致（实体边界 / 关系方向 / subtype 划分）。建议：TDD 采用"子集匹配 + 关键字段必含"宽松断言，全集精确断言仅做冒烟。
4. **E2 备用键匹配数据**：本目录未提供"文档中提及的公司名 → 实体"的备用键匹配数据样例。supplier_memo.md 中的"远洋冷链"等代称已在 entities 中显式列出，未做"代称→全称"映射。如 P3 需要该用例，建议补充第二份 MD 文档（带公司全称/简称混用）。
5. **E7 增量更新三层数据**：补丁 B3 已将同步/处理/索引三层降 TODO，本目录不提供增量更新数据样例。如发布期需要，由后续窗口补充。
6. **类型白名单自定义率阈值**：蓝图 §8-V5 写 ">50% 自定义则告警"，但 "告警" 的具体严重度（warning vs error vs fatal）未规定。建议：warning（不阻断，但 review 必看）。
7. **脏数据清洗策略可配置化**：rating 列的 "4.5分" / "N/A" 在本 fixture 中以 `expected.cleanse_rule` 显式标注，但 builder pipeline 是否需要把"清洗规则"做成可配置项（per_dataset_config）未规定。建议：MVP 内置默认规则 + per_dataset override 字段（curated_datasets.quality_score JSON 内）。
8. **C 路径 PDF/DOCX**：补丁 B6 已将 PDF/DOCX 列为"markitdown 可用时支持，不可用降级"，本目录不提供 PDF/DOCX 样例；如要验证降级路径，需 markitdown 不可用的环境或 stub。

---

## 字段命名约定

- 所有列名：snake_case 英文（如 supplier_id, contact_phone）
- 所有枚举值：snake_case 英文（如 electronics, food, in_transit）
- 中文：仅出现在 content/description/note 字段（贴近项目叙事）；不作为列名或枚举值。
- 日期：ISO 8601（YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SSZ）
- 金额：浮点（CNY，无千分位）
- 缺失值：CSV 留空（不写 "NULL" 或 "N/A" 字符串），JSON 用 null

---

## 版本与变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2025-09-02 | 初版 7 样本 + 6 expected fixture 落盘 |