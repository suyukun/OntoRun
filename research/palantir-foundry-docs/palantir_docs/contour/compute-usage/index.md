来源: https://palantir.com/docs/zh/foundry/contour/compute-usage/

# 使用Contour计算用量

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 使用Contour计算用量

在Foundry中的数据上运行Contour工作流程需要使用Foundry计算资源，这是一种以计算秒为单位衡量的资源。本文档详细说明了Contour如何使用计算资源，并提供了在产品中调查和管理计算用量的信息。

每个显示数据的Contour面板都由一个Contour后端查询支持。Foundry通过在自动扩展的Spark集群上执行查询来为Contour查询提供服务。Contour查询的计算秒数完全基于查询在执行时实际使用的计算秒数来衡量。然而，在交互模式中，所有Contour分析的计算资源都是“始终开启”的，以提供更快的响应；这意味着每个单独的交互查询使用计算秒数的速度比批处理计算更快。

查询使用的资源量取决于许多因素，例如输入数据集的大小和设计以及查询的复杂性（如所用的Contour面板）。

## 如何衡量计算

Contour使用Foundry的并行计算后端在Foundry数据上执行查询。因此，Contour中的计算是通过以下公式来衡量的。

注意，默认的interactive_contour_usage_rate是15。这是Contour基于始终开启的并行计算框架使用计算的速率。如果您与Palantir签订了企业合同，请在进行计算用量计算之前联系您的Palantir代表。

```
Copied!1
2
3
4
5
# 计算总的计算秒数
# total_compute_seconds 表示总的计算秒数
# contour_usage_rate 表示使用率系数
# driver_compute_seconds 和 executor_compute_seconds 分别表示驱动程序和执行程序的计算秒数
total_compute_seconds = contour_usage_rate * (driver_compute_seconds + executor_compute_seconds)
```

### 互动Contour使用

Contour的“始终准备好”执行系统旨在对终端用户的临时查询做出反应。Foundry计算秒中Contour查询的成本基于在Spark集群上执行查询所需的时间和执行查询时使用的核心数量。核心数量通过查看查询在其调度的Spark应用程序中的份额来得出。

在互动模式下，每次创建或更新Contour面板时都会使用计算。这包括影响Contour路径中给定面板下游面板的“级联”计算。例如，以下操作将在Contour分析中使用计算：

- 创建新面板（可能影响所有下游面板）
- 更新面板（可能影响所有下游面板）
- 点击路径顶部的更新数据
### 批量Contour使用

Contour路径可以“另存为”数据集。这将Contour后端生成的底层代码保存到数据集任务规范中。然后可以按计划或临时运行此数据集搭建。这些数据集任务被测量为批量任务，并且不会像互动Contour使用那样产生“始终开启”开销。

Contour批量数据集被测量为通用的并行化批量计算，类似于通过代码存储库和代码工作簿创建和更新的数据集。这些批量计算以与其他批量计算相同的速率使用计算。

## 调查Contour使用情况

来自Contour的互动使用始终附加到触发其的分析中。对于给定的Contour分析，所有互动计算都附加到分析资源本身。

运行计算的单个面板会产生可从搭建应用程序中查看的Spark指标。这可以从每个面板的上下文菜单中的查看任务部分访问。来自Contour的批量计算使用附加到计算生成的数据集中，类似于代码存储库和代码工作簿。对于互动和批量计算，您可以在资源管理应用程序中查看您的总体使用情况。

## 理解使用驱动因素

Contour运行在Spark计算框架上，因此受两个主要因素影响：数据规模和查询复杂性（运行在数据上的操作数量和类型）。必须在数据上执行的操作越多，后端必须使用的计算量就越大以计算结果。然而，由于某些操作比其他操作昂贵得多，可以通过添加操作来减少总体使用量（例如，在昂贵操作之前添加筛选）。

数据上的操作数量受Contour路径中面板数量的影响。路径中更远的面板依赖于路径中较早面板的输出。在路径中添加新面板可以更改通过路径发送的数据，要求重新计算面板并增加计算量。

拥有更多Contour用户可能会因查询增加而产生更多计算。然而，Contour有两个功能可以减少多用户的计算使用：检查点和缓存。

- Contour检查点由Contour后端自动管理。检查点允许Contour快速提供路径中较远位置的查询结果。这可以随着时间的推移减少较大Contour路径的计算，但不会完全消除计算。
- Contour还缓存相同数据上的相同查询结果。这意味着如果两个用户连续打开相同的Contour分析，计算只会运行一次。这允许仪表盘更有效地提供服务，并减少用户数量对计算使用的影响。请注意，更改输入数据或更改参数将不允许使用缓存，但对相同输入数据和参数的未来计算将再次使用缓存。
- 请注意，更改输入数据或更改参数将不允许使用缓存，但对相同输入数据和参数的未来计算将再次使用缓存。
## 使用Contour管理使用情况

优化分析和输入数据集可以减少成本和分析时间。了解更多关于Contour优化的信息。

## 计算使用情况

Contour遵循与平台中其他基于Spark的产品（如代码存储库）相同的Spark测量原则。通过基于成本的路由，Contour将自动优化后端驱动程序和执行器的大小，以有效满足数据大小和查询类型的需求。

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
 Example Contour Driver Size:
    num_vcpu: 2  # 虚拟CPU数量: 2
    gib_ram: 11  # RAM大小: 11 GiB
 Example Contour Executor Size:
    num_vcpu: 2  # 虚拟CPU数量: 2
    gib_ram: 12  # RAM大小: 12 GiB
    num_executors: 3  # 执行器数量: 3
 Query Duration: 3 seconds  # 查询持续时间: 3秒
 Interactive Contour Usage Rate: 15  # 交互式轮廓使用率: 15
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
15
16
17
18
driver_compute_seconds = interactive_usage_rate * driver_compute_seconds
                       = 15 * max(2vcpu, 11gib / 7.5gib) * 3sec
                       = 15 * 2 * 3 = 90 compute-seconds
                       # 驱动计算秒数 = 交互使用率 * 驱动计算秒数
                       # 计算过程：交互使用率为15，选择2个虚拟CPU（vcpu）和11gib内存除以7.5gib之间的最大值，乘以3秒
                       # 结果：90计算秒数

executor_compute_seconds = interactive_usage_rate * executor_compute_seconds
                         = 15 * max(2vcpu, 12gib / 7.5gib) * 3sec * 3executors
                         = 15 * 2 * 3 * 3 = 270 compute-seconds
                         # 执行器计算秒数 = 交互使用率 * 执行器计算秒数
                         # 计算过程：交互使用率为15，选择2个虚拟CPU（vcpu）和12gib内存除以7.5gib之间的最大值，乘以3秒，再乘以3个执行器
                         # 结果：270计算秒数

total_compute_seconds = driver_compute_seconds + executor_compute_seconds
                      = 90 compute-seconds + 270 compute-seconds = 360 compute-seconds
                      # 总计算秒数 = 驱动计算秒数 + 执行器计算秒数
                      # 结果：360计算秒数
```
