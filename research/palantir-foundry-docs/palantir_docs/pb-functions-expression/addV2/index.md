来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/addV2/

# 数字相加

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数字相加

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

计算所有输入列的和。

表达式类别: 数值

## 声明的参数

- 表达式- 要相加的列列表。List<Expression<Numeric>>
输出类型:数值

## 示例

### 示例 1: 基本案例

参数值:

- 表达式: [col_a,col_b]
| col_a | col_b | 输出 |
| --- | --- | --- |
| 0 | 1 | 1 |
| 3 | -2 | 1 |
