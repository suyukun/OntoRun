来源: https://palantir.com/docs/zh/foundry/code-repositories/artifact-repositories-overview/

# Artifact 存储库

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# Artifact 存储库

Artifact 存储库使用户能够发布和管理 Artifact，包括Conda ↗、Docker ↗和Maven ↗。

Artifact 存储库被用于在上传所有非以库形式创作或通过外部 URL 访问的 Conda、Docker 或 Maven Artifact。例如，您可能在本地机器上编写了一个 Conda 包，您希望在代码存储库中访问它。通过将 Conda 包发布到 Artifact 存储库，您将可以从代码存储库中的Library搜索面板访问它。

Artifact 存储库的关键功能包括：

- 发布 Artifact:生成词元并将 Artifact 推送到 Artifact 存储库。
- 搜索 Artifact:从 Artifact 存储库界面查找 Artifact。
- 召回 Conda Artifact:召回 Conda Artifact，以防止下游消费者使用特定版本编译代码。
了解更多关于 Artifact 存储库界面的信息以及如何创建一个 Artifact 存储库。
