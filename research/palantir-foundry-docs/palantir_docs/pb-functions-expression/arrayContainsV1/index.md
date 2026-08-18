来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/arrayContainsV1/

# 数组包含

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 数组包含

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果数组包含该值，则返回true。

表达式类别: 数组, 布尔值

## 声明的参数

- 数组- 要搜索的数组。Expression<Array<ComparableType>>
- 值- 要在数组中搜索的值。Expression<ComparableType>
输出类型:布尔值

## 示例

### 示例 1: 基本情况

参数值:

- 数组:part_ids
- 值: BRR-123
| part_ids | 输出 |
| --- | --- |
| [ AWE-112, BRR-123 ] | true |
| [ AWE-222, ABC-543 ] | false |

### 示例 2: 基本情况

描述: 允许不同数值类型之间的比较。参数值:

- 数组:ids
- 值: 1
| ids | 输出 |
| --- | --- |
| [ 1, 2 ] | true |
| [ 2, 3 ] | false |

### 示例 3: 空值情况

参数值:

- 数组:array
- 值:value
| array | value | 输出 |
| --- | --- | --- |
| [ 1, 2, 3 ] | null | false |
| null | 1 | false |
| null | null | false |
| [ 1, 2, 3,null] | null | true |
