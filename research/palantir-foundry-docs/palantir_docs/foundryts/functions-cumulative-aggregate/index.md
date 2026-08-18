来源: https://palantir.com/docs/zh/foundry/foundryts/functions-cumulative-aggregate/

# foundryts.functions.cumulative_aggregate

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.cumulative_aggregate

## foundryts.functions.cumulative_aggregate(aggregate)

返回一个计算单个时间序列中所有值的累计聚合的函数。

累计聚合是逐步为输入时间序列中的每个点计算的，考虑到所有先前的点，包括当前点。

支持的聚合函数：

| 聚合函数 | 描述 |
| --- | --- |
| min | 时间序列中当前点之前的最小值。 |
| max | 时间序列中当前点之前的最大值。 |
| count | 时间序列中当前点之前的所有点的计数。 |
| sum | 当前点之前的所有点值的总和。 |
| product | 当前点之前的点值的乘积。 |
| mean | 当前点之前的所有点值的平均值。 |
| standard_deviation | 当前点之前的所有点值的标准差。 |
| difference | 当前点值与时间序列中第一个点值之间的差异，提供序列内的相对更改。 |
| percent_change | 当前点值与时间序列中第一个点值之间的百分比更改，提供序列内的相对更改率。 |
| first | 时间序列中第一个点的值。 |
| last | 时间序列中当前（最后）点的值。 |

- 参数:aggregate(str) – 应用于每个点的聚合函数，使用上面聚合函数中的一个值。
- 返回:一个函数，该函数将单个时间序列作为输入，并为每个点计算指定的聚合，考虑到要评估点之前的所有点。
- 返回类型:(FunctionNode) -> FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

rolling_aggregate(),periodic_aggregate()

此函数仅适用于数值序列。

## 例子

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
>>> series = F.points(
...     (2, 10.0), (5, 20.0), (6, 30.0), (7, 40.0), (8, 50.0), (12, 60.0), name="series-1"
... )
# 创建一个数据点序列，名称为 "series-1"。每个数据点由一个时间戳和一个值组成。
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000002   10.0
1 1970-01-01 00:00:00.000000005   20.0
2 1970-01-01 00:00:00.000000006   30.0
3 1970-01-01 00:00:00.000000007   40.0
4 1970-01-01 00:00:00.000000008   50.0
5 1970-01-01 00:00:00.000000012   60.0
# 将数据点序列转换为 Pandas 数据框。时间戳以纳秒为单位从1970年1月1日开始。
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
>>> cumulative_agg = F.cumulative_aggregate("mean")(series)
# 使用累计聚合函数计算“平均值”，对时间序列数据进行处理
>>> cumulative_agg.to_pandas()
# 将结果转换为 Pandas DataFrame 格式以便查看
                      timestamp  value
0 1970-01-01 00:00:00.000000002   10.0
1 1970-01-01 00:00:00.000000005   15.0
2 1970-01-01 00:00:00.000000006   20.0
3 1970-01-01 00:00:00.000000007   25.0
4 1970-01-01 00:00:00.000000008   30.0
5 1970-01-01 00:00:00.000000012   35.0
# 输出结果显示每个时间戳对应的累计平均值
```
