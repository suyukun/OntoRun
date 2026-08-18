来源: https://palantir.com/docs/zh/foundry/model-integration/tutorial-train-jupyter-notebook/

# 2a. 教程 - 在 Jupyter® notebook 中训练模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 2a. 教程 - 在 Jupyter® notebook 中训练模型

在开始本教程的此步骤之前，您应已完成建模项目设置。在本教程中，您可以选择在 Jupyter® notebook 中或在代码库中训练模型。Jupyter® notebook 推荐用于快速和迭代的模型开发，而代码库推荐用于生产级数据和模型管道。

在本教程的此步骤中，我们将在 Jupyter® notebook 中使用代码工作区训练模型。此步骤将涵盖：

- 创建用于模型训练的 Jupyter® 代码工作区
- 拆分特征数据以用于测试和训练
- 在代码工作区中训练模型
- 从代码工作区发布模型
- 查看模型并将其提交到建模目标
## 2a.1 如何创建用于模型训练的 notebook

Foundry 中的代码工作区应用程序是一个基于网络的开发环境，提供第三方 IDE 以用于数据分析和模型开发。您可以直接从 Foundry 中的 Jupyter® notebook 发布模型，这些模型可用于下游应用程序。

代码工作区通过确保在您使用工作区时持续可用的计算资源，提供了一个交互式开发环境。代码工作区使您能够配置 Python 环境，变换数据，绘制图表，并在不等待计算资源或打包 Python 环境的情况下训练模型。

操作：在本教程前一步创建的code文件夹中，选择+ New > Jupyter Code Workspace。您的代码工作区应根据您正在训练的模型命名。在本例中，将存储库命名为median_house_price_model_notebook。选择Continue以使用默认计算资源和存储库配置，然后使用Create创建并启动工作区。

工作区创建完成后，我们需要创建一个 notebook 并安装一些依赖项来训练模型。在 Jupyterlab® 启动器屏幕中，选择要使用的 notebook 内核。

操作：选择基础Pythonconda 内核来创建一个新的 notebook，然后将文件重命名为model_training.ipynb。

## 2a.2 如何拆分特征数据以用于测试和训练

监督机器学习项目的第一步是将我们的标记特征数据拆分为用于训练和测试的独立数据集。最终，我们希望创建性能指标（估计我们的模型在新数据上表现的好坏），以便决定该模型是否足够好以用于生产环境，并向其他利益相关者传达对该模型结果的信任程度。我们必须使用独立的数据进行此验证，以帮助确保性能指标能够代表我们在现实世界中看到的情况。

### 将数据集导入到代码工作区

首先，让我们在代码工作区的 Jupyter® notebook 中使用我们的数据集。代码工作区允许我们为输入数据创建一个“别名”，这有助于提高代码的可读性。在这种情况下，我们将使用别名training_data。

操作：打开Data选项卡，然后选择Add dataset > Read existing datasets。添加我们之前创建的housing_features_and_labels数据集，并为其提供别名training_data。将提供的导入逻辑复制到您的 Jupyter® notebook 的单元格中。您可以按Shift + Enter来运行代码单元格。

```
Copied!1
2
3
4
from foundry.transforms import Dataset

# 从 Foundry 数据库中获取名为 "training_data" 的数据集，并将其读取为 Pandas DataFrame 格式
training_data = Dataset.get("training_data").read_table(format="pandas")
```

### 将数据拆分为测试和训练集

现在我们已经导入了数据集，接下来将数据拆分为测试和训练数据框。

操作：使用笔记本顶部的+选项创建一个新的笔记本单元格，然后复制下面的代码片段并运行该单元格。

```
Copied!1
2
3
4
5
6
7
8
# 从 training_data 中随机抽取 80% 的样本作为训练集
train_df = training_data.sample(frac=0.8, random_state=200)

# 将剩余的 20% 样本作为测试集
test_df = training_data.drop(train_df.index)

# 显示训练集数据
train_df
```

### 保存测试数据集到Foundry

接下来，我们可以将测试和训练数据集拆分保存回Foundry。这使我们能够记录用于训练和测试的数据集，以供将来参考。

