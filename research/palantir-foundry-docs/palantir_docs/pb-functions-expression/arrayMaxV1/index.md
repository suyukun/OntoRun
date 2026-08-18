来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayMaxV1/

# 数组最大值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组最大值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回数组列的最大值。

表达式类别: 数组

## 声明的参数

- 表达式- 从中返回最大元素的数组。Expression<Array<T>>
类型变量界限:T 接受数值型

输出类型:T

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: [ 1, 2, 3 ]
输出:3

### 示例 2: 空值情况

参数值:

- 表达式:array
| array | 输出 |
| --- | --- |
| null | null |
| [ 1,null] | 1 |
