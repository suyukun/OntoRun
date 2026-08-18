来源: https://palantir.com/docs/zh/foundry/model-integration/what-to-use/

# 选择合适的建模工具

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 选择合适的建模工具

Palantir 的建模产品套件使用户能够开发、管理和运营模型。本页面比较了不同的产品，帮助您选择适合您需求的工具。

## 特征工程

| 产品 | 详情 |
| --- | --- |
| Pipeline Builder | 大规模的点击式数据变换 |
| Code Workspaces | 在熟悉的环境中进行交互式、高级代码的数据分析和变换，如 JupyterLab® |
| Python Transforms | 在 Foundry 的基于网页的 IDE 中进行 PySpark 数据管道开发，Code Repositories |

## 模型训练

### 可用库

foundry_ml库和数据集支持的模型已进入其终止期，计划于Python 3.9 退役的同时在 2025 年 10 月被弃用和移除。

palantir_models库提供了在 Palantir 平台内发布和使用模型的灵活工具，使用model adapters的概念。

| 库 | 详情 |
| --- | --- |
| palantir_models | 通过Model Adapters在 Foundry 中发布和使用模型的灵活库；支持平台内生产的模型、外部模型和容器化模型 |
| foundry_ml | 计划于2025 年 10 月被移除的遗留模型开发库；除非绝对必要，否则应使用palantir_models代替foundry_ml |

### 代码编写环境

| 产品 | 库支持 | 详情 |
| --- | --- | --- |
| Code Workspaces | palantir_models | 在 Jupyter® notebooks 中进行交互式模型开发 |
| Code Repositories | palantir_models，foundry_ml（直到弃用） | 强大的基于网页的 IDE，具有原生 CI/CD 特性和对建模工作流程的支持；比 notebooks 交互性稍弱 |
| Code Workbooks | foundry_ml | Code Workbooks 中的建模支持仅限于foundry_ml模型，这些模型计划于2025 年 10 月被弃用 |

## 批量推理

模型可用于运行跨数据集的大规模批量推理管道。

| 产品 | 详情 | 注意事项 |
| --- | --- | --- |
| Modeling objectivebatch deployments | 可以从 Modeling Objectives 设置批量推理，提供更广泛的模型管理功能，如模型发布管理、升级、评估等 | 不支持多输出模型 |
| Python transforms | 可以直接在 Python transforms 中运行批量推理 | N/A |

## 模型部署

模型可以在 Foundry 中部署在 REST API 后面；部署模型将模型运营化，以供 Foundry 内外使用。

| 产品 | 详情 |
| --- | --- |
| Model direct deployments | 自动升级的模型部署；最适合快速迭代和部署 |
| Modeling objectivelive deployments | 生产级建模项目管理；Modeling Objectives 提供模型发布管理、升级、评估等工具 |

了解直接部署和通过 Modeling Objectives 部署之间的区别。

## 函数集成

将模型发布为函数可使模型用于下游应用程序，包括Workshop，Slate，Actions和更多。

| 产品 | 最适合 |
| --- | --- |
| Direct publish functions | 无代码函数创建 |
| Functions on Models | 使用 Typescript 函数运营化模型，允许与 Ontology 更深度的集成 |
