来源: https://palantir.com/docs/zh/foundry/transforms-python/incremental-examples/

# 示例

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例

本节包含大量可增量计算的变换示例：

- 追加
- 合并并追加
- 合并并替换
- 利用增量变换合并大型数据集
- 处理模式或逻辑更改
- 在分支上开发增量代码
- 示例总结
这些示例使用两个输入来演示增量计算：students和students_updated。students输入包含3个学生，并且不是增量的。这意味着它没有历史记录：

```
>>> students.dataframe('previous').sort('id').show()
+---+----+---+---+
| id|hair|eye|sex|
+---+----+---+---+
+---+----+---+---+
# 显示“previous”数据帧，按'id'排序后显示，但没有数据输出

>>>
>>> students.dataframe('current').sort('id').show()
+---+-----+-----+------+
| id| hair|  eye|   sex|
+---+-----+-----+------+
|  1|Brown|Green|Female|
|  2|  Red| Blue|  Male|
|  3|Blond|Hazel|Female|
+---+-----+-----+------+
# 显示“current”数据帧，按'id'排序后显示，包含3条记录

>>>
>>> students.dataframe('added').sort('id').show()
+---+-----+-----+------+
| id| hair|  eye|   sex|
+---+-----+-----+------+
|  1|Brown|Green|Female|
|  2|  Red| Blue|  Male|
|  3|Blond|Hazel|Female|
+---+-----+-----+------+
# 显示“added”数据帧，按'id'排序后显示，与“current”数据帧内容相同

>>>
>>> # Recall that the default read mode for inputs is 'added'
>>> students.dataframe('added') is students.dataframe()
True
# 默认读取模式是“added”，所以 students.dataframe('added') 与 students.dataframe() 是同一个对象
```

students_updated输入与students相同，但新增了三个学生的更新。此更新使输入具有增量特性。因此，它有一个非空的previousDataFrame。

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
>>> students_updated.dataframe('previous').sort('id').show()
+---+-----+-----+------+
| id| hair|  eye|   sex|
+---+-----+-----+------+
|  1|Brown|Green|Female|
|  2|  Red| Blue|  Male|
|  3|Blond|Hazel|Female|
+---+-----+-----+------+
>>>
>>> students_updated.dataframe('current').sort('id').show()
+---+-----+-----+------+
| id| hair|  eye|   sex|
+---+-----+-----+------+
|  1|Brown|Green|Female|
|  2|  Red| Blue|  Male|
|  3|Blond|Hazel|Female|
|  4|Brown|Green|Female|
|  5|Brown| Blue|  Male|
|  6|Blond|Hazel|Female|
+---+-----+-----+------+
>>>
>>> students_updated.dataframe('added').sort('id').show()
+---+-----+-----+------+
| id| hair|  eye|   sex|
+---+-----+-----+------+
|  4|Brown|Green|Female|
|  5|Brown| Blue|  Male|
|  6|Blond|Hazel|Female|
+---+-----+-----+------+
>>>
>>> # Recall that the default read mode for inputs is 'added'
>>> # 请记住，输入的默认读取模式是 'added'
>>> students_updated.dataframe('added') is students_updated.dataframe()
True
```

### 追加

仅追加的增量计算是指其新增输出行仅是新增输入行的函数。这意味着要计算其输出，变换执行以下操作：

- 查看任何新添加的输入数据，
- 计算任何新的输出行——这些仅是新增输入行的函数，并且
- 将新的输出追加到现有输出中。
更改列类型、将日期格式化为字符串以及筛选都是仅追加计算的例子。在这些例子中，每个新增输入行都被变换或删除以生成输出行。

请注意，使仅追加变换增量化的唯一不同之处是incremental()装饰。

在增量运行时，默认的读取模式added意味着变换只读取新学生，而默认的写入模式modify意味着变换仅将筛选后的新学生追加到输出中。

在非增量运行时，默认的读取模式added意味着变换读取完整的输入，而默认的写入模式replace意味着变换用完整的筛选学生集替换输出。

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
from transforms.api import transform, incremental, Input, Output

@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def incremental_filter(students, processed):
    new_students_df = students.dataframe()  # 从输入数据中获取DataFrame
    processed.write_dataframe(
        new_students_df.filter(new_students_df.hair == 'Brown')  # 过滤出头发颜色为棕色的学生
    )
```

