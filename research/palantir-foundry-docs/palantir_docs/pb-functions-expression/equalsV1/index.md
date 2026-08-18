来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/equalsV1/

# 等于

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 等于

> 支持于: 批处理，流处理

支持于: 批处理，流处理

如果左侧和右侧相等，则返回true。

表达式类别: 布尔

## 声明的参数

- 左侧- 左表达式。表达式<ComparableType>
- 右侧- 右表达式。表达式<ComparableType>
输出类型:布尔

## 示例

### 示例 1: 基本情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| 1 | 1 | true |
| 1 | 0 | false |

### 示例 2: 基本情况

参数值:

- 左侧:a
- 右侧:b
| a | b | 输出 |
| --- | --- | --- |
| 1.0 | 1 | true |
| 1.0 | 0 | false |

### 示例 3: 基本情况

参数值:

- 左侧:departure
- 右侧:destination
| departure | destination | 输出 |
| --- | --- | --- |
| Heathrow | Heathrow | true |
| Heathrow | Gatwick | false |

### 示例 4: 空值情况

参数值:

- 左侧:departure
- 右侧:destination
| departure | destination | 输出 |
| --- | --- | --- |
| null | null | true |
| null | Heathrow | false |
