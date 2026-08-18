来源: https://palantir.com/docs/zh/foundry/model-integration/tutorial-train-code-repositories/

# 2b. 教程 - 在代码库中训练模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 2b. 教程 - 在代码库中训练模型

在开始本教程的这一部分之前，您应该已经完成了建模项目设置。在本教程中，您可以选择在Jupyter® notebook或代码库中训练模型。Jupyter® notebook推荐用于快速和迭代的模型开发，而代码库则推荐用于生产级别的数据和模型管道。

在本教程的这一部分中，我们将在代码库中训练模型。这一步将涵盖：

- 创建用于模型训练的代码库
- 分割特征数据以进行测试和训练
- 在代码库中编写模型训练逻辑
- 在代码库中测试推理逻辑
- 查看模型并提交到建模目标
## 2b.1 如何创建用于模型训练的代码库

Foundry中的代码库应用程序是一个基于Web的开发环境，用于编写生产级别的数据和机器学习管道。Foundry提供了一个名为Model Training模板的机器学习模板库。

操作：在您在本教程上一步中创建的code文件夹中，选择+ New > Code repository。您的代码库应根据您正在训练的模型命名。在这种情况下，将库命名为 "median_house_price_model_repo"。选择Model Training模板，然后Initialize。

模型训练模板包含一个示例结构，我们将为本教程进行调整。您可以展开左侧的文件以查看一个示例项目。

## 2b.2 如何分割特征数据以进行测试和训练

监督式机器学习项目的第一步是将我们的标记特征数据分割成用于训练和测试的独立数据集。最终，我们将需要创建性能指标（对我们的模型在新数据上表现的估计），以便我们可以决定这个模型是否足够好以在生产环境中使用，并且我们可以与其他利益相关者沟通对该模型结果的信任程度。我们必须使用独立的数据进行此验证，以帮助确保性能指标能代表我们在真实环境中将看到的结果。

因此，我们将编写一个Python变换，将我们的标记特征数据拆分为训练和测试数据集。

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
from transforms.api import transform, Input, Output


@transform(
    features_and_labels_input=Input("<YOUR_PROJECT_PATH>/data/housing_features_and_labels"),
    training_output=Output("<YOUR_PROJECT_PATH>/data/housing_training_data"),
    testing_output=Output("<YOUR_PROJECT_PATH>/data/housing_test_data"),
)
def compute(features_and_labels_input, training_output, testing_output):
    # 将此 TransformInput 转换为 PySpark DataFrame
    features_and_labels = features_and_labels_input.dataframe()

    # 随机拆分 PySpark DataFrame，80% 用作训练数据，20% 用作测试数据
    training_data, testing_data = features_and_labels.randomSplit([0.8, 0.2], seed=0)

    # 将训练和测试数据写回到 Foundry
    training_output.write_dataframe(training_data)
    testing_output.write_dataframe(testing_data)
```

操作: 打开您库中的feature_engineering.py文件，并将上述代码复制到库中。更新路径以正确指向您在本教程上一步中上传的数据集。在左上角选择搭建以运行代码。您可以选择性地选择预览，以在数据的子集上测试逻辑以加快迭代速度。

您可以在此搭建执行期间继续进行2b.3。

## 2b.3 如何在代码库中编写模型训练逻辑

Foundry中的模型由两个组件组成，模型工件（在模型训练任务中生成的模型文件）和模型适配器（一个Python类，描述Foundry如何与模型工件进行交互以执行推理）。

模型训练模板由两个模块组成，model_training用于训练任务和model_adapters用于模型适配器。

### 模型依赖

模型训练几乎总是需要添加包含模型训练、序列化、推理或评估逻辑的Python依赖项。Foundry通过conda支持添加依赖项规范。这些依赖项规范用于创建一个解决的Python环境以执行模型训练任务。

在Foundry中，这些已解决的依赖项会自动与您的模型打包在一起，以确保您的模型自动拥有执行推理（生成预测）所需的所有逻辑。在此示例中，我们将使用pandas和scikit-learn来生成我们的模型，并使用dill来保存我们的模型。

操作:在左侧边栏中，选择库并添加scikit-learn = 1.2.0、pandas = 1.5.2和dill = 0.3.7的依赖项。然后选择提交以创建一个解决的Python环境。

### 模型适配器逻辑

模型适配器为Foundry中的所有模型提供了一个标准接口。标准接口确保所有模型都可以立即在生产应用程序中使用，因为Foundry将处理加载模型、其Python依赖项、暴露其API并与您的模型接口的基础设施。

为此，您必须创建一个ModelAdapter类的实例，以作为此通信层。

需要实现4个函数：

- 模型保存和加载:为了重用您的模型，您需要定义如何保存和加载模型。Palantir提供了许多默认方法的序列化（保存），在更复杂的情况下，您可以实现自定义序列化逻辑。
- api:定义模型的API，并告知Foundry模型需要什么类型的输入数据。
- predict:由Foundry调用以向模型提供数据。在此处，您可以将输入数据传递给模型并生成推理（预测）。
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

class SklearnRegressionAdapter(pm.ModelAdapter):
    # 使用DillSerializer进行自动序列化
    @pm.auto_serialize(
        model=DillSerializer()
    )
    def __init__(self, model):
        self.model = model

    @classmethod
    def api(cls):
        columns = [
            ('median_income', float),  # 中位收入
            ('housing_median_age', float),  # 住房中位年龄
            ('total_rooms', float),  # 总房间数
        ]
        return {"df_in": pm.Pandas(columns)}, \
               {"df_out": pm.Pandas(columns + [('prediction', float)])}  # 输出增加预测值列

    def predict(self, df_in):
        # 使用模型进行预测，并将结果添加到输入数据框中
        df_in['prediction'] = self.model.predict(
            df_in[['median_income', 'housing_median_age', 'total_rooms']]
        )
        return df_in
```

