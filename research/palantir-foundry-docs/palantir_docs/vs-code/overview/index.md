来源: https://palantir.com/docs/zh/foundry/vs-code/overview/

# VS Code Workspaces

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# VS Code Workspaces

VS Code workspaces 和 Palantir extension for Visual Studio Code 与 Microsoft 无关，也未获得其认可。

VS Code workspaces 目前处于测试阶段，并在所有启用 Code Workspaces 的组织中默认可用。

VS Code workspaces 是一个集成开发环境 (IDE)，用于在 Palantir 平台上编写和协作生产就绪的代码。VS Code workspaces 利用 Microsoft 的VS Code ↗，这是一个用于编辑和管理代码的开源 IDE。

要访问 VS Code workspace，首先在 Code Repositories 应用程序中打开现有或新的Python 变换或OSDK React仓库。从这里，在屏幕右上角选择Open in VS Code选项。这将带您进入一个 VS Code workspace，您的开发环境将自动设置好，允许您立即开始工作。

VS Code workspaces 仅适用于支持的工作流。

## Palantir extension for Visual Studio Code

除了我们平台内的 VS Code 实例之外，您还可以配置本地 VS Code 环境以与 Palantir 集成。为此，您需要下载并安装Palantir extension for Visual Studio Code，该扩展提供了与 Palantir 平台的本地集成，包括您在Code Repositories中看到的许多功能。该扩展目前处于测试阶段，当前专注于为 Python 变换提供功能。它在 VS Code Workspaces 中默认启用。

了解有关 Palantir extension for Visual Studio Code 功能的更多信息。

## 支持的工作流

VS Code workspaces 仍在开发中，可能会随着时间的推移而更改。目前在本地和平台内的 VS Code 版本中支持以下工作流：

- Python 变换
- OSDK React 应用程序
- 计算模块（仅限 Python 计算模块）
- Python 库
### Python 变换

Palantir extension for Visual Studio Code 会在启动时自动设置您的 Python 环境，并启用以下功能：

- 预览集成
- 调试支持
- 从编辑器内部触发数据集搭建
- 使用资源标识符显示资源路径，便于导航和参考
- 自动设置您的代码环境
- 代码片段以有效地编写重复代码
### OSDK React 应用程序

您必须启用web 托管才能使用 VS Code workspaces 进行 OSDK React 应用程序。

VS Code 已与Developer Console集成，允许您快速搭建 React 应用程序。您可以在 Developer Console 的Code repository部分创建一个 VS Code workspace。

Palantir 中 VS Code 与 React OSDK 应用程序集成的其他优点包括：

- 与 OSDK 完整的 Ontology 集成，以便与您的独特 Ontology 资源进行交互和编码
- 能够配置预配置 OAuth 的 git 仓库
- 一个持续集成设置，用于在每次发布时部署您的网站
- 自动设置您的 node/npm 环境
- 自动启动您的开发服务器，以便在编辑代码时即时反馈
## 比较：VS Code workspaces 与 Code Repositories

VS Code 和 Code Repositories 在预期的应用案例上有一些重叠。然而，它们的功能在以下方面有所不同：

- Code Repositories:一个由 Palantir 搭建的 IDE，满足所有代码管理需求，如编辑、版本控制和更改管理以及持续集成。Code Repositories 是用于 pull request 审核和仓库管理的预期平台工具。
- VS Code:一个由社区搭建的 IDE，专注于改进代码编辑体验。VS Code workspaces:一个部署在 Palantir 基础设施上的 VS Code 环境，可以从 Palantir 平台访问。Palantir extension for Visual Studio Code:一个可以安装并在本地 VS Code 应用程序中使用的扩展，直接与 Palantir 中的代码仓库集成。
- VS Code workspaces:一个部署在 Palantir 基础设施上的 VS Code 环境，可以从 Palantir 平台访问。
- Palantir extension for Visual Studio Code:一个可以安装并在本地 VS Code 应用程序中使用的扩展，直接与 Palantir 中的代码仓库集成。
| 功能 | Code Repositories | VS Code workspaces | Palantir extension for Visual Studio Code（通过本地 VS Code 应用程序） |
| --- | --- | --- | --- |
| 变换 |  |  |  |
| Python 变换预览 | 是 (Code Assist) | 是 (本地预览) | 是 (Code Assist/本地预览) |
| 完整数据预览 | 预览数据样本，可预筛选输入样本 | 是 | 是 (仅本地预览) |
| 调试器支持 | 是 | 是 | 是 |
| Java 变换 | 是 | 否 | 否 |
| OSDK React 应用程序 |  |  |  |
| Typescript Language Server | 否 | 是 | 是 |
| 实时重新加载代码更改 | 否 | 是 | 是 |
| Python 计算模块 |  |  |  |
| 运行和调试 Python 文件 | 否 | 是 | 是 |
| Python 库 |  |  |  |
| 运行和调试 Python 文件 | 否 | 是 | 是 |
| 工作流 |  |  |  |
| SQL 集成 | 是 | 否 | 否 |
| Typescript 函数预览 | 是 | 否 | 否 |
| IDE |  |  |  |
| Shell 终端 | 否 | 是 (远程主机) | 是 |
| 键绑定自定义 | 否 | 是 | 是 |
| 公共扩展支持 | 不适用 | 否 | 是，如果您的组织允许 |
| AIP 自动完成 | 是 | 否 | 否 |

### 价格

有关 VS Code workspace 的价格信息，请参阅Code Workspaces 计算使用。
