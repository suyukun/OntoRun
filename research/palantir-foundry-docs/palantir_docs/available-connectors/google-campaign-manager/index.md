来源: https://palantir.com/docs/zh/foundry/available-connectors/google-campaign-manager/

# Google Campaign Manager

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Google Campaign Manager

Google Campaign Manager连接器是一个由Palantir提供的驱动连接器。此驱动的官方文档可在此处 ↗找到。

## 网络

如果使用代理连接，必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 是否必需 |
| --- | --- |
| ads.google.com | 总是 |
| admanager.google.com | 总是 |
| accounts.google.com | 总是。用于OAuth |
