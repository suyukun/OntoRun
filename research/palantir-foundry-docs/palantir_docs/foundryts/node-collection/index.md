来源: https://palantir.com/docs/zh/foundry/foundryts/node-collection/

# foundryts.NodeCollection

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.NodeCollection

## classfoundryts.NodeCollection(*nodes, **kwargs)

FunctionNode或SummarizerNode的集合。

NodeCollection是一个可迭代对象，可以传递给期望多个时间序列的函数，或用于将集合中的每个节点映射到一个函数。

对于原始序列和点集，NodeCollection的数据框包含一个名为series的额外列，表示点所属的序列。series值将是时间序列同步中设置的系列ID或通过foundryts.functions.points()的别名。

确保不要直接将NodeCollection传递给期望单个输入时间序列的函数，因为这将出错。对于在节点的所有元素上应用相同的函数，使用NodeCollection.map()，它将变换后的点或摘要映射到最终数据框中的系列。请参考FoundryTS函数文档以查看函数的输入数量。

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
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
# 创建一个名为 series-1 的时间序列，包含三个数据点，每个数据点由一个时间戳和一个值组成。

>>> series_1.to_pandas()
# 将 series_1 转换为 Pandas DataFrame 格式，以便更容易地进行数据操作和分析。
                      timestamp  value
0 1970-01-01 00:00:00.000000001  100.0
1 1970-01-01 00:00:00.000000002  200.0
2 1970-01-01 00:00:00.000000003  300.0

>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
# 创建另一个名为 series-2 的时间序列，包含不同的值。

>>> series_2.to_pandas()
# 同样将 series_2 转换为 Pandas DataFrame 格式。
                      timestamp  value
0 1970-01-01 00:00:00.000000001  200.0
1 1970-01-01 00:00:00.000000002  400.0
2 1970-01-01 00:00:00.000000003  600.0
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
>>> nc = NodeCollection([series_1, series_2])
>>> nc.to_pandas()
     series                     timestamp  value
0  series-1 1970-01-01 00:00:00.000000001  100.0
1  series-1 1970-01-01 00:00:00.000000002  200.0
2  series-1 1970-01-01 00:00:00.000000003  300.0
3  series-2 1970-01-01 00:00:00.000000001  200.0
4  series-2 1970-01-01 00:00:00.000000002  400.0
5  series-2 1970-01-01 00:00:00.000000003  600.0
```

此代码片段展示了如何使用NodeCollection类将多个时间序列数据转换为 Pandas DataFrame 格式。NodeCollection被初始化为包含两个系列series_1和series_2。调用to_pandas()方法将这些数据转换为 DataFrame，其中包含三列：series（系列名称）、timestamp（时间戳）、value（数值）。

```
Copied!1
2
3
4
5
6
>>> scatter_plt = F.scatter()(nc) # scatter()函数需要两个输入时间序列
>>> scatter_plt.to_pandas()
   is_truncated  points.first_value  points.second_value              points.timestamp
0         False               100.0                200.0 1970-01-01 00:00:00.000000001
1         False               200.0                400.0 1970-01-01 00:00:00.000000002
2         False               300.0                600.0 1970-01-01 00:00:00.000000003
```

此代码创建一个散点图对象scatter_plt，其中scatter()函数需要正好两个输入时间序列。然后将该对象转换为pandas数据框格式进行查看。

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
>>> scaled_nc = F.scale(10)(nc) # error - scale() works on a single input series
>>> # 错误 - scale() 只能作用于单个输入序列
>>> scaled_nc = nc.map(F.scale(10)) # ok - we're mapping each series in the collection to the result of scale()
>>> # 正确 - 我们将集合中的每个序列映射到 scale() 的结果
>>> scaled_nc.to_pandas()
     series                     timestamp   value
0  series-1 1970-01-01 00:00:00.000000001  1000.0
1  series-1 1970-01-01 00:00:00.000000002  2000.0
2  series-1 1970-01-01 00:00:00.000000003  3000.0
3  series-2 1970-01-01 00:00:00.000000001  2000.0
4  series-2 1970-01-01 00:00:00.000000002  4000.0
5  series-2 1970-01-01 00:00:00.000000003  6000.0
```

#### columns()

返回表示pandas.DataFrame列名的字符串元组，该元组通过将此集合评估为数据框生成。

嵌套对象的键将被展平为一个元组，嵌套键用.连接。

非统一集合将包含集合中每个元素的所有列的并集。

- 返回：包含集合被评估为的结果数据框中列名的元组。
- 返回类型：Tuple[str]
## 示例

