来源: https://palantir.com/docs/zh/foundry/transforms-python/transforms-sidecar/

# Spark 边车变换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Spark 边车变换

以下文档假定您具备以下先决条件的工作知识：

- 容器化基础设施及容器镜像等概念 ↗。
- PySpark 变换。
Spark 边车变换允许您在利用 Spark 和变换提供的现有基础设施的同时，部署容器化代码。

容器化代码允许您打包任何代码和任何依赖项在 Foundry 中运行。容器化工作流与变换集成，这意味着调度、分支和数据健康都无缝集成。由于容器化逻辑与 Spark 执行器一起运行，您可以根据输入数据扩展容器化逻辑。

简而言之，任何可以在容器中运行的逻辑都可以用于在 Foundry 中处理、生成或消费数据。

如果您熟悉容器化概念，请使用以下部分了解如何使用 Spark 边车变换：

- 架构
- 构建镜像
- 推送镜像
- 编写 Spark 边车变换
了解更多关于 Foundry 中的容器化。

## 架构

Foundry 中的变换可以使用 Spark 驱动程序通过多个执行器分发处理，从而在数据集之间发送和接收数据，如下图所示：

使用@sidecar装饰器（在transforms-sidecar库中提供）注解变换，允许您指定一个容器，该容器在 PySpark 变换中与每个执行器并行启动。用户提供的容器，带有自定义逻辑并与每个执行器一起运行，称为边车容器。

在一个简单的应用案例中，只有一个执行器，数据流如下所示：

如果您编写一个变换，将输入数据集分区到多个执行器中，数据流将如下所示：

每个执行器与边车容器之间的接口是一个共享卷或目录，用于传递以下信息：

- 何时开始执行容器化逻辑。
- 在容器中处理哪些输入数据。
- 从容器中提取哪些输出数据。
- 何时结束容器化逻辑的执行。
这些共享卷通过@sidecar装饰器的Volume参数指定，并将在路径/opt/palantir/sidecars/shared-volumes/下的子文件夹中。

接下来的部分将指导您准备并编写您的 Spark 边车变换。

## 构建镜像

要构建与 Spark 边车变换兼容的镜像，该镜像必须符合镜像要求。该镜像还必须包含下面描述的关键组件，并包含在示例 Docker 镜像中。要构建此示例镜像，您将需要 Python 脚本entrypoint.py。

您需要在本地计算机上安装 Docker，并且必须能够访问dockerCLI 命令（官方文档 ↗）。

### Dockerfile

在本地计算机上的文件夹中，将以下内容放入名为Dockerfile的文件中：

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
FROM fedora:38

# 将 entrypoint.py 文件添加到 /usr/bin/entrypoint 路径
ADD entrypoint.py /usr/bin/entrypoint
# 修改 entrypoint.py 文件为可执行权限
RUN chmod +x /usr/bin/entrypoint

# 创建共享目录
RUN mkdir -p /opt/palantir/sidecars/shared-volumes/shared/
# 更改共享目录的拥有者为用户 5001
RUN chown 5001 /opt/palantir/sidecars/shared-volumes/shared/
# 设置环境变量 SHARED_DIR 指向共享目录
ENV SHARED_DIR=/opt/palantir/sidecars/shared-volumes/shared

# 切换到用户 5001
USER 5001

