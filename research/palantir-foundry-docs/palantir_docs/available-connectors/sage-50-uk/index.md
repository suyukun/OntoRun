来源: https://palantir.com/docs/zh/foundry/available-connectors/sage-50-uk/

# Sage 50 UK

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Sage 50 UK

Sage 50 UK 连接器是一个由Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| <URL> | 始终。URL连接属性，示例：http://MySite:5493/sdata/accounts50/GCRM/MyDatasetId/ |
