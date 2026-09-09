# 财富广场 ChatBI 展示层 · UX 审查报告 v0.1

> 审查人：资深 UX 专家（ToB 数据产品 / BILLING 级后台系统方向）
> 审查对象：chatbi/（React 18 + TS + Vite，http://localhost:5173）× 语义服务 http://127.0.0.1:8901
> 契约基线：docs/财富广场-ChatBI展示层产品设计_v0.2.md（§3 布局 / §3.2 消息卡 / §4.2 八状态）
> 方法：① 代码层布局审查（通读 index.css + 全部组件，画高度/overflow 链）② 渲染态截图走查（headless Chrome：长对话 / 修复对照 / 375px / 1920px / L3 抽屉 / 线上空态 六视角）③ Nielsen 十启发式 + Ant Design 企业级规范逐项评估 ④ 全量用户可见文案审查
> 纪律：只读代码，未改任何组件/CSS/配置；截图临时文件已清理；复现命令见附录 A
> 日期：2026-09-09

---

## 〇、执行摘要

| # | 级别 | 问题 | 一句话根因 | 工作量 |
|---|---|---|---|---|
| 1 | **P0** | 多轮对话后消息区无滚动条，输入框被顶出屏幕 | React 挂载点 `#root` 无样式，100vh 高度链在第一层就断裂（demo 直接挂 body 所以没这问题，属迁移回归） | **S** |
| 2 | **P1** | emoji 当图标（⭐📌✏️🗑⏳⧉■◻ / 🔥❄⛔ 徽章），「一点高级感都没有」 | emoji 分布在五处：契约 §3.2 示例本身、后端 profile、前端 mock 兜底、demo 视觉参照、壳内组件；前端 `labels.ts` 目前恰好覆盖了完成态徽章，但任何一处回潮就会复现 | M |
| 3 | **P1** | 配色杂、不简约大气（亮蓝 + 橙 + 多色徽章五色并现） | 色彩承担了本该由灰度/字重/留白承担的层级职能；主色饱和度过高、徽章全用实心彩底 | M（token 表已给出，见 §六） |
| 4 | **P1** | 次要文字对比度批量不达标 | 提示灰 `#98a2b3` 在白底仅 **2.58:1**（WCAG AA 要求 4.5:1），覆盖 hint/空态/耗时等 6 类小字 | **S** |
| 5 | **P1** | 文案硬伤 4 处 | `已记录（编号）` 占位符直出、空态让用户「见 README」、「半成品已丢弃」开发腔、L2/L3 内部编号泄漏到 UI | S |
| 6 | P2 | 窄屏（<700px）布局完全失效 | 侧栏固定 230px、无任何响应式断点（契约分期本就排在 P2，此处实锤基线） | M |
| 7 | P2 | 流式输出时强制滚底（滚动劫持）等交互细节 16 项 | 见 §四 P2 清单 | S~M |

总体判断：**信息架构与三级渐进披露（L1⊂L2⊂L3）的产品骨架是对的**，八状态覆盖完整、证据编号/校验摘要/防假数等可信设计都在线上；当前短板集中在**视觉体系（色彩/图标/密度）与一条断裂的布局链**，均属可在 1~2 天内收敛的工程问题，不动产品逻辑。

---

## 一、P0：布局高度链断裂（滚动条缺失 + 输入框不可见）

### 1.1 现象（已截图实锤）

对话轮次增多后：消息区**不出滚动条**、内容在视口底部被拦腰截断（截图中柱状图切半）、输入框完全不可见。用户无法回看历史，也无法继续提问。

### 1.2 实际高度链（代码走查）

预期链（demo chat.html 的链，是通的）：

```
body (height:100vh; flex column; overflow:hidden)     ← scripts/fortune_demo/chat.html:11
 ├─ header (flex:none)
 └─ .layout (flex:1; min-height:0)                    ← chat.html:14
     ├─ .side  → .hlist (flex:1; overflow-y:auto)
     └─ .main → .msgs (flex:1; overflow-y:auto) ← 滚动发生在这里
              → .inputrow (flex:none)
```

实际链（React 壳，断的）：