操作：选择添加 > 将数据写入新数据集来创建一个新的数据集输出。您可以将输出命名为housing_test_data并将输出保存到之前的data文件夹中。选择添加数据集和表格数据集作为数据集类型，并选择test_df作为Python变量。然后，您可以将代码复制到一个新单元格中并执行，以将数据集保存回Foundry。

```
Copied!1
2
3
4
5
6
7
from foundry.transforms import Dataset

# 获取名为 "housing_test_data" 的数据集
housing_test_data = Dataset.get("housing_test_data")

# 将数据写入到表中
housing_test_data.write_table(test_df)
```

## 2a.3 如何在Code Workspaces中训练模型

Foundry中的模型由两个组件组成：

- 模型工件：在模型训练任务中生成的模型文件。
- 模型适配器：一个Python类，用于描述Foundry应如何与模型工件交互以进行推理。
### 模型依赖

模型训练几乎总是需要添加包含模型训练、序列化、推理或评估逻辑的Python依赖项。Foundry支持通过conda和PyPI（pip）添加依赖项规范。这些依赖项规范创建了一个Python环境，可以用于训练模型。

在Foundry中，这些已解决的依赖项和Jupyter®笔记本中的所有Python.py文件会自动与您的模型一起打包，以确保您的模型在生产中自动具备执行推理（生成预测）所需的所有逻辑。Jupyter® Code Workspaces中的环境通过maestro命令进行管理。在此示例中，我们将使用pandas和scikit-learn来生成我们的模型，并使用dill来保存我们的模型。

操作：通过选择蓝色的+按钮打开启动器，然后启动终端。通过运行下面的命令添加所有三个依赖项。您还可以使用侧边栏中的Packages选项卡安装您希望安装的软件包的支持存储库，这将打开终端并为您运行maestro命令。

```
Copied!1
maestro env conda install scikit-learn pandas dill palantir_models palantir_models_serializers
```

这行命令在使用maestro环境管理工具来安装指定版本的Python库：

- scikit-learn=1.2.0：安装机器学习库scikit-learn的1.2.0版本。
- pandas=1.5.2：安装数据处理库pandas的1.5.2版本。
- dill=0.3.7：安装用于序列化Python对象的库dill的0.3.7版本。
- palantir_models：安装palantir_models库，可能用于特定的机器学习或数据处理任务。
- palantir_models_serializers：安装palantir_models_serializers库，可能用于palantir_models的序列化功能。
### 模型训练

操作：将上述代码复制到一个新单元格中并执行，以在Jupyter® Notebook内存中训练一个新模型。如果遇到ModuleNotFoundError或ImportError，请重启内核（Kernel > Restart Kernel...），以确保环境已获取到请求的依赖项更改。

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
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# 定义数值特征的列
numeric_features = ['median_income', 'housing_median_age', 'total_rooms']

# 创建用于数值特征的转换管道
numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),  # 使用中位数进行缺失值填补
        ("scaler", StandardScaler())  # 标准化数据
    ]
)

# 创建包含预处理和线性回归模型的管道
model = Pipeline(
    steps=[
        ("preprocessor", numeric_transformer),  # 数据预处理步骤
        ("classifier", LinearRegression())  # 线性回归模型
    ]
)

# 提取训练数据中的特征和目标变量
X_train = train_df[numeric_features]  # 特征数据
y_train = train_df['median_house_value']  # 目标变量

# 训练模型
model.fit(X_train, y_train)

