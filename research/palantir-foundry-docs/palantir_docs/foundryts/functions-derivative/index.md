来源: https://palantir.com/docs/zh/foundry/foundryts/functions-derivative/

# foundryts.functions.derivative

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.derivative

## foundryts.functions.derivative()

返回一个计算单个时间序列每秒值更改的函数。

对于时间序列中的每个点，从第二个点开始，输出一个以之前时间点的值的导数为值的刻度。每个值都被缩放为每秒率，而不考虑存储刻度的原始频率。

- 返回:一个接受单个时间序列作为输入并返回具有每秒导数值的时间序列的函数。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的值 |

此函数仅适用于数值序列。

integral()

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
14
>>> series = F.points(
...     (100, 100.0), (120, 200.0), (130, 230.0), (166, 266.0), (167, 366.0), name="series"
... )
# 定义一个时间序列 'series'，其中包括时间戳和对应的值。
# 每个元组的第一个元素是时间戳，第二个元素是对应的值。

>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000100  100.0
1 1970-01-01 00:00:00.000000120  200.0
2 1970-01-01 00:00:00.000000130  230.0
3 1970-01-01 00:00:00.000000166  266.0
4 1970-01-01 00:00:00.000000167  366.0
# 将时间序列转换为 Pandas DataFrame 格式，显示时间戳和对应的值。
```

```
Copied!1
2
3
4
5
6
7
>>> derivative_series = F.derivative()(series)  # 计算时间序列的导数
>>> derivative_series.to_pandas()  # 将结果转换为Pandas DataFrame格式
                      timestamp         value
0 1970-01-01 00:00:00.000000120  5.000000e+09
1 1970-01-01 00:00:00.000000130  3.000000e+09
2 1970-01-01 00:00:00.000000166  1.000000e+09
3 1970-01-01 00:00:00.000000167  1.000000e+11
```

在这个代码片段中，通过F.derivative()函数计算给定时间序列series的导数，得到的结果以DataFrame的形式显示，其中包含时间戳和对应的导数值。
