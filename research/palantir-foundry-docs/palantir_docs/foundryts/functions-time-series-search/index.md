来源: https://palantir.com/docs/zh/foundry/foundryts/functions-time-series-search/

# foundryts.functions.time_series_search

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.time_series_search

## foundryts.functions.time_series_search(predicate, labels=None, start=None, end=None, interval_values=None, before='nearest', internal='default', after='nearest', min_duration=None, max_duration=None)

返回一个函数，该函数将使用提供的条件在时间序列上搜索区间。

该函数将返回条件为true的时间区间。

每个返回的区间都会被评估为相关的statistics()。interval_values中的dsl()公式将用于评估最终的statistics()。

指定的插值策略用于填充缺失的时间戳。有关插值和策略的更多详细信息，请参见interpolate()。

此函数生成的区间等同于Quiver中的事件。当时间序列展示区间行为且分析时间序列需要访问区间时，这特别有用。然后，每个时间序列可以使用time_range()拆分为范围，以便每个区间成为新的time_range()，并且可以在每个时间范围上独立应用操作。

- 参数：predicate(str) – 使用dsl()条件程序搜索区间的条件。labels(Union[str,List[str]],非必填) – 每个输入时间序列的别名，以便在predicate和interval_values中引用它们（默认为[‘a’, ‘b’, …, ‘aa’, ‘ab’, …]）。start(int|datetime|str,非必填) – 开始在时间序列中评估区间的时间戳（包含）。对于与start时间戳重叠的区间，完整区间将包含在输出中（默认为pandas.Timestamp.min）。end(int|datetime|str,非必填) – 结束在时间序列中评估区间的时间戳（不包含）。对于与end时间戳重叠的区间，完整区间将包含在输出中（默认为pandas.Timestamp.max`）。interval_values(str,非必填) – 用于变换区间统计计算值的dsl()程序。这对于非数值输入时间序列是必需的，因为统计无法在非数值数据上计算。（默认为第一个输入时间序列）。before(Union[str,List[str]],非必填) – 在系列中的第一个点之前进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效策略（默认为NEAREST）。internal(Union[str,List[str]],非必填) – 在现有点之间进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效值（数值默认为LINEAR，枚举时间序列默认为PREVIOUS）。after(Union[str,List[str]],非必填) – 在系列中的最后一个点之后进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效策略（默认为NEAREST）。min_duration(int|str|datetime.timedelta,非必填) – 条件必须为true的最短持续时间，以使时间范围符合条件成为区间。max_duration(int|str|datetime.timedelta,非必填) – 条件必须为true的最长持续时间，以使时间范围符合条件成为区间。
- predicate(str) – 使用dsl()条件程序搜索区间的条件。
- labels(Union[str,List[str]],非必填) – 每个输入时间序列的别名，以便在predicate和interval_values中引用它们（默认为[‘a’, ‘b’, …, ‘aa’, ‘ab’, …]）。
- start(int|datetime|str,非必填) – 开始在时间序列中评估区间的时间戳（包含）。对于与start时间戳重叠的区间，完整区间将包含在输出中（默认为pandas.Timestamp.min）。
- end(int|datetime|str,非必填) – 结束在时间序列中评估区间的时间戳（不包含）。对于与end时间戳重叠的区间，完整区间将包含在输出中（默认为pandas.Timestamp.max`）。
- interval_values(str,非必填) – 用于变换区间统计计算值的dsl()程序。这对于非数值输入时间序列是必需的，因为统计无法在非数值数据上计算。（默认为第一个输入时间序列）。
- before(Union[str,List[str]],非必填) – 在系列中的第一个点之前进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效策略（默认为NEAREST）。
- internal(Union[str,List[str]],非必填) – 在现有点之间进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效值（数值默认为LINEAR，枚举时间序列默认为PREVIOUS）。
- after(Union[str,List[str]],非必填) – 在系列中的最后一个点之后进行插值的策略，可以是每个系列的列表，从interpolate()中使用一个有效策略（默认为NEAREST）。
- min_duration(int|str|datetime.timedelta,非必填) – 条件必须为true的最短持续时间，以使时间范围符合条件成为区间。
- max_duration(int|str|datetime.timedelta,非必填) – 条件必须为true的最长持续时间，以使时间范围符合条件成为区间。
- 返回值：一个函数，该函数返回满足输入时间序列条件的区间的统计信息。
- 返回类型：(Union[FunctionNode, NodeCollections]) -> SummaryNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| count | int | 区间中的数据点数量。 |
| earliest_point.timestamp | datetime | 区间中第一个数据点的时间戳。 |
| earliest_point.value | float | 区间中第一个数据点的值。 |
| end_timestamp | datetime | 区间结束的时间戳（不包含）。 |
| largest_point.timestamp | datetime | 区间中具有最大值的数据点的时间戳。 |
| largest_point.value | float | 区间中的最大值。 |
| latest_point.timestamp | datetime | 区间中最近数据点的时间戳。 |
| latest_point.value | float | 区间中最近数据点的值。 |
| mean | float | 区间中所有数据点的平均值。 |
| smallest_point.timestamp | datetime | 区间中具有最小值的数据点的时间戳。 |
| smallest_point.value | float | 区间中的最小值。 |
| start_timestamp | datetime | 区间中第一个数据点的时间戳。 |
| standard_deviation | float | 区间中数据点的标准偏差。 |
| duration.seconds | int | 区间的持续时间（以秒为单位）。 |
| duration.subsecond_nanos | int | 区间的持续时间（以纳秒为单位）。 |

