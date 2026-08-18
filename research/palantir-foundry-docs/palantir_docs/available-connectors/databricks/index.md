来源: https://palantir.com/docs/zh/foundry/available-connectors/databricks/

# Databricks

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Databricks

连接Foundry到Databricks，以读取和同步Databricks与Foundry之间的数据。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 普遍可用 |
| 批量导入 | 🟢 普遍可用 |
| 增量 | 🟢 普遍可用 |

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择**+ 新建来源**。
- 从可用的连接器类型中选择Databricks。
- 选择通过互联网使用直接连接或通过中介代理进行连接。
- 按照附加配置提示，使用以下部分中的信息继续设置您的连接器。
了解有关在Foundry中设置连接器的更多信息。

### 配置选项

Databricks连接器提供以下配置选项：

| 选项 | 是否必需? | 描述 |
| --- | --- | --- |
| Hostname | 是 | Databricks计算资源的服务器主机名值。 |
| HTTP Path | 是 | Databricks计算资源的HTTP路径值。 |

请参考官方Databricks文档 ↗以获取有关如何获取这些值的信息。

### 认证

您可以通过以下方式认证到Databricks：

- 个人访问词元:使用个人访问词元以Databricks用户身份进行认证。更多信息请参见官方Databricks文档 ↗。
- OAuth 机器对机器 (M2M):使用客户端ID和密钥以Databricks服务主体进行认证。更多信息请参见官方Databricks文档 ↗。
- 基本:使用用户名和密码以Databricks用户身份进行认证。基本认证是遗留认证方式，不推荐在生产中使用。更多信息请参见官方Databricks文档 ↗。
### 网络

Databricks连接器需要对配置选项中提供的Hostname在端口443上的网络访问。如果您使用通过互联网的直接连接，请确保存在一个出口策略。对于代理运行时，运行代理的服务器必须能够访问该域。
