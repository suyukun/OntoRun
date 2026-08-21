# P2 head-to-head 实验报告 v2（语义面增补后重跑：26 指标 + 对象接线 + topN + 度量过滤）

> 生成：2026-08-22 00:01 ｜ 依据：docs/P2-ChatBI闭环设计_v0.1.md §4 ｜ 数据集：data/des/enterprises/hc_precision（5 源库 18 表 1,000,000 行 + metrics.db 26 指标物化）
> 方法：30 问 × 2 形态各 1 次 LLM 调用（DeepSeek deepseek-chat，seed 20260822）。A=LLM 生成 SQL → 多层守卫 → DuckDB 本地执行；B=LLM 生成契约 JSON → validate_contract + ContractExecutor（PermissionContext.allow_all 内部口径）。正确性 = 期望口径 GT（确定 SQL 预计算）按 key 精确 + 数值容差（相对 0.5%）比对。本轮 B 提示词同步语义面：26 指标目录（含定义）、对象接线（Material/Code/Customer/Vendor/InventoryLocation/FinanceEntry）、topN、度量过滤、time_range、口径说明。

## 0. 结论先行（BLUF）

- **A=Baseline（NL2SQL 直查）成功率 66.7%（20/30）**；**B=本体版（受限结构化查询）成功率 33.3%（10/30）**；Δ = **-33.3pp**。
- **靶值判定：B≥85% 未达成**。B 成功率 33.3% 距 85% 仍有差距；且当前语义面存在**结构性天花板**——30 问中 10 问冷问题不可表达 + 3 问可表达但口径发散（J1 零单客户 / A2 join 路径 / T4 标签），**即使契约生成完美，B 上限也只有 17/30 = 56.7%**，85% 靶值在现有 30 问集上不可达（需先扩展语义面 + 修口径，见 §6/§7）。
- 但 v1 主要归因已修复并验证：**语义面覆盖从 8 问扩到 20 问**（v1 22 问拒答中本轮新可表达 12 问）；**V5 护栏按规模派生后 A1/L4/F5 三个大结果问题不再误拒**；topN（J4）、度量过滤（F4）、time_range（T3）、对象接线（L6）均落地且命中。B 拒答率从 v1 86.7% 降至本轮 43.3%。
- B 剩余拒答 13 问主要为 10 问冷问题（受限面不可表达）+ 少量 LLM 主动拒答/契约校验拒答；B 错答 7 问含 3 问口径发散 + 其余为 LLM 契约质量问题（如实记录，不重试美化）。

## 1. 靶值判定（设计 §4.3）

| 靶值 | 实测 | 达成 |
|---|---|---|
| A=Baseline 成功率 ≥ 70% | 66.7% | ❌ 未达成 |
| B=本体版成功率 ≥ 85% | 33.3% | ❌ 未达成 |
| Δ = B−A ≥ 10pp | -33.3pp | ❌ 未达成 |
| 拒答率 > 0（两形态） | A 3.3% / B 43.3% | ✅ 达成 |
| 执行延迟 P95 ≤ 500ms（A） | 200ms | ✅ 达成 |
| 执行延迟 P95 ≤ 500ms（B） | 86ms | ✅ 达成 |

> 执行延迟 P95 不含 LLM 网络耗时；B 仅对实际执行的契约计 P95。拒答率 > 0 由主跑拒答 + 负例演示共同证明（§5）。

## 2. 汇总指标（vs v1 对比）

