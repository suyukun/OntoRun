来源: https://palantir.com/docs/zh/foundry/transforms-python/transforms-python-api/

# 变换 Python API

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换 Python API

变换 Python API 提供类和装饰器以构建一个Pipeline。此页面包含关于可用函数的信息；您还可以阅读更多关于类的信息。

| 函数 | 描述 |
| --- | --- |
| configure([profile]) | 装饰器，用于修改变换的配置。 |
| incremental([require_incremental, ...]) | 装饰器，将输入和输出转换为它们的 transforms.api.incremental 对应项。 |
| lightweight([cpu_cores, memory_mb, memory_gb, gpu_type, container_image, container_tag, container_shell_command]) | 装饰器，使被装饰的变换在容器变换上运行。 |
| transform(ios) | 将计算函数包装为一个Transform对象。 |
| transform_df(output, inputs) | 注册包装的计算函数为 dataframe 变换。 |
| transform_pandas(output, inputs) | 注册包装的计算函数为 pandas 变换。 |
| transform_polars(output, inputs) | 注册包装的计算函数为 Polars 变换。 |

## configure

#### transforms.api.configure(profile=None, allowed_run_duration=None, run_as_user=False)

- 装饰器，用于修改变换的配置。
- 必须使用configure装饰器来包装一个Transform：
```
Copied!1
2
3
4
5
6
7
>>> @configure(profile=['EXECUTOR_MEMORY_MEDIUM'])
... # 使用装饰器 @configure 设置配置文件，此处设置了执行器的内存为中等大小
... @transform(...)
... # 使用装饰器 @transform 进行数据转换操作
... def my_compute_function(...):
...     # 定义一个名为 my_compute_function 的函数，具体实现省略
...     pass
```

#### 参数

- profile(str ↗或 List[str ↗], 非必填)要使用的变换配置文件的名称。
- 要使用的变换配置文件的名称。
- allowed_run_duration(timedelta ↗, 非必填)此任务在失败前可运行的最长时间。请谨慎使用。在配置允许的持续时间时，请考虑数据规模或形状的变化等变量。持续时间仅精确到分钟。重要提示：在用于增量变换时请小心，因为在运行快照时，持续时间可能会显著变化。
- 此任务在失败前可运行的最长时间。请谨慎使用。在配置允许的持续时间时，请考虑数据规模或形状的变化等变量。持续时间仅精确到分钟。重要提示：在用于增量变换时请小心，因为在运行快照时，持续时间可能会显著变化。
- run_as_user(Boolean, 非必填)确定变换是否以用户权限运行。启用时，任务可能会根据运行任务的用户权限表现不同。
- 确定变换是否以用户权限运行。启用时，任务可能会根据运行任务的用户权限表现不同。
#### 异常

- TypeError↗如果封装的对象不是Transform对象。
- 如果封装的对象不是Transform对象。
## incremental

#### transforms.api.incremental(require_incremental=False, semantic_version=1, snapshot_inputs=None)

- 装饰器，将输入和输出转换为其transforms.api.incremental对应物。
- incremental装饰器必须用于包装Transform:
```
Copied!1
2
3
4
>>> @incremental()  # 这是一个装饰器，用于标记函数的递增特性
... @transform(...)  # 这是另一个装饰器，通常用于标记函数的转换功能
... def my_compute_function(...):  # 定义一个名为 my_compute_function 的函数
...     pass  # 占位符，表示函数体为空
```

装饰器从输出数据集中读取搭建历史，以确定最后一次搭建时输入的状态。此信息被用于将TransformInput、TransformOutput和TransformContext对象转换为它们的增量对应物：IncrementalTransformInput、IncrementalTransformOutput和IncrementalTransformContext。

此装饰器也可以用于包装transform_df()和transform_pandas()装饰器。这些装饰器在输入上调用dataframe()和pandas()，不带任何参数，以提取PySpark和pandas DataFrame对象。这意味着使用的读取模式将始终为added，而写入模式将由incremental装饰器确定。要读取或写入任何非默认模式，您必须使用transform()装饰器。

