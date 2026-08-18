来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/UnhexV1/

# 从十六进制转换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从十六进制转换

> 支持于: 批处理

支持于: 批处理

hex的逆运算。将每对字符解释为一个十六进制数并转换为该数字的字节表示。

表达式类别: 数值, 字符串

## 声明的参数

- 表达式- 要进行unhex的字符串列。Expression<字符串>
输出类型:二进制

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:string_hex
| string_hex | 输出 |
| --- | --- |
| 68656C6C6F | aGVsbG8= |
| 3039 | MDk= |
| FFFFFFFFFFFFCFC7 | ////////z8c= |
| 4C6F6E646F6E | TG9uZG9u |

### 示例 2: 空值情况

参数值:

- 表达式:null
输出:null
