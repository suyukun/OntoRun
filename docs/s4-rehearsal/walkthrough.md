# S4 七幕实走查记录（M4 输入，2026-09-01）

> 环境：后端 :8000（已载再生数据 + 真实 DeepSeek key）；走查人 Rose；基准 = verify_demo_numbers.py 62/62。

## 实测通过项

| 幕 | 端点/操作 | 实测结果 |
|---|---|---|
| 0 对照帧 | 静态素材（前端帧） | 前端 ActComparison 组件（M3b，vitest 覆盖） |
| 1 揭示 | GET /risk/evidence/group-reveal?group=天晟集团有限公司 | conclusion=「逐家安全（8.0%/5.5%/8.2%），归集 86.4÷800=10.8% ≥ 预警线 → 橙」；rules_hits=[R1a,R1b]；denominator=base.ap_sys_param.CAP_GROUP_CONSOLIDATED；detail_rows 含三家分母 |
| 2 升级识别 | GET /risk/evidence/related-upgrade | 恒昌三线索（股权代持/交叉担保/资金往来，row_ref=RT-2026-900001/2/3）→ 102.4/800=12.8% 红；rules=[R2,R1a] |
| 3 确认（写回） | chat 多轮：确认 WS-2026-00014921 | outcome=applied，信号真实变更为已确认；AI 全程先校验状态再动作 |
| 3 反例（治理加分） | chat：对已确认信号重复提交 | AI 两次拒绝（「已确认完毕」「已不在草稿阶段」），引导合规路径；对天晟主信号（已处置中）的重复处置同样拒绝 |
| 4 证据链 | GET /risk/evidence/approval-chain | 返回 PROCESS 审批单 APP-2026-00000001 全链（signal+disposal+orders/tasks）+ 第二十三条驳回依据 |
| 5 报送初稿 | GET/POST /risk/reporting/draft | 12.8% 口径 + 2018 办法 37/34 条原文；橙→400 NOT_RED_WARNING |
| 6 看板 | GET /risk/dashboard | 前十大排名（天晟 10.8% #1）、七态计数、超期/响应时效 |

## 真实 LLM 对话样例（POST /agent/risk/chat，DeepSeek 实测）

问：「天晟集团的风险有多大？」→ 答：机构分解表（银行 48 亿 8.0%/证券 22 亿 5.5%/资管 16.4 亿 8.2%，单看安全）→ R1b 引 2018 办法第七/八条 → 归集 86.4÷800=10.8% ≥ 预警线 → 橙色预警。响应含 evidence 载荷（basis_tables/rules_hits/denominator/detail_rows/signals）。

## 已知走查发现（供彩排重点压测）

1. 天晟主信号（WS-2026-90000002）道具态为处置中 → 第 3 幕「提交处置」需改用其他待确认红色信号（如 WS-2026-00014921 先确认再处置），或演示时以第 2 幕确认动作作为写回演示点。
2. 天晟红色预警无关联审批单（approval_chain 如实返回「暂无待审批单」）→ 第 4 幕双签落在系统内真实 PROCESS 审批单上，话术需说明「以在办审批单演示」。
3. 处置多轮对话中 AI 走合规路径较谨慎（先确认后处置、拒绝重复提交）——演示话术应把这包装成卖点而非障碍。
