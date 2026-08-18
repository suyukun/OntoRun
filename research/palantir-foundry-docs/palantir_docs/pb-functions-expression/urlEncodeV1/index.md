来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/urlEncodeV1/

# Url 编码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Url 编码

> 支持于: 批处理，流处理

支持于: 批处理，流处理

对要在url中发送的字符串进行百分比编码。

表达式类别: 字符串

## 声明的参数

- 表达式- 要进行url编码的表达式。表达式<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:string
| string | 输出 |
| --- | --- |
| raw_string_with_no_special_characters | raw_string_with_no_special_characters |
| test/api?string=3 | test%2Fapi%3Fstring%3D3 |

### 示例 2: 空值情况

参数值:

- 表达式:null
输出:null
