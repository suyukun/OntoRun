来源: https://palantir.com/docs/zh/foundry/pipeline-builder/marketplace-pipeline-builder/

# 向Marketplace产品添加pipeline [Beta]

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 向Marketplace产品添加pipeline [Beta]

使用Foundry DevOps将您的Pipeline Builder pipelines包含在Marketplace产品中，以供其他用户安装和重用。了解如何创建您的第一个产品。

## 支持的功能

Marketplace产品支持所有Pipeline Builder功能，但以下情况除外：

- 具有时间序列目标的流式pipeline
- 以下类型的参数：结构类型常量、不由常量组成的复杂表达式、选项和结构定位器。
### 使用Marketplace linter检查Marketplace兼容性

在Pipeline Builder中，您可以使用Marketplace linter检查pipeline是否与Marketplace兼容。要启用此功能，请导航到设置，并在您的pipeline中选择启用Marketplace验证。此设置默认未启用。

启用后，pipeline底部的Pipeline警告部分将显示任何阻止您的pipeline在Marketplace中打包的出错。

如果没有Marketplace不兼容性，则错误/警告抽屉中不会出现Marketplace打包警告。请注意，其他类型的pipeline出错或警告可能仍然会出现。

## 将Pipeline Builder pipelines添加到产品

要将Pipeline Builder pipeline添加到产品中，首先创建一个产品，然后选择如下所示的Pipeline内容类型。

## Pipeline参数

您可以使用pipeline参数以便安装者在安装时自定义他们的pipeline。例如，您可以使用boolean参数根据安装者的输入选择pipeline的一个分支而不是另一个。参见支持的功能以获取支持的参数类型列表。当您使用参数打包pipeline时，该参数将作为pipeline的依赖项和安装者的输入显示，如下所示。

## 打包设置

要配置安装者所需或非必填的数据集和列，请导航到Pipeline输出面板 > 设置以访问打包设置。

默认情况下，所有列和输入数据集对于Marketplace安装都是必需的。如果有任何不需要的列或输入数据集，您可以将它们标记为非必填。非必填的输入数据集将默认为空，非必填的列值将在pipeline逻辑中使用时默认为null。
