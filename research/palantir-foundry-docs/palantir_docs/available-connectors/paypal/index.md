来源: https://palantir.com/docs/zh/foundry/available-connectors/paypal/

# PayPal

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# PayPal

PayPal连接器是一个Palantir提供的驱动程序连接器。此驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| api-3t.paypal.com | 仅当Schema=SOAP（默认）且UseSandbox=FALSE（默认）时 |
| api.paypal.com | 仅当Schema=REST且UseSandbox=FALSE（默认）时 |
| paypal.com | 仅当Schema=REST且UseSandbox=FALSE（默认）时 |
| api-3t.sandbox.paypal.com | 仅当Schema=SOAP（默认）且UseSandbox=TRUE时 |
| api.sandbox.paypal.com | 仅当Schema=REST且UseSandbox=TRUE时 |
| sandbox.paypal.com | 仅当Schema=REST且UseSandbox=TRUE时 |
