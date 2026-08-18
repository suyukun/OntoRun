来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/odbc-jdbc-drivers/

# Foundry 数据集的 ODBC 和 JDBC 驱动程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Foundry 数据集的 ODBC 和 JDBC 驱动程序

## 概述

Foundry 数据集的 ODBC 和 JDBC 驱动程序为从客户端应用程序（如 BI 工具和 ETL 工具）访问数据集提供了一个只读的基于 SQL 的接口。用户可以在 Foundry 中浏览项目和数据集，并执行 SQL 查询以访问表格数据。驱动程序利用服务器端的Foundry SQL 服务器来处理和执行 SQL 查询。

### JDBC 还是 ODBC？

在客户端应用程序支持这两种协议的情况下，我们推荐使用 JDBC。JDBC 驱动程序更容易安装和配置，数据加载性能更佳。

### Foundry SQL 服务器

驱动程序依赖 Foundry SQL 服务器来处理和执行针对 Foundry 数据集的 SQL 查询。查看Foundry SQL 服务器架构文档以了解有关架构的更多信息以及如何提高查询性能。

## 系统要求

### ODBC

| 操作系统 | 要求 |
| --- | --- |
| Windows | 64 位管理员权限安装最新的Microsoft Visual C++ Redistributable |

- 64 位
- 管理员权限
- 安装最新的Microsoft Visual C++ Redistributable
ODBC 驱动程序目前仅与 Windows 兼容。

### JDBC

| 操作系统 | 要求 |
| --- | --- |
| Windows | 最低 Java 版本：Java 11最高 Java 版本：Java 15 |
| macOS |
| Linux |

- 最低 Java 版本：Java 11
- 最高 Java 版本：Java 15
Java 16+ 在额外配置下被支持。有关更多详细信息，请参阅下面的指南。

## 设置指南

### ODBC

#### 第 1 部分：安装 ODBC 驱动程序

按照下载：ODBC 驱动程序中的说明运行 ODBC 驱动程序安装程序。

#### 第 2 部分：配置数据源名称 (DSN) 配置

要在客户端应用程序中使用驱动程序，首先为您的 Foundry 环境配置一个数据源名称 (DSN) 配置：

- 从开始菜单中，搜索ODBC并打开ODBC 数据源工具。选择 64 位版本。
- 在用户 DSN或系统 DSN选项卡上，点击添加...。
- 从驱动程序列表中选择FoundrySqlDriver。
- 输入以下必需参数：数据源名称：您计算机上的数据源名称。服务器：您的 Foundry 环境的 URL；例如https://<SUBDOMAIN>.palantirfoundry.com。词元：在 Foundry 内设置页面生成的安全词元。有关如何获取词元的说明，请参阅用户生成的词元文档。有关其他身份验证选项，请查看使用 OAuth 进行身份验证指南。
- 数据源名称：您计算机上的数据源名称。
- 服务器：您的 Foundry 环境的 URL；例如https://<SUBDOMAIN>.palantirfoundry.com。
- 词元：在 Foundry 内设置页面生成的安全词元。有关如何获取词元的说明，请参阅用户生成的词元文档。有关其他身份验证选项，请查看使用 OAuth 进行身份验证指南。
- 点击测试...以验证连接成功，然后点击确定以保存 DSN 配置。
有关其他配置参数和构建连接 URL 的说明，请参阅配置参数。

#### 第 3 部分：在客户端应用程序中配置 DSN

现在您已创建 DSN，您可以从支持 ODBC 源的客户端应用程序中引用它。请参阅客户端应用程序文档中的 ODBC 源。下面是与 Foundry 常用的一些应用程序的设置指南：

- Excel
- Power BI
- Microsoft Report Builder
#### （非必填）第 4 部分：执行 SQL 查询

如果客户端应用程序支持，测试一个从 Foundry 数据集返回行的 SQL 查询：

```
Copied!1
2
SELECT * FROM "/Path/To/Dataset" LIMIT 10
-- 从数据集 "/Path/To/Dataset" 中选择所有列，并限制返回结果为前10条记录
```

客户端应用程序可能允许您浏览项目并选择数据集以访问数据。

### JDBC

#### 第1部分：安装JDBC驱动

