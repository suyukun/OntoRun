来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-columns/

# 概念: 列

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概念: 列

要遵循本文档中的示例，请添加：from pyspark.sql import functions as F。

列由 PySpark 类管理：pyspark.sql.Column。每当您直接引用或从现有列派生表达式时，都会创建列实例。您可以通过以下任意方式引用列：

- F.col("column_name")
- F.column("column_name")
引用列不等同于执行选择，因为“选择”列是指子集化（和重新排序）您希望出现在结果数据集中的列。

## 目录

- 获取模式
- 选择：选择要保留的列
- 创建，更新
- 重命名，别名
- 删除：移除列
- 转换
- 当...否则
## 获取模式

### DataFrame.columns

返回所有列名作为一个 Python 列表。

```
Copied!1
2
columns = df.columns # ['age', 'name']
# 这行代码用于获取DataFrame对象df的所有列名。
```

## DataFrame.dtypes

返回所有列名及其数据类型作为元组列表

```
Copied!1
dtypes = df.dtypes # 获取数据框每列的数据类型，例如： [('age', 'int'), ('name', 'string')]
```

## 选择

### DataFrame.select(*cols)

返回一个新的DataFrame，其中包含源DataFrame的一部分列。

例如，我们有一个包含6个命名列的DataFrame：id，first_name，last_name，phone_number，address，is_active_member

| id | first_name | last_name | phone_number | zip_code | is_active_member |
| --- | --- | --- | --- | --- | --- |
| 1 | John | Doe | (123) 456-7890 | 10014 | true |
| 2 | Jane | Eyre | (213) 555-1234 | 90007 | true |
| ... | ... | ... | ... | ... | ... |

您可能希望将DataFrame变换为仅包含您关心的命名列（可用的一部分）。假设您只想要一个仅包含单列phone_number的表：

```
Copied!1
df = df.select("phone_number")  # 选择数据框中的“phone_number”列
```

或者您可能只需要id、first_name和last_name（至少有3种不同的方法可以完成相同的任务）：

- 直接传入列名:Copied!1df = df.select("id", "first_name", "last_name")或传入列实例:Copied!1df = df.select(F.col("id"), F.col("first_name"), F.col("last_name"))
直接传入列名:

```
Copied!1
df = df.select("id", "first_name", "last_name")
```

或传入列实例:

```
Copied!1
df = df.select(F.col("id"), F.col("first_name"), F.col("last_name"))
```

- 传入列名数组:Copied!12select_columns = ["id", "first_name", "last_name"]
df = df.select(select_columns)
传入列名数组:

```
Copied!1
2
select_columns = ["id", "first_name", "last_name"]
df = df.select(select_columns)
```

- 传入“解包”的数组:Copied!123select_columns = ["id", "first_name", "last_name"]
df = df.select(*select_columns)
# 等同于: df = df.select("id", "first_name", "last_name")idfirst_namelast_name1JohnDoe2JaneEyre.........select_columns前的*解包了数组，使其在功能上与#1相同（见注释）。这使您可以执行以下操作：Copied!123select_columns = ["id", "first_name", "last_name"]
return df.select(*select_columns, "phone_number")
# 等同于: df = df.select("id", "first_name", "last_name", "phone_number")idfirst_namelast_namephone_number1JohnDoe(123) 456-78902JaneEyre(213) 555-1234............
传入“解包”的数组:

```
Copied!1
2
3
select_columns = ["id", "first_name", "last_name"]
df = df.select(*select_columns)
# 等同于: df = df.select("id", "first_name", "last_name")
```

| id | first_name | last_name |
| --- | --- | --- |
| 1 | John | Doe |
| 2 | Jane | Eyre |
| ... | ... | ... |

select_columns前的*解包了数组，使其在功能上与#1相同（见注释）。这使您可以执行以下操作：

```
Copied!1
2
3
select_columns = ["id", "first_name", "last_name"]
return df.select(*select_columns, "phone_number")
# 等同于: df = df.select("id", "first_name", "last_name", "phone_number")
```

| id | first_name | last_name | phone_number |
| --- | --- | --- | --- |
| 1 | John | Doe | (123) 456-7890 |
| 2 | Jane | Eyre | (213) 555-1234 |
| ... | ... | ... | ... |

请记住，您的输出数据集将仅包含您选择的列，并且按照选择的顺序排列，而不是保留原始列的顺序。名称是唯一且区分大小写的，并且必须已经存在于您选择的数据集中的列。

该规则的一个例外是，您可以派生一个新列并立即以它进行选择。您需要为新派生的列提供一个alias或名称：

```
Copied!1
2
3
4
derived_column = F.concat_ws(":", F.col("string1"), F.col("string2"))
# 使用concat_ws函数将"string1"和"string2"两列的值用":"连接起来，并生成一个新的列derived_column
return df.select("string3", derived_column.alias("derived"))
# 从数据框中选择"string3"列和新的derived_column列，并将derived_column重命名为"derived"
```

