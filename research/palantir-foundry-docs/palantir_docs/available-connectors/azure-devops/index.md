来源: https://palantir.com/docs/zh/foundry/available-connectors/azure-devops/

# Azure DevOps

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Azure DevOps

Azure DevOps 连接器是一个Palantir提供的驱动连接器。该驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| dev.azure.com | 仅当Schema=REST（默认）且AzureDevOpsEdition='AzureDevOps Online'（默认）时 |
| analytics.dev.azure.com | 仅当Schema=Analytics且AzureDevOpsEdition='AzureDevOps Online'（默认）时 |
| <URL> | 仅当AzureDevOpsEdition='AzureDevOps OnPremise'时 |
| login.microsoftonline.com | 仅当AuthScheme=AzureAD（默认）且AzureEnvironment=GLOBAL（默认）时 |
| login.chinacloudapi.cn | 仅当AuthScheme=AzureAD（默认）且AzureEnvironment=CHINA时 |
| login.microsoftonline.us | 仅当AuthScheme=AzureAD（默认）且AzureEnvironment=USGOVT或USGOVTDOD时 |
