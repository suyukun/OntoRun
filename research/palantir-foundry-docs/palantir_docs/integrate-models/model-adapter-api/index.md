来源: https://palantir.com/docs/zh/foundry/integrate-models/model-adapter-api/

# 模型适配器 API

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 模型适配器 API

模型适配器的api()方法指定了执行该模型适配器的推理逻辑所需的输入和输出。输入和输出是分别指定的。

在运行时，会使用指定的输入调用模型适配器的predict()方法。

## 示例api()实现

以下示例显示了一个 API，指定了一个名为input_dataframe的输入和一个名为output_dataframe的输出。输入和输出对象都被指定为 Pandas 数据框，其中输入数据框有一个名为input_feature的float类型的列，输出数据框有两列：(1) 一个名为input_feature的float类型的列和 (2) 一个名为output_feature的int类型的列。

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
import palantir_models as pm


class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义输入数据结构，使用Pandas DataFrame，其中包含一个名为 "input_feature" 的浮点型列
        inputs = {
            "input_dataframe": pm.Pandas(columns=[("input_feature", float)])
        }
        # 定义输出数据结构，使用Pandas DataFrame，其中包含两个浮点型列："input_feature" 和 "prediction"
        outputs = {
            "output_dataframe": pm.Pandas(columns=[("input_feature", float), ("prediction", float)])
        }
        # 返回输入和输出的数据结构
        return inputs, outputs

    ...
```

API定义也可以扩展以支持任意类型的多个输入或输出：

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
import palantir_models as pm


class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义输入数据，包含一个数据帧和一个参数
        inputs = {
            "input_dataframe": pm.Pandas(columns=[("input_feature", float)]),  # 输入数据帧，包含一列名为 "input_feature" 的浮点型数据
            "input_parameter": pm.Parameter(float, default=1.0)  # 输入参数，默认为 1.0 的浮点数
        }
        # 定义输出数据，包含一个数据帧
        outputs = {
            "output_dataframe": pm.Pandas(columns=[("input_feature", float), ("prediction", float)])  # 输出数据帧，包含 "input_feature" 和 "prediction" 两列浮点型数据
        }
        return inputs, outputs

    ...
```

直接在模型目标应用程序中设置批量部署和自动模型评估仅兼容具有单个表格数据集输入的模型。如果您的模型适配器需要多个输入，可以在Python变换中设置批量推理。

## API类型

模型适配器API的输入和输出类型可以通过以下类指定，具体定义如下：

- pm.Pandas，用于Pandas数据框
- pm.Spark，用于Spark数据框
- pm.Parameter，用于常量、单值参数
- pm.FileSystem，用于Foundry数据集文件系统访问
- pm.MediaReference，用于媒体引用
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
# 以下类可以通过 `palantir_models` 或 `pm` 进行访问

class Pandas:
    def __init__(self, columns: List[Union[str, Tuple[str, type]]]):
        """
        定义一个 Pandas Dataframe 的输入或输出。
        可以通过参数指定列名和类型定义。
        """

class Spark:
    def __init__(self, columns: List[Union[str, Tuple[str, type]]] = []):
        """
        定义一个 Spark Dataframe (pyspark.sql.Dataframe) 的输入或输出。
        可以通过参数指定列名和类型定义。
        """

class Parameter:
    def __init__(self, type: type = Any, default = None):
        """
        定义一个常量单值的参数输入或输出。
        可以通过参数指定此参数的类型（默认为 Any）和默认值。
        """

class FileSystem:
    def __init__(self):
        """
        定义一个 FileSystem 访问输入或输出对象。
        仅在模型适配器的 `transform()` 或 `transform_write()` 方法与 Foundry Dataset 对象一起调用时可用。

        如果用作输入，返回数据集的 FileSystem 表示形式。

        如果用作输出，使用一个包含 `open()` 方法的对象将文件写入输出数据集。

        注意，FileSystem 输出只能通过调用 `.transform_write()` 使用。
        """

class MediaReference:
    def __init__(self):
        """
        定义一个 MediaReference 类型的输入对象。
        此输入期望为媒体引用对象的字符串化 JSON 表示或字典表示。

        此类型不支持作为 API 输出。
        """
```

在此代码中，我们定义了一些类用于处理数据输入和输出的不同类型。这些类包括 Pandas 和 Spark DataFrame 的输入输出定义、参数定义、文件系统访问对象以及媒体引用对象。每个类都具有特定的用途和用法，具体可以通过文档字符串了解。

## 指定表格列

对于Pandas或Spark输入和输出，可以将列指定为字符串列表来指定列名，或者为格式为(<name>, <type>)的两对象tuple列表，其中<name>是表示列名的字符串，<type>是表示列中数据类型的 Python 类型。如果为列定义提供了字符串，则其类型将默认为Any。

### 列类型

以下类型支持用于表格列：

- str
- int
- float
- bool
- list
- dict
- set
- tuple
- typing.Any
- MediaReference
列类型不被强制执行，而是作为向此模型适配器的消费者传达预期列类型的一种方式。唯一的例外是MediaReference类型，它期望列中的每个元素都是媒体引用字符串，并将在传递给此模型适配器的推理逻辑之前将每个元素转换为MediaReferenceObject。

## 参数类型

对于Parameter输入和输出，支持以下类型：

- str
- int
- float
- bool
- list
- dict
- set
- tuple
- typing.Any
参数类型是强制执行的，任何输入到model.transform()的参数如果不符合指定类型将抛出运行时出错。

## 示例predict()实现

此示例与上面定义的api()示例兼容。它使用 Pandas 数据框作为输入和输出，并带有一个参数。

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
class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        # 定义模型所需的输入和输出
        inputs = {
            # 输入数据框，包含名为 "input_feature" 的浮点型列
            "input_dataframe": pm.Pandas(columns=[("input_feature", float)]),
            # 输入参数，默认为 1.0 的浮点型参数
            "input_parameter": pm.Parameter(float, default=1.0)
        }
        outputs = {
            # 输出数据框，包含名为 "input_feature" 和 "prediction" 的浮点型列
            "output_dataframe": pm.Pandas(columns=[("input_feature", float), ("prediction", float)])
        }
        return inputs, outputs

    def predict(self, input_dataframe, input_parameter):
        # 使用模型进行预测，并根据输入参数进行调整
        outputs["prediction"] = self.model.predict(input_dataframe) * input_parameter
        return outputs
    ...
```

- 在api方法中，我们定义了模型的输入和输出格式，其中input_dataframe是一个包含特征列的 Pandas 数据框，input_parameter是一个可选的浮点参数。
- 在predict方法中，通过调用模型的predict方法进行预测，并将结果乘以input_parameter参数，以得到最终的预测结果。
- 在一个数据框中，传递给其构造函数的列列表仅包含所需的列。在运行时，可以在输入和输出数据框中包含额外的列。示例实现保留输入数据框，并在输出中添加预测列，从而有效地保留所有额外的列。
- 在评估期间，输出应始终包含模型预测和标签。在我们的示例中，确保标签列不会在方法中被删除。
- 一些模型要求仅将训练过程中使用的列传递给其预测方法。因此，我们建议仅提取特征列传递给模型。
- 一些模型要求保留列的顺序。当通过REST API请求以JSON对象形式传递输入时，列的顺序不一定被保留。因此，我们建议在传递给模型的推断方法之前重新排序列。