# 设置容器启动时的默认命令
ENTRYPOINT entrypoint -c "dd if=$SHARED_DIR/infile.csv of=$SHARED_DIR/outfile.csv"
```

此 Dockerfile 用于创建一个基于 Fedora 38 的容器，执行entrypoint.py脚本，脚本默认运行一个dd命令，将共享目录中的infile.csv复制到outfile.csv。

#### 定制化 Dockerfile

您可以搭建自己的 Dockerfile，如上所述，但请确保涵盖以下内容：

- 在第 10 行指定一个数值非 root 用户。这是镜像要求之一，有助于保持适当的安全态势，避免容器被赋予特权执行。
在第 10 行指定一个数值非 root 用户。这是镜像要求之一，有助于保持适当的安全态势，避免容器被赋予特权执行。

- 接下来，在第 6-8 行放置创建共享卷。如上面架构部分所讨论的，位于/opt/palantir/sidecars/shared-volumes/内的子目录中的共享卷是从 PySpark 变换到 sidecar 容器共享输入数据和输出数据的主要方法。第 6 行创建目录。第 7 行确保目录的权限授予创建的用户。第 8 行将此共享目录的路径存储为环境变量，以便在其他地方引用。
接下来，在第 6-8 行放置创建共享卷。如上面架构部分所讨论的，位于/opt/palantir/sidecars/shared-volumes/内的子目录中的共享卷是从 PySpark 变换到 sidecar 容器共享输入数据和输出数据的主要方法。

- 第 6 行创建目录。
- 第 7 行确保目录的权限授予创建的用户。
- 第 8 行将此共享目录的路径存储为环境变量，以便在其他地方引用。
- 最后，在第 3 行向容器添加一个简单的entrypoint脚本，并在第 12 行设置为ENTRYPOINT。这一步至关重要，因为 Spark sidecar 变换不会原生地指示 sidecar 容器在输入数据可用之前等待。此外，sidecar 变换不会指示容器保持活跃并等待输出数据被复制。提供的entrypoint脚本使用 Python 告诉容器在指定逻辑执行之前等待start_flag文件写入共享卷。当指定逻辑完成时，它会在同一目录中写入一个done_flag。容器会等待close_flag写入共享卷，然后才会自行停止并自动清理。
最后，在第 3 行向容器添加一个简单的entrypoint脚本，并在第 12 行设置为ENTRYPOINT。这一步至关重要，因为 Spark sidecar 变换不会原生地指示 sidecar 容器在输入数据可用之前等待。此外，sidecar 变换不会指示容器保持活跃并等待输出数据被复制。提供的entrypoint脚本使用 Python 告诉容器在指定逻辑执行之前等待start_flag文件写入共享卷。当指定逻辑完成时，它会在同一目录中写入一个done_flag。容器会等待close_flag写入共享卷，然后才会自行停止并自动清理。

如上例所示，容器化逻辑使用 POSIX Disk Dump (dd) 工具从共享目录中复制输入的 CSV 文件到存储在同一目录中的输出文件。这个传递给entrypoint脚本的“命令”可以是能够在容器中执行的任何逻辑。

### Entrypoint

在与您的Dockerfile相同的本地文件夹中，将以下代码片段复制到一个名为entrypoint.py的文件中。

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
46
47
48
#!/usr/bin/env python3

import os
import time
import subprocess
from datetime import datetime

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command", type=str, help="model command to execute")
args = parser.parse_args()
the_command = args.command.split(" ")

def run_process(exe):
    "Define a function for running commands and capturing stdout line by line"
    # 定义一个函数用于逐行捕获并运行命令的标准输出
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b"")

# 定义标志文件路径
start_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/start_flag"
done_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/done_flag"
close_flag_fname = "/opt/palantir/sidecars/shared-volumes/shared/close_flag"

# 等待启动标志文件
print(f"{datetime.utcnow().isoformat()}: waiting for start flag")
while not os.path.exists(start_flag_fname):
    time.sleep(1)
print(f"{datetime.utcnow().isoformat()}: start flag detected")

# 执行模型命令，并将输出记录到日志文件中
with open("/opt/palantir/sidecars/shared-volumes/shared/logfile", "w") as logfile:
    for item in run_process(the_command):
        my_string = f"{datetime.utcnow().isoformat()}: {item}"
        print(my_string)
        logfile.write(my_string)
        logfile.flush()
print(f"{datetime.utcnow().isoformat()}: execution finished writing output file")

# 写入完成标志文件
open(done_flag_fname, "w")
print(f"{datetime.utcnow().isoformat()}: done flag file written")

# 等待关闭标志文件出现后，允许脚本结束
while not os.path.exists(close_flag_fname):
    time.sleep(1)
print(f"{datetime.utcnow().isoformat()}: close flag detected. shutting down")
```

## 推送镜像

要推送镜像，请创建一个新的Artifacts仓库，并按照说明将您的镜像标记并推送到相关的Docker仓库。

- 创建一个Artifacts仓库。
- 更改类型为Docker。
- 按照屏幕上的说明生成一个词元。
- 使用以下命令模式搭建您的示例镜像docker build . --tag <container_registry>/<image_name>:<image_tag> --platform linux/amd64，其中：
- container_registry代表您的Foundry实例容器注册表的地址，您可以在将Docker镜像推送到Artifact仓库的说明中的最后一个命令中找到它。
- image_name和image_tag由您自行决定。此示例使用simple_example:0.0.1。
- 从Artifacts仓库复制粘贴说明以推送本地构建的镜像；确保您在最后一个命令中将<image_name>:<image_version>替换为上面镜像构建步骤中使用的image_name和image_version。
## 编写Spark sidecar变换

- 在代码仓库应用中创建一个Python数据变换仓库。
- 在左侧的Libraries选项卡下，添加transforms-sidecar并提交更改。
- 在Settings > Libraries下，添加您的Artifact仓库。
- 编写变换。
以下示例将回顾获取sidecar变换起始所需的关键信息。这两个示例使用相同的实用程序文件，可以在这里找到，您可以将其添加到您的代码仓库并按如下所示导入。

