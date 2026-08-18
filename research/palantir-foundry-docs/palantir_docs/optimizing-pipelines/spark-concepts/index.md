来源: https://palantir.com/docs/zh/foundry/optimizing-pipelines/spark-concepts/

# Spark 概念

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Spark 概念

## Spark 简介

什么是 Spark？

Spark 是一种分布式计算系统，在 Foundry 中用于大规模运行数据变换。它最初由加州大学伯克利分校的研究团队创建，随后在2000年代末被捐赠给 Apache 基金会。Foundry 允许您使用 Spark 作为基础计算层在大量数据上运行 SQL、Python、Java 和 Mesa 变换（Mesa 是一种专有的基于 Java 的 DSL）。

Spark 如何工作？

Spark 依赖于同时在多台计算机上分配任务以处理数据。这种过程允许同时跨用户和项目快速运行任务，使用的方法称为 MapReduce。这些计算机分为 drivers 和 executors。

- driver就像是您 Spark 任务的“指挥”。它负责将任务的工作分配给 executors。
- executor就像是您 Spark 任务的“工蜂”。它负责执行 driver 分配给它的任务部分的计算。这项工作被拆分为若干“分区”，每个 executor 被分配一些分区来运行您的代码。完成此任务后，它将返回 driver 并请求更多工作，直到任务完成。
- 每个 Spark 任务都有一些与之相关的变量，可以对其进行操作以创建最适合运行变换的 Spark 配置。每个 Spark 任务都需要在快速、轻松执行任务与运行该任务相关的成本和资源之间取得平衡。经验法则是，更多的 executors 和更多的内存应该会减少运行时间，同时也会增加成本。根据任务的特性，一些 drivers 和 executors 的组合和配置比其他的表现更好。（后面会详细讲解）Spark 配置是 Foundry 用于配置所述分布式计算资源（drivers 和 executors）所需的 CPU 核心数和内存的配置。
- 每个 Spark 任务都需要在快速、轻松执行任务与运行该任务相关的成本和资源之间取得平衡。
- 经验法则是，更多的 executors 和更多的内存应该会减少运行时间，同时也会增加成本。
- 根据任务的特性，一些 drivers 和 executors 的组合和配置比其他的表现更好。（后面会详细讲解）
- Spark 配置是 Foundry 用于配置所述分布式计算资源（drivers 和 executors）所需的 CPU 核心数和内存的配置。
- 每个 Spark 任务有 5 个可配置变量：Driver Cores：控制分配给 Spark driver 的 CPU 核心数Driver Memory：控制分配给 Spark driver 的内存量仅控制 JVM 内存。这不包括外部非 Spark 任务（例如对 Python 库的调用）所需的“堆外”内存Executor Cores：控制分配给每个 Spark executor 的 CPU 核心数，从而控制每个 executor 中同时运行的任务数Executor Memory：控制分配给每个 Spark executor 的内存量此内存在 executor 上运行的所有任务之间共享Number of Executors：控制请求运行任务的 executors 数量
- Driver Cores：控制分配给 Spark driver 的 CPU 核心数
- Driver Memory：控制分配给 Spark driver 的内存量仅控制 JVM 内存。这不包括外部非 Spark 任务（例如对 Python 库的调用）所需的“堆外”内存
- 仅控制 JVM 内存。这不包括外部非 Spark 任务（例如对 Python 库的调用）所需的“堆外”内存
- Executor Cores：控制分配给每个 Spark executor 的 CPU 核心数，从而控制每个 executor 中同时运行的任务数
- Executor Memory：控制分配给每个 Spark executor 的内存量此内存在 executor 上运行的所有任务之间共享
- 此内存在 executor 上运行的所有任务之间共享
- Number of Executors：控制请求运行任务的 executors 数量
- 所有内置 Spark 配置的列表可以在Spark 配置参考中找到。
## 调整 Spark 配置

- 您可能会遇到运行变换时的问题，这需要您调整 Spark 配置以创建一个自定义的非默认配置来启用您的特定任务。例如：您的任务可能需要更多内存。您的任务可能运行速度慢于应用案例所需。您可能会遇到导致任务完全出错的错误。
- 您的任务可能需要更多内存。
- 您的任务可能运行速度慢于应用案例所需。
- 您可能会遇到导致任务完全出错的错误。
- 要使用非默认 Spark 配置，首先需要将其导入到包含您变换的代码库中。此过程在Spark 配置使用的文档中有描述。导入后，可以按照应用变换配置文档中的指导为特定变换指派 Spark 配置。
- 导入后，可以按照应用变换配置文档中的指导为特定变换指派 Spark 配置。
### 何时从默认值修改您的 Spark 配置

