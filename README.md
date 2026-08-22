# OntoRun

研究「大模型如何嵌入真实业务系统」的机制——**聚焦语义接口层，本体论（ontology）为方法核心**。

> 一句话：把现实世界的语义层（对象、关系、业务规则、治理边界）做成大模型与系统之间的**语义接口**，让 LLM 经语义接口**执行受治理的动作并真实写回源系统**——不是新发明（Palantir Foundry Ontology 是国际标杆），本项目把这套机制用**最小可复现的闭环落地并公开证据链**。

## 成果状态

**M1 最小语义接口闭环（S1，tag v0.1.0）✅**

- **模拟零售供应链数据**（下单→履约→库存→发货→取消/退款，含 corner case）
- **可运行本体**：对象/链接/动作，Pydantic + 显式注册表
- **写回回路**：LLM → 语义接口 → 动作 → 源系统真变更 + 规则校验 + 全链路审计
- **三问测试**：能取消订单吗？源记录真变了吗？已发货的会被拦吗？——全部通过

**M2-M4 玩具→生产跨越（S2，tag v0.2.0）✅**

- **DES 企业样例**：模拟制造业零售供应链（18 表 5 系统 100 万行，含一物多码等 corner case）
- **ChatBI 混合闭环**：head-to-head 实证——受限结构化查询 60% 首超 NL2SQL，可表达集 ~85-90%（白皮书 v2 有完整实验报告）
- **映射治理**：62 条 GT recall@5=1.0 + 审核/校准/影响分析闭环
- **治理骨架**：操作权限门（越权 0）+ 会话持久化（重启不丢）+ 审计 WORM 链
- **方法论**：OSLM + 语义落地六步法（OSL-6）白皮书 v2，每步链到真实运行证据
- 全量测试 **645 passed / 2 skipped / 0 failed**（分层：全量仅阶段末/CI 跑，日常跑增量）

## 六层架构

| 层 | 职责 | 选型 |
|---|---|---|
| ① 前端 UX | 本体驱动 UI（改 schema 界面跟着变） | React + TS + Vite + AntD |
| ② LLM/Agent | 意图理解→决策→调动作 | OpenAI 兼容 SDK（DeepSeek，provider 热插拔） |
| ③ 语义接口 API | 对象/链接/动作标准接口 | FastAPI + schema 元数据 |
| ④ 本体运行时 | 索引/查询/写回回路/审计（自研） | Python |
| ⑤ 数据/源系统 | 模拟数据 + 独立源系统库 | SQLite 双库 + DuckDB 物化（发布期 PostgreSQL） |
| ⑥ 部署 | 本地可跑、可演示 | Docker Compose（发布期）+ CI |

## 目录结构

```
OntoRun/
├── src/                  # ontology / runtime / api / agent / app / builder / des
├── web/                  # 前端（本体驱动 UI + 方法论指针页）
├── data/                 # 模拟数据 + 源系统库（SQLite 双库，*.db 不入库可再生）
├── tests/                # pytest（后端，645 用例）
├── docs/                 # 白皮书 / 设计稿 / 实验报告 / 完成记录
├── research/             # 一手调研（Palantir Ontology 等）
├── scripts/              # start_dev.sh 一键起服务
└── .github/workflows/    # CI（lint + 全量 pytest + vitest）
```

## 快速开始

```bash
# 一键起服务（后端 :8000 + 前端 :5173，需 DEEPSEEK_API_KEY）
bash scripts/start_dev.sh

# 后端测试（增量，秒级）
python -m pytest tests/test_builder_pX.py -q

# 前端测试
cd web && npm run test
```

> ⚠️ 密钥/API Key 只放环境变量，绝不入库（见 .gitignore）。

## 文档

- `docs/白皮书_v2.md` —— 方法论白皮书 v2（OSLM / OSL-6 六步法，10 铁律 + 15 反模式 + 10 张力点，全部链到真实运行证据）
- `docs/P2-headtohead-实验报告v3.md` —— ChatBI head-to-head 实证（B 60% vs A，混合形态成立）
- `docs/S2-收口记录.md` —— S2 九阶段收口记录
- `docs/技术方案_v0.1.md` —— 六层架构技术方案
- `docs/learn-in-public_v0.1.md` —— learn in public 素材
- `web/public/methodology.html` —— 方法论指针 UI（OSL-6 每步链到真实运行/git commit）

## License

MIT
