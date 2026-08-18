来源: https://palantir.com/docs/zh/foundry/integrate-models/external-model-connection/

# 集成外部托管的模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 集成外部托管的模型

批处理部署目前不支持外部模型。请配置一个使用外部模型的Python变换。

Foundry允许创建一个模型，作为托管在第三方应用程序、服务或模型提供商（如Azure Machine Learning、Amazon SageMaker、OpenAI或Vertex AI）的模型的代理。这使得在Foundry之外开发的模型可以轻松地被Foundry用户、管道和操作应用程序使用。

一旦外部托管的模型被集成，Foundry提供以下功能：

- 与批处理变换和实时模型托管的集成。
- 完整的版本控制、细粒度的权限管理和受治理的模型沿袭。
- 通过建模目标进行模型管理和实时部署。
- 绑定到Foundry Ontology，以通过模型上的函数和假设情景分析实现操作化。
## 创建到外部托管模型的自定义连接

要创建到外部托管模型的连接，您将需要以下内容：

- 连接到外部托管模型的连接详情。
- 一个模型适配器，告诉Foundry如何创建连接并与外部托管模型进行接口。
- 一个Foundry出口策略，允许Foundry连接到外部托管模型。
您可以通过以下步骤创建一个代理外部托管模型的模型。

### 1. 创建新模型

第一步是创建一个新模型。这可以通过在Foundry项目中选择**+新建 > 模型**，或通过新的或现有的建模目标来完成。在建模目标中，选择添加模型。

下面的截图显示了在Foundry项目中通过选择**+新建 > 模型**创建新模型的过程。

下面的截图显示了通过在外部模型屏幕中选择添加模型通过建模目标创建新模型的过程。

### 2. 选择添加模型的方法

选择连接外部托管模型，然后选择下一步。

### 3. 设置出口策略

选择自定义连接作为外部托管模型的来源，并在下拉菜单中选择一个出口策略，然后选择下一步。

出口策略使Foundry项目或工件能够将数据从Foundry发送到外部系统。出口策略可能由您组织的Foundry安全模型控制。如果您拥有所需权限，您可以在控制面板应用程序中浏览和配置新的出口策略。

### 4. 配置模型适配器

为此模型选择模型适配器。模型适配器应配置为在加载时接收一个ExternalModelContext以初始化与外部托管模型的连接。有关更多信息，请参阅有关如何创建模型适配器的文档，查看外部模型的模型适配器示例，并查看ExternalModelContext的API定义。

### 5. 配置模型连接

定义自定义模型连接的模型连接详情。连接配置有两个组件：

- URL（非必填）：这是提供给模型适配器的基础URL，旨在作为模型推理函数的URL。
- 连接配置（非必填）：连接配置不会被加密，并且将在平台中随模型元数据一起查看。此组件可以存储特定的配置详情，例如模型名称、推理参数或阈值。
### 6. 配置凭证

定义自定义模型连接的凭证配置，然后选择下一步。

- 凭证配置（非必填）：凭证将被加密并安全地与模型一起存储。这些凭证将在模型加载时解密并提供给模型适配器。请注意，拥有模型访问权限的用户将能够使用此模型进行推理，无论他们对外部模型的基础访问如何。选择下一步以继续保存您的模型详情。
### 7. 配置详情并提交模型

输入您的模型保存位置、模型名称和此模型的版本备注。这将定义模型的Foundry名称、位置和元数据。

如果您是从建模目标创建此模型，请选择提交以创建您的模型并将此模型提交到您的建模目标中。在建模目标中，您可以导航到模型，查看配置并选择性地更新链接的凭证。

如果您在Foundry项目中创建此模型，请选择完成以保存此模型。

### 查看外部托管的模型

外部托管的模型允许用户更新凭证，查看连接配置，并复制出口策略RID，以便用户可以配置Python变换。

#### 在建模目标中提交外部模型

## 测试和操作化外部托管的模型

您可以通过多种方式测试和操作化外部托管的模型。您可以：

- 在建模目标中实时部署模型
- 配置一个使用外部模型的Python变换
### 在建模目标中实时部署

按照设置实时部署的说明进行实时推理。

如果您在与模型相同的Foundry项目中的建模目标中托管模型，则您的出口策略将自动添加到实时部署中。否则，您将需要将出口策略导入托管项目。

### 在建模目标中的批处理管道

外部托管的模型目前不支持批处理部署或在建模目标中的自动模型评估。

### Python变换

要配置一个使用外部模型的Python变换，您将需要手动启用该连接的网络出口。

