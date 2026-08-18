来源: https://palantir.com/docs/zh/foundry/transforms-common/local-preview/

# 在本地开发中预览变换

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在本地开发中预览变换

在使用VS Code进行本地开发中预览变换有两种主要方法：

- 使用适用于Visual Studio Code的Palantir扩展（Beta版）预览变换
- 使用基于Gradle的本地预览
## 使用适用于Visual Studio Code的Palantir扩展（Beta版）进行预览（仅限Python）

适用于Visual Studio Code的Palantir扩展支持本地预览功能。有关安装说明，请参阅扩展文档。一旦扩展安装完成并且环境已准备好进行预览，您的变换应自动在预览选项卡中被发现，如下所示。

## 基于Gradle的Java和Python本地预览

本节详细介绍了在本地开发中预览Python和Java变换所需的步骤。有关更多背景信息，请查看我们的Python本地开发和Java本地开发文档。您还可以了解更多关于如何预览变换。

### 先决条件和限制

本地预览支持要求本地分支必须跟踪远程分支，因此本地分支至少需要被推送一次，除了现有的本地开发先决条件外。请注意以下附加限制：

- 预览URI只能由运行预览的用户访问，并且仅在临时基础上可用。
### 运行数据集预览

在运行预览之前，必须为本地开发设置环境，并确保您的库已升级到最新的模板版本。

- 运行./gradlew displayTransformsList，这将返回所有可用变换的列表。
运行./gradlew displayTransformsList，这将返回所有可用变换的列表。

- 运行./gradlew datasetPreview --transformId=<transformId>，将<transformId>替换为其中一个变换ID（上图中的蓝色文本），这将返回一个链接到Foundry，在那里可以访问已经计算的预览。
运行./gradlew datasetPreview --transformId=<transformId>，将<transformId>替换为其中一个变换ID（上图中的蓝色文本），这将返回一个链接到Foundry，在那里可以访问已经计算的预览。

- （非必填）在上述命令中添加--printMode=table标志，以在终端中直接打印所有预览数据集的前10行，而不是提供预览链接。
（非必填）在上述命令中添加--printMode=table标志，以在终端中直接打印所有预览数据集的前10行，而不是提供预览链接。

- （非必填）要在预览中包含输入文件，请添加--inputFiles=<datasetAlias>:<path>，其中<datasetAlias>是所选变换函数的输入数据集之一，<path>是输入数据集内的文件路径。
（非必填）要在预览中包含输入文件，请添加--inputFiles=<datasetAlias>:<path>，其中<datasetAlias>是所选变换函数的输入数据集之一，<path>是输入数据集内的文件路径。

- （非必填）要在预览中包含输出文件，请添加--outputFiles=<datasetAlias>:<path>，其中<datasetAlias>是所选变换函数的输出数据集之一，<path>是输出数据集内的文件路径。
（非必填）要在预览中包含输出文件，请添加--outputFiles=<datasetAlias>:<path>，其中<datasetAlias>是所选变换函数的输出数据集之一，<path>是输出数据集内的文件路径。
