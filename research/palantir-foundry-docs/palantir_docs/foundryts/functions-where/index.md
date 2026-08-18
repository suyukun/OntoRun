来源: https://palantir.com/docs/zh/foundry/foundryts/functions-where/

# foundryts.functions.where

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.where

## foundryts.functions.where(true=None, false=None)

（已弃用）返回一个函数，以指定的函数分别变换非零和零值，用于分别处理真值和假值。

- 参数:true(FunctionNode| int | float, 非必填) – 用于变换非零值的函数或值（默认值为None，保持非零值不变）。false(FunctionNode| int | float, 非必填) – 用于变换零值的函数或值（默认值为None，保持零值不变）。
- true(FunctionNode| int | float, 非必填) – 用于变换非零值的函数或值（默认值为None，保持非零值不变）。
- false(FunctionNode| int | float, 非必填) – 用于变换零值的函数或值（默认值为None，保持零值不变）。
- 返回:一个函数，接受单一时间序列，并使用指定的函数分别变换非零和零值，用于分别处理真值和假值。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的值 |

此函数已弃用，将在未来版本中移除。

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
...     (1, 1.0),
...     (2, 0.0),
...     (3, 0.0),
...     name="series",
... )
# 创建一个名为 "series" 的数据点序列，其中包含三个点：(1, 1.0)、(2, 0.0) 和 (3, 0.0)

>>> series.to_pandas()
# 将数据点序列转换为 Pandas DataFrame 格式，显示时间戳和对应的值
                      timestamp  value
0 1970-01-01 00:00:00.000000001    1.0
1 1970-01-01 00:00:00.000000002    0.0
2 1970-01-01 00:00:00.000000003    0.0
```

这段代码展示了如何使用假定的F.points方法创建一个数据点序列，并将其转换为 Pandas DataFrame。每个点包含一个时间戳（以纳秒为单位）和一个对应的值。

```
Copied!1
2
3
4
5
6
7
8
>>> transformed_series = F.where(true=series * 2, false=-1)(series)
# 如果条件为真，则将 series 中的值乘以 2，否则赋值为 -1
>>> transformed_series.to_pandas()
# 将结果转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000001    2.0
1 1970-01-01 00:00:00.000000002   -1.0
2 1970-01-01 00:00:00.000000003   -1.0
```
