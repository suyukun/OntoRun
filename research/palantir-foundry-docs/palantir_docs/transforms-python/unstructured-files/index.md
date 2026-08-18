来源: https://palantir.com/docs/zh/foundry/transforms-python/unstructured-files/

# 读取和写入非结构化文件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 读取和写入非结构化文件

非结构化文件访问是一个高级主题。在阅读本页之前，请确保您已熟悉本用户指南中的其他内容。

您可能想在数据变换中访问文件，原因多种多样。如果您想处理非表格式（如XML或JSON）或压缩格式（如gz或zip）的文件，文件访问尤其有用。

transformsPython库允许用户读取和写入Foundry数据集中的文件。transforms.api.TransformInput提供一个只读的FileSystem对象，而transforms.api.TransformOutput提供一个只写的FileSystem对象。这些FileSystem对象允许基于Foundry数据集中文件路径的文件访问，从而抽象掉底层存储。

如果您想在数据变换中访问文件，必须使用transform()装饰器构造您的Transform对象。这是因为FileSystem对象由TransformInput和TransformOutput对象提供。transform()是唯一一个期望其计算函数的输入和输出分别为TransformInput和TransformOutput类型的装饰器。

## 导入文件

文件可以通过手动文件导入或通过数据连接同步到Foundry。结构化和非结构化文件可以导入到Foundry数据集中以便在下游应用中处理。文件也可以作为原始文件上传，而不修改其扩展名。以下示例指的是上传为Foundry数据集的文件，而不是原始文件。

Foundry还具有为上传到数据集的某些文件类型自动推断模式的功能。例如，当导入CSV类型的文件时，可以使用应用模式按钮自动应用模式。了解更多关于手动上传数据的信息。

## 浏览文件

可以使用transforms.api.FileSystem.ls()方法列出数据集中的文件。此方法返回一个transforms.api.FileStatus对象的生成器。这些对象捕获每个文件的路径、大小（以字节为单位）和修改时间戳（自Unix纪元以来的毫秒数）。请考虑以下Transform对象：

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
    hair_eye_color=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_eye_color(hair_eye_color, processed):
    # type: (TransformInput, TransformOutput) -> None
    # 数据转换代码
    pass
```

此代码定义了一个数据转换函数filter_eye_color，它接收输入数据集/examples/students_hair_eye_color并输出到/examples/hair_eye_color_processed。当前函数体内的转换逻辑还未实现。
在您的数据变换代码中，您可以浏览数据集文件：

```
Copied!1
2
3
4
list(hair_eye_color.filesystem().ls())
# 结果: [FileStatus(path='students.csv', size=688, modified=...)]
# 上面的代码列出了文件系统中的文件列表。
# 'students.csv' 是文件的路径，size=688 表示文件的大小为 688 字节，modified=... 表示文件的最后修改时间。
```

还可以通过传递一个glob或正则表达式模式来筛选ls()调用的结果：

```
Copied!1
2
3
4
5
6
7
list(hair_eye_color.filesystem().ls(glob='*.csv'))
# 使用通配符 '*.csv' 来列出所有 CSV 文件
# 结果: [FileStatus(path='students.csv', size=688, modified=...)]

list(hair_eye_color.filesystem().ls(regex='[A-Z]*\.csv'))
# 使用正则表达式 '[A-Z]*\.csv' 来匹配以大写字母开头的 CSV 文件
# 结果: []，没有找到符合条件的文件
```

## 读取文件

可以使用transforms.api.FileSystem.open()方法打开文件。这会返回一个类似 Python 文件流的对象。所有io.open()↗接受的选项也都被支持。注意，文件是作为流被读取的，这意味着不支持随机访问。

由open()方法返回的类似文件流的对象不支持seek或tell方法。因此，不支持随机访问。

考虑以下Transform对象：

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
    hair_eye_color=Input('/examples/students_hair_eye_color'),
    processed=Output('/examples/hair_eye_color_processed')
)
def filter_eye_color(hair_eye_color, processed):
    # type: (TransformInput, TransformOutput) -> None
    # 这个函数用于数据转换，输入是学生的头发和眼睛颜色数据，输出是处理后的数据
    pass
```

