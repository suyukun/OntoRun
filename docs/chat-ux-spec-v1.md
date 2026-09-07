# 前台对话窗交互与视觉设计规格 v1

> - **版本**：v1（S4 金控风险预警 · 高保真样式稿驱动）
> - **日期**：2026-09-03
> - **作者**：产品（PM）｜派单：Rose｜方向拍板：Jack
> - **状态**：待 Jack 过目后交前端实现
> - **适用范围**：S4 演示前台（纯前台 + 假数据，不接后台），AI 对话窗口 = 唯一一级入口
> - **精度声明**：本文档目标 = 前端拿到后**不再做任何设计决策**。所有尺寸/颜色/文案均为终值；标注〔假设〕的条目对应 §12 待澄清清单。
> - **技术底座**：React 19 + antd 6 + @ant-design/x 2.9 + ECharts 6；颜色/字体/圆角/阴影全部复用 web/src/risk/riskTheme.ts

---

## 0. 设计基调与判据

**一句话基调：像监管报表一样克制，像资深风险经理一样有条理。**

### 0.1 Trust-first 三原则（每个设计决策的检验问句）
问金控问数场景，每个决策必须能回答「这跟信任感有什么关系」：

1. **数字可信优先**：回答里出现的每个数字，必须能在两步内找到它的证据链入口（basis 表 / 规则 / 分母 / 审计号）。
2. **过程透明**：AI 的查表、勾稽、定级过程可展开查看（tools 块）——默认收起保克制，展开即透明。
3. **人有最终决定权**：任何写回类动作必须经 confirm 双签卡，人拍板后留痕、不可逆展示。

### 0.2 设计拨盘（Jack 拍板：变化性 3 / 动效 2 / 密度 4）
- **变化性 3（强重复结构）**：全站只有一套消息结构（消息头 + 块流），六类块共享同一容器语言（1px borderSoft + 8px 圆角 + 12px 内距）；同屏不出现第三种卡片形态。变化只允许来自数据本身（图表配色随预警等级变）。
- **动效 2（仅状态转换）**：只保留五处动效——流式打字机、侧栏折叠宽度、抽屉滑入、块级 fade-in 120ms、按钮 loading。禁止循环装饰动画（唯一例外：会话列表「生成中」三点跳动，因它承载真实状态）、禁止视差/stagger 编排。
- **密度 4（紧凑）**：表格行高 36、正文行高 26、块间距 12、卡内距 12。留白只服务于「阅读分节」，不做装饰性大留白。
- 独立方法论校验：design-taste-frontend（taste skill）拨盘推断表对 trust-first / regulated 场景给出 VARIANCE 3-4 / MOTION 2-3 / DENSITY 4-5，与拍板值一致，本文按 3/2/4 执行。

### 0.3 AI 味审美黑名单（违反即打回）
紫色/渐变主色；glassmorphism（backdrop-filter 毛玻璃）；三等分卡片阵列；emoji 作界面图标；彩色阴影；大于 12px 的大圆角容器多层堆叠；深色玻璃 + 霓虹；无意义插画。图标只用 @ant-design/icons 线性一族，统一描边。

### 0.4 与现有资产的关系
- **riskTheme.ts 直接复用**：色板/字体栈/圆角 6-8/阴影两档/字重 600 全部沿用，本文 §9 只做引用与补充，不另立色板。
- **AntdXPage.tsx 原型已验证的保留**：三区骨架、Bubble + ThoughtChain + Table/Card 组合、逐字流式、confirm 状态机。以下为**有意差异**：
  1. 原型临时色废弃：用户头像 #1677ff、AI 头像 #fa8c16、confirm 描边 #fa8c16、图表绿 #52c41a → 统一到 RISK_COLORS（#2a50ce / #c2410c / #067647）。原型色是 React 默认蓝与 AntD 默认橙，与金控冷灰一族冲突。
  2. 内容卡 maxWidth 620 → 提升为内容列全宽 728（AI 消息缩进后），理由：监管表格 5 列在紧凑密度下需要完整宽度，密度拨盘 4 优先可读性。
  3. ThoughtChain 缩进 44 → 32（消息头从 40px 头像规格改为 24px，见 §4.3）。

### 0.5 范围与非目标（S4 样式稿）
**做**：空态、消息流、六类块、证据链抽屉、输入区、四态（流式/思考/错误/会话切换）。
**不做**：登录与权限差异、会话搜索/重命名/删除、移动端专属布局（仅 <1024 兜底）、暗色主题〔假设〕、i18n、真实后端、服务端导出 PDF。

---

## 1. 研究输入：一线对话产品桌面端模式提炼

检索于 2026-09-03；5 条模式均标注来源与本产品落点。

**P1 对话与产物同屏（豆包 PC 端侧边工作台）**
豆包 PC 客户端 2026-08 升级为「对话 + 产物同屏」：左侧对话、右侧工作台展示任务产物，成果不挤占对话流。
→ **落点**：证据链抽屉即「产物同屏」的监管化变体；抽屉用 overlay 悬浮而非挤压中栏，保证阅读列宽度恒定（§2.6）。
来源：https://www.chinaz.com/2026/0821/1772290.shtml ；https://ai.zol.com.cn/1235/12353606.html

