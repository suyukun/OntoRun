来源: https://palantir.com/docs/zh/foundry/integrate-models/model-adapter-reference/

# API: ModelAdapter 参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# API: ModelAdapter 参考

模型适配器是一个已发布的 Python 库，提供了 Foundry 与存储模型工件之间的通信层，使 Foundry 能够加载、初始化并在任何模型上运行推理。

要实现一个ModelAdapter，您必须了解下面列出的类：

## ModelAdapter 实现

ModelAdapter类是所有模型适配器实现必须继承的抽象基类。所有模型适配器必须实现以下四个抽象方法：

- load()
- save()注意，对于使用默认序列化器定义的模型适配器，load()和save()不是必需的。
- 注意，对于使用默认序列化器定义的模型适配器，load()和save()不是必需的。
- api()
- 单输出的predict()和多输出的run_inference()
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
63
64
import palantir_models as pm
import models_api.models_api_executable as executable_api

class ExampleModelAdapter(pm.ModelAdapter):

    @classmethod
    def load(
        cls,
        state_reader: pm.ModelStateReader,
        container_context: Optional[executable_api.ContainerizedApplicationContext] = None,
        external_model_context: Optional[executable_api.ExternalModelExecutionContext] = None
    ) -> "pm.ModelAdapter":
        """
        Python或二进制模型:
            这是Foundry将调用的方法，用于反序列化您的ModelAdapter。ModelAdapter的作者需要编写逻辑，从save方法保存/序列化模型的相同位置加载已训练模型的状态，并初始化模型。

        容器模型:
            这是Foundry将在您的容器作为这个ModelAdapter的sidecar启动后调用的方法。ModelAdapter的作者需要使用container_context中的内容初始化适配器可能需要的任何类变量。例如，用户通常会提取相关服务URI，以便在#run_inference中向容器发送POST请求。

        外部托管模型:
            这是Foundry将在初始化您的模型适配器时调用的方法。ModelAdapter的作者需要编写逻辑，以初始化并保持与外部托管模型的连接以及其他所需的模型配置。

        :param state_reader: 可用于读取模型文件的ModelStateReader对象。
        :param container_context: 仅为容器支持的模型提供，默认为None。容器上下文包括从容器名称到服务URI的映射和共享目录挂载路径。
        :param external_model_context: 仅为外部托管模型提供，默认为None。external_model_context包括用户在创建使用此Model Adapter的外部托管模型时定义的配置引用。

        :return: 一个ModelAdapter实例。
        """

    def save(self, state_writer: pm.ModelStateWriter) -> None:
        """
        这是Foundry将调用的方法，用于序列化您的模型适配器。仅当这个ModelAdapter用于包装在Foundry中新训练或重新拟合的模型时，才需要此方法。

        ModelAdapter的作者需要编写逻辑，以将已训练模型的状态和相关元数据保存到ModelStateWriter中。

        :param state_writer: 模型被序列化并保存到的ModelStateWriter对象。
        """

    @classmethod
    def api(cls) -> pm.ModelApi:
        """
        定义此模型的预期输入和输出数据结构。

        :return: 模型的ModelApi对象。
        """

    def run_inference(self, inputs, outputs) -> None:
        """
        此方法将在ModelAdapter.api方法中定义的相关输入和输出被调用。

        在关联模型上运行推理。

        :param inputs: 在ModelAdapter.api方法中定义的输入命名元组。
        :param outputs: 在ModelAdapter.api方法中定义的输出命名元组。
          输出应在run_inference方法中写入。
        """

    def predict(self, *args, **kwargs) -> Union[Tabular, Parameter]:
        """
        此方法用于对多输入(>=1)到单输出(表格或参数)模型进行推理。
        输入应通过在api()方法中定义它们的名称写入此方法的签名中。生成的输出由此方法返回。

        请注意，如果使用predict()，则用户不需要定义run_inference()方法。
        """
