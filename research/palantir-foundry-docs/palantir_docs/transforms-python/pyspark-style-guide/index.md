来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-style-guide/

# 风格指南

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 风格指南

PySpark是一种包装语言，允许您与Apache Spark后端接口以快速处理数据。Spark可以在分布式服务器网络上操作非常大的数据集，正确使用时可以提供重大的性能和可靠性优势。即使对于经验丰富的Python开发人员来说，由于PySpark语法借用了Spark的JVM传统，因此实现了一些可能不熟悉的代码模式，它也带来了挑战。

这份关于PySpark代码风格的观点指南展示了常见情况和相关最佳实践，这些实践基于我们在PySpark代码库中遇到的最频繁的主题。

为了强制执行一致的代码风格，每个主要代码库都应该启用Pylint ↗，并使用相同的配置。我们提供了一些PySpark特定的检查器 ↗，您可以将它们额外包含到您的Pylint中，以匹配本文档中列出的规则。有关启用风格检查的详细信息，请参见启用风格检查的文档，其中包括我们为Python代码库提供的内置Pylint插件。

除了PySpark的特殊性之外，干净代码的一般实践在PySpark代码库中也很重要 - Google的PyGuide ↗是一个很好的起点。

## 除了解决歧义外，优先使用隐式列选择而不是直接访问

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
# 不推荐的写法
df = df.select(F.lower(df1.colA), F.upper(df2.colB))

# 推荐的写法
df = df.select(F.lower(F.col("colA")), F.upper(F.col("colB")))

# 评论：
# 上面的代码示例展示了如何在使用 PySpark 时选择列并转换其大小写。
# 不推荐的写法直接在 DataFrame 对象上调用列，可能会导致意外的结果，尤其是在多个 DataFrame 操作时。
# 推荐的写法使用 F.col 函数来明确指定列名，确保代码的可读性和可维护性。
```

首选的选项可能看起来更复杂、冗长且污染——这确实是正确的；事实上，最好完全避免使用F.col()。但在某些情况下，使用它或替代的显式选择是不可避免的。然而，有一个非常好的理由偏爱第二个例子而不是第一个。

如第一个案例中那样使用显式列时，数据框名称和模式都明确绑定到数据框变量。这意味着如果df1被删除或重命名，引用df1.colA将会出错。

相比之下，F.col("colA")将始终引用操作的数据框中名为“colA”的列，在这种情况下，该数据框名为df。它根本不需要跟踪其他数据框的状态，因此代码变得更加局部化，不易出现“远距离神秘交互”，这些通常难以调试。

避免第一个案例的其他好理由：

- 如果数据框变量名称较长，涉及它的表达式很快会变得难以管理；
- 如果列名包含空格或其他不支持的字符，需通过括号操作符访问，那么df1["colA"]与F.col(“colA”)一样难以编写；
- 将像F.col("prod_status") == 'Delivered'这样的抽象表达式指派给变量，可以在多个数据框中重复使用，而df.prod_status == 'Delivered'始终绑定到df
幸运的是，通常不需要用F.col()来构建复杂的表达式。唯一的例外是F.lower，F.upper，...和这些 ↗。

### 注意事项

在某些情况下，可以访问多个数据框中的列，并且名称可能会重叠。一个常见的例子是在匹配表达式中，如df.join(df2, on=(df.key == df2.key), how='left')。在这种情况下，直接通过数据框引用列是可以的。您也可以使用数据框别名来消除合并中的歧义（请参阅本指南中的合并部分了解更多信息）。

## 避免迭代列，建议使用列表推导

一般来说，在Spark中for循环效率较低。从高层次上看，这是因为Spark是延迟计算的，只会一次处理一个for循环。如果循环的所有部分可以同时处理，这可能会导致运行时间变慢，还可能导致Driver内存不足错误（OOMs）。要将数据集中所有列从大写重命名为小写，建议使用列表推导（如第二个例子标记为# good）而不是下面的第一个例子（标记为# bad）：

```
Copied!1
2
3
4
# 糟糕的代码示例：在循环中对数据框进行不必要的复制操作
for colm in df.columns:
    # 每次循环都重新复制整个数据框，效率低下
    df = df.withColumnRenamed(colm, colm.lower())
