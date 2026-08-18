来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/substringV1/

# 子字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 子字符串

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

提取子字符串。

表达式类别: 数值

## 声明的参数

- 表达式-无描述表达式<字符串>
- 起始- 子字符串起始的索引（包含）。负数表示从字符串末尾开始。这是1索引。表达式<整数>
- 非必填长度- 要提取的子字符串的长度。如果未提供，则提取字符串的剩余部分。表达式<整数>
输出类型:字符串

## 示例

### 示例 1: 基本案例

参数值:

- 表达式:string
- 起始:start
- 长度:length
| string | start | length | 输出 |
| --- | --- | --- | --- |
| hello, world | 1 | 5 | hello |
| hello, world | 8 | 5 | world |
| hello, world | -5 | 5 | world |

### 示例 2: 基本案例

描述: 当未提供长度时，子字符串将运行到字符串的末尾。参数值:

- 表达式:string
- 起始:start
- 长度:null
| string | start | 输出 |
| --- | --- | --- |
| hello, world | 1 | hello, world |
| hello, world | 8 | world |
| hello, world | -5 | world |

### 示例 3: 空值案例

描述: 在空值情况下，输出始终为空。参数值:

- 表达式:string
- 起始:start
- 长度:length
| string | start | length | 输出 |
| --- | --- | --- | --- |
| null | 1 | 5 | null |
| hello, world | null | 5 | null |
| hello, world | 1 | null | null |
| null | null | null | null |

### 示例 4: 边缘案例

描述: 当长度长于剩余的子字符串时，输出为直到字符串末尾的子字符串。参数值:

- 表达式:string
- 起始:start
- 长度:length
| string | start | length | 输出 |
| --- | --- | --- | --- |
| hello, world | -5 | 10 | world |
| hello, world | 1 | 20 | hello, world |
| hello, world | 12 | 5 | d |
| hello, world | 13 | 5 | 空字符串 |
| hello, world | 20 | 5 | 空字符串 |
| hello, world | 12 | -5 | 空字符串 |
