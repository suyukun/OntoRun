# DSH Bug 报告提交稿（可直接粘贴）

> 用途：在 GitHub Discussions（deepseek-ai/deepseek-harness）提交 bug。
> 生成：2026-08-17 ｜ v2：加入真实使用背景 ｜ 依据官方 `.github/ISSUE_TEMPLATE/bug.md` 模板。
> 操作说明见文末「提交指引」。

---

## 一、标题（建议）

**子代理仍使用已失效的旧模型通道：更换默认模型/删除 provider 后，旧会话子代理无法切换，只能新建会话**

> 备选短标题：**旧会话的子代理锁死在已删除的 provider 上，换模型也不生效**

## 二、正文（按官方模板，可直接粘贴）

<!-- 标题写中文行动或结果句；外露正文不超过 50 单位。 -->
子代理的模型通道被"锁死"在会话创建时的 provider 上：即使该 provider 的配额用尽、已被删除，或者用户改了默认模型、手动切换了会话模型，旧会话新派出的子代理仍然走旧通道，报错无法工作，只能新建会话绕过。

<details>
<summary>复现、预期与验收</summary>

- **真实场景**（我遇到的情况）：
  1. 会话/子代理原本使用 provider A（如某个按周配额计费的第三方通道）；
  2. provider A 的周配额用尽（报 `429 insufficient_quota`），于是把它从配置中删除，并把 `settings.yaml` 的 `agent-default-model` 改为 provider B；
  3. 回到原会话派子代理 → 仍走 provider A → 报 `NO_ADAPTER: no adapter registered for provider "A"`；
  4. 在 UI 里手动切换会话模型到 B → 再派子代理 → 仍然报错（切换不生效）。
- **复现步骤**：
  1. 会话模型选择 provider A，派一个子代理确认 A 生效；
  2. 删除 provider A 的 adapter（或使其失效），把 `agent-default-model` 改为 B；
  3. 原会话再派子代理。
- **实际结果**：子代理请求头仍为 provider A → `NO_ADAPTER` 报错；手动切换会话模型也无法纠正；只能 fork/新建会话解决。
- **预期结果**：① 删除/失效的 provider 不应继续被子代理使用——子代理应回退到 `agent-default-model` 当前值；或 ② 手动切换会话模型应传导到子代理继承路径；或 ③ 至少提供"重置会话模型为默认"的明确入口。
- **环境**：DSH 0.1.0-rc.6（Web profile），macOS。行为与具体 provider 无关，用任意 provider A/B 可复现。
- **验收条件**：旧会话在 provider 失效后，新派子代理不再走失效通道（回退默认模型）；或可通过非新建会话的操作恢复。

</details>

## 三、源码定位（给官方，讨论区可附）

`@deepseek-ai/dsh-subagent/lib/types/child-agent.js` L43-57：子代理创建时无条件继承 `parent.options.provider/model`：

```js
// Resolve the child's AgentOptions: the parent's provider/model/maxTokens
const parentProvider = parent.options.provider;
const parentModel = parent.options.model;
...parentProvider !== undefined ? { provider: parentProvider } : {},
...parentModel !== undefined ? { model: parentModel } : {},
```

该继承路径无视 `agent-default-model` 的变更（`dsh-agent-default-model` README 声明"默认值变更只影响之后从该默认值解析的 Agent"），且会话级切换不更新 `parent.options`，导致旧会话子代理永久锁死在失效 provider 上。

## 四、提交指引（在家操作）

1. 打开 `https://github.com/deepseek-ai/deepseek-harness/discussions`（登录 smashup@163.com 账号）。
2. New discussion → 选 bug/问题反馈 分类（若无则 General）。
3. 标题用「一」，正文用「二」整段粘贴（含 details 块）。
4. 「三」源码定位放评论区（可选，官方喜欢短）。
5. 提交后把链接发我。

## 五、v2 改动说明

- **加入真实场景**：配额用尽 → 删除 provider → 改默认模型 → 手动切换 → 全都不生效，只能新建会话。官方能立即理解"这个 bug 的真实痛感"。
- 复现步骤与 provider 解耦（A/B 泛指），强调"与具体 provider 无关，任意 A/B 可复现"——提高可信度。
- 预期结果给了 3 个修复方向（回退默认 / 切换传导 / 提供重置入口），让官方有选择，不越俎代庖。
