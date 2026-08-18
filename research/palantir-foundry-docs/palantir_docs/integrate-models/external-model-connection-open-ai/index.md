来源: https://palantir.com/docs/zh/foundry/integrate-models/external-model-connection-open-ai/

# 示例：集成 Open AI 模型

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：集成 Open AI 模型

以下文档提供了一个示例配置和模型适配器，用于与 Open AI 模型的自定义连接。

有关逐步指南，请参阅我们的文档：如何创建模型适配器和如何创建到外部托管模型的连接。

## 示例 Open AI 模型适配器

要在 Foundry 中使用此示例，请在代码库应用程序中使用模型适配器库发布并标记一个模型适配器。

该模型适配器配置了与我们在 Azure 托管的 Open AI 实例的连接。此配置已通过Python 3.8.17、pandas 1.5.3和openai 1.1.0测试。构建 OpenAI 客户端需要以下五个输入：

- base_url- 以base_url提供
- api_type- 在连接配置中提供
- api_version- 在连接配置中提供
- engine- 在连接配置中提供
- api_key- 以resolved_credentials提供
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
76
77
78
79
import palantir_models as pm
import models_api.models_api_executable as executable_api

from typing import Optional

import openai
import logging

logger = logging.getLogger(__name__)


class OpenAIModelAdapter(pm.ExternalModelAdapter):
  def __init__(self, base_url, api_type, api_version, engine, api_key):
    # 定义用于补全的引擎
    self.engine = engine

    # 设置 OpenAI 变量
    openai.api_type = api_type
    openai.api_key = api_key
    openai.api_base = base_url
    openai.api_version = api_version

  @classmethod
  def init_external(cls, external_context) -> "pm.ExternalModelAdapter":
    # 从 external_context 中初始化参数
    base_url = external_context.base_url
    api_type = external_context.connection_config["api_type"]
    api_version = external_context.connection_config["api_version"]
    engine = external_context.connection_config["engine"]
    api_key = external_context.resolved_credentials["api_key"]
    return cls(
      base_url,
      api_type,
      api_version,
      engine,
      api_key
    )

  @classmethod
  def api(cls):
    # 定义输入输出数据格式
    inputs = {"df_in": pm.Pandas(columns=[("prompt", str)])}
    outputs = {"df_out": pm.Pandas(columns=[("prompt", str), ("prediction", str)])}
    return inputs, outputs

  def predict(self, df_in):
    # 执行预测操作
    predictions = []
    for _, row in df_in.iterrows():
      messages = [{"role": "user", "content": row['prompt']}]
      try:
        response = openai.ChatCompletion.create(
          engine=self.engine,
          messages=messages,
        )
      except openai.error.Timeout as e:
        logger.error(f"OpenAI API request timed out: {e}")
        raise e
      except openai.error.APIError as e:
        logger.error(f"OpenAI API returned an API Error: {e}")
        raise e
      except openai.error.APIConnectionError as e:
        logger.error(f"OpenAI API request failed to connect: {e}")
        raise e
      except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI API request was invalid: {e}")
        raise e
      except openai.error.AuthenticationError as e:
        logger.error(f"OpenAI API request was not authorized: {e}")
        raise e
      except openai.error.PermissionError as e:
        logger.error(f"OpenAI API request was not permitted: {e}")
        raise e
      except openai.error.RateLimitError as e:
        logger.error(f"OpenAI API request exceeded rate limit: {e}")
        raise e
      predictions.append(response.choices[0].message.content)
    df_in['prediction'] = predictions
    return df_in
```

此代码定义了一个OpenAIModelAdapter类，用于通过 OpenAI 的 API 进行自然语言处理任务。它包含了初始化方法和一个predict方法，用于执行预测并处理可能的 API 异常。

## Open AI 模型配置

接下来，配置外部托管模型以使用此模型适配器，并按照模型适配器的要求提供必要的配置和凭证。

请注意，URL 以及配置和凭证映射使用与模型适配器中定义的相同密钥完成。

### 选择出口策略

下面的示例使用了一个为api.llm.palantir.tech（端口 443）配置的出口策略。

### 配置模型适配器

在连接外部托管模型对话框中选择已发布的模型适配器。

### 配置 URL 和连接配置

根据示例 Open AI 模型适配器的要求定义连接配置。

此适配器需要以下 URL:https://api.llm.palantir.tech/preview

此适配器需要以下连接配置：

- api_type- 用于进行推理的 Open AI 模型类型。
- api_version- 要使用的 API 版本。
- engine- 要使用的模型引擎。
### 配置凭证配置

根据示例 Open AI 模型适配器的要求定义凭证配置。

此适配器需要以下凭证配置：

- api_key- 查询 Open AI 所需的密钥。
## Open AI 模型使用

现在 Open AI 模型已经配置好，可以在实时部署或Python 变换中托管此模型。

下图显示了在实时部署中对 Open AI 模型进行的示例查询。
