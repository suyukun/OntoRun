来源: https://palantir.com/docs/zh/foundry/transforms-python/data-expectations-getting-started/

# 开始

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 开始

本指南将介绍如何在Python变换库中设置数据期望。有关数据期望的高级概述，请参见此页面。

### 库设置

打开代码库左侧的库搜索面板。搜索transforms-expectations并在库选项卡中点击“添加库”。

然后，您的代码库将解析所有依赖项并重新运行检查。这可能需要一点时间，之后您就可以在变换中开始使用该库。

### 变换设置

在您的变换文件中导入expectations和Check：

```
Copied!1
2
3
4
5
from transforms.api import transform_df, Input, Output, Check
from transforms import expectations as E

# 从 transforms.api 导入 transform_df, Input, Output 和 Check
# 从 transforms 导入期望模块 expectations，并命名为 E
```

对于一些常见的模式和列期望，您可能还需要导入types:

```
Copied!1
from pyspark.sql import types as T  # 从pyspark.sql导入类型模块并简写为T
```

### 创建检查

单个检查的基本结构：

```
Copied!1
2
3
Check(expectation, 'Check unique name', on_error='WARN/FAIL')
# 这行代码用于检查某个预期条件（expectation），并命名为'Check unique name'。
# 参数'on_error'指定在错误发生时应采取的动作，'WARN/FAIL'表示警告或失败。
```

- 期望- 单个期望，可以是多个子期望的复合期望（例如，使用any/all操作符）
- 检查唯一名称- 在变换中必须唯一（相同名称不能在输出和输入之间共享），并将在应用程序中标识检查（例如，数据健康，搭建应用程序）
- on_error- 定义任务在期望未满足时的行为：FAIL（默认）- 如果检查失败，任务将中止WARN- 任务将继续，警告将由数据健康生成和处理
- FAIL（默认）- 如果检查失败，任务将中止
- WARN- 任务将继续，警告将由数据健康生成和处理
指派检查到数据集

每个检查应该传递给单个输入或输出。将单个检查传递为checks=check1或将多个检查传递为数组：checks=[check1, check2, ...]

使用多个检查来创建更清晰的期望结构，并分别控制每个有意义检查的行为。

一个输出简单主键检查的示例：

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
from transforms.api import transform_df, Input, Output, Check
from transforms import expectations as E

@transform_df(
    Output(
        "/Users/data/dataset",
        checks=Check(E.primary_key('id'), 'Primary Key', on_error='FAIL')  # 检查'id'字段是否为主键，若不是则失败
    ),
    input=Input("Users/data/input")  # 输入数据集路径
)
def my_compute_function(input):
    return input  # 直接返回输入的数据集
```

### 复杂检查

您还可以使用复合期望来添加更复杂的检查。例如，让我们检查列age的类型是否为long并在给定范围内。请注意，我们可以定义复合期望并在变换中的多个检查中使用它，对出错应用不同的行为。

即使检查由复合期望组成，也会整体监控检查。如果您想监控（即观察并接收通知）复合期望的特定部分，建议将其拆分为几个不同的检查。

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
from transforms.api import transform_df, Input, Output, Check
from transforms import expectations as E

from pyspark.sql import types as T

# 我们假设年龄在0到200之间是有效的。
expect_valid_age = E.all(
    E.col('age').has_type(T.LongType()),  # 检查列'age'的类型是否为LongType
    E.col('age').gte(0),  # 检查列'age'的值是否大于等于0
    E.col('age').lt(200)  # 检查列'age'的值是否小于200
)

@transform_df(
    Output(
        "/Users/data/dataset",
        checks=[
            Check(E.primary_key('id'), 'Primary Key', on_error='FAIL'),  # 检查'id'列是否是主键
            Check(expect_valid_age, 'Valid age on output', on_error='FAIL')  # 检查输出数据集中的年龄是否有效
        ]
    ),
    input=Input(
        "Users/data/input",
        checks=Check(expect_valid_age, 'Valid age on input', on_error='WARN')  # 检查输入数据集中的年龄是否有效
    )
)
def my_compute_function(input):
    return input  # 返回输入数据集，未进行任何变换
```
