来源: https://palantir.com/docs/zh/foundry/time-series/sensor-object-end-to-end/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

传感器Object类型是时间序列数据的一种更高级配置，其中传感器Object保存其关联父级（也称为根Object）的传感器数据。请查看时间序列文档，以决定时间序列属性设置或传感器Object类型配置是否适合您的应用案例。

本文档将逐步介绍如何在Pipeline Builder中编写管道，在Ontology Manager中设置传感器Object类型，并使用示例航空Ontology和Foundry中的时间序列功能创建Quiver仪表盘和Workshop模块。

航空Ontology由示例Flight、Carrier、Route、Airport和Flight SensorObject类型组成。Flight通过这些Object上的flight_id外键链接到Aircraft、Flight Sensor、Route、Airport和Carrier对象。

航空Ontology来自一个概念数据的参考Ontology，可能不适用于您的注册。无论您的注册是否可用，使用此参考Ontology构建的这些示例将作为您创建自己的管道、Object类型和使用传感器Object类型的Workshop模块的参考。

您将通过指南制作的Workshop模块将允许您查看和与选定航班的传感器时间序列数据进行交互。

以下指南将引导您完成创建和支持此Workshop模块的步骤：

- 在Pipeline Builder中创建传感器Object类型数据
- 使用Ontology Manager创建传感器Object类型
- 在Workshop和Quiver中使用传感器Object类型时间序列数据