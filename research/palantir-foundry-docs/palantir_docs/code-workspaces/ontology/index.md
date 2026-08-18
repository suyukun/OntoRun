来源: https://palantir.com/docs/zh/foundry/code-workspaces/ontology/

# 与Ontology交互

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 与Ontology交互

Code Workspaces对Ontology SDK的支持处于测试阶段，可能尚未在您的注册中可用。如果您希望启用此功能，请联系Palantir支持团队。

受限视图支持的Ontology实体和查询函数尚未在Code Workspaces中支持。

Code Workspaces支持在JupyterLab®和RStudio®中使用object、link和操作类型与Ontology交互。

## 创建新的Ontology SDK

要在Code Workspaces中创建新的Ontology SDK，首先导航到Ontology侧边面板。每个Code Workspace可以有一个SDK，并且可以创建该SDK的多个版本。在Ontology侧边面板中，选择创建新SDK以打开SDK配置表单。

新的Ontology SDK需要一个包名和一个关联的Ontology。包名用于确定如何在代码中访问您的SDK：包名为example的SDK版本可以在库名称example_sdk下导入。SDK包名只能包含字母、数字和连字符，并且不能以连字符结尾。一旦发布，SDK包名将无法更改。

配置好SDK后，选择保存选择以继续。

## 选择数据实体

Ontology侧边面板包含两个选项卡：数据实体和SDK生成。

- 数据实体选项卡用于从您的Ontology中导入object和操作类型。
- SDK生成选项卡用于检查和安装SDK版本。
要选择数据实体，请导航到数据实体选项卡。选择添加并选择所需的数据实体类型以打开资源选择器对话框，从而浏览和选择数据实体。选择数据实体后，可以使用侧边面板底部的保存按钮保存您的选择。选择保存后，将生成一个新SDK版本以访问所选的数据实体。

在选择影响object类型或将object类型作为参数的操作类型时，这些object类型也将自动添加到选择中。如果任何已选择的object类型具有尚未导入到您的Code Workspace项目范围内的支持数据源，您还将被提示确认自动导入这些数据源。

## 更改选定的Ontology

要从不同的Ontology导入Ontology实体，请使用数据实体选项卡中的Ontology选择器。选择不同的Ontology后，选择保存以应用更改并生成新版本。更改选定的Ontology将重置SDK的数据范围，清除任何已选择的object、操作或link类型。

## 发布新的Ontology SDK版本

配置完成后，可以使用生成新版本按钮发布新的Ontology SDK版本，该按钮位于Ontology侧边面板的底部。已发布和待处理的版本可以通过SDK生成选项卡进行检查。

选择生成新版本后，新创建的版本将显示在SDK生成选项卡中。SDK版本在状态显示为“已发布”之前不可用。

发布失败的常见原因包括：

- 使用操作类型而不导入依赖的object类型。
- 使用的object类型具有不在项目范围内的支持数据源。
## 在代码中使用Ontology SDK版本

成功发布的版本可以在您的编辑器中导入和使用。首先，点击Ontology侧边面板SDK生成选项卡中您想使用的版本的卡片。这将展开卡片，其中包含几个针对您编辑器语言的代码片段。点击片段将其添加到剪贴板，以便粘贴到您的编辑器中。

可见的片段将根据您编辑器的语言而有所不同。所有支持的语言都有“安装包”片段，用于安装您的SDK版本，以及“初始化客户端”片段，用于导入SDK并初始化Foundry客户端以与Ontology交互。

## 使用Ontology SDK

Ontology SDK成功发布后，请按照说明安装和导入SDK。您可以运行以下命令：

```
Copied!1
!mamba install -y -q {sdk_package_name}
```

这个命令用于使用mamba包管理器安装指定的软件包。在这里，{sdk_package_name}是占位符，需要替换为实际的软件包名称。以下是选项的说明：

- -y: 自动确认所有提示，不需要用户手动确认。
- -q: 静默模式，减少输出信息的数量。
接下来，以下代码片段用于初始化FoundryClient，这将使您能够开始使用Ontology SDK。
```
Copied!1
2
from {sdk_package_name} import FoundryClient
client = FoundryClient()  # 创建 FoundryClient 实例
```

## 基本用法示例

在数据实体标签中可以选择任何导入的Object或链接类型，以查看该特定资源的用法示例。以下示例是更长、更通用的示例，展示了在Code Workspaces中端到端使用OSDK的用法。

### Python OSDK 使用示例

以下示例演示了如何使用Python与OSDK进行交互。此示例假设您SDK的最后一个成功发布版本包括Object类型"Aircraft"和操作类型"ActionMode"。示例中的术语{sdk_package_name}应替换为您SDK的包名称。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
# 定义AircraftObject为客户端本体中的Aircraft对象
AircraftObject = client.ontology.objects.Aircraft

# 获取一个对象并查看其属性
my_aircraft = AircraftObject.get(1)
my_aircraft.date_of_manufacture  # 获取飞机的制造日期

# 遍历对象
for aircraft in AircraftObject.take(2):
    print(aircraft.current_location)  # 打印每架飞机的当前位置

# 聚合操作
AircraftObject.aggregate({"min_id": Aircraft.id.min(),  # 获取最小ID
                          "max_id": Aircraft.id.max(),  # 获取最大ID
                          "aircraft_count": Aircraft.count()}).compute()  # 计算飞机总数

# 过滤操作
my_a330s = AircraftObject.where((Aircraft.type == "A330") | (Aircraft.id == 160)).take(1)  # 获取类型为A330或ID为160的飞机

# 动作: 验证并应用
import datetime
from {sdk_package_name}.types import ActionMode

# 验证制造日期的更改
action_validation = client.ontology.actions.change_manufacture_date({"mode": ActionMode.VALIDATION_ONLY},
                                                                     aircraft=1,
                                                                     date_of_manufacture="2020-05-01")
if action_validation.result == "VALID":
    # 如果验证通过，应用制造日期的更改
    client.ontology.actions.change_manufacture_date(aircraft=1, date_of_manufacture="2023-05-26")
```

### R OSDK 使用示例

Code Workspaces 通过reticulate ↗包支持 R 中的 OSDK，这允许您从 R 中调用 Python。

此示例演示了如何将 Python OSDK 版本导入 R 并与 Object 类型交互。此示例假设您的 SDK 包含一个名为 "Aircraft" 的 Object 类型。术语{sdk_package_name}应替换为您的 SDK 的包名。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
library(reticulate)

# 导入指定的Python SDK包
osdk <- import("{sdk_package_name}")
# 创建Foundry客户端
client <- osdk$FoundryClient()

# 获取Aircraft对象的接口
aircraft_object = client$ontology$objects$Aircraft

# 检索1个对象
aircraft_object$take(1L)

# 根据ID检索对象
aircraft_object$get("1")
```

由于R和Python具有不同的默认数值类型，当Python API需要整数时，必须在R中使用L后缀。在reticulate的官方文档中了解更多信息。↗

Jupyter®、JupyterLab®和Jupyter®标识是NumFOCUS的商标或注册商标。

RStudio®和Shiny®是Posit™的商标。

所有引用的第三方商标（包括标识和图标）仍为其各自所有者的财产。不暗示任何从属关系或认可。