| string3 | derived |
| --- | --- |
| 第三 | first |
| 三 | one |

## 创建，更新

### DataFrame.withColumn(name, column)

```
Copied!1
2
3
new_df = old_df.withColumn("column_name", derived_column)
# 使用withColumn方法在old_df数据框中添加或替换名为"column_name"的新列
# derived_column是计算得到的新列的值
```

- new_df: 结果数据框，包含old_df中的所有列，但添加了new_column_name。
- old_df: 我们想要应用新列的数据框
- column_name: 您要创建（如果在old_df中不存在）或更新（如果在old_df中已存在）的列的名称。
- derived_column: 导出列的表达式，应用于column_name（或您为列指定的任何名称）下的每一行。
给定一个现有的DataFrame，您可以使用withColumn方法创建新列或更新现有列的新值或修改值。这对于以下目标特别有用：

- 基于现有值导出新值Copied!1df = df.withColumn("times_two", F.col("number") * 2) # times_two = number * 2Copied!1df = df.withColumn("concat", F.concat(F.col("string1"), F.col("string2")))
基于现有值导出新值

```
Copied!1
df = df.withColumn("times_two", F.col("number") * 2) # times_two = number * 2
```

```
Copied!1
df = df.withColumn("concat", F.concat(F.col("string1"), F.col("string2")))
```

- 将值从一种类型转换为另一种类型Copied!12# 将`start_timestamp`转换为DateType并将新值存储在`start_date`中
df = df.withColumn("start_date", F.col("start_timestamp").cast("date"))
将值从一种类型转换为另一种类型

```
Copied!1
2
# 将`start_timestamp`转换为DateType并将新值存储在`start_date`中
df = df.withColumn("start_date", F.col("start_timestamp").cast("date"))
```

- 更新列Copied!12# 使用其全小写版本更新列`string`
df = df.withColumn("string", F.lower(F.col("string")))
更新列

```
Copied!1
2
# 使用其全小写版本更新列`string`
df = df.withColumn("string", F.lower(F.col("string")))
```

## 重命名, 别名

### DataFrame.withColumnRenamed(name, rename)

使用.withColumnRenamed()重命名列：

```
Copied!1
df = df.withColumnRenamed("old_name", "new_name")  # 将DataFrame中列名"old_name"重命名为"new_name"
```

查看重命名列任务的另一种方式，可以让您深入了解PySpark如何优化变换语句，是：

```
Copied!1
2
df = df.withColumn("new_name", F.col("old_name")).drop("old_name")
# 将DataFrame中的“old_name”列重命名为“new_name”列，并删除原来的“old_name”列
```

但是在某些情况下，您可以在不使用withColumn的情况下派生一个新列，并且仍然需要为其命名。这时，alias（或其方法别名，name）就派上用场了。以下是一些用法示例：

```
Copied!1
2
3
4
df = df.select(derived_column.alias("new_name"))  # 使用别名来重命名列为"new_name"
df = df.select(derived_column.name("new_name"))  # 等同于.alias("new_name")
df = df.groupBy("group") \  # 按"group"列进行分组
	.agg(F.sum("number").alias("sum_of_numbers"), F.count("*").alias("count"))  # 聚合操作：计算"number"列的总和并计数
```

我们还可以同时重命名多个列：

```
Copied!1
2
3
4
5
6
7
renames = {
    "column": "column_renamed",  # 将"column"列重命名为"column_renamed"
    "data": "data_renamed",      # 将"data"列重命名为"data_renamed"
}

for colname, rename in renames.items():
    df = df.withColumnRenamed(colname, rename)  # 遍历字典，将DataFrame中的列名进行重命名
```

## 删除

### DataFrame.drop(*cols)

返回一个新的DataFrame，其列为原始DataFrame的子集，并删除指定的列。（如果模式不包含给定的列名，则此操作失败。）

有两种删除列的方法：直接方式和间接方式。间接方式是使用select，选择您想保留的列的子集。直接方式是使用drop，提供您想丢弃的列的子集。两者的使用语法相似，只是这里的顺序无关紧要。以下是几个示例：

| id | first_name | last_name | phone_number | zip_code | is_active_member |
| --- | --- | --- | --- | --- | --- |
| 1 | John | Doe | (123) 456-7890 | 10014 | true |
| 2 | Jane | Eyre | (213) 555-1234 | 90007 | true |
| ... | ... | ... | ... | ... | ... |

假设您只想删除一列，phone_number：

```
Copied!1
df = df.drop("phone_number")  # 删除名为 "phone_number" 的列
```

或者您可能想要删除id、first_name和last_name（至少有三种不同的方法可以完成相同的任务）：

- 直接传入列名：Copied!1df = df.drop("id", "first_name", "last_name")或者Copied!1df = df.drop(F.col("id"), F.col("first_name"), F.col("last_name"))
直接传入列名：

