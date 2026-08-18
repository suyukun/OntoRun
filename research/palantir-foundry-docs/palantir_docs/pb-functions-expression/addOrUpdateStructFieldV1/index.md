来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/addOrUpdateStructFieldV1/

# 添加或更新结构体字段

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 添加或更新结构体字段

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

更新结构体的字段或添加一个新字段。

表达式类别: 结构体

## 声明的参数

- Expression- 更新结构体字段的表达式。Expression<AnyType>
- Locator- 定位具有多个条目的内部元素，例如 ['author', 'email']。StructLocator
- Struct- 要更新的结构体。Expression<Struct>
输出类型:Struct

## 例子

### 例子 1: 基本案例

参数值:

- Expression:value
- Locator: flight
- Struct:struct
| struct | value | 输出 |
| --- | --- | --- |
| {airline: {id: NA,},} | foo | {airline: {id: NA,},flight: foo,} |

### 例子 2: 基本案例

参数值:

- Expression:value
- Locator: flight
- Struct:struct
| struct | value | 输出 |
| --- | --- | --- |
| {airline: {id: FE,},} | {id: 1,} | {airline: {id: FE,},flight: {id: 1,},} |

### 例子 3: 基本案例

参数值:

- Expression:value
- Locator: airline.id
- Struct:struct
| struct | value | 输出 |
| --- | --- | --- |
| {airline: {id: NA,},} | 1 | {airline: {id: 1,},} |
| {airline: {id: FE,},} | 2 | {airline: {id: 2,},} |

### 例子 4: 空值案例

参数值:

- Expression:value
- Locator: airline.id
- Struct:struct
| struct | value | 输出 |
| --- | --- | --- |
| null | null | null |
| null | 1 | null |
| {airline: {id: FE,},} | null | {airline: {id:null,},} |
