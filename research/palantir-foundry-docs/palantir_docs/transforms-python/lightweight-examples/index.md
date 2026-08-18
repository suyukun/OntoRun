来源: https://palantir.com/docs/zh/foundry/transforms-python/lightweight-examples/

# 轻量级变换示例

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 轻量级变换示例

除了速度之外，轻量级变换还具有多功能性。轻量级变换不对用户选择的计算引擎做出假设。以下内容展示了如何利用各种计算引擎，同时依赖于轻量级API和变换API。之后，我们将演示通过使用我们自己的包含必要环境的Docker镜像来应用高度自定义的非Python数据处理应用程序。

## 现代单节点计算引擎

以下所有集成的基本原则是我们可以以多种格式访问我们的表格Foundry数据集，例如Pandas DataFrame、Arrow Table、Polars DataFrame，甚至是原始Parquet或CSV文件。这在轻量级API中也有展示。当尝试将内存中的表保存到Foundry时，我们可以将其以我们读取的任何格式传递。

### 使用Ibis

大多数现代计算引擎都采用解耦数据系统的概念，因此在行业标准的开源软件上运行。内存中存储表的事实标准是Arrow ↗。首先，我们将使用Ibis ↗（使用DuckDB后端），它内部使用Arrow格式。在这种情况下，我们可以通过my_input.arrow()调用将Foundry数据集读取为pyarrow.Table ↗对象，进行变换，然后使用my_output.write_table(...)将变换后的对象写回Foundry。请考虑以下示例代码片段：

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
import ibis
from transforms.api import lightweight, transform, Output, Input

@lightweight
@transform(my_input=Input('my-input'), my_output=Output('my-output'))
def my_ibis_transform(my_input, my_output):
    ibis_client = ibis.duckdb.connect(':memory:')  # 连接到 DuckDB 的内存数据库
    # 将 Foundry 数据集作为 pyarrow.Table 对象获取
    table = ibis_client.read_in_memory(my_input.arrow())
    # 执行数据转换
    results = (
        table
        .filter(table['name'].like('John%'))  # 筛选 'name' 列以 'John' 开头的行
        .execute()
    )
    # 将 pyarrow.Table 对象保存到 Foundry 数据集中
    my_output.write_table(results)
```

- ibis：一个用于大数据处理的 Python 库，提供了一种高层次的表达方式来进行数据分析。
- duckdb：一个内存数据库管理系统，适合用于分析数据处理。
- pyarrow.Table：Apache Arrow 中的一个数据结构，用于高效的列式数据处理。
- like：用于模式匹配的 SQL 操作符，这里用于筛选出名字以 "John" 开头的数据。
- Foundry：Palantir Foundry 是一个企业数据管理平台，允许用户在一个统一的环境中管理、分析和可视化数据。
### 使用 Apache DataFusion 和 DuckDB

有时候，直接将数据集的原始底层文件传递给我们的计算引擎，而省去数据反序列化步骤，会更为简单。我们可以通过调用my_input.path()来获取磁盘上文件的路径（这些文件会按需下载）。当涉及将原始文件写回 Foundry 时，我们需要注意两个限制：

- 通过此 API，只有 Parquet 文件可以存储在 Foundry 数据集中。
- 文件必须放置在my_output.path_for_write_table的值所指定的文件夹中。
当这两个条件都满足时，我们可以通过以下方式调用write_table，将数据写入此文件夹：my_output.write_table(my_output.path_for_write_table)。要查看此操作的实际应用，请参考以下演示如何在平台内使用DataFusion ↗的代码片段。

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
import datafusion
from datafusion import lit
from datafusion.functions import col, starts_with
from transforms.api import lightweight, transform, Output, Input

# 定义一个轻量级的转换函数，输入为'my-input'，输出为'my-output'
@lightweight
@transform(my_input=Input('my-input'), my_output=Output('my-output'))
def my_datafusion_transform(my_input, my_output):
    # 创建一个Datafusion的Session上下文
    ctx = datafusion.SessionContext()

    # 读取输入路径下的Parquet文件，加载为Datafusion表
    table = ctx.read_parquet(my_input.path())

    # 过滤表中'name'列以"John"开头的行，并将结果写入输出
    my_output.write_table(
        table
        .filter(starts_with(col("name"), lit("John")))  # 使用starts_with函数进行过滤
        .to_arrow_table()  # 将Datafusion表转换为Arrow表
    )
```

我们也可以对DuckDB ↗使用相同的方法，如以下代码片段所示。请注意，我们必须处理从文件夹中读取所有Parquet 文件。

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
import duckdb
from transforms.api import lightweight, transform, Output, Input