如果您的PySpark或pandas变换的新增输出行仅是新增输入行的函数（根据APPEND示例），默认模式将生成正确的增量变换。

如果您的变换以具有SNAPSHOT事务的数据集作为输入，但这并不影响以增量方式运行变换的能力（例如参考表），请查看snapshot_inputs参数以避免将变换运行为完整的SNAPSHOT。

如果您的变换执行复杂的逻辑（涉及合并、聚合、去重等），建议在使用此装饰器之前阅读增量文档。

#### 参数

- require_incremental(Boolean ↗, 非必填)如果为true，除非变换从未运行过，否则变换将拒绝非增量运行。这是基于所有输出数据集中没有提交的事务来确定的。
- 如果为true，除非变换从未运行过，否则变换将拒绝非增量运行。这是基于所有输出数据集中没有提交的事务来确定的。
- semantic_version(int ↗, 非必填)默认为1。此数字表示变换的语义性质。每当变换的逻辑发生更改以至于使现有输出无效时，应更改此数字。更改此数字会导致变换的后续运行以非增量方式运行。
- 默认为1。此数字表示变换的语义性质。每当变换的逻辑发生更改以至于使现有输出无效时，应更改此数字。更改此数字会导致变换的后续运行以非增量方式运行。
- snapshot_inputs(字符串列表, 非必填)对于哪些输入SNAPSHOT事务不使当前变换输出无效。例如，更新查找表不意味着先前计算的输出不正确。当所有输入（除这些以外）仅添加或没有新数据时，变换将以增量方式运行。在读取snapshot_inputs时，IncrementalTransformInput将仅显示输入数据集的当前视图。
- 对于哪些输入SNAPSHOT事务不使当前变换输出无效。例如，更新查找表不意味着先前计算的输出不正确。当所有输入（除这些以外）仅添加或没有新数据时，变换将以增量方式运行。在读取snapshot_inputs时，IncrementalTransformInput将仅显示输入数据集的当前视图。
- allow_retention(Boolean, 非必填)如果为true，foundry-retention进行的删除操作不会破坏增量性。
- 如果为true，foundry-retention进行的删除操作不会破坏增量性。
- strict_append(Boolean, 非必填)如果为true，底层Foundry事务类型将是APPEND。请注意，写操作可能不会覆盖任何文件，即使是辅助文件如Parquet摘要元数据或Hadoop SUCCESS文件。所有Foundry格式的增量写入都应支持此模式。
- 如果为true，底层Foundry事务类型将是APPEND。请注意，写操作可能不会覆盖任何文件，即使是辅助文件如Parquet摘要元数据或Hadoop SUCCESS文件。所有Foundry格式的增量写入都应支持此模式。
- v2_semantics(Boolean, 非必填)默认为false。如果为true，将使用v2增量语义。v2和v1增量语义之间不应有行为差异，我们建议所有用户设置为true。仅在使用v2语义时才支持非目录增量输入和输出。
- 默认为false。如果为true，将使用v2增量语义。v2和v1增量语义之间不应有行为差异，我们建议所有用户设置为true。仅在使用v2语义时才支持非目录增量输入和输出。
#### 引发

- TypeError↗如果包裹的对象不是Transform object。
- 如果包裹的对象不是Transform object。
- KeyError↗如果快照输入在Transform object上不存在。
- 如果快照输入在Transform object上不存在。
## lightweight

#### transforms.api.lightweight(cpu_cores=2, memory_mb=None, memory_gb=16, gpu_type=None, container_image=None, container_tag=None, container_shell_command=None)

- 装饰器用于使被装饰的变换在容器变换基础设施上运行。
- lightweight装饰器必须用于包装Transform:
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
>>> @lightweight
... @transform(
...     my_input=Input('/input'),
...     my_output=Output('/output')
... )
... def compute_func(my_input, my_output):
...     # 将输入的数据转换为 Pandas DataFrame 并写入输出
...     my_output.write_pandas(my_input.pandas())

