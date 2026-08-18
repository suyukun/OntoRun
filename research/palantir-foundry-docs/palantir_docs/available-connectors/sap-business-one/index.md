来源: https://palantir.com/docs/zh/foundry/available-connectors/sap-business-one/

# SAP Business One

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SAP Business One

SAP Business One连接器是一个Palantir提供的驱动连接器。此驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域 | 必需 |
| --- | --- |
| <URL> | 始终。URL连接属性；默认格式URL='http://[server]:[port]/b1s/[version]' |
