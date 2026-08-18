来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/rightPadV1/

# 右填充字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 右填充字符串

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

将字符串列用填充符右填充到指定长度。如果字符串的长度大于提供的长度，将会被截断。

表达式类别: 字符串

## 声明的参数

- Expression-无描述Expression<字符串>
- Length-无描述Expression<Integer>
- Pad-无描述Expression<字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- Expression: Hello world!
- Length: 15
- Pad: *
输出:Hello world!***

### 示例 2: 空值情况

参数值:

- Expression:String
- Length:Length
- Pad:Pad
| 字符串 | 长度 | 填充符 | 输出 |
| --- | --- | --- | --- |
| null | 15 | * | null |
| Hello world! | null | * | 空字符串 |
| Hello, world! | 15 | null | Hello, world! |
| null | null | null | null |

### 示例 3: 边缘情况

描述: 长度小于字符串将截断字符串。参数值:

- Expression: Hello world!
- Length: 5
- Pad: *
输出:Hello

### 示例 4: 边缘情况

描述: 长度为0将删除字符串。参数值:

- Expression: Hello world!
- Length: 0
- Pad: *
输出:空字符串