上述代码使用了一个增量转换器，它从输入路径/examples/students_hair_eye_color读取学生数据，并过滤出头发颜色为棕色的学生，将结果写入到输出路径/examples/hair_eye_color_processed。

### 合并和追加

有时，变换需要引用其先前的输出以便增量计算更新。一个例子是distinct()↗方法。 要在变换中删除重复行（假设当前输出是正确的），必须对输入中的任何新行进行去重，然后检查这些行是否已经存在于输出中。

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
@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def incremental_distinct(students, processed):
    new_students_df = students.dataframe()  # 从输入数据源读取学生数据并转换为DataFrame
    processed.write_dataframe(
        new_students_df.distinct().subtract(
            processed.dataframe('previous', schema=new_students_df.schema)  # 从已处理数据中减去先前的数据
        )
    )
```

在这里，我们在输出数据集上使用previous读取模式。这将返回上次搭建过程中输出的DataFrame↗。由于可能没有previous输出，我们必须为dataframe('previous')调用提供一个模式，以便可以正确构建一个空的DataFrame。

运行此代码时，输出数据集的模式将从数据中自动推断。这包括自动检测列的名称、类型、"nullability"（请参见StructField↗）以及列的顺序。为了确保搭建的可靠性，最好将dataframe的预期模式硬编码，而不是依赖Spark推断。

### 合并和替换

有些变换总是会替换它们的整个输出。然而，这些变换通常仍然可以从增量计算中受益。一个这样的例子是统计聚合。例如，计算每个不同值在列中出现的次数。

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
from pyspark.sql import functions as F

@incremental()
@transform(
    students=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def incremental_group_by(students, processed):
    # 计算新学生头发颜色的计数。
    new_hair_counts_df = students.dataframe().groupBy('hair').count()

    # 与旧的计数合并
    out_schema = new_hair_counts_df.schema
    all_counts_df = new_hair_counts_df.union(
        processed.dataframe('previous', schema=out_schema)
    )

    # 按头发颜色分组，汇总两个计数集。
    totals_df = all_counts_df.groupBy('hair').agg(F.sum('count').alias('count'))

    # 为了完全替换输出，我们总是将输出模式设置为 'replace'。
    # 在更改输出模式之前，检查点 totals 数据框。
    totals_df.localCheckpoint(eager=True)
    processed.set_mode('replace')
    processed.write_dataframe(totals_df.select(out_schema.fieldNames()))
```

该代码使用 Apache Spark 来处理和聚合学生数据，具体来说是根据头发颜色进行计数。函数incremental_group_by通过增量更新模式来处理输入数据集students和已有的处理结果processed。最终结果被写回processed，并且在写入之前对数据进行检查点以确保一致性和可靠性。
由于可能不存在previous输出，我们必须为dataframe('previous')调用提供一个模式，以便可以正确构建一个空的DataFrame。

### 合并并替换为模式更改

在某些情况下，需要使用输入以增量方式更新数据集，而输入的模式可能会更改。一个例子是当输入来自一个源表，该表中的列可能会随着时间的推移而增加或删除。在这种情况下，我们需要使用旧模式读取之前的输出，然后手动与新模式进行协调。

我们仍然需要定义当变换以SNAPSHOT模式运行时应如何表现，这意味着没有之前的输出。在这种情况下，调用processed.dataframe('current')会失败。

下面的示例展示了如何将新的students添加到现有的students_processed数据集中，即使新的students数据集的模式不同。

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
from pyspark.sql import functions as F

@incremental(
    snapshot_inputs=['students']
)
@transform(
    students=Input('/examples/students_raw'),  # 此数据集的模式可能会发生变化。注意这意味着它必须是一个 SNAPSHOT 事务，因此我们将其包含在 @incremental 装饰器的 "snapshot_inputs" 参数中。
    processed=Output('/examples/students_processed')
)
def incremental_group_by(students, processed, ctx):

    if not ctx.is_incremental:
        # 这种情况需要单独处理
        # ...
        return


    # 读取具有其关联模式的旧处理数据框
    # 由于我们尚未写入 processed，'current' 将为我们提供上一个事务
    # 注意：在此代码路径中，'processed' 的写入模式仍是 'modify' 是很重要的（见下面的警告）
    students_previous = processed.dataframe('current').localCheckpoint()

    # 合并旧数据框和新数据框，将缺失的列设置为 null
    students_all = students_previous.unionByName(students.dataframe(), allowMissingColumns=True)

    # 写出新的合并数据框
    processed.set_mode('replace')
    processed.write_dataframe(students_all)
