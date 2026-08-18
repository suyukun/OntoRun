来源: https://palantir.com/docs/zh/foundry/data-connection/export-tasks/

# 导出任务（旧版）

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 导出任务（旧版）

我们通常不建议使用导出任务将数据写回到外部源。然而，根据您在Foundry中的注册情况，某些源类型可能可以使用并支持导出任务。

以下导出任务文档是为尚未过渡到我们推荐的导出工作流的导出任务用户提供的。

Data Connection导出任务支持写入广泛的常见企业系统，包括：

- Amazon S3
- Azure Blob Filesystem (ABFS)
- HDFS
- JDBC兼容系统，包括：关系数据库PostgreSQLMicrosoft SQL ServerMySQL数据仓库TeradataSnowflakeVertica
- 关系数据库PostgreSQLMicrosoft SQL ServerMySQL
- PostgreSQL
- Microsoft SQL Server
- MySQL
- 数据仓库TeradataSnowflakeVertica
- Teradata
- Snowflake
- Vertica
- 文件系统，包括挂载在中介代理上的网络文件系统
- SFTP
## 平台内文档

详细的导出任务文档可在Foundry平台中查看。导航到平台导航侧边栏左下角的Help & support标签中的Custom Documentation。然后，导航到Data Connection>Sources>Export Tasks以查看配置选项的范围。

## 已知导出任务限制

- 导出任务未与权限标记和导出控制集成。通过导出任务导出的数据不需要导出数据集或流的取消标记权限。
- 导出任务未针对性能进行优化。导出大量数据可能导致长时间运行的任务或任务无法完成。
- 导出任务没有用户界面进行配置，必须使用YAML提供所需的配置选项进行配置。并非所有导出任务选项都记录供自助使用；在某些情况下，导出任务只能通过Palantir的支持进行配置。