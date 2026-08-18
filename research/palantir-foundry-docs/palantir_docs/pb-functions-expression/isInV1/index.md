来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isInV1/

# 是否包含

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否包含

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果列表包含该值，则返回true。

表达式类别: 布尔

## 声明的参数

- Contains（包含）- 要搜索的列表。List<Expression<T>>
- Value（值）- 要查找的值。Expression<T>
类型变量界限:T 接受 ComparableType

输出类型:布尔

## 示例

### 示例 1: 基本情况

描述: 元素可以是数组。参数值:

- Contains（包含）: [one,two]
- Value（值）:value
| one | two | value | 输出 |
| --- | --- | --- | --- |
| [ 1 ] | [ 2 ] | [ 1 ] | true |
| [ 1, 2 ] | [ 2 ] | [ 1 ] | false |

### 示例 2: 基本情况

描述: 您可以检查列表是否包含该值。参数值:

- Contains（包含）: [AWE-112, BRR-123]
- Value（值）:value
| value | 输出 |
| --- | --- |
| BRR-123 | true |
| ABC-543 | false |

### 示例 3: 基本情况

描述: 元素可以是结构体。参数值:

- Contains（包含）: [one,two]
- Value（值）:value
| one | two | value | 输出 |
| --- | --- | --- | --- |
| {part: AWE-112,} | {part: BRR-123,} | {part: AWE-112,} | true |
| {part: CSE-122,} | {part: BRR-123,} | {part: AWE-112,} | false |

### 示例 4: 空值情况

描述: 您可以检查空值。参数值:

- Contains（包含）: [one,two,three]
- Value（值）:value
| one | two | three | value | 输出 |
| --- | --- | --- | --- | --- |
| 1 | 2 | 3 | null | false |
| null | null | null | 1 | false |
| 1 | 2 | null | null | true |
