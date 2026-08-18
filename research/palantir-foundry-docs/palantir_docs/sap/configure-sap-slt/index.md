来源: https://palantir.com/docs/zh/foundry/sap/configure-sap-slt/

# 配置 SLT（SAP Landscape Transformation Replication Server）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 配置 SLT（SAP Landscape Transformation Replication Server）

SAP Landscape Transformation Replication Server（SLT）是一种数据复制工具，使用数据库触发器进行变更数据捕获（CDC），从而实现从源SAP系统到目标系统的高效数据复制。

SLT和Palantir Foundry Connector 2.0 for SAP Applications（“连接器”）可以配置为协同工作，以实现从SAP到Foundry的CDC复制。

在此设置中，将使用专用上下文（队列别名）创建SLT配置。

要将SAP表复制到Foundry，每个Object都将配置Foundry数据集同步。一旦配置了数据集同步，SLT将在相关SAP Object上配置触发器，SAP中该Object的更改将被捕获并存储在SLT服务器的队列中，用于ODP（Operational Data Provisioning）场景。Foundry将根据预配置的计划轮询此队列，以同步这些更改到Foundry数据集。

当首次为SAP Object配置Foundry数据集同步时，SLT将执行全量加载。后续触发器将仅获取该Object的更改。SLT队列的清理由SLT管理。

您还可以配置Foundry数据集同步以让SLT对特定SAP Object执行全量加载（快照），而不是以CDC模式（增量）运行。

本指南假定连接器已安装在实例上。您可以查看连接器安装说明。

## 先决条件

- Connector安装需要SAP NetWeaver 7.4 SP14+
- SAP SLT和源系统需要DMIS 2011_1_730组件SP15+
- 允许所有质量传输ID（MTID）的1复制的SAP SLT配置
确保在SLT系统上实施了以下SAP注释：

- SAP OSS Note1660374–获取等待时间不够长；超时
- SAP OSS Note2215583–从ODQ提取数据时由于数据内容移动出错
确保已阅读以下SAP注释，并在适用的情况下遵循相关步骤：

- SAP OSS Note2697016–无法在CNV_IUUC_DB_CONN131中复制表 - 其他配置具有不同的触发器设置 - SAP Landscape Transformation Replication Server。
- SAP OSS Note2787584-尽管用户拥有SAP_ALL，在LTRC中授权问题 - SLT
- SAP OSS Note3032108-支持1复制吗？- SLT
在SAP SLT场景中，旧版DMIS版本中表的注册最多为1:4（最多4个消费者）。从DMIS 2018 SP4开始，SAP的新CDC功能被启用，不再限制允许的消费者数量。

使用SLT的连接器可能会对SAP系统的资源要求较高。因此，在开始复制之前，应查看官方SAP的SLT尺寸文档。在从SAP环境开始数据提取之前，请确保SLT服务器（以及如果SLT和连接器在不同服务器上，连接器安装的SAP应用服务器）上有空闲的后台和对话进程。

- 前往事务SM50查看是否有空闲的后台和对话进程。如果没有空闲进程，传输数据到Foundry将失败。
- 有关系统尺寸的更多指导，请参阅官方SAPSLT尺寸指南 ↗。
## SLT配置

步骤2a和2b只需其中之一。我们建议遵循步骤2a并使用后安装向导。步骤3和4仅在远程SLT场景中需要。

- 1. 创建到源系统的RFC目标连接
- 2a. 推荐：使用后安装向导为源系统创建SLT配置
- 2b. 使用SLT工具为源系统创建SLT配置
- 3. 创建到连接器的RFC目标连接（远程SLT场景）
- 4. 配置连接器以使用SAP SLT（远程SLT场景）
### 1. 创建到源系统的RFC目标连接

要创建SLT将用于从SAP源系统复制数据的远程函数调用（RFC）连接，请参阅创建RFC连接。

### 2a. 使用后安装向导为源系统创建SLT配置

要使用连接器后安装向导创建SLT配置，使用/n/PALANTIR/POST_INST事务码并仅启用步骤7创建SLT配置。SLT配置的参数如下：

