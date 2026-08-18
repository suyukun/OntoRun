来源: https://palantir.com/docs/zh/foundry/sap/overview/

# 概述

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概述

Palantir Foundry Connector 2.0 for SAP Applications（“连接器”）是与Diskover Limited ↗合作开发的SAP认证附加组件。

连接器安全地从SAP系统（S/4HANA、ECC、Business Warehouse、SLT Replication Server）捕获数据和元数据，并将其集成到Foundry平台中。连接器安装在SAP应用层，遵循标准SAP安全策略，并使用原生SAP应用逻辑进行数据访问。

- 连接器安装：连接器是一个SAP认证附加组件，使用SAINT（SAP附加组件安装工具）进行安装。
连接器安装：连接器是一个SAP认证附加组件，使用SAINT（SAP附加组件安装工具）进行安装。

- 连接器通过HTTPS暴露访问：连接器通过SICF运行一个Web服务。这允许Foundry数据连接器通过HTTPS请求底层ERP或BW数据。
连接器通过HTTPS暴露访问：连接器通过SICF运行一个Web服务。这允许Foundry数据连接器通过HTTPS请求底层ERP或BW数据。

- 在Foundry中定义数据传输逻辑：数据传输的表、Object、筛选和计划在Foundry中定义，并由Foundry数据连接协调器执行。
在Foundry中定义数据传输逻辑：数据传输的表、Object、筛选和计划在Foundry中定义，并由Foundry数据连接协调器执行。

- 应用层访问：Palantir Foundry将请求发送到SAP NetWeaver应用层，与SAP下运行的数据库无关。没有直接的数据库访问，所有信息访问均来自应用层。
应用层访问：Palantir Foundry将请求发送到SAP NetWeaver应用层，与SAP下运行的数据库无关。没有直接的数据库访问，所有信息访问均来自应用层。

- SAP标准安全：Foundry将使用在SAP内安全授权的SAP用户调用连接器。因此，所有SAP标准安全程序和策略均适用。无需额外维护数据流安全。
SAP标准安全：Foundry将使用在SAP内安全授权的SAP用户调用连接器。因此，所有SAP标准安全程序和策略均适用。无需额外维护数据流安全。

- SAP应用逻辑访问：表、函数、BW InfoProviders和BEx查询都是可用于提取到Foundry的Object。
SAP应用逻辑访问：表、函数、BW InfoProviders和BEx查询都是可用于提取到Foundry的Object。

- 系统负载和可扩展性：连接器在开始提取之前检查系统上的数据负载。如果某些条件不满足，提取将中止。连接器完全符合SAP的可扩展性。连接器可以在同一应用服务器中共存，或者选择性地在保留用于数据处理的单独应用服务器中运行。
系统负载和可扩展性：连接器在开始提取之前检查系统上的数据负载。如果某些条件不满足，提取将中止。连接器完全符合SAP的可扩展性。连接器可以在同一应用服务器中共存，或者选择性地在保留用于数据处理的单独应用服务器中运行。

## 支持的功能

| 功能 | 状态 |
| --- | --- |
| 批量导入 | 🟢 一般可用 |
| 流导入 | 🟢 一般可用 |
| 交互式探索 | 🟢 一般可用 |
| 批量导出 | 🔴 开发中 |
| Webhooks | 🟢 一般可用 |

### 支持的SAP对象类型和系统

- SAP应用表
- SAP BW InfoProviders
- SAP SLT
- SAP BW BEx查询
- SAP ERP提取器
- SAP函数/BAPI
- SAP数据模型
- SAP CDS视图
- SAP HANA信息视图
## 设置指南

### 先决条件

- SAP NetWeaver 7.4 SP5或更高版本
- SAP NetWeaver 7.5（无最低SP级别）
如果您的主要SAP系统运行的NetWeaver应用服务器版本低于7.4 SP5，请参阅远程代理安装以了解如何设置远程连接的详细信息。

### 入门

以下是将您组织的SAP系统连接到Foundry的高级步骤。

- 与您的SAP基础团队合作，决定哪种连接模式最适合您的SAP环境。阅读有关三种连接模式的更多信息。
- 在您的组织网络中为安装代理创建空间。
- 确保代理具有与Foundry通信所需的网络出口。代理将通过的SAP服务器端口是ICM（Internet Communication Manager - SAP NetWeaver应用服务器的一个组件）的默认HTTPS端口。可以通过在SAP系统中运行SMICM事务代码找到端口号。
代理将通过的SAP服务器端口是ICM（Internet Communication Manager - SAP NetWeaver应用服务器的一个组件）的默认HTTPS端口。可以通过在SAP系统中运行SMICM事务代码找到端口号。

- 从Foundry下载连接器附加组件安装包。
- 请相关团队（如您的SAP基础团队）在相关SAP系统上安装Palantir Foundry Connector 2.0 for SAP Applications附加组件。
- 通过数据连接下载代理软件并安装。
- 设置一个源以将代理与SAP系统连接。