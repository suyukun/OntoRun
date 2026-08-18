来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/tableau-server-setup/

# Tableau Server 设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Tableau Server 设置

按照以下步骤设置 Tableau Server 以进行发布。这些步骤必须由管理员执行。JDBC 驱动程序 (.jar) 和 Tableau 连接器 (.taco) 文件与 Tableau Desktop 相同。

## 步骤 1: 安装 Foundry 数据集 JDBC 驱动程序

导航到下载: Foundry 数据集 JDBC 驱动程序下载.jar文件。将其放置在 Tableau Server 查找驱动程序的目录中。如果使用 Windows，位置是C:\Program Files\Tableau\Drivers。

## 步骤 2: 安装 Tableau 连接器文件

导航到下载: Tableau 连接器下载.taco文件。将文件放置在[Your Tableau Server Install Directory]/data/tabsvc/vizqlserver/Connectors目录中。默认情况下，在 Windows 上，这个位置是C:\ProgramData\Tableau\Tableau Server\data\tabsvc\vizqlserver\Connectors。

或者，您可以创建一个新的目录来存储连接器，然后通过运行tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors配置 Tableau Server 使用该目录。然后，将.taco文件放在那里。

### (非必填) 步骤 3: 为 Desktop 和 Server 设置 OAuth

如果您希望报表创建者能够在 Tableau Desktop 上通过 OAuth 进行身份验证并使用 OAuth 发布报表，则必须进行配置。有关更多信息，请参见Tableau OAuth: 设置指南。

### 步骤 4: 重启 Tableau Server

每次连接器文件更改时，您必须重启 Tableau Server。
