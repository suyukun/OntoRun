# ChatBI 展示层改造开发计划 v0.1

> 依据：产品设计文档 v0.2（两轮外部评审 P0 已闭环）+ demo 机制验证（scripts/fortune_demo/，commit ae7fdec~78bf40b）。
> 执行：子代理派活，模型 **zai-coding-cn/glm-5.3-flash**（Jack 指定），并发 ≤2 长任务。
> 代码落位：后端 **src/semantic/**（新包）+ 前端 **chatbi/**（新工程 Vite+React+TS）；scripts/fortune_demo/ 与 web/ 只读参照，不改动。
> 纪律：探索期测试只锁核心不变量；bash 显式 timeoutMs；派活前清点工作区防双飞；每任务交付 = 能跑的真实产物 + 如实验证报告。

## 任务卡

### T1 后端语义服务（src/semantic/ + tests/semantic/）
- **目标**：demo 语义层机制工程化——规则注册表配置化、iter_query 事件流、LLM 路由（DeepSeek env + 关键词降级 + 规则枚举硬校验）、八状态 block_reason 结构化（missing_param/out_of_range 分离）、trace JSONL 幂等（client_request_id）、会话/消息 SQLite 持久化（删除=hidden 标记，物理保留）、PII 脱敏钩子、LLM 原始输出脱敏、错误码体系、viz 字段进规则表。
- **API**：/api/profile · /api/chat(SSE) · /api/history · /api/trace/{rid} · DELETE /api/history/{rid} · /api/sessions CRUD。
- **数据**：复用 data/fortune/fortune.db 合成样本（build_sample.py 可复跑）。
- **验收**：pytest tests/semantic/ -q 全绿（核心不变量：六路径 final 帧 / 幂等 / 删除隐藏 / 数字填充）；curl 冒烟六状态各一问全过；uvicorn :8901 可起。
- **依赖**：无（波 1）。

### T2 ChatBI 壳工程（chatbi/）
- **目标**：Vite+React18+TS 脚手架；三栏布局；profile 装配（GET /api/profile，未联调时内置 mock 模式独立开发）；SSE 消费 hook useChatStream（AbortController 取消、step/token/final 分派、断连错误态）；MessageCard 骨架（L1 摘要条/回答流式/数据表格/L2 收起/L3 抽屉）；SessionBar（列表+新对话+四操作占位）；八状态状态机分发（v0.2 §4.2）。
- **验收**：npm run dev 可起；tsc --noEmit 零错；eslint 过；mock 模式下模拟查询可见消息卡骨架与流式效果。
- **依赖**：无（波 1，与 T1 并行；联调在波 2）。

### T3 消息卡与三级披露（依赖 T2）
- L1 摘要条（生成期动态「第 n/N 步」→完成后路径摘要）；L2 步骤列表按 path 连续编号（无跳号）；L3 详情抽屉（LLM 原始输出**脱敏**展示/完整 SQL/逐项校验/耗时）；八状态 UI + 错误文案映射（附录 B）；IME 组合键保护；停止/取消。

### T4 会话管理与持久化联调（依赖 T1+T2）
- 会话四操作（重命名/置顶/收藏/删除=隐藏）；历史回放（快照，数据变更后回放不变）；刷新恢复；client_request_id 重试幂等。

### T5 D6 模板方案与数字校验（依赖 T1）
- 句式模板注册表（按规则配置）；语义层数字填充；数字一致性校验器（渲染前全量比对，不一致整条拦截 + 数值对照展示）。

### T6 viz 契约与渲染（依赖 T3）
- 表格渲染（P0 必做）；图表按 viz 字段（P0 末若顺延则 P1 首项）；图表与表格同源（同一 rows）。

### T7 验收测试包与集成联调（依赖 T1-T6，Rose 主导）
- 八状态用例集、D6 数字一致性用例（抽 10 次全比对）、回放一致性、性能三段采样（P95）、BACKLOG 销号。

## 派活波次
- **波 1（现在，并行 2）**：T1 + T2
- **波 2（T1/T2 交付后，并行 2）**：T3 + T4；T5 插队（T1 交付即可开）
- **波 3**：T6 + T7 集成联调（Rose 主导，演示模式 v1 移 P1）

## 风险与预案
- LLM 路由延迟抖动 → 降级关键词匹配已内建；联调期若 DeepSeek 限流，用 mock 路由开关开发；
- 子代理卡限流症状识别（零文件动静 20 分钟）→ 先查限流窗口再判僵死（AGENTS.md）；
- 接管前必须终止旧会话 + 清点工作区（防同任务双飞）。

## 验收总门（Rose 阶段末执行）
T7 全过 + 产品设计 v0.2 §7 十二条验收逐条核对 + 全量新增 pytest 零失败。