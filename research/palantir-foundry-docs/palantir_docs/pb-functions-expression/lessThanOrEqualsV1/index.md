来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/lessThanOrEqualsV1/

# 小于或等于

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 小于或等于

> 支持于：批处理，流处理

支持于：批处理，流处理

如果左边小于或等于右边，则返回 true。

表达式类别：布尔

## 声明的参数

- Left- 左表达式。Expression<ComparableType>
- Right- 右表达式。Expression<ComparableType>
输出类型：Boolean

## 示例

### 示例 1：基本情况

参数值：

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0 | false |
| 1 | 1 | true |
| 0 | 1 | true |

### 示例 2：基本情况

参数值：

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0.5 | false |
| 1 | 1.0 | true |

### 示例 3：基本情况

参数值：

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| a | b | true |
| abc | abcd | true |
| b | aa | false |

### 示例 4：空值情况

参数值：

- Left:a
- Right:b
| a | b | 输出 |
| --- | --- | --- |
| null | null | true |
| 1 | null | false |
| null | 1 | true |
