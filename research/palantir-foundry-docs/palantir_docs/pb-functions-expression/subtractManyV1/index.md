来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/subtractManyV1/

# 减去多个表达式

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 减去多个表达式

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算一个数与所有输入列之间的差值。

表达式类别: 数值

## 声明的参数

- 表达式列表- 用于减法的表达式列表。List<Expression<Numeric>>
- 要减去的值- 要减去的表达式。Expression<Numeric>
输出类型:Numeric

## 示例

### 示例 1: 基本情况

参数值:

- 表达式列表: [col_b,col_c]
- 要减去的值:col_a
| col_a | col_b | col_c | 输出 |
| --- | --- | --- | --- |
| 5 | 3 | 2 | 0 |
| 2 | 4 | 0 | -2 |
| -2 | -4 | -2 | 4 |

### 示例 2: 基本情况

参数值:

- 表达式列表: [col_b]
- 要减去的值:col_a
| col_a | col_b | 输出 |
| --- | --- | --- |
| null | null | null |
| 1 | null | null |
| null | 10 | null |
