来源: https://palantir.com/docs/zh/foundry/foundryts/functions-time-shift/

# foundryts.functions.time_shift

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.time_shift

## foundryts.functions.time_shift(duration)

返回一个函数，该函数会将单个时间序列的所有时间戳按指定的持续时间向前或向后移动。

对于一个具有点(timestamp, value)的源时间序列，在按duration移动后，结果时间偏移的时间序列将具有点(timestamp + duration, value)。正的duration移动值将使时间戳向未来移动，而负的duration值将使时间戳向过去移动。

- 参数:duration(int,datetime.timedelta,str) – 指定的时间量，以整数、datetime.timedelta 对象或字符串的形式向前或向后移动时间戳。整数被解释为纳秒数。对于更易读的持续时间，可以提供一个 datetime.timedelta 对象或一个将被解析为 pandas.Timedelta 的字符串。字符串输入应遵循 pandas.to_timedelta 识别的格式，如 ‘1 day’, ‘1 hour’, ‘10 minutes’, 或 ’42s’。
- 返回:一个接受单个时间序列作为输入并返回时间偏移时间序列的函数。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的偏移时间戳 |
| value | float | str |

timestamp_scale(),value_shift()

## 示例

```
Copied!1
2
3
4
5
6
7
8
9
10
>>> time_shifted = F.time_shift(1000)(series)
# 使用函数F.time_shift(1000)对时间序列进行时间偏移，偏移量为1000个单位
>>> time_shifted.to_pandas()
# 将偏移后的时间序列转换为Pandas DataFrame格式进行查看
                      timestamp    value
0 1970-01-01 00:00:00.000001100  0.00000
1 1970-01-01 00:00:00.000001200      inf
2 1970-01-01 00:00:00.000001300  3.14159
3 1970-01-01 00:00:02.147484647  1.00000
# 显示时间戳和对应的数值，注意第二行的值为无穷大（inf）
```
