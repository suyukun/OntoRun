来源: https://palantir.com/docs/zh/foundry/migrate-models/overview/

# 从 foundry_ml 迁移到 palantir_models

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从 foundry_ml 迁移到 palantir_models

Python 库foundry_ml已经开始其终止期。foundry_ml库将于 2025 年 10 月 31 日被弃用，这与计划弃用的Python 3.9相对应。我们建议使用palantir_models框架在平台中开发、测试和服务模型来代替它。

使用foundry_ml训练的模型需要在 2025 年 10 月 31 日之前更新为使用palantir_models框架。使用foundry_ml开发的模型将不支持于建模目标、Python 变换或建模目标部署。在代码库中用foundry_ml搭建的模型需要在使用模型训练模板初始化的新代码库中重新搭建。在代码工作簿中用foundry_ml搭建的模型需要在 Jupyter 代码工作空间中重新搭建。
有关使用palantir_models搭建新模型的指导，请查看如何在代码库中训练模型或如何在 Jupyter notebook 中训练模型。

在本教程中，我们将在代码库中将使用foundry_ml搭建的模型迁移到palantir_models。我们将提供使用foundry_ml搭建模型的代码，并演示如何使用palantir_models重写此代码。

## 使用 foundry_ml 在代码库中搭建的示例模型

在以下代码片段中，我们编写了一个使用foundry_ml的 scikit-learn 线性回归模型，我们将其迁移到palantir_models：

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
from transforms.api import transform, Input, Output
from foundry_ml import Model, Stage
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# 定义一个transform装饰器，用于将输入和输出连接到数据管道中
@transform(
training_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_train_data"),  # 指定训练数据的路径
model_output=Output("<YOUR_PROJECT_PATH>/models/linear_regression_foundry_ml"),  # 指定模型输出的路径
)
def create_model(training_data_input, model_output):
    # 读取输入数据，转换为pandas DataFrame
    training_df = training_data_input.pandas()

    # 定义需要用来训练模型的数值特征
    numeric_features = ['median_income', 'housing_median_age', 'total_rooms']

    # 创建一个数据处理管道，首先进行标准化，然后进行线性回归
    pipeline = Pipeline([
    ("scaler", StandardScaler()),  # 标准化数据
    ("regressor", LinearRegression())])  # 线性回归模型

    # 提取特征和目标变量
    X_train = training_df[numeric_features]  # 特征变量
    y_train = training_df['median_house_value']  # 目标变量

    # 拟合管道，训练模型
    pipeline.fit(X_train, y_train)

    # 使用foundry_ml库包装模型，定义两个阶段：标准化和回归
    model = Model(Stage(pipeline["scaler"], output_column_name="features"),
            Stage(pipeline["regressor"]))

    # 保存训练好的模型到指定的输出路径
    model.save(model_output)
```

## 从 Code Repositories 中迁移自 foundry_ml 至 palantir_models

要将上述代码从foundry_ml迁移到palantir_models，请按照以下步骤操作。

### 第一步：使用模型训练模板打开一个新的代码库

Palantir 平台提供了一个名为Model Training的机器学习模板库。要在 Code Repositories 中访问它，请在被问及What are you building?时选择Models：

选择Model Training作为库类型：

模型训练模板包含我们将在本教程中适应的示例结构。您可以在左侧展开文件以查看示例项目：

### 第二步：编写模型适配器

模型适配器为 Foundry 中的所有模型提供了标准接口。此标准接口确保所有模型都可以立即在生产应用中使用。Palantir 平台将处理加载模型及其 Python 依赖项、与其接口并暴露其 API 的基础设施。

为实现这一点，您必须创建一个ModelAdapter类的实例作为这个通信层。

需要实现三个函数：

- 模型保存和加载:为了重用您的模型，您需要定义如何保存和加载模型。Palantir 提供了许多默认方法进行序列化（保存），在更复杂的情况下，您可以实现自定义序列化逻辑。
- API:定义模型的 API，并告知 Palantir 平台您的模型需要什么类型的输入数据。
- 预测:由 Palantir 平台调用以向您的模型提供数据。在这里，您可以将输入数据传递给模型并生成推断（预测）。
打开model_adapters/adapter.py文件并编写模型适配器：

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
import palantir_models as pm
from palantir_models_serializers import DillSerializer


class SklearnRegressionAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        model=DillSerializer()
    )
    def __init__(self, model):
        # 初始化函数，接收一个模型对象并存储为类的属性
        self.model = model

    @classmethod
    def api(cls):
        # 定义输入和输出的数据格式
        columns = [
            ('median_income', float),  # 中位收入
            ('housing_median_age', float),  # 房屋中位年龄
            ('total_rooms', float)  # 房间总数
        ]
        # 返回输入输出数据格式的描述，输入为三列，输出多一列预测结果
        return {'df_in': pm.Pandas(columns=columns)}, \
                {'df_out': pm.Pandas(columns=columns + [('prediction', float)])}

    def predict(self, df_in):
        # 使用模型进行预测，将预测结果添加到输入DataFrame中
        df_in['prediction'] = self.model.predict(df_in[['median_income', 'housing_median_age', 'total_rooms']])
        return df_in
```