**P2 居中限宽阅读列（ChatGPT / Claude / Gemini 桌面端）**
三家桌面/网页端均将消息流限制在约 768px 居中窄列，超宽屏两侧留白；社区长期诉求「大屏利用」并出现加宽聊天的 CSS 定制工具，反证窄列是刻意默认。
→ **落点**：阅读列 760px 居中；用户气泡限宽 560px；富内容走右侧抽屉而不是加宽中栏。
来源：https://community.openai.com/t/feature-request-better-use-of-large-screen-space-in-chatgpt-chats/1388551 ；https://www.justzix.com/zh/blog/customize-chatgpt-claude-gemini-ui-css-justzix

**P3 空态建议问题 / Prompt Starters**
主流产品空态 = 问候语 + 可点击建议问题 chips，把「空白输入框」换成「一键可跑的最佳实践」，是 AI 产品冷启动标配模式。
→ **落点**：§3 空态 6 问 chips，全部从金控剧本（fakeData.ts）出题，且分别对应六类块的演示路径。
来源：https://www.aiuxplayground.com/pattern/prompt-starters ；https://www.aiuxplayground.com/guides/ai-onboarding/

**P4 流式渲染 + 引用溯源是生产级 AI 产品标配**
生产级 LLM UX 模式集将 streaming、RAG citations（引用溯源）、empty states 列为标准模式；企业级 RAG 实践强调「回答必须能回指证据片段与来源」以建立可信度。
→ **落点**：流式打字机（§8.1）；每条 AI 回答常显「查看证据链」入口（§4.4）；证据链抽屉承载 basis / 规则 / 分母 / 审计四要素（§6）。
来源：https://github.com/arablex/llm-ux-patterns ；https://developer.aliyun.com/article/1750498

**P5 组件底座用官方而非手搓**
Ant Design X 官方提供 Bubble / Sender / Conversations / ThoughtChain / Welcome / Prompts 等对话全件，覆盖气泡、发送器、会话列表、思维链、空态欢迎与建议提示。
→ **落点**：§10 组件映射；样式经 antd ThemeConfig（riskLightTheme）+ 局部 token 覆写实现，不重造组件。
来源：https://x.ant.design/components/introduce

---

## 2. 布局规格

### 2.1 骨架
- 外壳：height 100vh，flex column，body overflow hidden（禁止整页滚动）。
- 顶栏：高 48px，白底，下缘 1px borderSoft。
- 顶栏下方：左栏 + 中栏（flex row，minWidth 0）。
- 右抽屉：绝对定位 overlay，不参与 flex 分配。

### 2.2 顶栏内容（从左到右）
| 位置 | 元素 | 规格 |
|---|---|---|
| 左 | 侧栏折叠钮 | icon-only Button（type=text）28x28，图标 PanelLeft 线性（折叠态镜像），色 textDim，hover 底 panelAlt |
| 左 | 产品标识 | 24x24 logo（accent 底、radius 6、白色盾形图标）+「OntoRun 风险智能体」14px semibold text，间距 8 |
| 中偏左 | 当前会话标题 | 14px textDim，max-width 320px 超长省略，hover title 显全名 |
| 中偏左 | 口径徽标 | 「安平金控 · 监管口径 v0.3」Tag：12px，无框，底 panelAlt，字 textFaint（只读标识，非按钮） |
| 右 | 证据链开关 | Button：FileSearchOutlined 16 + 文字「证据链」13px；开启态 = 文字 accent、底 #e7f0ff；默认态白底 |
| 右 | 用户身份 | 24px 圆头像（姓氏「张」12px 白字、底 textDim）+ title「风险合规部 · 张处长（演示）」，只读〔假设 1〕 |

### 2.3 左栏（会话列表）
- 宽：展开 240px / 折叠 56px；白底，右缘 1px borderSoft；内边距 8。
- **新建对话钮**：宽 100%（224px）、高 36、accent 底白字 13px、radius 6、左侧 PlusOutlined 16；折叠态收缩为 40x40 icon 钮居中。
- 分组标签「今天」：12px textFaint，padding 8 12。
- **会话项**：高 36、radius 6、padding 0 12、文字 13px；纯文字无图标（密度 4，扫读优先）。默认 text 色；hover 底 panelAlt；**当前项** = 底 panelAlt + 文字 text + 左缘 2px accent 竖条（高 16 垂直居中）。
- 项右缘 hover 出现 MoreOutlined（20x20，textFaint）——S4 不挂菜单，仅样式占位（灰置）。
- 预置会话（fakeData SESSIONS）：天晟集团风险归集 / 瑞华能源黄档解除 / 000098 勾稽质询。
- **生成中指示**：会话正在流式且非当前项 → 项右缘三点跳动（accent，600ms 循环；全站唯一循环动画）。

### 2.4 折叠行为
- 触发：顶栏折叠钮；快捷键 Cmd/Ctrl + B。
- 动画：width 240→56，180ms cubic-bezier(0.2, 0, 0, 1)；内容透明度在前 60ms 先行淡出，防文字挤压闪烁。
- 折叠态内容：新建 icon 钮 + 最多 5 个会话首字圆标（28x28，panelAlt 底 textFaint 12px，当前项 accent 底白字），纵向间距 8；hover 圆标 title 显会话全名。
- 状态持久：localStorage key = chat.sidebar.collapsed。

### 2.5 中栏（消息流 + 输入）
- 滚动区：flex 1，overflow-y auto，padding 24 24 8 24。
- **消息列：max-width 760px，margin 0 auto**（视口不足 808px 时左右 24px 兜底）。
- 输入区：中栏底部独立容器（非 sticky），白底；中栏页面底为 ink #f5f6f8，白底容器自然分层，**不加分隔线**；内容列 760 居中，容器距视口底 16px。

