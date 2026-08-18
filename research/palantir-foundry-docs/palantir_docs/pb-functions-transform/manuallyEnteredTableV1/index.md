来源: https://palantir.com/docs/zh/foundry/pb-functions-transform/manuallyEnteredTableV1/

# 手动输入表

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 手动输入表

> 支持于: 批处理, 流式处理

支持于: 批处理, 流式处理

使用手动输入的表数据创建输出。

变换类别: 其他

## 声明的参数

- Rows- 代表行的结构列表，结构字段代表列名和值。List<Literal<Struct>>
- Schema（非必填） - 如果存在，将被用于在列名和类型的模式。如果未定义，行必须是非空的并将用于推断模式。Type<Struct>
## 示例

### 示例 1: 基本情况

参数值:

- Rows: [{airline: foundry airlines,flight_code: 112,flight_number: XB-123,}, {airline: foundry airlines,flight_code: 533,flight_number: MT-444,}, {airline: new air,flight_code: 934,flight_number: KK-123,}]
- Schema: Struct<flight_code, flight_number, airline>
输入:

| flight_code | flight_number | airline |
| --- | --- | --- |
| 112 | XB-123 | foundry airlines |
| 533 | MT-444 | foundry airlines |
| 934 | KK-123 | new air |

输出:

| flight_code | flight_number | airline |
| --- | --- | --- |
| 112 | XB-123 | foundry airlines |
| 533 | MT-444 | foundry airlines |
| 934 | KK-123 | new air |