此代码定义了一个SklearnRegressionAdapter类，它是pm.ModelAdapter的子类。该类用于适配一个 sklearn 回归模型，并提供数据输入输出的接口。代码使用DillSerializer进行模型的序列化，api方法定义了输入输出数据框的格式，predict方法执行预测并返回结果。操作打开model_adapters/adapter.py文件并将上述逻辑粘贴到文件中。

### 模型训练逻辑

现在我们的依赖项已设置并且我们已编写了一个模型适配器，我们可以在 Foundry 中训练一个模型。

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
34
35
36
37
38
39
40
41
42
43
44
45
46
47
from transforms.api import transform, Input
from palantir_models.transforms import ModelOutput
from main.model_adapters.adapter import SklearnRegressionAdapter


@transform(
    training_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_training_data"),
    model_output=ModelOutput("<YOUR_PROJECT_PATH>/models/linear_regression_model"),
)
def compute(training_data_input, model_output):
    training_df = training_data_input.pandas()
    model = train_model(training_df)

    # 将训练好的模型封装在 ModelAdapter 中
    foundry_model = SklearnRegressionAdapter(model)

    # 发布并将训练好的模型写入 Foundry
    model_output.publish(
        model_adapter=foundry_model
    )


def train_model(training_df):
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    numeric_features = ['median_income', 'housing_median_age', 'total_rooms']
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),  # 使用中位数策略填补缺失值
            ("scaler", StandardScaler())  # 标准化特征
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", numeric_transformer),  # 预处理步骤
            ("classifier", LinearRegression())  # 线性回归模型
        ]
    )
    X_train = training_df[numeric_features]
    y_train = training_df['median_house_value']
    model.fit(X_train, y_train)  # 训练模型

    return model
```

在这个代码中，我们使用了Pipeline来组合数据预处理和模型训练步骤。首先，数值特征通过SimpleImputer进行缺失值填补，然后通过StandardScaler进行标准化。接着，处理后的特征被送入LinearRegression模型进行训练。最后，训练好的模型被封装在SklearnRegressionAdapter中，以便发布和保存。非必填：当您在迭代模型训练和模型适配器逻辑时，在运行搭建之前，以在您的训练数据子集上测试您的更改可能会很有用。在左上角选择预览以测试您的代码。

操作：打开您的代码库中的model_training/model_training.py文件，并将上述代码复制到代码库中。更新路径以正确指向您在步骤1.1中创建的训练数据集和模型文件夹。在左上角选择搭建以运行代码。

## 2b.4 如何在代码库中测试推理逻辑

一旦您的模型训练逻辑完成，您可以直接在您的代码库中生成预测（也称为推理）。

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
from transforms.api import transform, Input, Output
from palantir_models.transforms import ModelInput

@transform(
    testing_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_test_data"),
    model_input=ModelInput("<YOUR_PROJECT_PATH>/models/linear_regression_model"),
    predictions_output=Output("<YOUR_PROJECT_PATH>/data/housing_testing_data_inferences")
)
def compute(testing_data_input, model_input, predictions_output):
    # 使用模型对测试数据进行推断
    inference_outputs = model_input.transform(testing_data_input)
    # 将推断结果写入输出
    predictions_output.write_pandas(inference_outputs.df_out)
```

这段代码定义了一个数据转换函数compute，用于使用线性回归模型对房价测试数据进行推断，并将预测结果输出到指定路径。操作:打开存储库中的model_training/run_inference.py文件，并将上述代码复制到存储库中。更新路径以正确指向您之前创建的模型资产和测试数据集。在左上角选择搭建以运行代码。

一旦搭建完成，您可以在搭建输出面板中查看生成的预测。

## 2b.5 如何查看模型并将其提交到建模目标

模型搭建完成后，您可以通过在model_training/model_training.py文件中选择linear_regression_model或通过导航到我们先前创建的文件夹结构中的模型来打开模型。

模型视图包含模型训练的来源、用于生成此模型的训练数据集、模型 API 和发布为的模型适配器。重要的是，您可以发布多个不同版本到同一模型；这些模型版本在左侧边栏的下拉菜单中可用。

由于模型版本与训练期间使用的特定模型适配器相连接，您需要重新发布并搭建您的模型训练过程以应用对模型适配器逻辑的任何更改。

现在我们有了一个模型，我们可以将该模型提交到我们的建模目标中进行管理、评估和发布到运营应用程序。

操作:在代码中选择linear_regression_model以导航到您创建的模型资产，选择提交到建模目标并将该模型提交到您在本教程的第1步中创建的建模目标。系统会要求您提供提交名称和提交负责人。这是用于在建模目标中唯一跟踪模型的元数据。将模型命名为linear_regression_model并将自己标记为提交负责人。

## 下一步

现在我们已经在 Foundry 中训练了一个模型，我们可以继续进行模型管理、测试和模型评估。评估我们模型的性能。

非必填，您还可以在带有代码工作区应用程序的 Jupyter® 笔记本中训练模型，以实现快速和迭代的模型开发。
