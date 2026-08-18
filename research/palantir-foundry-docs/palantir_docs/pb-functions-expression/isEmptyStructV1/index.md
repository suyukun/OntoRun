来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/isEmptyStructV1/

# 是否为空结构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 是否为空结构

> 支持于: 批处理

支持于: 批处理

如果输入是一个空结构，则返回true，并递归检查内部数组和结构。

表达式类别: 布尔

## 声明的参数

- 表达式- 计算此结构是否为空或具有非空字段。Expression<Struct>
输出类型:布尔

## 示例

### 示例 1: 基础案例

参数值:

- 表达式:struct
| struct | 输出 |
| --- | --- |
| {airline: {id:null,name:null,},tail_no:null,} | true |
| {airline: {id: NA,name:null,},tail_no:null,} | false |

### 示例 2: 基础案例

参数值:

- 表达式:struct
| struct | 输出 |
| --- | --- |
| {airline: {ids:null,name:null,},tail_no:null,} | true |
| {airline: {ids: [null],name:null,},tail_no:null,} | true |
| {airline: {ids: [ foo, bar ],name:null,},tail_no:null,} | false |
| {airline: {ids: [ foo,null],name:null,},tail_no:null,} | false |

### 示例 3: 基础案例

参数值:

- 表达式:struct
| struct | 输出 |
| --- | --- |
| {airline: {name:null,},ids:null,tail_no:null,} | true |

### 示例 4: 基础案例

参数值:

- 表达式:struct
| struct | 输出 |
| --- | --- |
| {airline: {ids: {foo ->null,},name:null,},tail_no:null,} | true |
| {airline: {ids: {foo -> bar,},name:null,},tail_no:null,} | false |
| {airline: {ids: {foo -> bar,foo1 ->null,},name:null,},tail_no:null,} | false |

### 示例 5: 基础案例

参数值:

- 表达式:struct
| struct | 输出 |
| --- | --- |
| {airline: {ids: [ {airline: {ids: [null]... | true |
| {airline: {ids: [ {airline: {ids: [ foo, bar... | false |