| 参数 | 描述 |
| --- | --- |
| Context Name | 唯一的配置名称 |
| Context Description | 将在SAP事务LTRC和Foundry中显示给用户的上下文描述 |
| Data Transfer Jobs | 数据传输任务的数量 |
| Initial Load Jobs | 初始加载任务的数量 |
| Calculation Jobs | 初始加载范围计算的计算任务数量 |
| Authorization Group | 默认无授权组 |
| Source RFC Destination | 逻辑目的地 - 源系统的RFC目的地名称 |
| Read from Single Client | 如果数据将从单个客户端读取，请选中此选项 |
| Allow Multiple Usage | 如果允许多次使用，请选中此选项 |

### 2b. 使用SLT工具为源系统创建SLT配置

步骤2a和2b只需其中之一。我们建议使用步骤2a中详细介绍的后安装向导。

- 要创建SLT配置，使用LTRC事务码。
要创建SLT配置，使用LTRC事务码。

- 创建新配置。
创建新配置。

- 在常规数据部分，填写配置名称和描述。
在常规数据部分，填写配置名称和描述。

- 在源系统部分：选择RFC连接。选择我们之前创建的RFC目的地连接（例如，我们的示例中为SAP_SOURCE）。在配置源时不要被“RFC目标”这个名称所迷惑——您应该在此设置中选择源系统的连接。启用允许多次使用。此设置允许多个订阅者从源系统中检索复制的数据，配置创建后无法更改。如果仅使用一个订阅者，允许多次使用不会产生影响，因此我们建议在首次配置时启用。稍后启用多次使用需要您删除配置并创建新配置。在生产环境中，启用从单一客户端读取。使用的客户端号码将在RFC连接中定义。此设置将确保仅生产数据被复制到Foundry。在现有SLT环境中，所有配置应具有相同的设置。因此，请查看SAP OSS Note2372636 - 当存在不同的触发器选项时无法复制数据 - SLT。
在源系统部分：

- 选择RFC连接。
- 选择我们之前创建的RFC目的地连接（例如，我们的示例中为SAP_SOURCE）。
在配置源时不要被“RFC目标”这个名称所迷惑——您应该在此设置中选择源系统的连接。

- 启用允许多次使用。
此设置允许多个订阅者从源系统中检索复制的数据，配置创建后无法更改。如果仅使用一个订阅者，允许多次使用不会产生影响，因此我们建议在首次配置时启用。稍后启用多次使用需要您删除配置并创建新配置。

- 在生产环境中，启用从单一客户端读取。使用的客户端号码将在RFC连接中定义。此设置将确保仅生产数据被复制到Foundry。在现有SLT环境中，所有配置应具有相同的设置。因此，请查看SAP OSS Note2372636 - 当存在不同的触发器选项时无法复制数据 - SLT。
- 在目标系统部分：选择RFC连接。为场景选择操作数据供应（ODP）。对于较高支持包级别的SAP NetWeaver，该场景在其他下列出，而不是RFC连接。将RFC目标设置为NONE。设置任何别名作为队列别名。最好命名队列，以显示源系统SAP系统ID（SID）。此队列别名在后续定义Foundry数据集同步时用作上下文。
在目标系统部分：

- 选择RFC连接。
- 为场景选择操作数据供应（ODP）。对于较高支持包级别的SAP NetWeaver，该场景在其他下列出，而不是RFC连接。
- 将RFC目标设置为NONE。
- 设置任何别名作为队列别名。最好命名队列，以显示源系统SAP系统ID（SID）。此队列别名在后续定义Foundry数据集同步时用作上下文。
- 在数据传输设置部分，设置要在SAP SLT服务器上运行的数据传输任务、初始加载任务和数据计算任务的数量。有关复杂场景所需任务数量的更多信息，请参阅SLT尺寸指南 ↗。
在数据传输设置部分，设置要在SAP SLT服务器上运行的数据传输任务、初始加载任务和数据计算任务的数量。有关复杂场景所需任务数量的更多信息，请参阅SLT尺寸指南 ↗。

- 审核并创建连接。
审核并创建连接。

- 返回SLT主屏幕，对于事务码LTRC，确保在SLT系统上为ODP场景激活了BAdI实现。要检查设置，选择配置名称打开配置，然后单击专家功能选项卡。确保BAdI实现已激活，否则ODP将无法正常工作。
返回SLT主屏幕，对于事务码LTRC，确保在SLT系统上为ODP场景激活了BAdI实现。要检查设置，选择配置名称打开配置，然后单击专家功能选项卡。确保BAdI实现已激活，否则ODP将无法正常工作。

