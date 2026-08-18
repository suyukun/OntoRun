来源: https://palantir.com/docs/zh/foundry/code-workbook/getting-started/

# 起始

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 起始

## 设置数据集

本教程使用一个公开可用的数据集（下载 titanic_dataset.csv），其中包含关于泰坦尼克号乘客的信息。

该数据集包括乘客的姓名、年龄、性别及其他识别信息。导航到 Foundry 并打开您的个人项目。创建一个名为Code Workbook Tutorial的文件夹，并上传泰坦尼克号数据集，命名为titanic_dataset。

## 设置 Code Workbook

点击项目中的新建按钮并选择Code Workbook来创建一个新的 Workbook。

## 导入数据集

点击导入数据集以开始。在出现的对话框中，搜索titanic_dataset。选择您在设置过程中创建的文件，它应该位于/user/Code Workbook Tutorial/titanic_dataset。

一旦您确定了所需的数据集，点击文件，然后点击选择以将数据集添加到您的图表中。

## 使用 Python 变换数据

现在titanic_dataset已导入到工作簿中，我们可以使用代码和可重用的逻辑块对其进行变换。通过将鼠标悬停在titanic_dataset上并点击+号来添加一个下游变换。这将弹出一个显示各种变换选项的下拉菜单 - 选择 Python。

一个 Python 代码节点现在出现在图表上，并有一条连接线显示它是titanic_dataset的子节点。在逻辑选项卡顶部的文本框中为此变换赋予一个别名，titanic_filtered。

默认情况下，新创建的变换不会作为数据集保存在 Foundry 中。您可以通过点击保存为数据集切换按钮来选择将变换的结果保存为数据集。了解更多关于将变换保存为数据集的信息。被保存为数据集的变换有两个名称：别名和 Foundry 数据集的名称。

## 使用 Pandas dataframe

如果您更习惯于使用 Pandas 语法，您可以在 Python 节点中使用 Pandas。让我们更新titanic_filtered以使用 Pandas。

首先，我们需要更改titanic_dataset的输入类型。点击逻辑面板中的输入选项卡并展开侧边栏。您会看到输入类型设置为 Spark dataframe。点击下拉菜单并选择 Pandas dataframe 以将titanic_dataset的输入类型更改为 Pandas dataframe。

接下来，让我们更新代码以使用 Pandas dataframe。我们将执行相同的筛选。

```
Copied!1
2
3
4
def titanic_filtered(titanic_dataset):
    # 过滤出在泰坦尼克号上幸存的女性乘客
    output_df = titanic_dataset[(titanic_dataset['Survived'] == 1) & (titanic_dataset['Sex'] == 'female')]
    return output_df
```

该代码将输出一个包含泰坦尼克号女性幸存者的Pandas数据框。

## 使用控制台

控制台为Code Workbook提供了一个REPL（读取-评估-打印循环），能够对图中的任何变换或输入数据集进行快速、临时分析。为了在您首选的语言中快速迭代，您的工作簿中为每种启用的语言提供了一个控制台。

打开位于页面右侧的控制台。选择Python控制台：

您可以通过在Python中执行命令快速试验数据。您还可以通过高亮代码并使用键盘快捷键Cmd+Shift+Enter(macOS) 或Ctrl+Shift+Enter(Windows) 将代码从变换发送到控制台运行。

首先，您必须在Python控制台中导入以下PySpark SQL函数：

```
Copied!1
import pyspark.sql.functions as F  # 导入PySpark SQL模块中的functions库，并简写为F
```

然后，确定泰坦尼克号女性幸存者的最大年龄：

```
Copied!1
2
titanic_filtered.select(F.max('Age')).show()
# 显示泰坦尼克号数据集中乘客的最大年龄
```

您还可以使用SQL控制台计算相同的统计数据：

```
Copied!1
2
SELECT max(Age) AS max_age FROM titanic_filtered
-- 选择 titanic_filtered 表中的最大年龄，并将结果命名为 max_age
```
