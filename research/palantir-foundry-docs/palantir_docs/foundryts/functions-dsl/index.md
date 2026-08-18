来源: https://palantir.com/docs/zh/foundry/foundryts/functions-dsl/

# foundryts.functions.dsl

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# foundryts.functions.dsl

## foundryts.functions.dsl(program, return_type=None, labels=None, before='nearest', internal='default', after='nearest')

返回一个函数，该函数将DSL公式应用于一个或多个输入时间序列以生成新的时间序列。

该公式应用于输入时间序列中的每个时间戳。对于缺少值的输入时间序列的时间戳，使用指定的插值策略。有关可用策略的列表，请参阅interpolate()。

DSL公式可以应用于一元、二元或n元操作数。DSL中的所有操作都是可组合的，允许您通过组合更简单的操作来搭建复杂表达式。

查找↗ 时间序列DSL语法的完整参考。

- 参数:program(str) – 使用↗ 时间序列DSL参考文档中的语法应用于一个或多个输入时间序列的公式。return_type(Type,非必填) – （已弃用）用于变换系列值的类型。labels(List[str],非必填) – 有序标签列表，用于在公式中引用每个输入时间序列（默认是[‘a’, ‘b’, …, ‘aa’, ‘ab’, …]）。before(Union[str,List[str]],非必填) – 在系列中的第一个点之前进行插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（默认是NEAREST）。internal(Union[str,List[str]],非必填) – 在现有点之间插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（数字系列默认是LINEAR，枚举时间序列默认是PREVIOUS）。after(Union[str,List[str]],非必填) – 在系列中的第一个点之后进行插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（默认是NEAREST）。
- program(str) – 使用↗ 时间序列DSL参考文档中的语法应用于一个或多个输入时间序列的公式。
- return_type(Type,非必填) – （已弃用）用于变换系列值的类型。
- labels(List[str],非必填) – 有序标签列表，用于在公式中引用每个输入时间序列（默认是[‘a’, ‘b’, …, ‘aa’, ‘ab’, …]）。
- before(Union[str,List[str]],非必填) – 在系列中的第一个点之前进行插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（默认是NEAREST）。
- internal(Union[str,List[str]],非必填) – 在现有点之间插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（数字系列默认是LINEAR，枚举时间序列默认是PREVIOUS）。
- after(Union[str,List[str]],非必填) – 在系列中的第一个点之后进行插值的策略，可以是每个系列的列表，使用interpolate()中的有效策略（默认是NEAREST）。
- 返回:一个函数，该函数接受一个或多个时间序列并将公式应用于输入时间序列以返回单个更新的时间序列。
- 返回类型:(FunctionNode) -> FunctionNode
## 数据框架模式

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | pandas.Timestamp | 点的时间戳 |
| value | Union[float, str] | 点的值 |

interpolate(),udf()

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
>>> series_1 = F.points(
...     (10, 6.0),
...     (20, 11.0),
...     (30, 24.0),
...     (40, float("inf")),  # 无穷大值
...     (50, 45.0),
...     (60, 96.0),
...     name="series-1",
... )
>>> series_2 = F.points(
...     (10, 8.0),
...     (20, 12.0),
...     (30, 24.0),
...     (40, 48.0),
...     (50, float("NaN")),  # 非数字值（NaN）
...     (60, 196.0),
...     name="series-2",
... )
>>> series_1.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010    6.0
1 1970-01-01 00:00:00.000000020   11.0
2 1970-01-01 00:00:00.000000030   24.0
3 1970-01-01 00:00:00.000000040    inf
4 1970-01-01 00:00:00.000000050   45.0
5 1970-01-01 00:00:00.000000060   96.0
>>> series_2.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010    8.0
1 1970-01-01 00:00:00.000000020   12.0
2 1970-01-01 00:00:00.000000030   24.0
3 1970-01-01 00:00:00.000000040   48.0
4 1970-01-01 00:00:00.000000050    NaN
5 1970-01-01 00:00:00.000000060  196.0
```

在这个代码示例中，F.points()函数被用来创建两个数据序列series_1和series_2。每个序列由一组（时间戳，值）对组成。float("inf")表示无穷大，而float("NaN")表示一个非数字值。随后，to_pandas()方法被调用以将这些序列转换为 Pandas DataFrame 格式，便于数据分析和处理。

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
>>> sum_formula = "a+b"
>>> sum_series = F.dsl(sum_formula)([series_1, series_2])
# 将两个序列相加，生成一个新的序列
>>> sum_series.to_pandas()
# 转换为 pandas DataFrame 格式
                      timestamp  value
0 1970-01-01 00:00:00.000000010   14.0
1 1970-01-01 00:00:00.000000020   23.0
2 1970-01-01 00:00:00.000000030   48.0
3 1970-01-01 00:00:00.000000040    inf
4 1970-01-01 00:00:00.000000050    NaN
5 1970-01-01 00:00:00.000000060  292.0
```

