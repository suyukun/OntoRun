来源: https://palantir.com/docs/zh/foundry/transforms-python/use-python-libraries/

# 发现和使用 Python 库

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 发现和使用 Python 库

代码库允许您导入和使用公共库以及 Foundry 生成的库。以下信息仅适用于Python库。

## 发现 Python 库

要搜索 Python 库，请点击代码库环境左侧面板上的包选项卡。使用搜索框搜索可用的库。

点击库名以显示库详情，并选择添加库，这会将推荐的库版本添加到您的分支。

一旦您添加了库，代码助手依赖项将被刷新，您将可以从库中可用的包中导入模块。

### 添加例外依赖项

添加 Python 库有时需要将必要的构件库添加到您的代码库中并在项目中引用。在这种情况下，将出现一个对话框，请求您确认此操作。

依赖项对话框将突出显示任何您没有访问权限的必要库。您需要访问这些库才能使用该库。

代码库将尝试为您的库找到可用的支持库并自动使用它们。在需要特定支持库的情况下，您可以直接在库的构件设置页面中进行设置。

### 固定特定的库版本

如果您需要特定版本，您可以通过点击设置按钮并从列表中选择所需版本来“固定”它。这使您可以设置不同的版本来运行您的变换和测试。

请注意，在固定特定版本的库后，它将被添加到您的meta.yaml文件中，但不会通过任务运行器安装。验证检查成功通过后，重启代码助手以将更改应用到您的meta.yaml文件中。然后，您可以在您的库中开始使用所选版本的库。

在固定特定版本时要小心。固定版本可能会阻止您的代码获得重要更新。始终确保您检查并更新您的依赖项。

### 审查库更改

从您的库中添加和删除 Python 库的操作与任何其他代码更改行为相同。您应该提交您的更改并将其合并到受保护的分支。在拉取请求中，库更改将显示为meta.yaml文件中的更改。

有时，当您创建拉取请求时，您会看到.lock类型文件的合并冲突。这发生在更新时，您正在处理您的分支。在这种情况下，接受所有更改并继续您的拉取请求。

## 使用发布到共享频道的库

这是一个已弃用的功能，可能在您的环境中不可用。

如果您的库已发布到共享频道（请参阅发布 Python 库），您必须编辑 Python 子项目的build.gradle。您将修改隐藏文件，因此在继续之前请确保选择“显示隐藏文件”。您的变换 Python 项目需要访问发布共享库的频道。在变换 Python 子项目文件夹中的build.gradle文件中，添加以下内容：

```
Copied!1
2
3
 transformsPython {
     sharedChannels  "libs"
}
```

您必须编辑位于您的 Python 子项目文件夹中的build.gradle文件，而不是库根目录的文件。确保添加到文件末尾，以便apply plugin:已经被执行并正确处理。

## 构件库设置

通常，在使用 Python 库时不需要访问库设置。当您添加 Python 包时，所需的构件库将自动添加。您应避免在设置选项卡中直接编辑引用的 Python 库列表。

当使用共享库时，会将相关库的引用添加到项目中。您可以通过访问库设置选项卡的“构件”部分查看引用库的列表。

如果您手动添加了共享库依赖项而不是通过构件包搜索，您将需要通过构件设置将库库添加到您消费库的支持库中。请注意，这不被鼓励，因为包搜索将为您执行此操作。

## 任务运行器

任务运行器仅在较新的库中可用。您可以通过显示隐藏文件并检查templateConfig.json文件来检查库的版本。

- 如果您的库具有parentTemplateId为transforms，请确保parentTemplateVersion为 8.220.0 或更高，并且 Python 子模板为 1.484.0 或更高。
- 如果您的库具有parentTemplateId为python-library，请确保parentTemplateVersion为1.497.0或更高。
您可以升级您的库以启用此功能。

当任务运行器启用时，从左侧面板的库选项卡中添加包将不再提供新的代码助手工作区，而是开始在您当前环境的基础上安装请求的包，同时返回底层进程的所有日志。

如果安装成功，锁定文件将使用新环境更新。如果安装不成功，任务运行器底部面板将显示一个错误消息，可用于进一步挖掘问题。

任务运行器将仅更新run环境，目前不支持安装仅用于测试的依赖项。

## 高级设置

以下信息仅适用于管理员和高级用户。

### meta.yaml文件

您应该避免编辑meta.yaml文件，因为这容易出错。相反，应倾向于通过库搜索界面添加库。

要在代码库中使用 Python 库，必须将其包含在conda_recipe/meta.yaml文件中。这在通过库搜索界面添加库时会自动发生。

```
Copied!1
2
3
4
5
6
requirements:
...
run:
    - python
    ...
    - {LIBRARY NAME} # 用你的共享库的名称替换此处。
```

添加库后，点击meta.yaml文件顶部的“刷新依赖项”。这将确保代码辅助工具更新了新的依赖项，使您可以继续从可用的包中导入模块。

查看更多有关meta.yaml 文件的信息。

#### Conda 解析 Python 包

