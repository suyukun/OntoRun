来源: https://palantir.com/docs/zh/foundry/sap/addon-parameters/

# Palantir Foundry Connector 2.0 以 SAP 应用程序的参数

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Palantir Foundry Connector 2.0 以 SAP 应用程序的参数

## Connector 参数

以下参数控制 Palantir Foundry Connector 2.0 以 SAP 应用程序（“Connector”）：

以下列出的默认参数值适用于最新连接器版本的新安装。

| Param Id | Param Name | Possible Values | Default Value | Description |
| --- | --- | --- | --- | --- |
| BEX | ENGINE | Alphanumeric | V2 | 引入了一个新的 BEx 查询引擎，它带来了性能改进并额外支持查询元素，如显示属性。默认情况下未启用，但可以通过将此参数设置为 V3 来开启。 |
| BEX | PAGING_MEMBER_LIMIT | Numeric | 100 | BEx 查询的分页通过筛选支持。连接器会自动为每个页面生成单独的筛选器。这意味着可以运行大型 BEx 查询而无需手动拆分同步。筛选生成基于 BEx 查询行中的 InfoObjects。如果发布的 InfoObject ID 未高于阈值，则在筛选生成中使用该 InfoObject；否则将被丢弃。随后，BEx 查询对每个筛选器单独运行，以提取所有 BEx 查询数据。默认情况下，分页功能未启用。连接器使用阈值以防止不必要的维度被用作筛选候选。如果 InfoObject 的发布值超过PAGING_MEMBER_LIMIT，则被认为太细粒度，因此在筛选生成中被丢弃。 |
| BEX | RANGESIZE | Numeric | 1000 | 在生成筛选时，如果任何 InfoObject 有很多值且未应用成员限制，此参数将控制每页的筛选列表。 |
| BEX | SHOW_DISPLAY_ATTRIBUTES | TRUE / FALSE | FALSE | 要启用显示属性，需要将 BEx 查询引擎设置为 V3。显示属性可以系统范围启用（通过维护此参数）或在 Foundry 中的个别同步级别启用。 |
| BEX | TEXT | TRUE / FALSE / BEX | BEX | 如果此参数设置为 TRUE，则特征/关键数字的键和文本将连接为列名。如果此参数设置为 FALSE，则仅特征/关键数字的键将为列名。如果此参数设置为 BEX，将使用查询参数定义列名。 |
| EXTACTOR | DEFAULT_CONFIGURATION | Alphanumeric | None | 提取器支持多个上下文。此参数可用于设置默认上下文。这样就无需在 Foundry 同步中设置上下文，因为在这些情况下连接器会使用默认上下文。将此参数保留为“None”意味着提取器将默认在本地应用服务器上运行，而不是远程上下文。 |
| EXTRACTOR | DEBUG_MODE | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，将在后台任务中启动一个无限循环，该循环会摄取数据并以页面方式写入。 |
| EXTRACTOR | EXT_DATA_<dataType> | Numeric | N/A | 如果 ABAP 数据类型的输出长度不正确，可以使用此参数更改该数据类型的数据长度。在参数名称字段中，<dataType> 是指应更改长度的 ABAP 数据类型。 |
| EXTRACTOR | EXT_DTYPE_<dataType> | ABAP Data Types | N/A | 如果 Foundry 无法识别某个数据类型，可以使用此参数将数据类型更改为另一种类型。在参数名称字段中，<dataType> 是指需要更改的数据类型。 |
| EXTRACTOR | FETCH_OPTION | XML / DIRECT | XML | 此参数指示是使用 XML 还是 DIRECT 提取方法。XML 提取方法速度更快，因为它以压缩格式提取数据。DIRECT 提取方法较慢，因为它作为字符串提取数据并逐行处理。仅在 XML 提取方法因数据中的特殊字符出错时才使用 DIRECT 提取方法。 |
| EXTRACTOR | MAX_ROWS_PER_SYNC | Numeric | N/A | 如果设置了此参数，则仅对 APPEND 事务类型的同步生效。每个同步将在摄取MAX_ROWS_PER_SYNC行数据时停止。 |
| EXTRACTOR | RFC_CONFIGURATION |  | NONE | 此参数指示远程服务器的 RFC 名称。如果此参数未设置或设置为空白，RFC 配置将设置为“NONE”。 |
| EXTRACTOR | TIMESTAMP | ON / OFF | OFF | 当此参数设置为 ON 时，数据将包括一个时间戳，显示数据的获取时间和行顺序号。此信息可用于在管道中去重数据（如果需要）。 |
| EXTRACTOR | TRACE_BEFORE_FETCH | TRUE / FALSE | FALSE | 默认情况下，提取器的跟踪运行还包括复制（计算、初始数据传输和复制对象生成），这有时会超过跟踪的限制。通过将此属性设置为 TRUE，跟踪将在提取器提取操作之前开始，从而为跟踪结果带来更多清晰度。 |
| INCREMENTAL | RANGESIZE | Numeric | 900 | （内部参数）此参数用于表和 RemoteTable 对象的 CDPOS、CDHDR 和 TWIN 增量类型。此参数指示嵌套范围表中可以存在多少个条件来摄取数据。 |
| INFOPROVIDER | READ_OPEN_REQUEST | TRUE / FALSE | TRUE | 此参数用于在 InfoProvider 中切换读取绿色请求或所有请求（绿色和黄色）。默认行为是读取所有请求。 |
| JSON | CONVERT_RAW_TO_STRING | TRUE / FALSE | TRUE | 如果此参数设置为 FALSE，则在保存页面数据时禁用 JSON 转换。如果参数为 TRUE，数据将从 Xstring 转换为字符串。 |
| JSON | NUMC_KEEPZERO | TRUE / FALSE | FALSE | 在 SP23 之前，当使用非内核 JSON 转换时，NUMC类型字段中的前导零会被移除。将此参数设置为 TRUE 将确保保留前导零，符合内核 JSON 转换的行为。默认设置为 FALSE 以确保与现有管道的向后兼容性。 |
| JSON | REMOVE_EXTENDED | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，在提取数据之前，将从数据中移除不可打印的 ASCII 代码（字符代码 128 到 255）。 |
| JSON | REMOVE_NONPRINT | TRUE / FALSE | TRUE | 如果此参数设置为 TRUE，在提取数据之前，将从数据中移除不可打印字符。 |
| LOGGER | DB | TRUE / FALSE | TRUE | 此参数用于控制日志是否保存到连接器自己的日志表中。 |
| LOGGER | PAGEREAD_COMMIT | TRUE / FALSE | FALSE | 默认情况下，页面读取日志消息仅发送到 Foundry，而不存储在数据库中。 |
| LOGGER | SLG | TRUE / FALSE | FALSE | 此参数用于在 SAP SLG 日志中创建日志条目。 |
| LOGGER | SLG_EXPIRY | Numeric | 30 | SLG_EXPIRY可以按天设置；如果未设置，则适用标准 SAP SLG 过期策略。 |
| LOGGER | SLG_KEEP | TRUE / FALSE | FALSE | SLG_KEEP用于防止日志在 SLG 中被提前删除。 |
| LOGGER | TRACE_LEVEL | INFO/WARN/ERROR | WARN | 此参数控制哪些类型的日志消息将保存到数据库并返回到 Foundry。跟踪日志级别如下：ERROR– 仅记录类型为 E-Error 的日志消息；WARN– 仅记录类型为 W-Warning、I-Information、E-Error、T-Trace 的日志消息；INFO– 所有日志消息（S-Success、W-Warning、I-Information、E-Error、T-Trace） |
| NAMESPACE | TIMESTAMP | TRUE / FALSE | TRUE | 如果此参数设置为 TRUE，时间戳和行号字段将命名为/PALANTIR/TIMESTAMP和/PALANTIR/ROWNO（这现在是默认值），而不是ZPAL_TIMESTAMP和ZPAL_ROWNO（这在早期版本中是命名约定）。 |
| PAGE | MIN_PAGESIZE | Numeric | 5000 | 此参数设置在以页面方式写入数据时页面的最小行数。如果用户在 Foundry 中指定的页面大小低于此值，将被忽略并使用此最小值。这是为了防止非常小的页面大小导致的性能不佳。 |
| PAGE | PAGESIZE | Numeric | 10000 | 此参数设置在以页面方式写入数据时页面的默认行数。如果用户未在 Foundry 中指定页面大小参数，将使用此值。 |
| REMOTEBEX | ENGINE | Alphanumeric | V2 | 引入了一个新的 BEx 查询引擎，它带来了性能改进并额外支持查询元素，如显示属性。默认情况下未启用，但可以通过将此参数设置为 V3 来开启。 |
| REMOTEBEX | PAGING_MEMBER_LIMIT | Numeric | 100 | BEx 查询的分页通过筛选支持。连接器会自动为每个页面生成单独的筛选器。这意味着可以运行大型 BEx 查询而无需手动拆分同步。筛选生成基于 BEx 查询行中的 InfoObjects。如果发布的 InfoObject ID 未高于阈值，则在筛选生成中使用该 InfoObject；否则将被丢弃。随后，BEx 查询对每个筛选器单独运行，以提取所有 BEx 查询数据。默认情况下，分页功能未启用。连接器使用阈值以防止不必要的维度被用作筛选候选。因此，如果 InfoObject 的发布值超过PAGING_MEMBER_LIMIT，则被认为太细粒度，因此在筛选生成中被丢弃。 |
| REMOTEBEX | RANGESIZE | Numeric | 1000 | 在生成筛选时，如果任何 InfoObject 有很多值且未应用成员限制，此参数将控制每页的筛选列表。 |
| REMOTEBEX | TEXT | TRUE / FALSE / BEX | BEX | 如果此参数设置为 TRUE，则特征/关键数字的键和文本将连接为列名。如果此参数设置为 FALSE，则仅特征/关键数字的键将为列名。如果此参数设置为 BEX，将使用查询参数定义列名。 |
| REMOTEINFOPROVIDER | READ_OPEN_REQUEST | TRUE / FALSE | TRUE | 此参数用于在 InfoProvider 中切换读取绿色请求或所有请求（绿色和黄色）。默认行为是读取所有请求。 |
| REMOTETABLE | PARALLEL | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，同步将以并行处理模式运行。 |
| REMOTETABLE | PARALLEL_JOB | Numeric | 5 | 如果PARALLEL为 TRUE 且未在数据同步级别定义要使用的并行任务数量，则此参数的值将用作系统范围的默认值。 |
| REMOTETABLE | PARALLEL_PAGE_LIMIT | Numeric | 50000 | 如果结果集中行数少于此值，将不使用并行处理。 |
| REMOTETABLE | ROWCOUNT_BY_TABCLASS | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，对于簇表，系统返回的行数将为单个表；如果为 FALSE（默认），行数将为总簇。 |
| RETRY | COUNT | Numeric | 1 | 此参数指示如果系统资源检查失败，将重试同步的最大次数。 |
| RETRY | DELAY | Numeric | 5 | 如果系统资源检查失败，此参数指示在再次检查资源之前等待多长时间（以秒为单位）。 |
| SLT | CONTEXT_BASED_AUTHORIZATION | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，将根据授权对象/PALAU/SCN对 SLT 上下文进行授权检查。 |
| SLT | CONTEXT_CONFIGURATION |  | N/A | 此参数可用于设置系统范围的默认上下文名称，以在 Foundry 未发送上下文时使用。 |
| SLT | FETCH_OPTION | XML / DIRECT | XML | 此参数指示是使用 XML 还是 DIRECT 提取方法。XML 提取方法速度更快，因为它以压缩格式提取数据。DIRECT 提取方法较慢，因为它作为字符串提取数据并逐行处理。仅在 XML 提取方法因数据中的特殊字符出错时才使用 DIRECT 提取方法。 |
| SLT | MAX_ROWS_PER_SYNC | Numeric | N/A | 如果设置了此参数，则仅对 APPEND 事务类型的同步生效。每个同步将在摄取MAX_ROWS_PER_SYNC行数据时停止。 |
| SLT | PARALLEL | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，同步将以并行处理模式运行。 |
| SLT | PARALLEL_JOB | Numeric | 3 | 如果PARALLEL为 TRUE 且未在数据同步级别定义要使用的并行任务数量，则此参数的值将用作系统范围的默认值。 |
| SLT | PARALLEL_PAGE_LIMIT | Numeric | 50000 | 如果结果集中行数少于此值，将不使用并行处理。 |
| SLT | QUEUE | TRUE / FALSE | FALSE | 为 SLT 工作进程处理引入了一种新方法。默认情况下，连接器使用 BTC（后台）进程从 SLT 获取数据。如果多个同步正在运行，则每个同步使用一个 BTC 进程。将此参数设置为 TRUE 以使用单个 BTC 进程等待来自 SLT 的多个初始加载。一旦数据包到达 SLT，将启动 Foundry 进程。这提高了 BTC 资源效率。 |
| SLT | REMOTEAGENT_<contextName> |  | N/A | 如果 SLT 服务器和连接器在不同的服务器上，则应定义此参数。在参数名称中，<contextName> 表示 SLT 上下文名称。对于参数值，应定义 RFC 目标以指向 SLT 上下文的源系统。 |
| SLT | RFC_CONFIGURATION |  | NONE | 此参数指示远程服务器的 RFC 名称。如果此参数未设置或设置为空白，RFC 配置将设置为“NONE”。 |
| SLT | SLT_DATA_<dataType> | Numeric | N/A | 如果 ABAP 数据类型的输出长度不正确，可以使用此参数更改该数据类型的数据长度。在参数名称字段中，<dataType> 是指应更改长度的 ABAP 数据类型。 |
| SLT | SLT_DTYPE_<dataType> | ABAP Data Types | N/A | 如果 Foundry 无法识别某个数据类型，可以使用此参数将数据类型更改为另一种类型。在参数名称字段中，<dataType> 是指需要更改的数据类型。 |
| SLT | TIMESTAMP | ON / OFF | OFF | 当此参数设置为 ON 时，数据将包括一个时间戳，显示数据的获取时间和行顺序号。此信息可用于在管道中去重数据（如果需要）。 |
| SLT | TRACE_BEFORE_FETCH | TRUE / FALSE | FALSE | 默认情况下，为 SLT 运行跟踪还包括复制（计算、初始数据传输和复制对象生成），这有时会超过跟踪的限制。通过将此属性设置为 TRUE，跟踪将在 SLT 提取操作之前开始，从而为跟踪结果带来更多清晰度。 |
| SYSTEM | ABORT_RETRY_COUNT | Numeric | 10 | 此参数定义在事务关闭时尝试中止任务的次数。 |
| SYSTEM | AUTH_CHECK_SOURCE | TABLE / PFCG | PFCG | 用于配置自定义授权。 |
| SYSTEM | AUTH_GET_LIST | TRUE / FALSE | FALSE | 此参数用于启用或禁用对象类型值列表的授权检查。 |
| SYSTEM | CONTEXT_VALIDITY_CHECK | TRUE / FALSE | TRUE | 如果此参数设置为 FALSE，则即使 SLT 和远程代理上下文不是有效上下文，也不会从返回给 Foundry 的列表中排除。 |
| SYSTEM | CONTINUOUS_RESOURCE_CHECK | TRUE / FALSE | TRUE | 启用对所有请求（初始化和所有分页请求）的资源检查。如果为 FALSE，资源检查仅对初始化请求进行。 |
| SYSTEM | CPU_CHECK | TRUE / FALSE | TRUE | 启用或禁用 CPU 检查。 |
| SYSTEM | DYNAMIC_TABLE | V1 / V2 | V1 | 此参数可用于解决CL_ALV_TABLE_CREATE=>CREATE_DYNAMIC_TABLE中看到的问题，该问题达到动态表限制。要启用新的动态表例程，请将此参数设置为 V2。 |
| SYSTEM | ERP_SOURCE_INFO | TRUE / FALSE | TRUE | 用于定义是否将 ERP 源信息与上下文列表一起返回到 Foundry。 |
| SYSTEM | FAILED_AUTH_MAX_COUNT | Numeric | 200 | 此参数用于限制来自 SU53 的出错授权检查消息。可能会出现某些情况下在 SAP 系统中生成过多出错消息，这可能会影响提取过程。 |
| SYSTEM | FILTER_DECODE | TRUE / FALSE | FALSE | 设置为 TRUE 以启用非 Unicode 筛选。 |
| SYSTEM | INFOPROVIDER_AUTH_CHECK | TRUE / FALSE | FALSE | 设置为 TRUE 时，连接器将检查用户对授权相关 InfoObjects 的授权。这可以避免授权出错。使用 SAP API 基于行级授权生成筛选。 |
| SYSTEM | KILL_HANGING_JOB | TRUE / FALSE | FALSE | 如果设置为 TRUE，连接器将检查来自 Foundry 的分页请求，如果在一定时间后没有更多页面读取请求，则取消分页任务。 |
| SYSTEM | KILL_HANGING_JOB_THRESHOLD | Numeric | 1800 | 如果KILL_HANGING_JOB设置为 TRUE，此参数定义在任务被视为挂起之前等待的秒数。 |
| SYSTEM | MEMORY_CHECK | TRUE / FALSE | TRUE | 启用或禁用内存检查。 |
| SYSTEM | MEMORY_CHECK_SOURCE | ST06 / ST02 | ST06 | 此参数确定用于资源检查的内存消耗值将从 SAP 中的 ST02 事务代码还是 ST06 事务代码中检索。 |
| SYSTEM | PROCESS_CHECK | TRUE / FALSE | TRUE | 启用对允许的最小工作进程数量的检查；与PROCESS_MIN_BG和PROCESS_MIN_DIA配合使用。 |
| SYSTEM | RESOURCE_CHECK | TRUE / FALSE | TRUE | 启用或禁用资源检查。如果为 FALSE，所有检查将禁用；如果为 TRUE，其他参数（CPU_CHECK和MEMORY_CHECK）将被检查。 |
| SYSTEM | RESOURCE_CHECK_SERVER | LOCAL / ALL | ALL | ALL：检查所有应用服务器，如果任何服务器有可用资源则返回 TRUE。从处理当前请求的本地服务器开始。LOCAL：仅检查本地服务器，根据可用性返回 TRUE / FALSE。 |
| SYSTEM | SERVICE_ENCODING | Alphanumeric |  | 用于启用非 Unicode NetWeaver 7.4 安装的字符集支持。 |
| SYSTEM_THRESHOLD | CPU_LOAD | Numeric | 80 | 如果当前系统 CPU 负载高于此值，同步将被中止。 |
| SYSTEM_THRESHOLD | CPU_USER | Numeric | 80 | 如果当前系统 CPU 用户负载高于此值，同步将被中止。 |
| SYSTEM_THRESHOLD | MEMORY_FREE | Numeric | 5 | 如果当前系统的可用内存（%）低于此最小值，同步将被中止。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_BG | Numeric | 1 | SAP 应用服务器上同步继续所需的最小后台进程数量。 |
| SYSTEM_THRESHOLD | PROCESS_MIN_DIA | Numeric | 1 | SAP 应用服务器上同步继续所需的最小对话进程数量。 |
| TABLE | PARALLEL | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，同步将以并行处理模式运行。 |
| TABLE | PARALLEL_JOB | Numeric | 5 | 如果PARALLEL为 TRUE 且未在数据同步级别定义要使用的并行任务数量，则此参数的值将用作系统范围的默认值。 |
| TABLE | PARALLEL_PAGE_LIMIT | Numeric | 50000 | 如果结果集中行数少于此值，将不使用并行处理。 |
| TABLE | ROWCOUNT_BY_TABCLASS | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，对于簇表，系统返回的行数将为单个表；如果为 FALSE（默认），行数将为总簇。 |
| TCODE | DEBUG_MODE | TRUE / FALSE | FALSE | 如果此参数设置为 TRUE，将在后台任务中启动一个无限循环，该循环会摄取数据并以页面方式写入。 |
| TRACE | DURATION_LIMIT | Numeric | 30 | 如果同步正在运行并具有跟踪功能，并且达到此限制（以分钟为单位），则跟踪将自动关闭（以避免系统短转储）。 |
| TRACE | MAX_SESSION | Numeric | 10 | 同步的跟踪会话的默认最大会话数为 10，但可以使用此参数进行修改。这主要是为了防止并行提取生成每个并行任务的跟踪文件。 |
| TSV | CHARLIST | Alphanumeric | N/A | 此参数控制从非 Unicode 4.6C/620/640 系统的提取。默认使用固定字典字符，但可以使用此参数扩展此字典以添加缺失字符。 |
| TSV | ESCAPEMODE | AUTO / HEX / HEX_ZIPPED / CHAR_COMPARE | CHAR_COMPARE | 此参数控制从非 Unicode 4.6C/620/640 系统的提取。有一个固定的字符转义算法，可以使用此参数进行更改。 |
