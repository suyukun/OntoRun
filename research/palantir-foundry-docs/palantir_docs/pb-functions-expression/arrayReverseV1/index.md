来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayReverseV1/

# 数组反转

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组反转

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

反转“数组”中元素的顺序。

表达式类别: 数组

## 声明的参数

- 表达式- 要反转的数组。Expression<Array<T>>
类型变量界限:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: [ 1, 2, 3 ]
输出:[ 3, 2, 1 ]

### 示例 2: 空值情况

参数值:

- 表达式:array
| 数组 | 输出 |
| --- | --- |
| null | null |
| [ 1,null] | [null, 1 ] |
