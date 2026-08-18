来源: https://palantir.com/docs/zh/foundry/available-connectors/quickbooks-pos/

# QuickBooks POS

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# QuickBooks POS

QuickBooks POS 连接器是一个Palantir 提供的驱动连接器。该驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标 IP 地址，并且目标系统必须被配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| <URL> | 始终。URL 连接属性 - 运行 CData QuickBooks Gateway 的主机机器的地址和端口 |
