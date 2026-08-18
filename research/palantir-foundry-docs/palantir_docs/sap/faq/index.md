来源: https://palantir.com/docs/zh/foundry/sap/faq/

# 常见问题

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 常见问题

本页面详细介绍了有关 Palantir Foundry Connector 2.0 以用于 SAP 应用程序（“Connector”）的一些常见问题。

## 概述

- 建立连接常规问题为什么 Connector 需要在源 SAP 系统的 NetWeaver 应用服务器上安装 ABAP 附加组件？系统与版本Connector 支持哪些 SAP 系统？Connector 支持哪些 SAP 版本？Connector 是否支持 SAP IBP / SAP Ariba / ... ？认证“SAP 认证”到底是什么意思？我在哪里可以找到关于附加组件认证的详细信息？卸载附加组件可以卸载吗？负载与性能我们如何确保 Connector 不会使我们的 SAP 系统过载？许可使用 Connector 是否需要额外的 SAP 许可证？安全所有数据在传输和静止时都加密了吗？附加组件使用了哪些类型的授权角色？如何解决尝试同步数据到 Foundry 时遇到的 SSL 问题？数据集成方法为什么我们应该从源 ERP 提取数据（而不是例如 SAP BW）？
- 常规问题为什么 Connector 需要在源 SAP 系统的 NetWeaver 应用服务器上安装 ABAP 附加组件？
- 为什么 Connector 需要在源 SAP 系统的 NetWeaver 应用服务器上安装 ABAP 附加组件？
- 系统与版本Connector 支持哪些 SAP 系统？Connector 支持哪些 SAP 版本？Connector 是否支持 SAP IBP / SAP Ariba / ... ？
- Connector 支持哪些 SAP 系统？
- Connector 支持哪些 SAP 版本？
- Connector 是否支持 SAP IBP / SAP Ariba / ... ？
- 认证“SAP 认证”到底是什么意思？我在哪里可以找到关于附加组件认证的详细信息？
- “SAP 认证”到底是什么意思？
- 我在哪里可以找到关于附加组件认证的详细信息？
- 卸载附加组件可以卸载吗？
- 附加组件可以卸载吗？
- 负载与性能我们如何确保 Connector 不会使我们的 SAP 系统过载？
- 我们如何确保 Connector 不会使我们的 SAP 系统过载？
- 许可使用 Connector 是否需要额外的 SAP 许可证？
- 使用 Connector 是否需要额外的 SAP 许可证？
- 安全所有数据在传输和静止时都加密了吗？附加组件使用了哪些类型的授权角色？如何解决尝试同步数据到 Foundry 时遇到的 SSL 问题？
- 所有数据在传输和静止时都加密了吗？
- 附加组件使用了哪些类型的授权角色？
- 如何解决尝试同步数据到 Foundry 时遇到的 SSL 问题？
- 数据集成方法为什么我们应该从源 ERP 提取数据（而不是例如 SAP BW）？
- 为什么我们应该从源 ERP 提取数据（而不是例如 SAP BW）？
- 数据提取常规问题可以从 SAP 提取哪些类型的表？在数据提取时，如何将 ABAP 数据类型转换为 Foundry 数据类型？Connector 是否支持提取视图？技术细节在 Foundry 中针对给定的 SAP 源运行数据同步时会发生什么？如何解决以下数据同步出错？变更数据捕获Connector 提供哪些增量同步/变更数据捕获选项？在 SAP 中为任意表/对象设置增量同步时，incrementalField字段的良好选择是什么？为什么从事务类型SNAPSHOT切换到APPEND（以开始增量数据同步）时整个表会被复制？资源检查有哪些类型的资源检查可用？默认行为是什么，我如何覆盖它？SAP 商务仓库（BW）功能支持哪些 SAP BW 功能？敏感数据有什么选项可以确保敏感数据不会离开 SAP 系统，而不妨碍所需非敏感数据的提取？
- 常规问题可以从 SAP 提取哪些类型的表？在数据提取时，如何将 ABAP 数据类型转换为 Foundry 数据类型？Connector 是否支持提取视图？
- 可以从 SAP 提取哪些类型的表？
- 在数据提取时，如何将 ABAP 数据类型转换为 Foundry 数据类型？
- Connector 是否支持提取视图？
- 技术细节在 Foundry 中针对给定的 SAP 源运行数据同步时会发生什么？如何解决以下数据同步出错？
- 在 Foundry 中针对给定的 SAP 源运行数据同步时会发生什么？
- 如何解决以下数据同步出错？
- 变更数据捕获Connector 提供哪些增量同步/变更数据捕获选项？在 SAP 中为任意表/对象设置增量同步时，incrementalField字段的良好选择是什么？为什么从事务类型SNAPSHOT切换到APPEND（以开始增量数据同步）时整个表会被复制？
- Connector 提供哪些增量同步/变更数据捕获选项？
- 在 SAP 中为任意表/对象设置增量同步时，incrementalField字段的良好选择是什么？
- 为什么从事务类型SNAPSHOT切换到APPEND（以开始增量数据同步）时整个表会被复制？
- 资源检查有哪些类型的资源检查可用？默认行为是什么，我如何覆盖它？
- 有哪些类型的资源检查可用？
- 默认行为是什么，我如何覆盖它？
- SAP 商务仓库（BW）功能支持哪些 SAP BW 功能？
- 支持哪些 SAP BW 功能？
- 敏感数据有什么选项可以确保敏感数据不会离开 SAP 系统，而不妨碍所需非敏感数据的提取？
- 有什么选项可以确保敏感数据不会离开 SAP 系统，而不妨碍所需非敏感数据的提取？
- 数据输出技术细节如何从 Foundry 到 SAP 的数据输出得到支持？命名用户归属是否可以以命名用户（而不是技术用户/服务账户）的身份从 Foundry 数据输出到 SAP？
- 技术细节如何从 Foundry 到 SAP 的数据输出得到支持？
- 如何从 Foundry 到 SAP 的数据输出得到支持？
- 命名用户归属是否可以以命名用户（而不是技术用户/服务账户）的身份从 Foundry 数据输出到 SAP？
- 是否可以以命名用户（而不是技术用户/服务账户）的身份从 Foundry 数据输出到 SAP？
- Connector 维护升级如何升级 SAP 附加组件？SAP 附加组件多久会有新版本发布？日常维护SAP 附加组件是否确保其日志表定期截断以避免表空间被占满？
- 升级如何升级 SAP 附加组件？SAP 附加组件多久会有新版本发布？
- 如何升级 SAP 附加组件？
- SAP 附加组件多久会有新版本发布？
- 日常维护SAP 附加组件是否确保其日志表定期截断以避免表空间被占满？
- SAP 附加组件是否确保其日志表定期截断以避免表空间被占满？
## 建立连接

