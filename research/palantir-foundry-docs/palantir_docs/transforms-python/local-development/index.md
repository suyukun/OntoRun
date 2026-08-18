来源: https://palantir.com/docs/zh/foundry/transforms-python/local-development/

# 设置 Python 本地开发

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 设置 Python 本地开发

可以进行 Transforms Python 仓库的本地开发，从而实现高速迭代开发。

## 为 Python 变换库设置本地开发环境

### 克隆仓库

- 在仓库的菜单栏中，选择本地工作以打开对话框并复制给定的仓库 URL。
- 使用命令行，在本地机器上运行git clone <URI>于您选择的目录中。然后使用cd命令导航到仓库。
### 限制

- 授予用于克隆的词元是短期的并且仅可读，除了推送回到您的仓库。
- 您仍然需要将更改推送到 Foundry 以发布任务规格或工件，或者如果您希望运行检查或搭建。
### 预览

数据集预览在本地开发中是支持的。请参阅本地预览获取更多细节。

## 设置开发环境

### 先决条件

- 确保 Java 17 已安装，并且环境变量JAVA_HOME指向正确的 Java 安装。Java 17 可以从Oracle 网站 ↗下载。
根据您的操作系统设置JAVA_HOME环境变量：

- Windows: 在 PowerShell 中运行SETX JAVA_HOME -m "<java-home-dir>"。这会修改系统环境变量，您需要重启 shell 以使更改生效。或者，您可以运行[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "<java-home-dir>")在运行进程中设置JAVA_HOME。
- Linux 或 macOS: 运行export JAVA_HOME=<java-home-dir>。
- 确保您的仓库已升级到最新的模板版本，按照此处概述的步骤进行。
确保您的仓库已升级到最新的模板版本，按照此处概述的步骤进行。

- 确保环境变量CI、JEMMA和CA没有设置。
确保环境变量CI、JEMMA和CA没有设置。

- 如果在 Apple silicon Mac 上运行，确保安装了Rosetta 2 ↗。您可以通过在终端中运行/usr/sbin/softwareupdate --install-rosetta --agree-to-license来安装 Rosetta 2。
如果在 Apple silicon Mac 上运行，确保安装了Rosetta 2 ↗。您可以通过在终端中运行/usr/sbin/softwareupdate --install-rosetta --agree-to-license来安装 Rosetta 2。

## Visual Studio Code

- 确保您已安装Visual Studio Code ↗。
- 从 Visual Studio Code 网站或应用程序中的扩展选项卡安装Python 扩展 ↗。
- 如果在您的注册中启用，安装适用于 Visual Studio Code 的Palantir 扩展[Beta]。
### 要求

适用于 Visual Studio Code 的 Palantir 扩展处于 beta 状态，在您的注册中可能不可用。

要使用适用于 Visual Studio Code 的 Palantir 扩展，您必须在您的注册中拥有对代码仓库的访问权限。

如果您看到意外的语言服务器出错，例如导入出错，可能是 Python 解释器的自动设置失败。要解决此问题，您可以通过导航到命令面板 ↗，然后输入Python: Select interpreter并选择匹配路径的 Python 解释器：./maestro/bin/python来手动设置解释器。如果 Palantir 扩展成功运行命令Palantir: Install Python environment，那么.maestro文件夹应该存在。

## PyCharm

- 要设置 Python 开发环境，运行命令./gradlew condaDevelop。
要设置 Python 开发环境，运行命令./gradlew condaDevelop。

- 确保您本地安装了JetBrains PyCharm ↗。
确保您本地安装了JetBrains PyCharm ↗。

- 按照此处 ↗概述的步骤导入项目。
按照此处 ↗概述的步骤导入项目。

- 从状态栏的Python 解释器选择器 ↗中选择添加新解释器。
从状态栏的Python 解释器选择器 ↗中选择添加新解释器。

- 在添加 Python 解释器对话框的左侧窗格中，选择Virtualenv 环境。
在添加 Python 解释器对话框的左侧窗格中，选择Virtualenv 环境。

- 选择现有环境，并将解释器字段设置为来自您的 Conda 环境的 Python 解释器。可以通过运行./gradlew condaEnvList列出 Conda 环境路径。对于 Unix，Python 解释器路径是<your-conda-environment-dir>/bin/python。对于 Windows，Python 解释器路径是<your-conda-environment-dir>\python.exe。
选择现有环境，并将解释器字段设置为来自您的 Conda 环境的 Python 解释器。可以通过运行./gradlew condaEnvList列出 Conda 环境路径。

- 对于 Unix，Python 解释器路径是<your-conda-environment-dir>/bin/python。
- 对于 Windows，Python 解释器路径是<your-conda-environment-dir>\python.exe。
根据是否启用测试插件，安装的环境列表将包括./transforms-python/build/conda/run-env或./transforms-python/build/conda/test-env或两者。如果计划运行测试，应选择测试环境。

- 选择确定。
### （高级设置）基于 Gradle 的环境

如果适用于 Visual Studio Code 的 Palantir 扩展在您的注册中不可用，可以使用 Gradle 来设置 Python 环境。在新的终端窗口中，使用cd命令导航到仓库目录，然后运行./gradlew vsCode。这将创建一个 Python 环境，并通过将其放置在.vscode/setting.json文件中来配置 Visual Studio Code 使用该环境的 Python 解释器。