```
Copied!1
2
3
4
5
6
7
>>> even_only_formula = "a % 2 == 0 ? a : skip"  # 使用条件表达式过滤出偶数，"skip"表示跳过不符合条件的元素。
>>> even_series_1 = F.dsl(even_only_formula)(series_1)  # 应用公式过滤 series_1，保留偶数。
>>> even_series_1.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010    6.0
1 1970-01-01 00:00:00.000000030   24.0
2 1970-01-01 00:00:00.000000060   96.0
```

这段代码使用了一种基于公式的DSL（领域特定语言）来过滤数据序列中的偶数，并将结果转换为Pandas DataFrame格式展示。

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
>>> argmin_formula = "argmin(a,b)"
>>> argmin_series = F.dsl(argmin_formula)([series_1, series_2])
>>> argmin_series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010    0.0
1 1970-01-01 00:00:00.000000020    0.0
2 1970-01-01 00:00:00.000000030    0.0
3 1970-01-01 00:00:00.000000040    1.0 # 无穷大大于48
4 1970-01-01 00:00:00.000000050    0.0
5 1970-01-01 00:00:00.000000060    0.0
```

在这段代码中，我们使用一个定义为"argmin(a,b)"的公式来比较两个序列series_1和series_2，并且返回每一对元素中较小的值。然后使用to_pandas()方法将结果转换为 pandas 数据框格式。第 4 行的注释解释了此处为什么返回值是 1.0：因为比较中无穷大比48大，所以选择了较小的值。

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
>>> pow_formula = "pow(a, 2)"
>>> pow2_series = F.dsl(pow_formula)([series_1])
# 使用 pow 函数计算 series_1 中每个元素的平方
>>> pow2_series.to_pandas()
# 将结果转换为 Pandas DataFrame 格式
                      timestamp   value
0 1970-01-01 00:00:00.000000010    36.0
1 1970-01-01 00:00:00.000000020   121.0
2 1970-01-01 00:00:00.000000030   576.0
3 1970-01-01 00:00:00.000000040     inf  # 可能由于输入值过大导致计算结果为无穷大
4 1970-01-01 00:00:00.000000050  2025.0
5 1970-01-01 00:00:00.000000060  9216.0
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
>>> non_nan_formula = "isnan(b) ? a : b"
# 使用自定义的DSL公式“isnan(b) ? a : b”来处理两个系列的数据，如果b是NaN，则选择a的值，否则选择b的值。
>>> non_nan_series = F.dsl(non_nan_formula)([series_1, series_2])
# 将处理后的结果转换为Pandas DataFrame以便查看。
>>> non_nan_series.to_pandas()
                    timestamp  value
0 1970-01-01 00:00:00.000000010    8.0
1 1970-01-01 00:00:00.000000020   12.0
2 1970-01-01 00:00:00.000000030   24.0
3 1970-01-01 00:00:00.000000040   48.0
4 1970-01-01 00:00:00.000000050   45.0 # 仅从series-1获取的值
5 1970-01-01 00:00:00.000000060  196.0
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
>>> non_inf_formula = "isfinite(a) ? a : b"
>>> non_inf_series = F.dsl(non_inf_formula)([series_1, series_2])
>>> non_inf_series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010    6.0
1 1970-01-01 00:00:00.000000020   11.0
2 1970-01-01 00:00:00.000000030   24.0
3 1970-01-01 00:00:00.000000040   48.0 # 仅来自 series-2 的值
4 1970-01-01 00:00:00.000000050   45.0
5 1970-01-01 00:00:00.000000060   96.0
```

代码解释：

- non_inf_formula = "isfinite(a) ? a : b"定义了一个条件公式，用于检查a是否是有限的值（非无穷大）。如果是有限的，返回a，否则返回b。
- non_inf_series = F.dsl(non_inf_formula)([series_1, series_2])使用定义的公式生成一个新的数据序列non_inf_series，其中series_1和series_2是输入数据序列。
- non_inf_series.to_pandas()将结果数据序列转换为 Pandas 数据框。
- 在结果中，第四行的48.0仅来自于series-2，因为在该行中series-1的值不是有限的。
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
>>> assignment_formula = '''
... var doubled_shifted = a * 2; // 所有值都翻倍
... doubled_shifted += 10; // 在所有翻倍的值上加10
... doubled_shifted - b // 计算翻倍后加10的值与b的差值
... '''
>>> var_assigned_series = F.dsl(assignment_formula)([series_1, series_2])
>>> var_assigned_series.to_pandas()
                      timestamp  value
0 1970-01-01 00:00:00.000000010   14.0
1 1970-01-01 00:00:00.000000020   20.0
2 1970-01-01 00:00:00.000000030   34.0
3 1970-01-01 00:00:00.000000040    inf
4 1970-01-01 00:00:00.000000050    NaN
5 1970-01-01 00:00:00.000000060    6.0
```

这里的代码片段定义了一个数学公式assignment_formula，用于计算两个系列数据series_1和series_2的组合结果。公式的具体步骤如下：

- 将系列数据a的所有值翻倍，结果保存在doubled_shifted中。
- 在翻倍的结果上加上 10。
- 计算翻倍后加 10 的结果与b的差值。
最后，调用var_assigned_series.to_pandas()将结果转换为 Pandas 数据框格式进行显示。
