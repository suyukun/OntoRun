来源: https://palantir.com/docs/zh/foundry/available-connectors/odata/

# OData

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# OData

OData 连接器是一个Palantir 提供的驱动连接器。此驱动的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标 IP 地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| <URL> | 始终。URL 连接属性 |
| <FeedURL> | 仅 FeedURL 连接属性 |
| login.microsoftonline.com | 仅当AuthScheme=AzureAD或 SharePointOnline 且SharePointUseSSO=FALSE时 |
| <SharePointSSODomain> | 仅当SharePointUseSSO=TRUE且AuthScheme=SharePointOnline且用户的域与 SSO 服务的域不同时 |
| <KerberosKDC>:88 | 仅当AuthScheme=Negotiate时 |
| <KerberosServiceKDC>:88 | 仅当AuthScheme=Negotiate且 Kerberos 拓扑使用多个领域时 |
| <OAuthAuthorizationURL> | 仅当AuthScheme=OAuth时 |
| <OAuthAccessTokenURL> | 仅当AuthScheme=OAuth时 |
| <OAuthRefreshTokenURL> | 仅当AuthScheme=OAuth时 |
| <OAuthRequestTokenURL> | 仅当AuthScheme=OAuth时 |