```

## 模型save()和load()

palantir_models_serializers库提供了许多可用于常见建模框架的模型序列化（保存）和反序列化（加载）的默认序列化器。

在某些情况下，用户可能需要实现自定义逻辑进行模型序列化或反序列化。当您使用的建模框架没有可用的默认序列化器，或者您需要手动控制在任何给定时间加载到内存中的模型时，这可能是必要的。

在这些更复杂的情况下，请参阅下面的保存和加载的实现。

## 保存

### ModelStateWriter

ModelStateWriter被提供给ModelAdapter.save方法，以便ModelAdapter可以将模型工件保存/序列化到 Foundry 存储中。

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
# ModelStateWriter 可以从 palantir_models.models 模块中导入

from io import IOBase
from typing import ContextManager

class ModelStateWriter:
    def open(self, asset_file_path: str, mode: str = "wb") -> ContextManager[IOBase]:
        """
        打开一个类似文件的对象，用于序列化模型的工件和参数。
        :param asset_file_path: 要打开的文件路径。
        :param mode: 打开文件的模式，默认为“wb”（二进制写入模式）。
        """

    def put_file(self, local_file_path, asset_file_path=None):
        """
        将本地文件放入此模型的存储库中。
        :param local_file_path: 本地文件的路径。
        :param asset_file_path: 如果提供，文件将被放置在存储库中的此路径。
            否则，文件将被放置在存储库的根目录中。
        """

    def put_directory(self, local_root_path, asset_root_path = "/"):
        """
        将本地目录及其内容放入此模型的存储库中。
        :param local_root_path: 本地根路径。
        :param asset_root_path: 相对于存储库根路径放置此目录的路径。
        """
```

每当模型适配器通过model.publish()在变换中发布时，都会调用save()方法，此时ModelStateWriter的内容会被打包成一个zip文件，并持久化存储在由新创建的模型版本引用的工件库中。

### 示例: ModelStateWriter

以下示例将模型保存为model.pkl文件。

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
from palantir_models.models import ModelAdapter, ModelStateWriter

class ExampleModelAdapter(ModelAdapter):
    def __init__(self, model):
        self.model = model

    ...

    def save(self, state_writer: ModelStateWriter):
        # 使用状态写入器保存模型的状态到 "model.pkl" 文件中
        with state_writer.open("model.pkl", "wb") as model_outfile:
            pickle.dump(self.model, model_outfile)  # 将模型序列化并写入文件

    ...
```

## Load

### ModelStateReader

ModelAdapter.load方法提供了一个ModelStateReader，以便ModelAdapter可以读取/反序列化已保存的模型工件并初始化模型。

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
# ModelStateReader 可以从 palantir_models.models 中导入
from tempfile import TemporaryDirectory

class ModelStateReader:
    def open(self, asset_file_path: str, mode: str = "rb") -> ContextManager[IOBase]:
        """
        打开一个类似文件的对象，以反序列化模型的构件和参数。
        :param asset_file_path: 资产文件的路径
        :param mode: 打开文件的模式，默认为二进制读取模式 ("rb")
        """

    def extract_to_temp_dir(self, root_dir: str = None) -> AnyStr:
        """
        返回一个包含与此模型相关的模型构件的临时目录。
        :param root_dir: 如果指定，则为提取的根目录
        """

    def extract(self, destination_path: str = None) -> None:
        """
        将存储库提取到提供的本地目录路径。
        :param destination_path: 如果指定，则为存储库将被提取到的目录
        """
```

load()方法在模型适配器实例化时被调用（通过变换中的ModelInput，或启动由模型支持的实时或批量部署）。然后，此方法访问与ModelStateWriter写入的相同工件库，并通过ModelStateReader提供对其内容的访问。在执行任何变换或推理逻辑之前调用load()。

### 示例: ModelStateReader

以下示例加载一个模型文件，并返回一个用其初始化的模型适配器实例。

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
from palantir_models.models import ModelAdapter, ModelStateReader

class ExampleModelAdapter(ModelAdapter):
    def __init__(self, model):
        self.model = model

    @classmethod
    def load(cls, state_reader: ModelStateReader):
        # 使用 ModelStateReader 打开模型文件 "model.pkl" 并读取
        with state_reader.open("model.pkl", "rb") as model_infile:
            model = pickle.load(model_infile)  # 反序列化加载模型
        return cls(model)  # 返回 ExampleModelAdapter 的实例

    ...