```
body (height:100vh; flex column; overflow:hidden)     ← chatbi/src/index.css:16-25
 └─ #root  ←★ chatbi/index.html:9，全项目没有任何一条 #root 样式（index.css 全文 393 行无 #root）
     ├─ header                                        ← App.tsx:214
     └─ .layout (flex:1; min-height:0)                ← App.tsx:219；父级 #root 不是 flex，flex:1 失效
         └─ .msgs (overflow-y:auto)                    高度 auto、随内容长高，永远撑不到溢出 → 永不滚动
```

**断裂机制（实锤）**：`#root` 是 body（column flex）的唯一子项，默认 `flex: 0 1 auto`。它的主轴最小尺寸 `min-height: auto` 按 flexbox 规范取「内容高度」（因其 overflow: visible）→ **永远收缩不下来**。于是：

1. 消息一多，`#root` 高度 = 内容总高 > 100vh；
2. `body` 的 `overflow: hidden`（index.css:24）把溢出部分**直接裁掉**——既没有页面滚动条，`.msgs` 也因为自身高度无约束而从不溢出；
3. `.inputrow`（index.css:374）排在被裁区域里 → 视觉上「被顶出屏幕」。

**为什么 demo 没这个问题**：chat.html 的 DOM 直接挂在 body 下（chat.html:69-87），header/.layout 是 body 的 flex 子元素，链是通的。React 化时多包了一层 `#root` 而样式没跟上——**纯迁移回归**。

### 1.3 修复 CSS（S，一处改动）

```css
/* chatbi/src/index.css 追加：接通 100vh 高度链 */
#root {
  height: 100vh;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
/* 防御性补强（非必须，但防后续在 .main 里再插一级 flex 项时重蹈覆辙） */
.main { min-height: 0; }   /* 现仅有 min-width: 0（index.css:105） */
```

### 1.4 已验证

用 headless Chrome 对同一 DOM 做「断链 vs 修复」对照截图（1440×900，13 轮对话全状态堆叠）：

- 断链版：柱状图在视口底部被截断、无滚动条、输入框不可见；
- 修复版（仅加上述 `#root` 规则）：输入框固定回视口底部，`.msgs` 独立滚动。**修复有效**。

### 1.5 连带发现（同一次走查）

- **滚动劫持（P2-1）**：App.tsx:56-59 在每次 `messages` 变化时无条件 `scrollTop = scrollHeight`——流式输出期间每个 token 都会把用户拽回底部，想上滑回看会被持续拉扯。建议改为「仅当用户本就在底部附近（距底 <80px）才跟随」。
- **图表随容器失控放大 + 行长失控（P2-8）**：Chart.tsx:54 的 SVG `width:100%; height:auto` + viewBox 560×190，在 1440px 宽卡片里柱状图被等比放大到 ~370px 高；1440px 下气泡宽 94% ≈ 1170px，单行 ~90 字符，可读性差。建议内容列 `max-width: 860px`、图表容器 `max-height: 240px`。

---

## 二、渲染态截图走查记录（六视角）

| 视角 | 关键发现 |
|---|---|
| 长对话 1440×900（断链） | §一 P0 全部实锤；橙徽章/亮蓝图表/多色徽章同屏，杂色感直观可见 |
| 长对话 1440×900（修复版） | 滚动恢复、输入框回位；内容列过宽（行长 ~90 字）、图表过高（§1.5）；L1 条右侧「详情/▲收起过程」层级拥挤 |
| 窄屏 375×812 | **布局完全失效**：侧栏固定 230px（index.css:51-58）无断点，对话区仅剩 ~145px，徽章/气泡/KPI 数字全部裁切。契约分期把窄屏排 P2，维持 P2，最小改法：`@media (max-width:700px)` 侧栏折叠为抽屉/下拉 |
| 宽屏 1920×1080 | 气泡 94% 宽 ≈ 1600px，行长超 130 字符，阅读性崩坏（根因同 §1.5）；空态 chips 居中尚可 |
| L3 抽屉 | 三分区 Tab/脱敏声明/步骤含 SQL 结构完整；但无 Esc 关闭、无焦点管理（role="dialog" 无 aria-modal/焦点陷阱，DetailDrawer.tsx:30-41） |
| 线上实拍（5173，后端在线） | 启动即恢复最近会话（非空态）；完成态徽章确认为纯文字「月报口径（预聚合）」（§3.1 澄清的实证）；真实回答 1,778 人 + 3 项校验全过 + REQ 编号渲染正常。**新发现：侧栏 20+ 条同名会话标题堆叠、无时间戳/摘要，无法扫视区分 → P2-17**；线上与本地复现共用同一未修的高度链，长对话同样触发 P0 |

