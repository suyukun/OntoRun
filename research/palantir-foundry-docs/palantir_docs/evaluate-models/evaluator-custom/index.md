来源: https://palantir.com/docs/zh/foundry/evaluate-models/evaluator-custom/

# 自定义评估库

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 自定义评估库

评估库是在 Foundry 中发布的 Python 包，用于生成模型评估器。评估库被用于以可重用的方式衡量模型性能、公平性、稳健性及其他指标，适用于不同的建模目标。

除了 Foundry 默认的二元分类和回归模型评估器外，Foundry 还允许您创建可在建模目标中原生使用的自定义模型评估器。

## 建模目标中的自定义评估器

自定义评估器、其配置选项和生成的指标将以在评估器实现顶部的文档字符串中指定的名称和描述显示在建模目标应用程序中。

一旦自定义评估器发布，它将在建模目标应用程序中对任何具有查看已发布库权限的用户可用。这使您能够为整个组织编写可重用的逻辑，以计算标准化指标。

自定义评估器可在建模目标的评估库配置中选择；该库可以根据评估器定义的参数进行配置。

## 创建自定义评估器

要创建自定义评估器：

- 从Model Evaluator Template Library创建代码库。
- 实现您的自定义评估器。
- 为您的自定义评估器添加参数。
- 提交并发布一个新标签以应用您的更改。
### 创建代码库

代码库应用程序有许多模板实现；在这里，我们将使用Model Evaluator Template Library。导航到一个 Foundry 项目，选择**+ 新建** >库类型>模型集成>语言模板，选择Model Evaluator Template Library，最后选择初始化库。

#### 评估器模板结构

Model Evaluator Template Library在文件src/evaluator/custom_evaluator.py中有一个示例实现。任何EvaluatorPython 接口的实现都将自动注册并在您发布其库的新版本时可用。

包含自定义评估器逻辑的库可以发布多个评估器。任何额外的评估器实现文件都需要作为引用添加到评估器模板的build.gradle中的模型评估器模块列表中。

## 实现自定义评估器

要实现自定义评估器，您需要创建Evaluator接口的实现，并可选择提供供建模目标应用程序解释的配置字段。

在评估器模板库中，将您的评估器添加到文件src/evaluator/custom_evaluator.py中。

### 评估器接口

评估器的接口定义如下：

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
class Evaluator():

    def apply_spark(self, df: DataFrame) -> List[ComputedMetricValue]:
        """
        应用评估器在 PySpark DataFrame 上计算指标。

        :param df: 要计算指标的 PySpark DataFrame
        :return: 计算出的指标值列表
        """

        pass
```

要在模型目标应用程序中使用新配置的自定义评估器，您首先需要发布其存储库的新版本，为其提供一个新的存储库版本标签。

### 评估器文档

自定义评估器及其配置选项和生成的指标将在模型目标应用程序中显示，其名称和描述在实现顶部的文档字符串中指定。

所需的值为：

- display-name: 评估器的显示名称
- description: 评估器的描述
您可以选择性地添加零个或多个以下内容：

- param: 自定义评估器的配置参数
- metric: 评估器生成的指标
### 示例评估器实现

这是一个示例评估器，用于计算输入数据集的行数。

此示例评估器将在模型目标应用程序中显示为：

- 标题为Row Count Evaluator。
- 描述为This evaluator calculates the row count of the input DataFrame.。
- 生成的指标Row Count，其描述为The row count。
- 零个配置参数。
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
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from foundry_ml_metrics.evaluation import ComputedMetricValue, Evaluator

class CustomEvaluator(Evaluator):
    """
        :display-name: Row Count Evaluator
        :description: This evaluator calculates the row count of the input DataFrame.
        :metric Row Count: The row count
        :display-name: 行数评估器
        :description: 该评估器计算输入DataFrame的行数。
        :metric 行数: 行数
    """

    def apply_spark(self, df: DataFrame) -> List[ComputedMetricValue]:
        row_count = df.count()  # 计算DataFrame的行数

        return [
            ComputedMetricValue(
                metric_name='Row Count',  # 指标名称为“行数”
                metric_value=row_count  # 指标值为计算得到的行数
            )
        ]
```

在上述代码中，我们定义了一个名为CustomEvaluator的自定义评估器类，继承自Evaluator。该评估器类的作用是计算输入DataFrame的行数，并返回一个包含行数的ComputedMetricValue列表。

### 参数化评估器

通过提供配置参数，可以在建模目标应用中使评估器可配置。
配置参数将在运行时由建模目标应用填充用户输入的值。
评估器的用户将在配置建模目标中的自动评估时有机会配置参数的值。