```
Copied!1
2
3
4
5
6
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
# 创建两个数据系列：series_1 和 series_2
# series_1 包含点 (1, 100.0), (2, 200.0), (3, 300.0)
# series_2 包含点 (1, 200.0), (2, 400.0), (3, 600.0)
# 使用 name 参数分别命名为 "series-1" 和 "series-2"
```

```
Copied!1
2
3
>>> nc = NodeCollection(series_1, series_2)
>>> nc.columns() # 注意这里有一个额外的 series 列
('series', 'timestamp', 'value')
```

```
Copied!1
2
3
4
>>> dist = F.distribution()(nc)
>>> dist.columns()
('delta', 'distribution_values.count', 'distribution_values.end', 'distribution_values.start',
'end', 'end_timestamp', 'start', 'start_timestamp')
```

这个代码片段展示了如何获取一个分布对象的列名：

- delta: 变化量
- distribution_values.count: 分布值的计数
- distribution_values.end: 分布值的结束位置
- distribution_values.start: 分布值的起始位置
- end: 结束位置
- end_timestamp: 结束时间戳
- start: 起始位置
- start_timestamp: 起始时间戳
这些列名可能用于分析数值的分布及其时间属性。

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
>>> mixed_nc = NodeCollection([F.distribution()(series_1), F.statistics()(series_2)])
# NodeCollection 包含两个节点：一个是关于 series_1 的分布信息，另一个是关于 series_2 的统计信息。
('series', 'delta', 'distribution_values.count', 'distribution_values.end',
'distribution_values.start', 'end', 'end_timestamp', 'start', 'start_timestamp',
'count', 'earliest_point.timestamp', 'earliest_point.value', 'largest_point.timestamp',
'largest_point.value', 'latest_point.timestamp', 'latest_point.value', 'mean', 'smallest_point.timestamp',
'smallest_point.value')
# 输出的元组中包含了一些属性名称，这些属性可能来自于分布和统计分析的结果。
# 例如：distribution_values.count 表示分布值的数量，latest_point.value 表示最新点的值，mean 表示平均值等。
```

#### map(func)

将集合中的每个时间序列映射到输入函数的输出。

这对于对时间序列集合应用相同的一组查询非常有用。

- 参数：func(()-> FunctionNode|SummarizerNode) – FoundryTS 支持的函数，应用于集合中的每个时间序列。
- 返回值：更新的 NodeCollection，其中每个项目映射到应用func的相应输出。
- 返回类型：Iterable[NodeCollection]
NodeCollection.map_intervals()

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
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
# 创建一个名为 "series-1" 的数据点序列，包含三个数据点，时间戳分别是1, 2, 3，对应值是100.0, 200.0, 300.0
>>> series_1.to_pandas()
# 将 "series-1" 转换为 Pandas 数据框格式，显示时间戳和对应的值
                    timestamp  value
0 1970-01-01 00:00:00.000000001  100.0
1 1970-01-01 00:00:00.000000002  200.0
2 1970-01-01 00:00:00.000000003  300.0
>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
# 创建另一个名为 "series-2" 的数据点序列，时间戳和 "series-1" 相同，但对应值为200.0, 400.0, 600.0
>>> series_2.to_pandas()
# 将 "series-2" 转换为 Pandas 数据框格式，显示时间戳和对应的值
                    timestamp  value
0 1970-01-01 00:00:00.000000001  200.0
1 1970-01-01 00:00:00.000000002  400.0
2 1970-01-01 00:00:00.000000003  600.0
>>> nc = NodeCollection([series_1, series_2])
# 创建一个 NodeCollection 对象，包含 "series-1" 和 "series-2" 两个数据点序列
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
>>> scaled_nc = nc.map(F.scale(10))  # 将nc中的数值放大10倍
>>> scaled_nc.to_pandas()
     series                     timestamp   value
0  series-1 1970-01-01 00:00:00.000000001  1000.0
1  series-1 1970-01-01 00:00:00.000000002  2000.0
2  series-1 1970-01-01 00:00:00.000000003  3000.0
3  series-2 1970-01-01 00:00:00.000000001  2000.0
4  series-2 1970-01-01 00:00:00.000000002  4000.0
5  series-2 1970-01-01 00:00:00.000000003  6000.0
```

这段代码将nc数据集中的数值通过F.scale(10)函数放大10倍，然后将结果转换为Pandas DataFrame格式进行展示。

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
>>> mapped_summary_nc = nc.map(F.distribution())
# 将分布映射应用到数据集 `nc` 中。F.distribution() 是一个函数，可能用于计算某种分布统计数据。

