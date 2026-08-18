来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayAddV1/

# 数组添加

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组添加

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

在指定索引处向数组添加一个值。

表达式类别: 数组

## 声明的参数

- 数组- 要向其中添加元素的数组。Expression<Array<T>>
- 索引- 新元素应该插入到数组中的位置。第一个元素位于位置1。Expression<Integer>
- 值- 要添加到数组中的元素。Expression<T>
类型变量界限:T 接受 AnyType

输出类型:Array<T>

## 示例

### 示例 1: 基本情况

参数值:

- 数组:numbers
- 索引: 1
- 值: 1
| numbers | 输出 |
| --- | --- |
| [ 3, 5 ] | [ 1, 3, 5 ] |
| [ 2 ] | [ 1, 2 ] |
| [  ] | [ 1 ] |

### 示例 2: 空值情况

参数值:

- 数组:numbers
- 索引:index
- 值:value
| numbers | value | index | 输出 |
| --- | --- | --- | --- |
| null | 1 | 1 | null |
| [ 1 ] | null | 1 | [null, 1 ] |
| [ 1 ] | 1 | null | [ 1 ] |

### 示例 3: 边缘情况

参数值:

- 数组:numbers
- 索引: 10
- 值: 1
| numbers | 输出 |
| --- | --- |
| [ 3, 5 ] | [ 3, 5,null,null,null,null,null,null,null, 1 ] |