```

```
Copied!1
2
3
4
5
6
# good
df = df.select(
    *[F.col(colm).alias(colm.lower()) for colm in df.columns]
)
# 通过将列名转换为小写形式，选择DataFrame中的所有列。
# 使用select方法和列别名(alias)实现。
```

使用# good示例中的列表推导将避免上述讨论的性能缓慢和查询计划问题，同时仍能获得相同的期望结果。

## 重构复杂逻辑操作

逻辑操作通常位于.filter()或F.when()内，需要保持可读性。我们应用与链接函数相同的规则，将逻辑表达式保持在同一个代码块中，最多3 个表达式。如果它们变得更长，这通常是代码可以简化或提取的信号。将复杂的逻辑操作提取到变量或函数中，使代码更易读和理解，从而减少错误。

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
# bad
# 这是一个复杂的条件语句，用于判断产品状态。
# 使用 F.when 来创建条件表达式：
# 如果产品状态为 'Delivered' 或者 满足以下条件：
# 1. 实际交付日期与当前日期的差值小于0，并且
# 2. 当前注册信息匹配正则表达式 '.+'，或者
# 3. 实际交付日期与当前日期的差值小于0，并且（原始运营商或当前运营商）匹配正则表达式 '.+'
# 则返回 'In Service'
F.when( (df.prod_status == 'Delivered') | (((F.datediff(df.deliveryDate_actual, df.current_date) < 0) &
((df.currentRegistration.rlike('.+')) | ((F.datediff(df.deliveryDate_actual, df.current_date) < 0) &
(df.originalOperator.rlike('.+') | df.currentOperator.rlike('.+')))))), 'In Service')
```

我们可以通过不同方式简化上述代码。首先，让我们专注于将逻辑步骤分组到一些命名变量中。Pyspark要求表达式用括号括起来。这与用于分组逻辑运算的实际括号混合在一起时，会影响可读性。例如，上述代码中有一个冗余的(F.datediff(df.deliveryDate_actual, df.current_date) < 0)，原作者没有注意到，因为很难发现。

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
# 定义变量 has_operator，判断 originalOperator 和 currentOperator 是否匹配正则表达式 '.+'，即是否存在操作员
has_operator = (df.originalOperator.rlike('.+') | df.currentOperator.rlike('.+'))

# 定义变量 delivery_date_passed，判断实际交付日期是否在当前日期之前
delivery_date_passed = (F.datediff(df.deliveryDate_actual, df.current_date) < 0)

# 定义变量 has_registration，判断 currentRegistration 是否匹配正则表达式 '.+'，即是否存在注册信息
has_registration = (df.currentRegistration.rlike('.+'))

# 定义变量 is_delivered，判断产品状态是否为 'Delivered'
is_delivered = (df.prod_status == 'Delivered')

# 使用 F.when 函数生成新的列，根据条件判断产品是否 "In Service"
F.when(is_delivered | (delivery_date_passed & (has_registration | has_operator)), 'In Service')
```

以上示例更易于阅读，并且去掉了冗余表达。我们还可以通过减少操作次数进一步改进它。

```
Copied!1
2
3
4
5
6
7
8
# 好
has_operator = (df.originalOperator.rlike('.+') | df.currentOperator.rlike('.+'))  # 检查是否有运营商
delivery_date_passed = (F.datediff(df.deliveryDate_actual, df.current_date) < 0)  # 检查交付日期是否已过
has_registration = (df.currentRegistration.rlike('.+'))  # 检查是否有注册信息
is_delivered = (df.prod_status == 'Delivered')  # 检查产品是否已交付
is_active = (has_registration | has_operator)  # 检查是否活跃

