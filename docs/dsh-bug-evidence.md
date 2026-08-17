# DSH Bug 证据链：子代理模型继承 vs agent-default-model 变更失效

> 整理：2026-08-17 ｜ 用途：供独立 fork 窗口处理 DSH bug（复现/issue/PR）
> 状态：已 fork 验证绕过路径存在；待提 GitHub issue

## 一句话 bug 描述

**修改 `settings.yaml` 的 `agent-default-model` 后，已存在会话派出的 spawn 子代理仍然使用旧 provider/model，且会话内无任何途径纠正（手动切换会话模型也不生效），只能通过 fork/新会话绕过。**

## 复现步骤

1. settings.yaml 设 `agent-default-model: {provider: A, model: M1}`，启动 DSH web。
2. 在会话中把模型选择切到 `{provider: B, model: M2}`（或历史上设置过）。
3. 修改 settings.yaml 的 `agent-default-model` 为 `{provider: C, model: M3}`。
4. 在当前会话派一个子代理（`subagent`）→ 观察其请求头。

**预期**：子代理使用新的默认值（C/M3）。
**实际**：子代理请求头仍是会话创建时的 provider/model（A/M1 或 B/M2），即使该 provider 的 adapter 已被移除，报 `NO_ADAPTER: no adapter registered for provider "A"`。

## 实测证据

- 会话 jsonl 主请求：`provider=deepseek-official, model=deepseek-v4-flash`（264 次，正常）
- 同会话派出的子代理请求头：`provider=qwen-token-plan-cn, model=deepseek-v4-pro`
- settings.yaml 已改为 `deepseek-official / deepseek-v4-flash`，子代理仍请求 qwen → `NO_ADAPTER`
- 手动在 UI 切换会话模型后，子代理请求头仍为 qwen（切换不传导到子代理继承路径）
- fork 出新会话后，子代理立即恢复正常（探针 `探针OK fork通道正常`）

## 源码定位

**`@deepseek-ai/dsh-subagent/lib/types/child-agent.js` L43-57**：

```js
// Resolve the child's AgentOptions: the parent's provider/model/maxTokens
const parentProvider = parent.options.provider;
const parentModel = parent.options.model;
...parentProvider !== undefined ? { provider: parentProvider } : {},
...parentModel !== undefined ? { model: parentModel } : {},
```

子代理无条件继承父会话的 `options.provider/model`，**无视 `agent-default-model` 的变更**。

**相关模块**：
- `@deepseek-ai/dsh-agent-default-model`（README 明说"更改默认值只影响之后从该默认值解析选择的 Agent；现有会话仍沿用该选择"——即设计上会话级选择优先）
- `@deepseek-ai/dsh-subagent-spawn-in-process`（spawn provider，`inheritsParentContext=false` 但模型 options 仍继承）
- `@deepseek-ai/dsh-tool-subagent`（tool-subagent 装配无 agentOptions 覆盖，走继承）

## 设计意图 vs Bug 判断

- **设计上**：会话级模型选择优先于默认值（README 明确），这部分是设计。
- **Bug 部分**：① 手动切换会话模型**没有更新** `parent.options`（切换后子代理仍是旧 provider）——切换不持久化到继承路径；② provider adapter 被移除后，旧会话子代理无任何可纠正的 UI/设置入口，只能 fork——缺少"继承失效/重解析"机制。
- **修复方向建议**：子代理创建时，若父会话 options 对应的 provider 不可用（NO_ADAPTER），回退到 agent-default-model 当前值；或提供会话级"重置模型选择"入口。

## 影响

- 用户改默认模型后，旧会话的子代理全部失效且不可纠正（配置改了不生效）。
- 需 fork/新会话绕过，破坏工作流。

## 附件

- 失败日志示例（zstd 压缩，`~/.dsh/sessions/--Users-suyukun-Documents-OntoRun--/<failed-id>/session.jsonl.zstd`）：
  `{"type":"assistant/chunk","chunk":{"type":"finish","reason":{"kind":"error","failure":{"message":"no adapter registered for provider \"qwen-token-plan-cn\"","code":"NO_ADAPTER"}}}}`
