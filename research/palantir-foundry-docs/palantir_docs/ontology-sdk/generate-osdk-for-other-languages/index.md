来源: https://palantir.com/docs/zh/foundry/ontology-sdk/generate-osdk-for-other-languages/

# 为其他语言生成 OSDK

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 为其他语言生成 OSDK

OSDK 开发者控制台内置了 TypeScript 和 Python 的支持，可以通过 pip 和 Conda 进行代码生成，但不限于这些语言。开发者控制台还支持以行业标准OpenAPI 格式 ↗导出 API。您可以使用开源代码生成器基于下载的 OpenAPI 规范生成几乎任何语言的客户端。

## 导出 OpenAPI 规范

导航至开发者控制台应用程序中的Application API页面并打开SDK 生成选项卡。然后，选择Other languages并选择Export as OpenAPI。

由于导出的文件将包含开发者控制台应用程序中包含的资源的名称和描述，请确保这些字段不包含敏感信息。

## 在其他语言中生成客户端和服务器

一旦 OpenAPI 文件被导出，您可以使用开源生成器生成客户端和服务器。OpenAPI 生成器的列表可以在OpenAPI 生成器网站 ↗上找到。
