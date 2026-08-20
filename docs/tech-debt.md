# OntoRun 技术债登记

> 探索期欠的债显式记录，阶段迁移（S1->S2 等）时偿还。规则：每条 = 欠什么 / 为什么欠 / 何时还。

| # | 债务 | 原因（欠） | 偿还触发 | 状态 |
|---|---|---|---|---|
| TD-1 | builder 端点无 OpenAPI 契约测试 | 零到一 smoke 级 | P6 收口建 CI 时 | 开放 |
| TD-2 | pipeline_runs 走 in-memory 未落表 | P2 范围裁剪（蓝图未列表） | P6 全链路演示需历史 runs 时 | 开放 |
| TD-3 | extraction MockProvider 响应未 fixture 化 | P3 范围 | P4 E2E 精确断言时 | 关闭（P4：tests/golden/extraction_mock_responses.json + conftest fixture，P3 提取测试已重构引用） |
| TD-4 | alias_matcher no-match 率高（业务无关词未过滤） | P3 范围 | P4 映射效果评测时 | 评测完成（P4：partner_aliases.md x suppliers_dirty.csv，172 提及中 24 命中/148 no-match=86%，主因=提及公司不在供应商主表，算法非瓶颈；改进待 P6 效果评测时按需做） |
| TD-5 | Registry reload 全量重载（100+ 类型时延迟） | P3 简化 | P6 规模验证时 | 开放 |
| TD-6 | provider.chat 同步 blocking 未 async 化 | P3 范围 | P4 接真实 DeepSeek 时 | 关闭（P4：chat async 化 + 同步兼容包装，真调用不阻塞事件循环） |
| TD-7 | 测试制度演进史：P3 全量重跑 18 次教训（60s 超时陷阱） | 已固化进 AGENTS.md | 无需偿还，制度已修 | 关闭 |
| TD-8 | E6 审查 F2：绕过 API 直调引擎的非法 actor 走 failed 且 audit_ref 空（对账锚点缺失） | 独立审查发现（2026-08-20） | P6 全链路/权限治理时 | 开放 |
| TD-9 | E6 审查 F3：action_runs.executed_by 无 CHECK 白名单（audit_log.actor 有，schema 层不齐，store.py:200 vs :22） | 独立审查发现 | P6 治理 | 开放 |
| TD-10 | E6 审查 F4：audit_ref 无外键约束（store.py:203） | 独立审查发现 | P6 治理 | 开放 |
| TD-11 | E6 审查 F5：after 快照重读异常冒泡 → action_runs 缺行（对账缺口，action_runs.py:168-182） | 独立审查发现 | P6 收口 | 开放 |
| TD-12 | E6 审查 F6-F9（nit）：同秒排序不稳 / GET runs 无鉴权读快照 / dry_run 被拒语义 / 快照明文返回 | 独立审查发现 | P6 终审复核闭环时 | 开放 |
| TD-13 | E6 审查测试缺口：failed+有 effects 分支（after 重读源库新值）、dry_run+前置被拒组合（status=rejected 且 audit_ref 非空）无测试锁定 | 独立审查发现（E6 核心已被 15 用例锁定，此二为边界覆盖） | P6 全链路 E2E + 三问回归时补 | 开放 |