下载JDBC驱动（.jar文件），可以在下载：JDBC驱动页面找到。下载后，将文件放置在客户端应用程序文档中指定的用于配置JDBC连接的适当位置。

#### 第2部分：构建JDBC连接字符串

JDBC连接字符串格式为：

```
jdbc:foundrysql://<FOUNDRY_HOSTNAME>?Password=<TOKEN>
```

这是一个JDBC连接字符串，用于连接到Foundry SQL数据库。需要替换<FOUNDRY_HOSTNAME>为Foundry服务器的主机名，并将<TOKEN>替换为相应的访问令牌。

- FOUNDRY_HOSTNAME是您Foundry环境的主机名（例如subdomain.palantirfoundry.com）。
- TOKEN是从Foundry内部设置页面生成的安全词元。请参阅用户生成的词元文档以获取有关如何获取词元的说明。有关其他身份验证选项，请查看使用OAuth进行身份验证指南。
可以通过在连接字符串后附加&OptionalParam=<VALUE>来指定非必填参数。有关可用参数的完整列表，请参阅配置参数。

如果JDBC客户端需要显式指定驱动程序类，请指定com.palantir.foundry.sql.jdbc.FoundryJdbcDriver。

#### （非必填）第3部分：执行SQL查询

如果客户端应用程序支持，请测试从Foundry数据集返回行的SQL查询：
客户端应用程序可能允许您浏览项目并选择数据集以访问数据。

## 参考

### 配置参数

ODBC 和 JDBC 的可用配置参数相同。每个驱动程序可以通过两种方式之一进行配置：在客户端应用程序中使用连接字符串，或在客户端应用程序外进行配置：

|  | 使用连接字符串 | 在客户端应用程序外 |
| --- | --- | --- |
| ODBC | Driver=FoundrySqlDriver;BaseUrl=<FOUNDRY_HOSTNAME>;Pwd=<TOKEN>;OptionalParamOne=ABC;OptionalParamTwo=XYZ | 使用 Windows ODBC 数据源工具配置 DSN。请参阅第 2 部分。配置数据源名称 (DSN) 配置。 |
| JDBC | jdbc:foundrysql://<FOUNDRY_HOSTNAME>?Password=<TOKEN>&OptionalParamOne=ABC&OptionalParamTwo=XYZ | 使用foundry.ini config文件。请参阅使用 foundry.ini 配置文件配置 JDBC 驱动程序。 |

#### 参数参考

| 参数 | 连接字符串键 | 必填 | 描述 |
| --- | --- | --- | --- |
| Foundry URL | ODBCBaseUrl/ JDBC N/A | 是 | Foundry URL，例如https://<SUBDOMAIN>.palantirfoundry.com |
| 认证词元 | ODBCPwd/ JDBCPassword | 是 | 认证词元通过 Foundry UI 生成或通过OAuth 认证流程获取。 |
| 数据集分支 | Branch | 否 | 查询数据集的分支。如果未设置，则默认为master。 |
| 项目/目录 | Catalog | 否 | 将驱动程序显示的表限制为单个项目。设置为完整的项目路径，如/MyOrg/MyProject。设置此属性可以解决某些应用程序中的表浏览问题。 |
| 认证方法 | AuthMethod | 否 | 用于连接的认证方法。允许的值：Token（默认）、OauthFlow或ClientCredentials。有关使用基于 OAuth 的认证方法的指导，请参阅使用 OAuth 进行认证。 |
| OAuth 客户端 ID | OauthClientId | 否 | 在 Foundry 中注册并启用的第三方应用程序的客户端 ID。如果AuthMethod设置为OauthFlow或ClientCredentials，则必填。或者，可以在应用程序的用户名字段中设置。 |
| OAuth 客户端密钥 | OauthClientSecret | 否 | 在 Foundry 中注册并启用的第三方应用程序的客户端密钥。如果AuthMethod设置为ClientCredentials，则必填。或者，可以在应用程序的密码字段中设置。 |
| 代理主机 | ProxyHost | 否 | 如果需要访问 Foundry 的代理主机。应指定为myproxy.example.com，不需要添加前缀http。在 Windows 上，如果代理已被设置为默认的 Windows 代理，驱动程序将自动使用，因此可能不需要使用此参数。 |
| 代理端口 | ProxyPort | 否 | 代理端口。如果设置了代理主机，则必填。 |
| 代理用户名 | ProxyUsername | 否 | 如果代理需要认证的代理用户名。仅支持 HTTP 基本认证。 |
| 代理密码 | ProxyPassword | 否 | 代理密码。如果设置了代理用户名，则必填。 |
| 代理自动检测 | EnableProxyAutoDetect | 否 | 驱动程序是否应自动加载配置的操作系统代理（如果已设置）。允许的值：true（默认）或false。如果需要认证，仍需手动指定。设置为false以禁用并使用直接连接。 |
| SSL 信任库路径 | TrustStorePath | 否 | 自定义 SSL 证书信任库的路径，格式为.pem文件。如果 Foundry 证书不在默认操作系统信任库中，则必填。 |
| SQL 方言 | Dialect | 否 | 连接使用的SQL 方言。允许的值：ODBC（默认）、ANSI或SPARK。 |
| UTC 时间戳 | ODBCUtcTimestamps/ JDBC N/A | 否 | 时间戳是否应以 UTC 或本地时区返回。允许的值：true或false（默认）。在使用 BI 工具和发布报告时，此设置仅适用于本地 DSN，发布后可能会有所不同。此设置仅适用于 OBDC 时间戳，因为 JDBC 时间戳总是以 UTC 返回。 |

