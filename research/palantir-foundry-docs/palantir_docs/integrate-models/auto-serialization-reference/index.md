来源: https://palantir.com/docs/zh/foundry/integrate-models/auto-serialization-reference/

# API:palantir_models_serializers参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# API:palantir_models_serializers参考

palantir_models_serializers库提供了许多用于保存和加载在 Foundry 内训练的模型的默认序列化方法，大多数模型应该能够使用其中一个默认模型序列化器。

## 如何编写模型序列化器

在某些情况下，创建一个可重用的auto_serializer可能很有用，例如，如果您的组织有一个模型格式被重复使用并经常集成到 Foundry 作为模型，那么创建一个可重用的auto_serializer可以标准化和减少不同模型和团队之间的重复代码。

要创建一个auto_serializer，您应该扩展palantir_models.models._serialization.ModelSerializer基类并实现__init__、serialize和deserialize方法。

- __init__方法是使用者与您的序列化器交互的构造函数。
- serialize方法将提供您应该序列化到palantir_models.models._state_accessors.ModelStateWriter的对象。
- deserialize方法将在模型加载时调用，并允许您从提供的palantir_models.models._state_accessors.ModelStateReader中重新实例化并返回序列化的模型。
您的auto_serializer应该作为一个共享 Python 库发布。

## 提供的序列化器的实现

作为参考，我们在palantir_models_serializers中提供了现有默认序列化器的实现。

### palantir_models_serializers.CloudPickleSerializer

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
import importlib
from types import ModuleType
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader

class CloudPickleSerializer(ModelSerializer[object]):
    """使用 cloudpickle 库进行通用对象序列化的序列化器"""

    file_name = "cloudpickle.pkl"  # 保存序列化对象的文件名
    cloudpickle: ModuleType

    def __init__(self):
        self.cloudpickle = importlib.import_module("cloudpickle")  # 动态导入 cloudpickle 模块

    def serialize(self, writer: ModelStateWriter, obj: object):
        # 将对象 obj 序列化并写入到文件中
        with writer.open(self.file_name, "wb") as cloudpickle_file:
            self.cloudpickle.dump(obj, cloudpickle_file)

    def deserialize(self, reader: ModelStateReader) -> object:
        # 从文件中读取对象并反序列化
        with reader.open(self.file_name, "rb") as cloudpickle_file:
            obj = self.cloudpickle.load(cloudpickle_file)
        return obj
```

此代码定义了一个名为CloudPickleSerializer的类，用于利用cloudpickle库对通用对象进行序列化和反序列化操作。它通过ModelStateWriter和ModelStateReader进行文件操作，序列化后的对象存储在名为cloudpickle.pkl的文件中。

### palantir_models_serializers.DillSerializer

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
import importlib
from types import ModuleType
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader

class DillSerializer(ModelSerializer[object]):
    """Serializer utilizing the dill library for generic objects
    使用dill库对通用对象进行序列化的序列化器
    """

    file_name = "dill.pkl"
    dill: ModuleType

    def __init__(self):
        # 动态导入dill模块
        self.dill = importlib.import_module("dill")

    def serialize(self, writer: ModelStateWriter, obj: object):
        # 使用dill库将对象序列化并写入文件
        with writer.open(self.file_name, "wb") as dill_file:
            self.dill.dump(obj, dill_file, recurse=True)

    def deserialize(self, reader: ModelStateReader) -> object:
        # 从文件中读取并反序列化对象
        with reader.open(self.file_name, "rb") as dill_file:
            obj = self.dill.load(dill_file)
        return obj
```

此代码定义了一个名为DillSerializer的类，它使用dill库进行对象的序列化和反序列化。DillSerializer类继承自ModelSerializer。在序列化过程中，serialize方法将对象写入名为dill.pkl的文件中；在反序列化过程中，deserialize方法从该文件中读取对象。

### palantir_models_serializers.HfAutoModelSerializer

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
class HfAutoModelSerializer(ModelSerializer):
    """
    用于huggingface transformers的AutoModel类的序列化器，使用from_pretrained和save_pretrained方法。
    允许配置一个特定的子类（例如AutoModelForSequenceClassification或BertForTokenClassification），
    并传递额外的关键字参数给from_pretrained（例如num_labels=2）。
    """

    DIR_NAME = "model"  # 保存模型的目录名称

    def __init__(self, model_class=None, **load_kwargs):
        if model_class is None:
            # 如果没有提供model_class，默认使用transformers库的AutoModel
            transformers = importlib.import_module("transformers")
            model_class = transformers.AutoModel
        self.model_class = model_class
        self.load_kwargs = load_kwargs  # 用于加载模型的额外参数

    def serialize(self, writer: ModelStateWriter, obj):
        # 序列化方法，将模型保存到指定目录
        model_dir = writer.mkdir(self.DIR_NAME)
        obj.save_pretrained(model_dir)

    def deserialize(self, reader: ModelStateReader):
        # 反序列化方法，从指定目录加载模型
        model_dir = reader.dir(self.DIR_NAME)
        return self.model_class.from_pretrained(model_dir, **self.load_kwargs)