### 常规问题

#### 为什么 Connector 需要在源 SAP 系统的 NetWeaver 应用服务器上安装 ABAP 附加组件？

这种方法有许多好处，包括：

- 能够监控 SAP 资源使用情况以防止系统过载。
- 更广泛地访问/查询 SAP 工件（如视图、BW InfoProviders 和 BEx 查询，而不仅仅是原始数据）。
- 在 Foundry 中提供丰富的源探索体验，大大加快了在 SAP 中查找相关数据的过程，并允许创建批量数据同步。
- 更广泛地支持增量数据同步（变更数据捕获）。
- 更多的调试工具，用于在数据同步失败时调查问题。
### 系统与版本

#### Connector 支持哪些 SAP 系统？

- SAP R/3、SAP ECC 和 SAP S/4HANA
- SAP SLT 复制服务器（用于变更数据捕获）
- SAP BW（包括工具如 APO）
#### Connector 支持哪些 SAP 版本？

SAP 认证的附加组件运行在 NetWeaver 应用服务器上，因此 NetWeaver 版本（也称为 SAP_BASIS 组件版本）最为相关。

我们推荐的最低 NetWeaver 版本如下：

- NetWeaver 7.4 SP5 或以上
- NetWeaver 7.5（无最低 SP 级别）
如果您的主要 SAP 系统运行的 NetWeaver 应用服务器版本低于 7.4，我们有一个解决方案可以暴露 Connector 功能的子集。然而，该解决方案仍然需要一个 NetWeaver 应用服务器版本为 7.4 或更高的服务器作为网关，Foundry 将通过该网关连接到较早版本；此应用服务器可以为空或一个由更新的 SAP 系统（如 BW）使用的服务器。