以上代码定义了一个用于sklearn模型的适配器类SklearnRegressionAdapter，该类继承自pm.ModelAdapter。其主要功能是将模型序列化和进行预测。代码中使用了palantir_models和palantir_models_serializers库，并对输入和输出数据格式进行了定义。
有关模型适配器逻辑的更多信息，请参阅编写模型适配器。

### 步骤3：编写模型训练逻辑

在下面的示例中，train_model函数包含了来自foundry_ml的未更改训练逻辑示例。compute函数将模型与模型适配器一起封装，并发布模型。

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
from transforms.api import transform, Input
from palantir_models.transforms import ModelOutput
from main.model_adapters.adapter import SklearnRegressionAdapter
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

@transform(
    training_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_train_data"),
    model_output=ModelOutput("<YOUR_PROJECT_PATH>/models/linear_regression_model"),
)
def compute(training_data_input, model_output):
    # 从输入中获取训练数据，并转换为pandas DataFrame
    training_df = training_data_input.pandas()

    # 训练逻辑
    model = train_model(training_df)

    # 用模型适配器包装模型
    foundry_model = SklearnRegressionAdapter(model)

    # 发布模型
    model_output.publish(model_adapter=foundry_model)

def train_model(training_df):
    '''
    训练逻辑与原始foundry_ml示例保持不变。
    '''

    # 定义数值特征
    numeric_features = ['median_income', 'housing_median_age', 'total_rooms']

    # 创建一个流水线，包含标准化和线性回归
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression())])

    # 从训练数据中提取特征和目标变量
    X_train = training_df[numeric_features]
    y_train = training_df['median_house_value']

    # 拟合流水线到训练数据
    pipeline.fit(X_train, y_train)
    return pipeline
```

该代码实现了一个用于训练线性回归模型的Python函数。它利用scikit-learn库创建一个流水线，先对数据进行标准化，然后进行线性回归拟合。训练好的模型通过SklearnRegressionAdapter包装后发布。
打开您代码库中的model_training/model_training.py文件，并为您的模型编写compute函数。将模型的机器学习逻辑复制到train_model函数中。更新路径以正确指向训练数据集和模型。选择右上角的搭建以运行代码。

### 步骤4：编写模型推理逻辑

打开您代码库中的model_training/run_inference.py文件，并编写模型推理逻辑。更新路径以正确指向模型和测试数据集。选择右上角的搭建以运行代码。

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
from transforms.api import transform, Input, Output
from palantir_models.transforms import ModelInput

# 定义一个转换函数
@transform(
    testing_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_test_data"),  # 输入：测试数据路径
    model_input=ModelInput("<YOUR_PROJECT_PATH>/models/linear_regression_model_asset"),  # 模型输入：线性回归模型路径
    predictions_output=Output("<YOUR_PROJECT_PATH>/data/housing_testing_data_inferences")  # 输出：预测结果路径
)
def compute(testing_data_input, model_input, predictions_output):
    # 使用模型对测试数据进行推断
    inference_outputs = model_input.transform(testing_data_input)
    # 将推断结果写入输出路径
    predictions_output.write_pandas(inference_outputs.df_out)
```

按照以下步骤，应能成功将现有的foundry_ml模型从代码库迁移到palantir_models。
