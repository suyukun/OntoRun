来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/base64EncodeV1/

# Base64 编码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Base64 编码

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

对给定表达式进行 Base64 编码。

表达式类别: 二进制, 转换

## 声明的参数

- 表达式- 要编码的字符串或二进制表达式。表达式<二进制 | 字符串>
输出类型:字符串

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:city
| city | 输出 |
| --- | --- |
| TG9uZG9u | TG9uZG9u |
| Q29wZW5oYWdlbg== | Q29wZW5oYWdlbg== |
| TmV3IFlvcms= | TmV3IFlvcms= |

### 示例 2: 基本情况

参数值:

- 表达式:city
| city | 输出 |
| --- | --- |
| London | TG9uZG9u |
| Copenhagen | Q29wZW5oYWdlbg== |
| New York | TmV3IFlvcms= |

### 示例 3: 空值情况

参数值:

- 表达式:city
| city | 输出 |
| --- | --- |
| null | null |

### 示例 4: 空值情况

参数值:

- 表达式:city
| city | 输出 |
| --- | --- |
| null | null |
