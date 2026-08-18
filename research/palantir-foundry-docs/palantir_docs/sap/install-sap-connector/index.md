来源: https://palantir.com/docs/zh/foundry/sap/install-sap-connector/

# 安装 Palantir Foundry Connector 2.0 以用于 SAP 应用程序

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 安装 Palantir Foundry Connector 2.0 以用于 SAP 应用程序

Palantir Foundry Connector 2.0 以 SAP 附加组件的形式发布，需通过SAINT(SAP Add-On Installation Tool) 进行安装。该附加组件以 SAR 格式交付，文件名模式为：FOUNDRY-SAPCONN-INST-SP00SPXX.SAR

SP00SPXX代表从SP00到SPXX的安装文件，其中XX是支持包级别。

如果在BW/4HANA或S/4HANA上安装 Connector，请在安装中包含属性更改包。截至 SP22，这些包已包含在安装文件中。

以下是设置 Connector 所需的高层步骤：

- 下载安装包。
- 通过SAINT安装 Connector 附加组件。
- 在SU01中为 Foundry 创建一个技术用户。
- 运行安装后向导。
## 先决条件

- SAP NetWeaver 7.4 SP5 或更高版本
或

- SAP NetWeaver 7.5（无最低 SP 级别）
确保已阅读以下 SAP 说明并在适用时遵循相关步骤：

- SAP OSS 说明2645739-ABAP Add-On OCS 包未进行数字签名
## 安装 Connector 附加组件

- 使用被授权使用SAINT的用户登录到 SAP 系统客户端000。
- 运行SAINT事务。
- 将FOUNDRY-SAPCONN-INST-SP00SPXX.SAR导入 SAP 服务器；选择安装包>加载包>从前端。
对于某些 SAINT/SPAM 版本，SPAM 或 SAINT 设置可能会影响安装过程。禁用无法进行签名检查，SAP 说明 2520826 未实施项目下的检查期间导入部分。注意，对于某些 SPAM 版本，该项目根本没有描述，但仍应禁用。

- 选择开始进行安装。
- 显示可用的包。如果没有，请通过单击筛选图标停用筛选。
- 选择继续进入下一步。
- 对于 Connector 安装，选择PALANTIR和PALCONN。
- 选择继续进入支持包选择。
- 从列表中选择最高可用支持包，并确保两个组件都选择了相同的 SP 级别。
- 确认安装队列并点击继续。
- 对于准备阶段选择对话模式继续，对于其他阶段选择立即后台继续，并开始安装。
如果在安装期间标记了警告，请按照警告信息中描述的步骤进行解决。在大多数情况下，警告信息对于 Connector 和远程代理安装可以忽略。特别是，带有标题 "开放数据提取请求" 的警告信息可以忽略，因为安装不会更改 DDIC 结构，因此不会导致开放数据提取请求终止。

- 选择完成完成安装。
## 运行安装后向导

Connector 安装后向导简化了安装后配置活动。要执行安装后和配置，请登录到主客户端（不是000）。可以通过事务代码/n/PALANTIR/POST_INST或从 Connector 菜单（事务代码：/n/PALANTIR/）访问安装后向导。

### 向导步骤

共有 10 个步骤，可以一起运行或单独运行。要完成安装，所有步骤都需要启用。如果这不是 SLT 安装，请禁用创建 SLT 配置。SLT 配置在第 7 步中详细介绍。

执行用户需要有足够的授权以指派所需的授权角色给 Foundry 技术用户。此过程类似于通过SU01事务代码维护用户。如果用户指派是单独完成的，请禁用指派角色给 Foundry 用户和执行健康检查。

#### 1. 运行卸载修正

此步骤运行一个后台程序，修复 Connector 对象目录中的 SAP 包。此修正程序可以在任何时候运行，没有不利的副作用。

#### 2. 激活 SICF 服务

此步骤激活两个 Connector 服务，这对于数据传输是必需的。请注意，如果需要，这可以通过SICF事务代码手动完成。两个服务是：

- /default_host/sap/palantir
- /default_host/sap/opu/odata/palantir
#### 3. 生成角色

Connector 有自己的一套角色，这些角色在安装期间导入。安装后这些角色保持未生成状态。如果需要，可以使用PFCG事务代码通过Utilities > Mass Generation手动进行批量生成。

