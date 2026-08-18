来源: https://palantir.com/docs/zh/foundry/code-workbook/workbooks-languages/

# 语言

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 语言

## 支持的语言和版本

Code Workbook 目前支持三种语言：Python、R 和 SQL。

Code Workbook 目前支持的 Python 版本包括 Python 3.8 和 Python 3.9。不支持 Python 2，使用 Python 2 的环境将无法解析。我们强烈建议使用 Python 的较新版本，因为 Palantir Foundry 将弃用 Python 开发者文档中被视为生命周期结束 ↗的 Python 版本。

目前支持的 R 版本包括 R 3.5、R 3.6、R 4.0、R 4.1 和 R 4.2。不支持 R 3.3 和 R 3.4 版本，其相应的环境将无法初始化。

Code Workbook 中支持的 SQL 变体是Spark SQL ↗。

要在 Code Workbook 配置文件中启用特定语言，请参阅配置 Code Workbook 配置文件文档中的 Conda Environment 部分。下面提供了每种支持语言的系列示例，在相应的Python、R和SQL介绍中。

Palantir Foundry 将在 2024 年 2 月 1 日后不再支持 Python 3.6 和 Python 3.7。对于 Python 3.8 及更高版本，Foundry 将遵循 Python 软件基金会定义的弃用时间表（见版本生命周期表 ↗），这意味着在生命周期结束后，Foundry 将不再支持该 Python 版本。有关详细信息，请参阅Python 版本支持文档。

### 在工作簿中启用语言

需要进行特定配置以使支持的语言正常运行，如下节所述。

#### 启用 R

R 尚未提供自助服务。

要在 Code Workbook 中创建 R 变换，必须满足以下两个条件：

- 必须在您的注册中专门启用 R 语言。请联系您的 Palantir 代表以获取启用帮助。
- 当前使用的工作簿环境中必须存在包vector-spark-module-r。可以通过以下两种方式实现：在控制面板中切换配置文件的R复选框。这将自动将vector-spark-module-r包添加到配置文件的环境中。使用添加包下拉菜单手动将vector-spark-module-r添加到环境中。
- 在控制面板中切换配置文件的R复选框。这将自动将vector-spark-module-r包添加到配置文件的环境中。
- 使用添加包下拉菜单手动将vector-spark-module-r添加到环境中。
有关详细信息，请参阅配置 Code Workbook 配置文件。

#### 启用 Python

当前使用的工作簿环境中必须存在包vector-spark-module-py。可以通过以下两种方式实现：

- 在控制面板中切换配置文件的 Python 复选框。这将自动将vector-spark-module-py包添加到环境中。
- 使用添加包下拉菜单手动将vector-spark-module-py添加到环境中。
有关详细信息，请参阅配置 Code Workbook 配置文件。

#### 启用 SQL

SQL 变换不需要任何额外的包即可运行。因此，对于任何给定的配置文件，SQL 变换将始终默认可用。

如果您不打算在给定的配置文件中使用 Python 或 R，请考虑移除相关的vector-spark-module包以减少环境。您可以在需要时随时将它们重新添加。

## Python 简介

### Python 变换

Python 变换定义为具有任意数量输入、最多一个输出和非必填一个或多个可视化的 Python 函数。通过将变换的别名引用为函数参数，Code Workbook 将自动将所提到的别名的输出作为变换的输入。有关 Code Workbook 中变换的更多信息，请查阅变换概述文档。

一个简单的 Python 变换示例可以包括一个单一的 PySpark DataFrame 作为输入，使用 PySpark 语法变换数据，并将变换后的 Spark DataFrame 作为输出。

```
Copied!1
2
3
4
5
6
def child(input_spark_dataframe):
    from pyspark.sql import functions as F
    # 过滤DataFrame，将列'A'的值等于'value'的行保留
    return input_spark_dataframe.filter(F.col('A') == 'value') \
        # 新增一列'new_column'，并将该列的值设置为常量2
        .withColumn('new_column', F.lit(2))
```

### Python中Spark和Pandas之间的转换

在Python变换中，Spark和Pandas数据框之间的转换非常简单。

```
Copied!1
2
3
4
# 转换为 PySpark 数据框
spark_df = spark.createDataFrame(pandas_df)
# 转换为 pandas 数据框
pandas_df = spark_df.toPandas()
```

转换为pandas意味着将数据收集到驱动程序。因此，数据的大小受限于Spark模块上可用的驱动程序内存。如果您正在处理大型数据集，您可能需要首先使用Spark筛选和聚合数据，然后将其收集到pandas DataFrame中。

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
from pyspark.sql import functions as F
def filtering_before_pandas(input_spark_dataframe):
    # 使用 PySpark 进行数据过滤
    # 选择"name"和"age"列，并过滤出"age"小于等于18的行
    filtered_spark_df = input_spark_dataframe.select("name", "age").filter(F.col("age") <= 18)

    # 转换为 pandas DataFrame，这会将数据收集到驱动程序节点
    pandas_df = filtered_spark_df.toPandas()

    # 使用 pandas 进行操作
    # 计算年龄的平均值
    mean_age = pandas_df["age"].mean()
    # 计算年龄与平均年龄的差异，并将结果存储在新的列中
    pandas_df["age_difference_to_mean"] = pandas_df["age"] - mean_age

    # 输出结果 DataFrame
    return pandas_df
