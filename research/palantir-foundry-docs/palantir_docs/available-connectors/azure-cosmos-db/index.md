来源: https://palantir.com/docs/zh/foundry/available-connectors/azure-cosmos-db/

# Azure Cosmos DB

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Azure Cosmos DB

Azure Cosmos DB连接器是一个Palantir提供的驱动连接器。此驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| <AccountEndpoint> | 始终。AccountEndpoint连接属性（可能是https://<Server>:<Port>格式，也可能是完整URL） |
| login.microsoftonline.com | 仅当AuthScheme=AzureAD,AzureServicePrincipal, AzureServicePrincipalCert 且AzureEnvironment=GLOBAL（默认）时 |
| login.chinacloudapi.cn | 仅当AuthScheme=AzureAD,AzureServicePrincipal, AzureServicePrincipalCert 且AzureEnvironment=CHINA时 |
| login.microsoftonline.us | 仅当AuthScheme=AzureAD,AzureServicePrincipal, AzureServicePrincipalCert 且AzureEnvironment=USGOVT或USGOVTDOD时 |