- /PALANTIR/CONTENT_BEX_ALL
- /PALANTIR/CONTENT_CDS_ALL
- /PALANTIR/CONTENT_HANA_ALL
- /PALANTIR/CONTENT_DM_ALL
- /PALANTIR/CONTENT_EXT_ALL
- /PALANTIR/CONTENT_FUNCTION_ALL
- /PALANTIR/CONTENT_INFOPROV_ALL
- /PALANTIR/CONTENT_SLT_ALL
- /PALANTIR/CONTENT_TABLE_ALL
- /PALANTIR/CONTENT_TCODE_ALL
- /PALANTIR/DEBUG_USER
- /PALANTIR/MONITORING
- /PALANTIR/OAUTH_CLIENT
- /PALANTIR/SERVICE_SLT
- /PALANTIR/SERVICE_SLT_740
- /PALANTIR/SERVICE_USER
#### 4. 将角色指派给 Foundry 用户

第 3 步中的所有 Palantir 角色将被指派给在选择屏幕中定义的 SAP 用户。

如果此步骤生成关于角色指派、无法检索用户详细信息或缺乏授权的错误消息，这表明运行安装后向导的用户没有足够的权限。在这种情况下，请按照错误消息中的建议更正用户授权并重新运行程序。

如果此步骤生成错误消息，建议 Foundry 用户已锁，请联系锁定的所有者以将其移除，然后重新运行程序。

#### 5. 维护默认参数

可以通过这些选择设置资源检查和连续资源检查参数。默认值在选择屏幕中，可以根据您的要求进行更改。当程序以此选择运行时，Connector 参数将根据所选参数进行修改。这些参数也可以通过事务代码/n/PALANTIR/PARAM进行维护。

了解性能参数。

#### 6. 检查 ICM 设置

此步骤验证 ICM 设置、主机名和端口（用于 HTTP 和 HTTPS），并创建可用于测试连接的 URL。

#### 7. 创建 SLT 配置

如果连接是通过 SAP SLT 复制服务器，此步骤才相关。

如果在 SAP SLT 实例上安装了 Connector，可以由安装后向导创建新的 SLT 配置 (ODP)。您也可以使用LTRC事务代码创建 SLT 配置。

SLT 配置的参数如下：

| 参数 | 描述 |
| --- | --- |
| Context Name | 唯一配置名称。 |
| Context Description | 在 SAP 事务LTRC和 Foundry 中显示给用户的上下文描述。 |
| Data Transfer Jobs | 数据传输任务数量。 |
| Initial Load Jobs | 初始加载任务数量。 |
| Calculation Jobs | 用于初始加载范围计算的计算任务数量。 |
| Authorization Group | 默认无授权组。 |
| Replication Mode | 1 - 实时（默认）；2 - 时间间隔；3 - 时间计划；4 - 按需。 |
| Source RFC Destination | 逻辑目的地 - 源系统的 RFC 目的地名称。 |
| Read from Single Client | 如果数据将从单个客户端读取，请启用。 |
| Allow Multiple Usage | 如果允许多次使用，请启用。 |

#### 8. 执行健康检查

Connector 在已安装的 SAP 系统中具有各种指标来衡量健康状况。Connector 在以下类别中执行健康检查：

- AGENT: 检查 RFC 连接和源系统授权。仅与通过网关的远程连接相关。
- AUTHORIZATION: 检查 Foundry 用户在SM53中是否有任何缺失的授权。
- CONNECTOR: 检查 Connector 维护任务是否已在系统中计划。
- ROLE: 检查 Foundry 用户的角色和授权配置文件。
- SLT: 检查 SLT 配置是否正确和健康；例如，BADI_Implementation 是否激活，上下文是否激活，SLT 维护任务是否已计划，或源系统连接是否正常工作。
#### 9. 浏览器测试 URL

安装后，通过使用网络浏览器进行连接性测试来检查 Connector 是否正常运行是很重要的。所需的 URL 由安装后向导生成。

可用的测试有几种。第一和第二个测试是对 Connector 服务的同步调用；第三和第四个用于批量提取。

- 关于: Connector 的关于页面。
- T000 表: 使用table对象类型直接提取 T000 表。
- T000 带分页初始化: 使用table对象类型初始化 T000 表的后台提取。
- T000 带分页读取第 1 页: 将为之前的 URL 初始化的过程检索第一页。
#### 10. Foundry 的源定义模板

在运行带有 Foundry 中的源定义的程序后，将显示一个新选项卡“源定义”，其中包含 Foundry 中源配置的详细信息。

