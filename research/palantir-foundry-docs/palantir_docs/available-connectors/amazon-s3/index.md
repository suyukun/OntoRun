来源: https://palantir.com/docs/zh/foundry/available-connectors/amazon-s3/

# Amazon S3

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Amazon S3

将Foundry连接到AWS S3，以读取和同步S3与Foundry之间的数据。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 通用可用 |
| 批量导入 | 🟢 通用可用 |
| 增量 | 🟢 支持的文件格式通用可用 |
| 媒体集 | 🟢 通用可用 |
| 虚拟表 | 🟢 通用可用 |
| 文件导出 | 🟢 通用可用 |

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择**+ 新来源**。
- 从可用的连接器类型中选择S3。
- 选择使用通过互联网的直接连接或通过中介代理连接。
- 按照下面各节中的信息，遵循附加的配置提示以继续设置您的连接器。
了解更多有关在Foundry中设置连接器的信息。

## 连接详情

| 选项 | 必须吗？ | 描述 |
| --- | --- | --- |
| URL | 是 | S3桶的URL。数据连接支持s3a协议。应包含结尾斜杠。有关更多详细信息，请参阅AWS的官方文档 ↗。例如：s3://bucket-name/ |
| Endpoint | 是 | 用于访问S3的端点。例如：s3.amazonaws.com或s3.us-east-1.amazonaws.com |
| Region | 否 | 配置AWS服务时使用的AWS区域。当使用STS角色时，这是必需的。警告：同时提供区域和包含区域的S3端点可能会导致失败。例如：us-east-1或eu-central-1 |
| Network connectivity | 是 - 仅适用于直接连接 | 步骤1: Foundry出口策略为桶附加一个Foundry出口策略，以允许Foundry出口到S3。数据连接应用程序根据提供的连接详细信息建议适当的出口策略。例如：bucket-name.s3.us-east-1.amazonaws.com (Port 443)步骤2: AWS桶策略此外，您需要将相关的Foundry IP和/或桶详细信息列入白名单，以便从S3访问。您的Foundry IP详细信息可以在控制面板应用程序的网络出口下找到。有关如何在S3中配置桶策略的更多详细信息，请参阅官方AWS文档 ↗。注意：设置与您的Foundry注册在同一区域托管的S3桶的访问需要额外的配置。阅读更多关于这些要求的信息，请参阅网络出口文档。 |
| Client certificates & private key | 否 | 客户端证书和私钥可能是必需的，也可能不是，用于保护连接。 |
| Server certificates | 否 | 服务器证书可能是必需的，也可能不是，用于保护连接。 |
| Credentials | 是 | 选项1: 访问密钥和密钥提供用于连接S3的访问密钥ID和密钥。可以通过在您的AWS账户中为Foundry创建一个新的IAM用户来生成凭证，并授予该IAM用户对S3桶的访问权限。选项2: OpenID Connect (OIDC)按照显示的源系统配置说明设置OIDC。有关OpenID Connect的详细信息，请参阅官方AWS文档 ↗和我们的文档以了解OIDC如何与Foundry一起工作。有关创建AWS IAM用户的更多详细信息，请参阅官方AWS文档 ↗。查看我们的S3文档权限以了解Foundry期望用户具备的AWS权限。 |
| STS role | 否 | S3连接器可以选择性地假定安全令牌服务(STS)角色 ↗以连接到S3。有关更多详细信息，请参阅STS角色配置。 |
| Connection timeout | 否 | 在最初建立连接时等待的时间（以毫秒为单位），在放弃和超时之前。默认：50000 |
| Socket timeout | 否 | 在已建立的开放连接上传输数据时等待的时间（以毫秒为单位），在连接超时并关闭之前。默认：50000 |
| Max connections | 否 | 允许的最大开放HTTP连接数。默认：50 |
| Max error retries | 否 | 失败的可重试请求（例如：来自服务的5xx错误响应）的最大重试次数。默认：3 |
| Client KMS key | 否 | 使用AWS SDK执行客户端数据加密的KMS密钥名称或别名。在PCloud中使用此选项需要代理更改。 |
| Client KMS region | 否 | 用于KMS客户端的AWS区域。仅在提供AWS KMS密钥时相关。 |
| Match subfolder exactly | 否 | 可选地将子文件夹下指定的路径与S3中的确切子文件夹匹配。如果设置为false，则s3://bucket-name/foo/bar/和s3://bucket-name/foo/bar_baz/都将与子文件夹设置foo/bar/匹配。 |
| Proxy configurations | 是 - 仅适用于基于代理的连接 | 配置S3的代理设置。注意：如果(a)您的Foundry注册托管在AWS中，(b)您连接到的S3桶托管在与您的Foundry注册不同的AWS区域，并且(c)您通过数据连接代理进行连接，则这是必需的。有关更多详细信息，请参阅S3代理配置。 |
| Enable path style access | 否 | 使用路径样式访问URL（例如，https://s3.region-code.amazonaws.com/bucket-name/key-name）而不是虚拟托管样式访问URL（例如，https://bucket-name.s3.region-code.amazonaws.com/key-name）。有关更多详细信息，请参阅官方AWS文档 ↗。 |
| Catalog | 否 | 配置此S3桶中存储的表的目录。有关更多详细信息，请参阅虚拟表。 |