#### Connector 是否支持 SAP IBP / SAP Ariba / ... ?

如果 SAP 系统或模块运行在 NetWeaver 应用服务器上，则 Connector 将能够从中提取数据。

然而，如果 SAP 系统是基于云的（例如 SAP IBP）或不基于 NetWeaver（如 SAP Ariba），那么此 Connector 不是数据提取的合适解决方案。请联系 Palantir 支持团队以获取从这些系统中提取数据的其他选项。

### 认证

#### “SAP 认证”到底是什么意思？

SAP 认证的官方定义可在SAP 的网站 ↗上找到。

#### 我在哪里可以找到关于附加组件认证的详细信息？

附加组件的认证信息可在SAP 的网站 ↗上找到。

### 卸载

#### 附加组件可以卸载吗？

可以的——卸载是认证过程的一部分。附加组件使用自己的命名空间，卸载时会从 SAP 系统中删除所有内容。唯一遗留的痕迹将在SAINT安装日志中，显示附加组件的安装和卸载时间。

### 负载与性能

#### 我们如何确保 Connector 不会使我们的 SAP 系统过载？

Connector 设计时就将 SAP 系统负载和性能作为首要考虑因素。它提供了一种资源检查功能，旨在确保从 SAP 系统的数据复制不会危及最终用户体验或其他关键流程。

数据提取是分页的，并且在每个页面请求之前，附加组件都会评估内存使用率、CPU 使用率（系统和用户）以及运行的工作进程数量（对话和后台）。如果任何这些指标超出一组完全可配置的阈值，提取将被中止，并在资源可用性可能充足时重试。

此功能被许多大型企业在复杂的生产 SAP 系统环境中使用——在这些环境中，Connector 正在复制数十亿行数据，并且已被证明可以保护这些系统免受可能导致用户中断或其他运行中的过程的过载。

### 许可

#### 使用 Connector 是否需要额外的 SAP 许可证？

由于 Palantir 与 SAP 无关联，无法就您的 SAP 许可证提供法律建议，您需要自行负责评估您对 SAP 系统及 Connector 的现有或潜在使用范围及细节，以及它对您的 SAP 许可证和合同的影响。

根据我们的经验，通过应用层从 SAP ERP 系统定期提取数据可能被视为 SAP 所称的“间接静态读取”，在第三方非 SAP 系统中使用这些数据可能不需要获得许可。然而，用户将数据从第三方非 SAP 系统写回 SAP 时通常可能需要额外的 SAP 许可证。

如有任何顾虑，请咨询您的法律顾问和/或 SAP 代表以讨论您的 SAP 使用和许可证。

### 安全

#### 所有数据在传输和静止时都加密了吗？

是的：从 SAP 到 Data Connection Agent 的数据传输以及从 Agent 到 Foundry 的数据传输均通过 HTTPS 进行；临时存储在 Data Connection Agent 主机上的数据是加密的。

#### 附加组件使用了哪些类型的授权角色？

附加组件使用四种类型的授权角色：

