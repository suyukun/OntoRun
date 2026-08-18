来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/troubleshooting-odbc-jdbc/

# 配置 ODBC 和 JDBC 驱动时的故障排除问题

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置 ODBC 和 JDBC 驱动时的故障排除问题

## "ODBC 出错 [IM003] 无法加载指定的驱动程序"

### 问题

在 Windows 上尝试使用 ODBC 驱动程序时会出现以下错误：

> ODBC: ERROR [IM003] Specified driver could not be loaded due to system error 126: The specified module could not be found. (FoundrySqlDriver, C:\Program Files\Palantir\Foundry ODBC Driver\bin64\<ModuleName>.dll)

ODBC: ERROR [IM003] Specified driver could not be loaded due to system error 126: The specified module could not be found. (FoundrySqlDriver, C:\Program Files\Palantir\Foundry ODBC Driver\bin64\<ModuleName>.dll)

### 解决方案

确保您在主机上安装了最新的Microsoft Visual C++ Redistributable ↗。

## "FoundrySqlServer:InvalidDatasetCannotAccess"

### 问题

在使用 ODBC 驱动、JDBC 驱动或 Palantir Foundry 的 BI 工具连接器运行 SQL 查询时会出现以下错误：

> FoundrySqlServer:InvalidDatasetCannotAccess

FoundrySqlServer:InvalidDatasetCannotAccess

### 解决方案

在 ODBC 连接中配置的用户账户可能没有权限查看查询中引用的数据集。

采取以下操作之一来验证访问权限：

- 使用相关用户账户登录 Foundry，导航到相关数据集，并确保可以按预期访问数据。
- 权限足够的个人可以按照检查权限指南中的说明，代表相关账户验证访问权限。
## "FoundrySqlServer:TooManyRows"

### 问题

在使用 ODBC 驱动、JDBC 驱动或 Palantir Foundry 的 BI 工具连接器运行 SQL 查询时会出现以下错误：

> FoundrySqlServer:TooManyRows

FoundrySqlServer:TooManyRows

### 解决方案

出于性能原因，某些 SQL 查询会受到行数限制。查看Foundry SQL Server 的执行引擎的文档，了解这些限制以及如何定义避免它们的查询。

## 使用自定义 SSL 证书的连接错误

### 问题

在尝试使用 JDBC 或 ODBC 驱动连接到 Foundry 时，您可能会遇到一个错误消息，表明驱动无法与 Foundry 建立安全连接。错误消息可能如下所示：

> Dialogue transport failure; PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target

Dialogue transport failure; PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target

此错误表示驱动在连接到您的 Foundry URL 时，无法验证服务器的 SSL 证书是由受信任的证书颁发机构 (CA) 签署的。当 CA 不为您的操作系统的信任库所知，或驱动无法访问操作系统信任库时，会出现这种情况。

您可能会在以下场景中遇到自定义 CA 和证书：

- 您的 Foundry URL 使用您组织的域名，而不是 Palantir 提供的域名（例如，foundry.[your-organization].com而不是[your-organization].palantirfoundry.com）。
- 您组织的网络配置为执行 TLS 解密/检查，这会导致驱动看到的证书与 Foundry 最初呈现的证书不同。
### 解决方案

确保驱动可以访问您组织使用的自定义证书链，使用以下方法之一。

#### 选项 1：将自定义证书链加载到您的操作系统信任库中

默认情况下，驱动在验证 SSL 证书时使用操作系统的默认信任库。联系您组织的 IT 支持，了解是否可以将您组织的自定义证书链添加到其中。如果可以，驱动将能够在无需任何额外配置的情况下验证与 Foundry 的连接。

#### 选项 2：手动提供 PEM 格式的自定义证书链

如果您的组织无法将自定义证书链加载到操作系统的默认信任库中，您可以手动向驱动提供证书链。为此，请获取 PEM 格式的证书链，并使用 JDBC 或 ODBC 驱动的TrustStorePath连接参数指定该文件的路径：

- 从可信连接中获取证书链。例如，如果您已经可以在 Google Chrome 中访问 Foundry，请按照以下说明将证书链导出为 PEM 格式。如果您使用不同的浏览器，请参阅浏览器的文档以获取导出证书链的说明。打开 Google Chrome 并在新标签页中打开您的 Foundry URL。选择地址栏中的挂锁图标，选择连接是安全的，然后选择证书是有效的。如果 Chrome 报告连接不安全和/或证书无效，可能有其他问题导致计算机与 Foundry 的所有连接出现证书信任错误。请咨询您组织的 IT 支持和 Palantir 支持以获得帮助。选择详细信息选项卡。选择导出...。选择Base64 编码的 ASCII，证书链作为导出格式，并选择一个位置保存证书文件。选择保存。
从可信连接中获取证书链。例如，如果您已经可以在 Google Chrome 中访问 Foundry，请按照以下说明将证书链导出为 PEM 格式。如果您使用不同的浏览器，请参阅浏览器的文档以获取导出证书链的说明。

- 打开 Google Chrome 并在新标签页中打开您的 Foundry URL。
- 选择地址栏中的挂锁图标，选择连接是安全的，然后选择证书是有效的。
如果 Chrome 报告连接不安全和/或证书无效，可能有其他问题导致计算机与 Foundry 的所有连接出现证书信任错误。请咨询您组织的 IT 支持和 Palantir 支持以获得帮助。

- 选择详细信息选项卡。
- 选择导出...。
- 选择Base64 编码的 ASCII，证书链作为导出格式，并选择一个位置保存证书文件。选择保存。
- 通过指定TrustStorePath连接参数配置驱动以使用证书链。该属性的值应为您在上一步导出的文件的完整路径。请参阅ODBC & JDBC 驱动：连接参数以了解如何指定连接参数。
通过指定TrustStorePath连接参数配置驱动以使用证书链。该属性的值应为您在上一步导出的文件的完整路径。请参阅ODBC & JDBC 驱动：连接参数以了解如何指定连接参数。
