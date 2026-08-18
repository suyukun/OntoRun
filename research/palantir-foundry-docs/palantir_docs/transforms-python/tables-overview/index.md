来源: https://palantir.com/docs/zh/foundry/transforms-python/tables-overview/

# 虚拟表概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 虚拟表概述

虚拟表允许您在支持的数据平台中查询和写入表，而无需将数据存储在Foundry中。

您可以在Python变换中通过transforms-tables库与这些表进行交互。

## 先决条件

要从Python变换中与虚拟表交互，您必须：

- 升级您的Python代码库到最新版本。
- 从库选项卡安装transforms-tables。
## API概述

Python风格的虚拟表API提供TableInput和TableOutput类型，以便与虚拟表交互。

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
from transforms.api import transform
from transforms.tables import TableInput, TableOutput, TransformTableInput, TransformTableOutput

@transform(
    source_table=TableInput("ri.tables.main.table.1234"),  # 输入表，源数据表的标识符
    output_table=TableOutput("ri.tables.main.table.5678"), # 输出表，目标数据表的标识符
)
def compute(source_table: TransformTableInput, output_table: TransformTableOutput):
    ...  # 正常的transforms API操作
```

在 Python 变换中引用的表格不需要来自相同的来源，甚至不需要来自相同的平台。

上述示例依赖于变换中指定的表格已经存在于您的 Foundry 环境中。如果不是这种情况，您可以配置输出虚拟表在检查过程中创建，就像数据集输出一样。这需要额外的配置以指定表格应该存储的来源和位置。

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
from transforms.api import transform
from transforms.tables import TableInput, TableOutput, TransformTableInput, TransformTableOutput, SnowflakeTable

@transform(
    source_table=TableInput("ri.tables.main.table.1234"),  # 这是输入表的标识符
    output_table=TableOutput(
        "/path/to/new/table",  # 这是输出表的路径
        # 必须指定要创建表的数据连接源和表的标识符/位置
        "ri.magritte..source.1234",  # 指定数据源标识符
        SnowflakeTable("database", "schema", "table"),  # 指定Snowflake数据库、模式和表
    ),
)
def compute(source_table: TransformTableInput, output_table: TransformTableOutput):
    ...  # 正常的transforms API操作
```

这个代码片段中定义了一个数据转换函数compute，它从指定的输入表中获取数据，并将结果输出到指定的输出表。输入和输出表都是通过TableInput和TableOutput进行配置的，后者还需要指定数据连接源和表的位置信息。SnowflakeTable用于指定目标数据库、模式和表名。
创建后，可以从TableOutput中移除源和表元数据的额外配置，以使其更简洁。一旦创建了虚拟表，就无法更改源或位置。修改源或位置将导致检查失败。

可用的Table子类有：

- BigQueryTable(project: str, dataset: str, table: str)
- DeltaTable(path: str)
- FilesTable(path: str, format: FileFormat)
- IcebergTable(table: str, warehouse_path: str)
- SnowflakeTable(database: str, schema: str, table: str)
您必须根据所连接的源类型使用适当的类。
