来源: https://palantir.com/docs/zh/foundry/transforms-python/lightweight-overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

轻量级变换代表了一种新的后端，用于运行您的Python数据处理管道，同时允许您使用大部分您已熟悉的变换API。

随着单个计算机变得更强大，越来越多的数据变换可以在单个节点上运行。这意味着，对于中小型数据集，可以不依赖于分布式并行处理来执行变换。这种方法可以减少与Spark执行器分布式编排相关的开销，并使得可以使用单节点替代方案来编写数据管道，例如Polars ↗或DuckDB ↗。

随着我们继续扩展轻量级变换的功能，我们建议您始终将您的库升级到foundry-transforms-lib-python的5.400.0或类似版本，以保持最新的功能：

- 自带容器（BYOC）工作流
- 增量变换（在v0.556.0中添加）
## 快速开始

轻量级变换构建于容器编排基础设施之上，使用其功能时必须在您的Foundry注册中存在。

此示例展示了如何在Python变换管道中使用轻量级变换。假设我们有以下通过@transform_pandas使用pandas的Spark管道：

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
from transforms.api import transform_pandas, Input, Output

@transform_pandas(
    Output('/Project/folder/output'),
    df=Input('/Project/folder/input'),
)
def compute(df):
    # 筛选出名字以"A"开头的行，并选取"Name"和"Age"两列，最后按"Age"列进行排序
    return (
        df[df['Name'].str.startswith("A")]
            .loc[:, ['Name', 'Age']]
            .sort_values(by="Age")
    )
```

要将其转换为轻量级变换，您需要：

- 升级您的Python代码库到最新版本。
- 从库选项卡安装foundry-transforms-lib-python。
- 导入并在现有装饰器上应用@lightweight，如下代码片段所示：
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
from transforms.api import transform_pandas, Input, Output, lightweight

@lightweight
@transform_pandas(
    Output('/Project/folder/output'),
    df=Input('/Project/folder/input'),
)
def compute(df):
    return (
        df[df['Name'].str.startswith("A")]  # 过滤出名字以“A”开头的行
            .loc[:, ['Name', 'Age']]  # 选择“Name”和“Age”两列
            .sort_values(by="Age")  # 按“Age”列进行排序
    )
```

移动到轻量级变换，如上所示，可以将小数据上的变换速度提高一倍。

如上所示，@lightweight仅与@transform_pandas或仅依赖.pandas()方法的@transform管道兼容。

接下来，我们可以启用我们的变换以使用Polars，以提高可扩展性。

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
import polars as pl
from transforms.api import transform, Input, Output, lightweight

@lightweight
@transform(  # 已从 @transform_pandas 更改为 @transform
    output=Output('/Project/folder/output'),
    dataset=Input('/Project/folder/input'),
)
def compute(output, dataset):
    output.write_table(dataset
        .polars()  # 将输入数据转换为 Polars DataFrame
        .filter(pl.col('Name').str.starts_with('A'))  # 过滤掉名字不以'A'开头的记录
        .select(['Name', 'Age'])  # 选择'Name'和'Age'列
        .sort(by='Age')  # 按'Age'列排序
    )
```

这个代码片段使用了polars库对数据进行处理，并使用transforms框架进行数据输入和输出。
这个管道现在使用您所有可用的CPU核心，并配备了Polars的查询优化引擎，可以消除不必要的操作，并找到比Pandas更有效的算法来执行您的操作。

## 下一步

要了解有关轻量级变换的更多信息，请继续查看轻量级变换API文档。
