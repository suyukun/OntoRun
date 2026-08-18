来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/qlik-sense-getting-started/

# 起始指南

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 起始指南

本指南将教您如何在Qlik Sense中认证到Foundry，并起始加载数据集。

### 连接到Foundry

- 您需要准备好一个Foundry访问词元以进行认证。
- 您还需要您的服务器管理员创建的Foundry DSN的名称。
- 在Qlik Sense中，打开数据管理器，并点击图标以创建一个新连接。
- 选择OLE DB作为数据源。
- 选择Microsoft OLE DB Provider for ODBC Drivers作为提供者。
- 对于数据源，输入<Foundry_DSN>;PWD=<Token>，其中<Foundry_DSN>是您的服务器管理员创建的DSN名称，<Token>是您的Foundry词元。例如，您可能会得到类似Foundry;PWD=eyJwbG50ci...的结果。
- 选择Specific user name and password，但保持为空。
- 为连接选择一个合适的名称。(Qlik可能默认在名称中设置了词元，请将其移除！)
- 测试连接以检查一切是否正常，然后点击创建以打开表浏览器。
Qlik Sense目前对您可以输入到“密码”字段的最大密码长度有限制，比Foundry词元短。这就是为什么我们将词元设置在数据源字符串中而不是在密码字段中。

### 加载数据集

创建连接后，将打开一个表浏览器。您也可以通过选择先前创建的连接来打开此浏览器。在这里，您首先选择包含您想要加载的数据集的Foundry项目（这里称为“数据库”）。

然后将列出项目表，您可以选择您希望导入的表。

### 编写SQL查询

如果您熟悉SQL，您可以在Qlik Sense中编写自己的SQL查询。这对于筛选和聚合大型数据集非常有用，以便只有较小的变换数据被导入到Qlik中。

为此，在创建连接后，打开数据加载编辑器并创建一个新脚本。然后编写一个如下图所示的SQL查询。数据集可以通过其路径或数据集RID引用，用双引号括起来。

有关“LIB CONNECT”语法的更多文档，请参阅Qlik 文档。

要访问数据集的特定分支，请使用以下语法：

```
Copied!1
2
SELECT * FROM "branch"."dataset_path"
-- 从"branch"数据库中选择"dataset_path"表的所有数据
```