>>> @lightweight()
... @transform(
...    my_input=Input('/input'),
...    my_output=Output('/output')
... )
... def compute_func(my_input, my_output):
...     # 遍历输入文件系统中的所有文件，将其内容逐一复制到输出文件系统中
...     for file in my_input.filesystem().ls():
...         with my_input.filesystem().open(file.path) as f1:
...             with my_output.filesystem().open(file.path, "w") as f2:
...                 f2.write(f1.read())

>>> @lightweight(memory_gb=3.5)
... @transform_pandas(
...     Output('/output'),
...     my_input=Input('/input')
... )
... def compute_func(my_input):
...     # 直接返回输入的数据，假设它已经是 Pandas DataFrame
...     return my_input

>>> @lightweight(container_image='my-image', container_tag='0.0.1')
... @transform(my_output=Output('ri...my_output'))
... def run_data_generator_executable(my_output):
...     # 使用系统命令执行数据生成器，生成的数据写入指定的输出路径
...     os.system('$USER_WORKING_DIR/data_generator')
...     my_output.write_table(pd.read_csv('data.csv'))
```

轻量级变换是指在单个节点上运行而不依赖Spark的变换。轻量级变换对于中小型数据集更快且更具成本效益。然而，轻量级变换仅支持常规变换API的一个子集，包括pandas和文件系统API，同时提供更多访问数据集的方法。有关轻量级变换的更多信息，请查阅我们的文档。

要使用此装饰器，必须将foundry-transforms-lib-python添加为依赖项。

如果设置了container_image、container_tag或container_shell_command中的任意一个，则必须同时设置container_image和container_tag。如果未设置container_shell_command，将使用默认的入口点来启动Python环境并执行变换中指定的用户代码。

指定container_*参数被称为自带容器（BYOC）工作流。这确保用户代码库中的所有文件在运行时都可以在$USER_WORKING_DIR/user_code中访问，并且Python环境也将可用。

由container_image和container_tag指定的镜像必须可以从代码库的Artifacts支持库中获取。有关详细信息，请查阅BYOC文档。

#### 参数

- cpu_cores(浮点型, 非必填)分配给变换的CPU核心数量；可以是小数。默认值是2。
- 分配给变换的CPU核心数量；可以是小数。默认值是2。
- memory_mb(浮点型, 非必填)分配给容器的内存量，以MB为单位。可以指定memory_gb或memory_mb，但不能同时指定。
- 分配给容器的内存量，以MB为单位。可以指定memory_gb或memory_mb，但不能同时指定。
- memory_gb(浮点型, 非必填)分配给容器的内存量，以GB为单位。默认值是16GB。
- 分配给容器的内存量，以GB为单位。默认值是16GB。
- gpu_type(字符串, 非必填_)分配给变换的GPU类型。
- 分配给变换的GPU类型。
- container_image(字符串, 非必填_)用于变换容器的镜像。
- 用于变换容器的镜像。
- container_tag(字符串, 非必填_)用于变换容器的镜像标签。
- 用于变换容器的镜像标签。
- container_shell_command(字符串, 非必填_)在容器中执行的shell命令。如果未指定，将生成一个默认值，导致容器启动后执行用户的变换。
- 在容器中执行的shell命令。如果未指定，将生成一个默认值，导致容器启动后执行用户的变换。
## transform

#### transforms.api.transform(ios)

- 将计算函数包装为Transform对象。
将计算函数包装为Transform对象。

- transform装饰器用于从计算函数构建一个Transform对象。用于输入和输出的名称应为被包装计算函数的参数名称。在计算时，该函数会将其输入和输出作为TransformInput和TransformOutput对象传递。
transform装饰器用于从计算函数构建一个Transform对象。用于输入和输出的名称应为被包装计算函数的参数名称。在计算时，该函数会将其输入和输出作为TransformInput和TransformOutput对象传递。

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
>>> @transform(
...     first_input=Input('/path/to/first/input/dataset'),
...     second_input=Input('/path/to/second/input/dataset'),
...     first_output=Output('/path/to/first/output/dataset'),
...     second_output=Output('/path/to/second/output/dataset'),
... )
... def my_compute_function(first_input, second_input, first_output, second_output):
...     # type: (TransformInput, TransformInput, TransformOutput, TransformOutput) -> None
...     # 将第一个输入数据集中的数据写入到第一个输出数据集中
...     first_output.write_dataframe(first_input.dataframe())
...     # 将第二个输入数据集中的数据写入到第二个输出数据集中
...     second_output.write_dataframe(second_input.dataframe())
```

