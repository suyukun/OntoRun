来源: https://palantir.com/docs/zh/foundry/sap/oauth2-writeback/

# 用户归属的 SAP 数据输出与 OAuth 2.0

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 用户归属的 SAP 数据输出与 OAuth 2.0

本页面包含在 SAP 中设置 OAuth 2.0 服务器和在 Foundry 中设置 OAuth 2.0 客户端的说明。

## 在 SAP 中设置 OAuth 2.0 服务器

### 先决条件

- Palantir Foundry Connector 2.0 for SAP Applications ("Connector") 的 SP21 或更高版本
- SAP 中的 Foundry 技术用户应为SYSTEM用户
- /PALANTIR/OAUTH_CLIENT应指派给 Foundry 技术用户和任何希望从 Foundry 数据输出到 SAP 的终端用户
- /PALANTIR/CONTENT_FUNCTION_ALL应指派给终端用户
- 需激活/sap/public/bc节点下的所有服务（用于 OAuth 2.0 配置）/sap/bc/sec/oauth2*/default_host/sap/bc/webdynpro/sap/oauth2_authority
- /sap/bc/sec/oauth2*
- /default_host/sap/bc/webdynpro/sap/oauth2_authority
- SAP 网关已激活
- SAP NetWeaver 7.4 SP09 或更高版本（支持 OAuth 2.0 和 OData）
### 参考

- 注释 1688545 - AS ABAP 中的 OAuth 2.0 服务器故障排除 ↗（需要 SAP 登录）
- 帮助: AS ABAP 的 OAuth 2.0 服务器 ↗
### OAuth 2.0 配置

- 运行SOAUTH2事务。
- 选择创建...。
- 输入 Foundry 技术用户的用户名作为OAuth 2.0 客户端 ID。
- 选择下一步 >。
- 输入 Foundry 技术用户的用户名作为用户 ID。
- 确保勾选了客户端用户 ID 和密码和SSL 客户端证书。
- 选择下一步 >。
- 将重定向 URI设置为https://<FOUNDRY_DOMAIN>/workspace/oauth2-clients/callback。
- 选择下一步 >。
- 添加一个范围分配，OAuth 2.0 范围 ID为/PALANTIR/SRV_0001，描述如使用 SAP 函数进行 Palantir Foundry 数据输出。
- 选择下一步 >然后完成。
### OData 配置

- 在 SAP 的维护服务页面中，按照服务层次结构找到opu > odata > palantir。
- 右键点击palantir并选择激活服务。
- 在提示时选择是。
- 在创建/更改服务选项卡中，选择交互选项下的GUI 配置。
- 添加名称为~CHECK_CSRF_TOKEN，值为0（零）的参数。
- 按照此处说明禁用 CSRF_TOKEN 验证：https://help.sap.com/doc/saphelp\_hba/1.0/de-DE/e6/cae27d5e8d4996add4067280c8714e/content.htm
- 运行/IWFND/MAINT_SERVICE事务。
- 在系统别名下选择添加系统别名。
- 添加具有以下值的系统别名：服务文档标识符：/PALANTIR/SRV_0001用户角色：空主机名：空SAP 系统别名：LOCAL元数据默认：未勾选默认系统：已勾选技术服务名称：/PALANTIR/SRV外部服务名称：ODATA_SRV版本：1用户名：空
- 服务文档标识符：/PALANTIR/SRV_0001
- 用户角色：空
- 主机名：空
- SAP 系统别名：LOCAL
- 元数据默认：未勾选
- 默认系统：已勾选
- 技术服务名称：/PALANTIR/SRV
- 外部服务名称：ODATA_SRV
- 版本：1
- 用户名：空
## 在 Foundry 中设置 OAuth 2.0 客户端

此过程遵循配置外部应用程序中概述的一般方法，但已专门针对 SAP 系统进行调整。

### 源连接设置

确保 SAP 源 URL 使用 HTTPS，否则在使用 OAuth 流时，webhook 将出错。

- 创建一个新的REST API源。
- 使用用于 SAP 源的基础域 URL 和端口配置源。
- 选择基本认证并添加用于连接 SAP 的用户名和密码。
- 保存源。
### OAuth 2.0 授权流程 webhook 设置

- 在新REST API源的概览页面上，选择创建 webhook。
在新REST API源的概览页面上，选择创建 webhook。

- 为 webhook 命名（例如“SAP OAuth2 授权代码流 webhook”）。
为 webhook 命名（例如“SAP OAuth2 授权代码流 webhook”）。

- 前进到请求配置步骤。
前进到请求配置步骤。

- 在调用下，选择POST作为请求类型，并输入sap/bc/sec/oauth2/token作为路径。
在调用下，选择POST作为请求类型，并输入sap/bc/sec/oauth2/token作为路径。

- 在查询参数下，如果使用的客户端不是默认客户端，可能需要设置sap-client。
在查询参数下，如果使用的客户端不是默认客户端，可能需要设置sap-client。

- 向下滚动到输入参数并添加以下三个参数（均为字符串类型）：
- redirect_uri
- client_id
- authorization_code
- 向上滚动回调用并选择正文选项卡。
- 选择表单 URL 编码并添加以下四个条目：
- grant_type→authorization_code
- redirect_uri→ 映射到redirect_uri输入参数（请参见下文了解如何进行此操作）
- client_id→ 映射到client_id输入参数
- code→ 映射到authorization_code输入参数
- 要映射输入参数，请在字段中键入@，然后选择输入参数。找到相关参数，选择它，然后选择下面的添加。
- 完成的正文配置应如下所示：
- 前进到响应步骤。
- 创建以下五个输出参数。所有参数都应为字符串类型，并应从响应中按键提取。
- access_token
- token_type
- expires_in
- refresh_token
- scope
这是创建access_token的示例。所有输出参数应遵循此模式。

- 通过选择创建 webhook 并继续保存 webhook。
### OAuth 2.0 刷新流 webhook 设置

- 从REST API源创建一个新的 webhook。
- 为 webhook 命名一个不同的名称（例如“SAP OAuth2 刷新流 webhook”）。
- 请求方法应再次设置为POST，并使用相同的路径 (sap/bc/sec/oauth2/token)。
- 与前一个 webhook 一样，如有需要，设置sap-client为查询参数。
- 在头选项卡中，添加以下头：
- Content-Type→application/x-www-form-urlencoded
- 设置这两个输入参数（均为字符串）：
- client_id
- refresh_token
- 然后在正文选项卡下，添加以下三个条目：
- grant_type→refresh_token
- client_id→ 映射到client_id输入参数
- refresh_token→ 映射到refresh_token输入参数
- 创建与授权代码流 webhook 完全相同的五个输出参数。所有参数都应为字符串类型，并应从响应中按键提取。
- access_token
- token_type
- expires_in
- refresh_token
- scope
- 通过选择创建 webhook 并继续保存 webhook。
### 外部应用程序设置

- 导航到Foundry 控制面板并选择外部应用程序。
- 为应用程序命名，然后按照本地 OAuth 服务器的配置选项中概述的步骤进行操作。
- 之前创建的两个 webhook 应分别用作令牌 webhook和刷新令牌 webhook。
- 授权页面 URL应为以下形式：
```
https://<SAP_DOMAIN>/sap/bc/sec/oauth2/authorize
```

这个URL用于SAP系统中OAuth2授权过程的端点。
5. 在OAuth 2.0 设置下，将Client ID设置为 SAP OAuth 2.0 服务器配置中的客户端 ID。在Scopes下，添加/PALANTIR/SRV_0001。
6. 保存出站应用程序。
7. 现在可以在创建 SAP webhook 时使用此出站应用程序。
