来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/sqrtV1/

# 平方根

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 平方根

> 支持于：批处理，流处理

支持于：批处理，流处理

计算列的平方根。

表达式类别：数值

## 声明的参数

- 表达式-无描述Expression<Numeric>
输出类型:Double

## 示例

### 示例 1：基本情况

参数值:

- 表达式: 9.0
输出:3.0

### 示例 2：基本情况

参数值:

- 表达式: 16.3216
输出:4.04

### 示例 3：空值情况

参数值:

- 表达式:value
| value | 输出 |
| --- | --- |
| null | null |