Conda 是一个开源的、语言无关的包和环境管理器，被用于在代码库中解析包依赖项并将一组包安装到独立的环境中。更多信息请参阅官方 Conda 文档 ↗或环境创建介绍。

#### Conda 锁文件

在代码库中运行检查时，我们会解析meta.yaml文件中列出的包的 Conda 环境，并生成带有.lock扩展名的隐藏 Conda 锁文件；这些锁文件保存了 Conda 环境。这个预解析的环境使得 Conda 解析在您提交代码时的后续检查中更快。

我们在以下情况下重新解析 Conda 环境并写入新的锁文件：

- meta.yaml文件中的包列表发生了更改。
- 仓库已升级到较新的模板版本。
- 在您的锁文件中发现了已召回的包。
- 隐藏的 Conda 锁文件已被删除或编辑。
当我们重新解析环境并写入新的锁文件时，初始提交哈希为SUPERSEDED，后跟另一个提交哈希，它重新写入锁文件。当需要重新解析环境时，检查可能需要更长时间。

### 下载平台外已发布的 Python 库

可以从 Foundry 外部下载在 Palantir Foundry 内发布的库：

- 获取用户词元。在 Foundry 中，导航到您的用户帐户设置并选择词元。选择创建词元，输入词元的名称和描述，然后选择生成。复制您的词元。
不要与其他应用程序或用户共享您的词元；恶意行为者可能会利用它冒充您。

- 找到您的 Python 库的<identifier>。导航到感兴趣的 Python 库的代码库。浏览器 URL 现在应类似于：https://<my-foundry-url>/workspace/data-integration/code/repos/<identifier>/contents/refs%2Fheads%2F<branch>。在 URL 中，找到<identifier>，它看起来像ri.stemma.main.repository.XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX。
- 获取库的包索引。在本地计算机上打开终端并运行以下命令：curl -H "Authorization: Bearer $TOKEN" https://$STACK_URL/artifacts/api/repositories/$IDENTIFIER/contents/release/conda/$PLATFORM/repodata.json其中$TOKEN是您的用户词元，$STACK_URL与上一步中的<stack-url>相同，$IDENTIFIER是上一步中的<identifier>，$PLATFORM是仓库平台（例如noarch，linux-64）。上述命令的输出是库的内容索引（即它包含的包）。每个包的格式为<name>-<version>-<build-string>.tar.bz2。
- 下载特定包。您可以通过在终端中运行以下命令从 Python 库下载特定包：curl -H "Authorization: Bearer $TOKEN" https://$STACK_URL/artifacts/api/repositories/$IDENTIFIER/contents/release/conda/$PLATFORM/$PACKAGE，其中$PLATFORM是包平台（例如noarch，linux-64），$PACKAGE的格式为<name>-<version>-<build-string>.tar.bz2。
### 在任务运行器中运行任务

您可以通过手动指定命令从任务运行器中手动触发包安装。

例如，要安装pandas，请选择底部面板中的任务运行器选项卡，然后输入以下命令：

```
Copied!1
install --packageSpecs=pandas
```

该命令用于安装一个名为pandas的软件包。pandas是一个用于数据处理和分析的 Python 库。注意，这个命令的语法似乎不符合常见的包管理工具（如pip或conda），请确认是否使用的是特定的包管理工具或平台。
任务运行器还支持以下命令：

- uninstall: 从运行环境中卸载包。注意：此命令还会卸载依赖于指定包的任何包。此命令仅在较新的存储库中可用。如果您的存储库具有parentTemplateId为transforms，请确保Python子模板在1.525.0或更高版本。同样，如果您的存储库具有parentTemplateId为python-library，请确保parentTemplateVersion在1.525.0或更高版本。用法：uninstall --packageSpecs=<eg.numpy>用于Conda包。
- 注意：此命令还会卸载依赖于指定包的任何包。此命令仅在较新的存储库中可用。如果您的存储库具有parentTemplateId为transforms，请确保Python子模板在1.525.0或更高版本。同样，如果您的存储库具有parentTemplateId为python-library，请确保parentTemplateVersion在1.525.0或更高版本。
- 用法：uninstall --packageSpecs=<eg.numpy>用于Conda包。
- formatCode: 格式化存储库中的文件。使用Black来格式化代码，并使用pyproject.toml进行自定义格式化程序配置。请参阅Black格式化程序配置文件文档 ↗获取更多信息。
- whoneeds: 显示在当前运行环境中需要安装某个包的包树。注意：此命令仅在较新的存储库中可用。如果您的存储库具有parentTemplateId为transforms，请确保Python子模板在1.522.0或更高版本。同样，如果您的存储库具有parentTemplateId为python-library，请确保parentTemplateVersion在1.522.0或更高版本。用法：whoneeds --packageSpec=<eg.transforms>
- 注意：此命令仅在较新的存储库中可用。如果您的存储库具有parentTemplateId为transforms，请确保Python子模板在1.522.0或更高版本。同样，如果您的存储库具有parentTemplateId为python-library，请确保parentTemplateVersion在1.522.0或更高版本。
- 用法：whoneeds --packageSpec=<eg.transforms>
- tasks: 列出所有可运行的任务。