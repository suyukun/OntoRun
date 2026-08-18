来源: https://palantir.com/docs/zh/foundry/palantir-extension-for-visual-studio-code/transforms-build/

# 变换搭建

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 变换搭建

Visual Studio Code 的 Palantir 扩展提供了启动搭建的功能。搭建将在 Palantir 平台上运行，您将能够监控进度、查看日志，并直接从本地 Visual Studio Code 环境或 Palantir 平台中的 VS Code 工作区管理搭建。

## 启动搭建

您可以通过以下三种方式在本地 Visual Studio Code 环境或平台内的 VS Code 工作区内启动搭建：

- 从命令面板中选择Palantir: Build on Foundry选项。
- 从工具栏中选择Build图标：
- 打开Build面板并选择Build选项：
## 搭建过程

您可以为任何来自 Palantir 仓库的打开文件启动搭建。

要搭建文件，您必须将所有本地更改推送回远程仓库。

一旦您的本地分支与远程分支同步，搭建过程将开始并执行以下操作：

- 执行必要的检查
- 运行搭建
您可以导航到Builds面板以查看输出数据集的状态。
