来源: https://palantir.com/docs/zh/foundry/foundryts/search-search/

# foundryts.search.Search

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.search.Search

## classfoundryts.search.Search

用于使用Ontology执行时间序列搜索查询的接口。

此接口通过Ontology中的属性来搜索时间序列集合。可以通过细化的筛选来确定要在搜索中包含哪些对象。

这对于在程序化访问时间序列是动态的并基于Ontology的属性值时，查询多个时间序列非常有用。请考虑下面的示例：

您的Ontology包含一个股票对象类型，其属性为[ticker,sector,exchange,price]。
要获取“技术”领域所有股票的价格，您可以使用Search.series()进行以下查询：

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
>>> fts = FoundryTS()
>>> tech_stocks_price = fts.search.series(
...     query=(ontology("sector") == "Technology"),
...     object_types=["stock"],
...     property_type_id="price"
... )
>>> tech_stocks_price.to_pandas()
           series               timestamp   value
    0     stock-A 2023-01-01 00:00:00.000  150.75
    1     stock-A 2023-01-02 00:00:00.000  152.30
    2     stock-A 2023-01-03 00:00:00.000  148.90
    3     stock-B 2023-01-01 00:00:00.000  200.50
    4     stock-B 2023-01-02 00:00:00.000  202.75
    5     stock-B 2023-01-03 00:00:00.000  198.40
    6     stock-C 2023-01-01 00:00:00.000  120.10
    7     stock-C 2023-01-02 00:00:00.000  118.95
    8     stock-C 2023-01-03 00:00:00.000  121.70
    9     stock-D 2023-01-01 00:00:00.000  310.20
    10    stock-D 2023-01-02 00:00:00.000  312.50
    11    stock-D 2023-01-03 00:00:00.000  308.90
```

该代码片段用于从一个时间序列数据库中检索技术类股票的价格数据。

- FoundryTS()：初始化一个时间序列数据库实例。
- fts.search.series()：查询符合条件的时间序列数据。query=(ontology("sector") == "Technology")：筛选属于“Technology”行业的股票。object_types=["stock"]：指定查询的对象类型为股票。property_type_id="price"：选择要查询的属性类型为价格。
- query=(ontology("sector") == "Technology")：筛选属于“Technology”行业的股票。
- object_types=["stock"]：指定查询的对象类型为股票。
- property_type_id="price"：选择要查询的属性类型为价格。
- tech_stocks_price.to_pandas()：将查询结果转换为Pandas DataFrame格式以便于数据处理和分析。
输出的DataFrame中包含三个列：

- series：股票名称。
- timestamp：时间戳，表示该价格的日期和时间。
- value：对应时间点的股票价格。
同样，您可以搜索特定交易所的股票或使用您的对象类型的其他相关属性进行搜索。
搜索方法可通过FoundryTS.search单例属性访问，如上例所示。

搜索只能查询时间序列引用，而不能查询时间序列中的值（例如搜索值满足谓词的系列或点）。要搜索时间序列中的数据，请参见dsl()和time_series_search()。

#### abstractseries(query, max_results=10000, **kwargs)

使用传递的查询搜索时间序列，并返回包含所有结果的NodeCollection。

搜索语法使用==运算符检查Ontology中的属性相等性。 此外，您可以使用object_types将搜索范围限定为Ontology中的特定对象类型。建议这样做以避免搜索整个Ontology。

- 参数:query(Any) – 由上述运算符和操作数组成的搜索查询。max_results(int,非必填) – 要返回的系列定义结果的最大数量，介于1到10,000之间（默认是10,000）。**kwargs– 其他搜索行为的选项和标志。
- query(Any) – 由上述运算符和操作数组成的搜索查询。
- max_results(int,非必填) – 要返回的系列定义结果的最大数量，介于1到10,000之间（默认是10,000）。
- **kwargs– 其他搜索行为的选项和标志。
- 关键字参数:object_types(List[str],非必填) – 在查询中搜索具有时间序列属性的Ontology对象（默认是在所有时间序列对象中搜索）。property_type_id(str,非必填) – 要返回的对象中的时间序列属性，如果一个对象包含多个时间序列属性（TSPs）且未设置默认TSP，则这是必需的。↗ 可以在平台中为任何具有TSP的对象定义默认TSP。experimental_enable_complex_properties(bool,非必填) – 是否将时间序列属性（TSPs）发送到时间序列后端。当使用非原始时间依赖属性（例如↗ 模板）或由多个时间序列同步支持的时间序列属性（此类时间序列在Ontology中写为↗ 合格系列ID）时，这是必需的（默认是False）。
- object_types(List[str],非必填) – 在查询中搜索具有时间序列属性的Ontology对象（默认是在所有时间序列对象中搜索）。
- property_type_id(str,非必填) – 要返回的对象中的时间序列属性，如果一个对象包含多个时间序列属性（TSPs）且未设置默认TSP，则这是必需的。↗ 可以在平台中为任何具有TSP的对象定义默认TSP。
- experimental_enable_complex_properties(bool,非必填) – 是否将时间序列属性（TSPs）发送到时间序列后端。当使用非原始时间依赖属性（例如↗ 模板）或由多个时间序列同步支持的时间序列属性（此类时间序列在Ontology中写为↗ 合格系列ID）时，这是必需的（默认是False）。
- 返回:一个NodeCollection，包含所有与搜索查询匹配的时间序列引用作为FunctionNode。
- 返回类型:NodeCollection
确保您在查询中使用的属性（通过ontology()）是可搜索的，否则搜索将失败。时间序列属性不可搜索。

使用非原始时间依赖属性（例如模板或多同步属性）时，需要experimental_enable_complex_properties标志。

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
>>> tsp_search_without_query = fts.search.series(object_types=["stock-series"])
# 搜索不带查询条件的时间序列，指定对象类型为“stock-series”（股票系列）

>>> tsp_search_without_query.to_pandas()
# 将搜索结果转换为 Pandas DataFrame 格式

       series               timestamp  value
0    SPX_open 1970-01-01 00:00:00.000    1.5
1    SPX_open 1970-01-01 00:00:00.001    2.5
2    SPX_open 1970-01-01 00:00:00.004    3.5
3  ZVZZT_open 1970-01-01 00:00:00.000    2.5
4  ZVZZT_open 1970-01-01 00:00:00.001    3.5
5  ZVZZT_open 1970-01-01 00:00:00.004    4.5
```

