来源: https://palantir.com/docs/zh/foundry/foundryts/functions-last-point/

# foundryts.functions.last_point

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.last_point

## foundryts.functions.last_point()

返回一个提取单个时间序列中最新点的函数。

返回的点是给定时间序列范围内的最后出现的点。当序列为空时，返回一个空的摘要。

- 返回：一个接受单个时间序列并返回所提供序列中最后一个点的函数。数据框包含一行，带有最后一个点。
- 返回类型：(函数节点) -> SummarizerNode
## 数据框架架构

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

time_extent(),first_point()

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
>>> series = F.points(
...     (1, 0.0),            # 时间戳为1，值为0.0
...     (101, 10.2),         # 时间戳为101，值为10.2
...     (200, 11.3),         # 时间戳为200，值为11.3
...     (123450, 11.8),      # 时间戳为123450，值为11.8
... )
>>> series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000001    0.0
1 1970-01-01 00:00:00.000000101   10.2
2 1970-01-01 00:00:00.000000200   11.3
3 1970-01-01 00:00:00.000123450   11.8
```

该代码段通过F.points创建了一个时间序列对象，其中每个元组包含一个时间戳和一个值。使用series.to_pandas()方法将该时间序列对象转换为 Pandas DataFrame 格式。时间戳以纳秒为单位并格式化为标准日期时间格式。

```
Copied!1
2
3
4
>>> lp = F.last_point()(series)  # 使用 F.last_point() 函数获取 series 的最后一个数据点
>>> lp.to_pandas()  # 将最后一个数据点转换为 Pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000123450   11.8
```

这里的代码展示了如何使用F.last_point()函数提取时间序列series的最后一个数据点，并将其转换为 Pandas DataFrame 以便于数据处理和分析。
