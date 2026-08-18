来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/architecture/

# 架构

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 架构

本节中的外部 SQL 连接和 BI 工具集成由名为 Foundry SQL Server 的服务提供支持。该服务为对 Foundry 数据集的只读查询提供轻量级 SQL 会话和语句管理。Palantir 提供了 JDBC 和 ODBC 驱动程序，以使用开放标准促进客户端与此服务的交互，并为利用这些驱动程序的某些第三方平台提供插件实现。

## 支持的 SQL 方言

支持的 SQL 方言包括ANSI、ODBC和SparkSQL。

请注意，这些方言的支持仅限于只读功能。

## 执行引擎

Foundry SQL Server 会根据查询的复杂性自动选择执行引擎。每个执行引擎在整体性能、结果大小限制和支持的查询复杂性方面都有一套权衡。

### Spark 引擎

默认的查询执行引擎利用了 Spark SQL 功能。此引擎支持完整的 SQL 计算功能，如聚合、合并、排序、筛选等。需要使用此执行引擎的查询将受限于数据规模，因为结果必须在将结果传递给客户端应用程序之前在 Spark 驱动程序的内存中收集。这些限制取决于计算结果中的行数和字节数。

### 直接读取引擎

在可能的情况下，Foundry SQL Server 将使用直接读取引擎来执行查询。当查询不需要 SQL 计算时，Foundry SQL Server 将绕过 Spark SQL，直接从数据集的支持文件中流式传输记录。直接读取查询不受需要完整 SQL 计算的查询的相同规模限制。

直接读取查询符合以下条件：

- 在数据集上执行。视图当前不支持。
- 数据集文件采用支持的格式。目前直接读取支持的格式包括 Parquet、CSV、Avro 和 Soho。
- 查询不需要 SQL 计算。包含聚合、筛选、合并和排序谓词的查询不符合直接读取条件。
- 查询不从类型不符合直接读取条件的列中选择。array、map和struct类型不符合直接读取条件。
直接读取查询区分大小写。

## 注意事项

- 此功能旨在支持 Foundry 平台外部的客户端，如 PowerBI、Tableau 或其他下游应用程序。有关 Foundry 平台内基于 SQL 的变换，请参见SQL 变换。
- Foundry SQL Server 的架构已针对中等数据规模的临时交互查询进行了优化。