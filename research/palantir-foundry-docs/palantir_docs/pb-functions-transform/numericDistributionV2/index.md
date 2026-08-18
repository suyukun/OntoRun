来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/numericDistributionV2/

# 数值分布

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数值分布

> 支持于: Batch

支持于: Batch

计算指定列中数值的分布。

变换类别: 数值

## 声明参数

- 桶数量- 要分配的桶数量。Literal<Long>
- 列- 要计算分布的列。Column<Numeric>
- 数据集- 要应用分布的数据集。Table
- 最大值- 分布的最大值。Literal<Double>
- 最小值- 分布的最小值。Literal<Double>
## 示例

### 示例 1: 基本情况

参数值:

- 桶数量: 10
- 列:value
- 数据集: ri.foundry.main.dataset.a
- 最大值: 20.0
- 最小值: 0.0
输入:

| value |
| --- |
| 0.0 |
| 0.0 |
| 1.3 |
| 5.3 |
| 10.5 |

输出:

| bucket | min_value | max_value | count | bucket_start | bucket_end |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.0 | 1.3 | 3 | 0.0 | 2.0 |
| 2 | 5.3 | 5.3 | 1 | 4.0 | 6.0 |
| 5 | 10.5 | 10.5 | 1 | 10.0 | 12.0 |

### 示例 2: 基本情况

参数值:

- 桶数量: 3
- 列:value
- 数据集: ri.foundry.main.dataset.a
- 最大值: 25.0
- 最小值: -5.0
输入:

| value |
| --- |
| -15 |
| -5 |
| 0 |
| 15 |
| 20 |

输出:

| bucket | min_value | max_value | count | bucket_start | bucket_end |
| --- | --- | --- | --- | --- | --- |
| 0 | -5 | 0 | 2 | -5.0 | 5.0 |
| 2 | 15 | 20 | 2 | 15.0 | 25.0 |

### 示例 3: 边缘情况

参数值:

- 桶数量: 1
- 列:value
- 数据集: ri.foundry.main.dataset.a
- 最大值: 20.0
- 最小值: 20.0
输入:

| value |
| --- |
| -15 |
| -5 |
| 0 |
| 15 |
| 20 |

输出:

| bucket | min_value | max_value | count | bucket_start | bucket_end |
| --- | --- | --- | --- | --- | --- |
| 0 | 20 | 20 | 1 | 20.0 | 20.0 |

### 示例 4: 边缘情况

参数值:

- 桶数量: 1
- 列:value
- 数据集: ri.foundry.main.dataset.a
- 最大值: 20.0
- 最小值: -5.0
输入:

| value |
| --- |
| -15 |
| -5 |
| 0 |
| 15 |
| 20 |

输出:

| bucket | min_value | max_value | count | bucket_start | bucket_end |
| --- | --- | --- | --- | --- | --- |
| 0 | -5 | 15 | 3 | -5.0 | 20.0 |
| 1 | 20 | 20 | 1 | 20.0 | 45.0 |
