来源: https://palantir.com/docs/zh/foundry/available-connectors/ibm-cloud-object-storage/

# IBM Cloud Object Storage

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# IBM Cloud Object Storage

IBM Cloud Object Storage连接器是一个由Palantir提供的驱动连接器。该驱动的官方文档可以在这里 ↗找到。

## 网络

如果使用代理连接，则必须允许代理连接到您选择的系统。这意味着代理必须能够访问目标IP地址，并且目标系统必须配置为允许来自代理的连接。

如果使用直接连接，请确保将以下出口策略添加到连接器中：

| 域名 | 必需 |
| --- | --- |
| iam.bluemix.net | 始终 |
| resource-controller.cloud.ibm.com | 始终 |
| <Region>.cloud-object-storage.appdomain.cloud | 始终。区域连接属性被映射（也可能由IBM返回或是CRN的一部分） |
