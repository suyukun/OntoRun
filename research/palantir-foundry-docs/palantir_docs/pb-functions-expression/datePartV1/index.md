来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/datePartV1/

# 提取日期部分

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 提取日期部分

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

提取日期的一部分，如年份或星期几。

表达式类别: 日期时间

## 声明参数

- Expression- 要提取的日期。Expression<Date | Timestamp>
- Part- 要提取的日期部分。Enum<Day of month, Day of week, Day of year, Month, Quarter, Week of year, Year>
输出类型:Integer

## 示例

### 示例 1: 基本情况

参数值:

- Expression: 2022-02-10T10:00:00Z
- Part:DAY_OF_MONTH
输出:10

### 示例 2: 基本情况

参数值:

- Expression: 2022-02-10T10:00:00Z
- Part:DAY_OF_WEEK
输出:4

### 示例 3: 基本情况

参数值:

- Expression: 2022-02-10T10:00:00Z
- Part:DAY_OF_YEAR
输出:41

### 示例 4: 基本情况

参数值:

- Expression: 2022-02-10
- Part:MONTH
输出:2

### 示例 5: 基本情况

参数值:

- Expression: 2022-02-10
- Part:QUARTER
输出:1

### 示例 6: 基本情况

描述: 一年的周从星期一开始，星期天结束参数值:

- Expression: 2024-01-14T10:00:00Z
- Part:WEEK_OF_YEAR
输出:2

### 示例 7: 基本情况

描述: 一年的周遵循ISO 8601定义的闰周参数值:

- Expression: 2027-01-01T10:00:00Z
- Part:WEEK_OF_YEAR
输出:53

### 示例 8: 基本情况

参数值:

- Expression: 2022-02-10
- Part:YEAR
输出:2022

### 示例 9: 空值情况

参数值:

- Expression:date
- Part:YEAR
| date | 输出 |
| --- | --- |
| null | null |
