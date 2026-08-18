来源: https://palantir.com/docs/zh/foundry/code-repositories/prepare-datasets-download/

# 准备数据集以供下载

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 准备数据集以供下载

以下导出过程是一个高级工作流程，仅在无法通过Code Repositories中的操作菜单或从其他Foundry应用程序导出直接从Foundry界面下载数据时执行。

本指南解释了如何使用Code Repositories中的变换来准备CSV以供下载。在某些情况下，可能需要从Foundry中以CSV格式下载数据样本，而不使用Foundry界面中的操作菜单并选择下载为CSV。在这些情况下，我们建议在搭建期间准备导出文件，作为使用操作菜单的替代方案。

## 准备数据

准备CSV以供下载的第一步是创建一个经过筛选和清理的数据集。我们建议执行以下步骤：

- 确保数据样本可以导出并遵循数据导出控制规则。具体来说，您应该验证导出是否符合您组织的数据治理政策。
- 筛选数据，使其尽可能小以满足必要的目标。通常，CSV格式数据的未压缩大小应小于默认的HDFS块大小（128 MB）。为此，您应仅选择必要的列，并尽量减少行数。您可以通过筛选特定值或随机抽取任意数量的行（如1000行）来减少行数。
- 更改列类型为字符串。由于CSV格式缺乏模式（未强制的列类型和标签），建议将所有列转换为字符串。这对时间戳列尤其重要。
以下来自纽约出租车数据集的示例代码可能有助于您准备数据以供下载：

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
def prepare_input(my_input_df):
    from pyspark.sql import functions as F

    # 定义过滤条件的列和值
    filter_column = "vendor_id"
    filter_value = "CMT"
    # 按照过滤条件筛选数据
    df_filtered = my_input_df.filter(filter_value == F.col(filter_column))

    # 设定采样的目标行数
    approx_number_of_rows = 1000
    # 计算采样比例
    sample_percent = float(approx_number_of_rows) / df_filtered.count()

    # 根据采样比例对数据进行采样
    df_sampled = df_filtered.sample(False, sample_percent, seed=0)

    # 选择重要的列进行输出
    important_columns = ["medallion", "tip_amount"]

    # 将重要的列转换为字符串类型并返回
    return df_sampled.select([F.col(c).cast(F.StringType()).alias(c) for c in important_columns])
```

使用类似的逻辑和Spark概念，您也可以在其他Spark API中实现准备工作，如SQL或Java。

## 设置输出格式和合并分区

一旦数据准备好以导出，可以将输出格式设置为CSV。通过将输出格式设置为CSV，数据的底层格式将在Foundry中保存为CSV文件。您也可以将输出格式设置为JSON、ORC、Parquet或文本。最后，为了将结果存储在单个CSV文件中，您需要将数据合并为单个分区以便下载。

### Python

以下示例代码展示了如何在Python中合并数据：

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
from transforms.api import transform, Input, Output

@transform(
     output=Output("/path/to/python_csv"),  # 输出数据路径
     my_input=Input("/path/to/input")       # 输入数据路径
)
def my_compute_function(output, my_input):
     # 将输入数据的DataFrame重新分区为1个分区并写入到CSV文件中
     output.write_dataframe(my_input.dataframe().coalesce(1), output_format="csv", options={"header": "true"})
     # options={"header": "true"} 表示在CSV文件中包含表头
```

### SQL

以下示例代码展示了如何在SQL中合并数据：

```
Copied!1
CREATE TABLE `/path/to/sql_csv` USING CSV AS SELECT /*+ COALESCE(1) */ * FROM `/path/to/input`
```

这段代码用于在Spark SQL中创建一个表：

- CREATE TABLE/path/to/sql_csv``: 创建一个新表，表的数据将存储在指定的路径/path/to/sql_csv中。
- USING CSV: 指定表的数据格式为CSV。
- AS SELECT /*+ COALESCE(1) */ * FROM/path/to/input``: 通过从指定的输入路径/path/to/input中选择所有数据来填充表。/*+ COALESCE(1) */是一个优化提示，建议Spark在执行过程中将分区数缩减为1，以减少小文件的生成。
- /*+ COALESCE(1) */是一个优化提示，建议Spark在执行过程中将分区数缩减为1，以减少小文件的生成。
```
请注意，路径格式如 `/path/to/sql_csv` 和 `/path/to/input` 是占位符，在实际应用中需要替换为实际的文件路径。
查看[官方 Spark 文档 ↗](https://spark.apache.org/docs/3.1.1/api/java/org/apache/spark/sql/DataFrameWriter.html)以获取更多 CSV 生成选项。

## 访问文件以下载

一旦数据集搭建完成，导航到数据集页面的**详情**选项卡。CSV 应显示为可供下载。

![CSV 可供下载](../../foundry-docs/code-repositories/media/csv_download.png)
```