- 服务角色：这些角色是附加组件运行所必需的。请勿修改这些角色。
- 内容角色：这些角色是从 SAP 系统中提取数据所需的。可以根据业务需求通过复制来修改这些角色。
- 数据输出角色：如果启用了从 Foundry 到 SAP 系统的数据输出，则需要这些角色。
- 监控和调试角色：这些角色用于向 Foundry 公开 SAP 系统信息，以实现远程监控。
有关更多详细信息，请参阅Authorization roles。

#### 如何解决尝试同步数据到 Foundry 时遇到的 SSL 问题？

- javax.net.ssl.SSLHandshakeException: PKIX path building failed这意味着 Data Connection Agent 没有足够的信息来验证与 SAP 系统的 HTTPS 连接是否有效。通常，可以通过将相关的 SSL 证书上传到 Data Connection Agent 的信任库来解决此问题。要下载 SSL 证书，请从安装 Data Connection Agent 的（虚拟）机器上运行以下命令（将$HOST和$PORT替换为 SAP 系统的主机和端口号）：openssl s_client -showcerts -servername $HOST -connect $HOST:$PORT </dev/null 2>/dev/null |sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | python3 -c "from sys import stdin; text = stdin.read(); ca_cert = text.split('-----BEGIN CERTIFICATE-----')[-1][:-26]; ca_cert = ca_cert.replace('\n', ''); print('\n' + ca_cert)"注意，这假定openssl和python3已安装在机器上。命令将输出 SSL 证书的长字符串表示形式；将此字符串复制到剪贴板。现在，导航到 Foundry UI 中 Data Connection Agent 的配置页面。点击Agent Settings>Manage agent certificates>Add a new certificate。给证书一个别名（例如它来自的 SAP 系统的名称），并将剪贴板中的证书粘贴到标题为“pem...”的框中。保存更改，然后重启代理。
- 这意味着 Data Connection Agent 没有足够的信息来验证与 SAP 系统的 HTTPS 连接是否有效。
- 通常，可以通过将相关的 SSL 证书上传到 Data Connection Agent 的信任库来解决此问题。
- 要下载 SSL 证书，请从安装 Data Connection Agent 的（虚拟）机器上运行以下命令（将$HOST和$PORT替换为 SAP 系统的主机和端口号）：
```
openssl s_client -showcerts -servername $HOST -connect $HOST:$PORT </dev/null 2>/dev/null |sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | python3 -c "from sys import stdin; text = stdin.read(); ca_cert = text.split('-----BEGIN CERTIFICATE-----')[-1][:-26]; ca_cert = ca_cert.replace('\n', ''); print('\n' + ca_cert)"
```

- 命令将输出 SSL 证书的长字符串表示形式；将此字符串复制到剪贴板。
- 现在，导航到 Foundry UI 中 Data Connection Agent 的配置页面。
- 点击Agent Settings>Manage agent certificates>Add a new certificate。
- 给证书一个别名（例如它来自的 SAP 系统的名称），并将剪贴板中的证书粘贴到标题为“pem...”的框中。
- 保存更改，然后重启代理。
- javax.net.ssl.SSLPeerUnverifiedException: Hostname XXXXX not verified这通常意味着证书没有配置任何 SAN（主题备用名称）。由于使用 CN（通用名称）来验证域已被弃用，我们建议您要求 SAP Basis 团队（或安全团队）使用 SAN 颁发新证书。虽然不推荐，但在非生产环境中，可以在 Foundry 中的 SAP 源配置上使用以下设置以启用旧版主机名验证器：useLegacyHostnameVerifier: true。
- 这通常意味着证书没有配置任何 SAN（主题备用名称）。
- 由于使用 CN（通用名称）来验证域已被弃用，我们建议您要求 SAP Basis 团队（或安全团队）使用 SAN 颁发新证书。
- 虽然不推荐，但在非生产环境中，可以在 Foundry 中的 SAP 源配置上使用以下设置以启用旧版主机名验证器：useLegacyHostnameVerifier: true。
### 数据集成方法