F.when(is_delivered | (delivery_date_passed & is_active), 'In Service')  # 判断是否在服务中
```

注意，F.when表达式现在简洁且易读，期望的行为对于审阅此代码的任何人都是清晰的。读者只有在怀疑那里有出错时才需要查看单个表达式。 如果您的代码中有单元测试，并希望将其抽象为函数，这也使每个逻辑块易于测试。

最终示例中仍然存在一些代码重复：我们将如何去除这些重复留作读者的练习。

## 使用select语句指定模式契约

在 PySpark 变换的开始或返回之前进行 select 被认为是一种良好实践。此select语句规定了与读者和代码之间的契约，即输入和输出的预期 dataframe 模式。

任何 select 都应被视为一种清理操作，为变换的下一步准备 dataframe。

始终旨在保持 select 语句尽可能简单。由于常见的 SQL 惯用语，每个选定列允许使用最多一个来自spark.sql.function的函数，加上一个非必填.alias()以赋予其有意义的名称。请记住，这应当谨慎使用，如果在同一个 select 中有超过三个这样的使用，请重构为一个单独的函数，如clean_<dataframe name>()来封装操作。

绝不要允许在 select 中使用涉及多个 dataframe 的表达式或条件操作如.when()。

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
# bad
# 代码选择了飞机相关的字段，并对某些字段进行了别名和数据类型转换
aircraft = aircraft.select(
    'aircraft_id',  # 飞机ID
    'aircraft_msn',  # 飞机序列号
    F.col('aircraft_registration').alias('registration'),  # 飞机注册号，并重命名为registration
    'aircraft_type',  # 飞机类型
    F.avg('staleness').alias('avg_staleness'),  # 计算staleness的平均值，并重命名为avg_staleness
    F.col('number_of_economy_seats').cast('long'),  # 将经济舱座位数量转换为long类型
    F.avg('flight_hours').alias('avg_flight_hours'),  # 计算飞行小时数的平均值，并重命名为avg_flight_hours
    'operator_code',  # 运营商代码
    F.col('number_of_business_seats').cast('long'),  # 将商务舱座位数量转换为long类型
)
```

将相同类型的操作聚集在一起。所有单独的列应列在前面，而对spark.sql.function中函数的调用应分行列出。

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
# 优秀
aircraft = aircraft.select(
    'aircraft_id', 'aircraft_msn', 'aircraft_type', 'operator_code',
    F.col('aircraft_registration').alias('registration'),  # 将 aircraft_registration 列重命名为 registration
    F.col('number_of_economy_seats').cast('long'),  # 将 number_of_economy_seats 列转换为 long 类型
    F.col('number_of_business_seats').cast('long'),  # 将 number_of_business_seats 列转换为 long 类型
    F.avg('staleness').alias('avg_staleness'),  # 计算 staleness 列的平均值，并重命名为 avg_staleness
    F.avg('flight_hours').alias('avg_flight_hours'),  # 计算 flight_hours 列的平均值，并重命名为 avg_flight_hours
)
```

select()语句本质上重新定义了数据框的架构，因此它自然支持包括或排除列，无论是旧的还是新的，以及重新定义已存在的列。通过在单个语句中集中所有这些操作，更容易识别最终的架构，从而使代码更具可读性。它还使代码略微简洁。

使用别名代替调用withColumnRenamed()：

```
Copied!1
2
3
4
5
6
# 不推荐的写法
df.select('key', 'comments').withColumnRenamed('comments', 'num_comments')

# 推荐的写法
# 使用F.col()和alias()来重命名列，这种方式更为简洁和清晰
df.select('key', F.col('comments').alias('num_comments'))
```

不要使用withColumn()重新定义类型，而是在select中转换类型：

```
Copied!1
2
3
4
5
6
7
# 不推荐的做法
# 这里先选择了'comments'列，然后再对'comments'列进行类型转换
df.select('comments').withColumn('comments', F.col('comments').cast('double'))

# 推荐的做法
# 直接在select中对'comments'列进行类型转换，代码更简洁
df.select(F.col('comments').cast('double'))
```

但保持简单：

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
# bad 不推荐的写法
df.select(
    ((F.coalesce(F.unix_timestamp('closed_at'), F.unix_timestamp())  # 使用coalesce处理空值，获取关闭时间的时间戳
    - F.unix_timestamp('created_at')) / 86400).alias('days_open')  # 计算时间差并转换为天数，给结果起别名'days_open'
)

# good 推荐的写法
df.withColumn(
    'days_open',  # 新增列名'days_open'
    (F.coalesce(F.unix_timestamp('closed_at'), F.unix_timestamp()) - F.unix_timestamp('created_at')) / 86400
    # 使用withColumn方法直接在DataFrame中添加新列，逻辑与上面相同
)
```

