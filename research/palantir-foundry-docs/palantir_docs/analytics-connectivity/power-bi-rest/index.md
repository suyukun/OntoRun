来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/power-bi-rest/

# REST 连接器设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# REST 连接器设置

您可以从 Power BI® 访问 Palantir Foundry 数据集，而无需安装 Palantir Foundry ODBC 驱动程序。与 Power BI® 默认提供的内置 Palantir Foundry 连接器相比，此连接器仅支持较小的数据集大小。仅当无法安装 ODBC 驱动程序时才建议使用。Palantir Foundry REST 连接器仅支持以导入模式进行数据集摄取，而不支持直接查询。

### 步骤 1: 在自定义连接器目录中安装连接器

您可以部署非本地提供的自定义连接器，以将数据摄取到 Power BI® 中。在文件目录中找到 Power BI® 安装中的Custom Connectors文件夹。此目录应作为 Power BI® 安装的一部分创建。下载 Palantir Foundry REST 连接器并将其移动到此目录中。

下载:

- Palantir REST Power BI® 连接器
### 步骤 2: 配置 Power BI® 以使用自定义连接器

更改 Power BI® 桌面设置以允许未经验证的扩展，通过导航到选项 > 安全性 > 数据扩展。选择选项**（不推荐）允许任何扩展加载而不进行验证或警告**。

### 步骤 3: 摄取数据

重新启动 Power BI® 应用程序以使配置生效。自定义连接器在启动时加载，现在应可使用。您可以按照Power BI®: 入门指南中的说明进行操作，以搭建由 Foundry 数据支持的第一个报告。注意，当不使用 ODBC 连接器方法时，连接器将在 Power BI® 中显示为 "Palantir Foundry (REST)"。
