来源: https://palantir.com/docs/zh/foundry/analytics-connectivity/microstrategy/

# 从MicroStrategy连接到Foundry数据集

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 从MicroStrategy连接到Foundry数据集

## 概述

MicroStrategy分析平台包括一个MicroStrategy认证的连接器，用户可以轻松创建基于Foundry数据集的MicroStrategy报告和档案。该连接器提供与Foundry访问控制的兼容性，包括细粒度的权限。

### 支持的产品:

- MicroStrategy Workstation作为预览功能（2021年更新8发布）
- MicroStrategy Workstation（2021年更新9发布或更高版本）
- MicroStrategy Library（2021年更新9发布或更高版本）
### 认证方法

- 用户生成的词元
## 安装

### 第1部分：验证连接器是否已安装在MicroStrategy中

如果您使用的是2021年更新8发布的MicroStrategy，Palantir Foundry连接器应该已经作为预览功能 ↗安装。通过以下步骤进行验证：

- 打开MicroStrategy Workstation并启用预览功能。
- 在左侧边栏的管理部分中选择数据源旁边的加号。
- 在支持的数据源列表中搜索“Palantir Foundry”。如果在列表中找到它，请继续第2部分安装JDBC驱动程序。
如果您使用的是2021年更新9发布或更高版本，Palantir Foundry连接器应该已经安装在您的MicroStrategy版本中。通过以下步骤进行验证：

- 打开MicroStrategy Workstation。
- 在左侧边栏的管理部分中选择数据源。
- 在支持的数据源列表中搜索“Palantir Foundry”。如果在列表中找到它，您无需单独安装JDBC驱动程序；请继续下面的使用部分。
如果在支持的数据源列表中没有看到Palantir Foundry，请联系您的MicroStrategy支持代表获取下一步操作。您可能需要升级到最新的MicroStrategy版本和MicroStrategy Workstation。

### 第2部分：安装Palantir Foundry JDBC驱动程序

如果您使用的是2021年更新8发布，通过首先安装Foundry数据集的JDBC驱动程序来完成Foundry MicroStrategy集成的设置。导航到下载：Foundry数据集JDBC驱动程序下载并安装驱动程序。

如果您使用的是2021年更新9发布或更高版本，Foundry JDBC驱动程序已预安装在MicroStrategy Windows Workstation和MicroStrategy Intelligence Server中。如果您希望使用本地档案访问Foundry数据，则只需为MicroStrategy Mac Workstation安装JDBC驱动程序。

如果在安装过程中遇到任何问题，请联系您的Palantir代表。

现在连接器已安装，您可以在MicroStrategy中创建基于Foundry数据集的报告和档案。

## 使用

本指南将解释如何通过MicroStrategy进行Foundry认证，选择数据集，并开始创建您的第一个档案。

### 第1部分：创建Foundry数据源

在MicroStrategy中创建Foundry数据源有两种选择：

- 选项1：在MicroStrategy Workstation中创建Foundry数据源
- 选项2：使用MicroStrategy数据集创建Foundry数据源
#### 选项1：在MicroStrategy Workstation中创建Foundry数据源

- 如果您使用的是2021年更新8发布的MicroStrategy，请在帮助菜单中启用预览功能。如果您使用的是2021年更新9发布或更高版本，请继续下一步。
如果您使用的是2021年更新8发布的MicroStrategy，请在帮助菜单中启用预览功能。如果您使用的是2021年更新9发布或更高版本，请继续下一步。

- 在Workstation侧边栏的管理部分下，点击数据源旁边的加号图标。
在Workstation侧边栏的管理部分下，点击数据源旁边的加号图标。

- 在支持的数据源列表中找到并选择“Palantir Foundry”。
在支持的数据源列表中找到并选择“Palantir Foundry”。

- 为数据源指定一个名称并保持数据库版本不变。然后，选择您将使用该连接的MicroStrategy项目。选择默认数据库连接下拉菜单，然后添加新的数据库连接。
为数据源指定一个名称并保持数据库版本不变。然后，选择您将使用该连接的MicroStrategy项目。选择默认数据库连接下拉菜单，然后添加新的数据库连接。

