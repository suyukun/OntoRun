来源: https://palantir.com/docs/zh/foundry/available-connectors/google-spanner/

# Google Spanner

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Google Spanner

Google Spanner连接器是Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保向连接器添加以下出口策略：

| 域名 | 必需 |
| --- | --- |
| accounts.google.com | 始终。OAuth所需 |
| spanner.googleapis.com | 始终。有一个隐藏的属性Server可以用不同的URL覆盖此项。 |
| googleapis.com | 始终 |
