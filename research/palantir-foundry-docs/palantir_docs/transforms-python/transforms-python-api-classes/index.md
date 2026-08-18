来源: https://palantir.com/docs/zh/foundry/transforms-python/transforms-python-api-classes/

# 变换类

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换类

| 类 | 描述 |
| --- | --- |
| Check | 封装一个期望，以便可以在数据健康中注册。 |
| FileStatus | 一个collections.namedtuple，捕获关于FoundryFS文件的详细信息。 |
| FileSystem(foundry_fs[, read_only]) | 用于读取和写入数据集文件的文件系统对象。 |
| IncrementalTransformContext(ctx, is_incremental) | 增强了增量计算功能的TransformContext。 |
| IncrementalTransformInput(tinput[, prev_txrid]) | 增强了增量计算功能的TransformInput。 |
| IncrementalTransformOutput(toutput[, …]) | 增强了增量计算功能的TransformOutput。 |
| Input(alias) | 变换输入的规范。 |
| Output(alias[, sever_permissions]) | 变换输出的规范。 |
| Pipeline() | 用于分组一组Transform对象的对象。 |
| Transform(compute_func[, inputs, outputs, ...]) | 描述计算单步骤的可调用对象。 |
| TransformContext(foundry_connector[, parameters]) | 可以选择注入到变换的计算函数中的上下文对象。 |
| TransformInput(rid, branch, txrange, …) | 在运行时传递给Transform对象的输入对象。 |
| LightweightInput(alias) | 在运行时传递给轻量级变换对象的输入对象。 |
| IncrementalLightweightInput(alias) | 在运行时传递给增量轻量级变换对象的输入对象。 |
| TransformOutput(rid, branch, txrid, …) | 在运行时传递给Transform对象的输出对象。 |
| LightweightOutput(alias) | 在运行时传递给轻量级变换对象的输入对象。 |

## Check

### classtransforms.api.Check

封装一个期望，以便可以在数据健康中注册。

- expectationExpectation– 要评估的期望。
- Expectation– 要评估的期望。
- namestr– 检查的名称，用作稳定的标识符。
- str– 检查的名称，用作稳定的标识符。
- is_incrementalbool– 如果变换是增量运行的。
- bool– 如果变换是增量运行的。
- on_error(str, 非必填)– 如果期望不符合，采取的操作。目前有 'WARN', 'FAIL'。
- (str, 非必填)– 如果期望不符合，采取的操作。目前有 'WARN', 'FAIL'。
- description(str, 非必填)– 检查的描述。
- (str, 非必填)– 检查的描述。
## FileStatus

classtransforms.api.FileStatus

一个collections.namedtuple，捕获关于FoundryFS文件的详细信息。

创建FileStatus(path, size, modified)的新实例

- count(value) → integer -- 返回值的出现次数
- index(value[,start[,stop]]) → integer -- 返回值的第一个索引如果值不存在则引发ValueError
- 如果值不存在则引发ValueError
- modified字段编号2的别名
- 字段编号2的别名
- path字段编号0的别名
- 字段编号0的别名
- size字段编号1的别名
- 字段编号1的别名
## FileSystem

classtransforms.api.FileSystem(foundry_fs,read_only=False)

用于读取和写入数据集文件的文件系统对象。

