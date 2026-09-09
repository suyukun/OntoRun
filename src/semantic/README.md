# src/semantic — T1 后端语义服务（fortune-registration）

demo（`scripts/fortune_demo/`，只读）机制工程化：规则注册表配置化、iter_query 事件流、
LLM 路由（枚举硬校验 + 关键词降级）、八状态结构化、会话/消息持久化、幂等、错误码、
脱敏与 PII 钩子。产品契约：`docs/财富广场-ChatBI展示层产品设计_v0.2.md`。

## 启动

```bash
/opt/anaconda3/bin/python3 -m uvicorn src.semantic.app:app --port 8901
# 或复用冒烟脚本（自带起停服务 + 六状态断言）：
scripts/semantic_smoke.sh
```

依赖项目根 `.env`：`DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL`。
环境开关：`SEMANTIC_DISABLE_LLM=1` 强制关键词路由（联调/限流期）；
`SEMANTIC_APP_DB` / `SEMANTIC_TRACE_LOG` / `FORTUNE_DB` 覆盖存储路径（测试用）。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/profile | 附录 C schema（fortune-registration 档案，viz_map/rule_hints 由规则表生成） |
| POST | /api/chat | SSE：`{question, conversation_id?, client_request_id?}`；帧 step/token/final（+error 终帧）；阻塞步超 14s 发心跳注释帧 |
| GET | /api/history?limit=50 | trace JSONL 列表（过滤已隐藏） |
| GET | /api/trace/{rid} | 完整 trace 快照（已隐藏 → 404） |
| DELETE | /api/history/{rid} | 历史/会话删除 = 隐藏标记，trace 物理保留（审计链） |
| POST/GET | /api/sessions | 新建 / 列表（隐藏过滤，置顶优先） |
| GET/PATCH/DELETE | /api/sessions/{id} | 详情（含 messages，快照回放源）/ 重命名·置顶·收藏 / 删除=hidden |

chat 落库：每次问答向会话追加 user + assistant 两条消息；assistant 消息携带
完整 final result 快照（`result_json`）→ T4 快照回放直接消费。

## 八状态映射（§4.2，path→state 一对一，前端不猜文案）

| state | 后端 path | block_reason |
|---|---|---|
| success / success_warning | hot / cold_pushdown / cold_adhoc | —（warning=LLM 降级关键词，degraded=true） |
| empty | 同上（0 行） | — |
| ask_param | blocked_param | missing_param |
| reject_range | blocked_param | out_of_range |
| reject_unregistered | unregistered | — |
| reject_scope | rejected | — |
| validation_failed | validation_failed | — |
| error | error（error 帧） | —（另 canceled=断连） |

错误码（附录 B）：E_NET / E_ROUTE_FALLBACK / E_ROUTE_INVALID / E_SQL / E_VALIDATION /
E_PARAM_MISSING / E_PARAM_RANGE / E_SCOPE（见 errors.py，USER_COPY 为唯一用户文案来源）。

## 存储

- app 库（SQLite，建表 SQL 在包内 migrations/001_init.sql）：conversations / messages /
  idempotency（client_request_id→request_id，重复请求重放快照、不产生第二条 trace）/
  history_hidden；删除一律 hidden 标记，物理行保留。
- trace：JSONL 追加（data/fortune/trace_log.jsonl），final 即完整快照。

## 安全

- LLM 原始输出进 trace/详情前经 sanitize_llm_text（密钥样式串/系统提示词样式行打码）；
- PII 钩子 apply_pii_policy：usr_phone_erpt 等字段仅加密态（enc(aes):: 前缀）可直通，
  其余一律 ***MASKED***（fail-closed）；
- SQL 模板以绑定参数执行（展示用 compile_sql 仅替换 :named 供 trace 可读）；
- 数据边界（超范围拒答文案）从库中推导（config.data_range），非硬编码。

## 与 demo 的差异（逻辑原样迁移 + 工程化）

1. RULES 收敛为 rules.py 配置（新增 viz 字段：REG_TOTAL=kpi / REG_BY_CHANNEL=bar / GENDER_RATIO=pie）；profile 的 viz_map/rule_hints 由规则表生成，单一事实源。
2. 步骤编号改为按查询连续 1..N（demo 固定 1/2/7 跳号，违反 §7 #3）。
3. blocked_param 拆 ask_param / reject_range 两态，结构化 block_reason（demo 靠文案猜）。
4. extract_params 由「只认 7月/8月」改为通用「(YYYY)M月」解析 → 降级路径也能触达超范围态。
5. SQL 执行错误捕获 → E_SQL error 终帧 + trace 落盘（demo 直接 500）。
6. 空结果态（empty 文案，禁崩句）；demo 会除零/空引用。
7. 新增：会话/消息持久化、幂等、历史隐藏、心跳、断连 canceled trace（best-effort）、
   错误码体系、LLM 输出脱敏、PII 钩子——demo 均无。
8. LLM 调用加 6s 超时（demo 无超时会挂死 SSE）；异常只留类型名不泄内部细节。

## 已知限制（如实）

- 幂等记录发生在 final 帧时：执行中途的并发重复请求（同 crid）可能各产一条 trace（单用户 P0 场景可忽略）。
- 断连取消为 best-effort：阻塞在 sqlite/LLM 调用中的 step 无法被 close 打断，该查询 trace 可能缺失 canceled 标记。
- 空结果/校验失败/服务异常三态有实现与映射，但核心测试未覆盖（数据/注入属 T7 用例集）。
- 心跳只在 step 间隙判超时发注释帧；单步内 >14s 阻塞由 executor + wait_for 兜底，纯 CPU 长步不会提前中断。
- 回放（幂等重放/会话消息）不含 token 帧，直接给 steps+final 快照。

## 测试

```bash
/opt/anaconda3/bin/python3 -m pytest tests/semantic/ -q   # 仅本目录，核心不变量
scripts/semantic_smoke.sh                                  # 六状态 curl 冒烟
```
