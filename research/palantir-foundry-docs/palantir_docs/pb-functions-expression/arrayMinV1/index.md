来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayMinV1/

# 数组最小值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组最小值

> 支持于: 批处理，流处理

支持于: 批处理，流处理

返回数组列的最小值。

表达式类别: 数组

## 声明的参数

- 表达式- 返回最小元素的数组。Expression<Array<T>>
类型变量界限:T 接受数值型

输出类型:T

## 例子

### 示例 1: 基本情况

参数值:

- 表达式: [ 1, 2, 3 ]
输出:1

### 示例 2: 空值情况

参数值:

- 表达式:array
| array | 输出 |
| --- | --- |
| null | null |
| [ 1,null] | 1 |
