来源: https://palantir.com/docs/zh/foundry/available-connectors/azure-synapse/

# Azure Synapse

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Azure Synapse

Azure Synapse连接器是一个Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出站策略添加到连接器中：

| 域 | 必须 |
| --- | --- |
| <Server>:<Port> | 始终。服务器连接属性 |
| None | 始终。端口连接属性 |
| <StorageAccountLocation> | 仅用于在COPY模式下暂存数据 |
| login.microsoftonline.com | 仅在AuthScheme=AzureAD,AzureServicePrincipal, AzureServicePrincipalCert, AzurePassword 并且AzureEnvironment=GLOBAL（默认）时使用 |
| login.chinacloudapi.cn | 仅在AuthScheme=AzureAD,AzureServicePrincipal , AzureServicePrincipalCert, AzurePassword 并且AzureEnvironment=CHINA时使用 |
| login.microsoftonline.us | 仅在AuthScheme=AzureAD,AzureServicePrincipal, AzureServicePrincipalCert, AzurePassword 并且AzureEnvironment=USGOVT或 USGOVTDOD时使用 |
