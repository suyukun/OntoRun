来源: https://palantir.com/docs/zh/foundry/quiver/objects-overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

Object类型是Ontology的核心元素。Objects代表组织数字孪生中的特定实体或事件。

有多种方法可以将Objects或对象集添加到Quiver分析中：

- 通过搜索栏直接从Ontology中添加对象集或Object。
- 导入已保存的对象集（例如，从另一个Quiver分析或从Object Explorer中保存的对象集）。
- 导入给定类型的所有Objects，这些Objects与分析中的现有Object或对象集相关联。
添加到Quiver分析中的对象集可以通过图表和表格进行筛选、合并和可视化。

Quiver使您能够对对象集进行一系列操作，例如合并关联的Objects、筛选Objects，或对两个对象集进行交集或并集。您还可以使用Quiver的图表和表格库来可视化对象集。

此外，Quiver支持对Object属性进行变换。可以将单个Object的属性提取到指标卡片中进行可视化，或用作其他卡片的输入。对象集的属性值也可以进行聚合；例如，创建数值聚合或唯一值数组。

在Objects上进行高级变换，例如批量分析或派生属性，可以通过使用变换表来实现。

在Quiver中基于Objects的变换在执行关联Objects操作时，起始集限制为最多100,000个Objects，并在数据透视表中限制为最多1,000个桶。