| 指标 | A=Baseline | B=本体版 | v1 B（参考） | 说明 |
|---|---|---|---|---|
| 成功率 | 66.7%（20/30） | 33.3%（10/30） | 6.7%（2/30） | Δ = -33.3pp |
| 拒答率（fail-closed） | 3.3%（1/30） | 43.3%（13/30） | 86.7%（26/30） | B 拒答=受限面不可表达+校验/护栏拒答 |
| 错误答案率（执行成功但≠GT） | 8/30 | 7/30 | 2/30 | |
| 错误率（LLM/执行/解析失败） | 1/30 | 0/30 | 0/30 | |
| 执行延迟 P95 / 均值 | 200ms / 57ms（29 次） | 86ms / 37ms（20 次） | 165ms / 28ms | |
| LLM 单次延迟 P95 / 均值 | 1422ms / 1014ms | 1922ms / 1181ms | 1739ms / 1206ms | 网络+生成 |
| LLM token（输入/输出） | 39,865 / 1,960 | 91,794 / 2,196 | 31,063 / 2,272 | 30 问合计 |
| 成本估算（元） | ¥0.1372 | ¥0.2951 | ¥0.1136 | 见 §8 |

**分项解读**：
- B 语义面从 v1 的 8 问扩到 20 问（+12），本轮 B 正确 10 问 / 错答 7 问 / 拒答 13 问。v1 拒答的 22 问中，本轮新可表达 12 问（J1、J2、J3、J4、A2、A3、F4、L6、T1、T3、T4、T5），其中命中正确 5 问（J2、J4、F4、L6、T3）。
- B 错答 7 问构成：3 问语义面口径发散（J1/A2/T4，见 §6.2）+ 其余为 LLM 契约生成质量问题（如 J3、J5、F5、T1、T2）。
- B 拒答 13 问构成：10 问冷问题受限面不可表达 + 其余为 LLM 主动拒答或契约校验 fail-closed（拒答本身 = 受限面可控性价值，不视为错误）。
- 延迟：两形态执行 P95 均 ≤ 500ms（A 200ms / B 86ms）。B 的 P95 含大结果物化查询（A1 77,936 / L4 24,000 / F5 16,000 / L6 16,400 行），小查询（J6/F6 等）毫秒级。

## 3. 30 问结果表

> 「B可表达」= 本轮语义面（26 指标 + 5 对象 + topN/度量过滤/time_range）是否可表达；GT 行数来自预计算 GT；备注列标注口径说明/失败原因。

