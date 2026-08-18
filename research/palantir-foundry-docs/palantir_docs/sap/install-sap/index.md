来源: https://palantir.com/docs/zh/foundry/sap/install-sap/

# SAP 附加组件的安装

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# SAP 附加组件的安装

Palantir Foundry Connector 2.0 for SAP Applications ("Connector") 是一个基于 ABAP 的数据提取接口，由Diskover Limited ↗合作开发，用于将 SAP 系统中的数据集成到 Palantir Foundry。Connector 在 SAP NetWeaver 应用服务器上运行，并通过 REST API 调用以 HTTPS 提供数据。

Connector 可用于将数据从 SAP 直接同步到 Foundry，探索 SAP 中的数据，并通过远程函数将数据写入 SAP。

Connector 由三个应用组件组成：

- PALANTIR：Palantir 基础组件包含PALCONN (Connector)和PALAGENT (Remote Agent)所需的所有共享对象。因此，PALANTIR组件是PALCONN和PALAGENT组件的前提条件。
- PALCONN：Palantir Foundry Connector 应用组件包含所有连接器相关对象和服务。此组件不适用于远程代理，不能安装在 SAP NetWeaver 7.4 SP05 以下。
- PALAGENT：Palantir Foundry 远程代理应用组件包含所有远程代理相关对象和服务，以从运行在 NetWeaver 7.4 SP05 以下的 SAP 应用程序中摄取数据。NetWeaver 7.4 SP5 以下的系统必须通过运行 NetWeaver 7.4 SP5 或更高版本并安装了PALCONN组件的系统远程访问。
在安装到生产环境之前，请将附加组件安装到开发或沙箱系统并彻底测试。

## 安装场景

Connector 有三种安装场景可用。

对于所有场景，确保已下载相关的安装包后继续。

#### 独立安装

Connector 可以直接安装在源 SAP 系统上。在此场景中支持以下对象类型：

- SAP 表和视图
- InfoProviders
- BEx 查询
- SAP 业务内容提取器
- SAP 函数 / BAPIs
- SAP 基于 ABAP 的 CDS 视图
- 通过 SAP 函数的数据输出（可选地使用 OAuth 2.0 进行用户归属）
对于此场景，请按照以下指南操作：

- 安装 Connector
#### SLT 安装

在此场景中，Connector 安装在 SAP SLT 复制服务器上。

在这种情况下，仅支持 SLT 对象类型。

对于此场景，请按照以下指南操作：

- 安装 Connector
- 配置 SAP SLT
#### 远程代理安装

源 ERP 系统可能不符合 Connector 的安装要求。在此场景中，应部署一个版本为 7.4 SP5 或更高版本的 SAP NetWeaver 应用服务器作为源 SAP 系统的网关。Connector 应安装在网关服务器上，在那里它将通过 RFC 连接与源 ERP 系统通信，并通过 HTTPS 向 Foundry 提供数据。Connector 的远程代理应安装在源 ERP 系统上，以响应来自 Connector 的请求。

对于此场景，请按照以下指南操作：

- 使用主要安装指南将 Connector 安装到网关服务器
- 安装远程代理
如果源 ERP 系统低于 SAP NetWeaver 版本 7.0 SP32，请按照以下指南操作：

- 为 ERP 4.6C/4.7 (620/640) 安装远程代理
## 支持包和修复包

Connector 的新功能和产品修复作为支持包交付。要应用支持包，请按照以下步骤操作：

- 安装支持包
有时，Connector 的产品修复是在支持包生命周期之外交付的。在这些情况下，请按照以下说明操作：

- 安装修复包