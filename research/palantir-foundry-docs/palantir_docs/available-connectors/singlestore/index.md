来源: https://palantir.com/docs/zh/foundry/available-connectors/singlestore/

# SingleStore

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SingleStore

SingleStore连接器是一个Palantir提供的驱动连接器。该驱动的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域 | 必需 |
| --- | --- |
| <Server>:<Port> | 仅当UseSSH=FALSE,服务器支持列出多个地址时（即，Server='192.168.1.100,192.168.1.101'） |
| 无 | 始终。端口支持列出多个地址（即，Port='3306,3307'）；默认Port=3306 |
| <SSHServer>:<SSHPort> | 仅当UseSSH=TRUE,默认SSHPort=22 |
