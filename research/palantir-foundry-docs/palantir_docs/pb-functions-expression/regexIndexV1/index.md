来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/regexIndexV1/

# Regex索引

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Regex索引

> 支持于：Batch

支持于：Batch

返回一个数组，其中包含在给定表达式中找到正则表达式模式的索引。

表达式类别: 正则表达式, 字符串

## 声明的参数

- Expression- 要与正则表达式匹配的表达式。Expression<字符串>
- Regex- 要查找索引的正则表达式。Expression<字符串>
输出类型:Array<Integer>

## 示例

### 示例 1: 基本情况

描述: 你可以找到正则表达式模式及其索引。参数值:

- Expression: ababab
- Regex: ab
输出:[ 0, 2, 4 ]

### 示例 2: 基本情况

描述: 重叠的匹配不单独考虑; 整个匹配段被视为一个匹配。参数值:

- Expression: abcdcef
- Regex: .c.
输出:[ 0 ]

### 示例 3: 基本情况

描述: 正则表达式模式有时不匹配输入字符串，导致空数组。参数值:

- Expression: abdefg
- Regex: cd
输出:[  ]

### 示例 4: 空值情况

描述: 如果表达式为空，输出为空。参数值:

- Expression:null
- Regex: ab
输出:null

### 示例 5: 空值情况

描述: 如果模式为空，输出为空。参数值:

- Expression: ababab
- Regex:null
输出:null

### 示例 6: 空值情况

参数值:

- Expression:string
- Regex:pattern
| string | pattern | 输出 |
| --- | --- | --- |
| foofoo | foo | [ 0, 3 ] |
| foo | null | null |
| null | ab | null |
| null | null | null |
