来源: https://palantir.com/docs/zh/foundry/available-connectors/twilio/

# Twilio

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Twilio

Twilio连接器是一个Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| api.twilio.com | 始终 |
| sync.twilio.com | 仅用于ServiceLists和Services表 |
| insights.twilio.com | 仅用于CallSummary、CallEvents和CallMetrics视图 |
| conversations.twilio.com | 仅用于Conversation视图 |
