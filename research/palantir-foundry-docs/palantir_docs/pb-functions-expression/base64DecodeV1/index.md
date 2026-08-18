来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/base64DecodeV1/

# Base64 解码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Base64 解码

> 支持于: 批处理，流处理

支持于: 批处理，流处理

对给定表达式进行Base64解码。

表达式类别: 二进制, 转换

## 声明的参数

- Expression-无描述Expression<字符串>
输出类型:二进制

## 示例

### 示例 1: 基本情况

参数值:

- Expression:city_base64
| city_base64 | 输出 |
| --- | --- |
| TG9uZG9u | TG9uZG9u |
| Q29wZW5oYWdlbg== | Q29wZW5oYWdlbg== |
| TmV3IFlvcms= | TmV3IFlvcms= |
