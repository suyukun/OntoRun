来源: https://palantir.com/docs/zh/foundry/integrate-models/model-asset-code-repositories-sklearn/

# 在代码库中使用 scikit-learn 训练二元分类模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在代码库中使用 scikit-learn 训练二元分类模型

以下文档提供了一个示例，展示如何在代码库应用程序中使用模型训练模板，利用开源的UCI ML乳腺癌威斯康星（诊断）↗数据集训练scikit-learn二元分类模型。

有关以下步骤的详细演练，包括如何编写模型适配器和编写Python变换以进行模型训练，请参阅我们的文档：如何在代码库中训练模型。

## 1. 编写模型适配器

首先，使用代码库中的模型训练模板编写一个模型适配器。

以下示例逻辑假定以下情况：

- 此模型适配器使用scikit-learnmodel初始化。
- 提供给此模型的数据是表格形式。
- 此模型的输出是表格形式，包含来自columns、prediction、probability_0和probability_1的所有列，其中，prediction为0或1，0表示未检测到癌症，1表示检测到癌症。probability_0是未检测到癌症的概率。probability_1是检测到癌症的概率。
- prediction为0或1，0表示未检测到癌症，1表示检测到癌症。
- probability_0是未检测到癌症的概率。
- probability_1是检测到癌症的概率。
- 已将以下依赖项添加到存储库中：python 3.8.18、pandas 1.5.3、scikit-learn 1.3.2和dill 0.3.7。
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
import palantir_models as pm
from palantir_models_serializers import *

# 定义SklearnClassificationAdapter类，继承自pm.ModelAdapter
class SklearnClassificationAdapter(pm.ModelAdapter):

    @pm.auto_serialize(
        model=DillSerializer()  # 使用DillSerializer进行模型序列化
    )
    def __init__(self, model):
        self.model = model  # 初始化时传入一个模型实例

    @classmethod
    def api(cls):
        # 定义输入数据的列名
        columns = [
            'mean_radius', 'mean_texture', 'mean_perimeter', 'mean_area',
            'mean_smoothness', 'mean_compactness', 'mean_concavity',
            'mean_concave_points', 'mean_symmetry', 'mean_fractal_dimension',
            'radius_error', 'texture_error', 'perimeter_error', 'area_error',
            'smoothness_error', 'compactness_error', 'concavity_error',
            'concave_points_error', 'symmetry_error', 'fractal_dimension_error',
            'worst_radius', 'worst_texture', 'worst_perimeter', 'worst_area',
            'worst_smoothness', 'worst_compactness', 'worst_concavity',
            'worst_concave_points', 'worst_symmetry', 'worst_fractal_dimension'
        ]

        # 定义输入输出格式
        inputs = {"df_in": pm.Pandas(columns=columns)}
        outputs = {"df_out": pm.Pandas(columns= columns + [
                                            ("prediction", int),  # 添加预测结果列
                                            ("probability_0", float),  # 添加类别0的概率列
                                            ("probability_1", float)  # 添加类别1的概率列
                                        ])}
        return inputs, outputs  # 返回输入输出格式

    def predict(self, df_in):
        X = df_in.copy()  # 复制输入数据

        predictions = self.model.predict(X)  # 使用模型进行预测
        probabilities = self.model.predict_proba(X)  # 获取预测的概率

        df_in['prediction'] = predictions  # 将预测结果添加到输入数据中
        for idx, label in enumerate(self.model.classes_):
            df_in[f"probability_{label}"] = probabilities[:, idx]  # 将概率添加到输入数据中

        return df_in  # 返回包含预测结果和概率的DataFrame
