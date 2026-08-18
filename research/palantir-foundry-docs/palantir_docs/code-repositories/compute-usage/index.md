来源: https://palantir.com/docs/zh/foundry/code-repositories/compute-usage/

# 使用代码库计算用量

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用代码库计算用量

在代码库中运行搭建需要使用Foundry计算，这是一种以计算秒为单位的资源。本文档详细说明了搭建如何使用计算资源，并提供了关于在产品中调查和管理计算用量的信息。

在运行一个或多个数据集的变换搭建时，Foundry会将变换逻辑加载到其无服务器计算集群中并执行代码。搭建的长度和规模取决于代码的复杂性、输入和输出数据集的大小以及代码上设置的Spark计算配置文件。

在输入数据集上执行代码需要Foundry计算（以Foundry计算秒为单位测量），并在并行计算运行时需要Foundry存储来写入变换的输出。编写代码的行为不会产生计算用量；只有构建数据集才会产生计算用量。

## 测量Foundry计算

为代码库提供动力的变换引擎在后台使用并行计算，最常见的是在Spark可扩展计算框架中。代码库中的变换以任务在运行时使用的Foundry计算秒的总数来衡量。这些计算秒是在任务的整个持续时间内测量的，包括从输入数据集中读取、执行代码（包括I/O等待等操作）以及将输出数据集写回Foundry所花费的时间。

您可以配置变换以利用并行计算。计算秒是计算运行时间的度量，而不是墙钟时间，因此并行变换将在每个墙钟秒内产生多个计算秒。有关如何为代码库中的任务计算Foundry计算秒的并行计算的详细细分，请查看下面的示例。

在支付Foundry用量时，默认用量费率如下：

| vCPU / GPU | 用量费率 |
| --- | --- |
| vCPU | 1 |
| T4 GPU | 1.2 |

如果您与Palantir签订了企业合同，请在继续进行计算用量计算之前联系您的Palantir代表。

## 从代码库调查Foundry计算用量

用量信息可以在资源管理应用程序中找到，该应用程序允许深入查看用量指标。

虽然搭建是Foundry计算用量的驱动因素，但该用量会记录在与其关联的长期资源上。在数据集变换的情况下，资源是任务所实现的数据集（或一组数据集）。您可以在数据集详细信息选项卡下的资源用量指标中查看数据集的用量时间线。

请注意，对于产生多个输出数据集的变换，计算用量在所有数据集中平均分配。例如，如果一个变换任务创建了两个数据集，其中一个有五行，另一个有五百万行，Foundry计算秒的数量将在两个数据集之间平均分配。

## 了解Foundry计算用量的驱动因素

除非提前取消，否则代码库中的变换将运行，直到所有逻辑在所有数据上运行并将输出写回Foundry。影响此运行时间的两个主要因素是(1) 输入数据的大小和(2) 变换逻辑执行的计算操作的复杂性。

- 具有较大输入数据量的任务需要比具有相同逻辑的较小输入数据量的任务更多的计算。例如，一个在100GB数据上进行列处理的任务将使用比在10GB数据上进行相同处理的任务更多的Foundry计算秒。
- 在数据上执行更复杂操作的任务需要比执行相对较少操作的任务更多的计算。这有时被称为“任务复杂性”。作为一个基本示例，考虑两个数学运算之间的操作数量，5 * 5和5!。5 * 5是一个乘法运算。5!等于5 * 4 * 3 * 2 *1（四个乘法运算），这比5 * 5示例的复杂性高出一倍。随着任务变得更复杂，如聚合、合并或机器学习算法，任务在数据上必须完成的操作数量可能会增加。
- 作为一个基本示例，考虑两个数学运算之间的操作数量，5 * 5和5!。5 * 5是一个乘法运算。5!等于5 * 4 * 3 * 2 *1（四个乘法运算），这比5 * 5示例的复杂性高出一倍。随着任务变得更复杂，如聚合、合并或机器学习算法，任务在数据上必须完成的操作数量可能会增加。
## 使用代码库管理Foundry计算用量

对于每个任务，您可以查看驱动任务性能和计算用量的基本计算指标。有关更多详细信息，请查看了解Spark详情。