# 输出模型管道
model
```

## 2a.4 如何从代码工作区发布模型

现在我们已经创建了一个模型，可以将其发布到Foundry，以便将其与我们的生产应用程序集成。要发布模型，我们需要在Foundry中创建一个模型资源以保存模型，然后将模型包装在一个模型适配器中，以便Foundry知道如何与您的模型进行交互。

操作：在模型选项卡中，选择添加模型>创建新模型并将其命名为linear_regression_model。您可以将模型保存到之前创建的models文件夹中，然后选择创建以创建资源。

现在您已经创建了一个模型资源，Foundry会自动为您创建一个新的Python文件来实现模型适配器。模型适配器为Foundry中的所有模型提供了一个标准接口。标准接口确保所有模型可以立即用于生产应用程序，因为Foundry将处理加载模型、其Python依赖项、公开其API以及与您的模型接口所需的基础设施。

代码工作区中的模型适配器必须在一个单独的Python (.py) 文件中定义，并导入到笔记本中。

要创建模型适配器，您需要实现四个函数：

- 模型保存和加载：为了重用您的模型，您必须定义如何保存和加载模型。Palantir提供了许多默认方法进行序列化（保存），在更复杂的情况下，您可以实现自定义序列化逻辑。
- api:定义您的模型的API，并告诉Foundry您的模型需要什么类型的输入数据。
- predict:由Foundry调用以向您的模型提供数据。在这里，您可以将输入数据传递给模型并生成推断（预测）。
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
import palantir_models as pm
from palantir_models_serializers import DillSerializer


class LinearRegressionModelAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        model=DillSerializer()  # 使用DillSerializer序列化模型
    )
    def __init__(self, model):
        self.model = model  # 初始化时将传入的模型赋值给实例变量

    @classmethod
    def api(cls):
        columns = [
            ('median_income', float),  # 中位收入
            ('housing_median_age', float),  # 房屋中位年龄
            ('total_rooms', float),  # 房间总数
        ]
        return {"df_in": pm.Pandas(columns)}, \
               {"df_out": pm.Pandas(columns + [('prediction', float)])}  # 输出数据框包含预测结果

    def predict(self, df_in):
        df_in['prediction'] = self.model.predict(
            df_in[['median_income', 'housing_median_age', 'total_rooms']]  # 预测使用的输入特征
        )
        return df_in  # 返回包含预测结果的数据框
```

该代码定义了一个线性回归模型适配器类LinearRegressionModelAdapter，用于通过palantir_models库对线性回归模型进行适配和序列化处理。api方法定义了输入和输出的数据框格式，而predict方法则负责利用模型进行预测。操作:将上述代码复制到一个名为linear_regression_model_adapter.py的新文件中。从左侧模型侧边栏中选择发布模型版本代码片段，然后展开发布到Foundry部分，将相应的代码片段复制到您的主笔记本中。请确保将代码片段调整为您在Python中的新model变量。您可能希望在实际调用.publish函数之前测试您的模型适配器，您可以通过从适配器模型实例运行.transform来实现：

创建适配模型实例并进行测试：

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
# 加载 autoreload 扩展并自动重新加载所有模块
%load_ext autoreload
%autoreload 2
from palantir_models.code_workspaces import ModelOutput
from linear_regression_model_adapter import LinearRegressionModelAdapter # 如果类或文件名更改，请更新

# 将训练好的模型包装在 Foundry 的模型适配器中
linear_regression_model_adapter = LinearRegressionModelAdapter(model)
linear_regression_model_adapter.transform(test_df).df_out
```

将模型发布到Foundry：

```
Copied!1
2
3
4
# 获取对模型资源的可写引用。
model_output = ModelOutput("linear_regression_model")
# 将模型发布到 Foundry
model_output.publish(linear_regression_model_adapter)
```

非必填：您可以从一个将执行您的.ipynb文件的变换中发布模型，使用Palantir搭建基础设施。这使您能够在继续迭代您的Jupyter®笔记本的同时，并行运行长时间运行的训练任务。了解更多关于创建具有模型输出的变换的信息。

## 2a.5 如何查看模型并提交到建模目标

现在我们有了一个模型，我们可以将该模型提交到我们的建模目标以进行管理、评估，并发布到运营应用程序。

操作：在预览窗口中选择查看模型版本以导航到您创建的模型资产，然后选择提交到建模目标并将该模型提交到您在本教程的步骤1中创建的建模目标。系统会要求您提供提交名称和提交所有者。这是用于在建模目标内唯一跟踪模型的元数据。将模型命名为linear_regression_model并将自己标记为提交所有者。

## 下一步

现在我们已经在Foundry中训练了一个模型，我们可以继续进行模型管理、测试和模型评估。

您也可以在代码库应用程序中训练模型，该应用程序专为创建生产级模型训练流水线而设计。

Jupyter®，JupyterLab®，以及Jupyter®标志是NumFOCUS的商标或注册商标。

所有引用的第三方商标（包括徽标和图标）仍为其各自所有者的财产。无任何附属或认可的暗示。
