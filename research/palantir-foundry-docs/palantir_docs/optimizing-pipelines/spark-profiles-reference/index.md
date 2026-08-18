来源: https://palantir.com/docs/zh/foundry/optimizing-pipelines/spark-profiles-reference/

# Spark配置文件参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Spark配置文件参考

此页面是Foundry中可用的Spark配置文件的参考资料。了解更多关于Spark和配置文件的信息：

- Spark概念
- 应用Spark配置文件
## 驱动核心数

此系列的配置文件配置spark.driver.cores的值。

这控制了分配给spark驱动程序的CPU核心数。实际上，除非在同一个spark模块中同时运行许多spark任务的特殊情况，否则不需要覆盖这个设置。

## 驱动内存

此系列的配置文件配置spark.driver.memory的值。

这控制了分配给spark驱动程序JVM的内存量。在某些情况下可能需要增加此值，例如当将大量数据收集回驱动程序时，或者在执行大型广播合并时。

这只控制JVM内存，而不是Python进程可用的内存。如果您在本地拉取大量数据以使用Pandas进行变换，您将需要不同的配置文件。

## 执行器核心数

此系列的配置文件配置spark.executor.cores的值。

这控制了分配给每个spark执行器的CPU核心数，进而控制每个执行器中同时运行的任务数。实际上，在正常的变换任务中，几乎不需要覆盖此设置。

## 执行器内存

此系列的配置文件配置spark.executor.memory及相关设置的值。

这控制了分配给每个spark执行器JVM的内存量。如果每个spark任务处理的数据量非常大，可能需要增加此值。

这些内存是所有在执行器上运行的任务共享的（由执行器核心配置文件控制）。

## 执行器内存开销

此系列的配置文件配置spark.executor.memoryOverhead的值。

这控制了分配给每个容器的内存量，除了spark执行器JVM内存之外。如果您的任务需要大量JVM外部的内存，可能需要增加此值。

## 执行器数量

此系列的配置文件配置spark.executor.instances及相关设置的值。

这控制了运行任务所请求的执行器数量。增加此值会增加可以并行运行的任务数，从而提高性能（前提是任务足够并行），但会消耗更多资源。

实际上，只有在需要特别快速运行的大型任务中才需要覆盖此设置。

## 动态分配

此系列的配置文件配置spark.dynamicAllocation.enabled、spark.dynamicAllocation.minExecutors和spark.dynamicAllocation.maxExecutors的值。

这通过指定一个执行器范围而不是固定数量来控制运行任务所请求的执行器数量。Spark会将请求的执行器数量扩展到maxExecutors，并在不需要时释放执行器，这在所需的执行器数量不一致时或某些情况下用于加快启动时间可能很有帮助。模块不能保证接收到请求的maxExecutors数量，由于执行器数量可变，性能可能会有所不同。

实际上，只有在对动态分配的优缺点有特定了解的大型任务中才需要覆盖此设置。

## 自适应查询执行

此系列的配置文件启用和禁用自适应查询执行（AQE）。

启用AQE后，Spark将自动在运行时设置分区数，可能会加快您的搭建速度。它可以避免分区过少导致并行度不足，和分区过多导致开销过大。

AQE目标是每个分区的平衡输出大小为64 MB。例如，总输出大小为512 MB将产生约8个分区。

您可以使用此系列的文件大小配置文件增加目标大小。如果写入的数据经常被读取，例如在轮廓分析中，建议使用128MB及更大的分区大小。

如果总输出很小但计算时间非常长，例如由于昂贵的UDF，您可能希望禁用AQE。在这种情况下，AQE可能会减少并行度并降低计算速度。

## 每个任务的核心数

此系列的配置文件配置spark.task.cpus的值。

这控制了为每个任务分配的核心数。实际上，这应该很少需要覆盖。如果您想控制任务的并行度，应该查看执行器核心数。

## Arrow

使用这些配置文件启用或禁用Arrow以进行Pandas和PySpark数据框架之间的转换。要使用Arrow，请确保您的变换依赖于pyarrow包。

