来源: https://palantir.com/docs/zh/foundry/transforms-python/create-historical-dataset/

# 从快照创建历史数据集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从快照创建历史数据集

如果可能的话，最好将此类数据集从起始就以附加事务方式进行摄取。有关更多详细信息，请参见下文的警告。

## 工作流概览

有时，您可能会有一个原始数据集，其中每天/每周/每小时的新快照导入会将之前的视图替换为数据集的当前数据。然而，通常也很有必要保留以前的数据，以确定与之前视图相比发生了什么变化。如上所述，最好的做法是在摄取时使用附加事务并添加导入日期列来处理这种情况。然而，在无法实现的情况下，您可以在Python变换中使用incremental()装饰器，将这些常规快照附加到该数据集的历史版本中。有关此方法脆弱性的警告，请参见下文的警告。

### 示例代码

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
@incremental(snapshot_inputs=['input_data'])
@transform(
    input_data=Input("/path/to/snapshot/input"),
    history=Output("/path/to/historical/dataset"),
)
def my_compute_function(input_data, history):
    input_df = input_data.dataframe()

    # 请注意，如果输入数据每天会变化超过一次，可以使用 current_timestamp()
    # 在下面这行中为数据框添加当前日期作为新列
    input_df = input_df.withColumn('date', current_date())

    # 将更新后的数据框写入历史数据集
    history.write_dataframe(input_df)
```

### 为什么这有效

增量装饰器为输入和输出的读/写模式添加了额外的逻辑。在上面的例子中，我们对输入和输出使用了默认读/写模式。

#### 读取模式

使用SNAPSHOT输入时，默认的读取模式是current，这意味着它获取整个输入数据框，而不仅仅是自上次事务以来添加的行。然而，如果输入数据集是由APPEND事务创建的，我们可以使用incremental()装饰器来使用added读取模式，仅访问自上次搭建以来添加的那些行。该变换从current输出获取模式信息，因此不需要像读取数据框的previous版本时那样传递模式信息（例如，dataframe('previous', schema=input.schema)）。

#### 写入模式

当我们说一个变换是增量运行的，这意味着输出的默认写入模式设置为modify。这种模式在搭建期间用写入的数据修改现有输出。例如，当输出处于modify模式时，调用write_dataframe()会将写入的数据框追加到现有输出中。这正是此案例中发生的情况。

## 警告

由于此变换使用SNAPSHOT数据集作为输入，无法恢复搭建可能错过的快照（由于搭建失败或其他原因）。如果这是一个问题，请不要使用这种方法。相反，请联系输入数据集的所有者，看看是否可以将其转换为APPEND数据集，以便您可以访问数据集的先前事务。这就是增量计算的设计工作方式。

如果发生以下情况，将会失败：

- 向输入数据集添加列
- 现有表的列数与[input]数据模式不匹配
- 输入数据集上的列更改数据类型（例如，从integer到decimal）
- 您更改输入数据集，即使该数据集具有相同的模式。在这种情况下，它将完全用输入替换输出，而不是追加。
### 增加的资源消耗

使用这种模式可能会导致历史数据集中累积小文件。文件积累不是期望的结果，并会导致搭建时间增加，以及使用此历史数据集的下游变换或分析中的资源消耗增加。批处理和交互式计算时间可能会增加，因为读取每个文件时有开销。磁盘使用量可能会增加，因为压缩是在每个文件的基础上完成的，而不是在数据集内的文件之间完成的。
可以构建逻辑以定期重新快照数据并防止这种行为的发生。

通过检查输出文件的数量，我们可以确定一个最佳的增量写入模式。这种模式允许我们读取先前事务的输出作为数据框，将其与传入数据合并，并将数据文件合并在一起，将许多小文件变成一个较大的文件。

检查输出数据集文件系统中的文件数量，并使用if语句设置write_mode，如下例所示：

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
from transforms.api import transform, Input, Output, configure, incremental
from pyspark.sql import types as T

FILE_COUNT_LIMIT = 100

# 请确保在此处插入您期望的输出schema
schema = T.StructType([
    T.StructField('Value', T.DoubleType()),
    T.StructField('Time', T.TimestampType()),
    T.StructField('DataGroup', T.StringType())
])

def compute_logic(df):
    """
    这是您的转换逻辑
    """
    return df.filter(True)

@configure(profile=["KUBERNETES_NO_EXECUTORS"])
@incremental(semantic_version=1)
@transform(
    output=Output("/Org/Project/Folder1/Output_dataset_incremental"),
    input_df=Input("/Org/Project/Folder1/Input_dataset_incremental"),
)
def compute(input_df, output):
    df = input_df.dataframe('added')
    df = compute_logic(df)

    # 获取数据集中的文件列表
    files = list(output.filesystem(mode='previous').ls())

    if (len(files) > FILE_COUNT_LIMIT):
        # 增量合并并替换
        previous_df = output.dataframe('previous', schema)
        df = df.unionByName(previous_df)
        mode = 'replace'
    else:
        # 标准增量模式
        mode = 'modify'

    output.set_mode(mode)
    output.write_dataframe(df.coalesce(1))
```
