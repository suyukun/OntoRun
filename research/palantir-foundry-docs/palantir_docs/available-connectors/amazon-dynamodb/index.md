来源: https://palantir.com/docs/zh/foundry/available-connectors/amazon-dynamodb/

# Amazon DynamoDB

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Amazon DynamoDB

Amazon DynamoDB连接器是一个由Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| dynamodb.<AWSRegion>.<domain> | 始终。AWSRegion 映射 |
| sts.<Region>.amazonaws.<TLD> | 仅当AuthScheme=AwsIAMRoles,AwsMFA,TemporaryCredentials |
| cognito-idp.<AWSCognitoRegion>.amazonaws.<TLD> | 仅当AuthScheme=AwsCognitoBasic,AwsCognitoSrp |
| cognito-identity.<AWSCognitoRegion>.amazonaws.<TLD> | 仅当AuthScheme=AwsCognitoBasic,AwsCognitoSrp |
| <SSOLoginURL> | 仅当AuthScheme=Okta,ADFS,PingFederate,使用SSOLoginURL属性 |
| <Resource> | 仅当AuthScheme=AzureAD,在SSOProperties中设置Resource |
| <SSOExchangeURL> | 仅当AuthScheme=Okta |