```

### palantir_models_serializers.HfAutoTokenizerSerializer

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
class HfAutoTokenizerSerializer(ModelSerializer):
    """
    Serializer for huggingface transformers AutoTokenizer.
    用于huggingface transformers的AutoTokenizer的序列化器。
    """

    DIR_NAME = "tokenizer"  # 定义保存tokenizer的目录名称

    def __init__(self, tokenizer_class=None, **load_kwargs):
        # 初始化方法，如果没有提供tokenizer_class，默认使用AutoTokenizer
        if tokenizer_class is None:
            transformers = importlib.import_module("transformers")
            tokenizer_class = transformers.AutoTokenizer
        self.tokenizer_class = tokenizer_class
        self.load_kwargs = load_kwargs  # 额外的加载参数

    def serialize(self, writer: ModelStateWriter, obj):
        # 序列化方法，将tokenizer保存到指定目录
        tokenizer_dir = writer.mkdir(self.DIR_NAME)
        obj.save_pretrained(tokenizer_dir)

    def deserialize(self, reader: ModelStateReader):
        # 反序列化方法，从指定目录加载tokenizer
        tokenizer_dir = reader.dir(self.DIR_NAME)
        return self.tokenizer_class.from_pretrained(tokenizer_dir, **self.load_kwargs)
```

### palantir_models_serializers.HfPipelineSerializer

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
import importlib
from palantir_models import ModelSerializer, ModelStateReader, ModelStateWriter


class HfPipelineSerializer(ModelSerializer):
    """
    Serializer for huggingface transformers pipelines.
    Allows setting the pipeline task (e.g. sentiment-analysis).
    序列化器用于huggingface transformers的管道。
    允许设置管道任务（例如情感分析）。
    """

    DIR_NAME = "pipeline"

    def __init__(self, pipeline_type, **load_kwargs):
        # 动态导入transformers模块
        self.transformers = importlib.import_module("transformers")
        self.pipeline_type = pipeline_type
        self.load_kwargs = load_kwargs

    def serialize(self, writer: ModelStateWriter, obj):
        # 创建目录用于保存模型
        pipeline_dir = writer.mkdir(self.DIR_NAME)
        # 使用huggingface的save_pretrained方法保存模型
        obj.save_pretrained(pipeline_dir)

    def deserialize(self, reader: ModelStateReader):
        # 读取保存的模型目录
        pipeline_dir = reader.dir(self.DIR_NAME)
        # 使用huggingface的pipeline方法加载模型
        return self.transformers.pipeline(self.pipeline_type, model=pipeline_dir, **self.load_kwargs)
```

### palantir_models_serializers.JsonSerializer

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
import importlib
from types import ModuleType
from typing import Dict
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader

# 定义一个用于JSON序列化的类
class JsonSerializer(ModelSerializer[Dict]):
    """用于JSON可转换对象和字典的序列化器"""

    file_name = "config.json"
    json: ModuleType

    def __init__(self):
        # 动态导入json模块
        self.json = importlib.import_module("json")

    def serialize(self, writer: ModelStateWriter, obj: Dict):
        # 使用ModelStateWriter打开文件进行写操作，并将字典对象序列化为JSON格式写入文件
        with writer.open(self.file_name, "w") as conf:
            self.json.dump(obj, conf)

    def deserialize(self, reader: ModelStateReader) -> Dict:
        # 使用ModelStateReader打开文件进行读操作，并将JSON格式数据反序列化为字典对象
        with reader.open(self.file_name, "r") as conf:
            return self.json.load(conf)
```

In this code,JsonSerializeris a class that provides serialization and deserialization of JSON-convertible objects and dictionaries. It utilizes the Pythonjsonmodule to read and write data to a file namedconfig.json. The class dynamically imports thejsonmodule and usesModelStateWriterandModelStateReaderfor file operations.

### palantir_models_serializers.PytorchStateSerializer

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
import importlib
from types import ModuleType
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader


