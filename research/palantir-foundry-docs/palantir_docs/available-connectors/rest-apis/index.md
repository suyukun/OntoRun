来源: https://palantir.com/docs/zh/foundry/available-connectors/rest-apis/

# REST

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# REST

Foundry可以与提供REST（表述性状态转移）API的外部系统进行集成。根据您是同步、导出还是交互调用REST API，您可能需要采用不同的方法。在此页面上，您可以找到多种连接选项，以实现与REST API的安全高效集成。

## REST API来源

REST API来源可用于需要通过操作直接从Foundry应用程序向外部系统进行交互HTTP请求的工作流。例如，您可以创建一个Workshop应用程序，其中有一个按钮，使用webhook在点击时调用REST端点，将该应用程序连接到现有工作流和来源系统。

HTTP端点的webhooks应在数据连接中使用REST API来源类型。您需要配置基础URL、身份验证和一个非必填端口。

| 选项 | 必填 | 描述 |
| --- | --- | --- |
| 域 | 是 | 必须指定至少一个域。 |
| 身份验证 | 是 | 对于每个域，必须指定身份验证。选项包括None、Basic、Bearer Token和API Key。 |
| 端口 | 否 | 可以非必填地指定一个端口。默认情况下，所有REST webhooks将在端口443上使用HTTPS。仅在使用代理运行时时支持443以外的端口。 |
| 请求选项 | 否 | 当选择API Key身份验证时，您可以选择是否要在webhook请求中将API Key作为查询参数或头部传递。 |

下面的示例配置显示如何使用bearer token身份验证配置到https://my-domain.com的连接。

REST API来源类型不支持其他功能，例如同步或导出。传统的magritte-rest-v2来源类型不再推荐用于Webhooks工作流。对REST API的同步和导出应使用外部变换。

了解有关Foundry中Webhooks的更多信息。

## 代码库中的外部变换

使用Python变换库来配置网络出口和凭证，并编写逻辑以访问API。例如，您可以使用外部变换查询API以处理Foundry数据集元数据或与API服务交互以将图像输出到数据集。外部变换是配置需要调用REST API的同步和导出的推荐方法。

外部变换目前不支持使用代理运行时与本地系统通信。传统的magritte-rest-v2来源类型可用于本地REST API调用，但不再推荐用于直接连接。如果您需要调用防火墙后的REST API，请联系您的Palantir代表以获取更多信息。

了解有关使用外部变换调用API的更多信息。

## Foundry REST API

对于希望在Foundry平台上搭建应用程序的情况，请使用Foundry REST API。Foundry API使用OAuth 2.0协议进行身份验证，主要使用JSON请求和响应，并提供对Ontology和建模资源的支持。

了解有关Foundry API的更多信息。
