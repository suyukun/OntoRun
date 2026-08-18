来源: https://palantir.com/docs/zh/foundry/notepad/workshop-embed/

# 嵌入文档

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 嵌入文档

您可能希望允许用户在不打开 Notepad 应用程序的情况下读取或编辑文档。要实现此功能，请在 Workshop 中使用Notepad: 嵌入文档微件。

## Notepad: 嵌入文档微件

该微件以嵌入模式渲染文档。要进行配置，您需要提供文档的资源标识符 (rid)。此rid应类似于ri.notepad.main.notepad.aaaaaaaa-1234-bbb-5678-cccccccccccc，并且需要作为 Workshop 变量传递。

默认情况下，文档将以只读方式显示。切换允许编辑选项以允许用户编辑文档。

嵌入文档的编辑模式仅显示 Notepad 应用程序的简化版本，并不提供所有可用的编辑功能。使用 Notepad 应用程序可以访问所有操作。

要从 Workshop 中导出嵌入文档，请使用Notepad: 导出按钮。
