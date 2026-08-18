来源: https://palantir.com/docs/zh/foundry/transforms-python/data-expectations-reference/

# 参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 参考

以下是所有可用数据期望的分类列表。

## 运算符

```
Copied!1
2
3
4
5
6
7
from transforms import expectations as E

E.true()           # 总是通过
E.false()          # 总是失败
E.all(e1,e2,...)   # 当所有子期望都通过时通过
E.any(e1,e2,...)   # 当任意一个子期望通过时通过
E.negate(e1)       # 当子期望失败时通过
```

例子：

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
from transforms import expectations as E

# 定义一个期望集合，所有条件都需要满足
E.all(
    # 列 'a' 的值大于 0
    E.col('a').gt(0),
    # 列 'a' 的值小于 100
    E.col('a').lt(100),
    # 列 'b' 的值满足以下任意一个条件
    E.any(
        # 列 'b' 的值大于 100
        E.col('b').gt(100),
        # 列 'b' 的值小于 0
        E.col('b').lt(0)
    )
)
```

## 列期望

列期望以E.col('column_name')开始。

使用any操作符时，每行将单独检查是否满足任何列期望。
例如，要验证列c1的值应大于 10 或小于 0：

```
Copied!1
2
3
4
5
6
7
from transforms import expectations as E

# 检查列 "c1" 中的任意值是否小于0或大于10
E.any(
    E.col("c1").lt(0),  # 检查是否有值小于0
    E.col("c1").gt(10)  # 检查是否有值大于10
)
```

### 大于或小于

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
from transforms import expectations as E

# 检查列 'c' 中的值是否大于指定的数字或字符串
E.col('c').gt(number|string)

# 检查列 'c' 中的值是否大于或等于指定的数字或字符串
E.col('c').gte(number|string)

# 检查列 'c' 中的值是否小于指定的数字或字符串
E.col('c').lt(number|string)

# 检查列 'c' 中的值是否小于或等于指定的数字或字符串
E.col('c').lte(number|string)
```

```
Copied!1
2
3
4
from transforms import expectations as E

# 检查 'age' 列中的值是否都小于 120
E.col('age').lt(120)
```

该期望会忽略空值（意味着空值会自动通过）。要检查空值，请使用E.col('col').non_null()。

### 列比较

```
Copied!1
2
3
4
5
6
7
8
from transforms import expectations as E

E.col('c1').equals_col('c2')  # 列c1的值等于列c2的值
E.col('c1').not_equals_col('c2')  # 列c1的值不等于列c2的值
E.col('c1').gt_col('c2')  # 列c1的值大于列c2的值
E.col('c1').gte_col('c2') # 列c1的值大于或等于列c2的值
E.col('c1').lt_col('c2')  # 列c1的值小于列c2的值
E.col('c1').lte_col('c2') # 列c1的值小于或等于列c2的值
```

### 属性比较

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
from transforms import expectations as E

E.col('c').null_percentage().lt(value) # 检查列 'c' 中的空值百分比是否小于指定的值
E.col('c').null_count().gt(value) # 检查列 'c' 中的空值数量是否大于指定的值
E.col('c').distinct_count().equals(value) # 检查列 'c' 中的唯一值数量是否等于指定的值
E.col('c').approx_distinct_count().equals(value) # 检查列 'c' 中的近似唯一值数量是否等于指定的值，保证误差的相对标准偏差最大为 5%，是 distinct_count 的更快版本
E.col('c').sum().gt(value) # 检查列 'c' 的总和是否大于指定的值，仅适用于数值列
E.col('c').standard_deviation_sample().gt(value) # 检查列 'c' 的样本标准差是否大于指定的值，仅适用于数值列
E.col('c').standard_deviation_population().gt(value) # 检查列 'c' 的总体标准差是否大于指定的值，仅适用于数值列
```

例如：

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
from transforms import expectations as E

E.col("myCol").null_percentage().lt(0.1)    # myCol 的空值比例小于 10%
E.col("myCol").null_count().gt(100)         # myCol 的空值数量大于 100
E.col("myCol").distinct_count().equals(5)   # myCol 有 5 个不同的值（自版本 0.11.0 起）
E.col('myCol').approx_distinct_count().equals(5)   # myCol 近似有 5 个不同的值
E.col('myCol').sum().equals(5)              # myCol 的值之和等于 5
E.col('myCol').standard_deviation_sample().gt(5) # myCol 的样本标准差大于 5
E.col('myCol').standard_deviation_population().gt(5) # myCol 的总体标准差大于 5
```

