来源: https://palantir.com/docs/zh/foundry/foundryts/nodes-function-node/

# foundryts.nodes.FunctionNode

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.nodes.FunctionNode

## classfoundryts.nodes.FunctionNode(children)

用于变换一个或多个时间序列为新的时间序列的惰性查询容器，该时间序列是提供的变换函数的输出。

每个FunctionNode都可以被变换为另一个FunctionNode，或计算为最终的SummarizerNode。

您还可以通过FunctionNode.to_pandas()或FunctionNode.to_dataframe()将惰性FunctionNode解析为dataframe，这将以dataframe的形式生成变换后的时间序列。

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
...     (100, 0.0),  # 第一个数据点，时间戳为 100 纳秒，值为 0.0
...     (200, float("inf")),  # 第二个数据点，时间戳为 200 纳秒，值为无穷大
...     (300, 3.14159),  # 第三个数据点，时间戳为 300 纳秒，值为 3.14159
...     (2147483647, 1.0),  # 第四个数据点，时间戳为 2147483647 纳秒，值为 1.0
...     name="series"  # 给这个数据序列命名为 "series"
... )
>>> series.to_pandas()
                      timestamp    value
0 1970-01-01 00:00:00.000000100  0.00000
1 1970-01-01 00:00:00.000000200      inf
2 1970-01-01 00:00:00.000000300  3.14159
3 1970-01-01 00:00:02.147483647  1.00000
```

在这里，series是一个时间序列对象，其中每个数据点由一个时间戳和一个对应的值组成。时间戳是以纳秒为单位的整数，to_pandas()方法将此序列转换为 Pandas 数据框格式，显示了时间戳和对应的值。

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
>>> scaled = series.scale(1.5) # scaled 是一个尚未计算的 FunctionNode
# scaled 可以与其他 FunctionNode 操作链接，产生另一个未计算的 FunctionNode
>>> time_shifted = scaled.time_shift(1000)
# 将 time_shifted 转换为 Pandas 数据框会评估惰性查询，得到 scaled 和 time_shifted 函数的输出
>>> time_shifted.to_pandas()
                      timestamp     value
0 1970-01-01 00:00:00.000001100  0.000000
1 1970-01-01 00:00:00.000001200       inf
2 1970-01-01 00:00:00.000001300  4.712385
3 1970-01-01 00:00:02.147484647  1.500000
```

#### columns()

返回一个字符串元组，表示通过评估此节点生成的pandas.DataFrame的列名。

嵌套对象的键将被展平成一个元组，嵌套键用.连接。

