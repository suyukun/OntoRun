来源: https://palantir.com/docs/zh/foundry/foundryts/functions-rolling-aggregate/

# foundryts.functions.rolling_aggregate

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.rolling_aggregate

## foundryts.functions.rolling_aggregate(aggregate, window)

返回一个在单一时间序列上对滚动窗口内值进行聚合的函数。

滚动窗口是一个移动的数据点子集，它结束于当前时间戳（包括在内），并跨越一个指定的持续时间（窗口大小）。当新的数据点被添加时，如果它们在指定的持续时间之外，旧的数据点将从窗口中移出。

滚动窗口通常用于平滑数据、检测趋势和减少时间序列分析中的噪声。

支持的聚合函数：

| 聚合函数 | 描述 |
| --- | --- |
| min | 窗口内的最小值。 |
| max | 窗口内的最大值。 |
| count | 窗口内的点的数量。 |
| sum | 窗口内值的总和。 |
| product | 窗口内值的乘积。 |
| mean | 窗口内值的平均值。 |
| standard_deviation | 窗口内值的标准差。 |
| difference | 窗口内第一个点的值与最后一个点的值之间的差异，提供窗口内的相对更改。 |
| percent_change | 窗口内第一个点的值到最后一个点的值的百分比变化，提供窗口内的相对变化率。 |
| first | 窗口内的第一个值。 |
| last | 窗口内的最后一个值。 |

- 参数:aggregate(str) – 要应用的聚合函数。参见上面的聚合函数。window(str|int|datetime.timedelta|pandas.Timedelta) – 滚动窗口的持续时间，它决定了在任意时间评估多少个点，例如，5ms，或5e6。
- aggregate(str) – 要应用的聚合函数。参见上面的聚合函数。
- window(str|int|datetime.timedelta|pandas.Timedelta) – 滚动窗口的持续时间，它决定了在任意时间评估多少个点，例如，5ms，或5e6。
- 返回:一个函数，该函数接受单一时间序列作为输入，并在滚动窗口内为每个点计算指定的聚合。
- 返回类型:(FunctionNode) -> FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

cumulative_aggregate(),periodic_aggregate()

此函数仅适用于数值系列。

## 示例

```
Copied!1
2
3
4
5
6
>>> series = F.points(
...     (2, 10.0), (5, 20.0), (6, 30.0), (7, 40.0), (8, 50.0), (12, 60.0), name="series"
... )
# 这里使用了一个假设的函数 F.points 创建一个点序列（可能是一个时间序列或数值序列）
# 每个点由一个 x 坐标（整数）和一个 y 坐标（浮点数）组成
# 这些点被命名为 "series"
```

```
Copied!1
2
3
4
5
6
7
8
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000002   10.0
1 1970-01-01 00:00:00.000000005   20.0
2 1970-01-01 00:00:00.000000006   30.0
3 1970-01-01 00:00:00.000000007   40.0
4 1970-01-01 00:00:00.000000008   50.0
5 1970-01-01 00:00:00.000000012   60.0
```

这段代码使用series.to_pandas()将一个时间序列对象转换为 Pandas DataFrame 格式。结果显示了两个列：timestamp和value。timestamp列表示时间戳，以纳秒为单位，value列则表示对应的数值。

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
>>> rolling_difference = F.rolling_aggregate("difference", "3ns")(series)
>>> rolling_difference.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000002    0.0  # 在时间窗口内的差值为 0.0
1 1970-01-01 00:00:00.000000005    0.0  # 在时间窗口内的差值为 0.0
2 1970-01-01 00:00:00.000000006   10.0  # 在时间窗口内的差值为 10.0
3 1970-01-01 00:00:00.000000007   20.0  # 在时间窗口内的差值为 20.0
4 1970-01-01 00:00:00.000000008   20.0  # 在时间窗口内的差值为 20.0
5 1970-01-01 00:00:00.000000012    0.0  # 在时间窗口内的差值为 0.0
```

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
13
>>> rolling_percentage_change = F.rolling_aggregate("percent_change", "3ns")(series)
# 使用3纳秒的窗口计算滚动百分比变化

>>> rolling_percentage_change.to_pandas()
# 将结果转换为pandas数据框

                      timestamp     value
0 1970-01-01 00:00:00.000000002  0.000000
1 1970-01-01 00:00:00.000000005  0.000000
2 1970-01-01 00:00:00.000000006  0.500000
3 1970-01-01 00:00:00.000000007  1.000000
4 1970-01-01 00:00:00.000000008  0.666667
5 1970-01-01 00:00:00.000000012  0.000000
```

该代码段通过F.rolling_aggregate函数计算给定时间序列的滚动百分比变化。滚动窗口的大小设置为3纳秒。最后通过to_pandas()方法将结果转换为pandas数据框格式，以便于进一步分析和处理。
