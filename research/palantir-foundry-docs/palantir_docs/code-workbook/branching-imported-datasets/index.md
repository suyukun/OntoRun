来源: https://palantir.com/docs/zh/foundry/code-workbook/branching-imported-datasets/

# 选择导入的数据集分支

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 选择导入的数据集分支

Code Workbook 为导入的数据集实现了分支回退，这意味着Workbook中的分支层次结构将被用于确定从哪里提取导入的数据集。

例如，假设您的Workbook包含两个分支，master和develop，您的输入数据集titanic也有这两个分支。当您位于develop分支时，导入的数据集将默认从develop提取。如果有另一个数据集仅存在于master而不存在于develop，则输入数据将从master提取。

这种回退结构支持有用的工作流程。例如，如果您从另一个Workbook或存储库导入了数据集，并且希望使用该Workbook或存储库的分支版本测试您的变换，您可以简单地在您的Workbook中创建一个具有相同名称的新分支，导入的数据集将自动回退到适当的分支。

您还可以通过点击任何导入的数据集，并从下拉菜单中选择特定分支，手动选择导入数据集的分支：
