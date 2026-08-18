来源: https://palantir.com/docs/zh/foundry/foundryts/functions-scatter/

# foundryts.functions.scatter

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.scatter

## foundryts.functions.scatter(start=None, end=None, before='NONE', internal='LINEAR', after='NONE', regression=None, regression_fit=None)

返回一个函数，该函数将为两个时间序列生成对齐的 (x,y) 点列表。

散点图由 (x,y) 坐标组成。对于给定的两个时间序列，一个 (x,y) 坐标将由每个序列中时间戳匹配的点组成。对于底层序列时间戳不匹配的点，将使用配置的插值策略来处理缺失点的序列。

阅读关于 internal, before 和 after 支持的插值策略在interpolate()

此外，您可以传递一个回归函数来找到图中点的最佳拟合线。

- 参数:start(int|datetime|str,非必填) – 对齐点的起始时间戳（包含）（默认为 pandas.Timestamp.min）end(int|datetime|str,非必填) – 对齐点的结束时间戳（不包含）（默认为 pandas.Timestamp.max）before(str|List[str],非必填) – 用于对齐第一个点的插值策略名称，使用interpolate()中提供的插值策略（默认为NONE）internal(str|List[str],非必填) – 用于对齐序列中所有点的插值策略名称，使用interpolate()中提供的插值策略（默认为LINEAR）after(str|List[str],非必填) – 用于对齐最后一个点的插值策略名称，使用interpolate()中提供的插值策略（默认为NONE）regression(linear_regression()|polynomial_regression()|exponential_regression(), 非必填) – 其中一个回归函数的输出，这将提供最佳拟合线的点（以及其他相关指标）在两个输入序列之间（默认不使用回归）。
- start(int|datetime|str,非必填) – 对齐点的起始时间戳（包含）（默认为 pandas.Timestamp.min）
- end(int|datetime|str,非必填) – 对齐点的结束时间戳（不包含）（默认为 pandas.Timestamp.max）
- before(str|List[str],非必填) – 用于对齐第一个点的插值策略名称，使用interpolate()中提供的插值策略（默认为NONE）
- internal(str|List[str],非必填) – 用于对齐序列中所有点的插值策略名称，使用interpolate()中提供的插值策略（默认为LINEAR）
- after(str|List[str],非必填) – 用于对齐最后一个点的插值策略名称，使用interpolate()中提供的插值策略（默认为NONE）
- regression(linear_regression()|polynomial_regression()|exponential_regression(), 非必填) – 其中一个回归函数的输出，这将提供最佳拟合线的点（以及其他相关指标）在两个输入序列之间（默认不使用回归）。
- 返回:返回一个函数，该函数接受两个系列作为输入，并返回散点图的对齐点。结果数据框中的每一行代表一个对齐点。
- 返回类型:(NodeCollection) -> SummarizerNode
## 数据框架架构

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| is_truncated | bool | 此字段已弃用，应忽略。如果输出因系列过大而被截断。 |
| points.first_value | float | 第一个序列中点的值。 |
| points.second_value | float | 第二个序列中点的值。 |
| points.timestamp | datetime | 点的时间戳。 |
| regression.* | float | 来自回归函数的列（如果使用了回归）。 |

interpolate(),linear_regression(),polynomial_regression(),exponential_regression()

此函数仅适用于数值序列。

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
>>> series_1 = F.points((11, 21.0), (13, 23.0), (15, 25.0), (17, 27.0), name="series-1")
# 创建一个名为 series-1 的数据序列，包含四个点，每个点由一个时间戳和一个值组成

>>> series_2 = F.points((11, 21.0), (13, 23.0), (17, 37.0), (37, 47.0), name="series-2")
# 创建一个名为 series-2 的数据序列，包含四个点

>>> series_1.to_pandas()
# 将 series_1 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000011   21.0
1 1970-01-01 00:00:00.000000013   23.0
2 1970-01-01 00:00:00.000000015   25.0
3 1970-01-01 00:00:00.000000017   27.0