# 定义一个轻量级转换函数，使用装饰器指定输入和输出
@lightweight
@transform(my_input=Input('my-input'), my_output=Output('my-output'))
def my_duckdb_transform(my_input, my_output):
    # 使用 DuckDB 在内存中连接数据库
    duckdb.connect(database=':memory:').execute(f"""
        COPY
        (
            SELECT *
            FROM parquet_scan('{my_input.path()}/**/*.parquet')  -- 扫描输入路径下所有 Parquet 文件
            WHERE Name LIKE 'John%'  -- 过滤名字以 'John' 开头的记录
        )
        TO '{my_output.path_for_write_table}'
        (FORMAT 'parquet', PER_THREAD_OUTPUT TRUE)  -- 输出为 Parquet 格式，并开启多线程并行写入以优化性能
    """)

    # 将转换后的数据写入输出表
    my_output.write_table(my_output.path_for_write_table)
```

### 使用 cuDF

您还可以通过使用pandas.DataFrame来实现集成。以下代码片段展示了在轻量级变换中使用cuDF ↗的实例。这将基本上在可能的情况下，以高度并行化的方式在 GPU 上运行您的 Pandas 代码。

```
Copied!1
2
3
4
5
6
7
8
@lightweight(gpu_type='NVIDIA_T4', cpu_cores=4, memory_gb=32)
@transform(my_input=Input('my-input'), my_output=Output('my-output'))
def my_cudf_transform(my_input, my_output):
    import cudf  # 仅在运行时导入CUDF，而非CI过程中
    df = cudf.from_pandas(my_input.pandas()[['name']])  # 将输入数据转换为CUDF数据框，选择'name'列
    filtered_df = df[df['name'].str.startswith('John')]  # 过滤出'name'列以'John'开头的行
    sorted_df = filtered_df.sort_values(by='name')  # 对过滤后的数据按'name'列进行排序
    my_output.write_table(sorted_df)  # 将排序后的数据写入输出
```

这个代码片段定义了一个使用CUDF的轻量级数据转换函数，结合使用GPU和多核CPU进行高效计算。在函数内部，数据被转换、过滤和排序，最后写入输出。

上述代码片段假设您的Foundry注册配备了NVIDIA T4 GPU，并通过资源队列提供给您的项目。

## 自带容器工作流

大多数计算都可以简单地用Python表达。然而，有些应用案例可能需要依赖于非Python的执行引擎或脚本。例如，可能是一个F#应用程序、一个古老的VBA脚本，甚至只是一个即将弃用的Python版本。使用自带容器（BYOC）工作流时，可能性是无限的。简而言之，BYOC允许在本地创建一个包含所有特定依赖项和/或二进制文件的Docker镜像，然后在此镜像之上运行一个轻量级的变换。

以下是在Foundry中运行COBOL变换的示例。为简化起见，此示例在变换内编译COBOL程序。或者，您可以预先编译程序并将二进制可执行文件复制到Docker镜像中。首先，启用容器化工作流，然后按照这些镜像要求在本地构建Docker镜像。

以下是一个最小的Dockerfile示例：

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
FROM ubuntu:latest

# 更新包管理器并安装必要的软件包
RUN apt update && apt install -y coreutils curl sed build-essential gnucobol

# 创建一个新的用户，用户ID为5001
RUN useradd --uid 5001 user
# 切换到新创建的用户
USER 5001
```

请注意，轻量级运行不需要在Docker镜像中安装Python。

然后，搭建镜像并上传到Foundry。为此，创建一个Artifacts存储库并按照这些说明为我们的镜像打标签并推送。在此示例中，镜像被标记为名称my-image和版本0.0.1。在编写BYOC轻量级变换之前的最后一步是将此Artifacts存储库作为本地支持存储库添加到代码存储库中。

下面的示例考虑了一个COBOL脚本，该脚本生成一个CSV文件，其源代码位于我的代码存储库内的resources/data_generator.cbl。

最后一步是编写一个轻量级变换，允许数据处理程序连接到Foundry。下面的代码片段演示了如何通过Python API访问数据集，同时包含镜像中附带的任意可执行文件。要调用COBOL可执行文件，请使用Python标准库的函数（在本例中，os.system(...)）。

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
from transforms.api import Output, transform, lightweight

@lightweight(container_image='my-image', container_tag='0.0.1')
@transform(my_output=Output('my-output'))
def compile_cobol_data_generator(my_output):
    """展示如何引入难以通过Conda获取的依赖项。"""
    # 编译Cobol程序
    # （src文件夹中的所有内容在 $USER_WORKING_DIR/user_code 中可用）
    os.system("cobc -x -free -o data_generator $USER_WORKING_DIR/user_code/resources/data_generator.cbl")

    # 运行程序以创建并填充data.csv文件
    os.system('$USER_WORKING_DIR/data_generator')

    # 将结果存储到Foundry中
    my_output.write_table(pd.read_csv('data.csv'))
