# S2 P2 ChatBI 闭环完成记录（2026-08-21，读侧主体已落地）

> 编制：Rose ｜ 状态：P2 读侧闭环（指标/物化/契约 v0.2/权限）已实现并验证；head-to-head 实验待 Jack LLM 预算
> 依据：S2 开发计划 v0.3（P2 门禁）+ P2 设计 v0.1（上篇 58cdded + 下篇 ab8b7a7）

## 一、P2 目标与门禁
P2 = 本体读侧（对象→指标→物化结果）+ DuckDB 物化 + 受限结构化查询 + head-to-head 实验。
门禁：head-to-head 靶值 + P95 + 拒答率>0 + C4 reconcile + S1 零回归。

## 二、交付物（git 链）
| commit | 内容 |
|---|---|
| 58cdded + ab8b7a7 | P2 设计（上篇指标+物化 / 下篇契约 v0.2+head-to-head+Plan B） |
| 35a34aa | 指标注册表（des_metrics.yaml 15 指标 + M1-M7 校验） |
| 63a0fbb | DuckDB 物化管道（15 张 metric_<id> 表 + C4 全量重建 + T3 版本守卫 + reconcile diff=0） |
| 7c10f6f | 契约 v0.2 metric 执行路径（v0.1 兼容 + count_distinct 修复） |
| bf8df12 | 读侧权限接线（PermissionContext decide(read) + visible_attributes fail-closed） |
| be712f2 | P2 门禁测试 34 绿 |

## 三、验证结果
1. 物化：15 指标物化进 metrics.db（sales_amount_by_mat_month 77,936 行等），reconcile 15 条全 diff=0（C4 ✅）
2. 契约 v0.2：metric 查询「按物料+月销售金额」返回与源库直算逐位一致；非法 metric/维度 fail-closed；T3 版本守卫漂移拒答；v0.1 DQ-01（1200）完全兼容
3. 读侧权限：无 ctx 兼容；无策略 fail-closed；allow 放行；属性级 deny（old_code）请求不可见列拒答
4. 门禁测试：34 passed（指标注册表/物化 reconcile/契约 v0.2/权限/v0.1 兼容）
5. 阶段末全量 pytest：验证中（P2 代码增量回归此前 111 passed）

## 四、待办（P2 收尾）
1. **head-to-head 实验**（30 问 NL2SQL vs 本体版，定契约 v0.2 终版）——需 Jack 确认 LLM 预算（≈4-8 万 token，个位数元，火山套餐）后执行
2. 读侧权限的 API 层接线（FastAPI 路由带 actor → PermissionContext）——P4 权限完善一并做
3. 4 个本体对象注册（Customer/Vendor/InventoryLocation/FinanceEntry，⚠️ 等 Jack）——注册后指标 object_type 校验解除 planned 标记

## 五、待 Jack 拍板
1. P2 head-to-head LLM 预算
2. 4 个本体对象注册（⚠️ schema 变更）
3. P1.5 R3 审计修正策略
4. P4 PERMISSION_DENIED 错误码
