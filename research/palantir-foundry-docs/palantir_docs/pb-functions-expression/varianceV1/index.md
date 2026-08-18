来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/varianceV1/

# 方差

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 方差

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算列中值的总体方差。

表达式类别: 聚合

## 声明的参数

- 表达式- 计算方差的列。Expression<Numeric>
输出类型:Double

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| 2 |
| 4 |
| 3 |

输出:0.66666666667

### 示例 2: 空值情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| 2 |
| null |
| 3 |

输出:0.25
