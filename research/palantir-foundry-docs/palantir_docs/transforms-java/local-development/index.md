来源: https://palantir.com/docs/zh/foundry/transforms-java/local-development/

# 搭建 Java 本地开发环境

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 搭建 Java 本地开发环境

可以对变换 Java 仓库进行本地开发，以实现高速迭代开发。

## 为 Java 变换仓库设置本地开发环境

### 克隆仓库

- 在您的仓库菜单栏中，选择本地工作并复制仓库 URI，也称为 "git 远程 URL"。
仓库 URI (git 远程 URL) 包含与您的账户相关的敏感信息，不应分享。为了维护平台安全，请不要与他人分享此链接或公开发布。

- 使用命令行，在本地机器上运行git clone <URI>，选择一个目录。然后使用cd命令导航到该仓库。
### 限制

- 克隆时授予的词元是短期和只读的，推送回仓库除外。
- 您仍然需要将您的更改推送到 Foundry，以发布任务规范或制品，或者如果您希望运行检查或搭建。
### 预览

在本地开发中支持数据集预览。请参见本地预览以获取更多详细信息。

## 设置开发环境

### 先决条件

- 确保已安装 Java 17，并且环境变量JAVA_HOME指向正确的 Java 安装。您可以从Oracle 网站 ↗下载 Java 17。
根据您的操作系统设置JAVA_HOME环境变量：

- Windows：在 PowerShell 中运行SETX JAVA_HOME -m "<java-home-dir>"。这将修改系统环境变量，您需要重新启动 shell 以使更改生效。或者，您可以运行[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "<java-home-dir>")在运行的进程中设置JAVA_HOME。
- Linux 或 macOS：运行export JAVA_HOME=<java-home-dir>。
- 确保您的仓库已按照此处的步骤升级到最新的模板版本。
### 配置 IDE

- 在您的机器上安装IntelliJ Idea ↗。
- 打开命令行终端，使用cd导航到包含您仓库的目录，然后运行./gradlew openIdea。此 Gradle 任务将生成一个 IntelliJ Idea 项目并打开它。在 Windows 上，./gradlew openIdea命令必须从 Git BASH 运行，Git BASH 包含在Git for Windows ↗中。
- 在 Windows 上，./gradlew openIdea命令必须从 Git BASH 运行，Git BASH 包含在Git for Windows ↗中。
### 限制

- Gradle 命令必须从终端使用./gradlew运行，而不是使用 IntelliJ 的 Gradle 插件。
- 本地开发支持 Java 版本最多到 Java 17，目前不支持更高的 Java 版本。