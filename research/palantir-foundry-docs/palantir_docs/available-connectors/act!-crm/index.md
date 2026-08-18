来源: https://palantir.com/docs/zh/foundry/available-connectors/act!-crm/

# Act! CRM

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Act! CRM

Act! CRM 连接器是一个Palantir 提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标 IP 地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出站策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| <URL> | 始终。URL 连接属性（以下 URL 仍需在 URL 字段中输入） |
| apius.act.com | 仅当ActEdition='ActPremium Cloud' 且ActCloudRegion='US'时 |
| apiuk.act.com | 仅当ActEdition='ActPremium Cloud' 且ActCloudRegion='UK'时 |
| apiau.act.com | 仅当ActEdition='ActPremium Cloud' 且ActCloudRegion='AUS'或 'NZ' 时 |
| apieu.act.com | 仅当ActEdition='ActPremium Cloud' 且ActCloudRegion='EU'或 'InternationalEnglish' 时 |