### 等于

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').equals(value)    # 判断列 'c' 的值是否等于输入的值
```

例如：

```
Copied!1
2
3
4
from transforms import expectations as E

# 检查'test_column'列的值是否等于"success"
E.col('test_column').equals("success")
```

此预期会忽略空值（意味着空值将自动通过）。要检查空值，请使用E.col('col').non_null()。

### 不等于

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').not_equals(value)    # 列 'c' 的值不等于指定的输入值
```

```
Copied!1
2
3
4
from transforms import expectations as E

# 检查'test_column'列中的值不等于"failure"
E.col('test_column').not_equals("failure")
```

此预期会忽略空值（意味着空值会自动通过）。要检查空值，请使用E.col('col').non_null()。

### 空值

```
Copied!1
2
3
4
from transforms import expectations as E

E.col('c').non_null()    # 列值不为空
E.col('c').is_null()     # 列值为空
```

### 属于

此期望验证列值是否在批准值列表中。对于数组列，请参阅属于（数组）。

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').is_in(a, b, ...)    # 检查列 'c' 的值是否在给定的列表中
```

该期望对空值出错，除非您将None添加到允许的值中。

### rlike (正则表达式)

正则表达式部分匹配，类似于pyspark.sql.functions.rlike

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').rlike(regex expression)    # 列值是否与正则表达式匹配（部分匹配）
```

```
Copied!1
2
3
4
5
from transforms import expectations as E

# 使用正则表达式检查 'flight_number' 列中的值是否匹配指定的模式
# 模式: 以两个非数字字符开头，接着是2到4个数字字符
E.col('flight_number').rlike(r"^\D{2}\d{2,4}$")
```

此期望忽略空值（意味着空值将自动通过）。要检查空值，请使用E.col('col').non_null()。

### 拥有类型

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').has_type(Type)   # 列 'c' 应该是 Type 类型
```

这个数据期望需要从pyspark.sql导入types（在示例中：as T）

例如：

```
Copied!1
2
3
4
from transforms import expectations as E

# 检查列 'age' 的数据类型是否为长整型
E.col('age').has_type(T.LongType())
```

### 存在

```
Copied!1
2
3
from transforms import expectations as E

E.col('c').exists()  # 检查输出数据框中是否存在列 'c'
```

此预期检查输出数据框中是否存在具有提供名称的列。该列可以是任何类型。

## 时间戳预期

时间戳预期仅适用于类型为Timestamp的列。目前，不支持Date列。

### 静态时间戳比较

将时间戳列中的值与静态时间戳进行比较。静态时间戳可以作为ISO8601格式的字符串提供，也可以作为Python日期时间对象提供。所有时间戳都必须具备时区意识以避免歧义。

切勿将静态时间戳预期与从`datetime.now()`派生的时间戳一起使用。虽然这最初可能看起来会产生正确的结果，但这种行为不被支持，可能会导致结果不正确而不会发出警告。此外，如果您使用从datetime.now()派生的时间戳进行静态时间戳预期，Foundry中的数据健康和消息将不会引用正确的时间戳。相反，请使用相对时间戳比较预期。

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
from transforms import expectations as E

# 检查 "timestamp" 列中的日期是否在 "2020-12-14T11:32:23+0000" 之后
E.col("timestamp").is_after("2020-12-14T11:32:23+0000")

# 检查 "timestamp" 列中的日期是否在 datetime(2017, 11, 28, 23, 55, 59, 342380) 之前
E.col("timestamp").is_before(datetime(2017, 11, 28, 23, 55, 59, 342380))

# 检查 "timestamp" 列中的日期是否在 "2020-12-14T11:32:23+0000" 或之后
E.col("timestamp").is_on_or_after("2020-12-14T11:32:23+0000")

# 检查 "timestamp" 列中的日期是否在 "2020-12-14T11:32:23+0000" 或之前
E.col("timestamp").is_on_or_before("2020-12-14T11:32:23+0000")
```

### 列时间戳比较

比较一个时间戳列中的值与另一个时间戳列中的值。可以提供一个非必填的偏移量（整数秒数），并将其添加到另一列的值中。

比较将是：

```
first_column ($OPERATOR) second_column + offset_in_seconds
```

