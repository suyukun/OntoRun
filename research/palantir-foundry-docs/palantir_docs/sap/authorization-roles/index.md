来源: https://palantir.com/docs/zh/foundry/sap/authorization-roles/

# 授权角色

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 授权角色

## 概述

Palantir Foundry Connector 2.0 for SAP ("Connector") 使用四种类型的角色。

- 服务角色: 这些角色是 Connector 运行所必需的。不要修改这些角色。/PALANTIR/SERVICE_SLT: Palantir SLT 服务角色/PALANTIR/SERVICE_SLT_740: Palantir NetWeaver 7.4 服务角色/PALANTIR/SERVICE_USER: Palantir 服务角色
- /PALANTIR/SERVICE_SLT: Palantir SLT 服务角色
- /PALANTIR/SERVICE_SLT_740: Palantir NetWeaver 7.4 服务角色
- /PALANTIR/SERVICE_USER: Palantir 服务角色
- 内容角色: 这些角色是从 SAP 系统中提取数据所必需的。这些角色可以根据业务需求复制和修改。/PALANTIR/CONTENT_BEX_ALL: BEx 访问角色/PALANTIR/CONTENT_DM_ALL: 数据模型访问角色/PALANTIR/CONTENT_EXT_ALL: 提取器内容访问/PALANTIR/CONTENT_FUNCTION_ALL: 函数访问角色/PALANTIR/CONTENT_INFOPROV_ALL: InfoProvider 内容访问/PALANTIR/CONTENT_SLT_ALL: SLT 访问角色/PALANTIR/CONTENT_TABLE_ALL: 表内容访问/PALANTIR/CONTENT_TCODE_ALL: 事务代码内容访问/PALANTIR/CONTENT_HANAVIEW_ALL: HANA 信息视图内容访问/PALANTIR/CONTENT_CDS_ALL: ABAP CDS 视图内容访问
- /PALANTIR/CONTENT_BEX_ALL: BEx 访问角色
- /PALANTIR/CONTENT_DM_ALL: 数据模型访问角色
- /PALANTIR/CONTENT_EXT_ALL: 提取器内容访问
- /PALANTIR/CONTENT_FUNCTION_ALL: 函数访问角色
- /PALANTIR/CONTENT_INFOPROV_ALL: InfoProvider 内容访问
- /PALANTIR/CONTENT_SLT_ALL: SLT 访问角色
- /PALANTIR/CONTENT_TABLE_ALL: 表内容访问
- /PALANTIR/CONTENT_TCODE_ALL: 事务代码内容访问
- /PALANTIR/CONTENT_HANAVIEW_ALL: HANA 信息视图内容访问
- /PALANTIR/CONTENT_CDS_ALL: ABAP CDS 视图内容访问
- 数据输出角色: 如果启用了从 Foundry 到 SAP 系统的数据输出，则需要这些角色。/PALANTIR/OAUTH_CLIENT: Palantir Foundry OAuth 2.0 客户端角色
- /PALANTIR/OAUTH_CLIENT: Palantir Foundry OAuth 2.0 客户端角色
- 监控和调试角色: 这些角色是将 SAP 系统信息暴露给 Foundry 以实现远程监控所必需的。/PALANTIR/MONITORING: 监控/PALANTIR/DEBUG_USER: 调试用户访问
- /PALANTIR/MONITORING: 监控
- /PALANTIR/DEBUG_USER: 调试用户访问
## 服务角色

