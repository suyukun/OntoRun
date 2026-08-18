来源: https://palantir.com/docs/zh/foundry/available-connectors/netsuite-suiteanalytics/

# Oracle NetSuite SuiteAnalytics

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Oracle NetSuite SuiteAnalytics

通过SuiteAnalytics Connect将Foundry连接到Oracle NetSuite，以将数据从您的NetSuite ERP同步到Foundry。

需要在您的NetSuite实例上启用SuiteAnalytics。请参阅NetSuite文档 ↗以启用它。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 一般可用 |
| 批量同步 | 🟢 一般可用 |
| 增量 | 🟢 一般可用 |

## 设置

- 打开数据连接应用程序并在屏幕右上角选择**+ 新来源**。
- 从可用的连接器类型中选择JDBC。
- 选择使用直接连接通过互联网连接，或者通过代理运行时连接。
- 按照下列部分中的信息继续进行连接器的附加配置提示。
了解更多关于在Foundry中设置连接器的信息。

## 认证

您可以使用用户名/密码组合进行SuiteAnalytics认证。我们建议使用服务用户凭据而不是个人用户凭据。

### 在NetSuite中配置用户角色和权限

在NetSuite中，为控制访问，每个用户被指派一个或多个角色，每个角色是定义用户可以执行哪些任务和可以访问哪些数据的权限集合。我们建议为将连接到Foundry的用户进行以下配置：

- 创建一个具有适当权限的专用角色。从NetSuite的工具栏中选择设置>用户/角色>管理角色>新建，并为角色提供一个明确的名称。我们建议使用foundry-role。通过导航到角色页面底部并选择权限>设置，为角色添加系统范围的权限。选择SuiteAnalytics Connect，选择添加然后保存。注意：NetSuite文档建议添加SuiteAnalytics Connect: Read All权限，但对于NetSuite2.com数据源是无关的（参见详情 ↗）。添加此权限不会有任何效果。通过导航到角色页面底部并选择权限>列表，为角色添加您希望能够从Foundry查询的表的权限。选择您想要的表，选择添加然后保存。
- 从NetSuite的工具栏中选择设置>用户/角色>管理角色>新建，并为角色提供一个明确的名称。我们建议使用foundry-role。
- 通过导航到角色页面底部并选择权限>设置，为角色添加系统范围的权限。选择SuiteAnalytics Connect，选择添加然后保存。注意：NetSuite文档建议添加SuiteAnalytics Connect: Read All权限，但对于NetSuite2.com数据源是无关的（参见详情 ↗）。添加此权限不会有任何效果。
- 注意：NetSuite文档建议添加SuiteAnalytics Connect: Read All权限，但对于NetSuite2.com数据源是无关的（参见详情 ↗）。添加此权限不会有任何效果。
- 通过导航到角色页面底部并选择权限>列表，为角色添加您希望能够从Foundry查询的表的权限。选择您想要的表，选择添加然后保存。
- 将新角色指派给用户。从NetSuite的工具栏中选择设置>用户/角色>管理用户。选择您希望用于连接到Foundry的用户，然后选择编辑。导航到访问选项卡，并确保选中给予访问复选框。在角色选项卡中，从下拉列表中选择新创建的角色（foundry-role），选择添加然后保存。注意：NetSuite文档建议使用数据仓库集成器角色代替自定义角色。然而，此角色需要使用基于词元认证的访问（参见更多详情 ↗），这在Foundry中不可用。
- 从NetSuite的工具栏中选择设置>用户/角色>管理用户。选择您希望用于连接到Foundry的用户，然后选择编辑。
- 导航到访问选项卡，并确保选中给予访问复选框。
- 在角色选项卡中，从下拉列表中选择新创建的角色（foundry-role），选择添加然后保存。注意：NetSuite文档建议使用数据仓库集成器角色代替自定义角色。然而，此角色需要使用基于词元认证的访问（参见更多详情 ↗），这在Foundry中不可用。
- 注意：NetSuite文档建议使用数据仓库集成器角色代替自定义角色。然而，此角色需要使用基于词元认证的访问（参见更多详情 ↗），这在Foundry中不可用。
为了验证您是否添加了正确的权限，请以您已分配新角色的用户身份登录，并检查您是否可以查看所有预期的数据。

## 网络连接

SuiteAnalytics连接器需要网络访问您希望连接到的NetSuite Connect实例。

### 选项1：直接连接

如果您是通过直接连接进行连接，则在设置来源时必须添加适当的出口政策。

需要允许的服务主机和端口可以在NetSuite的配置主页上找到，网址为https://<YOUR_ACCOUNT_ID>.app.netsuite.com/app/external/odbc/suiteAnalyticsConnectDownload.nl。
要在没有您的NetSuite账户ID的情况下访问此页面：

- 登录到您的NetSuite账户主页。
- 找到左下角的设置面板并选择设置SuiteAnalytics Connect。
服务主机通常的形式为**<ACCOUNT_ID>.connect.api.netsuite.com**，端口为1708。

如果不存在这样的出口政策，您可以请求一个新的；否则您可以添加它。

由于这是使用非HTTPS协议，您需要添加：

- 一个按名称引用您服务主机的DNS政策，以及
- 一个明确引用IP范围的CIDR政策。您可以通过在终端中运行nslookup you-service-host来获取NetSuite实例的IP范围。NetSuite服务的IP地址可能会随时更改，且无事先通知。
### 选项2：代理连接

如果您是使用代理运行时进行连接，您必须确保代理主机已打开连接到您的NetSuite Connect实例所需的主机名、IP地址和端口的防火墙。

## 连接详情

| 选项 | 必需？ | 描述 |
| --- | --- | --- |
| URL | 是 | 形式为jdbc:ns://<SERVICE_HOST>:<SERVICE_PORT>，其中SERVICE_HOST和SERVICE_PORT可以从NetSuite的配置主页检索。通常的形式为**jdbc:ns://<ACCOUNT_ID>.connect.api.netsuite.com:1708** |
| Driver class | 是 | 需要是**com.netsuite.jdbc.openaccess.OpenAccessDriver** |
| Drivers | 是 | (选项1)对于直接连接，上传您可以从NetSuite的配置主页下载的最新JDBC驱动程序。(选项2)对于代理连接，与选项1相同的JDBC驱动程序需要正确签署以便上传到代理。请联系您的Palantir代表以进行此操作。参见如何将驱动程序添加到代理以获取更多详情。 |
| Credentials | 是 | 用于连接到Foundry的用户的用户名和密码。 |
| JDBC properties | 是 | 可用属性的完整列表在此处 ↗描述。以下属性是强制性的：-CustomProperties:(AccountID=<ACCOUNT_ID>;RoleID=<ROLE_ID>)*ROLE_ID是您分配给用户的角色（foundry-role）的内部ID。您可以在设置>用户/角色>管理角色页面上找到此值。如果未显示内部ID，请参见如何启用它 ↗。*-NegotiateSSLClose:false-ServerDataSource:NetSuite2.com自2021年11月8日起，新Connect用户只能使用NetSuite2.com数据源访问Connect服务。有关更多详情，请参见Oracle NetSuite的文档 ↗。-encrypted:1 |

其他连接参数与任何JDBC来源相同。

## 创建同步

NetSuite SuiteAnalytics来源可以通过探索来发现表并创建新同步。
您还可以从来源的概览页面手动创建新同步。