- 在编辑 Spark 配置时的经验法则是，每次只增加一个变量，每次只提升一个级别。例如，仅通过调整 executor 内存并将其从EXECUTOR_MEMORY_SMALL提升到EXECUTOR_MEMORY_MEDIUM，然后在调整其他任何内容之前再次运行任务。这确保您不会通过过度分配资源给任务而产生不必要的成本。
- 例如，仅通过调整 executor 内存并将其从EXECUTOR_MEMORY_SMALL提升到EXECUTOR_MEMORY_MEDIUM，然后在调整其他任何内容之前再次运行任务。这确保您不会通过过度分配资源给任务而产生不必要的成本。
- 虽然后端默认值并不总是映射到特定的 Spark 配置，但它们通常由标记为 SMALL 的内置配置来近似。非 Python 变换的正确默认值是EXECUTOR_CORES_SMALL, EXECUTOR_MEMORY_SMALL, DRIVER_CORES_SMALL, DRIVER_MEMORY_SMALL, NUM_EXECUTORS_2Python 在调用运行在 JVM 之外的 Python 库时，可能需要更多的非 JVM 额外开销内存。
- 非 Python 变换的正确默认值是EXECUTOR_CORES_SMALL, EXECUTOR_MEMORY_SMALL, DRIVER_CORES_SMALL, DRIVER_MEMORY_SMALL, NUM_EXECUTORS_2
- Python 在调用运行在 JVM 之外的 Python 库时，可能需要更多的非 JVM 额外开销内存。
- 如果您在使用 Spark 任务时遇到任何问题，第一步是优化您的代码。如果您已尽可能优化但仍然有问题，请继续阅读特定建议。
- 如果您已尽可能优化但仍然有问题，请继续阅读特定建议。
- 如果您的任务成功但运行速度慢于您的应用案例所需：尝试增加 executor 数量——增加 executor 数量会增加可以并行运行的任务数量，从而提高性能（前提是任务足够并行），同时使用更多资源也会增加成本。您可以查看给定搭建的 Builds 应用页面，以帮助您确定增加 executor 数量是否可以帮助提高任务的速度。如果任务并发性没有接近 executor 数量，那么增加 executor 数量可能不会帮助改善运行时间。如果您通过将 executor 数量加倍没有获得超过 1/3 的运行时间减少，那么您可能有低效的代码（例如，从 Catalog 读取大量数据或向 Catalog 写入大量数据）。如果您将变换生成 6 分钟任务的 executor 数量加倍，它应该在 4 分钟或更短时间内运行。如果减少一半的 executor 数量使任务运行时间减少不足 50%（例如从 4 分钟到 6 分钟），您应该降低到较低的 executor 数量以节省资金，除非运行时间至关重要。可以对大配置（如 128 个或更多 executors）施加限制，以确保只有经过批准的应用案例可以使用大量资源。如果您达到限制并需要更高，请联系您的 Palantir 代表。Executors 在启动期间通常以每分钟约 10 的速度累积到 driver。这意味着短时间任务中具有高 executor 数量的任务应使用较低的 executor 数量以减少系统中的颠簸。例如，任何少于 10 分钟的 64-executor 任务应降至 32 个 executors，因为当任务获取到所有的计算资源时，任务几乎已完成。
- 尝试增加 executor 数量——增加 executor 数量会增加可以并行运行的任务数量，从而提高性能（前提是任务足够并行），同时使用更多资源也会增加成本。您可以查看给定搭建的 Builds 应用页面，以帮助您确定增加 executor 数量是否可以帮助提高任务的速度。如果任务并发性没有接近 executor 数量，那么增加 executor 数量可能不会帮助改善运行时间。
- 您可以查看给定搭建的 Builds 应用页面，以帮助您确定增加 executor 数量是否可以帮助提高任务的速度。如果任务并发性没有接近 executor 数量，那么增加 executor 数量可能不会帮助改善运行时间。
- 如果您通过将 executor 数量加倍没有获得超过 1/3 的运行时间减少，那么您可能有低效的代码（例如，从 Catalog 读取大量数据或向 Catalog 写入大量数据）。如果您将变换生成 6 分钟任务的 executor 数量加倍，它应该在 4 分钟或更短时间内运行。如果减少一半的 executor 数量使任务运行时间减少不足 50%（例如从 4 分钟到 6 分钟），您应该降低到较低的 executor 数量以节省资金，除非运行时间至关重要。
- 如果您将变换生成 6 分钟任务的 executor 数量加倍，它应该在 4 分钟或更短时间内运行。
- 如果减少一半的 executor 数量使任务运行时间减少不足 50%（例如从 4 分钟到 6 分钟），您应该降低到较低的 executor 数量以节省资金，除非运行时间至关重要。
- 可以对大配置（如 128 个或更多 executors）施加限制，以确保只有经过批准的应用案例可以使用大量资源。如果您达到限制并需要更高，请联系您的 Palantir 代表。
- Executors 在启动期间通常以每分钟约 10 的速度累积到 driver。这意味着短时间任务中具有高 executor 数量的任务应使用较低的 executor 数量以减少系统中的颠簸。例如，任何少于 10 分钟的 64-executor 任务应降至 32 个 executors，因为当任务获取到所有的计算资源时，任务几乎已完成。
- 如果您的任务出错并且您收到 OOM（内存不足）错误或“Shuffle stage 出错”错误，而这与代码逻辑错误原因无关：尝试将 executor 内存从 SMALL 增加到 MEDIUM。这应该有助于处理大量数据。如果您认为需要从 MEDIUM 调整到 LARGE，请向专家寻求帮助。如有可能，请考虑简化您的变换，如故障排除指南中所述。
- 尝试将 executor 内存从 SMALL 增加到 MEDIUM。这应该有助于处理大量数据。如果您认为需要从 MEDIUM 调整到 LARGE，请向专家寻求帮助。如有可能，请考虑简化您的变换，如故障排除指南中所述。
- 如果您认为需要从 MEDIUM 调整到 LARGE，请向专家寻求帮助。如有可能，请考虑简化您的变换，如故障排除指南中所述。
- 如果将大量数据收集回 driver 或执行大型广播合并：尝试增加 driver 内存。
- 尝试增加 driver 内存。
- 如果您看到类似于“Spark 模块停止响应”的错误，并且输入数据集包含许多文件：首先尝试增加 driver 内存。如果在增加 driver 内存后错误仍然存在，请将 driver 核心数增加到 2。
- 首先尝试增加 driver 内存。
- 如果在增加 driver 内存后错误仍然存在，请将 driver 核心数增加到 2。
- 如果您有读取许多文件并遇到 GC（垃圾回收）问题的变换：尝试将 driver 核心数增加到 2。
- 尝试将 driver 核心数增加到 2。
## 推荐最佳实践