```

结合上面显示的save()方法使用时，此方法将检索在save()方法中持久化的相同model.pkl对象。一个ModelStateReader对象也提供给容器化模型，并由用户上传的 zip 文件支持。

### ContainerizedApplicationContext

ContainerizedApplicationContext是非必填的，并且仅当模型由一个或多个容器镜像支持时，才会提供给ModelAdapter.load方法。上下文对象包括一个共享目录挂载路径和一个从容器名称到其服务 URI 的映射。每个容器可以有多个服务 URI，因为拥有多个开放端口是有效的。

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
# 注意，这个类类型不需要在自定义适配器中导入
class ContainerizedApplicationContext:
    def services(self) -> Dict[str, List[str]]:
        """
        映射每个容器的名称到该容器提供的服务URI列表。
        """

    def shared_empty_dir_mount_path(self) -> str:
        """
        一个共享空目录的挂载路径，该目录在所有容器内以及模型适配器中可用。
        容器和模型入口点可以读取和写入该目录。
        """
```

一个示例填充的服务变量可能如下所示：

```
Copied!1
2
3
4
{
    "container1": ["localhost:8080"],  # container1 映射到本地的 8080 端口
    "container2": ["localhost:8080", "localhost:8081"],  # container2 映射到本地的 8080 和 8081 端口
}
```

### 示例: ContainerizedApplicationContext

以下示例通过提供的ContainerizedApplicationContext初始化一个具有特定卷路径、主机和端口的模型适配器。

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
from palantir_models.models import ModelAdapter, ModelStateReader
import models_api.models_api_executable as executable_api

class ExampleModelAdapter(ModelAdapter):
    def __init__(self, shared_volume_path, model_host_and_port):
        # 初始化方法，接收共享卷路径和模型的主机及端口
        self.shared_volume_path = shared_volume_path
        self.model_host_and_port = model_host_and_port

    @classmethod
    def load(cls, state_reader, container_context: executable_api.ContainerizedApplicationContext):
        # 类方法，用于加载模型适配器实例
        shared_volume_path = container_context.shared_empty_dir_mount_path
        # 从容器上下文中获取共享卷路径
        model_host_and_port = container_context.services["container1"][0]
        # 从容器上下文中获取模型的主机及端口信息
        return cls(shared_volume_path, model_host_and_port)

    ...
```

### ExternalModelContext

ExternalModelContext是非必填的，并且仅当模型是外部托管模型时才会提供给ModelAdapter.load方法。该上下文对象包含一个表示外部托管模型的对象，以及连接此外部托管模型所需的用户定义的解密密钥映射。

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
# 注意这个类类型不需要在编写的适配器中导入
class ExternalModelContext:
    def external_model(self) -> models_api_external_ExternalModel:
        """
        表示外部托管模型的对象，主要包含 base_url 和 connection_configuration。
        """

    def resolved_credentials(self) -> Dict[str, str]:
        """
        连接这个外部托管模型所需的用户定义的解密秘密值的映射。
        """

# 注意这个类类型不需要在编写的适配器中导入
class models_api_external_ExternalModel:
    def base_url(self) -> str:
        """
        用户定义的表示此外部托管模型托管地址的 url。
        """

    def connection_configuration(self) -> Dict[str, str]:
        """
        用户定义的未加密配置字段的字典。
        这用于存储特定的配置细节，如模型名称、推理参数或预测阈值。
        """
```

### 示例: ExternalApplicationContext

以下示例初始化一个模型适配器，该适配器执行对外部托管模型的请求。有关使用外部托管模型的更多信息，请阅读文档。

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
from palantir_models.models import ModelAdapter, ModelStateReader
import models_api.models_api_executable as executable_api

class ExampleModelAdapter(ModelAdapter):
    def __init__(self, url, credentials_map, configuration_map):
        # 从“连接配置”映射中提取模型配置
        model_name = configuration_map['model_name']
        model_parameter = configuration_map['model_parameter']

        # 从“凭证配置”映射中提取模型凭证
        secret_key = credentials_map['secret_key']

        # 在加载模型时初始化 http 客户端
        self.client = ExampleClient(url, model_name, model_parameter, secret_key)

    @classmethod
    def load(
            cls,
            state_reader: ModelStateReader,
            container_context: Optional[executable_api.ContainerizedApplicationContext] = None,
            external_model_context: Optional[executable_api.ExternalModelExecutionContext] = None,
            ) -> "ModelAdapter":
        return cls(
            url=external_model_context.external_model.base_url,
            credentials_map=external_model_context.resolved_credentials,
            configuration_map=external_model_context.external_model.connection_configuration,
        )

    ...