在一个任务中，Foundry计算秒由并行执行器的大小和数量驱动。这些设置都是可完全配置的。查看Spark计算配置文件文档以了解如何为每个任务设置。执行器的大小由其内存和vCPU数量决定。增加的vCPU和每个执行器的内存增加将增加该执行器产生的计算秒。

同时任务的数量由配置的执行器数量及其相应的vCPU数量驱动。如果没有指定配置覆盖，变换将使用默认的Spark配置文件。结果数据集的Foundry存储由创建的数据集的大小驱动。

最终，具有不同逻辑的任务可以通过非常不同的操作数量实现相同的结果。

### 优化代码以管理用量

有多种方法可以优化您的代码并管理任务使用的计算秒。此部分提供了关于常用优化技术的更多信息链接。

- Spark是Foundry采用的分布式集群计算框架，用于大多数类型的代码库批处理计算，提供了各种优化技术。了解更多关于优化Spark的信息。
- 在Spark中，您可以优化分区以加快搭建。最佳分区数量取决于行数、列数、列类型和内容。我们建议每128 MB数据集大小约一个分区的比例。
- 增量计算是一种有效的执行变换以生成输出数据集的方法。通过利用变换的搭建历史，增量计算避免了每次运行变换时都需要重新计算整个输出数据集。了解更多关于Python中的增量变换。了解更多关于Java中的增量变换。
- 了解更多关于Python中的增量变换。
- 了解更多关于Java中的增量变换。
- 特别是对于小到中等大小的数据集，还有其他几种计算引擎在单节点应用程序的基准测试中性能持续超过Spark。因此，使用这些替代方案运行您的管道可以提高处理速度并减少计算消耗。为了充分利用这些选择，我们建议熟悉轻量级变换。
- 如果您的搭建是使用调度进行编排的，我们建议阅读我们的调度最佳实践以优化成本。
## 计算Foundry计算用量

### 用量示例1：标准内存

此示例演示了对于具有标准内存请求的静态分配任务，如何测量Foundry计算。

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
Driver profile:
    vCPUs: 1
    GiB_RAM: 6
Executor profile:
    vCPUs: 1
    GiB_RAM: 6
    Count: 4
Total Job Wall-Clock Runtime:
    120 seconds

计算
driver_compute_seconds = max(num_vcpu, GiB_RAM/7.5) * num_seconds
                       = max(1vcpu, 6gib/7.5gib) * 120sec
                       = 120 compute-seconds

executor_compute_seconds = num_executors * max(num_vcpu, GiB_RAM/7.5) * num_seconds
                         = 4 * max(1, 6/7.5) * 120sec
                         = 480 compute-seconds

total_compute_seconds = 120 + 480 = 600 compute-seconds
```

### 翻译与注释

- Driver profile: 驱动程序配置vCPUs: 虚拟CPU数量GiB_RAM: 内存大小，以GiB为单位
- vCPUs: 虚拟CPU数量
- GiB_RAM: 内存大小，以GiB为单位
- Executor profile: 执行器配置Count: 执行器数量
- Count: 执行器数量
- Total Job Wall-Clock Runtime: 总作业挂钟运行时间
#### 计算步骤

- driver_compute_seconds: 驱动程序的计算秒数使用max(num_vcpu, GiB_RAM/7.5)来决定计算资源的使用，以秒为单位
- 使用max(num_vcpu, GiB_RAM/7.5)来决定计算资源的使用，以秒为单位
- executor_compute_seconds: 执行器的计算秒数计算每个执行器的计算需求，乘以执行器数量
- 计算每个执行器的计算需求，乘以执行器数量
- total_compute_seconds: 总计算秒数将驱动程序和执行器的计算秒数相加，得到总的计算秒数
- 将驱动程序和执行器的计算秒数相加，得到总的计算秒数
```
### 使用示例 2：大内存