- 按照提示添加有关您的Foundry连接的详细信息，包括连接属性。
按照提示添加有关您的Foundry连接的详细信息，包括连接属性。

#### 选项2：使用MicroStrategy数据集创建Foundry数据源

- 如果您使用的是2021年更新9发布或更高版本，您可以使用MicroStrategy数据集创建Foundry数据源。在Workstation的帮助菜单中禁用启用新的数据导入体验。
如果您使用的是2021年更新9发布或更高版本，您可以使用MicroStrategy数据集创建Foundry数据源。在Workstation的帮助菜单中禁用启用新的数据导入体验。

- 在分析部分下，选择数据集旁边的加号图标，然后在创建数据集对话框中选择数据导入立方体。
在分析部分下，选择数据集旁边的加号图标，然后在创建数据集对话框中选择数据导入立方体。

- 在数据源窗口中搜索“Palantir Foundry”并从列表中选择它。
在数据源窗口中搜索“Palantir Foundry”并从列表中选择它。

- 在选择导入选项窗口中选择任一选项，然后选择下一步。在本指南中，我们将选择选择表选项。
在选择导入选项窗口中选择任一选项，然后选择下一步。在本指南中，我们将选择选择表选项。

- 在从表中导入窗口中，通过选择数据源旁边的加号图标创建数据源。
在从表中导入窗口中，通过选择数据源旁边的加号图标创建数据源。

- 使用下面第2部分中显示的步骤提供连接属性。
使用下面第2部分中显示的步骤提供连接属性。

### 第2部分：配置Foundry连接设置

要创建到Foundry的连接，您必须提供以下连接属性：

- 服务器:您通常使用的访问Foundry的URL，例如<subdomain>.palantirfoundry.com。
- 目录:Foundry项目的路径，例如/MyOrg/MyProject。此字段仅在2021年更新9发布或更高版本中必填。设置此属性可以解决MicroStrategy中的表浏览问题。如果您使用的是2021年更新8发布，请切换到高级选项卡并在附加连接字符串参数中添加参数。
- 词元:在Foundry中生成的有效用户词元。请参阅用户生成的词元文档，了解如何获取词元。
MicroStrategy连接器仅支持基于词元的认证。

- 附加连接字符串参数（非必填）:切换到高级选项卡并指定任何其他连接参数。参数应由&符号分隔，例如OptionalParam1=<VALUE>&OptionalParam2=<VALUE>。在Foundry数据集的JDBC驱动程序参数参考文档中找到连接参数的完整列表。如果您使用的是2021年更新9发布或更高版本，Dialect设置为推荐值SPARK，以便Foundry在MicroStrategy中进行最佳集成，此设置不可更改。
### 第3部分：连接到Foundry并选择数据集

- 使用左侧的导航侧边栏选择数据集，然后选择数据导入立方体或智能立方体。
- 连接到Foundry并选择数据集：如果您使用的是2021年更新8发布，请选择在帮助菜单下启用新的数据导入体验。选择您之前创建的Foundry数据源，连接到它，然后导入您的Foundry数据集。如果您使用的是2021年更新9发布或更高版本，在数据源列表中搜索“Palantir Foundry”，选择它，然后在选择导入选项窗口中选择任一选项。在从表中导入窗口中，选择您之前创建的Foundry数据源，连接到它，并导入您的Foundry数据集。
- 如果您使用的是2021年更新8发布，请选择在帮助菜单下启用新的数据导入体验。选择您之前创建的Foundry数据源，连接到它，然后导入您的Foundry数据集。
- 如果您使用的是2021年更新9发布或更高版本，在数据源列表中搜索“Palantir Foundry”，选择它，然后在选择导入选项窗口中选择任一选项。在从表中导入窗口中，选择您之前创建的Foundry数据源，连接到它，并导入您的Foundry数据集。
- 继续在MicroStrategy中创建您的报告。