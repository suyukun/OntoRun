来源: https://palantir.com/docs/zh/foundry/foundryts/functions-exponential-regression/

# foundryts.functions.exponential_regression

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.exponential_regression

## foundryts.functions.exponential_regression(include_multiple=True, time_unit='ns', start=None, end=None)

返回一个对单个时间序列执行指数回归的函数。

指数回归找到输入时间序列点上最佳拟合指数曲线的参数。回归表示为y = Ae^(Bx)，其中A是初始值，B是增长率。返回的函数将提供参数A和B。

当数据表现出指数增长或衰减模式时，指数回归特别有用。

- 参数：include_multiple(bool,非必填) – 是否包含多个回归（默认值为 True）。time_unit(str,非必填) – 系数的时间单位，必须是“s”、“ms”、“us”、“ns”之一（默认值为“ns”）。start(str|int|datetime.datetime,非必填) – 用于计算指数回归的时间序列的起始点（包含）。end(str|int|datetime.datetime,非必填) – 用于计算指数回归的时间序列的终点（不包含）。
- include_multiple(bool,非必填) – 是否包含多个回归（默认值为 True）。
- time_unit(str,非必填) – 系数的时间单位，必须是“s”、“ms”、“us”、“ns”之一（默认值为“ns”）。
- start(str|int|datetime.datetime,非必填) – 用于计算指数回归的时间序列的起始点（包含）。
- end(str|int|datetime.datetime,非必填) – 用于计算指数回归的时间序列的终点（不包含）。
- 返回：一个接受单个时间序列并提供该时间序列的最佳拟合指数曲线参数的函数。
- 返回类型：(FunctionNode) ->SummarizerNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| max_bounds.first_value | float | y=Ae^(Bx)中初始值 (A) 的最大值。 |
| max_bounds.second_value | float | y=Ae^(Bx)中增长率 (B) 的最大值。 |
| min_bounds.first_value | float | y=Ae^(Bx)中初始值 (A) 的最小值。 |
| min_bounds.second_value | float | y=Ae^(Bx)中增长率 (B) 的最小值。 |
| regression_fit_function.exponential_regression_fit.aparameter | float | 指数回归拟合中y=Ae^(Bx)的估计参数 ‘A’（初始值）。 |
| regression_fit_function.exponential_regression_fit.bparameter | float | 指数回归拟合中y=Ae^(Bx)的估计参数 ‘B’（增长率）。 |

linear_regression(),polynomial_regression()

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
>>> series = F.points(
...     (10, 6.0), (20, 12.0), (30, 24.0), (40, 48.0), (50, 96.0), name="series"
... )
# 创建一个名为 "series" 的时间序列，包含若干点，每个点有一个时间戳和一个对应的值。

>>> series.to_pandas()
# 将时间序列转换为 Pandas 数据框格式。
                      timestamp  value
0 1970-01-01 00:00:00.000000010    6.0
1 1970-01-01 00:00:00.000000020   12.0
2 1970-01-01 00:00:00.000000030   24.0
3 1970-01-01 00:00:00.000000040   48.0
4 1970-01-01 00:00:00.000000050   96.0
# 这里展示了转换后的 Pandas 数据框，其中 'timestamp' 列是时间戳，'value' 列是对应的值。
```

```
Copied!1
2
3
4
>>> exponential_regr = F.exponential_regression()(series)
>>> exponential_regr.to_pandas()
   max_bounds.first_value  max_bounds.second_value  min_bounds.first_value  min_bounds.second_value  regression_fit_function.exponential_regression_fit.aparameter  regression_fit_function.exponential_regression_fit.bparameter
0                    50.0                     96.0                    10.0                      6.0                                                3.0                                                       0.069315
```

该代码用于对时间序列数据执行指数回归分析。以下是代码的解释：

- exponential_regr = F.exponential_regression()(series): 这行代码调用F.exponential_regression()方法对输入的时间序列数据series进行指数回归分析。返回的对象exponential_regr包含回归分析的结果。
- exponential_regr.to_pandas(): 将exponential_regr对象转换为 pandas 数据框格式，以便于进一步的数据处理和分析。
转换后的 pandas 数据框包含以下列：

- max_bounds.first_value: 最大边界的第一个值。
- max_bounds.second_value: 最大边界的第二个值。
- min_bounds.first_value: 最小边界的第一个值。
- min_bounds.second_value: 最小边界的第二个值。
- regression_fit_function.exponential_regression_fit.aparameter: 指数回归拟合的a参数。
- regression_fit_function.exponential_regression_fit.bparameter: 指数回归拟合的b参数。
这些参数和边界值用于描述指数回归模型的拟合结果。