>>> series_2.to_pandas()
# 将 series_2 转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000011   21.0
1 1970-01-01 00:00:00.000000013   23.0
2 1970-01-01 00:00:00.000000017   37.0
3 1970-01-01 00:00:00.000000037   47.0

>>> nc = NodeCollection([series_1, series_2])
# 创建一个 NodeCollection 对象，包含 series_1 和 series_2 两个数据序列
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
>>> scatter_plot = F.scatter( # 使用插值的散点图
...     before="NEAREST",     # "NEAREST" 表示在插值前使用最近值
...     internal="LINEAR",    # "LINEAR" 表示在插值过程中使用线性插值
...     after="NEAREST",      # "NEAREST" 表示在插值后使用最近值
... )(nc)
>>> scatter_plot.to_pandas()
    is_truncated  points.first_value  points.second_value              points.timestamp
    0         False                21.0                 21.0 1970-01-01 00:00:00.000000011
    1         False                23.0                 23.0 1970-01-01 00:00:00.000000013
    2         False                25.0                 30.0 1970-01-01 00:00:00.000000015
    3         False                27.0                 37.0 1970-01-01 00:00:00.000000017
    4         False                27.0                 47.0 1970-01-01 00:00:00.000000037
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
>>> lin_regression_scatter_plot = F.scatter(
...     before="NEAREST",
...     internal="LINEAR",
...     after="NEAREST",
...     regression=F.linear_regression(),
... )(nc)
>>> lin_regression_scatter_plot.to_pandas()
   is_truncated  points.first_value  points.second_value              points.timestamp  regression.max_bounds.first_value  regression.max_bounds.second_value  regression.min_bounds.first_value  regression.min_bounds.second_value  regression.regression_fit_function.linear_regression_fit.intercept  regression.regression_fit_function.linear_regression_fit.slope  regression.regression_fit_function.linear_regression_fit.statistics.rsquared
0         False                21.0                 21.0 1970-01-01 00:00:00.000000011                               27.0                                47.0                               21.0                                21.0                                         -59.926471                                                            3.720588                                                        0.827161
1         False                23.0                 23.0 1970-01-01 00:00:00.000000013                               27.0                                47.0                               21.0                                21.0                                         -59.926471                                                            3.720588                                                        0.827161
2         False                25.0                 30.0 1970-01-01 00:00:00.000000015                               27.0                                47.0                               21.0                                21.0                                         -59.926471                                                            3.720588                                                        0.827161
3         False                27.0                 37.0 1970-01-01 00:00:00.000000017                               27.0                                47.0                               21.0                                21.0                                         -59.926471                                                            3.720588                                                        0.827161
4         False                27.0                 47.0 1970-01-01 00:00:00.000000037                               27.0                                47.0                               21.0                                21.0                                         -59.926471                                                            3.720588                                                        0.827161
```

在这个代码示例中，我们使用F.scatter方法生成一个带有线性回归的散点图。各个参数的含义如下：

- before="NEAREST": 在回归分析前使用最近值。
- internal="LINEAR": 在内部使用线性插值。
- after="NEAREST": 在回归分析后使用最近值。
- regression=F.linear_regression(): 指定使用线性回归方法。
然后通过to_pandas()方法将结果转换为 Pandas 数据框，其中包含了以下字段：

- is_truncated: 是否被截断。
- points.first_value和points.second_value: 点的第一个和第二个值。
- points.timestamp: 点的时间戳。
- regression.max_bounds和regression.min_bounds: 回归分析的最大和最小边界值。
- regression.regression_fit_function.linear_regression_fit.intercept: 线性回归的截距。
- regression.regression_fit_function.linear_regression_fit.slope: 线性回归的斜率。
- regression.regression_fit_function.linear_regression_fit.statistics.rsquared: 回归模型的判定系数 (R^2)，表示拟合优度。