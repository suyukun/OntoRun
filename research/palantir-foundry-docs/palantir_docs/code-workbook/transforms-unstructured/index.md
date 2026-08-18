来源: https://palantir.com/docs/zh/foundry/code-workbook/transforms-unstructured/

# 访问非结构化文件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 访问非结构化文件

除了操作具有定义表模式的Foundry数据集之外，Code Workbook还支持访问数据集中的非结构化文件。这对于分析和变换非结构化数据（如图像和其他类型的媒体）、半结构化格式（如XML或JSON）、压缩格式（如GZ或ZIP文件）或R数据格式（如RDA和RDS）很有用。

## Python中的非结构化文件

### 读取文件

您可以通过将上游数据集读取为Python变换输入来在Python变换中读取文件。此API公开一个FileSystemObject，该Object允许基于Foundry数据集中文件路径的文件访问，从而抽象掉底层存储。了解更多关于FileSystem的信息。。其他信息，包括分支和RID（如变换输入文档中详细说明的），也会暴露。

使用输入助手栏或在输入选项卡中更改输入的类型。

只有导入的数据集和持久化的数据集可以作为Python变换输入读取。未保存为数据集的变换不能作为Python变换输入读取。

没有模式的数据集应自动作为变换输入读取。

#### 示例: 读取ZIP文件中的CSV

例如，以下代码将读取ZIP文件中的CSV，并将CSV内容返回为dataframe。

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
import tempfile
import zipfile
import shutil
import io
from pyspark.sql import Row

# datasetOfZippedFiles 是一个包含单个压缩文件的数据集，该压缩文件包含3个具有相同schema的CSV文件：["id", "name"]。
def sample(datasetOfZippedFiles):
    df = datasetOfZippedFiles
    fs = df.filesystem() # 这是文件系统对象。
    MyRow = Row("id", "name") # 定义行模式
    def process_file(file_status):
        with fs.open(file_status.path, 'rb') as f: # 打开文件状态路径
            with tempfile.NamedTemporaryFile() as tmp: # 创建临时文件
                shutil.copyfileobj(f, tmp) # 将文件内容复制到临时文件中
                tmp.flush() # 刷新临时文件
                with zipfile.ZipFile(tmp) as archive: # 打开压缩文件
                    for filename in archive.namelist(): # 遍历压缩文件中的所有文件名
                        with archive.open(filename) as f2: # 打开每个文件
                            br = io.BufferedReader(f2) # 创建缓冲读取器
                            tw = io.TextIOWrapper(br) # 创建文本包装器
                            tw.readline() # 跳过每个CSV的第一行
                            for line in tw: # 逐行读取
                                yield MyRow(*line.split(",")) # 生成每行的Row对象
    rdd = fs.files().rdd # 获取文件系统的RDD
    rdd = rdd.flatMap(process_file) # 使用flatMap处理每个文件
    df = rdd.toDF() # 将RDD转换为DataFrame
    return df
```

此代码的主要功能是处理包含多个CSV文件的压缩文件，将其解压缩后，读取CSV文件并转换为Spark DataFrame。代码利用了PySpark的RDD和DataFrame API进行数据处理。

### 写入文件

可以写入输出文件系统。这对于写入非表格数据格式（包括图像、PDF、文本文件等）非常有用。

调用Transforms.get_output()来实例化 TransformOutput。了解有关 TransformOutput API 的更多信息。

仅能在保存为数据集的节点中使用 TransformOutput 写入文件。不能在控制台中使用 TransformOutput 写入文件。

一旦实例化了 TransformOutput 并通过调用 filesystem() 或其他方法使用它，返回除 TransformOutput Object 以外的任何东西都将被忽略。

#### 示例：写入文本文件或数据集

以下代码是如何写入文本文件的示例：

```
Copied!1
2
3
4
5
6
7
8
def write_text_file():
    output = Transforms.get_output()  # 获取输出对象
    output_fs = output.filesystem()   # 获取输出对象的文件系统

    # 使用文件系统打开或创建一个名为 'my text file.txt' 的文本文件，以写入模式 ('w') 打开
    with output_fs.open('my text file.txt', 'w') as f:
        f.write("Hello world")  # 写入字符串 "Hello world" 到文件中
        f.close()  # 关闭文件，释放资源（尽管使用 'with' 上下文管理器会自动关闭文件，这行代码可以省略）
```

以下代码是如何编写数据集并指定分区和输出格式的示例。

```
Copied!1
2
3
4
5
def write_dataset(input_dataset):
    # 获取输出对象
    output = Transforms.get_output()
    # 将输入数据集写入输出对象，按"colA"和"colB"列进行分区，以CSV格式输出
    output.write_dataframe(input_dataset, partition_cols = ["colA", "colB"], output_format = 'csv')
```

## R 中的非结构化文件

### 读取文件

您可以通过读取上游数据集作为R变换输入来读取R变换中的文件。TransformInput对象被暴露出来，它允许基于Foundry数据集中文件路径的文件访问。了解有关FileSystemAPI的更多信息。

使用输入帮助栏或在输入选项卡中更改输入类型。

只有导入的数据集和持久化的数据集可以作为R变换输入读取。未保存为数据集的变换不能作为R变换输入读取。

默认情况下，没有架构的数据集应已设置为输入类型R变换输入。

#### 示例：加载RDS

使用下面的代码加载作为导入数据集中文件的RDS。RDS包含一个R data.frame。

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
RDS_reader <- function(RDS_dataset) {
    fs <- RDS_dataset$fileSystem()

    ## 文件名是 test_loading_RDS.rds

    path <- fs$get_path("test_loading_RDS.rds", 'r')  # 获取文件路径，模式为只读
    rds <- readRDS(path)  # 读取 RDS 文件
    return(rds)
}
```

