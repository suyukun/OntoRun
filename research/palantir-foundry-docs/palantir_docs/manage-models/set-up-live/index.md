来源: https://palantir.com/docs/zh/foundry/manage-models/set-up-live/

# 设置和使用实时部署

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 设置和使用实时部署

实时部署是一个持久的、可扩展的部署，您可以通过API端点与其交互。实时部署可以与您的批处理部署一起在建模目标中进行管理，享有自动升级、可观察性和权限结构的所有相同优势。

## 要求

在创建新的实时部署之前，建模目标必须包含一个具有相应标签（Staging或Production）的现有发布版本。

## 创建部署

要创建新的实时部署，请导航到建模目标底部的部署部分，并选择蓝色的**+ 创建部署**按钮。

填写部署名称、描述，以及此部署应基于当前预发布或生产发布的模型。配置完成后，点击创建部署。

选择新创建的部署以打开详细信息，您将看到中间状态，指示包含最新发布和推理代码的容器镜像正在部署中。

## API 名称

要通过模型上的函数将模型投入运行，您必须为部署定义一个API名称。API名称在部署所在的空间中必须是唯一的。要定义API名称，请选择API名称旁边的铅笔图标。

### 状态和健康

部署更新完成后，状态和健康都应显示为绿色对勾。这些表示部署已准备好进行查询，并已成功更新为包含最新发布的模型。

## 测试实时部署

您可以通过转到部署详细信息页面上的查询选项卡来测试实时部署端点。您可以编写输入请求，将其发送到实时端点，并查看模型输出响应。提供两种查询类型：单I/O和多I/O。

单I/O查询仅支持单个表格输入/输出，而多I/O查询仅支持在模型资产中定义的ModelAdapter API。模型资产支持单I/O和多I/O查询类型，而数据集支持的部署仅支持单I/O查询。

### 示例命令

以下是如何通过curl使用转换端点查询实时部署的示例：

```
Copied!1
2
3
4
curl -X POST https://<URL>/foundry-ml-live/api/inference/transform/ri.foundry-ml-live.main.live-deployment.<RID>
-H "Authorization: <BEARER_TOKEN>" -H "Accept: application/json" -H "Content-Type: application/json" -d
'{"requestData":[{"house-location":"New York", "bedrooms":3,"bathrooms":1.5}],
 "requestParams":{}}'
```

```
Copied!1
2
3
4
5
6
# 这段代码使用 curl 命令向一个机器学习推理服务发送 POST 请求。
# <URL> 是 API 的基地址，<RID> 是具体部署的标识符。
# "Authorization" 头部需要提供一个有效的 BEARER_TOKEN 以验证请求。
# 请求体中包含 "requestData"，这是一个列表，包含一组待预测的数据。
# 在这个例子中，数据代表一栋位于纽约的房子的特征，包括 3 间卧室和 1.5 间浴室。
# "requestParams" 目前是空的，但可用于传递额外的参数。
```

或者，下面的示例展示了如何通过curl使用多I/O与transformV2端点查询实时部署：

```
Copied!1
2
3
4
5
curl -X POST https://<URL>/foundry-ml-live/api/inference/transform/ri.foundry-ml-live.main.live-deployment.<RID>/v2
# 设置授权令牌
-H "Authorization: <BEARER_TOKEN>" -H "Accept: application/json" -H "Content-Type: application/json" -d
# 输入数据的 JSON 格式
'{"input_df":[{"house-location":"New York", "bedrooms":3,"bathrooms":1.5},{"house-location":"San Francisco", "bedrooms":2,"bathrooms":1}]}'
```

## 部署操作

### 管理操作

对于正在运行的实时部署，有两个选项可以选择：

- 禁用以关闭部署，但仍允许重新启用以利用相同的目标RID。
- 删除以完全移除部署。旧的目标RID将不再可以被查询。
禁用的实时部署仍会出现在目标的部署页面中，并且可以再次启用。

### 资源配置

实时部署配置有副本数量以及CPU和GPU数量。

您可以在创建部署时配置资源需求，并在之后进行编辑。编辑运行时配置将自动触发部署的重新运行，这将无停机时间地升级端点。