>>> mapped_summary_nc.to_pandas()
# 将映射后的结果转换为 Pandas DataFrame 格式，以便更容易查看和分析。

     series  delta  distribution_values.count  distribution_values.end  distribution_values.start    end end_timestamp  start               start_timestamp
0  series-1   20.0                          1                    120.0                      100.0  300.0    2262-01-01  100.0 1677-09-21 00:12:43.145225216
1  series-1   20.0                          1                    200.0                      180.0  300.0    2262-01-01  100.0 1677-09-21 00:12:43.145225216
2  series-1   20.0                          1                    300.0                      280.0  300.0    2262-01-01  100.0 1677-09-21 00:12:43.145225216
3  series-2   40.0                          1                    240.0                      200.0  600.0    2262-01-01  200.0 1677-09-21 00:12:43.145225216
4  series-2   40.0                          1                    400.0                      360.0  600.0    2262-01-01  200.0 1677-09-21 00:12:43.145225216
5  series-2   40.0                          1                    600.0                      560.0  600.0    2262-01-01  200.0 1677-09-21 00:12:43.145225216
# 表格中包含了每个系列（series）的数据分布信息：
# - `series`: 系列名称。
# - `delta`: 每个系列的增量。
# - `distribution_values.count`: 分布值的计数。
# - `distribution_values.end`: 分布的结束值。
# - `distribution_values.start`: 分布的起始值。
# - `end`: 分布的结束点。
# - `end_timestamp`: 结束时间戳。
# - `start`: 分布的起始点。
# - `start_timestamp`: 起始时间戳。
```

#### map_intervals(intervals, interval_name=None)

利用时间间隔为集合中的所有时间序列创建一个时间范围。

每个时间间隔用于在输入时间序列上创建foundryts.functions.time_range()，
可用于进一步的变换和分析。最好与手动创建Interval或通过将foundryts.functions.time_range()的结果转换为Interval结合使用。

结果数据框增加了interval.start和interval.end列。

- 参数:intervals(Interval|List[Interval]) – 一个或多个间隔，以为集合中的所有时间序列创建时间范围。interval_name(str,非必填) – 数据框中间隔列的可选别名。
- intervals(Interval|List[Interval]) – 一个或多个间隔，以为集合中的所有时间序列创建时间范围。
- interval_name(str,非必填) – 数据框中间隔列的可选别名。
- 返回:更新的NodeCollection，其中每个项目映射到应用func的相应输出。
- 返回类型:Iterable[NodeCollection]
foundryts.functions.time_series_search()

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
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
# 创建一个数据系列 series_1，包含三个时间点和值，并命名为 "series-1"
>>> series_1.to_pandas()
# 将 series_1 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001  100.0
1 1970-01-01 00:00:00.000000002  200.0
2 1970-01-01 00:00:00.000000003  300.0
>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
# 创建另一个数据系列 series_2，包含三个时间点和值，并命名为 "series-2"
>>> series_2.to_pandas()
# 将 series_2 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001  200.0
1 1970-01-01 00:00:00.000000002  400.0
2 1970-01-01 00:00:00.000000003  600.0
>>> nc = NodeCollection([series_1, series_2])
# 创建一个 NodeCollection 对象 nc，包含两个数据系列 series_1 和 series_2
>>> from foundryts.core.interval import Interval
# 从 foundryts.core.interval 导入 Interval 类
>>> intervals = [Interval(1, 2), Interval(2, 3), Interval(3, 4), Intervals(1,3)]
# 创建一个包含不同时间间隔的列表 intervals，其中最后一个 'Intervals' 拼写错误，应为 'Interval'
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
15
16
17
18
19
>>> nc = nc.map_intervals(intervals, interval_name="interval")
# 使用 map_intervals 方法映射区间，并命名为 "interval"

>>> nc.to_pandas()
# 将结果转换为 Pandas 数据框

     series interval  interval.start  interval.end                     timestamp  value
#   系列名称  区间名    区间开始          区间结束                             时间戳     值
0  series-1                        1             2 1970-01-01 00:00:00.000000001  100.0
1  series-1                        2             3 1970-01-01 00:00:00.000000002  200.0
2  series-1                        3             4 1970-01-01 00:00:00.000000003  300.0
3  series-1                        1             3 1970-01-01 00:00:00.000000001  100.0
4  series-1                        1             3 1970-01-01 00:00:00.000000002  200.0
5  series-2                        1             2 1970-01-01 00:00:00.000000001  200.0
6  series-2                        2             3 1970-01-01 00:00:00.000000002  400.0
7  series-2                        3             4 1970-01-01 00:00:00.000000003  600.0
8  series-2                        1             3 1970-01-01 00:00:00.000000001  200.0
9  series-2                        1             3 1970-01-01 00:00:00.000000002  400.0
# 这里的输出是一个包含时间序列、区间、开始和结束时间戳以及对应值的数据框
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
>>> scaled_nc = nc.map(F.scale(1000))
>>> scaled_nc.to_pandas() # 在每个时间区间上应用 scale() 函数
     series interval  interval.start  interval.end                     timestamp     value
0  series-1                        1             2 1970-01-01 00:00:00.000000001  100000.0
1  series-1                        2             3 1970-01-01 00:00:00.000000002  200000.0
2  series-1                        3             4 1970-01-01 00:00:00.000000003  300000.0
3  series-1                        1             3 1970-01-01 00:00:00.000000001  100000.0
4  series-1                        1             3 1970-01-01 00:00:00.000000002  200000.0
5  series-2                        1             2 1970-01-01 00:00:00.000000001  200000.0
6  series-2                        2             3 1970-01-01 00:00:00.000000002  400000.0
7  series-2                        3             4 1970-01-01 00:00:00.000000003  600000.0
8  series-2                        1             3 1970-01-01 00:00:00.000000001  200000.0
9  series-2                        1             3 1970-01-01 00:00:00.000000002  400000.0
```