#### 示例：在一组压缩的CSV文件内容上使用rbind

使用以下代码对一组压缩的CSV文件内容进行rbind操作。

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
result <- function(zip_file_with_csvs) {
    fs <- zip_file_with_csvs$fileSystem()

    ## 获取 zip 文件的远程路径（名称）
    zipfile_name <- fs$ls()[[1]]$path

    ## 获取 zip 文件的本地路径
    path <- fs$get_path(zipfile_name, 'r')

    # 列出压缩包中的文件
    zipped_files <- as.list(unzip(path, list = TRUE)$Name)

    # 对列表中的每个元素，返回一个数据框
    list_of_data_frames <- lapply(zipped_files, function(x){read.csv(unz(path, x), header = TRUE, sep = ",")})

    # 将所有的数据框绑定在一起
    rbind_df <- do.call(rbind,list_of_data_frames)

    return(rbind_df)

}
```

此代码定义了一个函数result，它接受一个包含 CSV 文件的 zip 文件对象作为参数。函数将 zip 文件中的 CSV 文件读取为数据框，并将所有数据框合并为一个数据框返回。

### 写入文件

可以写入到输出文件系统。这对于写入非表格数据格式（包括图像、PDF、文本文件等）非常有用。

调用new.output()来实例化一个 TransformOutput。了解更多关于FileSystemAPI 的信息。

只能在保存为数据集的节点中使用 TransformOutput 写入文件。无法在控制台中使用 TransformOutput 写入文件。

#### 示例：将 R data.frame 保存为 RDS 文件

使用下面的代码将 R data.frame 保存为 RDS 文件。

```
Copied!1
2
3
4
5
6
7
8
write_rds_file <- function(r_dataframe) {
    # 创建新的输出对象
    output <- new.output()
    # 获取文件系统对象
    output_fs <- output$fileSystem()
    # 保存R数据框为RDS文件，文件名为"my_RDS_file.rds"
    saveRDS(r_dataframe, output_fs$get_path("my_RDS_file.rds", 'w'))
}
```

#### 示例：将图保存为PDF

使用以下代码将图保存为PDF。

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
plot_pdf <- function() {
    library(ggplot2)
    theme_set(theme_bw())  # 预设黑白主题
    data("midwest", package = "ggplot2")

    # 散点图
    gg <- ggplot(midwest, aes(x=area, y=poptotal)) +
        geom_point(aes(col=state, size=popdensity)) +  # 根据州进行颜色区分，并根据人口密度调整点的大小
        geom_smooth(method="loess", se=F) +  # 添加LOESS平滑曲线，不显示置信区间
        xlim(c(0, 0.1)) +  # 设置x轴范围
        ylim(c(0, 500000)) +  # 设置y轴范围
        labs(subtitle="Area Vs Population",  # 设置副标题、坐标轴标签、主标题和数据来源
            y="Population",
            x="Area",
            title="Scatterplot",
            caption = "Source: midwest")

    output <- new.output()  # 假设这是一个生成输出对象的函数
    output_fs <- output$fileSystem()  # 获取文件系统对象
    pdf(output_fs$get_path("my pdf example.pdf", 'w'))  # 打开一个PDF文件用于写入
    plot(gg)  # 绘制图形到PDF文件
}
```

请注意，上述代码中的new.output()和output$fileSystem()并不是标准的R函数，在实际使用中可能需要定义或修改。如果这些函数没有定义，代码将无法正常工作。

#### 示例：使用连接写入TXT文件

使用下面的代码通过连接写入一个TXT文件。

```
Copied!1
2
3
4
5
6
write_txt_file <- function() {
    output <- new.output() # 创建新的输出对象
    output_fs <- output$fileSystem() # 获取文件系统对象
    conn <- output_fs$open("my file.txt", 'w') # 打开文件“my file.txt”用于写入
    writeLines(c("Hello", "world"), conn) # 将字符串“Hello”和“world”写入文件
}
```

#### 示例：上传TXT文件到远程路径

使用下面的代码将本地路径output.txt的文本文件上传到远程路径output_test.txt。在保存的数据集中，您将看到一个名为output_test.txt的文件。

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
upload <- function() {
    output <- new.output() # 创建一个新的输出对象
    output_fs <- output$fileSystem() # 获取输出对象的文件系统
    fileConn<-file("output.txt") # 打开一个名为 "output.txt" 的文件连接
    writeLines(c("Header 1"), fileConn) # 写入 "Header 1" 到文件中
    close(fileConn) # 关闭文件连接

    output_fs$upload("output.txt", "output_test.txt") # 将 "output.txt" 上传并重命名为 "output_test.txt"
}
```

#### 示例：使用分区写入Spark数据框

使用下面的代码以列A和B分区的方式写入Spark数据框。

```
Copied!1
2
3
4
5
6
write_partitioned_df <- function(spark_df) {
    output <- new.output()

    # 按照 colA 和 colB 列进行分区
    output$write.spark.df(spark_df, partition_cols=list("colA", "colB"))
}
```
