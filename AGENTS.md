# OntoRun 项目规则（AGENTS.md）

> 依据基线模板适配。方向/战略见 `方向与战略_v0.2.md`（本文件的母文件）；反模式复盘见 `~/.dsh/memory/workbuddy-antipatterns.md`。
> 规则确认人：Jack（过目后生效，未确认不派活）。

## 项目概述
- 项目名：**OntoRun**。一句话定位：研究"大模型如何嵌入真实业务系统/真实业务场景"的机制，**聚焦语义接口层**（本体论为方法核心）；传输层（MCP 类）/操作层（Action 写回）用现成方案，不造轮子。
- 目标与成功标准（DoD，第一里程碑 = **最小语义接口闭环**）：
  1. 一家模拟**零售供应链**企业的够复杂数据（非 demo、含 corner case；MVP 先做 1 条端到端流程：下单→履约→库存→发货→取消/退款）；
  2. 一个可运行的本体（对象/链接/动作，Pydantic + 显式注册表表达）；
  3. **LLM 经语义接口执行动作并写回源系统**：源记录真的变、规则校验生效、全程审计——通过"三问测试"（能取消订单吗？源记录真变了吗？已发货的会被拦吗？）；
  4. 方法论白皮书随闭环长出（不预先空写）；
  5. learn in public：随做随沉淀表达素材（③表达/分发贯穿始终）。

## 技术栈与项目结构（六层架构 v0.3，Jack 已确认 2026-08-14）

### 六层架构
| 层 | 职责 | MVP 选型 | 发布期演进 |
|---|---|---|---|
| ① 前端 UX | 漂亮的用户界面（本体驱动 UI） | React 18 + TypeScript + Vite + Ant Design | 同 |
| ② LLM/Agent | 意图理解→决策→调动作 | OpenAI 兼容 SDK，provider 热插拔（MVP=DeepSeek） | + MCP 类传输层（现成） |
| ③ 语义接口 API | 对象/链接/动作标准接口 | FastAPI + schema 元数据 | + 权限/治理 |
| ④ 本体运行时 | 索引/查询/写回回路/审计（**自研**，研究本身） | Python 自研 | 同（规模演进） |
| ⑤ 数据/源系统 | 模拟数据 + **独立源系统库** | SQLite（双库） | PostgreSQL |
| ⑥ 部署 | 本地可跑、可演示 | Docker Compose | GitHub/Gitee + 文档站 + 演示环境 |

### 五个关键设计决策
1. **本体运行时自研，其余全用现成**：对象注册/索引/查询/动作执行/审计/冲突消解自研（这是研究本身）；LLM/前端/传输全用成熟方案。
2. **本体驱动 UI**：界面由 schema 元数据自动生成（对象列表/详情/链接导航/动作表单），不硬编码业务页面；改 schema 界面跟着变。
3. **写回真实可验证**：独立"源系统"库，动作真的改源库记录（三问测试/E2E 在此验证）。
4. **LLM provider 热插拔**：MVP 接 DeepSeek（国内/便宜/OpenAI 兼容），可切通义/智谱/OpenAI；key 只放环境变量，不进代码。
5. **MVP 裁剪**：零售供应链 1 条端到端流程；分支/场景/权限矩阵发布期做，架构预留。
6. **RDFlib 不引入 MVP**（D-T2 已拍板 2026-08-14）：本体表达用 Pydantic + 显式注册表；"操作型本体 vs 描述型本体（RDF/OWL）"作为方法论论点，发布期如需 RDF 导出再引入。

### 目录结构
```
OntoRun/
├── AGENTS.md            # 本文件（规则）
├── 方向与战略_v0.2.md    # 方向宪法
├── research/            # 调研材料（palantir-ontology.md 等）
├── docs/                # 方法论白皮书（随落地长出）
├── src/
│   ├── ontology/        # 对象/链接/动作定义 + schema 注册（Pydantic）
│   ├── runtime/         # 本体运行时：索引/查询/写回/审计（自研）
│   ├── api/             # FastAPI：语义接口（对象/链接/动作）
│   ├── agent/           # LLM 接入（provider 热插拔，MVP=DeepSeek）
│   └── app/             # 演示入口（挂载 api + 静态前端）
├── web/                 # 前端：React 18 + TS + Vite + AntD（本体驱动 UI）
├── data/                # 模拟零售供应链数据 + 源系统库（SQLite 双库）
├── tests/               # pytest（后端）+ vitest（前端）
└── site/                # 网站静态源（发布阶段）
```

## 常用命令（可执行）
- 初始化仓库：`git init`（首件事；单一事实来源）
- 安装后端依赖（用 uv）：`uv pip install -r requirements.txt`（国内源 `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`）
- 安装前端依赖：`cd web && npm install --registry=https://registry.npmmirror.com`
- 后端测试：`pytest -v tests/`
- 前端测试：`cd web && npm run test`
- Lint：`ruff check . && ruff format .`；前端 `cd web && npm run lint`
- 类型检查：`mypy src/`；前端 `cd web && tsc --noEmit`
- 启动后端：`uvicorn src.app.main:app --reload`
- 启动前端：`cd web && npm run dev`
- 一键演示：`docker compose up`