这个代码片段定义了一个名为my_compute_function的函数，该函数使用装饰器@transform来指定输入和输出的数据集路径。函数中，first_output.write_dataframe()和second_output.write_dataframe()分别将从输入数据集中读取的数据写入到指定的输出数据集中。

#### 参数

- ios(输入或输出)kwargs（关键字参数）由命名的输入和输出规格组成。
- kwargs（关键字参数）由命名的输入和输出规格组成。
计算函数负责将数据写入其输出。

非必填地，TransformContext和相应的 SparkSession 也可以在计算函数内访问。您可以使用此功能创建空数据框，应用 Spark 配置等。在可能的情况下，我们建议使用现有的默认 Spark 配置文件，而不是通过SparkSession对象设置 Spark 配置值。

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
>>> @transform(
...     output=Output('/path/to/first/output/dataset'),
... )
... def my_compute_function(ctx, output):
...     # type: (TransformContext, TransformOutput) -> None
...
...     # 在这个例子中，使用Spark会话来创建一个空的数据框。
...     columns = [
...         StructField("col_a", StringType(), True)
...     ]
...     empty_df = ctx.spark_session.createDataFrame([], schema=StructType(columns))
...
...     # 将空的数据框写入输出
...     output.write_dataframe(empty_df)
```

## transform_df

#### transforms.api.transform_df(输出,输入)

- 将包装的计算函数注册为一个数据框架变换。
- transform_df装饰器被用于在从接收和返回pyspark.sql.DataFrame↗对象的计算函数构建Transform对象。类似于transform()装饰器，输入名称变为计算函数的参数名称。然而，一个transform_df仅接受单个Output规范作为位置参数。计算函数的返回值也是一个DataFrame↗，它会被自动写入到单个输出数据集中。
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
>>> @transform_df(
...     Output('/path/to/output/dataset'),  # 一个未命名的输出规范
...     first_input=Input('/path/to/first/input/dataset'),  # 第一个输入数据集
...     second_input=Input('/path/to/second/input/dataset'),  # 第二个输入数据集
... )
... def my_compute_function(first_input, second_input):
...     # type: (pyspark.sql.DataFrame, pyspark.sql.DataFrame) -> pyspark.sql.DataFrame
...     # 合并两个输入数据集并返回
...     return first_input.union(second_input)
```

#### 参数

