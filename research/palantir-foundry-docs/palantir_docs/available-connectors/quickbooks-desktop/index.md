来源: https://palantir.com/docs/zh/foundry/available-connectors/quickbooks-desktop/

# QuickBooks Desktop

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# QuickBooks Desktop

QuickBooks Desktop 连接器是一个Palantir 提供的驱动连接器。此驱动的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出站策略添加到连接器中：

| 域名 | 要求 |
| --- | --- |
| <URL> | 始终。URL连接属性 - 运行 CData QuickBooks Gateway 的主机机器的地址和端口 |