### 示例1：单次执行

下面的变换从transforms-sidecar库中导入了@sidecar装饰器和Volume原语。该变换将这两个项目用于注解，以便每个执行器启动一个simple-example:0.0.1容器实例。每对执行器/sidecar将共享一个位于/opt/palantir/sidecars/shared-volumes/shared的卷。

这个第一个示例启动一个带有一个执行器的容器实例，并遵循下图所示的架构：

然后，变换使用实用程序函数lanch_udf_once来启动user_defined_function的一个实例。该用户定义函数将在一个执行器上运行，并与一个sidecar容器实例通信。用户定义函数将调用导入的实用程序函数来执行以下操作：

- 将输入文件复制到共享目录，以便它们可以被sidecar容器访问。
- 复制启动标志，以便sidecar容器知道要执行。
- 等待容器化逻辑完成。
- 复制由容器化逻辑创建的文件。
- 复制关闭标志，以便容器可以停止并被清理。
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
from transforms.api import transform, Input, Output
from transforms.sidecar import sidecar, Volume
from myproject.datasets.utils import copy_files_to_shared_directory, copy_start_flag, wait_for_done_flag
from myproject.datasets.utils import copy_output_files, copy_close_flag, launch_udf_once


@sidecar(image='simple-example', tag='0.0.1', volumes=[Volume("shared")])
@transform(
    output=Output("<output dataset rid>"),
    source=Input("<input dataset rid>"),
)
def compute(output, source, ctx):
    def user_defined_function(row):
        # 将文件从源目录复制到共享目录
        copy_files_to_shared_directory(source)
        # 发送开始标志，通知容器已接收到所有输入文件
        copy_start_flag()
        # 循环等待，直到写入停止标志或者达到最大时间限制
        wait_for_done_flag()
        # 将输出文件从容器复制到输出数据集
        output_fnames = [
            "start_flag",  # 开始标志文件
            "outfile.csv", # 输出的CSV文件
            "logfile",     # 日志文件
            "done_flag",   # 完成标志文件
        ]
        copy_output_files(output, output_fnames)
        # 写入关闭标志，通知容器已提取数据
        copy_close_flag()
        # 用户自定义函数必须返回一些内容
        return (row.ExecutionID, "success")
    # 此函数启动一个任务，对应一个执行器，并启动一个“sidecar容器”
    launch_udf_once(ctx, user_defined_function)
```

### 示例 2：并行执行

此示例启动了多个 sidecar 容器实例，每个实例处理输入数据的一个子集。然后将信息收集并保存到输出数据集中。此示例更接近下图所示的架构：

以下变换使用不同的实用函数来分区输入数据并将单个文件发送到每个容器，在不同的输入数据块上执行相同的操作。这些实用函数被编写为将输出文件保存为单个文件和表格输出数据集。

您将看到与示例 1 中相同的参数配置在@sidecar装饰器和Volume规范中。

设置了一个@configure标志，以确保每个执行器仅启动一个任务，并且恰好可以启动四个执行器。此配置，再加上输入数据集恰好有四行数据且输入重新分区设置为4的事实，意味着将在四个执行器上启动四个用户定义函数的实例。因此，恰好会启动四个 sidecar 容器实例，并处理输入数据的各自段。

确保您的存储库在设置 > Spark下导入了两个 Spark 配置文件。

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
46
47
48
49
50
51
52
from transforms.api import transform, Input, Output, configure
from transforms.sidecar import sidecar, Volume
import uuid
from myproject.datasets.utils import copy_start_flag, wait_for_done_flag, copy_close_flag
from myproject.datasets.utils import write_this_row_as_a_csv_with_one_row
from myproject.datasets.utils import copy_output_files_with_prefix, copy_out_a_row_from_the_output_csv


@configure(["EXECUTOR_CORES_EXTRA_SMALL", "NUM_EXECUTORS_4"])
@sidecar(image='simple-example', tag='0.0.1', volumes=[Volume("shared")])
@transform(
    output=Output("<first output dataset rid>"),
    output_rows=Output("<second output dataset rid>"),
    source=Input("<input dataset rid>"),
)
def compute(output, output_rows, source, ctx):

    def user_defined_function(row):
        # 将文件从源目录复制到共享目录
        write_this_row_as_a_csv_with_one_row(row)

        # 发送开始标志，让容器知道所有输入文件已准备好。
        copy_start_flag()

        # 循环等待，直到停止标志被写入或者达到最大时间限制。
        wait_for_done_flag()

        # 将输出文件从容器复制到输出数据集
        output_fnames = [
            "start_flag",
            "infile.csv",
            "outfile.csv",
            "logfile",
            "done_flag",
        ]
        # 生成一个随机且唯一的前缀用于文件命名
        random_unique_prefix = f'{uuid.uuid4()}'[:8]
        copy_output_files_with_prefix(output, output_fnames, random_unique_prefix)

        # 从输出CSV中提取一行数据
        outdata1, outdata2, outdata3 = copy_out_a_row_from_the_output_csv()

        # 写入关闭标志，让容器知道数据已被提取。
        copy_close_flag()

        # 用户定义函数必须返回某些内容。
        return (row.data1, row.data2, row.data3, "success", outdata1, outdata2, outdata3)

    # 将源数据集分区为4，并映射到用户定义的函数
    results = source.dataframe().repartition(4).rdd.map(user_defined_function)
    columns = ["data1", "data2", "data3", "success", "outdata1", "outdata2", "outdata3"]
    output_rows.write_dataframe(results.toDF(columns))
```

