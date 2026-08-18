来源: https://palantir.com/docs/zh/foundry/available-connectors/microsoft-onenote/

# Microsoft OneNote

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Microsoft OneNote

Microsoft OneNote连接器是一个由Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在这里↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| graph.microsoft.com | 仅当AzureEnvironment=GLOBAL（默认）时 |
| login.microsoftonline.com | 仅当AuthScheme=AzureAD（默认）、AzureServicePrincipal、AzureServicePrincipalCert且AzureEnvironment=GLOBAL时 |
| microsoftgraph.chinacloudapi.cn | 仅当AzureEnvironment=CHINA时 |
| login.chinacloudapi.cn | 仅当AuthScheme=AzureAD（默认）、AzureServicePrincipal 、AzureServicePrincipalCert且AzureEnvironment=CHINA时 |
| graph.microsoft.us | 仅当AzureEnvironment=USGOVT时 |
| login.microsoftonline.us | 仅当AuthScheme=AzureAD（默认）、AzureServicePrincipal、AzureServicePrincipalCert且AzureEnvironment=USGOVT或USGOVTDOD时 |
| dod-graph.microsoft.us | 仅当AzureEnvironment=USGOVTDOD时 |
