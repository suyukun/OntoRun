# P2 head-to-head 实验报告（A=NL2SQL 直查 vs B=本体版受限结构化查询）

> 生成：2026-08-21 20:35 ｜ 依据：docs/P2-ChatBI闭环设计_v0.1.md §4 ｜ 数据集：data/des/enterprises/hc_precision（5 源库 18 表 1,000,000 行 + metrics.db 15 指标物化）
> 方法：30 问 × 2 形态各 1 次 LLM 调用（DeepSeek）。A=LLM 生成 SQL → 多层守卫（只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）→ DuckDB 本地执行；B=LLM 生成契约 JSON → validate_contract + ContractExecutor（PermissionContext.allow_all 内部口径）。正确性 = 期望口径 GT（确定 SQL 预计算）按 key 精确 + 数值容差（相对 0.5%）比对。

## 0. 结论先行（BLUF）

- **A=Baseline（NL2SQL 直查）成功率 63.3%（19/30）**；**B=本体版（受限结构化查询）成功率 6.7%（2/30）**；Δ = **-56.7pp**（为负）。
- **靶值判定：未达成**（B 距 85% 差距大，Δ 为负）→ **触发 Plan B**（设计 §5：B 成功率 < 85% 且冷问题 ≥ 20%）。
- 但 B 的低分主要由**语义面覆盖缺口**（当前仅 Material/Code 对象 + 15 指标，30 问仅 8 问在语义面内）与 **V5 结果护栏过严**（2400 行，挡住 3 个大结果问题）导致，不是「受限结构化查询」这一形态本身的必然失败——见 §6 语义面扩展分析。
- **契约 v0.2 终版建议：混合形态**——受限结构化查询（B）作主路径（可控/可枚举/fail-closed），Plan B（守卫化 LLM SQL）兜底冷问题；同时按设计 R5 增补指标/对象/链接，把 B 语义面从 8 问扩到 ~26-28 问。

## 1. 靶值判定（设计 §4.3）

| 靶值 | 实测 | 达成 |
|---|---|---|
| A=Baseline 成功率 ≥ 70% | 63.3% | ❌ 未达成 |
| B=本体版成功率 ≥ 85% | 6.7% | ❌ 未达成 |
| Δ = B−A ≥ 10pp | -56.7pp | ❌ 未达成 |
| 拒答率 > 0（两形态） | A 6.7% / B 86.7% | ✅ 达成 |
| 执行延迟 P95 ≤ 500ms（A） | 60ms | ✅ 达成 |
| 执行延迟 P95 ≤ 500ms（B） | 165ms | ✅ 达成 |

> P95 为执行延迟（不含 LLM 网络耗时）；B 仅对实际执行的契约计 P95（A1/L4/F5 等大结果问题被 V5 护栏拒答不计）。拒答率 > 0 由主跑拒答 + 负例演示共同证明（§5）。

## 2. 汇总指标

| 指标 | A=Baseline（NL2SQL） | B=本体版（受限结构化） | 说明 |
|---|---|---|---|
| 成功率 | 63.3%（19/30） | 6.7%（2/30） | Δ = -56.7pp |
| 拒答率（fail-closed） | 6.7%（2/30） | 86.7%（26/30） | B 拒答=受限面不可表达+校验/护栏拒答 |
| 错误答案率（执行成功但≠GT） | 7/30 | 2/30 | |
| 错误率（LLM/执行/解析失败） | 2/30 | 0/30 | |
| 执行延迟 P95 / 均值 | 60ms / 28ms（28 次执行） | 165ms / 28ms（10 次执行） | |
| LLM 单次延迟 P95 / 均值 | 1523ms / 996ms | 1739ms / 1206ms | 网络+生成 |
| LLM token（输入/输出） | 39,865 / 1,937 | 31,063 / 2,272 | 30 问合计 |
| 成本估算（元） | ¥0.1370 | ¥0.1136 | 见 §7 |

