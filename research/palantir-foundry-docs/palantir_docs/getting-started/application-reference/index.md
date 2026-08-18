来源: https://palantir.com/docs/zh/foundry/getting-started/application-reference/

# 应用程序参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 应用程序参考

您可以通过侧边栏上可访问的应用程序与Palantir平台互动。本页面提供了可用应用程序的参考，并描述了何时可能需要使用每个应用程序。

## 数据集成

| 应用程序 | 描述 | 用途 |
| --- | --- | --- |
| Data Lineage | Data Lineage显示了数据在平台中流动的图形。 | 探索Palantir平台中任何数据的来源或下游使用。 |
| Pipeline Builder | Pipeline Builder使用内置的数据变换创建从数据源到最终输出的端到端管道。 | 通过批量和流式管道集成数据以进行分析和应用程序搭建。 |
| Code Repositories[1] [2] | Code Repositories是一个基于网络的代码创作环境，支持版本控制和协作。 | 在Ontology中创建数据管道或编写函数。 |
| Dataset Preview | Dataset Preview显示数据集的内容和历史。 | 浏览数据集，了解其历史和其他元数据。 |
| Data Health | Data Health让您定义健康检查以确保数据集的高质量。 | 添加或监控数据集的健康检查。 |
| Data Connection | Data Connection允许您连接到数据源并将数据同步到Palantir平台。 | 连接到组织数据源或将新数据集同步到Palantir平台。 |
| HyperAuto (SDDI) | HyperAuto在常见ERP系统之上生成端到端数据管道。 | 从企业系统生成Ontology，而无需手动开发管道。 |

[1] Code Workbook或Code Workspaces可能更适合某些数据科学工作流。了解更多关于Code Workbook、Code Workspaces和Code Repositories的区别。[2] 对与技术背景较少的用户，Pipeline Builder可能更适合。

## 模型集成

| 应用程序 | 描述 | 用途 |
| --- | --- | --- |
| Model Assets | Model Assets支持将多种不同类型的模型集成到Palantir平台中。 | 训练模型，并在Palantir平台中连接到外部托管的模型。 |
| Modeling objectives | 一个建模目标允许组织利益相关者和模型开发人员协作和部署机器学习模型。 | 提交模型；讨论建模目标，并将模型部署到生产环境中。 |

## Ontology

| 应用程序 | 描述 | 用途 |
| --- | --- | --- |
| Ontology Manager | Ontology Manager使您能够定义组织的Ontology。 | 创建新的Object、链接和操作类型。 |
| Object Views | Object Views表示显示Object类型的规范方式。 | 定义可以跨应用案例使用的用户界面。 |
| Object Explorer | Object Explorer允许您搜索和可视化您的Ontology。 | 在Ontology中搜索和分析对象和链接。 |
| Vertex | Vertex使您能够探索对象关系并运行模拟。 | 创建相关对象的系统图，并使用模型运行端到端模拟。 |
| Automate | Automate允许终端用户和应用程序搭建者查看Palantir Ontology中的数据何时发生变化。 | 配置自动化以在满足特定条件时发送通知或提交操作。 |
| Foundry Rules | Foundry Rules使用户能够在平台中主动管理复杂的业务逻辑。 | 为各种应用案例创建并应用规则到数据集、对象和时间序列。 |
| Map | Map提供强大的地理空间和时间分析与可视化能力。 | 将平台中的数据集成到一个连贯的地理空间体验中。 |

## 应用程序搭建

| 应用程序 | 描述 | 用途 |
| --- | --- | --- |
| Workshop[1] | Workshop使终端用户能够创建互动和高质量的应用程序。 | 使用Ontology中的数据在一个快速、点选界面中创建应用程序。 |
| Slate[2] | Slate是一个可扩展的应用程序开发框架。 | 使用HTML、CSS和JavaScript创建定制应用程序。 |
| Carbon | Carbon让您可以结合平台中的应用程序和其他资源，为终端用户创建精选工作空间。 | 为终端用户提供结合多个应用程序或仪表盘的应用案例。 |

[1] 如果您的应用程序需要大量定制，Slate可能更合适。[2] 对于低到中等复杂度的应用程序，Workshop更合适，并且通常在时间上维护成本较低。

## 分析

了解更多关于平台中的分析应用程序和可用的分析类型。

| 应用程序 | 描述 | 用途 |
| --- | --- | --- |
| Contour[1] | Contour在数据集上实现高规模、自上而下的分析。 | 以点选方式分析表格数据。 |
| Quiver[2] | Quiver实现对Object数据和时间序列的分析。 | 以点选方式分析Ontology数据和时间序列。 |
| Code Workbook[3] | Code Workbook是一个基于网络的代码分析环境。 | 通过代码分析数据集，进行数据科学工作流或开发模型。 |
| Code Workspaces[3] | Code Workspaces将JupyterLab®和RStudio® Workbench第三方IDE引入Palantir。 | 使用高质量的Palantir Ontology数据，通过首选工具提高生产力并加速数据科学和统计工作流。 |
| Notepad | Notepad允许创建时点文档以呈现数据供他人分享。 | 展示分析工作流中的见解。 |
| Fusion | Fusion是Palantir平台的电子表格应用程序。 | 将可编辑电子表格中的数据同步到数据集中。 |

[1] 对于某些工作流，Quiver可能更合适。了解更多.[2] 对于某些工作流，Contour可能更合适。了解更多.[3] Code Repositories和Pipeline Builder推荐用于开发生产数据管道。了解更多关于Pipeline Builder和Code Workbook、Code Workspaces和Code Repositories的区别。