```

## 模型 API

模型适配器的api()方法指定了执行该模型适配器的推理逻辑所需的预期输入和输出。输入和输出是分别指定的。

### 示例api()

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
import palantir_models as pm

class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义输入数据结构，使用 Pandas 数据框，其中包含一个名为 'input_feature' 的特征列，数据类型为 float
        inputs = {
            "df_in": pm.Pandas([('input_feature', float)])
        }
        # 定义输出数据结构，使用 Pandas 数据框，其中包含一个名为 'output_feature' 的特征列，数据类型为 int
        outputs = {
            "df_out": pm.Pandas([('output_feature', int)])
        }
        # 返回输入和输出的数据结构定义
        return inputs, outputs

    ...
```

### 模型输入

ModelInput类型包含可以在ModelAdapter.api方法中定义的输入类型。模型适配器支持以下输入类型：

- 表格
- 参数
- 文件系统
- 媒体引用
注意：媒体引用支持目前处于测试阶段，仅支持在Python变换中的推理。具有模型的媒体引用不支持在建模目标应用程序中进行自动评估、批量部署或实时部署。

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
# DFType 和 ModelInput 可以从 palantir_models.models.api 中导入

class ModelInput:
    Tabular = TabularInput
    FileSystem = FileSystemInput
    Parameter = ParameterInput
    MediaReference = MediaReferenceInput

class TabularInput:
    def __init__(self, name: str, df_type: DFType = DFType.SPARK, columns: List[ModelApiColumn]):
        """
        用于指定 ModelAdapter 期望一个表格输入。
        如果适用，此输入类型将把表格输入转换为 `df_type` 中指定的类型。
        接受 Pandas 数据框、Spark 数据框和 TransformInputs 作为表格输入类型。
        """

class ParameterInput:
    def __init__(self, name: str, type: type, default = None):
        """
        用于指定 ModelAdapter 期望一个类型为 'type' 的常量值参数。
        参数输入可用的类型包括：str, int, float, bool, list, set, dict, tuple。
        如果在调用 .transform() 时没有直接传递，将使用提供的默认值。
        """

class FileSystemInput:
    def __init__(self, name: str):
        """
        用于指定 ModelAdapter 期望一个文件系统输入。
        """

class MediaReferenceInput:
    def __init__(self, name: str):
        """
        用于指定 ModelAdapter 期望一个媒体引用作为输入。
        """

class DFType(Enum):
    SPARK = "spark"
    PANDAS = "pandas"

class ModelApiColumn(NamedTuple):
    """
    用于指定表格输入的列名称和类型。
    """
    name: str
    type: type
    required: bool = True
```

### 表格输入

TabularInput用于指定提供给model.transform()的输入预期为表格类型。在此模型适配器的推理逻辑中，此输入的类型将是api()方法中指定的df_type参数。如有必要，将执行适当的类型转换。允许的表格类型如下：

- TransformInput
- Pandas DataFrame
- Spark DataFrame注意：Spark 数据帧仅在适配器 API 中支持表格输入，需指定df_type=DFType.SPARK。对于指定DFType.PANDAS的表格输入，不支持对 Spark 数据帧的转换。
- 注意：Spark 数据帧仅在适配器 API 中支持表格输入，需指定df_type=DFType.SPARK。对于指定DFType.PANDAS的表格输入，不支持对 Spark 数据帧的转换。
#### 列类型

TabularInputs 还指定了一系列ModelApiColumn，描述表格输入的预期列模式。type参数可以是以下之一：

- str
- int
- float
- bool
- list
- dict
- set
- tuple
- datetime.date
- datetime.time
- datetime.datetime
- typing.Any
- MediaReference
typing库中的List、Dict、Set和Tuple类型别名也被接受。一些示例如下：

- List[str],Set[str]
- Dict[str, float]
- Tuple[int, int]
列类型不会被强制执行，而是作为向该模型适配器的使用者传达预期列类型的方式。唯一的例外是MediaReference类型，期望列中的每个元素为媒体引用字符串，并将在传递到此模型适配器的推理逻辑之前将每个元素转换为MediaReference对象。

### 参数输入

ParameterInput用于指定提供给model.transform()的输入预期为参数类型。参数是具有type参数指定类型的常量值输入。接受的参数输入类型如下：

- str
- int
- float
- bool
- list
- dict
- set
- tuple
- typing.Any
参数类型是强制的，任何不符合指定类型的传递给model.transform()的参数输入将抛出错误。

参数输入还可以为在模型适配器的api()方法中定义的参数输入没有提供的model.transform()输入指定一个default值。

### 文件系统输入

FileSystemInput用于指定提供给model.transform()的输入预期为文件系统类型。仅支持 TransformInputs 作为FileSystemInput的输入类型。

### 媒体引用输入

MediaReferenceInput用于指定提供给model.transform()的输入预期为媒体引用。媒体引用预期为str类型，并包含完整的媒体引用对象定义。模型适配器将此媒体引用字符串转换为MediaReference对象，其中包含与被引用的媒体项交互的方法。

### 模型输出

ModelOutput包含在ModelAdapter.api方法中定义的输出类型。

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
# ModelOutput 可以从 palantir_models.models.api 导入

class ModelOutput:
    FileSystem = FileSystemOutput  # 文件系统输出
    Parameter = ParameterOutput    # 参数输出

class TabularOutput:
    def __init__(self, name: str):
        """
        用于指定 ModelAdapter 将产生一个表格输出。
        仅支持 Pandas 或 Spark 数据框作为表格输出类型。
        """

class ParameterOutput:
    def __init__(self, name: str, type: type, default = None):
        """
        用于指定 ModelAdapter 将产生一个类型为 'type' 的常量值参数。
        参数输出的可用类型有：str, int, float, bool, list, set, dict, tuple。
        如果在 `run_inference()` 中没有写入值，则使用提供的默认值。
        """
```