**分项解读**：
- A 全部 30 问可表达，失败 = 7 问 SQL 语义错误（J1 缺 LEFT JOIN 丢 0 单客户、A6 用抬头金额非项目金额、A5 单价过度舍入、J4 Top5 集合不同、T4 时段标签不同、J3 结果仅 60 行、F4 退款集合不同）+ 2 问执行错误（J2 未 join MARA、T3 VARCHAR vs DATE 类型）+ 2 问守卫拒答（A2 库名限定+表名拼错 COFC、L3 码空间标签错误且仅 2 类码）。
- B 当前语义面仅 8 问可表达：J6/F6 契约生成正确并命中；J5 契约粒度错（factory×location 非 location）；A3 契约映射到金额指标（非客户数）；A1/L4/F5 被 V5 结果护栏拒答；其余 22 问受限面不可表达，LLM 主动拒答或契约校验拒答。
- **拒答率**：A 的拒答来自守卫；B 的拒答 = LLM 主动拒答 + executor fail-closed。**两形态均满足拒答率 > 0**，且 B 的 fail-closed 是「语义面之外一律拒绝」，正是受限查询的可控性价值。
- **延迟**：两形态执行 P95 均 ≤ 500ms（A 60ms / B 165ms）。B 的 P95 含被 V5 护栏拒答的大结果扫描（A1 物化表 77,936 行 ~165ms），成功的小结果查询（J5/J6/F6）仅 ~7-19ms；A 的 P95 含 A1 的 77,936 行 SQL 聚合 ~166ms，两形态重查询同量级。

## 3. 30 问结果表

> 「B 可表达」列 = 当前语义面（Material/Code + 15 指标）是否可表达该问；期望口径要点仅标注需适配的题目（demo 数据缺字段，§8）。

