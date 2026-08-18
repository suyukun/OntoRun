来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/maxV1/

# 最大值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 最大值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算列中的最大值。

表达式类别: 数值

## 声明参数

- 表达式- 计算最大值的列。表达式<ComparableType>
输出类型:ComparableType

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

输出:4

### 示例 2: 空值情况

参数值:

- 表达式:values
给定输入表:

| values |
| --- |
| 2 |
| null |
| 3 |

输出:3