两种可用的模型输出都与其输入类似。一个主要区别是TabularOutput没有df_type参数。它能够接受Pandas和Spark数据帧。

## 模型推理

### predict()方法

对于具有单一表格或参数类型输出的模型，可以使用predict()方法代替run_inference()方法来定义模型适配器的推理逻辑。此方法的参数将是模型适配器的api()方法中定义的输入对象的名称。参数不要求保持与定义时相同的顺序，但名称必须匹配。

### predict()方法示例

以下示例定义了一个用于多表格输入、单表格输出模型适配器的predict()方法。

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
import palantir_models as pm

class ExampleModelAdapter(pm.ModelAdapter):
    ...

    # 定义类方法 api，指定模型的输入和输出格式
    @classmethod
    def api(cls):
        # 输入是两个 Pandas 数据框
        inputs = {"input_1": pm.Pandas(), "input_2": pm.Pandas()}
        # 输出也是一个 Pandas 数据框
        outputs = {"output_dataframe": pm.Pandas()}
        return inputs, outputs

    # 定义预测方法，接受两个输入数据框
    def predict(self, input_1, input_2):
        # 使用输入数据进行推理逻辑，生成结果数据框
        resulting_dataframe = ... # 使用 input_1 和 input_2 进行一些推理逻辑
        return resulting_dataframe
```

在上述示例中，两个输入（input_1和input_2）通过名称在predict()方法的签名中被引用。函数返回的数据框resulting_dataframe将被写入到名为output_dataframe的单一输出中。

### run_inference()方法

对于多输出模型或写入文件系统的模型，必须通过run_inference()方法定义自定义推理逻辑。此方法接受两个参数：inputs和outputs。这两个参数都是NamedTuples，其名称对应于在api()方法中定义的输入和输出的name参数。

### 输入

通过名称引用输入将访问传递给model.transform()的对象，该对象对应于具有相同名称的api()输入。

### 示例：输入

给定以下ModelAdapter定义：

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
from palantir_models as pm

class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义输入和输出的数据格式
        inputs = {
            "df_in": pm.Pandas([("input_feature", float)])  # 输入特征为浮点数
        }
        outputs = {
            "df_out_one": pm.Pandas([("feature_one", int)]),  # 输出一个整数特征
            "df_out_two": pm.Pandas([("output_feature_1", int),  # 输出特征1为整数
                                     ("output_feature_2", float)])  # 输出特征2为浮点数
        }
        return inputs, outputs

    def run_inference(self, inputs, outputs):
        # 获取输入数据帧
        my_input_df = inputs.df_in

        # 定义输出数据帧
        my_output_one = outputs.df_out_one
        my_output_two = outputs.df_out_two

    ...
```

以下对.transform()的调用：