避免在select语句中包含未使用的列，而是选择一组明确的列——这比使用.drop()是更优的选择，因为它保证了模式变更不会导致意外的列膨胀你的数据框。话虽如此，在所有情况下并不固有地不鼓励删除列；例如，在合并之后通常是合适的，因为合并通常会引入冗余列。

最后，建议使用.withColumn()来添加新列，而不是通过select语句来添加。

## 空列

如果需要添加一个空列以满足模式，请始终使用F.lit(None)来填充该列。切勿使用空字符串或其他字符串来表示空值（例如NA）。

除了在语义上是正确的之外，这样做的一个实际原因是保留使用像isNull这样的工具的能力，而不必验证空字符串、null 和'NA'等。

```
Copied!1
2
3
4
5
6
7
8
# 不推荐的写法
df = df.withColumn('foo', F.lit(''))

# 不推荐的写法
df = df.withColumn('foo', F.lit('NA'))

# 推荐的写法 - 注意需要进行类型转换，因为`None`是无类型的。根据预期的使用选择合适的类型。
df = df.withColumn('foo', F.lit(None).cast('string'))
```

## 使用注释

虽然注释可以为代码提供有用的见解，但重构代码以提高其可读性通常更有价值。代码本身应该是可读的。如果您使用注释逐步解释逻辑，您应该重构它。

```
Copied!1
2
3
4
5
6
7
# bad

# 将时间戳列转换为时间戳类型
cols = ["start_date", "delivery_date"]
for c in cols:
    # 将UNIX时间戳（以毫秒为单位）转换为TimestampType
    df = df.withColumn(c, F.from_unixtime(df[c] / 1000).cast(TimestampType()))
```

在上面的示例中，我们可以看到这些列正在被转换为时间戳。该注释并没有增加太多价值。此外，如果冗长的注释仅提供代码中已经存在的信息，可能仍然无济于事。例如：

```
Copied!1
2
3
4
5
6
# 改进后的代码

# 遍历每个列，去除1000因为是毫秒，并转换为时间戳类型
cols = ["start_date", "delivery_date"]
for c in cols:
    df = df.withColumn(c, F.from_unixtime(df[c] / 1000).cast(TimestampType()))
```

在这段代码中，我们遍历了名为cols的列表中的每个列名，将每个列的值从毫秒转换为标准的时间戳格式。from_unixtime函数用于将Unix时间戳（以秒为单位）转换为标准时间戳格式，而列中的时间戳值是以毫秒为单位的，所以需要除以1000进行转换，然后使用cast方法将其转换为TimestampType类型。
与其留下仅仅描述逻辑的注释，不如留下提供背景信息的注释，解释您在编写代码时做出决策的“原因”。这对于PySpark尤其重要，因为读者可以理解您的代码，但通常不了解输入到您的PySpark变换中的数据背景。小段逻辑可能需要花费数小时来深入研究数据以了解正确的行为，在这种情况下，解释理由的注释尤为重要。

```
Copied!1
2
3
4
5
6
7
# good

# 使用此数据集的消费者期望获得时间戳而不是日期，我们需要将时间调整为1000倍，
# 因为原始数据源以毫秒存储这些数据，即使文档说明它实际上是一个日期。
cols = ["start_date", "delivery_date"]
for c in cols:
    df = df.withColumn(c, F.from_unixtime(df[c] / 1000).cast(TimestampType()))
```

## UDFs（用户定义函数）

强烈建议在所有情况下避免使用UDFs，因为它们的性能远远低于原生PySpark。在大多数情况下，看似需要UDF的逻辑实际上可以重构为仅使用原生PySpark函数。

## Collect（及相关函数）

始终避免使用将数据收集到Spark驱动程序的函数，例如：