- /PALANTIR/SERVICE_USER: 这是用户运行 Connector 服务的基本角色。每次请求 Connector 时都会检查此角色。此角色中的授权对象如下：/PALAU/SRV: Palantir 服务授权对象，具有 03（显示）和 16（执行）活动。S_BTCH_JOB:（后台处理：后台任务的操作）Connector 运行后台任务（例如，分页或房屋清洁操作）；因此需要此授权对象。S_TCODE:（事务开始时的事务代码检查）这仅适用于 SU53 和 ST22 事务（SAP 中的授权检查工具和运行时错误），需要用于调试和正确的日志记录机制。S_RFC_ADM:（RFC 目标的管理）此对象用于 36（检查）和 39（扩展检查）活动，以确定 RFC 连接是否正常以及授权测试是否已检查。S_RFC:（RFC 访问的授权检查）此对象用于在 SLT 和远程代理场景中以 16（执行）活动运行远程函数调用。/SDF/E2E:（端到端诊断的授权）此对象用于从 Foundry 运行提取过程的跟踪，具有 03（显示）活动。S_ADMI_FCD:（系统授权）此对象用于使用 PADM（使用事务 SM04、SM50 进行进程管理）、ST0R（分析跟踪）、ST22（跨客户端转储分析）进行检查和跟踪。S_BTCH_JOB:（后台处理：后台任务的操作）此对象用于将 Connector 提取作为后台任务运行，除 MODI（修改其他用户的任务）外的所有活动。S_DATASET:（文件访问授权）此对象用于通过使用 SAP 中的 SAT 生成和访问跟踪文件，具有 33（读取）、A6（带筛选读取）、A7（带筛选写入）活动。S_TABU_NAM:（通过通用标准工具访问表）此对象用于访问 /PAL*、DMC*、IUUC* 表，具有 03（显示）活动。S_TABU_DIS:（表维护（通过标准工具如 SM30））此对象用于访问表，具有 03（显示）活动。
- /PALAU/SRV: Palantir 服务授权对象，具有 03（显示）和 16（执行）活动。
- S_BTCH_JOB:（后台处理：后台任务的操作）Connector 运行后台任务（例如，分页或房屋清洁操作）；因此需要此授权对象。
- S_TCODE:（事务开始时的事务代码检查）这仅适用于 SU53 和 ST22 事务（SAP 中的授权检查工具和运行时错误），需要用于调试和正确的日志记录机制。
- S_RFC_ADM:（RFC 目标的管理）此对象用于 36（检查）和 39（扩展检查）活动，以确定 RFC 连接是否正常以及授权测试是否已检查。
- S_RFC:（RFC 访问的授权检查）此对象用于在 SLT 和远程代理场景中以 16（执行）活动运行远程函数调用。
- /SDF/E2E:（端到端诊断的授权）此对象用于从 Foundry 运行提取过程的跟踪，具有 03（显示）活动。
- S_ADMI_FCD:（系统授权）此对象用于使用 PADM（使用事务 SM04、SM50 进行进程管理）、ST0R（分析跟踪）、ST22（跨客户端转储分析）进行检查和跟踪。
- S_BTCH_JOB:（后台处理：后台任务的操作）此对象用于将 Connector 提取作为后台任务运行，除 MODI（修改其他用户的任务）外的所有活动。
- S_DATASET:（文件访问授权）此对象用于通过使用 SAP 中的 SAT 生成和访问跟踪文件，具有 33（读取）、A6（带筛选读取）、A7（带筛选写入）活动。
- S_TABU_NAM:（通过通用标准工具访问表）此对象用于访问 /PAL*、DMC*、IUUC* 表，具有 03（显示）活动。
- S_TABU_DIS:（表维护（通过标准工具如 SM30））此对象用于访问表，具有 03（显示）活动。
以下角色仅在您连接到 SAP Landscape Transformation Replication Server 时需要：

- /PALANTIR/SERVICE_SLT: 运行 SLT API 所需的角色。此角色中的授权对象如下：S_DMIS:（SAP SLO 数据迁移服务器的授权对象）此对象限制为 03（显示）活动，以检查 API 端点并调用它们。
- S_DMIS:（SAP SLO 数据迁移服务器的授权对象）此对象限制为 03（显示）活动，以检查 API 端点并调用它们。
- /PALANTIR/SERVICE_SLT_740: 如果 SAP SLT 在 NetWeaver 7.4+ 上运行，则需要其他授权对象。这些对象如下：S_DMC_S_R:（MWB：在发送方/接收方中的读取/写入授权）此对象用于访问 Foundry 的 SLT 队列。S_BTCH_ADM:（后台处理：后台管理员）此对象代表 SAP SLT 管理 Connector 的后台任务，例如复制对象定义、复制过程对象以及启动到 SLT 队列的复制。S_DMIS:（SAP SLO 数据迁移服务器的授权对象）此对象限制为 03（显示）活动，以检查 API 端点并调用它们。S_DMIS_MOM:（MWB/迁移对象建模器的授权）
- S_DMC_S_R:（MWB：在发送方/接收方中的读取/写入授权）此对象用于访问 Foundry 的 SLT 队列。
- S_BTCH_ADM:（后台处理：后台管理员）此对象代表 SAP SLT 管理 Connector 的后台任务，例如复制对象定义、复制过程对象以及启动到 SLT 队列的复制。
- S_DMIS:（SAP SLO 数据迁移服务器的授权对象）此对象限制为 03（显示）活动，以检查 API 端点并调用它们。
- S_DMIS_MOM:（MWB/迁移对象建模器的授权）
## 内容角色

