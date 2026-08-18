来源: https://palantir.com/docs/zh/foundry/available-connectors/postgresql/

# PostgreSQL

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# PostgreSQL

将 Foundry 连接到PostgreSQL ↗，以读取和同步 PostgreSQL 数据库与 Foundry 之间的数据。此连接器使用主版本42的官方 PostgreSQL 驱动程序 ↗，兼容 PostgreSQL 8.2 及以上版本的所有版本。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 通常可用 |
| 批量同步 | 🟢 通常可用 |
| 增量 | 🟢 通常可用 |
| 更改数据捕获同步 | 🟡 Beta |
| 流式导出 | 🟡 Beta |

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择+ 新建源。
- 从可用的连接器类型中选择PostgreSQL。
- 选择通过互联网使用直接连接或通过代理运行时进行连接。
- 根据以下部分中的信息，按照其他配置提示继续设置连接器。
了解有关在 Foundry 中设置连接器的更多信息。

## 认证

Foundry PostgreSQL 连接器需要使用用户名和密码进行认证。我们建议使用服务凭证而不是个人用户凭证。

用户名和密码认证可以与客户端和/或服务器证书以及需要验证这些证书的 SSL 模式结合使用。

您必须确保提供的用户在目标数据库上具有必要的权限，并且有权限读取或写入目标表。在更改数据捕获的情况下，用户还可能需要在目标数据库上具有CREATE和REPLICATION权限。

## 网络

PostgreSQL 连接器需要访问您希望连接的数据库实例的网络。PostgreSQL 连接通常使用主机名或 IP 在端口 5432 上进行连接。

要启用 Foundry 到 PostgreSQL 的直接连接，必须在数据连接应用程序中设置源时添加适当的出口策略。

对于通过互联网访问的云托管 PostgreSQL 实例，例如 Amazon Relational Database Service (RDS) 中的 PostgreSQL，您必须为数据库的主机名或如果您未使用主机名则为 IP 地址添加出口策略。查看您所托管的云托管 PostgreSQL 实例提供商的官方文档，以获取有关所需网络配置的更多详细信息。

您需要确保已允许从 Foundry 到您的 PostgreSQL 实例的入站流量。您可以在控制面板的网络出口页面中查看流量从 Foundry 发出的出口 IP。查看您的托管提供商的文档，了解如何允许这些 IP 的流量到您的数据库实例。

如果您正在使用代理运行时连接，您必须确保代理主机已向主机名、IP 地址和端口开放防火墙，以连接到您的 PostgreSQL 数据库。

### Amazon RDS 中的 PostgreSQL

如果您正在连接到在 Amazon RDS 中托管的 PostgreSQL 托管实例，您可以使用具有必要出口策略的直接连接运行时。

- 要查找托管在 Amazon RDS 中的 PostgreSQL 实例的主机名，请在 AWS 控制台中导航到您的实例。RDS PostgreSQL 的基于主机名的出口策略示例如<your-database-name>.<unique-identifier>.<region>.rds.amazonaws.com (port 5432)
当连接到 RDS PostgreSQL 实例时，您可能需要在源配置面板中将 RDS 根证书颁发机构 (CA) 作为服务器证书添加。下载rds-ca-2019-root.pem从Amazon S3 站点 ↗，然后将证书详细信息复制到 Foundry 以信任与 Amazon RDS 的连接。有关使用 SSL/TLS 连接到 RDS 数据库实例的更多信息，请查看官方AWS 文档 ↗。

## 连接详情

| 选项 | 是否必需? | 描述 |
| --- | --- | --- |
| Host type | 是 | 指定 Foundry 应如何连接到您的 PostgreSQL 数据库。选项 1: 主机名提供一个主机名。这是所有 PostgreSQL 连接的推荐选项，并且在连接到云托管的 PostgreSQL 实例时应始终使用。例如，在Amazon RDS ↗中托管的实例。选项 2: IPv4提供一个 IPv4 地址。如果您通常使用 IPv4 地址连接，无论是在企业网络内还是通过互联网，则可以使用此选项。选项 3: IPv6提供一个 IPv6 地址。如果您通常使用 IPv6 地址连接，请使用此选项。 |
| Port | 是 | 指定连接时使用的端口。大多数 PostgreSQL 实例的默认端口为5432。有关端口的更多信息，请参见 PostgreSQL 的官方文档 ↗以及您的数据库实例的配置。 |
| Database name | 是 | 您在 PostgreSQL 实例中连接到的数据库名称。 |
| Authentication | 是 | 使用上面显示的认证指南进行配置。 |
| Network Connectivity | 是 | 您必须提供一个网络连接到您的 PostgreSQL 实例的运行时。对于企业防火墙后面的实例，通常需要使用代理运行时。对于云托管实例，请参阅网络部分以获取更多详细信息。 |
| SSL Mode | 是 | 默认设置为verify-full。有关更多详细信息，请查看 PostgreSQL JDBC 驱动程序上ssl-mode连接参数的官方文档 ↗。 |

## 更改数据捕获 [Beta]

PostgreSQL 的更改数据捕获同步处于 beta 状态。联系 Palantir 客服支持以访问此功能。

PostgreSQL 源支持更改数据捕获(CDC) 同步。

由于 PostgreSQL 支持逻辑复制，更改数据捕获可以将更改流式传输到配置的表中，几乎实时更新。根据PostgreSQL 文档 ↗:

> 逻辑复制是一种基于其复制标识（通常是主键）复制数据对象及其更改的方法。

逻辑复制是一种基于其复制标识（通常是主键）复制数据对象及其更改的方法。

Foundry 从 PostgreSQL 的更改数据捕获同步通过使用现有复制槽或在目标数据库上创建新的复制槽和发布来实现。每个数据连接源只能配置一个复制槽和发布，然而任何数量的表都可以通过单个连接流式传输到 Foundry。如果您希望使用多个复制槽或发布，您可以创建多个连接到您数据库的数据连接源。

在设置更改数据捕获同步之前，首先确保您有一个正常工作的 PostgreSQL 源连接。然后，导航到CDC 同步选项卡，并提供更改数据捕获所需的其他配置。

| 选项 | 是否必需? | 描述 |
| --- | --- | --- |
| 复制槽名称 | 是 | 用于 CDC 的复制槽的名称。如果槽不存在，将自动创建。有关更多信息，请参见PostgreSQL 官方文档 ↗。 |
| 发布名称 | 是 | 用于 CDC 的发布的名称。有关更多信息，请参见PostgreSQL 官方文档 ↗。 |
| 自动创建发布 | 是 | 如果启用，将为所有选定表自动创建发布。这要求用户在数据库上具有以下权限：CREATE和REPLICATION，以及对表的SELECT权限。 |

配置更改数据捕获所需的设置后，您可以导航到概览页面或停留在CDC 同步页面，选择+ 创建 CDC 同步以创建新的更改数据捕获同步。

探索运行时必须正常工作才能创建更改数据捕获同步。如果运行时仍在初始化，您可能需要等待几秒钟并刷新页面以继续创建更改数据捕获同步。

有关在 PostgreSQL 中使用 CDC 的更多信息，请查看您所使用的 PostgreSQL 版本的逻辑复制官方文档 ↗。