### 安全性和授权角色

更多详细信息可以在授权角色中找到。

### 性能参数

Connector 具有以下性能参数，以避免在系统资源不足以服务 Foundry 时产生不必要的系统负载。这些设置与 ST06 值进行比较。

以下列出的默认参数值适用于最新连接器版本的新安装。

- MEMORY_FREE: 可用内存百分比。如果此百分比低于系统默认值或用户定义值，提取将停止。Connector 默认值为5%。
- CPU_IDLE: CPU 空闲百分比。Connector 默认值为5%。
- CPU_USER: 用户事务的 CPU 利用率。Connector 默认值为80%。
- CPU_LOAD: 总 CPU 利用率。Connector 默认值为80%。
ST06 关键数字由 SAP 提供给 Connector。如果激活了虚拟化的增强监控，操作系统特定的信息将被虚拟化特定的信息丰富。这可能会影响 ST06 数字并误导 Connector。有关更多详细信息，请参阅 SAP OSS 文章 2266266。

初始系统默认值有意保守。如果您希望将其覆盖为更宽松，请通过/n/PALANTIR/PARAM事务进行维护。

以下参数用于启用或禁用资源检查：

| 参数 ID | 参数名称 | 参数值 | 默认 | 描述 |
| --- | --- | --- | --- | --- |
| SYSTEM | CPU_CHECK | TRUE/FALSE | TRUE | 启用或禁用 CPU 检查。 |
| SYSTEM | MEMORY_CHECK | TRUE/FALSE | TRUE | 启用或禁用内存检查。 |
| SYSTEM | RESOURCE_CHECK | TRUE/FALSE | TRUE | 启用或禁用资源检查。如果为 FALSE，则禁用所有检查；如果为 TRUE，则检查其他参数（CPU_CHECK 和 MEMORY_CHECK）。 |
| SYSTEM | CONTINUOUS_RESOURCE_CHECK | TRUE/FALSE | TRUE | 启用所有请求（初始化和所有分页请求）的资源检查。如果为 FALSE，资源检查仅对初始化请求执行。 |
| SYSTEM | PROCESS_CHECK | TRUE/FALSE | TRUE | 启用对允许的最小工作进程数量的检查；与 PROCESS_MIN_BG 和 PROCESS_MIN_DIA 一起使用。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_BG | 数字 | 1 | SAP 应用服务器上可用的最小后台进程数量。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_DIA | 数字 | 1 | SAP 应用服务器上可用的最小对话进程数量。 |

要检查实际值和参数值，您可以使用浏览器中的系统对象和资源函数：

```
Copied!1
https://<sap-server>:<port>/sap/palantir/system?obj=resource
```

这是一段URL格式的代码，通常用于访问SAP系统中的资源。以下是参数的说明：

- <sap-server>: 指SAP服务器的地址。
- <port>: 指连接SAP服务器所需的端口号。
- /sap/palantir/system?obj=resource: 路径和查询参数，用于指定访问SAP系统中的某个资源对象。
这种格式通常用于API调用，以获取或操作SAP系统中的数据资源。
请注意，此URL是一个SAP系统URL；您应确保此资源是可访问的。

输出将是以下格式：

```
MSGTYP	MSGTXT
S	Current CPU_LOAD value : 0,01 | system threshold value : 95,00
    # 当前的CPU负载值：0.01 | 系统阈值：95.00
S	Current CPU_USER value : 1,00 | system threshold value : 0,01
    # 当前的CPU用户使用率：1.00 | 系统阈值：0.01
S	Current CPU_IDLE value : 99,00 | system threshold value : 5,00
    # 当前的CPU空闲率：99.00 | 系统阈值：5.00
S	Current free memory percentage : 24,22 | system threshold value : 11,00
    # 当前的空闲内存百分比：24.22 | 系统阈值：11.00
S	Current PROCESS_MIN_BG value : 5 | system threshold value : 2
    # 当前的最小后台进程数：5 | 系统阈值：2
S	Current PROCESS_MIN_DIA value : 9 | system threshold value : 2
    # 当前的最小对话进程数：9 | 系统阈值：2
S	Resource check is Active
    # 资源检查处于激活状态
S	CPU Load check is Active
    # CPU负载检查处于激活状态
S	Memory consumption check is Active
    # 内存消耗检查处于激活状态
S	Process availability check is Active
    # 进程可用性检查处于激活状态
```