在您的数据变换代码中，您可以读取您的数据集文件：

```
Copied!1
2
3
4
with hair_eye_color.filesystem().open('students.csv') as f:
   f.readline()

# 读取CSV文件的第一行，即表头，返回结果为字符串 'id,hair,eye,sex\n'
```

数据流也可以传递到解析库中。例如，我们可以解析一个CSV文件。

```
Copied!1
2
3
4
5
6
import csv
with hair_eye_color.filesystem().open('students.csv') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)  # 跳过CSV文件的第一行（通常是标题行）

# Result: ['id', 'hair', 'eye', 'sex']  # 这是标题行的内容
```

正如之前提到的，您还可以处理非表格格式（例如XML或JSON）或压缩格式（例如gz或zip）的文件。例如，您可以读取压缩文件中的CSV，并使用下面的代码将其内容返回为一个数据框：

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
def process_file(file_status):
        with fs.open(file_status.path, 'rb') as f:
            with tempfile.NamedTemporaryFile() as tmp:
                shutil.copyfileobj(f, tmp)
                tmp.flush()
                with zipfile.ZipFile(tmp) as archive:
                    # 遍历压缩文件中的所有文件名
                    for filename in archive.namelist():
                        with archive.open(filename) as f2:
                            br = io.BufferedReader(f2)
                            tw = io.TextIOWrapper(br)
                            tw.readline() # 跳过每个CSV文件的第一行
                            for line in tw:
                                # 使用yield生成MyRow对象，参数为逗号分隔的值
                                yield MyRow(*line.split(","))
    rdd = fs.files().rdd
    rdd = rdd.flatMap(process_file)
    df = rdd.toDF() # 将RDD转换为DataFrame
```

这段代码主要用于处理压缩文件（如ZIP文件）中的CSV文件。它通过process_file函数读取文件中的内容，并将其转换为RDD，然后将RDD转换为DataFrame。代码中使用了生成器yield来逐行处理CSV数据。

### 随机访问

使用随机访问会导致显著的性能下降。我们建议重写您的代码，使其不依赖于seek方法。如果您仍然想使用随机访问，请参阅下文获取相关信息。

由于open()方法返回流对象，因此不支持随机访问。如果您需要随机访问，可以将文件缓冲到内存或磁盘上。假设hair_eye_color对应于一个TransformInput对象，以下是一些示例：

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
import io
import shutil

# 创建一个字符串IO对象s，用于在内存中读写字符串
s = io.StringIO()

# 打开'students.csv'文件，并将文件内容复制到字符串IO对象s中
with hair_eye_color.filesystem().open('students.csv') as f:
    shutil.copyfileobj(f, s)

# 获取字符串IO对象s的内容
s.getvalue()

# 结果: 'id,hair,eye,sex\n...'
```

这个代码片段的作用是读取一个CSV文件的内容，并将其存储在一个内存中的字符串对象中，以便后续处理。

```
Copied!1
2
3
4
5
6
with hair_eye_color.filesystem().open('students.csv') as f:
    lines = f.read().splitlines()
lines[0]

# 读取CSV文件'students.csv'中的第一行
# Result: 'id,hair,eye,sex'
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
import tempfile
with tempfile.NamedTemporaryFile() as tmp:
    # 打开 students.csv 文件并以二进制读取模式 ('rb') 读取
    with hair_eye_color.filesystem().open('students.csv', 'rb') as f:
        # 将文件内容复制到临时文件 tmp 中
        shutil.copyfileobj(f, tmp)
        # 刷新临时文件以确保数据写入
        tmp.flush()  # shutil.copyfileobj 不会自动刷新缓冲区
    # 以文本读取模式打开临时文件
    with open(tmp.name) as t:
        # 读取临时文件的第一行
        t.readline()

# 结果: 'id,hair,eye,sex\n'
```

