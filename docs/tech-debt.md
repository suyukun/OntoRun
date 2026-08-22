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
| TD-8 | E6 审查 F2：绕过 API 直调引擎的非法 actor 走 failed 且 audit_ref 空（对账锚点缺失） | 独立审查发现（2026-08-20） | P6 全链路/权限治理时 | 评估完成（S1 收口：维持现状 + 边界说明，见 §偿还记录） |
| TD-9 | E6 审查 F3：action_runs.executed_by 无 CHECK 白名单（audit_log.actor 有，schema 层不齐，store.py:200 vs :22） | 独立审查发现 | P6 治理 | 关闭（executed_by CHECK 已落地 + 存量库迁移，commit c3cea1c，见 §偿还记录） |
| TD-10 | E6 审查 F4：audit_ref 无外键约束（store.py:203） | 独立审查发现 | P6 治理 | 决策=低风险备选（维持应用层对账 + 发布期 Postgres 原生 FK，不擅改 DDL，见 §偿还记录） |
| TD-11 | E6 审查 F5：after 快照重读异常冒泡 → action_runs 缺行（对账缺口，action_runs.py:168-182） | 独立审查发现 | P6 收口 | 已修复（S1 收口：降级 failed run 不丢行，见 §偿还记录） |
| TD-12 | E6 审查 F6-F9（nit）：同秒排序不稳 / GET runs 无鉴权读快照 / dry_run 被拒语义 / 快照明文返回 | 独立审查发现 | P6 终审复核闭环时 | 部分处置（F6 已满足；F7-F9 保留发布期，见 §偿还记录） |
| TD-13 | E6 审查测试缺口：failed+有 effects 分支（after 重读源库新值）、dry_run+前置被拒组合（status=rejected 且 audit_ref 非空）无测试锁定 | 独立审查发现（E6 核心已被 15 用例锁定，此二为边界覆盖） | P6 全链路 E2E + 三问回归时补 | 已修复（S1 收口：tests/test_builder_p4.py 补 2 用例，见 §偿还记录） |
| TD-14 | 链接反向/入向遍历 404：前端 LinkNav 的 link_name 不随 direction 换名（out 传 name / in 应传 inverse_name），后端按名严格匹配即 404；React StrictMode 双请求致一次报两次 | Jack 试用发现（2026-08-20），根因已定位（web/src/components/LinkNav.tsx + src/runtime/query.py::_other_type） | Jack 拍板修复时（修法二选一：前端按 direction 传名，或后端按名解析定义再决定方向） | 开放 |
| TD-15 | 会话历史无持久化：前端消息内存态 + 后端 SessionManager 内存映射（刷新/重启即失） | MVP 简化 | 发布期（S2 用户体系/多进程时迁 Redis/DB） | 开放 |

---

## S1 收口偿还记录（2026-08-20）

> 偿还触发 = P6 收口（蓝图 §12 验收通过，S1 全链路一条命令 E2E 全绿）。本小节逐条记录
> 处置结果；TD-9 经 Jack 拍板已落地（schema CHECK + 存量库迁移）；TD-10 维持
> Jack 拍板的低风险备选（应用层对账，外键等 Postgres 发布期原生实现），未擅改 DDL。

### TD-11（已修复，代码修复）

- 病灶：`src/builder/logic/action_runs.py` 的 `_reread_records` 只捕 KeyError，非 KeyError
  异常冒泡 → after 快照构造失败 → action_runs 缺行（源库已变 + 审计已落 = 对账缺口）。
- 修复（action_runs.py:305-326）：`run_action` 将 after 快照构造包进 try/except 兜底；
  异常时降级为 `failed` action_run：`error=EXECUTION_FAILED + 稳定安全摘要`（F1 口径，
  不回显原始异常/SQL 细节，原始异常只进日志）、**保留 audit_ref 锚点**（引擎侧审计已落，
  对账闭合）、`after_snapshot` 带 `degraded: True` 显式降级标记（不伪造数据）。
- 回归测试（tests/test_builder_p4.py `test_snapshot_reread_failure_records_failed_run`）：
  注入重读异常 → 响应 200/failed、GET /runs 有 failed 行（不丢行）、audit_ref 对账到
  audit_log 的 applied 记录、源库状态如实反映（cancelled）、error 不含原始异常文本。

### TD-13（已修复，补测试）

- (a) failed + 有 effects 分支：`test_failed_with_effects_after_rereads_source_new_value`
  —— 注入引擎 ⑦ 同步失败（FAILED_CODE_SYNC + effects 存在）→ after 重读源库新值
  （cancelled），audit_ref 对账 failed 审计，源库状态如实。
- (b) dry_run + 前置被拒组合：`test_dry_run_rejected_combination` —— dry_run 请求 +
  已发货订单 → status=rejected 且 audit_ref 非空（拒绝优先于 dry_run 模拟，审计照落）。