```

为了在保存后保持排序的pandas DataFrame的顺序，将其保存为具有单个分区的Spark DataFrame：

```
Copied!1
2
3
4
import pyspark.pandas as p

# 将 Pandas DataFrame 转换为 PySpark DataFrame 并合并为一个分区
return p.from_pandas(df).to_spark().coalesce(1)
```

## R简介

### R变换

R变换定义为一个R函数，可以有任意数量的输入，最多一个输出，并且可选择一个或多个可视化。通过将变换的别名作为函数参数引用，Code Workbook会自动将该别名的输出作为变换的输入。有关Code Workbook中变换的更多信息，请查阅变换概述文档。

一个简单的R变换示例可以包括一个父R数据框，使用R变换数据，并有一个R数据框作为输出。

```
Copied!1
2
3
4
5
6
child <- def(r_dataframe) {
    library(tidyverse)
    # 选择col_A和col_B两列，并过滤col_A为TRUE的行，最后添加一个新列new_column，其值为1000
    new_df <- r_dataframe %>% dplyr::select(col_A, col_B) %>% dplyr::filter(col_A == true) %>% dplyr::mutate(new_column=1000)
    return(new_df)
}
```

注意：在R语言中，逻辑值应该是TRUE而不是true，否则可能会导致错误。

### 在Spark和R数据框之间转换

在R变换中，在Spark数据框和R数据框之间转换是直接的：

```
Copied!1
2
3
4
5
# 从 Spark DataFrame 转换为 R 的 data.frame
new_r_df <- SparkR::collect(spark_df)

# 从 R 的 data.frame 转换为 Spark DataFrame
spark_df <- SparkR::as.DataFrame(r_df)
```

请注意，转换为R data.frame意味着将数据收集到驱动程序。因此，数据的大小受Spark模块上可用驱动程序内存的限制。如果您正在处理大型数据集，您可能需要首先使用Spark筛选和聚合数据，然后将其收集到R data.frame中。

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
output_dataset <- function(spark_df) {
    library(tidyverse)

    # 使用 SparkR 选择需要的列
    input_dataset_filtered <- SparkR::select(spark_df, 'column_A', 'column_B')

    # 将 Spark 数据帧转换为 R 的数据帧
    local_df <- SparkR::collect(input_dataset_filtered)

    # 使用 tidyverse 的函数对数据进行转换
    # 过滤 column_A 为 true 的行，并创建一个新列 new_column 赋值为 1000
    local_df <- local_df %>% dplyr::filter(column_A == true) %>% dplyr::mutate(new_column = 1000)

    # 输出 R 数据帧
    return(local_df)
}
```

### R 故障排查

当在 Code Workbook 中导入的数据集被读取为 R 的 data.frame 时，该数据集通过收集到驱动程序从 Spark DataFrame 转换为 R 的 data.frame。

- 您将无法将任意大的数据读取为 R 的 data.frame。数据的大小受 Spark 模块上驱动内存的限制。要处理大数据，请考虑首先将数据集读取为 Spark DataFrame，使用 SparkR 变换数据使其更小，然后调用SparkR::collect()将其转换为 R 的 data.frame。或者，在使用 R 之前，使用 Python 或 SQL 将数据变换为更小的形式。
- 在收集某些数据类型到 R 的 data.frame 时，存在一些已知问题。在大多数情况下，我们在收集时使用一个称为r-arrow ↗的库，这加快了序列化和反序列化。特别是，使用 r-arrow 时，Long、Array、Map、Struct和Datetime类型不可转换。考虑去掉这些列或将它们转换为其他数据类型（例如字符串）。当尝试将这些类型的输入读取为 R 的 data.frame 时，您将在界面中收到警告。
Code Workbook 中的 R 是单线程的，这意味着在同一个 Spark 模块上一次只能运行一个 R 任务。如果您同时启动多个 R 任务，它们将顺序运行；排队的任务将在 Code Workbook 中显示为“正在排队”。

- 如果您有一个长时间运行的任务或任务，其中变换被保存为数据集，我们建议您运行批量搭建。批量搭建将在其自己的 Spark 模块上运行，允许您在共享 Spark 模块的相同工作簿或其他工作簿中继续迭代。
## SQL 简介

Code Workbook 支持的 SQL 变体是Spark SQL ↗。唯一支持的输入和输出类型是 Spark DataFrames。

一个简单的 SQL 变换示例可以在连接键上合并两个输入 DataFrame。

```
Copied!1
2
3
4
5
6
7
SELECT table_b.col_A, table_b.col_B, table_a.*
FROM table_a
JOIN table_b ON table_a.col_C == table_B.col_C
-- 从 table_a 和 table_b 中选择数据。
-- table_b.col_A 和 table_b.col_B 表示选择 table_b 中的 col_A 和 col_B 列。
-- table_a.* 表示选择 table_a 表中的所有列。
-- 使用 JOIN 操作将 table_a 和 table_b 联接在一起，条件是 table_a.col_C 等于 table_B.col_C。
```

要为SQL节点添加父节点，仅在代码中引用别名是不够的。您必须通过选择输入栏来使用UI，或使用**+**按钮创建子节点。
