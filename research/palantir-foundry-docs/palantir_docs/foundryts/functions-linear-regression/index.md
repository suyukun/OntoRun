来源: https://palantir.com/docs/zh/foundry/foundryts/functions-linear-regression/

# foundryts.functions.linear_regression

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.linear_regression

## foundryts.functions.linear_regression(include_intercept=True, time_unit='ns', start=None, end=None)

返回一个对单一时间序列执行线性回归的函数。

线性回归找到输入时间序列点上的最佳拟合线的参数。线性回归表示为y = Ax + B，其中A是线的斜率，B是y截距。返回的函数将提供参数A和B。

当需要识别和量化时间序列数据中的线性趋势时，线性回归非常有用。

- 参数:time_unit(str,非必填) – 系数的时间单位，必须是 “s”、 “ms”、 “us”、 “ns” 之一（默认是 “ns”）。start(str|int|datetime.datetime,非必填) – 计算线性回归的时间序列的起始点（包含）。end(str|int|datetime.datetime,非必填) – 计算线性回归的时间序列的终点（不包含）。
- time_unit(str,非必填) – 系数的时间单位，必须是 “s”、 “ms”、 “us”、 “ns” 之一（默认是 “ns”）。
- start(str|int|datetime.datetime,非必填) – 计算线性回归的时间序列的起始点（包含）。
- end(str|int|datetime.datetime,非必填) – 计算线性回归的时间序列的终点（不包含）。
- 返回:一个接受单一时间序列的函数，并使用线性回归返回时间序列点的最佳拟合线参数。
- 返回类型:(FunctionNode) ->SummarizerNode
## 数据框架架构

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| max_bounds.first_value | float | y=Ax+B中斜率 (A) 的最大值。 |
| max_bounds.second_value | float | y=Ax+B中截距 (B) 的最大值。 |
| min_bounds.first_value | float | y=Ax+B中斜率 (A) 的最小值。 |
| min_bounds.second_value | float | y=Ax+B中截距 (B) 的最小值。 |
| regression_fit_function.linear_regression_fit.slope | float | 线性回归拟合中y=Ax+B的参数 ‘A’ (斜率)。 |
| regression_fit_function.linear_regression_fit.intercept | float | 线性回归拟合中y=Ax+B的参数 ‘B’ (截距)。 |
| regression_fit_function.linear_regression_fit.statistics.rsquared | float | R平方值，指示线性回归的拟合优度。 |

exponential_regression(),polynomial_regression()

此函数仅适用于数值系列。

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
>>> lin_regr = F.linear_regression()(series)  # 使用线性回归函数拟合数据序列
>>> lin_regr.to_pandas()
   max_bounds.first_value  max_bounds.second_value  min_bounds.first_value  min_bounds.second_value  regression_fit_function.linear_regression_fit.intercept  regression_fit_function.linear_regression_fit.slope  regression_fit_function.linear_regression_fit.statistics.rsquared
0                    50.0                     96.0                    10.0                      6.0                                              -27.6                                                     2.16                                             0.870968
   # max_bounds 和 min_bounds 表示数据集的最大和最小边界值
   # intercept 表示回归线的截距
   # slope 表示回归线的斜率
   # rsquared 是决定系数 (R²)，表示模型的拟合优度
```
