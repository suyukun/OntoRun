来源: https://palantir.com/docs/zh/foundry/time-series/time-series-properties-use-case-ontology/

# 使用 Ontology Manager 为 Object 添加时间序列属性

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用 Ontology Manager 为 Object 添加时间序列属性

本指南参考了在时间序列 Object 类型上设置时间序列属性的文档。您可以根据需要向 Object 类型添加任意多的时间序列属性，假设每个 Object 始终会关联一个时间序列集合。请查阅我们的文档以了解选择时间序列 Object 类型或传感器 Object 类型的依据。

您必须为Route和AirportObject 类型重复以下步骤。在本指南结束时，Carrier、Route和AirportObject 类型将各有三个时间序列属性，分别为Daily Count of Flights、Daily Average Arrival Delay和Daily Average Departure Delay。

- 在 Ontology Manager 中导航到CarrierObject 类型，并选择Capabilities选项卡。
- 在Time series property部分中选择+ Add。
- 选择现有的Daily Count of Flights属性作为时间序列属性，然后选择Set as default time series property以便它在 Quiver 中自动出现。
- 选择您在Pipeline Builder中创建的时间序列同步。在我们的示例中，它被称为[Example] Time Series Sync | Event Pipeline。
- 对Daily Average Arrival Delay和Daily Average Departure Delay时间序列属性重复此过程。
现在时间序列属性已添加到 Object 类型中，我们准备在操作环境中使用时间序列属性。请继续阅读文档以了解如何在 Workshop 和 Quiver 中使用 Object 的时间序列属性。
