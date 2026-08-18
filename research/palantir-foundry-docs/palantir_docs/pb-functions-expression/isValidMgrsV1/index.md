来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isValidMgrsV1/

# 是否为有效的 MGRS

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为有效的 MGRS

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

如果输入是有效的 MGRS（军事网格参考系统）字符串，则返回 true。

表达式类别: 地理空间

## 声明的参数

- 表达式- 符合 MGRS（军事网格参考系统）格式的字符串。Expression<字符串>
输出类型:布尔型

## 示例

### 示例 1: 基本情况

参数值:

- 表达式:mgrs
| mgrs | 输出 |
| --- | --- |
| not an mgrs value | false |
| 4Q FJ | false |
| 1 6 | false |
| 4Q | false |
| 4Q FJ 1 | false |

### 示例 2: 基本情况

参数值:

- 表达式:mgrs
| mgrs | 输出 |
| --- | --- |
| 4Q FJ 1 6 | true |
| 4Q FJ 12345 67890 | true |

### 示例 3: 空情况

参数值:

- 表达式:mgrs
| mgrs | 输出 |
| --- | --- |
| null | false |
