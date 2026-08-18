来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/multiplyV2/

# 数字相乘

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数字相乘

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算所有输入列的乘积。

表达式类别: 数值

## 声明的参数

- 表达式- 要相乘的列的列表。List<Expression<Numeric>>
输出类型:数值

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: [col_a,col_b,col_c]
| col_a | col_b | col_c | 输出 |
| --- | --- | --- | --- |
| 10 | 2 | 3 | 60 |

### 示例 2: 空值情况

参数值:

- 表达式: [col_a,col_b]
| col_a | col_b | 输出 |
| --- | --- | --- |
| null | null | null |

### 示例 3: 空值情况

参数值:

- 表达式: [col_a,col_b]
| col_a | col_b | 输出 |
| --- | --- | --- |
| 1 | null | null |

### 示例 4: 空值情况

参数值:

- 表达式: [col_a,col_b]
| col_a | col_b | 输出 |
| --- | --- | --- |
| null | 1 | null |
