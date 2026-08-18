# OntoRun

研究「大模型如何嵌入真实业务系统」的机制——**聚焦语义接口层，本体论（ontology）为方法核心**。

> 一句话：把现实世界的语义层（对象、关系、业务规则、治理边界）做成大模型与系统之间的**语义接口**，让 LLM 经语义接口**执行受治理的动作并真实写回源系统**——不是新发明（Palantir Foundry Ontology 是国际标杆），本项目把这套机制用**最小可复现的闭环落地并公开证据链**。

## 第一里程碑（已达成）：最小语义接口闭环

- **模拟零售供应链数据**（下单→履约→库存→发货→取消/退款，含 corner case）
- **可运行本体**：对象/链接/动作，Pydantic + 显式注册表
- **写回回路**：LLM → 语义接口 → 动作 → 源系统真变更 + 规则校验 + 全链路审计
- **三问测试**：能取消订单吗？源记录真变了吗？已发货的会被拦吗？——全部通过
- 测试：187 后端 + 23 前端全绿（pytest + vitest）

## 六层架构

| 层 | 职责 | MVP 选型 |
|---|---|---|
| ① 前端 UX | 本体驱动 UI（改 schema 界面跟着变） | React 18 + TS + Vite + AntD |
| ② LLM/Agent | 意图理解→决策→调动作 | OpenAI 兼容 SDK（MVP=DeepSeek，热插拔） |
| ③ 语义接口 API | 对象/链接/动作标准接口 | FastAPI + schema 元数据 |
| ④ 本体运行时 | 索引/查询/写回回路/审计（自研） | Python |
| ⑤ 数据/源系统 | 模拟数据 + 独立源系统库 | SQLite（双库：源系统库 + 写回库） |
| ⑥ 部署 | 本地可跑、可演示 | Docker Compose（发布期） |

## 目录结构

```
OntoRun/
├── AGENTS.md              # 项目规则
├── 方向与战略_v0.2.md       # 方向宪法
├── research/             # 调研（Palantir Ontology / B站笔记 / nano-ontoprompt / 官方文档库）
├── docs/                 # 白皮书 / 技术方案 / 演示脚本 / learn-in-public
├── src/                  # ontology / runtime / api / agent / app
├── web/                  # 前端（本体驱动 UI）
├── data/                 # 模拟数据 + 源系统库（SQLite 双库）
└── tests/                # pytest（后端）+ vitest（前端）
```

## 快速开始

```bash
# 后端测试
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pytest -v tests/

# 前端
cd web && npm install --registry=https://registry.npmmirror.com
npm run test

# 本地启动（演示）
uvicorn src.app.main:app --reload   # 后端 :8000
cd web && npm run dev              # 前端 :5173
```

> ⚠️ 密钥/API Key 只放环境变量，绝不入库（见 .gitignore）。

## 文档

- `docs/白皮书_v0.1.md` —— 方法论白皮书（随闭环长出）
- `docs/技术方案_v0.1.md` —— 六层架构技术方案
- `docs/演示脚本_v0.1.md` —— 5 分钟演示脚本
- `docs/learn-in-public_v0.1.md` —— 表达/分发素材
- `research/palantir-ontology.md` —— Palantir Ontology 一手调研
- `research/nano-ontoprompt-analysis.md` —— 开源轻量本体构建平台代码研究

## 状态

- 第一里程碑（最小语义接口闭环）✅ 达成并通过验收
- 下一步：对外发布 / 继续研发（见 docs/）

## License

MIT