---

## 三、图标体系：去 emoji 化方案（对应「很丑、没高级感」）

### 3.1 现状盘点（emoji 的真实分布——比表面看到的更深）

| 层 | 位置 | 内容 |
|---|---|---|
| ① 契约示例 | 产品文档 v0.2 §3.2：L1 示例 `⏳ 校验中…`、`❄ 冷路径·明细下推`、`REQ…⧉` | **规范的示例本身带 emoji**——照抄契约的实现必然长出 emoji |
| ② 后端下发 | `GET /api/profile` → `path_labels`（实测在线返回）：`🔥 热路径·月报口径`、`❄ 冷路径·明细下推`、`🧊 冷路径·即席计算`、`⛔ 参数待补/超边界`、`🚫 未注册口径`、`🚫 范围外`、`⚠️ 校验未通过` | 数据源带 emoji |
| ③ 前端兜底 | chatbi/src/mock/profile.ts:21-28 同款 + `✋ 参数追问` | 同上 |
| ④ demo | scripts/fortune_demo/chat.html:91-92 `PATHNAMES` 全套 emoji（**用户视觉初版来源，用户看到的就是它**） | 视觉参照污染 |
| ⑤ 壳内组件（线上真实渲染，与 demo 同属「四处一起改」的第 4 处） | SessionBar.tsx:26-27,31-41（⭐📌✏️🗑）；App.tsx:203（🗑 历史）；MessageCard.tsx:192（⏳）、:208（⧉ 复制/✓/✗）、:121（◻ 空态）、:220（▲▼ 折叠）；ChatInput.tsx:38（■ 停止）；App.tsx:160（← 返回）；SessionBar.tsx:21（＋ 新对话）；DetailDrawer.tsx:34（×） | 全部待替换 |

**重要澄清（给排查者）**：线上 React 壳的完成态徽章目前其实是**纯文字**——MessageCard.tsx:29-38 的 `badgeText()` 让 labels.ts 的业务文案（`月报口径（预聚合）`等，labels.ts:4-24）优先于 profile 下发的 emoji 标签。「🔥❄ 徽章」主要活在 demo、mock 兜底与后端数据里。**但这属于巧合性防御**：契约与后端都视 emoji 为合法载荷，任何一处改动（如改 profile 驱动渲染）就会全面回潮。去 emoji 必须**四层一起改**。

另注意：测试锁了 emoji——chatbi/src/__tests__/messageCard.test.tsx:46 断言 `/⏳ 第 \d+ 步 · .+/`，改 ⏳ 必须同步改测试。

### 3.2 方案：零依赖内联 SVG 图标 + 文字优先（推荐）

依赖现状：chatbi/package.json 仅 react/react-dom，**零 UI 依赖**。引图标库（如 lucide-react：tree-shaking 后每图标 ~1KB、ESM、国内 npmmirror 可达）是可选项，但当前仅需 **11 枚图标**，自绘内联 SVG 组件更符合项目「零依赖/最小实现」纪律。

新建 `src/components/Icon.tsx`（单文件：24 viewBox / 1.5px stroke / currentColor / aria-hidden，默认 14-16px）：

| 现字符 | 用途 | 替代图标（命名对齐 lucide，每枚 3-5 条 path） | 位置 |
|---|---|---|---|
| ⭐ | 收藏 | `star`（已收藏 fill / 未收藏 stroke） | SessionBar / 历史 |
| 📌 | 置顶 | `pin` | SessionBar |
| ✏️ | 重命名 | `pencil` | SessionBar |
| 🗑 | 删除 | `trash` | SessionBar / 历史 |
| ＋ | 新对话 | `plus` | SessionBar |
| ⏳ | 进行中 | `loader`（慢速旋转；L1 文字已含「第 n 步」，图标仅装饰） | MessageCard L1 |
| ⧉ 复制 | 复制证据编号 | `copy` | MessageCard |
| ✓ / ✗ | 校验/复制成败 | `check` / `x`（同形异色，靠语义 token 区分） | MessageCard / StepList / Drawer |
| ◻ | 空结果 | `inbox` | MessageCard 空态 |
| ■ | 停止 | `square`（10px 实心） | ChatInput |
| ▲ / ▼ | 折叠指示 | `chevron-up` / `chevron-down`（150ms rotate 过渡） | MessageCard L2 |

