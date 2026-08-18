来源: https://palantir.com/docs/zh/foundry/available-connectors/zoho-books/

# Zoho Books

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Zoho Books

Zoho Books 连接器是一个Palantir 提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够访问目标 IP 地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器：

| 域名 | 必需 |
| --- | --- |
| <AccountsServer> - 默认: books.zoho.<Region> | 始终。设置在 AccountsServer 连接属性中 |
| accounts.zoho.<Region> | 始终 |

### 区域映射

使用以下区域映射完成域名 URL：

| 区域 | 端点 |
| --- | --- |
| US | .com |
| Europe | .eu |
| India | .in |
| Australia | .com.au |
| Japan | .jp |