```
Copied!1
2
# 该代码段表示在两个列（first_column 和 second_column）之间应用一个操作符 $OPERATOR，
# 并在结果中加上一个时间偏移量 offset_in_seconds。
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
from transforms import expectations as E

# 检查 `timestamp` 是否在 `second_timestamp` 之后
E.col("timestamp").is_after_col("second_timestamp")

# 检查 `timestamp` 是否在 `second_timestamp` 之后或同一时间
E.col("timestamp").is_on_or_after_col("second_timestamp")

# 操作符接受一个可选的 offset_in_second 参数
# 检查 `second_timestamp` 是否在 `timestamp` 之后不到一小时
E.col("timestamp").is_before_col("second_timestamp", 3600)

# 检查 `second_timestamp` 是否在 `timestamp` 之前超过2小时
E.col("timestamp").is_on_or_before_col("second_timestamp", -7200)
```

### 相对时间戳比较

将时间戳列的值与检查运行时的时间（例如搭建发生时）加上用户指定的偏移量进行比较。偏移量可以作为秒数的整数提供，也可以作为timedeltapython 对象提供。

我们预计相对时间戳比较的精度可达几分钟。这是由于检查被实例化或运行的时间存在不精确性。运行检查后使用的确切时间戳将在期望检查结果中呈现。

提供了两种主要方法：timestamp_offset_from_current_time和timestamp_offset_to_current_time。我们提供两种不同的方法，以帮助以自然的方式推理相对时间偏移。因此，我们仅支持正时间偏移作为参数。如果需要使用负偏移，请考虑使用另一种方法。

#### timestamp_offset_from_current_time

此方法用于未来的相对时间，其中timestamp - now()是正值。此值将与提供的偏移量进行比较。所有常规比较运算符都可以用于比较。

```
Copied!1
2
3
4
5
6
7
8
from datetime import timedelta
from transforms import expectations as E

# 时间戳值小于未来1小时
A = E.col("timestamp").timestamp_offset_from_current_time().lt(3600)

# 时间戳值大于未来2小时
B = E.col("timestamp").timestamp_offset_from_current_time().gt(timedelta(hours=2))
```

#### timestamp_offset_to_current_time

此方法被用于在过去的相对时间，其中now() - timestamp为正值。然后将此值与提供的偏移量进行比较。所有常规比较运算符都可用于比较。

```
Copied!1
2
3
4
5
6
7
8
from datetime import timedelta
from transforms import expectations as E

# 时间戳值小于过去90分钟
C = E.col("timestamp").timestamp_offset_to_current_time().lt(5400)

# 时间戳值大于过去2小时
D = E.col("timestamp").timestamp_offset_to_current_time().gt(timedelta(hours=2))
```

#### 示例：预期结果

假设检查于1月1日下午4点运行，以下是我们对不同时间戳值的上述检查的预期结果。

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
   < ------- PAST ---------------------  NOW  -------------------- FUTURE ------>
   |    1pm   |    2pm   |    3pm   |    4pm   |    5pm   |    6pm   |    7pm   |
---+----------+----------+----------+----------+----------+----------+----------+
 A |   PASS   |   PASS   |   PASS   |   PASS   |   FAIL   |   FAIL   |   FAIL   |
---+----------+----------+----------+----------+----------+----------+----------+
 B |   FAIL   |   FAIL   |   FAIL   |   FAIL   |   FAIL   |   FAIL*  |   PASS   |
---+----------+----------+----------+----------+----------+----------+----------+
 C |   FAIL   |   FAIL   |   PASS   |   PASS   |   PASS   |   PASS   |   PASS   |
---+----------+----------+----------+----------+----------+----------+----------+
 D |   PASS   |   FAIL*  |   FAIL   |   FAIL   |   FAIL   |   FAIL   |   FAIL   |
---+----------+----------+----------+----------+----------+----------+----------+
```

这段代码展示了一个时间表格，显示了在不同时间点（从1pm到7pm）四个项目（A、B、C、D）在测试中的通过（PASS）和失败（FAIL）状态。

- A项目：从1pm到4pm状态为通过（PASS），从5pm开始到7pm状态为失败（FAIL）。
- B项目：从1pm到5pm状态为失败（FAIL），在6pm标记为特定失败（FAIL*），到7pm状态变为通过（PASS）。
- C项目：在1pm和2pm状态为失败（FAIL），从3pm开始到7pm状态为通过（PASS）。
- D项目：在1pm状态为通过（PASS），从2pm开始标记为特定失败（FAIL*），之后的状态一直为失败（FAIL）。
注：星号（*）可能表示特定或需要注意的失败状态。
检查 B 和 D 中的比较是严格比较。使用ge和le进行非严格比较。

### 分组和属性时间戳比较

大多数时间戳比较也可用于常规数据框或分组数据框的派生属性。

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
from datetime import timedelta
from transforms import expectations as E

# 检查最大时间戳是否在给定的静态日期之后
E.col("timestamp").max_value().is_after("2020-12-14T12:23:50+0000")

# 检查最小时间戳是否在过去1天以内
E.col("timestamp").min_value().timestamp_offset_to_current_time().lt(timedelta(days=1))

# 检查每个类别中的最后日期是否在未来超过2个月
E.group_by("category")
    .col("timestamp")
    .max_value()
    .timestamp_offset_from_current_time()
    .gt(timedelta(months=2))
```

