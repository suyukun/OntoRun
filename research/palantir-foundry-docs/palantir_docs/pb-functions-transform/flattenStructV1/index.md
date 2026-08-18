来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/flattenStructV1/

# 扁平化结构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 扁平化结构

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

将结构中的所有字段转换为输出数据集中列。

变换类别: 结构

## 声明的参数

- 数据集- 包含结构列的数据集。表格
- 表达式- 评估为将被扁平化的结构列的表达式。表达式<结构>
- 最大深度- 指定嵌套结构将被扁平化的深度级别。字面值<整数>
- 非必填列前缀- 为在扁平化过程中创建的所有列添加前缀。字面值<字符串>
- 非必填分隔符- 分隔来自嵌套结构的字段名称。字面值<字符串>
## 示例

### 示例 1: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 表达式:raw
- 最大深度: 2
- 列前缀: new_
- 分隔符:null
输入:

| raw |
| --- |
| {airline: {id: NA,name: new air,},tail_no: NA-123,} |
| {airline: {id: FA,name: foundry airways,},tail_no: FA-123,} |

输出:

| new_airline_name | new_airline_id | new_tail_no | raw |
| --- | --- | --- | --- |
| new air | NA | NA-123 | {airline: {id: NA,name: new air,},tail_no: NA-123,} |
| foundry airways | FA | FA-123 | {airline: {id: FA,name: foundry airways,},tail_no: FA-123,} |

### 示例 2: 基本情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 表达式:raw
- 最大深度: 2
- 列前缀: new_
- 分隔符: #SEPARATOR#
输入:

| raw |
| --- |
| {airline: {id: NA,name: new air,},tail_no: NA-123,} |
| {airline: {id: FA,name: foundry airways,},tail_no: FA-123,} |

输出:

| new_airline#SEPARATOR#name | new_airline#SEPARATOR#id | new_tail_no | raw |
| --- | --- | --- | --- |
| new air | NA | NA-123 | {airline: {id: NA,name: new air,},tail_no: NA-123,} |
| foundry airways | FA | FA-123 | {airline: {id: FA,name: foundry airways,},tail_no: FA-123,} |

### 示例 3: 空值情况

参数值:

- 数据集: ri.foundry.main.dataset.a
- 表达式:raw
- 最大深度: 2
- 列前缀: new_
- 分隔符:null
输入:

| raw |
| --- |
| null |
| {airline:null,tail_no: NA-123,} |
| {airline: {id: FA,name:null,},tail_no: FA-123,} |

输出:

| new_airline_name | new_airline_id | new_tail_no | raw |
| --- | --- | --- | --- |
| null | null | null | null |
| null | null | NA-123 | {airline:null,tail_no: NA-123,} |
| null | FA | FA-123 | {airline: {id: FA,name:null,},tail_no: FA-123,} |
