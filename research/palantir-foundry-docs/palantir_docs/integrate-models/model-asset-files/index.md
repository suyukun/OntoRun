来源: https://palantir.com/docs/zh/foundry/integrate-models/model-asset-files/

# 从预训练文件发布模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从预训练文件发布模型

Palantir支持创建一个封装平台外生成权重的模型。这些文件可以包括开源模型权重、本地开发环境中训练的模型、代码工作区应用程序中训练的模型，以及来自遗留系统的模型权重。

一旦创建了Palantir模型，Palantir提供以下功能：

- 与批处理管道和实时模型托管的集成。
- 完整版本控制、细粒度权限管理和受管模型沿袭。
- 通过建模目标进行模型管理和实时部署。
- 绑定到Ontology，以便通过模型上的函数和假设情景分析进行操作化。
## 从模型文件创建模型

要从模型文件创建模型，您将需要以下内容：

- 可以上传到Palantir的模型文件
- 一个模型适配器，告诉Palantir如何加载和运行模型推理
### 1. 将模型文件上传到非结构化数据集

首先，将您的模型文件上传到Palantir平台中的一个非结构化数据集。在项目中选择+新建 > 数据集来创建一个新数据集。

然后，选择导入新数据并从您的计算机中选择要上传到模型的文件。

如果需要，您可以将许多不同的文件上传到同一个数据集中。该数据集将是非结构化的，意味着它不会有表格式架构。

### 2. 创建模型训练库以定义模型适配器逻辑

创建一个新的代码库，以管理从非结构化数据集中读取模型文件的逻辑。该逻辑将把这些文件封装在一个模型适配器中并发布为一个模型。在代码库应用程序中，选择用模型训练语言模板初始化一个模型集成库。

查看关于模型训练模板和模型适配器API的完整文档作为参考。

### 3. 将权重发布到模型

要将非结构化数据集中的模型文件作为Palantir模型发布，您必须编写一个完成以下任务的变换：

- 从非结构化数据集中加载保存的模型文件
- 实例化一个模型适配器
- 将模型适配器发布为模型资源
您可以将加载和发布模型的逻辑放在库中的model_training文件夹内。

有关更多信息，我们建议查看以下文档：

- 模型适配器API定义的完整文档
- 如何从非结构化数据集中读取文件
- 如何使用模型训练模板创建和发布模型适配器
- 本地训练模型的示例封装
一旦您定义了模型训练逻辑，选择搭建以执行读取模型文件和发布模型的逻辑。

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
from transforms.api import transform, Input
from palantir_models.transforms import ModelOutput, copy_model_to_driver

import palantir_models as pm
import palantir_models_serializers as pms

@transform(
    model_files=Input("<Model Files Dataset>"),
    model_output=ModelOutput("<Your Model Path>")
)
def compute(model_files, model_output):
    # 将模型文件复制到驱动器上
    model = copy_model_to_driver(model_files.filesystem())
    # 创建模型适配器
    wrapped_model = ExampleModelAdapter(model)
    # 发布模型输出
    model_output.publish(
        model_adapter=wrapped_model
    )

class ExampleModelAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        model=pms.DillSerializer()
    )
    def __init__(self, model):
        self.model = model  # 初始化模型

    @classmethod
    def api(cls):
        pass  # 实现此模型的API

    def predict(self, df_in):
        pass # 实现推理逻辑
```

这个代码主要用于在一个数据转换平台上加载和发布机器学习模型。ExampleModelAdapter类是一个适配器，用于包装实际的模型对象，并提供序列化支持和推理接口。

### 4. 使用已发布的模型

一旦您成功发布了模型，就可以以推理为目的使用该模型。请使用以下文档作为指导：

- 在建模目标中部署模型用于实时推理
- 在建模目标中将上传的模型用于批处理管道
- 配置执行模型推理的Python变换