这段代码实现了一个数据转换过程，使用一个用户定义的函数来处理每一行数据。函数将输入数据写入CSV，触发容器处理，然后提取输出数据并写入新的数据集。

### 示例实用工具

utils.py

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
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
import os
import shutil
import time
import csv
import pyspark.sql.types as T

VOLUME_PATH = "/opt/palantir/sidecars/shared-volumes/shared"
MAX_RUN_MINUTES = 10

def write_this_row_as_a_csv_with_one_row(row):
    """
    将给定行的数据写入CSV文件，文件中只有一行数据。
    """
    in_path = "/opt/palantir/sidecars/shared-volumes/shared/infile.csv"
    with open(in_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['data1', 'data2', 'data3'])
        writer.writerow([row.data1, row.data2, row.data3])

def copy_out_a_row_from_the_output_csv():
    """
    从输出的CSV文件中复制出一行数据。
    """
    out_path = "/opt/palantir/sidecars/shared-volumes/shared/outfile.csv"
    with open(out_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        values = "", "", ""
        for myrow in reader:
            values = myrow[0], myrow[1], myrow[2]
        return values

def copy_output_files_with_prefix(output, output_fnames, prefix):
    """
    将输出文件复制到共享目录，并为文件名加上前缀。
    """
    for file_path in output_fnames:
        output_fs = output.filesystem()
        out_path = os.path.join(VOLUME_PATH, file_path)
        try:
            with open(out_path, "rb") as shared_file:
                with output_fs.open(f'{prefix}_{file_path}', "wb") as output_file:
                    shutil.copyfileobj(shared_file, output_file)
        except FileNotFoundError as err:
            print(err)

def copy_files_to_shared_directory(source):
    """
    将源文件系统中的文件复制到共享目录。
    """
    source_fs = source.filesystem()
    for item in source_fs.ls():
        file_path = item.path
        with source_fs.open(file_path, "rb") as source_file:
            dest_path = os.path.join(VOLUME_PATH, file_path)
            with open(dest_path, "wb") as shared_file:
                shutil.copyfileobj(source_file, shared_file)

def copy_start_flag():
    """
    创建一个启动标志文件，并等待1秒。
    """
    open(os.path.join(VOLUME_PATH, 'start_flag'), 'w')
    time.sleep(1)

def wait_for_done_flag():
    """
    等待完成标志文件出现，检查时间不超过MAX_RUN_MINUTES。
    """
    i = 0
    while i < 60 * MAX_RUN_MINUTES and not os.path.exists(os.path.join(VOLUME_PATH, 'done_flag')):
        i += 1
        time.sleep(1)

def copy_output_files(output, output_fnames):
    """
    将输出文件复制到共享目录。
    """
    for file_path in output_fnames:
        output_fs = output.filesystem()
        out_path = os.path.join(VOLUME_PATH, file_path)
        try:
            with open(out_path, "rb") as shared_file:
                with output_fs.open(file_path, "wb") as output_file:
                    shutil.copyfileobj(shared_file, output_file)
        except FileNotFoundError as err:
            print(err)

def copy_close_flag():
    """
    等待5秒后，创建一个关闭标志文件。
    """
    time.sleep(5)
    open(os.path.join(VOLUME_PATH, 'close_flag'), 'w')  # send the close flag

def launch_udf_once(ctx, user_defined_function):
    """
    使用包含单行的数据框执行用户自定义函数。
    """
    schema = T.StructType([T.StructField("ExecutionID", T.IntegerType())])
    ctx.spark_session.createDataFrame([{"ExecutionID": 1}], schema=schema).rdd.foreach(user_defined_function)
```
