来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/renameStructFieldV1/

# 重命名结构字段

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 重命名结构字段

> 支持于: 批处理，流处理

支持于: 批处理，流处理

重命名结构中的字段。

表达式类别: 数据准备，结构

## 声明的参数

- 表达式-无描述表达式<结构>
- 重命名-无描述列表<元组<结构定位器, 字面量<字符串>>>
输出类型:结构

## 示例

### 示例 1: 基本案例

参数值:

- 表达式:struct
- 重命名: [(airline.id, identifier)]
| struct | 输出 |
| --- | --- |
| {airline: {id: NA,},} | {airline: {identifier: NA,},} |
| {airline: {id: FE,},} | {airline: {identifier: FE,},} |

### 示例 2: 基本案例

参数值:

- 表达式:struct
- 重命名: [(airline.id, identifier)]
| struct | 输出 |
| --- | --- |
| null | null |