- 返回:包含结果数据框中列名的元组，该数据框是当前节点评估的结果。
- 返回类型:元组[str]
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
>>> series_node = foundryts.functions.points(((100, 0.0), (200, 1.0))
# 创建一个时间序列节点，包含两个点：(100, 0.0) 和 (200, 1.0)
>>> series_node.columns()
("timestamp", "value")
# 输出序列节点的列名称：时间戳和数值

>>> stats_node = series_node.statistics(start=0, end=100, window_size=None)
# 计算时间序列节点的统计信息，开始时间为0，结束时间为100，窗口大小为None（不使用窗口计算）
>>> stats_node.columns()
("count", "smallest_point.timestamp", "start_timestamp", "latest_point.timestamp", "mean",
"earliest_point.timestamp", "largest_point.timestamp", "end_timestamp")
# 输出统计节点的列名称：计数、最小点的时间戳、开始时间戳、最新点的时间戳、均值、最早点的时间戳、最大点的时间戳、结束时间戳
```

#### cumulative_aggregate(*args, **kwargs)

请参阅foundryts.functions.cumulative_aggregate()

#### derivative()

请参阅foundryts.functions.derivative()

#### distribution(start=None, end=None, bins=None, start_value=None, end_value=None)

请参阅foundryts.functions.distribution()

#### dsl(program, return_type, labels=None, before='nearest', internal='linear', after='nearest')

请参阅foundryts.functions.dsl()

#### first_point()

请参阅foundryts.functions.first_point()

#### integral(method='LINEAR')

请参阅foundryts.functions.integral()

#### interpolate(before=None, internal=None, after=None, frequency=None, rename_columns_by=None, static_column_name=None)

请参阅foundryts.functions.interpolate()

#### last_point()

请参阅foundryts.functions.last_point()

#### mean(children)

请参阅foundryts.functions.mean()

#### periodic_aggregate(*args, **kwargs)

请参阅foundryts.functions.periodic_aggregate()

#### rolling_aggregate(*args, **kwargs)

请参阅foundryts.functions.rolling_aggregate()

#### scale(factor)

请参阅foundryts.functions.scale()

#### scatter(start_timestamp, end_timestamp, first_interpolation, second_interpolation, regression_fit)

请参阅foundryts.functions.scatter()

#### propertyseries_ids

此节点及其子节点使用的所有系列标识符。

#### skip_nonfinite()

请参阅foundryts.functions.skip_nonfinite()

#### statistics(start=None, end=None, window=None, **kwargs)

请参阅foundryts.functions.statistics()

#### sum(children)

请参阅foundryts.functions.sum()

#### time_extent()

请参阅foundryts.functions.time_extent()

#### time_range(start=None, end=None)

请参阅foundryts.functions.time_range()

#### time_shift(duration)

请参阅foundryts.functions.time_shift()

#### to_dataframe(fts=None)

将此节点评估为pyspark.sql.DataFrame。

PySpark DataFrame支持分布式数据处理和并行化变换。它们在处理大量行的数据帧时非常有用，例如加载原始系列中的所有点或FunctionNode的结果，或一起评估多个SummarizerNode或FunctionNode的结果。

- 参数：fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回：节点评估为PySpark dataframe的输出。
- 返回类型：pyspark.sql.DataFrame
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
>>> series_node = F.points(
...     (100, 0.0), (200, float("inf")), (300, 3.14159), (2147483647, 1.0), name="series"
... )
>>> series_node.to_dataframe().show()
+-------------------------------+---------+
| timestamp                     | value   |
+-------------------------------+---------+
| 1970-01-01 00:00:00.000000100 | 0.0     |
| 1970-01-01 00:00:00.000000200 | Infinity|
| 1970-01-01 00:00:00.000000300 | 3.14159 |
| 1970-01-01 00:00:02.147483647 | 1.0     |
+-------------------------------+---------+
```

这个代码片段创建了一个名为series_node的数据点序列，其中包括不同的时间戳和相应的值。每个数据点由一个时间戳（以纳秒为单位）和一个浮点值组成。最后，这些数据点被转换为一个数据框并显示出来。

- F.points(...): 创建一个数据点序列，F可能是一个特定库中用于处理时间序列数据的模块。
- 时间戳中的数字是自 Unix 纪元（1970年1月1日）以来的纳秒数。
- float("inf")表示正无穷大。
- series_node.to_dataframe().show(): 将数据点序列转换为数据框并展示。
#### to_pandas(fts=None)

将此节点评估为pandas.DataFrame。

这对于将原始或变换的时间序列数据加载到pandas.DataFrame中并使用pandas.DataFrame提供的操作进行变换非常有用。

- 参数:fts(foundryts.FoundryTS,非必填) – 用于执行查询的FoundryTS会话（如果未提供，将创建一个新会话）。
- 返回:节点输出评估为一个Pandas dataframe。
- 返回类型:pd.DataFrame
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
>>> series = F.points(
...     (100, 0.0), (200, float("inf")), (300, 3.14159), (2147483647, 1.0), name="series"
... )
# 使用 F.points 创建了一个时间序列，包含四个数据点，每个数据点由时间戳（整数）和对应的值（浮点数）组成。
# 其中，float("inf") 表示正无穷大。
>>> series.to_pandas()
# 将时间序列转换为 Pandas DataFrame 格式，方便数据分析和处理。
                    timestamp    value
0 1970-01-01 00:00:00.000000100  0.00000
1 1970-01-01 00:00:00.000000200      inf
2 1970-01-01 00:00:00.000000300  3.14159
3 1970-01-01 00:00:02.147483647  1.00000
# 输出的 DataFrame 显示了时间戳和对应的值，其中时间戳以纳秒为单位。
# 注意：第三个数据点的时间戳（2147483647）被转换为大约 2 秒的时间。
```

#### types()

返回一个包含pandas.DataFrame列类型的元组，该元组通过将此节点评估为pandas dataframe生成。

- 返回：包含结果dataframe中列类型的元组，当前节点被评估为该dataframe。
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
>>> node = foundryts.functions.points()
>>> node.types()
# 返回的数据类型是整数和浮点数
(<class 'int'>, <class 'float'>)
>>> stats_node = node.statistics(start=0, end=100, window_size=None)
>>> stats_node.types()
# 返回的数据类型包括整数、浮点数以及多个时间戳类型
(<class 'int'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>,
<class 'float'>, <class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>, <class 'float'>,
<class 'pandas._libs.tslibs.timestamps.Timestamp'>)
```

#### udf(函数, 列=None, 类型=None)

参见foundryts.functions.udf()

#### 单位转换(从单位, 到单位)

参见foundryts.functions.unit_conversion()

#### 值偏移(增量)

参见foundryts.functions.value_shift()

#### 条件选择(true=None, false=None)

参见foundryts.functions.where()
