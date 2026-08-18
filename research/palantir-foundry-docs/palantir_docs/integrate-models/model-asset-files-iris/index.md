来源: https://palantir.com/docs/zh/foundry/integrate-models/model-asset-files-iris/

# 示例：上传 scikit-learn 模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：上传 scikit-learn 模型

以下文档提供了一个将模型从现有模型文件集成到 Foundry 的示例。有关分步指南，请参阅我们的文档，了解如何从预训练文件发布模型。

## 从模型文件创建模型

以下示例使用了一个使用加州大学尔湾分校发布的Iris 分类数据集 ↗在本地训练的模型。该数据集有四个特征：sepal_length、sepal_width、petal_length和petal_width，可用于搭建一个预测鸢尾花特定种类的模型。

在此示例中，我们假设模型在本地使用scikit-learn 库 ↗作为K-最近邻分类器 ↗进行训练。此示例还假设模型使用Python 3.8.0和scikit-learn 1.3.2进行训练。

训练后，模型被保存为如下所定义的pickle 文件 ↗。

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
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

import pickle

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data  # 特征数据
y = iris.target  # 标签数据

# 将数据集拆分为训练集和测试集，测试集占40%
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.4, random_state=4)

# 创建KNN分类器，设置邻居数为5
knn = KNeighborsClassifier(n_neighbors = 5)
# 用训练数据集拟合模型
knn.fit(X_train, y_train)

# 将训练好的模型保存到文件中
with open("iris_model.pkl", "wb") as f:
    pickle.dump(knn, f)
```

这个代码示例演示了如何使用KNeighborsClassifier对鸢尾花数据集进行分类，并将训练好的模型使用pickle保存到文件中，便于以后加载和使用。

### 1. 将模型文件上传到非结构化数据集

scikit-train模型文件被上传到Palantir作为非结构化数据集，如下图所示：

## 2. 创建一个模型训练模板以定义模型适配器逻辑

在代码库应用中，使用模型集成语言模板创建一个新的模型训练库，然后添加对scikit-learn 1.3.2的依赖。定义读取模型文件和发布模型的逻辑。

### 3. 将模型文件发布为模型

一旦模型适配器逻辑执行完毕，模型将在平台上发布。

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
from transforms.api import transform, Input
import palantir_models as pm
from palantir_models.transforms import ModelOutput
from palantir_models_serializers import DillSerializer
import pickle
import os

# 定义一个数据转换函数，输入为模型文件，输出为模型预测结果
@transform(
    model_files=Input("<Your Input Path>"),  # 输入路径
    model_output=ModelOutput("<Your Output path>")  # 输出路径
)
def compute(model_files, model_output):
    fs = model_files.filesystem()  # 获取文件系统对象
    with fs.open("iris_model.pkl", "rb") as f:
        model = pkl.load(f)  # 从文件中加载模型

    model_adapter = IrisModelAdapter(model, "target")  # 创建模型适配器
    model_output.publish(
        model_adapter=model_adapter  # 发布模型适配器
    )

# 定义一个适配器类，用于适配模型的输入输出
class IrisModelAdapter(pm.ModelAdapter):

    @auto_serialize(
        model=DillSerializer(),  # 使用DillSerializer序列化模型
        prediction_column_name=DillSerializer()  # 使用DillSerializer序列化预测列名
    )
    def __init__(self, model, prediction_column_name="target"):
        self.model = model  # 初始化模型
        self.prediction_column_name = prediction_column_name  # 初始化预测列名

    @classmethod
    def api(cls):
        # 定义输入输出的列名和数据类型
        column_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        columns = [(name, float) for name in column_names]
        inputs = {"df_in": pm.Pandas(columns=columns)}
        outputs = {"df_out": pm.Pandas(columns=columns + [("target", int)])}
        return inputs, outputs

    def predict(self, df_in):
        inference_data = df_in  # 输入数据

        predictions = self.model.predict(inference_data.values)  # 模型预测
        inference_data[self.prediction_column_name] = predictions  # 将预测结果赋予新列
        return inference_data  # 返回包含预测结果的数据
```

### 4. 消费已发布的模型

一旦模型发布后，就可以在平台上进行推理消费。对于这个示例，我们将创建一个新的建模目标并提交模型。

- 通过导航到您希望目标所在的项目文件夹，然后选择新建 > 建模目标来创建一个新的建模目标。这将打开建模目标应用程序。
- 接下来，将模型提交到目标。在模型提交 > 提交模型部分，选择添加模型以打开对话框，如下所示。
- 选择从 Foundry 提交模型，然后选择下一步以打开对话框，在该对话框中，您可以从平台中的位置加载已发布的模型。
- 一旦提交模型，您将被引导回到建模目标概览页面，其中的模型提交部分将显示有关提交的信息。
- 从模型提交部分选择新提交的模型以打开模型页面。
- 选择右上角的创建新版本以打开一个新窗口来创建版本。
- 创建版本后，通过选择屏幕左上角的名称返回建模目标概览页面。向下滚动到部署部分，然后选择创建部署以打开另一个对话框窗口。
- 完成设置表单，然后选择右下角的创建部署。返回建模目标概览，向下滚动到部署部分，然后选择新部署的模型进行测试。
- 从页面左上角的查询选项卡，添加值并观察输出结果以测试模型。
有关创建和查询实时部署的更多详细信息，请参阅实时部署文档。