```

这段代码演示了如何使用指定的Docker容器来编译和运行Cobol程序，并将生成的数据存储到Foundry中。通过使用lightweight装饰器，我们可以在运行时带入特定的依赖环境，比如这里用到的Cobol编译器，这在Conda中可能比较难以获取。

预览不支持BYOC工作流。

使用搭建按钮最终将从我们的Docker镜像实例化一个容器并调用指定的命令。资源分配、日志记录、与Foundry的通信、权限执行和可审计性都将自动处理。

## 增量工作流

在foundry-transforms-lib-python库的0.556.0版本中支持增量轻量级变换。

要编写增量轻量级变换，请使用@lightweight装饰器，后跟@incremental装饰器。以下代码展示了一个示例：

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
from transforms.api import incremental, Input, lightweight, Output, transform

# 标记函数为轻量级变换
@lightweight()
# 标记函数为增量变换，并且要求输入必须为增量数据
@incremental(require_incremental=True)
# 定义数据转换函数，指定输入和输出
@transform(my_input=Input("my-input"), my_output=Output('my-output'))
def my_incremental_transform(my_input, my_output):
    # 将增量数据写入输出
    my_output.write_pandas(my_input.pandas(mode="added"))
```

## 文件处理工作流

轻量级变换可以处理没有模式的数据集的文件。需要使用foundry-transforms-lib-python库来实现。

要编写一个处理没有模式的数据集文件的轻量级变换，可以使用@lightweight装饰器，并通过my_input.filesystem().ls()列出文件。.filesystem().ls()语句适用于没有模式的数据集，但.path()、.pandas()、.polars()、.arrow()和.filesystem().files()语句仅适用于有模式的数据集。

### 代码示例: 文件处理的轻量级变换

以下代码展示了一个处理没有模式的数据集文件的轻量级变换示例。

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
from transforms.api import incremental, Input, lightweight, Output, transform

@lightweight()
@incremental()
@transform(my_input=Input("my-input"), my_output=Output('my-output'))
def my_incremental_transform(my_input, my_output):
    files = [f.path for f in my_input.filesystem().ls()]  # 获取输入目录中所有文件的路径
    fs = my_input.filesystem()
    polars_dataframes = []

    for curr_file_as_row in files:
        # 访问文件
        with fs.open(curr_file_as_row, "rb") as f:  # 这里的file_path应该是curr_file_as_row
            # <在此处处理文件>
            # 将处理后的数据作为DataFrame附加到polars_dataframes列表中

    # 将所有DataFrame合并为一个
    combined_df = union_polars_dataframes(polars_dataframes)
    my_output.write_table(combined_df)  # 将合并后的DataFrame写入输出
```

注意：

- 在with fs.open(file_path, "rb") as f:中，file_path应该替换为curr_file_as_row，以确保正确访问当前文件。
- 使用my_output.write_table而不是out.write_table来写入输出，这样才能正确地将合并后的 DataFrame 输出。
以下代码展示了解析Excel文件的示例：
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
from transforms.api import transform, Input, Output, lightweight
import tempfile
import shutil
import polars as pl
import pandas as pd


@lightweight()
@transform(
    my_output=Output("/path/tabular_output_dataset"),
    my_input=Input("/path/input_dataset_without_schema"),
)
def compute(my_input, my_output):
    # 列出输入数据集中所有的文件
    files = [f.path for f in my_input.filesystem().ls()]

    # 解析每个文件
    # 使用提供的文件系统打开指定路径的Excel文件
    def read_excel_to_polars(fs, file_path):
        with fs.open(file_path, "rb") as f:
            with tempfile.TemporaryFile() as tmp:
                # 从源数据集复制文件到本地文件系统
                shutil.copyfileobj(f, tmp)
                tmp.flush()  # shutil.copyfileobj 不会自动刷新

                # 读取Excel文件（此时文件可被定位）
                pandas_df = pd.read_excel(tmp)
                # 将可能的整数列转换为字符串列
                pandas_df = pandas_df.astype(str)
                # 将pandas数据框转换为polars数据框
                return pl.from_pandas(pandas_df)

    fs = my_input.filesystem()
    polars_dataframes = []

    for curr_file_as_row in files:
        # print(curr_file_as_row)  # 打印当前文件路径
        polars_dataframes.append(read_excel_to_polars(fs, curr_file_as_row))

    def union_polars_dataframes(dfs):
        return pl.concat(dfs)

    # 将所有数据框合并为一个
    combined_df = union_polars_dataframes(polars_dataframes)

    my_output.write_table(combined_df)
```

代码解释：

- 该代码从指定输入路径中读取Excel文件，将其转换为Polars数据框，并将所有读取的数据框合并为一个整体数据框，最后将合并后的数据框写入到指定的输出路径。
- 使用了tempfile和shutil库将文件从远程系统复制到本地临时文件中进行处理。
- pandas用于读取Excel文件，polars用于高效的数据操作和合并。
## 下一步

要了解更多关于轻量级变换的信息，可以从您的Foundry部署的Reference ResourcesMarketplace商店安装Lightweight examplesMarketplace产品，或者导航到变换API参考。
