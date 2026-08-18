来源: https://palantir.com/docs/zh/foundry/app-building/overview/

# 应用案例开发

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 应用案例开发

Palantir平台旨在通过一系列强大的工具为多元化的构建者群体提供应用案例开发的支持，包括应用程序搭建工具、工作流搭建工具、集成的分析工具和开发者工具。每个工具都利用了Foundry核心的安全性、数据沿袭、数据和计算原语，让团队专注于提供操作功能，而不是管理基础设施。关键是，Palantir平台中的每个工具都被设计为能够持续、安全地丰富一组一致的数据和模型资产（包含在Ontology中）。这使得知识能够在企业范围内的操作工作流扩展时复合增长。

## 应用程序搭建

Palantir平台中的主要应用程序搭建工具是Workshop和Slate。

### Workshop

Workshop是一个灵活的面向对象的应用程序搭建工具。Workshop利用了Ontology中的语义原语（如对象、链接）和动能原语（如操作、函数），以实现高度互动的桌面和移动应用程序的快速交付。在Workshop中的应用程序搭建体验使用户能够通过无代码、低代码和基于代码的微件创建强大的应用程序。无需技术专长即可开始使用微件，并将对象、链接和操作编织成用户驱动的工作流，远远超越了仪表盘或被动可视化。同时，基于代码的函数丰富可以无缝嵌入Workshop微件中，以允许复杂的交互、级联过程和复杂的数据捕获。

了解更多关于Workshop的信息。

### Slate

Slate为构建者提供了一套灵活的工具，以快速创建操作应用程序和互动仪表盘。Slate使应用程序开发人员能够通过拖放界面构建动态和响应式应用程序，从而减少开发时间和成本。Slate包含与Foundry Ontology无缝集成的功能，同时也允许开发人员使用HTML、CSS和JavaScript完全自定义应用程序。通过定制的Slate应用程序，组织各级的利益相关者可以快速探索和理解他们的数据，以便做出更明智的决策。

了解更多关于Slate的信息。

## 工作流搭建

Palantir平台中的主要工作流搭建工具是Workflow Lineage、Automate、Solution Designer和Use Cases。

### Workflow lineage

Workflow Lineage处于测试阶段，功能可能在产品正式发布前更改。Workflow Lineage可能在所有注册中不可用。

Workflow Lineage为构建AI应用、操作和代理提供了一个互动工作空间。Workflow Lineage使您能够将LLMs集成到您的管道中并大规模运行它们，包含错误处理、自动重试、保证输出模式和其他生产级工具。Workflow Lineage还帮助您构建、测试和发布功能丰富的、AI驱动的函数，这些函数利用您应用中的Ontology。

### Automate

Automate为您提供了一个设置和执行平台中所有业务自动化的单一入口。Automate应用程序允许用户定义条件和效果；条件被连续检查，当指定条件满足时，效果会自动执行。

了解更多关于Automate的信息。

### Carbon

Carbon能够为特定用户组配置定制的平台体验，称为工作空间。Carbon可以为需要执行关键操作工作流的技术水平较低的用户提供专注的体验。每个Carbon工作空间都是应用程序和资源的精选集合，可以配置以优化给定的操作、终端用户工作流。例如，一个飞机零件维护工作空间可能由一个包含动态更新的需要维护的零件列表的Workshop应用程序组成，伴随Ontology驱动的操作以分类每个零件；另一个用于调查每个零件维护问题的应用程序；以及一个Quiver分析显示随着时间推移的维护趋势。Carbon允许Foundry应用程序和分析功能的丰富组合被集成到专注的操作体验中。

了解更多关于Carbon的信息。

### Solution Designer

Solution Designer是一个互动工具，用于创建使用Palantir平台构建的解决方案的架构表示，包括一方和第三方集成点的表示、平台资源的链接、按需访问文档和最佳实践等。

了解更多关于Solution Designer的信息。

### Use Cases

Use Cases应用程序允许构建者在单一操作界面内组织他们的工作。通过将文件系统视图与本体管理视图相结合，开发人员可以访问专注于其负责工作的精选视图。

了解更多关于Use Cases应用程序的信息。

## 开发者工具链

Palantir开发者工具链使您能够使用您自己的工具在Palantir平台之上构建您自己的应用程序。Palantir开发者工具链的核心是Ontology SDK (OSDK)。

### Ontology SDK

Ontology SDK允许您直接从开发环境访问Ontology的全部功能。您可以使用开发者控制台生成一个Ontology特定的SDK。Ontology SDK可以作为TypeScript的NPM（Node Package Manager）包，或作为Python的Pip或Conda创建，并且仅包含您Ontology的预选子集。SDK允许您访问对象类型、应用操作以更新Ontology中的数据、调用函数以及运行AIP启用注册的AIP逻辑函数。开发者控制台还包括为您的应用选择的实体提供的Ontology特定文档。应用程序使用OAuth流程作为公共或保密客户端访问数据。

了解更多关于Ontology SDK的信息。

### APIs

关于Palantir API的信息可以在API文档中找到。
