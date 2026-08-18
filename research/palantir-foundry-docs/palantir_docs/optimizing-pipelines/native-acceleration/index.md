来源: https://palantir.com/docs/zh/foundry/optimizing-pipelines/native-acceleration/

# 原生加速

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 原生加速

您可以通过启用Velox ↗的原生加速来提高Spark的性能。

原生加速是一种利用低级硬件优化来提高批处理任务性能的技术。这些性能提升是通过将计算从Java虚拟机（JVM）语言转移到原生语言（如C++）实现的，这些语言被编译为机器代码并直接在机器的硬件上运行。通过使用平台特定的功能，原生加速旨在显著减少处理大规模数据工作负载所需的时间，从而加速任务执行并提高资源利用率。

原生加速可用于Python变换和Pipeline Builder。

## 搭建分析

您可以在Spark详情页面中对原生加速搭建进行基本分析。在查询计划选项卡下，选择物理计划；您将看到如下内容：

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
== Physical Plan ==
AdaptiveSparkPlan
+- == Final Plan ==
   Execute InsertIntoHadoopFsRelationCommand
   +- WriteFiles
      +- CollectMetrics
         +- VeloxColumnarToRowExec
            +- ^ ProjectExecTransformer
               +- ^ InputIteratorTransformer
                  +- ^ InputAdapter
                     +- ^ RowToVeloxColumnar
                        +- ^ HashAggregate
                           +- ^ VeloxColumnarToRowExec
                              +- ^ AQEShuffleRead
                                 +- ^ ShuffleQueryStage
                                    +- ColumnarExchange
                                       +- ^ ProjectExecTransformer
                                          +- ^ RowToVeloxColumnar
                                             +- * ColumnarToRow
                                                +- BatchScan parquet
```

这段代码展示了一个物理计划（Physical Plan），主要用于大数据处理框架Spark中的执行计划分析。下面是对每个步骤的简单解释：

- AdaptiveSparkPlan：自适应执行计划，用于动态调整执行计划以优化性能。
- Execute InsertIntoHadoopFsRelationCommand：执行插入命令，将数据写入Hadoop文件系统。
- WriteFiles：将数据写入文件。
- CollectMetrics：收集执行过程中的指标。
- VeloxColumnarToRowExec：将列存储格式转换为行存储格式。
- ProjectExecTransformer：执行列的选择和计算。
- InputIteratorTransformer：处理输入迭代器。
- InputAdapter：适配输入数据。
- RowToVeloxColumnar：将行存储格式转换为列存储格式。
- HashAggregate：执行哈希聚合操作。
- AQEShuffleRead：自适应查询执行（AQE）中的Shuffle读取。
- ShuffleQueryStage：处理Shuffle的查询阶段。
- ColumnarExchange：在不同执行节点之间进行列式数据交换。
- ColumnarToRow：将列式数据转换为行式数据。
- BatchScan parquet：批量扫描Parquet格式的数据。
这些步骤组成了一个完整的数据处理流程，展示了数据从读取、转换、聚合到最终写入的全过程。
虽然与传统的Spark查询计划大致相似，但您会注意到几个关键区别。代替ProjectExec节点的是ProjectExecTransformer。这意味着操作将在Velox查询引擎中本地执行。查询计划的所有卸载节点将在树中标记为^符号。本地执行的块夹在RowToVeloxColumnar和VeloxColumnarToRowExec之间。这些节点负责将Spark数据集转换为Arrow DataFrames，反之亦然。这种序列化/反序列化有很大的成本。

通常有两个模式表明本地加速性能不佳：

- 用^符号表示的本地执行节点的百分比很小。
- 大量的RowToVeloxColumnar和VeloxColumnarToRowExec节点导致高序列化开销。
如果性能不如预期，这种分析可能会有所帮助。对管道的小更改可能会对卸载的计算量产生很大影响。像检查点这样的功能可以用来手动将可以全部本地执行的搭建块组合在一起。

## 本地加速的实现和架构

Foundry的本地加速实现是基于Apache Gluten ↗项目构建的。Foundry本地加速利用Velox ↗查询引擎在运行时加速Spark任务。Velox用C++编写，并且专为数据库加速而设计 ↗，提供开发者API在Arrow DataFrames ↗上运行操作级别的操作。Gluten提供了将Spark运行时与Velox绑定所需的“粘合剂”。

在此设置中，管道首先生成一个正常搭建的Spark查询计划（一个没有本地加速的计划）。然后在计划上应用附加的优化规则，以确定查询的部分是否可以使用Velox运行。这个决定基于Velox是否有等效实现以及Gluten中是否存在实现的映射。查询可以在操作级别卸载：这大致对应于SQL语句，如SELECT、FILTER或JOIN。任何可以卸载的查询计划部分都会在此阶段标记。

一旦计划步骤完成，查询将通过正常的Spark引擎执行。这意味着所有任务调度、执行器编排和生命周期管理都按正常进行。区别在于，当执行器到达已标记为本地执行的查询计划部分时。如果发生这种情况，则不会调用Spark中的默认实现，而是调用Velox实现。

这种架构特别有利，因为它支持那些不能全部用Velox完成计算的查询。这是因为卸载决策是在操作级别而不是整个计划上做出的。支持的操作数量在不断增加，但用户编写的代码，如UDFs，永远无法卸载，因为不存在本地实现。

查看支持的操作符和表达式的完整列表 ↗

## 为什么本地加速更快？

Spark是用Scala编写的，一种JVM语言，并包含许多优化，例如代码生成 ↗以提高其性能。此外，JVM本身包含优化，如C2编译器 ↗，旨在尽可能利用许多平台特定的功能。然而，本地语言如C++继续提供更好的性能，主要有三个原因：

- 编译时优化:Java和Scala被编译为字节码，然后由JVM执行，而本地语言如C++直接编译为机器码。这允许C++编译器在编译时进行广泛的优化，从而显著减少运行时开销。相比之下，JVM语言依赖于即时（JIT）编译，这发生在执行期间，可能无法达到相同水平的优化，因为它必须在编译时间和快速启动之间取得平衡。
- 无垃圾回收（GC）:在C++中，内存管理是手动处理的，这消除了与垃圾回收（GC）相关的开销。在JVM语言中，GC过程可能会引入不可预测的暂停和开销，特别是在内存密集型应用程序中会影响性能。
- 直接硬件访问和矢量化API的可用性:C++提供对硬件功能和低级系统资源的直接访问，使开发人员能够利用平台特定的优化和矢量化API，如SSE、AVX和其他SIMD（单指令多数据）指令。这种直接访问允许进行精细调优的性能优化，而在JVM语言中，由于抽象层可能无法实现相同水平的硬件交互。
## 本地加速的内存配置注意事项

在Foundry中运行带有本地加速的Spark需要与正常批处理管道略有不同的配置。Spark支持使用堆外内存 ↗执行某些操作。堆外内存是不由JVM管理的内存，消除了GC的开销，从而提高了性能。默认情况下，我们在Foundry中不启用堆外内存，因为这样做可能会为管道引入额外的维护成本。启用堆外内存对于本地加速是必要的，因为Velox修改的数据帧必须是堆外的，以便原生进程可以访问。Foundry仍然需要足够的堆内内存来处理除Velox数据变换之外的所有内容（例如，编排、调度和搭建管理代码仍在JVM中运行），但理想情况下，大多数工作现在将在堆外执行。配置管道以使用本地加速在平衡堆内和堆外内存方面引入了额外的维护成本。
