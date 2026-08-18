# Palantir Foundry 官方中文文档库 导读

> 归档日期：2026-08-18 ｜ 来源：Jack 爬取 palantir.com/docs/zh/foundry/（1709 页，0 错误）
> 原始 zip：/Users/suyukun/Downloads/palantir_foundry_docs.zip ｜ 本库：research/palantir-foundry-docs/（已 commit b7baecd）
> 用途：本项目背景知识参考库。全文为 AIP 机器翻译（每页开头标注），个别术语翻译不准时对照原文链接。

---

## 1. 库概况

- 规模：1709 个页面 / 71 个模块 / 解压后约 11MB；每页是独立 Markdown，顶部带原文 URL 可溯源
- 索引：palantir_docs/README_INDEX.md（全量列表，按模块排序）
- 检索建议：cd research/palantir-foundry-docs/palantir_docs && grep -rl '关键词' --include=index.md .

## 2. 爬取盲区（重要，如实标注）

**本次爬取不含独立的 ontology 核心模块**——即 docs/zh/foundry/ontology/** 下的对象类型(Object Type)、链接类型(Link Type)、动作类型(Action Type)、Actions 服务、Ontology Manager 等核心页面不在 1709 页内（71 个模块列表里没有 ontology/）。
本体核心内容由以下材料补位：
1. research/palantir-ontology.md（Palantir 官方 Ontology 一手调研，2026-08-14）
2. research/palantir-bilibili-notes.md（B站「零点未来」8 集笔记，EP04/05/07 覆盖对象/链接/动作/五层架构）
3. research/nano-ontoprompt-analysis.md（开源轻量平台的动作执行实现）
若需要，可补爬 docs/zh/foundry/ontology/**（预计 ~150-200 页），待 Jack 定。

## 3. 重点目录导读（按 Jack 指定顺序）

| 模块 | 页数 | 与我们项目的关系 |
|---|---|---|
| ontology-sdk/ | 18 | **语义接口 API 层(③)的类型化客户端范式**：Developer Console 生成 SDK（TS/Python/Java/OpenAPI），强类型安全、词元权限仅限所授权本体实体（安全设计）——本体元数据→生成 SDK 的模式可借鉴到我们的 API 层 |
| platform-overview/ | 5 | **白皮书框架的官方佐证**：overview 页明确 Ontology=决策(数据/逻辑/操作三组件)，与我们白皮书"数据→逻辑→操作"分层同构 |
| code-workspaces/ | 12 | 与 Ontology 交互：JupyterLab/RStudio 里选 object/action 类型→生成 SDK 版本→导入。ontology/ 页是"本体元数据驱动代码生成"的直接案例 |
| workshop/ | 95 | **本体驱动 UI 的官方证据**：actions-use 页——"表单组件是基于操作定义自动生成的"，正印证我们设计决策 #2（改 schema 界面跟着变）。动作类型定义全流程：概览(API名/显示名/状态)→规则(改哪些属性)→表单(参数自动生成)→安全性和提交条件(正则条件模板)→保存 |
| pipeline-builder/ + building-pipelines/ | 50+40 | 数据转换链路（B站笔记 EP04 五阶段的数据侧）：Pipeline Builder、LLM 变换、转换步骤——我们双库中"清洗/映射"环节的工程参考 |
| data-connection/ + available-connectors/ | 29+191 | 连接器大全（文件/SQL/Mongo/REST/云厂商等），发布期多源演进与"从原系统拉原始数据不预处理"原则（可追溯合规）的参考 |
| pb-functions-expression/ | 301 | **Functions/表达式系统**：未来 Logic 层（B站笔记五层架构缺的那层）的函数/表达式语法参考，量大可按需查 |
| getting-started/ | 17 | 平台入门/角色/交付用例（delivering-a-use-case 页对"用例驱动落地"有方法论价值） |

## 4. 对我们项目最有用的 5 个落点

1. **workshop/actions-use → 本体驱动 UI + 动作类型定义流程**：直接给我们的"改 schema 界面跟着变"和"动作=参数/规则/提交条件"设计背书。白皮书可引用（标注 AIP 翻译）。
2. **platform-overview/overview → 数据/逻辑/操作三分法**：我们白皮书三层接口框架的官方同构，作方法论文撑。
3. **ontology-sdk → 语义接口 API 层演进**：Palantir 从本体生成类型化 SDK（S-1 里的 DS-SDK 落地形态），我们③层未来可参考"schema 元数据→生成客户端"。
4. **pb-functions-expression → Logic 层参考**：若做 Functions（业务函数封装），301 页表达式参考是最全的对照。
5. **data-connection/available-connectors → 发布期多源演进**：我们 MVP 是 SQLite 双库，发布期接多数据源时参考其连接器分类与增量同步。

## 5. 关键页面速查

- workshop/actions-use/index.md —— 操作类型定义全流程（本体驱动 UI 证据）
- platform-overview/overview/index.md —— Ontology=数据/逻辑/操作
- ontology-sdk/overview/index.md —— OSDK 概念与生成
- code-workspaces/ontology/index.md —— JupyterLab/RStudio 生成 OSDK
- getting-started/delivering-a-use-case/index.md —— 用例驱动交付方法论

---

*导读仅覆盖核心页；1709 页全量库按需 grep 检索。*
