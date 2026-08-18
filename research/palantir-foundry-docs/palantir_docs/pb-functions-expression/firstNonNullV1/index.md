来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/firstNonNullV1/

# 第一个非空值 (合并)

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 第一个非空值 (合并)

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

选择输入中的第一个非空值。在 SQL 中称为合并。

表达式类别: 数据准备

## 声明的参数

- 表达式- 将返回这些表达式的第一个非空值。List<Expression<T>>
- 非必填将空字符串视为 null。- 将所有空字符串视为 null 值。Literal<Boolean>
类型变量界限:T 接受 AnyType

输出类型:T

## 示例

### 示例 1: 基本案例

参数值:

- 表达式: [tail_number,airline]
- 将空字符串视为 null。:null
| tail_number | airline | 输出 |
| --- | --- | --- |
| XB-123 | null | XB-123 |
| null | MT | MT |

### 示例 2: 基本案例

参数值:

- 表达式: [tail_number,airline]
- 将空字符串视为 null。: true
| tail_number | airline | 输出 |
| --- | --- | --- |
| XB-123 | null | XB-123 |
| 空字符串 | MT | MT |

### 示例 3: Null 案例

参数值:

- 表达式: [tail_number,airline]
- 将空字符串视为 null。:null
| tail_number | airline | 输出 |
| --- | --- | --- |
| null | null | null |
