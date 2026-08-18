来源: https://palantir.com/docs/zh/foundry/integrate-models/external-model-connection-vertex-ai/

# 示例：集成 Vertex AI 模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：集成 Vertex AI 模型

以下文档提供了一个示例配置和模型适配器，用于自定义连接到托管在 Google 的 Vertex AI 中的模型。

有关分步指南，请参阅有关如何创建模型适配器和如何创建连接到外部托管模型的文档。

## 示例 Vertex AI 表格模型适配器

首先，使用代码仓库应用中的模型适配器库发布并标记模型适配器。下面的模型适配器使用Vertex AI SDK for Python ↗和框架配置连接到托管在 Vertex AI 中的模型。以下代码已在Python 3.8.17、pandas 1.5.3、google-cloud-aiplatform 1.32.0、google-auth 2.23.0、google-auth-oauthlib 1.1.0版本中测试。

请注意，此模型适配器做出以下假设：

- 此模型适配器假设提供给该模型的数据是表格数据。
- 此模型适配器将输入数据序列化为 JSON 并将此数据发送到托管的 Vertex AI 模型。
- 此模型适配器假设响应可以从 JSON 反序列化为 pandas 数据框。
- 此模型适配器需要四个输入来构建 Vertex AI 客户端。region_name- 作为连接配置提供project_id- 作为连接配置提供endpoint_id- 作为连接配置提供google_application_credentials- 作为凭证提供
- region_name- 作为连接配置提供
- project_id- 作为连接配置提供
- endpoint_id- 作为连接配置提供
- google_application_credentials- 作为凭证提供
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
54
55
56
57
58
59
60
61
62
63
64
65
66
67
import palantir_models as pm
import models_api.models_api_executable as executable_api

from google.oauth2 import service_account
from google.cloud import aiplatform
from google.api_core import exceptions

import json
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VertexAITabularAdapter(pm.ExternalModelAdapter):
  """
  :display-name: Vertex AI Tabular Model Adapter
  :description: 用于Vertex AI模型的默认模型适配器，该模型期望输入和输出为表格数据。
  """

  def __init__(self, project_id, region_name, endpoint_id, google_application_credentials):
    self.endpoint_id = endpoint_id
    # google_application_credentials 预计为Google提供的密钥文件的有效字符串表示
    credentials = service_account.Credentials.from_service_account_info(
      json.loads(google_application_credentials),
      scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    aiplatform.init(project=project_id, location=region_name, credentials=credentials)

  @classmethod
  def init_external(cls, external_context) -> "pm.ExternalModelAdapter":
    project_id = external_context.connection_config["project_id"]
    region_name = external_context.connection_config["region_name"]
    endpoint_id = external_context.connection_config["endpoint_id"]
    google_application_credentials = external_context.resolved_credentials["google_application_credentials"]
    return cls(
      project_id,
      region_name,
      endpoint_id,
      google_application_credentials
    )

  @classmethod
  def api(cls):
    inputs = {"df_in": pm.Pandas()}
    outputs = {"df_out": pm.Pandas()}
    return inputs, outputs

  def predict(self, df_in):
    instances = df_in.to_dict(orient='records')
    try:
      endpoint = aiplatform.Endpoint(endpoint_name=self.endpoint_id)
    except ValueError as error:
      logger.error("初始化端点对象时出错，请仔细检查输入的 endpoint_id, project_id 和 region_name。")
      raise error
    try:
      # 假设模型的输出是可JSON序列化的
      # 如果结果对执行器来说太大，可能会导致内存不足
      prediction_result = endpoint.predict(instances=instances)
    except exceptions.Forbidden as error:
      logger.error("执行推理时出错，提供的 google_application_credentials 权限不足。")
      raise error
    except exceptions.BadRequest as error:
      logger.error("执行推理时出错，请仔细检查输入的数据框。")
      raise error
    return pd.json_normalize(prediction_result.predictions)
```

在此代码中，我们定义了一个VertexAITabularAdapter类，用于与 Google Cloud 的 Vertex AI 进行交互。这个类继承了pm.ExternalModelAdapter，并实现了与 Vertex AI 模型进行推理的功能。代码的关键部分包括凭证初始化、端点对象的创建和错误处理，以确保推理过程的顺利进行。

## Vertex AI 表格模型配置

接下来，配置外部托管模型以使用此模型适配器，并根据模型适配器的要求提供所需的配置和凭据。在此示例中，假设模型托管在us-central1，但这是可配置的。

请注意，上述VertexAITabularAdapter不需要 URL，因此留空；但是，配置和凭据映射使用与模型适配器中定义的相同的键完成。

### 选择出口策略

下面使用了一个已为us-central1-aiplatform.googleapis.com（端口 443）配置的出口策略。

### 配置模型适配器

在连接外部托管模型对话框中选择已发布的模型适配器。

### 配置连接配置

根据示例 Vertex AI 表格模型适配器的要求定义连接配置。

此适配器需要以下连接配置：

- region_name- 托管模型的 Google 区域名称。
- project_id- 此外部托管模型所属项目的唯一标识符。
- endpoint_id- 外部托管模型的唯一标识符。
### 配置凭据配置

根据示例 Vertex AI 表格模型适配器的要求定义凭据配置。

此适配器需要以下凭据配置：

- google_application_credentials- 这是服务账户私钥文件的全部内容，可以用于获取服务账户的凭据。您可以使用Google Cloud Console 的凭据页面 ↗创建私钥。
## Vertex AI 表格模型使用

现在 Vertex AI 模型已配置好，可以在实时部署或Python 变换中托管。

下图显示了在实时部署中对 Vertex AI 模型进行示例查询。
