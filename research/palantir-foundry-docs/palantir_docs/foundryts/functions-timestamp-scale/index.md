来源: https://palantir.com/docs/zh/foundry/foundryts/functions-timestamp-scale/

# foundryts.functions.timestamp_scale

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.timestamp_scale

## foundryts.functions.timestamp_scale(factor)

（已弃用）返回一个函数，该函数将单个时间序列的每个时间戳乘以指定的整数因子。

对于具有点(timestamp, value)的源时间序列，以factor进行缩放后，
结果时间缩放后的时间序列将具有点(timestamp * factor, value)。

- 参数:factor(int) – 与序列中每个时间戳相乘的缩放因子。
- 返回:一个函数，接受单个时间序列作为输入，并返回时间缩放后的时间序列。
- 返回类型:(FunctionNode) ->FunctionNode
## 数据框架架构

| 列名称 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的缩放值 |

scale(),time_shift(),value_shift()

此操作已弃用并执行无操作，结果时间序列保持不变。此函数将在未来版本中删除。

后端将自动统一不同时间单位为相同单位。

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
>>> series = F.points(
...     (1, 1.0),  # 第一个点，时间戳为1，值为1.0
...     (101, 2.0), # 第二个点，时间戳为101，值为2.0
...     (200, 4.0), # 第三个点，时间戳为200，值为4.0
...     (201, 8.0), # 第四个点，时间戳为201，值为8.0
...     name="series",
... )
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    1.0
1 1970-01-01 00:00:00.000000101    2.0
2 1970-01-01 00:00:00.000000200    4.0
3 1970-01-01 00:00:00.000000201    8.0
```

这个代码片段创建了一个时间序列数据，使用F.points函数定义了多个点，每个点由一个时间戳和一个值组成。然后通过series.to_pandas()方法将其转换为 Pandas 数据框显示。在输出中，timestamp列显示了对应的纳秒时间戳，value列显示了每个点的值。

```
Copied!1
2
3
4
5
6
7
>>> timescaled_series = F.timestamp_scale(99)(series) # 无操作，已弃用的操作
>>> timescaled_series.to_pandas() # 结果系列未改变
                      timestamp  value
0 1970-01-01 00:00:00.000000001    1.0
1 1970-01-01 00:00:00.000000101    2.0
2 1970-01-01 00:00:00.000000200    4.0
3 1970-01-01 00:00:00.000000201    8.0
```

此代码段演示了一个已弃用的时间尺度操作F.timestamp_scale(99)，对series没有实际影响，结果序列保持不变。