注意：Python 的timedelta不支持months参数，因此在实际代码中，timedelta(months=2)可能会导致错误。在这种情况下，应该使用timedelta(days=60)或类似的解决方案来表示2个月的时间跨度。

## 数组期望

并非所有的期望都适用于数组类型的列。数组类型的列只能使用下面描述的特定期望。

### 数组等于

is_in期望同样适用于数组类型的列。对于数组，该期望测试数组仅包含在is_in子句中指定的值。

```
Copied!1
2
3
4
from transforms import expectations as E

# 'array_col'列中的任何数组只能包含值'a'、'b'或'c'。
E.col('array_col').is_in('a', 'b', 'c')
```

### 数组包含

array_contains期望允许您检查数组列的每一行是否包含特定值。

```
Copied!1
2
3
4
from transforms import expectations as E

# 检查 'array_col' 列中的所有行是否都包含值 'a'
E.col('array_col').array_contains('a') # 所有行在 'array_col' 中必须包含值 'a'。
```

### 数组大小

size期望允许您检查数组的每一行是否具有特定大小。

```
Copied!1
2
3
4
from transforms import expectations as E

E.col('array_col').size().gt(1) # 'array_col' 的长度必须大于1。
E.col('array_col').size().equals(2) # 'array_col' 的长度必须等于2。
```

## 分组期望

分组期望以E.group_by('column_1', 'column_2', ...)起始。分组期望允许对列的组合设置期望。

### 唯一性

```
Copied!1
2
3
4
from transforms import expectations as E

E.group_by('col1', 'col2').is_unique()
# 当组合在一起时，组合列的值在数据集中是唯一的
```

### 行数

行数预期测试用于测试每个分组的行数。如果 group_by 为空，则测试整个数据集的行数。

```
Copied!1
2
3
4
5
from transforms import expectations as E

E.group_by('col1', 'col2').count().gt(100)    # 对于每个由 'col1' 和 'col2' 分组的数据，其行数必须大于 100
E.group_by().count().lt(100)    # 数据集的行数小于 100。
E.count().equals(0)    # 空分组的简写。断言数据集的行数等于 0。
```

### 分组属性预期

所有属性比较预期也可以被用于在分组预期。

```
Copied!1
2
3
4
5
6
7
from transforms import expectations as E

# 对于每一个按 'col1' 分组的组，'value_col' 的不同值的数量必须等于3。
E.group_by('col1').col('value_col').distinct_count().equals(3)

# 对于每一个按 'col1' 分组的组，'value_col' 的空值百分比必须小于50%。
E.group_by('col1').col('value_col').null_percentage().lt(0.5)
```

## 主键

主键期望接受一个或多个列名并验证：

- 每列没有空值
- 列的组合是唯一的
```
Copied!1
2
3
4
from transforms import expectations as E

E.primary_key('c1')             # 列 `c1` 是唯一且不能为空。
E.primary_key('c1', 'c2',...)   # 列 {'c1', 'c2',...} 每个都不能为空，并且组合在一起是唯一的。
```

| 期望值 | 描述 | 示例 |
| --- | --- | --- |
| E.primary_key('c1') | 列c1是唯一且非空 | E.primary_key('object_id') |
| E.primary_key('c1', 'c2',...) | 列 {'c1', 'c2',...} 每个都非空，且组合在一起是唯一的 | E.primary_key('time', 'event') |

例如：

```
Copied!1
2
3
4
from transforms import expectations as E

# 设置 'time' 和 'event' 作为主键
E.primary_key('time', 'event')
```

## 模式预期

所有模式预期都以E.schema()开始。

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
from transforms import expectations as E

# 数据集的列必须包含所列出的列。
E.schema().contains({'col_name':type})