### 2.6 右抽屉（证据链）
- 宽 min(400px, 38vw)；top 48、right 0、bottom 0；白底，左缘 1px borderSoft + 阴影 -6px 0 16px rgba(16, 24, 40, 0.08)。
- **不加遮罩**：允许边看对话边查证据（监管场景双栏核对是真实动作）。
- 动画：translateX(100%→0) 200ms cubic-bezier(0.2, 0, 0, 1)；关闭反向。
- 打开不改变中栏消息列位置。

### 2.7 断点
| 视口 | 行为 |
|---|---|
| ≥1440px | 完整三区；抽屉 400px |
| 1024–1439px | 左栏默认折叠（用户可展开）；抽屉 360px |
| <1024px | 左栏改 overlay（同抽屉交互，加遮罩 rgba(16,24,40,0.32)）；抽屉 min(400px, 92vw)。演示非目标，仅保证不烂 |

---

## 3. 空态设计（新会话首屏）

### 3.1 结构与文案（终稿）
消息列 760 内垂直布局，起始于 38% 视高处：
1. Logo 48x48（accent 底，radius 10，白色盾形图标）。
2. 主标题：**今天要看什么风险？**（20px/30，semibold，text，上距 20）
3. 副标题：我可以按监管口径查预警、拆计算过程、起草处置提议——每个数字都带证据链。（14px/22，textDim，上距 8，max-width 520 居中）
4. 建议 chips（上距 32）：见 3.2。
5. 底部声明（空态内距视口底 24，居中）：**演示环境 · 数据为模拟金控剧本 · 安平集团口径 v0.3**——12px textFaint。监管演示必须显式声明模拟数据，此行在空态常驻。

### 3.2 建议 chips（6 问，全部从 fakeData 剧本出题）
| # | 文案（终稿） | 图标 | 命中演示 |
|---|---|---|---|
| 1 | 天晟集团现在有什么风险预警？ | AlertOutlined | text 结论 + table 明细 |
| 2 | 为什么各家机构都安全，归集反而触发橙色预警？ | QuestionCircleOutlined | REVEAL_TEXT 拆释（单家 vs 归集） |
| 3 | R1a 归集集中度怎么算的？分母是什么？ | CalculatorOutlined | text 公式（86.4 亿 ÷ 800 亿 = 10.8%）+ 依据入口 |
| 4 | 画一张各机构占比与预警线的对比图 | BarChartOutlined | chart（ECHOPT） |
| 5 | 生成天晟集团风险处置建议报告 | FileTextOutlined | report 报告卡 |
| 6 | 提议冻结天晟集团新增授信，走审批 | AuditOutlined | confirm 双签卡 |

### 3.3 chip 规格
- 布局：grid 2 列，gap 12（<1024 单列）；每格宽约 356px。
- 容器：白底，1px borderSoft，radius 8，padding 12 14；图标 16px textFaint 在左，间距 8。
- 文字：13px/20 text，左对齐，单行超长省略（最长 chip #4「画一张各机构占比与预警线的对比图」约 234px < 356 可完整显示）。
- hover：border → accent，底 panelAlt；无位移、无阴影。
- active：底 #e7f0ff。focus-visible：外圈 0 0 0 3px rgba(42, 80, 206, 0.12)。
- **点击行为 = 直接发送**（不填充输入框）：演示 5 分钟内见效优先〔假设 3〕。

---

## 4. 消息流规格

### 4.1 垂直节奏
| 间隔 | 值 |
|---|---|
| 同一 AI 回答内块与块 | 12px |
| 消息头 → 首块 | 8px |
| 用户消息 → AI 回答 | 20px |
| AI 回答结束 → 下一条用户消息 | 28px |
| 滚动区首条消息上距 | 8px |

### 4.2 用户消息（气泡）
- 右对齐；**无头像**（用户身份在顶栏唯一表达，省横向空间）。
- 底色 **#e7f0ff**（WARN_TAG_TINTS.BLUE.bg，与 accent 同族的唯一浅底）；文字 15px/24 text（浅底深字，不用白字——长文本可读性优先）；无边框。
- max-width 560px（阅读列的 74%）；radius 12，右上角 4（方向暗示）；padding 10 14。
- 时间不常显，hover title 显 HH:mm（用户消息不承载审计职能）。

### 4.3 AI 回答（无气泡块流）
- 结构 = 消息头 + 内容块流；整体左对齐，内容缩进 **32px**（头像 24 + 间距 8）；内容宽 = 760 − 32 = **728px**。
- **消息头**：24x24 logo（accent 底 radius 6 白盾）+「风险智能体」13px textDim + 时间 HH:mm 12px textFaint（**常显**——监管问答必须有时点）；三者 baseline 对齐，间距 8。
- **决策：AI 回答不用气泡框**。理由：AI 回答的主载体是表格/图表/报告，气泡内距 + 圆角会吃掉约 56px 宽度并弱化数据块可扫读性；ChatGPT/Kimi/豆包桌面端 AI 回答均为无框流。

### 4.4 消息操作条（AI 回答尾部）
- **常显行**（距末块 10px）：「查看证据链 · 审计 #A-1024」13px accent，hover 下划线；点击打开右抽屉并锚定本条回答。信任入口不允许 hover 才出现（P4）。
- hover 追加 icon 钮（20x20，textFaint→hover text）：复制（CopyOutlined，复制整条 Markdown）、重新生成（RedoOutlined，重发原问题）。

