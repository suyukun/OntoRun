来源: https://palantir.com/docs/zh/foundry/available-connectors/sap-concur/

# SAP Concur

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SAP Concur

SAP Concur 连接器是一个Palantir 提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标 IP 地址，并且目标系统必须被配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必须 |
| --- | --- |
| developer.concur.com | 总是 |
| us2.api.concursolutions.com | 仅在UseSandbox=FALSE（默认）且Region=US（默认）时 |
| www-us2.api.concursolutions.com | 仅在UseSandbox=FALSE（默认）且Region=US（默认）时 - OAuth 授权 URL |
| eu2.api.concursolutions.com | 仅在UseSandbox=FALSE（默认）且Region=EU时 |
| www-eu2.api.concursolutions.com | 仅在UseSandbox=FALSE（默认）且Region=EU时 - OAuth 授权 URL |
| cn.api.concurcdc.cn | 仅在UseSandbox=FALSE（默认）且Region=CN时 |
| www-cn.api.concurcdc.cn | 仅在UseSandbox=FALSE（默认）且Region=CN时 - OAuth 授权 URL |
| us-impl.api.concursolutions.com | 仅在UseSandbox=TRUE且Region=US（默认）时 |
| www-us-impl.api.concursolutions.com | 仅在UseSandbox=TRUE且Region=US（默认）时 - OAuth 授权 URL |
| emea-impl.api.concursolutions.com | 仅在UseSandbox=TRUE且Region=EU时 |
| www-emea-impl.api.concursolutions.com | 仅在UseSandbox=TRUE且Region=EU时 - OAuth 授权 URL |
| <GeoLocation> | 仅在UseNewOAuthVersion=FALSE时 - GeoLocation 属性（除非设置了 OAuthAccessToken，否则自动检索） |
| <ConcurInstanceURL> | 仅用于较旧的 API 版本（API v1-3） |
| concursolutions.com | 仅在UseNewOAuthVersion=FALSE且 GeoLocation 为空且 ConcurInstanceURL 为空时 |