这个代码片段对nc对象的每个时间区间应用了一个缩放函数scale(1000)，然后将结果转换为一个 pandas 数据帧进行展示。

#### to_dataframe(numPartitions=16)

评估集合中的所有时间序列，并将结果连接到pyspark.sql.DataFrame。

PySpark DataFrame支持分布式数据处理和并行化变换。当处理具有大量行的数据框时，它们非常有用，例如加载原始系列中的所有点或FunctionNode的结果，或一起评估多个SummarizerNode或FunctionNode的结果。

一个额外的series列将使用系列ID或foundryts.functions.points()别名标记结果所属的系列。

- 参数:numPartitions(int,非必填) – 指定用于在Spark执行器之间分配集合中的时间序列数据的分区数量，以优化并行数据处理。当执行器数量较多时，更高的值可以提高性能，而执行器较少时较低的值可能更高效。根据时间序列集合的大小和您的Spark配置（例如，执行器数量和执行器内存）进行调整（默认值为16）。
- 返回:集合中所有时间序列和操作的输出被评估为一个PySpark dataframe。
- 返回类型:pyspark.sql.DataFrame
NodeCollection.to_pandas()

为大型集合设置适当的numPartitions值。

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
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
# 创建一个名为 series-1 的数据序列，包含三个点，每个点有一个时间戳和一个值
>>> series_1.to_pandas()
# 将 series-1 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001  100.0
1 1970-01-01 00:00:00.000000002  200.0
2 1970-01-01 00:00:00.000000003  300.0
>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
# 创建一个名为 series-2 的数据序列，包含三个点，每个点有一个时间戳和一个值
>>> series_2.to_pandas()
# 将 series-2 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001  200.0
1 1970-01-01 00:00:00.000000002  400.0
2 1970-01-01 00:00:00.000000003  600.0
>>> nc = NodeCollection(series_1, series_2)
# 创建一个 NodeCollection 对象，包含 series-1 和 series-2 两个数据序列
>>> nc.to_dataframe()
# 将 NodeCollection 转换为 DataFrame 格式
+---------+-----------------------------+-----+
|  series |                 timestamp   |value|
+---------+-----------------------------+-----+
|series-1 |1970-01-01 00:00:00.000000001|100.0|
|series-1 |1970-01-01 00:00:00.000000002|200.0|
|series-1 |1970-01-01 00:00:00.000000003|300.0|
|series-2 |1970-01-01 00:00:00.000000001|200.0|
|series-2 |1970-01-01 00:00:00.000000002|400.0|
|series-2 |1970-01-01 00:00:00.000000003|600.0|
+---------+-----------------------------+-----+
```

#### to_pandas(parallel=4, mode='thread')

评估此集合中的时间序列查询，并将结果连接到pandas.DataFrame。

有关dataframe的形状详细信息，请参阅FunctionNode.to_pandas()和SummarizerNode.to_pandas()。

一个额外的series列将使用系列ID或foundryts.functions.points()别名注明结果属于哪个系列。

- 参数:parallel(int,非必填) – 用于评估时间序列查询的并行线程或进程的数量。如果设置为1，则不进行多处理（默认值为4）。mode(str,非必填) – 有效选项是process或thread，每个选项控制多处理线程池的类型。
- parallel(int,非必填) – 用于评估时间序列查询的并行线程或进程的数量。如果设置为1，则不进行多处理（默认值为4）。
- mode(str,非必填) – 有效选项是process或thread，每个选项控制多处理线程池的类型。
- 返回:集合中时间序列查询的输出评估为一个Pandas dataframe。
- 返回类型:pd.DataFrame
NodeCollection.to_dataframe()

集合中每个时间序列查询的结果都存储并连接到最终的dataframe，因此结果必须适合内存。

并行执行将增加内存使用和资源消耗。使用process模式可能引入开销。过度的并行可能会降低性能。

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
>>> series_1 = F.points((1, 100.0), (2, 200.0), (3, 300.0), name="series-1")
>>> series_1.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001  100.0
1 1970-01-01 00:00:00.000000002  200.0
2 1970-01-01 00:00:00.000000003  300.0
# 创建一个时间序列 series_1，并将其转换为 pandas DataFrame 格式

>>> series_2 = F.points((1, 200.0), (2, 400.0), (3, 600.0), name="series-2")
>>> series_2.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001  200.0
1 1970-01-01 00:00:00.000000002  400.0
2 1970-01-01 00:00:00.000000003  600.0
# 创建另一个时间序列 series_2，并将其转换为 pandas DataFrame 格式

>>> nc = NodeCollection(series_1, series_2)
# 将两个时间序列 series_1 和 series_2 收集到一个 NodeCollection 中
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
>>> nc.to_pandas()
      series                     timestamp  value
0  series-1 1970-01-01 00:00:00.000000001  100.0
1  series-1 1970-01-01 00:00:00.000000002  200.0
2  series-1 1970-01-01 00:00:00.000000003  300.0
3  series-2 1970-01-01 00:00:00.000000001  200.0
4  series-2 1970-01-01 00:00:00.000000002  400.0
5  series-2 1970-01-01 00:00:00.000000003  600.0
```

