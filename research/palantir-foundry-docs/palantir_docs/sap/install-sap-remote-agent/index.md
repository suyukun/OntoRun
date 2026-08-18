来源: https://palantir.com/docs/zh/foundry/sap/install-sap-remote-agent/

# 安装远程代理

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 安装远程代理

远程代理旨在通过主要的Palantir Foundry Connector 2.0 for SAP Applications（“Connector”）访问远程SAP系统。如果SAP NetWeaver的版本低于7.4 SP05，或者您希望在系统环境中将两个或多个SAP系统视为单个Foundry Source，则应安装远程代理。远程代理的最低SAP NetWeaver版本要求是NetWeaver 7.00 SP32。对于更低的产品版本或NetWeaver 7.00的支持包，请参见安装ERP 4.6C/4.7（620/640）的远程代理。

在远程SAP系统中安装远程代理，请按照以下步骤进行：

- 下载安装包。
- 使用被授权使用SAINT的用户登录到SAP系统客户端000。
- 运行SAINT事务。
- 将FOUNDRY-SAPCONN-INST-SP00SPXX.SAR导入到SAP服务器：选择安装包>加载包>从前端。
对于某些SAINT/SPAM版本，SPAM或SAINT设置可能会影响安装过程。取消选中*“无法进行签名检查，SAP note 2520826未实施”项下的“检查期间的检查”*部分。还需要注意的是，对于某些SPAM版本，此复选框根本没有描述——您仍应取消选中此框。

- 选择开始进行安装。
- 可用包被列出。
如果未列出，请点击筛选图标以取消激活筛选。

- 继续下一步。
- 对于Connector安装，选择PALANTIR和PALAGENT。
- 选择继续以进入支持包选择。
- 从列表中选择最高可用的支持包，并确保两个组件选择了相同的SP级别。
- 确认安装队列并点击继续。
- 对于准备阶段，选择对话模式下继续，对于其他阶段，选择立即在后台继续，并开始安装。
安装过程中可能会有一些警告标记；请按照警告信息中描述的步骤进行操作。在大多数情况下，警告信息可在Connector和远程代理安装中忽略。特别是，标题为*“打开数据提取请求”*的警告信息可以忽略。

- 选择完成以完成安装。
- 运行PFCG事务代码并为以下角色执行授权配置文件生成和用户比较：/PALANTIR/CONTENT_RBEX_ALL/PALANTIR/CONTENT_RFUNCT_ALL/PALANTIR/CONTENT_RINFOPRV_ALL/PALANTIR/CONTENT_RTABLE_ALL/PALANTIR/CONTENT_RTCODE_ALL/PALANTIR/SERVICE_USER
- /PALANTIR/CONTENT_RBEX_ALL
- /PALANTIR/CONTENT_RFUNCT_ALL
- /PALANTIR/CONTENT_RINFOPRV_ALL
- /PALANTIR/CONTENT_RTABLE_ALL
- /PALANTIR/CONTENT_RTCODE_ALL
- /PALANTIR/SERVICE_USER
## 配置

Connector和Connector远程代理通过SAP远程函数调用（RFCs）进行通信。因此，需要两个RFC连接：一个从Connector到远程代理，另一个从远程代理到Connector。下一节详细介绍如何创建这些RFC连接。

### RFC配置

RFC配置需要四个步骤：

- 创建到SAP系统的RFC连接。
- 创建从Connector到远程SAP系统的RFC（SOURCE）。
- 创建从远程SAP系统到Connector的RFC（TARGET）。
- 通过网络浏览器测试Connector远程代理。
#### 创建到源/目标系统的RFC目标连接

在本节中，需要两个RFC连接：一个从Connector到远程代理，另一个从远程代理到Connector。请参阅创建RFC连接文档以创建RFC连接。

对从远程SAP系统到Connector的目标RFC定义重复相同的步骤。您可以将其命名为SAP_TARGET，而不是SAP_SOURCE。（这些名称可以自由定义。）

#### 配置远程代理和注册Connector

- 登录到主要的Connector系统。
- 运行事务/n/PALANTIR/PARAM_A1。
- 输入以下参数值：Agent ID: 代理标识符（也称为CONTEXT）Is 4.7 or older: 代理版本标志Agent Desc: 代理描述（供参考使用）
- Agent ID: 代理标识符（也称为CONTEXT）
- Is 4.7 or older: 代理版本标志
- Agent Desc: 代理描述（供参考使用）
- 运行事务/n/PALANTIR/PARAM_A2并输入以下参数：Agent ID: 代理ID（如上一步中定义）Param ID: 参数ID（参数分类）Param Name: 参数名称（代理使用）Param Value: 参数值（代理使用）
- Agent ID: 代理ID（如上一步中定义）
- Param ID: 参数ID（参数分类）
- Param Name: 参数名称（代理使用）
- Param Value: 参数值（代理使用）
| Param Id | Param Name | Param Values | Description |
| --- | --- | --- | --- |
| RFC | SOURCE |  | 从Connector到远程SAP系统的RFC连接。 |
| RFC | TARGET |  | 从远程SAP系统到Connector的RFC连接。 |
| SYSTEM | CPU_CHECK | TRUE/FALSE | 启用或禁用CPU检查。 |
| SYSTEM | MEMORY_CHECK | TRUE/FALSE | 启用或禁用内存检查。 |
| SYSTEM | RESOURCE_CHECK | TRUE/FALSE | 启用或禁用资源检查。如果为FALSE，_所有_检查都被禁用；如果为TRUE，则检查其他参数（CPU_CHECK和MEMORY_CHECK）。 |
| SYSTEM | CONTINUOUS_RESOURCE_CHECK | TRUE/FALSE | 启用所有请求（初始化和所有分页请求）的资源检查。如果为FALSE，仅对初始化请求进行资源检查。 |
| SYSTEM | PROCESS_CHECK | TRUE/FALSE | 启用对允许的最小工作进程数量的检查；与PROCESS_MIN_BG和PROCESS_MIN_DIA一起使用。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_BG | 数值 | SAP应用服务器上可用的最小后台进程数量。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_DIA | 数值 | SAP应用服务器上可用的最小对话进程数量。 |