## 编码规范
- 语言：中文沟通，代码/命令/变量用英文。
- 代码风格：数据不可变（更新返回新对象）；小文件 200–400 行（≤800）；函数 <50 行；无 4 层以上嵌套；无硬编码值（用常量/配置）。
- 风格示例（本体对象定义）：
```python
from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: str = Field(..., description="全局唯一客户号")
    name: str
    segment: str  # 枚举：retail / sme / corporate
    risk_level: str = "low"
```

## 测试（分阶段 · 当前=零到一档，P6 全链路绿后切稳定档）
- **核心不变量（必须全绿）**：三问测试 E2E（写回回路：LLM->动作->源系统变更->审计落库）+ 每阶段主路径冒烟。
- **核心算法模块 TDD**（测试即规格）：E2 映射四技法 / E3 七道校验 / E4 状态机 / DAG 引擎。
- **脚手架/CRUD/路由**：smoke 级（端点通、状态流转对），不写逐字段单测，不凑覆盖率。
- **反馈回路**：日常 = 增量测试（pytest tests/test_builder_pX.py -q，秒级）+ ruff；全量 pytest 每阶段末由 Rose 跑一次，不进子代理循环。 **子代理禁止跑全量 pytest（全量仅 Rose 在阶段末跑一次）；bash 长命令必须显式设 timeoutMs（默认 60s 会截断 3 分钟级测试造成反复重跑）。**
- **覆盖率 80% 挂起**：P6 收口时只对 mapping/extraction/pipeline/logic 四模块核算。
- **独立 red-team**：仅 P6 终审一次（额度硬约束下审查边际价值低于主线推进；核心算法靠测试即规格兜底）。
- 测试失败修实现，不修测试（除非测试本身错）。

## LLM 调用与限流纪律
- 优先使用已付费套餐内模型（当前=火山 Coding Plan Pro），以省费用为目的；自费 API（plan 外 provider）仅兜底，启用前告知 Jack。
- 子代理并发 ≤2 个长任务（长任务 = 预计 >10 分钟或多轮工具调用的编码/审查任务）；交付即收尾，不让 continuable 长挂（idle 占配额窗口）。
- 429 应对顺序：① 并发控制（治本）-> ② 退避等待（DSH retryPolicy 长退避，见 ~/.dsh/settings.yaml）-> ③ 套餐内换模型（试验性，账户级限流下不保证有效）-> ④ plan 外 provider（最后手段）。

## Git 工作流
- commit 用英文 conventional commits：feat/fix/refactor/docs/test/chore/perf/ci。
- 本地 git = 单一事实来源；远端/GitHub/Gitee 发布须 Jack 确认（发布阶段定）。

## 边界（三档）
- ✅ 总是：先理解/复现再动手；改完跑验证并如实报告；每个动作留可验收产物；随手沉淀 learn-in-public 素材。
- ⚠️ 先问：加依赖；改本体 schema（对象/链接/动作定义）；删除文件/数据；对外发布（GitHub/公众号/小红书）；引入新 LLM 提供商；涉及 Jack 时间投入的安排。
- 🚫 绝不：密钥/凭据进代码；编造验证结果；自评"定稿"（须独立 red-team 审查）；重复造轮子（传输/操作层）；偏离研究对象（滑向"MCP 教程"或"概念科普"）；未确认 AGENTS.md 就派活。

## 安全要求
- 密钥/token/密码绝不进代码，只用环境变量或密钥管理。
- LLM 输出视为不可信输入：动作参数必须校验（类型/枚举/边界），防注入（prompt injection、动作参数注入）。
- 动作执行要有权限边界与审计日志；错误信息不泄漏敏感数据。
- 发现安全问题立即停、先指出、再继续。

## 验收标准
- 零到一档（当前）：核心不变量全绿 + lint 通过；阶段末全量 pytest 零回归。
- 稳定档（P6 后）：test/lint/build 全通过才算完成。
- 交付 = 能跑的真实产物 + 真实执行结果；被阻断诚实说明并给替代方案。
- 第一里程碑验收 = 三问测试通过 + E2E 测试全绿 + 方法论白皮书有内容随闭环产出。

## 项目特有约定（反模式复盘直接引用）
1. **研究对象锚定**：每个交付物必须能回答"这跟语义接口/本体论落地有什么关系"（防目标漂移）。
2. **内容密度 > 文件数量**：宁要一篇讲透，不要一堆脚手架。
3. **独立对抗审查**：交付物定稿前由独立 red-team 子代理审查，不接受同 agent 自评。
4. **落地先行**：先跑通最小闭环，方法论从里面长出来；禁止先写方法论再落地。
5. **单一事实来源** = 本地 git + 本目录文件；不依赖外部网盘同步。
6. **待定项未定不派活**：行业已定=零售供应链（MVP 1 条端到端流程）；剩余待定（动作清单、LLM 实测配置等）Jack 拍板前不派编码活。

## 团队派活映射（规则确认后才启用）
- 架构：本体运行时架构、技术选型、方案评审
- 数据：模拟企业数据、本体建模、写回/源系统设计
- AI：LLM 接入、语义接口、动作执行
- 后端：FastAPI 服务、运行时实现
- 测试：E2E 测试、验收把关
- 产品：表达/分发素材、UX（后续阶段）