- output(Output)变换的单个Output规格。
- 变换的单个Output规格。
- inputs(Input)由命名的Input规格组成的kwargs（关键字参数）。
- 由命名的Input规格组成的kwargs（关键字参数）。
非必填地，_TransformContext_和相应的SparkSession也可以在计算函数中访问。您可以使用它来创建空数据框，应用Spark配置等等。 在可能的情况下，我们建议使用现有的默认Spark配置文件，而不是通过SparkSession对象设置Spark配置值。

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
>>> @transform_df(
...     Output('/path/to/output/dataset')  # 指定输出数据集的路径
... )
... def my_compute_function(ctx):
...     # type: (TransformContext) -> pyspark.sql.DataFrame
...
...     # 在这个例子中，Spark会话用于创建一个空的数据框。
...     columns = [
...         StructField("col_a", StringType(), True)  # 定义数据框的列结构，col_a为字符串类型且可为空
...     ]
...     return ctx.spark_session.createDataFrame([], schema=StructType(columns))  # 使用指定的列结构创建一个空的DataFrame
```

## transform_pandas

#### transforms.api.transform_pandas(output,inputs)

- 将包装的计算函数注册为 pandas 变换。
要使用 pandas 库，您必须在meta.yml文件中添加pandas作为运行依赖项。

transform_pandas装饰器用于从一个计算函数构建一个Transform对象，该函数接受并返回pandas.DataFrame↗对象。这个装饰器类似于transform_df()装饰器，然而pyspark.sql.DataFrame↗对象在计算之前会被转换为pandas.DataFrame↗对象，并在计算之后转换回来。

```
Copied!1
2
3
4
5
6
7
8
>>> @transform_pandas(
...     Output('/path/to/output/dataset'),  # 一个未命名的输出规范
...     first_input=Input('/path/to/first/input/dataset'),
...     second_input=Input('/path/to/second/input/dataset'),
... )
... def my_compute_function(first_input, second_input):
...     # 类型注释： (pandas.DataFrame, pandas.DataFrame) -> pandas.DataFrame
...     return first_input.concat(second_input)  # 将两个DataFrame进行连接
```

此代码使用了一个装饰器@transform_pandas，它接收输出和输入数据集路径。函数my_compute_function将两个输入的pandas.DataFrame连接起来，并返回结果。
请注意，transform_pandas应仅用于可以放入内存的数据集。如果您有较大的数据集，希望先筛选后再转换为 pandas，您应该使用transform_df()装饰器和pyspark.sql.SparkSession.createDataFrame()↗方法编写您的变换。

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
>>> @transform_df(
...     Output('/path/to/output/dataset'),  # 未命名的输出规范
...     first_input=Input('/path/to/first/input/dataset'),
...     second_input=Input('/path/to/second/input/dataset'),
... )
... def my_compute_function(ctx, first_input, second_input):
...     # type: (pyspark.sql.DataFrame, pyspark.sql.DataFrame) -> pyspark.sql.DataFrame
...     pd = first_input.filter(first_input.county == 'UK').toPandas()
...     # 在转换回 PySpark DataFrame 之前，对数据的一个子集执行 pandas 操作
...     return ctx.spark_session.createDataFrame(pd)
```

这段代码使用了一个装饰器@transform_df来定义一个数据转换函数my_compute_function。该函数从两个输入数据集中提取数据，并过滤出county字段等于'UK'的数据。过滤后的数据被转换为 Pandas DataFrame 进行处理，最后再转换回 PySpark DataFrame 并返回。

#### 参数

- output(输出)变换的单个输出规范。
- 变换的单个输出规范。
- inputs(输入)由命名的输入规范组成的kwargs（关键字参数）。
- 由命名的输入规范组成的kwargs（关键字参数）。
## transform_polars

#### transforms.api.transform_polars(output,inputs)

- 将包装的计算函数注册为Polars变换。
要使用此装饰器，您必须在meta.yml文件中添加foundry-transforms-lib-python和polars作为运行依赖项。

transform_polars装饰器用于从接受和返回polars.DataFrame↗对象的计算函数构建变换对象。此装饰器类似于transform_df()装饰器，但用户代码会传递polars.DataFrame↗对象。

transform_polars装饰器只是@lightweight装饰器的一个简单包装。使用它会创建一个轻量级变换，缺少常规变换的一些特性。有关轻量级变换的更多信息，请查看我们的文档。

Spark配置文件和某些其他变换功能无法与@lightweight变换一起使用，因此也无法与@transforms_polars一起使用。

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
>>> @transform_polars(
...     Output('ri.main.foundry.dataset.out'),  # 一个未命名的输出规范
...     first_input=Input('ri.main.foundry.dataset.in1'),
...     second_input=Input('ri.main.foundry.dataset.in2'),
... )
... def my_compute_function(ctx, first_input, second_input):
...     # type: (polars.DataFrame, polars.DataFrame) -> polars.DataFrame
...     # 将两个输入的数据集通过'id'字段进行内连接
...     return first_input.join(second_input, on='id', how="inner")
```

#### 参数

- output(Output)变换的单个Output规范。
- 变换的单个Output规范。
- inputs(Input)由命名的Input规范组成的 kwargs（关键字参数）。
- 由命名的Input规范组成的 kwargs（关键字参数）。