#### 为什么我们应该从源 ERP 提取数据（而不是例如 SAP BW）？

从最细粒度的源数据开始，有助于确保数据集成的下游应用最灵活和有用。使用预处理数据可能看似捷径，但这样做会立即缩小未来可以解决的问题范围。

如果有现有的 BW 报告或查询要使用，一个好的模式是同时提取原始 ERP 数据和 BW 数据。

## 数据提取

### 常规问题

#### 可以从 SAP 提取哪些类型的表？

透明表、池表和聚簇表都可以从 SAP 提取。

#### 在数据提取时，如何将 ABAP 数据类型转换为 Foundry 数据类型？

下表显示了不同类型如何从一个系统映射到另一个系统。

SAP ABAP 数据类型 | Foundry 数据类型 | 描述
--- | --- | ---
ACCP | String | 记账期间
CHAR | String | 固定长度字符字符串
CLNT | String | 客户端字段
CUKY | String | 货币键（由 CURR 引用）
CURR | Decimal | 货币字段
D16D | Decimal | 以 BCD 格式保存的十进制浮点数
D16N | Decimal | 十进制浮点数
D16R | Decimal | 以二进制数保存的十进制浮点数
D16S | Decimal | 带缩放的十进制浮点数（已过时但仍被旧系统使用）
D34D | Decimal | 以 BCD 格式保存的十进制浮点数
D34N | Decimal | 十进制浮点数
D34R | Decimal | 以二进制数保存的十进制浮点数
D34S | Decimal | 带缩放的十进制浮点数（已过时但仍被旧系统使用）
DATN | Date | 格式为 YYYYMMDD 的日期（本地 HANA 类型 DATE）
DATS | Date | 日期值
DEC | Decimal | 有符号固定点十进制数
FLTP | Double | 浮点数
INT1 | Integer | 非常小的有符号精确整数
INT2 | Integer | 小的有符号精确整数
INT4 | Integer | 常规有符号精确整数
LANG | String | 语言键
LCHR | String | 固定长度字符字符串
LRAW | Binary | 未解释的可变长度字节字符串
NUMC | String | 文本字符串
PREC | String | QUAN 字段的精度
QUAN | Decimal | DEC 字段的数量
RAW | Binary | 未解释的字节字符串
RAWSTRING | Binary | 可变长度字符字符串数据
TIMS | String* | 时间值
UNIT | String | 单位键（由 QUAN 引用）

由于 Foundry 没有专用的Time数据类型（与Date或Timestamp区分开来），TIMS类型表示为String。建议在 Foundry 数据变换管道的第一步中，将TIMS类型字段与其相应的DATS类型字段结合，形成新的Date或Timestamp字段。

#### Connector 是否支持提取视图？

SAP 中有几种类型的“视图”：

- ERP 视图：可以使用“ERP 表”对象类型提取；在同步配置的下拉列表中，您将在对象名称旁边看到“VIEW”。
- ABAP CDS 视图：这些视图的支持已在附加组件的 SP21 中添加。
- HANA 信息视图：这些视图的支持已在附加组件的 SP22 中添加。
### 技术细节

#### 在 Foundry 中针对给定的 SAP 源运行数据同步时会发生什么？

当在 Foundry 中针对给定的 SAP 源运行数据同步时，会发生以下步骤：

- 数据连接协调器尝试联系合适的数据连接代理以启动同步。
- 在数据连接代理上运行的 SAP 插件被触发并开始同步过程。
- 向 SAP 附加组件发送的第一个请求是分页初始化请求，这导致 SAP 附加组件查询相关表或对象并开始向/PALANTIR/空间中的表写入数据页面（高度压缩）。
- 向 SAP 附加组件发送的后续请求按顺序轮询数据页面（如果给定页面尚未可用则暂停并重试），直到到达最后一个数据页面——这些数据页面被写为加密的 Apache Parquet 文件在数据连接代理主机上。
- 在检索最后一个数据页面后，向 SAP 附加组件发送分页关闭请求。
- 数据连接代理现在继续将 Apache Parquet 文件上传到 Foundry，直到所有数据都已传输到目标数据集。
#### 如何解决以下数据同步出错？

