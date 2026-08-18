来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/assignTimestampsAndWatermarksV1/

# 指派时间戳和水印

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 指派时间戳和水印

> 支持于: 流处理

支持于: 流处理

指派时间戳和水印给输入数据，筛选掉时间戳为空的记录。

变换类别: 其他

## 声明的参数

- 数据集- 指派时间戳和水印的数据集。表格
- 时间戳表达式- 评估为要指派的时间戳的表达式。表达式<时间戳>
- 非必填对每条记录发出水印- 如果为true，水印将在流中的每条记录中传播。这通常效率低下，并会增加性能开销，但在流被重播时提供确定性行为。在大多数情况下，建议将此值设置为false。文字<布尔>
## 示例

### 示例 1: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 时间戳表达式:timestamp
- 对每条记录发出水印:null
输入:

| timestamp | temperature | sensor_id |
| --- | --- | --- |
| 1969-12-31T23:59:50Z | 28 | sensor_1 |
| 1969-12-31T23:59:40Z | 30 | sensor_2 |
| 1969-12-31T23:59:35Z | 29 | sensor_1 |

输出:

| timestamp | temperature | sensor_id |
| --- | --- | --- |
| 1969-12-31T23:59:50Z | 28 | sensor_1 |
| 1969-12-31T23:59:40Z | 30 | sensor_2 |
| 1969-12-31T23:59:35Z | 29 | sensor_1 |

### 示例 2: 空值情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 时间戳表达式:timestamp
- 对每条记录发出水印:null
输入:

| timestamp | temperature | sensor_id |
| --- | --- | --- |
| 1969-12-31T23:59:50Z | 28 | sensor_1 |
| null | 30 | sensor_2 |
| null | 29 | sensor_1 |

输出:

| timestamp | temperature | sensor_id |
| --- | --- | --- |
| 1969-12-31T23:59:50Z | 28 | sensor_1 |
