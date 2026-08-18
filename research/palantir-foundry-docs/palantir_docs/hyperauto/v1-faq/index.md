来源: https://palantir.com/docs/zh/foundry/hyperauto/v1-faq/

# HyperAuto V1 常见问题

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# HyperAuto V1 常见问题

## 一般使用技巧和指导

- 我可以在 SDDI 仓库中调试和预览代码吗？
- 我可以配置一个自动添加新表的计划吗？
- 我的一个表/派生元素由于MODULE_UNREACHABLE出错，我该怎么办？
- 我将表<TABLE_NAME>添加到我的管道中，但当我尝试搭建我的管道时，出现AssertionError: 0 instances of <TABLE_NAME> found in 'objects' metadata table出错
- 如果我在 Bellhop 配置文件中添加新表，是否需要增加语义版本？
- 我可以禁用 SDDI 仓库生成的一些中间阶段吗？
### 我可以在 SDDI 仓库中调试和预览代码吗？

可以，您可以在 SDDI 仓库中调试和预览代码。在 SDDI 仓库中，导航到文件/transforms-bellhop/src/software_defined_data_integrations/transforms/pipeline_builder.py并从预览按钮中选择您要预览的变换。

### 我可以配置一个自动添加新表的计划吗？

一个 SDDI 仓库会生成一个名为BUILD的数据集，该数据集连接到仓库生成的所有最终数据集。为了确保所有新引入的表都被搭建，创建一个新的完整搭建计划（包括上游数据集），以这个BUILD数据集为目标。智能调度器将仅为原始数据已刷新的管道部分启动搭建。

### 我的一个表/派生元素由于MODULE_UNREACHABLE出错，我该怎么办？

MODULE_UNREACHABLE通常表示您的 Spark 环境中的 DRIVER_MEMORY 不足。您可以在 SourceConfig.yaml 文件中为选定的表应用 Spark 配置文件；详情请参阅配置参考。不要忘记首先将指派的配置文件导入到您的仓库配置中。

### 我将表<TABLE_NAME>添加到我的管道中，但当我尝试搭建我的管道时，出现AssertionError: 0 instances of <TABLE_NAME> found in 'objects' metadata table出错

确保在新表被引入并添加到您的 SDDI 管道后，重新运行元数据数据集objects、links、fields和diffs。

### 如果我在 Bellhop 配置文件中添加新表，是否需要增加语义版本？

不，在 Bellhop 配置文件中添加新表后，您不需要增加语义版本。但是，您需要重新搭建元数据数据集objects、links、fields和diffs。

### 我可以禁用 SDDI 仓库生成的一些中间阶段吗？

可以。可以通过使用PipelineConfig 文件中的参数来禁用外键生成、丰富阶段和重命名阶段。需要增加deploymentSemanticVersion以使更改生效。

禁用任何或所有这些步骤将导致数据架构后果，并可能导致数据的下游使用中断。