```

请注意，使用.dataframe()调用的读取模式评估是惰性的（按需调用），这意味着评估会被延迟直到需要该值。数据框读取的输出根据数据集的写入模式在write_dataframe调用期间进行评估，从而忽略之前的写入模式。调用.localCheckpoint(eager=True)强制读取数据，并在此时评估输出写入模式，且不会重新计算。

### 利用增量变换来合并大型数据集

假设您有两张表 - 客户提交的Orders和已完成的Deliveries- 我们希望计算一个表DeliveryDuration，显示物品交付所需的时间。即使Orders和Deliveries表都只会追加新行，且不会修改任何行，简单地合并这两个增量数据集也是行不通的。例如，Orders表可能包含尚未出现在Deliveries表中的orderIds。

```
Orders:                               Deliveries:
+---------+---------------+           +---------+--------------+           +---------+------------------+
| orderId | submittedDate |           | orderId | deliveryDate |           | orderId | deliveryDuration |
+---------+---------------+           +---------+--------------+   ---->   +---------+------------------+
| 1001    | 2019-08-21    |  join on  | 1001    | 2019-08-23   |           | 1001    | 2                |
+---------+---------------+  orderId  +---------+--------------+           +---------+------------------+
| 1002    | 2019-08-22    |
+---------+---------------+
| 1003    | 2019-08-23    |
+---------+---------------+
```

上述表格演示了如何通过orderId字段将Orders表与Deliveries表进行连接（join），从而生成一个新的表格DeliveryDuration。在这个新表格中，我们通过计算deliveryDate和submittedDate之间的时间差，得到每个订单的交付持续时间deliveryDuration。
假设orderId在Orders和Deliveries表中都严格递增，我们可以检查我们为其计算了deliveryDuration的最后一个orderId（maxComputedOrderId），并且只从Orders和Deliveries表中获取orderId大于maxComputedOrderId的行：

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
35
36
37
38
39
40
41
42
43
44
45
from transforms.api import transform, Input, Output, incremental
from pyspark.sql import types as T
from pyspark.sql import functions as F

@incremental(snapshot_inputs=['orders', 'deliveries'])
@transform(
    orders=Input('/example/Orders'),
    deliveries=Input('/example/Deliveries'),
    delivery_duration=Output('/example/New_Delivery_Date')
)
def compute_delivery_duration(orders, deliveries, delivery_duration):
    def to_fields(datatype, names, nullable=True):
        # 为每个字段创建StructField
        return [T.StructField(n, datatype, nullable) for n in names]

    # 为deliveryDuration生成一个schema
    fields = to_fields(T.IntegerType(), ['orderId', 'deliveryDuration'])

    # 显式定义schema，因为不能引用之前版本的schema
    maxComputedOrderId = (
        delivery_duration
        .dataframe('previous', schema=T.StructType(fields))
        .groupby()
        .max('orderId')
        .collect()[0][0]
    )

    # 在第一次迭代时，maxComputedOrderId为空，因为delivery_duration数据集尚不存在
    if maxComputedOrderId == None:
        maxComputedOrderId = 0

    # 过滤掉已经处理过的orders和deliveries
    ordersNotProcessed = orders.dataframe().filter(F.col('orderId') > maxComputedOrderId)
    deliveriesNotProcessed = deliveries.dataframe().filter(F.col('orderId') > maxComputedOrderId)

    # 计算新的deliveryDuration
    newDurations = (
        ordersNotProcessed
        .join(deliveriesNotProcessed, 'orderId', how='left')
        .withColumn('deliveryDuration', F.datediff(F.col('deliveryDate'), F.col('submittedDate')))
        .drop(*['submittedDate', 'deliveryDate'])
    )

    # 将计算结果写入delivery_duration
    delivery_duration.write_dataframe(newDurations)
```

### 代码说明

这段代码实现了一个增量计算任务，用于计算订单的交付时长并将结果存储到输出数据集中。compute_delivery_duration函数接收三个参数：orders、deliveries和delivery_duration，分别对应订单数据集、交付数据集和输出数据集。代码中的增量计算通过只处理orderId大于上次计算的最大orderId的记录来实现，从而提高性能。