interpolate(),statistics()

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
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
>>> discrete_series = F.points(
...     (0, 1.0),
...     (1, 2.0),
...     (2, 2.0),
...     (3, 3.0),
...     (4, 5.0),
...     (5, 6.0),
...     (6, 4.0),
...     (7, 2.0),
...     (8, 6.0),
...     (9, 7.0),
...     (10, 8.0),
...     (11, 10.0),
...     (12, 11.0),
...     name="discrete",  # 设置时间序列的名称为 "discrete"
... )
>>> discrete_series.to_pandas()
                       timestamp  value
0  1970-01-01 00:00:00.000000000    1.0
1  1970-01-01 00:00:00.000000001    2.0
2  1970-01-01 00:00:00.000000002    2.0
3  1970-01-01 00:00:00.000000003    3.0
4  1970-01-01 00:00:00.000000004    5.0
5  1970-01-01 00:00:00.000000005    6.0
6  1970-01-01 00:00:00.000000006    4.0
7  1970-01-01 00:00:00.000000007    2.0
8  1970-01-01 00:00:00.000000008    6.0
9  1970-01-01 00:00:00.000000009    7.0
10 1970-01-01 00:00:00.000000010    8.0
11 1970-01-01 00:00:00.000000011   10.0
12 1970-01-01 00:00:00.000000012   11.0
```

该代码段创建了一个离散时间序列discrete_series，其中每个点由一个时间戳（整数）和一个对应的值组成。然后，它将该序列转换为 Pandas DataFrame 格式，其中时间戳被表示为相应的时间，并显示其值。时间戳从1970年1月1日开始，以纳秒为单位增量。

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
14
>>> even_search = F.time_series_search(
...     predicate="discrete % 2 == 0",  # 筛选条件：只选择偶数
...     interval_values="discrete",     # 使用离散值作为区间值
...     labels="discrete",              # 使用离散值作为标签
... )(discrete_series)
# 找到3个区间：
# 区间1: [(1, 2.0), (2, 2.0)]
# 区间2: [(5, 6.0), (6, 4.0), (7, 2.0), (8, 6.0)]
# 区间3: [(10, 8.0), (11, 10.0)]
>>> even_search.to_pandas()
   count  duration.seconds  duration.subsecond_nanos      earliest_point.timestamp  earliest_point.value                      end_time       largest_point.timestamp  largest_point.value        latest_point.timestamp  latest_point.value  mean      smallest_point.timestamp  smallest_point.value  standard_deviation                    start_time
0      2                 0                         2 1970-01-01 00:00:00.000000001                   2.0 1970-01-01 00:00:00.000000003 1970-01-01 00:00:00.000000002                  2.0 1970-01-01 00:00:00.000000002                 2.0   2.0 1970-01-01 00:00:00.000000002                   2.0            0.000000 1970-01-01 00:00:00.000000001
1      4                 0                         4 1970-01-01 00:00:00.000000005                   6.0 1970-01-01 00:00:00.000000009 1970-01-01 00:00:00.000000008                  6.0 1970-01-01 00:00:00.000000008                 6.0   4.5 1970-01-01 00:00:00.000000007                   2.0            1.658312 1970-01-01 00:00:00.000000005
2      2                 0                         2 1970-01-01 00:00:00.000000010                   8.0 1970-01-01 00:00:00.000000012 1970-01-01 00:00:00.000000011                 10.0 1970-01-01 00:00:00.000000011                10.0   9.0 1970-01-01 00:00:00.000000010                   8.0            1.000000 1970-01-01 00:00:00.000000010
```