**文字优先原则**（比图标更重要）：hover 才出现的低频操作（重命名/置顶/收藏/删除）在 12px 会话条目里本就点不准——收进一个 `more-horizontal`（⋯）菜单，菜单项用**纯文字**（AntD 规范：纯图标按钮必须配 Tooltip）；「详情」「重试」「发送」这类主操作继续文字按钮，不配图标。

**配套改动清单**：① 契约 §3.2 示例去 emoji（改纯文字版式：`路径 · 校验摘要 · 证据编号`）② 后端 profile `path_labels` 去前缀 emoji ③ mock/profile.ts 同步 ④ chat.html 归档、不再作视觉参照 ⑤ messageCard.test.tsx:46 正则同步。工作量 **M**。

---

## 四、问题清单（分级全量）

### P0（功能缺陷，阻塞演示）

**P0-1 消息区无滚动条 / 输入框不可见** —— 现象/根因/修复/验证见 §一。工作量 **S**。

### P1（体验硬伤）

**P1-1 emoji 图标体系** → §三。**M**
**P1-2 次要文字对比度批量不达标**
- 根因：`#98a2b3` 同时用于 `.l2hint`（index.css:166）、`.empty`（:108）、`.hint`（:227）、`.stp-ms`（:271）、`.basis-path`（:367）、`.req-ic`（:199），白底 2.58:1，低于 WCAG AA 小字 4.5:1（数据分析场景常遇投影/低亮度屏，更糟）。
- 建议：新增 token `--sub2: #667085`（4.97:1）替换上述六处；`--sub`（#5a6572，5.93:1）保留。**S**
- 连带：橙徽章白字 4.01:1 亦不达标——§六徽章改描边后自然解决。

**P1-3 文案硬伤包（4 处）**

| 现文案 | 位置 | 问题 | 建议 |
|---|---|---|---|
| `查询执行出错，已记录（编号）` | labels.ts:29 | 「（编号）」是未实现的占位符，原样显示给用户 | 「查询执行出错，已记录（证据编号见本卡上方）」或模板插值 request_id |
| `mock 数据模式：试试示例问题（八状态关键字见 README）` | App.tsx:241 | 让终端用户「见 README」，工程视角泄漏 | 「内置演示数据：试试示例问题，或直接输入」；关键字对照收进 tooltip/帮助 |
| `连接已中断，半成品已丢弃。` | MessageCard.tsx:173 | 开发腔 + 威胁感 | 「连接中断，本次回答未完成，可重试。」 |
| `决策过程（L2 · n 步）`、`详情（L3）· …` | MessageCard.tsx:250；DetailDrawer.tsx:33 | L2/L3 内部编号泄漏（附录 G 术语表亦未定义其用户文案） | 「决策过程（n 步）」「详情」；L1/L2/L3 留在代码与文档 |

工作量合计 **S**。

**P1-4 配色体系杂、不简约大气** → §六。**M**

### P2（打磨；多项与契约分期对齐）