```

## 2. 编写一个Python变换以训练模型

在同一仓库中的model_training/model_training.py中编写模型训练逻辑。

此示例使用scikit-learn库中提供的开源UCI ML乳腺癌威斯康星（诊断）数据集 ↗。

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
from transforms.api import transform
from palantir_models.transforms import ModelOutput
from main.model_adapters.adapter import SklearnClassificationAdapter
from sklearn.datasets import load_breast_cancer
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 使用 transform 装饰器定义模型输出路径
@transform(
    model_output=ModelOutput("/path/to/model_asset"),
)
def compute(model_output):
    # 加载乳腺癌数据集，返回 DataFrame 格式的特征和标签
    X_train, y_train = load_breast_cancer(as_frame=True, return_X_y=True)
    # 将特征列名中的空格替换为下划线
    X_train.columns = X_train.columns.str.replace(' ', '_')
    columns = X_train.columns

    # 定义数值特征的预处理流水线：缺失值填补和标准化
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),  # 使用中位数填补缺失值
            ("scaler", StandardScaler())  # 标准化数据
        ]
    )

    # 创建列变换器，将数值预处理应用于所有列，其他列不变
    preprocessor = make_column_transformer(
        (numeric_transformer, columns),
        remainder="passthrough"
    )

    # 定义模型流水线，包括预处理和随机森林分类器
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=50, max_depth=3))  # 设置随机森林参数
        ]
    )
    # 用训练数据拟合模型
    model.fit(X_train, y_train)

    # 创建模型适配器并发布模型
    foundry_model = SklearnClassificationAdapter(model)
    model_output.publish(model_adapter=foundry_model)
```

## 3. 使用模型

### 在Python变换中运行推理

您可以在Python变换中运行模型推理。例如，一旦模型训练完成，将下面的推理逻辑复制到model_training/run_inference.py文件中，并选择搭建。

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
from transforms.api import transform, Output
from palantir_models.transforms import ModelInput
from sklearn.datasets import load_breast_cancer

# 装饰器定义一个转换函数，指定输出数据集和模型输入
@transform(
    inference_output=Output("ri.foundry.main.dataset.5dd9907f-79bc-4ae9-a106-1fa87ff021c3"),
    model=ModelInput("ri.models.main.model.cfc11519-28be-4f3e-9176-9afe91ecf3e1"),
)
def compute(inference_output, model):
    # 加载乳腺癌数据集，返回数据帧格式
    X, y = load_breast_cancer(as_frame=True, return_X_y=True)
    # 将特征列名中的空格替换为下划线
    X.columns = X.columns.str.replace(' ', '_')

    # 使用模型进行推理，得到推理结果
    inference_results = model.transform(X)
    # 将推理结果写入指定输出数据集
    inference_output.write_pandas(inference_results.df_out)
```

### 在建模目标中执行实时推理

Palantir模型可以提交到建模目标，以实现以下功能：

- 自动模型评估
- 批处理管道
- 实时托管
在将此模型提交到建模目标后，您可以启动沙箱部署以托管此模型进行实时推理。一旦沙箱启动并准备就绪，您就可以执行实时推理并将此模型连接到运营应用程序。

下面的示例显示了使用单一I/O端点的二分类模型输入：

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
[
  {
    "mean_radius": 15.09, // 平均半径
    "mean_texture": 23.71, // 平均纹理
    "mean_perimeter": 92.65, // 平均周长
    "mean_area": 944.07, // 平均面积
    "mean_smoothness": 0.53, // 平均平滑度
    "mean_compactness": 0.21, // 平均紧密度
    "mean_concavity": 0.76, // 平均凹陷度
    "mean_concave_points": 0.39, // 平均凹点数
    "mean_symmetry": 0.08, // 平均对称性
    "mean_fractal_dimension": 0.14, // 平均分形维数
    "radius_error": 0.49, // 半径误差
    "texture_error": 0.82, // 纹理误差
    "perimeter_error": 2.51, // 周长误差
    "area_error": 17.22, // 面积误差
    "smoothness_error": 0.07, // 平滑度误差
    "compactness_error": 0.01, // 紧密度误差
    "concavity_error": 0.05, // 凹陷度误差
    "concave_points_error": 0.05, // 凹点数误差
    "symmetry_error": 0.01, // 对称性误差
    "fractal_dimension_error": 0.08, // 分形维数误差
    "worst_radius": 12.95, // 最差半径
    "worst_texture": 20.66, // 最差纹理
    "worst_perimeter": 185.41, // 最差周长
    "worst_area": 624.87, // 最差面积
    "worst_smoothness": 0.18, // 最差平滑度
    "worst_compactness": 0.26, // 最差紧密度
    "worst_concavity": 0.01, // 最差凹陷度
    "worst_concave_points": 0.05, // 最差凹点数
    "worst_symmetry": 0.29, // 最差对称性
    "worst_fractal_dimension": 0.05 // 最差分形维数
  }
]
```
