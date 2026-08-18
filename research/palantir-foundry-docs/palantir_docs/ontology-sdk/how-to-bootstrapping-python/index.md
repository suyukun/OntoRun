来源: https://palantir.com/docs/zh/foundry/ontology-sdk/how-to-bootstrapping-python/

# 启动一个新的Ontology SDK Python应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 启动一个新的Ontology SDK Python应用程序

在本页中，我们将逐步讲解创建一个使用Ontology SDK的Python应用程序的过程。下面的示例可以与许多Python框架一起使用，例如Flask©,Streamlit©, 和Jupyter™（外部链接）。

## 1：先决条件

### 创建一个Developer Console应用程序

请按照创建一个新的Developer Console应用程序页面中列出的步骤进行操作。

### 设置您的词元

在本地环境中导出您的词元。下面是使用示例个人访问词元的示例，但您可以在Developer Console中生成一个生命周期更长的词元。由于这是您的个人访问词元，因此不应将其检入源代码管理。

### 检查 Python 版本

Python SDK 需要 Python 版本在 3.9 和 3.11 之间。要检查您使用的 Python 版本，请输入以下命令：

```
Copied!1
2
python3 --version
# 此命令用于检查系统上安装的 Python 3 的版本。
```

### 非必填：设置证书

如果您的组织需要证书以用于网络流量，您可能需要告知Python证书的位置。

```
Copied!1
2
3
4
5
# 设置 SSL 证书文件路径
export SSL_CERT_FILE="/path/to/my.crt"

# 设置 Requests 模块使用的 CA 证书路径
export REQUESTS_CA_BUNDLE="/path/to/my.crt"
```

## 2: 安装最新版本的SDK

运行以下命令以安装最新版本的SDK，将任何< >替换为可在您的应用程序概览页面上找到的特定于应用程序的值。

```
Copied!1
pip install <YOUR-PACKAGE-NAME> --upgrade --extra-index-url "https://:$FOUNDRY_TOKEN@<INDEX-URL>"
```

此命令用于安装或升级指定的 Python 包<YOUR-PACKAGE-NAME>。以下是参数的说明：

- --upgrade：此选项用于升级已安装的包到最新版本。
- --extra-index-url：此选项用于指定额外的 Python 包索引 URL，从该 URL 安装包。需要使用环境变量$FOUNDRY_TOKEN进行身份验证。
请确保将<YOUR-PACKAGE-NAME>和<INDEX-URL>替换为实际的包名和索引 URL。

### 开发您的前端应用

在您的应用中，初始化 Foundry 客户端并开始开发。

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
import os
from <PACKAGE-NAME> import FoundryClient
from <PACKAGE-NAME>.core.api import UserTokenAuth

# 使用环境变量中的令牌创建用户身份验证对象
auth = UserTokenAuth(hostname="<YOUR-FOUNDRY-URL>", token=os.environ["FOUNDRY_TOKEN"])

# 用创建的认证对象初始化Foundry客户端
client = FoundryClient(auth=auth, hostname="<YOUR-FOUNDRY-URL>")

# 通过客户端获取本体对象并打印其中的一个
object = client.ontology.objects.<ANY-OBJECT>
print(object.take(1))
```

请注意，<PACKAGE-NAME>和<ANY-OBJECT>需要替换为实际的包名和对象名。
