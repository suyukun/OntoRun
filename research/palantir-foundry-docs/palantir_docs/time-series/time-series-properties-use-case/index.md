来源: https://palantir.com/docs/zh/foundry/time-series/time-series-properties-use-case/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

对象上的时间序列属性支持强大的分析工作流。此文档将逐步介绍在Pipeline Builder中编写管道、在Ontology Manager中设置对象，以及使用示例航空Ontology和Foundry中的时间序列功能创建Quiver仪表盘和Workshop模块的各个步骤。

航空Ontology由示例Flight、Carrier、Route、Airport和Flight Sensor对象类型组成。Flight通过这些对象上的flight_id外键链接到Aircraft、Flight Sensor、Route、Airport和Carrier对象。

航空Ontology来自一个使用开源数据的参考Ontology，这些数据可能无法用于您的注册。无论您是否可用，这些使用此示例Ontology构建的示例将作为您创建自己的管道、对象类型和带有时间序列属性的Workshop模块的参考。

通过指南生成的Workshop模块将允许您使用航班数据在Carrier、Route和Airport对象上使用和查看时间序列属性。

以下指南将引导您完成创建和支持此Workshop模块的步骤：

- 使用Pipeline Builder从'Flight'对象集中生成时间序列属性
- 将时间序列属性添加到航空对象
- 在Workshop和Quiver中使用航空对象上的时间序列属性