- DataFrame.collect()
- DataFrame.first()
- DataFrame.head(...)
- DataFrame.take(...)
- DataFrame.show(...)
使用这些函数会消除Spark这种分布式框架的优势，导致性能下降或内存不足错误。我们强烈建议使用以下功能代替这些函数：

- 在代码库中使用预览与调试功能来检查开发变换时变量（包括Spark DataFrames）的状态。
- 使用原生PySpark函数（如果可能）或UDFs（在逻辑无法用原生函数编码的少数情况下）处理DataFrames中的map/aggregate值。
## 合并

小心合并操作。如果执行左合并，而右侧有多个键匹配，该行将根据匹配次数被重复。这被称为“合并爆炸”，可能会显著膨胀数据集的大小。始终仔细检查假设，以确保您正在合并的键是唯一的，除非您预计会有倍增。

不良合并是许多问题的根源，并且可能难以调试。有些事情可以提供帮助，例如明确指定how，即使您使用的是默认值（inner）：

```
Copied!1
2
3
4
5
6
7
8
# 不推荐的写法
flights = flights.join(aircraft, 'aircraft_id')

# 也不推荐的写法
flights = flights.join(aircraft, 'aircraft_id', 'inner')

# 推荐的写法
flights = flights.join(aircraft, 'aircraft_id', how='inner')
```

解释：

- 第一种和第二种写法的参数传递不够明确，不利于代码的可读性。
- 第三种写法通过明确指定参数how='inner'提高了代码的可读性和可维护性。
还要避免使用right合并。如果您准备使用right合并，请切换数据框的顺序，并改用left合并。这更加直观，因为您正在进行操作的数据框是您合并时所围绕的中心。
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
# bad
flights = aircraft.join(flights, 'aircraft_id', how='right')
# 这是一个糟糕的做法，因为这里的join顺序可能导致不必要的数据丢失。
# 使用right join时，会保留右表（flights）中的所有记录，但可能丢弃左表（aircraft）中没有匹配的记录。

# good
flights = flights.join(aircraft, 'aircraft_id', how='left')
# 这是一个较好的做法，left join会保留左表（flights）中的所有记录，
# 即使在右表（aircraft）中没有匹配的记录，也不会丢失左表的数据。
```

合并数据帧时，避免使用在输出中重复列的表达式：

```
Copied!1
2
3
4
5
# 错误 - 列 aircraft_id 会在输出中重复
output = flights.join(aircraft, flights.aircraft_id == aircraft.aircraft_id, how='inner')

# 正确
output = flights.join(aircraft, 'aircraft_id', how='inner')
```

避免重命名所有列以避免冲突。您可以为整个数据框起一个别名，并使用该别名选择最终需要的列。

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
# bad
# 在这里，使用了循环对列名进行重命名，增加了代码的复杂性和可读性问题
columns = ["start_time", "end_time", "idle_time", "total_time"]
for col in columns:
    flights = flights.withColumnRenamed(col, 'flights_' + col)
    parking = parking.withColumnRenamed(col, 'parking_' + col)

flights = flights.join(parking, on="flight_code", how="left")

# 选择重命名后的列，代码冗长且不直观
flights = flights.select(
    F.col("flights_start_time").alias("flight_start_time"),
    F.col("flights_end_time").alias("flight_end_time"),
    F.col("parking_total_time").alias("client_parking_total_time")
)

# good
# 使用表别名（alias）提高了代码的可读性和简洁性
flights = flights.alias("flights")
parking = parking.alias("parking")

flights = flights.join(parking, on="flight_code", how="left")

# 使用表别名前缀来选择列，简洁明了
flights = flights.select(
    F.col("flights.start_time").alias("flight_start_time"),
    F.col("flights.end_time").alias("flight_end_time"),
    F.col("parking.total_time").alias("client_parking_total_time")
)
```

在这种情况下，请记住：

