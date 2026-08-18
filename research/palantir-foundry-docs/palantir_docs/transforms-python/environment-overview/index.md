来源: https://palantir.com/docs/zh/foundry/transforms-python/environment-overview/

# 概览

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 概览

用于变换的Python环境是在检查期间使用Hawk包管理器根据conda_recipe/meta.yaml文件中指定的包列表解决的。使用包选项卡，您可以发现可用包并自动将其添加到您的meta.yml以便于环境解析。这个解析后的环境会在内部发布到Artifacts中，准备在搭建过程中使用。

当变换被搭建时，它会获取环境文件并安装环境文件中指定的所需包。如果由于某种原因失败，变换将在搭建过程中使用Hawk再次解析环境。

### 有用的资源

请参阅环境创建简介，了解使用Conda、Mamba和Hawk创建环境的介绍。有关常见环境问题的一般故障排除，请参阅环境故障排除指南。
