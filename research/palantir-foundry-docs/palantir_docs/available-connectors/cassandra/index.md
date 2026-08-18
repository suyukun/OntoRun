来源: https://palantir.com/docs/zh/foundry/available-connectors/cassandra/

# Cassandra

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Cassandra

Cassandra 连接器是一个由Palantir提供的驱动连接器。此驱动的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须被配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| <Server>:<Port> | 仅当UseSSH=FALSE（默认），服务器和端口连接属性（默认：localhost:9042） |
| <LDAPServer>:<LDAPPort> | 仅当AuthScheme=LDAP（默认Port=389) |
| <SSHServer>:<SSHPort> | 仅当UseSSH=TRUE（默认Port=22) |
| <KerberosKDC>:88 | 仅当AuthScheme=Kerberos |
| <KerberosServiceKDC>:88 | 仅当AuthScheme=Kerberos且 Kerberos 拓扑使用多个领域 |