| 问 | 组 | 问法 | B可表达 | GT行数 | A结果 | B结果 | A exec(ms) | B exec(ms) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| J1 | G1 | 每个客户各下过多少单？ | — | 10000 | wrong | refusal | 12.6 | - |  |
| J2 | G1 | 各品类库存金额排行 | — | 250 | error | refusal | 1.0 | 0.1 | 口径说明: demo 库无单价列（MARA/MARC/M |
| J3 | G1 | 哪些供应商到货准时率最高？ | — | 4962 | wrong | refusal | 60.1 | - | 口径说明: demo 库无准时/交货期字段（无计划收货日 |
| J4 | G1 | 退款金额 Top5 客户 | — | 5 | wrong | refusal | 25.7 | - | 口径说明: 「退款」= REF_TYPE='SO' 且  |
| J5 | G1 | 各仓库库存水位 | ✅ | 3 | correct | wrong | 6.4 | 18.9 | GT key 缺失: ('W01',) |
| J6 | G1 | 有多少一物多码的物料？ | ✅ | 1 | correct | correct | 3.3 | 7.8 |  |
| A1 | G2 | 各月各物料销售金额合计 | ✅ | 77936 | correct | refusal | 165.9 | 164.6 | 口径说明: 设计契约列指向销售物化（metric b1） |
| A2 | G2 | 品类×工厂×月三维汇总 | — | 12000 | refusal | refusal | None | 0.1 | 口径说明: 三维带月的可用数据源 = 报工流水（COFV |
| A3 | G2 | 各月下单客户数 | — | 24 | correct | wrong | 15.2 | 22.5 | GT key ('2025-01',) 值不匹配 |
| A4 | G2 | 整体客单价 | — | 1 | correct | refusal | 36.0 | - | 口径说明: 金额口径 = 订单项目销售金额合计（VBAP |
| A5 | G2 | 物料价格区间 | — | 1 | wrong | refusal | 14.1 | - | 口径说明: demo 库无主数据单价列；适配口径 = 采 |
| A6 | G2 | 各月订单量与金额趋势 | — | 24 | wrong | refusal | 17.9 | - |  |
| F1 | G3 | corporate 客户的高额订单 | — | 1281 | correct | refusal | 17.6 | - | 口径说明: corporate = KTOKD '000 |
| F2 | G3 | 低于安全库存的物料清单 | — | 9 | correct | refusal | 7.6 | - | 口径说明: demo 库无安全库存字段；适配口径 = 物 |
| F3 | G3 | 已发货未送达的订单 | — | 22574 | correct | refusal | 59.2 | - | 口径说明: demo 库销售订单无发货/送达状态；适配口 |
| F4 | G3 | 退款超过阈值的订单 | — | 4100 | wrong | refusal | 17.2 | - | 口径说明: 退款 = REF_TYPE='SO' 且 W |
| F5 | G3 | 指定品类×仓库组合的库存 | ✅ | 16000 | correct | refusal | 25.1 | - | 口径说明: 品类在库存单表不可关联（库存行无品类列），适 |
| F6 | G3 | 含多码物料明细 | ✅ | 1200 | correct | correct | 5.1 | 10.7 |  |
| L1 | G4 | 某物料的供应商是谁？ | — | 10 | correct | refusal | 27.3 | - | 口径说明: 样例物料 MAT-2026-0001-K4V |
| L2 | G4 | 订单对应客户及金额 | — | 1 | correct | refusal | 12.0 | - | 口径说明: 样例订单 SO-2026-000001；订单 |
| L3 | G4 | 物料多码全码列表 | ✅ | 6000 | refusal | refusal | None | 0.1 | 口径说明: 每个一物多码物料（old_code 非空）的 |
| L4 | G4 | 库存位置-物料-库存量 | ✅ | 24000 | correct | refusal | 29.8 | 59.0 | 校验/护栏拒答 |
| L5 | G4 | 订单→退款链路 | — | 8216 | correct | refusal | 27.4 | - | 口径说明: 退款 = REF_TYPE='SO' 且 W |
| L6 | G4 | 财务条目对应订单来源 | — | 16400 | correct | refusal | 34.8 | - | 口径说明: SO 类型财务分录（ACDOCA.REF_T |
| T1 | G5 | 月订单量趋势 | — | 24 | correct | refusal | 9.0 | - |  |
| T2 | G5 | 月库存金额趋势 | ✅ | 24 | correct | refusal | 38.2 | - | 口径说明: 设计契约列即指向销售物化（metric b1 |
| T3 | G5 | 近 30 天日销售 | — | 30 | error | refusal | 0.9 | - | 口径说明: 「近 30 天」= 数据末 30 天（202 |
| T4 | G5 | 本月 vs 上月退款对比 | — | 2 | wrong | refusal | 12.7 | - | 口径说明: 本月=2026-12、上月=2026-11（ |
| T5 | G5 | 平均到货时长趋势 | — | 24 | correct | refusal | 44.6 | - | 口径说明: demo 库无到货时长字段；适配口径 = 平 |
| T6 | G5 | 季度汇总 | — | 8 | correct | refusal | 56.4 | 0.2 | 口径说明: 季度 = 年 + Q + FLOOR((月- |

## 4. B 形态逐问细账（可表达集 + 失败原因）

| 问 | B 结果 | 明细 |
|---|---|---|
| J5 各仓库库存水位 | wrong | GT key 缺失: ('W01',) |
| J6 有多少一物多码的物料？ | correct |  |
| A1 各月各物料销售金额合计 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 结果行数 77936 超过护栏上限 2400（V5，请加过滤） |
| F5 指定品类×仓库组合的库存 | refusal | 受限面不可表达（LLM 主动拒答）：LLM 拒答(受限面不可表达): 问题需要按“品类×仓库组合”查询库存，但“仓库组合”这一语义（仓库组合的维度或字段）不在给定的受限面内；给定指标 stock_balance_by |
| F6 含多码物料明细 | correct |  |
| L3 物料多码全码列表 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: group_by 超过上限 4（V5）; link_traversal 未知键: ['f |
| L4 库存位置-物料-库存量 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 结果行数 24000 超过护栏上限 2400（V5，请加过滤） |
| T2 月库存金额趋势 | refusal | 受限面不可表达（LLM 主动拒答）：LLM 拒答(受限面不可表达): 本体和指标注册表均不提供按月的库存金额趋势：stock_balance_* 指标只支持按地点/物料维度（无月份维度），且度量是 stock_bal |
| A3 各月下单客户数 | wrong | GT key ('2025-01',) 值不匹配 |

## 5. 拒答率 > 0 的 fail-closed 证据（独立负例，不烧 LLM）

> 重要边界（如实标注）：注册表已含 Vendor(scm.LFA1)/InventoryLocation(erp.MARD)/FinanceEntry(fin.ACDOCA) 等对象，但 ContractExecutor 的 v0.1 对象路径未接线跨库源表——SELECT * FROM scm.LFA1 报 Catalog Error（fail-closed）。因此当前实际可查询对象面 = Material/Code（物化内存表），B 的表达全部依赖 15 指标物化 + Material/Code 对象；注册对象 ≠ 可查询对象，这是 P2 实现缺口，也是本体版语义面扩大的前提之一（对齐设计 §1.5 R5）。


**A 形态多层守卫**（设计 §5：只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）——5/5 注入或非法 SQL 被拒答：

| 用例 | 触发 | 守卫捕获 |
|---|---|---|
| 注入多语句 | SELECT * FROM MARA; DROP TABLE MARA | ✅ 含禁用片段: ';'；含禁用片段: 'drop' |
| 注入注释逃逸 | SELECT * FROM MARA WHERE MATNR='x' --' OR 1=1 | ✅ 含禁用片段: '--' |
| 写库 DML | DELETE FROM MARA WHERE MATNR='MAT-2026-0001-K4V' | ✅ 非 SELECT/WITH 单语句 |
| 非白名单表 | SELECT * FROM sys.sensitive | ✅ 引用非白名单表: ['sys.sensitive'] |
| 外部数据源 | SELECT * FROM read_csv('/etc/passwd') | ✅ 含禁用片段: 'read_csv'；引用非白名单表: ['read_csv'] |

**B 形态契约校验**（V1-V5 + M 系列 + P2-2 time_range fail-closed）——5/5 非法契约被拒答：

| 用例 | 触发 | 校验拒答 |
|---|---|---|
| 未知 metric_id | {"contract_version": "0.2", "metric": {"metric_id": "not_a_metric"}} | ✅ 契约校验失败（fail-closed 拒答）: metric_id 不在指标注册表（M 系列）: 'not_a_metric' |
| 未知对象（V1 白名单） | {"contract_version": "0.1", "object_type": "FooObject", "filters": {}, | ✅ 契约校验失败（fail-closed 拒答）: object_type 未注册或非法（V1 白名单）: 'FooObject' |
| 已注册对象但源表未接线（fail-closed） | {"contract_version": "0.1", "object_type": "Vendor", "filters": {}, "a | ✅ 契约执行失败（fail-closed 拒答）: Catalog Error: Table with name "scm.LFA1" does |
| 非 metric 契约带 time_range（P2-2 fail-closed） | {"contract_version": "0.1", "object_type": "Material", "filters": {},  | ✅ 契约校验失败（fail-closed 拒答）: 非 metric 契约不支持 time_range（v0.1 对象路径 fail-close |
| 维度过滤值注入 | {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_m | ✅ 契约校验失败（fail-closed 拒答）: 过滤值含疑似 SQL 片段（V4 防注入拒答）: matnr |
| time_range 非法 | {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_m | ✅ 契约校验失败（fail-closed 拒答）: time_range.from 必须 ≤ to: '2026-02-01' > '2026- |

## 6. 冷问题语义面扩展分析（设计 R5：指标可按实验增补，注册表加一条成本低）

B 当前语义面覆盖 8 问；22 问为冷问题。逐问给出「转可表达」所需扩展——均为 R5 授权的注册表/契约增量：

| 冷问题 | 所需扩展 |
|---|---|
| J1 每个客户各下过多少单？ | Customer 对象 + order_count_by_customer 指标（COUNT(DISTINCT VBELN)），或注册 Order 对象 + 链接 |
| J2 各品类库存金额排行 | stock_balance_by_mat_group 指标（加 MATKL 维度），或 stock 指标维度扩展 material_group |
| J3 哪些供应商到货准时率最高？ | receipt_qty_by_vendor 指标（Σ MSEG.MENGE WHERE BWART=101，按 LIFNR） |
| J4 退款金额 Top5 客户 | customer_refund_by_customer 指标（Σ -WSL WHERE SO 且 WSL<0）+ 契约 Top-N/排序截断扩展 |
| A2 品类×工厂×月三维汇总 | 3 维指标 cofv_qty_by_matkl_werks_month，或注册 COFV 对象走 v0.1 对象路径 |
| A3 各月下单客户数 | customer_count_by_month 指标（COUNT(DISTINCT KUNNR)） |
| A4 整体客单价 | 契约表达式扩展（除法/复合度量），或派生客单价指标 |
| A5 物料价格区间 | 需先补单价语义（派生 EKPO.NETWR/MENGE 或新增 price 字段）+ min/max 指标 |
| A6 各月订单量与金额趋势 | order_count_by_month 指标（订单数）；金额已可表达，需双度量或两契约 |
| F1 corporate 客户的高额订单 | Customer 对象 + segment(KTOKD) 过滤 + 订单 join（Order 对象或 order 指标） |
| F2 低于安全库存的物料清单 | 契约按度量值过滤扩展（HAVING 语义）或物化 low_stock 清单指标 |
| F3 已发货未送达的订单 | AUFK 对象 + status 过滤（状态过滤载体） |
| F4 退款超过阈值的订单 | 契约按度量值过滤扩展 + refund 语义指标 |
| L1 某物料的供应商是谁？ | 注册 material.vendor 链接（1 跳，EKPO→EKKO→LFA1 映射） |
| L2 订单对应客户及金额 | 注册 Order 对象 + order.customer 链接 |
| L5 订单→退款链路 | 注册 Order→Finance 链接（退款链路） |
| L6 财务条目对应订单来源 | 注册 FinanceEntry 对象 + finance.order 链接（条目明细路径） |
| T1 月订单量趋势 | order_count_by_month 指标 |
| T3 近 30 天日销售 | 日粒度指标（substr(1,10)）或 time_range 粒度扩展 |
| T4 本月 vs 上月退款对比 | refund 指标 + 双 time_range 对比扩展 |
| T5 平均到货时长趋势 | cofv_avg_hrs_by_month 指标（AVG ISMN1） |
| T6 季度汇总 | 季度维度派生指标（group_by 表达式扩展或预聚合季度） |

> 结论：受限结构化查询**形态本身**可表达 30 问中的 ~26-28 问（除 Top-N 截断、比值/除法、按度量值过滤 3 类需契约能力扩展）；当前只覆盖 8 问 = **语义面未按 30 问集扩充**（R5 待办），非形态之错。

## 7. 契约 v0.2 终版建议

**判定：head-to-head 未达成 → 按设计 §5 触发 Plan B，但终版 = 混合形态（受限结构化主路径 + 守卫化 SQL 兜底冷问题），而非纯 Plan B：**

1. **受限结构化查询（B）定为主路径**：可表达问题走契约（指标物化 + 对象路径），语义可枚举、可审计、fail-closed 拒答，可控性显著优于纯 SQL。
2. **Plan B 兜底冷问题**：~20% 冷问题（Top-N / 比值 / 任意 join / 明细）交给守卫化 LLM SQL（§5 实测 5/5 拦截注入）；审计粒度从「契约语义」降级为「SQL 文本」（设计 §5 同口径，报告如实标注）。
3. **v0.2 能力扩展（建议下一迭代落门禁 tests/test_p2_chatbi.py）**：
   - 语义面增补：按 §6 表注册 ~10 个新指标（订单数/退款/到货量/客户数/报工工时/日粒度等）+ 注册 Customer/Order/FinanceEntry 对象与 material.vendor 链接（对齐设计 §1.5 R5）；
   - V5 结果护栏语义修正（red-team P3-9）：上限按查询对象/指标规模派生，当前锚定 MARA（2400 行）挡住 A1/L4/F5 三个大结果问题，应改 analytics 口径；
   - 契约表达力：按度量值过滤（F2/F4）、Top-N/排序截断（J4）、表达式/除法（A4）、双 time_range 对比（T4）。
4. **风险与边界如实标注**：J3/F2/F3/A5/T5 因 demo 数据缺字段，口径已适配（§8）；LLM 生成有随机性，B 对可表达问题的契约质量直接影响成功率，不重试美化。

## 8. 实验方法、边界与可复现

- **口径适配清单**（demo 缺字段，如实调整期望口径）：J2 品类库存金额→库存量（无单价列）；J3 供应商准时率→到货量（无准时字段）；A5 物料价格区间→采购单价区间（无主数据价格）；F2 安全库存→阈值 1200（无安全库存字段）；F3 已发货未送达→工单 REL 状态（订单无发货状态）；T5 平均到货时长→平均报工工时（无到货时长）；T2 月库存金额→月销售金额（无库存月份维度，设计契约列本就指向销售物化）。
- **阈值文档化**：F1 高额=NETWR>90000；F4 |WSL|>50000；F5 仓库 W01/W02；T3 近 30 天=2026-12-02..31（数据止 2026-12-31）；T4 本月=2026-12 / 上月=2026-11。
- **比较口径**：key 列精确 + 数值列相对容差 0.5%（吸收显示舍入，仍抓住真实错误）；集合无序；列序按题目声明规范。B 的 V5 护栏拒答（结果 > 2400 行）按拒答计。
- **LLM 不确定性与诚实交付**：单次生成有随机性，本次如实记录；失败/拒答/错误全部计数，不重试美化。
- **可复现**：python3 scripts/headtohead/gt.py（GT）→ runner.py（主跑，seed 20260821）→ reeval.py（修正 GT/容差后重估，不烧 LLM）→ negatives.py（负例）→ report.py（本报告）。只读源库；未跑全量 pytest。

## 9. 待确认项（交 Jack 拍板）

1. **混合形态终版是否采纳**：受限结构化主路径 + 守卫化 SQL 兜底冷问题；确认后按 §7 增补指标/对象/链接，重跑一次全语义面实验验证 B 成功率能否过 85%。
2. **V5 结果护栏口径**：改为按查询规模派生（改 contract.py 常量/配置），还是保留现状（接受大结果问题拒答）？
3. **DeepSeek 计费口径**：本次按官方公开价（输入 ¥3/M、输出 ¥9/M）估算约 ¥0.2x；实际套餐/账单口径待对账。
4. **口径适配可否接受**：J2/J3/A5/F2/F3/T5 等因 demo 缺字段而适配的口径，是否需在 1M 行 demo 中补字段（改 schema = 先问）再复测？