```
Copied!1
df = df.drop("id", "first_name", "last_name")
```

或者

```
Copied!1
df = df.drop(F.col("id"), F.col("first_name"), F.col("last_name"))
```

- 传入一个数组：Copied!12drop_columns = ["id", "first_name", "last_name"]
df = df.drop(drop_columns)
传入一个数组：

```
Copied!1
2
drop_columns = ["id", "first_name", "last_name"]
df = df.drop(drop_columns)
```

- 传入一个“解包”的数组：Copied!123drop_columns = ["id", "first_name", "last_name"]
df = df.drop(*drop_columns)
# 同上: df = df.drop("id", "first_name", "last_name")phone_numberzip_codeis_active_member(123) 456-789010014true(213) 555-123490007true.........drop_columns前的*解包数组，使其在功能上表现得与#1相同（见注释）。这使您可以执行以下操作：Copied!123drop_columns = ["id", "first_name", "last_name"]
df = df.drop(*drop_columns, "phone_number")
# 同上: df = df.drop("id", "first_name", "last_name", "phone_number")zip_codeis_active_member10014true90007true......
传入一个“解包”的数组：

```
Copied!1
2
3
drop_columns = ["id", "first_name", "last_name"]
df = df.drop(*drop_columns)
# 同上: df = df.drop("id", "first_name", "last_name")
```

| phone_number | zip_code | is_active_member |
| --- | --- | --- |
| (123) 456-7890 | 10014 | true |
| (213) 555-1234 | 90007 | true |
| ... | ... | ... |

drop_columns前的*解包数组，使其在功能上表现得与#1相同（见注释）。这使您可以执行以下操作：

```
Copied!1
2
3
drop_columns = ["id", "first_name", "last_name"]
df = df.drop(*drop_columns, "phone_number")
# 同上: df = df.drop("id", "first_name", "last_name", "phone_number")
```

| zip_code | is_active_member |
| --- | --- |
| 10014 | true |
| 90007 | true |
| ... | ... |

## 转换

### Column.cast(type)

以下是所有存在的数据类型：NullType、StringType、BinaryType、BooleanType、DateType、TimestampType、DecimalType、DoubleType、FloatType、ByteType、IntegerType、LongType、ShortType、ArrayType、MapType、StructType、StructField

通常，您可以使用列上的cast方法将大多数数据类型从一种转换为另一种：

```
Copied!1
2
3
4
from pyspark.sql.types import StringType
df.select(df.age.cast(StringType()).alias("age"))
# 假设 df.age 是 IntegerType 类型
# 将 df.age 列从整型转换为字符串类型，并重命名为 "age"
```

或

```
Copied!1
2
3
df.select(df.age.cast("string").alias("age"))
# 将 age 列的数据类型转换为字符串类型，并将其别名为 "age"
# 效果上与使用 StringType() 相同
```

| 年龄 |
| --- |
| "2" |
| "5" |

强制转换本质上是创建一个新的派生列，您可以直接在其上执行select、withColumn、筛选等操作。"向下转换" 和 "向上转换" 的概念也适用于PySpark，因此您可能会失去以前数据类型中存储的更细粒度的信息，或获得垃圾信息。

## 当...否则

F.when(condition, value).otherwise(value2)

参数：

- condition- 布尔列表达式
- value- 字面值或列表达式
评估为与value或value2参数相同的列表达式。如果未调用Column.otherwise()，则为不匹配的条件返回None(null) 的列表达式。

when、otherwise操作符提供了类似于if-else语句的功能，用于计算新的列值。基本用法是：

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
# CASE WHEN (age >= 21) THEN true ELSE false END
# 如果年龄大于或等于21，则返回True；否则返回False
at_least_21 = F.when(F.col("age") >= 21, True).otherwise(False)

# CASE WHEN (last_name != "") THEN last_name ELSE null
# 如果last_name不为空，则返回last_name；否则返回None（空值）
last_name = F.when(F.col("last_name") != "", F.col("last_name")).otherwise(None)

# 选择列并为其设置别名
df = df.select(at_least_21.alias("at_least_21"), last_name.alias("last_name"))
```

您可以根据需要多次链接when语句：

```
Copied!1
2
3
4
5
# 根据年龄对数据进行分类：
# 如果年龄大于等于 35，则分为 "A" 类；
# 如果年龄大于等于 21 且小于 35，则分为 "B" 类；
# 否则分为 "C" 类。
switch = F.when(F.col("age") >= 35, "A").when(F.col("age") >= 21, "B").otherwise("C")
```

这些评估可以指派到列中，或用于筛选：

```
Copied!1
2
df = df.withColumn("switch", switch) # 在数据框中添加一个名为 "switch" 的列，值为 A、B 或 C
df = df.where(~F.isnull(last_name)) # 过滤掉 last_name 为 null 的行（空字符串已被视为 null 值）
```
