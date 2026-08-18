来源: https://palantir.com/docs/zh/foundry/foundryts/nodes-summarizer-node/

# foundryts.nodes.SummarizerNode

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.nodes.SummarizerNode

## classfoundryts.nodes.SummarizerNode(children)

用于汇总一个或多个FunctionNode至最终结果的惰性查询容器。

SummarizerNode是原始或变换后的时间序列的最终评估形式，无法被FoundryTS进一步变换。通常使用SummarizerNode.to_pandas()或SummarizerNode.to_dataframe()将SummarizerNode评估为数据框，并使用相应的数据框库执行变换和分析。

## 示例

```
Copied!1
2
3
4
5
6
>>> dist_node = series.distribution() # SummarizerNode
>>> dist_node.to_pandas()
        delta  distribution_values.count  distribution_values.end  distribution_values.start      end end_timestamp  start               start_timestamp
0  0.314159                          1                 0.314159                   0.000000  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
1  0.314159                          1                 1.256636                   0.942477  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
2  0.314159                          1                 3.141590                   2.827431  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
```

此代码片段展示了如何使用series.distribution()方法生成一个SummarizerNode对象，并将其转换为 Pandas 数据框格式。以下是各个字段的解释：

- delta: 增量值。
- distribution_values.count: 分布值的计数。
- distribution_values.end: 分布值的结束值。
- distribution_values.start: 分布值的起始值。
- end: 总体结束值。
- end_timestamp: 结束时间戳。
- start: 总体起始值。
- start_timestamp: 起始时间戳。
此表格展示了分布值的计数和范围，以及与时间相关的信息。

#### columns()

返回一个字符串的元组，表示通过将此节点评估为pandas dataframe而生成的pandas.DataFrame的列名。

嵌套对象的键将被展平为一个元组，其中嵌套键通过.连接。

- 返回值:包含当前节点被评估为结果dataframe中列名称的元组。
- 返回类型:Tuple[str]
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
>>> node = foundryts.functions.series("series1")
# 创建一个时间序列对象，命名为 node，使用 "series1" 作为时间序列的名称

>>> node.columns()
("timestamp", "value")
# 获取 node 的列名，返回 ("timestamp", "value")，表示时间序列包含时间戳和对应的值

>>> stats_node = series.statistics(start=0, end=100, window_size=None)
# 计算时间序列的统计信息，范围从 start=0 到 end=100，window_size=None 表示不使用滑动窗口

>>> stats_node.columns()
("count", "smallest_point.timestamp", "start_timestamp", "latest_point.timestamp", "mean",
"earliest_point.timestamp", "largest_point.timestamp", "end_timestamp")
# 获取统计信息节点的列名，返回多个统计指标，包括计数、最小点时间戳、起始时间戳、最新点时间戳、平均值、最早点时间戳、最大点时间戳和结束时间戳
```

#### propertyseries_ids

此节点及其子节点使用的所有系列标识符。

#### to_dataframe(fts=None)

将此节点评估为pyspark.sql.DataFrame。

PySpark DataFrame支持分布式数据处理和并行化变换。当处理具有大量行的数据框时，它们可能很有用，例如加载原始系列中的所有点或FunctionNode的结果，或者一起评估多个SummarizerNode或FunctionNode的结果。

- 参数:fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回:节点的输出评估为一个PySpark dataframe。
- 返回类型:pyspark.sql.DataFrame
## 例子

#### to_dict(fts=None)

将此节点评估为嵌套字典，并包含此节点的结果。

如果SummarizerNode返回多个结果，该方法将返回字典列表，每个列表项对应一个结果。

- 参数：fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回：节点评估为字典或字典列表的输出。
- 返回类型：Union[Dict[str, Any], List[Dict[str, Any]]]
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
>>> series = F.points(
...     (100, 0.0), (200, float("inf")), (300, 3.14159), (2147483647, 1.0), name="series"
... ) # FunctionNode
# 通过 F.points 函数创建一个时间序列，包含时间戳和对应的值
# (100, 0.0), (200, float("inf")), (300, 3.14159), (2147483647, 1.0) 是时间戳和值的对
# name="series" 用于给时间序列命名为 "series"

>>> series.to_pandas()
# 将时间序列转换为 Pandas 数据框格式
                    timestamp    value
0 1970-01-01 00:00:00.000000100  0.00000
1 1970-01-01 00:00:00.000000200      inf
2 1970-01-01 00:00:00.000000300  3.14159
3 1970-01-01 00:00:02.147483647  1.00000
# 输出数据框，其中 timestamp 是时间戳，value 是对应的值
# 注意：时间戳是以1970-01-01 00:00:00为基准的纳秒时间
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
20
21
22
23
24
25
26
>>> dist_node = series.distribution() # SummarizerNode
>>> dist_node.to_pandas()
{
    'start_timestamp': Timestamp('1677-09-21 00:12:43.145225216'), # 开始时间戳
    'end_timestamp': Timestamp('2262-01-01 00:00:00'), # 结束时间戳
    'start': 0.0, # 分布开始值
    'end': 3.1415900000000003, # 分布结束值
    'delta': 0.314159, # 每个分布区间的宽度
    'distribution_values': [ # 分布区间的详细信息
        {
            'start': 0.0, # 当前区间开始值
            'end': 0.314159, # 当前区间结束值
            'count': 1 # 当前区间内的元素数量
        },
        {
            'start': 0.942477, # 当前区间开始值
            'end': 1.256636, # 当前区间结束值
            'count': 1 # 当前区间内的元素数量
        },
        {
            'start': 2.8274310000000002, # 当前区间开始值
            'end': 3.1415900000000003, # 当前区间结束值
            'count': 1 # 当前区间内的元素数量
        }
    ]
}
```

