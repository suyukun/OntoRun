来源: https://palantir.com/docs/zh/foundry/integrate-models/external-model-connection-sagemaker/

# 示例：集成 Amazon SageMaker 模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：集成 Amazon SageMaker 模型

以下文档提供了一个示例配置和模型适配器，用于自定义连接到托管在 Amazon SageMaker 中的模型。

有关逐步指南，请参阅如何创建模型适配器和如何创建与外部托管模型的连接的文档。

## 示例 Amazon SageMaker 表格模型适配器

首先，使用代码库应用中的模型适配器库发布并标记一个模型适配器。下面的模型适配器使用AWS SDK for Python (Boto3) ↗和框架配置与托管在 Amazon SageMaker 中的模型的连接。以下代码经过测试，适用于版本Python 3.8.17、boto3 1.28.1和pandas 1.5.3。

请注意，此模型适配器做出了以下假设：

- 此模型适配器假设提供给该模型的数据是表格形式的。
- 此模型适配器将输入数据序列化为 JSON 并将其发送到托管的 Amazon SageMaker 模型。
- 此模型适配器假设响应可以从 JSON 反序列化为 pandas dataframe。
- 此模型适配器需要四个输入来构建一个 Boto3 客户端。region_name- 作为连接配置提供endpoint_name- 作为连接配置提供access_key_id- 作为凭证提供secret_access_key- 作为凭证提供
- region_name- 作为连接配置提供
- endpoint_name- 作为连接配置提供
- access_key_id- 作为凭证提供
- secret_access_key- 作为凭证提供
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
68
69
70
71
72
73
74
75
import palantir_models as pm
import models_api.models_api_executable as executable_api

import boto3
import json
import pandas as pd
import logging
from typing import Optional
from botocore.exceptions import ClientError

# 创建日志记录器
logger = logging.getLogger(__name__)


class SageMakerTabularAdapter(pm.ExternalModelAdapter):
    """
    :display-name: SageMaker 表格模型适配器
    :description: SageMaker模型的默认适配器，用于期望表格输入并输出表格数据的模型。
    """

    def __init__(self, region_name, endpoint_name, access_key_id, secret_access_key):
        self.endpoint_name = endpoint_name
        self.runtime = boto3.client(
            'runtime.sagemaker',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name
        )

    @classmethod
    def init_external(cls, external_context) -> "pm.ExternalModelAdapter":
        # 从外部上下文中初始化所需的AWS配置信息
        region_name = external_context.connection_config["region_name"]
        endpoint_name = external_context.connection_config["endpoint_name"]
        access_key_id = external_context.resolved_credentials["access_key_id"]
        secret_access_key = external_context.resolved_credentials["secret_access_key"]
        return cls(
            region_name,
            endpoint_name,
            access_key_id,
            secret_access_key
        )

    @classmethod
    def api(cls):
        # 定义输入和输出的数据格式，均为Pandas DataFrame
        inputs = {"df_in": pm.Pandas()}
        outputs = {"df_out": pm.Pandas()}
        return inputs, outputs

    def predict(self, df_in):
        # 将输入数据转换为JSON格式的payload
        payload = {
            "instances": df_in.apply(lambda row: {"features": row.tolist()}, axis=1).tolist()
        }
        try:
            # 调用SageMaker的终端节点以进行预测
            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType="application/json",
                Body=json.dumps(payload)
            )
        except ClientError as error:
            # 捕获并记录调用失败的错误
            logger.error("SageMaker推理调用失败。这可能表示此模型的出口策略有误。请仔细检查配置的出口策略并确保远程终端仍然可用。")
            raise error
        try:
            # 假定模型的输出可进行JSON反序列化
            # 如果结果对执行器来说太大，反序列化可能导致内存不足
            result = json.loads(response['Body'].read().decode())
        except ValueError as error:
            logger.error("此SageMakerTabularAdapter期望结果可进行JSON反序列化。")
            raise error
        # 将结果转换为Pandas DataFrame
        return pd.json_normalize(result)
```

## Amazon SageMaker 表格模型配置

接下来，配置外部托管模型以使用此模型适配器，并提供模型适配器所需的配置和凭据。在本示例中，模型假定托管在us-east-1，但这是可配置的。

请注意，上述SageMakerTabularAdapter不需要 URL，因此留空；但是，配置和凭据映射使用与模型适配器中定义的相同的键完成。

### 选择出口策略

下面使用的出口策略已为runtime.sagemaker.us-east-1.amazonaws.com(端口 443) 配置。

### 配置模型适配器

在连接外部托管模型对话框中选择已发布的模型适配器。

### 配置连接配置

根据示例 Amazon SageMaker 表格模型适配器的要求定义连接配置。

此适配器需要以下连接配置：

- region_name- 模型托管的 AWS 区域名称。
- endpoint_name- 外部托管模型的唯一标识符。
### 配置凭据配置

根据示例 Amazon SageMaker 表格模型适配器的要求定义凭据配置。

此适配器需要以下凭据配置：

- access_key_id- 这是调用 SageMaker 模型的用户的唯一标识符。
- secret_access_key- 这是调用 SageMaker 模型的用户的密钥。
## Amazon SageMaker 表格模型使用

现在 Amazon SageMaker 模型已配置，可以在实时部署或Python 变换中托管此模型。

下图显示了在实时部署中向 Amazon SageMaker 模型发出的示例查询。
