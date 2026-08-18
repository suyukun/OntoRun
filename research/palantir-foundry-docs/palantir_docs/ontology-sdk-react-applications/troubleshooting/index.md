来源: https://palantir.com/docs/zh/foundry/ontology-sdk-react-applications/troubleshooting/

# 故障排除

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 故障排除

本页面包含在开发OSDK React应用程序时可能遇到的错误的故障排除提示。如果您有其他问题或无法通过本指南解决您的问题，请报告问题给Palantir客服支持。

## 工作区错误

如果在Palantir平台内工作，您将使用运行在Palantir代码工作区基础设施上的VS Code工作区。更多故障排除信息可以在以下文档中找到：

- VS Code工作区故障排除
- 代码工作区故障排除
## npm故障排除步骤

如果您在运行npm命令时遇到问题，请尝试以下故障排除步骤：

- 删除锁定文件（package-lock.json）和依赖文件夹（node_modules/），然后重新运行出错的命令。
- 暂停并恢复工作区。
### NPM MODULE_NOT_FOUND错误：添加新依赖

代码库要求显式声明您的依赖。

默认情况下，我们添加以下npm库：

- 常见的OSDK依赖：foundry-sdk-asset-bundle，osdk-templates-bundle
- npmjs.com ↗镜像：external-npm-npmjs
- 您的OSDK：SDK Artifacts Repository - <rid>
如果您尝试添加一个在任何支持库中不存在的软件包，npm install <package>命令可能会失败。例如，如果您尝试安装的软件包是私有的，您必须确保它作为库Artifact存在。查看我们的Artifacts文档以获取更多信息。

示例错误：

当VS Code工作区内无法访问npmjs.com时，npm将发出错误code E401 Incorrect or missing password。
