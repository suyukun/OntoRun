来源: https://palantir.com/docs/zh/foundry/foundryts/functions-distribution/

# foundryts.functions.distribution

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.distribution

## foundryts.functions.distribution(start=None, end=None, start_value=None, end_value=None, bins=None)

返回一个函数，该函数将评估一个或多个时间序列的分布。

分布是将点分解为值的分箱，以划分请求的值范围。
评估分布返回一个描述其范围内点数的分箱列表，以及范围的起始和结束。

分布可以应用于单个系列或多个系列，在这种情况下，分布函数在最终数据框中为每个分箱考虑所有系列的值的并集。

每个分箱的值范围的增量是恒定的，并使用以下公式计算
(最大值 - 最小值) / (分箱数)

- 参数:start(Union[int,datetime,str],非必填) – 时间戳（包含），用于起始评估提供的系列的分布（默认是任何输入时间序列中最早的时间戳）end(Union[int,datetime,str],非必填) – 时间戳（不包含），用于结束评估提供的系列的分布（默认是任何输入时间序列中最新的时间戳）start_value(float,非必填) – 值范围的下界（包含），用于评估分布（默认是任何输入时间序列的最小值）end_value(float,非必填) – 值范围的上界（不包含），用于评估分布（默认是任何输入时间序列的最大值）bins(int,非必填) – 用于分配点的值分箱数（默认是10）。
- start(Union[int,datetime,str],非必填) – 时间戳（包含），用于起始评估提供的系列的分布（默认是任何输入时间序列中最早的时间戳）
- end(Union[int,datetime,str],非必填) – 时间戳（不包含），用于结束评估提供的系列的分布（默认是任何输入时间序列中最新的时间戳）
- start_value(float,非必填) – 值范围的下界（包含），用于评估分布（默认是任何输入时间序列的最小值）
- end_value(float,非必填) – 值范围的上界（不包含），用于评估分布（默认是任何输入时间序列的最大值）
- bins(int,非必填) – 用于分配点的值分箱数（默认是10）。
- 返回:一个函数，接受一个或多个系列作为输入，并在指定或默认数量的分箱中生成分布。
- 返回类型:(Union[FunctionNode,NodeCollection]) -> SummarizerNode
## 数据框架架构

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| start_timestamp | datetime | 分布的起始时间（包含） |
| end_timestamp | datetime | 分布的结束时间（不包含） |
| start | float | 值的下界（包含） |
| end | float | 值的上界（不包含） |
| delta | float | 每个分箱的最小值和最大值之间的差异。鉴于分箱的计算方式，所有分箱的delta是固定的。 |
| distribution_values.start | float | 分布分箱的起始值 |
| distribution_values.end | float | 分布分箱的结束值 |
| distribution_values.count | int | 分布分箱中的实例数 |

statistics(),scatter()

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
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
>>> series_1 = F.points(
...     (1, 0.0),
...     (101, 10.2),
...     (200, 11.3),
...     (201, 11.1),
...     (299, 11.2),
...     (300, 12.0),
...     (400, 11.7),
...     (500, 16.0),
...     (123450, 11.8),
...     name="series-1",
... )
# 创建一个名为 series-1 的时间序列，包含一组时间戳和对应的值

>>> series_2 = F.points(
...     (1, 0.5),
...     (101, 0.2),
...     (200, 1.3),
...     (201, 0.1),
...     (299, 1.2),
...     (300, 1.4),
...     (400, 1.0),
...     (500, 2.0),
...     (123450, 1.0),
...     name="series-2",
... )
# 创建一个名为 series-2 的时间序列，包含一组时间戳和对应的值

>>> series_1.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    0.0
1 1970-01-01 00:00:00.000000101   10.2
2 1970-01-01 00:00:00.000000200   11.3
3 1970-01-01 00:00:00.000000201   11.1
4 1970-01-01 00:00:00.000000299   11.2
5 1970-01-01 00:00:00.000000300   12.0
6 1970-01-01 00:00:00.000000400   11.7
7 1970-01-01 00:00:00.000000500   16.0
8 1970-01-01 00:00:00.000123450   11.8
# 将 series_1 转换为 Pandas DataFrame 格式，其中包含时间戳和对应的值

>>> series_2.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    0.5
1 1970-01-01 00:00:00.000000101    0.2
2 1970-01-01 00:00:00.000000200    1.3
3 1970-01-01 00:00:00.000000201    0.1
4 1970-01-01 00:00:00.000000299    1.2
5 1970-01-01 00:00:00.000000300    1.4
6 1970-01-01 00:00:00.000000400    1.0
7 1970-01-01 00:00:00.000000500    2.0
8 1970-01-01 00:00:00.000123450    1.0
# 将 series_2 转换为 Pandas DataFrame 格式，其中包含时间戳和对应的值

>>> nc = NodeCollection(series_1, series_2)
# 创建一个 NodeCollection 对象，包含 series_1 和 series_2 两个时间序列
```

```
Copied!1
2
3
4
5
6
>>> single_dist = F.distribution(bins=3)(series_1) # 单个序列的分布
>>> single_dist.to_pandas()
      delta  distribution_values.count  distribution_values.end  distribution_values.start   end end_timestamp  start               start_timestamp
0  5.333333                          1                 5.333333                   0.000000  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
1  5.333333                          1                10.666667                   5.333333  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
2  5.333333                          7                16.000000                  10.666667  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
```

### 代码说明：

- single_dist = F.distribution(bins=3)(series_1)：计算series_1的分布，将其分为3个区间（bins）。
- single_dist.to_pandas()：将分布数据转换为 Pandas 数据帧格式。
- 表格中的每一行代表一个区间：delta：区间宽度。distribution_values.count：该区间内的元素数量。distribution_values.start和distribution_values.end：区间的起始和结束值。start和end：整个数据集的起始和结束值。start_timestamp和end_timestamp：时间戳范围。
- delta：区间宽度。
- distribution_values.count：该区间内的元素数量。
- distribution_values.start和distribution_values.end：区间的起始和结束值。
- start和end：整个数据集的起始和结束值。
- start_timestamp和end_timestamp：时间戳范围。
```
Copied!1
2
3
4
5
6
>>> multiple_dist = F.distribution(bins=3)(nc) # 多个序列的分布计算，设置分成3个区间
>>> multiple_dist.to_pandas()
      delta  distribution_values.count  distribution_values.end  distribution_values.start   end end_timestamp  start               start_timestamp
0  5.333333                         10                 5.333333                   0.000000  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
1  5.333333                          1                10.666667                   5.333333  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
2  5.333333                          7                16.000000                  10.666667  16.0    2262-01-01    0.0 1677-09-21 00:12:43.145225216
```

这个代码片段计算了一个数据序列的分布，将其划分为3个区间（bins）。每个区间的宽度为delta = 5.333333，并显示了每个区间的样本数（distribution_values.count）、区间的起始值和结束值。时间戳列用于标识数据的时间范围。
