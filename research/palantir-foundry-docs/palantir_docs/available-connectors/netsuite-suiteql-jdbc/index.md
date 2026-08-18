来源: https://palantir.com/docs/zh/foundry/available-connectors/netsuite-suiteql-jdbc/

# Oracle NetSuite SuiteQL

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Oracle NetSuite SuiteQL

使用 SuiteQL 框架将 Foundry 连接到 Oracle NetSuite，并开始从您的 NetSuite ERP 同步数据到 Foundry。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 探索 | 🟢 通常可用 |
| 批量同步 | 🟢 通常可用 |
| 增量同步 | 🟢 通常可用 |

## 设置

- 打开数据连接应用程序，并在屏幕右上角选择+ 新建来源。
- 从可用的连接器类型中选择NetSuite SuiteQL。
- 选择通过直接连接连接互联网，或通过代理运行时进行连接。
- 根据以下部分中的信息，按照额外的配置提示继续设置您的连接器。
了解更多关于在 Foundry 中设置连接器的信息。

### 认证

NetSuite SuiteQL 来源使用基于词元的认证 (TBA) ↗。

必须在您的账户上启用基于词元的认证功能。要启用 TBA，请参见NetSuite 文档 ↗。

#### 在 NetSuite 中配置用户角色和权限

NetSuite 中的访问控制通过将角色指派给用户进行配置；每个角色都是一组权限，定义了用户可以执行哪些任务以及可以访问哪些数据。我们建议为将连接到 Foundry 的用户进行以下配置：

- 创建一个专用角色并赋予适当的权限。从 NetSuite 的工具栏中选择设置>用户/角色>管理角色>新建，并为该角色提供一个明确的名称。我们建议使用foundry-role。您可以选择勾选仅限 Web 服务配置框。通过导航到角色页面底部并选择权限>设置，为角色添加系统范围的权限。需要添加的最低权限是：使用访问词元登录REST Web 服务自定义记录类型自定义字段添加所需权限后请记得保存。通过导航到角色页面底部并选择权限>报告，为角色添加报告权限。选择：SuiteAnalytics 工作簿，记得添加权限然后保存。通过导航到角色页面底部并选择权限>列表，为角色添加您希望从 Foundry 查询的表的权限。选择您想要的表，选择添加然后保存。
创建一个专用角色并赋予适当的权限。

- 从 NetSuite 的工具栏中选择设置>用户/角色>管理角色>新建，并为该角色提供一个明确的名称。我们建议使用foundry-role。您可以选择勾选仅限 Web 服务配置框。
- 您可以选择勾选仅限 Web 服务配置框。
- 通过导航到角色页面底部并选择权限>设置，为角色添加系统范围的权限。需要添加的最低权限是：使用访问词元登录REST Web 服务自定义记录类型自定义字段添加所需权限后请记得保存。
- 使用访问词元登录
- REST Web 服务
- 自定义记录类型
- 自定义字段
- 添加所需权限后请记得保存。
- 通过导航到角色页面底部并选择权限>报告，为角色添加报告权限。选择：SuiteAnalytics 工作簿，记得添加权限然后保存。
- SuiteAnalytics 工作簿，
- 记得添加权限然后保存。
- 通过导航到角色页面底部并选择权限>列表，为角色添加您希望从 Foundry 查询的表的权限。选择您想要的表，选择添加然后保存。
- 将新角色指派给用户。从 NetSuite 的工具栏中选择设置>用户/角色>管理用户。选择您希望用来连接 Foundry 的用户，并选择编辑。导航到访问选项卡，并确保勾选了给予访问权限复选框。在角色选项卡中，从下拉列表中选择新创建的角色 (foundry-role)，选择添加然后保存。
将新角色指派给用户。

- 从 NetSuite 的工具栏中选择设置>用户/角色>管理用户。选择您希望用来连接 Foundry 的用户，并选择编辑。
- 导航到访问选项卡，并确保勾选了给予访问权限复选框。
- 在角色选项卡中，从下拉列表中选择新创建的角色 (foundry-role)，选择添加然后保存。
要验证您添加了正确的权限，请以被指派新角色的用户身份登录，并检查您是否可以查看所有预期的数据。

