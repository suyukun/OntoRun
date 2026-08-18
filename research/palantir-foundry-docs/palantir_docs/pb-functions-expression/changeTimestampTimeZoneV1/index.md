来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/changeTimestampTimeZoneV1/

# 更改时间戳时区

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 更改时间戳时区

> 支持于: 批处理

支持于: 批处理

更改时间戳的时区。

表达式类别: 日期时间

## 声明的参数

- 输出时区- 目标时区。TimeZone
- 时间戳- 时间戳列。Expression<Timestamp>
- 非必填输入时区- 当前时间戳记录的时区。Expression<字符串>
输出类型:Timestamp

## 示例

### 示例 1: 基本情况

参数值:

- 输出时区: America/Chicago
- 时间戳: 2020-04-28T05:09:00Z
- 输入时区: US/Eastern
输出:2020-04-28T04:09:00Z

### 示例 2: 基本情况

参数值:

- 输出时区: Australia/Sydney
- 时间戳:timestamp
- 输入时区:time_zone
| timestamp | time_zone | 输出 |
| --- | --- | --- |
| 2020-04-28T10:09:00Z | US/Eastern | 2020-04-29T00:09:00Z |
| 2020-04-28T10:09:00Z | UTC | 2020-04-28T20:09:00Z |

### 示例 3: 空值情况

参数值:

- 输出时区: US/Eastern
- 时间戳: 2020-04-28T10:09:00Z
- 输入时区:null
输出:2020-04-28T06:09:00Z

### 示例 4: 空值情况

参数值:

- 输出时区: Australia/Sydney
- 时间戳:timestamp
- 输入时区:time_zone
| timestamp | time_zone | 输出 |
| --- | --- | --- |
| null | US/Eastern | null |
| null | null | null |
| 2020-04-28T10:09:00Z | null | 2020-04-28T20:09:00Z |
