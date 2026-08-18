来源: https://palantir.com/docs/zh/foundry/code-workbook/r-filesystem/

# R 文件系统 API

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# R 文件系统 API

## RTransformInput对象

用于在 Foundry 数据集上进行低级操作的接口。

spark.df()

- 返回输入数据集的pyspark.sql.DataFrame ↗。
data.frame()

- 返回输入数据集的R data.frame ↗。
fileSystem()

- 返回一个FileSystem对象以直接访问FoundryFS。
## RTransformOutput对象

用于在 Foundry 数据集上进行低级写操作的接口。

write.spark.df(df,partition_cols=NULL,bucket_cols=NULL,bucket_count=NULL,sort_by=NULL)

- 将给定的DataFrame ↗写入输出数据集。参数df(pyspark.sql.DataFrame) – 要写入的 PySpark dataframe。partition_cols(List[str], 非必填) - 写入数据时使用的列分区。bucket_cols(List[str], 非必填) - 用于对数据进行分桶的列。如果指定了 bucket_count，则必须指定。bucket_count(int, 非必填) – 桶的数量。如果指定了 bucket_cols，则必须指定。sort_by(List[str], 非必填) - 用于对分桶数据进行排序的列。
将给定的DataFrame ↗写入输出数据集。

| 参数 | df(pyspark.sql.DataFrame) – 要写入的 PySpark dataframe。partition_cols(List[str], 非必填) - 写入数据时使用的列分区。bucket_cols(List[str], 非必填) - 用于对数据进行分桶的列。如果指定了 bucket_count，则必须指定。bucket_count(int, 非必填) – 桶的数量。如果指定了 bucket_cols，则必须指定。sort_by(List[str], 非必填) - 用于对分桶数据进行排序的列。 |
| --- | --- |

- df(pyspark.sql.DataFrame) – 要写入的 PySpark dataframe。
- partition_cols(List[str], 非必填) - 写入数据时使用的列分区。
- bucket_cols(List[str], 非必填) - 用于对数据进行分桶的列。如果指定了 bucket_count，则必须指定。
- bucket_count(int, 非必填) – 桶的数量。如果指定了 bucket_cols，则必须指定。
- sort_by(List[str], 非必填) - 用于对分桶数据进行排序的列。
write.data.frame(rdf)

- 将给定的R data.frame ↗写入输出数据集。
fileSystem()

- 返回一个FileSystem对象以直接访问FoundryFS。
## RFileSystem对象

ls(glob=NULL,regex='.*',show_hidden=FALSE)

- 列出与给定模式（glob或regex）匹配的所有文件，基于数据集的根目录。参数glob(str,非必填) – 一个 Unix 文件匹配模式。也支持 globstar。regex(str,非必填) – 用于匹配文件名的正则表达式模式。show_hidden(bool,非必填) – 包括隐藏文件，即以 ‘.’ 或 ‘_’ 开头的文件。返回文件状态命名元组（路径、大小、修改时间）的 R 数组 - 逻辑路径、文件大小（字节）、修改时间戳（自1970年1月1日 UTC以来的毫秒数）
列出与给定模式（glob或regex）匹配的所有文件，基于数据集的根目录。

| 参数 | glob(str,非必填) – 一个 Unix 文件匹配模式。也支持 globstar。regex(str,非必填) – 用于匹配文件名的正则表达式模式。show_hidden(bool,非必填) – 包括隐藏文件，即以 ‘.’ 或 ‘_’ 开头的文件。 |
| --- | --- |
| 返回 | 文件状态命名元组（路径、大小、修改时间）的 R 数组 - 逻辑路径、文件大小（字节）、修改时间戳（自1970年1月1日 UTC以来的毫秒数） |

- glob(str,非必填) – 一个 Unix 文件匹配模式。也支持 globstar。
- regex(str,非必填) – 用于匹配文件名的正则表达式模式。
- show_hidden(bool,非必填) – 包括隐藏文件，即以 ‘.’ 或 ‘_’ 开头的文件。
open(path,open='r',disk_optimal=FALSE,encoding=default)

- 以给定模式打开一个 FoundryFS 文件。参数path(str) – 文件在数据集中的逻辑路径。（远程路径）open(str) - 打开连接的模式的描述。disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。返回一个 R 连接对象
以给定模式打开一个 FoundryFS 文件。

| 参数 | path(str) – 文件在数据集中的逻辑路径。（远程路径）open(str) - 打开连接的模式的描述。disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。 |
| --- | --- |
| 返回 | 一个 R 连接对象 |

- path(str) – 文件在数据集中的逻辑路径。（远程路径）
- open(str) - 打开连接的模式的描述。
- disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。
- encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。
get_path(path,open='r',disk_optimal=FALSE,encoding=default)

- 对于给定的 FoundryFS（远程）路径，返回本地临时路径。参数path(str) – 文件在数据集中的逻辑路径。（远程路径）open(str) - 打开连接的模式的描述。disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。返回str
对于给定的 FoundryFS（远程）路径，返回本地临时路径。

| 参数 | path(str) – 文件在数据集中的逻辑路径。（远程路径）open(str) - 打开连接的模式的描述。disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。 |
| --- | --- |
| 返回 | str |

- path(str) – 文件在数据集中的逻辑路径。（远程路径）
- open(str) - 打开连接的模式的描述。
- disk_optimal(bool,非必填) – 控制 FoundryFileSystem 如何处理文件输入/输出。
- encoding(str,非必填) - 默认为 R 语言默认值（UTF-8）。
upload(local_path,remote_path)

- 将文件从本地路径上传到远程路径。仅写入。参数local_path(str) – 要上传的文件的本地路径。remote_path(str) - 文件在数据集中的逻辑路径。返回None
将文件从本地路径上传到远程路径。仅写入。

| 参数 | local_path(str) – 要上传的文件的本地路径。remote_path(str) - 文件在数据集中的逻辑路径。 |
| --- | --- |
| 返回 | None |

- local_path(str) – 要上传的文件的本地路径。
- remote_path(str) - 文件在数据集中的逻辑路径。
## 高级主题:disk_optimal设置

在FileSystem方法open()和get_path()中，disk_optimal参数控制文件输入和输出（i/o）的处理方式。

默认情况下，disk_optimal在open()和get_path()中设置为FALSE。在此模式下，文件保证在被访问之前被下载。

如果选择将disk_optimal设置为TRUE，文件将在代码执行时同时下载。临时本地路径必须通过fifo()打开才能正确读取。注意并非所有库都支持读取此类文件。

当您读取的文件非常大时，可以选择将disk_optimal设置为TRUE。

例如，假设我们有一个非常大的 txt 文件，我们只想读取前 10 行。使用以下代码仅打印前 10 行，而无需读取整个文件。

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
disk_optimal_example<- function(large_txt_file) {
    fs <- large_txt_file$fileSystem()

    ## 使用 fifo() 打开一个连接
    ## 文本文件名为 large_txt_file.txt
    ## 使用 disk_optimal 参数以优化磁盘读取性能
    conn <- fs$open("large_txt_file.txt", "r", disk_optimal = TRUE)

    A <- readLines(conn, n = 10)
    print(A)
    return(NULL)
}
```

如果您想使用 R TransformOutput 写入文件然后读取，则必须将disk_optimal设置为 false。
