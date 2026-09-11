# SPEC 工具与机制选型对比 v0.1（2026-09-11）

> 命题：SPEC 机制有没有现成工具/技能可借？——补齐 v0.1 调研缺的「可安装工具/CLI」维度，为「借工具 vs 继续手搓」给决策依据。
> 调研人：Rose · 协议：tech-selection-research（web_search 2 次/8 query，预算 30 内；GitHub API/官方 README 一手抓取，全部当日核验）
> **结论先行：制度骨架不动，定向借三件——①自写 governance 测试（唯一稳的机器门禁）②抄 spec-kit 收口/checklist 提示词模板 ③沙盒试跑 spec-kit 半天校准我们模板。全面引入任一工具都不划算（驾驶舱不适配：其命令流需在交互式 agent 会话里逐步人手驱动，我们的执行单元是派活件）。**
> 状态：**已拍板（Jack，2026-09-11）：方案 A「抄机制不装产品」**。已执行：governance 门禁上线（tests/test_governance.py §5，上线即抓到 1 处状态头缺失并补登）、沙盒冒烟完成、converge 语义入模板收口节。

## 1. 候选工具事实表（截至 2026-09-11）

| 工具 | 维护状态（GitHub API 一手） | 安装/国内可达 | 定位 | 对我们的判断 |
|---|---|---|---|---|
| GitHub Spec Kit v1.0.6 | 135.3k★，MIT，2026-09-10 刚发版，极活跃 | `uv tool install specify-cli`（PyPI， tuna 源可装；也支持 uvx from git） | 六步 SDD：constitution→specify→plan→tasks→implement→**converge**；可选 clarify/analyze/checklist；支持 `--integration <agent> --integration-options="--skills"` 装成 agent skill | **机制最全，模板值得抄/校准**；但 slash 命令流默认驾驶舱是 IDE 交互会话（人逐步敲命令）；我们的执行单元是 Rose 派活件——要用其流程须把命令提示词翻译成派活语言，CLI 剩余价值≈脚手架文件 |
| OpenSpec（Fission-AI） | 67.9k★，MIT，当日有 push，活跃 | `npm i -g @fission-ai/openspec`（npmmirror 可达；Node ≥20.19） | brownfield 优先；changes/ 目录（proposal/specs/design/tasks）→apply→archive；`/opsx:*` 工作流 | **`openspec validate` 是确定性 CLI 结构校验**（spec delta、MODIFIED 对照主 specs、`--all --json`）——全候选中唯一真机器门禁，但其文件制度与 docs/plans/ 双轨 |
| AWS Kiro | 闭源 IDE | — | requirements/design/tasks 三件套 + EARS | EARS 已吸收进模板 A3，无可装物 |
| Tessl | 平台路线，tessl-cli 仓库不存在（API 404） | — | 企业 spec 平台（T4 报道） | 观察，不可借 |
| claude-task-master | 28k★，**2026-04-28 后无 push** | — | PRD→任务管理 | 出局（维护停滞） |

## 2. 机制对照：我们已有什么、真缺什么

| spec-kit/OpenSpec 机制 | 我们的对应物 | 判定 |
|---|---|---|
| constitution（项目原则，每轮必读） | AGENTS.md 三铁律+边界三档 | ✅ 已有，且含验收标准 |
| specify（需求/用户故事） | A 表（A1-A5） | ✅ 已有，更严（非目标+NC 预算） |
| clarify（开工前澄清） | NC 答题卡（批量推送/默认级一句话清零） | ✅ 已有，Jack 时间成本更低 |
| plan/tasks（带路径任务表） | B/C 表 | ✅ 已有（C1 硬性带路径+前置组） |
| **converge（对照 spec 收口，剩余工作回填任务表）** | 收口五步 | ⚠️ 有流程但**靠自觉**（缺口②） |
| analyze（交叉一致性检查）/checklist（"unit tests for English"） | 无直接对应 | ○ 可借提示词模板 |
| **机器门禁** | 派活前 grep NC-OPEN（靠自觉执行） | ❌ 全候选的检查多为 LLM 提示词级（软），**唯一例外是 openspec validate（CLI 结构校验，硬）**——铁律②要求机器验证，只有两条路：自写 governance 测试，或借 validate 思路 |

DSH 技能目录复用：tech-selection-research（本篇即其产出）、multi-agent-adversarial-review（本决策的对抗复核选项，见答题卡 Q4）；session-handoff/stage-check/idea-capture 与 SPEC 机制互补不重叠，无新增可借。

## 3. 反方证据（防工具崇拜）