### 类型处理

以下表格显示了 Foundry 类型如何映射到 ODBC 和 JDBC 类型。

| Foundry 类型 | ODBC 类型 | JDBC 类型 |
| --- | --- | --- |
| 数组 | 编码为 JSON 并作为字符串 (SQL_WVARCHAR) 返回。 | 与 ODBC 相同 |
| 二进制 | 编码为十六进制字符串 (SQL_WVARCHAR)，前缀为0x。 | byte[] |
| 布尔 | SQL_BIT | boolean |
| 字节 | SQL_TINYINT | byte |
| 日期 | SQL_DATE | java.sql.Date |
| 十进制 | SQL_DECIMAL | java.math.BigDecimal |
| 双精度 | SQL_DOUBLE | double |
| 浮点 | SQL_DOUBLE | float |
| 整数 | SQL_INTEGER | int |
| 长整型 | SQL_BIGINT | long |
| 映射 | 编码为 JSON 并作为字符串 (SQL_WVARCHAR) 返回。 | 与 ODBC 相同 |
| 短整型 | SQL_SMALLINT | short |
| 字符串 | SQL_WVARCHAR。最大字符串列长度参数可以通过StringColumnLength属性设置。 | java.lang.String |
| 结构体 | 编码为 JSON 并作为字符串 (SQL_WVARCHAR) 返回。 | 与 ODBC 相同 |
| 时间戳 | SQL_TIMESTAMP。默认情况下，时间会转换为系统的本地时区。可以通过UtcTimestamps属性更改。 | java.sql.Timestamp以 UTC 时区。UtcTimestamps属性无效。 |

### SQL 方言

下表概述了可用 SQL 方言的某些 SQL 语法和特性（请参阅配置参数中的Dialect参数）。

|  | Spark（推荐） | ANSI, ODBC |
| --- | --- | --- |
| 标识符引用（列名、表名） | 反引号：SELECT * FROM `/Space/Project/...` | 双引号：SELECT * FROM "/Space/Project/..." |
| 字符串字面量引用 | 单引号或双引号：WHERE column = 'value' OR column = "value" | 单引号：WHERE column = 'value' |
| 日期字面量 | SELECT DATE 'yyyy-mm-dd' | 与 Spark 相同 |
| 当前日期 | SELECT CURRENT_DATE | 与 Spark 相同 |
| 附加参考 | Spark SQL 指南：SQL 参考 ↗ | 支持的函数：ODBC 参考 ↗ |

## 使用指南

### 使用 SQL 查询 Foundry 数据集

可以通过路径或 RID 在 SQL 查询中引用数据集。SQL 语法取决于连接设置的方言（请参阅配置参数）。

#### SPARK 方言

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
-- 基本的 SELECT 语句
SELECT * FROM `/Path/To/Dataset`

