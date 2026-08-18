来源: https://palantir.com/docs/zh/foundry/contour/expressions-window-functions/

# 窗口函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 窗口函数

PostgreSQL 文档 ↗将窗口函数定义如下：

> 一个窗口函数在与当前行相关的一组表行上执行计算。这类似于可以使用聚合函数完成的计算类型。但与常规聚合函数不同，使用窗口函数不会导致行组合成单个输出行——行保留其独立的身份。在幕后，窗口函数能够访问的不仅仅是查询结果的当前行。

一个窗口函数在与当前行相关的一组表行上执行计算。这类似于可以使用聚合函数完成的计算类型。但与常规聚合函数不同，使用窗口函数不会导致行组合成单个输出行——行保留其独立的身份。在幕后，窗口函数能够访问的不仅仅是查询结果的当前行。

本文档解释了一些您可能希望在 Contour表达式中使用的窗口函数的语法。有关窗口函数的更多背景信息，请参阅以下附加资源：

- 窗口函数 (PostgreSQL 文档) ↗
- SQL 窗口函数 (Mode Analytics 教程) ↗
- SQL 窗口函数简介 (Apache Drill) ↗
- 分析函数 (Oracle 文档) ↗
## 基本语法

在最基本的情况下，窗口函数可以分解为：

<function> OVER <some window>

其中函数是支持的聚合函数之一，窗口是表中行的子集。

您可以通过使用()来省略窗口——这将函数应用于表中的所有行。

以下示例将在每行中添加一个条目，其中包含date列中的最大值。

```
Copied!1
2
-- 计算数据集中日期字段的最大日期
MAX("date") OVER ()
```

## PARTITION BY

您还可以在窗口定义之前添加一个非必填的PARTITION BY子句。PARTITION BY根据给定列中的值对窗口内的行进行分组。然后将聚合函数分别应用于每个分区。

例如，在一个包含人员记录的表中，以下表达式计算男性和女性的总数，并为该行中的性别值添加计数：

```
Copied!1
COUNT("person_id") OVER (PARTITION BY "gender")
```

这是一个SQL窗口函数的例子，用于计算每个性别组中person_id的数量。以下是具体说明：

- COUNT("person_id"): 这是一个聚合函数，用于计算行数。在这里，它用于计算每个性别组中的person_id个数。
- OVER: 指定窗口函数的使用。
- PARTITION BY "gender": 按照gender列对数据进行分组，每个性别组单独计算person_id的数量。
通过这个窗口函数，你可以在不改变查询结果行数的情况下，得到每个性别组中的person_id数量。

## ORDER BY

对于在表达式中定义窗口的情况，您必须指定窗口的边界以及如何对表中的行进行排序。该子表达式可以简化为：

<如何排序表> ROWS BETWEEN <起始位置> AND <结束位置>

其中“如何排序表”是 (1) 按哪个列排序和 (2) 是升序还是降序排序。

以下是指定窗口边界（“起始位置”和“结束位置”）的可能情况：

- UNBOUNDED PRECEDING: 从表的开始到当前行。
- n PRECEDING(例如2 PRECEDING): 从当前行之前的n行到当前行。
- CURRENT ROW
- n FOLLOWING(例如5 FOLLOWING): 从当前行到当前行之后的n行。
- UNBOUNDED FOLLOWING: 从当前行到表的结束。
以下是一个示例表，其中标注了上述每种可能性：

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
FIRST_NAME |
------------
Adam       |<-- UNBOUNDED PRECEDING
...        |
Alison     |
Amanda     |
Jack       |
Jasmine    |
Jonathan   | <-- 1 PRECEDING
Leonard    | <-- CURRENT ROW
Mary       | <-- 1 FOLLOWING
Tracey     |
...        |
Zoe        | <-- UNBOUNDED FOLLOWING
```

这段代码展示了一个窗口函数操作中，窗口帧（Window Frame）的定义示例：

- UNBOUNDED PRECEDING：从分区的第一个行开始。
- 1 PRECEDING：窗口帧在当前行之前的1行。
- CURRENT ROW：窗口帧包含当前行。
- 1 FOLLOWING：窗口帧在当前行之后的1行。
- UNBOUNDED FOLLOWING：一直到分区的最后一行。
在窗口函数中，这些帧边界用于定义计算的范围。
(来源:blog.jooq.org ↗)

因此，给定一个包含销售记录的表，您可以使用以下方法找到最近5次销售的平均销售额：

```
Copied!1
2
3
4
AVG("sale_value") OVER (
    ORDER BY "date_of_sale" ASC
    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
)
```

这是一个SQL窗口函数示例，计算滑动窗口内的平均销售值：

- AVG("sale_value"): 计算销售值的平均值。
- OVER (ORDER BY "date_of_sale" ASC): 指定按销售日期升序排序。
- ROWS BETWEEN 4 PRECEDING AND CURRENT ROW: 定义窗口范围为当前行和前四行之间的行。这意味着平均值是基于当前行及其之前的四行数据计算的。
“最近5次销售”是窗口。OVER之后的子表达式按日期对表格进行排序，然后对于每一行，计算前4行和当前行的平均值。
## 综合应用

以下复杂示例结合了上述所有语法。此表达式显示了按产品类别分组的累计销售数量，直到当前销售。

```
Copied!1
2
3
4
5
6
7
8
COUNT("sale_id") OVER (
    PARTITION BY "product_category"
    -- 按照产品类别进行分区
    ORDER BY "date_of_sale" ASC
    -- 按销售日期升序排序
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    -- 从分区开始到当前行计算计数
)
```

请注意，现在的条目是按分区排序的——换句话说，表格首先进行分区，然后在每个分区内对行进行排序。

## 更多示例

假设您有一个记录购买商品的表格。您可以使用以下窗口函数来得出一个新列，用于计算购买的运行总计：

```
Copied!1
2
SUM("item_cost") OVER (ORDER BY "purchase_date" ASC
    RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )
