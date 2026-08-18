来源: https://palantir.com/docs/zh/foundry/integrate-models/container-model-adapter-example/

# 示例：实现一个容器模型适配器

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 示例：实现一个容器模型适配器

以下是为容器支持的模型定义的示例模型适配器。假设使用的镜像是一个简单的Flask服务器，在/mirror端点侦听，以接收仅包含“text”字段的请求Object。模型适配器将在响应Object的“returnedText”字段中逐字返回该文本。

您可以在API：ModelAdapter参考文档中查看container_contextObject的完整定义。

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
import requests
import json
import pandas as pd

import palantir_models as pm


class ExampleIdentityFunctionModelAdapter(pm.ContainerModelAdapter):
    """
        :display-name: Example Identity Function Model Adapter
        :description: Reference example of a model adapter for container-backed model
        :display-name: 示例身份函数模型适配器
        :description: 容器支持模型的模型适配器的参考示例
    """
    def __init__(self, shared_volume_path, model_host_and_port):
        self.shared_volume_path = shared_volume_path
        self.model_host_and_port = model_host_and_port

    @classmethod
    def init_container(cls, container_context):
        # 初始化容器时获取共享卷路径
        shared_volume_path = container_context.shared_empty_dir_mount_path
        # 注意此适配器仅期望一个容器名称和一个提供的服务URI
        model_host_and_port = list(container_context.services.values())[0][0]
        return cls(shared_volume_path, model_host_and_port)

    @classmethod
    def api(cls):
        # 定义输入输出的数据格式，输入是包含"text"列的Pandas DataFrame，输出是包含"text"和"returnedText"列的Pandas DataFrame
        inputs = {"input_df": pm.Pandas(columns=[("text", str)])}
        outputs = {"output_df": pm.Pandas(columns=[("text", str), ("returnedText", str)])}
        return inputs, outputs

    def predict(self, input_df):
        def run_inference_on_row(row):
            # 构建请求数据
            request = {"text": row.text}
            # 向模型服务发送POST请求
            response = requests.post("http://" + self.model_host_and_port + "/mirror", json=request)
            # 解析返回的JSON响应
            json_res = json.loads(response.content.decode("utf-8"))
            return (row.text, json_res["returnedText"])

        # 对输入数据逐行进行推理
        results = [run_inference_on_row(row) for row in input_df.itertuples()]
        columns = ["text", "returnedText"]
        # 返回包含推理结果的DataFrame
        return pd.DataFrame(results, columns=columns)
```

在这个代码中，ExampleIdentityFunctionModelAdapter是一个用于容器支持模型的适配器示例。通过init_container方法初始化时，获取共享卷路径和服务URI。在api方法中定义了输入输出的数据格式为包含文本的 Pandas DataFrame。predict方法中，逐行对输入数据进行推理，并通过 HTTP POST 请求与模型服务进行交互，最后返回包含原文本和模型返回文本的 DataFrame。