-- 使用 WHERE 子句进行过滤
SELECT * FROM `/Path/To/Dataset`
WHERE years < 13 AND category = 'Z';  -- 过滤条件：years 小于 13 且 category 等于 'Z'

-- 使用 JOIN 进行表连接
SELECT *
FROM `/Path/To/Dataset_A` a
JOIN `/Path/To/Dataset_B` b
    ON a.id = b.fk_id;  -- 连接条件：a 表的 id 等于 b 表的 fk_id
```

#### ODBC 和 ANSI 方言

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
-- 基本的 SELECT 语句
SELECT * FROM "/Path/To/Dataset";

-- 使用 WHERE 子句进行过滤
SELECT * FROM "/Path/To/Dataset"
WHERE years < 13 AND category = 'Z';
-- 过滤条件：years 小于 13 且 category 为 'Z'

-- 使用 JOIN 进行表连接
SELECT *
FROM "/Path/To/Dataset_A" a
JOIN "/Path/To/Dataset_B" b
    ON a.id = b.fk_id;
-- 在 a.id 和 b.fk_id 匹配的情况下连接 Dataset_A 和 Dataset_B
```

请参阅指南：识别数据集的RID或文件路径以获取有关使用数据集标识符的更多说明。

### 使用OAuth进行身份验证

ODBC和JDBC驱动程序支持OAuth 2.0流程，以提供更多身份验证选项，而不是手动生成与单个Foundry账户绑定的身份验证词元：

- 个人用户：驱动程序在您的浏览器中打开登录提示，以便您对Foundry进行身份验证。
- 服务用户：驱动程序连接到Foundry，作为在Foundry中注册的第三方应用程序所附的服务用户。
- 外部应用程序（针对开发人员）：第三方应用程序与Foundry的OAuth系统集成，以代表其用户获取词元。
在可能的情况下，我们建议使用这些基于OAuth的选项，而不是词元生成，因为它们更安全，并允许共享嵌入连接字符串，而无需共享个人用户的词元。

#### 个人用户（仅限Windows上的ODBC）

ODBC驱动程序在Windows上运行时支持自动OAuth登录和授权流程。请按照以下步骤设置此流程：

- (由Foundry管理员完成)在Foundry中注册一个第三方应用程序，指定以下配置选项：客户端类型：大多数情况下推荐公共客户端；如果您的应用案例需要，则支持机密客户端。授权授予类型：启用授权代码授予并将重定向URL设置为http://127.0.0.1/foundrydriver/oauthredirect。确保应用程序已注册和启用。从应用程序详细信息屏幕复制应用程序的客户端ID并与任何在其计算机上设置ODBC连接的用户共享。
- 客户端类型：大多数情况下推荐公共客户端；如果您的应用案例需要，则支持机密客户端。
- 授权授予类型：启用授权代码授予并将重定向URL设置为http://127.0.0.1/foundrydriver/oauthredirect。
- 确保应用程序已注册和启用。
- 从应用程序详细信息屏幕复制应用程序的客户端ID并与任何在其计算机上设置ODBC连接的用户共享。
- 从您的Foundry管理员处收到客户端ID后，设置以下ODBC连接参数：AuthMethod=OauthFlowOauthClientId=<YOUR_CLIENT_ID>或者，可以在应用程序的用户名字段中而不是OauthClientId中设置客户端ID，以便在应用程序内配置凭据。仍然必须设置AuthMethod。
- AuthMethod=OauthFlow
- OauthClientId=<YOUR_CLIENT_ID>或者，可以在应用程序的用户名字段中而不是OauthClientId中设置客户端ID，以便在应用程序内配置凭据。仍然必须设置AuthMethod。
- （非必填）如果您在Windows ODBC管理员应用程序中配置这些设置，您可以选择测试选项以触发登录提示并验证登录是否正常工作。
下次在客户端应用程序中使用驱动程序时，您将被提示在浏览器中登录Foundry。之后，您不需要每次使用驱动程序时都登录，尽管有时可能会再次提示。

#### 服务用户

对于不与个人用户关联的工作流（例如按计划刷新仪表盘的数据），我们推荐基于OAuth的服务用户，利用具有OAuth客户端凭据授予类型的第三方应用程序。驱动程序通过长效的客户端ID/密钥对向Foundry进行身份验证，这比手动创建的带有生成词元的服务账户更易于管理。

