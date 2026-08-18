来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/regexFindV1/

# 正则表达式查找

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 正则表达式查找

> 支持于：批处理，流处理

支持于：批处理，流处理

将表达式与正则表达式进行匹配。正则表达式可以匹配字符串的任何部分。

表达式类别：正则表达式，字符串

## 声明的参数

- Expression- 要与正则表达式匹配的表达式。Expression<字符串>
- Regex- 要查找的正则表达式。Expression<字符串>
输出类型：布尔型

## 示例

### 示例 1：基本情况

描述：模式必须在字符串中，但不必匹配完整值。参数值：

- Expression: abcdefg
- Regex: abc
输出：true

### 示例 2：基本情况

描述：可以找到正则表达式模式。参数值：

- Expression: abcdefg
- Regex: abc?d
输出：true

### 示例 3：基本情况

描述：正则表达式模式有时不匹配输入字符串。参数值：

- Expression: abdefg
- Regex: ab?d
输出：true

### 示例 4：空值情况

描述：空模式不匹配。参数值：

- Expression: foo
- Regex:null
输出：false

### 示例 5：空值情况

描述：空列不匹配。参数值：

- Expression:null
- Regex: ab?d.*
输出：false

### 示例 6：空值情况

参数值：

- Expression:foo
- Regex:pattern
| foo | pattern | 输出 |
| --- | --- | --- |
| foo | ( | false |
| foo | null | false |
| null | foo | false |
| null | null | false |