这段代码通过time_series_search函数找到离散时间序列中所有偶数的区间，并将结果转换为 Pandas 数据框格式。筛选出的区间分别包含2个、4个和2个点。每个区间的详细统计信息如计数、持续时间、最早和最新点的时间戳及值、平均值和标准偏差等都在输出中展示。

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
14
>>> search_formula = F.time_series_search(
...     predicate="discrete % 2 == 0",  # 谓词：筛选出所有偶数的离散值
...     interval_values="discrete * 2",  # 将筛选出的离散值乘以2作为区间值
...     labels="discrete",  # 使用离散值作为标签
... )(discrete_series)
# 3个区间包含点（值翻倍后）：
# 区间 1: [(1, 4.0), (2, 4.0)]
# 区间 2: [(5, 12.0), (6, 8.0), (7, 4.0), (8, 12.0)]
# 区间 3: [(10, 16.0), (11, 20.0)]
>>> search_formula.to_pandas()
   count  duration.seconds  duration.subsecond_nanos      earliest_point.timestamp  earliest_point.value                      end_time       largest_point.timestamp  largest_point.value        latest_point.timestamp  latest_point.value  mean      smallest_point.timestamp  smallest_point.value  standard_deviation                    start_time
0      2                 0                         2 1970-01-01 00:00:00.000000001                   4.0 1970-01-01 00:00:00.000000003 1970-01-01 00:00:00.000000002                  4.0 1970-01-01 00:00:00.000000002                 4.0   4.0 1970-01-01 00:00:00.000000002                   4.0            0.000000 1970-01-01 00:00:00.000000001
1      4                 0                         4 1970-01-01 00:00:00.000000005                  12.0 1970-01-01 00:00:00.000000009 1970-01-01 00:00:00.000000008                 12.0 1970-01-01 00:00:00.000000008                12.0   9.0 1970-01-01 00:00:00.000000007                   4.0            3.316625 1970-01-01 00:00:00.000000005
2      2                 0                         2 1970-01-01 00:00:00.000000010                  16.0 1970-01-01 00:00:00.000000012 1970-01-01 00:00:00.000000011                 20.0 1970-01-01 00:00:00.000000011                20.0  18.0 1970-01-01 00:00:00.000000010                  16.0            2.000000 1970-01-01 00:00:00.000000010
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
>>> min_duration_search = F.time_series_search(
...     predicate="discrete % 2 == 0",  # 只选择值为偶数的间隔
...     interval_values="discrete",
...     labels="discrete",
...     min_duration="3ns",  # 最小持续时间为3纳秒
... )(discrete_series)
# 第一个和最后一个间隔被过滤，因为持续时间 < 3
# 1 个满足条件的间隔包含以下点：
# [(5, 6.0), (6, 4.0), (7, 2.0), (8, 6.0)]
>>> min_duration_search.to_pandas()
   count  duration.seconds  duration.subsecond_nanos      earliest_point.timestamp  earliest_point.value                      end_time       largest_point.timestamp  largest_point.value        latest_point.timestamp  latest_point.value  mean      smallest_point.timestamp  smallest_point.value  standard_deviation                    start_time
0      4                 0                         4 1970-01-01 00:00:00.000000005                   6.0 1970-01-01 00:00:00.000000009 1970-01-01 00:00:00.000000008                  6.0 1970-01-01 00:00:00.000000008                 6.0   4.5 1970-01-01 00:00:00.000000007                   2.0            1.658312 1970-01-01 00:00:00.000000005
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
14
>>> max_duration_search = F.time_series_search(
...     predicate="discrete % 2 == 0",  # 筛选条件：离散值是偶数
...     interval_values="discrete",  # 间隔值为离散值
...     labels="discrete",  # 标签为离散值
...     max_duration="3ns",  # 最大间隔持续时间为3纳秒
... )(discrete_series)
# 第二个间隔被过滤，因为持续时间 > 3
# 2个间隔包含以下点：
# 间隔 1: [(1, 2.0), (2, 2.0)]
# 间隔 2: [(10, 8.0), (11, 10.0)]
>>> max_duration_search.to_pandas()
   count  duration.seconds  duration.subsecond_nanos      earliest_point.timestamp  earliest_point.value                      end_time       largest_point.timestamp  largest_point.value        latest_point.timestamp  latest_point.value  mean      smallest_point.timestamp  smallest_point.value  standard_deviation                    start_time
