来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/timestampDiffV1/

# 减去时间戳/日期

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 减去时间戳/日期

> 支持于: 批处理, 流处理

支持于: 批处理, 流处理

返回给定时间单位的差值。

表达式类别: 日期时间

## 声明的参数

- End- 减去的结束日期或时间。表达式<日期 | 时间戳>
- Start- 被减去的起始日期或时间。表达式<日期 | 时间戳>
- Unit- 时间单位。枚举<天, 小时, 毫秒, 分钟, 月, 季度, 秒, 周, 年>
输出类型:长整型

## 示例

### 示例 1: 基本情况

参数值:

- End: 2022-10-01T10:00:00Z
- Start: 2022-10-01T09:00:00Z
- Unit:HOURS
输出:1

### 示例 2: 空值情况

参数值:

- End:End
- Start:Start
- Unit:HOURS
| Start | End | 输出 |
| --- | --- | --- |
| null | 2020-01-01 | null |
| 2020-01-01 | null | null |
| null | null | null |
