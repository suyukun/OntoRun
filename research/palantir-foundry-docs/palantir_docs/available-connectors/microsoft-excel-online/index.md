来源: https://palantir.com/docs/zh/foundry/available-connectors/microsoft-excel-online/

# Microsoft Excel Online

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Microsoft Excel Online

Microsoft Excel Online连接器是一个Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保向连接器添加以下出口策略：

| 域名 | 必须 |
| --- | --- |
| <Server> | 始终需要。对于Exchange Online，使用Server='https://outlook.office365.com/EWS/Exchange.asmx' |
| outlook.office365.com | 仅当Platform=Exchange_Online且Schema=EWS时 |
| graph.microsoft.com | 仅当Platform=Exchange_Online且Schema=MSGraph时 |
| login.microsoftonline.com | 仅当Platform=Exchange_Online（默认）且AuthScheme=AzureAD, AzureServicePrincipal或AzureServicePrincipalCert时 |
| <KerberosKDC>:88 | 仅当AuthScheme=Negotiate时 |
| <KerberosServiceKDC>:88 | 仅当AuthScheme=Negotiate且Kerberos拓扑使用多个领域时 |