## S3的必需读取和同步权限

以下AWS权限是S3桶交互式探索所必需的：

```
Copied!1
2
3
4
5
{
    "Action": ["s3:ListBucket"], // 操作：列出S3存储桶中的对象
    "Resource": ["arn:aws:s3:::path/to/bucket"], // 资源：指定存储桶的ARN（Amazon资源名称）
    "Effect": "Allow", // 效果：允许执行指定的操作
}
```

以下AWS权限是从S3进行批量同步、虚拟表和媒体同步所需的：

```
Copied!1
2
3
4
5
{
    "Action": ["s3:GetObject"],  // 指定的动作是从S3中获取对象
    "Resource": ["arn:aws:s3:::path/to/bucket/*"],  // 指定的资源是S3桶中的路径
    "Effect": "Allow",  // 允许上述动作的效果
}
```

请参阅关于 Amazon S3 中策略和权限的官方 AWS 文档 ↗，了解有关如何在 S3 中配置桶策略的更多详细信息。

## S3 代理配置（基于代理的连接）

使用数据连接代理连接到 S3 时，可以通过两种方式定义代理设置：

- 源配置：直接在源配置中定义每个代理设置，如下表所述。
- 代理的系统属性：作为后备，您可以在代理的系统属性中配置代理设置。为此，请在代理的高级配置设置中包含适当的 JVM 参数（例如，-Dhttps.proxyHost=example.proxy.com）。
| 参数 | 必填？ | 默认值 | 描述 |
| --- | --- | --- | --- |
| host | Y |  | HTTP 代理主机（无方案）。 |
| port | Y |  | HTTP 代理的端口。 |
| protocol | N | HTTPS | 使用的协议。可以是HTTPS或HTTP。 |
| nonProxyHosts | N |  | 不应使用代理的主机名列表（或通配符域名）。例如：`*.s3-external-1.amazonaws.com |
| credentials | N |  | 如果您的代理需要基本 HTTP 身份验证（由HTTP 407 响应 ↗触发），请包含此块。 |
| credentials.username | N |  | HTTP 代理的明文用户名。 |
| credentials.password | N |  | HTTP 代理的加密密码。 |

## STS 角色配置

STS 角色配置允许您使用AWS Security Token Service ↗在从 S3 读取时假设一个角色。

| 参数 | 必填？ | 默认值 | 描述 |
| --- | --- | --- | --- |
| roleArn | Y |  | STS 角色 ARN 名称。 |
| roleSessionName | Y |  | 假设此角色时使用的会话名称。 |
| roleSessionDuration | N | 3600 秒 | 会话持续时间。 |
| externalId | N |  | 假设角色时使用的外部 ID。 |

## 云身份配置

云身份认证允许 Foundry 访问您 AWS 实例中的资源。云身份在控制面板的注册级别进行配置和管理。了解如何配置云身份。

使用云身份认证时，角色 ARN 将显示在凭证部分。选择Cloud identity凭证选项后，还必须配置以下内容：

- 在目标 Amazon AWS 账户中配置一个身份和访问管理 (IAM) 角色。
- 授予 IAM 角色访问您希望连接的 S3 桶的权限。您通常可以使用桶策略 ↗来实现这一点。
- 在 S3 源配置详细信息中，在Security Token Service (STS) 角色 ↗配置下添加 IAM 角色。在访问 S3 时，Foundry 中的云身份 IAM 角色将尝试假设AWS 账户 IAM 角色 ↗。
- 配置相应的信任策略 ↗，以允许云身份 IAM 角色假设目标 AWS 账户 IAM 角色。
## 虚拟表

本节提供有关使用来自 S3 源的虚拟表的更多详细信息。在同步到 Foundry 数据集时，本节不适用。

| 虚拟表功能 | 状态 |
| --- | --- |
| 源格式 | 🟢 普遍可用：Avro ↗、Delta ↗、Iceberg ↗、Parquet ↗ |
| 手动注册 | 🟢 普遍可用 |
| 自动注册 | 🔴 不可用 |
| 下推计算 | 🔴 不可用 |
| 增量管道支持 | 🟢 Delta 表普遍可用：仅限APPEND（详情）🟢 Iceberg 表普遍可用：仅限APPEND（详情）🔴 Parquet 表不可用 |

注册虚拟表时，请记住以下源配置要求：

- 您必须将源设置为直接连接。虚拟表不支持使用中介代理。
- 确保已根据连接详细信息中的网络连接部分建立双向连接和白名单。
- 如果在代码库中使用虚拟表，请参阅虚拟表文档以获取所需的其他源配置详细信息。
- 如果您的桶包含.，您必须启用路径样式访问并设置适当的出口策略。
请参阅上述连接详细信息部分以获取更多详细信息。

### Delta

要启用由虚拟表支持的管道的增量支持，请确保在源 Delta 表上启用了更改数据馈送 ↗。在Python 变换中支持current和added读取模式。_change_type、_commit_version和_commit_timestamp列将在 Python 变换中可用。

### Iceberg

需要 Iceberg 目录来加载由 Apache Iceberg 表支持的虚拟表。要了解有关 Iceberg 目录的更多信息，请参阅Apache Iceberg 文档 ↗。在源上注册的所有 Iceberg 表都必须使用相同的 Iceberg 目录。

默认情况下，表将使用 S3 中的 Iceberg 元数据文件创建。在注册表时，必须提供指示这些元数据文件位置的warehousePath。

AWS Glue ↗可以用作存储在 S3 中的表的 Iceberg 目录。要了解有关此集成的更多信息，请参阅AWS Glue 文档 ↗。在源上配置的凭证必须有权访问您的 AWS Glue 数据目录。AWS Glue 可以在源上的连接详细信息选项卡中进行配置。在此源上注册的所有 Iceberg 表将自动使用 AWS Glue 作为目录。表应使用database_name.table_name命名模式注册。

Unity Catalog ↗可以在 Databricks 中使用 Delta Universal Format (UniForm) 时用作 Iceberg 目录。要了解有关此集成的更多信息，请参阅Databricks 文档 ↗。与 AWS Glue 一样，可以在源上的连接详细信息选项卡中配置目录。您需要提供端点和个人访问词元以连接到 Unity Catalog。表应使用catalog_name.schema_name.table_name命名模式注册。

增量支持依赖于 Iceberg增量读取 ↗，目前仅支持追加。支持在Python 变换中的current和added读取模式。

### Parquet

使用 Parquet 的虚拟表依赖于模式推断。最多将使用 100 个文件来确定模式。

## 以 S3 格式导出数据

要导出到 S3，首先为您的 S3 连接器启用导出。然后，创建一个新的导出。

## S3 所需的导出权限

导出数据到 S3 需要以下 AWS 权限：

```
Copied!1
2
3
4
5
{
    "Action": ["s3:PutObject"], // 指定允许执行的操作，这里是将对象上传到 S3 存储桶中
    "Resource": ["arn:aws:s3:::path/to/bucket/*"], // 指定可以操作的资源，这里是特定存储桶路径下的所有对象
    "Effect": "Allow", // 指定策略的效果，这里是允许执行指定的操作
}
```

请参阅AWS 官方文档关于 Amazon S3 中的策略和权限 ↗，以获取有关如何配置 S3 中存储桶策略的更多详细信息。

### 以配置导出选项

| 选项 | 必填？ | 默认值 | 描述 |
| --- | --- | --- | --- |
| Path Prefix | 否 | N/A | 应用于导出文件的路径前缀。导出文件的完整路径计算为s3://<bucket-name>/<path-in-source-config>/<path-prefix>/<exported-file> |
| Canned ACL | 否 | N/A | 设置附加到上传文件的 AWS 访问控制列表 (ACL)，使用其中一个预设的 ACL。有关每个 ACL 的描述，请参阅AWS 文档 ↗。 |