### 4.5 多块连排节奏（问数标准应答结构）
默认顺序：**tools（折叠行）→ text（结论先行，首句直接给结论、关键数字加粗）→ table（明细）→ chart（对比/趋势）→ confirm（仅处置类）→ 操作条**。
出块规则：非处置类不出 confirm；简单口径问只出 tools + text；**同屏至多 1 表 1 图**，禁止同类卡重复堆叠。

---

## 5. 六类内容块规格

通用容器语言：块级卡 = 白底 + 1px borderSoft + radius 8 + 内距 12；块标题行 = 左侧 13px semibold text + 右侧操作 icon（20x20，textFaint，hover text）。以下只写各块差异。

### 5.1 text（Markdown 富文本）
- 正文 15px/26 text；段距 10；strong = 600 + tabular-nums（**回答中所有数字必须加粗**，如 10.8%）。
- 行内 code = 等宽字体（§9.2）13px，底 panelAlt，radius 4，padding 1 5；表名/参数名/审计号一律 code 样式（如 ap_group_customer、CAP_WARN_LINE）。
- 链接 accent，无下划线，hover 下划线；列表 15/26 缩进 22，项距 4。
- 标题降级：AI 输出的 h1/h2/h3 一律渲染为 15px semibold（对话流内不允许大标题断层）。
- 禁：blockquote、hr、图片。
- 渲染验收样例（REVEAL_TEXT）：「逐家单看都安全：银行 8.0%（行内限额内）……归集 86.4 亿 ÷ 并表资本 800 亿 = **10.8% ≥ 预警线 10%** → 橙色预警（R1a）」——数字全部加粗、公式行保留整段。

### 5.2 table
- 块标题：「归集集中度明细」+ 右操作：复制 CSV、放大（Modal 内同表，宽 720）。
- antd Table size=small：行高 36（py 6）；表头 12.5px semibold textDim、底 panelAlt；行分隔 1px borderSoft；外框 1px borderSoft radius 8 overflow hidden。
- 数字列右对齐 + tabular-nums；「状态」列 = ZH_WARN_META 淡彩标签：安全 = green 文字无底；触达 = 黄 tint（bg #fdf3e3 / border #ecc89a / 字 #b54708）；橙色预警 = 橙 tint（bg #fdeae1 / border #f2bda1 / 字 #c2410c）。
- **命中预警行**（归集 R1a）整行强调：底 #fdf1ea + 左缘 2px #c2410c（一眼看到超标行）。
- 行数 > 8：max-height 396px 内滚 + 底部条「共 N 行 · 展开全部」13px accent。
- 列宽指引（TABLE_ROWS 5 列 / 728 宽）：机构 180 / 敞口 120 右对齐 / 占比 110 右对齐 / 参考线 160 / 状态 120，余量给机构名。
- 空数据：占位行「本口径下无记录」13px textFaint，高 64 居中。

### 5.3 chart（ECharts 6）
- 块标题：「各机构占比 vs 预警线」+ 副标题 12px textFaint「口径：归集集中度 = 归集敞口 ÷ 并表资本」+ 右操作：放大、下载 PNG、查看依据。
- 尺寸：内嵌高 **260px**、宽 100%（728）；放大 Modal 720x480（同 option 重渲染）。
- 数据色语义映射（替代原型 #52c41a/#fa8c16）：达标 #067647 / 触达 #b54708 / 预警 #c2410c / 危急 #b42318。以 TABLE_ROWS：安平银行绿、安平证券黄、安平资管黄、归集橙——颜色即风险等级，不需要图例解释。
- 阈值 markLine：1.5px 虚线 #c2410c + 右端标签「预警线 10%」（11px #c2410c，底 #fdeae1，padding 2 6，radius 4）。
- 坐标轴：轴线/标签 11px textFaint；y 轴 formatter {value}%；分割线 borderSoft 1px 实线（禁虚线网格——密度 4 下虚线显噪）。
- tooltip：白底 1px borderSoft radius 6 + 阴影 xs；无动画。
- 动画：入场 300ms easeOutCubic 仅一次；禁循环动画。
- 图例默认关（类目即 x 轴）；多序列时开，底部居中 12px。柱宽 28。

### 5.4 report（报告卡）
- 形态：**索引卡而非全文**。容器 728 全宽 + 左缘 3px accent 竖条 + 1px borderSoft。
- 行 1：FileTextOutlined 16 accent + 标题 14px semibold「天晟集团风险处置建议报告」+ Tag「草稿」（黄 tint）。
- 行 2：摘要 13px/22 textDim，两行截断。示例：「归集集中度 10.8% 触发 R1a 橙色预警，建议冻结新增授信并核查关联交易……」
- 行 3：meta 12px textFaint「生成 14:32 · 依据 3 表 2 规则 · 审计 #A-1024」+ 右侧按钮组：预览（Button size=small 默认态）、下载 MD（text 钮）〔假设 4〕。
- 预览 Modal：宽 720、高 80vh 内滚；页眉「安平金控 · 风险处置建议（模拟）」12px textFaint；正文按 §5.1 排版，报告内允许 h3 = 16px semibold 分节；页脚审计号 code 样式。
- 生成中：行 1-3 骨架（Skeleton 3 行）+ 标题行 spinner。

