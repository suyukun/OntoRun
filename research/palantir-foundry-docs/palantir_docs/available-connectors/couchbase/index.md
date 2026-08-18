来源: https://palantir.com/docs/zh/foundry/available-connectors/couchbase/

# Couchbase

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Couchbase

Couchbase 连接器是一个由 Palantir 提供的驱动程序连接器。此驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标 IP 地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| <Server> | 仅当ConnectionMode=Direct（默认）时；服务器连接属性。可以是 IP 地址或 HTTP/S URL。可以接受多个 URL |
| <DNSServer> | 仅当ConnectionMode=Cloud时，DNS 服务器用于查找服务器地址（默认端口为 53，端口可以通过 <Server>:<Port> 传递，但不是必需的） |
| <N1QLPort> | 仅当ConnectionMode=Direct且CouchbaseServer=N1QL时，端口默认为 SSL 为 18093，非 SSL 为 8093 |
| <AnalyticsPort> | 仅当ConnectionMode=Direct且CouchbaseServer=Analytics时，端口默认为 SSL 为 18095，非 SSL 为 8095 |
| <WebConsolePort> | 仅当ConnectionMode=Direct时，端口默认为 SSL 为 18091，非 SSL 为 8091 |
