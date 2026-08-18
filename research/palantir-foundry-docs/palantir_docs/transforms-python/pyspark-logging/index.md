来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-logging/

# 日志记录

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 日志记录

可以从 Foundry 中的 PySpark 输出各种调试信息。

## 代码工作簿

Python 内置的print将输出到代码编辑器右侧代码工作簿的输出部分，错误通常会显示在那里。

```
Copied!1
2
3
def new_dataset(some_input_dataset):
    # 打印示例日志输出
    print("example log output")
```

```
示例日志输出
```

## 代码存储库

代码存储库使用 Python 内置的日志库 ↗。这在网上有广泛的文档支持，并允许您控制日志级别（ERROR，WARNING，INFO），以便于筛选。

日志输出会出现在您的输出数据集的日志文件中，以及您的搭建的驱动程序日志中（Dataset -> Details -> Files -> Log Files，以及Builds -> Build -> 任务状态日志; 分别选择"Driver logs"）。

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
import logging

# 创建一个日志器对象，用于记录日志信息
logger = logging.getLogger(__name__)

@transform_df(
    ...
)
def some_transformation(some_input):
    # 记录一条信息级别的日志
    logger.info("example log output")
```

```
INFO [2018-01-01T12:00:00] some_transformation: example log output
```

此代码行是一个日志信息的示例。通常用于记录程序执行过程中的重要事件。在这里：

- INFO表示日志级别为信息级别，通常用于记录程序正常运行的信息。
- [2018-01-01T12:00:00]表示日志记录的时间戳。
- some_transformation可能是执行的某个转换或操作的名称。
- example log output是日志的具体输出信息。
### 从Python UDF内部记录日志

Spark会捕获从创建查询的顶级驱动程序进程输出的日志，例如上面的some_transformation函数。然而，它不会捕获从用户自定义函数（UDFs）内部写入的日志。如果您在PySpark查询中使用UDF并需要记录数据，请创建并调用第二个UDF，返回您希望捕获的数据。

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
@transform_df(
    ...
)
def some_transformation(some_input):
    logger.info("log output related to the overall query")
    # 记录与整个查询相关的日志输出

    @F.udf("integer")
    def custom_function(integer_input):
        # 自定义函数，将输入整数加上5
        return integer_input + 5

    @F.udf("string")
    def custom_log(integer_input):
        # 自定义日志函数，记录原始整数在加5前的值
        return "Original integer was %d before adding 5" % integer_input

    df = (
        some_input
        .withColumn("new_integer", custom_function(F.col("example_integer_col")))
        # 增加一个新列 "new_integer"，值为原始列 "example_integer_col" 加5后的结果
        .withColumn("debugging", custom_log(F.col("example_integer_col")))
        # 增加一个新列 "debugging"，记录原始整数的日志信息
    )
```

注意：在withColumn的括号中，缺少了右括号)，我已在代码中补充。

## 示例

我们经常想记录查询中的信息。PySpark 有多种方式检查 DataFrame，我们可以将这些信息发送到上述的日志记录机制。

在这些示例中，我们将使用 Code Workbook 的print语法，但print可以替换为 Transforms & Authoring 的logger。

### DataFrame 列

我们可以使用df.columns检查 DataFrame 上存在的列。这会生成一个字符串列表。

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
def employee_phone_numbers(employee_df, phone_number_df):
    # 打印员工数据框的列名
    print("employee columns are {}".format(employee_df.columns))
    # 打印电话数据框的列名
    print("phone columns are {}".format(phone_df.columns))
    # 使用左连接（left join）将员工数据框与电话数据框通过'employee_id'列连接
    df = employee_df.join(phone_number_df, 'employee_id', 'left')
    # 打印连接后的数据框的列名
    print("joined columns are {}".format(df.columns))
```

```
Copied!1
2
3
employee 表的列为 ['name', 'employee_id']  # 员工表包含员工的姓名和员工ID
phone 表的列为 ['phone_number', 'employee_id']  # 电话表包含电话号码和对应的员工ID
joined 表的列为 ['name', 'employee_id', 'phone_number']  # 连接表包含员工的姓名、员工ID和电话号码
```

### 验证合并行为

假设我们正在执行一个左合并，期望是一对一的关系，并希望验证左侧DataFrame中的行数保持不变。

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
def employee_phone_numbers(employee_df, phone_number_df):
    # 获取初始员工数据的行数
    original_employee_rows = employee_df.count()
    print("Incoming employee rows {}".format(original_employee_rows))

    # 使用员工ID进行左连接，合并员工数据与电话号码数据
    df = employee_df.join(phone_number_df, 'employee_id', 'left')
    # 获取合并后数据的行数
    rows_after_join = df.count()
    print("Final employee rows {}".format(rows_after_join))

    # 判断合并后的行数是否大于初始行数
    if rows_after_join > original_employee_rows:
        print("Some employees have multiple phone numbers!")  # 如果大于，说明某些员工有多个电话号码
    else:
        print("Data is correct")  # 否则数据正确
```

