来源: https://palantir.com/docs/zh/foundry/available-connectors/zuora/

# Zuora

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Zuora

Zuora连接器是一个Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| rest.zuora.com | 仅当Tet=USProduction(默认) |
| rest.apisandbox.zuora.com | 仅当Tet=USAPISandbox |
| rest.pt1.zuora.com | 仅当Tet=USPerformanceTest |
| rest.eu.zuora.com | 仅当Tet=EUProduction |
| rest.sandbox.eu.zuora.com | 仅当Tet=EUSandbox |
| rest.na.zuora.com | 仅当Tet=USCloudProduction |
| rest.sandbox.na.zuora.com | 仅当Tet=USCloudAPISandbox |
| rest.test.zuora.com | 仅当Tet=USCentralSandbox |
| rest.test.eu.zuora.com | 仅当Tet=EUCentralSandbox |
| <URL> | 仅用于US Production复制环境的URL连接属性 |