要配置新的实时部署，选择创建部署，在部署类型下选择实时，然后输入副本数量和资源配置。

要编辑已配置的副本和资源，请导航到建模项目中的部署部分，从列出的部署中选择您的部署，然后选择运行时配置下的编辑按钮来编辑副本或资源配置。

### 查看部署服务日志

每个实时部署都会发出一系列描述部署启动进程的日志；这些日志包括部署将尝试下载和安装的发布环境中Conda包的URI，以及关于下载模型本身的详细信息。如果部署未能成功启动，可能会有相关的警告或出错级别日志帮助您了解发生了什么。

要直接从正在运行的实时部署中查看服务日志，请导航到部署详细信息页面上的日志和指标选项卡。您可以指定要搜索的时间窗口，通过任何字段筛选日志，并从视图中添加或移除列。您还可以使用右上角的下载按钮将所有日志下载为文本文件。

由于您可能已将部署配置为使用多个副本运行，因此您可能会看到似乎重复的日志——每组日志来自不同的副本。然而，每个日志都包含一个带有唯一node_id的标签，您可以根据需要通过副本进行筛选。您可以使用以下符号进行操作：

```
Copied!1
tags.node_id:{在此处插入 UUID}
```

要直接从您的模型发出日志，您可以使用标准的Python日志记录模块。实时部署将在日志和指标选项卡中使每一行日志可供查询。

```
Copied!1
2
3
4
5
6
7
import logging

# 创建一个名为 'model-logger' 的日志记录器
log = logging.getLogger('model-logger')

# 记录一条信息级别的日志
log.info("Emitting info directly from the model")
```

要从基于容器的模型发出日志，请在配置模型版本时启用遥测功能。

您实时部署的日志保留期为7天，之后将无法查看或下载。

### 查看部署指标

日志 & 指标选项卡提供两种类型的指标：Kubernetes 主机和推理容器。请确保了解这些指标类型之间的差异，以便正确监控和调试您的模型。

#### Kubernetes 主机指标

Kubernetes 主机指标显示主机上运行的所有进程所使用的内存和CPU使用率百分比，而不仅仅是与特定模型相关的进程。这些指标对于调试与调度和资源限制相关的问题非常重要。例如，如果您的模型性能较慢，但主机指标达到100%，您的模型可能正在被 Kubernetes 主机限制。

#### 推理容器指标

推理容器指标对于调试Python模型和模型适配器逻辑中的资源使用非常有帮助。这些指标提供了推理容器的确切内存使用和CPU核心使用情况，独立于整个Kubernetes主机。目前，使用指标不适用于基于容器的模型。

如果您只能查看Kubernetes主机指标而无法查看推理容器指标，您的容器可能在运行过时版本的实时部署。重启您的实时部署以更新版本并查看所有指标。

### Spark模型支持

支持的Spark版本可能会在即将发布的版本中发生变化，并且不保证向后兼容性。如果您的模型与当前的Spark版本不兼容，您可能需要重新搭建它。

所有实时部署现在都初始化了一个JDK和一个Spark发行版。这使得Spark模型可以与实时部署兼容。在这个交互式环境中，只支持本地Spark，这意味着所有处理都在单个JVM内完成。

由于实时部署期望输入和输出类型为Pandas数据帧，只要模型是标准支持的PySpark模型，foundry_ml Python库就会处理包装您的Spark模型。在任一方向转换数据帧时，尤其是在处理自定义Spark类型时，可能会出现数据类型转换问题。

在开发期望Spark数据帧的自定义模型时，您应该在预处理阶段或直接在transform函数中手动执行此转换。以下是一个简单的示例：

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
import pandas as pd
from pyspark.sql import SparkSession

def _transform(model, df):
    # 检查输入数据框是否为 Pandas 数据框
    if isinstance(df, pd.DataFrame):
        # 如果是 Pandas 数据框，则将其转换为 Spark 数据框
        df = SparkSession.builder.getOrCreate().createDataFrame(df)
    # 使用模型的 predict_spark_df 方法对 Spark 数据框进行预测
    return model.predict_spark_df(df)
```