该代码段将数据转换为Pandas DataFrame格式。数据包括三个列：series表示数据系列，timestamp表示时间戳，value表示数值。这个数据表格可以用于进一步的数据分析和处理。

#### to_rdd(numPartitions=16)

#### 已弃用

自版本1.0.0起已弃用。

通过评估此集合中的节点，返回一个 (key,object) 的RDD。如果此NodeCollection中的节点是通过分组或窗口操作生成的，相关键将包含给定的元数据键或区间。否则，它将是节点的系列标识符。

- 参数:numPartitions(int) – 用于spark执行的分区数量
- 返回类型:pyspark.RDD
#### types()

返回pandas.DataFrame列类型的元组，该列将通过将集合评估为数据帧而生成。

- 返回:包含集合被评估为的数据帧中列类型的元组。
- 返回类型:Tuple[Type]
非统一集合将包含集合中每个元素所有类型的并集。

## 示例

```
Copied!1
2
3
>>> nc = NodeCollection(series_1, series_2)
>>> nc.types()
(<class 'str'>, <class 'int'>, <class 'float'>)
```

这个代码段展示了创建一个NodeCollection对象，并调用其types()方法来获取series_1和series_2中节点的数据类型。返回值是一个元组，包含这些节点的类型：字符串、整数和浮点数。

```
Copied!1
2
3
4
5
6
7
>>> dist = F.distribution()(nc)
>>> dist.types()
(<class 'float'>, <class 'int'>, <class 'float'>, <class 'float'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>)
# 该代码首先定义了一个分布对象 `dist`，然后调用 `types()` 方法以获取分布中各字段的类型。
# 返回的类型包括浮点数 (float)、整数 (int) 和时间戳 (Timestamp)。
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
>>> mixed_nc = NodeCollection([F.distribution()(series_1), F.statistics()(series_2)])
>>> print(mixed_nc.types())
(<class 'str'>, <class 'float'>, <class 'int'>, <class 'float'>, <class 'float'>,
<class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'int'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>)
```

这个代码片段创建了一个NodeCollection对象，包含了两个节点，这两个节点分别是通过F.distribution()和F.statistics()函数处理series_1和series_2得到的。然后，代码打印出mixed_nc中元素的类型。

- NodeCollection：假设是一个自定义的类，用于存储和操作一组节点。
- F.distribution()和F.statistics()：假设是数据处理函数，分别对series_1和series_2进行分布和统计操作。
- mixed_nc.types()返回一个元组，包含了mixed_nc中各个元素的类型。
- 输出显示mixed_nc包含多种数据类型，如字符串（str）、浮点数（float）、整数（int）、以及时间戳（pandas._libs.tslibs.timestamps.Timestamp）。
该输出帮助开发人员理解数据集合中不同元素的类型分布。
