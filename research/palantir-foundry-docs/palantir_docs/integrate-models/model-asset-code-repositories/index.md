来源: https://palantir.com/docs/zh/foundry/integrate-models/model-asset-code-repositories/

# 在代码库中训练模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在代码库中训练模型

模型资产目前不支持SparkML库。我们建议您切换到单节点机器学习框架，如PyTorch、TensorFlow、XGBoost、LightGBM或scikit-learn。如果您需要SparkML，可以使用数据集支持的模型来训练模型。

模型可以在代码库应用中使用模型训练模板进行训练。

要训练模型，请完成以下步骤：

- 编写模型适配器
- 编写Python变换以训练模型
- 搭建Python变换以发布训练后的模型
- 使用模型
## 1. 编写模型适配器

模型使用模型适配器以确保Foundry正确初始化、序列化、反序列化并在模型上进行推理。您可以在代码库中从模型适配器库模板或模型训练模板中编写模型适配器。

模型适配器不能直接在Python变换库中编写。要从现有库中生成模型，请使用模型适配器库并将该库导入到变换库中，或迁移到模型训练模板。

阅读更多关于何时使用每种类型的模型适配器库，以及如何在模型适配器创建文档中创建它们。以下步骤假定使用模型训练模板。

### 模型适配器实现

模型适配器和模型训练代码应在不同的Python模块中，以确保训练后的模型可以在下游变换中使用。在模板中，我们有单独的model_adapters和model_training模块用于此目的。在adapter.py文件中编写您的模型适配器。

模型适配器的定义将依赖于所训练的模型。要了解更多信息，请查阅ModelAdapter API参考，查看示例sklearn模型适配器，或阅读监督学习教程以了解更多。

## 2. 编写Python变换以训练模型

接下来，在您的代码库中，创建一个新的Python文件来存放您的训练逻辑。

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
from transforms.api import transform, Input
from palantir_models.transforms import ModelOutput
from model_adapter.example_adapter import ExampleModelAdapter  # 这是您自定义的 ModelAdapter

@transform(
    training_data=Input("/path/to/training_data"),
    model_output=ModelOutput("/path/to/model")                 # 这是模型的路径
)
def compute(training_data, model_output):
    '''
        此函数包含读取和写入 Foundry 的逻辑。
    '''
    trained_model = train_model(training_data)                 # 1. 在 Python transform 中训练模型
    wrapped_model = ExampleModelAdapter(trained_model)         # 2. 使用自定义 ModelAdapter 包装已训练的模型
    model_output.publish(                                      # 3. 将包装后的模型保存到 Foundry
        model_adapter=wrapped_model                            #    Foundry 将调用 ModelAdapter.save 来生成模型
    )


def train_model(training_data):
    '''
        此函数包含您的自定义训练逻辑。
    '''
    pass
```

此逻辑正在发布到ModelOutput。在您提交更改后，Foundry 将自动在提供的路径上创建一个模型资源。您还可以通过@configure注解配置模型训练所需的资源，如CPU、内存和GPU需求。

## 3. 预览您的Python变换以测试您的逻辑

在代码库应用中，您可以选择预览来测试您的变换逻辑，而无需运行完整的搭建。请注意，预览将在比您可能通过@configure注解配置的更小的资源配置文件上运行。

### ModelOutput预览

ModelOutput预览允许您验证您的模型训练逻辑以及模型序列化、反序列化和API实现。

### ModelInput预览

ModelInput预览允许您针对现有模型验证您的推理逻辑。请注意，在代码库中进行预览时，每个ModelInput的大小限制为5GB。

## 4. 搭建您的Python变换以发布训练好的模型

在您的代码库中，选择搭建来运行您的变换。Foundry 将在执行您的训练逻辑之前解析Python依赖项和模型的依赖项。

调用ModelOutput.publish()将会在Foundry上发布您的模型版本。Foundry 将调用ModelAdapter.save()函数，并赋予您的ModelAdapter序列化所有执行所需字段的能力。

## 5. 使用模型

### 提交到建模目标

模型可以发布到建模目标以：

- 自动模型评估
- 批处理管道
- 实时托管
### 在Python变换中运行推理

您还可以在管道中使用Palantir模型，具体如下所述。

如果在不同的Python变换库中使用模型，您必须将模型适配器Python库添加到您的编写Python环境。这通常可以在Palantir中的模型资源页面上找到。

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

@transform(
    inference_output=Output("/path/to/inference_output"),  # 指定推理输出的路径
    inference_input=Input("/path/to/inference_input"),    # 指定推理输入的路径
    model=ModelInput("/path/to/model"),                   # 指定模型的路径
)
def compute(inference_output, inference_input, model):        # model 将是 ExampleModelAdapter 的一个实例
    inference_results = model.transform(inference_input)  # inference_results 将是 predict() 或 run_inference() 方法的返回结果。
    # 替换 "output_data" 为模型版本 API 中指定的输出，可以在模型版本的网页上查看。
    # 例如，对于 Hugging Face 适配器，inference_results.output_data 是合适的输出。
    inference = inference_results.output_data
    inference_output.write_pandas(inference)  # 将推理结果写入指定的输出路径
```

此代码在使用 Palantir 的平台进行机器学习推理时，将模型的推理输入转换为推理输出。通过指定路径，可以进行模型的输入输出管理和模型版本控制。

## ModelInput 和 ModelOutput API

在上述变换中调用的ModelInput和ModelOutputObject 是直接负责与代码库中的模型进行交互的 Object。以下是这些 Object 的摘要：

### ModelInput

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
# ModelInput 可以从 palantir_models.transforms 模块中导入

class ModelInput:
    def __init__(self, model_rid_or_path: str, model_version: Optional[str] = None):
        '''
            `ModelInput` 类用于检索现有模型以便在转换中使用。它接受最多两个参数：
            1. 模型的路径（或模型的 RID）。
            2. （可选）要检索的模型版本 RID。
               如果未提供，则使用最近发布的模型。

            例如：ModelInput("/path/to/model/asset")
        '''
        pass
```

在变换函数中，由ModelInput指定的模型将被实例化为与检索到的模型版本关联的模型适配器的实例。Foundry将在启动变换搭建之前，调用ModelAdapter.load或使用定义的@auto_serialize实例来设置模型。因此，ModelInput实例可以访问其关联的加载模型状态和模型适配器中定义的所有方法。

### ModelOutput

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
# ModelOutput 可以从 palantir_models.transforms 模块中导入

class ModelOutput:
    def __init__(self, model_rid_or_path: str):
        '''
            `ModelOutput` 用于发布模型的新版本。
            `ModelOutput` 接受一个参数，即模型的路径（或模型 RID）。
            如果该资产尚不存在，当用户选择 Commit 或 Build 并执行转换检查（CI）时，ModelOutput 将创建该资产。
        '''
        pass
```

在变换函数中，通过指派ModelOutput检索到的Object是一个WritableModel，能够通过使用publish()方法发布新的模型版本。此方法以模型适配器作为参数，并创建与之关联的新模型版本。在publish()期间，平台使用定义的@auto_serialize实例或执行实现的save()方法。这允许模型适配器将模型文件或检查点序列化到state_writerObject中。
