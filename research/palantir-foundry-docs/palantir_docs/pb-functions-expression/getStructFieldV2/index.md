来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/getStructFieldV2/

# 获取结构体字段

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取结构体字段

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

从结构体中提取字段。

表达式类别: 结构体

## 声明的参数

- 定位器- 提取多个条目中的内部元素，如 ['author', 'email']。StructLocator
- 结构体-无描述Expression<Struct>
输出类型:AnyType

## 示例

### 示例 1: 基本情况

参数值:

- 定位器: airline.id
- 结构体:struct
| 结构体 | 输出 |
| --- | --- |
| {airline: {id: NA,},} | NA |
| {airline: {id: FE,},} | FE |

### 示例 2: 基本情况

参数值:

- 定位器: airline.id
- 结构体:struct
| 结构体 | 输出 |
| --- | --- |
| {airline:null,} | null |
| {airline: {id:null,},} | null |
| null | null |