### 5.5 tools（过程透明）
- **完成态默认折叠为一行**（距消息头 8）：CheckCircleOutlined 14 textFaint + 13px textDim「已核查 3 张表 · 执行 2 条规则 · 勾稽通过 · 1.8s」+ 右缘 ChevronDown 16 textFaint；整行可点，hover 底 panelAlt radius 6。
- **展开态** = 垂直步骤列表（ThoughtChain 或等价自绘）：节点状态点（finish = 6px 圆 #067647；process = LoadingOutlined 14 accent）+ 步骤名（API 名等宽 12.5px 底 panelAlt radius 4 padding 1 6，如 risk_group_reveal）+ 中文动作 13px semibold text；描述行 12.5px/20 textDim，技术标识内联 code 样式（GRP-2026-900001 · ap_group_customer × ap_concentration_limit）；耗时右对齐 12px textFaint。节点间距 12，连接线 1px borderSoft。
- 剧本三步（fakeData TOOL_STEPS）：risk_group_reveal 查分组归集明细 / 勾稽对账（86.4 + 0.0 = 86.4 ✓）/ R1a 定级（阈值 CAP_WARN_LINE=10% · 金控办法 32/33 自设 · 安平风管部 2025-06-30 批）。
- **进行中**：骨架先行（两行 Skeleton 高 14、宽 60%/40%）+ 当前步 spinner；每步完成 fade-in 120ms。
- 展开记忆：单次回答内用户展开后保持；新回答默认折叠。

### 5.6 confirm（双签卡）
- 容器（待确认态）：1px #f2bda1 + 左缘 3px #c2410c + 底 #fff + radius 8。
- 标题行：AuditOutlined 16 #c2410c +「AI 提议 · 需人工拍板」13px semibold #c2410c + 右侧状态 Tag（待确认 = 橙 tint；已执行 = green；已驳回 = textDim）。
- 正文：提议 14px/24 text「冻结天晟集团新增授信」；依据行 12.5px textDim「R1a 归集 10.8% ≥ 预警线 10%（处置依据：2023 关联交易办法第二十三条）」+ 尾随「查看依据」accent 链接。
- 操作区（上距 12）：批准执行（Button primary，accent，loading 600ms 模拟写回）+ 驳回（Button default）。提交即双钮 disabled 防重复。〔v1.1 勘误 2026-09-02：移除原「审批意见 Input」——Jack 裁决双签短期非重点，confirm 收敛为纯拍板动作，不含自由文本输入；原 §5.6 与 §11 验收语义自相矛盾，以本勘误为准。〕
- **执行后（终态不可逆）**：容器边框退为 borderSoft、标题行变灰「AI 提议 · 已处置」（textDim）；按钮区隐藏，下插状态条（上方 1px borderSoft 分隔）：CheckCircleOutlined 14 +「已执行 · 源库写回 ✓ · 审计 #A-1024 · 操作人 张处长 · 14:32」13px #067647。卡保留在消息流中（追溯可查）。
- 驳回后：状态条「已驳回 · 退回 AI 重新起草」textDim + 时间；同样保留。
- 〔假设 2〕单签即达「人拍板」演示意图；若剧本要求上级复核，需追加第二状态段，待口径包确认。

---

## 6. 证据链抽屉

### 6.1 入口（三处，行为一致）
1. AI 消息操作条「查看证据链」（§4.4）——锚定该条回答。
2. table / chart 块右上「查看依据」icon——锚定该块所在回答。
3. 顶栏「证据链」开关——锚定当前会话最近一条带依据的 AI 回答；无则禁用态 + title「当前会话暂无带依据的回答」〔假设 8〕。

### 6.2 结构
- 头部（高 48，下缘 1px borderSoft）：「证据链」14px semibold + 审计号 Tag（等宽 12px，底 panelAlt：#A-1024）+ 右上 Close 20x20。
- 正文滚动，四区，区距 24；区标题 = 13px semibold text + 左侧 3x12 accent 短条：
  1. **数据来源（basis 表）**：每表一行：表名等宽 13px code 样式 + 行数 + 快照时间 12px textFaint（示例：ap_group_customer · 1,284 行 · 快照 08:00〔假设 5，数值待数据侧〕）+ hover 复制钮。
  2. **规则**：R1a 归集集中度 / R1b 机构参考线——规则名 13px semibold + 表达式 code 块（等宽 12px，底 panelAlt，padding 8，radius 6）+ 阈值来源行 12px textFaint（阈值 CAP_WARN_LINE=10% · 金控办法 32/33 自设 · 安平风管部 2025-06-30 批）。
  3. **口径**：键值行（key 12px textFaint 定宽 88 + value 13px text）：分母 = 集团并表资本 800 亿（CAP_GROUP_CONSOLIDATED）；统计周期 = T-1 日终〔假设〕。
  4. **审计轨迹**：时间线（左缘 1px borderSoft 竖线 + 6px 圆点 accent）：时间 12px textFaint 等宽 + 动作 13px text——14:31:02 查询归集明细 / 14:31:03 勾稽对账通过 / 14:31:04 R1a 定级 orange。
- 底部固定条（高 40，上缘 1px borderSoft）：「本回答全部数字可回溯至以上来源」12px textFaint +「导出审计包」text 钮灰置（title「演示版未开放」）。

### 6.3 交互
- 锚定不同回答时抽屉内容即时替换（无动画）。
- ESC 关闭；再次点顶栏开关关闭。
- 抽屉打开不影响中栏滚动。

