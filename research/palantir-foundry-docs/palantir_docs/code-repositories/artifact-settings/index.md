来源: https://palantir.com/docs/zh/foundry/code-repositories/artifact-settings/

# 工件设置

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 工件设置

如果您希望导入和使用Python库，请参阅有关共享Python库的部分。

工件选项卡包含可以在您的代码库中引用的库列表，我们称之为支持库。这是您Foundry环境中所有共享代码库的列表，以及外部或公共库。您可以使用工件选项卡来发现和添加支持库。

查看工件设置需要artifacts:view-repository权限，管理工件设置需要artifacts:manage-repository权限。

### 向您的代码库添加新工件

要添加新工件，请点击“添加”并选择两种类型的库之一：

- 本地库- 这些是您的Foundry环境中配置为共享库的其他代码库。
- 外部库- 存储在您的Foundry环境之外的工件库。这些可能是外部Foundry库或在您的环境中可用的公共工件库。
如果添加的工件库包含对其他库的引用，它们也会被添加。所有已添加库的依赖项需要相同的访问权限。

当从不同项目添加本地库时，将向该库添加项目引用。这需要在您自己的代码库上具有compass:view-project-imports和compass:import-resource-to权限，并在引用的共享库上具有compass:import-resource-from权限。

虽然可以重新排序和删除支持库，但这可能会破坏使用这些库中的包的变换的搭建。只有在考虑可能的影响后再采取此操作。
