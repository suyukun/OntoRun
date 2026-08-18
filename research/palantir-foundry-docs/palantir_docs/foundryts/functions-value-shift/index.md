来源: https://palantir.com/docs/zh/foundry/foundryts/functions-value-shift/

# foundryts.functions.value_shift

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.value_shift

## foundryts.functions.value_shift(delta)

返回一个将单个时间序列的所有值按指定增量进行变换的函数。

对于具有点(timestamp, value)的源时间序列，在以delta进行变换后，结果值变换后的时间序列将具有点(timestamp, value + delta)。

- 参数：delta(int) – 用于变换每个点的值的增量。
- 返回：一个接受单个时间序列作为输入并返回值变换后的时间序列的函数。
- 返回类型：(FunctionNode) ->FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | float | 点的变换值 |

timestamp_scale(),time_shift()

此函数仅适用于数值序列。

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
>>> value_shifted = F.value_shift(3.0)(series)
# 使用 F.value_shift 对 series 进行值偏移操作，偏移量为3.0
>>> value_shifted.to_pandas()
# 将结果转换为 Pandas 数据框格式
                      timestamp    value
0 1970-01-01 00:00:00.000000100  3.00000
1 1970-01-01 00:00:00.000000200      inf
2 1970-01-01 00:00:00.000000300  6.14159
3 1970-01-01 00:00:02.147483647  4.00000
# 输出的结果包含时间戳和对应的值，其中某些值可能为无穷大（inf）
```

```
Copied!1
2
3
4
5
6
7
>>> negative_value_shifted = F.value_shift(-3.0)(series)
>>> negative_value_shifted.to_pandas()
                      timestamp    value
0 1970-01-01 00:00:00.000000100 -3.00000
1 1970-01-01 00:00:00.000000200      inf
2 1970-01-01 00:00:00.000000300  0.14159
3 1970-01-01 00:00:02.147483647 -2.00000
```

该代码片段展示了使用F.value_shift(-3.0)函数对一个数据序列series进行值平移操作，并将结果转换为 Pandas 数据框的过程。

- negative_value_shifted = F.value_shift(-3.0)(series)：对series中的每个值减去3.0。
- negative_value_shifted.to_pandas()：将平移后的结果转换为 Pandas 数据框格式以便查看。
输出显示了时间戳timestamp和相应的值value。注意第二行的值为inf，这表明在平移操作中可能存在无穷大值的情况。
