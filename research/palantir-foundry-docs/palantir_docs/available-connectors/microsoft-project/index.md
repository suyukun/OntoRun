来源: https://palantir.com/docs/zh/foundry/available-connectors/microsoft-project/

# Microsoft Project

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Microsoft Project

Microsoft Project连接器是一个Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域 | 必需 |
| --- | --- |
| <URL> | 始终 |
| <SSOLoginURL> | 仅当AuthScheme=ADFS,OKTA |
| login.microsoftonline.com | 仅当AuthScheme=AzureAD,OAuth且AzureEnvironment=GLOBAL（默认） |
| login.chinacloudapi.cn | 仅当AuthScheme=AzureAD,OAuth且AzureEnvironment=CHINA |
| login.microsoftonline.us | 仅当AuthScheme=AzureAD,OAuth且AzureEnvironment=USGOVT或USGOVTDOD |
| <Subdomain>.onelogin.com | 仅当AuthScheme=OneLogin,在SSOProperties中设置 |