- 如果不需要重叠的列，最好在合并之前删除它们；
- 如果需要保留两者，最好在合并之前重命名其中一个；
- 在输出数据集之前，您应始终解决不明确的列，因为变换完成运行后，您将无法区分它们。
关于合并的最后一点，不要将.dropDuplicates()或.distinct()用作解决问题的权宜之计。如果观察到意外的重复行，几乎总有一个根本原因导致这些重复行出现。添加.dropDuplicates()只会掩盖这个问题，并增加运行时间的开销。

## 表达式的链式调用

链式调用表达式是一个有争议的话题，但我们确实建议对链式调用的使用进行一些限制。请参阅本节的结论，了解我们提出此建议背后的理由。

避免将表达式链式调用成具有不同类型的多行表达式。尤其是在它们具有不同的行为或上下文时。例如，将列的创建或合并与选择和筛选混合使用。

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
# 差的写法
df = (
    df
    .select("a", "b", "c", "key")
    .filter(df.a == "truthiness")
    .withColumn("boverc", df.b / df.c)
    .join(df2, "key", how="inner")
    .join(df3, "key", how="left")
    .drop('c')
)

# 较好的写法（分步处理）
# 第一步：选择并整理我们需要的数据
# 第二步：创建我们需要的列
# 第三步：与其他数据框进行连接

df = (
    df
    .select("a", "b", "c", "key")
    .filter(df.a == "truthiness")
)

df = df.withColumn("boverc", df.b / df.c)

df = (
    df
    .join(df2, "key", how="inner")
    .join(df3, "key", how="left")
    .drop('c')
)
```

在较好的写法中，将代码分成多个步骤，使代码更易于阅读和维护。每个步骤都有明确的目的：首先选择并过滤数据，然后添加新列，最后进行数据连接和删除不需要的列。
将每组表达式隔离到各自的逻辑代码块中可以提高可读性，并使查找相关逻辑变得更容易。

例如，下面代码的读者可能会跳到他们看到数据框被指派df = df...的位置。

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
# bad
df = (
    df
    .select('foo', 'bar', 'foobar', 'abc')
    .filter(df.abc == 123)  # 使用直接引用列的方式进行过滤
    .join(another_table, 'some_field')  # 直接连接另一张表，未指定连接方式，默认为内连接
)

# better
df = (
    df
    .select('foo', 'bar', 'foobar', 'abc')
    .filter(F.col('abc') == 123)  # 使用F.col()明确指定列名，代码更具可读性
)

df = df.join(another_table, 'some_field', how='inner')  # 明确指定连接方式为内连接
```

将表达式串联在一起是有正当理由的。这些通常代表原子逻辑步骤，是可以接受的。应用一个规则，规定在同一块中最多可以串联的表达式数量，以保持代码的可读性。我们建议链条不超过3-5个语句。

如果发现自己在构建更长的链条，或者由于变量的大小而遇到麻烦，考虑将逻辑提取到一个单独的函数中：

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
# bad
customers_with_shipping_address = (
    customers_with_shipping_address
    .select("a", "b", "c", "key")
    .filter(F.col("a") == "truthiness")
    .withColumn("boverc", F.col("b") / F.col("c"))
    .join(df2, "key", how="inner")
)

# also bad
customers_with_shipping_address = customers_with_shipping_address.select("a", "b", "c", "key")
customers_with_shipping_address = customers_with_shipping_address.filter(df.a == "truthiness")

customers_with_shipping_address = customers_with_shipping_address.withColumn("boverc", F.col("b") / F.col("c"))

customers_with_shipping_address = customers_with_shipping_address.join(df2, "key", how="inner")

# better
def join_customers_with_shipping_address(customers, df_to_join):
    # 函数用于将 customers 与另一个 DataFrame 进行连接

    customers = (
        customers
        .select("a", "b", "c", "key")  # 选择所需的列
        .filter(df.a == "truthiness")  # 过滤条件
    )

    customers = customers.withColumn("boverc", F.col("b") / F.col("c"))  # 添加新列 "boverc"
    customers = customers.join(df_to_join, "key", how="inner")  # 用 "key" 列进行内连接
    return customers  # 返回连接后的 DataFrame
