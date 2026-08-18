来源: https://palantir.com/docs/zh/foundry/available-connectors/basecamp/

# Basecamp

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Basecamp

Basecamp 连接器是一个由Palantir提供的驱动程序连接器。该驱动程序的官方文档可以在此处 ↗找到。

## 网络

如果使用代理连接，代理必须被允许连接到您选择的系统。这意味着代理必须能够到达目标IP地址，并且目标系统必须被配置为允许来自代理的连接。

如果使用直接连接，请确保向连接器添加以下出口策略：

| 域名 | 必需 |
| --- | --- |
| launchpad.37signals.com | 仅OAuth流程需要 - 不用于基本身份验证 |
| 3.basecampapi.com | 仅在连接到basecamp V3实例时需要 |
| basecamp.com | 仅在连接到basecamp V1/V2实例时需要 |
