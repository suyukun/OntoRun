来源: https://palantir.com/docs/zh/foundry/ontology-sdk/how-to-add-to-existing-typescript/

# 将 Ontology SDK 包添加到现有应用程序中

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将 Ontology SDK 包添加到现有应用程序中

本页面将引导您完成将 Ontology SDK 包添加到现有应用程序的过程。如果您没有现有应用程序，请查看启动新的 Ontology SDK 应用程序的文档。

## 1: 先决条件

### 创建一个 Developer Console 应用程序

请按照创建新的 Developer Console 应用程序页面上的步骤操作。

### 设置您的词元

在您的本地环境中导出您的词元。下面是使用示例个人访问词元的例子，但您可以在 Developer Console 中生成一个更长时间有效的词元。此词元不应被检入源代码控制，因为它是您的个人访问词元。

### 检查 Node 版本

TypeScript SDK 需要 Node 18 或更高版本才能工作。要检查您使用的 Node 版本，请使用以下命令。

## 2: 将Ontology SDK添加到现有项目中

### 设置NPM注册表

将以下代码添加到您的存储库或用户.npmrc文件中，用应用程序特定的值替换任何< >：

```
// <REGISTRY-URL-FROM-OVERVIEW-PAGE>:_authToken=${FOUNDRY_TOKEN}
// 使用 FOUNDRY_TOKEN 进行身份验证，与注册表 URL 关联
<PACKAGE-NAME>:registry=https://<REGISTRY-URL-FROM-OVERVIEW-PAGE>
// 指定 <PACKAGE-NAME> 的注册表 URL
```

### 非必填: 设置证书

如果您的组织要求网络流量使用证书，您可能需要告诉 Node 该证书的位置。

```
Copied!1
2
export NODE_EXTRA_CA_CERTS="/path/to/my.crt"
# 设置环境变量 NODE_EXTRA_CA_CERTS，以指定额外的 CA 证书路径
```

### 安装最新版本的SDK

运行以下命令以安装您的SDK包：

```
Copied!1
2
3
4
5
6
7
8
# 安装指定包的最新版本
npm install <PACKAGE-NAME>@latest

# 安装 @osdk/client 包的最新版本
npm install @osdk/client@latest

# 安装 @osdk/oauth 包的最新版本
npm install @osdk/oauth@latest
```

### 初始化 Foundry 客户端以开始开发

将以下代码添加到您的应用程序中，并用您的包的具体内容替换任何< >：

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
import { createPublicOauthClient } from "@osdk/oauth";
import { createClient } from "@osdk/client";
import { <ANY-OBJECT-NAME> } from "<PACKAGE-NAME>";
import React, { useEffect } from "react";

// 创建公共OAuth客户端
const auth = createPublicOauthClient("<YOUR-CLIENT-ID>", "<YOUR-FOUNDRY-URL>", "<YOUR-REDIRECT-URL>");
// 创建客户端实例，传入OAuth认证信息
const client: Client = createClient("<YOUR-FOUNDRY-URL>", "<YOUR-ONTOLOGY-RID>", auth);

export default function SimpleReactComponent() {
    useEffect(() => {
        // 在组件挂载时执行
        if (auth.getTokenOrUndefined()) {
            // 如果存在Token，则尝试刷新Token
            auth.refresh().catch(() =>
            /**
               如果无法刷新Token（例如用户未登录），则初始化Foundry的登录流程
               一旦登录完成，用户将被重定向回 http://localhost:8080/auth/callback
            **/
            auth.signIn())
        } else {
            // 如果没有Token，使用客户端实例获取对象的分页数据
            client(<ANY-OBJECT-NAME>).fetchPage({ $pageSize: 10 }).then((object) => {
                console.log(object.data); // 打印获取到的数据
            });
        }
    }, []);
};
```