```
// 输入的员工记录数：100
// 最终的员工记录数：105
// 有些员工有多个电话号码！
Incoming employee rows 100
Final employee rows 105
Some employees have multiple phone numbers!
```

### Spark查询计划

您可以通过调用.explain()来访问Spark将用于生成给定DataFrame的优化物理计划。

```
Copied!1
2
3
4
5
6
7
def employee_phone_numbers(employee, phone):
    # 筛选出生日月份与当前月份相同的员工
    employee = employee.where(F.month(employee.birthday) == F.month(F.current_date()))
    # 使用左连接将员工信息与电话信息合并，基于'employee_id'
    df = employee.join(phone, 'employee_id', 'left')
    # 解释查询计划以便于调试和优化
    df.explain()
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
== Physical Plan ==
*(2) Project [employee_id#9734, name#9732, birthday#9733, phone_number#9728]
+- *(2) BroadcastHashJoin [employee_id#9734], [employee_id#9729], LeftOuter, BuildRight
   :- *(2) Filter (month(birthday#9733) = 10)  // 筛选出生月份为10月的记录
   :  +- *(2) FileScan parquet !ri.foundry.main.transaction.00000000-e98a-c557-a20f-5eea5f373e36:ri.foundry.main.transaction.00000000-e98a-c557-a20f-5eea5f373e36@00000000-1ebd-4a81-9f64-2d4c8a8472bc:master.ri.foundry.main.dataset.6ad20cd7-45b0-4312-b096-05f57487f650[name#9732,birthday#9733,employee_id#9734] Batched: true, Format: Parquet, Location: FoundryCatalogFileIndex[sparkfoundry://.../datasets/ri.f..., PartitionFilters: [], PushedFilters: [], ReadSchema: struct<name:string,birthday:date,employee_id:int>
   +- BroadcastExchange HashedRelationBroadcastMode(List(cast(input[1, int, true] as bigint)))
      +- *(1) Project [phone_number#9728, employee_id#9729]
         +- *(1) Filter isnotnull(employee_id#9729)  // 过滤掉employee_id为空的记录
            +- *(1) FileScan csv !ri.foundry.main.transaction.00000000-e989-4f9a-90d5-996f088611db:ri.foundry.main.transaction.00000000-e989-4f9a-90d5-996f088611db@00000000-1ebc-f483-b75d-dbcc3292d9e4:master.ri.foundry.main.dataset.f5bf4c77-37c0-4e29-8a68-814c35442bbd[phone_number#9728,employee_id#9729] Batched: false, Format: CSV, Location: FoundryCatalogFileIndex[sparkfoundry://.../datasets/ri.f..., PartitionFilters: [], PushedFilters: [IsNotNull(employee_id)], ReadSchema: struct<phone_number:int,employee_id:int>
```

解释：

- 此计划展示了一个物理执行计划，其中包含一个广播哈希连接（BroadcastHashJoin），在两个数据集之间进行左外连接。
- 首先筛选出生月份为10月的记录，然后读取Parquet格式的数据文件。
- 其次，过滤掉employee_id为空的记录，读取CSV格式的数据文件。
- 最终，使用employee_id进行连接，并投影出所需的字段：employee_id、name、birthday和phone_number。
### 查看数据

假设我们想查看哪些员工拥有最多的电话号码。我们将提取我们感兴趣的数据集（拥有多个号码的员工）并调用.take(3)来检索前 3 行作为列表。或者，使用.collect()可以将 DataFrame 的所有行检索为一个列表。

将过多数据导入您的Python环境可能会导致内存耗尽。只collect()少量数据。

```
Copied!1
2
3
4
5
6
def multiple_numbers(phone_numbers):
    df = phone_numbers.groupBy('employee_id').agg(
        F.count('phone_number').alias('numbers')  # 统计每个员工的电话号码数量
    ).where('numbers' > 1).sort(F.col('numbers').desc())  # 过滤出电话号码数量大于1的员工，并按数量降序排序

    print(df.take(3))  # 输出前三个记录
```

```
Copied!1
2
3
4
5
[
    Row(employee_id=70, numbers=4),  # 员工ID为70的记录，数量为4
    Row(employee_id=90, numbers=2),  # 员工ID为90的记录，数量为2
    Row(employee_id=25, numbers=2)   # 员工ID为25的记录，数量为2
]
```