- 在 SAP 数据中遇到意外值 解析字段 YYY 中的值 XXX 出错如果日期或数字值格式不正确且无法解析，则可能发生这种情况。有关更多详细信息，请参阅忽略意外值。
- 如果日期或数字值格式不正确且无法解析，则可能发生这种情况。有关更多详细信息，请参阅忽略意外值。
- 当前 CPU 用户负载(X%) 高于最大 CPU 用户参数(Y%)，请增加 CPU_USER 阈值！，系统资源低于阈值。当 CPU、内存或工作进程资源检查失败时，您可能会看到此形式的出错。问题在于根据为保护系统免于过载而定义的阈值，相关系统资源不足。有时，这可能是一个理想的结果——正确的解决方案是等待系统负载较轻时再重试同步。然而，也可能是相关资源检查阈值过于保守。要了解如何重新配置阈值，请参阅性能参数。
- 当 CPU、内存或工作进程资源检查失败时，您可能会看到此形式的出错。问题在于根据为保护系统免于过载而定义的阈值，相关系统资源不足。有时，这可能是一个理想的结果——正确的解决方案是等待系统负载较轻时再重试同步。然而，也可能是相关资源检查阈值过于保守。要了解如何重新配置阈值，请参阅性能参数。
- 出错：用户 XXXXX 没有足够的授权进行此服务调用。此出错表示尚未为 SAP 附加组件使用的技术用户生成必要的授权角色，或者角色分配不正确。请查看授权角色。
- 此出错表示尚未为 SAP 附加组件使用的技术用户生成必要的授权角色，或者角色分配不正确。请查看授权角色。
### 变更数据捕获

#### Connector 提供哪些增量同步/变更数据捕获选项？

- SAP SLT 复制服务器（如果可用）数据根据源 ERP 中的触发器复制到 Foundry。
- 数据根据源 ERP 中的触发器复制到 Foundry。
- SAP ERP 或 S/4HANA可以使用 BW 提取器（如果可用）将数据复制到 Foundry，基于提取器管理的增量。附加组件还包括其自己的全面灵活的变更数据捕获方法，可以配置为与各种标准 SAP 表一起使用。有关更多详细信息，请参阅增量更新。
- 可以使用 BW 提取器（如果可用）将数据复制到 Foundry，基于提取器管理的增量。
- 附加组件还包括其自己的全面灵活的变更数据捕获方法，可以配置为与各种标准 SAP 表一起使用。有关更多详细信息，请参阅增量更新。
#### 在 SAP 中为任意表/对象设置增量同步时，incrementalField字段的良好选择是什么？

理想情况下，提供的增量字段应该是单调递增的值；然而，并不总是能找到这样的字段。最佳选择可能是日期字段（不带时间组件）。因此，系统使用“等于或大于”比较（而不仅仅是“大于”），以便如果前一次同步在给定日期的中途运行，也不会遗漏数据。结果，可能会在 Foundry 中的结果数据集中出现重复值。应在 Foundry 中的数据变换管道的第一步中删除这些重复值；例如，通过检查主键的重复行。有关更多详细信息，请参阅增量更新。

#### 为什么从事务类型SNAPSHOT切换到APPEND（以开始增量数据同步）时整个表会被复制？

如果数据同步以SNAPSHOT事务类型开始，则 Connector 不会跟踪任何增量状态。随后切换到APPEND将导致第一次增量同步从 SAP 系统提取所有数据，然后仅继续提取“增量”（自上次同步以来的更改）。因此，建议提前计划哪些数据同步应该是增量的，并以APPEND事务类型开始这些同步。