| # | 问题 | 根因（文件:行） | 建议 | 量 |
|---|---|---|---|---|
| P2-1 | 流式输出滚动劫持 | App.tsx:56-59 无条件滚底 | 距底 <80px 才跟随 | S |
| P2-2 | 窄屏 <700px 布局崩坏（截图实锤） | index.css:51-58 侧栏固定、无断点 | ≤700px 侧栏折叠；契约分期 P2 | M |
| P2-3 | 切会话时短暂显示上一会话消息 | App.tsx:62-75 fetch 前不清空 | 切换即清空 + 骨架占位 | S |
| P2-4 | 重命名/删除用原生 prompt/confirm | App.tsx:140,146,200 | 统一轻量 Modal，气质对齐 §六 | M |
| P2-5 | 会话操作 hover-only，触屏/键盘不可达 | index.css:85-92 无 :focus-within | focus-within 同 hover；触屏常显 ⋯ 菜单（配合 §三） | S |
| P2-6 | L1 条可点击但不可键盘操作 | MessageCard.tsx:183-189 role=button 无 tabindex/onKeyDown | 补 tabindex + Enter/Space | S |
| P2-7 | L3 抽屉无 Esc/焦点陷阱/aria-modal | DetailDrawer.tsx:30-41 | Esc 关闭 + 锁 body 滚动 + 焦点管理 | S |
| P2-8 | 宽屏内容列过宽 / 图表失控放大 | index.css:132；Chart.tsx:54 | 内容列 max-width:860px；图表 max-height:240px | S |
| P2-9 | 历史列表直出 request_id 原文 | App.tsx:192 | rid 缩为末 6 位等宽小字，主信息=问题+时间+路径 | S |
| P2-10 | 数值列可能被长表头挤压 | index.css:309-316 | `td.num{white-space:nowrap}`；长表头省略 | S |
| P2-11 | 柱状图 >10 分类时标签重叠 | Chart.tsx:46-47 | TOP10+「其他」聚合，或仅 hover 显数值 | M |
| P2-12 | 本地降级模式新会话排在列表底部 | useSessions.ts:127-137；SessionBar.tsx:16 | 本地按创建时间倒序，对齐服务端语义 | S |
| P2-13 | mock 拒答文案带「（Jack 2026-09-08 收窄指令）」 | mock/stream.ts:174 | 演示数据也是交付物：「当前语义范围仅注册域，扩展需先注册口径」 | S |
| P2-14 | 「✗ 未复制」技术腔 | MessageCard.tsx:208 | 成败两态即可 | S |
| P2-15 | 「数据边界来自语义层元数据」术语泄漏 | MessageCard.tsx:142 | 「数据覆盖范围以系统登记为准」 | S |
| P2-16 | 圆角 7/8/10/12/14/18 混用、间距无 4/8 栅格；z-index 40/41 硬编码 | index.css 全文；:319-327 | 栅格化 + 圆角三档（6/10/14）+ z-index token；随 T3 精修 | M |
| P2-17 | 会话列表同名堆叠、无时间/摘要元信息（live 实拍：20+ 条「2026年8月注册用户数是多少？」级重复标题） | 会话模型仅 title（types.ts:111-116）；SessionBar.tsx:25-28 仅渲染标题 | 列表项加相对时间 + 首问摘要或路径徽章；同名自动去重合并可选 | S |

---

## 五、启发式评估（Nielsen 十条 × AntD 规范）

| 启发式 | 评价 | 证据 / 对应问题 |
|---|---|---|
| 1 系统状态可见 | **良好偏上** | L1 直播（第 n 步→生成中）+2.5s 呼吸态+骨架屏齐全；扣分：滚动劫持（P2-1） |
| 2 贴近真实世界 | **有硬伤** | 「语义层元数据」「半成品」「README」（P1-3/P2-15）；L2/L3 编号泄漏 |
| 3 用户控制 | **中** | 停止/重试/取消/历史回放齐；扣分：Esc 缺失（P2-7）、原生 confirm（P2-4） |
| 4 一致性 | **有硬伤** | 两种 Tab 样式（App.tsx:32-33 内联 vs DetailDrawer tabs 类样式）；圆角/间距无栅格（P2-16）；历史面板内联 style（App.tsx:157-209）与类样式双轨 |
| 5 防错 | **良好** | IME 组合键保护（ChatInput.tsx:29-34）、busy 置灰、删除二次确认、幂等重试——最扎实的部分 |
| 6 识别而非回忆 | **中** | 示例 chips 好；扣分：追问 chips 硬编码 ['8月','7月']（MessageCard.tsx:22，已注释标 T5） |
| 7 灵活高效 | **中** | 无会话搜索/快捷键（Enter 已有）；演示模式未做（契约 P1，不扣） |
| 8 美学简约 | **不达标** | emoji + 五色徽章 + 亮蓝橙撞色（P1-1/P1-4） |
| 9 容错 | **良好** | 八状态文案清晰、校验失败给数值对照、断流标「已中断」——可信设计在线 |
| 10 帮助文档 | **中** | 证据编号 hover 说明好；空态指引提 README（P1-3） |

**AntD 规范对照**：表格行距 6px 偏紧（建议 8px）；L1 条右簇与左侧徽章基线不齐（宽屏尤甚）；z-index 硬编码应收 token；空/加载/错误三态齐全（好于多数同类壳）；色彩系统见 §六。

---

## 六、配色体系重设计（应 Jack「简约、大气」要求）

### 6.1 现色诊断