# 数据集的列必须与所列出的列完全匹配（不能有多余的列）。
E.schema().equals({'col_name':type})

# 数据集的列必须是所列出列的子集。
# 数据集中的所有列必须在检查中定义。
# 可以在检查中定义的列不必在数据集中存在。
E.schema().is_subset_of({'col_name':type})
```

例如：

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
from transforms import expectations as E

# 定义一个数据模式，该模式包含 'id' 和 'name' 字段
E.schema().contains(
    {
        'id': T.IntegerType(),  # 'id' 字段为整数类型
        'name': T.StringType()  # 'name' 字段为字符串类型
    }
)
```

此数据期望需要从pyspark.sql导入types（在示例中：as T）。

Lightweight变换中的模式期望需要使用Polars 数据类型 ↗代替：

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
from transforms import expectations as E
import polars as pl

# 定义一个期望的模式，其中包含字段'name'（字符串类型）和'int_list'（由Int32类型整数构成的列表）
E.schema().contains(
    {
        'name': pl.String(),  # 字段 'name' 类型为字符串
        'int_list': pl.List(pl.Int32)  # 字段 'int_list' 类型为整数列表，列表中的元素为Int32
    }
)
```

## 条件

条件期望包含三个期望并验证：

- 通过“when”期望的行也通过“then”期望
- 未通过“when”期望的行通过“otherwise”期望
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
from transforms import expectations as E

# 使用期望表达式来处理条件逻辑
E.when(
    when_exp,      # 如果条件 when_exp 为真
    then_exp       # 则执行 then_exp
).otherwise(
    otherwise_exp  # 否则执行 otherwise_exp
)
```

例如，当 "myCol" 大于 0 时，"myOtherCol" 必须在 ["a"] 中，否则 "myOtherCol" 必须在 ["b"] 中。

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
from transforms import expectations as E

# 使用 when-otherwise 模式创建条件逻辑
E.when(
    E.col("myCol").gt(0),  # 当列 "myCol" 的值大于 0
    E.col("myOtherCol").is_in("a")  # 则 "myOtherCol" 中的值应该在 "a" 中
).otherwise(
    E.col("myOtherCol").is_in("b")  # 否则，"myOtherCol" 中的值应该在 "b" 中
)
```

使用E.true()和E.false()为条件期望的otherwise分支设置简单的默认值。

## 外部值期望

警告：这是一个实验性功能。

外部值期望验证不同数据集之间的数据关系。这些期望涉及合并，评估成本可能非常高，因此请谨慎使用。

### 参照完整性

此期望验证预期数据集选定列中的所有值是否在外部数据集的指定列中存在。空值被忽略。

匹配的外部列通过使用其他数据集的名称创建的数据集引用限定：E.dataset_ref('other_dataset_name').col('f_col')。

外部数据集必须是您变换的输入（您不能简单地传入 RID 或路径），并且在E.dataset_ref中的引用应该是指派给它的变量名称。

使用列引用类似于is_in()的用法：

```
Copied!1
2
E.col('pk').is_in_foreign_col(E.dataset_ref('other_dataset').col('fk'))
# 检查当前数据集中的主键（pk）是否存在于其他数据集的外键（fk）中
```

## Cross-Dataset Row Count Comparisons

跨数据集的行数比较可用于比较一个数据集中的行数与另一个数据集中的行数。

例如，我们可以检查输出数据集的行数是否与输入数据集的行数相同：

```
Copied!1
2
E.count().equals(E.dataset_ref('input_dataset_name').count())
# 检查当前数据集的行数是否等于指定输入数据集的行数
```

用于比较的数据集通过使用其他数据集的名称创建的数据集引用进行限定。

您可以使用以下运算符进行数据集行数比较：

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
from transforms import expectations as E

# 验证计数是否等于输入数据集的计数
E.count().equals(E.dataset_ref('input_dataset_name').count()) # Equal to

# 验证计数是否小于输入数据集的计数
E.count().lt(E.dataset_ref('input_dataset_name').count()) # Less than

# 验证计数是否小于或等于输入数据集的计数
E.count().lte(E.dataset_ref('input_dataset_name').count()) # Less than or equal to

# 验证计数是否大于或等于输入数据集的计数
E.count().gte(E.dataset_ref('input_dataset_name').count()) # Greater than or equal to

# 验证计数是否大于输入数据集的计数
E.count().gt(E.dataset_ref('input_dataset_name').count()) # Greater than
```