- files(glob=None,regex='.*',show_hidden=False,packing_heuristic=None)创建一个DataFrame↗，包含此数据集中可访问的路径。DataFrame↗按文件大小分区，每个分区包含总大小最多为spark.files.maxPartitionBytes字节的文件路径，或者如果单个文件大于spark.files.maxPartitionBytes则按单个文件分区。文件的大小计算为其磁盘文件大小加上spark.files.openCostInBytes。参数glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。packing_heuristic(str ↗, 非必填_) – 指定用于将文件打包到Spark分区中的启发式。可能的选择有ffd（First Fit Decreasing）或wfd（Worst Fit Decreasing）。虽然wfd产生的分布不均匀，但速度更快，因此推荐用于包含大量文件的数据集。如果未指定启发式，将自动选择一个。返回包含(path, size, modified)的DataFrame返回类型pyspark.sql.DataFrame
- 创建一个DataFrame↗，包含此数据集中可访问的路径。
- DataFrame↗按文件大小分区，每个分区包含总大小最多为spark.files.maxPartitionBytes字节的文件路径，或者如果单个文件大于spark.files.maxPartitionBytes则按单个文件分区。文件的大小计算为其磁盘文件大小加上spark.files.openCostInBytes。
- 参数glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。packing_heuristic(str ↗, 非必填_) – 指定用于将文件打包到Spark分区中的启发式。可能的选择有ffd（First Fit Decreasing）或wfd（Worst Fit Decreasing）。虽然wfd产生的分布不均匀，但速度更快，因此推荐用于包含大量文件的数据集。如果未指定启发式，将自动选择一个。
- glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。
- regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。
- show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。
- packing_heuristic(str ↗, 非必填_) – 指定用于将文件打包到Spark分区中的启发式。可能的选择有ffd（First Fit Decreasing）或wfd（Worst Fit Decreasing）。虽然wfd产生的分布不均匀，但速度更快，因此推荐用于包含大量文件的数据集。如果未指定启发式，将自动选择一个。
- 返回包含(path, size, modified)的DataFrame
- 包含(path, size, modified)的DataFrame
- 返回类型pyspark.sql.DataFrame
- pyspark.sql.DataFrame
- ls(glob=None,regex='.*',show_hidden=False)递归遍历所有目录，并列出从数据集根目录起匹配给定模式的所有文件。参数glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。生成FileStatus- 逻辑路径、文件大小（字节）、修改时间戳（自1970年1月1日UTC以来的毫秒数）。
- 递归遍历所有目录，并列出从数据集根目录起匹配给定模式的所有文件。
- 参数glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。
- glob(str ↗, 非必填_) – Unix文件匹配模式。支持globstar；要递归搜索文件（例如pdf），请使用**/*.pdf。
- regex(str ↗, 非必填_) – 匹配文件名的正则表达式模式。
- show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。
- 生成FileStatus- 逻辑路径、文件大小（字节）、修改时间戳（自1970年1月1日UTC以来的毫秒数）。
- FileStatus- 逻辑路径、文件大小（字节）、修改时间戳（自1970年1月1日UTC以来的毫秒数）。
- open(_path,mode='r',kwargs)以给定模式打开FoundryFS文件。kwargs是关键字参数。参数path(str ↗) – 数据集中文件的逻辑路径。kwargs– 剩余的关键字参数传递给io.open()↗show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。返回连接到流的Python文件对象。返回类型文件
- 以给定模式打开FoundryFS文件。kwargs是关键字参数。
- 参数path(str ↗) – 数据集中文件的逻辑路径。kwargs– 剩余的关键字参数传递给io.open()↗show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。
- path(str ↗) – 数据集中文件的逻辑路径。
- kwargs– 剩余的关键字参数传递给io.open()↗
- show_hidden(bool ↗, 非必填_) – 包括隐藏文件，即以.或_开头的文件。
- 返回连接到流的Python文件对象。
- 连接到流的Python文件对象。
- 返回类型文件
- 文件
## IncrementalTransformContext

### classtransforms.api.IncrementalTransformContext(ctx,is_incremental)

带有增量计算功能的TransformContext。

- auth_headerstr– 用于运行变换的身份验证头。
- str– 用于运行变换的身份验证头。
- fallback_branchesList[str]– 运行变换时配置的回退分支。
- List[str]– 运行变换时配置的回退分支。
- is_incrementalbool– 如果变换是增量运行的。
- bool– 如果变换是增量运行的。
- parametersdict of (str, any)– 变换参数。
- dict of (str, any)– 变换参数。
- spark_sessionpyspark.sql.SparkSession– 用于运行变换的Spark会话。
- pyspark.sql.SparkSession– 用于运行变换的Spark会话。
## IncrementalTransformInput

### classtransforms.api.IncrementalTransformInput(tinput,prev_txrid=None)

具有增量计算功能的TransformInput。

- dataframe(mode='added')返回给定读取模式的pyspark.sql.DataFrame。仅支持_current_，_previous_和_added_模式。参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_返回数据集的DataFrame。返回类型Dataframe↗
- 返回给定读取模式的pyspark.sql.DataFrame。
- 仅支持_current_，_previous_和_added_模式。
- 参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_
- mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_
- 返回数据集的DataFrame。
- 数据集的DataFrame。
- 返回类型Dataframe↗
- Dataframe↗
- filesystem(mode='added')为给定读取模式从_FoundryFS_构建一个_FileSystem_对象。仅支持_current_，_previous_和_added_模式。参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_返回给定视图的文件系统对象。返回类型FileSystem
- 为给定读取模式从_FoundryFS_构建一个_FileSystem_对象。
- 仅支持_current_，_previous_和_added_模式。
- 参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_
- mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_added_
- 返回给定视图的文件系统对象。
- 给定视图的文件系统对象。
- 返回类型FileSystem
- FileSystem
- pandas()pandas.DataFrame ↗: 包含输入数据集完整视图的Pandas DataFrame。
- pandas.DataFrame ↗: 包含输入数据集完整视图的Pandas DataFrame。
- branchstr– 输入数据集的分支。
- str– 输入数据集的分支。
- pathstr– 输入数据集的项目路径。
- str– 输入数据集的项目路径。
- ridstr– 数据集的资源标识符。
- str– 数据集的资源标识符。
## IncrementalTransformOutput

classtransforms.api.IncrementalTransformOutput(toutput,prev_txrid=None,mode='replace')

具有增量计算功能的TransformOutput。

- abort()中止事务，允许任务成功完成而不写入任何数据。有关更多详细信息，请参见Python Abort。
- 中止事务，允许任务成功完成而不写入任何数据。有关更多详细信息，请参见Python Abort。
- dataframe(mode='current',schema=None)返回给定读取模式的pyspark.sql.DataFrame ↗。参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_current_。schema(pyspark.types.StructType, 非必填) - 构建空DataFrame时使用的PySpark模式。使用读取模式‘previous’时必须提供。返回数据集的DataFrame。返回类型DataFrame↗引发ValueError↗- 如果使用模式‘previous’时未传递任何模式
- 返回给定读取模式的pyspark.sql.DataFrame ↗。
- 参数mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_current_。schema(pyspark.types.StructType, 非必填) - 构建空DataFrame时使用的PySpark模式。使用读取模式‘previous’时必须提供。
- mode(str ↗, 非必填) – 读取模式之一，current，previous，added，modified，removed。默认_current_。
- schema(pyspark.types.StructType, 非必填) - 构建空DataFrame时使用的PySpark模式。使用读取模式‘previous’时必须提供。
- 返回数据集的DataFrame。
- 数据集的DataFrame。
- 返回类型DataFrame↗
- DataFrame↗
- 引发ValueError↗- 如果使用模式‘previous’时未传递任何模式
- ValueError↗- 如果使用模式‘previous’时未传递任何模式
- filesystem(mode='current')构建一个用于写入_FoundryFS_的_FileSystem_对象。参数mode(str ↗, 非必填) – 读取模式之一，added，current_或_previous。默认值为current_。仅可写入当前文件系统。引发NotImplementedError↗– 当前不支持。
- 构建一个用于写入_FoundryFS_的_FileSystem_对象。
- 参数mode(str ↗, 非必填) – 读取模式之一，added，current_或_previous。默认值为current_。仅可写入当前文件系统。
- mode(str ↗, 非必填) – 读取模式之一，added，current_或_previous。默认值为current_。仅可写入当前文件系统。
- 引发NotImplementedError↗– 当前不支持。
- NotImplementedError↗– 当前不支持。
- pandas(mode='current')pandas.DataFrame ↗: 给定读取模式的Pandas DataFrame。
- pandas.DataFrame ↗: 给定读取模式的Pandas DataFrame。
- set_mode(mode)更改数据集的写入模式。参数mode(str ↗) – 写入模式之一‘replace’或‘modify’。在modify模式下，写入输出的任何内容都会追加到数据集中。在replace模式下，写入输出的任何内容都会替换数据集。
- 更改数据集的写入模式。
- 参数mode(str ↗) – 写入模式之一‘replace’或‘modify’。在modify模式下，写入输出的任何内容都会追加到数据集中。在replace模式下，写入输出的任何内容都会替换数据集。
- mode(str ↗) – 写入模式之一‘replace’或‘modify’。在modify模式下，写入输出的任何内容都会追加到数据集中。在replace模式下，写入输出的任何内容都会替换数据集。
数据写入后无法更改写入模式。

- write_dataframe(df,partition_cols=None,bucket_cols=None,bucket_count=None,sort_by=None,output_format=None,options=None)将给定的DataFrame ↗写入输出数据集。参数df(_pyspark.sql.DataFrame ↗) – 要写入的PySpark DataFrame。partition_cols(List[str ↗], 非必填) - 写入数据时使用的列分区。bucket_cols(List[str ↗], 非必填) – 数据分桶的列。如果指定了bucket_count，则必须指定。bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。sort_by(List[str ↗], 非必填) – 按哪个列对分桶数据进行排序。output_format(str ↗, 非必填) – 输出文件格式，默认为‘parquet’。options(dict ↗, 非必填) – 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的其他选项。
- 将给定的DataFrame ↗写入输出数据集。
- 参数df(_pyspark.sql.DataFrame ↗) – 要写入的PySpark DataFrame。partition_cols(List[str ↗], 非必填) - 写入数据时使用的列分区。bucket_cols(List[str ↗], 非必填) – 数据分桶的列。如果指定了bucket_count，则必须指定。bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。sort_by(List[str ↗], 非必填) – 按哪个列对分桶数据进行排序。output_format(str ↗, 非必填) – 输出文件格式，默认为‘parquet’。options(dict ↗, 非必填) – 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的其他选项。
- df(_pyspark.sql.DataFrame ↗) – 要写入的PySpark DataFrame。
- partition_cols(List[str ↗], 非必填) - 写入数据时使用的列分区。
- bucket_cols(List[str ↗], 非必填) – 数据分桶的列。如果指定了bucket_count，则必须指定。
- bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。
- sort_by(List[str ↗], 非必填) – 按哪个列对分桶数据进行排序。
- output_format(str ↗, 非必填) – 输出文件格式，默认为‘parquet’。
- options(dict ↗, 非必填) – 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的其他选项。
- write_pandas(pandas_df)将给定的pandas.DataFrame ↗写入输出数据集。参数pandas_df(pandas.DataFrame ↗) – 要写入的DataFrame。
- 将给定的pandas.DataFrame ↗写入输出数据集。
- 参数pandas_df(pandas.DataFrame ↗) – 要写入的DataFrame。
- pandas_df(pandas.DataFrame ↗) – 要写入的DataFrame。
- branchstr– 数据集的分支。
- str– 数据集的分支。
- pathstr– 数据集的项目路径。
- str– 数据集的项目路径。
- ridstr– 数据集的资源标识符。
- str– 数据集的资源标识符。
## Input

classtransforms.api.Input(alias,branch,stop_propagating,stop_requiring,checks)

变换输入的规范。

- 参数alias(str ↗, 非必填) – 数据集的rid或数据集的绝对项目路径。如果未指定，参数未绑定。branch(str ↗, 非必填)：解决输入数据集的分支名称。如果未指定，在搭建时解决。stop_propagating(Markings, 非必填)：要停止从此传播的安全权限标记。请参阅权限标记和删除继承的权限标记文档。stop_requiring(OrgMarkings, 非必填)：在此输入上假定的组织权限标记。checks(List[Check], Check, 非必填)：一个或多个:class:Check对象。failure_strategy(str ↗, 非必填)：输入更新失败时的策略。必须是continue或fail之一。如果未指定，默认为fail。
- alias(str ↗, 非必填) – 数据集的rid或数据集的绝对项目路径。如果未指定，参数未绑定。
- branch(str ↗, 非必填)：解决输入数据集的分支名称。如果未指定，在搭建时解决。
- stop_propagating(Markings, 非必填)：要停止从此传播的安全权限标记。请参阅权限标记和删除继承的权限标记文档。
- stop_requiring(OrgMarkings, 非必填)：在此输入上假定的组织权限标记。
- checks(List[Check], Check, 非必填)：一个或多个:class:Check对象。
- failure_strategy(str ↗, 非必填)：输入更新失败时的策略。必须是continue或fail之一。如果未指定，默认为fail。
## Output

classtransforms.api.Output(alias=None,sever_permissions=False,checks=None)

变换输出的规范。

- 参数alias(str ↗, 非必填) - 数据集的rid或数据集的绝对项目路径。如果未指定，参数未绑定。sever_permissions(bool ↗, 非必填) - 如果为true，则将数据集的权限与其输入的权限分离。如果参数未绑定，则忽略checks(List[Check], Check, 非必填) - 一个或多个:class:Check对象。
- alias(str ↗, 非必填) - 数据集的rid或数据集的绝对项目路径。如果未指定，参数未绑定。
- sever_permissions(bool ↗, 非必填) - 如果为true，则将数据集的权限与其输入的权限分离。如果参数未绑定，则忽略
- checks(List[Check], Check, 非必填) - 一个或多个:class:Check对象。
## Pipeline

classtransforms.api.Pipeline

用于分组一组Transform对象的对象。

- add_transforms(*transforms)将给定的Transform对象注册到_Pipeline_实例。参数transforms(Transform) – 要注册的变换。引发ValueError↗– 如果多个Transform对象写入相同的Output别名。
- 将给定的Transform对象注册到_Pipeline_实例。
- 参数transforms(Transform) – 要注册的变换。
- transforms(Transform) – 要注册的变换。
- 引发ValueError↗– 如果多个Transform对象写入相同的Output别名。
- ValueError↗– 如果多个Transform对象写入相同的Output别名。
- discover_transforms(*modules)递归查找并导入模块，注册每个模块级变换。此方法递归查找并导入从给定模块的___路径___开始的模块。每个找到的模块都会被导入，并且任何作为Transform实例的属性（通过变换装饰器构造）都将被注册到管道。参数modules(module) – 开始搜索的模块。
- 递归查找并导入模块，注册每个模块级变换。
- 此方法递归查找并导入从给定模块的___路径___开始的模块。每个找到的模块都会被导入，并且任何作为Transform实例的属性（通过变换装饰器构造）都将被注册到管道。
- 参数modules(module) – 开始搜索的模块。
- modules(module) – 开始搜索的模块。
```
Copied!1
2
3
4
5
6
7
>>> import myproject
>>> p = Pipeline()
>>> p.discover_transforms(myproject)
# 该代码导入了一个名为 myproject 的模块。
# 然后创建了一个 Pipeline 对象实例 p。
# 接着调用 p 的 discover_transforms 方法，传入 myproject 模块。
# 这个方法可能用于在 myproject 中发现或注册一些数据转换操作。
```

找到的每个模块都会被导入。尽量避免在模块级别执行代码。

- transformsList[Transform]– 注册到管道中的变换列表。
- List[Transform]– 注册到管道中的变换列表。
## Transform

classtransforms.api.Transform(compute_func,inputs=None,outputs=None,profile=None)

一个描述计算单步骤的可调用对象。

一个变换由若干Input规格、若干Output规格和一个计算函数组成。

使用提供的装饰器构建Transform对象是惯用的：transform(),transform_df(), 和transform_pandas()。

注意：原始的计算函数通过Transform的__call__方法暴露。

- 参数compute_func(Callable) –  用于包装的计算函数。inputs(Dict[str ↗,Input]) - 映射输入名称到Input规格的字典。outputs(Dict[str ↗,Output]) - 映射输入名称到Output规格的字典。profile(str ↗, 非必填) – 在运行时使用的变换配置文件名称。
参数

- compute_func(Callable) –  用于包装的计算函数。
- inputs(Dict[str ↗,Input]) - 映射输入名称到Input规格的字典。
- outputs(Dict[str ↗,Output]) - 映射输入名称到Output规格的字典。
- profile(str ↗, 非必填) – 在运行时使用的变换配置文件名称。
- compute(ctx=None, _kwargs_)**使用上下文及一组输入和输出计算变换。参数ctx(TransformContext, 非必填) – 如果请求，传递给变换的上下文对象。kwargs(TransformInput或TransformOutput) - 映射输入名称到Input规格的字典。kwarg是关键字参数的缩写。outputs(Dict[str ↗,Output]) - 传递给计算函数的输入、输出和上下文对象。返回运行变换后的输出对象。返回类型dict of (str ↗,TransformOutput)
compute(ctx=None, _kwargs_)**

- 使用上下文及一组输入和输出计算变换。
- 参数ctx(TransformContext, 非必填) – 如果请求，传递给变换的上下文对象。kwargs(TransformInput或TransformOutput) - 映射输入名称到Input规格的字典。kwarg是关键字参数的缩写。outputs(Dict[str ↗,Output]) - 传递给计算函数的输入、输出和上下文对象。
- ctx(TransformContext, 非必填) – 如果请求，传递给变换的上下文对象。
- kwargs(TransformInput或TransformOutput) - 映射输入名称到Input规格的字典。kwarg是关键字参数的缩写。
- outputs(Dict[str ↗,Output]) - 传递给计算函数的输入、输出和上下文对象。
- 返回运行变换后的输出对象。
- 运行变换后的输出对象。
- 返回类型dict of (str ↗,TransformOutput)
- dict of (str ↗,TransformOutput)
- versionstr– 一个用于比较两个变换版本的字符串，用于考虑逻辑陈旧性。例如，一个SQL变换可能会获取SQL查询的哈希值。理想情况下，SQL查询应被转换为一个格式，以便对语义上等效的变换产生相同的版本。即SQL查询select A, B from foo;应该与SQL查询 select A, B from (select * from foo);具有相同的版本。如果没有指定版本，将使用存储库的版本。引发ValueError↗– 如果计算函数的对象哈希失败
version

- str– 一个用于比较两个变换版本的字符串，用于考虑逻辑陈旧性。
- 例如，一个SQL变换可能会获取SQL查询的哈希值。理想情况下，SQL查询应被转换为一个格式，以便对语义上等效的变换产生相同的版本。即SQL查询select A, B from foo;应该与SQL查询 select A, B from (select * from foo);具有相同的版本。
- 如果没有指定版本，将使用存储库的版本。
- 引发ValueError↗– 如果计算函数的对象哈希失败
- ValueError↗– 如果计算函数的对象哈希失败
## TransformContext

classtransforms.api.TransformContext(foundry_connector,parameters=None)可以选择注入到变换计算函数中的上下文对象。

- auth_headerstr– 用于运行变换的授权头。此授权头具有有限的范围，并且只有运行任务所需的权限。它不应用于API调用。
- str– 用于运行变换的授权头。此授权头具有有限的范围，并且只有运行任务所需的权限。它不应用于API调用。
- fallback_branchesList[str]– 在运行变换时配置的回退分支。
- List[str]– 在运行变换时配置的回退分支。
- parametersdict of (str, any)– 变换参数。
- dict of (str, any)– 变换参数。
- spark_sessionpyspark.sql.SparkSession– 用于运行变换的Spark会话。
- pyspark.sql.SparkSession– 用于运行变换的Spark会话。
## TransformInput

classtransforms.api.TransformInput(rid,branch,txrange,dfreader,fsbuilder)

在运行时传递给Transform对象的输入对象。

- dataframe()返回给定读取模式的pyspark.sql.DataFrame ↗。返回数据集的数据框。返回类型pyspark.sql.DataFrame ↗
- 返回给定读取模式的pyspark.sql.DataFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pyspark.sql.DataFrame ↗
- pyspark.sql.DataFrame ↗
- filesystem()构建一个用于从_FoundryFS_读取的_FileSystem_对象。返回一个用于从Foundry读取的_FileSystem_对象。返回类型FileSystem
- 构建一个用于从_FoundryFS_读取的_FileSystem_对象。
- 返回一个用于从Foundry读取的_FileSystem_对象。
- 一个用于从Foundry读取的_FileSystem_对象。
- 返回类型FileSystem
- FileSystem
- pandas()pandas.DataFrame ↗: 包含输入数据集全视图的Pandas数据框。
- pandas.DataFrame ↗: 包含输入数据集全视图的Pandas数据框。
- branchstr– 输入数据集的分支。
- str– 输入数据集的分支。
- pathstr– 输入数据集的项目路径。
- str– 输入数据集的项目路径。
- ridstr– 数据集的资源标识符。
- str– 数据集的资源标识符。
- column_descriptionsDict<str, str>– 数据集的列描述。
- Dict<str, str>– 数据集的列描述。
- column_typeclassesDict<str, str>– 数据集的列类型类。
- Dict<str, str>– 数据集的列类型类。
## LightweightInput

classtransforms.api.LightweightInput(alias)

其目的是通过委托给Foundry Data Sidecar模仿TransformInput的API子集，同时通过支持各种数据格式进行扩展。

- dataframe()返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- filesystem()构建一个用于从_FoundryFS_读取的_FileSystem_对象。返回一个用于从Foundry读取的_FileSystem_对象。返回类型FileSystem
- 构建一个用于从_FoundryFS_读取的_FileSystem_对象。
- 返回一个用于从Foundry读取的_FileSystem_对象。
- 一个用于从Foundry读取的_FileSystem_对象。
- 返回类型FileSystem
- FileSystem
- pandas()返回一个包含数据集的pandas.DataFrame ↗。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- arrow()返回一个包含数据集的pyarrow.Table ↗。返回数据集的表。返回类型pyarrow.Table ↗
- 返回一个包含数据集的pyarrow.Table ↗。
- 返回数据集的表。
- 数据集的表。
- 返回类型pyarrow.Table ↗
- pyarrow.Table ↗
- polars(lazy: Optional[bool]=False)根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。返回数据集的数据框。返回类型polars.DataFrame ↗或polars.LazyFrame ↗
- 根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型polars.DataFrame ↗或polars.LazyFrame ↗
- polars.DataFrame ↗或polars.LazyFrame ↗
- path()返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。返回包含数据集文件的目录路径。返回类型str ↗
- 返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。
- 返回包含数据集文件的目录路径。
- 包含数据集文件的目录路径。
- 返回类型str ↗
- str ↗
## IncrementalLightweightInput

classtransforms.api.IncrementalLightweightInput(alias)

其目的是通过委托给Foundry Data Sidecar模仿IncrementalTransformInput的API子集，同时通过支持各种数据格式进行扩展。它是LightweightInput的增量对应物。

- dataframe(mode)返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。
- 参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- filesystem()构建一个用于从_FoundryFS_读取的_FileSystem_对象。返回一个用于从Foundry读取的_FileSystem_对象。返回类型FileSystem
- 构建一个用于从_FoundryFS_读取的_FileSystem_对象。
- 返回一个用于从Foundry读取的_FileSystem_对象。
- 一个用于从Foundry读取的_FileSystem_对象。
- 返回类型FileSystem
- FileSystem
- pandas()(mode)返回一个包含数据集的pandas.DataFrame ↗。参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。
- 参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- arrow()(mode)返回一个包含数据集的pyarrow.Table ↗。参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。返回数据集的表。返回类型pyarrow.Table ↗
- 返回一个包含数据集的pyarrow.Table ↗。
- 参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- 返回数据集的表。
- 数据集的表。
- 返回类型pyarrow.Table ↗
- pyarrow.Table ↗
- polars(lazy=False,mode)根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。参数lazy(Optional[bool]) – 选择惰性或急切的Polars数据框。mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。返回数据集的数据框。返回类型polars.DataFrame ↗或polars.LazyFrame ↗。
- 根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。
- 参数lazy(Optional[bool]) – 选择惰性或急切的Polars数据框。mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- lazy(Optional[bool]) – 选择惰性或急切的Polars数据框。
- mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型polars.DataFrame ↗或polars.LazyFrame ↗。
- polars.DataFrame ↗或polars.LazyFrame ↗。
- path(mode)返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_返回包含数据集文件的目录路径。返回类型str ↗
- 返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。
- 参数mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_
- mode(str ↗, 非必填) – 读取模式之一，current、previous、added、modified、removed。默认为_added_
- 返回包含数据集文件的目录路径。
- 包含数据集文件的目录路径。
- 返回类型str ↗
- str ↗
## TransformOutput

classtransforms.api.TransformOutput(rid,branch,txrid,dfreader,dfwriter,fsbuilder)

在运行时传递给Transform对象的输出对象。

- abort()中止事务，允许任务成功完成而不写入任何数据。有关更多详细信息，请参见Python Abort。
- 中止事务，允许任务成功完成而不写入任何数据。有关更多详细信息，请参见Python Abort。
- dataframe()返回一个包含输出数据集全视图的pyspark.sql.DataFrame ↗。返回数据集的数据框。返回类型pyspark.sql.DataFrame ↗
- 返回一个包含输出数据集全视图的pyspark.sql.DataFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pyspark.sql.DataFrame ↗
- pyspark.sql.DataFrame ↗
- filesystem()构建一个用于写入到_FoundryFS_的_FileSystem_对象。返回一个用于写入到Foundry的_FileSystem_对象。
- 构建一个用于写入到_FoundryFS_的_FileSystem_对象。
- 返回一个用于写入到Foundry的_FileSystem_对象。
- 一个用于写入到Foundry的_FileSystem_对象。
- 返回类型FileSystem
- FileSystem
- pandas()pandas.DataFrame ↗: 包含输出数据集全视图的Pandas数据框。
- pandas.DataFrame ↗: 包含输出数据集全视图的Pandas数据框。
- set_mode(mode)更改数据集的写入模式。参数mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。
- 更改数据集的写入模式。
- 参数mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。
- mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。
- write_dataframe(df,partition_cols=None,bucket_cols=None,bucket_count=None,sort_by=None,output_format=None,options=None,column_descriptions=None,column_typeclasses=None)将给定的DataFrame ↗写入到输出数据集中。参数df(pyspark.sql.DataFrame ↗) – 要写入的PySpark数据框。partition_cols(List[str ↗], 非必填) - 写入数据时要使用的列分区。bucket_cols(List[str ↗], 非必填) - 用于对数据进行分桶的列。如果指定了bucket_count，则必须指定。bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。sort_by(List[str ↗], 非必填) - 用于对分桶数据进行排序的列。output_format(str ↗, 非必填) - 输出文件格式，默认为'parquet'。文件格式基于Spark的DataFrameWriter ↗及其他类型，包括'csv'、'json'、'orc'和'text'。options(dict ↗, 非必填) - 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的额外选项。column_descriptions(Dict[str ↗,str ↗], 非必填) - 列名称到其字符串描述的映射。此映射与DataFrame的列相交，必须包含描述（最多800个字符）。column_typeclasses(Dict[str ↗, List[Dict[str ↗,str ↗]], 非必填) - 列名称到其列类型类的映射。列表中的每个类型类是一个_Dict[str ↗,str ↗]_，其中只有两个键是有效的："name"和"kind"。这些键中的每一个都映射到用户想要的相应字符串。
- 将给定的DataFrame ↗写入到输出数据集中。
- 参数df(pyspark.sql.DataFrame ↗) – 要写入的PySpark数据框。partition_cols(List[str ↗], 非必填) - 写入数据时要使用的列分区。bucket_cols(List[str ↗], 非必填) - 用于对数据进行分桶的列。如果指定了bucket_count，则必须指定。bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。sort_by(List[str ↗], 非必填) - 用于对分桶数据进行排序的列。output_format(str ↗, 非必填) - 输出文件格式，默认为'parquet'。文件格式基于Spark的DataFrameWriter ↗及其他类型，包括'csv'、'json'、'orc'和'text'。options(dict ↗, 非必填) - 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的额外选项。column_descriptions(Dict[str ↗,str ↗], 非必填) - 列名称到其字符串描述的映射。此映射与DataFrame的列相交，必须包含描述（最多800个字符）。column_typeclasses(Dict[str ↗, List[Dict[str ↗,str ↗]], 非必填) - 列名称到其列类型类的映射。列表中的每个类型类是一个_Dict[str ↗,str ↗]_，其中只有两个键是有效的："name"和"kind"。这些键中的每一个都映射到用户想要的相应字符串。
- df(pyspark.sql.DataFrame ↗) – 要写入的PySpark数据框。
- partition_cols(List[str ↗], 非必填) - 写入数据时要使用的列分区。
- bucket_cols(List[str ↗], 非必填) - 用于对数据进行分桶的列。如果指定了bucket_count，则必须指定。
- bucket_count(int ↗, 非必填) – 桶的数量。如果指定了bucket_cols，则必须指定。
- sort_by(List[str ↗], 非必填) - 用于对分桶数据进行排序的列。
- output_format(str ↗, 非必填) - 输出文件格式，默认为'parquet'。文件格式基于Spark的DataFrameWriter ↗及其他类型，包括'csv'、'json'、'orc'和'text'。
- options(dict ↗, 非必填) - 传递给org.apache.spark.sql.DataFrameWriter#option(String, String)的额外选项。
- column_descriptions(Dict[str ↗,str ↗], 非必填) - 列名称到其字符串描述的映射。此映射与DataFrame的列相交，必须包含描述（最多800个字符）。
- column_typeclasses(Dict[str ↗, List[Dict[str ↗,str ↗]], 非必填) - 列名称到其列类型类的映射。列表中的每个类型类是一个_Dict[str ↗,str ↗]_，其中只有两个键是有效的："name"和"kind"。这些键中的每一个都映射到用户想要的相应字符串。
- write_pandas(pandas_df)将给定的pandas.DataFrame ↗写入到输出数据集中。参数pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- 将给定的pandas.DataFrame ↗写入到输出数据集中。
- 参数pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- branchstr– 数据集的分支。
- str– 数据集的分支。
- pathstr– 数据集的项目路径。
- str– 数据集的项目路径。
- ridstr– 数据集的资源标识符。
- str– 数据集的资源标识符。
## LightweightOutput

classtransforms.api.LightweightInput(alias)

其目的是通过委托给Foundry Data Sidecar模仿TransformOutput的API子集。

- filesystem()构建一个用于从_FoundryFS_读取的_FileSystem_对象。返回一个用于从Foundry读取的_FileSystem_对象。返回类型FileSystem
- 构建一个用于从_FoundryFS_读取的_FileSystem_对象。
- 返回一个用于从Foundry读取的_FileSystem_对象。
- 一个用于从Foundry读取的_FileSystem_对象。
- 返回类型FileSystem
- FileSystem
- dataframe()返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。它是pandas()的别名。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- pandas()返回一个包含数据集的pandas.DataFrame ↗。返回数据集的数据框。返回类型pandas.DataFrame ↗
- 返回一个包含数据集的pandas.DataFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型pandas.DataFrame ↗
- pandas.DataFrame ↗
- arrow()返回一个包含数据集的pyarrow.Table ↗。返回数据集的表。返回类型pyarrow.Table ↗
- 返回一个包含数据集的pyarrow.Table ↗。
- 返回数据集的表。
- 数据集的表。
- 返回类型pyarrow.Table ↗
- pyarrow.Table ↗
- polars(lazy: Optional[bool]=False)根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。返回数据集的数据框。返回类型polars.DataFrame ↗或polars.LazyFrame ↗
- 根据lazy参数的值返回一个polars.DataFrame ↗或polars.LazyFrame ↗。
- 返回数据集的数据框。
- 数据集的数据框。
- 返回类型polars.DataFrame ↗或polars.LazyFrame ↗
- polars.DataFrame ↗或polars.LazyFrame ↗
- path()返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。返回包含数据集文件的目录路径。返回类型str ↗
- 返回一个包含下载的数据集文件路径的str ↗，这些文件可能是CSV、Parquet或Avro文件。
- 返回包含数据集文件的目录路径。
- 包含数据集文件的目录路径。
- 返回类型str ↗
- str ↗
- write_pandas(pandas_df)将给定的pandas.DataFrame ↗写入到输出数据集中。它委托给write_table。参数pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- 将给定的pandas.DataFrame ↗写入到输出数据集中。它委托给write_table。
- 参数pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- pandas_df(pandas.DataFrame ↗) – 要写入的数据框。
- write_table(df)将给定的pandas.DataFrame ↗、pyarrow.Table ↗、polars.DataFrame ↗或polars.LazyFrame ↗，或path写入到输出数据集中。如果给定path（无论是str还是pathlib.Path），其值必须与path_for_write_table返回的值匹配。参数df(pandas.DataFrame ↗,pyarrow.Table ↗,polars.DataFrame ↗或polars.LazyFrame ↗, 或path) – 要写入的数据框。
- 将给定的pandas.DataFrame ↗、pyarrow.Table ↗、polars.DataFrame ↗或polars.LazyFrame ↗，或path写入到输出数据集中。如果给定path（无论是str还是pathlib.Path），其值必须与path_for_write_table返回的值匹配。
- 参数df(pandas.DataFrame ↗,pyarrow.Table ↗,polars.DataFrame ↗或polars.LazyFrame ↗, 或path) – 要写入的数据框。
- df(pandas.DataFrame ↗,pyarrow.Table ↗,polars.DataFrame ↗或polars.LazyFrame ↗, 或path) – 要写入的数据框。
- path_for_write_table用于与write_table一起使用的数据集文件的路径。返回类型str ↗
- 用于与write_table一起使用的数据集文件的路径。
- 返回类型str ↗
- str ↗
- set_mode(mode)更改数据集的写入模式。参数mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。
- 更改数据集的写入模式。
- 参数mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。
- mode(str ↗) – 写入模式之一，‘replace’或‘modify’。在修改模式下，写入到输出的任何内容都会追加到数据集中。在替换模式下，写入到输出的任何内容都会替换数据集。