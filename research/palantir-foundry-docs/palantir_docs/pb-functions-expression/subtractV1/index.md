来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/subtractV1/

# 数字相减

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数字相减

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将一个数字从另一个数字中减去。

表达式类别: 数值

## 声明的参数

- Left- 左侧数字。Expression<Numeric>
- Right- 右侧数字。Expression<Numeric>
输出类型:数值

## 示例

### 示例 1: 基本情况

参数值:

- Left:col_a
- Right:col_b
| col_a | col_b | 输出 |
| --- | --- | --- |
| 32 | 4 | 28 |
| -5 | -3 | -2 |
