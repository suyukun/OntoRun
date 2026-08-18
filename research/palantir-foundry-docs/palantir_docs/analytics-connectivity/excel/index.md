来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/excel/

# Excel

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Excel

本指南将教您如何使用 Foundry ODBC 驱动程序将数据集导入 Excel。

## 配置 Foundry 连接

- 打开 Windows ODBC 管理员应用程序（在 Windows 搜索栏中搜索“odbc”并打开与您的 Excel 版本匹配的 32 位或 64 位版本）。
- 创建一个新的用户 DSN，选择 FoundrySqlDriver 驱动程序。为其赋予一个有意义的名称，例如Foundry Excel。
- 对于服务器，输入您的 Foundry URL（例如：myorganization.palantirfoundry.com）。
- 非必填：如果您使用 OAuth 进行身份验证，请设置OAuth 属性。
- 非必填：您可以在此处保存身份验证词元，但我们建议稍后在 Excel 中输入，当您导入数据时会提示输入。
- 点击OK以保存 DSN。
## 通过 SQL 导入数据

- 在 Excel 中，打开数据选项卡并在功能区中点击获取数据。选择从其他来源 -> 从 ODBC。
- 选择您在上一步中配置的 DSN。
- 在“高级选项”下，输入 SQL 查询以导入数据。如果您想导入数据集/YourProject/yourdataset，您可以输入SELECT * FROM "/YourProject/yourdataset"。如果您熟悉 SQL，您可以在此处输入更高级的查询，例如筛选和聚合。
- 如果您想导入数据集/YourProject/yourdataset，您可以输入SELECT * FROM "/YourProject/yourdataset"。
- 如果您熟悉 SQL，您可以在此处输入更高级的查询，例如筛选和聚合。
- 点击OK。
- 如果这是您首次导入数据，系统会提示您输入凭据。如果使用 OAuth，选择“默认或自定义”凭据类型，保持字段为空并点击“连接”。否则，您将需要一个身份验证词元。选择“数据库”，输入您的用户名。在“密码”字段中，输入您的词元，而不是您的 Foundry 密码。
- 如果使用 OAuth，选择“默认或自定义”凭据类型，保持字段为空并点击“连接”。
- 否则，您将需要一个身份验证词元。选择“数据库”，输入您的用户名。在“密码”字段中，输入您的词元，而不是您的 Foundry 密码。
- 点击连接。
## 通过表浏览器导入数据

默认情况下，如果您按照上述步骤操作但未输入 SQL 查询，表浏览器将显示为空状态。这可以通过在您的 DSN 中添加catalog属性并将其设置为完整的项目路径（例如MyOrg/MyProject）来解决。您可以通过在驱动程序 DSN 设置窗口中点击附加属性，然后点击添加来实现。然后表浏览器应该能正确显示，尽管您将被限制为每个 DSN 仅浏览一个项目。

## 将数据导入 Microsoft Access

同样的 Foundry 连接器也可以用于将数据导入 Access 数据库。

- 在 Access 中，打开外部数据选项卡并在功能区中点击新数据源。选择从其他来源 -> ODBC 数据库。
- 选择您想要导入源数据还是链接到源数据。
- 在机器数据源选项卡下，选择您在本指南第一步中配置的 DSN。您需要在驱动程序 DSN 设置窗口中保存您的身份验证词元。您需要如前一步所述设置catalog属性。您的项目路径必须符合Access 表名限制 ↗。
- 您需要在驱动程序 DSN 设置窗口中保存您的身份验证词元。
- 您需要如前一步所述设置catalog属性。
- 您的项目路径必须符合Access 表名限制 ↗。
- 从表浏览器中选择您的表，然后点击OK。