请按照以下步骤为服务用户设置OAuth：

- (由Foundry管理员完成。)在Foundry中注册一个第三方应用程序：客户端类型：选择机密客户端。授权授予类型：启用客户端凭据授予，并确保将客户端ID和客户端密钥对存储在安全位置。确保应用程序已注册和启用。确保生成的服务用户已被授予通过ODBC或JDBC驱动程序访问的任何数据集的访问权限。应用程序生成的服务用户列在客户端凭据授予详细信息面板中。
- 客户端类型：选择机密客户端。
- 授权授予类型：启用客户端凭据授予，并确保将客户端ID和客户端密钥对存储在安全位置。
- 确保应用程序已注册和启用。
- 确保生成的服务用户已被授予通过ODBC或JDBC驱动程序访问的任何数据集的访问权限。应用程序生成的服务用户列在客户端凭据授予详细信息面板中。
- 配置驱动程序时设置以下配置参数：AuthMethod=ClientCredentialsOauthClientId=<YOUR_CLIENT_ID>OauthClientSecret=<YOUR_CLIENT_SECRET>或者，可以在应用程序的用户名和密码字段中而不是OauthClientId和OauthClientSecret中设置客户端ID和客户端密钥，以便在应用程序内配置凭据。仍然必须设置AuthMethod。
- AuthMethod=ClientCredentials
- OauthClientId=<YOUR_CLIENT_ID>
- OauthClientSecret=<YOUR_CLIENT_SECRET>或者，可以在应用程序的用户名和密码字段中而不是OauthClientId和OauthClientSecret中设置客户端ID和客户端密钥，以便在应用程序内配置凭据。仍然必须设置AuthMethod。
驱动程序现在将作为OAuth应用程序的服务用户连接到Foundry。

#### 外部应用程序（针对开发人员）

应用程序开发人员可以将ODBC和JDBC驱动程序集成到运行其自身OAuth客户端以管理与第三方应用程序的OAuth登录流程的应用程序中。此选项允许完全控制登录流程，包括将用户重定向到Foundry进行身份验证，以及在用户完成身份验证和授权后处理授权响应。请参阅为Foundry编写OAuth2客户端文档以代表Foundry用户获取访问词元。

一旦您的应用程序代表用户获得访问词元，可以通过标准密码属性将其传递给驱动程序：

- ODBCPwd/ JDBCPassword=<ACCESS_TOKEN_OBTAINED_FROM_TOKEN_ENDPOINT>
### 启用ODBC驱动程序中的日志记录

如果需要启用驱动程序日志记录以排查问题，请按照以下步骤操作。请注意，这些步骤可能需要管理员权限。

- 创建一个文件夹以保存日志，例如My Documents\Foundry Driver logs。
- 打开WindowsODBC数据源工具。您可以通过在Windows搜索栏中搜索“ODBC”找到此工具。选择64位版本。
- 打开系统DSN选项卡。选择FoundrySql源，然后选择配置。请注意，选择哪个Foundry数据源并不重要，因为日志记录设置适用于使用Foundry驱动程序的所有数据源。
- 在配置窗口中选择日志选项。
- 将日志级别设置为DEBUG。将日志路径设置为您之前创建的文件夹。
- 选择确定以保存设置。
重新启动客户端应用程序并执行要排查的问题的操作。日志应出现在您选择的文件夹中。如果您需要Palantir或其他支持团队的支持，可以将此文件夹压缩为zip文件以共享。

完成故障排除后，返回ODBC数据源工具并通过将日志级别设置为OFF来禁用日志记录。建议此步骤以提高性能。

### 启用JDBC驱动程序中的日志记录

JDBC驱动程序将发现您的Java应用程序在类路径上提供的任何SLF4J日志记录器。具体而言，您的应用程序应提供org.slf4j.impl.StaticLoggerBinder和org.slf4j.impl.StaticMDCBinder类的实现。您可以通过添加slf4j-simple（版本1.X）作为项目依赖项来使用默认实现。

如果您未配置SLF4J日志记录器，则在首次加载驱动程序时会看到以下消息：

```
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
SLF4J: Failed to load class "org.slf4j.impl.StaticMDCBinder".
SLF4J: Defaulting to no-operation MDCAdapter implementation.
SLF4J: See http://www.slf4j.org/codes.html#no_static_mdc_binder for further details.
```

