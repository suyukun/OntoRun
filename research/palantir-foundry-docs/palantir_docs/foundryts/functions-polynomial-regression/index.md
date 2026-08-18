来源: https://palantir.com/docs/zh/foundry/foundryts/functions-polynomial-regression/

# foundryts.functions.polynomial_regression

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.polynomial_regression

## foundryts.functions.polynomial_regression(max_degree=0, time_unit='ns', start=None, end=None)

返回一个用于计算单一时间序列的多项式回归的函数。

多项式回归找到指定次数的最佳拟合多项式曲线的参数，该多项式曲线覆盖输入时间序列的点。多项式表达为y = a0 + a1*x + a2*x^2 + ... + an*x^n，其中系数a0, a1, ..., an由回归确定。

当变量之间的关系比简单线性关系更复杂时，多项式回归非常有用。

- 参数：max_degree(int,非必填) – 拟合多项式的最大次数（默认为0）。例如，次数为2拟合二次多项式。time_unit(str,非必填) – 系数的时间单位，必须为 “s”, “ms”, “us”, “ns” 之一（默认为 “ns”）。start(str|int|datetime.datetime,非必填) – 用于计算多项式回归的时间序列的起始点（包含）。end(str|int|datetime.datetime,非必填) – 用于计算多项式回归的时间序列的终点（不包含）。
- max_degree(int,非必填) – 拟合多项式的最大次数（默认为0）。例如，次数为2拟合二次多项式。
- time_unit(str,非必填) – 系数的时间单位，必须为 “s”, “ms”, “us”, “ns” 之一（默认为 “ns”）。
- start(str|int|datetime.datetime,非必填) – 用于计算多项式回归的时间序列的起始点（包含）。
- end(str|int|datetime.datetime,非必填) – 用于计算多项式回归的时间序列的终点（不包含）。
- 返回：一个接受单一时间序列的函数，返回使用多项式回归计算的时间序列点的最佳拟合多项式曲线的参数。
- 返回类型：(FunctionNode) ->SummarizerNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| max_bounds.first_value | float | 第一个系数 (a0) 的最大值。 |
| max_bounds.second_value | float | 第二个系数 (a1) 的最大值。 |
| min_bounds.first_value | float | 第一个系数 (a0) 的最小值。 |
| min_bounds.second_value | float | 第二个系数 (a1) 的最小值。 |
| regression_fit_function.polynomial_regression_fit.coefficients.coefficient | float | 多项式回归拟合的系数值。 |
| regression_fit_function.polynomial_regression_fit.coefficients.degree | int | 与每个系数对应的多项式次数。 |

exponential_regression(),linear_regression()

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
>>> poly_regr = F.polynomial_regression(3)(series)
>>> poly_regr.to_pandas()
   max_bounds.first_value  max_bounds.second_value  min_bounds.first_value  min_bounds.second_value  regression_fit_function.polynomial_regression_fit.coefficients.coefficient  regression_fit_function.polynomial_regression_fit.coefficients.degree
0                    50.0                     96.0                    10.0                      6.0                                          -4.800000                                                                           0
1                    50.0                     96.0                    10.0                      6.0                                           1.585714                                                                           1
2                    50.0                     96.0                    10.0                      6.0                                          -0.066429                                                                           2
3                    50.0                     96.0                    10.0                      6.0                                           0.001500                                                                           3
```

这是一个多项式回归的示例：

- F.polynomial_regression(3)(series)：执行一个三阶多项式回归。
- poly_regr.to_pandas()：将回归结果转换为Pandas数据框格式。
数据框中包含以下字段：

- max_bounds.first_value和max_bounds.second_value：最大边界的第一个和第二个值。
- min_bounds.first_value和min_bounds.second_value：最小边界的第一个和第二个值。
- regression_fit_function.polynomial_regression_fit.coefficients.coefficient：多项式回归拟合的系数。
- regression_fit_function.polynomial_regression_fit.coefficients.degree：系数对应的多项式的阶数。
每一行表示一个多项式项的系数和对应的阶数。
