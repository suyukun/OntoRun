来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arraysHaveIntersectionV1/

# 数组有交集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组有交集

> 支持于：批处理，流处理

支持于：批处理，流处理

检查给定数组是否至少有一个共享元素。

表达式类别：数组，布尔

## 声明的参数

- 表达式- 要检查的数组列表。List<Expression<Array<T>>>
类型变量界限：T 接受 AnyType

输出类型：布尔

## 示例

### 示例 1：基本情况

参数值：

- 表达式: [[ 1, 2, 3 ], [ 3, 4 ]]
输出：true

### 示例 2：基本情况

参数值：

- 表达式: [[ 1, 2 ], [ 3, 4 ]]
输出：false

### 示例 3：基本情况

参数值：

- 表达式: [[ 1, 2, 3 ], [ 3, 4 ], [ 2, 3 ]]
输出：true

### 示例 4：空值情况

参数值：

- 表达式: [first_array,second_array]
| first_array | second_array | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | null | false |
| null | null | false |
