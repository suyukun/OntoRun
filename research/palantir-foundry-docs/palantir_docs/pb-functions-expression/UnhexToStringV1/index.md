来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/UnhexToStringV1/

# 从十六进制转换为字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从十六进制转换为字符串

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

与hex相反，将每对字符解释为一个十六进制数，并转换为该数字字节表示的utf-8字符串。

表达式类别: 字符串

## 声明的参数

- 表达式- 要进行unhex的字符串列。Expression<字符串>
输出类型:字符串

## 示例

### 示例1: 基本案例

参数值:

- 表达式:string_hex
| string_hex | 输出 |
| --- | --- |
| 68656C6C6F | hello |
| 4C6F6E646F6E | London |

### 示例2: 空值案例

参数值:

- 表达式:null
| string_hex | 输出 |
| --- | --- |
| null | null |
