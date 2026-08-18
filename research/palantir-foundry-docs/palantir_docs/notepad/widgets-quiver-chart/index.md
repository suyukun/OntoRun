来源: https://palantir.com/docs/zh/foundry/notepad/widgets-quiver-chart/

# Quiver 图表

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Quiver 图表

要在Notepad 模板中模板化 Quiver 图表，首先创建一个Quiver 仪表盘。然后，您可以使用 Notepad 的Quiver 仪表盘画布微件从中嵌入一个图表。

您可以使用Quiver 图表部分从 Quiver 分析中集成图表或表格。您可以通过插入菜单或直接通过 Quiver 中的复制到 Notepad按钮添加 Quiver 图表。

这两种选项略有不同：

- 当通过复制到 Notepad嵌入时，将捕获图表及其筛选状态。这意味着在 Quiver 分析中应用的所有筛选都将保留，并且在添加到 Notepad 后，您将无法在微件属性配置中调整分析和特定图表。
请注意，当复制粘贴设定为自动更新版本的函数和其他图表时，粘贴的图表将固定在复制时的最新可用版本。

- 当通过插入菜单嵌入时，筛选状态不会被捕获。可以在微件属性配置中调整 Quiver 分析和图表。
## 微件属性

- Quiver 分析：选定的分析。
- 要呈现的 Object 图表：要在选定分析中呈现的图表。