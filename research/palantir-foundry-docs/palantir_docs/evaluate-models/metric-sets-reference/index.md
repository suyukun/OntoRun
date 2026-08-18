来源: https://palantir.com/docs/zh/foundry/evaluate-models/metric-sets-reference/

# 指标集参考

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 指标集参考

一个指标集作为命名指标的容器，我们将其定义为模型输出的任何汇总。 支持的指标包括数值、图表和图像。

在 Python 中，指标集通过foundry_ml_metrics包中的MetricSet类实现（需要在环境配置中包含foundry_ml）。

所有指标都可以通过MetricSet.add方法添加，参数如下：

- name指标的字符串名称
- value你想添加的指标的值
- subset一个dict<str, str>描述此指标所针对的数据子集
- stage一个 Foundry ML 模型阶段或阶段 uuid，将其绑定到特定阶段，默认为最后一个模型阶段
下面是创建一个空指标集的示例，以说明这个概念。

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
import foundry_ml_metrics

def Metrics(Model, validation_hold_out):

    # 初始化 MetricSet 对象，传入模型和输入数据
    metric_set = foundry_ml_metrics.MetricSet(
        model = Model,
        input_data=validation_hold_out
    )

    val_df = validation_hold_out.dataframe()

    # 在数据集上运行模型以获取推断结果
    inference_results = Model.transform(val_df)

    # 计算指标
    y_true, y_pred = ...
    acc = ...
    f1 = ...

    # 将指标添加到 metric_set 中
    metric_set.add(name='Accuracy', value=acc)
    metric_set.add(name='F1 Score', value=f1)

    return metric_set
```

在创建时，您必须将model和input_data参数传递给MetricSet。

要保存一个 MetricSet，像保存模型一样返回它。上面的示例代表了从代码工作簿中保存的方法。

## 输入数据集

输入数据集是对模型应用的数据的特定版本的明确引用，然后在此基础上计算出指标。通过手动跟踪这些信息，您可以创建模型性能的记录和完整的来源。当在一个建模目标中评估多个模型时，此功能是必要的，以确保这些模型是在相同数据上进行评估。

输入数据集必须作为Python变换输入类型传递到MetricSets中，以获取适当的元数据。注意：代码工作簿仅支持导入的数据集。按照最佳实践，我们必须在一个独立于测试/训练拆分的工作簿中进行验证。

## 指标类型

### 数值指标

数值指标是最基本的指标类型，通常是分析师对模型性能的第一洞察。数值指标只是简单的 pythonint或float类型，并简单地添加到指标集中。

```
Copied!1
2
metric_set.add(name='My numeric metric', value=1.5)
# 向 metric_set 添加一个名为 'My numeric metric' 的数值型指标，其值为 1.5
```

### 图表指标

图表提供了模型性能的可视化表现，超越了简单的数值指标。foundry_ml提供了直接保存数据到各种格式图表的功能。由于数据被保存，这允许更优越的模型比较能力，特别是在建模目标中。

所有支持的图表都是通过foundry_ml_metrics.charts包中的函数创建的。

考虑一个例子：

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
import foundry_ml_metrics.charts

# 创建一条折线图，x轴为[0.0, 1.0]，y轴为[1.0, 0.0]
line_chart = foundry_ml_metrics.charts.line(xs=[0.0, 1.0], ys=[1.0, 0.0])

# 创建一个柱状图，类别为"category 1"和"category 2"，对应的y值为0.56和0.41
bar_chart = foundry_ml_metrics.charts.bar(xs=["category 1", "category 2"], ys=[0.56, 0.41])

# 将折线图添加到度量集合中
metric_set.add(name='My line chart', value=line_chart)

# 将柱状图添加到度量集合中
metric_set.add(name='My bar chart', value=bar_chart)
```

### 图像指标

Python 拥有大量的开源绘图库，可以保存图像。为了利用这一点，foundry_ml允许您提供与 matplotlib 和 seaborn 兼容的图像对象作为指标值。

```
Copied!1
2
3
4
5
6
7
from matplotlib import pyplot
# 绘制一个简单的折线图，x轴为[0, 1]，y轴为[1, 0]
pyplot.plot([0, 1], [1, 0])
# 获取当前的图形对象
matplotlib_plot = pyplot.gcf()
# 将图形对象添加到metric_set中，命名为'My image chart'
metric_set.add(name='My image chart', value=matplotlib_plot)
```

## 验证数据子集

模型性能经常在数据集的不同子集上有所不同。为了协助分析这一点，MetricSet.add方法接受一个subset参数，这是一个描述您应用的任何筛选的Python字符串字典。筛选的语义名称帮助用户理解他们的模型在代表现实世界问题的不同数据切片上的性能。

指标和子集将出现在建模目标中。

例如，也许在经典的开源鸢尾花数据上，您正在计算模型在低于平均值和高于平均值的花瓣长度上的准确性。

这可以通过以下方式完成：

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
def compute_accuracy(testing_df):
    # 实现准确率计算的函数
    compute_accuracy = ...

    # 创建一个 MetricSet 对象来记录模型的指标
    metric_set = foundry_ml_metrics.MetricSet(
        model = Model,
        input_data=testing_df
    )

    # 在所有数据上计算预测结果
    predictions = Model.transform(testing_df)
    # subset = {} 表示针对总体数据集，默认情况
    metric_set.add(name='accuracy', subset={}, value=compute_accuracy(predictions))

    # 过滤数据，计算 sepal_length 大于 3 的子集的准确率
    predictions_long = predictions.filter('sepal_length > 3')
    metric_set.add(name='accuracy', subset={'sepal_length': 'long'}, value=compute_accuracy(predictions_long))

    # 过滤数据，计算 sepal_length 小于 3 的子集的准确率
    predictions_short = predictions.filter('sepal_length < 3')
    metric_set.add(name='accuracy', subset={'sepal_length': 'short'}, value=compute_accuracy(predictions_short))
```

可以为子集字典提供任意数量的字段。

## 更新指标

指标集表示为数据集，并通过 Foundry 搭建计算。当模型就地更新或新的输入数据版本可用时，您必须重新搭建指标集，因为它与模型和输入数据集的特定版本相关联。

重要的是，如果您更新并重新运行模型，还需要重新搭建关联的指标集以防止信息过时，因为它们与特定的模型（和输入数据集）版本相关联。否则，您将在模型预览中看不到指标。
