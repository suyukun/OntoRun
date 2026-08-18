来源: https://palantir.com/docs/zh/foundry/code-workbook/workbooks-input-output-types/

# 输入和输出

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 输入和输出

## 输入类型和转换

Code Workbook允许您指定一个变换将接收的每个输入的类型。您可以通过选择变换名称下拉菜单来设置输入类型：

如果请求的输入类型与实际输入类型不匹配，Code Workbook会执行必要的转换。

例如：如果transform_A的输出是一个pandas dataframe，而其派生变换transform_B手动将输入设置为Spark dataframe，Code Workbook会将pandas dataframe转换为请求的Spark dataframe。如果transform_C的输出是一个pandas dataframe，而其派生transform_D请求其输入为R data.frame，Code Workbook会先将pandas dataframe转换回Spark dataframe，然后再转换为R data.frame。

以下流程图提供了Code Workbook如何处理输入类型之间转换的概述：

## 输入和输出限制

### 输出类型

一个Code Workbook变换可以有任意数量的输入，每个输入可以配置不同的输入类型。然而，一个变换只能有一个输出。目前不支持多个输出。

Code Workbook仅允许根据语言在其变换中使用某些类型的输出：

| 语言 | 允许的输出类型 |
| --- | --- |
| Python | Spark dataframe, Pandas dataframe, FoundryObject, None |
| R | R data.frame, FoundryObject, NULL |
| SQL | Spark dataframe |

如果一个变换返回的类型不是上述列出的类型之一，Code Workbook将返回不支持的类型错误。

Code Workbook允许您运行具有None/NULL返回值的变换，但下游变换将不接受None/NULL作为输入。

### Python输入类型

默认情况下，Python变换将接受其输入为Spark dataframes。您可以通过选择变换名称下拉菜单来设置输入类型，Code Workbook会负责将上游输出转换为所需的输入类型：

Python变换中支持以下输入类型：

| 输入类型 | 描述 |
| --- | --- |
| Spark dataframe (default) | pySpark dataframe的类pyspark.sql.dataframe.DataFrame |
| Pandas dataframe | Pandas dataframe的类pandas.core.frame.DataFrame |
| Python transform input (仅在输入“保存为数据集”时可用) | 允许直接文件访问输入的FileSystemobject。请参阅访问非结构化文件文档。 |
| Object | 一个Foundry模型Object允许您执行建模工作流。请参阅模型文档。 |

### R输入类型

默认情况下，R变换将接受其输入为R data.frames。您可以通过选择变换名称下拉菜单来设置输入类型，Code Workbook会将上游输出转换为所需的输入类型：

R变换中支持以下输入类型：

| 输入类型 | 描述 |
| --- | --- |
| Spark dataframe | SparkR dataframe的类SparkDataFrame |
| R data.frame (default) | R dataframe的类data.frame |
| R transform input (仅在输入“保存为数据集”时可用) | 允许直接文件访问输入的FileSystemobject。请参阅访问非结构化文件文档。 |
| Object | 一个Foundry模型Object允许您执行建模工作流。请参阅模型文档。 |

### SQL输入和输出类型

SQL变换中唯一支持的输入和输出类型是Spark dataframes。dataframe可以在SQL中作为表读取。
