来源: https://palantir.com/docs/zh/foundry/data-connection/webhooks-overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

您可以使用Data Connection配置Webhooks，以将Foundry连接到Foundry之外的系统和工作流。

每个Webhook提供了一种向Palantir Foundry外部系统发出请求的方法。例如，您可以创建一个Webhook，当用户在Foundry应用程序中选择一个按钮时，它会对外部服务器执行一个HTTP请求，从而将该应用程序连接到现有工作流和源系统。

每个Webhook在Data Connection中与单个源相关联。源存储连接到外部系统所需的凭据。根据Webhook关联的源的类型，某些任务类型可供使用。例如，在使用REST时，您可以灵活地配置应向外部服务发出的HTTP调用。

可以灵活配置Webhooks以接受特定输入并捕获外部系统请求的输出。此外，您可以设置Webhook执行的时间、并发性和速率限制。有关详细的配置选项，请参阅Webhooks参考。

请参阅文档的以下部分以了解有关Webhooks的更多信息：

- 按照教程设置Webhook。
- 查看Webhooks参考以了解更多关于配置、限制和权限的信息。
- 查看操作文档以了解如何为终端用户应用程序配置Webhooks。
- 了解如何从外部函数调用webhooks，以编写自定义代码与外部系统交互。