来源: https://palantir.com/docs/zh/foundry/pipeline-builder/core-concepts/

# 核心概念

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 核心概念

本页介绍了与Pipeline Builder相关的Foundry数据集成的核心概念。

## 搭建

数据集、分支、变换和输出的概念是Pipeline Builder的基础。我们建议在搭建第一个pipeline以及变换数据和集成至pipeline输出时先查看这些主题。

### 数据集

数据集是一个pipeline的构建模块。在数据集成过程中，从数据进入Foundry到数据被映射到Ontology对象模型时，数据被表示为Foundry数据集。

从根本上说，一个Foundry数据集是围绕存储在后备文件系统中的文件集合的一个封装。Pipeline Builder主要用于结构化数据，但也可以用于半结构化数据。

了解更多关于Pipeline Builder中输入数据集的信息。

### 分支

版本控制对维护健康的pipeline工作流程至关重要。在Pipeline Builder中，版本控制通过pipeline分支实现，其运作方式类似于Git版本控制中的代码分支。

pipeline分支是pipeline的一个副本，用户可以在其上进行迭代而无需保存回主pipeline，类似于Git中的代码分支。用户可以更改、预览、保存并在其分支上搭建。一旦他们对更改满意，就可以提议合并回主分支，类似于合并Git拉取请求。

了解更多关于Pipeline Builder中的分支的信息。

### 变换

变换可以被视为一个函数定义；即变换接受一组输入（如数据集）并产生一组输出。pipeline是由数据集、数据期望和通过变换连接的目标数据输出组成的链接。

了解更多关于Pipeline Builder中的变换的信息。

### Pipeline输出

Pipeline Builder中的输出是pipeline中执行的变换结果，可以是数据集或Ontology组件，如对象类型、对象链接类型或时间序列。输出可以用于其他Foundry应用程序，如Quiver或Code Workbook。

了解更多关于Pipeline Builder中的pipeline输出的信息。

## 管理

计划和数据期望的概念对于维护健康、稳定的pipeline非常有用。我们建议在搭建第一个pipeline后学习更多关于这些主题的知识。

### 计划

计划被用于在Foundry中以递归的方式运行数据集搭建，以保持数据持续流动。在Pipeline Builder中，可以在特定时间、特定节奏或基于父资源的状态安排搭建；例如，您可以设置在上游数据集更新时进行搭建。

了解更多关于Pipeline Builder中的计划的信息。

### 数据期望

Pipeline Builder通过单元测试支持对输出和中间变换的数据期望。数据期望是可以应用于数据集输出的要求。这些要求（称为“期望”）可用于创建检查以提高数据pipeline的稳定性。

可以在每个pipeline输出上设置数据期望，以定义对结果输出的期望。Pipeline Builder目前支持两种数据期望类型：主键和行数。

如果任何期望出错，搭建将会失败。任务期望面板将显示哪些数据期望通过和失败。

了解更多关于Pipeline Builder中的数据期望的信息。