```

这段代码使用了窗口函数在SQL中进行累积求和操作：

- SUM("item_cost")：计算当前窗口内"item_cost"列的和。
- OVER：定义窗口函数的范围。
- ORDER BY "purchase_date" ASC：按照"purchase_date"列的升序排列。
- RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW：定义窗口范围从查询结果的起始行到当前行（包含当前行）。这意味着对于每一行，计算从第一行到当前行的"item_cost"的累积和。
要计算按类别分组的累计总和，您可以添加分区：
```
Copied!1
2
3
SUM(“item_cost”) OVER (PARTITION BY “category”
    ORDER BY “purchase_date” ASC
    RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```

-- 此SQL窗口函数用于计算每个“category”（类别）内的累积“item_cost”（物品成本）
-- PARTITION BY “category”：按“category”列分区
-- ORDER BY “purchase_date” ASC：按“purchase_date”（购买日期）升序排序
-- RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW：从窗口的开始到当前行进行累加

```
这将按“category”列对行进行分区，按购买日期对每个类别中的行进行排序，并计算该类别中所有项目成本的运行总计。

## 陨石数据示例

您可以使用[陨石着陆数据集](../../foundry-docs/contour/media/meteorite_landings.csv)亲自尝试以下示例。该数据集来自The Meteoritical Society，通过[NASA数据门户 ↗](https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-9sfh)获取。

此表达式计算每个类别中最大的陨石：
```sql
-- 计算每个 "class" 分组中的最大 "mass" 值
MAX("mass") OVER (PARTITION BY "class" )
```

如果我们使用上述窗口函数推导出一个新列max_size_by_class：

……那么生成的表格将如下所示：

| name | class | mass | max_size_by_class |
| --- | --- | --- | --- |
| Jiddat al Harasis 450 | H3.7-5 | 217.741 | 3879 |
| Ramlat as Sahmah 422 | H3.7-5 | 3879 | 3879 |
| … |  |  |  |
| Beni Semguine | H5-an | 18 | 33.9 |
| Miller Range 07273 | H5-an | 33.9 | 33.9 |
| … |  |  |  |
| Allan Hills 88102 | Howardite | 8.33 | 40000 |
| Allan Hills 88135 | Howardite | 4.75 | 40000 |
| … |  |  |  |
| Yamato 81020 | CO3.0 | 270.34 | 3912 |
| Northwest Africa 2918 | CO3.0 | 237 | 3912 |

计算以陨石类别随时间的质量累积和（累计总和）：

```
Copied!1
2
3
4
SUM("mass") OVER (PARTITION BY "class"
    ORDER BY "year" ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

此SQL代码计算一个窗口函数。以下是代码的解释：

- SUM("mass") OVER (...)：计算窗口内的质量和。
- PARTITION BY "class"：按类对数据进行分区。
- ORDER BY "year" ASC：按照年份进行升序排序。
- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW：定义窗口的范围，从分区内的第一行到当前行。
这段代码的功能是计算每个“class”分区内，从最早的年份到当前行的累积“mass”总和。
这将按陨石类别对表进行分区，对每个分区按日期排序，然后对每行计算当前行与所有前面行在mass列的和，并将该和作为新列添加到当前行。

要计算按陨石类别分类的总（非累计）质量总和：

```
Copied!1
2
3
SUM("mass") OVER (PARTITION BY "class")
-- 计算"mass"的总和，按"class"进行分区
-- 这意味着对于每个"class"类别，计算其各自的"mass"总和
```

此聚合本身可能并不有用，但如果我们展开它，我们可以计算一个更有趣的统计数据——这颗陨石占该类别总质量的百分比是多少？

```
Copied!1
2
-- 计算每个“class”分组中，“mass”占总和的百分比
"mass" / (SUM("mass") OVER (PARTITION BY "class")) * 100
```

计算每个类别中找到的陨石总数（计数）：

```
Copied!1
2
3
COUNT("id") OVER (PARTITION BY "class")
-- 计算每个“class”分组中“id”的数量
-- 使用窗口函数 OVER()，通过 PARTITION BY 子句实现分组计数
```

## 非确定性

在窗口函数中使用ROW_NUMBER、FIRST、LAST、ARRAY_AGG或ARRAY_AGG_DISTINCT时，要注意非确定性。假设我们以列A进行分区并以列B进行排序。如果对于相同的列A值，有多行具有相同的列B值，那么这些窗口函数的结果可能是非确定的——在相同的输入数据和逻辑下，它们可能产生不同的结果。