允许的配置字段为：

- int: 整数
- float: 浮点数
- bool: 布尔值（True 或 False）
- str: 字符串值
- Field[float]: 输入DataFrame中的浮点数列
- Field[int]: 输入DataFrame中的整数列
- Field[str]: 输入DataFrame中的字符串列
可以通过将参数包装在Optional（来自内置的typing包）中使其成为非必填。

例如：

- 一个非必填的str将是Optional[str]
- 一个非必填的Field[str]将是Optional[Field[str]]
### 带有配置字段的示例评估器

这是一个示例评估器，它计算输入数据集的行数以及当输入数据框被筛选使得输入列column等于value时的行数。

此示例评估器将在建模目标应用中显示为：

- 标题为Configurable Row Count Evaluator。
- 描述为此评估器计算输入DataFrame的行数，筛选到指定的值。
- 生成的指标Row Count，描述为未筛选的行数。
- 生成的指标Filtered Row Count，描述为筛选的行数。
- 两个配置参数：在评估数据集中的一列，必须是名称为column的整数，描述为筛选列。一个名称为value的整数值，描述为筛选值。
- 在评估数据集中的一列，必须是名称为column的整数，描述为筛选列。
- 一个名称为value的整数值，描述为筛选值。
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
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from foundry_ml_metrics.evaluation import ComputedMetricValue, Evaluator, Field

class CustomEvaluator(Evaluator):
    """
        :display-name: Configurable Row Count Evaluator
        :description: This evaluator calculates the row count of the input DataFrame, filtered to the specified value.

        :param column: Filtered column
        :param value: Filtered value

        :metric Row Count: The unfiltered row count
        :metric Filtered Row Count: The filtered row count
    """

    column: Field[int]
    value: int

    def __init__(self, column: Field[int], value: int):
        # 初始化函数，接受一个列名和一个过滤值
        self.column = column
        self.value = value

    def apply_spark(self, df: DataFrame) -> List[ComputedMetricValue]:
        # 从 Field 对象中获取列名
        column_name = self.column.name
        # 获取过滤值
        column_value = self.value

        # 计算总行数
        row_count = df.count()

        # 计算过滤后的行数
        filtered_row_count = df.filter(
            F.col(column_name) == column_value
        ).count()

        # 返回计算的指标值，包括总行数和过滤后的行数
        return [
            ComputedMetricValue(
                metric_name='Row Count',  # 总行数指标
                metric_value=row_count
            ),
            ComputedMetricValue(
                metric_name='Filtered Row Count',  # 过滤后行数指标
                metric_value=filtered_row_count
            )
        ]
```

这个代码定义了一个自定义的评估器类CustomEvaluator，用于计算输入 DataFrame 的行数以及根据指定值过滤后的行数。通过继承Evaluator类，提供了两个指标：总行数和过滤后的行数。

## 参考类

以下类作为参考提供。

### 字段

字段用作配置参数，以指示建模目标应用程序需要实现哪些属性。Field具有以下接口。

```
Copied!1
2
class Field():
    name: str  # 定义一个属性 name，用于存储字段名称的字符串
```

### ComputedMetricValue

ComputedMetricValue存储有关要附加到Foundry模型的指标信息。

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
class ComputedMetricValue():
    """
    由评估器计算的度量，包括度量名称、值和子集信息。
    """
    metric_name: str  # 度量名称
    metric_value: MetricValue  # 度量值

    def __init__(self, metric_name, metric_value):
        self.metric_name = metric_name
        self.metric_value = metric_value
```

### 指标值

指标值可以是以下任何一种：

- 数值类型，可以是以下类型之一：intnp.int8np.int16np.int32np.int64np.uint8np.uint16np.uint32np.uint64floatnp.float32np.float64
- int
- np.int8
- np.int16
- np.int32
- np.int64
- np.uint8
- np.uint16
- np.uint32
- np.uint64
- float
- np.float32
- np.float64
- 图形，可以是以下类型之一：matplotlib.Figurematplotlib.pyplot.Figure
- matplotlib.Figure
- matplotlib.pyplot.Figure
- 任何实现了以下其中一个方法的类：get_figure(self) -> Figure：注意许多seaborn图实现了此函数。save(self, path: str)：注意许多seaborn图实现了此函数。savefig(self, path: str)
- get_figure(self) -> Figure：注意许多seaborn图实现了此函数。
- save(self, path: str)：注意许多seaborn图实现了此函数。
- savefig(self, path: str)
- 柱状图
- 折线图