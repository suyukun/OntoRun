来源: https://palantir.com/docs/zh/foundry/code-repositories/configure-repositories-in-control-panel/

# 在控制面板中配置代码库设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 在控制面板中配置代码库设置

适用于 Visual Studio Code 的 Palantir 扩展处于测试阶段，仅对少部分用户开放。与此扩展相关的设置仅适用于具有该扩展访问权限的用户。对于其他用户，这些设置将无效。

您可以在控制面板中配置许多组织范围的代码库设置。要修改这些设置，您需要具有用户体验管理员角色。

## 可用设置

- 本地开发：启用后，您组织中的用户将能够克隆代码库并在本地进行工作。此设置默认启用。
- 适用于 Visual Studio Code 的 Palantir 扩展：启用后，您组织中的用户将能够在本地使用适用于 Visual Studio Code 的 Palantir 扩展。此扩展通过连接到远程代码助手工作区，使用户能够查看其库中的变换，预览数据集等。此设置默认启用，但仅在用户可以使用适用于 Visual Studio Code 的 Palantir 扩展时适用。
- 通过适用于 Visual Studio Code 的 Palantir 扩展进行本地预览：默认情况下，使用适用于 Visual Studio Code 的 Palantir 扩展时，数据不会下载到用户的计算机上，因为操作在远程代码助手工作区运行。但是，当启用此设置时，您组织中的用户可以在本地预览数据集。数据集的本地预览涉及将数据集的一部分下载并临时存储到用户的计算机上，只要他们拥有该数据的适当权限。此设置默认禁用。