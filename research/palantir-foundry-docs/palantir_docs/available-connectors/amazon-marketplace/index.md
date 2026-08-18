来源: https://palantir.com/docs/zh/foundry/available-connectors/amazon-marketplace/

# Amazon Marketplace

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Amazon Marketplace

Amazon Marketplace连接器是一个Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| sts.<AWSRegion>.amazon.com | 仅当Schema=SellingPartner,AWSRegion 映射 |
| sellingpartnerapi-<AWSRegion>.amazon.com | 仅当Schema=SellingPartner,SellingPartner 映射 |
| sandbox.sellingpartnerapi-<AWSRegion>.amazon.com | 仅当Schema=SellingPartner和UseSandbox=True,SellingPartner 沙盒映射 |
| mws.amazonservices.<Marketplace> | 仅当Schema=Marketplace,AWSMarketplace 映射 |
| api.amazon.com | 仅当使用OAuth时 |
| Seller Central URLs | 仅当使用OAuth时 |
| oa.cdata.com | 仅当使用嵌入式CData OAuth凭据时 |
