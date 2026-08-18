来源: https://palantir.com/docs/zh/foundry/compute-modules/authoring-locally-overview/

# 在本地开发环境中创建计算模块

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在本地开发环境中创建计算模块

计算模块功能处于测试阶段，可能无法在所有注册中使用。如果计算模块在您的注册中可用，请导航到计算模块应用程序以获取最新文档。

从根本上说，计算模块是遵循基本API的Docker容器，因此可以在任何可以搭建Docker镜像的地方编写。本文档提供了各种计算模块API如何交互的高级概述。

有关计算模块的具体示例，请参见创建一个基本的Python计算模块。

## 实现计算模块API

如果您需要使用不支持的语言，或者您想要最大的灵活性，您将需要创建一个连接到计算模块API的HTTPS客户端。此客户端将从服务器获取任务，处理它们，然后将结果发送回服务器。

### 连接信息

工作者需要知道连接详细信息以与服务器通信。为了方便，这些详细信息存储在一个文件中，文件路径在名为CONNECTION_TO_RUNTIME的环境变量（或“env var”）中指定。环境变量将在启动时存在，但文件可能在您的容器启动时尚未写入。该文件包含一个具有以下属性的JSON对象：

- host: 服务器主机名。始终为localhost。
- 始终为localhost。
- port: 服务器端口。端口始终为8945。
- 端口始终为8945。
- getJobPath: 获取任务的API端点。/interactive-module/api/internal-query/job
- /interactive-module/api/internal-query/job
- postResultPath: 提交任务结果的API端点。/interactive-module/api/internal-query/results
- /interactive-module/api/internal-query/results
- moduleAuthToken: 模块的认证词元。一个名为MODULE_AUTH_TOKEN的环境变量指向存储此信息的文件，并将在启动时存在。
- 一个名为MODULE_AUTH_TOKEN的环境变量指向存储此信息的文件，并将在启动时存在。
- trustStorePath: SSL证书文件的路径。一个名为CONNECTIONS_TO_OTHER_PODS_CA_PATH的环境变量指向存储此信息的文件，并将在启动时存在。
- 一个名为CONNECTIONS_TO_OTHER_PODS_CA_PATH的环境变量指向存储此信息的文件，并将在启动时存在。
连接信息文件的示例内容：

```
Copied!1
2
3
4
5
6
7
8
{
    "host": "localhost",  // 服务器主机名或IP地址，通常是'localhost'表示本地服务器
    "port": 8945,  // 服务器监听的端口号
    "getJobPath": "/api/v1/getJob",  // 获取作业的API路径
    "postResultPath": "/api/v1/postResult",  // 提交结果的API路径
    "moduleAuthToken": "your_auth_token",  // 模块认证令牌，用于身份验证
    "trustStorePath": "/path/to/ssl/certificate"  // SSL证书存储路径，用于安全通信
}
```

### 获取任务

为了从服务器获取任务，工作者需要向getJobPath端点发送一个 HTTPS GET 请求。请求必须包含Module-Auth-Token头，其值为moduleAuthToken。

如果服务器有可用的任务，它将以 JSON 对象的形式响应包含任务详情的信息。工作者应解析响应并从computeModuleJobV1属性中提取jobId。获取任务的端点是长轮询的，因此如果没有任务接收，服务器会阻塞最多 5 秒，而一旦有任务存在则会立即返回。您应该在while循环中调用此端点而不需要延迟。如果没有任务存在，服务器将以 HTTP 状态204响应，如果有任务存在，它将以状态200响应。

任务响应示例：

```
Copied!1
2
3
4
5
6
7
8
{
   "type": "computeModuleJobV1", // 计算模块作业版本1
   "computeModuleJobV1": {
        "jobId": "12345",       // 作业ID
        "queryType": "double",  // 查询类型，表示需要执行的操作类型
        "query": 2              // 查询或操作的输入参数
   }
}
```

在将结果发布回服务器时，必须使用jobId。queryType可用于路由任务。如果您从函数中调用，queryType将与函数名相同。查询字段包含一个事件，可以被用于在作为函数的参数。

### 发送任务结果

一旦工作者处理完任务，必须将结果发送回服务器。为此，工作者发送一个HTTPS POST请求到postResultPath端点，并将jobId附加到路径中。请求必须包含以下头信息：

- Module-Auth-Token：moduleAuthToken的值。
- Content-Type：设置为application/octet-stream。
编译后的路径将类似于${connectionInfo.host}:${connectionInfo.port}${connectionInfo.postResultPath}/${jobId}。

请求体应包含任务结果作为编码的字节流，其在Python中的示例如下：json.dumps(result).encode('utf-8')

### 错误处理和重试

工作者应处理在获取连接信息、获取任务和发送任务结果时的错误和重试。在提供的代码示例中，如果读取连接信息文件失败，工作者会重试，直到达到最大尝试次数（MAX_READ_ATTEMPTS）。工作者还会在GET和POST请求期间处理错误，即使出错也会继续获取和处理任务。

### 实现步骤

- 从CONNECTION_TO_RUNTIME环境变量中指定的文件中读取连接信息。
- 使用来自trustStorePath的SSL证书搭建一个HTTPS代理。
- 创建一个循环以持续获取和处理任务：发送GET请求到getJobPath端点以获取任务。如果有任务可用，根据任务的具体要求处理它。发送POST请求到postResultPath端点，并附带jobId以发送任务结果。在GET和POST请求期间处理错误和重试。
- 发送GET请求到getJobPath端点以获取任务。
- 如果有任务可用，根据任务的具体要求处理它。
- 发送POST请求到postResultPath端点，并附带jobId以发送任务结果。
- 在GET和POST请求期间处理错误和重试。
- 启动循环以获取和处理任务。
请参见创建一个基本的Python计算模块以获取搭建docker镜像的步骤

## 创建Docker镜像

使用Python3的基础镜像创建一个Dockerfile，并将环境变量DEPLOYED_APP_PATH更新为app.py，如下所示。一旦创建了文件，在项目文件夹中运行命令docker build . --platform=linux/amd64以创建Docker镜像。

```
Copied!1
2
3
4
5
6
7
FROM --platform=linux/amd64 python:latest
# 指定基础镜像为最新版本的 python，且平台为 linux/amd64。

...

COPY app.py $(DEPLOYED_APP_PATH}/
# 复制本地的 app.py 文件到容器中的指定路径 $(DEPLOYED_APP_PATH)。
```

确保映像平台与您要部署的资源队列对齐。一些 Foundry 实例可以支持部署linux/arm64映像，但默认情况下仅支持linux/amd64。如果您是在 Apple Silicon（M 系列非英特尔芯片）上搭建映像，请仔细检查映像的架构。

现在您已经搭建了 Docker 映像，可以继续部署计算模块。
