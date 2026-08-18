来源: https://palantir.com/docs/zh/foundry/transforms-python/velox-overview/

# 使用Velox加速Spark

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用Velox加速Spark

Spark加速是一种利用低级硬件优化来提高Spark任务性能的技术。通过使用平台特定的功能，本地加速旨在显著减少处理大规模数据工作负载所需的时间，从而实现更快的任务执行和资源利用率的提高。

Velox ↗是一个可重用的、高性能、低级数据处理库，提供了一组用于搭建高性能数据处理系统的原语。它被设计为用于搭建高级数据处理系统的基础，并在Foundry中用于加速Spark任务。

阅读更多关于Foundry中的本地加速。

## 快速开始

Spark加速可以用于任何现有的Spark管道。您无需对逻辑进行任何更改。

要在Python变换管道中使用本地加速，您必须完成以下步骤：

- 升级您的Python代码库到最新版本。
- 配置堆外内存配置文件。
- 启用VELOX后端，如以下代码片段所示：
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
from transforms.api import configure, ComputeBackend, Input, Output, transform_df


@configure(
    ["EXECUTOR_MEMORY_MEDIUM", "EXECUTOR_MEMORY_OFFHEAP_FRACTION_HIGH"],  # 配置执行器内存和内存使用率
    backend=ComputeBackend.VELOX)  # 指定计算后端为VELOX
@transform_df(
    Output('/Project/folder/output'),  # 指定输出数据路径
    source_df=Input('/Project/folder/input'),  # 指定输入数据路径
)
def compute(source_df):
    # 这里是计算逻辑的实现
    ...
```

## 配置加速 Spark 的内存

要优化本地加速的 Spark 项目，首先使用EXECUTOR_MEMORY_OFFHEAP_FRACTION_HIGH设置来配置堆外内存。此内存由 Velox 使用，Velox 处理一些 JVM 之外的任务。观察性能，并根据需要上下调整堆外内存。

要使用分数堆外配置文件，您还必须设置 EXECUTOR_MEMORY_X 配置文件。您的任务可能已经有这个配置。
