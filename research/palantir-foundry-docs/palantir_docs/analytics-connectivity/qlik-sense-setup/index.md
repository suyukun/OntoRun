来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/qlik-sense-setup/

# 服务器设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 服务器设置

您现在可以从Qlik Sense访问Palantir Foundry数据集，并使用它们搭建互动仪表盘。要在Qlik Sense中使用Foundry，您必须在Qlik Sense服务器上安装Foundry ODBC驱动程序。

请按照以下指南完成设置。这些步骤必须由具有Qlik Sense服务器访问权限的人完成。

### 步骤1：安装ODBC驱动程序

导航到下载页面：ODBC驱动程序下载驱动程序。在Qlik Sense服务器上安装它。

### 步骤2：配置Foundry DSN

Qlik Sense需要预先配置ODBC DSN。

- 在Qlik Sense服务器上，打开Windows ODBC管理工具，并为FoundrySqlDriver创建一个新的系统DSN。
- 将您的Foundry URL设置为服务器。
- 选择“附加属性”，并添加一个新属性UserAgent，值为QLIKSENSE。这将启用针对Qlik Sense优化的设置。
- 点击OK保存DSN。
我们建议在DSN中留空访问词元字段，并在您在Qlik Sense中创建连接时再设置它。请记住，如果您在DSN中设置了词元，任何可以访问该DSN的人都能够查看词元提供访问的数据。

设置UserAgent属性非常重要。没有它，数据将无法正确加载。

### （非必填）步骤3：预配置Qlik Sense连接

如果用户能够在Qlik Sense中创建自己的连接，您可以跳过此步骤。否则，您需要预配置Foundry连接并授予用户访问权限。有关如何创建连接，请参阅快速入门指南。