这些角色作为示例提供。通过复制这些角色并限制对系统中所需对象的访问来调整授权配置文件的内容。

### Connector 的角色

- /PALANTIR/CONTENT_TABLE_ALL: 需要此角色才能从数据库表和视图中提取数据。/PALAU/TAB: Palantir 表授权对象：默认情况下允许所有表，使用*通配符。
- /PALAU/TAB: Palantir 表授权对象：默认情况下允许所有表，使用*通配符。
- /PALANTIR/CONTENT_DM_ALL: 需要此角色才能从数据库表中提取数据模型。/PALAU/DMO: Palantir 数据模型授权对象：默认情况下允许所有表，使用*通配符。
- /PALAU/DMO: Palantir 数据模型授权对象：默认情况下允许所有表，使用*通配符。
- /PALANTIR/CONTENT_FUNCTION_ALL: 需要此角色才能从 SAP 系统中运行 RFC 函数。可能需要额外的授权，具体取决于所使用的业务功能。/PALAU/FUN: Palantir 函数授权对象：默认情况下允许所有函数，使用*通配符。
- /PALAU/FUN: Palantir 函数授权对象：默认情况下允许所有函数，使用*通配符。
- /PALANTIR/CONTENT_TCODE_ALL: 需要此角色才能从 SAP 系统中运行事务代码（ALV SE38 报告）。可能需要额外的授权，具体取决于所使用的业务功能。/PALAU/TCO: Palantir 事务代码授权对象：默认情况下允许所有事务代码，使用*通配符。
- /PALAU/TCO: Palantir 事务代码授权对象：默认情况下允许所有事务代码，使用*通配符。
- /PALANTIR/CONTENT_HANANVIEW_ALL: 需要此角色才能从 HANA 信息视图中提取数据。/PALAU/HAN: Palantir HANA 授权对象：默认情况下允许所有 HANA 信息视图，使用*通配符。
- /PALAU/HAN: Palantir HANA 授权对象：默认情况下允许所有 HANA 信息视图，使用*通配符。
- /PALANTIR/CONTENT_CDS_ALL: 需要此角色才能从 ABAP CDS 视图中提取数据。/PALAU/CDS: Palantir CDS 授权对象：默认情况下允许所有 CDS 视图，使用*通配符。
- /PALAU/CDS: Palantir CDS 授权对象：默认情况下允许所有 CDS 视图，使用*通配符。
以下角色仅在您连接到 SAP 商务仓库（BW）服务器时需要：

