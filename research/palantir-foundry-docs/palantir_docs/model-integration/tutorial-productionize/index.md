来源: https://palantir.com/docs/zh/foundry/model-integration/tutorial-productionize/

# 4. 教程 - 将模型投入生产

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 4. 教程 - 将模型投入生产

在继续本教程之前，您应该已经完成了模型项目设置和模型训练，以及非必填的模型评估教程。此时，您应该在您的建模目标中至少有一个模型。

在本教程的这一步中，您将使用您的机器学习模型并设置该模型的生产用法。

- 在建模目标中发布一个模型。
- 为批处理创建一个批处理部署。
- 为您的模型创建一个交互式实时端点。
## 4.1 在建模目标中发布一个模型

现在我们有了一个模型，可以将其部署到生产中。根据该模型的预期用途，我们可能希望通过以下几种方式之一将其投入生产：

- 在批处理部署中：为数据集生成预测，推荐用于一次计算一组记录的预测。
- 在实时部署中：在REST端点后托管模型，推荐用于从外部系统使用模型，或者需要与模型进行实时交互时。
- 在Python变换中：适用于快速迭代的变换。
### 什么是建模目标中的发布？

批处理和实时部署都由模型发布支持。如果在建模目标中发布一个新模型，那么该建模目标中的部署将自动升级以使用新发布的模型。

这使得模型使用者可以使用模型而无需担心其具体实现。数据科学家可以专注于改进模型，而应用程序开发人员则专注于搭建有用的应用程序。

### 发布管理

发布和部署分为预发布和生产。模型开发人员可以在生产发布之前将模型发布到预发布环境。这会升级预发布部署，同时保持生产部署不变。然后，数据科学家或应用程序构建者可以在预发布环境中测试新模型，然后再将模型投入生产。

所有发布以及发布模型的个人都被记录下来，以确保团队可以跟踪哪个模型在什么时间被使用。这有助于回答诸如GDPR或欧盟AI法案要求的监管问题。

操作：导航到建模目标的主页并滚动到发布部分。选择发布到预发布，然后选择箭头图标将模型发布到生产。您需要为发布指定一个发布编号，例如“1.0”。

## 4.2 如何为批处理创建一个批处理部署

批处理部署将从输入数据集中创建一个Foundry变换。批处理部署的输出是一个数据集，该数据集是使用模型对输入数据集运行推断（生成预测）的结果。

操作：点击创建部署并配置一个生产批处理部署。给部署起个名字Batch deployment，并描述为Production batch deployment。选择您之前创建的housing_inference_data数据集作为输入数据集，并在您的data文件夹中创建一个名为house_price_predictions的新输出数据集。选择创建部署以保存配置。

现在，我们可以安排批处理部署，以便每当新模型发布时，我们的输出数据集将自动更新——确保我们始终使用最佳预测。让我们在输出数据集上添加一个计划，以便当它收到新逻辑时重建。

操作：在部署表中选择您的批处理部署。选择名为house_price_predictions的输出数据集。在所有操作下，选择管理计划。在house_price_predictions数据集上，选择创建新计划 -> 当多个时间或事件条件满足时，当house_price_predictions数据集接收新逻辑时。最后，选择保存以保存计划。

最后，由于我们尚未更新house_price_predictions数据集，我们可以运行此操作以生成预测。在构建完成后，您可以打开house_price_predictions数据集以查看预测列中的新推导预测。

操作：在计划视图中选择立即运行以构建house_price_predictions数据集。构建完成后，您可以通过右键单击house_price_predictions数据集并选择打开来查看生成的预测。

## 4.3 如何为您的模型创建一个交互式实时端点

实时部署是一个可查询的端点，它在REST端点后托管生产模型。当您希望与模型进行交互时，实时部署非常有用，并且可以从以下位置查询：

- 模型上的函数：模型上的函数使得可以直接从Foundry中的Slate或Workshop应用程序查询模型。
- 实时外部系统：如需要根据用户行为生成实时预测的网站。
- CURL：用于本地测试您的模型。
在此示例中，您可能希望搭建一个交互式仪表盘，允许用户输入有关人口普查区的详细信息，并查看这如何影响房价中位数。

操作：从目标主页，点击创建部署并配置一个生产实时部署。给部署起个名字Live deployment，并描述为Production live deployment。点击创建部署以保存配置。

实时部署可能需要几分钟才能启动。一旦初始化，您可以设置实时操作应用程序以连接到模型。

