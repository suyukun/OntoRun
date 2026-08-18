来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayRepeatV1/

# 数组重复

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组重复

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回一个数组，其中包含的array被连接value次。

表达式类别: 数组

## 声明参数

- 数组- 要重复的数组。Expression<Array<T>>
- 值- 连接'array'的次数。Expression<Integer>
类型变量界限:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本情况

参数值:

- 数组: [ 1, 2 ]
- 值: 2
输出:[ 1, 2, 1, 2 ]

### 示例 2: 空值情况

参数值:

- 数组:array
- 值:value
| array | value | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | null | null |
| null | 1 | null |
| null | null | null |
