来源: https://palantir.com/docs/zh/foundry/pipeline-builder/management-create-custom-functions/

# 创建自定义函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 创建自定义函数

自定义函数使您能够将一系列变换保存为单个变换，以便在您的管道中重复使用。此功能对于在管道中重复逻辑但在单一位置进行管理非常有用。

一个自定义函数包括一个名称（必填）、描述（非必填）、函数参数（非必填）和函数定义（必填）。

创建自定义函数需要两个步骤：

- 将您的逻辑定义为一系列变换面板。
- 将变换面板转换为新的自定义函数。
下面，我们将为每个步骤提供一个示例。

## 定义一系列变换面板

假设您有一个users表，并且您想创建一个主键以唯一标识每个用户。您知道每个用户的first_name、last_name和first_login_date是一个唯一的组合。您希望向数据集中添加一个String类型的primary_key列，它是这三列的哈希值，然后删除first_name、last_name和first_login_date。最后，如果有重复项，您希望每个用户只保留一行，并保留age值最低的行。

首先，将first_name、last_name和first_login_date合并到一列中。您可以使用Concatenate strings变换将这三列合并在一起。

在Separator字段中输入-。然后，在Expressions下拉菜单中选择每一列。对于前两列，选择first_name和last_name。然而，first_login_date列不是我们第三个字段可供选择的选项。这是因为它是Date类型，而Concatenate strings函数只接受String类型。

为了解决这个问题，从Expressions选项卡中插入一个Cast表达式。参数将是first_login_date作为Expression，以及String作为要转换的Type。这样可以避免您需要全局更改first_login_date，因为这会影响所有下游变换面板。

一旦您选择Apply，输出表应如下所示：

现在，您必须对primary_key中的数据进行去标识化。实现这一点的一种方法是通过应用Hash sha256变换为primary_key中的每个值创建一个哈希。在同一个面板中，选择Reuse value选项，将Concatenate strings替换为Hash sha256。

此选项保留现有值并将其作为新变换的第一个输入。

选择Apply后，验证您的输出是否与预期一致：一个包含关于每行的唯一数据的primary_key: String列。

现在，您会注意到primary_key中的第一行和最后一行是相同的。您希望保留age为25的行，并删除first_name、last_name和first_login_date。为此，添加一个Aggregate变换。在第一个字段Group by columns中输入primary_key，在第二个字段Aggregations中输入age，并使用Min表达式：

最后，输出表应如下图所示。您可以验证primary_key = b3c01...只有一行，并且age是25。

## 将一系列变换面板转换为自定义函数

现在，假设您希望在管道中的三个不同位置重复使用此逻辑。我们可以通过使用Shift + Down Arrow选择这两个面板，然后选择顶部栏中的**+**按钮，将我们的逻辑转换为自定义函数。

这将带您进入自定义函数创建页面。您会注意到列输入first_name、last_name、first_login_date和age被划掉；这是因为您正在创建的函数将在您的管道中对任何四个正确类型的输入都是通用的，无论列名是什么。

要定义这些输入，选择Add argument四次。通过点击黄色框来配置参数名称。

然后，通过点击每个参数右侧的齿轮图标配置参数类型。这里，您希望前两个参数为Expression<String>类型，以表示String类型的列，第三个参数为Expression<Date>类型，最后一个参数为Expression<Integer>类型。

现在，您可以像之前一样将新的参数添加到这两个面板中。然而，它们现在会在Parameters部分而不是Columns部分中可用。

一旦您完成配置，为函数命名为Primary key generator，给它一个非必填描述，并选择Apply all changes。

新的函数现在可以在任何变换路径中使用。下次您需要使用此模式创建主键时，可以在变换下拉菜单中搜索Primary key generator。

您可以使用原始列first_name、last_name、first_login_date和age填充您的自定义函数。

通过将相关的列名称填入您的自定义函数中，您将产生与在路径中使用相同变换创建函数相同的结果。然而，通过创建自定义函数，您可以保存函数逻辑以在管道中重复使用，而不是使用单独的变换面板重新创建逻辑。