- 从主菜单进入SA38事务。根据SAP OSS Note1660374 - 获取等待时间不够长；超时的描述，运行程序SAP_RSADMIN_MAINTAIN设置参数RODPS_FETCH_TIMEOUT。指定值（秒）。
从主菜单进入SA38事务。根据SAP OSS Note1660374 - 获取等待时间不够长；超时的描述，运行程序SAP_RSADMIN_MAINTAIN设置参数RODPS_FETCH_TIMEOUT。指定值（秒）。

### 3. 创建到连接器的RFC目标连接（远程SLT场景）

连接器可以部署在满足要求的单独SAP实例上。在这种情况下，连接器通过RFC连接与SLT服务器通信。因此，需要一个RFC连接来启用通信通道。

有关设置说明，请参阅RFC连接指南。

### 4. 配置连接器以使用SAP SLT（远程SLT场景）

如果SLT和连接器在不同实例上，请按照以下额外的配置步骤：

- 打开事务/n/PALANTIR/PARAM
- 输入以下参数值：参数ID：SLT参数名称：RFC_CONFIGURATION参数值：在本节开头创建的RFC配置名称（例如，SLT_SERVER_RFC）
- 参数ID：SLT
- 参数名称：RFC_CONFIGURATION
- 参数值：在本节开头创建的RFC配置名称（例如，SLT_SERVER_RFC）
如果这些参数未在配置表中设置，它们将默认为以下值：

- 时间戳：OFF
- fetchOption：XML
- pageSize：50000
## 大表同步的性能考虑

连接器使用SAP的ODP框架将数据复制到Foundry。ODP将数据从源系统复制到ODP队列（表名ODQDATA_F）。数据在ODQ中暂存，一旦数据被传输到ODP队列，连接器将开始将请求的数据分页到/PALANTIR/PAG_01和/PALANTIR/PAG_02表。在将所有页面成功传输到Foundry后，Foundry发送关闭请求以管理表，并且此关闭请求会删除/PALANTIR/PAG*表中的条目。

在运行初始（例如，历史或批量）同步时，请仔细查看数据库尺寸并考虑空间需求。空间不足可能导致SLT复制任务失败和传输到Foundry，因此首先根据要复制的表进行数据库尺寸准备。

## 用于解决已知SAP问题的参数

还有两个参数用于解决SAP中已知的问题。

### 问题：SAP SLT服务器未提供日期/时间字段的确切字段长度

问题：SAP SLT服务器未提供日期/时间字段的确切字段长度。此问题已通过SAP注释修复。然而，如果您确实遇到任何关于数据类型长度的问题，可以在注释实施之前设置以下参数：

- 参数ID =SLT
- 参数名称 =SLT_DATA_XXX(XXX指字段的技术名称)
- 参数值 =数据类型的长度
在SAP NetWeaver的早期支持包（SP 14）中，DATS字段被SAP设置为16个字符。然而，DATS字段应为8个字符（YYYYMMDD）。TIMS字段也被SAP设置为16个字符；TIMS数据应为6个字符（HHMMSS）。

为了解决此问题，请设置以下参数：

| 参数Id | 参数名称 | 参数值 |
| --- | --- | --- |
| SLT | SLT_DATA_DATS | 8 |
| SLT | SLT_DATA_TIMS | 6 |

### 问题：SAP QUAN数据类型没有3个小数位

问题：SAP有特定的数据类型用于数量和金额。数量数据类型QUAN默认包含3个小数位。当连接器尝试获取包含QUAN数据类型的数据时，它会自动为这些QUAN数据类型创建3个小数位。然而，某些包含QUAN数据类型的SAP表具有不同数量的小数位，但传送到Foundry时却被认为有3个小数位。

为了解决此问题，请使用以下参数：

- 参数ID =SLT
- 参数名称 =SLT_DTYPE_XXX(XXX指字段的数据类型)
- 参数值 =将被考虑的数据类型名称
设置参数如下，以将QUAN数据类型更改为十进制数据类型：

| 参数Id | 参数名称 | 参数值 |
| --- | --- | --- |
| SLT | SLT_DTYPE_QUAN | DEC |