这段代码展示了如何使用SummarizerNode来获取数据的分布信息。结果包含了数据的时间戳范围、值的范围、每个区间的宽度以及每个区间的元素数量。

#### to_object(fts=None)

将该节点评估为一个包含此节点结果的Python对象。

如果SummarizerNode返回多个结果，此方法返回一个对象列表，每个列表项对应一个结果。

- 参数:fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回:节点的输出评估为一个Python对象或对象列表。
- 返回类型:Union[Any, List[Any]]
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
>>> dist_node = series.distribution() # SummarizerNode
# 获取时间序列的分布节点
>>> dist_node.to_object()
_CuratedDistribution(start_timestamp=Timestamp(epoch_seconds=-9223372037, offset_nanos=145224193),
    # 分布的开始时间戳
    end_timestamp=Timestamp(epoch_seconds=9214646400, offset_nanos=0),
    # 分布的结束时间戳
    start=0.0, end=3.1415900000000003,
    # 分布的起始值和终止值
    delta=0.314159,
    # 分布间隔的增量
    distribution_values=[
        DistributionDataPoint(start=0.0, end=0.314159, count=1),
        # 分布区间从0.0到0.314159，计数为1
        DistributionDataPoint(start=0.942477, end=1.256636, count=1),
        # 分布区间从0.942477到1.256636，计数为1
        DistributionDataPoint(start=2.8274310000000002, end=3.1415900000000003, count=1)
        # 分布区间从2.8274310000000002到3.1415900000000003，计数为1
    ]
)
```

#### to_pandas(fts=None)

将此节点评估为pandas.DataFrame。

SummarizerNode的DataFrame结果将被展平为pandas.DataFrame，其中包含一行（如果总结器返回多个结果，则每个元素一行），以及结果对象中每个叶级值的一列。嵌套键将用点分隔。

- 参数：fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回：节点评估为Pandas dataframe的输出。
- 返回类型：pd.DataFrame
## 示例

```
Copied!1
2
3
4
5
6
>>> dist_node = series.distribution() # SummarizerNode
>>> dist_node.to_pandas()
      delta  distribution_values.count  distribution_values.end  distribution_values.start      end end_timestamp  start               start_timestamp
0  0.314159                          1                 0.314159                   0.000000  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
1  0.314159                          1                 1.256636                   0.942477  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
2  0.314159                          1                 3.141590                   2.827431  3.14159    2262-01-01    0.0 1677-09-21 00:12:43.145225216
```

该代码段展示了如何从series对象中获取一个分布节点 (SummarizerNode)，然后转换为 Pandas 数据框格式进行查看。

- delta列表示每个分布段的增量。
- distribution_values.count列表示每个分布段内的值的数量。
- distribution_values.start和distribution_values.end列分别表示每个分布段的起始和结束值。
- start和end列表示整个分布的开始和结束。
- start_timestamp和end_timestamp列提供了时间戳信息，显示分布的时间范围。
#### types()

返回一个元组，其中包含通过将此节点评估为pandas.DataFrame时生成的列的类型。

- 返回：元组，包含当前节点评估为的结果数据框中列的类型。
- 返回类型：Tuple[Type]
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
>>> node = foundryts.functions.points()
# 创建一个点函数节点

>>> node.types()
# 返回节点的数据类型
(<class 'int'>, <class 'float'>)
# 该节点返回整数和浮点数类型的数据

>>> stats_node = foundryts.functions.series("series1").statistics(start=0, end=100, window_size=None)
# 创建一个统计函数节点，用于计算时间序列 "series1" 的统计信息
# 参数 start 和 end 定义了计算的时间范围，window_size 为 None 表示不使用窗口

>>> stats_node.types()
# 返回统计节点的数据类型
(<class 'int'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>, <class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>)
# 该节点返回的数据类型包括整数、浮点数和时间戳
```
