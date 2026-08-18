来源: https://palantir.com/docs/zh/foundry/foundryts/functions-time-range/

# foundryts.functions.time_range

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.time_range

## foundryts.functions.time_range(start=None, end=None)

返回一个函数，用于筛选单个时间序列到指定的时间范围。

每个时间范围都作为一个独立的序列。为查询设置时间范围会使其更高效，因为查询只会读取时间范围内的点，而不是整个时间序列的所有点。这对于对时间序列的区间进行操作也很有用。

- 参数:start(int,str,datetime.datetime,非必填) – 时间范围的起始点（包含）。整数被解释为纳秒数。对于更易读的时间段，你可以提供一个datetime.timedelta对象或一个将被解析为pandas.Timedelta的字符串。字符串输入应遵循pandas.to_timedelta识别的格式，例如‘1 day’、‘1 hour’、‘10 minutes’或‘42s’。（默认是时间序列的第一个点）end(int,str,datetime.datetime,非必填) – 时间范围的终点（不包含）。整数被解释为纳秒数。对于更易读的时间段，你可以提供一个datetime.timedelta对象或一个将被解析为pandas.Timedelta的字符串。字符串输入应遵循pandas.to_timedelta识别的格式，例如‘1 day’、‘1 hour’、‘10 minutes’或‘42s’。（默认是时间序列的最后一个点）
- start(int,str,datetime.datetime,非必填) – 时间范围的起始点（包含）。整数被解释为纳秒数。对于更易读的时间段，你可以提供一个datetime.timedelta对象或一个将被解析为pandas.Timedelta的字符串。字符串输入应遵循pandas.to_timedelta识别的格式，例如‘1 day’、‘1 hour’、‘10 minutes’或‘42s’。（默认是时间序列的第一个点）
- end(int,str,datetime.datetime,非必填) – 时间范围的终点（不包含）。整数被解释为纳秒数。对于更易读的时间段，你可以提供一个datetime.timedelta对象或一个将被解析为pandas.Timedelta的字符串。字符串输入应遵循pandas.to_timedelta识别的格式，例如‘1 day’、‘1 hour’、‘10 minutes’或‘42s’。（默认是时间序列的最后一个点）
- 返回:接受单个时间序列作为输入并返回筛选后的时间范围的函数。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | str |

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
11
12
>>> series = F.points((1, 1.0), (101, 2.0), (200, 4.0), (201, 8.0), name="series")
# 创建一个时间序列对象，包含四个数据点，每个数据点由一个时间戳和一个值组成。
# 参数name="series"用于为这个序列命名。

>>> series.to_pandas()
# 将时间序列对象转换为Pandas数据框格式。
                    timestamp  value
0 1970-01-01 00:00:00.000000001    1.0
1 1970-01-01 00:00:00.000000101    2.0
2 1970-01-01 00:00:00.000000200    4.0
3 1970-01-01 00:00:00.000000201    8.0
# 打印转换后的Pandas数据框，其中包含每个时间戳对应的值。
```

```
Copied!1
2
3
4
5
6
7
>>> time_range = F.time_range(start=200, end=201)(series)
# 创建一个时间范围，范围从时间戳200到201，并应用于`series`数据
>>> time_range.to_pandas()
# 将时间范围转换为Pandas DataFrame格式
                      timestamp  value
0 1970-01-01 00:00:00.000000200    4.0
1 1970-01-01 00:00:00.000000201    8.0
```

```
Copied!1
2
3
4
5
6
7
>>> smaller_time_range = F.time_range(start=200, end=201)(series)
# 使用 F.time_range 函数，从 `series` 中提取时间范围在 200 到 201 的数据
>>> smaller_time_range.to_pandas()
# 将提取后的数据转换为 Pandas DataFrame 格式
                    timestamp  value
0 1970-01-01 00:00:00.000000200    4.0
# 输出结果显示时间戳和对应的值
```

```
Copied!1
2
3
4
5
6
>>> unbounded_start_range = F.time_range(end=201)(series)
>>> unbounded_start_range.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    1.0
1 1970-01-01 00:00:00.000000101    2.0
2 1970-01-01 00:00:00.000000200    4.0
```

这个代码片段演示了如何使用F.time_range创建一个时间范围对象，该对象从一个未绑定的起始时间到一个指定的结束时间（201）。然后，使用to_pandas()方法将其转换为 Pandas DataFrame 格式。

- F.time_range(end=201)：创建一个时间范围对象，该范围的结束时间为时间戳201。
- unbounded_start_range.to_pandas()：将时间范围对象转换为 Pandas DataFrame，以便于数据处理和查看。
结果表明，该时间范围从1970年1月1日开始，数据点有三个，分别在不同的纳秒时间戳下具有不同的值。

```
Copied!1
2
3
4
5
6
>>> unbounded_end_range = F.time_range(start=101)(series)
>>> unbounded_end_range.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000101    2.0
1 1970-01-01 00:00:00.000000200    4.0
2 1970-01-01 00:00:00.000000201    8.0
```

```
Copied!1
# 生成一个以时间戳为起点的时间范围，并将结果转换为Pandas DataFrame格式
```
