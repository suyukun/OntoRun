来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/urlDecodeV1/

# Url 解码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Url 解码

> 支持于: 批处理，流处理

支持于: 批处理，流处理

将百分比编码的字符串解码为纯文本。

表达式类别: 转换, 字符串

## 声明的参数

- 表达式- 需要进行url解码的表达式。表达式<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:string
| 字符串 | 输出 |
| --- | --- |
| raw_string_with_no_special_characters | raw_string_with_no_special_characters |
| test%2Fapi%3Fstring%3D3 | test/api?string=3 |

### 示例 2: 空值情况

参数值:

- 表达式:null
输出:null
