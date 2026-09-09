# chatbi — 财富广场 ChatBI 壳工程（T2）

Vite + React 18 + TypeScript 对话壳骨架。产品契约：`docs/财富广场-ChatBI展示层产品设计_v0.2.md`（布局 §3、八状态 §4.2、SSE 协议附录 A、错误矩阵附录 B、profile schema 附录 C）。视觉精修归 T3。

## 启动

```bash
npm install    # 国内源：npm install --registry=https://registry.npmmirror.com
npm run dev    # http://localhost:5173；/api 代理到 localhost:8901（T1 语义服务）
npm run build  # tsc --noEmit + vite build
npm run lint   # eslint .
npm run test   # vitest：mock 模式核心流程 + 八状态映射
```

注：`.npmrc` 已含 `legacy-peer-deps=true`——npm 10.9 arborist 在 vitest 4 可选 peer 集上崩溃（edgesOut null，两次实证）的规避，npm 升级后可移除。

## mock 数据模式（独立开发，不依赖后端）

启动时 `GET /api/profile`（经 Vite 代理）：

- **后端在线**（T1：`uvicorn src.semantic... :8901`）→ 真实 profile 装配（端点/示例问题/路径徽章），SSE 直连后端；
- **后端未起**（网络失败/非 200/结构缺失）→ 自动降级为内置 mock profile + mock 事件回放，页头显示橙色「**mock 数据**」标识。

### mock 关键字 → 场景对照（八状态全覆盖）
- 服务异常|停服|宕机 → error 帧（服务异常）
- 断流|断网|断开 → 无 final 帧（已中断）

| 问题包含 | mock 场景 | §4.2 状态 |
|---|---|---|
| 「渠道」 | 冷路径·明细下推，4 行数据 | 2 成功 |
| 「男女」/「性别」 | 冷路径·维表即席 | 2 成功 |
| 「降级」 | 成功 + 黄标「简化路由」 | 2b 成功·含告警 |
| 「凌晨」 | 0 行 | 2c 成功·空结果 |
| 无月份的「注册…」 | 追问「哪个月份？」+ 参数 chips | 3 参数追问 |
| 「9月」/「去年」 | 数据边界说明 | 5 拒答·范围超限 |
| 「活动」/「日活」/「活跃」 | 域说明拒答 | 6 拒答·范围外 |
| 「校验」 | 同源交叉失败拦截 | 7 校验失败 |
| 其他任意 | 未注册口径 | 4 拒答·口径缺失 |
| （真实模式）停服/断网/断流 | E_NET 脱敏文案 + 重试；断流标「已中断」 | 8 服务异常 |

## 组件清单

| 文件 | 职责 |
|---|---|
| `src/App.tsx` | 三栏布局（会话栏 230px / 对话区 / 输入区）、profile 装配与降级、消息流状态 |
| `src/components/SessionBar.tsx` | 会话列表 + 新对话 + 四操作（重命名/置顶/收藏/删除；本地态占位，删除有二次确认） |
| `src/components/ChatInput.tsx` | 输入区：IME 组合键保护（compositionstart/end 期间 Enter 不发送）、生成中停止按钮 |
| `src/components/MessageCard.tsx` | 消息卡：L1 摘要条（生成期「第 n/N 步」动态→完成后路径徽章+证据编号）→ 回答流式 → 数据表格 → L2 决策过程（默认收起，点击 L1 展开）→ 八状态 UI 分支 |
| `src/components/DataTable.tsx` | 数据区表格（列由 rows 首行推导，与图表同源） |
| `src/components/DetailDrawer.tsx` | L3 详情抽屉（决策过程/结论依据/返回数据 Tab 容器占位） |
| `src/hooks/useChatStream.ts` | SSE 消费：fetch reader 解析 data: 帧（兼容 event-name 风格）、AbortController 取消、30s 无帧看门狗、断流→「已中断」、error 帧→服务异常；mock 模式按序列延时回放 |
| `src/state/deriveStatus.ts` | 八状态推导（path→状态一对一；blocked_param 按 block_reason 拆分） |
| `src/mock/profile.ts` | 内置 mock profile（附录 C 字段子集）+ 徽章文案兜底 |
| `src/mock/stream.ts` | mock 事件序列（step/token/final，格式对齐附录 A 与 demo iter_query） |

## 已知边界（后续任务接管）

- 会话/消息**不持久化**：切换会话清空画布；服务端持久化/历史回放/删除隐藏在 T4；
- L1 完成后摘要、L3 脱敏 LLM 原始输出/耗时展示、追问 chips 由规则表生成：T3/T5；
- 视觉细节与响应式：T3。