---

## 7. 输入区

### 7.1 形态
- 位置：中栏底部，内容列 760 居中，容器距视口底 16px。
- 容器：白底，1px border，radius 12，padding 12 14；默认阴影 xs（§9.5）。
- focus：border → accent + 外圈 0 0 0 3px rgba(42, 80, 206, 0.08)。
- 输入框：textarea 自适应 1–5 行，行高 24，字号 15px text；超 5 行（120px）内滚。
- **占位文案（终稿）**：向风险智能体提问，如：为什么归集 10.8% 触发橙色预警？——占位即能力示例（textFaint）。

### 7.2 行为
- **Enter 发送；Shift+Enter 换行；IME 组合输入中（isComposing）Enter 不发送**（中文输入法关键细节）。
- 发送钮：32x32 radius 8 accent 底白 SendOutlined 16；空输入 disabled（底 panelAlt、icon textFaint）。
- 生成中：发送钮变停止钮（白底 1px border、StopOutlined 14 text 色，hover border→textDim），点击打断流式；此间 Enter 不发送。
- 字数：输入 >400 时右下角显示 n/500（12px textFaint，按钮左侧 8）；500 截断〔假设 11：演示值〕。
- 发送后：立即清空、保持 focus。
- 附件/截图/模型选择器：不做（最小实现，x Sender 相关 slot 留空）。
- 输入区下方不放提示行；快捷键说明入容器 title。

---

## 8. 状态设计

### 8.1 流式打字机
- text 块逐 token 追加；尾部光标 = 2x16 accent 竖条，blink 800ms steps(1)；完成即消失。
- Markdown 安全渲染：未闭合表格先按纯文本行渲染，闭合后整块升级为 table 卡；升级瞬间位置不变（前置文本已输出）。
- 用户消息与消息头出现：80ms fade；块级 fade-in 120ms（全站唯一块级入场动效）。

### 8.2 思考中（tools 过程）
- ≤800ms：直接出内容，无中间态。
- >800ms：出现消息头 + tools 骨架（两行 Skeleton，高 14，宽 60%/40%）。
- >8s：骨架下追加 12px textFaint「正在核对口径与阈值…」（业务语言；禁「Thinking」裸词）。
- 流式期间该回答锁定不可编辑。

### 8.3 错误态
- 消息位插入错误卡：底 #fceceb（WARN_TAG_TINTS.RED.bg）+ 1px #efb3ae + radius 8 + padding 12 14；CloseCircleOutlined 16 #b42318 +「本次回答生成失败」13px semibold #b42318 + 原因一行 12.5px textDim（网络超时 / 服务暂不可用；**不暴露堆栈与敏感信息**）+ 右侧「重试」Button size=small（重发原问题，成功后错误卡移除）。
- 不用全局 toast（监管场景错误也要留痕在流内）。

### 8.4 会话切换
- 本地假数据切换 <100ms：直接渲染 + 消息列 120ms fade。
- 每会话滚动位置独立记忆。
- 生成中切走：后台继续流式；左栏该项三点跳动；切回续显。
- 切到空会话 → 空态（§3）。

### 8.5 滚动
- 跟随：新内容处于视口底部 120px 内时自动吸底。
- 用户上滚 >80px 解除跟随；输入区上方 12px 处浮出「回到底部」钮：36x36 圆形、白底、1px borderSoft、阴影 xs、ArrowDown 16 + 未读数圆标（12px，accent 字，#e7f0ff 底）；点击回底并恢复跟随。

---

## 9. 视觉 token 总表

### 9.1 颜色（全部引用 risk/riskTheme.ts，前端不新增色值）
| token | 值 | 用途 |
|---|---|---|
| RISK_COLORS.accent | #2a50ce | 品牌强调：logo、链接、当前会话左条、发送钮、时间线节点 |
| RISK_COLORS.ink | #f5f6f8 | 中栏/页面底 |
| RISK_COLORS.surface | #ffffff | 顶栏、左栏、卡片、抽屉、输入容器 |
| RISK_COLORS.panelAlt | #f0f3f9 | hover 底、表头底、code 底、折叠态会话圆标 |
| RISK_COLORS.border | #e5e8ee | 输入容器默认边框 |
| RISK_COLORS.borderSoft | #eef1f6 | 卡边框、分隔线、表格线 |
| RISK_COLORS.text | #101828 | 主文字 |
| RISK_COLORS.textDim | #475467 | 次级文字 |
| RISK_COLORS.textFaint | #636d80 | meta/时间/占位/禁用 |
| WARN_TAG_TINTS.BLUE.bg | #e7f0ff | 用户气泡底、chip active 底、证据链开启态底、未读圆标底 |
| RISK_COLORS.green / yellow / orange / red | #067647 / #b54708 / #c2410c / #b42318 | 语义：达标 / 触达 / 预警 / 危急（图表、标签、confirm） |
| WARN_TAG_TINTS 黄/橙/红 | bg #fdf3e3 / #fdeae1 / #fceceb；border #ecc89a / #f2bda1 / #efb3ae | 预警等级淡彩标签、错误卡 |

### 9.2 字体
- 界面栈：沿用 riskLightTheme token.fontFamily（-apple-system, PingFang SC, Microsoft YaHei…）。
- 等宽栈（chat 新增）：'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace——表名/参数名/表达式/审计号/时间戳。
- 数字一律 fontVariantNumeric: tabular-nums（riskTheme R.num）。

