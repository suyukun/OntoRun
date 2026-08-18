来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arraysZipV1/

# 数组 zip

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组 zip

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将给定数组列表压缩成一个合并的结构体数组，其中第 n 个结构体包含输入数组的所有第 n 个值。

表达式类别: 数组

## 声明的参数

- 表达式- 要压缩的数组列表。List<Expression<Array<AnyType>>>
输出类型:Array<Struct>

## 示例

### 示例 1: 基本案例

参数值:

- 表达式: [first_array,second_array]
| first_array | second_array | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | [ 4, 5, 6 ] | [ {first_array: 1,second_array: 4,}, {first_array: 2,<... |

### 示例 2: 空值案例

参数值:

- 表达式: [first_array,second_array]
| first_array | second_array | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | null | [ {first_array: 1,second_array:null,}, {first_array... |
| null | null | [  ] |
| [  ] | [  ] | [  ] |

### 示例 3: 边缘案例

描述: 使用最长长度的数组。参数值:

- 表达式: [first_array,second_array]
| first_array | second_array | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | [ 4, 5 ] | [ {first_array: 1,second_array: 4,}, {first_array: 2,<... |