接下来，您可以从模型版本中找到所需的出口策略名称，并使用该模型输入配置Python变换。

#### 依赖项

在此示例中，以下依赖项设置在Python变换库中。请注意，添加了对external-model-adapters的依赖以进行模型推理，以及对transforms-external-systems的依赖以与外部系统交互。

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
requirements:
  build:
    - python 3.8.*  # 构建阶段需要 Python 3.8 版本
    - setuptools    # 使用 setuptools 构建和打包 Python 项目

  run:
    - python 3.8.*  # 运行时需要 Python 3.8 版本
    - transforms {{ PYTHON_TRANSFORMS_VERSION }}  # 使用指定版本的 transforms 包
    - transforms-expectations  # transforms 的附加功能包，处理期望
    - transforms-verbs  # transforms 的附加功能包，处理动词
    - transforms-external-systems  # transforms 的附加功能包，处理外部系统
    - external-model-adapters 1.0.0  # 外部模型适配器，指定版本为 1.0.0
```

#### 示例变换

这个简单示例采用外部托管模型并执行推理。请注意，计算函数中添加了必需的export_control和egress策略作为输入。egress策略应使用模型中定义的相同egress策略。

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
from transforms.api import transform, Input, Output
from palantir_models.transforms import ModelInput
from transforms.external.systems import EgressPolicy, use_external_systems, ExportControl

# 使用外部系统装饰器来定义出口控制和出口策略
@use_external_systems(
    export_control=ExportControl(markings=['<MARKING_ID>']),  # 标记用于出口控制
    egress=EgressPolicy('ri.resource-policy-manager.<RID>')   # 定义出口策略
)
# 定义转换函数，指定输出、模型输入和数据输入
@transform(
    output=Output("/Foundry/Externally Hosted Models/data/inferences"),  # 输出数据路径
    model=ModelInput("/Foundry/Externally Hosted Models/models/Regression Model"),  # 模型输入路径
    foundry_input=Input("/Foundry/Externally Hosted Models/data/regression_features_input")  # 数据输入路径
)
def compute(
        export_control,
        egress,
        output,
        model,
        foundry_input
    ):
    # 从输入中获取数据框
    input_df = foundry_input.pandas()
    # 使用模型进行转换操作
    results = model.transform(input_df)
    # 将结果写入到输出路径
    output.write_pandas(results.df_out)
```

## 示例模型适配器结构

以下提供了一个用于外部托管模型的模型适配器的示例结构。

有关更多信息，我们建议参考以下内容：

- 完整的模型适配器API定义
- 如何创建和发布模型适配器
- 连接到托管在Amazon SageMaker中的模型的示例
- 连接到托管在Google Vertex AI中的模型的示例
- 连接到Open AI模型的示例
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
import palantir_models as pm

import json
import pandas as pd


class ExampleModelAdapter(pm.ExternalModelAdapter):

    def __init__(self, url, credentials_map, configuration_map):
        # 从“连接配置”映射中提取模型配置
        model_name = configuration_map['model_name']
        model_parameter = configuration_map['model_parameter']

        # 从“凭证配置”映射中提取模型凭证
        secret_key = credentials_map['secret_key']

        # 在模型加载时初始化 HTTP 客户端
        self.client = ExampleClient(url, model_name, model_parameter, secret_key)

    @classmethod
    def init_external(cls, external_context: pm.ExternalContext) -> "pm.ExternalModelAdapter":
        return cls(
            url=external_context.base_url,
            credentials_map=external_context.resolved_credentials,
            configuration_map=external_context.connection_config,
        )

    @classmethod
    def api(cls):
        # 定义输入和输出的数据格式为 Pandas 数据框
        inputs = {"df_in": pm.Pandas()}
        outputs = {"df_out": pm.Pandas()}
        return inputs, outputs

    def predict(self, df_in):
        # 构建预测请求的有效载荷
        payload = {
            "instances": df_in.apply(lambda row: {"features": row.tolist()}, axis=1).tolist()
        }

        # 客户端是一个示例，需要根据实际的外部模型进行编辑连接
        response = self.client.predict(
            ContentType="application/json",
            Body=json.dumps(payload)
        )

        # 读取响应并解析预测结果
        result = response["Body"].read().decode()
        predictions = pd.DataFrame(json.loads(result)["predictions"])
        return predictions
```

此代码实现了一个ExampleModelAdapter类，用于连接和调用外部模型服务。通过配置和凭证映射初始化 HTTP 客户端，支持基于 Pandas 数据框的输入输出。预测方法通过 HTTP 客户端发送请求并解析返回的预测结果。
