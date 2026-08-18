来源: https://palantir.com/docs/zh/foundry/available-connectors/adobe-commerce/

# Adobe Commerce

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Adobe Commerce

Adobe Commerce 连接器是一个由 Palantir 提供的驱动程序连接器。这个驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标 IP 地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| <URL> | 始终 |
