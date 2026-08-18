来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/tableau-getting-started/

# 起始

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 起始

本指南将教您如何通过Tableau进行Foundry认证、选择数据集，并开始搭建您的第一个互动仪表盘。

## 在Tableau中选择Foundry作为您的数据源

- 启动Tableau并选择连接到数据。
- 在连接到服务器下，点击更多。
- 搜索并选择Palantir的Foundry。
### 输入您的Foundry URL

在Palantir的Foundry对话框中，在服务器字段中输入您的Foundry URL。您可以通过登录、复制URL，并删除https://前缀以及.com之后的任何内容来找到您的Foundry URL。

例如，如果您的Foundry链接是https://myfoundrylink.palantir.com/workspace/home，您应该在Tableau提示中输入myfoundrylink.palantir.com。

## 通过Foundry进行认证

有两种方式可以通过Foundry进行认证：Foundry OAuth或Foundry词元。在大多数情况下，我们建议使用OAuth以简化认证过程。

### Foundry OAuth认证（推荐）

- 在认证下拉菜单中选择Foundry OAuth。
- 在OAuth URL字段中输入https://，后跟您在服务器字段中输入的相同URL。
- 选择登录，您将被重定向到浏览器中的登录窗口。
- 登录，然后选择允许以授权Tableau使用您的Foundry账户进行连接。
- 一旦您被重定向到一个显示信息"Tableau created this window to authenticate. It is now safe to close it"的网页，关闭窗口并返回Tableau Desktop。
如果您在登录Foundry时收到出错信息，可能是因为您的组织尚未启用Tableau的OAuth登录选项。在这种情况下，请联系您的Foundry管理员以获取支持，参考启用OAuth客户端的说明。

#### 使用OAuth发布报告

如果您打算在使用OAuth时将报告发布到带有嵌入凭据的Tableau Server，您首先需要通过导航到Tableau Server中的我的账户设置 > 数据源的保存凭据来配置凭据。有关更多信息，请参阅Tableau文档中的管理数据连接的保存凭据 ↗。

### Foundry词元认证

- 在认证下拉菜单中选择Foundry词元。
- 在词元字段中输入一个唯一的用户生成词元。
- 点击登录。
按照这些说明操作后，您现在应该可以在左侧边栏下的连接中看到您的Foundry环境。

## 选择您的数据集

要开始处理特定数据集，请使用左侧边栏中的导航选项。在数据库部分，从下拉菜单中选择一个Foundry项目。然后在表部分，使用搜索字段按名称或完整路径查找数据集。

加载数据集后，选择连接模式（实时或提取），然后继续像往常一样创建您的Tableau仪表盘。

## 高数据规模和Tableau数据提取

更高的数据规模可以通过使用Tableau数据提取 ↗来处理，并确保查询在由Foundry SQL Server处理时"直接读取合格"。有关直接读取功能的详细信息，请参阅架构。
