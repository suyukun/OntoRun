来源: https://palantir.com/docs/zh/foundry/available-connectors/zoho-crm/

# Zoho CRM

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Zoho CRM

Zoho CRM连接器是一个Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保向连接器添加以下出口策略：

| 域名 | 必需 |
| --- | --- |
| <APIDomain> - 默认: zohoapis.<Region> | 始终。如果UseSandbox=FALSE（默认），Region连接属性映射到TLD（默认Region=US--> .com）；APIDomain可用于手动设置OAuthAccessToken时 |
| sandbox.zohoapis.<Region> | 仅当UseSandbox=TRUE时 |
| <AccountsServer> - 默认: accounts.zoho.<Region> | 始终。通过OAuth流程自动检索；手动提供OAuthAccessToken时在AccountsServer连接属性中设置 |

### 区域映射

使用以下区域映射来完成域名URL：

| 区域 | 终端 |
| --- | --- |
| 美国 | .com |
| 欧洲 | .eu |
| 印度 | .in |
| 澳大利亚 | .com.au |
| 日本 | .jp |
| 中国 | .com.cn |