以上信息是SLF4J（简单日志门面）在运行时产生的警告信息：

- Failed to load class "org.slf4j.impl.StaticLoggerBinder"：未能加载StaticLoggerBinder类。这通常意味着SLF4J没有找到具体的日志实现。
Failed to load class "org.slf4j.impl.StaticLoggerBinder"：未能加载StaticLoggerBinder类。这通常意味着SLF4J没有找到具体的日志实现。

- Defaulting to no-operation (NOP) logger implementation：由于未能找到具体的日志实现，SLF4J将使用一个不执行任何操作的日志实现（NOP logger）。
Defaulting to no-operation (NOP) logger implementation：由于未能找到具体的日志实现，SLF4J将使用一个不执行任何操作的日志实现（NOP logger）。

- Failed to load class "org.slf4j.impl.StaticMDCBinder"：未能加载StaticMDCBinder类。
Failed to load class "org.slf4j.impl.StaticMDCBinder"：未能加载StaticMDCBinder类。

- Defaulting to no-operation MDCAdapter implementation：由于未能找到具体的MDC实现，SLF4J将使用一个不执行任何操作的MDC适配器。
Defaulting to no-operation MDCAdapter implementation：由于未能找到具体的MDC实现，SLF4J将使用一个不执行任何操作的MDC适配器。

建议查看相应的SLF4J文档链接以获取更多详细信息，这些链接提供了解决这些警告的方法和说明。通常情况下，添加合适的SLF4J绑定库（如slf4j-log4j12.jar或slf4j-simple.jar）可以解决这个问题。

### 使用foundry.ini配置文件配置 JDBC 驱动程序

除了使用连接字符串外，JDBC 驱动程序还可以通过配置文件进行配置。为此，请在 JDBC .jar 文件所在的目录中创建一个名为foundry.ini的文件。

.ini 文件分为两个部分：low-priority和high-priority。在low-priority部分指定的属性优先级低于连接字符串属性。这意味着，如果在low-priority部分和连接字符串中指定了相同的属性，将使用连接字符串中的值。相比之下，在high-priority部分指定的属性将优先于连接属性。这在从开发机器发布报告到服务器的情况下非常有用，此时服务器属性需要优先于开发属性。

foundry.ini文件示例：

```
Copied!1
2
3
4
5
6
7
8
9
[high-priority]
# 设置代理服务器的主机名
proxyHost=myproxy.abc
# 设置代理服务器的端口号
proxyPort=1234

[low-priority]
# 设置分支为生产分支
branch=production-branch
```

### 将JDBC驱动程序用于Java 16及以上版本

JDBC驱动程序默认支持的最大Java版本为Java 15。要将驱动程序用于Java 16及以上版本，请在您的应用程序中设置--add-opensJava运行时选项为java.base/java.nio=ALL-UNNAMED。

#### 示例：Java命令

```
Copied!1
java --add-opens=java.base/java.nio=ALL-UNNAMED -jar your_application.jar
```

以上命令用于运行一个Java应用程序，并且打开java.base模块中的java.nio包给所有未命名模块（ALL-UNNAMED）。这可能是为了绕过模块化系统的封装限制，以便允许未命名模块访问java.nio包的内部实现。这在某些情况下可能是必要的，例如使用反射访问内部类或方法。

#### 示例：环境变量

在某些情况下，在_JAVA_OPTIONS环境变量中指定选项更为方便，因为某些 Java 环境会自动检测并应用它。在基于 Unix 的系统上，可以使用export命令进行配置：

```
export _JAVA_OPTIONS="--add-opens=java.base/java.nio=ALL-UNNAMED"
```

以上代码是设置环境变量_JAVA_OPTIONS，用于为Java程序提供默认的JVM启动参数。

- --add-opens=java.base/java.nio=ALL-UNNAMED：这是一个JVM参数，允许模块java.base中的包java.nio对所有未命名模块开放。这个参数通常用于解决Java模块系统（Jigsaw）引入后，因访问限制导致的反射访问问题。
- 这个参数通常用于解决Java模块系统（Jigsaw）引入后，因访问限制导致的反射访问问题。