### 处理模式或逻辑更改

假设我们现在想在增量数据集中添加另一列。向输出中添加另一列不会使is_incremental标志失效，因此下一次运行将计算新行并写入带有新列的数据，此列在之前写入的所有行中将为空。

然而，我们可能希望为之前的行填充此列。增加变换的semantic_version将使其非增量地运行一次，如果您使用的是“added”读取模式，输入将包含所有数据，使您能够重新计算并添加新列。

如果您的变换是从快照输入创建历史数据集，那么情况会稍微复杂一些，因为之前的数据是您输入中的快照事务堆栈。在这种情况下，请联系您的Palantir代表。

在此示例中，我们讨论了添加新列，但上述推理适用于各种逻辑更改。

### 在分支上开发增量代码

创建新分支并在其上运行搭建，将增量运行搭建。简单来说，您创建分支所基于的原始分支上的最后一个提交事务将被视为新分支上的第一次搭建的前一个事务。

### 示例总结

我们了解了如何通过以下方式增量处理数据：

- 获取新添加的行，处理它们并将其附加到输出中，
- 获取新添加的行，根据输出中已存在的行筛选它们，并将其附加到输出中，
- 获取新添加的行，基于新行和输出中已存在的行计算聚合，并用新的聚合统计替换输出，
- 利用增量变换合并大型数据集。
我们还探讨了如何：

- 处理增量变换的模式或逻辑更改，
- 在不基于输入的完整内容重建的情况下，在分支上开发增量代码。
## 增量Python出错

要理解增量出错，了解事务和数据集视图的概念会更容易且有时是必要的。

### 目录事务出错

#### 有用的背景

当一个任务增量运行时，其增量输入数据集仅由未处理的事务范围组成，而不是完整的数据集视图。

想象一下数据集的以下事务历史：

```
SNAPSHOT (1) --> UPDATE (2) --> UPDATE (3) --> UPDATE (4) --> UPDATE (5)
                                   |
                       Last processed transaction
                       最后处理的事务
```

这个代码片段显示了一个事务处理的流程图。SNAPSHOT表示初始快照状态，后续的UPDATE表示每次更新操作。在图中，箭头表示事务的执行顺序。“Last processed transaction”指的是最后一个已处理的事务，在这个例子中，标记在UPDATE (4)。
上次数据集搭建时，最新的事务是(3)。从那时起，事务(4)和(5)已提交，因此未处理的事务范围是(4) — (5)。

数据集视图是事务范围(1) — (5)。视图“顶部”的事务（最新的）有时被称为分支的HEAD（同样是类比于git）。就像在git中一样，分支是指向事务的指针，因此我们说分支指向事务(5)。多个分支可以指向多个事务，并且分支可能共享一个事务历史：

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
graph TD;
    SNAPSHOT1[SNAPSHOT (1)] --> UPDATE2[UPDATE (2)];
    UPDATE2 --> UPDATE3[UPDATE (3)];
    UPDATE3 --> UPDATE4[UPDATE (4)];
    UPDATE4 --> UPDATE5[UPDATE (5)];
    UPDATE3 --> featureBranch[UPDATE];

    class SNAPSHOT1,UPDATE2,UPDATE3,UPDATE4,UPDATE5 developBranch;
    class featureBranch featureBranch;

    classDef developBranch fill:#f9f,stroke:#333,stroke-width:2px;
    classDef featureBranch fill:#9f9,stroke:#333,stroke-width:2px;
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
%% 该图描述了一个版本控制系统中的分支和更新流程。
%% [develop] 是主开发分支，从 SNAPSHOT (1) 开始，经过一系列更新到达 UPDATE (5)。
%% [feature-branch] 是从 UPDATE (3) 分叉出来的一个特性分支。
graph TD;
    SNAPSHOT1[SNAPSHOT (1)] --> UPDATE2[UPDATE (2)];
    UPDATE2 --> UPDATE3[UPDATE (3)];
    UPDATE3 --> UPDATE4[UPDATE (4)];
    UPDATE4 --> UPDATE5[UPDATE (5)];
    UPDATE3 --> featureBranch[UPDATE];

    class SNAPSHOT1,UPDATE2,UPDATE3,UPDATE4,UPDATE5 developBranch;
    class featureBranch featureBranch;

    classDef developBranch fill:#f9f,stroke:#333,stroke-width:2px;
    classDef featureBranch fill:#9f9,stroke:#333,stroke-width:2px;
