来源: https://palantir.com/docs/zh/foundry/code-workbook/hidden-repository/

# 隐藏代码存储库

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 隐藏代码存储库

Code Workbook通过使用分支提供轻量级版本控制。此外，每个工作簿都有一个特殊的隐藏代码存储库支持。此存储库作为在代码工作簿中编写的代码的安全备份，同时也显示工作簿中所有代码更改的历史记录。

你可以通过在Code Workbook界面的右上角打开齿轮图标菜单，并选择打开隐藏代码存储库来访问工作簿的隐藏代码存储库。

## 特殊属性

工作簿的隐藏存储库将始终具有以下属性：

- 存储库是只读的：存储库内容只能查看，不能直接在存储库中更新。更新存储库的唯一方法是在工作簿中进行代码更改。
- 存储库默认隐藏：只能通过Code Workbook界面发现。
- 存储库存储三个独立的文件：pipeline.R、pipeline.py和pipeline.sql文件分别包含转换后的工作簿针对各自语言的所有代码。
- 存储库保存完整的更改历史：每个分支的工作簿代码更改的完整历史记录可在隐藏存储库的分支选项卡下查看。
- 存储库包含一个隐藏的workbook.yml文件：该文件存储有关工作簿的基本元数据。
在工作簿分支上进行的每次代码更改都会自动在隐藏代码存储库中对应的分支创建一个新的提交。

## 代码转换

提交到隐藏存储库的Code Workbook代码会自动转换为代码存储库语法。例如，考虑以下在Code Workbook中的代码单元格：

```
Copied!1
2
3
def rename_column(dataset):
    # 将数据集中列名从 "old_name" 重命名为 "new_name"
    return dataset.withColumnRenamed("old_name", "new_name")
```

代码将在隐藏存储库的pipeline.py文件中转换为以下内容：

```
Copied!1
2
3
4
5
6
7
@transform_pandas(
    Output(rid="ri.foundry.main.dataset.id-1"),
    dataset=Input(rid="ri.vector.main.dataset.id-2")
)
def rename_column(dataset):
    # 使用withColumnRenamed方法将列名从"old_name"改为"new_name"
    return dataset.withColumnRenamed("old_name", "new_name")
```

如果在一个代码工作簿中存在多于一个给定语言的代码单元，每个代码单元将会附加在同一个唯一文件中：R语言为pipeline.R，Python为pipeline.py，SQL为pipeline.sql。这允许您在一个文件中查看所有给定语言的代码。在工作簿的全局代码部分编写的代码也将存储在相应的文件中。

## 恢复丢失的代码

通过定期存储工作簿的备份，隐藏代码库是恢复丢失或意外删除代码的推荐方法。要查看给定工作簿分支的历史记录，打开隐藏库顶部的分支选项卡，选择所需的分支（例如master），然后选择您想要查看代码更改的提交。然后，您可以复制代码并将其粘贴回工作簿中。
