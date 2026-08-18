来源: https://palantir.com/docs/zh/foundry/integrate-models/serialization/

# 模型的序列化

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 模型的序列化

为了在工作流中重用模型，Palantir 需要能够反序列化存储的权重。由于序列化过程可能对模型类型是特定的，因此模型适配器的作者需要详细说明这一过程。请注意，这不涉及容器模型，序列化通常是容器生命周期的一部分，或者外部模型，这些模型的权重是外部托管的。

## 自动序列化

为了简化平台内模型权重的序列化和反序列化，Palantir 提供了一个palantir_models_serializers库，该库提供了许多用于保存和加载模型的默认序列化方法：

- Dill
- Cloudpickle
- JSON
- YAML
- Hugging Face
- PyTorch
- Tensorflow
- XGBoost
### 如何使用默认序列化器

可以通过在模型适配器的__init__方法上使用@auto_serialize注解来使用默认序列化器。Palantir 将自动使用您选择的序列化方法保存和加载模型适配器内容。您可以对多个参数使用auto_serialize，每个参数使用不同的序列化器。您的__init__方法中的每个参数在您的@auto_serialize定义中必须有一个等效的参数。

请注意，为了避免可能的冲突，palantir_models_serializers包不包含对以下序列化框架的依赖。除了palantir_models_serializers之外，您仍需添加对相关序列化包的依赖。

### 使用auto_serialization的模型定义示例

下面是一个有效的Python 变换，它训练并发布模型。AutoSerializationAdapter使用DillSerializer来序列化模型。

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
from transforms.api import transform
from palantir_models.transforms import ModelOutput

from sklearn.linear_model import LinearRegression
import numpy as np


@transform(
    model_output=ModelOutput("/Foundry/path/to/model_asset"),
)
def compute(model_output):
    # 创建训练数据
    x_values = [i for i in range(100)]  # 自变量
    y_values = [2 * i for i in x_values]  # 因变量

    # 将列表转换为NumPy数组并重新调整形状
    X = np.array(x_values, dtype=np.float32).reshape(-1, 1)  # 自变量矩阵
    y = np.array(y_values, dtype=np.float32).reshape(-1, 1)  # 因变量矩阵

    # 创建线性回归模型
    model = LinearRegression()
    # 拟合模型
    model.fit(X, y)

    # 发布模型输出
    model_output.publish(
        model_adapter=AutoSerializationAdapter(
            model,
            {'prediction_column': 'prediction'}  # 预测列名
        )
    )

import palantir_models as pm
from palantir_models_serializers import DillSerializer

class AutoSerializationAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        model=DillSerializer()  # 使用Dill序列化器自动序列化模型
    )
    def __init__(self, model):
        self.model = model

    @classmethod
    def api(cls):
        inputs = {"df_in": pm.Pandas()}  # 输入为Pandas DataFrame
        outputs = {"df_out": pm.Pandas()}  # 输出为Pandas DataFrame
        return inputs, outputs

    def predict(self, df_in):
        # 使用模型进行预测，并将结果存储在'df_in'的'prediction'列中
        df_in['prediction'] = self.model.predict(df_in)
        return df_in
```

### 使用多个auto_serialization的示例模型定义

上述模型适配器可以扩展为包含一个使用默认JsonSerializer序列化的非必填配置字典。

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
import palantir_models as pm
from palantir_models_serializers import DillSerializer, JsonSerializer

# 定义一个自动序列化适配器类，用于模型的序列化和反序列化
class AutoSerializationAdapter(pm.ModelAdapter):

    # 使用自动序列化装饰器，指定模型使用DillSerializer进行序列化，配置使用JsonSerializer进行序列化
    @pm.auto_serialize(
        model=DillSerializer(),
        config=JsonSerializer()
    )
    def __init__(self, model, config={}):
        # 初始化模型和配置，默认预测列名为'prediction'
        self.model = model
        self.prediction_column = config['prediction_column'] if 'prediction_column' in config else 'prediction'

    # 定义类方法，用于API接口的输入输出格式
    @classmethod
    def api(cls):
        inputs = {"df_in": pm.Pandas()}  # 输入格式为Pandas DataFrame
        outputs = {"df_out": pm.Pandas()}  # 输出格式为Pandas DataFrame
        return inputs, outputs

    # 定义预测方法，接收输入的DataFrame，并在其中添加预测结果列
    def predict(self, df_in):
        # 预测结果存储在指定的预测列中
        df_in[self.prediction_column] = self.model.predict(df_in)
        return df_in
```

## 默认序列化器

### Dill

palantir_models_serializers.DillSerializer将通过调用dill.dump和dill.load使用dill ↗序列化和反序列化Python对象，以保存和加载对象到磁盘。

DillSerializer类可以用于序列化许多Python对象，包括scikit-learn和statsmodels。

### Cloudpickle

palantir_models_serializers.CloudPickleSerializer将通过调用cloudpickle.dump和cloudpickle.load使用Cloudpickle ↗序列化和反序列化Python对象，以保存和加载对象到磁盘。

CloudPickleSerializer类可以用于序列化许多Python对象，包括scikit-learn和statsmodels。

### JSON

palantir_models_serializers.JsonSerializer将通过调用yaml.safe_dump和json.safe_load序列化Python字典为JSON。

### YAML