## 写入文件

文件的写入方式与使用open()方法类似。该方法返回一个只能写入的Python文件流对象。所有被io.open()↗接受的关键字参数也受到支持。请注意，文件作为流写入，这意味着不支持随机访问。请考虑以下变换对象：
在您的数据变换代码中，可以写入输出文件系统。在以下示例中，您使用内置的Python序列化器pickle模块来持久化模型：

```
Copied!1
2
3
4
5
6
import pickle

# 使用 processed.filesystem().open 打开一个名为 'model.pickle' 的文件，模式为 'wb'（写入二进制）
with processed.filesystem().open('model.pickle', 'wb') as f:
    # 使用 pickle.dump 将模型对象序列化并写入文件
    pickle.dump(model, f)
```

## 分布式处理

与基于DataFrame↗对象的数据变换不同，理解驱动程序和执行器代码与基于文件的变换之间的区别非常重要。计算函数在驱动程序（一台机器）上执行，Spark会自动将DataFrame↗函数分配给执行器（多台机器）进行处理。

要通过文件API受益于分布式处理，我们必须利用Spark来分配计算。为此，我们创建一个FileStatus的DataFrame↗，并将其分配到我们的执行器上。每个执行器上的任务可以打开其被指派的文件并进行处理，结果由Spark聚合。

文件API提供了files()函数，它接受与ls()函数相同的参数，但返回一个FileStatus对象的DataFrame↗。这个DataFrame按文件大小进行分区，以帮助在文件大小不同时平衡计算。可以使用两个Spark配置选项控制分区：

- spark.sql.files.maxPartitionBytes ↗是读取文件时打包到单个分区中的最大字节数。
spark.sql.files.maxPartitionBytes ↗是读取文件时打包到单个分区中的最大字节数。

- spark.sql.files.openCostInBytes ↗是打开文件的估计成本，通过能够在相同时间内扫描的字节数来衡量。这会加到文件大小上以计算文件在分区中使用的总字节数。
spark.sql.files.openCostInBytes ↗是打开文件的估计成本，通过能够在相同时间内扫描的字节数来衡量。这会加到文件大小上以计算文件在分区中使用的总字节数。

要修改这些属性的值，您必须创建一个自定义变换配置文件，并通过configure()装饰器将其应用于您的变换。有关更多信息，请参阅代码库文档中定义变换配置文件的部分。
现在，让我们逐步完成一个示例。假设我们有CSV文件需要解析和连接。我们使用flatMap()↗对每个FileStatus对象应用处理函数。此处理函数必须根据pyspark.sql.SparkSession.createDataFrame()↗生成行。

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
import csv
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType
from transforms.api import transform, Input, Output

@transform(
    processed=Output('/examples/hair_eye_color_processed'),
    hair_eye_color=Input('/examples/students_hair_eye_color_csv'),
)
def example_computation(hair_eye_color, processed):
    def process_file(file_status):
        with hair_eye_color.filesystem().open(file_status.path) as f:
            r = csv.reader(f)
            # 从我们的头部行构造一个pyspark.Row
            header = next(r)
            MyRow = Row(*header)
            for row in r:
                yield MyRow(*row)

    schema = StructType([
        StructField('student_id', StringType(), True),
        StructField('hair_color', StringType(), True),
        StructField('eye_color', StringType(), True),
    ])

    files_df = hair_eye_color.filesystem().files('**/*.csv')
    processed_df = files_df.rdd.flatMap(process_file).toDF(schema)
    processed.write_dataframe(processed_df)
```

虽然可以在不传递模式的情况下调用toDF()，但如果您的文件处理返回零行，则Spark的模式推断将失败，并抛出ValueError: RDD is empty异常。因此，我们建议您始终手动指定模式。
