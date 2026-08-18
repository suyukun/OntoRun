来源: https://palantir.com/docs/zh/foundry/code-workbook/templates-getting-started/

# 起始

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 起始

在本教程中，我们将学习：

- 创建图表
- 创建模板
- 使用模板
## 创建图表

由于titanic_dataset包含行（代表乘客）和列（代表乘客信息），我们可以使用条形图可视化某个乘客属性（例如性别或舱位）的乘客数量。例如，以下是按性别划分的乘客数量：

在此示例中，我们将创建一个变换来创建所需的图表。创建一个名为bar_chart_of_row_counts的Python变换，并插入以下代码：

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
def bar_chart_of_row_counts(titanic_dataset):
    import matplotlib.pyplot as plt
    from pyspark.sql import functions as F
    import numpy as np

    input_df = titanic_dataset
    categorical_column = "Sex"  # 类别列名称为"Sex"

    # 计算每个类别的计数
    total = input_df \
        .groupBy(categorical_column) \
        .agg(F.count("*").alias("count")) \
        .orderBy("count")

    # 将汇总后的数据集转换为 pandas 数据帧
    total_pdf = total.toPandas()

    # 绘图代码
    fig = plt.figure()
    ax = fig.add_subplot(111)

    y_pos = np.arange(len(total_pdf[categorical_column]))  # 确定 y 轴位置
    ax.set_yticks(y_pos)
    ax.barh(y_pos, total_pdf["count"])  # 绘制水平柱状图
    ax.set_yticklabels(total_pdf[categorical_column])  # 设置 y 轴标签为类别名称
    plt.xlabel("count")  # x 轴标签为“count”
    plt.ylabel(categorical_column)  # y 轴标签为类别列名

    plt.tight_layout()
    plt.show()

    # 返回汇总后的数据帧，以便将其保存为数据集
    return total
```

当您运行此变换时，上方显示的图表将出现在工作簿中的图形变换节点中。您还可以通过将鼠标悬停在变换节点中的图表上并选择查看图像来跳转到全屏图像视图。此图像查看器也可以从内容侧边栏和可视化选项卡中访问。

要将图表创建为SVG格式，请在创建绘图之前使用以下代码：

```
Copied!1
set_output_image_type('svg')  # 设置输出图像类型为 'svg'
```

或者使用装饰器以提高可见性：

```
Copied!1
2
3
4
5
@output_image_type('svg')
def bar_chart_of_row_counts(titanic_dataset):
    # 生成行计数的条形图
    # titanic_dataset: 输入的泰坦尼克号数据集
    # ...
```

## 创建模板

接下来，我们将把这个变换转换成一个模板，以便可以进行泛化和重用。点击代码编辑器右上角的操作按钮，然后点击创建模板。

现在您将进入全屏编辑器中的模板创建视图。在模板编辑器中，您可以编辑模板的名称、描述和参数。让我们将此模板命名为按类别变量的行数条形图，并给出如下描述：创建一个变换，其中包含任何输入数据集中一个分类列的行数条形图。

任何输入数据集——在这个例子中，仅仅是titanic_dataset——都会自动作为类型为dataset的参数添加到模板中。点击模板编辑器中的titanic_dataset以更改它。由于我们希望这个模板是通用的，因此让我们将参数名称从titanic_dataset更改为input_dataset并添加描述。

在变换代码中，两个{{{input_dataset}}}的实例将被高亮显示。接下来，让我们参数化输入列。要在代码主体中将一个变量指派为模板的输入参数，请在变换的右上角点击添加新参数，并在代码中高亮显示相应的变量。如下所示，突出显示字符串"Sex"：

这会将代码的这一部分添加为类型为column且来源数据集为input_dataset的参数。在模板编辑器中，编辑param1参数名称并将其重命名为selected_column。

在这个示例代码中，我们在变换的顶部将列名定义为变量，因此我们只需要参数化一次。当您对其他变换进行模板化时，可以使用添加按钮来添加相同参数的更多实例。

接下来，选择此模板是否应默认保存为数据集。通过选中保存为数据集框，模板在添加时将默认作为持久化变换添加。如果保存为数据集未选中，模板将默认应用为非持久化变换。在这种情况下，我们选择默认保存为数据集，因为我们希望在其他应用中使用输出。

最后，点击创建模板按钮以创建并保存模板。每当您创建新模板时，必须选择一个文件夹来保存它。在这个例子中，您可以将模板保存在您的家庭文件夹中。

只有有访问权限的用户才能发现和使用模板，因此您可以在仍在处理模板时将其保存在您的家庭文件夹中，并在您希望推广其更广泛使用时将其移动到共享文件夹中。模板也可以添加到数据目录中。

## 使用模板

创建并保存模板后，您可以以点选方式使用模板。

要查看可用模板，请在变换创建视图中点击浏览所有模板。

浏览模板支持按名称、描述和标签搜索模板，或基于收藏夹、最近使用的模板或文件结构进行浏览。要应用模板，点击其名称并选择“选择”。让我们添加我们刚刚创建的模板。

将模板添加到图形后，您可以重命名变换并填写输入。通过点击点击此处添加数据集并在图形中点击titanic_dataset来指派input_dataset参数。现在，您可以选择任何列作为selected_column参数，以基于该列创建图表。

选择运行以计算变换。对于输出可视化的变换，图形视图是图中的默认视图。您可以右键单击，选择编辑，然后选择显示表视图以表格形式查看节点。

## 编辑模板

如果您想更新支持模板的代码，请点击操作，然后点击编辑模板以进入代码编辑器并编辑模板。