此示例演示了如何以较大内存请求测量静态分配任务的 Foundry Compute。
```markdown
Driver Profile:
    vCPUs: 2
    GiB_RAM: 6
Executor profile:
    vCPUs: 1
    GiB_RAM: 15
    Count: 4
Total Job Wall-Clock Runtime:
    120 seconds

计算:
driver_compute_seconds = max(num_vcpu, GiB_RAM/7.5) * num_seconds
                       = max(2vcpu, 6gib/7.5gib) * 120sec
                       = 240 compute-seconds

executor_compute_seconds = num_executors * max(num_vcpu, GiB_RAM/7.5) * num_seconds
                         = 4 * max(1, 15/7.5) * 120sec
                         = 960 compute-seconds

total_compute_seconds = driver_compute_seconds + executor_compute_seconds
                      = 240 + 960 = 1200 compute-seconds
```

### 代码解释：

- Driver Profile和Executor profile描述了计算任务的资源配置，其中包括虚拟CPU数量（vCPUs）和内存大小（GiB_RAM）。
- Total Job Wall-Clock Runtime给出了任务的总运行时间，单位为秒。
### 计算过程：

- driver_compute_seconds计算了Driver节点的总计算秒数。公式中使用max(num_vcpu, GiB_RAM/7.5)来选择CPU或内存中对计算影响最大的因素。
- executor_compute_seconds计算了Executor节点的总计算秒数。Executor的数量为4，每个Executor的计算负载也是通过max函数确定的。
- total_compute_seconds最后计算了整个任务的总计算秒数，将Driver和所有Executor的计算秒数相加得到最终结果。
### 使用示例3：动态执行器数量

此示例演示了如何衡量Foundry Compute在动态分配任务中的表现，其中部分任务执行时间使用两个执行器完成，其余任务时间使用四个执行器完成。

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
Driver Profile:
    vCPUs: 2
    GiB_RAM: 6
Executor profile:
    vCPUs: 1
    GiB_RAM: 6
    Count:
        min: 2
        max: 4
Total Job Wall-Clock Runtime:
    120 seconds:
        2 executors: 60 seconds
        4 executors: 60 seconds

计算:
driver_compute_seconds = max(num_vcpu, GiB_RAM/7.5) * num_seconds
                       = max(2vcpu, 6gib/7.5gib) * 120sec
                       = 240 compute-seconds

# 计算使用2个执行器时的计算秒数
2_executor_compute_seconds = num_executors * max(num_vcpu, GiB_RAM/7.5) * num_seconds
                           = 2 * max(1, 6/7.5) * 60sec
                           = 120 compute-seconds

# 计算使用4个执行器时的计算秒数
4_executor_compute_seconds = num_executors * max(num_vcpu, GiB_RAM/7.5) * num_seconds
                           = 4 * max(1, 6/7.5) * 60sec
                           = 240 compute-seconds

total_compute_seconds = driver_compute_seconds + 2_executor_compute_seconds + 4_executor_compute_seconds
                      = 240 + 120 + 240 = 600 compute-seconds
```

在这个代码中，我们计算了驱动程序和执行器在不同配置下的计算时间（以计算秒为单位）。其中，max(num_vcpu, GiB_RAM/7.5)用于选择 vCPU 数量和内存容量的最大值来计算每秒所需的计算能力。

### 使用示例 4: GPU 计算

此示例演示了如何为静态分配的任务测量 Foundry GPU 计算。

```
Driver profile:
    T4 GPU: 1
Executor profile:
    T4 GPU: 1
    Count: 4
Total Job Wall-Clock Runtime:
    120 seconds

计算：
driver_compute_seconds = num_gpu * gpu_usage_rate * num_seconds
                       = 1gpu * 1.2 * 120sec
                       = 144 compute-seconds
# 驱动程序计算时间：使用1个GPU，使用率为1.2，运行时间为120秒，总计算秒数为144。

executor_compute_seconds = num_executors * num_gpu * gpu_usage_rate * num_seconds
                         = 4 * 1 * 1.2 * 120sec
                         = 576 compute-seconds
# 执行程序计算时间：4个执行器，每个使用1个GPU，使用率为1.2，运行时间为120秒，总计算秒数为576。

total_compute_seconds = 144 + 576 = 720 compute-seconds
# 总计算时间：驱动程序和执行程序的计算秒数之和为720。
```
