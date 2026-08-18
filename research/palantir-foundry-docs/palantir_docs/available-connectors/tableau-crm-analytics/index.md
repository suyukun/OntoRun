来源: https://palantir.com/docs/zh/foundry/available-connectors/tableau-crm-analytics/

# Tableau CRM 分析

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Tableau CRM 分析

Tableau CRM 分析连接器是一个Palantir 提供的驱动连接器。该驱动的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域 | 必需 |
| --- | --- |
| <InstanceURL> | 始终。由 Salesforce 在身份验证时返回；可以通过 InstanceURL 属性设置，当InitiateOAuth=OFF时 |
| login.salesforce.com | 仅当UseSandbox=FALSE且子域为空时 |
| test.salesforce.com | 仅当UseSandbox=TRUE时 |
| <Subdomain>.cloudforce.com | 仅当子域连接属性用于自定义品牌身份验证页面时 |