操作：选择您的实时部署。当部署升级后，打开查询标签。粘贴以下示例并选择运行来测试模型。

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
[
  {
    "housing_median_age": 33.4,  // 房屋中位年龄
    "total_rooms": 1107.0,       // 总房间数
    "total_bedrooms": 206,       // 总卧室数
    "population": 515.3,         // 人口数量
    "households": 200.9,         // 家庭数量
    "median_income": 4.75        // 中位收入
  }
]
```

非必填：在查询文本框中使用示例查询，选择复制图标以复制一个示例CURL请求，您可以使用它在本地测试模型。您需要更新<BEARER_TOKEN>、和<DEPLOYMENT_RID>以匹配您的Foundry环境和实时部署。您可以按照生成用户词元文档生成一个<BEARER_TOKEN>。

```
Copied!1
2
3
curl --http2 -H "Content-Type: application/json" -H "Authorization: <BEARER_TOKEN>" \
-d '{"requestData":[ { "housing_median_age": 33.4, "total_rooms": 1107.0, "total_bedrooms": 206, "population": 515.3, "households": 200.9, "median_income": 4.75 } ], "requestParams":{}}' \
--request POST <STACK>/foundry-ml-live/api/inference/transform/<DEPLOYMENT_RID>
```

### 代码解释

- curl --http2: 使用HTTP/2协议来进行请求。
- -H "Content-Type: application/json": 设置请求头为JSON格式。
- -H "Authorization: <BEARER_TOKEN>": 设置请求的授权头，使用Bearer令牌进行身份验证。
- -d '{...}': 使用POST请求发送的数据，这里是JSON格式的数据。包含以下字段：housing_median_age: 房屋的中位数年龄。total_rooms: 总房间数。total_bedrooms: 总卧室数。population: 人口数。households: 家庭户数。median_income: 中位收入。
- housing_median_age: 房屋的中位数年龄。
- total_rooms: 总房间数。
- total_bedrooms: 总卧室数。
- population: 人口数。
- households: 家庭户数。
- median_income: 中位收入。
- --request POST: 指定请求方法为POST。
- <STACK>/foundry-ml-live/api/inference/transform/<DEPLOYMENT_RID>: 请求的URL，其中<STACK>和<DEPLOYMENT_RID>需要替换为实际的堆栈地址和部署的资源ID。
实时部署由持续运行的服务器支持。启动后，Foundry不会自动终止暂存或生产部署。实时部署可能会很昂贵，因此请确保在完成教程后禁用或删除此实时部署。

您可以通过实时部署视图中的操作下拉菜单禁用或删除实时部署。

## 下一步

此时，我们已成功设置了一个机器学习项目，搭建了一个新模型，评估了其性能，并将其部署，使模型现在可以用于操作。

在阅读教程结论之前，考虑训练您的模型的新版本，评估其性能，然后通过创建新的生产发布来更新您的部署。您可以使用以下逻辑，通过scikit-learn训练一个随机森林回归器，并使用一个新的派生属性housing_age_per_income。您无需为以下代码更新您的模型适配器逻辑。

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
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
from transforms.api import transform, Input
from palantir_models.transforms import ModelOutput
from main.model_adapters.adapter import SklearnRegressionAdapter


@transform(
    training_data_input=Input("<YOUR_PROJECT_PATH>/data/housing_training_data"),
    model_output=ModelOutput("<YOUR_PROJECT_PATH>/models/random_forest_regressor_model"),
)
def compute(training_data_input, model_output):
    # 读取训练数据
    training_df = training_data_input.pandas()
    # 训练模型
    model = train_model(training_df)

    # 将训练好的模型包装在ModelAdapter中
    foundry_model = SklearnRegressionAdapter(model)

    # 发布并将训练好的模型写入Foundry
    model_output.publish(
        model_adapter=foundry_model
    )


def derive_housing_age_per_income(X):
    # 计算住房年龄与收入的比率
    X['housing_age_per_income'] = X['housing_median_age'] / X['median_income']
    return X


def train_model(training_df):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, FunctionTransformer

    # 定义数值特征
    numeric_features = ['median_income', 'housing_median_age', 'total_rooms']

    # 定义数值特征的转换器
    numeric_transformer = Pipeline(
        steps=[
            ("rooms_per_person_transformer", FunctionTransformer(derive_housing_age_per_income, validate=False)),
            ("imputer", SimpleImputer(strategy="median")),  # 使用中位数进行缺失值填补
            ("scaler", StandardScaler())  # 标准化
        ]
    )

    # 建立模型的流水线
    model = Pipeline(
        steps=[
            ("preprocessor", numeric_transformer),  # 预处理步骤
            ("regressor", RandomForestRegressor())  # 使用随机森林回归器
        ]
    )
    # 提取训练特征和目标变量
    X_train = training_df[numeric_features]
    y_train = training_df['median_house_value']
    # 训练模型
    model.fit(X_train, y_train)

    return model
```