### TD-12（部分处置）

| nit | 结论 | 说明 |
|---|---|---|
| F6 同秒排序不稳 | **已满足** | `list_by_action` 自 P4 起即 `ORDER BY created_at DESC, id DESC`（action_runs.py:152），同秒按 id 辅助排序，无需改动 |
| F7 GET runs 无鉴权读快照 | 保留（发布期） | MVP 无用户体系（本地演示）；快照/审计属敏感数据，发布期随权限治理统一加鉴权 |
| F8 dry_run 被拒语义 | 保留（设计如此） | 拒绝优先于 dry_run 模拟：引擎 docstring 已写明「拒绝路径早退语义不变」（action_engine.py:220-221）；TD-13(b) 测试已锁定该语义 |
| F9 快照明文返回 | 保留（发布期） | MVP 内部演示可接受；发布期随鉴权治理（与 F7 同批） |

### TD-8（评估完成：维持现状 + 边界说明）

- 现状：引擎层已兜底非法 actor（action_engine.py:228-235，`actor not in ALLOWED_ACTORS`
  → failed + 稳定 message，**源库零变更、无真实写回**）；action_runs 落 failed 行且
  audit_ref 空（对账锚点缺失 = 无审计记录可引用，与 dry_run 的 audit_ref 空同语义）。
- 结论：**维持现状**。理由：非法 actor 无法产生真实写回（引擎在参数校验前即拒绝），
  audit_ref 空只影响「审计留痕」不影响「数据完整性」；API 层另有 X-Actor 400 白名单拦截在前
  （builder_logic_action_routes.py:79-96），直调引擎仅测试/内部代码可达。边界已在本表
  记录 + action_runs 模块 docstring 说明；发布期权限治理时再评估加 actor 告警。

### TD-9（已修复，Jack 已拍板，commit c3cea1c）

- 落地 DDL（`src/runtime/store.py`）：`BUILDER_SCHEMA` 的 action_runs 定义改为
  `executed_by TEXT NOT NULL DEFAULT 'api' CHECK (executed_by IN ('human','llm','api'))`
  （列定义抽为 `ACTION_RUNS_COLUMNS` 常量，建表与迁移重建共用单一来源）。
- 同源收口（防双轨漂移）：`ALLOWED_ACTORS` 收至 `src.runtime.store` 单一来源
  （`action_engine` 改为从此导入；API 层 X-Actor 白名单引用不变）；CHECK 值经
  `ACTOR_VALUES_SQL` 派生注入 `audit_log.actor` 与 `action_runs.executed_by`，
  并由 test_builder_p4.py `TestExecutedByCheck.test_check_values_same_source_as_allowed_actors`
  做机器断言锁定同源。
- 存量库迁移（v4 幂等补丁 `_apply_builder_patches` / `_patch_action_runs_executed_by_check`）：
  SQLite 无 `ALTER ADD CONSTRAINT`，重建表迁移——单事务内建新表（含 CHECK）→
  INSERT..SELECT 拷数据 → DROP 旧表 → RENAME → 重建索引；失败整体回滚不丢数据；
  新库/已迁移库经 sqlite_master 检出幂等跳过。本机演示库 data/ontology/ontology.db
  已执行迁移（action_runs 0 行，数据零损失，schema_version 仍为 1）。
- schema_version 评估：**不 bump**。理由：v2/v3 先例即「幂等补丁只追加 note 不升号」
  （link_types.fk_field / action_runs.audit_ref 均如此）；bump 会破坏
  `get_schema_version()==1` 既有契约（tests/test_b2_action_engine.py:736）。
  版本历史记于 note 注脚（`v4 patch: action_runs.executed_by CHECK（TD-9）`）。
- 测试：`TestExecutedByCheck` 四用例——非法直插被拒（IntegrityError）、白名单三值
  （human/llm/api）可插、DDL 与 ALLOWED_ACTORS 同源机器检查、存量库迁移后数据保留
  + 约束生效。

### TD-10（Jack 决策：低风险备选，不擅改 DDL）

- 现状：`action_runs.audit_ref` 无外键（store.py:203），仅应用层对账（测试断言
  audit_ref 可对账到 audit_log.audit_id）。
- **Jack 决策（2026-08-20）= 低风险备选**：维持空串 + 应用层对账不变（不把
  audit_ref 改可空、不加 SQLite 外键、不开 `PRAGMA foreign_keys`），发布期随
  Postgres 迁移由 DB 原生外键实现。理由：SQLite 默认 foreign_keys=OFF，外键落地
  须在 Store 连接层统一开启（主要工作量）且属破坏性变更（dry_run 空串→NULL、
  API 返回 '' vs null 需同步）；当前对账已有测试锁定，收益 < 成本。
- 本次未改 TD-10 相关 DDL（保持 `audit_ref TEXT NOT NULL DEFAULT ''` 不变）。