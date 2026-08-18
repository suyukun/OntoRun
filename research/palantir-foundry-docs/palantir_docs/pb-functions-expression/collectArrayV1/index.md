来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/collectArrayV1/

# 收集数组

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 收集数组

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

在每个组内收集一个值数组。空值将被忽略。

表达式类别: 聚合

## 声明的参数

- 表达式- 要收集到数组中的值列。Expression<T>
类型变量界限:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:factor
给定输入表:

| factor |
| --- |
| 2 |
| 2 |
| 3 |

输出:[ 2, 2, 3 ]

### 示例 2: 空值情况

参数值:

- 表达式:factor
给定输入表:

| factor |
| --- |
| 2 |
| null |
| 3 |

输出:[ 2, 3 ]
