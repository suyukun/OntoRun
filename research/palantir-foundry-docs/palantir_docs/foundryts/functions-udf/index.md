来源: https://palantir.com/docs/zh/foundry/foundryts/functions-udf/

# foundryts.functions.udf

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.udf

## foundryts.functions.udf(func, columns=None, types=None)

返回一个函数，该函数将在查询结果的数据框上调用用户定义的函数。

用户定义函数（UDF）是一种特殊的时间序列功能，允许在返回数据框的查询结果上运行自定义的Python代码。UDF应用于所有查询结果的最终数据框。

- 参数:func(Callable[[pandas.DataFrame], Any]) – 要应用的用户定义函数。columns(List[str],非必填) – 当func返回pandas.DataFrame时，结果数据框的列名列表
（默认为输入数据框中的原始列名）。types(List*[*Any],非必填) – 当func返回pandas.DataFrame时，结果数据框的列类型列表
（默认为输入数据框中的原始列类型）。
- func(Callable[[pandas.DataFrame], Any]) – 要应用的用户定义函数。
- columns(List[str],非必填) – 当func返回pandas.DataFrame时，结果数据框的列名列表
（默认为输入数据框中的原始列名）。
- types(List*[*Any],非必填) – 当func返回pandas.DataFrame时，结果数据框的列类型列表
（默认为输入数据框中的原始列类型）。
- 返回:将UDF应用于输入的 :py`pandas.DataFrame` 的结果。
- 返回类型:Any
dsl()

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
>>> series = F.points((0, 0.0), (100, 100.0), (140, 140.0), (200, 200.0), name="series")
# 创建一个名为 "series" 的时间序列数据，其中包含时间戳和对应的值
>>> series.to_pandas()
# 将时间序列数据转换为 Pandas DataFrame 格式以便查看
                      timestamp  value
0 1970-01-01 00:00:00.000000000    0.0
1 1970-01-01 00:00:00.000000100  100.0
2 1970-01-01 00:00:00.000000140  140.0
3 1970-01-01 00:00:00.000000200  200.0
# 数据展示：每一行包含一个时间戳和其对应的值
```

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
>>> def double(df: pandas.DataFrame) -> pandas.DataFrame:
...     df["value"] *= 2  # 将 "value" 列的值乘以2
...     return df
>>> doubled_series = F.udf(double, ["timestamp", "value"], [int, float])(series)
# 使用自定义函数 `double` 并指定输入输出类型为 ["timestamp", "value"] 和 [int, float]，对 `series` 进行变换
>>> doubled_series.to_pandas()
# 将结果转换为 pandas DataFrame
                      timestamp  value
0 1970-01-01 00:00:00.000000000    0.0
1 1970-01-01 00:00:00.000000100  200.0
2 1970-01-01 00:00:00.000000140  280.0
3 1970-01-01 00:00:00.000000200  400.0
```
