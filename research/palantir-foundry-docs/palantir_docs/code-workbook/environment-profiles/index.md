来源: https://palantir.com/docs/zh/foundry/code-workbook/environment-profiles/

# Code Workbook 配置文件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Code Workbook 配置文件

Code Workbook 配置文件是一组预定义的 Conda 软件包和 Spark 设置，作为应用案例或用户组的有用默认环境。对于给定的 Code Workbook 配置文件，您还可以配置预热模块以减少用户等待时间。

例如，数据科学组可能希望配置一个数据科学配置文件，其中包含像tensorflow和keras这样的 Conda 软件包，以及更高的驱动程序内存。

在 Code Workbook 中，用户可以在环境配置对话框中从 Code Workbook 配置文件列表中进行选择。用户随后可以进一步自定义 Conda 软件包。用户无法为给定的 Code Workbook 配置文件自定义 Spark 设置。

对于给定的配置文件，权限边界是项目。对配置文件具有只读访问权限的用户可以将配置文件导入项目中。一旦配置文件被导入项目中，任何在项目中使用 Code Workbook 的人都可以使用该配置文件。

## Artifacts 配置文件

在控制面板中创建的新 Code Workbook 配置文件使用 Artifacts。基于 Artifacts 的配置文件允许使用由 Artifacts 安全生成的库，包括在 Foundry 中编写但未发布到shared渠道的 Python 库。请参阅控制面板文档以了解更多关于创建 Artifacts 配置文件的信息。

### 使用 Artifacts 配置文件

在控制面板中创建 Artifacts 配置文件后，用户可以在 Code Workbook 中使用该配置文件。Artifacts 配置文件包含请求的软件包列表和提供这些软件包的支持仓库列表。要使用配置文件，必须将配置文件上的所有支持仓库添加为工作簿项目中的项目导入。如果您没有权限导入配置文件上的所有支持仓库，则将无法使用该配置文件设置环境。

如果在任何时候，配置文件的支持仓库不再导入到项目中，您将无法获取环境，直到它作为导入添加，您将在 UI 中收到提示。

### 自定义 Artifacts 配置文件

在 Code Workbook 中使用自定义 Artifacts 配置文件时，使用的支持仓库列表是 Code Workbook 的而不是配置文件的。新创建的 Code Workbook 初始化时没有支持仓库，当用户在 Workbook 中使用自定义 Artifacts 环境时，支持仓库列表会自动填充。注意，这意味着在 Workbook 中的所有分支上，所有自定义 Artifacts 环境的用户都在添加和使用相同的支持仓库列表。

在 Code Workbook 中使用自定义 Artifacts 环境时，Workbook 的所有支持仓库必须导入到项目中。如果在任何时候，Workbook 的支持仓库不再导入到项目中，您将无法获取环境，直到它作为导入添加，您将在 UI 中收到提示。

### 未来计划

在未来，所有现有的配置文件和环境将迁移以使用 Artifacts。这意味着无论基础配置文件如何，用户都将能够使用由 Artifacts 安全生成的库。