- /PALANTIR/CONTENT_BEX_ALL: 需要此角色才能从 SAP BW（商务仓库）BEx 查询中提取数据。/PALAU/BEX:（Palantir BEx 授权对象）：默认情况下允许所有 BEx 查询，使用*通配符。
- /PALAU/BEX:（Palantir BEx 授权对象）：默认情况下允许所有 BEx 查询，使用*通配符。
- /PALANTIR/CONTENT_EXT_ALL: 需要此角色才能从 SAP BW（商务仓库）提取器（已启用 ODP）中提取数据。/PALAU/EXT: Palantir 提取器授权对象：默认情况下允许所有已启用 ODP 的提取器，使用*通配符。
- /PALAU/EXT: Palantir 提取器授权对象：默认情况下允许所有已启用 ODP 的提取器，使用*通配符。
- /PALANTIR/CONTENT_INFOPROV_ALL: 需要此角色才能从 SAP BW（商务仓库）InfoProviders 中提取数据。/PALAU/INF: Palantir InfoProvider 授权对象：默认情况下允许所有 InfoProviders，使用*通配符。S_RS_AUTH: 角色中的 BI 分析授权：这是 BW 系统中的所有分析授权。请根据需要调整。S_RS_COMP: 商务智能 - 组件：这是 BW 系统中的所有 BEx 对象授权。请根据需要调整。S_RS_COMP1: 商务智能 - 组件：对所有者的增强：这是 BW 系统中的所有 BEx 对象授权。请根据需要调整。
- /PALAU/INF: Palantir InfoProvider 授权对象：默认情况下允许所有 InfoProviders，使用*通配符。
- S_RS_AUTH: 角色中的 BI 分析授权：这是 BW 系统中的所有分析授权。请根据需要调整。
- S_RS_COMP: 商务智能 - 组件：这是 BW 系统中的所有 BEx 对象授权。请根据需要调整。
- S_RS_COMP1: 商务智能 - 组件：对所有者的增强：这是 BW 系统中的所有 BEx 对象授权。请根据需要调整。
以下角色仅在您连接到 SAP Landscape Transformation (SLT) Replication Server 时需要：

- /PALANTIR/CONTENT_SLT_ALL: 需要此角色才能从将表从连接的系统复制到 SAP SLT 的 SLT 队列中提取数据。/PALAU/SLT:（Palantir SLT 授权对象）：默认情况下允许所有表，使用*通配符。
- /PALAU/SLT:（Palantir SLT 授权对象）：默认情况下允许所有表，使用*通配符。
## 数据输出角色

- /PALANTIR/OAUTH_CLIENT: 启用从 Foundry 到 SAP 系统的数据输出时需要此角色。它提供 OAuth 2.0 配置所需的授权对象。S_SERVICE: 外部服务启动时检查。这些服务受限于/PALANTIR/*服务。S_OA2C_ADM: OAuth 2.0 客户端配置S_OA2C_USE: OAuth 2.0 客户端使用S_SCOPE: OAuth 2.0 范围。此角色仅限于/PALANTIR/SRV_0001范围，用于使用 SAP 函数的 Palantir Foundry 数据输出。
- S_SERVICE: 外部服务启动时检查。这些服务受限于/PALANTIR/*服务。
- S_OA2C_ADM: OAuth 2.0 客户端配置
- S_OA2C_USE: OAuth 2.0 客户端使用
- S_SCOPE: OAuth 2.0 范围。此角色仅限于/PALANTIR/SRV_0001范围，用于使用 SAP 函数的 Palantir Foundry 数据输出。
## 监控和调试的角色

- /PALANTIR/MONITORING: 启用通过 Connector 远程监控 SAP 系统所需的角色。它提供广泛的系统信息，如运行时错误分析（ST22）、SAP 系统日志（SM21）、SAP 后台任务监控（SM37）、授权分析（SU53）、互联网通信管理器（ICM）、系统资源监控（ST02、ST06）、SAP SLT 控制台（LTRC）、SAP SLT 操作 Delta 队列监控（ODQMON）。
- /PALANTIR/DEBUG_USER: 在发生事件时，Palantir 支持所需的角色；开发人员可能需要在 SAP 系统中调试问题。此角色收集 Connector 开发团队所需的所有授权对象。
## 远程代理角色

远程代理角色与主 Connector 的相应角色相同。这些角色可以在安装 Connector 远程代理的远程系统中维护。

### NetWeaver 7.0 及以上的角色

- /PALANTIR/CONTENT_RBEX_ALL: 远程 BEx 内容访问
- /PALANTIR/CONTENT_RFUNCT_ALL: 远程函数内容访问
- /PALANTIR/CONTENT_RTCODE_ALL: 远程事务代码内容访问
- /PALANTIR/CONTENT_RINFOPRV_ALL: 远程 InfoProvider 内容访问
- /PALANTIR/CONTENT_RTABLE_ALL: 远程表内容访问
- /PALANTIR/SERVICE_USER: Palantir 服务角色
### 版本 46C、620 或 640 的基础发布的角色

- /PALAGT47/CONTENT_RTABLE_ALL: 远程表内容访问
- /PALAGT47/SERVICE_USER: Palantir 服务角色