| 问 | 组 | 问法 | B可表达 | GT行数 | A结果 | B结果 | A exec(ms) | B exec(ms) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| J1 | G1 | 每个客户各下过多少单？ | ✅ | 10000 | wrong | refusal | 16.4 | 0.0 | 校验/护栏拒答 |
| J2 | G1 | 各品类库存金额排行 | ✅ | 250 | correct | correct | 12.2 | 18.6 | 口径说明: demo 库无单价列（MARA/MARC |
| J3 | G1 | 哪些供应商到货准时率最高？ | ✅ | 4962 | wrong | wrong | 200.5 | 22.2 | 行数不一致: GT 4962 vs answ |
| J4 | G1 | 退款金额 Top5 客户 | ✅ | 5 | correct | correct | 36.6 | 19.6 | 口径说明: 「退款」= REF_TYPE='SO'  |
| J5 | G1 | 各仓库库存水位 | ✅ | 3 | correct | wrong | 9.7 | 16.2 | GT key 缺失: ('W01',) |
| J6 | G1 | 有多少一物多码的物料？ | ✅ | 1 | correct | correct | 5.8 | 11.2 |  |
| A1 | G2 | 各月各物料销售金额合计 | ✅ | 77936 | correct | correct | 280.5 | 192.0 | 口径说明: 设计契约列指向销售物化（metric b |
| A2 | G2 | 品类×工厂×月三维汇总 | ✅ | 12000 | refusal | wrong | - | 43.5 | 口径发散 |
| A3 | G2 | 各月下单客户数 | ✅ | 24 | correct | refusal | 24.3 | 0.1 | 校验/护栏拒答 |
| A4 | G2 | 整体客单价 | — | 1 | correct | refusal | 53.6 | - | 口径说明: 金额口径 = 订单项目销售金额合计（VB |
| A5 | G2 | 物料价格区间 | — | 1 | wrong | refusal | 71.1 | - | 口径说明: demo 库无主数据单价列；适配口径 = |
| A6 | G2 | 各月订单量与金额趋势 | — | 24 | wrong | refusal | 20.9 | 0.0 | 受限面不可表达 |
| F1 | G3 | corporate 客户的高额订单 | — | 1281 | correct | refusal | 24.6 | - | 口径说明: corporate = KTOKD '0 |
| F2 | G3 | 低于安全库存的物料清单 | — | 9 | correct | refusal | 19.3 | 0.1 | 口径说明: demo 库无安全库存字段；适配口径 = |
| F3 | G3 | 已发货未送达的订单 | — | 22574 | correct | refusal | 115.9 | - | 口径说明: demo 库销售订单无发货/送达状态；适 |
| F4 | G3 | 退款超过阈值的订单 | ✅ | 4100 | wrong | correct | 41.7 | 20.8 | 口径说明: 退款 = REF_TYPE='SO' 且 |
| F5 | G3 | 指定品类×仓库组合的库存 | ✅ | 16000 | correct | wrong | 25.7 | 16.1 | answer 列数不足 (need 4) |
| F6 | G3 | 含多码物料明细 | ✅ | 1200 | correct | correct | 8.4 | 76.9 |  |
| L1 | G4 | 某物料的供应商是谁？ | — | 10 | correct | refusal | 117.4 | - | 口径说明: 样例物料 MAT-2026-0001-K |
| L2 | G4 | 订单对应客户及金额 | — | 1 | error | refusal | 12.4 | - | 口径说明: 样例订单 SO-2026-000001； |
| L3 | G4 | 物料多码全码列表 | ✅ | 6000 | wrong | correct | 7.3 | 81.0 | 口径说明: 每个一物多码物料（old_code 非空 |
| L4 | G4 | 库存位置-物料-库存量 | ✅ | 24000 | correct | correct | 51.1 | 74.9 |  |
| L5 | G4 | 订单→退款链路 | — | 8216 | correct | refusal | 33.6 | - | 口径说明: 退款 = REF_TYPE='SO' 且 |
| L6 | G4 | 财务条目对应订单来源 | ✅ | 16400 | correct | correct | 58.9 | 86.1 | 口径说明: SO 类型财务分录（ACDOCA.REF |
| T1 | G5 | 月订单量趋势 | ✅ | 24 | correct | wrong | 8.3 | 16.1 | 行数不一致: GT 24 vs answer |
| T2 | G5 | 月库存金额趋势 | ✅ | 24 | correct | wrong | 39.2 | 15.8 | 行数不一致: GT 24 vs answer |
| T3 | G5 | 近 30 天日销售 | ✅ | 30 | correct | correct | 129.0 | 19.6 | 口径说明: 「近 30 天」= 数据末 30 天（2 |
| T4 | G5 | 本月 vs 上月退款对比 | ✅ | 2 | wrong | wrong | 12.3 | 15.4 | 口径发散 |
| T5 | G5 | 平均到货时长趋势 | ✅ | 24 | correct | refusal | 186.1 | 0.1 | 口径说明: demo 库无到货时长字段；适配口径 = |
| T6 | G5 | 季度汇总 | — | 8 | wrong | refusal | 34.8 | - | 口径说明: 季度 = 年 + Q + FLOOR(( |

## 4. B 形态逐问细账（可表达集 + 失败/拒答原因）

| 问 | B 结果 | 明细 |
|---|---|---|
| J1 每个客户各下过多少单？ | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: 聚合 count_distinct 非可加，禁物化表子集重聚合 gr |
| J2 各品类库存金额排行 | correct |  |
| J3 哪些供应商到货准时率最高？ | wrong | 行数不一致: GT 4962 vs answer 10 |
| J4 退款金额 Top5 客户 | correct |  |
| J5 各仓库库存水位 | wrong | GT key 缺失: ('W01',) |
| J6 有多少一物多码的物料？ | correct |  |
| A1 各月各物料销售金额合计 | correct |  |
| A2 品类×工厂×月三维汇总 | wrong | 语义面口径发散：join 路径分歧：cofv_qty_by_matkl_werks_month 以 COFV.MATNR→MARA 取物料组，GT 以 AUFK.MATNR→MARA；demo 数 | 实际：GT key ('Z-FERT-01', 'PL01 |
| A3 各月下单客户数 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: 聚合 count_distinct 非可加，禁物化表子集重聚合 gr |
| F4 退款超过阈值的订单 | correct |  |
| F5 指定品类×仓库组合的库存 | wrong | answer 列数不足 (need 4) |
| F6 含多码物料明细 | correct |  |
| L3 物料多码全码列表 | correct |  |
| L4 库存位置-物料-库存量 | correct |  |
| L6 财务条目对应订单来源 | correct |  |
| T1 月订单量趋势 | wrong | 行数不一致: GT 24 vs answer 0 |
| T2 月库存金额趋势 | wrong | 行数不一致: GT 24 vs answer 0 |
| T3 近 30 天日销售 | correct |  |
| T4 本月 vs 上月退款对比 | wrong | 语义面口径发散：呈现标签差异：refund_amount_by_month 返回月份标签（2026-11/2026-12），GT 为 cur/prev 标签；数值一致仅标签不同（key 精确比较失 | 实际：GT key 缺失: ('cur',) |
| T5 平均到货时长趋势 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: 聚合 avg 非可加，禁物化表子集重聚合 group_by: cof |
| A6 各月订单量与金额趋势 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: 聚合 count_distinct 非可加，禁物化表子集重聚合 gr |
| F2 低于安全库存的物料清单 | refusal | 校验/护栏拒答（fail-closed）：校验/执行拒答(fail-closed): 契约校验失败（fail-closed 拒答）: 未知顶层键（additionalProperties:false）: |

## 5. 拒答率 > 0 的 fail-closed 证据（独立负例，不烧 LLM）

**A 形态多层守卫**（只读白名单视图 / 单语句 / 禁注入 / 结果护栏 / 超时）：

| 用例 | 触发 | 守卫捕获 |
|---|---|---|
| 注入多语句 | SELECT * FROM MARA; DROP TABLE MARA | ✅ 含禁用片段: ';'；含禁用片段: 'drop' |
| 注入注释逃逸 | SELECT * FROM MARA WHERE MATNR='x' --' OR 1=1 | ✅ 含禁用片段: '--' |
| 写库 DML | DELETE FROM MARA WHERE MATNR='MAT-2026-0001-K4V' | ✅ 非 SELECT/WITH 单语句 |
| 非白名单表 | SELECT * FROM sys.sensitive | ✅ 引用非白名单表: ['sys.sensitive'] |
| 外部数据源 | SELECT * FROM read_csv('/etc/passwd') | ✅ 含禁用片段: 'read_csv'；引用非白名单表: ['read_csv'] |

**B 形态契约校验**（V1-V5 + M 系列 + P2-2 time_range fail-closed）：

| 用例 | 触发 | 校验拒答 |
|---|---|---|
| 未知 metric_id | {"contract_version": "0.2", "metric": {"metric_id": "not_a_metric"}} | ✅ 契约校验失败（fail-closed 拒答）: metric_id 不在指标注册表（M 系列）: 'not_a_metric' |
| 未知对象（V1 白名单） | {"contract_version": "0.1", "object_type": "FooObject", "filters": {}, | ✅ 契约校验失败（fail-closed 拒答）: object_type 未注册或非法（V1 白名单）: 'FooObject' |
| 对象过滤字段不在白名单（V2） | {"contract_version": "0.1", "object_type": "Vendor", "filters": {"not_ | ✅ 契约校验失败（fail-closed 拒答）: 过滤字段不在 Vendor 白名单: not_a_field |
| 非 metric 契约带 time_range（P2-2 fail-closed） | {"contract_version": "0.1", "object_type": "Material", "filters": {},  | ✅ 契约校验失败（fail-closed 拒答）: 非 metric 契约不支持 time_range（v0.1 对象路径 fail-close |
| 维度过滤值注入 | {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_m | ✅ 契约校验失败（fail-closed 拒答）: 过滤值含疑似 SQL 片段（V4 防注入拒答）: matnr |
| time_range 非法 | {"contract_version": "0.2", "metric": {"metric_id": "sales_amount_by_m | ✅ 契约校验失败（fail-closed 拒答）: time_range.from 必须 ≤ to: '2026-02-01' > '2026- |

> 本轮对象接线已修复 v1 的「注册对象≠可查询对象」缺口：Vendor/InventoryLocation/FinanceEntry 的 v0.1 对象路径可查（物化表 vendor/inventory_location/finance_entry）。

## 6. 剩余缺口分析（B 为何仍未过 85%）

### 6.1 结构性天花板：30 问集的语义面上限

- **10 问冷问题（受限面不可表达）**：A4、A5、A6、F1、F2、F3、L1、L2、L5、T6。逐问所需扩展：
| 冷问题 | 所需扩展 |
|---|---|
| A4 整体客单价 | 契约表达式/除法扩展（Σ金额 / COUNT DISTINCT 客户），或派生客单价指标 |
| A5 物料价格区间 | 补单价语义（EKPO.NETWR/MENGE 派生 price）+ min/max 指标 |
| A6 各月订单量与金额 | 双度量契约（单 metric 契约只能一个度量）或 order+sales 复合指标 |
| F1 corporate 高额订单 | Customer.segment(KTOKD) 过滤 + Order 对象/链接（订单 join） |
| F2 低库存清单 | 分组后度量过滤（HAVING 语义）；当前度量过滤仅物化粒度行级 WHERE |
| F3 已发货未送达 | AUFK 对象 + status 过滤（状态过滤载体） |
| L1 某物料供应商 | material.vendor 链接（1 跳，EKPO→EKKO→LFA1 映射） |
| L2 订单对应客户及金额 | Order 对象 + order.customer 链接 |
| L5 订单→退款链路 | 需 订单号+客户+退款 三联指标（refund+customer+vbeln 合一）或 Order→Finance 链接 |
| T6 季度汇总 | 季度派生维度指标（group_by 表达式扩展或预聚合季度） |

- **3 问可表达但口径发散（参考契约执行也必 wrong）**：J1 零单客户缺口 / A2 join 路径发散 / T4 标签呈现差异（详见 §4 与 §6.2）。
- **结论：B 完美契约上限 = 17/30 = 56.7%**，低于 85% 靶值（25.5/30）。要在 30 问集达成 85%，需把上述 10 问冷问题转可表达（≥8 问）+ 修 3 问口径发散 + 保持 B 契约生成质量。
- **可表达集内成功率**（仅计 20 问可表达集）：本轮 50.0%（10/20）；剩余失败 = 4 问 LLM 契约质量问题（J5/F5/T1/T2）+ 2 问冗余 group_by 拒答（A3/T5）+ 3 问口径发散/缺口（J1/A2/T4）+ 1 问口径歧义（J3），见 §4/§6.3。

### 6.2 语义面口径发散专项（新发现，v1 未暴露）

| 问 | 发散点 | 影响 |
|---|---|---|
| J1 每客户下单数 | 指标 order_count_by_customer 只含 ≥1 单的 9,823 客户，无 LEFT JOIN（0 单客户）语义 | B 少 177 行 → 行数不一致必 wrong |
| A2 品类×工厂×月 | cofv_qty_by_matkl_werks_month 以 COFV.MATNR 取物料组，GT 以 AUFK.MATNR；demo 两列几乎全不同 | 数值偏差 ~14% 必 wrong（指标口径需拍板） |
| T4 本月vs上月退款 | refund_amount_by_month 返回月份标签，GT 为 cur/prev 标签；数值一致 | key 精确比较失败；标签归一化后可判对 |
| J3 供应商到货准时率 | 「最高」口径歧义：GT 全量 4,962 供应商按量降序，LLM 读成 Top-N（topN=10） | 行数不一致必 wrong；两形态同受此歧义影响（A 本轮也 wrong） |

### 6.3 B 契约生成质量（LLM 随机性如实记录）

B 在可表达 20 问上，正确/错答/拒答分布见 §2；单次生成有随机性（seed 20260822），不重试美化。契约质量受提示词语义面完整度影响，本轮已含指标定义/对象/示例契约，仍存在 LLM 选错指标粒度或 group_by 越界等偶发（见 §4 明细）。

## 7. 结论与建议

1. **混合形态终版方向不变，但 85% 靶值需重新对齐**：B 语义面从 8→20 问、V5 误拒修复、topN/度量过滤/对象接线均落地验证，受限结构化查询（B）作主路径的能力成立；但当前 30 问集上 B 有 ~10 问冷问题 + 3 问口径发散，**85% 成功率的靶值在现有语义面下不可达**——建议按 §6.1 扩展（8 问）并修 §6.2 口径（3 问）后重跑，或将靶值对齐「可表达问题集内成功率」。
2. **口径发散需 Jack 拍板**：A2 cofv 指标 join 路径（COFV.MATNR vs AUFK.MATNR）、T4 标签口径（月份 vs cur/prev）、J1 零单客户（指标补 LEFT JOIN 语义或调整 GT 口径）。
3. **V5 护栏已按规模派生**（red-team P3-9 落地）：A1/L4/F5 大结果问题从 v1 误拒改为放行，不再掩盖语义面表达力。
4. **拒答即可控性**：B 的 fail-closed 拒答（冷问题/非法契约）是受限查询的核心价值，本轮负例 5/5 拦截保持。

## 8. 方法、边界与可复现

- **口径适配清单**（与 v1 相同，demo 缺字段如实调整）：J2 品类库存金额→库存量；J3 供应商准时率→到货量；A5 物料价格区间→采购单价区间；F2 安全库存→阈值 1200；F3 已发货未送达→工单 REL 状态；T5 平均到货时长→平均报工工时；T2 月库存金额→月销售金额（设计契约列本就指向销售物化）。
- **阈值文档化**：F1 高额=NETWR>90000；F4 |WSL|>50000；F5 仓库 W01/W02；T3 近 30 天=2026-12-02..31；T4 本月=2026-12 / 上月=2026-11。
- **比较口径**：key 列精确 + 数值列相对容差 0.5%；集合无序；列序按题目声明。B 的 fail-closed（校验/护栏）按拒答计，LLM 主动拒答按拒答计。
- **成本估算**：DeepSeek 官方公开价 输入 ¥3/M、输出 ¥9/M；本轮 B 提示词含 26 指标目录更长，token/成本较 v1 略增，合计仍个位数元。
- **LLM 不确定性与诚实交付**：单次生成有随机性（seed 20260822），失败/拒答/错误全部计数，不重试美化；对比 v1（seed 20260821）如实标注。
- **可复现**：gt.py（GT）→ runner.py 20260822（主跑）→ negatives.py（负例）→ report_v2.py（本报告）。只读源库；未跑全量 pytest。harness 改动点见 §9.4。

## 9. 待确认项（交 Jack 拍板）

1. **85% 靶值的口径**：继续按 30 问集扩展语义面（§6.1 10 问转可表达 + §6.2 3 问修口径）后重跑冲 85%，还是先把靶值对齐「可表达问题集内成功率」（本轮可表达 20 问集内为 50.0% = 10/20）？
2. **A2 cofv 指标 join 路径**：COFV.MATNR vs AUFK.MATNR 以哪个为准（demo 数据两列几乎全不同，涉及报工物料归属语义）？
3. **T4 标签口径**：退款对比的 key 用月份标签还是 cur/prev 标签（呈现层 vs 数据层）？
4. **harness 改动点**（Rose 复核）：scripts/headtohead/questions.py（20 问 b_expressible/b_contract/b_note 更新）、prompts.py（B 语义面/对象/契约 schema 示例/口径注入）、runner.py（L6 对象明细提取 + B 提示词带口径）。未改 src/des/* 与 GT。