### 9.3 字阶（px/行高，字重仅 400 与 600）
| 字号/行高 | 用途 |
|---|---|
| 11/16 | 图表轴标签、极小注 |
| 12/20 | meta、时间戳、声明行、Tag |
| 13/20 | 次级正文、块标题、会话项、chips、按钮 |
| 14/22 | report 标题、顶栏标题、confirm 提议 |
| 15/26 | 正文（text 块） |
| 15/24 | 气泡文字、输入框 |
| 20/30 | 空态主标题 |

### 9.4 间距与圆角
- 间距基数 4：气泡 padding 10 14｜卡内距 12｜块间距 12｜角色切换 28｜消息头→首块 8｜输入容器距底 16｜滚动区左右 24。
- 圆角：气泡 12（右上 4）｜输入容器 12｜卡/chips 8｜按钮/输入钮 6｜logo/头像 6（沿用 antd token borderRadius 6 / borderRadiusLG 8）。

### 9.5 阴影 / 动效 / z-index
- 阴影仅三档：xs = 0 1px 2px rgba(16,24,40,0.06)（输入容器、浮钮）；sm = 0 2px 6px rgba(16,24,40,0.08)（tooltip、放大 Modal）；drawer = -6px 0 16px rgba(16,24,40,0.08)。禁彩色阴影与更大扩散。
- 动效：micro 160ms（hover、fade）｜panel 180–200ms（侧栏宽、抽屉位移）｜图表入场 300ms 一次；曲线统一 cubic-bezier(0.2, 0, 0, 1)；仅动 opacity / transform / width；prefers-reduced-motion 下全部 0ms。
- z-index：内容内浮层 10 < 顶栏、回到底部 20 < 证据抽屉 30 < 左栏 overlay 态 40 < Modal 100。

### 9.6 chat 专属新增 token（仅 4 项，放 web/src/chat/chatTokens.ts，必须由 RISK_COLORS / WARN_TAG_TINTS 派生或注释来源）
1. chatFontMono：§9.2 等宽栈
2. chatUserBubbleBg = WARN_TAG_TINTS.BLUE.bg
3. chatFocusRing = rgba(42, 80, 206, 0.08)（由 RISK_ACCENT 派生）
4. chatHitRowBg = #fdf1ea（预警命中行底，ORANGE tint 60% 不透明等效）

---

## 10. 组件命名与 @ant-design/x 映射（给前端，不写实现）

    web/src/chat/
    ├── ChatShell.tsx        # 三区骨架 + 顶栏 + 断点
    ├── SessionSidebar.tsx   # 左栏（展开/折叠两态）
    ├── MessageFlow.tsx      # 滚动区 + 垂直节奏 + 回到底部
    ├── MessageItem.tsx      # 消息头 + 块流 + 操作条
    ├── blocks/
    │   ├── BlockText.tsx    ├── BlockTable.tsx   ├── BlockChart.tsx
    │   ├── BlockReport.tsx  ├── BlockTools.tsx   ├── BlockConfirm.tsx
    ├── EvidenceDrawer.tsx
    ├── ChatComposer.tsx
    ├── EmptyState.tsx       # 空态 + SuggestionChips
    └── chatTokens.ts        # §9.6 四项

x 组件映射：Conversations = 左栏列表；Bubble = 用户气泡（variant filled + 底色覆写）；AI 块流 = 自绘布局（仅 text 块可包 Bubble variant borderless）；Sender = 输入区；ThoughtChain = tools 展开态；Welcome + Prompts = 空态标题与建议问题。以 x 2.9 实际 API 为准，覆写值以本文档为准。

---

## 11. 高保真样式稿验收清单

1. 三区：左栏 240/56 折叠动画 180ms；阅读列 760 居中；抽屉 400 overlay 不挤压中栏。
2. 空态：6 chips 2 列排布，点击直接发送，且各自命中剧本对应块型。
3. 用户气泡 #e7f0ff、右对齐、560 上限；AI 回答无框、缩进 32、消息头含常显时点。
4. 天晟剧本一屏六块齐全：tools 折叠行 / text 加粗数字 / table 橙 tint 命中行 / chart 橙柱 + 阈值线 / report 索引卡 / confirm 橙框。
5. confirm 批准后：状态条含 审计 #A-1024 · 操作人 · 时间；卡边框退灰且不可逆。
6. 「查看证据链 · 审计 #A-1024」常显；抽屉四区完整、审计时间线可见。
7. 全站颜色与 riskTheme 一致；无 #1677ff / #fa8c16 / #52c41a 残留。
8. 图表配色语义映射（达标绿/触达黄/预警橙），阈值线含「预警线 10%」标签。
9. 错误卡在消息流内、可重试、无堆栈泄漏。
10. 流式光标 accent 2x16；表格闭合升级瞬间无布局跳变。
11. IME 组合中 Enter 不误发。
12. 断点 1440 / 1024 行为符合 §2.7。
13. 阴影仅 xs / sm / drawer 三档；无 glassmorphism、无渐变、无紫色。
14. 「演示环境 · 模拟数据」声明在空态常显。

---

## 12. 待澄清问题清单（12 条，均已给默认假设）