1. **SDD ≠ 银弹**（alexcpn/speckit_test 实测，T5）：spec/plan/tasks 最终仍是模型 context——SDD 改善 context 质量但不产生架构判断与选型纪律；其实测中 Spec Kit v0.8.9+Opus 4.7 在选库环节失败。**推论：选型拍板（NC/人确认）不能外包给工具，我们的事前确认协议方向正确。**
2. **Thoughtworks 雷达：spec-kit = Assess 环**（T3，"worth exploring"，未到 Trial）：社区极热但企业收敛证据尚早。
3. **自家实证：制度首日返工率 0**（docs/制度首日复盘_2026-09-11.md）——已验证骨架别推翻；同篇 UX v0.1 试填作废教训：**方向不稳时更重的流程=更大浪费**。
4. **驾驶舱差异（Jack 质询后修正，2026-09-11）**：控制结构两边相同——都是人指挥 AI（Jack 全程掌舵，流程步骤由人控制）；差异在每一步的**消费方式**：spec-kit 的命令需在交互式 agent 会话里逐步人手触发，我们的每一步是批量派活件。要用它的流程就得把命令提示词翻译成派活语言；翻译完成后 CLI 的剩余价值＝脚手架与模板文件（可直接复制）。装 CLI ≠ 用上它的纪律，抄模板零成本的结论不变。此差异同时提升沙盒冒烟的价值：亲手验一遍「逐命令驾驶」是否真比派活制省力。

## 4. 缺口 × 解法（三个已知开放缺口逐一对应）

| 缺口 | 解法 | 成本 |
|---|---|---|
| ① 门禁靠 Rose 自觉 grep | **governance 测试**：pytest 校验门槛稿（NC-OPEN=0 / C1 任务表存在 / D1 基线输出已贴 / 收口状态头），派活前与收口各跑一次 | S 级，单文件 ~100 行，Rose 亲写 |
| ② converge 收口靠自觉 | 抄 spec-kit converge 语义进模板收口节：对照 A 表逐条打勾 + **剩余工作回填任务表**（而非口头"完成"） | 模板一处修订 |
| ③ spec-kit 只调研未试用 | **✅ 冒烟已试（2026-09-11 /tmp 实测）**：tuna 源 `uv tool install specify-cli` 秒装 v1.0.6；`specify init` 生成 .specify/（5 模板+6 bash 脚本）+ .claude/skills/ 10 个 SKILL.md——生成物与 DSH 技能体系同构，拷贝+汉化即可能用 | 实际 2 分钟 |

## 5. 选项与打分（权重默认值，**待 Jack 确认/调整**——质量门②）

权重：适配 DSH 派活模式 .25 / 机器可验证(铁律②) .20 / 缺口覆盖 .20 / 不推翻已验证部分 .15 / 迁移成本 .10 / 国内可达 .10

| 选项 | 内容 | 得分 |
|---|---|---|
| **A（推荐）制度不动+定向借三件** | §4 全部：governance 测试＋converge 模板修订＋沙盒试跑 spec-kit | **4.8** |
| B 全面引入 spec-kit 或 OpenSpec | 装 CLI、换文件制度 | 2.8（双轨/推翻已验证流程；冒烟后下修安装成本——PyPI 秒装、生成物即文件，但六步流替代已实证的 ABCD 制度这一核心代价不变） |
| C 最保守：只写 governance 测试 | 不借模板不试跑 | 4.4（缺口②③继续裸奔） |

## 6. 诚实标注

- OpenSpec validate 的「校验深度」（是否覆盖 requirement 语义，还是仅结构）未逐条实测，仅官方 CLI 文档（T1/T3）确认存在与用途。
- spec-kit checklist/analyze 的**效果**仍无真块实测（冒烟只验证了安装与生成物形态：全部是 markdown 提示词文件，无运行时服务）。
- alexcpn 实验基于 v0.8.9（现 v1.0.6），converge 为其后新增，其批评对 converge 步骤适用性未验证。
- Tessl 仅 T4 报道，未注册试用。

## 7. 来源清单（全部 2026-09-11 当日核验）

| 来源 | 级别 |
|---|---|
| api.github.com/repos/{github/spec-kit, Fission-AI/OpenSpec, eyaltoledano/claude-task-master}（stars/push/license/release v1.0.6） | T1 一手数据 |
| github/spec-kit README（jsdelivr 抓取：安装/命令表/skills 模板优先级/brownfield） | T3 官方 |
| Fission-AI/OpenSpec README + docs/cli.md（jsdelivr 抓取：opsx 工作流/validate --all --json/stores beta） | T3 官方 |
| cremich/promptz.lib kiro-specs.md（三件套结构，与 v0.1 调研一致） | T5 |
| thoughtworks.com/radar → GitHub Spec Kit = Assess 环 | T3 |
| alexcpn/speckit_test（SDD 非银弹实验复盘） | T5 线索（27k 字实验记录） |
| devops.com Tessl 报道 | T4 |
