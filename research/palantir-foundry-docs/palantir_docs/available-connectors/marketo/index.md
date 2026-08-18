来源: https://palantir.com/docs/zh/foundry/available-connectors/marketo/

# Marketo

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Marketo

Marketo连接器是一个Palantir提供的驱动连接器。此驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须被配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域 | 必需 |
| --- | --- |
| <RESTEndpoint> | 仅当使用Schema=REST时 |
| <SOAPEndpoint> | 仅当使用Schema=SOAP时 |
