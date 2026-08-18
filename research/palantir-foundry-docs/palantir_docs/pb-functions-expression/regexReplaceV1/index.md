来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/regexReplaceV1/

# 正则表达式替换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 正则表达式替换

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

使用正则表达式模式替换字符串。

表达式类别: 正则表达式, 字符串

## 声明的参数

- Expression- 要替换的输入字符串。Expression<字符串>
- Pattern- 要匹配的正则表达式模式。Expression<字符串>
- Replace- 替换字符串。Expression<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本案例

参数值:

- Expression:tail_number
- Pattern: (\w\w)(-)
- Replace: **-
| tail_number | 输出 |
| --- | --- |
| MT-123 | **-123 |
| XB-434 | **-434 |
| MT-123, XB-434 | **-123, **-434 |

### 示例 2: 基本案例

参数值:

- Expression:tail_number
- Pattern: (\w\w)(-)
- Replace: $1
| tail_number | 输出 |
| --- | --- |
| MT-123 | MT123 |
| XB-434 | XB434 |
| MT-123, XB-434 | MT123, XB434 |

### 示例 3: 空案例

参数值:

- Expression:tail_number
- Pattern:regex
- Replace: foo
| tail_number | regex | 输出 |
| --- | --- | --- |
| MT-123 | ( | null |

### 示例 4: 空案例

描述: 空输入产生空输出。参数值:

- Expression:null
- Pattern: (\w\w)(-)
- Replace: **
输出:null

### 示例 5: 空案例

描述: 空输入产生空输出。参数值:

- Expression: foo
- Pattern: bar
- Replace:null
输出:null