```

解释：

- 主开发分支[develop]从 SNAPSHOT (1) 开始，经过多个更新（2到5）。
- 从 UPDATE (3) 分叉出一个特性分支[feature-branch]，进行独立的更新。
```
#### 出错: `Catalog:TransactionsNotInView`

为了使任务增量运行，会在任务起始时运行一系列检查。
其中一个检查验证未处理事务范围是严格增量的（即，仅追加文件更改，请参见[增量计算要求](./incremental-reference.md#requirements-for-incremental-computation)）。它通过比较未处理事务范围和已处理事务范围中的文件来实现。

然而，如果分支的HEAD已经移动，增量任务现在处于不一致状态：比较两个范围已经没有意义，因此会抛出出错 `Catalog:TransactionNotInView`。

请参阅下方的图示以了解此错误如何发生：
```

SNAPSHOT (1) ─> UPDATE (2) ─> UPDATE (3)      ─> UPDATE (4) ─> UPDATE (5)
|          (last processed                  (branch's previous
|            transaction)                     HEAD, now orphan)
|
└─> UPDATE (6) --> UPDATE (7, branch's current HEAD)

```
此图展示了一个更新历史的流程，以下是对图中各元素的解释：

- `SNAPSHOT (1)`: 初始快照。
- `UPDATE (2)`: 第一次更新。
- `UPDATE (3)`: 第二次更新，标记为“最后处理的事务”。
- `UPDATE (4)` 和 `UPDATE (5)`: 第三和第四次更新，其中 `UPDATE (5)` 是分支的前一个 HEAD，现在已经成为孤立节点。
- 从 `UPDATE (2)` 分支出一个新的路径：
  - `UPDATE (6)`: 第五次更新。
  - `UPDATE (7)`: 第六次更新，当前分支的 HEAD。
这里处理的交易范围是 (1) — (5)，当前分支的 HEAD 指向 (7)，当前视图包含交易 (1)、(2)、(6) 和 (7)。

这是一个不一致的状态，因为并非所有处理的交易都位于分支的 HEAD 之上：实际上 (3) 不是。换句话说，之前的 HEAD (3) 不再是当前视图的一部分，因此抛出 `Catalog:TransactionNotInView`。

#### 错误: `Catalog:InconsistentBranchesOrder`

另一个可能抛出的 Catalog 错误是 `Catalog:InconsistentBranchesOrder`，当最后处理的交易 (`prevTransaction`) 大于分支的 HEAD (`endTransaction`) 时会发生这种情况。如果数据集的 HEAD 被移动到之前交易之前的某个交易，就会发生这种情况。

请参见下面的图示说明此错误如何发生：
```

SNAPSHOT (1) --> UPDATE (2) --> UPDATE (3) --> UPDATE (4) --> UPDATE (5)
|                             |
Current HEAD            Last processed transaction
当前的HEAD节点             最后处理的事务

```
此代码段描述了一个版本控制或事务处理的流程，其中：

- **SNAPSHOT (1)**: 这是初始快照或初始状态。
- **UPDATE (2)** 到 **UPDATE (5)**: 这些是连续的更新步骤。
- **Current HEAD**: 表示当前的最新状态或版本。
- **Last processed transaction**: 表示最后一个已处理的事务。
#### 纠正出错

分支的HEAD可以由于两个原因发生更改：

* 用户通过目录端点有意识地更新了分支的HEAD。
* 一些事务没有通过变换任务提交。例如，当你在代码工作簿中合并分支时，数据集也会被“合并”。
* 然而，[代码工作簿](../code-workbook/overview.md) 数据集上的事务始终是 `SNAPSHOT`，因此它们不会导致不一致的状态。

为了纠正这个问题，你需要：

* 以快照形式运行变换；例如，通过更改语义版本。这将启动一个新的数据集视图，从而重置上述增量检查。
* 手动更新分支的HEAD，以指向已处理范围下游的一个事务。这必须使用 `updateBranch2` 端点，并将最新处理的事务作为 parentRef。请注意，我们仅建议有经验的用户使用此端点。
```
