来源: https://palantir.com/docs/zh/foundry/foundryts/functions-series/

# foundryts.functions.series

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.series

## foundryts.functions.series(*args)

创建一个对所有输入时间序列的引用，以便可以对其进行操作。

每个输入时间序列ID被转换为NodeCollection中的一个元素，其中每个元素只是Foundry生态系统中现有时间序列的引用。

- 参数:*args(*str) – 用于创建NodeCollection中时间序列引用的所有时间序列ID的参数。
参数:*args(

```
*
```

str) – 用于创建NodeCollection中时间序列引用的所有时间序列ID的参数。

- 返回:传递的所有时间序列ID的:py`NodeCollection`。
返回:传递的所有时间序列ID的:py`NodeCollection`。

- 返回类型:py:class:`NodeCollection
返回类型:py:class:

```
`
```

NodeCollection

## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| series | str | 时间序列ID |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

points()

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
>>> altimeter_series = F.series(
...     "altimeter_aircraft-1",
...     "altimeter_aircraft-2",
... )
# 创建一个序列对象，包含两个高度计数据系列，分别是飞机1和飞机2的高度计数据

>>> altimeter_series.to_pandas()
# 将序列对象转换为Pandas数据框，以便更方便的数据处理和分析

                   series               timestamp     value
0    altimeter_aircraft-1 2024-09-06 07:00:00.000 -1.185493
1    altimeter_aircraft-1 2024-09-06 07:01:30.983  0.830117
2    altimeter_aircraft-1 2024-09-06 07:03:01.966  0.115240
3    altimeter_aircraft-1 2024-09-06 07:04:32.949  0.059973
4    altimeter_aircraft-1 2024-09-06 07:06:03.932 -0.290032
..                    ...                     ...       ...
495  altimeter_aircraft-2 2024-09-06 19:30:36.585  1.204543
496  altimeter_aircraft-2 2024-09-06 19:32:07.568 -1.183036
497  altimeter_aircraft-2 2024-09-06 19:33:38.551  0.216189
498  altimeter_aircraft-2 2024-09-06 19:35:09.534 -0.854239
499  altimeter_aircraft-2 2024-09-06 19:36:40.517  0.312806
# 输出的数据框中包含三个列：系列名称（series）、时间戳（timestamp）和对应的值（value）
```
