来源: https://palantir.com/docs/zh/foundry/foundryts/functions-skip-nonfinite/

# foundryts.functions.skip_nonfinite

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.skip_nonfinite

## foundryts.functions.skip_nonfinite()

返回一个函数，该函数筛选时间序列中所有具有非有限值的点。

非有限值可以是inf或NaN。

- 返回:一个接受单个时间序列并返回仅包含有限点值的筛选时间序列的函数。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的值 |

此函数仅适用于数值系列。

where()

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
>>> series = F.points(
...     (100, 100.0),
...     (120, float("nan")),  # 使用float("nan")表示缺失值NaN
...     (130, 230.0),
...     (166, float("inf")),  # 使用float("inf")表示正无穷大
...     (167, 366.0),
...     (168, float("-inf")), # 使用float("-inf")表示负无穷大
...     name="series",        # 设置数据序列的名称为 "series"
... )
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000100  100.0
1 1970-01-01 00:00:00.000000120    NaN
2 1970-01-01 00:00:00.000000130  230.0
3 1970-01-01 00:00:00.000000166    inf
4 1970-01-01 00:00:00.000000167  366.0
5 1970-01-01 00:00:00.000000168   -inf
```

这段代码创建了一个时间序列数据集，并将其转换为Pandas DataFrame格式。时间戳是从1970年1月1日开始的纳秒级时间。NaN用于表示缺失数据，inf和-inf分别表示正无穷和负无穷。

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
>>> finite_series = F.skip_nonfinite()(series)
>>> finite_series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000100  100.0
1 1970-01-01 00:00:00.000000130  230.0
2 1970-01-01 00:00:00.000000167  366.0

# 通过调用 F.skip_nonfinite() 函数，过滤掉了不可用的（非有限的）数据点。
# 然后将结果转换为 Pandas DataFrame 格式进行展示。
```
