来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/rightStringV1/

# 字符串右侧

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 字符串右侧

> 支持于: 批处理，流处理

支持于: 批处理，流处理

根据索引提取字符串的右侧部分。

表达式类别: 字符串

## 声明的参数

- 表达式-无描述Expression<字符串>
- 长度- 从字符串右侧提取的字符数。Expression<Integer>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: Hello world!
- 长度: 6
输出:world!

### 示例 2: 空值情况

参数值:

- 表达式:字符串
- 长度:长度
| 字符串 | 长度 | 输出 |
| --- | --- | --- |
| null | 1 | null |
| Hello world! | null | null |
| null | null | null |

### 示例 3: 边缘情况

描述: 长度大于字符串长度将返回完整字符串。参数值:

- 表达式: Hello world!
- 长度: 15
输出:Hello world!
