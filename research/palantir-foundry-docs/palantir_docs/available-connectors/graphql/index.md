来源: https://palantir.com/docs/zh/foundry/available-connectors/graphql/

# GraphQL

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# GraphQL

GraphQL连接器是一个由Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出站策略添加到连接器：

| 域名 | 必须 |
| --- | --- |
| <URL> | 始终 |
| <OAuthRequestTokenURL> | 仅当使用AuthScheme=OAuth和OAuthVersion=1.0时 |
| <OAuthAuthorizationURL> | 仅当使用AuthScheme=OAuth时 |
| <OAuthAccessTokenURL> | 仅当使用AuthScheme=OAuth时 |
| <OAuthRefreshTokenURL> | 仅当使用AuthScheme=OAuth和OAuthVersion=2.0时 |
| cognito-idp.<AWSCognitoRegion>.amazonaws.<TLD> | 仅当AuthScheme=AwsCognitoBasic,AwsCognitoSrp,AWSRegion Mappings时 |
| cognito-identity.<AWSCognitoRegion>.amazonaws.<TLD> | 仅当AuthScheme=AwsCognitoBasic,AwsCognitoSrp,AWSRegion Mappings时 |
