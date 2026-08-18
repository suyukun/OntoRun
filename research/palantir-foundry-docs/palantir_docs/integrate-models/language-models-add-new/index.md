来源: https://palantir.com/docs/zh/foundry/integrate-models/language-models-add-new/

# 添加对新语言模型的支持

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 添加对新语言模型的支持

除了无代码语言模型外，Foundry还支持用户与流行的语言模型框架集成，如Hugging Face ↗或spaCy ↗。通过Conda或Pip可用的任何Python框架都可以在Foundry中使用。然而，由于许多框架从互联网下载预训练模型、语料库或其他配置，它们通常需要额外的步骤才能在Foundry中完全功能。这是由于Foundry的安全架构，默认情况下，拒绝用户编写的Python代码访问公共互联网。所需的额外步骤取决于语言模型框架的具体情况。

## Hugging Face

要为不作为无代码语言模型提供的Hugging Face语言模型添加支持，可以选择以下两种方法：

- 将模型文件作为原始数据集导入。
- 将Hugging Face域名列入允许列表。
### 将模型文件作为数据集导入

您可以将任何模型从Hugging Face模型库导入为数据集。您可以在代码库或代码工作区中使用该数据集。

首先，从Hugging Face下载 ↗模型文件。然后，将模型作为无模式数据集上传，以将文件带入Foundry。这些文件可以通过前端上传（新建 > 数据集 > 导入 > 选择所有文件）或通过数据连接同步上传，如果模型文件存储在您私人网络的共享驱动器上。

导入的数据集应包含Hugging Face模型详细信息中的文件和版本标签的所有文件。然而，只需要一个二进制模型文件（例如，pytorch_model.bin或tf_model.h5）。在大多数情况下，我们建议使用PyTorch模型作为二进制模型文件。

一旦模型文件存储在数据集中，您可以在变换中使用该数据集作为输入。根据模型的大小，您可能需要指定一个Spark配置文件，如DRIVER_MEMORY_MEDIUM，以将模型加载到内存中。下面的代码使用了来自foundry-huggingface-adapters的实用工具：

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
from palantir_models.transforms import ModelOutput
from transforms.api import transform, Input
from transformers import AutoTokenizer, AutoModel
from huggingface_adapters.utils import copy_model_to_driver

# 定义一个转换函数，将Hugging Face模型从输入路径复制到Driver并进行处理
@transform(
    model_output=ModelOutput("/path/to/output/model_asset"), # 输出模型的路径
    hugging_face_raw=Input("/path/to/input/dataset"), # 输入数据集的路径
)
def compute(model_output, hugging_face_raw):
    # 将Hugging Face模型复制到Driver的临时目录
    temp_dir = copy_model_to_driver(hugging_face_raw.filesystem())
    # 从临时目录加载预训练的分词器
    tokenizer = AutoTokenizer.from_pretrained(temp_dir)
    # 从临时目录加载预训练的模型
    model = AutoModel.from_pretrained(temp_dir)

    # 用模型适配器包装模型并作为新模型保存
    # model_output.publish(...)
    # 这里需要实现将包装后的模型发布的逻辑
```

根据应用案例，您可以使用一个语言模型适配器，例如EmbeddingAdapter：

```
Copied!1
2
3
4
5
6
7
# 其他导入
from huggingface_adapters.embedding_adapter import EmbeddingAdapter
# ...
    model_output.publish(
        model_adapter=EmbeddingAdapter(tokenizer, model), # 使用EmbeddingAdapter将tokenizer和model进行适配
        change_type=ModelVersionChangeType.MINOR # 设定模型版本变化类型为次要更新
    )
```

#### 将 Hugging Face 域名加入允许列表

或者，您可以在 Foundry 注册的网络出口策略中，将相关的 Hugging Face 域名加入允许列表。需要加入允许列表的相关域名是https://huggingface.co ↗和https://cdn-lfs.huggingface.co ↗。有关网络出口配置的详细信息，请参阅Foundry 管理文档。

此外，从 Hugging Face 加载模型的代码库必须添加transforms-external-systems库并进行相应配置以使用新创建的出口策略。配置设置完成后，可以在 Python 变换中加载开源语言模型。

如果您收到错误PermissionError: [Errno 13] Permission denied: '/.cache'，您必须在加载模型时传入一个缓存目录，如下例所示。

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
from palantir_models.transforms import ModelOutput
from transforms.api import transform, Input
from transforms.external.systems import use_external_systems, EgressPolicy, ExportControl
from transformers import AutoTokenizer, AutoModel
import tempfile

@use_external_systems(
    export_control=ExportControl(markings=['<marking ID>']),  # 设置导出控制的标记
    egress=EgressPolicy(<policy RID>),  # 设置数据流出策略
)
@transform(
    model_output=ModelOutput('/path/to/output/model_asset'),  # 模型输出路径
    text_input=Input('/path/to/input/dataset'),  # 文本输入数据集路径
)
def compute(export_control, egress, model_output, text_input):
    CACHE_DIR = tempfile.mkdtemp()  # 创建临时缓存目录
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased", cache_dir=CACHE_DIR)  # 加载预训练的BERT分词器
    model = AutoModel.from_pretrained("bert-base-cased", cache_dir=CACHE_DIR)  # 加载预训练的BERT模型

    # Wrap the model instance with a model adapter and save it in the Palantir platform
    # 将模型实例包装为适配器并在Palantir平台上保存
    # model_output.publish(...)
```

注意：<marking ID>和<policy RID>需要被替换为实际的标记和策略ID。

#### 在 Foundry 中的使用

一旦您通过数据集或通过 Hugging Face 域获得语言模型的访问权限，您可以通过使用模型适配器将其包装为 Palantir 模型，从而与之集成，具体定义请参阅代码库中的模型训练文档。
