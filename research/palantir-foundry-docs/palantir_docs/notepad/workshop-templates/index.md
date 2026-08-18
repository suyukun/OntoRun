来源: https://palantir.com/docs/zh/foundry/notepad/workshop-templates/

# 从模板生成并导出文档

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从模板生成并导出文档

以允许他人基于您的模板生成新文档，请使用Notepad: Template Button微件。您也可以选择启用将生成的文档导出为PDF。

## Notepad: Template Button 微件

将Notepad: Template Button添加到您的 Workshop 应用程序后，通过点击+ Select并浏览到您的文件来选择您的文档模板。这将把您的模板添加到Document templates列表中。

接下来，点击新模板条目以打开其配置。首先，选择一个Template Version。如果没有可用版本，请在新标签页中打开模板并发布模板版本。选择版本将自动加载模板所需的输入参数到Template Inputs下。

当您在Templates list中添加多个模板时，可以为您的模板指定一个Menu display name。如果您未设置显示名称，将使用Button display设置中的Custom text。

### 保存选项

- Allow users to choose save location: 用户可以在生成文档之前选择自己的保存位置和文件名。任何预定义的Default save location都将被忽略。
- Default save name: 为新生成的文档定义默认文件名。当设置为Export generated notepad as PDF时，该值也将用于PDF文件名。
- Default save location: 调整新文档的保存位置。这可以通过手动选择文件夹或通过 Workshop 字符串变量传递 Compass RID 来配置。默认情况下，文档将保存在生成它的用户的主文件夹中。
### 模板输入

根据模板及其版本，您的 Notepad 模板可能需要多个模板输入。对于这些输入中的每一个，链接一个相同数据类型（字符串、数字、日期、时间戳、Object 或对象集）的Workshop 变量，您希望用作模板的输入。这些变量的当前值将在每次选择Notepad: Template Button时用于从模板生成文档。

如果您的输入参数需要一个单一 Object，请确保将其链接到包含一个 Object 的 Workshop 对象集变量。

### 点击选项

点击选项允许您在用户使用Notepad: Template Button时修改行为：

- Export generated Notepad as PDF:文档将在生成后自动下载为PDF。默认情况下，生成的 Notepad 文档不会保存在 Foundry 中。因此，除了Default save name之外的所有保存选项都将被忽略。Save Notepad from PDF export:当设置时，用于导出为PDF的生成的 Notepad 文档也将保存在 Compass 中。
- Save Notepad from PDF export:当设置时，用于导出为PDF的生成的 Notepad 文档也将保存在 Compass 中。
- Open generated Notepad in new tab:文档将在新标签页中打开。
此外，您可以指定在创建文档时应执行的 Workshop事件或操作。例如，这可以用于通过使用Created document输出变量将新生成文档的 RID 持久化为 Object 属性。