#### 在 NetSuite 中配置集成和访问词元

集成记录在 NetSuite 中用于管理与外部系统的连接。我们建议以下配置以连接到 Foundry：

- 使用 TBA 创建一个新的集成记录（参见更多详情 ↗）。从 NetSuite 的工具栏中选择设置>集成>管理集成>新建，并为集成提供一个明确的名称。我们建议使用foundry-integration。确保状态是启用的，并且仅勾选了基于词元的认证。其他所有框应不勾选。在您保存后，记录下CLIENT ID和CLIENT SECRET。您将需要它们来配置 Foundry。
- 从 NetSuite 的工具栏中选择设置>集成>管理集成>新建，并为集成提供一个明确的名称。我们建议使用foundry-integration。
- 确保状态是启用的，并且仅勾选了基于词元的认证。其他所有框应不勾选。
- 在您保存后，记录下CLIENT ID和CLIENT SECRET。您将需要它们来配置 Foundry。
CLIENT ID和CLIENT SECRET仅在您首次保存集成记录时显示。您必须重置它们才能获取新的，这将使之前的值失效。

- 创建并分配一个 TBA 词元。从 NetSuite 的工具栏中选择设置>用户/角色>访问词元>新建。如果您无法为其他用户管理词元，请在 NetSuite 的主页左下角设置面板中选择管理访问词元。选择新创建的应用程序（在我们的示例中为foundry-integration）、已指派新角色的用户（foundry-role）和新创建的角色。如果您无法为其他用户管理词元，您的用户将默认被选中。确保您的用户已被指派新创建的角色（foundry-role）。在您保存后，记录下TOKEN ID和TOKEN SECRET。您将需要它们来配置 Foundry。
- 从 NetSuite 的工具栏中选择设置>用户/角色>访问词元>新建。如果您无法为其他用户管理词元，请在 NetSuite 的主页左下角设置面板中选择管理访问词元。
- 如果您无法为其他用户管理词元，请在 NetSuite 的主页左下角设置面板中选择管理访问词元。
- 选择新创建的应用程序（在我们的示例中为foundry-integration）、已指派新角色的用户（foundry-role）和新创建的角色。如果您无法为其他用户管理词元，您的用户将默认被选中。确保您的用户已被指派新创建的角色（foundry-role）。
- 如果您无法为其他用户管理词元，您的用户将默认被选中。确保您的用户已被指派新创建的角色（foundry-role）。
- 在您保存后，记录下TOKEN ID和TOKEN SECRET。您将需要它们来配置 Foundry。
TOKEN ID和TOKEN SECRET仅在您首次保存词元时显示。您需要创建一个新词元以获取新的TOKEN ID和TOKEN SECRET。

了解更多关于 NetSuite 中词元管理的信息。 ↗

### 网络

NetSuite SuiteQL 连接器需要对您希望连接的 NetSuite 实例的网络访问。

#### 选项 1：直接连接

如果您是通过直接连接进行连接，您需要向来源添加以下出口策略：

- <ACCOUNT_ID>.suitetalk.api.netsuite.com 在端口 443 上。您可以在连接到 NetSuite 时在网址中找到您的账户 ID。
如果此出口策略不存在，您可以请求出口策略；否则，您可以添加出口策略。

#### 选项 2：代理连接

如果您是通过代理运行时进行连接，您必须确保代理主机已开放连接到您的 NetSuite Connect 实例所需的主机名、IP 地址和端口的防火墙。

### 连接详情

| 选项 | 必需的？ | 描述 |
| --- | --- | --- |
| Account ID | 是 | NetSuite 账户 ID，可在您的 NetSuite 实例 URL 中找到作为前缀 |
| Client ID | 是 | 创建foundry-integration时复制的CLIENT ID |
| Client secret | 是 | 创建foundry-integration时复制的CLIENT SECRET |
| Access token | 是 | 创建TBA 词元时复制的TOKEN ID |
| Access token secret | 是 | 创建TBA 词元时复制的CLIENT ID |

## 创建同步

可以通过探索NetSuite SuiteQL 来源来发现表并创建新的同步。您也可以从来源的概览页面手动创建新的同步。
