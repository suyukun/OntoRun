来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/dateAddV2/

# 向日期添加值

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 向日期添加值

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回 'start' 之后 'value' 天/周/月/季度/年的日期。

表达式类别: 日期时间

## 声明的参数

- Date- 要添加值的日期。Expression<Date>
- Unit- 'value' 参数的日期单位。Enum<Days, Months, Quarters, Weeks, Years>
- Value- 要添加的天数/周数/季度数/年数。Expression<Integer>
输出类型:Date

## 示例

### 示例 1: 基本案例

参数值:

- Date: 2022-02-01
- Unit:DAYS
- Value: 2
输出:2022-02-03

### 示例 2: 基本案例

参数值:

- Date: 2022-02-01
- Unit:MONTHS
- Value: 2
输出:2022-04-01

### 示例 3: 基本案例

参数值:

- Date: 2022-02-01
- Unit:QUARTERS
- Value: 2
输出:2022-08-01

### 示例 4: 基本案例

参数值:

- Date: 2022-02-01
- Unit:YEARS
- Value: 2
输出:2024-02-01

### 示例 5: 空值案例

参数值:

- Date:date
- Unit:YEARS
- Value:value
| date | value | 输出 |
| --- | --- | --- |
| 2022-02-01 | null | null |
| null | 2 | null |
| null | null | null |