```
Copied!1
2
3
4
5
6
7
8
@transform(
    my_input_data=Input(...),  # 输入数据
    my_output_data_one=Output(...),  # 输出数据一
    my_output_data_two=Output(...),  # 输出数据二
    my_model=ModelInput(...)  # 模型输入
)
def compute(my_input_data, my_output_data_one, my_output_data_two, my_model):
    my_model_outputs = my_model.transform(my_input_data)  # 使用模型对输入数据进行转换
```

在模型适配器的run_inference()方法中，my_input_df对象是对名为"input_dataframe"的输入的引用，该输入是Pandas类型的表格输入，将等于从变换传入的my_input_dataTransformInput的pandas表示形式。

### 输出

通过名称引用输出将提供一个可写对象，该对象对应于同名的api()输出。每个对象都有一个.write()方法，用于指定将哪些数据写入每个输出。

### 示例：输出

给定以下ModelAdapter定义：

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
from palantir_models as pm

class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义输入输出的数据格式
        inputs = {
            "input_dataframe": pm.Pandas([('input_feature', float)])  # 输入是一个DataFrame，其中包含一个浮点数类型的列
        }
        outputs = {
            "output_dataframe_one": pm.Pandas([('output_feature', int)]),  # 输出是两个DataFrame，每个包含一个整数类型的列
            "output_dataframe_two": pm.Pandas([('output_feature', int)]),
        }
        return inputs, outputs

    def run_inference(self, inputs, outputs):
        my_input_df = inputs.input_dataframe  # 从输入中获取DataFrame
        # 对输入DataFrame进行处理，生成新的DataFrame
        my_output_dataframe_one = do_something_to_input_and_return_a_new_dataframe(my_input_df)
        my_output_dataframe_two = do_something_else_to_input_and_return_a_new_dataframe(my_input_df)
        # 将结果写入输出DataFrame
        outputs.output_dataframe_one.write(my_output_dataframe_one)
        outputs.output_dataframe_two.write(my_output_dataframe_two)

    ...
```

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
@transform(
    my_input_data=Input(...),  # 输入数据
    my_output_data_one=Output(...),  # 输出数据一
    my_output_data_two=Output(...),  # 输出数据二
    my_model=ModelInput(...)  # 模型输入
)
def compute(my_input_data, my_output_data_one, my_output_data_two, my_model):
    # 使用模型对输入数据进行转换
    my_model_outputs = my_model.transform(my_input_data)
    # 获取转换后的第一个输出数据框
    my_output_dataframe_one = my_model_outputs.output_dataframe_one
    # 获取转换后的第二个输出数据框
    my_output_dataframe_two = my_model_outputs.output_dataframe_two
    # 将第一个输出数据框写入 my_output_data_one
    my_output_data_one.write_pandas(my_output_dataframe_one)
    # 将第二个输出数据框写入 my_output_data_two
    my_output_data_two.write_pandas(my_output_dataframe_two)
```

在变换中，my_output_dataframe_one和my_output_dataframe_two对象将等于在模型适配器的run_inference()方法中写入output_dataframe_one和output_dataframe_two输出的对象（在本例中为my_output_dataframe_one和my_output_dataframe_two）。

## 媒体引用

有关 Foundry 中媒体引用的信息可以在此处找到。

如果在模型适配器的api()中指定了类型为MediaReference的参数输入或表格输入列，通过model.transform()提供的媒体引用字符串将被转换为MediaReference对象。此对象类型提供与媒体引用交互的方法。

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
class MediaReference:
    @property
    def media_reference(self):
        """
        原始媒体引用字符串。
        """

    @property
    def media_item_rid(self):
        """
        从媒体引用中提取的媒体项RID。
        """

    def get_media_item(self):
        """
        以文件对象形式返回媒体项。
        """

    def get_media_item_via_access_pattern(self, access_pattern_name, access_pattern_path):
        """
        以文件对象形式返回媒体项的访问模式。
        根据媒体集的持久性策略，计算后可能会缓存访问模式。
        """

    def transform_media_item(self, output_path, transformation):
        """
        对媒体项应用转换，并以文件对象形式返回。
        output_path 将提供给转换过程。
        转换计算将由 Mio 完成，而不是由这个 Spark 模块完成。
        """

    def get_media_item_metadata(self):
        """
        返回媒体项的元数据（宽度、高度等）。
        """
```