| # | 问题 | 本文档默认假设 |
|---|---|---|
| 1 | 用户身份/头像来源与登录态 | 单角色演示「风险合规部 · 张处长」，头像取姓氏字，无登录态 |
| 2 | confirm「双签」是否含上级复核人 | 单签 + 审计留痕已达「人拍板」意图；若剧本要求复核，卡片需加第二状态段 |
| 3 | 建议问题点击行为 | 直接发送；备选「填充输入框可修改」 |
| 4 | 报告下载格式 | 下载 Markdown；PDF 走预览 Modal 的浏览器打印 |
| 5 | 抽屉内 basis 行数/快照时间等演示数值 | 由数据侧给假值，本文以「1,284 行 · 快照 08:00」占位 |
| 6 | 暗色主题 | S4 仅浅色（riskTheme 亦仅浅色） |
| 7 | 会话管理范围 | 仅新建/切换/折叠；重命名/删除/置顶不做 |
| 8 | 顶栏「证据链」无依据时行为 | 禁用态 + title 说明 |
| 9 | 旧原型临时色（#1677ff/#fa8c16/#52c41a）废弃 | 原型对决已完成使命，AntdXPage 后续按本文更新 |
| 10 | 移动端/窄屏 | 非目标，仅 <1024 兜底不烂 |
| 11 | 输入字数上限 500 | 演示值，接真实后端时对齐 |
| 12 | 「证据链」术语与口径包用语是否一致 | 统一用「证据链」，消息级入口动词用「查看」；请口径包负责人确认 |

### 12.1 裁决记录（2026-09-02，Jack 拍板）

| # | 问题 | 裁决 |
|---|---|---|
| 2 | confirm 双签是否含上级复核 | **双签短期非重点**。当前场景主逻辑 = 问 AI → 分析结果回答（问数优先）；confirm 块保留为能力演示，不作为标准应答必含项；后续批次（多轮对话/真实问数）以问数链路为先，双签工作流后置 |
| 3 | 建议问题点击行为 | 点击即发送；**关键约束 = 建议问题必须「问得准、答得上来」**：命中真实剧本口径；真数据批次起，每条 chip 必须有后端真实可答链路，答不上来的不上 chips |
| 12 | 证据链术语 | 统一用「证据链」，后续随口径包细化再调整 |

其余 9 条（#1、4–11）按本文档默认假设执行。

### 12.2 批 3 交付注记（2026-09，真实问数链路）

- **范围**：读路径问数接线（裁决 #2「问数优先」）。live 模式下回答/证据/图表全部来自 `/agent/risk/chat`（ap_anping 六库实查 + DeepSeek）；写路径不接线——need_confirm 渲染真实提议卡，但拍板按钮明确提示「写回链路后续批次接入」，不伪造执行态。
- **数据源开关**：默认 fake（剧本演示）。live = URL 加 `?src=live` 或 `VITE_CHAT_DATA_SOURCE=live`；live 模式所有会话空态开场（不预置剧本历史）。
- **chips 契约盘点结果（裁决 #3 硬约束）**：6 问 4 直答；c2 补「天晟集团」主语（原问后端必反问定位）、c4 改为提问后由前端从揭示载荷 detail_rows 派生真图（后端只读不出图）、c1 用全称「天晟集团有限公司」（同名农业系集团多，短称有定位反问概率）。
- **载荷映射**：evidence[] → 抽屉五区（结论/basis 表/命中规则/口径分母/明细行引用）；intent → tools 步骤文案；rules_hits[R1a].computed.ratio + detail_rows → 图表派生（org_reference_ratio 是本机构当前占比而非参考线，机构柱用中性色，不臆测色语义）。
- **已知风险（M5 演示前需数据侧确认）**：同题多跑存在「定位反问」概率（LLM 路由方差），非前端问题；建议数据侧补集团别名表或演示前用 patch 脚本重置到剧本态。

### 12.2b 批 4-② SSE 流式注记（2026-09，流式对话链路）

- **端点**：`POST /agent/risk/chat/stream`（SSE，`text/event-stream`）。帧契约：`token {text}` 正文增量 / `tool_start {name}` / `tool_result {name, outcome}` 工具实查直播 / `final {session_id, reply, need_confirm, outcome, evidence}` 终帧（与旧端点响应体同构）/ `error {message}` 编排异常。会话管理、F22②反问定位、P1-1 追问上下文注入与旧端点同源；旧端点 `/agent/risk/chat` 保留（评测/冒烟兼容）。
- **后端流式**：DeepSeekProvider.chat_stream（stream=True 聚合 tool_calls delta，token 增量实时回调）；Agent._llm_call 在 on_event 存在时对**本轮全部 LLM 调用**（首轮/工具追问/终答）走流式——终答逐字推送而非整包；on_event=None 时行为与原版完全一致（评测/存量调用零改动）。编排在 worker 线程 + queue 中运行，generator 即时 yield（无攒批）。
- **前端流式**：`streamRiskChat`（fetch reader 解析 SSE 帧，final 兑现完整响应）；`runLive` 消费事件流——tool_start 直播 tools 块步骤、token 增量渲染 text 块（BlockText liveStream 分支，不走路内打字机）、final 兑现 evidence/needConfirm/chartSeries 并覆盖修正 reply。工具帧缺失时按载荷 intent 补建步骤。
- **实测**（真 DeepSeek，2026-09-07）：事件序 `token→tool→…→final` 正确；首 token 1.0–4.9s（重提示词 + 20 工具 prefill 方差，非代码问题）；工具步骤实时直播；终答逐字流式后 final 帧确认。

---

*本文档只含设计规格，不含实现代码；所有数值即终值，变更走版本号 v1.x。*
