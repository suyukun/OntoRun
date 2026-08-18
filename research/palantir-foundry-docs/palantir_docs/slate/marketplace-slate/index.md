来源: https://palantir.com/docs/zh/foundry/slate/marketplace-slate/

# 将 Slate 应用添加到 Marketplace 产品 [Beta]

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 将 Slate 应用添加到 Marketplace 产品 [Beta]

使用Foundry DevOps将您的 Slate 应用包含在Marketplace 产品中，以便其他用户安装和重用。了解如何创建您的第一个产品。

## 支持的功能

Marketplace 产品目前支持通过Platform选项卡配置的具有对象集和函数源的 Slate 应用。Marketplace 还支持没有数据加载的静态 Slate 应用。

## 将 Slate 应用添加到产品

要将 Slate 应用添加到产品，首先创建一个产品，然后选择如下所示的Slate 应用内容类型。

## 打包使用 Code Sandbox 微件的 Slate 应用

具有 Code Sandbox 微件对外部库依赖的 Slate 应用可以与 Marketplace 一起打包。

如果您希望在安装时生成库文件的副本，请确保在创建产品时在Content选项卡下的Files选项卡中包含这些库的文件。当用户安装产品时，他们会在其项目中获得这些文件的副本。Code Sandbox 微件将引用其库文件的副本。

Slate 还支持通过 CDN 链接（例如https://unpkg.com/browse/chart.js@2.7.1/）提供库。CDN 链接保持不变，因此安装的 Slate 应用将具有相同的 CDN 链接。这可能意味着用户需要配置其 CSP 以允许 CDN 链接。

有关使用 Code Sandbox 微件的库的更多信息，请参见Code Sandbox 微件文档。
