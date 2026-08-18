来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/greaterThanOrEqualsV1/

# 大于或等于

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 大于或等于

> 支持于: Batch, Streaming

支持于: Batch, Streaming

如果左边大于或等于右边，则返回true。

表达式类别: 布尔

## 声明的参数

- Left- 左表达式。Expression<ComparableType>
- Right- 右表达式。Expression<ComparableType>
输出类型:布尔

## 示例

### 示例 1: 基本案例

参数值:

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0 | true |
| 1 | 1 | true |
| 0 | 1 | false |

### 示例 2: 基本案例

参数值:

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0.5 | true |
| 1 | 1.0 | true |

### 示例 3: 基本案例

参数值:

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| b | a | true |
| abcd | abc | true |
| aa | b | false |

### 示例 4: 空值案例

参数值:

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| null | null | true |
| 1 | null | true |
| null | 1 | false |
