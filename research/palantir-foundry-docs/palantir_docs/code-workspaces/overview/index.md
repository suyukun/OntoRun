来源: https://palantir.com/docs/zh/foundry/code-workspaces/overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

Code Workspaces 将 JupyterLab®、RStudio® Workbench 和 VS Code 第三方 IDE 引入 Palantir Foundry，帮助用户通过在 Foundry Ontology 的高质量数据上使用他们喜爱的工具来提高生产力并加速他们的数据科学和统计工作流程。Code Workspaces 容器与 Foundry 生态系统的其他部分本地集成，将熟悉的 IDE 与 Foundry 平台的优势结合起来，例如数据安全性、分支、搭建调度和资源管理。

Code Workspaces 为平台管理员提供了一种易于部署、全面管理、安全且面向生产的方式，以提供 JupyterLab®、RStudio® Workbench 和 VS Code 给用户，并且内置了 Foundry 的数据治理和对 FedRAMP、GxP 以及其他标准的合规性。通过 Code Workspaces，用户可以安全地连接到现有内部系统，并在具有 Foundry 访问控制和数据权限的数据上搭建分析、变换、模型、应用程序或整个工作流程。

## 主要功能

Code Workspaces 的主要功能包括：

- 安全性：Code Workspaces 构建于支持整个平台的Foundry 安全性核心组件之上，例如强大的权限和细粒度的访问控制。这为 Code Workspaces 中可用的第三方 IDE 提供了 Foundry 的安全模型。例如，限制 Foundry 中数据集的访问也将限制 Code Workspaces IDE 的访问，确保工具间的一致权限。
- 可定制环境：Code Workspaces 允许用户定义自定义环境配置文件，并根据需要增加或减少其工作空间的计算资源。
- Git 工作流支持：Code Workspaces 由代码库基础设施支持，提供行业标准的版本控制功能，如分支、合并和提交历史。这些功能使得多个用户更容易和安全地在同一工作空间中操作。
- 应用程序：Code Workspaces 目前支持用于 Python 应用的Dash ↗和Streamlit ↗，以及用于 R 应用的Shiny® ↗。用户可以直接在 Code Workspaces 中使用 Foundry 的版本控制、分支和数据治理功能来创建应用程序工作流程。
- 模型集成（测试版）：用户可以在 Code Workspace 中创建模型资产并通过建模目标跟踪这些资产。可以从同一工作空间创建多个模型。
- 变换/搭建集成（实验性）：Code Workspaces 作为变换的开发环境。Code Workspaces 中编写的逻辑可以发布为数据变换管道，并与 Foundry 的数据集成工具包无缝集成，包括搭建、调度、数据沿袭和健康检查。我们支持 R 变换和 Python/Jupyter® 变换。
## 何时使用 Code Workspaces

Foundry 提供多种应用程序，您可以用于分析或编码目的。例如，如果您是一名分析师，您可能更适合使用 Contour，Foundry 的点选式低代码界面用于数据集分析。

如果您需要编写大规模数据管道、设置数据连接或处理流数据，其他 Foundry 工具比 Code Workspaces 功能更强大；对于这些应用案例，我们建议使用Pipeline Builder、数据连接和Foundry Streaming。

具体而言，Code Workspaces 在单个节点上运行，而其他 Foundry 应用程序利用 Spark 基础设施。因此，我们建议进行大规模数据变换的用户选择Pipeline Builder或代码库而不是 Code Workspaces。

Code Workspaces 适合搭建机器学习模型或熟悉在 JupyterLab® 或 RStudio® Workbench 中工作的用户。

## 了解更多

Code Workspaces 目前支持三种环境：JupyterLab®、RStudio®和VS Code

关于 Code Workspaces 的更多信息可以在常见问题解答中找到。

通过此教程开始使用 Code Workspaces。

RStudio® 和 Shiny® 是 Posit™ 的商标。

Jupyter®、JupyterLab® 和 Jupyter® 徽标是 NumFOCUS 的商标或注册商标。

所有引用的第三方商标（包括徽标和图标）仍然是其各自所有者的财产。不暗示任何附属关系或认可。
