来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/sha256V1/

# 哈希 sha256

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 哈希 sha256

> 支持于: 批处理，流处理

支持于: 批处理，流处理

使用sha256哈希算法对输入进行哈希。

表达式类别: 字符串

## 声明的参数

- 表达式-无描述Expression<Binary | 字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式: Hello World!
输出:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069

### 示例 2: 空值情况

参数值:

- 表达式:value
| value | 输出 |
| --- | --- |
| null | null |
