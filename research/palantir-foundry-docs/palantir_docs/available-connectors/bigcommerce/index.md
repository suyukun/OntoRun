来源: https://palantir.com/docs/zh/foundry/available-connectors/bigcommerce/

# BigCommerce

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# BigCommerce

BigCommerce连接器是一个Palantir提供的驱动连接器。该驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| login.bigcommerce.com | 始终需要。认证和词元端点 |
| api.bigcommerce.com | 始终需要 |
| store-{STORE_ID}.mybigcommerce.com | 始终需要。在某些情况下，您插入/更新数据时似乎会使用 |
