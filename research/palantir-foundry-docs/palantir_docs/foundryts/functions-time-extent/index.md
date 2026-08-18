来源: https://palantir.com/docs/zh/foundry/foundryts/functions-time-extent/

# foundryts.functions.time_extent

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.time_extent

## foundryts.functions.time_extent()

返回一个提取单个时间序列的时间范围（最早和最晚时间戳）的函数。

返回的函数通过识别给定时间序列中第一个到最后一个时间戳的范围来计算时间范围。

- 返回值:一个接受单个时间序列并返回其时间范围的函数。数据框包含一行数据，包含时间范围。
- 返回类型:(函数节点) -> SummarizerNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| extent.earliest_timestamp | pandas.Timestamp | 序列中第一个点的时间戳。 |
| extent.latest_timestamp | pandas.Timestamp | 序列中最后一个点的时间戳。 |

## 示例

```
Copied!1
2
3
4
>>> time_ext = F.time_extent()(series)
>>> time_ext.to_pandas()
      extent.earliest_timestamp       extent.latest_timestamp
0 1970-01-01 00:00:00.000000001 1970-01-01 00:00:00.000123450
```

```
Copied!1
2
3
4
# 这段代码计算一个时间序列的时间范围。
# 首先，通过 F.time_extent() 函数对 series 进行处理，得到时间范围 time_ext。
# 然后，调用 time_ext.to_pandas() 方法将时间范围转换为 Pandas 数据框格式。
# 输出结果显示了时间序列的最早时间戳和最晚时间戳。
```