这个代码片段展示了如何使用fts.search.series方法获取股票时间序列数据，并将其转换为 Pandas DataFrame 格式。结果显示了不同股票（如SPX_open和ZVZZT_open）在不同时间点的数值。

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
>>> tsp_search = fts.search.series((search.ontology("ticker") == "SPX"))
# 使用 `fts.search.series` 方法来搜索时间序列，其中 `search.ontology("ticker") == "SPX"` 表示筛选出代号为 "SPX" 的数据。

>>> tsp_search.to_pandas()
# 将搜索到的时间序列数据转换为 Pandas DataFrame 格式。

      series               timestamp  value
#     系列名称               时间戳      值

0   SPX_open 1970-01-01 00:00:00.000    1.5
#   SPX 开盘价  时间戳为 1970-01-01 00:00:00.000  值为 1.5

1   SPX_open 1970-01-01 00:00:00.001    2.5
#   SPX 开盘价  时间戳为 1970-01-01 00:00:00.001  值为 2.5

2   SPX_open 1970-01-01 00:00:00.004    3.5
#   SPX 开盘价  时间戳为 1970-01-01 00:00:00.004  值为 3.5

3  SPX_close 1970-01-01 00:00:00.005   15.0
#   SPX 收盘价  时间戳为 1970-01-01 00:00:00.005  值为 15.0

4  SPX_close 1970-01-01 00:00:00.006   25.0
#   SPX 收盘价  时间戳为 1970-01-01 00:00:00.006  值为 25.0

5  SPX_close 1970-01-01 00:00:00.007   35.0
#   SPX 收盘价  时间戳为 1970-01-01 00:00:00.007  值为 35.0
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
13
14
15
>>> tsp_search_with_experimental_properties = fts.search.series(
...     (search.ontology("ticker") == "SPX"),
...     object_types=["stock-series"],
...     experimental_enable_complex_properties=True,
... )
# 使用 `fts.search.series` 方法进行搜索，寻找标识符为 "SPX" 的股票系列数据
# `experimental_enable_complex_properties=True` 启用实验性的复杂属性功能

>>> tsp_search_with_experimental_properties.to_pandas()
# 将搜索结果转换为 Pandas DataFrame 格式以便于数据处理和分析
                        series               timestamp  value
0  stock-series:SPX:open_price 1970-01-01 00:00:00.000    1.5
1  stock-series:SPX:open_price 1970-01-01 00:00:00.001    2.5
2  stock-series:SPX:open_price 1970-01-01 00:00:00.004    3.5
# 显示结果中的数据行，包括系列名称、时间戳和对应的值
```
