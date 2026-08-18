来源: https://palantir.com/docs/zh/foundry/building-pipelines/infer-schema/

# 为CSV或JSON文件推断架构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 为CSV或JSON文件推断架构

在Foundry中处理数据集时，如果它们具有架构会更容易。通过在数据集中选择应用架构按钮，Foundry允许您手动为包含CSV或JSON文件的数据集添加架构。应用架构按钮将根据数据的子集自动推断架构。应用架构后，在数据集视图中选择编辑架构以修改列类型或应用其他解析选项，以删除不规则行、更改编码，或添加其他列，例如文件路径、行的字节偏移量、导入时间戳或行号。

基于初始数据集文件静态应用的架构如果数据更改可能会过时。因此，让Spark在半结构化数据的变换管道的第一步动态推断架构可能会很有帮助。

请注意，在每次管道搭建时动态推断架构会有性能成本，因此这种技术应谨慎使用（例如，当架构可能更改时）。

以下是CSV和JSON输入的示例。

Parquet是变换的默认输出文件格式，不允许某些可能出现在自动推断架构中的特殊字符。因此，我们建议您使用下面示例中的sanitize_schema_for_parquet以防止潜在问题。

除了动态架构推断之外，还有许多其他使用场景可以使用SparkSession.read ↗读取所有或部分数据集文件，如下面的示例。如果您的使用场景实际上不需要动态架构推断行为，您应该通过将inferSchema设置为False（这将导致所有列成为字符串）来禁用它，或者通过省略该选项并显式传递架构 ↗。禁用自动架构推断将显著提高性能和一致性，特别是对于增量管道，在增量批次之间不同的架构推断结果可能会引发问题。

### CSV

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
from transforms.api import transform, Input, Output
from transforms.verbs.dataframes import sanitize_schema_for_parquet

@transform(
    output=Output("/Company/sourceA/parsed/data"),  # 输出路径
    raw=Input("/Company/sourceA/raw/data_csv"),  # 输入路径
)
def read_csv(ctx, raw, output):
    filesystem = raw.filesystem()
    hadoop_path = filesystem.hadoop_path
    files = [f"{hadoop_path}/{f.path}" for f in filesystem.ls()]
    df = (
        ctx
        .spark_session
        .read
        .option("encoding", "UTF-8")  # UTF-8 是默认编码
        .option("header", True)  # 第一行作为标题
        .option("inferSchema", True)  # 自动推断数据类型
        .csv(files)  # 读取 CSV 文件
    )
    output.write_dataframe(sanitize_schema_for_parquet(df))  # 写入经过清理的 DataFrame 到输出路径
```

### JSON

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
from transforms.api import transform, Input, Output
from transforms.verbs.dataframes import sanitize_schema_for_parquet

@transform(
    output=Output("/Company/sourceA/parsed/data"),
    raw=Input("/Company/sourceA/raw/data_json"),
)
def read_json(ctx, raw, output):
    filesystem = raw.filesystem()  # 获取原始数据的文件系统对象
    hadoop_path = filesystem.hadoop_path  # 获取Hadoop路径
    files = [f"{hadoop_path}/{f.path}" for f in filesystem.ls()]  # 列出文件系统中的所有文件，构建完整路径列表
    df = (
        ctx
        .spark_session
        .read
        .option("multiline", False)  # 设置multiline选项，False为默认设置；如果每个文件包含一个JSON对象而不是换行分隔的JSON对象，则设置为True
        .json(files)  # 读取JSON文件
    )
    output.write_dataframe(sanitize_schema_for_parquet(df))  # 将DataFrame写入输出，确保模式适合Parquet格式
```

此代码定义了一个数据转换函数read_json，用于从JSON格式的原始数据中读取，并将其转换为适合Parquet存储的格式。主要步骤包括获取文件系统路径、列出文件、读取JSON数据，并应用模式清理以适合Parquet格式存储。
