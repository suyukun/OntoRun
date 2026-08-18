来源: https://palantir.com/docs/zh/foundry/contour/expressions-relative-dates/

# 派生相对日期

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 派生相对日期

本指南将向您展示如何使用Contour的表达语言从数据集中派生相对日期。

在本例中，我们希望查看按日历周分组的日期，并查看属于前八周的行（即不包括当前日历周）。

为此，我们将派生一些中间列：

- departure_week：确定日历周——此日期位于一年中的第几周（1-52）
- departure_year_week_as_integer：创建一个整数，即年份加上日历周（例如，“201501”是2015年的第一周）
- latest_calendar_week：找到数据集中最近的一周
最后，得到关注的列：

- within_last_8_weeks：将每个日期与latest_calendar_week进行比较，以确定它是否属于前八周（返回true或false）
我们还将派生一个可以在图表中用于美观显示年份和日历周的标签列：departure_week_label。

有更简单的方法来计算直接的“属于过去八周内”，但本指南旨在提供尽可能多的示例（并展示如何使用Contour以符合明确要求）。

## 派生相对日期

从具有日期列的数据集开始。这里我们在原始数据集中使用名为departure_date_time的列。您可以根据数据集适当更改列名。

您可能希望筛选到几个月的范围以加快加载速度。然后，点击Table以打开表格视图。在表格编辑视图中，点击Expression以派生每个新列。

或者，您可以直接从路径添加表达式面板，而无需导航到表格视图。

### departure_week

将第一列命名为departure_week。

我们将使用week_of_year函数来确定departure_date_time列中每个日期的一年中的周数。对于第1-9周，我们将使用case语句在数字前面加上0进行格式化。最终列表达式应如下所示：

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
CASE week_of_year("departure_date_time")
WHEN 1 THEN '01' -- 如果是第一周，返回字符串 '01'
WHEN 2 THEN '02' -- 如果是第二周，返回字符串 '02'
WHEN 3 THEN '03' -- 如果是第三周，返回字符串 '03'
WHEN 4 THEN '04' -- 如果是第四周，返回字符串 '04'
WHEN 5 THEN '05' -- 如果是第五周，返回字符串 '05'
WHEN 6 THEN '06' -- 如果是第六周，返回字符串 '06'
WHEN 7 THEN '07' -- 如果是第七周，返回字符串 '07'
WHEN 8 THEN '08' -- 如果是第八周，返回字符串 '08'
WHEN 9 THEN '09' -- 如果是第九周，返回字符串 '09'
ELSE CAST (week_of_year("departure_date_time") AS STRING) -- 否则，将周数转换为字符串
END
```

你也可以通过使用左侧填充 (lpad) 函数来简化上述操作，而不是使用 case 语句：lpad(week_of_year("departure_date_time"), 2, '0')。这将为任何需要的值左侧添加一个零，以确保每个值总共有两位数字。

### departure_year_week_as_integer

在此列中，我们将年份与我们刚刚得出的departure_week列中的值连接在一起。

我们将使用年份函数从departure_date_time列中的每个日期提取年份。然后我们将departure_week列添加到结果中，使用 || 字符将它们连接在一起。最后，我们将结果值转换为整数。
最终列表达式应如下所示：

```
Copied!1
CAST (year("departure_date_time")||"departure_week" AS INTEGER)
```

```
Copied!1
2
3
4
5
-- 此代码用于将出发日期时间的年份与出发周进行字符串连接，并将结果转换为整数类型。
-- year("departure_date_time")：提取出发日期时间的年份。
-- "departure_week"：表示出发的周数。
-- ||：用于连接两个字符串。
-- CAST(... AS INTEGER)：将连接后的字符串结果转换为整数。
```

### latest_calendar_week

现在我们将在刚刚创建的列中找到最大值——最大值应该是数据中的最新周。（我们假设数据会定期更新，因此“数据中的最新周”大致等于当前周。）

语法是一个窗口函数。如果您有兴趣了解更多关于窗口函数的信息，可以阅读SQL 文档 ↗或查看窗口函数文档；否则，只需复制该函数：

```
Copied!1
max("departure_year_week_as_integer") OVER ()
```

```
Copied!1
2
-- 这个SQL函数计算列 "departure_year_week_as_integer" 的最大值。
-- OVER () 表示计算是在整个数据集的范围内进行，而不分组。
```

这将创建一个仅仅是范围最大值的列，因此每行都相同。

### within_last_8_weeks

要生成此列，我们将使用几个比较语句来检查日期是否落在数据最新一周之前的八周内。如果是，则该行的值使用 true。否则，使用 false。

```
Copied!1
2
3
4
5
6
7
8
CASE
    WHEN ("departure_year_week_as_integer" < "latest_calendar_week")
    AND ("departure_year_week_as_integer" > ("latest_calendar_week" - 9))
    -- 判断departure_year_week_as_integer是否在最新周数之前且在最近9周之内
    THEN TRUE
    ELSE FALSE
    -- 若不符合上述条件，则返回FALSE
END
```

### departure_week_label

此列仅将年份和日历周以字符串的形式呈现，以用于标记图表。我们将使用年份函数从每个日期中提取年份，然后添加“.CW”和日历周。

```
Copied!1
2
3
-- 使用 || 运算符进行字符串拼接
-- 从 departure_date_time 列提取年份，并与 '.CW' 和 calendar_week 列的值拼接成一个字符串
year("departure_date_time") || '.CW' || "calendar_week"
```

现在我们已经拥有所有派生列，点击表格以退出表格视图（或者如果您直接将表达式面板添加到路径中，请继续您的分析）。

## 在图表中使用相对日期

您可以使用筛选器以保留within_last_8_weeks等于true的行，然后使用筛选后的数据集创建图表。
在下图中，我们使用了departure_week_label来显示当前日期之前八周内每周的独特航班数量：

您可以将此图表添加到报告中，并定期查看以获取过去几个月的最新视图。
