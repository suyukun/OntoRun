来源: https://palantir.com/docs/zh/foundry/manage-models/direct-function-publishing/

# 直接将模型发布为函数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 直接将模型发布为函数

Foundry中的特定模型可以直接发布为函数。这种方法类似于模型上的函数并包含相同的好处，但直接发布提供了一种更简化的无代码方法来实现模型的操作化。

## 模型要求

为了支持直接发布，模型必须满足以下要求：

- 模型必须是一个模型资产。
- 模型输入必须是参数输入。
- 模型只能产生一个参数输出。
### 示例：支持的模型

下面的模型API支持直接发布：

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
def api(cls):
    # 定义模型输入参数，包括花萼长度、花萼宽度、花瓣长度、花瓣宽度，类型为浮点数
    inputs = [
        ModelInput.Parameter(name="sepal_length", type=float),
        ModelInput.Parameter(name="sepal_width", type=float),
        ModelInput.Parameter(name="petal_length", type=float),
        ModelInput.Parameter(name="petal_width", type=float),
    ]

    # 定义模型输出参数，包括预测结果，类型为字符串
    outputs = [
        ModelOutput.Parameter(name="prediction", type=str)
    ]

    # 返回一个模型API实例，包含定义的输入和输出参数
    return ModelApi(inputs, outputs)
```

### 示例：不支持的模型

虽然下面的模型API是有效的，但不能直接作为函数发布，因为它接受表格输入并返回多个输出：

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
def api(cls):
    # 定义输入，包含两个表格输入和一个可选的参数输入
    inputs = [
        ModelInput.Tabular(
            name="table_1",  # 表格输入1的名称
            df_type=DFType.PANDAS,  # 指定数据框类型为Pandas
            columns=[ModelApiColumn(name="text", type=str, required=True)],  # 指定表格列名和类型，"text"列是必须的
        ),
        ModelInput.Tabular(
            name="table_2",  # 表格输入2的名称
            df_type=DFType.PANDAS,  # 指定数据框类型为Pandas
            columns=[ModelApiColumn(name="text", type=str, required=True)],  # 指定表格列名和类型，"text"列是必须的
        ),
        ModelInput.Parameter(name="suffix", type=str, required=False),  # 可选参数输入，名称为"suffix"，类型为字符串
    ]
    # 定义输出，包含两个表格输出
    outputs = [
        ModelOutput.Tabular(name="table_1_out", columns=[]),  # 表格输出1的名称
        ModelOutput.Tabular(name="table_2_out", columns=[]),  # 表格输出2的名称
    ]
    return ModelApi(inputs, outputs)  # 返回定义好的API模型接口
```

对于不支持直接发布的模型API，请使用模型上的函数。

## 以直接模型部署将模型发布为函数

要以直接模型部署将支持的模型发布为函数，您必须首先创建一个直接模型部署。一旦您的直接模型部署正在运行，选择侧边栏中的加号**+**图标，并提供一个模型函数名称。此函数将在每次新模型版本发布到模型分支时自动升级。

## 在建模目标中将模型发布为函数

要通过建模目标将支持的模型发布为函数，您必须首先创建一个实时部署。一旦您的模型正在运行，导航到部署的详细信息页面。在这里，发布函数卡片将会显示。

选择发布函数按钮。然后，您将被引导完成设置函数参数的过程。

一旦您的函数已发布，发布函数卡片将显示哪个函数由实时部署支持。与所有函数一样，您可以在Ontology管理器中查看已发布的函数，其中也提供有关部署的健康信息。

需要注意的是，一个目标仅限于生成一个函数。然而，您仍然可以根据需要发布该函数的新版本。

## 发布新函数版本

当模型重新训练或部署的API更改时，您可能需要发布一个新函数版本。以下是发布新函数版本的示例情况及方法。

### 模型重新训练

当模型重新训练且模型的API未更改时，无需发布新函数版本。当前版本将继续指向部署。然而，如果您选择发布新函数版本，请注意旧函数版本将继续工作。

### 模型API更改

如果您尝试将具有不同模型API的模型发布到实时部署，将会出现以下警告：

请勿忽视此警告。将实时部署更新为具有不同模型API的新模型将需要手动操作以修复下游使用。对话框将指导您完成为受发布影响的任何部署发布新函数版本的过程。

如果您选择不发布新函数版本，当前函数版本的任何使用都会中断。要解决此问题，请返回到部署的详细信息页面并从那里发布新函数版本。
