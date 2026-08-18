来源: https://palantir.com/docs/zh/foundry/foundryts/functions-points/

# foundryts.functions.points

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.points

## foundryts.functions.points(*list_of_points, name='point-set')

创建一组用户定义的点，这些点作为时间序列而不是通过同步写入。

这对于创建用于插值或DSL公式等操作的参考时间序列非常有用。对于在不设置测试时间序列的情况下熟悉FoundryTS，这也是一个有帮助的工具。

- 参数:*list_of_points(Tuple*[*TimestampType,float]|Tuple*[*TimestampType,str]) – 时间戳和该时间戳点值的元组作为非关键词位置参数。name(str,非必填) – 点集的别名，将用作所有下游操作的时间序列ID。
- *list_of_points(Tuple*[*TimestampType,float]|Tuple*[*TimestampType,str]) – 时间戳和该时间戳点值的元组作为非关键词位置参数。
- name(str,非必填) – 点集的别名，将用作所有下游操作的时间序列ID。
- 返回:一个点集，像时间序列一样用于所有下游操作。
- 返回类型:函数节点
## 数据框架模式

| 列名称 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

series()

所有点值应具有相同的类型。

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
>>> numeric_series = F.points(
...     (0, 0.0), (100, 100.0), (140, 140.0), (200, 200.0), name="numeric"
... )
# 创建一个数值序列，其中包含四个数据点，每个点由一个时间戳和对应的数值组成。
# 这些数据点的名称为 "numeric"。

>>> numeric_series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000000    0.0
1 1970-01-01 00:00:00.000000100  100.0
2 1970-01-01 00:00:00.000000140  140.0
3 1970-01-01 00:00:00.000000200  200.0
# 将创建的数值序列转换为 Pandas DataFrame 格式。
# 输出的 DataFrame 显示了每个数据点的时间戳和对应的数值。
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
16
17
18
19
>>> enum_series = F.points(
...     (100, "ON"),
...     (120, "ON"),
...     (130, "OFF"),
...     (150, "ON"),
...     (160, "OFF"),
...     name="enum",
... )
# 创建一个名为 `enum` 的时间序列，其中每个点都有一个时间戳和一个状态（"ON" 或 "OFF"）

>>> enum_series.to_pandas()
# 将时间序列转换为 Pandas DataFrame 格式
                      timestamp value
0 1970-01-01 00:00:00.000000100    ON
1 1970-01-01 00:00:00.000000120    ON
2 1970-01-01 00:00:00.000000130   OFF
3 1970-01-01 00:00:00.000000150    ON
4 1970-01-01 00:00:00.000000160   OFF
# 显示时间戳和对应的状态值
```
