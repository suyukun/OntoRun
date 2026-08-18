# DSH Bug 提交交接包（给提交智能体）

> 用途：交接给"另一个智能体"代为在 GitHub 提交 bug 报告。本包自包含，提交智能体无需再查历史。
> 生成：2026-08-17 ｜ 目标仓库：deepseek-ai/deepseek-harness

---

## 一、你的任务（提交智能体必读）

1. 用 Jack 的 GitHub 账号（邮箱 smashup@163.com）登录 GitHub。
2. 在 `deepseek-ai/deepseek-harness` 仓库的 **Discussions** 里发一篇 **bug 报告**（不是 Issue——官方 CONTRIBUTING 明确"目前不接受外部 PR"，鼓励走 Discussions 报告问题）。
3. 按本包"第三节 提交内容"逐段粘贴（标题 + 正文 + 可选源码定位）。
4. 提交完成后，把讨论帖链接返回给 Jack 确认。

## 二、背景知识（供你理解，不提交）

- **项目**：DeepSeek Harness（DSH），DeepSeek 官方的 agent 框架（GitHub 14.3 万 stars，MIT，活跃开发中）。
- **官方贡献政策**：CONTRIBUTING.md 明确"目前无法接受外部 PR"，但**鼓励在 GitHub Discussions 报告 bug**（团队会看、纳入资源分配）。所以目标是发一篇**高质量 bug 报告**，建立信任，等官方开放 PR 或主动接触。
- **官方模板**：仓库 `.github/ISSUE_TEMPLATE/bug.md` 要求——标题用中文行动/结果句、正文一句话说清错误结果、细节放 `<details>` 折叠、正文尽量短（≤50 单位）。
- **Bug 本质**（一句话）：DSH 的子代理（subagent）创建时无条件继承父会话的模型 provider/model；当该 provider 被删除或失效、且用户已修改默认模型后，旧会话派出的子代理仍然锁死在失效 provider 上，报 `NO_ADAPTER` 错误，且无法在会话内纠正，只能新建会话绕过。

## 三、提交内容（逐段粘贴）

### 标题（二选一，推荐第一个）

```
子代理仍使用已失效的旧模型通道：更换默认模型/删除 provider 后，旧会话子代理无法切换，只能新建会话
```

备选：
```
旧会话的子代理锁死在已删除的 provider 上，换模型也不生效
```

### 正文（含 details 折叠，整体粘贴）

```markdown
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
```

### 评论区（可选，建议发，帮助官方定位）

```markdown
补充源码定位：

`@deepseek-ai/dsh-subagent/lib/types/child-agent.js` L43-57：子代理创建时无条件继承 `parent.options.provider/model`：

```js
// Resolve the child's AgentOptions: the parent's provider/model/maxTokens
const parentProvider = parent.options.provider;
const parentModel = parent.options.model;
...parentProvider !== undefined ? { provider: parentProvider } : {},
...parentModel !== undefined ? { model: parentModel } : {},
```

该继承路径无视 `agent-default-model` 的变更，且会话级切换不更新 `parent.options`，导致旧会话子代理永久锁死在失效 provider 上。
```

## 四、操作步骤（提交智能体执行）

1. 打开 `https://github.com/deepseek-ai/deepseek-harness/discussions`。
   - 若未登录，用账号（邮箱 smashup@163.com）登录 GitHub。
2. 点击页面上的 **New discussion**（新建讨论）。
3. 选择分类：优先 **bug / 问题反馈** 类；若列表无此类，选 **General**（通用）或最接近的"问题报告"类。
4. **标题**：粘贴第三节的标题（推荐第一个）。
5. **正文**：粘贴第三节的正文（markdown 整段，含 details 折叠）。
6. 点 **Start discussion** 发布。
7. 发布后：追加一条评论，粘贴第三节的"源码定位"（可选但建议）。
8. 把讨论帖 URL 返回给 Jack。

## 五、注意事项（提交智能体遵守）

- **只发一次**，不要重复提交同一 bug。
- 正文不要改动措辞（Jack 已确认），除非 GitHub 渲染异常（如代码块失效）才做最小修正。
- 不要提"我们"或任何个人背景（OntoRun、WorkBuddy 等一律不出现）；保持第三方视角的 bug 报告口吻。
- 若 Discussions 里已有相同 bug 的帖子：不要重复发，改为在该帖下补充回复（附源码定位），并说明情况。
- 若 GitHub 要求绑定邮箱验证：告知 Jack 处理，不要自行用其他账号。

## 六、预期结果（提交后）

- 官方小团队可能不立即回复（CONTRIBUTING 说团队小、无法回复每个帖子，但会关注）。
- 我们的目标是：报告被看到、被认可为高质量 bug；后续可 Upvote 提升曝光；等官方开放 PR 或主动联系。
- 提交后请把链接给 Jack，由 Jack 决定后续跟进动作。
