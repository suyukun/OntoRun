来源: https://palantir.com/docs/zh/foundry/palantir-extension-for-visual-studio-code/extension-features/

# 功能列表: Visual Studio Code的Palantir扩展

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 功能列表: Visual Studio Code的Palantir扩展

本页面描述了Visual Studio Code中Palantir扩展可用的功能。

- 变换搭建
## 命令

以下部分列出了Visual Studio Code中Palantir扩展可用的命令。使用这些命令可以在Palantir生态系统内处理Python变换时提高工作效率，例如在开发管道期间。

如果某个命令未集成在界面中，可以使用命令面板调用。您可以通过Cmd+Shift+P（macOS）或Ctrl+Shift+P（Windows/Linux）快捷键访问命令面板。

### 预览和搭建

#### 运行预览

执行当前变换文件的预览。

- 命令:palantir.transforms.previewFile
- 图标:
#### 在Foundry上搭建

在Foundry上为所选文件启动搭建过程。

- 命令:palantir.transforms.buildFile
- 图标:
#### 打开预览面板

显示预览面板以快速访问变换预览。

- 命令:palantir.transforms.openPreviewPanel
### 变换管理

#### 创建新变换

初始化一个新的变换项目。

- 命令:palantir.transforms.createTransform
#### 安装Python环境

设置开发变换所需的Python环境。

- 命令:palantir.transforms.initializePythonEnvironment
#### 安装Python测试环境

设置用于变换开发的Python测试环境。

- 命令:palantir.transforms.initializePythonTestEnvironment
### 仓库和文件管理

#### 在浏览器中打开文件

在网页浏览器中打开当前选择的文件。

- 命令:palantir.openFileInBrowser
#### 打开仓库

提供快速访问仓库的方式，通过网页浏览器。

- 命令:palantir.openRepository
### 仅用于本地开发的命令

#### 克隆代码仓库

允许克隆仓库用于本地开发。

- 命令:palantir.cloneRepository
#### 重启Code Assist工作区

重启Code Assist的工作区。

- 命令:palantir.code-assist.restartWorkspace
#### 刷新词元

刷新认证词元以保持对Palantir服务的访问。

- 命令:palantir.refreshToken
- 图标:
## 代码片段

Visual Studio Code中的代码片段 ↗是一些模板，可以更轻松地输入重复的代码模式。

以下是Visual Studio Code中Palantir扩展提供的所有可用代码片段的列表。符号→代表Tab键。

### 长格式代码片段

| 代码片段 | 输出代码模板 |
| --- | --- |
| python_transform→ | 一个Python变换 |
| polars_transform→ | 一个使用Polars的Python轻量级变换 |
| pandas_transform→ | 一个使用pandas的Python轻量级变换 |

### 短格式代码片段

| 代码片段 | 输出代码模板 |
| --- | --- |
| ptf→ | 一个Python变换 |
| pltf→ | 一个使用Polars的Python轻量级变换 |
| pdtf→ | 一个使用pandas的Python轻量级变换 |
