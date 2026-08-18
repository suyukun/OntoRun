来源: https://palantir.com/docs/zh/foundry/available-connectors/zoho-creator/

# Zoho Creator

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Zoho Creator

Zoho Creator 连接器是一个由Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域 | 必需 |
| --- | --- |
| <APIDomain> - 默认: creatorapp.zoho.<Region> | 总是。区域连接属性映射到顶级域名（默认Region=US--> .com）；在手动设置OAuthAccessToken时可以使用APIDomain |
| <AccountsServer> - 默认: accounts.zoho.<Region> | 总是。通过OAuth流程自动检索；在手动提供OAuthAccessToken时设置于AccountsServer连接属性中 |

### 区域映射

使用以下区域映射完成域URL：

| 区域 | 终端 |
| --- | --- |
| 美国 | .com |
| 欧洲 | .eu |
| 印度 | .in |
| 澳大利亚 | .com.au |
| 日本 | .jp |
| 中国 | .com.cn |