- **彩色承担了层级**：亮蓝 #2563eb 同时用于主按钮/用户气泡/链接 hover/柱状图/徽章——「行动=数据=身份」三种含义混在一个色值上；橙色徽章再叠加，蓝橙撞色；
- **徽章全实心彩底**：橙/蓝/灰/warn/bad 五色徽章可同屏（截图走查确认），其中橙底白字 4.01:1 不达标；
- **中性色阶只有 4 档**（#f4f6f9/#fff/#e3e7ec/#1a2332），没有成体系灰阶供层级表达，逼界面用彩色补层级；
- 提示灰 #98a2b3 过浅（2.58:1）——「浅」被误用作「次要」的表达手段。

### 6.2 设计原则（唯一审美判据：简约、大气）

1. **层级靠灰度、字重、留白，不靠彩色**——彩色只留给「语义」（成功/警告/失败）与「主行动」；
2. **单一克制主色**：弃亮蓝与橙，主行动用**墨蓝黑**（Linear/Vercel 式黑按钮）；
3. **状态色只留三色且降饱和**，徽章一律**描边式（outline）**；
4. 参考气质：Linear / Vercel / Notion 的「安静的高级感」——近黑墨字、大留白、几乎不可见的边框、彩色只作状态信号。

### 6.3 色彩 token 表（现色 → 新色对照）

| Token | 现值 | 新值 | 用途 | 白底对比度 |
|---|---|---|---|---|
| `--bg` 页面背景 | #f4f6f9 | **#f7f8fa** | 冷灰底（去蓝倾向，更中性） | — |
| `--surface` 卡片 | #fff | **#ffffff** | 卡片/气泡 | — |
| `--line` 边框 | #e3e7ec | **#e4e4e7** | 中性灰边 | — |
| `--line-strong`（新增） | — | **#d4d4d8** | 描边徽章/输入框静默边 | — |
| `--ink` 正文 | #1a2332 | **#1a1d23** | 近黑墨（去蓝相） | 16.9:1 |
| `--sub` 次要文字 | #5a6572 | **#52525b** | 次级文字/表头 | 7.7:1 |
| `--sub2`（新增，替换散落的 #98a2b3） | — | **#667085** | hint/耗时/空态 | 5.0:1 |
| `--acc` 主色 | #2563eb | **#1f2937** 墨蓝黑 | 主按钮/用户气泡/链接/图表主色 | 14.7:1（白字） |
| `--acc-hover`（新增） | — | **#111827** | 主按钮 hover | — |
| `--ring`（新增） | — | **#94a3b8** | 焦点环（唯一「亮」色，仅键盘焦点出现） | — |
| `--ok` 成功 | #15803d | **#3a7a49** | 校验全过/成功 dot | 4.7:1（底 #f2f7f2） |
| `--warn` 警告 | #b45309 | **#8d6126** | 降级标注/mock 标 | 5.0:1（底 #faf5ec） |
| `--bad` 失败 | #b91c1c | **#a14646** | 校验失败/错误 | 5.5:1（底 #faf2f2） |
| header 背景 | #101828 | **#131316** | 近黑中性 | — |

删除 token：`--hot`（橙）——热/冷路径改为**文字 + dot** 表达，不再占彩色位。

### 6.4 徽章规范：实心彩底 → 低饱和描边式

```css
/* 通用描边徽章：白底 + 1px 边 + 深字，语义只用字色与 dot 表达 */
.badge {
  background: var(--surface);
  border: 1px solid var(--line-strong);
  color: var(--sub);
  font-weight: 600;            /* 层级靠字重，不靠彩底 */
  border-radius: 999px;
  padding: 2px 10px;
  display: inline-flex; align-items: center; gap: 6px;
}
/* dot：路径语义的最小彩色表达（6px 圆点） */
.badge .dot { width: 6px; height: 6px; border-radius: 50%; flex: none; }
.path-hot  .dot { background: var(--ink); }   /* 预聚合 = 实心墨点 */
.path-cold .dot { background: #94a3b8; }      /* 即席 = 灰点（pushdown/adhoc 合并一档，文字已区分） */
/* 状态徽章：仅真正需要扫视捕获的两种状态吃语义色，仍描边 */
.path-validation_failed { border-color: #ecd4d4; color: var(--bad); background: #fdf7f7; }
.warnbadge { border: 1px solid #ead9c8; color: var(--warn); background: var(--surface); }
.oktext    { color: var(--ok); }              /* 纯文字，无底 */
```

要点：**路径徽章（月报口径/明细即席）整体退出彩色系统**——它们是「来源信息」不是「告警」；彩色只留给校验失败/降级。同时解决橙徽章对比度问题。

