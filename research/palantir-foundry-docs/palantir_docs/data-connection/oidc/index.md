来源: https://palantir.com/docs/zh/foundry/data-connection/oidc/

# OpenID Connect (OIDC) 身份验证

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# OpenID Connect (OIDC) 身份验证

OpenID Connect (OIDC) ↗，也称为OIDC，是一种开放的身份验证协议，允许您在不使用静态凭据的情况下对外部源资源进行身份验证。

使用OIDC时，您无需在Foundry中为源系统配置凭据。因此，您可以避免将源系统凭据复制为Foundry中的长期机密。相反，您将配置Foundry与源系统之间的信任关系。Foundry充当OIDC身份提供者；每当Foundry中的工作流程需要与源系统进行身份验证时（例如，数据连接同步），Foundry将签发一个包含识别所用数据连接源声明的OIDC词元。源系统能够验证这些声明，并提供一个可用于与源系统后续交互的短期访问词元。该访问词元的范围，例如它被允许访问的资源，完全在源系统中使用可用的本地身份验证和授权工具进行管理。在配置信任关系时，您可以添加条件以筛选传入请求。不受信任的Foundry源无法请求访问它们不应访问的源系统资源的访问词元。

## 支持的来源

以下来源支持OIDC身份验证。有关如何在OIDC和Palantir之间设置信任关系的更多详细信息，请参阅各个来源的文档。

- Azure Data Lake Storage Gen2 (Azure Blob Storage)
- BigQuery
- Google Cloud Storage
- S3
- Snowflake
## OIDC身份词元

以下是Foundry生成的OIDC词元示例：

```
Copied!1
2
3
4
5
6
7
8
9
10
{
  "iss": "https://pltroidcpublicexample.blob.store.com/foundry",  // 签发者，表示签发该令牌的实体
  "sub": "ri.magritte..source.7f3b8e21-4d9a-6c2e-1b7d-8a5f3c9e0b4f",  // 主题，表示令牌所指代的主体
  "aud": "your-source-system-audience",  // 受众，表示令牌的预期接收者
  "iat": <issued-at>,  // 签发时间，表示令牌的签发时间
  "nbf": <not-before>,  // 生效时间，表示令牌在此时间之前无效
  "exp": <expiry>,  // 过期时间，表示令牌的过期时间
  "jti": "<token-unique-identifier>",  // 令牌唯一标识符，防止令牌重放攻击
  "scp": "<additional-scope>",  // 额外的权限范围
}
```

| Claim | 声明类型 | 描述 |
| --- | --- | --- |
| iss | 发行者网址 | 用于标识 Foundry 作为 OIDC 身份提供商的 URL。 |
| sub | 主体 | 连接到您的源系统的 Foundry 源的源 RID。 |
| aud | 受众 | 标识您的源系统的已配置受众。 |

应该使用source-rid来筛选传入的请求，以便不受信任的 Foundry 源无法访问您的资源。

Foundry 生成的 OIDC 词元在一小时后过期。
