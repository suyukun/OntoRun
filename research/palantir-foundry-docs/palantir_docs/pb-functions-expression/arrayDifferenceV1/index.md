来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayDifferenceV1/

# 数组差异

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组差异

> 支持于: 批处理，流处理

支持于: 批处理，流处理

返回left数组中所有不在right数组中的唯一元素。

表达式类别: 数组

## 声明的参数

- Left array-无描述Expression<Array<T>>
- Right array-无描述Expression<Array<T>>
类型变量界限:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本情况

参数值:

- Left array: [ 1, 2, 3 ]
- Right array: [ 2, 3, 4 ]
输出:[ 1 ]

### 示例 2: 空值情况

参数值:

- Left array:first_array
- Right array:second_array
| first_array | second_array | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | null | [ 1, 2, 3 ] |
| null | [ 1, 2, 3 ] | null |
| null | null | null |

### 示例 3: 边缘情况

描述: 左数组中的重复项将被移除。参数值:

- Left array: [ 1, 1, 2, 3 ]
- Right array: [ 2, 3, 4 ]
输出:[ 1 ]