当使用Pandas数据框调用spark.createDataFrame()或toPandas()时，Spark必须序列化所有行以将它们从一种格式转换为另一种格式。对于大型数据框，这个过程很慢，可能会成为变换的瓶颈。在使用Pandas变换时，这种序列化在读取和写入数据时都会发生。

Arrow是一种更高效的序列化格式，可以显著加快这种转换（如Arrow网站↗所述）。

## Kubernetes

此系列的配置文件控制您的Spark任务执行的低级细节。

当使用与底层机器的CPU架构无关的库时，您可以使用配置文件强制Spark任务在特定架构上运行。请注意，某些环境只能访问具有AMD架构的机器；在这些环境中，使用ARM架构覆盖的任务将不会成功。

## 配置文件表

| 配置文件系列 | 配置文件名称 | Spark设置 |
| --- | --- | --- |
| 驱动核心数 | DRIVER_CORES_SMALL | spark.driver.cores: 1 |
| 驱动核心数 | DRIVER_CORES_MEDIUM | spark.driver.cores: 2 |
| 驱动核心数 | DRIVER_CORES_LARGE | spark.driver.cores: 4 |
| 驱动核心数 | DRIVER_CORES_EXTRA_LARGE | spark.driver.cores: 8 |
| 驱动核心数 | DRIVER_CORES_EXTRA_EXTRA_LARGE | spark.driver.cores: 16 |
| 驱动内存 | DRIVER_MEMORY_SMALL | spark.driver.memory: 3g |
| 驱动内存 | DRIVER_MEMORY_MEDIUM | spark.driver.memory: 6g; spark.driver.maxResultSize: 4g |
| 驱动内存 | DRIVER_MEMORY_LARGE | spark.driver.memory: 13g; spark.driver.maxResultSize: 8g |
| 驱动内存 | DRIVER_MEMORY_EXTRA_LARGE | spark.driver.memory: 27g; spark.driver.maxResultSize: 16g |
| 驱动内存 | DRIVER_MEMORY_EXTRA_EXTRA_LARGE | spark.driver.memory: 54g; spark.driver.maxResultSize: 32g |
| 驱动内存开销 | DRIVER_MEMORY_OVERHEAD_SMALL | spark.driver.memoryOverhead: 1g |
| 驱动内存开销 | DRIVER_MEMORY_OVERHEAD_MEDIUM | spark.driver.memoryOverhead: 2g |
| 驱动内存开销 | DRIVER_MEMORY_OVERHEAD_LARGE | spark.driver.memoryOverhead: 4g |
| 驱动内存开销 | DRIVER_MEMORY_OVERHEAD_EXTRA_LARGE | spark.driver.memoryOverhead: 8g |
| 驱动内存开销 | DRIVER_MEMORY_OVERHEAD_EXTRA_EXTRA_LARGE | spark.driver.memoryOverhead: 16g |
| 执行器核心数 | EXECUTOR_CORES_EXTRA_SMALL | spark.executor.cores: 1 |
| 执行器核心数 | EXECUTOR_CORES_SMALL | spark.executor.cores: 2 |
| 执行器核心数 | EXECUTOR_CORES_MEDIUM | spark.executor.cores: 4 |
| 执行器核心数 | EXECUTOR_CORES_LARGE | spark.executor.cores: 6 |
| 执行器核心数 | EXECUTOR_CORES_EXTRA_LARGE | spark.executor.cores: 8 |
| 执行器内存 | EXECUTOR_MEMORY_EXTRA_SMALL | spark.executor.memory: 3g; spark.executor.memoryOverhead: 768m |
| 执行器内存 | EXECUTOR_MEMORY_SMALL | spark.executor.memory: 6g; spark.executor.memoryOverhead: 1536m |
| 执行器内存 | EXECUTOR_MEMORY_MEDIUM | spark.executor.memory: 13g; spark.executor.memoryOverhead: 2g |
| 执行器内存 | EXECUTOR_MEMORY_LARGE | spark.executor.memory: 27g; spark.executor.memoryOverhead: 3g |
| 执行器内存堆外 | EXECUTOR_MEMORY_OFFHEAP_FRACTION_MINIMUM | 用于堆外内存的份额（必须设置一个“执行器内存”配置文件）：30% |
| 执行器内存堆外 | EXECUTOR_MEMORY_OFFHEAP_FRACTION_LOW | 用于堆外内存的份额（必须设置一个“执行器内存”配置文件）：50% |
| 执行器内存堆外 | EXECUTOR_MEMORY_OFFHEAP_FRACTION_MODERATE | 用于堆外内存的份额（必须设置一个“执行器内存”配置文件）：70% |
| 执行器内存堆外 | EXECUTOR_MEMORY_OFFHEAP_FRACTION_HIGH | 用于堆外内存的份额（必须设置一个“执行器内存”配置文件）：80% |
| 执行器内存堆外 | EXECUTOR_MEMORY_OFFHEAP_FRACTION_MAXIMUM | 用于堆外内存的份额（必须设置一个“执行器内存”配置文件）：90% |
| 执行器内存开销 | EXECUTOR_MEMORY_OVERHEAD_SMALL | spark.executor.memoryOverhead: 1g |
| 执行器内存开销 | EXECUTOR_MEMORY_OVERHEAD_MEDIUM | spark.executor.memoryOverhead: 2g |
| 执行器内存开销 | EXECUTOR_MEMORY_OVERHEAD_LARGE | spark.executor.memoryOverhead: 4g |
| 执行器内存开销 | EXECUTOR_MEMORY_OVERHEAD_EXTRA_LARGE | spark.executor.memoryOverhead: 8g |
| 执行器数量 | KUBERNETES_NO_EXECUTORS | spark.kubernetes.local.submission: true; spark.sql.shuffle.partitions: 1 |
| 执行器数量 | NUM_EXECUTORS_1 | spark.executor.instances: 1; spark.dynamicAllocation.maxExecutors: 1 |
| 执行器数量 | NUM_EXECUTORS_2 | spark.executor.instances: 2; spark.dynamicAllocation.maxExecutors: 2 |
| 执行器数量 | NUM_EXECUTORS_4 | spark.executor.instances: 4; spark.dynamicAllocation.maxExecutors: 4 |
| 执行器数量 | NUM_EXECUTORS_8 | spark.executor.instances: 8; spark.dynamicAllocation.maxExecutors: 8 |
| 执行器数量 | NUM_EXECUTORS_16 | spark.executor.instances: 16; spark.dynamicAllocation.maxExecutors: 16 |
| 执行器数量 | NUM_EXECUTORS_32 | spark.executor.instances: 32; spark.dynamicAllocation.maxExecutors: 32 |
| 执行器数量 | NUM_EXECUTORS_64 | spark.executor.instances: 64; spark.dynamicAllocation.maxExecutors: 64 |
| 执行器数量 | NUM_EXECUTORS_128 | spark.executor.instances: 128; spark.dynamicAllocation.maxExecutors: 128 |
| 执行器数量 | NUM_EXECUTORS_256 | spark.executor.instances: 256; spark.dynamicAllocation.maxExecutors: 256 |
| 执行器数量 | NUM_EXECUTORS_512 | spark.executor.instances: 512; spark.dynamicAllocation.maxExecutors: 512 |
| 任务CPU数量 | TASK_CPUS_2 | spark.task.cpus: 2 |
| 任务CPU数量 | TASK_CPUS_4 | spark.task.cpus: 4 |
| 动态分配 | DYNAMIC_ALLOCATION_DISABLED | spark.dynamicAllocation.enabled: false |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED | spark.dynamicAllocation.enabled: true |
| 动态分配 | DYNAMIC_ALLOCATION_MIN_2 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 2 |
| 动态分配 | DYNAMIC_ALLOCATION_MIN_4 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 4 |
| 动态分配 | DYNAMIC_ALLOCATION_MIN_8 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 8 |
| 动态分配 | DYNAMIC_ALLOCATION_MIN_16 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 16 |
| 动态分配 | DYNAMIC_ALLOCATION_MAX_8 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.maxExecutors: 8 |
| 动态分配 | DYNAMIC_ALLOCATION_MAX_16 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.maxExecutors: 16 |
| 动态分配 | DYNAMIC_ALLOCATION_MAX_32 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.maxExecutors: 32 |
| 动态分配 | DYNAMIC_ALLOCATION_MAX_64 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.maxExecutors: 64 |
| 动态分配 | DYNAMIC_ALLOCATION_MAX_128 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.maxExecutors: 128 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_1_2 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 1; spark.dynamicAllocation.maxExecutors: 2 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_2_4 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 2; spark.dynamicAllocation.maxExecutors: 4 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_4_8 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 4; spark.dynamicAllocation.maxExecutors: 8 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_8_16 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 8; spark.dynamicAllocation.maxExecutors: 16 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_16_32 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 16; spark.dynamicAllocation.maxExecutors: 32 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_32_64 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 32; spark.dynamicAllocation.maxExecutors: 64 |
| 动态分配 | DYNAMIC_ALLOCATION_ENABLED_64_128 | spark.dynamicAllocation.enabled: true; spark.dynamicAllocation.minExecutors: 64; spark.dynamicAllocation.maxExecutors: 128 |
| 动态分配 | DYNAMIC_ALLOCATION_FAST_SCALE_DOWN | spark.dynamicAllocation.executorIdleTimeout: 10s |
| 动态分配 | DYNAMIC_ALLOCATION_SLOW_SCALE_UP_2M | spark.dynamicAllocation.schedulerBacklogTimeout: 2m |
| Shuffle分区 | SHUFFLE_PARTITIONS_SMALL | spark.sql.shuffle.partitions: 20 |
| Shuffle分区 | SHUFFLE_PARTITIONS_MEDIUM | spark.sql.shuffle.partitions: 200 |
| Shuffle分区 | SHUFFLE_PARTITIONS_LARGE | spark.sql.shuffle.partitions: 2000 |
| Shuffle分区 | SHUFFLE_PARTITIONS_EXTRA_LARGE | spark.sql.shuffle.partitions: 20000 |
| 自适应查询执行 | ADAPTIVE_ENABLED | spark.sql.adaptive.enabled: true |
| 自适应查询执行 | ADAPTIVE_DISABLED | spark.sql.adaptive.enabled: false |
| 自适应查询执行 | ADVISORY_PARTITION_SIZE_MEDIUM | spark.sql.adaptive.enabled: true; spark.sql.adaptive.shuffle.targetPostShuffleInputSize: 128MB |
| 自适应查询执行 | ADVISORY_PARTITION_SIZE_LARGE | spark.sql.adaptive.enabled: true; spark.sql.adaptive.shuffle.targetPostShuffleInputSize: 256MB |
| RPC消息大小 | RPC_MESSAGE_MAX_SIZE_512M | spark.rpc.message.maxSize: 512 |
| RPC消息大小 | RPC_MESSAGE_MAX_SIZE_1G | spark.rpc.message.maxSize: 1024 |
| RPC消息大小 | RPC_MESSAGE_MAX_SIZE_MAX | spark.rpc.message.maxSize: 2047 |
| 传统 | LEGACY_ALLOW_UNTYPED_SCALA_UDF | spark.sql.legacy.allowUntypedScalaUDF: true |
| 传统 | LEGACY_ALLOW_NEGATIVE_DECIMAL_SCALE | spark.sql.legacy.allowNegativeScaleOfDecimal: true |
| 传统 | LEGACY_ALLOW_HASH_ON_MAPTYPE | spark.sql.legacy.allowHashOnMapType: true |
| 传统 | LEGACY_NAME_NON_STRUCT_GROUPING_KEY_AS_VALUE | spark.sql.legacy.dataset.nameNonStructGroupingKeyAsValue: true |
| 传统 | LEGACY_ARRAY_EXISTS_NULL_HANDLING | spark.sql.legacy.followThreeValuedLogicInArrayExists: false |
| 传统 | LEGACY_ALLOW_AMBIGUOUS_SELF_JOIN | `spark.sql.analyzer.failAmbiguousSelfJoin: false |
