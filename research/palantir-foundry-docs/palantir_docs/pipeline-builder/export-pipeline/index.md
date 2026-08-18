来源: https://palantir.com/docs/zh/foundry/pipeline-builder/export-pipeline/

# 导出管道代码

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 导出管道代码

在Pipeline Builder中搭建时，您可以将管道代码导出到现有的Java变换库。当您需要访问特定的Java库时，此导出功能非常有用。

在导出过程中，您的管道将被转换为Java变换代码，然后推送到目标库。请在此过程中注意以下事项：

- 目标库指定分支上的任何现有代码或文件将被删除。
- Java变换代码的新输出可能并不总是与Pipeline Builder管道的输出完全相同。有关详细信息，请参阅将Pipeline Builder导出到Java变换。
- 此过程不可逆，这意味着对Java变换代码的任何更改都无法推送回Pipeline Builder管道。
- 某些管道变换无法转换为代码。
打开您想要导出的管道，导航到设置 > 导出代码。将出现一个弹出窗口，您可以在其中搜索并选择现有的目标Java变换库。然后，选择导出来自的Pipeline Builder分支，并可选择在目标库中创建一个新分支。

管道导出将在您的库中以PipelineLogic.java和PipelineOutputs.java文件的形式在transforms-java/src/main/java/com/中可用。

## 将Pipeline Builder导出到Java变换

将Pipeline Builder管道导出为Java代码时，重要的是要认识到新输出可能并不总是与原始管道输出相同。原因有以下几点：

- 代码生成的限制：某些功能（如用户定义函数（UDFs）和LLM调用）不受支持，需要手动实现。这将在生成的代码中显示为todo。
- 与原生Spark的差异：Pipeline Builder中的某些表达式经过优化并以不同于原生Spark的方式实现，以提高可靠性和更好的错误处理。我们无法导出这些自定义优化，必须恢复为原生Spark表达式，这在某些边缘情况下可能表现不同。
代码生成中所有其他受支持的表达式都根据Spark测试用例进行了验证。导出到Java变换应被视为一个起始点，用户可以手动验证以确保完全准确。
