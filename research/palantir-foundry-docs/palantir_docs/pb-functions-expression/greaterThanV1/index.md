来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/greaterThanV1/

# 大于

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 大于

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

如果左侧大于右侧，则返回true。

表达式类别: 数值

## 声明的参数

- 左侧- 左侧表达式。Expression<ComparableType>
- 右侧- 右侧表达式。Expression<ComparableType>
输出类型:Boolean

## 示例

### 示例 1: 基本情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0 | true |
| 1 | 1 | false |
| 0 | 1 | false |

### 示例 2: 基本情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 0.5 | true |
| 1 | 1.0 | false |

### 示例 3: 基本情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| b | a | true |
| abcd | abc | true |
| aa | b | false |

### 示例 4: 空值情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| null | null | true |
| 1 | null | false |
| null | 1 | false |