```

添加了中文注释，说明了代码的每一步操作。
事实上，超过三个语句的链条是分解为独立、命名良好的函数的理想候选，因为它们已经是封装的、独立的逻辑块。

### 原因

对链式调用的这些限制有几个原因：

- 区分 PySpark 代码和 SQL 代码。链式调用违反了大多数（如果不是全部的话）其他 Python 风格。在 Python 中不进行链式调用，而是指派。
- 不鼓励创建大型单一代码块。这些通常更适合提取为一个命名函数。
- 这不需要是全有或全无的；最多三到五行的链式调用在实用性与可读性之间取得平衡。
- 如果你使用 IDE，这使得使用自动提取或进行代码移动更容易（例如，在 PyCharm 中使用 Ctrl/Cmd+Shift+Up）。
- 大型链条难以阅读和维护，特别是如果链条是嵌套的。
## 多行表达式

你可以链式表达的原因是因为 PySpark 是从 Spark 开发而来的，而 Spark 源自 JVM 语言。这意味着一些设计模式被传递过来，即链式调用。

然而，Python 不优雅地支持多行表达式，唯一的替代方案是提供显式的换行符，或者将表达式括在括号中。只有当链条发生在根节点时，才需要提供显式换行符。例如：

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
# 需要使用 `\` 进行换行
df = df.filter(F.col('event') == 'executing')\
       .filter(F.col('has_tests') == True)\
       .drop('has_tests')

# 因为链式调用不是在根节点进行，因此不需要使用 `\`
df = df.withColumn('safety', F.when(F.col('has_tests') == True, 'is safe')  # 如果 `has_tests` 列为真，则标记为 'is safe'
                              .when(F.col('has_executed') == True, 'no tests but runs')  # 如果 `has_executed` 列为真，则标记为 'no tests but runs'
                              .otherwise('not safe'))  # 否则标记为 'not safe'
```

因此，为保持一致性，将整个表达式括在一个括号块中，并避免使用\：

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
# bad
df = df.filter(F.col('event') == 'executing')\
    .filter(F.col('has_tests') == True)\
    .drop('has_tests')

# good
df = (
  df
  .filter(F.col('event') == 'executing')
  .filter(F.col('has_tests') == True)
  .drop('has_tests')
)
```

这段代码展示了两种格式化方式的对比。虽然两者在功能上是等价的，但“good”的格式更具可读性。通过使用小括号，可以使代码看起来更清晰，尤其是在链式调用的情况下。这种格式更容易维护和调试。

## 其他注意事项和建议

- 当心变得过于庞大的函数。一般来说，文件不应超过250行，函数不应超过70行。
- 尝试将代码保持在逻辑块中。例如，如果有多行代码引用相同的内容，请尝试将它们放在一起。将它们分开会使读者更难理解上下文。
- 测试您的代码。如果可以运行本地测试，请这样做，并确保您的新代码已被测试覆盖。如果无法运行本地测试，请在您的分支上搭建数据集，并手动验证数据是否符合预期。
- 避免将.otherwise(value)作为一般回退。如果您将键列表映射到值列表，并且出现许多未知键，使用otherwise会将所有这些键掩盖为一个值。
- 不要在存储库中保留已注释掉的代码。这适用于单行代码、函数、类或模块。依赖于git及其分支或查看历史记录的功能。
- 当遇到由集成多个不同来源表组成的大型单一变换时，将其拆分为自然的子步骤，并将逻辑提取到函数中。这便于更高层次的可读性，并允许代码在变换之间的重用性和一致性。
- 在命名函数或变量时，尽量做到明确和描述性。除了包装对象变换的顶层变换外，努力捕捉函数实际执行的操作，而不是仅通过函数内部使用的对象来命名。
- 在引入新的导入别名时要三思，除非有充分的理由。例如，如果一个导入的模块在不同文件中多次调用，并且该模块对几乎所有开发人员都是常见和熟悉的，这可能是合理的。一些已建立的别名是来自pySpark的types和functions，from pyspark.sql import types as T, functions as F。
- 避免在筛选条件、新列的值等中使用字面字符串或整数。相反，将它们提取到变量、常量、字典或类中，以捕捉其含义。这使代码更具可读性，并在整个存储库中强制保持一致性。