class PytorchStateSerializer(ModelSerializer):
    """Serializer for PyTorch state dictionaries."""
    # 用于序列化 PyTorch 状态字典的序列化器

    STATE_DICT_FILE_NAME = "model_state_dict.pt"
    torch: ModuleType

    def __init__(self):
        # 动态导入 torch 模块
        self.torch = importlib.import_module("torch")

    def serialize(self, writer: ModelStateWriter, obj: dict):
        """Serializes the state_dict of a PyTorch model."""
        # 序列化 PyTorch 模型的 state_dict
        with writer.open(self.STATE_DICT_FILE_NAME, "wb") as file_path:
            self.torch.save(obj, file_path)

    def deserialize(self, reader: ModelStateReader) -> dict:
        """Deserializes the state_dict of a PyTorch model."""
        # 反序列化 PyTorch 模型的 state_dict
        with reader.open(self.STATE_DICT_FILE_NAME, "rb") as file_path:
            state_dict = self.torch.load(file_path)
            return state_dict
```

### palantir_models_serializers.TensorflowKerasSerializer

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
import importlib
from types import ModuleType
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader


class TensorflowKerasSerializer(ModelSerializer):
    """Serializer for tensorflow keras models"""
    # TensorFlow Keras模型的序列化器

    DIR_NAME: str = "tensorflow_saved_model_dir"  # 保存模型的目录名称
    tensorflow: ModuleType  # 用于存储TensorFlow模块

    def __init__(self):
        self.tensorflow = importlib.import_module("tensorflow")  # 动态导入TensorFlow模块

    def serialize(self, writer: ModelStateWriter, obj: "tensorflow.keras.Model"):
        # 序列化方法，用于保存Keras模型
        dir_path = writer.mkdir(self.DIR_NAME)  # 创建目录
        obj.save(dir_path)  # 保存模型到指定目录

    def deserialize(self, reader: ModelStateReader) -> "tensorflow.keras.Model":
        # 反序列化方法，用于加载Keras模型
        dir_path = reader.dir(self.DIR_NAME)  # 获取保存模型的目录路径
        obj = self.tensorflow.keras.models.load_model(dir_path, compile=False)  # 加载模型，不编译
        obj.compile()  # 编译模型
        return obj  # 返回加载的模型
```

### palantir_models_serializers.XGBoostSerializer

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
from palantir_models import ModelSerializer
from palantir_models.models._serialization import ModelStateReader, ModelStateWriter
from xgboost.sklearn import XGBModel


class XGBoostSerializer(ModelSerializer[XGBModel]):
    """Simple Serializer for XGBoost SkLearn Models."""
    # XGBoost SkLearn模型的简单序列化器

    file_name = "xgboost_model.json"  # 模型文件名

    def serialize(self, writer: ModelStateWriter, obj: XGBModel):
        # 序列化方法，将XGBModel对象保存为文件
        with writer.open(self.file_name, "w") as xgbfile:
            obj.save_model(xgbfile.name)  # 保存模型到指定文件名

    def deserialize(self, reader: ModelStateReader) -> XGBModel:
        # 反序列化方法，从文件中加载XGBModel对象
        model = XGBModel()  # 创建一个新的XGBModel对象
        with reader.open(self.file_name, "r") as xgbfile:
            model.load_model(xgbfile.name)  # 从指定文件名加载模型
            return model  # 返回加载后的模型
```

### palantir_models_serializers.YamlSerializer

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
import importlib
from types import ModuleType
from typing import Dict
from palantir_models.models._serialization import ModelSerializer
from palantir_models.models._state_accessors import ModelStateWriter, ModelStateReader


class YamlSerializer(ModelSerializer[Dict]):
    """用于将可以转换为 YAML 的对象和字典进行序列化的类"""

    file_name = "config.yaml"
    yaml: ModuleType

    def __init__(self):
        # 动态导入 yaml 模块
        self.yaml = importlib.import_module("yaml")

    def serialize(self, writer: ModelStateWriter, obj: Dict):
        # 使用 ModelStateWriter 将字典对象序列化到 YAML 文件
        with writer.open(self.file_name, "w") as conf:
            self.yaml.safe_dump(obj, conf)

    def deserialize(self, reader: ModelStateReader) -> Dict:
        # 使用 ModelStateReader 从 YAML 文件反序列化为字典对象
        with reader.open(self.file_name, "r") as conf:
            return self.yaml.safe_load(conf)
```

这段代码定义了一个YamlSerializer类，用于将字典对象序列化为 YAML 格式并保存到文件，以及从文件中反序列化为字典对象。importlib模块用于动态导入yaml库，确保在需要时才加载该模块。
