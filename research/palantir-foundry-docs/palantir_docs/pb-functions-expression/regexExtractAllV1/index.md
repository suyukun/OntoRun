来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/regexExtractAllV1/

# 提取所有正则表达式匹配项

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取所有正则表达式匹配项

> 支持于: 批处理

支持于: 批处理

将所有正则表达式匹配项提取到一个数组中。

表达式类别: 正则表达式, 字符串

## 声明的参数

- Expression- 从中提取值的字符串。Expression<字符串>
- Group- 要提取的组号。如果为0，则匹配整个正则模式。Literal<Integer>
- Pattern- 要匹配的正则表达式模式。Regex
输出类型:Array<字符串>

## 示例

### 示例 1: 基本情况

描述: 从每个代码中提取前两个首字母。参数值:

- Expression: MT-112, XB-967
- Group: 1
- Pattern: (\w\w)(-)
输出:[ MT, XB ]

### 示例 2: 空值情况

描述: 空输入会产生空输出。参数值:

- Expression:null
- Group: 1
- Pattern: (\w\w)(-)
输出:null