### 6.5 应用位置清单（改造时逐处对表）

| 位置 | 现状 | 改为 |
|---|---|---|
| `.newchat` 主按钮（index.css:59-68） | 亮蓝实心 | `--acc` 墨蓝黑实心，hover `--acc-hover` |
| 用户气泡 `.m.user .bub`（:131） | #2563eb 实心白字 | `--acc` 墨蓝黑白字（14.7:1） |
| path 徽章 6 类（:178-184） | 五色实心 | §6.4 描边 + dot |
| `oktext/warnbadge/badtext`（:167-176） | 彩字彩底散用 | 语义 token 三色 |
| 柱状图 bars（Chart.tsx:65） | var(--acc) 亮蓝 | `--acc` @80% 透明，hover 100%；网格 `--line`；数值标签 `--sub` |
| KPI 大数字（Chart.tsx:86-88） | --ink | 不变（已对） |
| 表头 th（:310） | #f0f3f7 蓝灰 | #fafafa，表头文字 `--sub` |
| 骨架屏/斑马纹/hover（:239-315） | 蓝灰系底 | 中性灰系（#f4f4f5 系） |
| 「mock 数据」flag（:38-46） | 高饱和橙实心 | 描边 warn（warnbadge 同款） |
| header 副标题 | #98a2b3 | #a1a5ad（深底提示灰，7:1+） |

### 6.6 落地顺序

① 先换 token（:root 一处）+ 徽章类（§6.4）→ 全局气质立变；② 主按钮/用户气泡/图表三处硬编码色；③ 圆角间距栅格（P2-16）随 T3 精修。全程纯样式层，预估 0.5~1 天。

---

## 七、Top5 立即修复清单（按性价比排序）

1. **P0-1 滚动条**：`#root` 高度链修复 CSS（§1.3）——一行块级修复，演示前必须完成。**S**
2. **P1-4 配色 token 收敛第一批**：§6.3 token 表 + §6.4 徽章描边——直接回应「要简约、大气」。**M**
3. **P1-1 去 emoji**：Icon.tsx（11 枚内联 SVG）+ 四层数据源 + 契约示例 + 测试同步。**M**
4. **P1-2 对比度**：`--sub2: #667085` 替换六处 #98a2b3。**S**
5. **P1-3 文案包**：E_SQL 占位符 / 空态 README / 半成品已丢弃 / L2L3 术语。**S**

（P2 清单排入 T3 视觉精修；其中 P2-1/P2-3/P2-7 各 ~10 行代码，可捎带。）

## 八、建议的视觉规范方向（一段话）

以「安静的数据权威」为目标：界面主体是**一套完整的中性灰阶**（#f7f8fa 底 → #ffffff 卡 → #e4e4e7 边 → #1a1d23 墨字，层级用灰度深浅、600/400 字重与 8px 留白栅格表达，彩色从装饰位全部退场），唯一的「黑」是主行动色（墨蓝黑 #1f2937，Linear/Vercel 式黑按钮与用户气泡），唯一的彩色是三个降饱和语义色（成功/警告/失败，只以描边徽章、字色与 6px dot 出现，永不大面积铺底）；emoji 全部替换为 24 viewBox/1.5 stroke 单色内联 SVG，低频操作收进文字菜单；数据是主角——表格与图表只有墨、灰两色加一个语义态，让「校验未通过」的红成为整个界面里最醒目的颜色。这正是 BILLING 级系统「平时安静、异常醒目」的专业气质。

---

## 附录 A：证据与复现

- 审查截图（六张）为临时产物，已按纪律清理；复现：
  ```bash
  CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  "$CH" --headless=new --disable-gpu --timeout=20000 --window-size=1440,900 \
    --screenshot=bug.png "file://$PWD/scripts/fortune_demo/ux_audit_tmp/ux_audit_app_bug.html"
  ```
- 高度链断言可机器验证：`grep -c '#root' chatbi/src/index.css` → 0，而 chatbi/index.html:9 存在 `<div id="root">`。
- 对比度按 WCAG 相对亮度公式计算，关键值：#98a2b3/白 = 2.58:1；#667085/白 = 4.97:1；白/#d9541e = 4.01:1。
- 后端 profile 实测：`curl http://127.0.0.1:8901/api/profile` → path_labels 含 🔥❄🧊⛔🚫⚠️。