palantir_models_serializers.YamlSerializer将通过调用yaml.safe_dump和yaml.safe_load使用JSON序列化Python字典。

### Hugging Face

palantir_models_serializers库目前为Hugging Face 模型 ↗提供三个默认序列化器：HfPipelineSerializer、HfAutoTokenizerSerializer和HfAutoModelSerializer。所有三个 Hugging Face 序列化器都要求在您的Python环境中添加transformers库作为依赖项。

#### HfPipelineSerializer

palantir_models_serializers.HfPipelineSerializer将使用save_pretrained序列化一个transformers.pipeline↗对象，并在加载时重新实例化您的pipeline对象。

HfPipelineSerializer有一个必填的字符串参数，代表pipeline的任务 ↗。任何附加的kwargs将被用于加载pipeline。

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
import palantir_models as pm
from palantir_models_serializers import HfPipelineSerializer
from transformers import pipeline
import pandas as pd

class HFNerAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        pipeline=HfPipelineSerializer("ner"),
    )
    def __init__(self, pipeline):
        # 初始化函数，接受一个NER管道对象
        self.pipeline = pipeline

    @classmethod
    def api(cls):
        # 定义模型输入和输出的接口
        inputs = {"df_in" : pm.Pandas([("text", str)])}  # 输入为DataFrame，包含"text"列
        outputs = {"df_out" : pm.Pandas([("text", str), ("generation", str)])}  # 输出为DataFrame，包含"text"和"generation"列
        return inputs, outputs

    def predict(self, df_in: pd.DataFrame):
        # 预测函数，接受一个DataFrame作为输入
        result = self.pipeline(df_in["text"].tolist())  # 使用NER管道对输入文本进行命名实体识别
        df_in["generation"] = result  # 将识别结果添加到DataFrame的新列"generation"中
        return df_in  # 返回带有识别结果的DataFrame
```

#### HfAutoModelSerializer 和 HfAutoTokenizerSerializer

palantir_models_serializers.HfAutoModelSerializer和palantir_models_serializers.HfAutoTokenizerSerializer将使用save_pretrained和from_pretrained序列化transformers.AutoModel和transformers.AutoTokenizer模型。

注意，对于某些模型和词元器，建议使用特定的模型或词元器类而不是通用的类；在这些情况下，可以将特定类作为第一个model_class参数传递给序列化器。

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
import palantir_models as pm
from palantir_models_serializers import HfAutoModelSerializer, HfAutoTokenizerSerializer
from transformers import AutoModelForSeq2SeqLM
import pandas as pd
import torch

# 定义一个文本生成适配器类，继承自 pm.ModelAdapter
class HFTextGenerationAdapter(pm.ModelAdapter):

    # 使用装饰器进行自动序列化，指定模型和分词器序列化器
    @pm.auto_serialize(
        model=HfAutoModelSerializer(AutoModelForSeq2SeqLM),
        tokenizer=HfAutoTokenizerSerializer()
    )
    def __init__(self, model, tokenizer):
        self.model = model  # 初始化模型
        self.tokenizer = tokenizer  # 初始化分词器

    # 定义一个类方法，描述输入输出的数据格式
    @classmethod
    def api(cls):
        inputs = {"df_in" : pm.Pandas([("text", str)])}  # 输入数据格式为Pandas DataFrame，包含"text"列
        outputs = {"df_out" : pm.Pandas([("text", str), ("generation", str)])}  # 输出数据格式为Pandas DataFrame，包含"text"和"generation"列
        return inputs, outputs

    # 定义预测方法，进行文本生成
    def predict(self, df_in: pd.DataFrame):
        # 使用分词器将输入文本列表转换为输入ID，并进行填充
        input_ids = self.tokenizer(
            df_in["text"].tolist(),
            return_tensors="pt",  # 返回PyTorch张量
            padding=True  # 启用填充
        ).input_ids

        # 使用模型生成输出
        outputs = self.model.generate(input_ids)
        # 解码生成的输出为文本
        result = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # 将生成的文本加入输入DataFrame中
        df_in["generation"] = result
        return df_in  # 返回更新后的DataFrame
```

### PyTorch

palantir_models_serializers.PytorchStateSerializer将使用torch.save和torch.load序列化和反序列化torch.nn.Module↗，以将您的对象保存到磁盘并从磁盘加载。

### TensorFlow

palantir_models_serializers.TensorflowKerasSerializer将使用obj.save和tensorflow.keras.models.load_model序列化和反序列化tensorflow.keras.Model↗，以将您的模型保存到磁盘并从磁盘加载。当您的模型被反序列化时，Foundry 将调用obj.compile()。

### XGBoost

palantir_models_serializers.XGBoostSerializer将使用save_model和load_model序列化和反序列化xgboost.sklearn.XGBModel↗，以将您的模型保存到磁盘并从磁盘加载。XGBModel类是许多 XGBoost 模型的基类，包括xgboost.XGBClassifier、xgboost.XGBRegressor和xgboost.XGBRanker。

### 编写您自己的 AutoSerializer

请参阅每个序列化器的完整实现和有关如何添加新的默认序列化器的文档。

如果您认为应该有一个未列出的默认序列化器，请联系您的 Palantir 代表。

## 自定义序列化

在默认序列化器不足的情况下，用户可以实现load()和save()方法。有关更多详细信息和示例，请参阅API 参考。