### 针对管理员

- 当应用案例结束时，删除为此应用案例创建的所有自定义配置。这将减少混乱，避免创建太多自定义配置导致混淆。
- 这将减少混乱，避免创建太多自定义配置导致混淆。
- 设置权限，使资源密集型配置仅在管理员显式授权后才可访问。例如，NUM_EXECUTORS_32和EXECUTOR_MEMORY_LARGE（及以上）应仅在请求和批准该请求后可用。除EXECUTOR_CORES_SMALL之外的所有 executor 核心值都应严格控制（因为这是增加计算能力的隐蔽方式，我们更倾向于在几乎所有情况下引导用户到 NUM_EXECUTORS 配置）。
- 例如，NUM_EXECUTORS_32和EXECUTOR_MEMORY_LARGE（及以上）应仅在请求和批准该请求后可用。
- 除EXECUTOR_CORES_SMALL之外的所有 executor 核心值都应严格控制（因为这是增加计算能力的隐蔽方式，我们更倾向于在几乎所有情况下引导用户到 NUM_EXECUTORS 配置）。
### 针对调整 Spark 配置

- 尽量坚持使用默认（即无）配置。这将减少成本和混乱。
- 这将减少成本和混乱。
- 如果您无法使用默认配置，尽量坚持使用内置配置。
- 在设置新配置时，用您的名字或应用案例的名字保存它。这将提高组织性，并确保该配置在未经您同意的情况下不会被其他用户或项目使用。否则，您可能会得到太多配置的列表，而不知道哪个配置是为哪个用途设置的。
- 这将提高组织性，并确保该配置在未经您同意的情况下不会被其他用户或项目使用。
- 否则，您可能会得到太多配置的列表，而不知道哪个配置是为哪个用途设置的。
- 当增加内存时，任何超出 8:1 资源（由EXECUTOR_CORES_SMALL和EXECUTOR_MEMORY_MEDIUM的组合指示）的请求应得到管理员的批准。阻止EXECUTOR_CORES_EXTRA_SMALL和EXECUTOR_MEMORY_LARGE。如果用户请求这些，通常是优化不佳的迹象或关键工作流。
- 配置应可分离。每个配置应仅影响一个 Spark 变量（或一个逻辑组合的 Spark 变量）。例如，在创建新配置时，仅更改 executor 数量，然后在不更改其他变量如 executor 内存或 driver 内存的情况下进行尝试。
- 例如，在创建新配置时，仅更改 executor 数量，然后在不更改其他变量如 executor 内存或 driver 内存的情况下进行尝试。
- 除非在特殊情况下许多 Spark 任务在同一 Spark 模块中同时运行，否则不应覆盖 driver cores 的默认配置。
- 默认的 executor cores 配置很少应被覆盖。
- 任何运行时间少于 15 分钟的任务不应使用 64 个 executors。如此多的 executors 会将大部分时间花在简单的启动上。
- 如此多的 executors 会将大部分时间花在简单的启动上。
- 每当创建自定义配置并运行时，请在Spark 详情中查看事后性能。Spark 详情将跟踪任务的性能速度并详细说明并发任务。
- Spark 详情将跟踪任务的性能速度并详细说明并发任务。