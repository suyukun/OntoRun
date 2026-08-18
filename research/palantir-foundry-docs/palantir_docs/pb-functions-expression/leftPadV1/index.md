来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/leftPadV1/

# 左填充字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 左填充字符串

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将字符串列左填充到指定长度。

表达式类别: 字符串

## 声明的参数

- 表达式-无描述Expression<字符串>
- 长度-无描述Expression<整数>
- 填充字符-无描述Expression<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本案例

参数值:

- 表达式: Hello world!
- 长度: 15
- 填充字符: *
输出:***Hello world!

### 示例 2: 空值案例

参数值:

- 表达式:String
- 长度:Length
- 填充字符:Pad
| 字符串 | 长度 | 填充字符 | 输出 |
| --- | --- | --- | --- |
| null | 15 | * | null |
| Hello world! | null | * | 空字符串 |
| Hello, world! | 15 | null | Hello, world! |
| null | null | null | null |

### 示例 3: 边缘案例

描述: 长度小于字符串，将截断字符串。参数值:

- 表达式: Hello world!
- 长度: 5
- 填充字符: *
输出:Hello

### 示例 4: 边缘案例

描述: 长度为0将删除字符串。参数值:

- 表达式: Hello world!
- 长度: 0
- 填充字符: *
输出:空字符串