0      2                 0                         2 1970-01-01 00:00:00.000000001                   2.0 1970-01-01 00:00:00.000000003 1970-01-01 00:00:00.000000002                  2.0 1970-01-01 00:00:00.000000002                 2.0   2.0 1970-01-01 00:00:00.000000002                   2.0                 0.0 1970-01-01 00:00:00.000000001
1      2                 0                         2 1970-01-01 00:00:00.000000010                   8.0 1970-01-01 00:00:00.000000012 1970-01-01 00:00:00.000000011                 10.0 1970-01-01 00:00:00.000000011                10.0   9.0 1970-01-01 00:00:00.000000010                   8.0                 1.0 1970-01-01 00:00:00.000000010
```

这段代码使用F.time_series_search函数在给定的discrete_series数据中寻找满足条件的时间间隔。筛选条件为离散值为偶数，最大间隔持续时间为3纳秒。最终结果转化为Pandas数据框格式，显示每个间隔的统计信息。

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
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
>>> toggle_series = F.points(
...     (0, "OFF"),
...     (1, "ON"),
...     (2, "OFF"),
...     (3, "OFF"),
...     (4, "ON"),
...     (5, "ON"),
...     (6, "ON"),
...     (7, "OFF"),
...     (8, "ON"),
...     (9, "ON"),
...     (10, "OFF"),
...     (11, "OFF"),
...     (12, "ON"),
...     name="toggle",
... )
# 创建一个名为 "toggle" 的时间序列，其中包含每个时间点的状态（"ON" 或 "OFF"）。
>>> toggle_series.to_pandas()
                       timestamp value
0  1970-01-01 00:00:00.000000000   OFF
1  1970-01-01 00:00:00.000000001    ON
2  1970-01-01 00:00:00.000000002   OFF
3  1970-01-01 00:00:00.000000003   OFF
4  1970-01-01 00:00:00.000000004    ON
5  1970-01-01 00:00:00.000000005    ON
6  1970-01-01 00:00:00.000000006    ON
7  1970-01-01 00:00:00.000000007   OFF
8  1970-01-01 00:00:00.000000008    ON
9  1970-01-01 00:00:00.000000009    ON
10 1970-01-01 00:00:00.000000010   OFF
11 1970-01-01 00:00:00.000000011   OFF
12 1970-01-01 00:00:00.000000012    ON
# 将 toggle_series 转换为 Pandas DataFrame 格式，显示每个时间戳及其对应的状态。
>>> cross_series_search = F.time_series_search(
...     predicate='toggle == "ON"',
...     interval_values="discrete",
...     labels=["toggle", "discrete"],
... )([toggle_series, discrete_series])
# 在 toggle_series 中搜索状态为 "ON" 的时间段，并在 discrete_series 中创建相应的时间间隔。
# 4 Intervals in discrete_series created from intervals in toggle_series where predicate is true:
# Interval 1: [(1, 2.0)]
# Interval 2: [(4, 5.0), (5, 6.0), (6, 4.0)]
# Interval 3: [(8, 6.0), (9, 7.0)]
# Interval 4: [(12, 11.0)]
# 在 toggle_series 中状态为 "ON" 的时间段对应的 discrete_series 时间间隔:
# 间隔 1: [(1, 2.0)]
# 间隔 2: [(4, 5.0), (5, 6.0), (6, 4.0)]
# 间隔 3: [(8, 6.0), (9, 7.0)]
# 间隔 4: [(12, 11.0)]
>>> cross_series_search.to_pandas()
   count  duration.seconds  duration.subsecond_nanos      earliest_point.timestamp  earliest_point.value                      end_time       largest_point.timestamp  largest_point.value        latest_point.timestamp  latest_point.value  mean      smallest_point.timestamp  smallest_point.value  standard_deviation                    start_time
0      1                 0                         1 1970-01-01 00:00:00.000000001                   2.0 1970-01-01 00:00:00.000000002 1970-01-01 00:00:00.000000001                  2.0 1970-01-01 00:00:00.000000001                 2.0   2.0 1970-01-01 00:00:00.000000001                   2.0            0.000000 1970-01-01 00:00:00.000000001
1      3                 0                         3 1970-01-01 00:00:00.000000004                   5.0 1970-01-01 00:00:00.000000007 1970-01-01 00:00:00.000000005                  6.0 1970-01-01 00:00:00.000000006                 4.0   5.0 1970-01-01 00:00:00.000000006                   4.0            0.816497 1970-01-01 00:00:00.000000004
2      2                 0                         2 1970-01-01 00:00:00.000000008                   6.0 1970-01-01 00:00:00.000000010 1970-01-01 00:00:00.000000009                  7.0 1970-01-01 00:00:00.000000009                 7.0   6.5 1970-01-01 00:00:00.000000008                   6.0            0.500000 1970-01-01 00:00:00.000000008
3      1                 0                         1 1970-01-01 00:00:00.000000012                  11.0 1970-01-01 00:00:00.000000013 1970-01-01 00:00:00.000000012                 11.0 1970-01-01 00:00:00.000000012                11.0  11.0 1970-01-01 00:00:00.000000012                  11.0            0.000000 1970-01-01 00:00:00.000000012
# 将 cross_series_search 结果转换为 Pandas DataFrame，显示每个间隔的统计信息，包括计数、持续时间、起始和结束时间等。
```