如果数据集由于从SNAPSHOT切换到APPEND而导致数据重复，请按照重置增量同步步骤进行操作。

### 资源检查

#### 有哪些类型的资源检查可用？

有三种不同的资源检查可用：

- CPU_CHECK：防止同步在 CPU 使用率超过给定阈值时运行
- MEMORY_CHECK：防止同步在内存使用率超过给定阈值时运行
- PROCESS_CHECK：防止同步在可用进程数量低于给定阈值时运行
#### 默认行为是什么，我如何覆盖它？

默认情况下，所有资源检查都开启并且这些资源检查是“连续”应用的，这意味着在每个页面请求之前都会进行检查，而不仅仅是在同步开始时。

要在单个数据同步级别覆盖默认行为，请在 Data Connection UI 中执行以下步骤：Extras>Resource Check/Continuous Resource Check>Off。

### SAP 商务仓库（BW）功能

#### 支持哪些 SAP BW 功能？

数据可以从以下位置提取：

- SAP BW InfoProviders——包括数据存储对象（DSOs）、InfoCubes 和 InfoObjects
- SAP BW BEx 查询
### 敏感数据

#### 有什么选项可以确保敏感数据不会离开 SAP 系统，而不妨碍所需非敏感数据的提取？

在最高级别上，可以修改附加组件的内容授权角色，以防止提取整个表或对象。

在行级别限制可以提取的数据可以使用筛选器来实现，这些筛选器在数据离开 SAP 系统之前应用：

- 筛选器可以在 Foundry 中的 Data Connection UI 中的同步配置中定义。
- 然而，也可以在 SAP 系统本身的 Connector Cockpit 中设置“预筛选器”——这些筛选器将应用于表以及任何来自 Foundry 的筛选器，这意味着它们也将适用于在 Source Explorer 和同步配置 UI 中显示的数据预览。有关更多详细信息，请参阅Prefilters。
通过列限制数据提取有两种方法（如上所述的筛选方法一样，这些方法在数据离开 SAP 系统之前应用）：

- 同步配置 UI 提供了“删除列”功能，以选择从数据提取中排除哪些列。
- Connector Cockpit 提供了一系列加密和数据掩码配置。
## 数据输出

### 技术细节

#### 如何从 Foundry 到 SAP 的数据输出得到支持？

SAP 认证的附加组件提供了从 Foundry 调用 SAP 函数的支持。推荐使用 BAPI（业务 API）函数，因为它们具有良好定义的结构和清晰的失败消息，但附加组件支持调用任何类型的函数模块（如果需要）。

要设置数据输出，您需要创建一个 Foundry Webhook。有关更多详细信息，请参阅Webhooks以获取概述以及Webhook Configuration - SAP以获取 SAP 特定详细信息。

### 命名用户归属

#### 是否可以以命名用户（而不是技术用户/服务账户）的身份从 Foundry 数据输出到 SAP？

可以——这可以通过使用 OAuth 2.0 授权码流来支持。在此场景中，SAP 系统充当 OAuth 2.0 服务器，Foundry 充当 OAuth 2.0 客户端。当用户首次尝试从 Foundry 数据输出到 SAP 时，他们将被重定向到 SAP 系统中的授权对话框，以确认他们愿意允许 Foundry 代表他们将数据输出到 SAP。

有关更多详细信息，请参阅用户归属的 SAP 数据输出与 OAuth 2.0。

## Connector 维护

### 升级

#### 如何升级 SAP 附加组件？

您将获得新的支持包（SP）。请按照升级的文档说明。

#### SAP 附加组件多久会有新版本发布？

没有固定的发布计划，但通常每 2-3 个月会交付一个新的支持包（SP）。

### 日常维护

#### SAP 附加组件是否确保其日志表定期截断以避免表空间被占满？

是的，但您需要启用相关的日常维护任务，因为这些任务不能由SAINT安装过程自动开启。有关更多详细信息，请参阅设置和配置日常维护任务。
